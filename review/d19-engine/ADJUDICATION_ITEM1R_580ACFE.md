# Adjudication of the GPT-6 Sol re-review of the item 1 repairs at 580acfe

Review: `review/d19-engine/SOL6_ITEM1_REREVIEW_580ACFE.md` (FIX for pilot use
of the choices report; I1R-1..I1R-5, made from an attached packet because
Codex's command runner failed in this environment). Adjudicated and repaired
by Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-10. Not yet re-reviewed.

| ID | Decision | Repair and evidence |
|---|---|---|
| I1R-1 Medium | AGREE, repaired | `choices.consistent` now checks every cause code in the Annex B order of `dsr.evaluate`: a rules 1-4 code (`BEFORE_CLASSIFIER`) is allowed whatever the classifier says; otherwise `UNSUPPORTED_LAW` iff the classifier refuses (a NaN diagnostic refuses through `classifier.within`); a rules 5-6 code (`AFTER_CLASSIFIER`) only after acceptance; any other code is refused; an available result must carry finite `z`, `s0` and `block` and the `U_G` nominee. Test `test_a_record_must_follow_from_its_thresholds_and_nominee` covers every pre- and post-classifier code both ways, a null and a NaN z, and an unknown code. |
| I1R-2 Medium | AGREE, repaired | At `K = 1` the two rule entries must be identical. Test `test_at_k_1_both_rules_must_be_one_result` (and that `K = 2` may differ). |
| I1R-3 Medium | AGREE, repaired | Each development record now holds `column_checks`: per column, Annex B rules 1-2 (all values finite; nonzero sample variance, computed as `dsr.evaluate` does), so §9's per-column failure rates cover failures before any `L_j` exists; rule 3 (`L_j` unavailable) and the cap are per column in `columns`. Family reason precedence is unchanged. End-to-end test asserts the field. |
| I1R-4 Medium | AGREE, repaired | The report carries `status` (`ok` or `margin_failed`) and `qualifies_before_coverage` is false on a margin failure; `d19_choose` prints `margin_failed: ...` to stderr and no `z_crit` line, and exits 3. Script-level test `test_a_margin_failure_exits_3_and_never_reads_as_a_choice` runs the real `main` on real chains with the margin forced. |
| I1R-5 Low | AGREE, repaired | A pilot report carries `measurement_only`, stating that its statuses, `z_crit` and final thresholds are not qualification decisions and pointing to the event counts. End-to-end test asserts it. |

Out of the reviewer's reach (it could not run commands): its I1-4 note that
the attachments lacked the manifest and `Cell` encoding. `cells_from_manifest`
admits only the five laws of `generator.LAWS`, which equal `AGNOSTIC_LAWS`
today; any new law fails closed at the `d19_choose` guard.

No calibration was run.

## Checks after repair (2026-10-10, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_choices.py -q -p no:cacheprovider` | 0 | 15 passed |
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py -q -p no:cacheprovider -k "margin_failure or development_run_needs or independent_section_2"` | 0 | 4 passed |
| `.venv/Scripts/python -m pytest` the five calibration files (`rundef`, `chunks`, `reduce`, `binomial`, `choices`) `-q -p no:cacheprovider` | 0 | 105 passed in 374.85 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those five files | 0 | 1801 passed, 9 skipped in 373.10 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 139 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_choose.py` | 0 | No issues in 67 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |
