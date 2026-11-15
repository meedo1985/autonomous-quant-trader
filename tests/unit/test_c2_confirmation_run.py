"""R-14a confirmation module, slice 6b part 1: the confirmation read contract
(DESIGN §7.2 C-T; DESIGN_SLICE6B.md 6B-3) and the per-trial pre-look record
(6B-4). Synthetic data only (the screen tests' path and trial fixtures)."""

from __future__ import annotations

import dataclasses
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import test_calibration_screen as ts  # the screen tests' fixtures

from aqt.backtest.costs import CostModelError
from aqt.backtest.event_contract import EventContractError
from aqt.features.factory import FeatureFactoryError
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


# §3 identity fields as `result_identity` gives them (synthetic values)
IDENTITY: dict[str, Any] = {
    "trial_index": 0, "seed_l266": "5" * 64, "estimator_seed": 0,
    "data_manifest_sha256": "6" * 64, "protocol_hash": "7" * 64,
    "engine_commit": "8" * 40, "confirmation_module_sha256": "9" * 64,
    "image_digest": "sha256:" + "a" * 64,
}  # fmt: skip
WINDOW = (ts.W0, ts.WINDOW_H // 24)  # the governing (w0, T)


def _result(trial: dict[str, Any], **over: Any) -> dict[str, Any]:
    args: dict[str, Any] = {
        "cycle_id": "C2",
        "trial": trial,
        "record": _record(trial),
        "attempt_id": "a1",
        "path": ts._screen_path(),
        "w0": ts.W0,
        "window_hours": ts.WINDOW_H,
        "identity": IDENTITY,
    }
    return cf.trial_result(**{**args, **over})


def test_the_pre_look_record_is_the_baseline_e_diff_and_its_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch)
    got = _result(trial)
    d = cf.baseline_d(trial, ts._screen_path(), ts.W0, ts.WINDOW_H, 0)
    assert got["schema"] == "aqt.c2.trial_result.v2"
    assert {k: got[k] for k in cf.IDENTITY_KEYS} == IDENTITY
    assert got["d"] == [cf.hexf(x) for x in d]
    assert got["d_sha256"] == cf._floats_sha256(d)  # LG5-3, A7 step 2
    assert got["window_id"] == cf.window_id(ts.W0, ts.W0 + timedelta(hours=ts.WINDOW_H))
    assert got["days"][0] == "2022-01-01T00:00:00Z" and len(got["days"]) == 30
    assert (got["reason"], got["configuration_hash"]) == (None, _record(trial)[
        "configuration_hash"])  # fmt: skip
    # nominate's input, decoded and re-checked
    h, days, values, reason = cf.completed_entry(got, WINDOW)
    assert (h, reason) == (got["configuration_hash"], None)
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
    assert cf.completed_entry(got, WINDOW)[2:] == ([], reason)  # §5: by reason


def test_a_caller_input_error_is_not_unavailability(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch)
    with pytest.raises(cf.SealError, match="estimator_seed"):
        _result(trial, identity={**IDENTITY, "estimator_seed": -1})


def test_a_d_that_does_not_match_its_own_hash_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # internal consistency only: a d moved with its hash under another trial is
    # not caught here (R14S6-F-3, R14D6B-S-2: binding comes with rev 2)
    got = _result(ts._screen_trial(tmp_path, monkeypatch))
    got["d"][0] = cf.hexf(1.0)
    with pytest.raises(cf.CycleError, match="d_sha256"):
        cf.completed_entry(got, WINDOW)
    with pytest.raises(cf.CycleError, match="pre-look"):
        cf.completed_entry({**got, "schema": "other"}, WINDOW)


# --- R14S6-F-2: completed_entry decodes exactly -------------------------------------


