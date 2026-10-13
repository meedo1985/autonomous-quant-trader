"""Held-out certification runner (scripts/d19_heldout.py, prereg §6, §8)."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from calibration import choices, classifier, dsr, reduce
from calibration.generator import Cell
from calibration.seeds import cj, sha

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "d19_heldout.py"
_spec = importlib.util.spec_from_file_location("d19_heldout_under_test", SCRIPT)
assert _spec is not None and _spec.loader is not None
heldout = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(heldout)

QOBJ = "c" * 64
WIDE = 1e300  # a classifier that accepts every draw


def _thresholds(t: int) -> dict[str, dict[str, float]]:
    return {
        "upper": {"T": float(t)} | dict.fromkeys(classifier.UPPER, WIDE),
        "lower": {"T": float(t)} | dict.fromkeys(classifier.LOWER, -WIDE),
    }


def _cells() -> list[dict[str, object]]:
    return [
        {"cell_id": "c-k2", "k": 2, "t": 64, "law": "gaussian",
         "dependence": "independent"},
        {"cell_id": "d-k1", "k": 1, "t": 64, "law": "gaussian",
         "dependence": "independent"},
    ]  # fmt: skip


def _fixture(n: int = 3) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    tests = choices.test_manifest([("c-k2", "gaussian"), ("d-k1", "gaussian")])
    report = {
        "m": len(tests),
        "tests": tests,
        "z_crit": "1.96",
        "family_block_rule": "largest",
        "qualifies": True,
        "margin_ok": True,
        "cells": {
            "c-k2": {"status": "qualifying", "held_out": n},
            "d-k1": {"status": "demoted_availability", "held_out": None},
        },
        "final_thresholds": {"T=64": _thresholds(64)},
    }
    defn = {
        "cell_manifest": {"cells": _cells()},
        "prereg_sha256": "p" * 64,
        "gating": {"identity": "x"},
        "engine_commit": "e",
    }
    return report, defn, {"allocation": {"c-k2": n}}


@pytest.fixture
def cheap(monkeypatch: pytest.MonkeyPatch) -> None:
    """Method V marked verified and U_G available: one replication is fast."""
    monkeypatch.setattr(dsr, "_V_VERIFIED", True)
    monkeypatch.setattr(heldout.d19_run.gates, "u_g", lambda *a, **k: None)


def test_namespace_and_anchor_follow_section_8() -> None:
    assert heldout.namespace(1) == "d19-heldout-v1"
    assert heldout.namespace(2) == "d19-heldout-v2"
    with pytest.raises(ValueError, match="attempt"):
        heldout.namespace(3)
    expected = hashlib.sha256(
        b'{"beacon_randomness":"' + b"a" * 64 + b'","qobj":"' + QOBJ.encode()
        + b'","round":7}'
    ).hexdigest()  # fmt: skip
    assert heldout.anchor(QOBJ, 7, "a" * 64) == expected
    with pytest.raises(ValueError, match="64 lowercase hex"):
        heldout.anchor(QOBJ, 7, "A" * 64)
    with pytest.raises(ValueError, match="positive integer"):
        heldout.anchor(QOBJ, 0, "a" * 64)


def test_a_replication_is_the_development_record_under_held_out_seeds(
    cheap: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    cell = Cell("c-k2", 2, 64)
    bounds = reduce.for_k(tuple(_thresholds(64).values()), 2)  # type: ignore[arg-type]
    ns, anchor = "d19-heldout-v1", "a" * 64
    record = heldout.replication(cell, anchor, ns, "p" * 64, 4, bounds)
    assert choices.consistent(record, bounds) is None
    monkeypatch.setitem(heldout.d19_run.NAMESPACES, "dev", ns)
    assert record == heldout.d19_run.dev_replication(cell, anchor, "p" * 64, 4, bounds)
    other = heldout.replication(cell, anchor, "d19-heldout-v2", "p" * 64, 4, bounds)
    assert other["diagnostics"] != record["diagnostics"]


def test_plan_runs_the_final_cells_at_their_allocation_with_frozen_thresholds() -> None:
    report, defn, freeze = _fixture(20_000)
    [(cell, n, (upper, lower))] = heldout.plan(report, defn, freeze)
    assert (cell.cell_id, n) == ("c-k2", 20_000)
    assert upper["K"] == 2.0 and set(lower) == {"K", "T", *classifier.LOWER}
    with pytest.raises(ValueError, match="outside the cell manifest"):
        heldout.plan(report, defn, {"allocation": {"c-k2": 20_000, "x": 20_000}})


def _rep(error: bool = False, dsr_: bool = False, u_g: bool = False) -> choices.Rep:
    if dsr_:
        return choices.Rep("UNSUPPORTED_LAW", None, None)
    return choices.Rep(None, 3.0 if error else 0.5, "G-1" if u_g else None)


def test_tally_counts_each_test_and_skips_demoted_cells() -> None:
    tests = choices.test_manifest([("a", "gaussian"), ("q", "semi-joint"), ("d", "t5")])
    cells = {u: {"status": "qualifying"} for u in ("a", "q/trend", "q/vol")}
    cells["d"] = {"status": "demoted_availability"}
    report = {"m": len(tests), "tests": tests, "z_crit": "1.96", "cells": cells}
    n = 20_000
    a = [_rep(error=i < 300, dsr_=300 <= i < 305, u_g=i == 305) for i in range(n)]
    trend = [_rep(error=i < 500) for i in range(n)]
    vol = [_rep(error=200 <= i < 600, u_g=i == 1) for i in range(n)]
    result = heldout.tally(report, {"a": a, "q/trend": trend, "q/vol": vol})
    rows = {tuple(t["test"]): t for t in result["tests"]}
    assert result["m"] == 3 + 8 + 3 and result["alpha"] == 0.025 / 14
    assert [rows["a", "agnostic", k]["events"] for k in ("error", "dsr", "u_g")] == [
        300, 5, 1,
    ]  # fmt: skip
    assert rows["q", "joint", "error_joint"]["events"] == 600  # either family
    assert rows["q", "joint", "u_proc_joint"]["events"] == 1
    assert not rows["d", "agnostic", "error"]["run"]
    assert rows["q", "joint", "error_joint"]["within"] is True  # 600/20k vs 0.05
    assert rows["a", "agnostic", "error"]["within"] is True
    assert result["accepted"] is False  # q/trend: 500/20k, UCB above 0.025
    assert rows["q/trend", "trend", "error"]["within"] is False
    vol_missing = {"a": a, "q/trend": trend}
    with pytest.raises(ValueError, match="q/vol error: a qualifying unit"):
        heldout.tally(report, vol_missing)
    half = {**cells, "q/vol": {"status": "demoted_availability"}}
    with pytest.raises(ValueError, match="qualifying unit has no replications"):
        heldout.tally(report | {"cells": half}, {"a": a, "q/trend": trend})


def test_tally_accepts_when_every_run_test_is_within() -> None:
    tests = choices.test_manifest([("a", "gaussian")])
    reps = {"a": [_rep(error=i < 100) for i in range(20_000)]}
    report = {"m": 3, "tests": tests, "z_crit": "1.96",
              "cells": {"a": {"status": "qualifying"}}}  # fmt: skip
    assert heldout.tally(report, reps)["accepted"] is True
    with pytest.raises(ValueError, match="M tests"):
        heldout.tally(report | {"m": 4}, reps)
    with pytest.raises(ValueError, match="a qualifying unit has no replications"):
        heldout.tally(report, {})


def test_the_attempt_inputs_are_written_once(tmp_path: Path) -> None:
    record = {"anchor": "x", "round": 1}
    heldout.attempt_record(tmp_path, "d19-heldout-v1", record)
    heldout.attempt_record(tmp_path, "d19-heldout-v1", record)
    with pytest.raises(ValueError, match="another attempt"):
        heldout.attempt_record(tmp_path, "d19-heldout-v1", {**record, "round": 2})
    assert (tmp_path / "heldout-v1" / "attempt.json").read_bytes() == cj(record)
    assert [p.name for p in (tmp_path / "heldout-v1").iterdir()] == ["attempt.json"]


def test_certify_rebuilds_the_anchor_from_the_attempt_record(tmp_path: Path) -> None:
    ns = "d19-heldout-v1"
    with pytest.raises(ValueError, match="no attempt record"):
        heldout.recorded_anchor(tmp_path, ns, QOBJ)
    key = heldout.anchor(QOBJ, 9, "b" * 64)
    record = {"anchor": key, "beacon_randomness": "b" * 64, "qobj": QOBJ, "round": 9}
    heldout.attempt_record(tmp_path, ns, record)
    assert heldout.recorded_anchor(tmp_path, ns, QOBJ) == key
    with pytest.raises(ValueError, match="not this object's attempt record"):
        heldout.recorded_anchor(tmp_path, ns, "d" * 64)
    (tmp_path / "heldout-v1" / "attempt.json").write_bytes(cj(record | {"anchor": "0"}))
    with pytest.raises(ValueError, match="not this object's attempt record"):
        heldout.recorded_anchor(tmp_path, ns, QOBJ)
    assert heldout.binding(QOBJ, key) == sha(
        {"anchor": key, "qualification_object_sha256": QOBJ}
    )


def _object(tmp_path: Path, files: dict[str, bytes]) -> tuple[Path, str]:
    obj = tmp_path / "obj"
    obj.mkdir()
    for name, data in files.items():
        (obj / name).write_bytes(data)
    manifest = {n: hashlib.sha256(d).hexdigest() for n, d in files.items()}
    (obj / "manifest.json").write_bytes(cj(manifest))
    return obj, sha(manifest)


def _head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()  # fmt: skip


def _gate_object(
    tmp_path: Path, change: dict[str, Any] | None = None, runner: bytes | None = None
) -> tuple[Path, str]:
    report, defn, freeze = _fixture(20_000)
    defn["engine_commit"] = _head()
    parts = {"choices.json": report, "definition.json": defn, "freeze.json": freeze}
    for key, value in (change or {}).items():
        name, field = key.split("__")
        parts[f"{name}.json"][field] = value
    files = {n: cj(v) for n, v in parts.items()}
    files["mapping.py"] = b"reviewed mapping"
    files["heldout.py"] = runner or SCRIPT.read_bytes()
    return _object(tmp_path, files)


def test_gate_checks_the_object_engine_runtime_and_this_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[object] = []
    monkeypatch.setattr(heldout.mapping, "check_engine", lambda *a: calls.append(a))
    monkeypatch.setattr(heldout.mapping, "check_runtime", lambda d: calls.append(d))
    obj, posted = _gate_object(tmp_path)
    report, defn, freeze = heldout.gate(obj, posted)
    assert calls == [(defn, heldout.ROOT, b"reviewed mapping"), defn]
    assert freeze == {"allocation": {"c-k2": 20_000}}
    with pytest.raises(ValueError, match="not the posted one"):
        heldout.gate(obj, "0" * 64)
    (obj / "heldout.py").write_bytes(b"edited")
    with pytest.raises(ValueError, match="heldout.py does not match"):
        heldout.gate(obj, posted)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"definition__engine_commit": "f" * 40}, "not readable"),
        ({"choices__qualifies": False}, "does not qualify"),
        ({"choices__m": 5}, "test manifest"),
        ({"choices__tests": []}, "test manifest"),
        ({"freeze__allocation": {"c-k2": 40_000}}, "allocation"),
        (
            {
                "freeze__allocation": {"c-k2": 3},
                "choices__cells": {"c-k2": {"status": "qualifying", "held_out": 3}},
            },
            "allocation",
        ),  # fmt: skip
    ],
)
def test_gate_refuses(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    change: dict[str, object],
    message: str,
) -> None:
    monkeypatch.setattr(heldout.mapping, "check_engine", lambda *a: None)
    monkeypatch.setattr(heldout.mapping, "check_runtime", lambda d: None)
    obj, posted = _gate_object(tmp_path, change)
    with pytest.raises(ValueError, match=message):
        heldout.gate(obj, posted)


def test_gate_refuses_another_runner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(heldout.mapping, "check_engine", lambda *a: None)
    monkeypatch.setattr(heldout.mapping, "check_runtime", lambda d: None)
    obj, posted = _gate_object(tmp_path, runner=SCRIPT.read_bytes() + b"# edit")
    with pytest.raises(ValueError, match="not the object's heldout.py"):
        heldout.gate(obj, posted)


def test_run_then_certify(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    cheap: None,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """End to end in one process: run prints chain heads only (P18-6), a
    resume with other beacon inputs is refused, certify reduces."""
    fixture = _fixture(3)
    monkeypatch.setattr(heldout, "gate", lambda obj, posted: fixture)
    monkeypatch.setattr(
        heldout, "_pool", lambda jobs: [heldout.worker(*j) for j in jobs]
    )
    store = tmp_path / "store"
    common = ["--object", str(tmp_path), "--posted", QOBJ, "--attempt", "1",
              "--store", str(store)]  # fmt: skip
    beacon = ["--round", "9", "--randomness", "b" * 64]
    assert heldout.main(["run", *common, *beacon]) == 0
    out = capsys.readouterr().out.splitlines()
    assert len(out) == 1 and out[0].startswith("d19-heldout-v1/c-k2: ")
    assert heldout.main(["run", *common, *beacon]) == 0  # resume: same head
    assert capsys.readouterr().out.splitlines() == out
    other = ["--round", "10", "--randomness", "b" * 64]
    assert heldout.main(["run", *common, *other]) == 1
    assert "another attempt" in capsys.readouterr().err
    chunk = json.loads(
        (store / "heldout-v1" / "c-k2" / "chunk-0000000.json").read_bytes()
    )
    key = heldout.anchor(QOBJ, 9, "b" * 64)
    assert chunk["binding"] == heldout.binding(QOBJ, key)
    assert chunk["namespace"] == "d19-heldout-v1"
    # HO-R1: a lost attempt record cannot let another anchor resume the chain
    attempt = store / "heldout-v1" / "attempt.json"
    kept = attempt.read_bytes()
    attempt.unlink()
    assert heldout.main(["run", *common, *other]) == 1
    assert "binding does not match" in capsys.readouterr().err
    attempt.write_bytes(kept)

    report = tmp_path / "report.json"
    code = heldout.main(["certify", *common, "--out", str(report)])
    result = json.loads(report.read_text("utf-8"))
    assert code == 2 and result["accepted"] is False  # 3 replications bound nothing
    assert result["chain_heads"] == {"c-k2": out[0].split(": ")[1]}
    rows = {tuple(t["test"]): t for t in result["tests"]}
    assert rows["c-k2", "agnostic", "dsr"] | {"ucb": 0} == {
        "test": ["c-k2", "agnostic", "dsr"], "run": True, "n": 3, "events": 0,
        "ucb": 0, "bound": 0.0035, "within": False,
    }  # fmt: skip
    assert not rows["d-k1", "agnostic", "error"]["run"]


def test_certify_refuses_an_incomplete_chain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(heldout, "gate", lambda obj, posted: _fixture(3))
    report, store = tmp_path / "report.json", tmp_path / "store"
    args = ["certify", "--object", str(tmp_path), "--posted", QOBJ,
            "--attempt", "1", "--store", str(store), "--out", str(report)]  # fmt: skip
    assert heldout.main(args) == 1 and "no attempt record" in capsys.readouterr().err
    key = heldout.anchor(QOBJ, 9, "b" * 64)
    record = {"anchor": key, "beacon_randomness": "b" * 64, "qobj": QOBJ, "round": 9}
    heldout.attempt_record(store, "d19-heldout-v1", record)
    assert heldout.main(args) == 1 and "chain missing" in capsys.readouterr().err
    assert not report.exists()
