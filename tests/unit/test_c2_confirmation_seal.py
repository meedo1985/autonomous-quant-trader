"""R-14a confirmation module, slice 5a: sealing (DESIGN §5.3, §5.5; Annex D
§D-1.7, §D-3.5; A7). The A4 generator copy must equal the lockbox module's
(Q-D1); a sealed artifact must pass the lockbox's own pre-read checks.
Synthetic data only (the screen tests' path and trial fixtures)."""

from __future__ import annotations

import hashlib
import inspect
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import test_calibration_screen as ts  # the screen tests' fixtures

from aqt.backtest.costs import (
    ewma_hourly_volatility_bps_series,
    hourly_log_returns_bps,
)
from aqt.backtest.event_contract import run_event_contract
from aqt.features.columns import feature_columns
from calibration import c2_confirmation as cf
from calibration import c2_lockbox as lb
from calibration import dsr, screen
from calibration.seeds import cj, sha

SHARED = ("LockboxError", "hexf", "_time", "window_id", "seed_material",
          "replicate_indices", "Forecast", "forecast", "_floats_sha256")  # fmt: skip
CONSTANTS = ("M_DAYS", "ATTEMPTS", "QUANTILE", "PURPOSE", "ASSET", "COST",
             "SEED_SOURCE")  # fmt: skip
CODE = {
    "lockbox_module_sha256": "1" * 64,
    "confirmation_module_sha256": "2" * 64,
    "engine_commit": "3" * 40,
    "screen_object_sha256": "4" * 64,
}
PROTOCOL = "5" * 64
FAMILY_SEED = "6" * 64
SEED_L266 = "7" * 64
EVAL = "8" * 64
WINDOW = cf.window_id(ts.W0, ts.W0 + timedelta(hours=ts.WINDOW_H))


# --- Q-D1: the A4 generator is the lockbox's, text for text -----------------


@pytest.mark.parametrize("name", SHARED)
def test_the_a4_copy_is_the_lockbox_source(name: str) -> None:
    assert inspect.getsource(getattr(cf, name)) == inspect.getsource(getattr(lb, name))


@pytest.mark.parametrize("name", CONSTANTS)
def test_the_a4_constants_are_the_lockbox_values(name: str) -> None:
    assert getattr(cf, name) == getattr(lb, name)


def test_the_a4_copy_gives_the_lockbox_reference_vectors() -> None:
    d = lb.reference_d()
    ours = cf.forecast(d, lb.REFERENCE_SEED_HEX, lb.REFERENCE_WINDOW)
    theirs = lb.forecast(d, lb.REFERENCE_SEED_HEX, lb.REFERENCE_WINDOW)
    assert (ours.psi, ours.block, ours.indices, ours.replicates, ours.q) == (
        theirs.psi, theirs.block, theirs.indices, theirs.replicates, theirs.q,
    )  # fmt: skip


# --- the prediction artifact --------------------------------------------------


def _nominee(trial_id: str = "t000") -> dict[str, Any]:
    return {
        "trial_id": trial_id,
        "configuration_hash": "9" * 64,
        "hypothesis_hash": "a" * 64,
        "protocol_hash": PROTOCOL,
        "trial_index": 3,
        "seed_l266": SEED_L266,
        "estimator_seed_policy": cf.POLICY,
        "estimator_seed": screen.estimator_seed(SEED_L266),
    }


def _artifact(**over: Any) -> dict[str, Any]:
    d = lb.reference_d()
    args: dict[str, Any] = {
        "cycle_id": "C2",
        "family": "trend",
        "nominee": _nominee(),
        "window": lb.REFERENCE_WINDOW,
        "d": d,
        "d_sha256": lb._floats_sha256(d),
        "evaluation_record_sha256": EVAL,
        "family_seed": FAMILY_SEED,
        "code": CODE,
    }
    args.update(over)
    return cf.prediction_artifact(**args)


def _lockbox_accepts(artifact: dict[str, Any], nominee: dict[str, Any]) -> None:
    request = lb.Request(
        cycle_id="C2", family="trend", nominee_trial_id=nominee["trial_id"],
        hypothesis_hash=nominee["hypothesis_hash"],
        configuration_hash=nominee["configuration_hash"],
        prediction_artifact_sha256=hashlib.sha256(cj(artifact)).hexdigest(),
        family_seed=FAMILY_SEED, seed_l266=nominee["seed_l266"],
        manifest_sha256="b" * 64, trial_index=nominee["trial_index"],
    )  # fmt: skip
    signed = lb.Signed(
        protocol_hash=PROTOCOL, image_digest="sha256:" + "c" * 64, **CODE
    )
    a = lb._check_shape(artifact)
    lb._check_identity(a, request, signed)
    lb._check_p4(a)


def test_a_sealed_artifact_passes_the_lockbox_pre_read_checks() -> None:
    artifact = _artifact()
    assert artifact["stream"]["seed_hex"] == sha(
        {"family_seed": FAMILY_SEED, "trial_id": "t000"}
    )  # R-13
    assert artifact["source"]["n"] == 120
    assert len(artifact["replicates_sorted"]) == 2000
    _lockbox_accepts(artifact, _nominee())


def test_d_must_hash_to_the_pre_look_d_sha256() -> None:
    with pytest.raises(cf.SealError, match="pre-look"):
        _artifact(d_sha256="0" * 64)


@pytest.mark.parametrize(
    "over",
    [
        {"nominee": {**_nominee(), "extra": 1}},
        {"code": {**CODE, "image_digest": "x"}},
        {"code": {k: v for k, v in CODE.items() if k != "engine_commit"}},
    ],
)
def test_artifact_fields_are_exact(over: dict[str, Any]) -> None:
    with pytest.raises(cf.SealError, match="fields"):
        _artifact(**over)


def test_a_short_source_is_refused_by_the_a4_generator() -> None:
    d = lb.reference_d()[:15]
    with pytest.raises(cf.LockboxError, match="INSUFFICIENT_OBSERVATIONS"):
        _artifact(d=d, d_sha256=lb._floats_sha256(d))


# --- the baseline re-run (A7 step 1) ------------------------------------------


def _independent_d(trial: dict[str, Any], path: np.ndarray) -> tuple[float, ...]:
    """The same pair through the frozen blocks, written out in the test."""
    warmup = trial["warmup_hours"]
    series = screen.path_series(path, 0, ts.W0 - timedelta(hours=warmup))
    first, columns = feature_columns(series)
    sigma = ewma_hourly_volatility_bps_series(hourly_log_returns_bps(series))
    closes = [b.close for b in series.bars]
    signal = screen.load(trial["signal"], trial["signal_sha256"])
    cand, _ = screen.leg_targets(
        trial, signal, None, columns, first, closes, warmup, ts.WINDOW_H, 0
    )
    bench = screen.benchmark_targets(columns, first, warmup, ts.WINDOW_H)
    c, b = (
        screen.daily_returns(run_event_contract(series, t, warmup, sigma_bps=sigma))
        for t in (cand, bench)
    )
    return tuple(x - y for x, y in zip(c, b, strict=True))


def test_baseline_d_is_the_daily_ediff_of_the_1x_btc_pair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = ts._screen_trial(tmp_path, monkeypatch)
    path = ts._screen_path()
    d = cf.baseline_d(trial, path, ts.W0, ts.WINDOW_H, 0)
    assert len(d) == ts.WINDOW_H // 24
    assert d == _independent_d(trial, path)
    assert any(x != 0 for x in d)
    with pytest.raises(cf.SealError, match="path length"):
        cf.baseline_d(trial, path[:-1], ts.W0, ts.WINDOW_H, 0)
    with pytest.raises(cf.SealError, match="estimator_seed"):
        cf.baseline_d(trial, path, ts.W0, ts.WINDOW_H, -1)


# --- statuses (a)-(d) and the sealing record (§D-1.7) ------------------------


def _nomination(available: bool, nominee: str | None = "t000") -> cf.Nomination:
    empty = dsr.FamilyResult("NOT_EVALUATED")
    return cf.Nomination(available, None if available else "U", nominee, None,
                         empty, empty)  # fmt: skip


def _seal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, outcome: str | None, **over: Any
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    trial = ts._screen_trial(tmp_path, monkeypatch)
    path = ts._screen_path()
    record = {
        "trial_id": "t000",
        "hypothesis_hash": "a" * 64,
        "configuration_hash": screen.trial_sha256(trial),
        "trial_index": 3,
    }
    seeds = {
        "families": {
            "trend": {
                "family_seed": FAMILY_SEED,
                "trials": {
                    "t000": {
                        "trial_index": 3,
                        "seed_l266": SEED_L266,
                        "estimator_seed_policy": cf.POLICY,
                        "estimator_seed": screen.estimator_seed(SEED_L266),
                    }
                },
            }
        }
    }
    d = cf.baseline_d(trial, path, ts.W0, ts.WINDOW_H, 0)
    args: dict[str, Any] = {
        "family": "trend",
        "nomination": _nomination(True),
        "outcome": outcome,
        "cycle_id": "C2",
        "protocol_hash": PROTOCOL,
        "seeds": seeds,
        "record": record,
        "trial": trial,
        "path": path,
        "w0": ts.W0,
        "window_hours": ts.WINDOW_H,
        "window": WINDOW,
        "d_sha256": cf._floats_sha256(d),
        "evaluation_record_sha256": EVAL,
        "code": CODE,
    }
    args.update(over)
    return cf.seal_family(**args)


def test_status_a_seals_an_eligible_nominee(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    entry, artifact = _seal(tmp_path, monkeypatch, "PROCEEDS_TO_LOCKBOX")
    assert artifact is not None and entry["status"] == "a"
    assert (
        entry["prediction_artifact_sha256"] == hashlib.sha256(cj(artifact)).hexdigest()
    )
    assert (entry["seed_l266"], entry["trial_index"]) == (SEED_L266, 3)
    nominee = artifact["nominee"]
    assert (nominee["trial_id"], nominee["protocol_hash"]) == ("t000", PROTOCOL)
    assert artifact["source"]["window_id"] == WINDOW
    assert artifact["source"]["d_sha256"] == cf._floats_sha256(
        cf.baseline_d(ts._screen_trial(tmp_path, monkeypatch), ts._screen_path(),
                      ts.W0, ts.WINDOW_H, 0)
    )  # fmt: skip
    _lockbox_accepts(artifact, nominee)


@pytest.mark.parametrize(
    ("outcome", "over", "status", "reason"),
    [
        (None, {"nomination": _nomination(False, None)}, "b", "U"),
        ("FAILED", {}, "c", "NOT_ELIGIBLE"),
        ("NO_RESULT", {}, "d", "GATE_UNAVAILABLE"),  # (d) governs over (c)
        ("PROCEEDS_TO_LOCKBOX", {"d_sha256": "0" * 64}, "d", "SEAL_FAILED:SealError"),
        ("PROCEEDS_TO_LOCKBOX", {"window": "w"}, "d", "SEAL_FAILED:SealError"),
        (
            "PROCEEDS_TO_LOCKBOX",
            {"nomination": _nomination(True, "t001")},
            "d",
            "SEAL_FAILED:SealError",
        ),
    ],
)
def test_statuses_b_c_d(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    outcome: str | None,
    over: dict[str, Any],
    status: str,
    reason: str,
) -> None:
    entry, artifact = _seal(tmp_path, monkeypatch, outcome, **over)
    assert (entry["status"], entry["reason"], artifact) == (status, reason, None)
    assert entry["prediction_artifact_sha256"] is None
    assert entry["seed_l266"] is None


def test_an_unknown_outcome_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(cf.CycleError, match="unknown nominee outcome"):
        _seal(tmp_path, monkeypatch, "MAYBE")


def test_the_sealing_record() -> None:
    entry = {"status": "b", "reason": "U"}
    rec = cf.sealing_record("C2", EVAL, 1_000_000, {"vol": entry, "trend": entry})
    assert rec["schema"] == "aqt.lockbox.sealing.v1"
    assert list(rec["families"]) == ["trend", "vol"]
    with pytest.raises(cf.CycleError, match="declared families"):
        cf.sealing_record("C2", EVAL, 1, {"other": entry})
    with pytest.raises(cf.CycleError, match="declared families"):
        cf.sealing_record("C2", EVAL, 1, {})
    with pytest.raises(cf.CycleError, match="status"):
        cf.sealing_record("C2", EVAL, 1, {"trend": {"status": "e"}})
