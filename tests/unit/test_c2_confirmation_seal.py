"""R-14a confirmation module, slice 5a: sealing (DESIGN §5.3, §5.5; Annex D
§D-1.7, §D-3.5; A7). The A4 generator copy must equal the lockbox module's
(Q-D1); a sealed artifact must pass the lockbox's own pre-read checks.
Synthetic data only (the screen tests' path and trial fixtures)."""

from __future__ import annotations

import functools
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


@pytest.mark.parametrize(
    ("part", "key", "value"),
    [
        ("source", "n", -1),
        ("source", "n", True),
        ("source", "d_sha256", "bad"),
        ("source", "evaluation_record_sha256", "A" * 64),
        ("source", "window_id", 7),
        ("block", "value", "bad"),
        ("block", "value", cf.hexf(0.5)),  # a block length below 1
        ("block", "value", cf.hexf(float("inf"))),
        ("block", "raw", "bad"),
        ("block", "psi_sha256", "0" * 63),
        ("block", "clipping", "SIDEWAYS"),
    ],
)
def test_the_lockbox_refuses_bad_source_and_block_values(
    part: str, key: str, value: object
) -> None:
    # R14S5-S-3: values are checked before any read, not only the keys
    artifact = _artifact()
    artifact[part] = {**artifact[part], key: value}
    with pytest.raises(lb._Refused, match="PREDICTION_ARTIFACT_INVALID"):
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


def _independent_d(
    trial: dict[str, Any], path: np.ndarray, seed: int = 0
) -> tuple[float, ...]:
    """The same pair through the frozen blocks, written out in the test: the
    walk-forward model column at the registered seed, the overlay fresh."""
    warmup = trial["warmup_hours"]
    series = screen.path_series(path, 0, ts.W0 - timedelta(hours=warmup))
    first, columns = feature_columns(series)
    if trial["model"] is not None:
        _, preds = screen.walk_forward(trial, series, first, columns, warmup,
                                       ts.WINDOW_H, 0, None, seed)  # fmt: skip
        col = [float("nan")] * len(columns["rv_168"])
        for i, y in enumerate(preds):  # one emission per day, held 24 hours
            for h in range(24):
                col[warmup + 24 * i + h - 1 - first] = y
        columns = {**columns, "model:m": tuple(col)}
    sigma = ewma_hourly_volatility_bps_series(hourly_log_returns_bps(series))
    closes = [b.close for b in series.bars]
    signal = screen.load(trial["signal"], trial["signal_sha256"])
    overlay = (
        None if trial["overlay"] is None
        else screen.load(trial["overlay"], trial["overlay_sha256"])
    )  # fmt: skip
    cand, _ = screen.leg_targets(
        trial, signal, overlay, columns, first, closes, warmup, ts.WINDOW_H, 0
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


OVERLAY = (
    "def o(t, m, state):\n"
    "    state['n'] = state.get('n', 0) + 1\n"
    "    return 0.0 if state['n'] % 48 < 12 else t\n"
)


def test_baseline_d_runs_the_registered_model_and_overlay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # R14S5-S-4: a model nominee with an overlay at a nonzero registered seed;
    # the model fits use that seed and dropping the overlay changes d
    digest = ts._module(tmp_path, monkeypatch, "seal_overlay", OVERLAY)
    trial = ts._model_trial(tmp_path, monkeypatch, overlay="seal_overlay:o",
                            overlay_sha256=digest)  # fmt: skip
    seeds: list[int] = []
    real = screen.build_model

    def build(cls: str, params: Any, seed: int) -> Any:
        seeds.append(seed)
        return real(cls, params, seed)

    monkeypatch.setattr(screen, "build_model", build)
    path = ts._long_path()
    d = cf.baseline_d(trial, path, ts.W0, ts.WINDOW_H, 12345)
    assert seeds and set(seeds) == {12345}
    assert d == _independent_d(trial, path, 12345)
    plain = {**trial, "overlay": None, "overlay_sha256": None}
    assert d != cf.baseline_d(plain, path, ts.W0, ts.WINDOW_H, 12345)


# --- statuses (a)-(d) and the sealing record (§D-1.7) ------------------------


def _nomination(available: bool, nominee: str | None = "t000") -> cf.Nomination:
    empty = dsr.FamilyResult("NOT_EVALUATED")
    return cf.Nomination(available, None if available else "U", nominee, None,
                         empty, empty)  # fmt: skip


@pytest.fixture(autouse=True)
def _line266_loaded() -> None:
    cf.load_line266()  # as the loader does before any protected read


@functools.cache
def _l266() -> str:
    assert cf._TRIAL_SEED is not None
    return cf._TRIAL_SEED(protocol_hash=PROTOCOL, hypothesis_hash="a" * 64,
                          trial_index=3)  # fmt: skip


def _seal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    outcome: str | None,
    seed_over: dict[str, Any] | None = None,
    **over: Any,
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
                        "seed_l266": _l266(),
                        "estimator_seed_policy": cf.POLICY,
                        "estimator_seed": screen.estimator_seed(_l266()),
                        **(seed_over or {}),
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
    assert (entry["seed_l266"], entry["trial_index"]) == (_l266(), 3)
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


@pytest.mark.parametrize(
    "seed_over",
    [
        {"trial_index": 4},
        {"seed_l266": "7" * 64},
        {"estimator_seed_policy": "OTHER"},
        {"estimator_seed": "plus_one"},
        {"estimator_seed": True},
    ],
)
def test_seeds_off_the_record_or_line_266_give_status_d(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, seed_over: dict[str, Any]
) -> None:
    # R14S5-S-1: an artifact the lockbox would refuse is never status (a)
    if seed_over.get("estimator_seed") == "plus_one":
        seed_over = {"estimator_seed": screen.estimator_seed(_l266()) + 1}
    entry, artifact = _seal(tmp_path, monkeypatch, "PROCEEDS_TO_LOCKBOX", seed_over)
    assert (entry["status"], entry["reason"], artifact) == (
        "d", "SEAL_FAILED:SealError", None
    )  # fmt: skip


def test_without_line_266_loaded_sealing_gives_status_d(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seed = _l266()
    seeds = {"families": {"trend": {"family_seed": FAMILY_SEED, "trials": {
        "t000": {"trial_index": 3, "seed_l266": seed,
                 "estimator_seed_policy": cf.POLICY,
                 "estimator_seed": screen.estimator_seed(seed)}}}}}  # fmt: skip
    monkeypatch.setattr(cf, "_TRIAL_SEED", None)
    entry, _ = _seal(tmp_path, monkeypatch, "PROCEEDS_TO_LOCKBOX", seeds=seeds)
    assert (entry["status"], entry["reason"]) == ("d", "SEAL_FAILED:SealError")


def test_a_seed_record_without_the_family_invalidates_the_evaluation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # R14S5-S-5: a seed-derivation failure, not a sealing failure
    with pytest.raises(cf.CycleError, match="no family seed"):
        _seal(tmp_path, monkeypatch, "FAILED", family="vol")
    with pytest.raises(cf.CycleError, match="no family seed"):
        _seal(tmp_path, monkeypatch, "FAILED", seeds={})


def test_an_unknown_outcome_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(cf.CycleError, match="unknown nominee outcome"):
        _seal(tmp_path, monkeypatch, "MAYBE")


def test_the_sealing_record() -> None:
    entry = {"status": "b", "reason": "U"}
    both = ("trend", "vol")
    rec = cf.sealing_record("C2", EVAL, 1_000_000, {"vol": entry, "trend": entry},
                            both)  # fmt: skip
    assert rec["schema"] == "aqt.lockbox.sealing.v1"
    assert list(rec["families"]) == ["trend", "vol"]
    one = cf.sealing_record("C2", EVAL, 1, {"vol": entry}, ("vol",))
    assert list(one["families"]) == ["vol"]
    # R14S5-S-2: a declared family missing from the record is refused
    for entries, declared in (
        ({"trend": entry}, both),
        ({"other": entry}, ("other",)),
        ({}, both),
        ({"trend": entry, "vol": entry}, ("trend",)),
        ({}, ()),
    ):
        with pytest.raises(cf.CycleError, match="declared families"):
            cf.sealing_record("C2", EVAL, 1, entries, declared)
    with pytest.raises(cf.CycleError, match="status"):
        cf.sealing_record("C2", EVAL, 1, {"trend": {"status": "e"}}, ("trend",))
