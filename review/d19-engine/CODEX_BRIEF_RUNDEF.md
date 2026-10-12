You are implementing one bounded piece of the D-19 calibration engine in the repository in your working directory (branch `d19-calibration-engine`, already checked out). Follow AGENTS.md and the `ponytail` skill at full intensity: read first, reuse what exists, smallest complete change. Do NOT commit, push, use the network, or touch `src/aqt/`, `docs/`, `protocols/`, `schemas/`, `specs/`, `FROZEN_HASHES.json` or any `.sha256` file. Synthetic data only.

## Read first
- `git show origin/docs/d19-recommendation:review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md` — section 13 (rev 7g, accepted), item 6 "Running on the server" is the specification for this task. Section 8 (seeds) for context.
- `calibration/` (all modules), especially `chunks.py` (chunk store; `Chain.gating` is compared on every chunk, `Chain.host` is recorded only), `dsr.py` (`runtime_identity`, `canaries`, `v_runtime_check`, `evaluate`, numerics "v"), `seeds.py`, `generator.py`, `gates.py`, `classifier.py`.
- `scripts/d19_pilot.py`, `tests/unit/test_calibration_engine.py`, `tests/unit/test_calibration_chunks.py`.

## Build
1. `calibration/rundef.py`:
   - `reference_vectors() -> dict[str, str]`: the reference-vector suite. A small fixed set of synthetic cases (cover K in {1, 2, 5, 20}; at least one GARCH and one AR law; T small enough that the whole suite runs in well under 60 s on a laptop core). Each case: fixed seed via `seeds.outer_seed` with a fixed anchor and namespace "refvec", `generator.generate`, then `dsr.evaluate(..., numerics="v")` and, when there is a nominee, `gates.u_g` as the pilot does; the value is the SHA-256 of the canonical JSON (`seeds.cj`) of every output (floats exactly as produced). Keyed by a stable case name.
   - `host_provenance() -> dict[str, str]`: CPU model, microcode, host kernel release. On Linux read `/proc/cpuinfo` (`model name`, `microcode`, first CPU) and `platform.release()`; elsewhere `platform.processor()` and `platform.release()`, microcode "". Never compared.
   - `gating(image_digest: str) -> dict`: `{"identity": dsr.runtime_identity(), "image_digest": image_digest, "canaries": dsr.canaries(), "reference_vectors": reference_vectors()}`.
   - `build(*, prereg_commit, engine_commit, cell_manifest, seed_spec, image_digest, exploration_manifest_sha256, generator_sha256) -> dict`: the run definition of §13 item 6 (preregistration commit, engine commit, generator code hash, cell manifest, seed specification, image digest, exploration-data manifest hash, gating). Include `"record_type": "aqt.d19.run_definition.v1"`.
   - `definition_sha256(defn) -> str` = `seeds.sha(defn)`. `write(path, defn)` writes canonical JSON (temp file + `os.replace`); `load(path)` reads it and refuses (ValueError) a file that is not a dict with that record_type.
   - `generator_sha256(root: Path) -> str`: SHA-256 over the sorted (relative path, file bytes) of every `calibration/*.py` file — the "generator code" hash.
   - `start_gate(defn) -> dict`: run on every start and resume (§13 item 6 "Start and resume"): `dsr.v_runtime_check(defn["gating"]["identity"], defn["gating"]["canaries"])`; the image digest from environment variable `AQT_IMAGE_DIGEST` must equal `defn["gating"]["image_digest"]`; `reference_vectors()` must equal the recorded ones. Any mismatch raises `RuntimeError` starting "U_ops:" naming which part differs. Returns `defn["gating"]` (what every `chunks.Chain.gating` must be).
2. `scripts/d19_run_definition.py` with subcommands `record --out PATH --prereg-commit C --engine-commit C --cell-manifest FILE --seed-spec FILE --exploration-manifest FILE` (image digest from `AQT_IMAGE_DIGEST`, required) printing the definition hash; and `check --definition PATH` running `start_gate` and printing `start gate passed: <hash>` or exiting 1 with the error. Set the method-V environment exactly as `scripts/d19_pilot.py` does before importing NumPy.
3. `tests/unit/test_calibration_rundef.py`: reference vectors deterministic across two calls and across a fresh subprocess with the pinned environment (pattern: `test_method_v_runtime_check_needs_the_pinned_runtime`); `build`/`write`/`load` round-trip and hash stability; `start_gate` passes in a fresh pinned subprocess with matching `AQT_IMAGE_DIGEST`, and fails ("U_ops") on a wrong image digest, on a changed reference vector, and on a changed canary; `load` refuses a wrong record_type; `generator_sha256` changes when a calibration file changes (use a tmp copy). Keep tests fast.

## Checks you must run and report (exact command + result)
- `.venv/Scripts/python.exe -m pytest tests/unit/test_calibration_rundef.py tests/unit/test_calibration_chunks.py tests/unit/test_calibration_engine.py -q -p no:cacheprovider`
- `.venv/Scripts/python.exe -m ruff check calibration scripts tests` and `.venv/Scripts/python.exe -m ruff format --check calibration scripts tests`
- `.venv/Scripts/python.exe -m mypy calibration` (2 pre-existing import-untyped errors for `aqt.metrics` are known; report any others)
- Time of `reference_vectors()` on this machine.

If pytest cannot run in your sandbox, say so and give the code anyway. Finish with: files changed, any deviation from this brief and why, open questions.

## IMPORTANT: how to deliver (overrides "Checks you must run")
You run in a READ-ONLY sandbox: you cannot write files. Read everything you need, run read-only commands (you may run Python snippets that write nothing to the repo, e.g. timing `reference_vectors` logic in memory). Then output the COMPLETE contents of every new or changed file, each as:

=== FILE: <relative path> ===
```python
<entire file>
```

No diffs, no partial files, no ellipses. The orchestrator writes them verbatim and runs the checks. After the files, list deviations and open questions.
