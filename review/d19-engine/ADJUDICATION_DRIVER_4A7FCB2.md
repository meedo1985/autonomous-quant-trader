# Adjudication of the GPT-6 Sol re-review 3 of the D-19 run driver at 4a7fcb2

Review: `review/d19-engine/SOL6_DRIVER_REREVIEW_4A7FCB2.md` (DR4-1 blocker,
DR4-2 non-blocking; DR3-1..DR3-3 confirmed repaired). Adjudicated and
repaired by Claude (Opus 5.5) on 2026-10-05.

| ID | Decision | Repair |
|---|---|---|
| DR4-1 BLOCKER | AGREE, repaired | The parent computes `definition_sha256` of the definition it validated and gated, and passes it to every worker; a worker that reloads a definition with another hash refuses before its start gate and before any chunk ("the run definition changed after the run started"). Test: a worker given another expected hash refuses and creates no store. |
| DR4-2 NON-BLOCKING | AGREE, repaired | The killed-worker test runs the driver in a separate Python process with a 180 s timeout, so a regression to a hanging pool fails the test (TimeoutExpired) instead of hanging the run. |

Requirements still carried (no full run before they pass review): FE-4, FE-7.

## Checks after repair (2026-10-05)

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest tests/unit/test_calibration_rundef.py tests/unit/test_calibration_chunks.py tests/unit/test_calibration_engine.py -q -p no:cacheprovider` | 80 passed |
| `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --ignore=<the three files above>` | 1786 passed, 9 skipped |
| `.venv/Scripts/python.exe -m ruff check .` / `ruff format --check .` | clean / 132 files formatted |
| `.venv/Scripts/python.exe -m mypy calibration src` | 62 files, no issues |
| `.venv/Scripts/lint-imports.exe` | 6 kept, 0 broken |
| `pwsh -NoProfile -File review/task6/verify_frozen.ps1` | PASS |
