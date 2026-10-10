"""D-19 Q5/QJ rule libraries (proposal revision 3, accepted 2026-10-11).
Synthetic returns only."""

from __future__ import annotations

import itertools
from collections.abc import Callable

import numpy as np
import pytest

from calibration import rules, semi
from calibration.generator import benchmark_exposure

R = np.random.default_rng(11).normal(0, 0.035, (320, 2))
V_BAR = rules.reference_variance(R)


def test_the_rule_index_is_one_to_one_and_balanced() -> None:
    triples = [rules.index(i) for i in range(rules.RULES)]
    assert len(set(triples)) == 27 and triples[0] == (0, 0, 0)
    for d in range(3):
        assert sorted(t[d] for t in triples[:3]) == [0, 1, 2]
    for d, e in itertools.combinations(range(3), 2):
        assert len({(t[d], t[e]) for t in triples[:9]}) == 9
    with pytest.raises(ValueError):
        rules.index(27)


def test_trial_identities() -> None:
    for family in rules.FAMILIES:
        assert len({rules.trial(family, i) for i in range(27)}) == 27
    assert rules.trial("trend", 0) == ("trend", ("SMA_200", 0.60), 24)
    assert rules.trial("vol", 0) == ("vol", ("EWMA_168h", 0.60), 24)
    ewma = [rules.trial("vol", i) for i in range(27) if rules.index(i)[0] == 0]
    assert {h for _, _, h in ewma} == {24}
    assert {p[0] for _, p, _ in ewma} == set(rules.EWMA_NAMES)


@pytest.mark.parametrize("family", rules.FAMILIES)
def test_every_rule_is_causal(family: str) -> None:
    """Row t must not change when rows t, t+1, ... of the path change."""
    base = rules.library(family, 27, V_BAR)(R)
    for cut in (0, 1, 22, 120, 230, 319):
        other = R.copy()
        other[cut:] = np.random.default_rng(cut).normal(0, 0.08, other[cut:].shape)
        changed = rules.library(family, 27, V_BAR)(other)
        np.testing.assert_array_equal(changed[: cut + 1], base[: cut + 1])


def test_reference_variance_and_the_source_guard() -> None:
    assert V_BAR == pytest.approx(float(np.mean(R[:, 0] ** 2)), rel=0, abs=0)
    for column, bad in [(0, -1.0), (0, np.nan), (0, np.inf), (1, np.nan), (1, -np.inf)]:
        source = R.copy()
        source[5, column] = bad
        with pytest.raises(ValueError):
            rules.reference_variance(source)


def test_a_non_finite_price_index_is_refused() -> None:
    """1e300 x 1e300 overflows: the trend rules raise rather than clip."""
    with pytest.raises(ValueError, match="non-finite price index"):
        rules.trend_targets(np.full(5, 1e300), V_BAR, 0)


# Accepted proposal revision 3, written out independently of the module.
ORDER = [
    (0, 0, 0), (1, 1, 1), (2, 2, 2), (0, 1, 2), (1, 2, 0), (2, 0, 1), (0, 2, 1),
    (1, 0, 2), (2, 1, 0), (0, 0, 1), (1, 1, 2), (2, 2, 0), (0, 1, 0), (1, 2, 1),
    (2, 0, 2), (0, 2, 2), (1, 0, 0), (2, 1, 1), (0, 0, 2), (1, 1, 0), (2, 2, 1),
    (0, 1, 1), (1, 2, 2), (2, 0, 0), (0, 2, 0), (1, 0, 1), (2, 1, 2),
]  # fmt: skip
TAU = (0.60, 0.40, 0.80)
HOURS = (24, 72, 168)


def _expected_trial(family: str, m: int, s: int, k: int) -> tuple[object, ...]:
    if family == "trend":
        return ("trend", (("SMA_200", "SMA_100", "SMA_50")[m], TAU[k]), HOURS[s])
    if m == 0:
        return ("vol", (("EWMA_168h", "EWMA_72h", "EWMA_336h")[s], TAU[k]), 24)
    return ("vol", (("HAR_RV", "GARCH_1_1")[m - 1], TAU[k]), HOURS[s])


