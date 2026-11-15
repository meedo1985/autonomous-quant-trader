"""Slice 6b build B2b: result entries, attempt binding and completion, order
breaches (DESIGN_SLICE6B rev 16 §3). Synthetic ledgers only."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from aqt.core import attempts
from aqt.core.ledger import append_entry, read_entries
from calibration import c2_confirmation as cf

H = "a" * 64
CRASH = cf.CRASH
W0 = datetime(2026, 1, 1, tzinfo=UTC)
WINDOW = (W0, 2)
WID = cf.window_id(W0, W0 + 2 * cf.DAY)
TRIAL_OF = {(H, 0): "t0", (H, 1): "t1"}
CONFIG = {"t0": "c" * 64, "t1": "d" * 64}


def _identity(tid: str) -> dict[str, Any]:
    return {
        "trial_index": int(tid[1]), "seed_l266": "5" * 64, "estimator_seed": 7,
        "data_manifest_sha256": "6" * 64, "protocol_hash": H,
        "engine_commit": "8" * 40, "confirmation_module_sha256": "9" * 64,
        "image_digest": "sha256:" + "e" * 64,
    }  # fmt: skip


def expected(tid: str, family: str = "trend") -> dict[str, Any]:
    return {"cycle_id": "c1", "trial_id": tid, "family": family,
            "configuration_hash": CONFIG[tid], "window_id": WID,
            **_identity(tid)}  # fmt: skip


def _payload(tid: str, aid: str, *, reason: str | None = None,
             family: str = "trend", **over: Any) -> dict[str, Any]:  # fmt: skip
    d = [0.5, -0.25]
    rec = {
        "schema": cf.TRIAL_RESULT_SCHEMA, **expected(tid, family), "attempt_id": aid,
        "days": [cf._time(W0), cf._time(W0 + cf.DAY)],
        "d": None if reason else [cf.hexf(x) for x in d],
        "d_sha256": None if reason else cf._floats_sha256(d), "reason": reason,
    }  # fmt: skip
    return {**rec, **over}


class Led:
    def __init__(self, tmp: Path) -> None:
        self.path = tmp / "ledger.jsonl"

    def start(
        self, aid: str, idx: int, family: str = "trend", cycle: str = "c1"
    ) -> None:
        attempts.start_attempt(self.path, attempt_id=aid, family=family, cycle=cycle,
                               partition="confirmation", hypothesis_hash=H,
                               protocol_hash=H, trial_index=idx,
                               symbols=["BTCUSDT"])  # fmt: skip

    def out(
        self, aid: str, outcome: str = "failed", reason: str | None = CRASH
    ) -> None:
        attempts.finish_attempt(self.path, attempt_id=aid, outcome=outcome,
                                reason_code=reason)  # fmt: skip

    def result(self, tid: str, aid: str, **kw: Any) -> None:
        append_entry(
            self.path, record_type=cf.RESULT_ENTRY, payload=_payload(tid, aid, **kw)
        )

    def ledger(self, family: str = "trend") -> cf.FamilyLedger:
        return cf.family_ledger(
            read_entries(self.path),
            family=family,
            cycle="c1",
            trial_of=TRIAL_OF,
            trial_ids=["t0", "t1"],
            expected=lambda t: expected(t, family),
            window=WINDOW,
        )


# --- honest sequences: stated states, never a CycleError ---------------------------


def test_result_entry_completes_the_attempt_and_any_outcome_may_follow(
    tmp_path: Path,
) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.result("t0", "attempt-a0")
    led.out("attempt-a0")  # the runner's crash outcome racing the result entry
    led.start("attempt-a1", 1)
    led.result(
        "t1", "attempt-a1", reason="DAYS_INCOMPLETE"
    )  # an unavailable run is a result
    got = led.ledger()
    assert got.states == {"t0": "completed", "t1": "completed"}
    assert got.breaches == [] and got.breach_reason is None
    assert [r["attempt_id"] for r in got.results] == ["attempt-a0", "attempt-a1"]
    assert got.attempts[0]["end"] == 1  # the result entry's position, not the outcome's


def test_no_result_before_the_first_outcome_is_a_crash_whatever_it_says(
    tmp_path: Path,
) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.out(
        "attempt-a0", outcome="failed", reason="TRIAL_CODE_ERROR"
    )  # not the crash code
    led.start("attempt-a1", 1)
    led.result("t1", "attempt-a1")
    got = led.ledger()
    assert got.attempts[0]["reason_code"] == CRASH and got.attempts[0]["end"] == 1
    assert got.states == {"t0": "rerun", "t1": "completed"}


def test_a_writes_its_result_and_dies_while_b_crashes(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.start("attempt-b0", 1)
    led.result("t0", "attempt-a0")  # A dies after its result: no outcome
    led.out("attempt-b0")  # B crashes
    got = led.ledger()
    assert got.states == {"t0": "completed", "t1": "rerun"}
    led.start("attempt-b1", 1)  # B's re-run in the slot
    led.result("t1", "attempt-b1")
    assert led.ledger().states == {"t0": "completed", "t1": "completed"}


def test_running_and_unstarted(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    assert led.ledger().states == {"t0": "running", "t1": "unstarted"}


def test_results_and_outcomes_of_other_cycles_and_families_are_left_alone(
    tmp_path: Path,
) -> None:
    led = Led(tmp_path)
    led.start("attempt-x0", 0, cycle="c0")
    led.out("attempt-x0")
    led.out("attempt-x0")  # a duplicate outcome in another cycle: ignored
    led.start("attempt-v0", 0, family="vol")
    led.result("t0", "attempt-v0", family="vol")
    led.start("attempt-a0", 0)
    led.result("t0", "attempt-a0")
    got = led.ledger()
    assert got.breaches == [] and got.states == {"t0": "completed", "t1": "unstarted"}
    assert led.ledger("vol").states["t0"] == "completed"


# --- order breaches (rule 1): that family only, reported not raised ----------------


def test_double_outcome_is_an_order_breach(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.out("attempt-a0")
    led.out("attempt-a0")
    led.start("attempt-a1", 1)
    led.result("t1", "attempt-a1")
    got = led.ledger()
    assert got.breach_reason == "LEDGER_ORDER:attempt-a0"
    assert got.breaches == [
        {"attempt_id": "attempt-a0", "kind": "second outcome", "position": 2}
    ]
    assert got.states == {"t0": "final", "t1": "completed"}  # FINAL-F-2, no slot


def test_duplicate_crash_outcome_after_a_legitimate_rerun(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.out("attempt-a0")
    led.start("attempt-a1", 0)  # the re-run
    led.result("t0", "attempt-a1")
    led.out("attempt-a0")  # a second crash outcome for the first attempt
    got = led.ledger()
    assert got.breach_reason == "LEDGER_ORDER:attempt-a0"
    assert got.states == {
        "t0": "completed",
        "t1": "unstarted",
    }  # last attempt completed


def test_second_result_and_result_after_outcome_are_breaches(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.result("t0", "attempt-a0")
    led.result("t0", "attempt-a0")  # second result entry
    led.start("attempt-a1", 1)
    led.out("attempt-a1")
    led.result("t1", "attempt-a1")  # result after its outcome
    got = led.ledger()
    assert [(b["attempt_id"], b["kind"]) for b in got.breaches] == [
        ("attempt-a0", "second result entry"),
        ("attempt-a1", "result after outcome")]  # fmt: skip
    assert got.breach_reason == "LEDGER_ORDER:attempt-a0"
    assert got.states == {"t0": "final", "t1": "final"}
    assert len(got.results) == 3  # every result kept for u_proc_present (B2c)


def test_a_breach_leaves_the_other_family(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.out("attempt-a0")
    led.out("attempt-a0")
    led.start("attempt-v0", 0, family="vol")
    led.result("t0", "attempt-v0", family="vol")
    assert led.ledger().breach_reason == "LEDGER_ORDER:attempt-a0"
    vol = led.ledger("vol")
    assert vol.breaches == [] and vol.states["t0"] == "completed"


def test_extra_start_in_an_unbreached_family_is_still_a_cycle_error(
    tmp_path: Path,
) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.result("t0", "attempt-a0")
    led.start("attempt-a1", 0)  # a start after a result entry (trial_states l.806-809)
    with pytest.raises(cf.CycleError, match="not permitted"):
        led.ledger()


# --- binding and identity (rule 2): CycleError, nothing written ---------------------


@pytest.mark.parametrize(("change", "match"), [
    ({"seed_l266": "4" * 64}, "derived identity"),
    ({"estimator_seed": 8}, "derived identity"),
    ({"data_manifest_sha256": "7" * 64}, "derived identity"),
    ({"image_digest": "sha256:" + "f" * 64}, "derived identity"),
    ({"configuration_hash": "f" * 64}, "derived identity"),
    ({"trial_index": 1}, "derived identity"),
    ({"window_id": cf.window_id(W0 + cf.DAY, W0 + 3 * cf.DAY)}, "governing window"),
])  # fmt: skip
def test_identity_mismatch_refuses(
    tmp_path: Path, change: dict[str, Any], match: str
) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.result("t0", "attempt-a0", **change)
    with pytest.raises(cf.CycleError, match=match):
        led.ledger()


def test_moved_unknown_or_early_attempt_id_refuses(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.result(
        "t0", "attempt-a0"
    )  # before its attempt's start (and unknown at this point)
    led.start("attempt-a0", 0)
    with pytest.raises(cf.CycleError, match="not bound"):
        led.ledger()

    led2 = Led(tmp_path / "x")
    (tmp_path / "x").mkdir()
    led2.start("attempt-a0", 0)
    led2.start("attempt-a1", 1)
    led2.result("t0", "attempt-a1")  # a result moved under the other trial's attempt
    with pytest.raises(cf.CycleError, match="not bound"):
        led2.ledger()

    led3 = Led(tmp_path / "y")
    (tmp_path / "y").mkdir()
    led3.start("attempt-v0", 0, family="vol")
    led3.result("t0", "attempt-v0")  # a trend result bound to a vol start
    with pytest.raises(cf.CycleError, match="not bound"):
        led3.ledger()


def test_malformed_result_entry_refuses(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.result("t0", "attempt-a0", d_sha256="0" * 64)  # d no longer hashes to it
    with pytest.raises(cf.CycleError, match="d_sha256"):
        led.ledger()


def test_shifted_days_are_not_an_identity_breach(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.result(
        "t0", "attempt-a0", days=[cf._time(W0 + cf.DAY), cf._time(W0 + 2 * cf.DAY)]
    )
    got = led.ledger()  # nominate gives MISALIGNED_SERIES (U_ops), B2c
    assert got.states["t0"] == "completed"


def test_outcome_without_any_start_is_a_cycle_error(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    append_entry(led.path, record_type=attempts.ATTEMPT_OUTCOME_RECORD_TYPE,
                 payload={"attempt_id": "ghost", "outcome": "failed"})  # fmt: skip
    with pytest.raises(cf.CycleError, match="never started"):
        led.ledger()


# --- B2c: nominate's §5 precedence from the ledger (owner C-3, B-5) ------------------


def _always(x: Any, lengths: list[float]) -> bool:
    return True


def _nominate(got: cf.FamilyLedger) -> cf.Nomination:
    completed = {}
    for a in got.attempts:  # the last completed attempt's result per trial
        if a["completed"]:
            r = next(r for r in got.results if r["attempt_id"] == a["attempt_id"])
            completed[a["trial_id"]] = cf.completed_entry(r["payload"], WINDOW)
    done = {t: c for t, c in completed.items() if got.states[t] == "completed"}
    return cf.nominate("trend", got.states, WINDOW, done, CONFIG, "f" * 64, "largest",
                       _always, breach=got.breach_reason,
                       results=got.results)  # fmt: skip


def test_days_incomplete_then_a_duplicate_result_is_u_proc(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.result("t0", "attempt-a0", reason="DAYS_INCOMPLETE")
    led.result("t0", "attempt-a0", reason="DAYS_INCOMPLETE")  # breach
    led.start("attempt-a1", 1)
    led.result("t1", "attempt-a1")
    n = _nominate(led.ledger())
    assert (n.available, n.cause, n.reason) == (
        False,
        "U_proc",
        "LEDGER_ORDER:attempt-a0",
    )
    assert n.u_proc_present and [r["reason"] for r in n.u_proc_results] == [
        "DAYS_INCOMPLETE", "DAYS_INCOMPLETE"]  # fmt: skip
    assert n.failing == {"t0": "final"}


def test_breached_family_with_a_superseded_u_proc_result_is_u_proc(
    tmp_path: Path,
) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.out("attempt-a0")  # crash: t0 gets the slot
    led.start("attempt-a1", 0)  # re-run
    led.result("t0", "attempt-a1", reason="TRIAL_CODE_ERROR")
    led.out("attempt-a1")  # outcome after the result: fine
    led.out("attempt-a1")  # second outcome: breach
    led.start("attempt-b0", 1)
    led.result("t1", "attempt-b0")
    n = _nominate(led.ledger())
    assert (n.cause, n.reason) == ("U_proc", "LEDGER_ORDER:attempt-a1")


def test_breached_family_without_u_proc_results_is_u_ops(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.result("t0", "attempt-a0", reason="MISSING_DAY")  # a U_ops reason
    led.result("t0", "attempt-a0", reason="MISSING_DAY")
    n = _nominate(led.ledger())
    assert (n.cause, n.u_proc_present) == ("U_ops", False)


def test_unbreached_running_trial_beats_days_incomplete(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)  # still running at the look
    led.start("attempt-a1", 1)
    led.result("t1", "attempt-a1", reason="DAYS_INCOMPLETE")
    n = _nominate(led.ledger())
    assert (n.cause, n.u_proc_present) == ("U_ops", True)  # rule 2 first (rev 6)
    assert n.reason == "t0: running; t1: DAYS_INCOMPLETE"
    assert n.failing == {"t0": "running", "t1": "DAYS_INCOMPLETE"}


def test_unbreached_u_ops_reason_beats_u_proc_reason(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.result("t0", "attempt-a0", reason="SIGMA_UNBOUND")
    led.start("attempt-a1", 1)
    led.result("t1", "attempt-a1", reason="DAYS_INCOMPLETE")
    assert _nominate(led.ledger()).cause == "U_ops"  # rule 3


def test_unbreached_days_incomplete_alone_is_u_proc(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.result("t0", "attempt-a0")
    led.start("attempt-a1", 1)
    led.result("t1", "attempt-a1", reason="DAYS_INCOMPLETE")
    n = _nominate(led.ledger())
    assert (n.cause, n.reason) == ("U_proc", "t1: DAYS_INCOMPLETE")  # rule 4, B-5


def test_unbreached_shifted_days_are_misaligned_u_ops(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-a0", 0)
    led.result("t0", "attempt-a0",
               days=[cf._time(W0 + cf.DAY), cf._time(W0 + 2 * cf.DAY)])  # fmt: skip
    led.start("attempt-a1", 1)
    led.result("t1", "attempt-a1", reason="DAYS_INCOMPLETE")
    n = _nominate(led.ledger())
    assert n.cause == "U_ops" and n.failing["t0"] == "MISALIGNED_SERIES"
