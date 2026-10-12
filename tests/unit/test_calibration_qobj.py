"""The qualification object builder (`calibration/qobj.py`), on synthetic
chains only."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from calibration import chunks, qobj, rundef
from calibration.seeds import cj

CELL = {"cell_id": "gaussian.independent.k1.t1240", "k": 1, "t": 1240,
        "law": "gaussian", "dependence": "independent"}  # fmt: skip
GATING = {"image_digest": "sha256:" + "ab" * 32}


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                          text=True, check=True).stdout.strip()  # fmt: skip


def _repo(tmp: Path, files: dict[str, bytes], push: bool = True) -> tuple[Path, str]:
    """A repository with `files` committed; with `push`, also on a remote
    branch (S16-2, QO-2)."""
    tmp.mkdir()
    _git(tmp, "init", "-q")
    for name, data in files.items():
        (tmp / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp / name).write_bytes(data)
    _git(tmp, "add", "-A")
    _git(tmp, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x")
    if push:
        remote = tmp.with_name(tmp.name + ".git")
        _git(tmp.parent, "init", "-q", "--bare", str(remote))
        _git(tmp, "remote", "add", "origin", str(remote))
        _git(tmp, "push", "-q", "origin", "HEAD:refs/heads/main")
        _git(tmp, "fetch", "-q", "origin")
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
    local, unpushed = _repo(tmp_path / "l", {"defs/d.json": b"{}"}, push=False)
    with pytest.raises(ValueError, match="cannot read the remote"):
        qobj.committed_before(local, unpushed, "defs/d.json", b"{}", later)
    # QO-2: a stale local tracking ref does not count once the remote lost it
    _git(root.with_name(root.name + ".git"), "update-ref", "-d", "refs/heads/main")
    assert _git(root, "branch", "-r", "--contains", commit)  # stale ref remains
    with pytest.raises(ValueError, match="on no branch of origin"):
        qobj.committed_before(root, commit, "defs/d.json", b"{}", later)


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


def _setup(tmp_path: Path):  # type: ignore[no-untyped-def]
    prereg = b"accepted preregistration\n"
    explore = cj({"manifest_sha256": "e" * 64})
    defn = {"record_type": rundef.RECORD_TYPE, "prereg_sha256":
            hashlib.sha256(prereg).hexdigest(), "exploration_manifest_sha256":
            "e" * 64, "gating": GATING,
            "cell_manifest": {"purpose": "qualification", "cells": [CELL],
                              "replications": dict(rundef.PRESCRIBED)}}  # fmt: skip
    data = cj(defn)
    later = {s: b"later " + s.encode() for s in qobj.LATER.values()}
    later[qobj.LATER["preregistration.md"]] = prereg
    reviews = {
        name: {"sha256": hashlib.sha256(later[qobj.LATER[name]]).hexdigest(),
               "record": f"review/{name}.md"}
        for name in qobj.REVIEWED
    }  # fmt: skip
    records = {f"review/{name}.md": b"accepted" for name in qobj.REVIEWED}
    root, commit = _repo(
        tmp_path / "root",
        {**later, **records, qobj.FREEZE_REVIEWS: cj(reviews),
         "runs/definition.json": data},
    )  # fmt: skip
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
                             str(CELL["cell_id"]), rundef.PRESCRIBED[ns], GATING,
                             {"cpu": ns})  # fmt: skip
        heads[f"{ns}/{CELL['cell_id']}"] = chunks.run(chain, lambda rep: rep)
    report: dict[str, object] = {k: None for k in qobj.REPORT}
    report |= {"m": 3, "tests": [[CELL["cell_id"], "agnostic", b]
                                 for b in ("error", "dsr", "u_g")]}  # fmt: skip
    report |= {"qualifies": True, "margin_ok": True, "chain_heads": heads,
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
    """Small prescribed counts, so the synthetic chains stay small, and a
    stand-in for the fresh choose (it must equal choices.json), which runs
    the start gate of a real pinned checkout."""
    monkeypatch.setattr(rundef, "PRESCRIBED", {"threshold": 3, "dev": 2})
    monkeypatch.setattr(
        qobj, "_choose", lambda r, d, s: (d.parent / "choices.json").read_bytes()
    )


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
    assert not out.with_name(out.name + ".partial").exists()  # QO-7: renamed


def _not_qualifying(k, p):  # type: ignore[no-untyped-def]
    report = json.loads((p / "choices.json").read_bytes())
    report["qualifies"] = False
    (p / "choices.json").write_bytes(cj(report))


def _no_screen(k, p):  # type: ignore[no-untyped-def]
    (k["root"] / qobj.LATER["screen.py"]).unlink()


def _other_exploration(k, p):  # type: ignore[no-untyped-def]
    (p / "explore.json").write_bytes(cj({"manifest_sha256": "f" * 64}))


def _other_prereg(k, p):  # type: ignore[no-untyped-def]
    (k["root"] / qobj.LATER["preregistration.md"]).write_bytes(b"other")


def _started_earlier(k, p):  # type: ignore[no-untyped-def]
    k["threshold_started"] = datetime(2000, 1, 1, tzinfo=UTC)


def _out_exists(k, p):  # type: ignore[no-untyped-def]
    k["out"].mkdir()


def _commit_all(root: Path) -> None:
    _git(root, "add", "-A")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "y")


def _unreviewed_screen(k, p):  # type: ignore[no-untyped-def]
    (k["root"] / qobj.LATER["screen.py"]).write_bytes(b"changed after review")
    _commit_all(k["root"])


def _no_review_record(k, p):  # type: ignore[no-untyped-def]
    (k["root"] / "review" / "heldout.py.md").unlink()
    _commit_all(k["root"])


def _short_test_manifest(k, p):  # type: ignore[no-untyped-def]
    report = json.loads((p / "choices.json").read_bytes())
    report["tests"] = report["tests"][:2]
    (p / "choices.json").write_bytes(cj(report))


def _uncommitted_mapping(k, p):  # type: ignore[no-untyped-def]
    (k["root"] / qobj.LATER["mapping.py"]).write_bytes(b"edited, not committed")


def _review_record_is_a_directory(k, p):  # type: ignore[no-untyped-def]
    reviews = json.loads((k["root"] / qobj.FREEZE_REVIEWS).read_bytes())
    reviews["screen.py"]["record"] = "review"  # a tracked directory
    (k["root"] / qobj.FREEZE_REVIEWS).write_bytes(cj(reviews))
    _commit_all(k["root"])


def _review_record_is_a_symlink(k, p):  # type: ignore[no-untyped-def]
    # a committed symbolic link (mode 120000) to a missing file, built in the
    # index directly so the test runs where links cannot be created (QOR3-1)
    link = _git(k["root"], "hash-object", "-w", "--stdin")  # empty blob
    _git(k["root"], "update-index", "--add", "--cacheinfo",
         f"120000,{link},review/link.md")  # fmt: skip
    reviews = json.loads((k["root"] / qobj.FREEZE_REVIEWS).read_bytes())
    reviews["screen.py"]["record"] = "review/link.md"
    (k["root"] / qobj.FREEZE_REVIEWS).write_bytes(cj(reviews))
    _git(k["root"], "add", qobj.FREEZE_REVIEWS)
    _git(
        k["root"],
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "commit",
        "-q",
        "-m",
        "z",
    )


def _report_lacks_z_crit(k, p):  # type: ignore[no-untyped-def]
    report = json.loads((p / "choices.json").read_bytes())
    del report["z_crit"]
    (p / "choices.json").write_bytes(cj(report))


def _other_counts(k, p):  # type: ignore[no-untyped-def]
    defn = json.loads((p / "definition.json").read_bytes())
    defn["cell_manifest"]["replications"]["dev"] = 1
    (p / "definition.json").write_bytes(cj(defn))


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (_not_qualifying, "does not qualify"),
        (_no_screen, "sources missing"),
        (_other_exploration, "exploration manifest"),
        (_other_prereg, "preregistration"),
        (_started_earlier, "after the start"),
        (_out_exists, "already exists"),
        (_unreviewed_screen, "not the reviewed version"),
        (_no_review_record, "no committed review record"),
        (_review_record_is_a_directory, "no committed review record"),
        (_review_record_is_a_symlink, "no committed review record"),
        (_report_lacks_z_crit, "lacks"),
        (_short_test_manifest, "M tests"),
        (_uncommitted_mapping, "not committed as it stands"),
        (_other_counts, "prescribed counts"),
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


def test_a_chain_changed_during_the_build_is_refused(
    tmp_path: Path, fakes: None, monkeypatch: pytest.MonkeyPatch
) -> None:  # QO-6
    kwargs = _setup(tmp_path)
    chosen = (tmp_path / "choices.json").read_bytes()
    chunk = kwargs["store"] / "dev" / CELL["cell_id"] / "chunk-0000000.json"

    def choose_then_tamper(r, d, s):  # type: ignore[no-untyped-def]
        chunk.unlink()
        return chosen

    monkeypatch.setattr(qobj, "_choose", choose_then_tamper)
    with pytest.raises(chunks.ChainError):
        qobj.build(**kwargs)
    assert not kwargs["out"].exists()


def test_a_host_change_during_staging_is_refused(
    tmp_path: Path, fakes: None, monkeypatch: pytest.MonkeyPatch
) -> None:  # QO-6: the host lists are rechecked just before publishing
    kwargs = _setup(tmp_path)
    chunk = kwargs["store"] / "dev" / CELL["cell_id"] / "chunk-0000000.json"
    real = qobj.cj

    def cj_then_tamper(value):  # type: ignore[no-untyped-def]
        out = real(value)
        if isinstance(value, dict) and "freeze.json" in value:  # the manifest
            record = json.loads(chunk.read_bytes())
            record["host"] = {"cpu": "changed"}
            chunk.write_bytes(real(record))
        return out

    monkeypatch.setattr(qobj, "cj", cj_then_tamper)
    with pytest.raises(ValueError, match="host provenance changed"):
        qobj.build(**kwargs)
    assert not kwargs["out"].exists()