@pytest.mark.parametrize("family", rules.FAMILIES)
def test_the_accepted_table_and_constants_are_pinned(family: str) -> None:
    assert [rules.index(i) for i in range(27)] == ORDER
    assert [rules.trial(family, i) for i in range(27)] == [
        _expected_trial(family, *t) for t in ORDER
    ]
    assert (rules.SMA_DAYS, rules.HORIZONS, rules.TAUS) == (
        (200, 100, 50),
        (1, 3, 7),
        TAU,
    )
    assert (rules.TREND_EWMA_HALF_LIFE, rules.EWMA_HALF_LIVES) == (7, (7, 3, 14))
    assert (rules.GARCH_ALPHA, rules.GARCH_BETA) == (0.10, 0.85)
    assert (rules.HAR_BETAS, rules.HAR_C, rules.HAR_LAGS) == (
        (0.35, 0.35, 0.20),
        0.10,
        22,
    )


# Up-drifting, high-vol path: trend signals are mostly on and sizes mostly
# below 1, so a changed return tends to show in the targets.
UP = np.random.default_rng(12).normal(0.004, 0.06, 240)
UP_V_BAR = float(np.mean(UP**2))
PROBES = (None, 0.6, -0.6, 0.0)  # None: the path's own r_t


def _first_violation(targets: Callable[[np.ndarray], np.ndarray]) -> int | None:
    """The first day t at which target 0..t differs between r_t probes."""
    for t in range(len(UP)):
        outs = []
        for value in PROBES:
            other = UP.copy()
            if value is not None:
                other[t] = value
            outs.append(targets(other)[: t + 1])
        if any(not np.array_equal(o, outs[0]) for o in outs[1:]):
            return t
    return None


def _target_fn(family: str, i: int) -> Callable[[np.ndarray], np.ndarray]:
    f = rules.trend_targets if family == "trend" else rules.vol_targets
    return lambda r: f(r, UP_V_BAR, i)


@pytest.mark.parametrize("family", rules.FAMILIES)
def test_every_target_ignores_its_own_day(family: str) -> None:
    """What this proves: for every rule and every day t of the test path,
    targets 0..t are identical under four values of r_t (its own, +60%,
    -60%, 0). It does not prove that every conceivable partial look-ahead
    would change a target under those probes; the witness test below shows
    that the whole-rule one-day look-ahead of each rule is caught."""
    for i in range(27):
        assert _first_violation(_target_fn(family, i)) is None, f"rule {i}"


@pytest.mark.parametrize("family", rules.FAMILIES)
def test_the_check_catches_each_rules_one_day_look_ahead(family: str) -> None:
    """Witness, per rule: the same rule run on the path shifted one day
    earlier (target t then reads r_1 .. r_t) must fail the check above."""
    for i in range(27):
        honest = _target_fn(family, i)

        def peeking(
            r: np.ndarray, f: Callable[[np.ndarray], np.ndarray] = honest
        ) -> np.ndarray:
            return f(np.append(r[1:], 0.0))

        assert _first_violation(peeking) is not None, f"rule {i} not caught"


def test_ewma_and_garch_against_direct_recursions() -> None:
    r = R[:, 0]
    lam, v = 0.5 ** (1 / 3), [V_BAR]
    for t in range(1, len(r)):
        v.append(lam * v[-1] + (1 - lam) * r[t - 1] ** 2)
    np.testing.assert_allclose(rules.ewma_variance(r, V_BAR, 3), v, rtol=1e-14)
    a, b = rules.GARCH_ALPHA, rules.GARCH_BETA
    g = [V_BAR]
    for t in range(1, len(r)):
        g.append((1 - a - b) * V_BAR + a * r[t - 1] ** 2 + b * g[-1])
    for h in rules.HORIZONS:
        expected = []
        for gt in g:  # E[g_{t+k}] by its own recursion, averaged over k < H
            path, e = [], gt
            for _ in range(h):
                path.append(e)
                e = (1 - a - b) * V_BAR + (a + b) * e
            expected.append(np.mean(path))
        np.testing.assert_allclose(
            rules.garch_variance(r, V_BAR, h), expected, rtol=1e-12
        )


