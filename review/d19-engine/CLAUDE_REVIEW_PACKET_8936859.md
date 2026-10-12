# D-19 threshold-driver adversarial review packet

Status: READY FOR HUMAN RELAY; NOT SENT. Claude Opus 5.5 implemented the
driver. A separate Claude Fable 5.1 review would be adversarial but would
not replace the recorded Codex review or the owner's decision.

Base: `96a223e`. Reviewed code commit: `8936859`. Review-record commit:
`9ed93cd`. The worktree was clean after the review commit. Scope is the
threshold namespace driver and its supporting manifest, run-plan, and tests.
Qualification, development, and held-out runs remain refused. No calibration
or server access was performed.

Validation (local Windows venv): focused pytest 81 passed; remaining pytest
1786 passed and 9 skipped; Ruff check and format passed; mypy found no issues
in 62 files; import linter kept 6 contracts; frozen verifier passed 28/28
trusted bytes and inventory, 14/14 sidecars, Constitution self-hash and all
reported bindings. Exact commands and results:
`review/d19-engine/ADJUDICATION_DRIVER_C71554B.md`.

Open requirements: FE-4 (host `docker inspect` image digest in the launcher),
FE-7 (re-pilot measurement of non-finite threshold draws). The owner has not
authorized a calibration run. Pilot acceptance is limited to the threshold
driver's code; it is not a qualification decision.

Review the diff below against preregistration §8 and §13 rev 7g, and the
checklist in `DRIVER_REREVIEW_PROMPT_4.md`. In particular, try to break
worker start gating, parent-to-worker definition binding, seed derivation,
resume identity, malformed manifest refusal, and failure on a killed worker.
Return every finding with a stable ID, severity (BLOCKER, NON-BLOCKING, or
QUESTION), file/line, triggering scenario, evidence, impact, and minimal
correction. State missing evidence explicitly. Do not propose strategy logic
or a governance change as an automatic code edit.

