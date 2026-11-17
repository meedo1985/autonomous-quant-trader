"""Slice 6b build B4c: evaluate_trial (DESIGN_SLICE6B rev 16 §1, §3 rule 4,
FINAL-F-4). Real ledgers and threads; steps 2-3 (`prepare`, tested in
test_c2_confirmation_prepare.py) are replaced by verified inputs, and the
read-and-compute step by a recorder that serves a well-formed result."""

from __future__ import annotations

import dataclasses
import threading
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from aqt.core import attempts
from aqt.core.ledger import GENESIS_HASH, append_entry, read_entries
from calibration import c2_confirmation as cf

H = "a" * 64
W0 = datetime(2026, 1, 1, tzinfo=UTC)
T_DAYS = 2
ENTRIES: list[dict[str, Any]] = [
    {"family": f, "trial_id": t, "hypothesis_hash": H, "configuration_hash": c * 64,
     "trial_index": i}
    for i, (f, t, c) in enumerate((("trend", "t0", "c"), ("trend", "t1", "d"),
                                   ("vol", "v0", "e")))
]  # fmt: skip


def inputs() -> cf.Inputs:
    started = cf.Started(
        protocol_hash=H, lockbox_module_sha256="4" * 64,
        confirmation_module_sha256="9" * 64, engine_commit="8" * 40,
        screen_object_sha256="7" * 64, image_digest="sha256:" + "e" * 64,
        protocol=b"", declaration=b"", declaration_sha256="0" * 64, chain_log={},
    )  # fmt: skip
    trials = [{"trial_id": e["trial_id"], "family": e["family"]} for e in ENTRIES]
    declared: dict[str, list[dict[str, Any]]] = {}
    for t in trials:
        declared.setdefault(t["family"], []).append(t)
    decl = cf.Declaration(
        cycle_id="c1", entries=ENTRIES, declared=declared, trials=trials,
        data_manifest_sha256="6" * 64, last_seen=W0, embargo_days=0,
        anchor_head_hash=GENESIS_HASH, anchor_entry_count=0,
        screen_record_sha256="3" * 64,
    )  # fmt: skip
    seeds = {"families": {f: {"trials": {
        e["trial_id"]: {"trial_index": e["trial_index"], "seed_l266": "5" * 64,
                        "estimator_seed": 7}
        for e in ENTRIES if e["family"] == f}} for f in declared}}  # fmt: skip
    return cf.Inputs(started, decl, None, None, None, W0, T_DAYS, seeds, Path("."))  # type: ignore[arg-type]


def payload(tid: str, aid: str) -> dict[str, Any]:
    d = [0.5, -0.25]
    return {
        "schema": cf.TRIAL_RESULT_SCHEMA, **inputs().expected(tid), "attempt_id": aid,
        "days": [cf._time(W0 + k * cf.DAY) for k in range(T_DAYS)],
        "d": [cf.hexf(x) for x in d], "d_sha256": cf._floats_sha256(d), "reason": None,
    }  # fmt: skip


