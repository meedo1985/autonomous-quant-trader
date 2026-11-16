"""Slice 6b build B5b: the read, the nomination and the gates
(DESIGN_SLICE6B rev 16 §2 step 8, §5, §8, §9). Real ledgers for the family
states; the frozen gate and DSR code (own tests) replaced by recorders."""

from __future__ import annotations

import dataclasses
import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import test_c2_confirmation_signed as sg
import test_c2_confirmation_trial as tt

from aqt.core.ledger import append_entry, read_entries
from calibration import c2_confirmation as cf
from calibration import dsr

BOUNDS = ({"u": 1.0}, {"l": 0.0})
NOMINEE_GATES = {g: cf.Gate(cf.PASS) for g in cf.NOMINEE_GATES}
FAMILY_GATES = {g: cf.Gate(cf.PASS) for g in ("G-9", "G-10", "G-13")}


def inputs() -> cf.Inputs:
    base = tt.inputs()
    seeds = {"families": {
        f: {"family_seed": f"{f}-seed", "trials": {
            tid: {**s, "trial_seed": f"{tid}-tseed"} for tid, s in v["trials"].items()}}
        for f, v in base.seeds["families"].items()}}  # fmt: skip
    trials = [{**t, "warmup_hours": 10} for t in base.decl.trials]
    declared: dict[str, list[dict[str, Any]]] = {}
    for t in trials:
        declared.setdefault(t["family"], []).append(t)
    decl = dataclasses.replace(base.decl, trials=trials, declared=declared)
    return dataclasses.replace(base, seeds=seeds, decl=decl,
                               signed=cf.signed_c2(sg.protocol()))  # fmt: skip


def payload(tid: str, aid: str, d: list[float]) -> dict[str, Any]:
    return {**tt.payload(tid, aid), "d": [cf.hexf(x) for x in d],
            "d_sha256": cf._floats_sha256(d)}  # fmt: skip


