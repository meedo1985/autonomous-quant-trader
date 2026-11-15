"""Slice 6b build B5c: the evaluation record, sealing, persist and the
closing entry (DESIGN_SLICE6B rev 16 §4, §10-§12). Real ledgers; the earlier
steps (own tests) replaced by verified inputs and recorders."""

from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import test_c2_confirmation_families as tf
import test_c2_confirmation_trial as tt

from aqt.core.ledger import GENESIS_HASH, read_entries
from calibration import c2_confirmation as cf
from calibration import dsr
from calibration.seeds import cj

EVAL_KEYS = {"schema", "cycle_id", "chain_log", "signed", "declaration_sha256",
             "headers_sha256", "capture_record_sha256", "capture_before_tip_window",
             "eligibility", "seeds", "ledger", "trials", "families"}  # fmt: skip
FAMILY_KEYS = {
    "states",
    "A_f",
    "reason",
    "cause",
    "failing",
    "u_proc_results",
    "u_proc_present",
    "nominee",
    "dsr",
    "gates",
    "outcome",
    "cpcv",
}


def inputs() -> cf.Inputs:
    base = tf.inputs()
    headers = cf.Headers(height=1, cycle_start=tt.W0, tip_block_hash="b" * 64,
                         tip_time=tt.W0, headers_sha256="c" * 64)  # fmt: skip
    capture = cf.Capture(timestamp="20260101000000", record_sha256="d" * 64,
                         before_tip_window=False)  # fmt: skip
    seeds = {**base.seeds, "beacon": {"round": 42}}
    started = dataclasses.replace(base.started, chain_log={"k": "v"})
    return dataclasses.replace(base, headers=headers, capture=capture, seeds=seeds,
                               started=started)  # fmt: skip


def nomination(
    nominee: str | None, v_z: float = 2.5, t12_z: float = 2.5
) -> cf.Nomination:
    v = dsr.FamilyResult(None, block=3.0, nominee=1 if nominee else None, z=v_z,
                         columns=((2.0, False),))  # fmt: skip
    t12 = dataclasses.replace(v, z=t12_z)
    return cf.Nomination(nominee is not None, None if nominee else "NO", nominee,
                         v_z, t12, v, cause=None if nominee else "U_ops")  # fmt: skip


def evaluations(trend: str | None = "t1") -> dict[str, cf.FamilyEvaluation]:
    gates = {g: cf.Gate(cf.PASS, values={"x": 0.5, "n": np.int64(3)}) for g in cf.GATES}
    return {
        "trend": cf.FamilyEvaluation(nomination(trend), gates if trend else {},
                                     "PROCEEDS_TO_LOCKBOX" if trend else None,
                                     np.zeros(3) if trend else None,
                                     {"role": "diagnostic_only", "ess": 300.0}
                                     if trend else None, {}),
        "vol": cf.FamilyEvaluation(nomination(None), {}, None, None, None, {}),
    }  # fmt: skip


