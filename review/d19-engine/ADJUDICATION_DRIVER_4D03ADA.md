# Adjudication of the GPT-6 Sol re-review of the D-19 run driver at 4d03ada

Review: `review/d19-engine/SOL6_DRIVER_REREVIEW_4D03ADA.md` (DR2-1..DR2-3;
the spawn path, namespace, K = 1 fields, bit-pattern encoding and chunk
binding confirmed; `prereg_sha256` accepted as the §8 preregistration hash).
Adjudicated and repaired by Claude (Opus 5.5) on 2026-10-05.

| ID | Decision | Repair |
|---|---|---|
| DR2-1 BLOCKER | AGREE, repaired | `rundef.run_plan` refuses every `qualification` manifest until the complete frozen cell manifest (every candidate cell at T = T_C2) and all generators (skew-t, Q2m, Q5, QJ) are built and verified; only `pilot` runs are possible now. Tests: a prescribed-count qualification plan is refused. |
| DR2-2 BLOCKER | AGREE, repaired | The seed specification is derived, never supplied: `rundef.seed_spec(prereg_sha256)` = §8 anchor and namespaces, written by `build`; `--seed-spec` removed from `record`. The driver uses the recorded anchor and refuses (in each worker) a definition whose seed specification is not the §8 one. Test: the recorded spec equals the derived one; a definition with another anchor is refused. |
| DR2-3 NON-BLOCKING | AGREE, repaired | The changed-plan test now keeps the cells identical and changes only the count (3 → 501). |

Requirements still carried (no full run before they pass review): FE-4
(launcher: digest from host `docker inspect`, `nice 19`, `MemoryMax`), FE-7
(re-pilot measures non-finite threshold draws). Development and held-out
namespaces and qualification runs are not available yet.

## Checks after repair (2026-10-05)

The single background full-suite run was stopped by the system for low
memory before pytest finished (format and import contracts had passed). The
suite was then run in the foreground in two parts:

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest tests/unit/test_calibration_rundef.py tests/unit/test_calibration_chunks.py tests/unit/test_calibration_engine.py -q -p no:cacheprovider` | 77 passed |
| `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --ignore=<the three files above>` | 1786 passed, 9 skipped |
| `.venv/Scripts/python.exe -m ruff check .` / `ruff format --check .` | clean / 132 files formatted |
| `.venv/Scripts/python.exe -m mypy calibration src` | 62 files, no issues |
| `.venv/Scripts/lint-imports.exe` | 6 kept, 0 broken |
| `pwsh -NoProfile -File review/task6/verify_frozen.ps1` | PASS |