def _bad(got: dict[str, Any], case: str) -> Any:
    bad = {**got, "d": list(got["d"]), "days": list(got["days"])}
    if case == "upper_hex":
        bad["d"][0] = bad["d"][0].upper()
    elif case == "spaced_hex":
        bad["d"][0] = bad["d"][0][:8] + " " + bad["d"][0][8:15]
    elif case == "short_hex":
        bad["d"][0] = bad["d"][0][:14]
    elif case == "loose_day":
        bad["days"][0] = "2022-1-1T0:0:0Z"
    elif case == "nan":
        bad["d"][0] = cf.hexf(float("nan"))
        bad["d_sha256"] = cf._floats_sha256([float("nan"), *(
            cf.completed_entry(got, WINDOW)[2][1:])])  # fmt: skip
    elif case == "null_d_with_hash":
        bad.update(d=None, reason=None)
    elif case == "d_with_reason":
        bad["reason"] = "TRIAL_CODE_ERROR"
    elif case == "missing_field":
        del bad["cycle_id"]
    elif case == "extra_field":
        bad["note"] = "x"
    elif case == "window_mismatch":
        bad["window_id"] = cf.window_id(ts.W0 + H, ts.W0 + H + cf.DAY)
    elif case == "d_length":  # hash re-made: only the length is wrong
        bad["d"] = bad["d"][:-1]
        bad["d_sha256"] = cf._floats_sha256(cf.completed_entry(got, WINDOW)[2][:-1])
    elif case == "null_d_hash_and_reason":  # only the stray hash is wrong
        bad.update(d=None, reason="TRIAL_CODE_ERROR")
    elif case == "upper_config_hash":
        bad["configuration_hash"] = bad["configuration_hash"].upper()
    elif case == "repeated_day":  # canonical strings, ends unchanged
        bad["days"][1] = bad["days"][2]
    elif case == "empty_id":
        bad["cycle_id"] = ""
    elif case == "empty_days":
        bad["days"] = []
    elif case == "last_day_overflows":
        bad["days"] = ["9999-12-31T00:00:00Z"]
    elif case == "wrong_type":
        bad["d"] = "00"
    elif case == "not_a_dict":
        return [got]
    return bad


# R14S6R-F-2: each case names the clause that must refuse it
@pytest.mark.parametrize(("case", "match"), [
    ("upper_hex", "one canonical float64"), ("spaced_hex", "one canonical float64"),
    ("short_hex", "one canonical float64"), ("loose_day", "canonical consecutive"),
    ("nan", "not finite"), ("null_d_with_hash", "needs a reason"),
    ("null_d_hash_and_reason", "needs a reason"), ("d_with_reason", "no reason"),
    ("missing_field", "fields are not"), ("extra_field", "fields are not"),
    ("window_mismatch", "window_id"), ("d_length", "one canonical float64"),
    ("wrong_type", "no reason"), ("not_a_dict", "not a pre-look"),
    ("upper_config_hash", "configuration_hash"), ("repeated_day", "consecutive"),
    ("empty_id", "cycle_id"), ("empty_days", "non-empty list"),
    ("last_day_overflows", "not a UTC time"),
])  # fmt: skip
def test_a_malformed_pre_look_record_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, case: str, match: str
) -> None:
    got = _result(ts._screen_trial(tmp_path, monkeypatch))
    with pytest.raises(cf.CycleError, match=match):
        cf.completed_entry(_bad(got, case), WINDOW)


def test_an_unavailable_run_without_a_reason_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch)

    def failing(*_: object) -> None:
        raise screen.RunUnavailable("TRIAL_CODE_ERROR")

    monkeypatch.setattr(cf, "baseline_d", failing)
    got = _result(trial)
    with pytest.raises(cf.CycleError, match="reason"):
        cf.completed_entry({**got, "reason": ""}, WINDOW)


# --- R14S6-F-6, F-7: trial_path and the read contract's untested branches -----------


def test_a_w0_off_the_hour_is_refused_not_floored() -> None:
    _, _, rows, start = _read(4801)
    with pytest.raises(cf.CycleError, match="on the hour"):
        cf.trial_path(rows, start, ts.W0 + timedelta(minutes=30), 4000, ts.WINDOW_H)
    with pytest.raises(cf.CycleError, match="whole hours"):
        cf.trial_path(rows, start, ts.W0, 4000.0, ts.WINDOW_H)  # type: ignore[arg-type]


def test_a_gap_inside_a_series_of_the_right_length_is_refused() -> None:
    # duplicates cannot reach here (BarSeries refuses them at construction);
    # a gap with one extra bar at the end keeps the length right
    btc, eth, rows, start = _read()
    end = start + len(rows) * H
    k = 100
    later = btc.bars[k:]
    shifted = tuple(dataclasses.replace(b, open_time=b.open_time + H) for b in later)
    gapped = dataclasses.replace(btc, bars=btc.bars[:k] + shifted)
    with pytest.raises(cf.CycleError, match="not at its hour"):
        cf.check_confirmation_read(gapped, eth, start, end)


def test_a_series_of_another_interval_is_refused() -> None:
    btc, eth, rows, start = _read()
    end = start + len(rows) * H
    object.__setattr__(btc, "interval", 2 * H)  # a series claiming another interval
    with pytest.raises(cf.CycleError, match="hourly"):
        cf.check_confirmation_read(btc, eth, start, end)


def test_an_ohlcv_rule_breach_from_confirmation_path_is_a_c_t_refusal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    btc, eth, rows, start = _read()
    end = start + len(rows) * H

    def breach(_: object) -> None:
        raise screen.TrialError("high below low")

    monkeypatch.setattr(screen, "confirmation_path", breach)
    with pytest.raises(cf.CycleError, match="C-T: high below low"):
        cf.check_confirmation_read(btc, eth, start, end)


@pytest.mark.parametrize("error", [CostModelError("x"), FeatureFactoryError("x")])
def test_cost_and_feature_errors_are_recorded_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch)

    def failing(*_: object) -> None:
        raise error

    monkeypatch.setattr(cf, "baseline_d", failing)
    got = _result(trial)
    assert (got["d"], got["reason"]) == (None, type(error).__name__)
    assert cf.completed_entry(got, WINDOW)[2:] == ([], type(error).__name__)


def test_trial_path_refuses_a_bad_window_or_a_naive_w0() -> None:
    # R14S6R-F-4
    _, _, rows, start = _read(4801)
    for window in (-1, 0, True, 50.0):
        with pytest.raises(cf.CycleError, match="whole hours"):
            cf.trial_path(rows, start, ts.W0, 4000, window)  # type: ignore[arg-type]
    with pytest.raises(cf.CycleError, match="naive"):
        cf.trial_path(rows, start, ts.W0.replace(tzinfo=None), 4000, ts.WINDOW_H)


def test_trial_result_never_writes_a_record_the_look_refuses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # R14S6R-F-5: an empty cycle id is refused when written, not at the look
    with pytest.raises(cf.CycleError, match="cycle_id"):
        _result(ts._screen_trial(tmp_path, monkeypatch), cycle_id="")


# --- DESIGN_SLICE6B §3, §13: result entry v2 and completed_entry against the window --


def test_result_identity_takes_this_processs_own_values() -> None:
    started = cf.Started(
        protocol_hash="7" * 64, lockbox_module_sha256="b" * 64,
        confirmation_module_sha256="9" * 64, engine_commit="8" * 40,
        screen_object_sha256="c" * 64, image_digest="sha256:" + "a" * 64,
        protocol=b"", declaration=b"", declaration_sha256="d" * 64, chain_log={},
    )  # fmt: skip
    seeds = {"trial_index": 0, "trial_seed": "x", "seed_l266": "5" * 64,
             "estimator_seed_policy": cf.POLICY, "estimator_seed": 0}  # fmt: skip
    assert cf.result_identity(started, seeds, "6" * 64) == IDENTITY


@pytest.mark.parametrize(("key", "value"), [
    ("trial_index", "0"), ("trial_index", True), ("seed_l266", "5" * 63),
    ("estimator_seed", 2**31), ("estimator_seed", -1), ("estimator_seed", 0.0),
    ("data_manifest_sha256", "6" * 63), ("protocol_hash", "G" * 64),
    ("confirmation_module_sha256", None), ("engine_commit", "8" * 64),
    ("image_digest", ""), ("image_digest", 1),
])  # fmt: skip
def test_malformed_identity_fields_are_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, key: str, value: Any
) -> None:
    got = _result(ts._screen_trial(tmp_path, monkeypatch))
    with pytest.raises(cf.CycleError, match="identity fields"):
        cf.completed_entry({**got, key: value}, WINDOW)


def test_trial_result_needs_exactly_the_identity_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch)
    short = {k: v for k, v in IDENTITY.items() if k != "image_digest"}
    with pytest.raises(cf.CycleError, match="identity fields"):
        _result(trial, identity=short)


def test_window_id_is_checked_against_the_governing_window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    got = _result(ts._screen_trial(tmp_path, monkeypatch))
    with pytest.raises(cf.CycleError, match="governing window"):
        cf.completed_entry(got, (ts.W0 + cf.DAY, WINDOW[1]))
    with pytest.raises(cf.CycleError, match="governing window"):
        cf.completed_entry(got, (ts.W0, WINDOW[1] + 1))


def test_well_formed_shifted_days_pass_for_nominate_to_judge(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """§3 rule 2: days differing from the window are MISALIGNED_SERIES at
    `nominate`, not a refusal; their window_id is still the governing one."""
    got = _result(ts._screen_trial(tmp_path, monkeypatch))
    shifted = [cf._time(ts.W0 + (k + 1) * cf.DAY) for k in range(len(got["days"]))]
    _, days, values, _ = cf.completed_entry({**got, "days": shifted}, WINDOW)
    assert days[0] == ts.W0 + cf.DAY and len(values) == len(days)
