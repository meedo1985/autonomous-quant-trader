"""R-14a confirmation module, slice 2: the nominee's runs (DESIGN §5.2
step 6). The fixtures are the screen tests' synthetic paths and trials.
Synthetic data only."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import test_calibration_screen as ts  # the screen tests' fixtures

import aqt.metrics.statistics as st
from calibration import c2_confirmation as cf
from calibration import screen

SEED, WINDOW, G = ts.NULL_STREAM
SCREENED = ("G-3", "G-5", "G-6", "G-7", "G-8", "G-11", "G-14")
FLAT = "def s(row, params, state):\n    return 0.0\n"
NAN = "def s(row, params, state):\n    return float('nan')\n"


def _both(
    trial: dict[str, Any], path: Any, hours: int
) -> tuple[dict[str, Any], dict[str, cf.Gate]]:
    frozen = screen.screen_gates(trial, path, ts.W0, hours, SEED, WINDOW, G)
    ours = cf.nominee_gates(trial, path, ts.W0, hours, SEED, WINDOW, G, 0)
    return frozen, ours


def _agree(frozen: dict[str, Any], ours: dict[str, cf.Gate]) -> None:
    """UNAVAILABLE exactly when the screen gives a reason, with that reason;
    N/A exactly where it gives N/A; otherwise a PASS or FAIL decision."""
    for gate in SCREENED:
        f, o = frozen[gate], ours[gate]
        if f is None:
            assert o.result in (cf.PASS, cf.FAIL), gate
        elif f == screen.NA:
            assert o.result == cf.NA, gate
        else:
            assert (o.result, o.reason) == (cf.UNAVAILABLE, f), gate


@pytest.mark.parametrize(
    ("code", "change"),
    [
        (ts.TREND, {}),
        (FLAT, {}),
        (NAN, {}),
        (ts.PARAM_SIGNAL, {"parameter_point": {"k": 0}, "grid": {"k": [0, 5]}}),
        (ts.PARAM_SIGNAL, {"parameter_point": {"k": 5}, "grid": {"k": [0, 5, 10]}}),
        (ts.PARAM_SIGNAL, {"parameter_point": {"k": 10}, "grid": {"k": [5, 10]}}),
        (ts.TREND, {"g11_class": "constant_signal"}),
        (ts.TREND, {"sigma": "HAR_RV", "family": "vol"}),
    ],
)
def test_availability_agrees_with_the_frozen_screen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, code: str, change: dict[str, Any]
) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch, code, **change)
    frozen, ours = _both(trial, ts._screen_path(), ts.WINDOW_H)
    _agree(frozen, ours)
    assert set(ours) == set(cf.NOMINEE_GATES)


def test_g11_draws_every_shift_and_decides(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch)
    frozen, ours = _both(trial, ts._g11_path(), ts.WINDOW_G11_H)
    _agree(frozen, ours)
    g = ours["G-11"]
    want = screen.g11_shifts(SEED, WINDOW, ts.WINDOW_G11_H // 24, G)
    assert g.values["shifts_sha256"] == screen.g11_shifts_sha256(want)
    assert 0 <= g.values["below"] <= 500
    assert g.result == (cf.PASS if g.values["below"] >= 476 else cf.FAIL)


def test_g1_uses_the_r13_trial_seed_stream(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[st.ReplicateStream] = []
    got: list[st.PairedBootstrapInterval] = []
    real = st.paired_sharpe_improvement_interval

    def spy(*a: Any, stream: st.ReplicateStream) -> st.PairedBootstrapInterval:
        seen.append(stream)
        got.append(real(*a, stream=stream))
        return got[-1]

    monkeypatch.setattr(st, "paired_sharpe_improvement_interval", spy)
    trial = ts._screen_trial(tmp_path, monkeypatch)
    ours = cf.nominee_gates(
        trial, ts._screen_path(), ts.W0, ts.WINDOW_H, SEED, WINDOW, G, 0
    )
    assert ours["G-1"] == cf.g1(got[0])  # R14C-S-6: the decision on that interval
    (s,) = seen
    assert (
        s.trial_seed_hex,
        s.asset,
        s.cost_multiplier,
        s.evaluation_window_id,
        s.purpose,
    ) == (SEED, "BTCUSDT", "1.0", WINDOW, "paired_sharpe_ci")


def test_g4_and_g12_read_the_baseline_btc_series(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: dict[str, Any] = {}
    real_g4, real_g12 = cf.g4, cf.g12

    def g4(w0: Any, w1: Any, days: Any, cand: Any, bench: Any) -> cf.Gate:
        calls["g4"] = (w0, w1, days, cand, bench)
        return real_g4(w0, w1, days, cand, bench)

    def g12(returns: Any, horizon: int) -> cf.Gate:
        calls["g12"] = (returns, horizon)
        return real_g12(returns, horizon)

    monkeypatch.setattr(cf, "g4", g4)
    monkeypatch.setattr(cf, "g12", g12)
    trial = ts._screen_trial(tmp_path, monkeypatch)
    cf.nominee_gates(trial, ts._screen_path(), ts.W0, ts.WINDOW_H, SEED, WINDOW, G, 0)
    w0, w1, days, cand, bench = calls["g4"]
    assert (w0, len(days), days[0], days[-1]) == (ts.W0, 30, ts.W0, ts.W0 + 29 * cf.DAY)
    assert calls["g12"] == (cand, trial["horizon_hours"])
    assert len(cand) == len(bench) == 30


@pytest.mark.parametrize("case", ["pass", "fail", "unavailable"])
def test_g14_wires_the_nominee_and_500_seeded_draws(
    monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    """C-12 (5), (7): draw None is the nominee's own fit (its model_seed);
    draws d = 0..499 carry (trial_seed, window_id, d)."""
    draws: list[Any] = []

    def walk_forward(
        trial: Any,
        series: Any,
        first: Any,
        columns: Any,
        j0: int,
        n: int,
        lag: int,
        draw: Any = None,
        model_seed: int = 0,
    ) -> tuple[list[int], list[float]]:
        draws.append((draw, model_seed))
        rows = list(range(j0, j0 + n, 24))
        if draw is None and case == "pass":  # nominee tracks the target
            return rows, [float(i) for i in range(len(rows))]
        k = 1 if draw is None else draw[2] + 1  # "fail": nominee ranks like draw 0
        return rows, [float((-1) ** i * k) for i in range(len(rows))]

    monkeypatch.setattr(screen, "walk_forward", walk_forward)

    def labels(series: Any, sigma: Any, rows: Any, h: int) -> list[float]:
        if case == "unavailable":
            raise screen.RunUnavailable("NONFINITE_LABEL")
        return [float(i) for i in range(len(rows))]

    monkeypatch.setattr(screen, "labels", labels)
    series = ts._series("BTCUSDT", list(range(48 + 24 * 40)), 1.0)
    trial = {"horizon_hours": 24}
    g = cf._g14(
        trial,
        lambda s: (series, 0, {}),
        series.bars[48].open_time,
        48,
        24 * 40,
        SEED,
        WINDOW,
        7,
    )
    assert draws[0] == (None, 7)
    if case == "unavailable":
        assert (g.result, g.reason) == (cf.UNAVAILABLE, "NONFINITE_LABEL")
        return
    assert [d for d, _ in draws[1:]] == [(SEED, WINDOW, d) for d in range(500)]
    if case == "pass":
        assert (g.result, g.values["below"]) == (cf.PASS, 500)
    else:
        assert g.result == cf.FAIL and g.values["below"] < 476