class World:
    def __init__(self, tmp: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        self.path = tmp / "ledger.jsonl"
        self.reads = 0
        self.during: Callable[[], Any] = lambda: None
        monkeypatch.setattr(cf, "prepare", lambda started, sources: inputs())

        def run_trial(inp: cf.Inputs, tid: str, aid: str, read: Any) -> dict[str, Any]:
            read()
            return payload(tid, aid)

        monkeypatch.setattr(cf, "run_trial", run_trial)

    def read(self) -> None:
        self.reads += 1
        self.during()

    def start(self, aid: str, idx: int, family: str = "trend", **kw: Any) -> None:
        args = {"cycle": "c1", "partition": "confirmation", "protocol_hash": H, **kw}
        attempts.start_attempt(self.path, attempt_id=aid, family=family,
                               hypothesis_hash=H, trial_index=idx,
                               symbols=["BTCUSDT"], **args)  # fmt: skip

    def out(self, aid: str) -> None:
        attempts.finish_attempt(self.path, attempt_id=aid, outcome="failed",
                                reason_code=cf.CRASH)  # fmt: skip

    def result(self, tid: str, aid: str) -> None:
        append_entry(self.path, record_type=cf.RESULT_ENTRY, payload=payload(tid, aid))

    def look(self) -> None:
        append_entry(self.path, record_type=cf.LOOK_ENTRY,
                     payload=cf.look_entry("c1", ["trend", "vol"], "0" * 64, W0,
                                           "9" * 64))  # fmt: skip

    def terminate(self) -> None:
        end = {"cycle_id": "c1", "kind": "PRE_PICK", "reason": "x"}
        append_entry(self.path, record_type=cf.TERMINATION_ENTRY, payload=end)

    def evaluate(self, tid: str, aid: str) -> dict[str, Any]:
        sources = {"ledger_path": self.path}
        return cf.evaluate_trial(None, sources, tid, aid, self.read)  # type: ignore[arg-type]

    def results(self) -> list[dict[str, Any]]:
        return [e.payload for e in read_entries(self.path)
                if e.record_type == cf.RESULT_ENTRY]  # fmt: skip

    def refused(self, tid: str, aid: str, match: str, reads: int = 0) -> None:
        before = read_entries(self.path)
        with pytest.raises(cf.CycleError, match=match):
            self.evaluate(tid, aid)
        assert self.reads == reads  # 0: refused before any protected-data read
        assert read_entries(self.path) == before  # nothing appended


@pytest.fixture
def w(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> World:
    return World(tmp_path, monkeypatch)


def test_a_running_attempt_gets_exactly_one_result_entry(w: World) -> None:
    w.start("attempt-a0", 0)
    got = w.evaluate("t0", "attempt-a0")
    assert got == payload("t0", "attempt-a0") and w.reads == 1
    assert w.results() == [got]
    led = cf.family_ledger(read_entries(w.path), family="trend", cycle="c1",
                           trial_of=inputs().trial_of, trial_ids=["t0", "t1"],
                           expected=inputs().expected, window=(W0, T_DAYS))  # fmt: skip
    assert led.states["t0"] == "completed"
    assert [e.record_type for e in read_entries(w.path)].count(
        attempts.ATTEMPT_OUTCOME_RECORD_TYPE
    ) == 0  # evaluate_trial writes no outcome


# --- refused before any protected-data read ---------------------------------------


def test_an_undeclared_trial_or_an_unbound_attempt_is_refused(w: World) -> None:
    w.start("attempt-a0", 0)
    w.start(
        "attempt-v-as-t0", 0, family="vol"
    )  # t0's (hypothesis, index), another family
    w.start("attempt-x0", 0, partition="exploration")
    w.refused("t9", "attempt-a0", "not a declared trial")
    w.refused("t0", "attempt-nope", "not a start of t0")
    w.refused("t1", "attempt-a0", "not a start of t1")  # a0 is t0's attempt
    w.refused("t0", "attempt-v-as-t0", "not a start of t0")
    w.refused("t0", "attempt-x0", "not a start of t0")


def test_an_attempt_of_another_cycle_is_refused(w: World) -> None:
    w.start("attempt-a0", 0, cycle="c0")
    w.refused("t0", "attempt-a0", "not a start of t0")


def test_an_attempt_with_an_outcome_or_a_result_is_refused(w: World) -> None:
    w.start("attempt-a0", 0)
    w.out("attempt-a0")  # crashed
    w.refused("t0", "attempt-a0", "not running")
    w.start("attempt-a1", 1)
    w.result("t1", "attempt-a1")  # already has its result
    w.refused("t1", "attempt-a1", "not running")


@pytest.mark.parametrize("entry", ["look", "terminate"])
def test_a_look_or_termination_entry_refuses_every_trial(w: World, entry: str) -> None:
    w.start("attempt-a0", 0)
    getattr(w, entry)()
    w.refused("t0", "attempt-a0", "look or termination entry")


def test_a_breached_family_is_refused_and_the_other_family_runs(w: World) -> None:
    w.start("attempt-a1", 1)
    w.out("attempt-a1")
    w.out("attempt-a1")  # a second outcome: order breach of trend
    w.start("attempt-a0", 0)
    w.refused(
        "t0", "attempt-a0", r"trend has an order breach \(LEDGER_ORDER:attempt-a1\)"
    )
    w.start("attempt-b0", 2, family="vol")
    w.evaluate("v0", "attempt-b0")
    assert [r["attempt_id"] for r in w.results()] == ["attempt-b0"]


def test_a_start_with_another_protocol_hash_is_refused(w: World) -> None:
    w.start("attempt-a0", 0, protocol_hash="b" * 64)
    w.refused("t0", "attempt-a0", "another protocol hash")


def test_a_malformed_result_entry_of_the_family_is_refused(w: World) -> None:
    w.start("attempt-a1", 1)
    moved = {**payload("t1", "attempt-a1"), "seed_l266": "0" * 64}
    append_entry(w.path, record_type=cf.RESULT_ENTRY, payload=moved)
    w.start("attempt-a0", 0)
    w.refused("t0", "attempt-a0", "does not match its derived identity")


# --- re-checked under the look lock after the read ---------------------------------


@pytest.mark.parametrize(
    ("during", "match", "theirs"),
    [
        (lambda w: w.out("attempt-a0"), "not running", 0),
        (lambda w: w.result("t0", "attempt-a0"), "not running", 1),  # another process's
        (lambda w: w.look(), "look or termination entry", 0),
        (lambda w: w.terminate(), "look or termination entry", 0),
        (lambda w: (w.out("attempt-a1"), w.out("attempt-a1")), "order breach", 0),
    ],
)
def test_a_change_during_the_read_refuses_without_appending(
    w: World, during: Callable[[World], Any], match: str, theirs: int
) -> None:
    w.start("attempt-a0", 0)
    w.start("attempt-a1", 1)
    w.during = lambda: during(w)
    with pytest.raises(cf.CycleError, match=match):
        w.evaluate("t0", "attempt-a0")
    assert w.reads == 1
    assert len(w.results()) == theirs  # only what the other writer appended


def test_a_double_launch_gives_one_entry_and_one_refusal(w: World) -> None:
    w.start("attempt-a0", 0)
    both = threading.Barrier(2)
    w.during = lambda: both.wait(timeout=10)  # both pass the pre-read check
    outcome: list[str] = []

    def launch() -> None:
        try:
            w.evaluate("t0", "attempt-a0")
            outcome.append("entry")
        except cf.CycleError as e:
            outcome.append(f"refused: {e}")

    threads = [threading.Thread(target=launch) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert sorted(outcome) == ["entry", "refused: attempt 'attempt-a0' is not running"]
    assert w.results() == [payload("t0", "attempt-a0")]


def test_the_append_waits_for_the_look_lock(w: World) -> None:
    w.start("attempt-a0", 0)
    read_done, done = threading.Event(), threading.Event()
    w.during = read_done.set

    def launch() -> None:
        w.evaluate("t0", "attempt-a0")
        done.set()

    with cf.look_lock(w.path):
        t = threading.Thread(target=launch)
        t.start()
        assert read_done.wait(timeout=10)  # past the read, now at the lock
        assert not done.wait(timeout=0.3) and w.results() == []
    t.join(timeout=10)
    assert done.is_set() and len(w.results()) == 1


# --- run_trial: the read and its cut ----------------------------------------------


def test_run_trial_cuts_the_trials_warm_up_and_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inp = inputs()
    trial = {**inp.decl.trials[0], "warmup_hours": 10}
    decl = dataclasses.replace(inp.decl, trials=[trial, *inp.decl.trials[1:]])
    inp = dataclasses.replace(inp, decl=decl)
    seen: dict[str, Any] = {}

    def check_read(comp: Any, served: Any, **kw: Any) -> str:
        seen["read"] = (comp, served, kw)
        return "rows"

    def trial_path(rows: Any, start: Any, w0: Any, warmup: Any, hours: Any) -> str:
        seen["path"] = (rows, start, w0, warmup, hours)
        return "path"

    monkeypatch.setattr(cf, "check_read", check_read)
    monkeypatch.setattr(cf, "trial_path", trial_path)
    monkeypatch.setattr(cf, "trial_result", lambda **kw: kw)
    got = cf.run_trial(inp, "t0", "attempt-a0", lambda: ("comp", {"k": "v"}))
    start = W0 - 10 * cf.HOUR
    assert seen["read"] == ("comp", {"k": "v"}, {
        "decl": inp.decl, "protocol_hash": H, "start": start,
        "end": W0 + T_DAYS * cf.DAY})  # fmt: skip
    assert seen["path"] == ("rows", start, W0, 10, T_DAYS * 24)
    assert got["path"] == "path" and got["record"] == ENTRIES[0]
    assert got["identity"] == {k: inp.expected("t0")[k] for k in cf.IDENTITY_KEYS}
    assert (got["cycle_id"], got["attempt_id"], got["window_hours"]) == (
        "c1",
        "attempt-a0",
        48,
    )
    for bad in (None, ("comp",), ["comp", {}]):

        def serve(b: Any = bad) -> Any:
            return b

        with pytest.raises(cf.CycleError, match="did not serve"):
            cf.run_trial(inp, "t0", "attempt-a0", serve)
