"""Slice 6b build B5a: opening the look (DESIGN_SLICE6B rev 16 §2 steps 4-7,
§4, §8). Real ledgers and threads; the inputs `prepare` verified and the
qualification report are given directly (both have their own tests)."""

from __future__ import annotations

import dataclasses
import threading
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import test_c2_confirmation_signed as sg
import test_c2_confirmation_trial as tt

from aqt.core.ledger import append_entry, read_entries
from calibration import c2_confirmation as cf

REPORT = {"z_crit": "2.345", "family_block_rule": "largest"}
BOUNDS = ({"u": 1.0}, {"l": 0.0})


class World(tt.World):
    def __init__(self, tmp: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        super().__init__(tmp, monkeypatch)
        self.now = (datetime.now(UTC) + timedelta(seconds=2)).replace(microsecond=0)
        self.day0 = self.now - timedelta(days=10)
        self.report = dict(REPORT)
        self.bounds_calls: list[tuple[int, int]] = []
        monkeypatch.setattr(cf, "_now", lambda: self.now)
        monkeypatch.setattr(cf, "qualification_report", lambda obj, p: self.report)

        def bounds(report: Any, t_days: int, k: int) -> Any:
            self.bounds_calls.append((t_days, k))
            return BOUNDS

        monkeypatch.setattr(cf, "classifier_bounds", bounds)

    def inputs(self) -> cf.Inputs:
        headers = cf.Headers(height=1, cycle_start=self.day0, tip_block_hash="b" * 64,
                             tip_time=self.day0, headers_sha256="c" * 64)  # fmt: skip
        return dataclasses.replace(
            tt.inputs(), headers=headers, signed=cf.signed_c2(sg.protocol())
        )

    def open(self) -> cf.Look:
        sources = {"ledger_path": self.path, "object_dir": Path("obj")}
        return cf.open_look(self.inputs(), sources)

    def looks(self) -> list[Any]:
        return [e for e in read_entries(self.path) if e.record_type == cf.LOOK_ENTRY]

    def refused(self, match: str) -> None:  # type: ignore[override]
        before = read_entries(self.path) if self.path.exists() else None
        with pytest.raises(cf.CycleError, match=match):
            self.open()
        after = read_entries(self.path) if self.path.exists() else None
        assert after == before  # nothing written

    def finish_all(self) -> None:
        for aid, tid, idx, fam in (("attempt-a0", "t0", 0, "trend"),
                                   ("attempt-a1", "t1", 1, "trend"),
                                   ("attempt-b0", "v0", 2, "vol")):  # fmt: skip
            self.start(aid, idx, family=fam)
            self.result(tid, aid)


@pytest.fixture
def w(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> World:
    return World(tmp_path, monkeypatch)


def test_the_look_entry_is_appended_with_the_step_5_clock(w: World) -> None:
    w.finish_all()
    head = read_entries(w.path)[-1].entry_hash
    w.now = w.now.replace(microsecond=123456)
    got = w.open()
    whole = w.now.replace(microsecond=0)
    [entry] = w.looks()
    assert entry.payload == cf.look_entry("c1", ["trend", "vol"], head, whole, "9" * 64)
    assert entry.recorded_at_utc == cf._time(whole)
    assert (got.now, got.entry_hash, got.report) == (whole, entry.entry_hash, REPORT)
    assert got.bounds == {"trend": BOUNDS, "vol": BOUNDS}
    assert sorted(w.bounds_calls) == [(tt.T_DAYS, 1), (tt.T_DAYS, 2)]  # (T, K_f)
    assert got.families["trend"].states == {"t0": "completed", "t1": "completed"}
    assert got.ledger.look is None and len(got.ledger.entries) == 6


def test_a_running_trial_is_waited_for_until_day_180(w: World) -> None:
    w.start("attempt-a0", 0)  # t0 running, t1 and v0 unstarted
    w.refused("not allowed yet")
    w.day0 = w.now - timedelta(days=cf.LOOK_DAYS)
    got = w.open()
    assert got.families["trend"].states["t0"] == "running" and len(w.looks()) == 1


def test_one_second_before_day_180_is_still_early(w: World) -> None:
    w.start("attempt-a0", 0)
    w.day0 = w.now - timedelta(days=cf.LOOK_DAYS) + timedelta(seconds=1)
    w.refused("not allowed yet")


def test_a_breached_family_is_not_waited_for(w: World) -> None:
    w.start("attempt-a1", 1)
    w.out("attempt-a1")
    w.out("attempt-a1")  # trend breached; t0 never started
    w.start("attempt-b0", 2, family="vol")
    w.result("v0", "attempt-b0")
    got = w.open()
    assert got.families["trend"].breach_reason == "LEDGER_ORDER:attempt-a1"


def test_a_second_look_or_a_termination_is_refused(w: World) -> None:
    w.finish_all()
    w.open()
    w.refused("one look has already run")
    w2_path = w.path.with_name("other.jsonl")
    w.path = w2_path
    w.finish_all()
    w.terminate()
    w.refused("cycle ended before the pick")


def test_the_clock_floor_is_the_last_ledger_entry(w: World) -> None:
    w.finish_all()
    last = datetime.strptime(read_entries(w.path)[-1].recorded_at_utc,
                             "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)  # fmt: skip
    w.now = last - timedelta(seconds=1)
    w.refused("before day 0 or the last ledger entry")


@pytest.mark.parametrize(
    ("key", "value"), [("z_crit", "2.3450"), ("family_block_rule", "median")]
)
def test_signed_rows_must_equal_the_qualification_object(
    w: World, key: str, value: str
) -> None:
    w.finish_all()
    w.report[key] = value
    w.refused(f"signed {key} is not the qualification object's")


def test_a_classifier_refusal_writes_nothing(
    w: World, monkeypatch: pytest.MonkeyPatch
) -> None:
    w.finish_all()

    def refuse(*a: Any) -> None:
        raise cf.CycleError("no frozen thresholds for T=2")

    monkeypatch.setattr(cf, "classifier_bounds", refuse)
    w.refused("no frozen thresholds")


def test_an_identity_breach_refuses_the_look(w: World) -> None:
    w.start("attempt-a0", 0)
    moved = {**tt.payload("t0", "attempt-a0"), "estimator_seed": 8}
    append_entry(w.path, record_type=cf.RESULT_ENTRY, payload=moved)
    w.refused("does not match its derived identity")


def _slip_in(w: World, monkeypatch: pytest.MonkeyPatch, entry: Any) -> None:
    """Another writer that does not take the look lock appends just before
    the look entry."""
    real = append_entry

    def append(path: Any, **kw: Any) -> Any:
        if kw["record_type"] == cf.LOOK_ENTRY:
            entry()
        return real(path, **kw)

    monkeypatch.setattr(cf, "append_entry", append)


def test_an_intervening_entry_of_this_cycle_stops_the_look(
    w: World, monkeypatch: pytest.MonkeyPatch
) -> None:
    w.start("attempt-a0", 0)  # t0 running at day 180
    w.day0 = w.now - timedelta(days=cf.LOOK_DAYS)
    _slip_in(w, monkeypatch, lambda: w.out("attempt-a0"))  # not seen at step 4
    with pytest.raises(cf.CycleError, match="came before the look entry"):
        w.open()
    assert len(w.looks()) == 1  # the look entry stands, with no closing entry


def test_an_intervening_entry_of_another_cycle_is_allowed(
    w: World, monkeypatch: pytest.MonkeyPatch
) -> None:
    w.finish_all()
    _slip_in(w, monkeypatch, lambda: w.start("attempt-z0", 0, cycle="c0"))
    w.open()
    assert len(w.looks()) == 1


def test_two_concurrent_looks_give_one_entry_and_one_refusal(w: World) -> None:
    w.finish_all()
    both = threading.Barrier(2)
    real = w.inputs

    def inputs() -> cf.Inputs:
        both.wait(timeout=10)  # both reach the lock together
        return real()

    w.inputs = inputs  # type: ignore[method-assign]
    outcome: list[str] = []

    def look() -> None:
        try:
            w.open()
            outcome.append("look")
        except cf.CycleError as e:
            outcome.append(str(e))

    threads = [threading.Thread(target=look) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert sorted(outcome) == ["look", "the cycle's one look has already run"]
    assert len(w.looks()) == 1