```diff
diff --git a/calibration/generator.py b/calibration/generator.py
index 157001c..4f42d5a 100644
--- a/calibration/generator.py
+++ b/calibration/generator.py
@@ -6,6 +6,7 @@ authorised; the measured pilot only needs cost-representative cells."""
 
 from __future__ import annotations
 
+import re
 from dataclasses import dataclass
 
 import numpy as np
@@ -25,6 +26,55 @@ class Cell:
     # near_duplicates | exact_duplicate | opposites | clusters | factor
 
 
+LAWS = ("gaussian", "t5", "ar0.2", "ar0.5", "garch")
+DEPENDENCES = (
+    "independent",
+    "equi0.5",
+    "equi0.9",
+    "equi0.99",
+    "near_duplicates",
+    "exact_duplicate",
+    "opposites",
+    "clusters",
+    "factor",
+)
+K_VALUES = (1, 2, 5, 20)  # §13 rev 7g item 1
+_CELL_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
+
+
+def cells_from_manifest(manifest: object) -> list[Cell]:
+    """The manifest's cells, or ValueError (DR-2): exactly the five fields,
+    unique path-safe ids, K in {1, 2, 5, 20}, T >= 16, a law and dependence
+    this generator implements and that fit K. Nothing falls through to a
+    generator default."""
+    if not isinstance(manifest, dict) or not isinstance(manifest.get("cells"), list):
+        raise ValueError("cell manifest has no list of cells")
+    cells, seen = [], set()
+    for entry in manifest["cells"]:
+        if not isinstance(entry, dict) or set(entry) != set(Cell.__slots__):
+            raise ValueError(f"cell entry does not have exactly {Cell.__slots__}")
+        cell = Cell(**entry)
+        if not isinstance(cell.cell_id, str) or not _CELL_ID.fullmatch(cell.cell_id):
+            raise ValueError(f"cell id is not path-safe: {cell.cell_id!r}")
+        if cell.cell_id in seen:
+            raise ValueError(f"duplicate cell id: {cell.cell_id}")
+        seen.add(cell.cell_id)
+        if type(cell.k) is not int or cell.k not in K_VALUES:
+            raise ValueError(f"{cell.cell_id}: K must be one of {K_VALUES}")
+        if type(cell.t) is not int or cell.t < 16:
+            raise ValueError(f"{cell.cell_id}: T must be an integer >= 16")
+        if cell.law not in LAWS or cell.dependence not in DEPENDENCES:
+            raise ValueError(f"{cell.cell_id}: unknown law or dependence")
+        if cell.k == 1 and cell.dependence != "independent":
+            raise ValueError(f"{cell.cell_id}: K = 1 has no dependence")
+        if cell.dependence == "clusters" and cell.k not in (5, 20):
+            raise ValueError(f"{cell.cell_id}: clusters need K = 5 or 20")
+        cells.append(cell)
+    if not cells:
+        raise ValueError("cell manifest has no cells")
+    return cells
+
+
 @dataclass(frozen=True, slots=True)
 class Legs:
     x: np.ndarray  # T x K E-DIFF columns, population mean 0
diff --git a/calibration/rundef.py b/calibration/rundef.py
index 91baa0d..0d9add5 100644
--- a/calibration/rundef.py
+++ b/calibration/rundef.py
@@ -204,6 +204,42 @@ def loaded_outside(root: Path) -> list[str]:
     return outside
 
 
+PRESCRIBED = {"threshold": 300_000}  # §13 rev 7g item 4
+SEED_NAMESPACES = {"threshold": "d19-threshold-v1"}  # prereg §8
+
+
+def seed_spec(prereg_sha256: str) -> dict[str, object]:
+    """The seed specification a run definition records, derived, never
+    supplied (DR2-2): prereg §8's anchor for threshold and development
+    runs is the preregistration hash, and its namespaces."""
+    return {"anchor": prereg_sha256, "namespaces": dict(SEED_NAMESPACES)}
+
+
+def run_plan(manifest: object) -> dict[str, int]:
+    """Replications per namespace, from the cell manifest, or ValueError
+    (DR-3). A `qualification` run uses exactly the prescribed counts; a
+    `pilot` run (the measured re-pilot) any positive count. Both are in the
+    run definition, so its hash binds them and a resume cannot change them."""
+    if not isinstance(manifest, dict):
+        raise ValueError("cell manifest is not an object")
+    purpose, counts = manifest.get("purpose"), manifest.get("replications")
+    if purpose not in ("qualification", "pilot") or not isinstance(counts, dict):
+        raise ValueError("cell manifest needs purpose and replications")
+    if set(counts) != set(PRESCRIBED) or not all(
+        type(n) is int and n >= 1 for n in counts.values()
+    ):
+        raise ValueError(f"replications must be positive integers for {PRESCRIBED}")
+    if purpose == "qualification":
+        # DR2-1: a qualification run needs the complete frozen cell
+        # manifest (every candidate cell at T = T_C2) and every generator
+        # (skew-t, Q2m, Q5, QJ); neither exists yet, so none is accepted.
+        raise ValueError(
+            "qualification runs are refused until the frozen cell manifest "
+            "and all generators are built and verified"
+        )
+    return dict(counts)
+
+
 def bytecode_problem() -> str | None:
     """Why engine code may not be running from its hashed source, or None
     (R6-1): a stale, unchecked or planted `.pyc` can run different code while
@@ -234,7 +270,6 @@ def build(
     engine_commit: str,
     generator_code_sha256: str,
     cell_manifest: object,
-    seed_spec: object,
     image_digest: str,
     exploration_manifest_sha256: str,
 ) -> dict[str, Any]:
@@ -246,7 +281,7 @@ def build(
         "engine_commit": engine_commit,
         "generator_sha256": generator_code_sha256,
         "cell_manifest": cell_manifest,
-        "seed_spec": seed_spec,
+        "seed_spec": seed_spec(prereg_sha256),
         "exploration_manifest_sha256": exploration_manifest_sha256,
         "gating": gating(image_digest),
     }
diff --git a/scripts/d19_run.py b/scripts/d19_run.py
new file mode 100644
index 0000000..31d4f1c
--- /dev/null
+++ b/scripts/d19_run.py
@@ -0,0 +1,132 @@
+"""D-19 run driver (prereg §13 rev 7g item 6), started by the owner's
+launcher on the calibration machine inside the pinned image.
+
+  run --definition PATH --store DIR --namespace threshold
+      One hash-chained chain per cell of the run definition's manifest, in
+      worker processes. Every worker runs the start gate itself before any
+      chunk (R3-3) and builds its chain only from the run-definition hash and
+      the gating the gate returns (FE-5); host provenance is recorded, never
+      compared. Restarting resumes: finished chunks are verified and kept.
+      The replication count comes from the run definition's plan (DR-3),
+      seeds from prereg §8: namespace d19-threshold-v1, anchor = the
+      preregistration hash recorded in the definition (DR-1).
+
+Only the threshold namespace is built: each replication is the classifier
+diagnostics of one generator draw. Development and held-out need the
+tau/z_crit selection and the qualification object and are refused here.
+
+The launcher must take AQT_IMAGE_DIGEST from `docker inspect` on the host
+(FE-4) and run this under `nice 19` with a systemd `MemoryMax` of 2.5 GB.
+Synthetic data only.
+"""
+
+from __future__ import annotations
+
+import os
+import sys
+import tempfile
+from pathlib import Path
+
+os.environ["OPENBLAS_NUM_THREADS"] = "1"  # method V pinned runtime (VS1-4)
+os.environ["OPENBLAS_CORETYPE"] = "Haswell"
+ROOT = Path(__file__).resolve().parents[1]
+sys.path[:0] = [str(ROOT), str(ROOT / "src")]  # this checkout's code only (RR-2)
+# No cached bytecode is read or written, in this process and in every worker,
+# which re-runs these lines when it imports this script (R6-1).
+sys.dont_write_bytecode = True
+sys.pycache_prefix = tempfile.mkdtemp(prefix="d19-no-bytecode-")
+
+import argparse  # noqa: E402
+import multiprocessing  # noqa: E402
+import struct  # noqa: E402
+from concurrent.futures import ProcessPoolExecutor  # noqa: E402
+from typing import Any  # noqa: E402
+
+from calibration import chunks, classifier, rundef  # noqa: E402
+from calibration.generator import Cell, cells_from_manifest, generate  # noqa: E402
+from calibration.seeds import outer_seed, stream  # noqa: E402
+
+NAMESPACES = rundef.SEED_NAMESPACES  # prereg §8
+WORKERS = 2  # §13 rev 7g item 6: two workers, not a run-time choice (DR5-1)
+
+
+def _exact(values: dict[str, float]) -> dict[str, str]:
+    """Each value as its IEEE-754 binary64 bit pattern (big-endian hex):
+    every NaN payload and signed zero kept (DR-4)."""
+    return {n: struct.pack(">d", v).hex() for n, v in sorted(values.items())}
+
+
+def threshold_replication(cell: Cell, anchor: str, rep: int) -> dict[str, str]:
+    """One threshold-run draw: the classifier diagnostics, bit-exact."""
+    seed = outer_seed(anchor, cell.cell_id, NAMESPACES["threshold"], rep)
+    legs = generate(cell, stream(seed, "market"), stream(seed, "columns"))
+    return _exact(classifier.diagnostics(legs.x))
+
+
+def worker(
+    definition: Path, store: Path, namespace: str, cell_id: str, expected: str
+) -> str:
+    """One chain, in its own process: the start gate first, then the chunks
+    (R3-3, FE-5). Returns the chain head."""
+    defn = rundef.load(definition)
+    if rundef.definition_sha256(defn) != expected:  # DR4-1
+        raise ValueError("the run definition changed after the run started")
+    gating = rundef.start_gate(defn, ROOT)
+    manifest = defn["cell_manifest"]
+    cells = {c.cell_id: c for c in cells_from_manifest(manifest)}
+    replications = rundef.run_plan(manifest)[namespace]
+    if defn["seed_spec"] != rundef.seed_spec(defn["prereg_sha256"]):
+        raise ValueError("seed specification is not the §8 one (DR2-2)")
+    cell, anchor = cells[cell_id], defn["seed_spec"]["anchor"]
+    chain = chunks.Chain(
+        store / namespace / cell_id,
+        binding=rundef.definition_sha256(defn),
+        namespace=namespace,
+        cell_id=cell_id,
+        replications=replications,
+        gating=gating,
+        host=rundef.host_provenance(),
+    )
+    return chunks.run(chain, lambda rep: threshold_replication(cell, anchor, rep))
+
+
+def main(argv: list[str] | None = None) -> int:
+    parser = argparse.ArgumentParser(description="D-19 run driver")
+    sub = parser.add_subparsers(dest="command", required=True)
+    run = sub.add_parser("run")
+    run.add_argument("--definition", type=Path, required=True)
+    run.add_argument("--store", type=Path, required=True)
+    run.add_argument("--namespace", required=True)
+    args = parser.parse_args(argv)
+    if args.namespace not in NAMESPACES:
+        print(f"namespace {args.namespace!r} is not built", file=sys.stderr)
+        return 1
+    defn = rundef.load(args.definition)
+    try:
+        cells = cells_from_manifest(defn["cell_manifest"])  # DR-2
+        rundef.run_plan(defn["cell_manifest"])  # DR-3
+        rundef.start_gate(defn, ROOT)  # fail fast; every worker checks again
+    except (ValueError, RuntimeError) as error:
+        print(error, file=sys.stderr)
+        return 1
+    expected = rundef.definition_sha256(defn)  # every worker must load this
+    jobs: list[tuple[Any, ...]] = [
+        (args.definition, args.store, args.namespace, c.cell_id, expected)
+        for c in cells
+    ]
+    # A worker that dies (killed, out of memory) breaks the executor, which
+    # then fails every pending job instead of waiting for it (DR3-1).
+    context = multiprocessing.get_context("spawn")
+    try:
+        with ProcessPoolExecutor(WORKERS, mp_context=context) as pool:
+            heads = list(pool.map(worker, *zip(*jobs, strict=True)))
+    except Exception as error:  # noqa: BLE001 - any worker failure stops the run
+        print(f"run stopped: {type(error).__name__}: {error}", file=sys.stderr)
+        return 1
+    for job, head in zip(jobs, heads, strict=True):
+        print(f"{job[2]}/{job[3]}: {head}")
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
diff --git a/scripts/d19_run_definition.py b/scripts/d19_run_definition.py
index fee06f9..17cfc52 100644
--- a/scripts/d19_run_definition.py
+++ b/scripts/d19_run_definition.py
@@ -2,7 +2,7 @@
 calibration machine inside the pinned image.
 
   record --out PATH --prereg-commit C --engine-commit C
-         --cell-manifest FILE --seed-spec FILE --exploration-manifest FILE
+         --cell-manifest FILE --exploration-manifest FILE
       Measure this machine's gating identity and write the run definition;
       prints its SHA-256. The engine code must equal the engine commit (this
       checkout's HEAD) file by file; the preregistration is read from its
@@ -35,6 +35,7 @@ sys.dont_write_bytecode = True
 sys.pycache_prefix = tempfile.mkdtemp(prefix="d19-no-bytecode-")
 
 from calibration import rundef  # noqa: E402
+from calibration.generator import cells_from_manifest  # noqa: E402
 
 PREREG_PATH = (
     "review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md"
@@ -87,7 +88,6 @@ def main(argv: list[str] | None = None) -> int:
     record.add_argument("--prereg-commit", required=True)
     record.add_argument("--engine-commit", required=True)
     record.add_argument("--cell-manifest", type=Path, required=True)
-    record.add_argument("--seed-spec", type=Path, required=True)
     record.add_argument("--exploration-manifest", type=Path, required=True)
     check = sub.add_parser("check")
     check.add_argument("--definition", type=Path, required=True)
@@ -110,14 +110,20 @@ def main(argv: list[str] | None = None) -> int:
         except (OSError, subprocess.CalledProcessError):
             print(f"cannot read {PREREG_PATH} at {args.prereg_commit}", file=sys.stderr)
             return 1
+        manifest = json.loads(args.cell_manifest.read_bytes())
+        try:  # DR-2, DR-3: a bad manifest never enters a run definition
+            cells_from_manifest(manifest)
+            rundef.run_plan(manifest)
+        except ValueError as error:
+            print(f"cell manifest: {error}", file=sys.stderr)
+            return 1
         code_hash = rundef.generator_sha256(ROOT)
         defn = rundef.build(
             prereg_commit=prereg_id,
             prereg_sha256=hashlib.sha256(prereg).hexdigest(),
             engine_commit=args.engine_commit,
             generator_code_sha256=code_hash,
-            cell_manifest=json.loads(args.cell_manifest.read_bytes()),
-            seed_spec=json.loads(args.seed_spec.read_bytes()),
+            cell_manifest=manifest,
             image_digest=digest,
             exploration_manifest_sha256=hashlib.sha256(
                 args.exploration_manifest.read_bytes()
diff --git a/tests/unit/test_calibration_rundef.py b/tests/unit/test_calibration_rundef.py
index 0b23687..f19895c 100644
--- a/tests/unit/test_calibration_rundef.py
+++ b/tests/unit/test_calibration_rundef.py
@@ -6,11 +6,13 @@ data only."""
 
 from __future__ import annotations
 
+import concurrent.futures
 import importlib.util
 import json
 import os
 import py_compile
 import shutil
+import struct
 import subprocess
 import sys
 import types
@@ -22,6 +24,10 @@ from calibration import dsr, fast, gates, rundef
 
 ROOT = Path(__file__).resolve().parents[2]
 DIGEST = "sha256:" + "ab" * 32
+CELLS = json.dumps({"purpose": "pilot", "replications": {"threshold": 3}, "cells": [
+    {"cell_id": "c-k2", "k": 2, "t": 60, "law": "garch", "dependence": "equi0.5"},
+    {"cell_id": "c-k1", "k": 1, "t": 60, "law": "t5", "dependence": "independent"},
+]})  # fmt: skip
 
 
 def _git(root: Path, *args: str) -> str:
@@ -47,7 +53,8 @@ def _checkout(tmp: Path) -> Path:
     shutil.copytree(ROOT / "src" / "aqt", root / "src" / "aqt",
                     ignore=shutil.ignore_patterns("__pycache__"))  # fmt: skip
     (root / "scripts").mkdir()
-    shutil.copy(ROOT / "scripts" / "d19_run_definition.py", root / "scripts")
+    for script in ("d19_run_definition.py", "d19_run.py"):
+        shutil.copy(ROOT / "scripts" / script, root / "scripts")
     prereg = root / "review" / "governance-statistics-amendment"
     prereg = prereg / "d19-preregistration" / "PREREGISTRATION.md"
     prereg.parent.mkdir(parents=True)
@@ -61,14 +68,13 @@ def _checkout(tmp: Path) -> Path:
 
 def _record(root: Path, out: Path, commit: str) -> subprocess.CompletedProcess[str]:
     inputs = out.parent
-    for name, text in (("cells", '{"cells": ["c1"]}'), ("seeds", '{"anchor": "x"}'),
+    for name, text in (("cells", CELLS), ("seeds", '{"anchor": "x"}'),
                        ("exploration", "{}")):  # fmt: skip
         (inputs / f"{name}.json").write_text(text)
     return _script(
         root, "record", "--out", str(out), "--prereg-commit", "HEAD",
         "--engine-commit", commit,
         "--cell-manifest", str(inputs / "cells.json"),
-        "--seed-spec", str(inputs / "seeds.json"),
         "--exploration-manifest", str(inputs / "exploration.json"),
     )  # fmt: skip
 
@@ -409,7 +415,6 @@ def test_record_refuses_a_file_changed_while_recording(
         "record", "--out", str(out), "--prereg-commit", "HEAD",
         "--engine-commit", _git(root, "rev-parse", "HEAD"),
         "--cell-manifest", str(inputs / "cells.json"),
-        "--seed-spec", str(inputs / "seeds.json"),
         "--exploration-manifest", str(inputs / "exploration.json"),
     ])  # fmt: skip
     assert code == 1 and not out.exists()
@@ -460,7 +465,6 @@ def test_a_git_dir_override_cannot_record_another_repository(tmp_path: Path) ->
         "--out", str(inputs / "d.json"), "--prereg-commit", "HEAD",
         "--engine-commit", _git(other, "rev-parse", "HEAD"),
         "--cell-manifest", str(inputs / "cells.json"),
-        "--seed-spec", str(inputs / "seeds.json"),
         "--exploration-manifest", str(inputs / "exploration.json"),
     ]  # fmt: skip
     done = subprocess.run(command, env=env, cwd=root, capture_output=True,
@@ -479,3 +483,356 @@ def test_the_start_gate_itself_refuses_cached_bytecode(
     monkeypatch.setattr(sys, "dont_write_bytecode", False)
     with pytest.raises(RuntimeError, match="bytecode caching is not disabled"):
         rundef.start_gate({"generator_sha256": "", "gating": {}}, ROOT)
+
+
+def _driver(root: Path, out: Path, store: Path, *args: str,
+            digest: str = DIGEST) -> subprocess.CompletedProcess[str]:  # fmt: skip
+    env = {**os.environ, rundef.IMAGE_DIGEST_ENV: digest}
+    command = [sys.executable, str(root / "scripts" / "d19_run.py"), "run",
+               "--definition", str(out), "--store", str(store), *args]  # fmt: skip
+    return subprocess.run(command, env=env, cwd=root, capture_output=True,
+                          text=True, check=False)  # fmt: skip
+
+
+def test_the_driver_runs_one_bound_chain_per_cell_and_resumes(
+    recorded: tuple[Path, Path], tmp_path: Path
+) -> None:
+    """Two workers, one chain per manifest cell; every chunk carries the
+    run-definition hash and the gating the start gate returned (FE-5); a
+    second run computes nothing new and ends at the same heads."""
+    root, out = recorded
+    store = tmp_path / "store"
+    args = ("--namespace", "threshold")
+    first = _driver(root, out, store, *args)
+    assert first.returncode == 0, first.stderr
+    defn = rundef.load(out)
+    for cell in ("c-k2", "c-k1"):
+        chunk = json.loads(
+            (store / "threshold" / cell / "chunk-0000000.json").read_bytes()
+        )
+        assert chunk["binding"] == rundef.definition_sha256(defn)
+        assert chunk["gating"] == defn["gating"]
+        assert len(chunk["results"]) == 3
+    k1 = json.loads((store / "threshold" / "c-k1" / "chunk-0000000.json").read_bytes())
+    assert set(k1["results"][0]) == classifier_fields(1)
+    before = {p: p.read_bytes() for p in store.rglob("*.json")}
+    second = _driver(root, out, store, *args)
+    assert second.returncode == 0, second.stderr
+    assert second.stdout == first.stdout
+    assert {p: p.read_bytes() for p in store.rglob("*.json")} == before
+
+
+def classifier_fields(k: int) -> set[str]:
+    from calibration import classifier
+
+    return set(classifier.required(k))
+
+
+def test_the_driver_refuses_unbuilt_namespaces_and_a_failed_gate(
+    recorded: tuple[Path, Path], tmp_path: Path
+) -> None:
+    root, out = recorded
+    store = tmp_path / "store"
+    done = _driver(root, out, store, "--namespace", "heldout")
+    assert done.returncode == 1 and "is not built" in done.stderr
+    done = _driver(root, out, store, "--namespace", "threshold", digest="sha256:other")
+    assert done.returncode == 1 and "image digest differs" in done.stderr
+    assert not store.exists()
+
+
+def test_a_worker_runs_the_start_gate_before_any_chunk(
+    recorded: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
+) -> None:
+    """R3-3: the worker itself gates; a refusal there writes nothing."""
+    root, out = recorded
+    script = root / "scripts" / "d19_run.py"
+    spec = importlib.util.spec_from_file_location("d19_run_under_test", script)
+    assert spec is not None and spec.loader is not None
+    monkeypatch.setattr(sys, "dont_write_bytecode", sys.dont_write_bytecode)
+    monkeypatch.setattr(sys, "pycache_prefix", sys.pycache_prefix)
+    driver = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(driver)
+
+    def refused(*_: object) -> dict[str, object]:
+        raise RuntimeError("U_ops: start gate: refused in the worker")
+
+    monkeypatch.setattr(driver.rundef, "start_gate", refused)
+    store = tmp_path / "store"
+    with pytest.raises(RuntimeError, match="refused in the worker"):
+        driver.worker(
+            out, store, "threshold", "c-k2", rundef.definition_sha256(rundef.load(out))
+        )
+    assert not store.exists()
+
+
+def _load_driver(root: Path, monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
+    spec = importlib.util.spec_from_file_location(
+        "d19_run_loaded", root / "scripts" / "d19_run.py"
+    )
+    assert spec is not None and spec.loader is not None
+    monkeypatch.setattr(sys, "dont_write_bytecode", sys.dont_write_bytecode)
+    monkeypatch.setattr(sys, "pycache_prefix", sys.pycache_prefix)
+    driver = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(driver)
+    return driver
+
+
+def test_threshold_seeds_follow_prereg_section_8(
+    recorded: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
+) -> None:
+    """DR-1/DR-5: namespace d19-threshold-v1, anchor = the recorded
+    preregistration hash; every stored draw equals that computation."""
+    from calibration import classifier
+    from calibration.generator import Cell, generate
+    from calibration.seeds import outer_seed, stream
+
+    root, out = recorded
+    driver = _load_driver(root, monkeypatch)
+    monkeypatch.setattr(driver.rundef, "start_gate", lambda defn, _root: defn["gating"])
+    store = tmp_path / "store"
+    driver.worker(
+        out, store, "threshold", "c-k2", rundef.definition_sha256(rundef.load(out))
+    )
+    chunk = json.loads(
+        (store / "threshold" / "c-k2" / "chunk-0000000.json").read_bytes()
+    )
+    defn = rundef.load(out)
+    cell = Cell("c-k2", 2, 60, "garch", "equi0.5")
+    for rep_, stored in enumerate(chunk["results"]):
+        seed = outer_seed(defn["prereg_sha256"], "c-k2", "d19-threshold-v1", rep_)
+        legs = generate(cell, stream(seed, "market"), stream(seed, "columns"))
+        expected = classifier.diagnostics(legs.x)
+        assert stored == {
+            n: struct.pack(">d", v).hex() for n, v in sorted(expected.items())
+        }
+
+
+def test_a_chain_carries_the_gating_its_worker_gate_returned(
+    recorded: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
+) -> None:
+    """FE-5/DR-5: not the definition's copy, the worker gate's return."""
+    root, out = recorded
+    driver = _load_driver(root, monkeypatch)
+    monkeypatch.setattr(driver.rundef, "start_gate", lambda *_: {"from": "worker gate"})
+    store = tmp_path / "store"
+    driver.worker(
+        out, store, "threshold", "c-k1", rundef.definition_sha256(rundef.load(out))
+    )
+    chunk = json.loads(
+        (store / "threshold" / "c-k1" / "chunk-0000000.json").read_bytes()
+    )
+    assert chunk["gating"] == {"from": "worker gate"}
+
+
+def _record_plan(root: Path, inputs: Path, name: str, count: int) -> Path:
+    """A pilot definition with the fixture's cells and `count` draws."""
+    manifest = inputs / f"{name}-cells.json"
+    manifest.write_text(
+        json.dumps({**json.loads(CELLS), "replications": {"threshold": count}})
+    )
+    (inputs / "exploration.json").write_text("{}")
+    out = inputs / f"{name}.json"
+    done = _script(
+        root, "record", "--out", str(out), "--prereg-commit", "HEAD",
+        "--engine-commit", _git(root, "rev-parse", "HEAD"),
+        "--cell-manifest", str(manifest),
+        "--exploration-manifest", str(inputs / "exploration.json"),
+    )  # fmt: skip
+    assert done.returncode == 0, done.stderr
+    return out
+
+
+def test_an_interrupted_run_resumes_identically_and_a_new_plan_cannot_extend_it(
+    recorded: tuple[Path, Path], tmp_path: Path
+) -> None:
+    """DR-3/DR3-2: a 501-draw plan (two chunks): the second chunk deleted as
+    if the run stopped, then resumed byte-identically. A finished 500-draw
+    run cannot be extended by a 501-draw definition: its chunk covers the
+    same range 0-500, so only the definition hash (the count) refuses it."""
+    root, _ = recorded
+    inputs = tmp_path / "in"
+    inputs.mkdir()
+    big = _record_plan(root, inputs, "big", 501)
+    exact = _record_plan(root, inputs, "exact", 500)
+    args = ("--namespace", "threshold")
+    store = tmp_path / "store"
+    assert _driver(root, big, store, *args).returncode == 0
+    chain = store / "threshold" / "c-k1"
+    whole = {p.name: p.read_bytes() for p in chain.iterdir()}
+    assert sorted(whole) == ["chunk-0000000.json", "chunk-0000500.json"]
+    (chain / "chunk-0000500.json").unlink()
+    (chain / "chunk-0000500.tmp").write_bytes(b"torn")
+    assert _driver(root, big, store, *args).returncode == 0
+    assert {p.name: p.read_bytes() for p in chain.iterdir()} == whole
+    finished = tmp_path / "finished"
+    assert _driver(root, exact, finished, *args).returncode == 0
+    extended = _driver(root, big, finished, *args)
+    assert extended.returncode == 1 and "binding does not match" in extended.stderr
+
+
+def test_the_driver_refuses_a_malformed_definition_before_any_store(
+    recorded: tuple[Path, Path], tmp_path: Path
+) -> None:
+    """DR3-3: through the driver, not only the validator."""
+    root, out = recorded
+    defn = rundef.load(out)
+    cells = defn["cell_manifest"]["cells"]
+    defn["cell_manifest"]["cells"] = [cells[0], cells[0]]
+    bad = tmp_path / "bad.json"
+    rundef.write(bad, defn)
+    store = tmp_path / "store"
+    done = _driver(root, bad, store, "--namespace", "threshold")
+    assert done.returncode == 1 and "duplicate cell id" in done.stderr
+    assert not store.exists()
+
+
+def _die(*_: object) -> str:
+    os._exit(3)  # a worker killed mid-run (DR3-1)
+
+
+def test_a_killed_worker_stops_the_run_instead_of_hanging(
+    recorded: tuple[Path, Path], tmp_path: Path
+) -> None:
+    """DR3-1/DR4-2: in a separate process with a timeout, so a regression to a
+    hanging pool fails promptly instead of hanging the test run."""
+    root, out = recorded
+    script = str(root / "scripts" / "d19_run.py")
+    code = "\n".join([
+        "import importlib.util, sys",
+        f"sys.path[:0] = [{str(Path(__file__).parent)!r}]",
+        "import test_calibration_rundef as t",
+        f"spec = importlib.util.spec_from_file_location('drv', {script!r})",
+        "d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)",
+        "d.rundef.start_gate = lambda defn, root: defn['gating']",
+        "d.worker = t._die",
+        f"sys.exit(d.main(['run', '--definition', {str(out)!r}, '--store', "
+        f"{str(tmp_path / 'store')!r}, '--namespace', 'threshold']))",
+    ])  # fmt: skip
+    env = {**os.environ, "PYTHONPATH": f"{ROOT}{os.pathsep}{ROOT / 'src'}"}
+    command = [sys.executable, "-c", code]
+    done = subprocess.run(command, env=env, cwd=root, capture_output=True,
+                          text=True, timeout=180, check=False)  # fmt: skip
+    assert done.returncode == 1 and "BrokenProcessPool" in done.stderr, done.stderr
+
+
+def test_a_worker_refuses_a_definition_replaced_after_the_start(
+    recorded: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
+) -> None:
+    """DR4-1: the worker reloads the file; a different hash is refused."""
+    root, out = recorded
+    driver = _load_driver(root, monkeypatch)
+    monkeypatch.setattr(driver.rundef, "start_gate", lambda d, _root: d["gating"])
+    with pytest.raises(ValueError, match="changed after the run started"):
+        driver.worker(out, tmp_path / "store", "threshold", "c-k1", "0" * 64)
+    assert not (tmp_path / "store").exists()
+
+
+@pytest.mark.parametrize(
+    ("manifest", "message"),
+    [
+        ({"cells": "x"}, "no list of cells"),
+        ({"cells": []}, "no cells"),
+        ({"cells": [{"cell_id": "a", "k": 2, "t": 60, "law": "gaussian"}]}, "exactly"),
+        (
+            {
+                "cells": [
+                    _c := {
+                        "cell_id": "a",
+                        "k": 2,
+                        "t": 60,
+                        "law": "gaussian",
+                        "dependence": "independent",
+                    },
+                    _c,
+                ]
+            },
+            "duplicate",
+        ),  # fmt: skip
+        ({"cells": [{**_c, "cell_id": "../x"}]}, "path-safe"),
+        ({"cells": [{**_c, "k": 3}]}, "K must be"),
+        ({"cells": [{**_c, "t": 8}]}, "T must be"),
+        ({"cells": [{**_c, "law": "cauchy"}]}, "unknown law"),
+        ({"cells": [{**_c, "k": 1, "dependence": "equi0.5"}]}, "K = 1"),
+        ({"cells": [{**_c, "dependence": "clusters"}]}, "clusters"),
+    ],
+)
+def test_a_malformed_cell_manifest_is_refused(manifest: object, message: str) -> None:
+    from calibration.generator import cells_from_manifest
+
+    with pytest.raises(ValueError, match=message):
+        cells_from_manifest(manifest)
+
+
+@pytest.mark.parametrize(
+    ("manifest", "message"),
+    [
+        ({"purpose": "pilot"}, "purpose and replications"),
+        (
+            {"purpose": "x", "replications": {"threshold": 3}},
+            "purpose and replications",
+        ),
+        ({"purpose": "pilot", "replications": {"threshold": 0}}, "positive"),
+        ({"purpose": "pilot", "replications": {"threshold": 3, "dev": 1}}, "positive"),
+        ({"purpose": "qualification", "replications": {"threshold": 3}}, "refused"),
+    ],
+)
+def test_a_bad_run_plan_is_refused(manifest: object, message: str) -> None:
+    with pytest.raises(ValueError, match=message):
+        rundef.run_plan(manifest)
+    prescribed = {"purpose": "qualification", "replications": {"threshold": 300_000}}
+    with pytest.raises(ValueError, match="qualification runs are refused"):
+        rundef.run_plan(prescribed)  # DR2-1
+
+
+def test_the_recorded_seed_specification_is_the_section_8_one(
+    recorded: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
+) -> None:
+    """DR2-2: derived from the preregistration hash; a definition carrying
+    another one is refused by the worker."""
+    root, out = recorded
+    defn = rundef.load(out)
+    assert defn["seed_spec"] == {
+        "anchor": defn["prereg_sha256"],
+        "namespaces": {"threshold": "d19-threshold-v1"},
+    }
+    defn["seed_spec"]["anchor"] = "0" * 64
+    changed = tmp_path / "changed.json"
+    rundef.write(changed, defn)
+    driver = _load_driver(root, monkeypatch)
+    monkeypatch.setattr(driver.rundef, "start_gate", lambda d, _root: d["gating"])
+    with pytest.raises(ValueError, match="seed specification"):
+        driver.worker(changed, tmp_path / "store", "threshold", "c-k1",
+                      rundef.definition_sha256(rundef.load(changed)))  # fmt: skip
+
+
+def test_the_parent_hands_its_definition_hash_to_every_worker(
+    recorded: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
+    capsys: pytest.CaptureFixture[str],
+) -> None:  # fmt: skip
+    """DR5-1/DR5-2: `main` runs exactly two workers and passes the hash of the
+    definition it gated; the file replaced after the parent's gate (here,
+    inside that gate) is refused by the real worker. Threads stand in for
+    processes so the replacement and the pool size can be observed."""
+    root, out = recorded
+    copy = tmp_path / "definition.json"
+    shutil.copy(out, copy)
+    driver = _load_driver(root, monkeypatch)
+    sizes: list[int] = []
+
+    class InProcess(concurrent.futures.ThreadPoolExecutor):
+        def __init__(self, workers: int, mp_context: object = None) -> None:
+            sizes.append(workers)
+            super().__init__(workers)
+
+    def gate_then_replace(defn: dict[str, object], _root: Path) -> object:
+        replaced = {**defn, "engine_commit": "f" * 40}
+        rundef.write(copy, replaced)  # a different definition, same path
+        return defn["gating"]
+
+    monkeypatch.setattr(driver, "ProcessPoolExecutor", InProcess)
+    monkeypatch.setattr(driver.rundef, "start_gate", gate_then_replace)
+    store = tmp_path / "store"
+    code = driver.main(["run", "--definition", str(copy), "--store", str(store),
+                        "--namespace", "threshold"])  # fmt: skip
+    assert code == 1 and "changed after the run started" in capsys.readouterr().err
+    assert sizes == [2] and not store.exists()
```
