import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from calibration import classifier, grid, mapping, rundef
from calibration.seeds import cj, sha


def _x(k: int, t: int = grid.T_C2 + 30) -> np.ndarray:
    return np.random.default_rng(7).standard_normal((t, k))


def _entry(values: dict[str, float], widen: float) -> dict[str, dict[str, str]]:
    """Bounds around `values`: upper tails + widen, lower tails - widen."""
    up = {n: v + (widen if n in classifier.UPPER else 0.0) for n, v in values.items()
          if n not in classifier.LOWER}  # fmt: skip
    lo = {n: v - (widen if n in classifier.LOWER else 0.0) for n, v in values.items()
          if n not in classifier.UPPER}  # fmt: skip
    return {"upper": {n: v.hex() for n, v in up.items()},
            "lower": {n: v.hex() for n, v in lo.items()}}  # fmt: skip


def _report(x: np.ndarray) -> dict[str, object]:
    values = classifier.diagnostics(x[-grid.T_C2 :])
    tight = dict(values, max_excess_kurtosis=values["max_excess_kurtosis"] - 0.01)
    other_k = classifier.diagnostics(_x(1)[-grid.T_C2 :])
    return {
        "cells": {
            "q1-k2": {"status": "qualifying"},
            "q1-k2-tight": {"status": "qualifying"},
            "qj-k2/trend": {"status": "qualifying"},
            "demoted-k2": {"status": "challenge"},
            "q1-k1": {"status": "qualifying"},
        },
        "cell_bounds": {
            "q1-k2": _entry(values, 0.5),
            "q1-k2-tight": _entry(tight, 0.0),  # kurtosis just outside
            "qj-k2/trend": _entry(values, 0.0),  # ties accepted
            "demoted-k2": _entry(values, 1.0),  # matches, but not final
            "q1-k1": _entry(other_k, 10.0),  # another K
        },
    }


def test_accepts_only_final_qualifying_cells_of_its_k_holding_every_tail():
    x = _x(2)
    record = mapping._compare(x, _report(x))
    assert record["accepted"] and record["reason"] is None
    assert record["cells"] == ["q1-k2", "qj-k2/trend"]
    assert record["days"] == grid.T_C2
    assert float.fromhex(record["diagnostics"]["T"]) == grid.T_C2


def test_uses_the_last_t_c2_days():
    x = _x(2)
    report = _report(x)
    shifted = np.vstack([x[:30] * 50, x[30:]])  # warm-up rows never read
    assert mapping._compare(shifted, report)["cells"] == ["q1-k2", "qj-k2/trend"]


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        (lambda x: x[: grid.T_C2 - 1], "fewer than T_C2 days after warm-up"),
        (
            lambda x: np.where(np.arange(len(x))[:, None] == len(x) - 1, np.nan, x),
            "non-finite diagnostic",
        ),  # fmt: skip
        (lambda x: x**3, "outside every final qualifying cell"),
    ],
)
def test_refusals(change, reason):
    x = _x(2)
    record = mapping._compare(change(x), _report(x))
    assert (
        not record["accepted"] and record["cells"] == [] and record["reason"] == reason
    )


def _object(tmp_path, report, defn):
    obj = tmp_path / "obj"
    obj.mkdir()
    files = {"choices.json": cj(report), "definition.json": cj(defn),
             "mapping.py": b"reviewed"}  # fmt: skip
    for name, data in files.items():
        (obj / name).write_bytes(data)
    manifest = {n: hashlib.sha256(d).hexdigest() for n, d in files.items()}
    (obj / "manifest.json").write_bytes(cj(manifest))
    return obj, sha(manifest)


def test_load_checks_the_posted_hash_and_each_file(tmp_path):
    obj, posted = _object(tmp_path, {"cells": {}}, {"engine_commit": "c"})
    assert mapping.load(obj, posted) == (
        {"cells": {}},
        {"engine_commit": "c"},
        b"reviewed",
    )
    with pytest.raises(ValueError, match="not the posted one"):
        mapping.load(obj, "0" * 64)
    for name in ("choices.json", "definition.json", "mapping.py"):
        good = (obj / name).read_bytes()
        (obj / name).write_bytes(good + b" ")
        with pytest.raises(ValueError, match=f"{name} does not match"):
            mapping.load(obj, posted)
        (obj / name).write_bytes(good)


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _engine_repo(tmp_path, change=None):
    """A repository whose one commit holds every loaded engine module but
    this file, with `change` (path, bytes) applied."""
    repo = tmp_path / "repo"
    for rel, path in mapping.loaded().items():
        if rel != mapping.SELF:
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (repo / rel).write_bytes(path.read_bytes())
    if change:
        (repo / change[0]).write_bytes(change[1])
    _git(repo, "init", "-q")
    _git(repo, "-c", "core.autocrlf=false", "add", ".")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "e")
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return repo, {
        "engine_commit": head,
        "generator_sha256": sha(rundef.code_inventory(repo)),
    }


SELF_BYTES = Path(mapping.__file__).read_bytes()


@pytest.fixture
def no_bytecode(monkeypatch):
    monkeypatch.setattr(mapping.rundef, "bytecode_problem", lambda: None)


def test_check_engine_binds_the_commit_and_every_loaded_module(tmp_path, no_bytecode):
    repo, defn = _engine_repo(tmp_path)
    mapping.check_engine(defn, repo, SELF_BYTES)
    with pytest.raises(ValueError, match="not the run's recorded code"):
        mapping.check_engine(defn | {"generator_sha256": "0" * 64}, repo, SELF_BYTES)
    with pytest.raises(ValueError, match="not readable"):
        mapping.check_engine(defn | {"engine_commit": "f" * 40}, repo, SELF_BYTES)
    with pytest.raises(ValueError, match="calibration/mapping.py is not the run's"):
        mapping.check_engine(defn, repo, SELF_BYTES + b"# changed")


@pytest.mark.parametrize("rel", ["calibration/grid.py", "calibration/classifier.py"])
def test_check_engine_refuses_another_loaded_module(tmp_path, no_bytecode, rel):
    repo, defn = _engine_repo(tmp_path, (rel, b"T_C2 = 1239"))
    with pytest.raises(ValueError, match=f"the loaded {rel} is not the run's"):
        mapping.check_engine(defn, repo, SELF_BYTES)


def test_check_engine_refuses_bytecode_and_outside_modules(tmp_path, monkeypatch):
    repo, defn = _engine_repo(tmp_path)
    monkeypatch.setattr(mapping.rundef, "bytecode_problem", lambda: "cache on")
    with pytest.raises(ValueError, match="cache on"):
        mapping.check_engine(defn, repo, SELF_BYTES)
    monkeypatch.setattr(mapping.rundef, "bytecode_problem", lambda: None)
    outside = tmp_path / "elsewhere.py"
    outside.write_text("")
    fake = type(sys)("calibration.elsewhere")
    fake.__file__ = str(outside)
    monkeypatch.setitem(sys.modules, "calibration.elsewhere", fake)
    with pytest.raises(ValueError, match="calibration.elsewhere is not loaded"):
        mapping.check_engine(defn, repo, SELF_BYTES)


def test_check_runtime_refuses_another_image(monkeypatch):
    monkeypatch.setattr(mapping.dsr, "v_runtime_check", lambda *a: None)
    monkeypatch.setattr(mapping.rundef, "reference_vectors", lambda: {"r": "1"})
    gating = {"identity": {}, "canaries": {}, "image_digest": "sha256:a",
              "reference_vectors": {"r": "1"}}  # fmt: skip
    monkeypatch.setenv(mapping.rundef.IMAGE_DIGEST_ENV, "sha256:a")
    mapping.check_runtime({"gating": gating})
    monkeypatch.setenv(mapping.rundef.IMAGE_DIGEST_ENV, "sha256:b")
    with pytest.raises(RuntimeError, match="image digest differs"):
        mapping.check_runtime({"gating": gating})
    monkeypatch.setenv(mapping.rundef.IMAGE_DIGEST_ENV, "sha256:a")
    monkeypatch.setattr(mapping.rundef, "reference_vectors", lambda: {"r": "2"})
    with pytest.raises(RuntimeError, match="reference vectors differ"):
        mapping.check_runtime({"gating": gating})


def test_map_design_checks_and_carries_the_object_hash(tmp_path, monkeypatch):
    x = _x(2)
    calls = []
    monkeypatch.setattr(
        mapping, "check_engine", lambda d, r, m: calls.append(("e", d, r, m))
    )
    monkeypatch.setattr(mapping, "check_runtime", lambda d: calls.append(("r", d)))
    defn = {"engine_commit": "c"}
    obj, posted = _object(tmp_path, json.loads(cj(_report(x))), defn)
    record = mapping.map_design(obj, posted, x, tmp_path)
    assert calls == [("e", defn, tmp_path, b"reviewed"), ("r", defn)]
    assert record["cells"] == ["q1-k2", "qj-k2/trend"]
    assert record["qualification_object_sha256"] == posted
    with pytest.raises(ValueError, match="not the posted one"):
        mapping.map_design(obj, "0" * 64, x, tmp_path)


def test_record_hash_is_canonical():
    x = _x(2)
    record = mapping._compare(x, _report(x))
    assert mapping.record_sha256(record) == sha(json.loads(json.dumps(record)))
