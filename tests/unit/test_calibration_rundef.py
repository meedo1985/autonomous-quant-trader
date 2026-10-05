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

from calibration import dsr, fast, gates, rundef

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
    prereg = root / "review" / "governance-statistics-amendment"
    prereg = prereg / "d19-preregistration" / "PREREGISTRATION.md"
    prereg.parent.mkdir(parents=True)
    prereg.write_text("# prereg\n")
    (root / ".gitignore").write_text("__pycache__/\n")
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "e")
    return root


def _record(root: Path, out: Path, commit: str) -> subprocess.CompletedProcess[str]:
    inputs = out.parent
    for name, text in (("cells", '{"cells": ["c1"]}'), ("seeds", '{"anchor": "x"}'),
                       ("exploration", "{}")):  # fmt: skip
        (inputs / f"{name}.json").write_text(text)
    return _script(
        root, "record", "--out", str(out), "--prereg-commit", "HEAD",
        "--engine-commit", commit,
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
    assert done.returncode == 1 and "engine code differs from HEAD" in done.stderr


@pytest.mark.parametrize("hide", ["skip-worktree", "ignored-extra"])
def test_record_sees_changes_git_status_would_hide(tmp_path: Path, hide: str) -> None:
    """RR-3: the code is compared with HEAD's blobs, not through git status."""
    root = _checkout(tmp_path)
    (tmp_path / "in").mkdir()
    if hide == "skip-worktree":
        _git(root, "update-index", "--skip-worktree", "calibration/seeds.py")
        with (root / "calibration" / "seeds.py").open("a") as handle:
            handle.write("\n")
    else:
        (root / ".gitignore").write_text("__pycache__/\ncalibration/extra.py\n")
        _git(root, "add", ".gitignore")
        _git(
            root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "i"
        )
        (root / "calibration" / "extra.py").write_text("X = 1\n")
    assert _git(root, "status", "--porcelain") == ""  # git status sees nothing
    done = _record(root, tmp_path / "in" / "d.json", _git(root, "rev-parse", "HEAD"))
    assert done.returncode == 1 and "engine code differs from HEAD" in done.stderr


def test_the_code_hash_is_the_same_for_crlf_and_lf_checkouts(tmp_path: Path) -> None:
    """RR-4: one commit, one identity on Windows and Linux."""
    lf, crlf = tmp_path / "lf", tmp_path / "crlf"
    for root in (lf, crlf):
        shutil.copytree(ROOT / "calibration", root / "calibration",
                        ignore=shutil.ignore_patterns("__pycache__"))  # fmt: skip
    for path in (lf / "calibration").glob("*.py"):
        path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
    for path in (crlf / "calibration").glob("*.py"):
        text = path.read_bytes().replace(b"\r\n", b"\n")
        path.write_bytes(text.replace(b"\n", b"\r\n"))
    assert rundef.generator_sha256(lf) == rundef.generator_sha256(crlf)


def test_engine_modules_loaded_from_elsewhere_are_reported(tmp_path: Path) -> None:
    """RR-2: this test process loaded `aqt` and `calibration` from the
    repository, so for any other root they are outside it."""
    assert rundef.loaded_outside(ROOT) == []
    outside = rundef.loaded_outside(tmp_path)
    assert "calibration.rundef" in outside and "aqt.metrics.statistics" in outside


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


def test_every_gate_runs_after_an_earlier_refusal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RR-1: a fault in a later gate is never hidden by an earlier refusal."""
    monkeypatch.setattr(dsr, "_V_VERIFIED", True)

    def broken(*_: object, **__: object) -> str | None:
        raise ArithmeticError("engine fault in G-12")

    monkeypatch.setattr(gates, "g12", broken)
    with pytest.raises(ArithmeticError, match="G-12"):
        rundef._unavailable_outputs()  # noqa: SLF001 - G-2 refuses first


def test_reference_outputs_cover_every_trace_branch_and_the_benchmark(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RR-5: G-1 block and replicates, G-10 variances (K = 20), G-12 ESS per
    horizon, the benchmark leg, and the unavailable case's cause."""
    monkeypatch.setattr(dsr, "_V_VERIFIED", True)
    k20 = rundef._reference_outputs(rundef.REFERENCE_CASES[3])  # noqa: SLF001
    kinds = {entry[0] for entry in k20["u_g_trace"]}  # type: ignore[union-attr,index]
    assert kinds == {"g1_block", "g1_replicate", "g10_var", "g12_ess"}
    horizons = [e[1] for e in k20["u_g_trace"] if e[0] == "g12_ess"]  # type: ignore[union-attr,index]
    assert horizons == [24, 72, 168]
    assert set(k20) >= {"x", "benchmark", "candidates", "result", "u_g"}
    unavailable = rundef._unavailable_outputs()  # noqa: SLF001
    assert unavailable["u_g"] == "INVALID_SERIES"


@pytest.mark.parametrize("gate", ["g10", "g12"])
def test_reference_vectors_see_g10_and_g12_numerics(
    monkeypatch: pytest.MonkeyPatch, gate: str
) -> None:
    """RR-5: a change in a traced G-10 or G-12 number that flips no
    availability changes the K = 20 vector."""
    monkeypatch.setattr(dsr, "_V_VERIFIED", True)
    case = rundef.REFERENCE_CASES[3]
    before = rundef._reference_outputs(case)  # noqa: SLF001
    original = getattr(gates, gate)

    def nudged(values: object, trace: list[object] | None = None) -> str | None:
        reason = original(values, trace)
        if trace:
            trace[-1] = (*trace[-1][:-1], "changed")  # type: ignore[index]
        return reason

    monkeypatch.setattr(gates, gate, nudged)
    after = rundef._reference_outputs(case)  # noqa: SLF001
    assert after["u_g"] == before["u_g"] and after["u_g_trace"] != before["u_g_trace"]
