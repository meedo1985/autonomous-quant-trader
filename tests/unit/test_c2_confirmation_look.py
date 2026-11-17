"""Slice 6b build B3: the cycle's ledger (anchor, start protocol hash), the look,
closing and termination entries, `look_allowed` and its clock floor
(DESIGN_SLICE6B rev 16 §2, §4, §5.1, §13). Synthetic ledgers only."""

from __future__ import annotations

import dataclasses
import subprocess
import sys
import threading
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from aqt.core import attempts
from aqt.core.ledger import GENESIS_HASH, append_entry, read_entries
from calibration import c2_confirmation as cf

P = "a" * 64  # the signed protocol hash
T0 = datetime(2026, 3, 1, tzinfo=UTC)  # day 0
HOUR = timedelta(hours=1)


def decl(count: int = 0, head: str = GENESIS_HASH, cycle: str = "c1") -> cf.Declaration:
    return cf.Declaration(
        cycle_id=cycle, entries=[], declared={}, trials=[],
        data_manifest_sha256="6" * 64, last_seen=T0, embargo_days=0,
        anchor_head_hash=head, anchor_entry_count=count, screen_record_sha256="7" * 64,
    )  # fmt: skip


class Led:
    def __init__(self, tmp: Path) -> None:
        self.path = tmp / "ledger.jsonl"

    def start(self, aid: str, cycle: str = "c1", protocol: str = P) -> None:
        attempts.start_attempt(self.path, attempt_id=aid, family="trend", cycle=cycle,
                               partition="confirmation", hypothesis_hash=P,
                               protocol_hash=protocol, trial_index=0,
                               symbols=["BTCUSDT"])  # fmt: skip

    def add(self, record_type: str, payload: dict[str, Any],
            at: datetime | None = None) -> None:  # fmt: skip
        append_entry(self.path, record_type=record_type, payload=payload,
                     recorded_at_utc=at or T0)  # fmt: skip

    def look(self, cycle: str = "c1", **over: Any) -> None:
        self.add(cf.LOOK_ENTRY, {**cf.look_entry(cycle, ["vol", "trend"], "1" * 64, T0,
                                                 "9" * 64), **over})  # fmt: skip

    def close(self, cycle: str = "c1") -> None:
        self.add(cf.CLOSING_ENTRY, cf.closing_entry(cycle, "2" * 64, "3" * 64))

    def terminate(self, cycle: str = "c1") -> None:
        self.add(
            cf.TERMINATION_ENTRY,
            {"cycle_id": cycle, "kind": "LOOK_WITHOUT_RECORD", "reason": "x"},
        )

    def entries(self) -> tuple[Any, ...]:
        return read_entries(self.path)

    def cycle(
        self, d: cf.Declaration | None = None, protocol: str = P
    ) -> cf.CycleLedger:
        return cf.cycle_ledger(self.entries(), d or decl(), protocol)


# --- the anchor (A-1) and each start's protocol hash ------------------------------


def test_an_empty_ledger_extends_the_genesis_anchor(tmp_path: Path) -> None:
    got = Led(tmp_path).cycle()
    assert (got.look, got.closing, got.terminations, got.head_hash) == (
        None, None, [], GENESIS_HASH)  # fmt: skip