def test_har_against_a_direct_forward_iteration() -> None:
    r = R[:, 0]
    b_d, b_w, b_m = rules.HAR_BETAS
    for h in rules.HORIZONS:
        got = rules.har_variance(r, V_BAR, h)
        for t in (0, 3, 21, 22, 200):
            hist = [V_BAR] * 22 + list(r[:t] ** 2)  # r_s^2 = v_bar for s < 0
            fs = []
            for _ in range(h):
                f = (
                    rules.HAR_C * V_BAR
                    + b_d * hist[-1]
                    + b_w * np.mean(hist[-5:])
                    + b_m * np.mean(hist[-22:])
                )
                fs.append(f)
                hist.append(f)
            assert got[t] == pytest.approx(np.mean(fs), rel=1e-12)


def test_har_constants_keep_v_bar_fixed() -> None:
    assert sum(rules.HAR_BETAS) + rules.HAR_C == pytest.approx(1.0)
    flat = np.full(60, np.sqrt(V_BAR))
    np.testing.assert_allclose(rules.har_variance(flat, V_BAR, 7), V_BAR)


def test_the_band_gates_every_rebalance_from_zero() -> None:
    targets = np.array([0.05, 0.12, 0.15, 0.3, 0.2, 0.25, 1.0, 0.95, 0.0])
    # 0.3 - 0.2 is 0.09999999999999998 in binary64; it reaches the band
    assert rules.held(targets).tolist() == [0, 0.12, 0.12, 0.3, 0.2, 0.2, 1, 1, 0]


def test_trend_reads_on_refresh_days_and_waits_for_l_prices() -> None:
    i = next(i for i in range(27) if rules.index(i)[:2] == (2, 2))  # L 50, H 7
    up = np.full(120, 0.01)
    target = rules.trend_targets(up, V_BAR, i)
    assert not target[:50].any()  # fewer than 50 prices: 0
    assert target[56] > 0 and target[55] == 0  # first refresh at or after 50
    assert np.all(target[56:63] == target[56])  # held for 7 days
    flat = rules.trend_targets(np.zeros(120), V_BAR, i)
    assert not flat.any()  # strict: price equal to its SMA is no signal


def test_a_vol_rule_has_a_day_0_target_from_v_bar() -> None:
    e = rules.library("vol", 1, V_BAR)(R)
    size = min(1.0, 0.60 / np.sqrt(365 * V_BAR))
    assert e[0, 0] == (size if size >= 0.10 else 0.0)


def test_qj_shares_the_path_and_the_signs() -> None:
    """Both families' columns are s (e - e^b) r with one path and one sign
    sequence; the trend columns come first."""
    k, t, warmup = 2, 120, 250
    legs = semi.semi_empirical(R, rules.joint(k, V_BAR), np.random.default_rng(1),
                               np.random.default_rng(2), t, warmup)  # fmt: skip
    path = R[semi.stationary_indices(np.random.default_rng(1), len(R), t + warmup, 20)]
    e = np.hstack([rules.library(f, k, V_BAR)(path) for f in ("trend", "vol")])[warmup:]
    r = path[warmup:, 0]
    e_b = benchmark_exposure(path[:, 0])[warmup:]
    signs = semi.block_signs(np.random.default_rng(2), t, 20)
    np.testing.assert_array_equal(
        legs.x, signs[:, None] * (e - e_b[:, None]) * r[:, None]
    )
    assert legs.x.shape == (t, 2 * k)


@pytest.mark.parametrize(("family", "k"), [("trends", 2), ("vol", 0), ("vol", 28)])
def test_unknown_libraries_are_refused(family: str, k: int) -> None:
    with pytest.raises(ValueError):
        rules.library(family, k, V_BAR)