class World(tt.World):
    def __init__(self, tmp: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        super().__init__(tmp, monkeypatch)
        self.calls: dict[str, list[Any]] = {}
        self.available = {"trend": "t1", "vol": "v0"}
        self.mp = monkeypatch

        def nominate(family: str, states: Any, window: Any, completed: Any,
                     hashes: Any, family_seed: Any, rule: Any, classifier: Any,
                     **kw: Any) -> cf.Nomination:  # fmt: skip
            self.record("nominate", (family, states, window, completed, hashes,
                                     family_seed, rule, classifier, kw))  # fmt: skip
            empty = dsr.FamilyResult("NOT_EVALUATED")
            nominee = self.available.get(family)
            return cf.Nomination(nominee is not None, None if nominee else "NO",
                                 nominee, 1.0, empty, empty)  # fmt: skip

        def recorder(name: str, value: Any) -> Any:
            def f(*a: Any, **kw: Any) -> Any:
                self.record(name, (a, kw))
                return value() if callable(value) else value

            return f

        monkeypatch.setattr(cf, "nominate", nominate)
        monkeypatch.setattr(cf, "check_read", recorder("check_read", "rows"))
        monkeypatch.setattr(cf, "trial_path", recorder("trial_path", "path"))
        monkeypatch.setattr(
            cf, "nominee_gates", recorder("nominee_gates", lambda: dict(NOMINEE_GATES))
        )
        monkeypatch.setattr(
            cf, "family_gates", recorder("family_gates", lambda: dict(FAMILY_GATES))
        )
        monkeypatch.setattr(cf, "cpcv_report", recorder("cpcv", {"role": "d"}))
        monkeypatch.setattr(cf, "benchmark_spec_sha256", lambda: "f" * 64)

    def record(self, name: str, value: Any) -> None:
        self.calls.setdefault(name, []).append(value)

    def look(self) -> cf.Look:  # type: ignore[override]
        inp = inputs()
        cycle = cf.cycle_ledger(read_entries(self.path), inp.decl, tt.H)
        fams = {f: cf.family_ledger(
            cycle.pre_look, family=f, cycle="c1", trial_of=inp.trial_of,
            trial_ids=[t["trial_id"] for t in ts], expected=inp.expected,
            window=(inp.w0, inp.t_days))
            for f, ts in inp.decl.declared.items()}  # fmt: skip
        return cf.Look(cycle, fams, tt.W0, "0" * 64,
                       {"trend": BOUNDS, "vol": BOUNDS}, {})  # fmt: skip

    def finish_all(self) -> None:
        for aid, tid, idx, fam in (("attempt-a0", "t0", 0, "trend"),
                                   ("attempt-a1", "t1", 1, "trend"),
                                   ("attempt-b0", "v0", 2, "vol")):  # fmt: skip
            self.start(aid, idx, family=fam)
            self.result(tid, aid)

    def evaluate(self) -> dict[str, cf.FamilyEvaluation]:  # type: ignore[override]
        return cf.evaluate_families(inputs(), self.look(), self.read)

    def read(self) -> Any:
        self.reads += 1
        return ("composite", {"served": 1})


@pytest.fixture
def w(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> World:
    return World(tmp_path, monkeypatch)


def test_every_family_is_nominated_from_the_look_ledger(w: World) -> None:
    w.finish_all()
    got = w.evaluate()
    calls = {c[0]: c for c in w.calls["nominate"]}
    fam, states, window, completed, hashes, fseed, rule, classifier, kw = calls["trend"]
    assert states == {"t0": "completed", "t1": "completed"}
    assert window == (tt.W0, tt.T_DAYS)
    assert set(completed) == {"t0", "t1"}
    assert completed["t0"] == cf.completed_entry(tt.payload("t0", "attempt-a0"),
                                                 (tt.W0, tt.T_DAYS))  # fmt: skip
    assert hashes == {"t0": "c" * 64, "t1": "d" * 64}
    assert (fseed, rule) == ("trend-seed", "largest")
    assert kw["breach"] is None
    assert [r["attempt_id"] for r in kw["results"]] == ["attempt-a0", "attempt-a1"]
    assert got["trend"].completed == completed and set(got) == {"trend", "vol"}


def test_the_classifier_is_the_familys_bounds(
    w: World, monkeypatch: pytest.MonkeyPatch
) -> None:
    from calibration import classifier

    seen: list[Any] = []
    monkeypatch.setattr(classifier, "diagnostics", lambda x: {"x": float(x.sum())})

    def within(v: Any, u: Any, lo: Any) -> bool:
        seen.append((v, u, lo))
        return True

    monkeypatch.setattr(classifier, "within", within)
    assert cf.within_law(BOUNDS)(np.ones((2, 3)), [1.0]) is True
    assert seen == [({"x": 6.0}, BOUNDS[0], BOUNDS[1])]


def test_a_rerun_uses_the_completed_attempts_result(w: World) -> None:
    w.start("attempt-a0", 0)
    w.out("attempt-a0")  # crash, no result
    w.start("attempt-a2", 0)
    append_entry(w.path, record_type=cf.RESULT_ENTRY,
                 payload=payload("t0", "attempt-a2", [1.0, 2.0]))  # fmt: skip
    got = cf.completed_results(inputs(), w.look().families["trend"])
    assert got == {"t0": cf.completed_entry(payload("t0", "attempt-a2", [1.0, 2.0]),
                                            (tt.W0, tt.T_DAYS))}  # fmt: skip


def test_a_breach_is_passed_to_nominate(w: World) -> None:
    w.start("attempt-a1", 1)
    w.out("attempt-a1")
    w.out("attempt-a1")
    w.start("attempt-b0", 2, family="vol")
    w.result("v0", "attempt-b0")
    w.available = {}
    w.evaluate()
    kw = {c[0]: c[8] for c in w.calls["nominate"]}
    assert kw["trend"]["breach"] == "LEDGER_ORDER:attempt-a1"
    assert kw["vol"]["breach"] is None


def test_nominees_get_every_gate_from_one_read(w: World) -> None:
    w.finish_all()
    got = w.evaluate()
    assert w.reads == 1  # once for both nominees
    args, kw = w.calls["check_read"][0]
    assert args == ("composite", {"served": 1})
    assert kw["start"] == tt.W0 - 10 * cf.HOUR and kw["end"] == tt.W0 + 2 * cf.DAY
    ng = {a[0]["trial_id"]: a for a, _ in w.calls["nominee_gates"]}
    assert ng["t1"][1:] == ("path", tt.W0, 48, "t1-tseed", inputs().window_id, 30, 7)
    fg = w.calls["family_gates"][0][0]
    assert fg[1:] == ("2.345", "f" * 64, "b" * 64)  # signed z_crit, G-13 inputs
    for f in ("trend", "vol"):
        assert got[f].outcome == "PROCEEDS_TO_LOCKBOX"
        assert set(got[f].gates) == set(cf.GATES) and got[f].path == "path"
        assert got[f].cpcv == {"role": "d"}
    cp = w.calls["cpcv"][0][0]
    assert cp[1:] == ("path", tt.W0, 48, 7, cf.Gate(cf.PASS))


def test_no_nominee_means_no_read(w: World) -> None:
    w.finish_all()
    w.available = {}
    got = w.evaluate()
    assert w.reads == 0 and "check_read" not in w.calls
    assert all(e.gates == {} and e.outcome is None for e in got.values())


def test_a_missing_benchmark_spec_makes_g13_unavailable(
    w: World, monkeypatch: pytest.MonkeyPatch
) -> None:
    w.finish_all()
    monkeypatch.setattr(cf, "benchmark_spec_sha256", lambda: None)
    got = w.evaluate()
    assert got["trend"].gates["G-13"] == cf._unavailable("BENCHMARK_SPEC_MISSING")
    assert got["trend"].outcome == "NO_RESULT"


def test_a_failing_gate_fails_the_nominee(
    w: World, monkeypatch: pytest.MonkeyPatch
) -> None:
    w.finish_all()
    bad = {**NOMINEE_GATES, "G-2": cf.Gate(cf.FAIL)}
    monkeypatch.setattr(cf, "nominee_gates", lambda *a, **k: dict(bad))
    assert w.evaluate()["vol"].outcome == "FAILED"


def test_a_bad_read_is_refused(w: World, monkeypatch: pytest.MonkeyPatch) -> None:
    w.finish_all()
    with pytest.raises(cf.CycleError, match="did not serve"):
        cf.evaluate_families(inputs(), w.look(), lambda: "composite")


def test_benchmark_spec_sha256_hashes_the_engine_file(tmp_path: Path) -> None:
    assert cf.benchmark_spec_sha256(tmp_path) is None
    spec = tmp_path / cf.BENCHMARK_SPEC
    spec.parent.mkdir()
    spec.write_bytes(b"benchmarks v1.1")
    assert (
        cf.benchmark_spec_sha256(tmp_path)
        == hashlib.sha256(b"benchmarks v1.1").hexdigest()
    )


def test_an_earlier_completed_attempt_is_not_used_when_the_last_runs(w: World) -> None:
    """FINAL-F-2 in a breached family: t0's last attempt runs, so t0 is not
    completed although an earlier attempt has a result."""
    w.start("attempt-a1", 1)
    w.out("attempt-a1")
    w.out("attempt-a1")  # breach
    w.start("attempt-a0", 0)
    w.result("t0", "attempt-a0")
    w.start("attempt-a2", 0)  # a later attempt of t0, running
    fam = w.look().families["trend"]
    assert fam.states["t0"] == "running"
    assert cf.completed_results(inputs(), fam) == {}


def test_each_nominee_is_cut_with_its_own_warm_up(
    w: World, monkeypatch: pytest.MonkeyPatch
) -> None:
    w.finish_all()
    inp = inputs()
    trials = [{**t, "warmup_hours": 10 if t["family"] == "trend" else 30}
              for t in inp.decl.trials]  # fmt: skip
    declared: dict[str, list[dict[str, Any]]] = {}
    for t in trials:
        declared.setdefault(t["family"], []).append(t)
    decl = dataclasses.replace(inp.decl, trials=trials, declared=declared)
    cf.evaluate_families(dataclasses.replace(inp, decl=decl), w.look(), w.read)
    starts = sorted(kw["start"] for _, kw in w.calls["check_read"])
    assert starts == [tt.W0 - 30 * cf.HOUR, tt.W0 - 10 * cf.HOUR] and w.reads == 1


def test_an_error_in_the_diagnostic_does_not_abort_the_look(
    w: World, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R14B6F-F-6: C-14 is diagnostic only (§9); its failure is recorded."""
    w.finish_all()

    def boom(*a: Any) -> None:
        raise KeyError("ess")

    monkeypatch.setattr(cf, "cpcv_report", boom)
    got = w.evaluate()
    for f in ("trend", "vol"):
        assert got[f].cpcv == {"role": cf.CPCV_ROLE, "status": cf.UNAVAILABLE,
                               "reason": "C14_ERROR:KeyError"}  # fmt: skip
        assert got[f].outcome == "PROCEEDS_TO_LOCKBOX"  # gates untouched