def test_the_ledger_must_extend_the_declared_anchor(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.start("attempt-x0", cycle="c0")
    led.start("attempt-a0")
    head = led.entries()[0].entry_hash
    assert led.cycle(decl(1, head)).entries == led.entries()
    for d in (decl(1, "f" * 64), decl(3, head), decl(0, head)):
        with pytest.raises(cf.CycleError, match="anchor"):
            led.cycle(d)


@pytest.mark.parametrize("kind", ["start", "result", "look", "closing", "termination"])
def test_an_entry_of_this_cycle_before_the_anchor_is_refused(
    tmp_path: Path, kind: str
) -> None:
    led = Led(tmp_path)
    if kind == "start":
        led.start("attempt-a0")
    elif kind == "result":
        led.add(cf.RESULT_ENTRY, {"cycle_id": "c1"})
    elif kind == "look":
        led.look()
    elif kind == "closing":
        led.close()
    else:
        led.terminate()
    led.start("attempt-a1")
    with pytest.raises(cf.CycleError, match="precedes the anchor"):
        led.cycle(decl(1, led.entries()[0].entry_hash))


def test_an_outcome_of_this_cycle_before_the_anchor_is_refused(tmp_path: Path) -> None:
    """B3-A-3: only the outcome precedes the anchor; its start lies after it
    (a hash-valid ledger `finish_attempt` itself would not write)."""
    led = Led(tmp_path)
    led.add(attempts.ATTEMPT_OUTCOME_RECORD_TYPE,
            {"attempt_id": "attempt-a0", "outcome": "completed"})  # fmt: skip
    led.start("attempt-a0")
    anchor = decl(1, led.entries()[0].entry_hash)
    with pytest.raises(cf.CycleError, match="entry 0 of this cycle precedes"):
        led.cycle(anchor)
    assert led.cycle(dataclasses.replace(anchor, cycle_id="c0")).look is None


def test_every_start_of_this_cycle_carries_the_signed_protocol_hash(
    tmp_path: Path,
) -> None:
    led = Led(tmp_path)
    led.start("attempt-x0", cycle="c0", protocol="b" * 64)  # another cycle: allowed
    led.start("attempt-a0")
    assert led.cycle().look is None
    led.start("attempt-a1", protocol="b" * 64)
    with pytest.raises(cf.CycleError, match="protocol hash"):
        led.cycle()


@pytest.mark.parametrize("family,partition", [("vol", "confirmation"),
                                              ("trend", "exploration")])  # fmt: skip
def test_the_protocol_hash_holds_in_every_family_and_partition(
    tmp_path: Path, family: str, partition: str
) -> None:
    led = Led(tmp_path)
    attempts.start_attempt(led.path, attempt_id="attempt-a0", family=family,
                           cycle="c1", partition=partition, hypothesis_hash=P,
                           protocol_hash="b" * 64, trial_index=0,
                           symbols=["BTCUSDT"])  # fmt: skip
    with pytest.raises(cf.CycleError, match="protocol hash"):
        led.cycle()


# --- look, closing and termination entries (§4, §5.1) -----------------------------


def test_look_closing_and_termination_entries_are_found(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.look(cycle="c0")  # another cycle's look: ignored
    led.start("attempt-a0")
    led.look()
    led.add(cf.RESULT_ENTRY, {"cycle_id": "c0"})  # a late entry of another cycle
    led.close()
    led.terminate()
    got = led.cycle()
    assert (got.look, got.closing, got.terminations) == (2, 4, [5])
    assert got.pre_look == led.entries()[:2]
    assert got.entries[2].payload["families"] == ["trend", "vol"]


@pytest.mark.parametrize("order", ["two looks", "closing first", "two closings"])
def test_a_second_look_or_a_stray_closing_is_refused(
    tmp_path: Path, order: str
) -> None:
    led = Led(tmp_path)
    if order == "two looks":
        led.look()
        led.look()
    elif order == "closing first":
        led.close()
        led.look()
    else:
        led.look()
        led.close()
        led.close()
    with pytest.raises(cf.CycleError, match="second look|no look before"):
        led.cycle()


@pytest.mark.parametrize(
    "over",
    [{"now": ""}, {"families": "trend"}, {"families": [1]}, {"extra": "x"},
     {"ledger_head_before": 5}, {"now": "not-a-time"}, {"now": "2026-3-01T00:00:00Z"},
     {"ledger_head_before": "not-a-hash"},
     {"confirmation_module_sha256": "A" * 64}],
)  # fmt: skip
def test_a_malformed_look_entry_is_refused(
    tmp_path: Path, over: dict[str, Any]
) -> None:
    led = Led(tmp_path)
    led.look(**over)
    with pytest.raises(cf.CycleError, match="well-formed"):
        led.cycle()


def test_a_closing_entry_with_malformed_hashes_is_refused(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.look()
    led.add(cf.CLOSING_ENTRY, cf.closing_entry("c1", "bad", "3" * 64))
    with pytest.raises(cf.CycleError, match="well-formed"):
        led.cycle()


_BAD_IDS: list[Any] = ["missing", None, "", ["c1"]]


@pytest.mark.parametrize("kind", ["look", "closing", "termination"])
@pytest.mark.parametrize("bad", _BAD_IDS)
def test_a_control_entry_without_a_cycle_id_cannot_vanish(
    tmp_path: Path, kind: str, bad: Any
) -> None:
    """B3-A-1: the form is checked before the cycle filter."""
    led = Led(tmp_path)
    payload = {
        "look": cf.look_entry("c1", ["trend"], "1" * 64, T0, "9" * 64),
        "closing": cf.closing_entry("c1", "2" * 64, "3" * 64),
        "termination": {"cycle_id": "c1", "kind": "k", "reason": "r"},
    }[kind]
    rtype = {"look": cf.LOOK_ENTRY, "closing": cf.CLOSING_ENTRY,
             "termination": cf.TERMINATION_ENTRY}[kind]  # fmt: skip
    if bad == "missing":
        del payload["cycle_id"]
    else:
        payload["cycle_id"] = bad
    led.add(rtype, payload)
    with pytest.raises(cf.CycleError, match="well-formed"):
        led.cycle()


def test_a_malformed_termination_entry_is_refused(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.add(cf.TERMINATION_ENTRY, {"cycle_id": "c1", "kind": "LOOK_WITHOUT_RECORD"})
    with pytest.raises(cf.CycleError, match="well-formed"):
        led.cycle()


# --- look_allowed: one look, no look after termination, the clock floor -----------


def fam(states: dict[str, str], breached: bool = False) -> cf.FamilyLedger:
    breaches = [{"attempt_id": "attempt-a0", "kind": "second outcome", "position": 0}]
    return cf.FamilyLedger([], breaches if breached else [], [], states)


def test_look_allowed_refuses_after_a_look_or_a_termination(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.look()
    done = {"trend": fam({"t0": "completed"})}
    with pytest.raises(cf.CycleError, match="already run"):
        cf.look_allowed(done, led.cycle(), T0, T0 + timedelta(days=1))
    led2 = Led(tmp_path / "x")
    led2.path.parent.mkdir()
    led2.terminate()
    with pytest.raises(cf.CycleError, match="no pick"):
        cf.look_allowed(done, led2.cycle(), T0, T0 + timedelta(days=1))


def test_the_look_clock_floor(tmp_path: Path) -> None:
    led = Led(tmp_path)
    led.add("aqt.other.v1", {"x": 1}, at=T0 + timedelta(days=2))
    done = {"trend": fam({"t0": "completed"})}
    cyc = led.cycle()
    assert cf.look_allowed(done, cyc, T0, T0 + timedelta(days=2))
    for now in (T0 + timedelta(days=2, seconds=-1), T0 - timedelta(days=1)):
        with pytest.raises(cf.CycleError, match="before day 0 or the last"):
            cf.look_allowed(done, cyc, T0, now)
    with pytest.raises(cf.CycleError, match="whole UTC seconds"):
        cf.look_allowed(done, cyc, T0, T0 + timedelta(days=3, microseconds=5))
    for bad in (datetime(2026, 3, 5), datetime(2026, 3, 5, tzinfo=timezone(HOUR))):
        with pytest.raises(cf.CycleError, match="whole UTC seconds"):  # naive, +01:00
            cf.look_allowed(done, cyc, T0, bad)
    with pytest.raises(cf.CycleError, match="before day 0"):  # empty ledger, early
        cf.look_allowed(
            done, Led(tmp_path / "e").cycle(), T0, T0 - timedelta(seconds=1)
        )


def test_a_breached_family_is_not_waited_for(tmp_path: Path) -> None:
    cyc = Led(tmp_path).cycle()
    now = T0 + timedelta(days=10)
    breached = fam({"t0": "running"}, breached=True)
    assert cf.look_allowed(
        {"trend": breached, "vol": fam({"t1": "final"})}, cyc, T0, now
    )
    assert cf.look_allowed({"trend": breached}, cyc, T0, now)  # nothing to wait for
    assert not cf.look_allowed(
        {"trend": fam({"t0": "running"}), "vol": fam({"t1": "final"})}, cyc, T0, now
    )
    assert cf.look_allowed(
        {"trend": fam({"t0": "running"})}, cyc, T0, T0 + timedelta(days=180)
    )


# --- the look lock (§4) -------------------------------------------------------------


def _waiter(path: Path, got: threading.Event) -> threading.Thread:
    def run() -> None:
        with cf.look_lock(path):
            got.set()

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t


def test_the_look_lock_blocks_a_second_holder_until_released(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    got = threading.Event()
    with cf.look_lock(path):
        assert (tmp_path / "ledger.jsonl.look.lock").is_file()
        waiter = _waiter(path, got)
        assert not got.wait(0.3)  # blocked, no deadline
        # the append lock is a different sidecar: appends still work inside
        append_entry(path, record_type="aqt.other.v1", payload={"x": 1})
    assert got.wait(5)
    waiter.join(5)


def test_the_look_lock_is_released_on_an_exception(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    with pytest.raises(RuntimeError), cf.look_lock(path):
        raise RuntimeError("abort inside the locked section")
    got = threading.Event()
    _waiter(path, got).join(5)
    assert got.is_set()


def test_a_leftover_sidecar_file_is_not_a_lock(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    (tmp_path / "ledger.jsonl.look.lock").write_bytes(b"stale")
    with cf.look_lock(path):
        pass


def test_day_180_minus_one_second_still_waits(tmp_path: Path) -> None:
    cyc = Led(tmp_path).cycle()
    running = {"trend": fam({"t0": "running"})}
    day180 = T0 + timedelta(days=180)
    assert not cf.look_allowed(running, cyc, T0, day180 - timedelta(seconds=1))
    assert cf.look_allowed(running, cyc, T0, day180)


def test_a_dead_holder_releases_the_look_lock(tmp_path: Path) -> None:
    """B3-A review note: the OS releases a killed process's lock."""
    path = tmp_path / "ledger.jsonl"
    code = (
        "import sys, time\n"
        "from calibration import c2_confirmation as cf\n"
        "with cf.look_lock(sys.argv[1]):\n"
        "    print('held', flush=True)\n"
        "    time.sleep(600)\n"
    )
    proc = subprocess.Popen([sys.executable, "-c", code, str(path)],
                            stdout=subprocess.PIPE, text=True,
                            cwd=Path(cf.__file__).parents[1])  # fmt: skip
    try:
        assert proc.stdout is not None and proc.stdout.readline().strip() == "held"
        got = threading.Event()
        waiter = _waiter(path, got)
        assert not got.wait(1.0)  # another process holds it
        proc.kill()
        proc.wait(30)
        assert got.wait(30)
        waiter.join(5)
    finally:
        proc.kill()


@pytest.mark.parametrize(
    "payload",
    [{"attempt_id": ["x"], "family": "trend", "partition": "confirmation"},
     {k: v for k, v in {"attempt_id": "attempt-x", "family": "trend",
      "partition": "confirmation", "hypothesis_hash": P, "protocol_hash": P,
      "trial_index": 0, "symbols": ["BTCUSDT"]}.items()}],  # no `cycle`
)  # fmt: skip
def test_a_malformed_start_is_a_cycle_error(
    tmp_path: Path, payload: dict[str, Any]
) -> None:
    """R14B6F-F-4: not a KeyError or TypeError."""
    led = Led(tmp_path)
    led.add(attempts.ATTEMPT_STARTED_RECORD_TYPE, payload)
    with pytest.raises(cf.CycleError, match="start entry is malformed"):
        led.cycle()


def test_an_outcome_or_result_with_an_unhashable_attempt_id_is_not_ours() -> None:
    """R14B6F-F-4: `of_cycle` never raises on a malformed attempt_id."""
    ours = frozenset({"attempt-a"})
    for rt in (attempts.ATTEMPT_OUTCOME_RECORD_TYPE, cf.RESULT_ENTRY):
        e = SimpleNamespace(record_type=rt, payload={"attempt_id": ["attempt-a"]})
        assert cf.of_cycle(e, "c1", ours) is False


@pytest.mark.parametrize(
    ("record_type", "payload", "match"),
    [
        (attempts.ATTEMPT_OUTCOME_RECORD_TYPE, {"attempt_id": []}, "outcome entry"),
        (attempts.ATTEMPT_OUTCOME_RECORD_TYPE, {"outcome": "failed"}, "outcome entry"),
        (cf.RESULT_ENTRY, {"cycle_id": "other", "attempt_id": []}, "result entry"),
    ],
)  # fmt: skip
def test_a_malformed_outcome_or_result_id_is_refused_by_the_readers(
    tmp_path: Path, record_type: str, payload: dict[str, Any], match: str
) -> None:
    """B6FR-A-2: `family_attempts` and `family_ledger` refuse, never a
    KeyError or TypeError."""
    led = Led(tmp_path)
    led.start("attempt-a")
    bad = SimpleNamespace(record_type=record_type, payload=payload)
    with pytest.raises(cf.CycleError, match=match):
        cf.family_ledger([*led.entries(), bad], family="trend", cycle="c1",
                         trial_of={(P, 0): "t0"}, trial_ids=["t0"],
                         expected=lambda tid: {}, window=(T0, 2))  # fmt: skip
