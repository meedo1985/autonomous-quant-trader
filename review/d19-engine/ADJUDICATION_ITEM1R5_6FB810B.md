# Adjudication of the GPT-6 Sol focused re-review at 6fb810b

Review: `review/d19-engine/SOL6_ITEM1R4_REREVIEW_6FB810B.md` (FIX for pilot
use; I1R5-1..I1R5-3; I1R4-1 closed, I1R4-2 partly; **the stated scope of
`consistent` accepted for pilot use**; from a packet). Adjudicated and
repaired by Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-10. Not yet
re-reviewed.

| ID | Decision | Repair and evidence |
|---|---|---|
| I1R5-1 Medium | AGREE, repaired | When the recomputed family blocks are equal under both rules, the two entries must be identical: one input, family seed, classifier result and block give one `dsr.evaluate` result. Test `test_equal_blocks_one_result_and_k_t_positive_integers` (lengths 3, 3: largest available, median `INVALID_REPLICATE`). The old K = 2 case of `test_at_k_1_both_rules_must_be_one_result` was itself such an impossible record (equal blocks, different z); it now uses lengths 2 and 4 (blocks 4 and 3), where the rules may differ. |
| I1R5-2 Medium | AGREE, repaired | Decoded `K` and `T` must both be positive integers before anything else is checked. Same test (T = 9.5, -9, NaN, inf). |
| I1R5-3 Medium | AGREE, repaired | T = 0 is refused by the same check before any division, and `ArithmeticError` joins the exceptions that `consistent` reports as "malformed record" instead of raising. Same test (T = 0). |

The real-data driver tests (development records of both cells, accepted
and refused, and `d19_choose` end to end) still pass the stricter check.

No calibration was run.

## Checks after repair (2026-10-10, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_choices.py -q -p no:cacheprovider` (first run) | 1 | 18 passed, 1 failed: the old K = 2 case of `test_at_k_1_both_rules_must_be_one_result` was an impossible record the new rule correctly refuses; the case was rebuilt with different blocks |
| same, after the rebuild | 0 | 19 passed |
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py -q -p no:cacheprovider -k "column_checks or development_run_needs or independent_section_2 or margin_failure"` | 0 | 5 passed |
| `.venv/Scripts/python -m pytest` the five calibration files (`rundef`, `chunks`, `reduce`, `binomial`, `choices`) `-q -p no:cacheprovider` | 0 | 110 passed in 353.86 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those five files | 0 | 1801 passed, 9 skipped in 357.26 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 139 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_choose.py` | 0 | No issues in 67 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |
