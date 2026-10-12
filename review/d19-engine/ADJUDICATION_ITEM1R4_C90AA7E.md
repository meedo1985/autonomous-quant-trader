# Adjudication of the GPT-6 Sol focused re-review at c90aa7e

Review: `review/d19-engine/SOL6_ITEM1R3_REREVIEW_C90AA7E.md` (FIX for pilot
use; I1R4-1, I1R4-2; I1R3-1/2 repaired; from a packet). Adjudicated and
repaired by Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-10. Not yet
re-reviewed.

| ID | Decision | Repair and evidence |
|---|---|---|
| I1R4-1 Medium | AGREE, repaired | `choices.consistent` recomputes every value derived from the stored column lengths, exactly as `dsr.evaluate` does: each entry's `length_ratio` must equal `max(L_j)/T`, and each entry's block `L` must equal `dsr.family_block(lengths, rule)` under its own rule. The test helper's "valid" record was itself the reviewer's counterexample (ratio 0.05 with lengths 3 at T = 9); it now stores 3/9. Test `test_derived_values_and_the_record_schema_are_checked` (wrong ratio; median block 4 with lengths 3, 3). |
| I1R4-2 Medium | AGREE, repaired | The exact record keys and entry keys the driver writes; `column_checks` pairs `[bool, bool]` for a finite column and `[False, None]` otherwise; `columns` pairs `[hex or null, bool]`; the `U_G` nominee null iff `u_g` is `NO_NOMINEE`, otherwise an integer in range K with `u_g` null or another string. Every malformed input returns a problem string: the body runs inside one `try` that turns `KeyError`, `TypeError`, `IndexError`, `ValueError`, `AttributeError` into "malformed record". Tests: same test (variance `None` on a finite column; missing `u_g`; an extra entry key; a lost nominee; five malformed records that must return a problem, not raise). |

**Boundary, now stated in the docstring.** `consistent` checks structure,
the Annex B order, cross-rule agreement, per-column agreement, and every
value recomputable from the stored lengths. It does not check z_f*, S0,
which trial is nominated, or the U_G outcome: those need the bootstrap or
the gates to recompute. They are bound by the chain hashes (§13 item 6)
and reproduce from the §8 seeds (Constitution §27). Further review should
judge the check against this stated scope rather than against "every
record the driver can write", which only recomputation could establish.

The real-data driver tests still pass: every real development record
(accepted and refused, both cells) passes the stricter check, and
`d19_choose` end to end.

No calibration was run.

## Checks after repair (2026-10-10, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_choices.py -q -p no:cacheprovider` | 0 | 18 passed |
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py -q -p no:cacheprovider -k "column_checks or development_run_needs or independent_section_2 or margin_failure"` | 0 | 5 passed |
| `.venv/Scripts/lint-imports.exe` (after `choices` imports `dsr`) | 0 | 6 contracts kept, 0 broken |
| `.venv/Scripts/python -m pytest` the five calibration files (`rundef`, `chunks`, `reduce`, `binomial`, `choices`) `-q -p no:cacheprovider` | 0 | 109 passed in 357.46 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those five files | 0 | 1801 passed, 9 skipped in 488.96 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 139 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_choose.py` | 0 | No issues in 67 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |
