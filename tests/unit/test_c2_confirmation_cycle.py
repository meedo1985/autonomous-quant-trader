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

from aqt.core import attempts
from aqt.core.ledger import read_entries
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
    cf.check_declaration(
        {"trend": _trials("trend", 20), "vol": _trials("vol", 1)}, True
    )
    with pytest.raises(
        cf.CycleError, match="21 trials > 20"
    ):  # owner decision R14C-S-5
        cf.check_declaration(
            {"trend": _trials("trend", 21), "vol": _trials("vol", 1)}, True
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
    """R14C-S-3: w0 is derived as partition start + g; T from the window end."""
    start = W0 - timedelta(days=30)
    end = W0 + timedelta(days=365)
    ok: dict[str, Any] = {"partition_start": start, "window_end": end, "t_min": 365,
          "last_seen": start, "embargo_days": 30, "g_days": 30}  # fmt: skip
    assert cf.check_eligibility(**ok) == (W0, 365)
    with pytest.raises(cf.CycleError, match="bound g"):
        cf.check_eligibility(**{**ok, "embargo_days": 29})
    with pytest.raises(cf.CycleError, match="inside the embargo"):
        cf.check_eligibility(**{**ok, "last_seen": start + timedelta(seconds=1)})
    with pytest.raises(cf.CycleError, match="day boundary"):
        cf.check_eligibility(**{**ok, "window_end": end - timedelta(hours=1)})
    with pytest.raises(cf.CycleError, match="T_min"):  # 364 complete days
        cf.check_eligibility(**{**ok, "window_end": end - timedelta(days=1)})
    with pytest.raises(cf.CycleError, match="day boundary"):
        cf.check_eligibility(**{**ok, "partition_start": start + timedelta(hours=1)})
    with pytest.raises(cf.CycleError, match="day boundary"):  # naive time
        cf.check_eligibility(**{**ok, "window_end": end.replace(tzinfo=None)})


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


def _a(tid: str, outcome: str | None = "completed",
       reason: str | None = None) -> dict[str, Any]:  # fmt: skip
    return {"trial_id": tid, "outcome": outcome, "reason_code": reason}


CRASH, PARTIAL = cf.CRASH, "PARTIAL_OUTPUT"


def test_rerun_slot_goes_to_the_first_crash_of_the_family_only() -> None:
    """R14C-S-2: the slot is derived from the family's ordered attempts."""
    ids = ["t1", "t2", "t3", "t4"]
    got = cf.trial_states([_a("t1", "failed", CRASH), _a("t2", "failed", CRASH),
                           _a("t3", "failed", PARTIAL), _a("t1")], ids)  # fmt: skip
    assert got == {"t1": "completed", "t2": "final", "t3": "final", "t4": "unstarted"}
    assert cf.trial_states([_a("t1", "failed", CRASH)], ["t1"]) == {"t1": "rerun"}
    assert cf.trial_states([_a("t1", None)], ["t1"]) == {"t1": "running"}
    second = [_a("t1", "failed", CRASH), _a("t1", "failed", CRASH)]
    assert cf.trial_states(second, ["t1"]) == {"t1": "final"}


@pytest.mark.parametrize(
    "seq",
    [
        [_a("t1", "failed", PARTIAL), _a("t1")],  # partial output is final
        [_a("t1"), _a("t1")],  # two completions
        [_a("t1", "failed", CRASH), _a("t2", "failed", CRASH), _a("t2")],  # slot used
        [_a("t1", "failed", CRASH), _a("t1", "failed", CRASH), _a("t1")],  # 3rd attempt
        [_a("t9")],  # undeclared
    ],
)
def test_attempt_sequences_outside_p18_1_are_refused(seq: list[dict[str, Any]]) -> None:
    with pytest.raises(cf.CycleError):
        cf.trial_states(seq, ["t1", "t2"])


def test_family_attempts_come_from_the_durable_ledger(tmp_path: Any) -> None:
    led = tmp_path / "ledger.jsonl"
    h = "a" * 64

    def start(aid: str, idx: int, family: str = "trend",
              partition: str = "confirmation") -> None:  # fmt: skip
        attempts.start_attempt(led, attempt_id=aid, family=family, cycle="c1",
                               partition=partition, hypothesis_hash=h, protocol_hash=h,
                               trial_index=idx, symbols=["BTCUSDT"])  # fmt: skip

    start("attempt-a1", 0)
    attempts.finish_attempt(
        led, attempt_id="attempt-a1", outcome="failed", reason_code=CRASH
    )
    start("attempt-a2", 1)
    start("attempt-x1", 0, family="vol")  # another family: ignored
    start("attempt-x2", 0, partition="exploration")  # not counted: ignored
    start("attempt-a3", 0)
    attempts.finish_attempt(led, attempt_id="attempt-a3", outcome="completed")
    trial_of = {(h, 0): "t000", (h, 1): "t001"}
    entries = read_entries(led)
    got = cf.family_attempts(entries, family="trend", cycle="c1", trial_of=trial_of)
    assert got == [_a("t000", "failed", CRASH), _a("t001", None), _a("t000")]
    assert cf.trial_states(got, ["t000", "t001"]) == {
        "t000": "completed", "t001": "running"}  # fmt: skip
    with pytest.raises(cf.CycleError, match="undeclared"):
        cf.family_attempts(
            entries, family="trend", cycle="c1", trial_of={(h, 0): "t000"}
        )


# --- P18-2 one look ----------------------------------------------------------------


def test_look_trigger() -> None:
    start = W0
    states = {"a": "completed", "b": "final"}
    assert cf.look_allowed(states, start, start + timedelta(days=1), False, False)
    running = {"a": "completed", "b": "running"}
    assert not cf.look_allowed(
        running, start, start + timedelta(days=179), False, False
    )
    assert cf.look_allowed(running, start, start + timedelta(days=180), False, False)
    with pytest.raises(cf.CycleError, match="no pick"):
        cf.look_allowed(states, start, start, True, False)
    with pytest.raises(cf.CycleError, match="already"):
        cf.look_allowed(states, start, start, False, True)


# --- P18-3, P18-4, A-V1 nomination ---------------------------------------------------


Completed = dict[str, tuple[str, list[Any], list[float]]]
DAYS = [W0 + timedelta(days=i) for i in range(400)]


def _family(k: int = 3, t: int = 400) -> tuple[Completed, dict[str, str]]:
    rng = np.random.default_rng(11)
    cols = rng.normal(0.0005, 0.01, (t, k))
    cols[:, 1] += 0.002  # t001 clearly best
    completed = {
        f"t{j:03d}": (f"h{j}", DAYS[:t], cols[:, j].tolist()) for j in range(k)
    }
    return completed, {tid: c[0] for tid, c in completed.items()}


def _done(hashes: dict[str, str]) -> dict[str, str]:
    return {tid: "completed" for tid in hashes}


def always(x: np.ndarray, lengths: list[float]) -> bool:
    return True


def test_nominee_is_the_best_trial_and_both_numerics_reported() -> None:
    completed, hashes = _family()
    n = cf.nominate(
        "trend", _done(hashes), completed, hashes, FAMILY_SEED, "largest", always
    )
    assert (n.available, n.nominee) == (True, "t001")
    assert n.z == n.v.z and n.task12.reason is None  # A-V1: V governs, Task 12 reported
    assert n.x is not None and n.x.shape == (400, 3)


def test_tie_goes_to_the_lowest_declared_id_whatever_the_given_order() -> None:
    completed, hashes = _family()
    completed["t000"] = ("h0", DAYS, completed["t001"][2])  # t000 ties t001 exactly
    states = {"t002": "completed", "t001": "completed", "t000": "completed"}
    n = cf.nominate("trend", states, completed, hashes, FAMILY_SEED, "largest", always)
    assert n.nominee == "t000"


def test_unfinished_mismatched_or_misaligned_trial_fails_the_family_as_u_ops() -> None:
    """R14C-S-4: A_f needs every declared trial completed per the attempt
    records, its hash, and one identical day index; each failure is U_ops."""
    completed, hashes = _family()

    def run(states: dict[str, str], comp: Completed) -> cf.Nomination:
        return cf.nominate(
            "trend", states, comp, hashes, FAMILY_SEED, "largest", always
        )

    missing = {k: v for k, v in completed.items() if k != "t002"}
    n = run({**_done(hashes), "t002": "final"}, missing)
    assert (n.available, n.cause) == (False, "U_ops") and "no completed" in str(
        n.reason
    )
    n = run({**_done(hashes), "t002": "unstarted"}, missing)
    assert (n.available, n.cause) == (False, "U_ops")
    n = run(_done(hashes), {**completed, "t002": ("other", DAYS, completed["t002"][2])})
    assert (n.cause, n.reason) == ("U_ops", "t002: configuration hash mismatch")
    shifted = [d + timedelta(days=1) for d in DAYS]
    n = run(_done(hashes), {**completed, "t002": ("h2", shifted, completed["t002"][2])})
    assert n.cause == "U_ops" and "MISALIGNED_SERIES" in str(n.reason)
    rev = list(reversed(DAYS))
    n = run(_done(hashes), {**completed, "t002": ("h2", rev, completed["t002"][2])})
    assert n.cause == "U_ops" and "MISALIGNED_SERIES" in str(n.reason)
    with pytest.raises(cf.CycleError, match="without a completed attempt"):
        run({**_done(hashes), "t002": "final"}, completed)
    with pytest.raises(cf.CycleError, match="do not match"):
        run({"t000": "completed"}, completed)


def test_classifier_is_required_and_can_refuse() -> None:
    completed, hashes = _family()
    with pytest.raises(cf.CycleError, match="classifier"):
        cf.nominate(
            "trend", _done(hashes), completed, hashes, FAMILY_SEED, "largest", None
        )
    n = cf.nominate("trend", _done(hashes), completed, hashes, FAMILY_SEED, "largest",
                    lambda x, lengths: False)  # fmt: skip
    assert (n.available, n.reason, n.cause) == (False, "UNSUPPORTED_LAW", "U_proc")


def test_family_gates_use_the_nomination_matrix() -> None:
    completed, hashes = _family()
    n = cf.nominate(
        "trend", _done(hashes), completed, hashes, FAMILY_SEED, "largest", always
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
    ok = {g: cf.Gate(cf.NA if g in cf.NA_GATES else cf.PASS) for g in cf.GATES}
    assert cf.nominee_outcome(ok) == "PROCEEDS_TO_LOCKBOX"
    assert cf.nominee_outcome({**ok, "G-2": cf.Gate(cf.FAIL)}) == "FAILED"
    assert (
        cf.nominee_outcome(
            {**ok, "G-2": cf.Gate(cf.FAIL), "G-4": cf.Gate(cf.UNAVAILABLE, "x")}
        )
        == "NO_RESULT"
    )


def test_incomplete_gate_map_is_no_result_and_na_only_where_fixed() -> None:
    """R14C-S-1: a gate not computed counts as UNAVAILABLE (P18-7); N/A only
    for the gates Annex C fixes it for."""
    ok = {g: cf.Gate(cf.PASS) for g in cf.GATES}
    assert cf.nominee_outcome({}) == "NO_RESULT"
    assert (
        cf.nominee_outcome({k: v for k, v in ok.items() if k != "G-13"}) == "NO_RESULT"
    )
    with pytest.raises(cf.CycleError, match="not fixed by Annex C"):
        cf.nominee_outcome({**ok, "G-2": cf.Gate(cf.NA)})
    with pytest.raises(cf.CycleError, match="unknown gates"):
        cf.nominee_outcome({**ok, "G-15": cf.Gate(cf.PASS)})


def test_r13_seeds_are_recorded_per_trial() -> None:
    got = cf.seeds_record(FAMILY_SEED, ["t000", "t001"])
    assert got["t001"] == sha({"family_seed": FAMILY_SEED, "trial_id": "t001"})
    assert len(set(got.values())) == 2
