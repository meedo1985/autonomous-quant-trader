# Adjudication of the GPT-6 Sol re-review 2 of the D-19 run driver at 31be6f9

Review: `review/d19-engine/SOL6_DRIVER_REREVIEW_31BE6F9.md` (DR3-1 blocker;
DR3-2, DR3-3 non-blocking; DR2-1..DR2-3 confirmed repaired). Adjudicated and
repaired by Claude (Opus 5.5) on 2026-10-05.

| ID | Decision | Repair |
|---|---|---|
| DR3-1 BLOCKER | AGREE, repaired | `multiprocessing.Pool.starmap` replaced by `concurrent.futures.ProcessPoolExecutor` (spawn context): a worker that dies breaks the executor, which fails pending jobs with `BrokenProcessPool` instead of waiting; any worker failure prints "run stopped: ..." and exits 1. Test: a worker that calls `os._exit(3)` stops the run with exit 1 and `BrokenProcessPool` reported. The old `Pool` version was not run against this test, since it would hang the test process (the reviewer's finding). |
| DR3-2 NON-BLOCKING | AGREE, repaired | The extension test now runs a finished 500-draw definition, then a 501-draw definition with identical cells on the same store: the chunk range 0-500 is identical, so only the binding (definition hash, which includes the count) refuses it ("binding does not match"). The interruption-resume check stays on a fresh store. |
| DR3-3 NON-BLOCKING | AGREE, repaired | A definition with a duplicated cell is run through the driver: exit 1, "duplicate cell id", no store created. |

Requirements still carried (no full run before they pass review): FE-4, FE-7.

## Checks after repair (2026-10-05)

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest tests/unit/test_calibration_rundef.py tests/unit/test_calibration_chunks.py tests/unit/test_calibration_engine.py -q -p no:cacheprovider` | 79 passed |
| `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --ignore=<the three files above>` | 1786 passed, 9 skipped |
| `.venv/Scripts/python.exe -m ruff check .` / `ruff format --check .` | clean / 132 files formatted |
| `.venv/Scripts/python.exe -m mypy calibration src` | 62 files, no issues |
| `.venv/Scripts/lint-imports.exe` | 6 kept, 0 broken |
| `pwsh -NoProfile -File review/task6/verify_frozen.ps1` | PASS |
