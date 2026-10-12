"""The qualification object builder (`calibration/qobj.py`), on synthetic
chains only."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from calibration import chunks, qobj, reduce, rundef
from calibration.seeds import cj

CELL = {"cell_id": "gaussian.independent.k1.t1240", "k": 1, "t": 1240,
        "law": "gaussian", "dependence": "independent"}  # fmt: skip
GATING = {"image_digest": "sha256:" + "ab" * 32}


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                          text=True, check=True).stdout.strip()  # fmt: skip


def _repo(tmp: Path, files: dict[str, bytes]) -> tuple[Path, str]:
    tmp.mkdir()
    _git(tmp, "init", "-q")
    for name, data in files.items():
        (tmp / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp / name).write_bytes(data)
    _git(tmp, "add", "-A")
    _git(tmp, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x")
    return tmp, _git(tmp, "rev-parse", "HEAD")


def test_the_definition_must_be_committed_before_the_run_started(
    tmp_path: Path,
) -> None:
    root, commit = _repo(tmp_path / "r", {"defs/d.json": b"{}"})
    later = datetime.now(UTC) + timedelta(hours=1)
    assert qobj.committed_before(root, commit, "defs/d.json", b"{}", later) > 0
    with pytest.raises(ValueError, match="after the start"):
        qobj.committed_before(root, commit, "defs/d.json", b"{}",
                              datetime.now(UTC) - timedelta(days=1))  # fmt: skip
    with pytest.raises(ValueError, match="not this run definition"):
        qobj.committed_before(root, commit, "defs/d.json", b"{ }", later)
    with pytest.raises(ValueError, match="not found"):
        qobj.committed_before(root, commit, "defs/other.json", b"{}", later)
    with pytest.raises(ValueError, match="time zone"):
        qobj.committed_before(root, commit, "defs/d.json", b"{}", datetime(2030, 1, 1))


def _chain(store: Path, ns: str, host: dict[str, object]) -> chunks.Chain:
    return chunks.Chain(store / ns / CELL["cell_id"], "b" * 64, ns,
                        str(CELL["cell_id"]), 2, GATING, host)  # fmt: skip


def test_host_provenance_is_fixed_per_chain(tmp_path: Path) -> None:  # S16-4
    chain = _chain(tmp_path, "threshold", {"cpu_model": "A"})
    chunks.run(chain, lambda rep: rep)
    before = qobj.host_sha256(chain)
    path = chain.path(0)  # host is outside the chunk digest by design
    record = json.loads(path.read_bytes())
    record["host"] = {"cpu_model": "B"}
    path.write_bytes(cj(record))
    assert chunks.verify(chain)  # the chain still verifies
    assert qobj.host_sha256(chain) != before  # but the object's hash moves


def _setup(tmp_path: Path, qualifies: bool = True, purpose: str = "qualification"):  # type: ignore[no-untyped-def]
    prereg = b"accepted preregistration\n"
    explore = cj({"manifest_sha256": "e" * 64})
    defn = {"record_type": rundef.RECORD_TYPE, "prereg_sha256":
            hashlib.sha256(prereg).hexdigest(), "exploration_manifest_sha256":
            "e" * 64, "gating": GATING,
            "cell_manifest": {"purpose": purpose, "cells": [CELL],
                              "replications": {"threshold": 2, "dev": 2}}}  # fmt: skip
    data = cj(defn)
    later = {s: b"later " + s.encode() for s in qobj.LATER.values()}
    later[qobj.LATER["preregistration.md"]] = prereg
    root, commit = _repo(tmp_path / "root", {**later, "runs/definition.json": data})
    run_root = tmp_path / "run"
    for src in qobj.ENGINE.values():
        (run_root / src).parent.mkdir(parents=True, exist_ok=True)
        (run_root / src).write_bytes(b"engine " + src.encode())
    (tmp_path / "definition.json").write_bytes(data)
    (tmp_path / "explore.json").write_bytes(explore)
    store = tmp_path / "store"
    binding = rundef.definition_sha256(defn)
    heads = {}
    for ns in qobj.NAMESPACES:
        chain = chunks.Chain(store / ns / CELL["cell_id"], binding, ns,
                             str(CELL["cell_id"]), 2, GATING, {"cpu": ns})  # fmt: skip
        heads[f"{ns}/{CELL['cell_id']}"] = chunks.run(chain, lambda rep: rep)
    report = {"qualifies": qualifies, "margin_ok": True, "chain_heads": heads,
              "cells": {CELL["cell_id"]: {"status": "qualifying",
                                          "held_out": 20000}}}  # fmt: skip
    (tmp_path / "choices.json").write_bytes(cj(report))
    kwargs = {
        "root": root,
        "run_root": run_root,
        "definition": tmp_path / "definition.json",
        "definition_repo_path": "runs/definition.json",
        "definition_commit": commit,
        "threshold_started": datetime.now(UTC) + timedelta(hours=1),
        "store": store,
        "choices_json": tmp_path / "choices.json",
        "exploration_manifest": tmp_path / "explore.json",
        "out": tmp_path / "obj",
    }
    return kwargs


@pytest.fixture
def fakes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stand-ins for the parts whose own tests cover them: the fresh choose
    (it must equal choices.json), the run plan (qualification is refused
    until BO-1), and the per-cell threshold fit."""
    monkeypatch.setattr(
        qobj, "_choose", lambda r, d, s: (d.parent / "choices.json").read_bytes()
    )
    monkeypatch.setattr(rundef, "run_plan", lambda m: m["replications"])
    fit = [({"K": 1.0}, {"K": 0.5})]
    monkeypatch.setattr(reduce, "cell_thresholds", lambda chain, joint=False: fit)


def test_a_qualifying_run_gives_an_object_hashed_by_its_manifest(
    tmp_path: Path, fakes: None
) -> None:
    kwargs = _setup(tmp_path)
    digest = qobj.build(**kwargs)
    out = kwargs["out"]
    manifest = json.loads((out / "manifest.json").read_bytes())
    assert digest == hashlib.sha256(cj(manifest)).hexdigest()
    for name, h in manifest.items():
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() == h
    assert set(manifest) >= set(qobj.ENGINE) | set(qobj.LATER) | {
        "definition.json",
        "freeze.json",
    }
    freeze = json.loads((out / "freeze.json").read_bytes())
    assert set(freeze["host_provenance_sha256"]) == {
        f"{ns}/{CELL['cell_id']}" for ns in qobj.NAMESPACES
    }
    assert freeze["allocation"] == {CELL["cell_id"]: 20000}
    own = json.loads((out / "cell_thresholds.json").read_bytes())
    assert own[CELL["cell_id"]]["upper"] == {"K": (1.0).hex()}


def _not_qualifying(k, p):  # type: ignore[no-untyped-def]
    (p / "choices.json").write_bytes(cj({"qualifies": False, "margin_ok": True}))


def _no_screen(k, p):  # type: ignore[no-untyped-def]
    (k["root"] / qobj.LATER["screen.py"]).unlink()


def _other_exploration(k, p):  # type: ignore[no-untyped-def]
    (p / "explore.json").write_bytes(cj({"manifest_sha256": "f" * 64}))


def _other_prereg(k, p):  # type: ignore[no-untyped-def]
    (k["root"] / qobj.LATER["preregistration.md"]).write_bytes(b"other")


def _started_earlier(k, p):  # type: ignore[no-untyped-def]
    k["threshold_started"] = datetime(2000, 1, 1, tzinfo=UTC)


def _out_not_empty(k, p):  # type: ignore[no-untyped-def]
    k["out"].mkdir()
    (k["out"] / "x").write_bytes(b"")


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (_not_qualifying, "does not qualify"),
        (_no_screen, "sources missing"),
        (_other_exploration, "exploration manifest"),
        (_other_prereg, "preregistration"),
        (_started_earlier, "after the start"),
        (_out_not_empty, "not empty"),
    ],
)
def test_the_builder_refuses(  # type: ignore[no-untyped-def]
    tmp_path: Path, fakes: None, change, message: str
) -> None:
    kwargs = _setup(tmp_path)
    change(kwargs, tmp_path)
    with pytest.raises(ValueError, match=message):
        qobj.build(**kwargs)


def test_a_chain_that_differs_from_choices_is_refused(
    tmp_path: Path, fakes: None
) -> None:
    kwargs = _setup(tmp_path)
    report = json.loads((tmp_path / "choices.json").read_bytes())
    report["chain_heads"][f"dev/{CELL['cell_id']}"] = "0" * 64
    (tmp_path / "choices.json").write_bytes(cj(report))
    with pytest.raises(ValueError, match="chain head differs"):
        qobj.build(**kwargs)


def test_a_fresh_choose_that_differs_is_refused(
    tmp_path: Path, fakes: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    kwargs = _setup(tmp_path)
    monkeypatch.setattr(qobj, "_choose", lambda r, d, s: b"{}")
    with pytest.raises(ValueError, match="fresh choose"):
        qobj.build(**kwargs)
    assert not kwargs["out"].exists()  # nothing written
