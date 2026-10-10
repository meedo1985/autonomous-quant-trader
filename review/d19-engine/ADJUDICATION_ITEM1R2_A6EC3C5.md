# Adjudication of the GPT-6 Sol re-review of the I1R repairs at a6ec3c5

Review: `review/d19-engine/SOL6_ITEM1R_REREVIEW_A6EC3C5.md` (FIX for pilot
use of the choices report; I1R2-1, I1R2-2; made from an attached packet).
Adjudicated and repaired by Claude Opus 5.5 (`claude-opus-5-5`) on
2026-10-10. Not yet re-reviewed.

| ID | Decision | Repair and evidence |
|---|---|---|
| I1R2-1 Medium | AGREE, repaired | `choices.consistent` now checks every field against what that return of `dsr.evaluate` sets: an available result has finite `z`, `s0`, `block` and an integer nominee in `range(K)` equal to the `U_G` nominee; a rules 5-6 refusal (`INVALID_REPLICATE`, `INVALID_ARITHMETIC`) has a finite `block` and null `z`, `s0`, nominee; every other refusal (rules 1-4, `UNSUPPORTED_LAW`) has all four null. Cause-code order and the K = 1 equality are kept. Test `test_fields_that_dsr_evaluate_cannot_produce_are_refused` corrupts valid records field by field (nominee null, out of range, boolean, string; a rules 1-4 refusal carrying z, S0, L or a nominee; `UNSUPPORTED_LAW` with L; a rules 5-6 refusal without L, with a NaN L, or with z). The test helper now builds records exactly as `dev_replication` writes them, and the real-data driver tests (development and `choose` end to end) still pass the stricter check. |
| I1R2-2 Medium | AGREE, repaired | `column_checks` (now a function in `scripts/d19_run.py`) records raw per-column predicates `[all finite, nonzero sample variance]` with the variance `null` (not evaluated) for a non-finite column; documented as per-column predicates for §9, not the family outcome. Test `test_column_checks_do_not_claim_a_variance_check_for_a_non_finite_column` (finite, constant, NaN and inf columns). |

On the reviewer's test remark: the NaN-diagnostic refusal is enforced by
`classifier.within`, which returns False for any non-finite diagnostic
(`calibration/classifier.py`, reviewed in D19CR-1); `consistent` relies on
it unchanged.

No calibration was run.

## Checks after repair (2026-10-10, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_choices.py -q -p no:cacheprovider` | 0 | 16 passed |
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py -q -p no:cacheprovider -k "column_checks or development_run_needs or independent_section_2 or margin_failure"` | 0 | 5 passed |
| `.venv/Scripts/python -m pytest` the five calibration files (`rundef`, `chunks`, `reduce`, `binomial`, `choices`) `-q -p no:cacheprovider` | 0 | 107 passed in 338.58 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those five files | 0 | 1801 passed, 9 skipped in 367.75 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 139 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_choose.py` | 0 | No issues in 67 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |
