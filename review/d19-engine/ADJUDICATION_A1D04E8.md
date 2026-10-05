# Adjudication of the GPT-6 Sol re-review of the D-19 engine at a1d04e8

Review: `review/d19-engine/SOL6_REREVIEW_A1D04E8.md` (R6-1, R6-2; R5-1 and
R5-2 confirmed). Adjudicated and repaired by Claude (Opus 5.5) on 2026-10-05.

| ID | Decision | Repair |
|---|---|---|
| R6-1 BLOCKER | AGREE, repaired | The entry script sets `sys.dont_write_bytecode = True` and points `sys.pycache_prefix` at a new empty temporary directory before importing any engine module, so no cached `.pyc` (stale, unchecked-hash or planted) is ever read. `start_gate` refuses unless `bytecode_problem()` is None: caching disabled, the cache directory empty, and every `aqt`/`calibration` module loaded from a `.py` source with no cache outside that directory. Tests: a planted unchecked-hash `.pyc` for `calibration/seeds.py` that prints a marker never runs and the gate passes on the source; this pytest process (caching on) fails `bytecode_problem()`. Mutation check: without the two settings the planted-bytecode test fails. Driver requirement added: every worker entry point sets the same two settings first. |
| R6-2 MAJOR | AGREE, repaired | Every git call runs with all `GIT_*` environment variables removed, so `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE`/object-directory overrides cannot point `record` at another repository. Test: with `GIT_DIR`/`GIT_WORK_TREE` naming another repository with identical engine files, recording that repository's HEAD is refused. Mutation check: without the filter the test fails. |

Carried to the driver task (no full run before they pass review): R3-3,
FE-4, FE-5, FE-7, and the R6-1 entry-point settings in every worker.

## Checks after repair (2026-10-05)

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider` | 1840 passed, 9 skipped |
| `.venv/Scripts/python.exe -m ruff check .` / `ruff format --check .` | clean / 131 files formatted |
| `.venv/Scripts/python.exe -m mypy calibration src` | 62 files, no issues |
| `.venv/Scripts/lint-imports.exe` | 6 kept, 0 broken |
| `pwsh -NoProfile -File review/task6/verify_frozen.ps1` | PASS |
