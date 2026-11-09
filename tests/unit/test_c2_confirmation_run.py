"""R-14a confirmation module, slice 6b part 1: the confirmation read contract
(DESIGN §7.2 C-T; DESIGN_SLICE6B.md 6B-3) and the per-trial pre-look record
(6B-4). Synthetic data only (the screen tests' path and trial fixtures)."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import test_calibration_screen as ts  # the screen tests' fixtures

from aqt.backtest.event_contract import EventContractError
from calibration import c2_confirmation as cf
from calibration import screen

H = timedelta(hours=1)


def _read(warmup: int = 4801) -> tuple[Any, Any, Any, Any]:
    """BTC and ETH series over [w0 - warmup, w1) from the screen fixture."""
    path = ts._screen_path(warmup)
    rows = path[:-1]  # the read never includes the bar at w1
    start = ts.W0 - timedelta(hours=warmup)
    return (screen.path_series(rows, 0, start), screen.path_series(rows, 1, start),
            rows, start)  # fmt: skip


# --- 6B-3: the read contract -------------------------------------------------------


def test_a_valid_read_gives_exactly_the_served_rows() -> None:
    btc, eth, rows, start = _read()
    end = ts.W0 + timedelta(hours=ts.WINDOW_H)
    got = cf.check_confirmation_read(btc, eth, start, end)
    assert got.shape == (4801 + ts.WINDOW_H, 2, 5)
    np.testing.assert_array_equal(got, rows)


@pytest.mark.parametrize("breakage", ["swapped", "short", "late_start", "eth_shifted"])
def test_a_read_off_the_contract_is_refused(breakage: str) -> None:
    btc, eth, rows, start = _read()
    end = ts.W0 + timedelta(hours=ts.WINDOW_H)
    if breakage == "swapped":
        btc, eth = eth, btc
    elif breakage == "short":
        btc = screen.path_series(rows[1:], 0, start + H)
    elif breakage == "late_start":
        start += H
    else:  # same length, one hour later: not on identical times
        eth = screen.path_series(rows, 1, start + H)
    with pytest.raises(cf.CycleError, match="C-T"):
        cf.check_confirmation_read(btc, eth, start, end)


def test_an_object_that_is_not_a_bar_series_is_refused() -> None:
    # Bar refuses bad OHLC at construction; only a BarSeries is accepted, and
    # confirmation_path re-checks the OHLC rules on the joint rows
    btc, eth, rows, start = _read()
    end = start + len(rows) * H
    with pytest.raises(cf.CycleError, match="C-T"):
        cf.check_confirmation_read(list(btc.bars), eth, start, end)  # type: ignore[arg-type]


def test_the_span_must_be_whole_hours() -> None:
    btc, eth, _, start = _read()
    with pytest.raises(cf.CycleError, match="whole hours"):
        cf.check_confirmation_read(btc, eth, start, start - H)


def test_each_trial_takes_its_own_warm_up_from_the_read() -> None:
    _, _, rows, start = _read(4801)
    path = cf.trial_path(rows, start, ts.W0, 4000, ts.WINDOW_H)
    np.testing.assert_array_equal(path, screen.confirmation_path(rows[801:]))
    assert len(path) == 4000 + ts.WINDOW_H + 1
    with pytest.raises(cf.CycleError, match="does not cover"):
        cf.trial_path(rows, start, ts.W0, 4802, ts.WINDOW_H)
    with pytest.raises(cf.CycleError, match="does not cover"):
        cf.trial_path(rows[:-1], start, ts.W0, 4000, ts.WINDOW_H)  # w1 not reached


# --- 6B-4: the pre-look record -----------------------------------------------------


def _record(trial: dict[str, Any]) -> dict[str, Any]:
    return {"trial_id": trial["trial_id"],
            "configuration_hash": screen.trial_sha256(trial)}  # fmt: skip


def _result(trial: dict[str, Any], **over: Any) -> dict[str, Any]:
    args: dict[str, Any] = {
        "cycle_id": "C2",
        "trial": trial,
        "record": _record(trial),
        "attempt_id": "a1",
        "path": ts._screen_path(),
        "w0": ts.W0,
        "window_hours": ts.WINDOW_H,
        "estimator_seed": 0,
    }
    return cf.trial_result(**{**args, **over})


def test_the_pre_look_record_is_the_baseline_e_diff_and_its_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch)
    got = _result(trial)
    d = cf.baseline_d(trial, ts._screen_path(), ts.W0, ts.WINDOW_H, 0)
    assert got["schema"] == "aqt.c2.trial_result.v1"
    assert got["d"] == [cf.hexf(x) for x in d]
    assert got["d_sha256"] == cf._floats_sha256(d)  # LG5-3, A7 step 2
    assert got["window_id"] == cf.window_id(ts.W0, ts.W0 + timedelta(hours=ts.WINDOW_H))
    assert got["days"][0] == "2022-01-01T00:00:00Z" and len(got["days"]) == 30
    assert (got["reason"], got["configuration_hash"]) == (None, _record(trial)[
        "configuration_hash"])  # fmt: skip
    # nominate's input, decoded and re-checked
    h, days, values = cf.completed_entry(got)
    assert h == got["configuration_hash"]
    assert days == [ts.W0 + k * cf.DAY for k in range(30)]
    assert tuple(values) == d


def test_a_trial_off_its_record_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch)
    with pytest.raises(cf.CycleError, match="immutable record"):
        _result(trial, record={**_record(trial), "configuration_hash": "0" * 64})
    with pytest.raises(cf.CycleError, match="immutable record"):
        _result(trial, record={**_record(trial), "trial_id": "t999"})


@pytest.mark.parametrize(
    ("error", "reason"),
    [
        (screen.RunUnavailable("TRIAL_CODE_ERROR"), "TRIAL_CODE_ERROR"),
        (EventContractError("x"), "EventContractError"),
        (cf.SealError("DAYS_INCOMPLETE"), "DAYS_INCOMPLETE"),
    ],
)
def test_an_unavailable_run_is_recorded_not_dropped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, error: Exception, reason: str
) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch)

    def failing(*_: object) -> None:
        raise error

    monkeypatch.setattr(cf, "baseline_d", failing)
    got = _result(trial)
    assert (got["d"], got["d_sha256"], got["reason"]) == (None, None, reason)
    assert cf.completed_entry(got)[2] == []  # nominate: MISALIGNED_SERIES, U_ops


def test_a_caller_input_error_is_not_unavailability(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch)
    with pytest.raises(cf.SealError, match="estimator_seed"):
        _result(trial, estimator_seed=-1)


def test_a_tampered_pre_look_d_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    got = _result(ts._screen_trial(tmp_path, monkeypatch))
    got["d"][0] = cf.hexf(1.0)
    with pytest.raises(cf.CycleError, match="d_sha256"):
        cf.completed_entry(got)
    with pytest.raises(cf.CycleError, match="pre-look"):
        cf.completed_entry({**got, "schema": "other"})