@pytest.fixture
def w(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tf.World:
    world = tf.World(tmp_path, monkeypatch)
    world.finish_all()
    return world


def test_the_evaluation_record_has_the_schemas_fields(w: tf.World) -> None:
    look = w.look()
    rec = cf.evaluation_record(inputs(), look, evaluations())
    assert set(rec) == EVAL_KEYS and rec["schema"] == "aqt.c2.evaluation.v1"
    assert set(rec["families"]["trend"]) == FAMILY_KEYS
    json.loads(cj(rec))  # canonical JSON, no NaN, every value plain
    assert rec["eligibility"] == {"w0": cf._time(tt.W0), "T": 2,
                                  "cycle_start": cf._time(tt.W0)}  # fmt: skip
    assert rec["ledger"] == {
        "anchor": {"head_hash": GENESIS_HASH, "entry_count": 0},
        "head_hash": look.ledger.head_hash, "entry_count": 6,
        "look_entry_hash": "0" * 64}  # fmt: skip
    want = {tid: hashlib.sha256(cj(tt.payload(tid, aid))).hexdigest()
            for tid, aid in (("t0", "attempt-a0"), ("t1", "attempt-a1"),
                             ("v0", "attempt-b0"))}  # fmt: skip
    assert rec["trials"] == want
    trend = rec["families"]["trend"]
    assert trend["gates"]["G-1"] == {"result": "PASS", "reason": None,
                                     "values": {"x": cf.hexf(0.5), "n": 3}}  # fmt: skip
    assert trend["dsr"]["V"]["z"] == cf.hexf(2.5)
    assert trend["dsr"]["V"]["columns"] == [[cf.hexf(2.0), False]]
    assert trend["cpcv"] == {"role": "diagnostic_only", "ess": cf.hexf(300.0)}
    assert (
        rec["signed"]["z_crit"] == "2.345"
        and rec["signed"]["engine_commit"] == "8" * 40
    )
    assert (
        rec["families"]["vol"]["cause"] == "U_ops"
        and rec["families"]["vol"]["gates"] == {}
    )


@pytest.mark.parametrize(
    ("t12_z", "differs"), [(2.5, False), (2.0, True), (2.4, False)]
)
def test_differs_compares_nominee_reason_and_g9(
    w: tf.World, t12_z: float, differs: bool
) -> None:
    ev = evaluations()
    ev["trend"] = dataclasses.replace(
        ev["trend"], nomination=nomination("t1", 2.5, t12_z)
    )
    rec = cf.evaluation_record(inputs(), w.look(), ev)
    assert rec["families"]["trend"]["dsr"]["differs"] is differs  # z_crit 2.345


def test_plain_refuses_an_unknown_type() -> None:
    assert cf._plain((1.5, np.float64(2.0), [True, None])) == [
        cf.hexf(1.5), cf.hexf(2.0), [True, None]]  # fmt: skip
    with pytest.raises(cf.CycleError, match="no record form for set"):
        cf._plain({1})


def test_sealing_uses_the_nominees_record_result_and_code(
    w: tf.World, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: dict[str, Any] = {}

    def seal_family(**kw: Any) -> Any:
        seen[kw["family"]] = kw
        if kw["family"] == "trend":
            return {"status": "a"}, {"artifact": kw["family"]}
        return {"status": "b"}, None

    monkeypatch.setattr(cf, "seal_family", seal_family)
    sealing, artifacts = cf.seal_families(inputs(), w.look(), evaluations(), "e" * 64)
    t = seen["trend"]
    assert t["record"] == tt.ENTRIES[1] and t["trial"]["trial_id"] == "t1"
    assert t["d_sha256"] == tt.payload("t1", "attempt-a1")["d_sha256"]
    assert (t["window_hours"], t["window"], t["evaluation_record_sha256"]) == (
        48, inputs().window_id, "e" * 64)  # fmt: skip
    assert t["code"] == {
        "lockbox_module_sha256": "4" * 64,
        "confirmation_module_sha256": "9" * 64,
        "engine_commit": "8" * 40,
        "screen_object_sha256": "7" * 64,
    }
    assert seen["vol"]["record"] is None and seen["vol"]["d_sha256"] is None
    assert artifacts == {"trend": {"artifact": "trend"}}
    assert sealing["beacon_round"] == 42 and set(sealing["families"]) == {
        "trend",
        "vol",
    }


class Steps:
    """`evaluate_look` with its earlier steps replaced."""

    def __init__(self, w: tf.World, monkeypatch: pytest.MonkeyPatch) -> None:
        self.w = w
        self.order: list[str] = []
        self.persisted: list[Any] = []
        look = w.look()
        monkeypatch.setattr(cf, "prepare", lambda s, src: inputs())
        monkeypatch.setattr(cf, "open_look", lambda i, src: self.step("look", look))
        monkeypatch.setattr(
            cf,
            "evaluate_families",
            lambda i, lk, r: self.step("families", evaluations()),
        )
        monkeypatch.setattr(cf, "seal_families",
                            lambda i, lk, f, sha: self.step("seal", (
                                {"sealing": sha}, {"trend": {"a": 1}})))  # fmt: skip

    def step(self, name: str, value: Any) -> Any:
        self.order.append(name)
        return value

    def persist(
        self, evaluation: bytes, sealing: bytes, artifacts: dict[str, bytes]
    ) -> None:
        self.order.append("persist")
        assert not self.closings()  # nothing closed before persist returns
        self.persisted.append((evaluation, sealing, artifacts))

    def closings(self) -> list[Any]:
        return [
            e for e in read_entries(self.w.path) if e.record_type == cf.CLOSING_ENTRY
        ]

    def run(self, persist: Any = None) -> Any:
        sources = {"ledger_path": self.w.path}
        return cf.evaluate_look(None, sources, self.w.read, persist or self.persist)  # type: ignore[arg-type]


def test_persist_gets_the_exact_bytes_then_the_closing_entry_is_last(
    w: tf.World, monkeypatch: pytest.MonkeyPatch
) -> None:
    s = Steps(w, monkeypatch)
    evaluation, sealing, artifacts = s.run()
    assert s.order == ["look", "families", "seal", "persist"]
    [(ev_bytes, seal_bytes, art_bytes)] = s.persisted
    assert ev_bytes == cj(evaluation) and seal_bytes == cj(sealing)
    assert art_bytes == {"trend": cj({"a": 1})} and artifacts == {"trend": {"a": 1}}
    assert sealing == {"sealing": hashlib.sha256(ev_bytes).hexdigest()}
    [closing] = s.closings()
    assert closing == read_entries(w.path)[-1]
    assert closing.payload == cf.closing_entry(
        "c1",
        hashlib.sha256(ev_bytes).hexdigest(),
        hashlib.sha256(seal_bytes).hexdigest(),
    )


def test_a_failed_persist_leaves_no_closing_entry(
    w: tf.World, monkeypatch: pytest.MonkeyPatch
) -> None:
    s = Steps(w, monkeypatch)

    def fail(*a: Any) -> None:
        raise OSError("disk full")

    with pytest.raises(OSError, match="disk full"):
        s.run(fail)
    assert s.closings() == []


def test_an_abort_after_the_look_persists_nothing_and_closes_nothing(
    w: tf.World, monkeypatch: pytest.MonkeyPatch
) -> None:
    s = Steps(w, monkeypatch)

    def abort(*a: Any) -> None:
        raise cf.CycleError("C-T: abort")

    monkeypatch.setattr(cf, "evaluate_families", abort)
    with pytest.raises(cf.CycleError, match="C-T"):
        s.run()
    assert s.persisted == [] and s.closings() == []
