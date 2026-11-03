"""R-14a lockbox module, slice 3a: the lockbox run, read and computed twice
(DESIGN §6.4, §7.1; Annex D §D-1.8 items 3-6, §D-3.3). Synthetic data only."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from aqt.data.bars import Bar, BarSeries
from calibration import c2_lockbox as lb
from calibration import screen

# a trend rule; a constant 1.0 at tau 0.60 would equal the benchmark (d = 0)
SIGNAL = (
    b"def s(row, params, state):\n    return 1.0 if row['ema_dist_72'] > 0 else 0.0\n"
)
BROKEN = b"def s(row, params, state):\n    return row['missing']\n"
CAPTURE = {k: hashlib.sha256(k.encode()).hexdigest() for k in lb.CAPTURE_KEYS}
REPS = sorted(-1.0 + 0.001 * i for i in range(2000))


def _bars(symbol: str, seed: int, drop: int | None = None) -> BarSeries:
    rng = np.random.default_rng(seed)
    closes = 100.0 * np.exp(np.cumsum(rng.normal(0.00002, 0.004, lb.READ_HOURS)))
    opens = np.concatenate([[100.0], closes[:-1]])
    bars = [
        Bar(lb.S_PRE + i * lb.HOUR, o, max(o, c) * 1.001, min(o, c) * 0.999, c, 1.0)
        for i, (o, c) in enumerate(zip(opens, closes, strict=True))
        if i != drop
    ]
    return BarSeries(symbol, tuple(bars))


@pytest.fixture(scope="module")
def market() -> tuple[BarSeries, BarSeries]:
    return _bars("BTCUSDT", 1), _bars("ETHUSDT", 2)


@pytest.fixture
def code(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Callable[..., dict[str, Any]]:
    monkeypatch.syspath_prepend(str(tmp_path))

    def trial(
        source: bytes = SIGNAL, name: str = "lb_signal", **change: Any
    ) -> dict[str, Any]:
        (tmp_path / f"{name}.py").write_bytes(source)
        t: dict[str, Any] = {
            "trial_id": "t007",
            "family": "trend",
            "signal": f"{name}:s",
            "signal_sha256": hashlib.sha256(source).hexdigest(),
            "overlay": None,
            "overlay_sha256": None,
            "s_inputs": ["ema_dist_72", "rv_168"],
            "tau": "0.60",
            "sigma": "EWMA_168h",
            "g11_class": "signal_timed",
            "model": None,
            "horizon_hours": 72,
            "parameter_point": {"span": 72},
            "grid": {"span": [24, 72, 168]},
            "warmup_hours": 4800,
        }
        t.update(change)
        return t

    return trial


def _run(trial: dict[str, Any], read: Callable[[], tuple[BarSeries, BarSeries]],
         twice: bool = False) -> dict[str, Any]:  # fmt: skip
    f = lb.compute_twice if twice else lb.compute
    return f("C2/trend/1", trial, 12345, read, -0.5, REPS, CAPTURE)


def test_rule_based_run_twice(
    market: tuple[BarSeries, BarSeries], code: Callable[..., dict[str, Any]]
) -> None:
    calls = []

    def read() -> tuple[BarSeries, BarSeries]:
        calls.append(1)
        return market

    b = _run(code(), read, twice=True)
    assert len(calls) == 2  # read and computed twice
    assert b["reasons"] == []
    assert all(b["values"][k] is not None for k in lb.VALUE_KEYS)
    assert all(c is not None for c in b["conditions"].values())
    assert b["upside"]["status"] == "COMPUTED"


def test_legs_cover_exactly_the_lockbox_days(
    market: tuple[BarSeries, BarSeries], code: Callable[..., dict[str, Any]]
) -> None:
    legs = lb.run_asset(code(), market[0], 0, 12345)
    assert len(legs.candidate) == lb.M_DAYS == len(legs.benchmark)


def test_btc_gap_fails_btc_only(
    market: tuple[BarSeries, BarSeries], code: Callable[..., dict[str, Any]]
) -> None:
    gapped = _bars("BTCUSDT", 1, drop=lb.WARMUP_HOURS + 100)
    b = _run(code(), lambda: (gapped, market[1]))
    # a missing BTC hour refuses the BTC run only; never filled (§D-3.3)
    assert b["reasons"] == ["RUN:DAYS_INCOMPLETE"]
    assert b["values"]["t_l"] is None and b["values"]["mdd_btc_cand"] is None
    assert b["values"]["eth_e_improv"] is not None
    assert b["conditions"]["L1"] is None and b["conditions"]["L4"] is not None


def test_eth_gap_fails_eth_only(
    market: tuple[BarSeries, BarSeries], code: Callable[..., dict[str, Any]]
) -> None:
    gapped = _bars("ETHUSDT", 2, drop=5)  # in the warm-up history
    b = _run(code(), lambda: (market[0], gapped))
    assert b["reasons"] == ["RUN:DAYS_INCOMPLETE"]
    assert b["values"]["t_l"] is not None and b["values"]["eth_e_improv"] is None
    assert b["conditions"]["L4"] is None


def test_wrong_range_and_asset_refused(
    market: tuple[BarSeries, BarSeries], code: Callable[..., dict[str, Any]]
) -> None:
    short = BarSeries("BTCUSDT", market[0].bars[1:])
    assert "RUN:DAYS_INCOMPLETE" in _run(code(), lambda: (short, market[1]))["reasons"]
    swapped = _run(code(), lambda: (market[1], market[0]))
    assert swapped["reasons"] == ["RUN:DAYS_INCOMPLETE"]  # both assets wrong
    assert swapped["values"]["t_l"] is None
    assert swapped["values"]["eth_e_improv"] is None


def test_trial_code_error_is_run_failed(
    market: tuple[BarSeries, BarSeries], code: Callable[..., dict[str, Any]]
) -> None:
    b = _run(code(BROKEN, "lb_broken"), lambda: market)
    assert b["reasons"] == ["RUN:RUN_FAILED"]
    assert (b["result"], b["cause_class"]) == ("FAIL", "TECHNICAL")


def test_nondeterministic_read_is_technical(
    market: tuple[BarSeries, BarSeries], code: Callable[..., dict[str, Any]]
) -> None:
    other = (_bars("BTCUSDT", 9), market[1])
    reads = iter([market, other])
    b = _run(code(), lambda: next(reads), twice=True)
    assert b["reasons"] == ["RUN:RUN_FAILED"]
    assert b["values"]["q"] is not None and b["values"]["t_l"] is None


def test_model_trial_refits_with_estimator_seed(
    market: tuple[BarSeries, BarSeries],
    code: Callable[..., dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # R14L-S-7: a spy at the frozen model-construction boundary
    seeds: list[int] = []
    build = screen.build_model

    def spy(cls: str, params: Any, seed: int) -> Any:
        seeds.append(seed)
        return build(cls, params, seed=seed)

    monkeypatch.setattr(screen, "build_model", spy)
    model = {
        "id": "m1",
        "class": "ridge",
        "params": {"alpha": "1.0"},
        "target": "vol_scaled_target",
        "features": ["ret_24h"],
    }
    source = (
        b"def s(row, params, state):\n    return 1.0 if row['model:m1'] > 0 else 0.0\n"
    )
    t = code(
        source,
        "lb_model_signal",
        model=model,
        s_inputs=["model:m1", "ret_24h"],
        warmup_hours=screen.MODEL_WARMUP_HOURS,
    )
    b = _run(t, lambda: market)
    assert b["reasons"] == [] and b["values"]["t_l"] is not None
    # 16 refits (k = 0..15) per asset, every one with the estimator seed
    assert len(seeds) == 2 * 16 and set(seeds) == {12345}


def test_bad_estimator_seed_refused(code: Callable[..., dict[str, Any]]) -> None:
    def read() -> tuple[BarSeries, BarSeries]:
        raise AssertionError("no read after a refused seed")

    with pytest.raises(lb.LockboxError):
        lb.compute("x", code(), -1, read, 0.0, REPS, CAPTURE)
