"""R-14a lockbox module, slice 1 (DESIGN §6.2, §7.1, §8; Annex D §D-3.8).
Synthetic data only."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import UTC, datetime, timedelta

import pytest

import aqt.metrics.statistics as st
from aqt.backtest.event_contract import EventContractError, EventResult
from aqt.data.bars import Bar, BarSeries
from aqt.metrics.descriptive import _max_drawdown
from calibration import c2_lockbox as lb
from calibration.seeds import cj

SEED = hashlib.sha256(b"test-seed").hexdigest()
WINDOW = lb.window_id(
    datetime(2022, 1, 1, tzinfo=UTC), datetime(2022, 3, 1, tzinfo=UTC)
)
H = timedelta(hours=1)


# --- A4 generator ------------------------------------------------------------


def test_seed_material_is_the_production_layout_with_lockbox_purpose() -> None:
    stream = st.ReplicateStream(
        SEED, st.CONVENTION_DOCUMENT_SHA256, "BTCUSDT", "1.0", WINDOW
    )
    frozen = json.loads(
        st.replicate_seed_material(stream, output_length=457, replicate_index=7)
    )
    ours = json.loads(lb.seed_material(SEED, WINDOW, 7))
    assert ours == [*frozen[:3], "lockbox_prediction", *frozen[4:]]
    assert ours[7] == 457


def test_draw_order_matches_bootstrap_indices(monkeypatch: pytest.MonkeyPatch) -> None:
    # with n = m = 457 and the frozen seed material, the two generators coincide
    stream = st.ReplicateStream(
        SEED, st.CONVENTION_DOCUMENT_SHA256, "BTCUSDT", "1.0", WINDOW
    )
    monkeypatch.setattr(
        lb,
        "seed_material",
        lambda s, w, r: st.replicate_seed_material(
            stream, output_length=457, replicate_index=r
        ),
    )
    for r, block in ((0, 1.0), (3, 6.5), (1999, 457.0)):
        assert lb.replicate_indices(
            SEED, WINDOW, 457, block, r
        ) == st.bootstrap_indices(
            stream, observations=457, replicate_index=r, block=block
        )


def test_indices_are_457_over_n() -> None:
    idx = lb.replicate_indices(SEED, WINDOW, 40, 4.0, 0)
    assert len(idx) == 457 and all(0 <= i < 40 for i in idx)
    with pytest.raises(lb.LockboxError):
        lb.replicate_indices(SEED, WINDOW, 40, 41.0, 0)
    with pytest.raises(lb.LockboxError):
        lb.seed_material(SEED, WINDOW, 2000)


def test_forecast_and_refusals() -> None:
    d = lb.reference_d()[:60]
    f = lb.forecast(d, SEED, WINDOW)
    assert len(f.replicates) == 2000 and len(f.indices) == 2000
    assert f.q == st.type_seven_quantile(f.replicates, 0.05)
    assert f.replicates[5] == st.sharpe([d[i] for i in f.indices[5]]).scaled
    with pytest.raises(lb.LockboxError, match="INSUFFICIENT_OBSERVATIONS"):
        lb.forecast(d[:15], SEED, WINDOW)
    with pytest.raises(lb.LockboxError, match="ZERO_VARIANCE"):
        lb.forecast([0.01] * 30, SEED, WINDOW)


# --- A5 reference vectors and startup --------------------------------------


def test_reference_vectors_reproduce_and_startup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    got = lb.vectors_sha256()
    assert got == lb.vectors_sha256()
    v = lb.reference_vectors()
    assert v["block"]["degenerate"] is False and v["block"]["reason"] is None
    assert len(v["first_indices"]["0"]) == 10
    assert lb.startup_result() == (got, "REFERENCE_VECTOR_MISMATCH")  # not frozen
    monkeypatch.setattr(lb, "FROZEN_VECTORS_SHA256", got)
    assert lb.startup_result() == (got, "PASS")
    monkeypatch.setattr(lb, "FROZEN_VECTORS_SHA256", "0" * 64)
    assert lb.startup_result()[1] == "REFERENCE_VECTOR_MISMATCH"


# --- A6 adapter --------------------------------------------------------------

START = datetime(2024, 1, 1, tzinfo=UTC)
DAYS = 3


def _series(symbol: str = "BTCUSDT", hours: int = 24 * DAYS + 1, warm: int = 2,
            gap: int | None = None, interval: timedelta = H) -> BarSeries:  # fmt: skip
    times = [START + (i - warm) * interval for i in range(hours + warm)]
    if gap is not None:
        del times[warm + gap]
    return BarSeries(
        symbol,
        tuple(Bar(t, 100.0, 101.0, 99.0, 100.0, 1.0, interval) for t in times),
        interval,
    )


def _result(equity: list[float] | None = None, start: int = 2) -> EventResult:
    eq = equity or [1.0 + 0.001 * math.sin(i) for i in range(24 * DAYS)]
    return EventResult(start, tuple(0.5 for _ in eq), tuple(eq), (), 0)


def test_adapter_valid() -> None:
    s = _series()
    c, b = _result(), _result([1.0] * 24 * DAYS)
    legs = lb.adapt(s, c, s, b, "BTCUSDT", START, DAYS)
    assert len(legs.candidate) == DAYS == len(legs.benchmark)
    assert legs.mdd_candidate == _max_drawdown((1.0, *c.equity))  # bit-equal


@pytest.mark.parametrize(
    "case",
    ["asset", "series", "start", "interval", "gap", "length", "short", "instant"],
)
def test_adapter_refusals(case: str) -> None:
    s, c, b = _series(), _result(), _result()
    other_s = s
    asset, start = "BTCUSDT", START
    if case == "asset":
        asset = "ETHUSDT"
    elif case == "series":  # identical timestamps, lengths, starts; other prices
        other_s = BarSeries(
            "BTCUSDT",
            tuple(Bar(x.open_time, 50.0, 51.0, 49.0, 50.0, 1.0) for x in s.bars),
        )
    elif case == "start":
        b = _result(start=3)
    elif case == "interval":
        s = other_s = _series(interval=2 * H)
    elif case == "gap":
        s = other_s = _series(gap=30)
    elif case == "length":
        c = b = _result([1.0] * (24 * DAYS - 1))
    elif case == "short":
        s = other_s = _series(hours=24 * DAYS)  # no terminal bar
    elif case == "instant":
        start = START + H
    with pytest.raises(lb.LockboxError, match="DAYS_INCOMPLETE"):
        lb.adapt(s, c, other_s, b, asset, start, DAYS)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), 0.0, -1.0])
def test_adapter_equity(bad: float) -> None:
    s = _series()
    eq = [1.0] * (24 * DAYS)
    eq[10] = bad
    with pytest.raises(lb.LockboxError, match="NONFINITE_EQUITY"):
        lb.adapt(s, _result(eq), s, _result(), "BTCUSDT", START, DAYS)


def test_run_error_mapping() -> None:
    def raise_(e: Exception) -> lb.Legs:
        raise e

    assert (
        lb.run_legs(lambda: raise_(lb.LockboxError("DAYS_INCOMPLETE")))
        == "DAYS_INCOMPLETE"
    )
    assert (
        lb.run_legs(lambda: raise_(EventContractError("equity after bar 4 is nan")))
        == "NONFINITE_EQUITY"
    )
    assert (
        lb.run_legs(
            lambda: raise_(EventContractError("fill at 3 would consume all equity"))
        )
        == "NONFINITE_EQUITY"
    )
    assert (
        lb.run_legs(lambda: raise_(EventContractError("delay must be one of")))
        == "RUN_FAILED"
    )
    assert lb.run_legs(lambda: raise_(RuntimeError("x"))) == "RUN_FAILED"


# --- B4.2 bundles ------------------------------------------------------------


def _label(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


CAPTURE = {
    "engine_commit": "eeaa7282e3b7c87790c162d679016c290d5f4ea5",
    "image_digest": "sha256:" + _label("example-image"),
    "input_manifest_sha256": _label("example-input-manifest"),
    "lockbox_module_sha256": _label("example-lockbox-module"),
    "prediction_artifact_sha256": _label("example-prediction-artifact"),
}
PASS_VALUES = {
    "eth_e_improv": "3fc70a3d70a3d70a",
    "mdd_btc_bench": "3fceb851eb851eb8",
    "mdd_btc_cand": "3fcae147ae147ae1",
    "mdd_eth_bench": "3fd51eb851eb851f",
    "mdd_eth_cand": "3fd3333333333333",
    "q": "bfe7645a1cac0831",
    "t_l": "3fda5e353f7ced91",
}


def _values(**over: str | None) -> dict[str, float | None]:
    raw = {**PASS_VALUES, **over}
    return {k: None if x is None else lb.unhexf(x) for k, x in raw.items()}


def test_pass_fixture_byte_exact() -> None:
    upside = {"exceeds_p95": False, "k": 1275, "reason": None, "status": "COMPUTED"}
    bundle = lb.assemble("C2/trend/1", _values(), [], upside, CAPTURE)
    bundle["operational"] = {
        "read_start": "2026-12-01T00:00:05Z",
        "sealed_at": "2026-12-01T03:10:00Z",
        "startup_check_id": "C2/startup/1",
    }
    raw = cj(bundle)
    assert len(raw) == 1053
    assert hashlib.sha256(raw).hexdigest() == (
        "d64d228b84a1aaf6015a6860af7f69f2315cc77865e0afad4547822ab54ba520"
    )


def test_rev4_eth_rows() -> None:
    up = lb.upside(None, [])
    false_null = lb.assemble(
        "C2/trend/1", _values(eth_e_improv="bfb999999999999a", mdd_eth_cand=None),
        ["ETH_MDD:NONFINITE_RESULT"], up, CAPTURE,
    )  # fmt: skip
    assert false_null["conditions"] == {"L1": True, "L2": True, "L3": True, "L4": False}
    assert (false_null["result"], false_null["cause_class"]) == ("FAIL", "PERFORMANCE")
    true_null = lb.assemble(
        "C2/trend/1",
        _values(mdd_eth_cand=None),
        ["ETH_MDD:NONFINITE_RESULT"],
        up,
        CAPTURE,
    )
    assert true_null["conditions"]["L4"] is None
    assert (true_null["result"], true_null["cause_class"]) == ("FAIL", "TECHNICAL")
    assert true_null["values"]["mdd_eth_cand"] is None


def test_precedence_and_reasons() -> None:
    up = lb.upside(None, [])
    v = _values(t_l=None, mdd_btc_cand=lb.hexf(0.9))  # L3 false, L1/L2 null
    b = lb.assemble(
        "x",
        v,
        ["RUN:RUN_FAILED", "BTC_EDIFF:ZERO_VARIANCE", "RUN:RUN_FAILED"],
        up,
        CAPTURE,
    )
    assert (b["result"], b["cause_class"]) == ("FAIL", "PERFORMANCE")
    assert b["reasons"] == ["BTC_EDIFF:ZERO_VARIANCE", "RUN:RUN_FAILED"]
    with pytest.raises(lb.LockboxError):
        lb.assemble("x", v, ["BTC:OOPS"], up, CAPTURE)
    neg_zero = lb.assemble("x", _values(t_l=lb.hexf(-0.0)), [], up, CAPTURE)
    assert neg_zero["conditions"]["L2"] is False


def test_upside_counts_strictly_below() -> None:
    reps = sorted([0.1 * i for i in range(2000)])
    u = lb.upside(reps[10], reps)
    assert u["status"] == "COMPUTED" and u["k"] == 10 and u["exceeds_p95"] is False
    assert lb.upside(1e9, reps)["exceeds_p95"] is True
    assert lb.upside(None, reps)["reason"] == "T_L_UNAVAILABLE"


def _legs(seed: float) -> lb.Legs:
    c = tuple(0.01 * math.sin(seed + i) + 0.002 for i in range(457))
    b = tuple(0.008 * math.cos(seed + 2 * i) for i in range(457))
    return lb.Legs(c, b, 0.10, 0.12)


def test_btc_and_eth_independent() -> None:
    reps = sorted(0.001 * i - 1 for i in range(2000))
    eth_failed = lb.evaluate("x", _legs(0.0), "RUN_FAILED", -1.0, reps, CAPTURE)
    assert eth_failed["values"]["t_l"] is not None
    assert (
        eth_failed["conditions"]["L4"] is None
        and "RUN:RUN_FAILED" in eth_failed["reasons"]
    )
    btc_failed = lb.evaluate("x", "DAYS_INCOMPLETE", _legs(1.0), -1.0, reps, CAPTURE)
    assert btc_failed["values"]["eth_e_improv"] is not None
    assert btc_failed["conditions"]["L1"] is None
    assert btc_failed["upside"]["status"] == "NOT_COMPUTED"
    with pytest.raises(lb.LockboxError):
        lb.evaluate("x", _legs(0.0), _legs(1.0), -1.0, reps, {"engine_commit": "x"})


def test_t_l_is_ediff_of_btc_legs() -> None:
    legs = _legs(0.3)
    b = lb.evaluate("x", legs, _legs(1.0), -1.0, [0.0] * 2000, CAPTURE)
    d = [x - y for x, y in zip(legs.candidate, legs.benchmark, strict=True)]
    assert lb.unhexf(b["values"]["t_l"]) == st.sharpe(d).scaled
