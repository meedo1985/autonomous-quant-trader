# Adjudication of the CI findings on `2f062b7` (draft PR #83)

- Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-02, the module's author,
  against CI run 41484940358 on `2f062b7`. Repairs are in the commit that adds this file;
  the owner approved both repairs before they were made.
- Format: `ID | source | Verdict | reasoning and evidence | disposition | validation`.

| ID | Source | Verdict | Reasoning and evidence | Disposition | Validation |
|---|---|---|---|---|---|
| R14L5-CI-1 | CI `calibration-tests` and `checks`: `test_d19_deploy::test_the_engine_loads_no_third_party_package_but_numpy` | AGREE (BLOCKER) | `calibration/c2_lockbox.py` imported `trial_seed` from `aqt.core.preregistration`, which imports `jsonschema` at module load. The engine image is numpy-only, so the lockbox module would fail to import in the image. Introduced in slice 2 (`8b62696`). | Repaired without touching `aqt.core.preregistration`: `c2_lockbox.trial_seed` rebuilds L266's seed byte for byte (domain `aqt.trial_seed.v1`, compact canonical JSON array, SHA-256 hex) and refuses the same inputs with `LockboxError`; `_check_identity` catches `LockboxError` in place of `PreregistrationError` (same `IDENTITY_MISMATCH`). | `test_trial_seed_is_the_preregistration_one_and_refuses_the_same` (equality on three triples, the domain constant, and the same five refusals); `test_d19_deploy` engine-import test passes. |
| R14L5-CI-2 | CI `checks`: `test_c2_lockbox_run::test_model_trial_refits_with_estimator_seed` (`RUN:RUN_FAILED`) | AGREE (test placement) | The hidden error is `ModuleNotFoundError: sklearn` inside `screen.build_model`: the `checks` job (hosted Python 3.12, no model libraries) ran the lockbox tests, which belong to the engine runtime. Not a lockbox logic defect. | `.github/workflows/ci.yml`: `tests/unit/test_c2_lockbox*.py` now run in `calibration-tests` (the image's numpy and model libraries) and are ignored in `checks`. | CI on the repair commit. |

**Open before signing C2 (unchanged):** the launch route; acceptance provenance (owner
decision); the reference vectors on the qualified image; the S4 format bindings; the store
build's §D-3.7 obligations; the source of an authenticated `family_seed_f`.

Validation (Mac, repo `.venv`, Python 3.12.16; this CPU lacks AVX2, so the Haswell-pinned
engine tests run in CI only): lockbox tests 123 passed and 1 not runnable here (needs
sklearn, R14L5-CI-2); engine-import test passed; ruff, ruff format, mypy src, mypy strict on
the changed files, lint-imports (7 kept) clean. `test_calibration_rundef` passed in CI on
`2f062b7`.
