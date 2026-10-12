# Adjudication of the Fable 5.1 review of D-19 engine item 1 at 3a84b86

Review: `review/d19-engine/FABLE_ITEM1_REVIEW_3A84B86.md` (ACCEPT for pilot
use; I1-1..I1-8). Adjudicated and repaired by Claude Opus 5.5
(`claude-opus-5-5`) on 2026-10-10, on the owner's instruction to fix
I1-1..I1-6. The repairs are not yet re-reviewed.

| ID | Decision | Repair and evidence |
|---|---|---|
| I1-1 NON-BLOCKING | AGREE, repaired | `test_development_records_equal_an_independent_section_2_computation` now runs for both cells (`pilot-k2`, `pilot-k1`) and twice per cell: with the pooled thresholds widened by 1e6 (every replication accepted, so the bootstrap, S0 and z_f* are reached; asserts at least one non-null z, and at K = 2 that the two rules' blocks differ when both are available) and narrowed by 1e6 (every replication refused). Each stored rule record must equal an independent `dsr.evaluate` field for field. |
| I1-2 NON-BLOCKING | AGREE, repaired | Per rule the record now holds `block` (L), `s0` and the DSR `nominee` besides `reason`, `z` and `length_ratio`; per replication the `U_G` `nominee` and every column's `(L_j, capped)` (`columns`), from a new `FamilyResult.columns` field set on every return of `dsr.evaluate` after the block lengths are computed. §9's per-column cap and failure rates come from `columns`. `FamilyResult` gaining a field changes the reference-vector outputs (`dataclasses.asdict(result)`), which are measured on the server before the threshold run and are not pinned in the repository. |
| I1-3 NON-BLOCKING | AGREE, repaired | `scripts/d19_choose.py` recomputes the pooled development thresholds from the verified threshold chains and checks every development record with `choices.consistent`: the classifier refused iff the record says `UNSUPPORTED_LAW` (whenever rules 1-4 let it run), and an available DSR result nominated the `U_G` nominee. Any mismatch stops with exit 1. The report records every chain's final head (`chain_heads`, both namespaces) and `dev_thresholds_sha256`. Test `test_a_record_must_follow_from_its_thresholds_and_nominee`. |
| I1-4 NON-BLOCKING | AGREE, repaired | `d19_choose` refuses any cell whose law is not in the literal family-agnostic list (`AGNOSTIC_LAWS`, Q1-Q4), so adding Q5/QJ (or skew-t) fails closed until their tests are counted. `M` from the frozen manifest's enumerated tests comes with the manifest (engine item 3). |
| I1-5 NON-BLOCKING | AGREE, repaired | `dev_replication` takes `prereg` separately from `anchor` and passes `defn["prereg_sha256"]` as the family seed's `protocol_hash`. The held-out design must reuse the P18-7 `U_G` nominee rule (interpretation 2); noted for that item. |
| I1-6 NON-BLOCKING | AGREE, repaired (first proposed repair) | Every UCB-to-tau comparison `choose` makes (cap, DSR, `U_G` at 20k/40k, and the two counts around each qualifying cell's error limit) records its relative margin; the report carries `smallest_margin` and `margin_ok` (`MARGIN_MIN = 1e-6`, three orders above the measured ~2e-9 error). Below it, `d19_choose` writes the report and exits 3 (fail closed; the owner decides). Test `test_a_target_comparison_inside_the_margin_is_flagged`. The `lgamma` numerics are unchanged. |
| I1-7 QUESTION | AGREE, no code change | Yes: a pilot measures cost and rates only. With fewer than about 7,700 development replications every cell is `demoted_cap` and `z_crit` is null, so choice steps 2-3 are validated by the unit tests on synthetic records. The pilot report will say so, and the per-cell counts (dsr, `U_G`, capped) are already in the report's `cells`. |
| I1-8 QUESTION / owner proposal | Carried to the owner, no code change | The re-pilot times the two block-rule evaluations separately. If the second rule's cost is material, the owner may decide the prefix proposal (choose the rule on the first ~2,000 development replications per cell), which changes the accepted preregistration. |

No calibration was run.

## Checks after repair (2026-10-10, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_choices.py -q -p no:cacheprovider` | 0 | 14 passed |
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py -q -p no:cacheprovider -k "independent_section_2 or development_run_needs"` | 0 | 3 passed |
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py tests/unit/test_calibration_chunks.py tests/unit/test_calibration_reduce.py tests/unit/test_calibration_binomial.py tests/unit/test_calibration_choices.py -q -p no:cacheprovider` | 0 | 103 passed in 569.93 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those five files | 0 | 1801 passed, 9 skipped in 560.78 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 139 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_choose.py` | 0 | No issues in 67 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |
