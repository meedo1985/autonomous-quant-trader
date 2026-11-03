"""R-14a confirmation module, slice 1: gate decisions (Annex C C-1..C-12;
DESIGN §8 "per gate: a PASS, a FAIL and an UNAVAILABLE case"). Synthetic
data only."""

from __future__ import annotations

import ast
import math
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

import aqt.metrics.statistics as st
from calibration import c2_confirmation as cf
from calibration import gates

W0 = datetime(2022, 1, 1, tzinfo=UTC)
DAY = timedelta(days=1)


def _stats(e: float = 0.5, dd: float = 0.0, net: float = 0.1) -> dict[str, float]:
    return {"e_improv": e, "dd_excess": dd, "net_return": net}


def _interval(
    reason: str | None = None, lower: float | None = 0.1
) -> st.PairedBootstrapInterval:
    stream = st.ReplicateStream(
        "0" * 64, st.CONVENTION_DOCUMENT_SHA256, "BTCUSDT", "1.0", gates.WINDOW
    )
    return st.PairedBootstrapInterval(
        100, stream, st.BlockLength(100), "py", reason=reason, lower=lower, upper=1.0
    )


def test_r14a_item3_the_two_modules_never_import_each_other() -> None:
    root = Path(cf.__file__).parent
    for name, other in (
        ("c2_confirmation", "c2_lockbox"),
        ("c2_lockbox", "c2_confirmation"),
    ):
        tree = ast.parse((root / f"{name}.py").read_text(encoding="utf-8"))
        imported = {
            a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names
        }
        imported |= {
            f"{n.module}.{a.name}"
            for n in ast.walk(tree)
            if isinstance(n, ast.ImportFrom)
            for a in n.names
        }
        assert not any(other in i for i in imported), name


# --- G-1 .. G-3, G-5..G-7 ----------------------------------------------------


def test_g1() -> None:
    assert cf.g1(_interval(lower=0.1)).result == cf.PASS
    assert cf.g1(_interval(lower=0.0)).result == cf.FAIL  # strictly > 0
    u = cf.g1(_interval(reason="INSUFFICIENT_OBSERVATIONS", lower=None))
    assert (u.result, u.reason) == (cf.UNAVAILABLE, "INSUFFICIENT_OBSERVATIONS")


def test_dd_condition_is_absolute_and_inclusive() -> None:
    assert cf.g2(_stats(dd=0.05)).result == cf.PASS
    assert cf.g2(_stats(dd=math.nextafter(0.05, 1))).result == cf.FAIL
    assert cf.g2("RUN_INVALID") == cf.Gate(cf.UNAVAILABLE, "RUN_INVALID", {})


def test_g3_negative_finite_eth_improvement_fails() -> None:  # Astra's example
    assert cf.g3(_stats(e=-1e-9)).result == cf.FAIL
    assert cf.g3(_stats(e=0.0)).result == cf.FAIL
    assert cf.g3(_stats(e=0.2, dd=0.06)).result == cf.FAIL
    assert cf.g3(_stats(e=0.2)).result == cf.PASS
    assert cf.g3(_stats(e=math.nan)).result == cf.UNAVAILABLE


@pytest.mark.parametrize(
    ("btc", "expected"),
    [
        (_stats(), cf.PASS),
        (_stats(e=0.0), cf.FAIL),
        (_stats(net=0.0), cf.FAIL),
        (_stats(dd=0.051), cf.FAIL),
        ("RUN_INVALID", cf.UNAVAILABLE),
    ],
)
def test_survival(btc: cf.Stats, expected: str) -> None:
    assert cf.survival(btc, cf.g3(_stats())).result == expected


def test_survival_needs_g3() -> None:
    assert cf.survival(_stats(), cf.g3(_stats(e=-1.0))).result == cf.FAIL
    u = cf.survival(_stats(), cf.g3("FEATURES_UNAVAILABLE"))
    assert (u.result, u.reason) == (cf.UNAVAILABLE, "G-3:FEATURES_UNAVAILABLE")


# --- G-4 ---------------------------------------------------------------------


def test_g4_boundaries_from_w0_clipped_never_chained() -> None:
    b = cf.g4_boundaries(
        datetime(2022, 11, 30, tzinfo=UTC), datetime(2023, 9, 1, tzinfo=UTC)
    )
    # Feb 28 is clipped; May 30 comes from w0, not from the clipped Feb 28
    assert [x.date().isoformat() for x in b] == [
        "2022-11-30", "2023-02-28", "2023-05-30", "2023-08-30",
    ]  # fmt: skip


def _days(w1: datetime) -> list[datetime]:
    return [W0 + k * DAY for k in range((w1 - W0) // DAY)]


def _legs(days: list[datetime], wins: set[int]) -> tuple[list[float], list[float]]:
    bounds = cf.g4_boundaries(W0, days[-1] + DAY)
    cand, bench = [], []
    for k, d in enumerate(days):
        block = sum(b <= d for b in bounds[1:])
        sign = 1.0 if block in wins else -1.0
        cand.append(0.001 * sign + 0.002 * (-1) ** k)
        bench.append(0.002 * (-1) ** (k + 1))
    return cand, bench


def test_g4_rate() -> None:
    w1 = datetime(2023, 4, 1, tzinfo=UTC)  # 5 complete blocks, no partial
    days = _days(w1)
    n = len(cf.g4_boundaries(W0, w1)) - 1
    assert n == 5
    cand, bench = _legs(days, set(range(math.ceil(0.6 * n))))
    g = cf.g4(W0, w1, days, cand, bench)
    assert g.result == cf.PASS and g.values["n"] == n
    cand, bench = _legs(days, set(range(math.ceil(0.6 * n) - 1)))
    assert cf.g4(W0, w1, days, cand, bench).result == cf.FAIL


def test_g4_zero_variance_block_is_not_a_win_and_partial_block_reported() -> None:
    w1 = datetime(2022, 8, 15, tzinfo=UTC)  # 2 complete blocks + partial
    days = _days(w1)
    cand, bench = _legs(days, {0, 1})
    for i, d in enumerate(days):
        if d < datetime(2022, 4, 1, tzinfo=UTC):
            cand[i] = 0.01  # block 0 candidate constant
    g = cf.g4(W0, w1, days, cand, bench)
    assert [b["win"] for b in g.values["blocks"]] == [False, True]
    assert g.result == cf.FAIL  # 1/2 < 0.60
    assert isinstance(g.values["partial_block_e_improv"], float)


def test_g4_exactly_zero_improvement_is_not_a_win() -> None:
    w1 = datetime(2022, 7, 1, tzinfo=UTC)  # 2 complete blocks
    days = _days(w1)
    cand, bench = _legs(days, {0, 1})
    bench = list(cand)  # identical legs: E-IMPROV exactly 0 in every block
    g = cf.g4(W0, w1, days, cand, bench)
    assert [b["e_improv"] for b in g.values["blocks"]] == [0.0, 0.0]
    assert (g.result, g.values["wins"]) == (cf.FAIL, 0)


@pytest.mark.parametrize("damage", ["missing", "duplicate", "nonfinite"])
def test_g4_integrity(damage: str) -> None:
    w1 = datetime(2022, 7, 1, tzinfo=UTC)
    days = _days(w1)
    cand, bench = _legs(days, {0, 1})
    if damage == "missing":
        del days[40], cand[40], bench[40]
    elif damage == "duplicate":
        days[41] = days[40]
    else:
        cand[40] = math.inf
    assert cf.g4(W0, w1, days, cand, bench).result == cf.UNAVAILABLE


def test_g4_no_complete_block() -> None:
    w1 = datetime(2022, 3, 1, tzinfo=UTC)
    days = _days(w1)
    g = cf.g4(W0, w1, days, *_legs(days, set()))
    assert (g.result, g.reason) == (cf.UNAVAILABLE, "NO_COMPLETE_BLOCK")


# --- G-8 ---------------------------------------------------------------------


def _trial(point: int) -> dict[str, object]:
    return {"grid": {"tau": ["0.40"], "lookback": [10, 20, 30]},
            "parameter_point": {"tau": "0.40", "lookback": point}}  # fmt: skip


def test_g8() -> None:
    inner = _trial(20)
    assert cf.g8(inner, 1.0, [0.5, 0.6]).result == cf.PASS  # median 0.55 >= 0.5
    assert cf.g8(inner, 1.0, [0.2, 0.7]).result == cf.FAIL  # median 0.45
    assert cf.g8(_trial(30), 1.0, [0.9]).result == cf.FAIL  # boundary
    assert cf.g8(inner, 0.0, [0.5, 0.6]).result == cf.FAIL  # v <= 0
    assert cf.g8(inner, 1.0, [None, 0.6]).result == cf.UNAVAILABLE
    assert (
        cf.g8({"grid": {"tau": ["0.40"]}, "parameter_point": {}}, None, []).result
        == cf.NA
    )


# --- G-10 --------------------------------------------------------------------


def _ranked_matrix(iid: bool) -> np.ndarray:
    """Clean: every row is the same alternating noise plus a level rising
    with the trial, so every half ranks the trials alike (phi = 0). iid: pure
    noise, so the IS-best is a coin flip OOS (phi near 0.5)."""
    rng = np.random.default_rng(7)
    t, k = 32, 20
    if iid:
        return np.asarray(rng.normal(0, 1e-2, (t, k)), dtype=float)
    wiggle = np.where(np.arange(t) % 2 == 0, 1e-2, -1e-2)[:, None]
    return np.asarray(wiggle + np.arange(1, k + 1) * 1e-4, dtype=float)


def test_pbo_na_unavailable_and_pass() -> None:
    assert cf.pbo(np.zeros((40, 19))).result == cf.NA
    assert cf.pbo(np.ones((15, 20))).reason == "INSUFFICIENT_OBSERVATIONS"
    assert cf.pbo(np.ones((32, 20))).reason == "NO_SHARPE_ON_HALF"
    g = cf.pbo(_ranked_matrix(iid=False))
    assert (g.result, g.values["splits"]) == (cf.PASS, 12870) and g.values["phi"] == 0.0


def test_pbo_exact_tie_averages_over_tied_trials() -> None:
    # identical columns: every trial ties IS-best and has OOS midrank (N+1)/2,
    # so each tied score is 0.5 (logit = 0) and phi is exactly 0.5
    x = np.repeat(_ranked_matrix(iid=True)[:, :1], 20, axis=1)
    g = cf.pbo(x)
    assert (g.result, g.values["phi"]) == (cf.FAIL, 0.5)


def test_pbo_fail() -> None:
    g = cf.pbo(_ranked_matrix(iid=True))
    assert g.result == cf.FAIL and g.values["phi"] > cf.PBO_LIMIT


# --- G-11, G-14 --------------------------------------------------------------


def test_null_rule() -> None:
    draws: list[float | None] = [*[0.0] * 476, *[2.0] * 24]
    assert cf.null_rule(1.0, draws).result == cf.PASS
    assert (
        cf.null_rule(1.0, [0.0] * 475 + [1.0] * 25).result == cf.FAIL
    )  # ties not below
    assert cf.null_rule(1.0, [1.0] * 500).result == cf.FAIL  # 500 tied (Astra)
    assert cf.null_rule(1.0, [None, *draws[1:]]).result == cf.UNAVAILABLE
    assert cf.null_rule(1.0, draws[:499]).reason == "DRAW_COUNT"


# --- G-12, G-9, G-13 ---------------------------------------------------------


def test_g12() -> None:
    rng = np.random.default_rng(3)
    assert cf.g12(rng.normal(0, 1, 400).tolist(), 24).result == cf.PASS
    assert cf.g12(rng.normal(0, 1, 100).tolist(), 24).result == cf.FAIL
    assert cf.g12([0.0, 1.0], 48).reason == "INVALID_HORIZON"
    assert cf.g12([0.0], 24).result == cf.UNAVAILABLE


def test_g9_and_g13() -> None:
    assert cf.g9(2.0, "2.0").result == cf.PASS
    assert cf.g9(math.nextafter(2.0, 0), "2.0").result == cf.FAIL
    assert cf.g9(None, "2.0").result == cf.UNAVAILABLE
    assert cf.g13("a" * 64, "a" * 64).result == cf.PASS
    assert cf.g13("a" * 64, "b" * 64).result == cf.FAIL
