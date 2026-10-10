"""D-19 Q5/QJ rule libraries (proposal revision 3, accepted 2026-10-11).
Synthetic returns only."""

from __future__ import annotations

import itertools

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
    for bad in (-1.0, np.nan):
        source = R.copy()
        source[5, 0] = bad
        with pytest.raises(ValueError):
            rules.reference_variance(source)


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
