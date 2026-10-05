"""D-19 run definition and start gate (prereg §13 rev 7g item 6, D19CR-4,
FE-1..FE-4, FE-8): recorded from a clean pinned checkout in one fresh
process, re-checked in another; a change to the code, the runtime identity,
the image digest, a canary or a reference vector stops the start. Synthetic
data only."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from calibration import dsr, fast, rundef

ROOT = Path(__file__).resolve().parents[2]
DIGEST = "sha256:" + "ab" * 32


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                          text=True, check=True).stdout.strip()  # fmt: skip


def _script(
    root: Path, *args: str, digest: str = DIGEST
) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, rundef.IMAGE_DIGEST_ENV: digest,
           "PYTHONPATH": f"{root}{os.pathsep}{root / 'src'}"}  # fmt: skip
    script = root / "scripts" / "d19_run_definition.py"
    return subprocess.run([sys.executable, str(script), *args], env=env, cwd=root,
                          capture_output=True, text=True, check=False)  # fmt: skip


def _checkout(tmp: Path) -> Path:
    """A clean git checkout holding only what the engine runs."""
    root = tmp / "engine"
    shutil.copytree(ROOT / "calibration", root / "calibration",
                    ignore=shutil.ignore_patterns("__pycache__"))  # fmt: skip
    shutil.copytree(ROOT / "src" / "aqt", root / "src" / "aqt",
                    ignore=shutil.ignore_patterns("__pycache__"))  # fmt: skip
    (root / "scripts").mkdir()
    shutil.copy(ROOT / "scripts" / "d19_run_definition.py", root / "scripts")
    (root / ".gitignore").write_text("__pycache__/\n")
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "e")
    return root


def _record(root: Path, out: Path, commit: str) -> subprocess.CompletedProcess[str]:
    inputs = out.parent
    for name, text in (("cells", '{"cells": ["c1"]}'), ("seeds", '{"anchor": "x"}'),
                       ("exploration", "{}"), ("prereg", "# prereg")):  # fmt: skip
        (inputs / f"{name}.json").write_text(text)
    return _script(
        root, "record", "--out", str(out), "--prereg-commit", "e148a28",
        "--prereg-file", str(inputs / "prereg.json"), "--engine-commit", commit,
        "--cell-manifest", str(inputs / "cells.json"),
        "--seed-spec", str(inputs / "seeds.json"),
        "--exploration-manifest", str(inputs / "exploration.json"),
    )  # fmt: skip


@pytest.fixture(scope="module")
def recorded(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    tmp = tmp_path_factory.mktemp("rundef")
    root = _checkout(tmp)
    out = tmp / "run_definition.json"
    done = _record(root, out, _git(root, "rev-parse", "HEAD"))
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == rundef.definition_sha256(rundef.load(out))
    return root, out


def test_the_start_gate_passes_on_the_recording_checkout(
    recorded: tuple[Path, Path],
) -> None:
    root, out = recorded
    defn = rundef.load(out)
    assert set(defn["gating"]) == {
        "identity",
        "image_digest",
        "canaries",
        "reference_vectors",
    }
    assert len(defn["gating"]["reference_vectors"]) == len(rundef.REFERENCE_CASES) + 1
    assert defn["prereg_sha256"] and defn["engine_commit"] == _git(
        root, "rev-parse", "HEAD"
    )
    done = _script(root, "check", "--definition", str(out))
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == f"start gate passed: {rundef.definition_sha256(defn)}"


def test_record_refuses_another_commit_or_a_dirty_checkout(tmp_path: Path) -> None:
    """FE-1: the recorded engine commit is the code that runs."""
    root = _checkout(tmp_path)
    (tmp_path / "in").mkdir()
    done = _record(root, tmp_path / "in" / "d.json", "0" * 40)
    assert done.returncode == 1 and "is not this checkout's HEAD" in done.stderr
    with (root / "calibration" / "seeds.py").open("a") as handle:
        handle.write("\n")
    done = _record(root, tmp_path / "in" / "d.json", _git(root, "rev-parse", "HEAD"))
    assert done.returncode == 1 and "uncommitted changes" in done.stderr


def test_a_code_change_after_recording_stops_the_start(
    recorded: tuple[Path, Path], tmp_path: Path
) -> None:
    """FE-1/FE-2: a later edit of the engine or of `src/aqt` it calls."""
    root, out = recorded
    for edited in ("calibration/seeds.py", "src/aqt/metrics/statistics.py"):
        copy = tmp_path / edited.replace("/", "_")
        shutil.copytree(root, copy)
        with (copy / edited).open("a") as handle:
            handle.write("\n")
        done = _script(copy, "check", "--definition", str(out))
        assert done.returncode == 1 and "engine code differs" in done.stderr


def test_another_image_digest_stops_the_start(recorded: tuple[Path, Path]) -> None:
    root, out = recorded
    done = _script(root, "check", "--definition", str(out), digest="sha256:other")
    assert done.returncode == 1 and "U_ops: start gate: image digest" in done.stderr


@pytest.mark.parametrize(
    ("part", "message"),
    [
        ("reference_vectors", "reference vectors differ"),
        ("canaries", "canary"),
        ("identity", "runtime differs"),
    ],
)
def test_a_changed_recorded_value_stops_the_start(
    recorded: tuple[Path, Path], tmp_path: Path, part: str, message: str
) -> None:
    root, out = recorded
    defn = rundef.load(out)
    first = next(iter(defn["gating"][part]))
    defn["gating"][part][first] = "0" * 64
    changed = tmp_path / "changed.json"
    rundef.write(changed, defn)
    done = _script(root, "check", "--definition", str(changed))
    assert done.returncode == 1 and "U_ops" in done.stderr
    assert message in done.stderr


def test_reference_vectors_see_the_u_g_numerics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FE-3: a change in G-1's replicate arithmetic that flips no
    availability still changes the suite."""
    monkeypatch.setattr(dsr, "_V_VERIFIED", True)
    before = rundef.reference_vectors()
    mean_var = fast.mean_var

    def nudged(values: object) -> tuple[float, float]:
        mean, var = mean_var(values)  # type: ignore[arg-type]
        return mean + 1e-15, var

    monkeypatch.setattr(fast, "mean_var", nudged)
    after = rundef.reference_vectors()
    assert before["refvec-k5-garch"] != after["refvec-k5-garch"]


def test_load_refuses_a_file_that_is_not_a_run_definition(tmp_path: Path) -> None:
    path = tmp_path / "x.json"
    path.write_text(json.dumps({"record_type": "something.else"}))
    with pytest.raises(ValueError, match="not a D-19 run definition"):
        rundef.load(path)
