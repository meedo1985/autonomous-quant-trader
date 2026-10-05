"""D-19 run definition and start gate (prereg §13 rev 7g item 6, D19CR-4):
recorded in one fresh pinned process, re-checked in another; any change to
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

from calibration import rundef

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "d19_run_definition.py"
DIGEST = "sha256:" + "ab" * 32


def _script(*args: str, digest: str = DIGEST) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, rundef.IMAGE_DIGEST_ENV: digest}
    return subprocess.run([sys.executable, str(SCRIPT), *args], env=env, cwd=ROOT,
                          capture_output=True, text=True, check=False)  # fmt: skip


@pytest.fixture(scope="module")
def recorded(tmp_path_factory: pytest.TempPathFactory) -> Path:
    tmp = tmp_path_factory.mktemp("rundef")
    (tmp / "cells.json").write_text('{"cells": ["c1"]}')
    (tmp / "seeds.json").write_text('{"anchor": "x"}')
    (tmp / "exploration.json").write_text("{}")
    out = tmp / "run_definition.json"
    done = _script(
        "record", "--out", str(out), "--prereg-commit", "e148a28",
        "--engine-commit", "f" * 40, "--cell-manifest", str(tmp / "cells.json"),
        "--seed-spec", str(tmp / "seeds.json"),
        "--exploration-manifest", str(tmp / "exploration.json"),
    )  # fmt: skip
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == rundef.definition_sha256(rundef.load(out))
    return out


def test_the_start_gate_passes_on_the_recording_runtime(recorded: Path) -> None:
    """Reference vectors and canaries recomputed in a fresh process match."""
    defn = rundef.load(recorded)
    assert set(defn["gating"]) == {
        "identity",
        "image_digest",
        "canaries",
        "reference_vectors",
    }
    assert len(defn["gating"]["reference_vectors"]) == len(rundef.REFERENCE_CASES)
    done = _script("check", "--definition", str(recorded))
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == (
        f"start gate passed: {rundef.definition_sha256(defn)}"
    )


def test_another_image_digest_stops_the_start(recorded: Path) -> None:
    done = _script("check", "--definition", str(recorded), digest="sha256:other")
    assert done.returncode == 1 and "U_ops: start gate: image digest" in done.stderr


@pytest.mark.parametrize(
    ("part", "message"),
    [("reference_vectors", "reference vectors differ"), ("canaries", "canary")],
)
def test_a_changed_recorded_value_stops_the_start(
    recorded: Path, tmp_path: Path, part: str, message: str
) -> None:
    defn = rundef.load(recorded)
    first = next(iter(defn["gating"][part]))
    defn["gating"][part][first] = "0" * 64
    changed = tmp_path / "changed.json"
    rundef.write(changed, defn)
    done = _script("check", "--definition", str(changed))
    assert done.returncode == 1 and "U_ops" in done.stderr
    assert message in done.stderr


def test_load_refuses_a_file_that_is_not_a_run_definition(tmp_path: Path) -> None:
    path = tmp_path / "x.json"
    path.write_text(json.dumps({"record_type": "something.else"}))
    with pytest.raises(ValueError, match="not a D-19 run definition"):
        rundef.load(path)


def test_the_generator_hash_covers_every_calibration_file(tmp_path: Path) -> None:
    shutil.copytree(ROOT / "calibration", tmp_path / "calibration")
    before = rundef.generator_sha256(tmp_path)
    assert before == rundef.generator_sha256(ROOT)
    with (tmp_path / "calibration" / "seeds.py").open("a") as handle:
        handle.write("\n")
    assert rundef.generator_sha256(tmp_path) != before
