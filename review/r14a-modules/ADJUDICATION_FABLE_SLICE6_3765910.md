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

## Re-check adjudication (R14S6R-F-1..6)

Re-check record: `review/r14a-modules/FABLE_RECHECK_SLICE6_7FD85F9.md` (`claude-fable-5-2`, ACCEPT WITH NOTES, committed `c42a52e`). It was adjudicated and repaired by Claude Opus 5.5 (`claude-opus-5-5`) on 2026-11-10.

| ID | Decision | Change / reason |
|---|---|---|
| R14S6R-F-1 | repaired | In `completed_entry`, `days[-1] + DAY` is computed inside the `try`, and `OverflowError` is mapped to `CycleError` (case `last_day_overflows`). |
| R14S6R-F-2 | repaired (tests) | Every malformed case now has `match=` naming its clause. Six cases were added: `null_d_hash_and_reason`, `upper_config_hash`, `repeated_day`, `empty_id`, `empty_days` and `last_day_overflows`. `d_length` re-makes the hash, so only the length is wrong. |
| R14S6R-F-3 | repaired, in part | With `sources`, `load_line266` refuses if any `LINE266_MODULES` name, or any listed name, is already loaded, whether or not it is listed. A fresh-process test covers `{}` with `aqt.core.paths` preloaded. **Not repaired:** requiring `sources` to equal the listed set exactly. Extra names in `sources` are how the existing gate tests inject probe modules, and `start` always passes exactly `LINE266_MODULES` (not reachable through `start`). |
| R14S6R-F-4 | repaired | `trial_path` refuses a naive `w0` and a `window_hours` that is not an int of at least 1 (bool refused). One older test now expects the new message for a float warm-up. |
| R14S6R-F-5 | repaired | `trial_result` ends with a `completed_entry` self-check, so it never writes a record the look would refuse (test: empty `cycle_id`). |
| R14S6R-F-6 | not repaired (note) | `start` reports a preloaded module only as `line 266 did not load: SeedError`. This is deliberate: `start` reports the type only, as for every line-266 failure. The fresh-process test proves the refusal. |

Validation (2026-11-10): the c2 confirmation and lockbox files gave 411 passed. `ruff check` passed; `ruff format --check` reported 164 files already formatted. `mypy src` was clean. `mypy --strict --follow-imports=silent` on the 3 task files was clean. `lint-imports` kept 7 contracts and broke 0. The full suite was not rerun: only `calibration/c2_confirmation.py` and its two test files changed, and no other code imports that module (checked with grep; `c2_lockbox.py` only names its path, and the lockbox tests are among the 411).
