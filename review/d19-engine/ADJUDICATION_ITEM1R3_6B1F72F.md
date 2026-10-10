# Adjudication of the GPT-6 Sol focused re-review at 6b1f72f

Review: `review/d19-engine/SOL6_ITEM1R2_REREVIEW_6B1F72F.md` (FIX for pilot
use of the choices report; I1R3-1, I1R3-2; from a packet; I1R2-2 closed).
Adjudicated and repaired by Claude Opus 5.5 (`claude-opus-5-5`) on
2026-10-10. Not yet re-reviewed.

Rather than add the two cases one at a time, `choices.consistent` was
rewritten to check the whole shape of a development record against
`dsr.evaluate` and `dev_replication`, field by field:

| ID | Decision | Repair and evidence |
|---|---|---|
| I1R3-1 Medium | AGREE, repaired | Outcomes reached before the block rule is applied (rules 1-4 and `UNSUPPORTED_LAW`, `RULE_FREE`) must be one identical result under both rules; `length_ratio` (max L_j/T, rule-free) must be equal under both rules in every case; K = 1 entries stay identical. Test `test_outcomes_before_the_block_rule_and_column_fields_must_agree` (largest `INVALID_SERIES`, median `ZERO_VARIANCE_COLUMN`; differing max L/T). |
| I1R3-2 Medium | AGREE, repaired | Per entry, `length_ratio` is a finite hex exactly from rule 4 on (`BLOCK_LENGTH_CAPPED`, `UNSUPPORTED_LAW`, rules 5-6, available) and null otherwise; `z`, `s0`, `block`, nominee as in I1R2-1. Per record, `column_checks` must match rules 1-2 (a column not finite iff `INVALID_SERIES`; otherwise a zero-variance column iff `ZERO_VARIANCE_COLUMN`); `columns` is null iff rules 1-2 stopped the family, otherwise K pairs of finite-or-null length and cap flag, a null length iff `BLOCK_LENGTH_UNAVAILABLE`, and (when all lengths exist) a capped column iff `BLOCK_LENGTH_CAPPED`. Tests: the same test above (every cause code valid at K = 2; `UNSUPPORTED_LAW` without max L/T or without columns; `INVALID_SERIES` with lengths or with all columns finite; `ZERO_VARIANCE_COLUMN` without a zero-variance column; `BLOCK_LENGTH_CAPPED` without a capped column; `BLOCK_LENGTH_UNAVAILABLE` with every length; an available result with a capped column). The test helper `_record` now builds whole records per cause code. |

Also: `test_development_records_equal_an_independent_section_2_computation`
now asserts that every real development record (accepted and refused, both
cells) passes `consistent` with the thresholds it was made with, so the
stricter check is shown not to refuse records the driver writes.

No calibration was run.

## Checks after repair (2026-10-10, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_choices.py -q -p no:cacheprovider` (first run) | 1 | 16 passed, 1 failed: an older assert matched the previous message text ("finite"); updated to the new message ("z does not match") |
| same, after the update | 0 | 17 passed |
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py -q -p no:cacheprovider -k "column_checks or development_run_needs or independent_section_2 or margin_failure"` | 0 | 5 passed |
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py -q -p no:cacheprovider -k independent_section_2` (with the real-record check) | 0 | 2 passed |
| `.venv/Scripts/python -m pytest` the five calibration files (`rundef`, `chunks`, `reduce`, `binomial`, `choices`) `-q -p no:cacheprovider` | 0 | 108 passed in 332.97 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those five files | 0 | 1801 passed, 9 skipped in 394.96 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 139 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_choose.py` | 0 | No issues in 67 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |
