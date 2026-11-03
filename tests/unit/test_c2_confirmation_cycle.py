"""R-14a confirmation module, slice 3: the Annex A orchestration (P18-0..7,
A-U1, A-B7, A-V1; DESIGN §2, §8). Synthetic data only."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any

import numpy as np
import pytest
import test_calibration_screen as ts  # the screen tests' trial fixture

from calibration import c2_confirmation as cf
from calibration import dsr, screen
from calibration.seeds import sha

FAMILY_SEED = hashlib.sha256(b"family").hexdigest()
W0 = datetime(2022, 1, 1, tzinfo=UTC)


@pytest.fixture(autouse=True)
def _v_runtime_checked(monkeypatch: pytest.MonkeyPatch) -> None:
    # the real run passes dsr.v_runtime_check on the pinned image at startup
    # (A-V1; loader slice); synthetic tests here only exercise the logic
    monkeypatch.setattr(dsr, "_V_VERIFIED", True)


def _trials(family: str, n: int) -> list[dict[str, Any]]:
    return [ts._trial(trial_id=f"t{i:03d}", family=family) for i in range(n)]


# --- P18-1 declared set --------------------------------------------------------


def test_declaration_rules() -> None:
    cf.check_declaration(
        {"trend": _trials("trend", 2), "vol": _trials("vol", 1)}, eligible=True
    )
    with pytest.raises(cf.CycleError, match="both families"):
        cf.check_declaration({"trend": _trials("trend", 2)}, eligible=True)
    with pytest.raises(cf.CycleError, match="not researched"):
        cf.check_declaration({"trend": _trials("trend", 1), "vol": []}, eligible=True)
    cf.check_declaration({"trend": _trials("trend", 1), "vol": []}, eligible=False)
    with pytest.raises(cf.CycleError, match="> 80"):
        cf.check_declaration(
            {"trend": _trials("trend", 81), "vol": _trials("vol", 1)}, True
        )
    dup = _trials("trend", 2)
    dup[1]["trial_id"] = "t000"
    with pytest.raises(cf.CycleError, match="duplicate"):
        cf.check_declaration({"trend": dup, "vol": _trials("vol", 1)}, eligible=True)
    with pytest.raises(cf.CycleError, match="is not a vol trial"):
        cf.check_declaration(
            {"trend": _trials("trend", 1), "vol": _trials("trend", 1)}, True
        )


# --- P18-0 (iii), A-B7 (v) -------------------------------------------------------


def test_eligibility_recomputed() -> None:
    last = W0 - timedelta(days=30)
    ok: dict[str, Any] = {"w0": W0, "t_days": 1200, "t_min": 365, "last_seen": last,
          "embargo_days": 30, "g_days": 30}  # fmt: skip
    cf.check_eligibility(**ok)
    with pytest.raises(cf.CycleError, match="bound g"):
        cf.check_eligibility(**{**ok, "embargo_days": 29})
    with pytest.raises(cf.CycleError, match="inside the embargo"):
        cf.check_eligibility(**{**ok, "last_seen": last + timedelta(seconds=1)})
    with pytest.raises(cf.CycleError, match="T_min"):
        cf.check_eligibility(**{**ok, "t_days": 364})


# --- A-U1 screen record ------------------------------------------------------------


def test_screen_record_must_match_set_object_and_outcome() -> None:
    trials = _trials("trend", 2)
    rec = {
        "trial_set_sha256": screen.trial_set_sha256(trials),
        "qualification_object_sha256": "a" * 64,
        "outcome": "SCREEN_AVAILABLE",
    }
    raw = json.dumps(rec).encode()
    digest = hashlib.sha256(raw).hexdigest()
    cf.check_screen_record(raw, digest, trials, "a" * 64)
    with pytest.raises(cf.CycleError, match="bytes"):
        cf.check_screen_record(raw, "b" * 64, trials, "a" * 64)
    with pytest.raises(cf.CycleError, match="trial set"):
        cf.check_screen_record(raw, digest, trials[:1], "a" * 64)
    with pytest.raises(cf.CycleError, match="qualification object"):
        cf.check_screen_record(raw, digest, trials, "c" * 64)
    bad = json.dumps({**rec, "outcome": "INVALID"}).encode()
    with pytest.raises(cf.CycleError, match="INVALID"):
        cf.check_screen_record(bad, hashlib.sha256(bad).hexdigest(), trials, "a" * 64)


# --- P18-1 re-run accounting ---------------------------------------------------------


CRASH = {"outcome": "failed", "reason_code": cf.CRASH}
DONE = {"outcome": "completed"}
PARTIAL = {"outcome": "failed", "reason_code": "PARTIAL_OUTPUT"}


def test_rerun_only_first_crash_while_the_slot_is_free() -> None:
    assert cf.trial_state([], None, "t1") == "unstarted"
    assert cf.trial_state([DONE], None, "t1") == "completed"
    assert cf.trial_state([CRASH], None, "t1") == "rerun"
    assert cf.trial_state([CRASH], "t9", "t1") == "final"  # slot already used
    assert cf.trial_state([PARTIAL], None, "t1") == "final"  # not a crash
    assert cf.trial_state([CRASH, DONE], "t1", "t1") == "completed"  # the re-run
    assert cf.trial_state([CRASH, CRASH], "t1", "t1") == "final"  # second crash
    with pytest.raises(cf.CycleError):
        cf.trial_state([DONE, DONE], None, "t1")


# --- P18-2 one look ----------------------------------------------------------------


def test_look_trigger() -> None:
    start = W0
    states = {"a": "completed", "b": "final"}
    assert cf.look_allowed(states, start, start + timedelta(days=1), False, False)
    running = {"a": "completed", "b": "rerun"}
    assert not cf.look_allowed(
        running, start, start + timedelta(days=179), False, False
    )
    assert cf.look_allowed(running, start, start + timedelta(days=180), False, False)
    with pytest.raises(cf.CycleError, match="no pick"):
        cf.look_allowed(states, start, start, True, False)
    with pytest.raises(cf.CycleError, match="already"):
        cf.look_allowed(states, start, start, False, True)


# --- P18-3, P18-4, A-V1 nomination ---------------------------------------------------


def _family(
    k: int = 3, t: int = 400
) -> tuple[dict[str, tuple[str, list[float]]], dict[str, str]]:
    rng = np.random.default_rng(11)
    cols = rng.normal(0.0005, 0.01, (t, k))
    cols[:, 1] += 0.002  # t001 clearly best
    completed = {f"t{j:03d}": (f"h{j}", cols[:, j].tolist()) for j in range(k)}
    return completed, {tid: h for tid, (h, _) in completed.items()}


def always(x: np.ndarray, lengths: list[float]) -> bool:
    return True


def test_nominee_is_the_best_trial_and_both_numerics_reported() -> None:
    completed, hashes = _family()
    n = cf.nominate(
        "trend", list(hashes), completed, hashes, FAMILY_SEED, "largest", always
    )
    assert (n.available, n.nominee) == (True, "t001")
    assert n.z == n.v.z and n.task12.reason is None  # A-V1: V governs, Task 12 reported
    assert n.x is not None and n.x.shape == (400, 3)


def test_tie_goes_to_the_lowest_declared_id_whatever_the_given_order() -> None:
    completed, hashes = _family()
    completed["t000"] = ("h0", completed["t001"][1])  # t000 ties t001 exactly
    n = cf.nominate("trend", ["t002", "t001", "t000"], completed, hashes, FAMILY_SEED,
                    "largest", always)  # fmt: skip
    assert n.nominee == "t000"


def test_unfinished_or_mismatched_trial_fails_the_family() -> None:
    completed, hashes = _family()
    missing = dict(completed)
    del missing["t002"]
    n = cf.nominate(
        "trend", list(hashes), missing, hashes, FAMILY_SEED, "largest", always
    )
    assert not n.available and "no completed evaluation" in str(n.reason)
    wrong = {**completed, "t002": ("other", completed["t002"][1])}
    n = cf.nominate(
        "trend", list(hashes), wrong, hashes, FAMILY_SEED, "largest", always
    )
    assert not n.available and "hash mismatch" in str(n.reason)


def test_classifier_is_required_and_can_refuse() -> None:
    completed, hashes = _family()
    with pytest.raises(cf.CycleError, match="classifier"):
        cf.nominate(
            "trend", list(hashes), completed, hashes, FAMILY_SEED, "largest", None
        )
    n = cf.nominate("trend", list(hashes), completed, hashes, FAMILY_SEED, "largest",
                    lambda x, lengths: False)  # fmt: skip
    assert (n.available, n.reason) == (False, "UNSUPPORTED_LAW")


def test_family_gates_use_the_nomination_matrix() -> None:
    completed, hashes = _family()
    n = cf.nominate(
        "trend", list(hashes), completed, hashes, FAMILY_SEED, "largest", always
    )
    g = cf.family_gates(n, "1.0", "a" * 64, "a" * 64)
    assert g["G-10"].result == cf.NA  # 3 trials < 20: frozen N/A
    assert g["G-13"].result == cf.PASS
    assert g["G-9"].result == (cf.PASS if n.z is not None and n.z >= 1.0 else cf.FAIL)


# --- P18-5, P18-7 ------------------------------------------------------------------


def test_cause_codes_and_no_fallback() -> None:
    assert cf.cause_code(cf.Gate(cf.UNAVAILABLE, "MISSING_DAY")) == "U_ops"
    assert cf.cause_code(cf.Gate(cf.UNAVAILABLE, "G-3:SIGMA_UNBOUND")) == "U_ops"
    assert (
        cf.cause_code(cf.Gate(cf.UNAVAILABLE, "INSUFFICIENT_SHIFT_RANGE")) == "U_proc"
    )
    assert cf.cause_code(cf.Gate(cf.PASS)) is None
    ok = {"G-1": cf.Gate(cf.PASS), "G-8": cf.Gate(cf.NA)}
    assert cf.nominee_outcome(ok) == "PROCEEDS_TO_LOCKBOX"
    assert cf.nominee_outcome({**ok, "G-2": cf.Gate(cf.FAIL)}) == "FAILED"
    assert (
        cf.nominee_outcome(
            {**ok, "G-2": cf.Gate(cf.FAIL), "G-4": cf.Gate(cf.UNAVAILABLE, "x")}
        )
        == "NO_RESULT"
    )


def test_r13_seeds_are_recorded_per_trial() -> None:
    got = cf.seeds_record(FAMILY_SEED, ["t000", "t001"])
    assert got["t001"] == sha({"family_seed": FAMILY_SEED, "trial_id": "t001"})
    assert len(set(got.values())) == 2
