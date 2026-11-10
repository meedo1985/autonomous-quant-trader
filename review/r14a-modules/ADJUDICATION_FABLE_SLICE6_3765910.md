# Adjudication of the Fable 5.2 review of slices 6a/6b part 1 (R14S6-F-1..10)

Review record: `review/r14a-modules/FABLE_REVIEW_SLICE6_3765910.md` (reviewer model `claude-fable-5-2`, verdict FIX, committed `a74dddf`).
Adjudicated and repaired by Claude Opus 5.5 (`claude-opus-5-5`) on 2026-11-10, on the owner's "go ahead with the repairs" (code fixes F-1, F-2, F-6, F-7, F-9).
This record proposes nothing for governance and activates nothing.

| ID | Decision | Change / reason |
|---|---|---|
| R14S6-F-1 | accepted, repaired | `load_line266` with `sources` now refuses (`SeedError`) a listed module that is already in `sys.modules`, instead of skipping its hash check. Checked first: in a fresh process, importing `calibration.c2_confirmation` loads neither listed module (`aqt.core.paths`, `aqt.core.preregistration`), so a legitimate `start` is unaffected. New fresh-process test: `aqt.core.paths` is preloaded and passed with a hash that matches nothing, and the load is refused. The old code returned "loaded". The in-process start tests' fixture now unloads the two modules, because each test already stands for a fresh process (`_START_FAILED`). |
| R14S6-F-2 | accepted, repaired | `completed_entry` decodes exactly: the key set must equal the schema; ids must be non-empty strings; `configuration_hash` and `d_sha256` must be 64 lower-case hex characters; each `d` item must be 16; days must round-trip through `_time` and be consecutive; `window_id` must equal the days' window; `len(d)` must equal `len(days)`; values must be finite; `(d, d_sha256, reason)` must be either (list, hash, null) or (null, null, non-empty string). Any breach is a `CycleError`. There is one parametrized test with 13 cases, plus an empty-reason case. |
| R14S6-F-3 | accepted in direction (as R14D6B-S-2), design rev 2 | Code binding waits for rev 2. The test is renamed `test_a_d_that_does_not_match_its_own_hash_is_refused`, and a comment states what it does not prove. |
| R14S6-F-4 | accepted, owner/S4 proposal in rev 2 | Record fields (`estimator_seed`, data-manifest identity, code identity) will be proposed in DESIGN_SLICE6B rev 2. Not code now. |
| R14S6-F-5 | open question to owner | P18-7 binding for how an unavailable run's reason survives nomination. Not code. |
| R14S6-F-6 | accepted, repaired | `trial_path` refuses a `w0` off the hour and a non-integer or negative warm-up (C-T refusal, not floor or crash). Test added. |
| R14S6-F-7 | accepted, repaired | Tests added: a gap inside a series of the right length; another interval; the `screen.TrialError` to C-T mapping (by making `confirmation_path` raise); and `CostModelError` and `FeatureFactoryError` recorded as unavailable. A duplicate hour cannot reach the read: `BarSeries` refuses it at construction, and the test comment says so. |
| R14S6-F-8 | accepted as a pre-signing step, no code | Run the authenticated-load test on the qualified Linux image before signing and record its Python version. |
| R14S6-F-9 | strict check N/A for the imported file, reason recorded | All 10 errors are in the older `tests/unit/test_calibration_screen.py`: 8 non-explicit re-exports of `calibration.screen`, 1 `append` result and 1 tuple type. That file is outside this task. Strict mypy on this task's files, with imports followed silently, is clean (below). The errors are not silenced. |
| R14S6-F-10 | accepted | The review record is now committed, and this record lists the validation commands. Part 1's validation goes into the 6b local gate record when 6b closes. |

## Validation (2026-11-10, Windows, Python 3.14.7, `.venv`)

| Command | Result |
|---|---|
| `pytest -q -p no:cacheprovider tests/unit/test_c2_confirmation_*.py tests/unit/test_c2_lockbox*.py` | 402 passed (5 min 38 s) |
| `ruff check src tests calibration` | All checks passed |
| `ruff format --check src tests calibration` | 164 files already formatted |
| `mypy src` | no issues, 56 files |
| `mypy --strict --follow-imports=silent calibration/c2_confirmation.py tests/unit/test_c2_confirmation_run.py tests/unit/test_c2_confirmation_start.py` | no issues, 3 files |
| `lint-imports` | 7 kept, 0 broken |
| full suite at `7fd85f9` (`pytest --collect-only`: 2739 tests) | **2729 passed, 10 skipped, 0 failed**. Run in batches because two single runs were stopped for low memory: `tests/canaries tests/integration tests/oracles tests/reference` gave 262 passed. The c2 files gave 402 passed (above). The other 47 unit files, in alphabetical order, ran as 6/6/6/2/8/19 files and gave 184, 111, 164, 191 + 1 skipped, 704 + 9 skipped, and 711 passed. |

Section 16: if `calibration/c2_confirmation.py` is a protected component, these repairs still need the different-model and owner PR review before merge. The branch is not merged.
