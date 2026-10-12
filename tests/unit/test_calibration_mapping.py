import hashlib
import json
import subprocess
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
    files = {"choices.json": cj(report), "definition.json": cj(defn)}
    for name, data in files.items():
        (obj / name).write_bytes(data)
    manifest = {n: hashlib.sha256(d).hexdigest() for n, d in files.items()}
    (obj / "manifest.json").write_bytes(cj(manifest))
    return obj, sha(manifest)


def test_load_checks_the_posted_hash_and_each_file(tmp_path):
    obj, posted = _object(tmp_path, {"cells": {}}, {"engine_commit": "c"})
    assert mapping.load(obj, posted) == ({"cells": {}}, {"engine_commit": "c"})
    with pytest.raises(ValueError, match="not the posted one"):
        mapping.load(obj, "0" * 64)
    for name in ("choices.json", "definition.json"):
        good = (obj / name).read_bytes()
        (obj / name).write_bytes(good + b" ")
        with pytest.raises(ValueError, match=f"{name} does not match"):
            mapping.load(obj, posted)
        (obj / name).write_bytes(good)


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _engine_repo(tmp_path, classifier_bytes):
    """A repository whose one commit holds this classifier and one script."""
    repo = tmp_path / "repo"
    (repo / "calibration").mkdir(parents=True)
    (repo / "calibration" / "classifier.py").write_bytes(classifier_bytes)
    (repo / "scripts").mkdir()
    (repo / "scripts" / "d19_x.py").write_bytes(b"x = 1")
    (repo / "README").write_bytes(b"not code")
    _git(repo, "init", "-q")
    _git(repo, "add", ".")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "e")
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return repo, head, sha(rundef.code_inventory(repo))


def test_check_engine_binds_the_commit_and_the_loaded_classifier(tmp_path):
    real = Path(classifier.__file__).read_bytes()
    repo, head, recorded = _engine_repo(tmp_path, real)
    mapping.check_engine({"engine_commit": head, "generator_sha256": recorded}, repo)
    with pytest.raises(ValueError, match="not the run's recorded code"):
        mapping.check_engine(
            {"engine_commit": head, "generator_sha256": "0" * 64}, repo
        )
    with pytest.raises(ValueError, match="not readable"):
        mapping.check_engine(
            {"engine_commit": "f" * 40, "generator_sha256": recorded}, repo
        )


def test_check_engine_refuses_another_classifier(tmp_path):
    repo, head, recorded = _engine_repo(tmp_path, b"# another classifier")
    with pytest.raises(ValueError, match="loaded classifier is not the run's"):
        mapping.check_engine(
            {"engine_commit": head, "generator_sha256": recorded}, repo
        )


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
    monkeypatch.setattr(mapping, "check_engine", lambda d, r: calls.append(("e", d, r)))
    monkeypatch.setattr(mapping, "check_runtime", lambda d: calls.append(("r", d)))
    defn = {"engine_commit": "c"}
    obj, posted = _object(tmp_path, json.loads(cj(_report(x))), defn)
    record = mapping.map_design(obj, posted, x, tmp_path)
    assert calls == [("e", defn, tmp_path), ("r", defn)]
    assert record["cells"] == ["q1-k2", "qj-k2/trend"]
    assert record["qualification_object_sha256"] == posted
    with pytest.raises(ValueError, match="not the posted one"):
        mapping.map_design(obj, "0" * 64, x, tmp_path)


def test_record_hash_is_canonical():
    x = _x(2)
    record = mapping._compare(x, _report(x))
    assert mapping.record_sha256(record) == sha(json.loads(json.dumps(record)))
