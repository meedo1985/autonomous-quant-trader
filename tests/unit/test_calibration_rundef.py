"""D-19 run definition and start gate (prereg §13 rev 7g item 6, D19CR-4,
FE-1..FE-4, FE-8): recorded from a clean pinned checkout in one fresh
process, re-checked in another; a change to the code, the runtime identity,
the image digest, a canary or a reference vector stops the start. Synthetic
data only."""

from __future__ import annotations

import importlib.util
import json
import os
import py_compile
import shutil
import struct
import subprocess
import sys
import types
from pathlib import Path

import pytest

from calibration import dsr, fast, gates, rundef

ROOT = Path(__file__).resolve().parents[2]
DIGEST = "sha256:" + "ab" * 32
CELLS = json.dumps({"purpose": "pilot", "replications": {"threshold": 3}, "cells": [
    {"cell_id": "c-k2", "k": 2, "t": 60, "law": "garch", "dependence": "equi0.5"},
    {"cell_id": "c-k1", "k": 1, "t": 60, "law": "t5", "dependence": "independent"},
]})  # fmt: skip


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
    for script in ("d19_run_definition.py", "d19_run.py"):
        shutil.copy(ROOT / "scripts" / script, root / "scripts")
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
    for name, text in (("cells", CELLS), ("seeds", '{"anchor": "x"}'),
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
    engine = ("aqt", "calibration")
    assert not [m for m in rundef.loaded_outside(ROOT) if m.split(".")[0] in engine]
    assert __name__ in rundef.loaded_outside(ROOT)  # not hashed code
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

    final = rundef.reference_vectors()[case.cell_id]
    monkeypatch.setattr(gates, gate, nudged)
    after = rundef._reference_outputs(case)  # noqa: SLF001
    assert after["u_g"] == before["u_g"] and after["u_g_trace"] != before["u_g_trace"]
    assert rundef.reference_vectors()[case.cell_id] != final  # R3-4: final hash


def test_the_recorded_prereg_commit_is_a_full_id(recorded: tuple[Path, Path]) -> None:
    """R3-1: "HEAD" on the command line is stored as the commit it named."""
    root, out = recorded
    assert rundef.load(out)["prereg_commit"] == _git(root, "rev-parse", "HEAD")


def test_the_code_inventory_holds_the_d19_entry_points() -> None:
    inventory = rundef.code_inventory(ROOT)
    assert "scripts/d19_run_definition.py" in inventory
    assert "scripts/d19_pilot.py" in inventory
    assert not any(
        rel.startswith("scripts/") and "/d19_" not in rel for rel in inventory
    )


def test_an_entry_script_outside_the_hashed_code_stops_the_start(
    recorded: tuple[Path, Path],
) -> None:
    """R3-2: a driver or launcher that is not hashed code cannot pass."""
    root, out = recorded
    other = root / "launcher.py"
    shutil.copy(root / "scripts" / "d19_run_definition.py", other)
    text = other.read_text(encoding="utf-8").replace("parents[1]", "parents[0]")
    other.write_text(text, encoding="utf-8")
    env = {**os.environ, rundef.IMAGE_DIGEST_ENV: DIGEST}
    command = [sys.executable, str(other), "check", "--definition", str(out)]
    done = subprocess.run(command, env=env, cwd=root, capture_output=True,
                          text=True, check=False)  # fmt: skip
    other.unlink()
    assert done.returncode == 1 and "entry point is not hashed code" in done.stderr


def test_the_start_gate_refuses_modules_loaded_outside_the_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R3-2/R3-4: `start_gate` itself refuses, not only the helper."""
    (tmp_path / "scripts").mkdir()
    entry = tmp_path / "scripts" / "d19_driver.py"
    entry.write_text("")
    monkeypatch.setattr(sys.modules["__main__"], "__file__", str(entry))
    with pytest.raises(RuntimeError, match="loaded outside the checkout"):
        rundef.start_gate({"generator_sha256": "", "gating": {}}, tmp_path)


def test_a_nested_helper_inside_the_checkout_is_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R4-1: a module loaded from inside the checkout but outside the hashed
    code (here `calibration/extra/worker.py`, added after recording)."""
    helper = tmp_path / "calibration" / "extra" / "worker.py"
    helper.parent.mkdir(parents=True)
    helper.write_text("X = 1\n")
    spec = importlib.util.spec_from_file_location("d19_extra_worker", helper)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setitem(sys.modules, "d19_extra_worker", module)
    assert "d19_extra_worker" in rundef.loaded_outside(tmp_path)
    assert "calibration/extra/worker.py" not in rundef.code_inventory(tmp_path)


def test_a_git_replacement_ref_cannot_stand_in_for_the_engine_commit(
    tmp_path: Path,
) -> None:
    """R4-2: with `refs/replace` mapping commit A to B, plain `ls-tree`/`show`
    of A read B's tree; the working tree matches B, the record says A."""
    root = _checkout(tmp_path)
    (tmp_path / "in").mkdir()
    a = _git(root, "rev-parse", "HEAD")
    with (root / "calibration" / "seeds.py").open("a") as handle:
        handle.write("# B\n")
    ident = ["-c", "user.name=t", "-c", "user.email=t@t"]
    _git(root, *ident, "commit", "-q", "-am", "B")
    b = _git(root, "rev-parse", "HEAD")
    _git(root, "checkout", "-q", a)
    _git(root, "checkout", b, "--", "calibration/seeds.py")  # worktree as B
    _git(root, "replace", a, b)
    assert _git(root, "show", f"{a}:calibration/seeds.py").endswith("# B")
    done = _record(root, tmp_path / "in" / "d.json", a)
    assert done.returncode == 1 and "engine code differs from HEAD" in done.stderr


def test_an_engine_module_inside_the_runtime_installation_is_reported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """R5-1: an `aqt`/`calibration` module under `sys.prefix` (the virtual
    environment) is not covered by the code hash, so it is reported."""
    fake = types.ModuleType("aqt.d19_fake")
    fake.__file__ = str(
        Path(sys.prefix) / "Lib" / "site-packages" / "aqt" / "d19_fake.py"
    )
    monkeypatch.setitem(sys.modules, "aqt.d19_fake", fake)
    assert "aqt.d19_fake" in rundef.loaded_outside(ROOT)


def test_record_refuses_a_file_changed_while_recording(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R5-2: an engine file edited after the first check and before writing
    leaves nothing written."""
    root = _checkout(tmp_path)
    spec = importlib.util.spec_from_file_location(
        "d19_record_under_test", root / "scripts" / "d19_run_definition.py"
    )
    assert spec is not None and spec.loader is not None
    # the script switches bytecode caching off process-wide: restore after
    monkeypatch.setattr(sys, "dont_write_bytecode", sys.dont_write_bytecode)
    monkeypatch.setattr(sys, "pycache_prefix", sys.pycache_prefix)
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)

    def build_while_editing(**_: object) -> dict[str, object]:
        with (root / "calibration" / "seeds.py").open("a") as handle:
            handle.write("# edited during recording\n")
        return {"record_type": rundef.RECORD_TYPE}

    monkeypatch.setattr(script.rundef, "build", build_while_editing)
    monkeypatch.setenv(rundef.IMAGE_DIGEST_ENV, DIGEST)
    inputs = tmp_path / "in"
    inputs.mkdir()
    for name in ("cells", "seeds", "exploration"):
        (inputs / f"{name}.json").write_text("{}")
    out = inputs / "d.json"
    code = script.main([
        "record", "--out", str(out), "--prereg-commit", "HEAD",
        "--engine-commit", _git(root, "rev-parse", "HEAD"),
        "--cell-manifest", str(inputs / "cells.json"),
        "--seed-spec", str(inputs / "seeds.json"),
        "--exploration-manifest", str(inputs / "exploration.json"),
    ])  # fmt: skip
    assert code == 1 and not out.exists()


def test_a_planted_bytecode_file_never_runs(
    recorded: tuple[Path, Path], tmp_path: Path
) -> None:
    """R6-1: an unchecked-hash `.pyc` for `calibration/seeds.py` that would
    run different code is never read; the gate passes on the source."""
    root, out = recorded
    copy = tmp_path / "engine"
    shutil.copytree(root, copy)
    seeds = copy / "calibration" / "seeds.py"
    planted = tmp_path / "planted.py"
    planted.write_text(seeds.read_text(encoding="utf-8") + "\nprint('PLANTED')\n")
    py_compile.compile(
        str(planted),
        cfile=importlib.util.cache_from_source(str(seeds)),
        dfile=str(seeds),
        invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH,
    )
    done = _script(copy, "check", "--definition", str(out))
    assert "PLANTED" not in done.stdout + done.stderr
    assert done.returncode == 0, done.stderr


def test_the_start_gate_needs_bytecode_disabled() -> None:
    """R6-1: this pytest process caches bytecode, so the gate's check fails."""
    assert rundef.bytecode_problem() is not None


def test_a_git_dir_override_cannot_record_another_repository(tmp_path: Path) -> None:
    """R6-2: GIT_DIR/GIT_WORK_TREE pointing at another repository whose
    engine files match are ignored; its HEAD is not this checkout's."""
    root = _checkout(tmp_path / "a")
    other = _checkout(tmp_path / "b")
    ident = ["-c", "user.name=t", "-c", "user.email=t@t"]
    _git(other, *ident, "commit", "-q", "--allow-empty", "-m", "other")
    (tmp_path / "in").mkdir()
    inputs = tmp_path / "in"
    for name in ("cells", "seeds", "exploration"):
        (inputs / f"{name}.json").write_text("{}")
    env = {**os.environ, rundef.IMAGE_DIGEST_ENV: DIGEST,
           "GIT_DIR": str(other / ".git"), "GIT_WORK_TREE": str(other)}  # fmt: skip
    command = [
        sys.executable, str(root / "scripts" / "d19_run_definition.py"), "record",
        "--out", str(inputs / "d.json"), "--prereg-commit", "HEAD",
        "--engine-commit", _git(other, "rev-parse", "HEAD"),
        "--cell-manifest", str(inputs / "cells.json"),
        "--seed-spec", str(inputs / "seeds.json"),
        "--exploration-manifest", str(inputs / "exploration.json"),
    ]  # fmt: skip
    done = subprocess.run(command, env=env, cwd=root, capture_output=True,
                          text=True, check=False)  # fmt: skip
    assert done.returncode == 1 and "is not this checkout's HEAD" in done.stderr


def test_the_start_gate_itself_refuses_cached_bytecode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """R7-1: `start_gate` calls the bytecode check (this pytest process
    caches bytecode), not only the helper."""
    entry = ROOT / "scripts" / "d19_run_definition.py"
    monkeypatch.setattr(sys.modules["__main__"], "__file__", str(entry))
    monkeypatch.setattr(rundef, "loaded_outside", lambda _root: [])
    monkeypatch.setattr(sys, "dont_write_bytecode", False)
    with pytest.raises(RuntimeError, match="bytecode caching is not disabled"):
        rundef.start_gate({"generator_sha256": "", "gating": {}}, ROOT)


def _driver(root: Path, out: Path, store: Path, *args: str,
            digest: str = DIGEST) -> subprocess.CompletedProcess[str]:  # fmt: skip
    env = {**os.environ, rundef.IMAGE_DIGEST_ENV: digest}
    command = [sys.executable, str(root / "scripts" / "d19_run.py"), "run",
               "--definition", str(out), "--store", str(store), *args]  # fmt: skip
    return subprocess.run(command, env=env, cwd=root, capture_output=True,
                          text=True, check=False)  # fmt: skip


def test_the_driver_runs_one_bound_chain_per_cell_and_resumes(
    recorded: tuple[Path, Path], tmp_path: Path
) -> None:
    """Two workers, one chain per manifest cell; every chunk carries the
    run-definition hash and the gating the start gate returned (FE-5); a
    second run computes nothing new and ends at the same heads."""
    root, out = recorded
    store = tmp_path / "store"
    args = ("--namespace", "threshold", "--workers", "2")
    first = _driver(root, out, store, *args)
    assert first.returncode == 0, first.stderr
    defn = rundef.load(out)
    for cell in ("c-k2", "c-k1"):
        chunk = json.loads(
            (store / "threshold" / cell / "chunk-0000000.json").read_bytes()
        )
        assert chunk["binding"] == rundef.definition_sha256(defn)
        assert chunk["gating"] == defn["gating"]
        assert len(chunk["results"]) == 3
    k1 = json.loads((store / "threshold" / "c-k1" / "chunk-0000000.json").read_bytes())
    assert set(k1["results"][0]) == classifier_fields(1)
    before = {p: p.read_bytes() for p in store.rglob("*.json")}
    second = _driver(root, out, store, *args)
    assert second.returncode == 0, second.stderr
    assert second.stdout == first.stdout
    assert {p: p.read_bytes() for p in store.rglob("*.json")} == before


def classifier_fields(k: int) -> set[str]:
    from calibration import classifier

    return set(classifier.required(k))


def test_the_driver_refuses_unbuilt_namespaces_and_a_failed_gate(
    recorded: tuple[Path, Path], tmp_path: Path
) -> None:
    root, out = recorded
    store = tmp_path / "store"
    done = _driver(root, out, store, "--namespace", "heldout")
    assert done.returncode == 1 and "is not built" in done.stderr
    done = _driver(root, out, store, "--namespace", "threshold", digest="sha256:other")
    assert done.returncode == 1 and "image digest differs" in done.stderr
    assert not store.exists()


def test_a_worker_runs_the_start_gate_before_any_chunk(
    recorded: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R3-3: the worker itself gates; a refusal there writes nothing."""
    root, out = recorded
    script = root / "scripts" / "d19_run.py"
    spec = importlib.util.spec_from_file_location("d19_run_under_test", script)
    assert spec is not None and spec.loader is not None
    monkeypatch.setattr(sys, "dont_write_bytecode", sys.dont_write_bytecode)
    monkeypatch.setattr(sys, "pycache_prefix", sys.pycache_prefix)
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)

    def refused(*_: object) -> dict[str, object]:
        raise RuntimeError("U_ops: start gate: refused in the worker")

    monkeypatch.setattr(driver.rundef, "start_gate", refused)
    store = tmp_path / "store"
    with pytest.raises(RuntimeError, match="refused in the worker"):
        driver.worker(out, store, "threshold", "c-k2")
    assert not store.exists()


def _load_driver(root: Path, monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(
        "d19_run_loaded", root / "scripts" / "d19_run.py"
    )
    assert spec is not None and spec.loader is not None
    monkeypatch.setattr(sys, "dont_write_bytecode", sys.dont_write_bytecode)
    monkeypatch.setattr(sys, "pycache_prefix", sys.pycache_prefix)
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    return driver


def test_threshold_seeds_follow_prereg_section_8(
    recorded: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """DR-1/DR-5: namespace d19-threshold-v1, anchor = the recorded
    preregistration hash; every stored draw equals that computation."""
    from calibration import classifier
    from calibration.generator import Cell, generate
    from calibration.seeds import outer_seed, stream

    root, out = recorded
    driver = _load_driver(root, monkeypatch)
    monkeypatch.setattr(driver.rundef, "start_gate", lambda defn, _root: defn["gating"])
    store = tmp_path / "store"
    driver.worker(out, store, "threshold", "c-k2")
    chunk = json.loads(
        (store / "threshold" / "c-k2" / "chunk-0000000.json").read_bytes()
    )
    defn = rundef.load(out)
    cell = Cell("c-k2", 2, 60, "garch", "equi0.5")
    for rep_, stored in enumerate(chunk["results"]):
        seed = outer_seed(defn["prereg_sha256"], "c-k2", "d19-threshold-v1", rep_)
        legs = generate(cell, stream(seed, "market"), stream(seed, "columns"))
        expected = classifier.diagnostics(legs.x)
        assert stored == {
            n: struct.pack(">d", v).hex() for n, v in sorted(expected.items())
        }


def test_a_chain_carries_the_gating_its_worker_gate_returned(
    recorded: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """FE-5/DR-5: not the definition's copy, the worker gate's return."""
    root, out = recorded
    driver = _load_driver(root, monkeypatch)
    monkeypatch.setattr(driver.rundef, "start_gate", lambda *_: {"from": "worker gate"})
    store = tmp_path / "store"
    driver.worker(out, store, "threshold", "c-k1")
    chunk = json.loads(
        (store / "threshold" / "c-k1" / "chunk-0000000.json").read_bytes()
    )
    assert chunk["gating"] == {"from": "worker gate"}


def test_an_interrupted_run_resumes_identically_and_a_new_plan_cannot_extend_it(
    recorded: tuple[Path, Path], tmp_path: Path
) -> None:
    """DR-3/DR-5: a 501-draw plan (two chunks); the second chunk deleted as
    if the run stopped, then resumed byte-identically; the earlier 3-draw
    definition on the same store is refused (another binding)."""
    root, small = recorded
    plan = {"purpose": "pilot", "replications": {"threshold": 501},
            "cells": [json.loads(CELLS)["cells"][1]]}  # fmt: skip
    inputs = tmp_path / "in"
    inputs.mkdir()
    big = inputs / "big.json"
    manifest = inputs / "cells.json"
    manifest.write_text(json.dumps(plan))
    for name in ("seeds", "exploration"):
        (inputs / f"{name}.json").write_text("{}")
    done = _script(
        root, "record", "--out", str(big), "--prereg-commit", "HEAD",
        "--engine-commit", _git(root, "rev-parse", "HEAD"),
        "--cell-manifest", str(manifest), "--seed-spec", str(inputs / "seeds.json"),
        "--exploration-manifest", str(inputs / "exploration.json"),
    )  # fmt: skip
    assert done.returncode == 0, done.stderr
    store = tmp_path / "store"
    args = ("--namespace", "threshold", "--workers", "1")
    assert _driver(root, big, store, *args).returncode == 0
    chain = store / "threshold" / "c-k1"
    whole = {p.name: p.read_bytes() for p in chain.iterdir()}
    assert sorted(whole) == ["chunk-0000000.json", "chunk-0000500.json"]
    (chain / "chunk-0000500.json").unlink()
    (chain / "chunk-0000500.tmp").write_bytes(b"torn")
    assert _driver(root, big, store, *args).returncode == 0
    assert {p.name: p.read_bytes() for p in chain.iterdir()} == whole
    other = _driver(root, small, store, *args)
    assert other.returncode != 0 and "ChainError" in other.stderr  # refused


@pytest.mark.parametrize(
    ("manifest", "message"),
    [
        ({"cells": "x"}, "no list of cells"),
        ({"cells": []}, "no cells"),
        ({"cells": [{"cell_id": "a", "k": 2, "t": 60, "law": "gaussian"}]}, "exactly"),
        (
            {
                "cells": [
                    _c := {
                        "cell_id": "a",
                        "k": 2,
                        "t": 60,
                        "law": "gaussian",
                        "dependence": "independent",
                    },
                    _c,
                ]
            },
            "duplicate",
        ),  # fmt: skip
        ({"cells": [{**_c, "cell_id": "../x"}]}, "path-safe"),
        ({"cells": [{**_c, "k": 3}]}, "K must be"),
        ({"cells": [{**_c, "t": 8}]}, "T must be"),
        ({"cells": [{**_c, "law": "cauchy"}]}, "unknown law"),
        ({"cells": [{**_c, "k": 1, "dependence": "equi0.5"}]}, "K = 1"),
        ({"cells": [{**_c, "dependence": "clusters"}]}, "clusters"),
    ],
)
def test_a_malformed_cell_manifest_is_refused(manifest: object, message: str) -> None:
    from calibration.generator import cells_from_manifest

    with pytest.raises(ValueError, match=message):
        cells_from_manifest(manifest)


@pytest.mark.parametrize(
    ("manifest", "message"),
    [
        ({"purpose": "pilot"}, "purpose and replications"),
        (
            {"purpose": "x", "replications": {"threshold": 3}},
            "purpose and replications",
        ),
        ({"purpose": "pilot", "replications": {"threshold": 0}}, "positive"),
        ({"purpose": "pilot", "replications": {"threshold": 3, "dev": 1}}, "positive"),
        ({"purpose": "qualification", "replications": {"threshold": 3}}, "exactly"),
    ],
)
def test_a_bad_run_plan_is_refused(manifest: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        rundef.run_plan(manifest)
    prescribed = {"purpose": "qualification", "replications": {"threshold": 300_000}}
    assert rundef.run_plan(prescribed) == {"threshold": 300_000}
