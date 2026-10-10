# Adjudication of the GPT-6 Sol re-review of the FA repairs at eef38b3

Review: `review/d19-engine/SOL6_FA_REREVIEW_EEF38B3.md` (verdict FIX for
pilot runs; FR-1 blocker, FR-2..FR-5 non-blocking). Adjudicated and
repaired by Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-10. The repairs
are not yet re-reviewed.

| ID | Decision | Repair and evidence |
|---|---|---|
| FR-1 BLOCKER | AGREE, repaired | The lock moved to `<namespace>/.locks/<cell_id>`. A cell id must start with a letter or digit (`generator._CELL_ID`), so no chain directory can be `.locks` and no lock can collide with a chain. No lock file from an earlier layout exists (no calibration run has happened). Test `test_a_lock_never_collides_with_another_cells_chain` (cells `pilot-a` and `pilot-a.lock`); it fails on the eef38b3 layout and passes after. |
| FR-2 NON-BLOCKING | AGREE, repaired | `main` snapshots `multiprocessing.active_children()` before creating the pool and on failure terminates only children that appeared after it. Test `test_a_failure_terminates_only_the_runs_own_workers[chain failed]`. |
| FR-3 NON-BLOCKING | AGREE, repaired | The failure path catches `BaseException`: the run's workers are terminated on Ctrl-C / `SystemExit` too, then the interruption is re-raised; ordinary failures still exit 1. Test `test_a_failure_terminates_only_the_runs_own_workers[KeyboardInterrupt]`. |
| FR-4 NON-BLOCKING | AGREE, repaired | `run` lists the directories `mkdir(parents=True)` will create and fsyncs the parent of each (POSIX), so the namespace and cell entries are durable on a first run. Not testable on the Windows dev machine (directory fsync is POSIX only); covered by inspection. |
| FR-5 NON-BLOCKING | AGREE, repaired | The driver's module docstring (its run procedure for the launcher) now says to stop the whole service control group, never the parent alone, and why. |

Still open from the earlier adjudication: FA-1 governance part (owner) and
the FA-2 `runtime_identity` proposal; FE-4 and FE-7 carried. No
calibration was run.

## Checks after repair (2026-10-10, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_chunks.py -q -p no:cacheprovider` (first) | 1 | 13 passed, 1 failed: the new FR-1 test passed `root` twice to the `_chain` helper (`TypeError`); test fixed to use `dataclasses.replace` |
| same, after the test fix | 0 | 14 passed |
| same, `-k collides`, with `calibration/chunks.py` at eef38b3 (stashed) | 1 | 1 failed (the test detects FR-1) |
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py -q -p no:cacheprovider -k terminates_only` | 0 | 2 passed |
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py tests/unit/test_calibration_chunks.py -q -p no:cacheprovider` | 0 | 76 passed in 258.74 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider --ignore=tests/unit/test_calibration_rundef.py --ignore=tests/unit/test_calibration_chunks.py` | 0 | 1801 passed, 9 skipped in 361.20 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python.exe -m ruff format --check .` | 0 | 132 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py` | 0 | No issues in 63 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| `C:\Users\PMP Cordination\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and exact inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |
