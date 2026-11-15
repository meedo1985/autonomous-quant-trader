# Adjudication of the Astra review of 6b build B5b/B5c (record `ASTRA_REVIEW_B5BC_8F05D2F.md`)

- Adjudicated and repaired by Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-15.
- Astra verdict: FIX (B5BC-A-1 high, B5BC-A-2 and B5BC-A-3 medium). Readings B5B-R-1..3,
  B5C-R-2..6 AGREE; B5B-R-4 and B5C-R-1 PARTIAL (resolved by A-3 and A-1/A-2); B5B-D-1
  PARTIAL: the hash reading is supported, cause classification per A-1; the owner accepted
  B5B-D-1 in `73bbc5f` (after this review run started).

| ID | Decision | Repair |
|---|---|---|
| B5BC-A-1 high | Accepted | Each gate in the record carries `cause` (`cause_code`: U_ops if its reason is in `U_OPS_REASONS`, else U_proc, None when not UNAVAILABLE). The family's `cause` is the nomination's when A_f fails, otherwise `gate_cause(gates)`: U_ops if any UNAVAILABLE gate is U_ops (infrastructure first, P18-7), else U_proc, None when no gate is UNAVAILABLE. Tests: procedure only, infrastructure only, mixed, none |
| B5BC-A-1 (`BENCHMARK_SPEC_MISSING`) | Not changed; owner item | `U_OPS_REASONS` is the owner-bound list (B-5, A-7); `BENCHMARK_SPEC_MISSING` is not in it, so G-13 missing its specification counts U_proc. A missing engine file reads as infrastructure (U_ops). Proposed to the owner as **B5BC-O-1**: add `BENCHMARK_SPEC_MISSING` to `U_OPS_REASONS`. Left unchanged until decided |
| B5BC-A-2 medium | Accepted | The family record now carries `breaches` (every breach: attempt, kind, position, in ledger order) and `attempts` (the §3-rewritten attempt history), from the look's `FamilyLedger`. §10's field list is extended with these two fields to satisfy §3 rule 1 ("all breaches are listed in the record", full attempt history kept). Test: two breached attempts, both recorded |
| B5BC-A-3 medium | Accepted | `test_no_code_path_reads_the_report` now checks every use of `cpcv_report`, `c14` and `cpcv` against statement-level patterns: the producer assignment `c14 = cpcv_report(...)` in `evaluate_families`, `c14` as a `FamilyEvaluation(...)` argument, the dataclass field, and in `evaluation_record` only `ev.cpcv is None` and `_plain(ev.cpcv)`; any other use, in any file, fails. New test with Astra's counterexample (a gate decided from `c14`), a second reader in `evaluate_look`, and a reference in another module: each is caught |

Extra tests Astra named, added: different warm-ups for the two nominees (one read, two
cuts); a nominee or reason change in `differs`; a failure in sealing after the evaluation
record is serialised (nothing persisted, no closing entry).

`of_cycle`: Astra found no regression.

Not repaired: B5BC-O-1 (owner decision, above).

## Checks after repair

- New tests against the pre-repair module: 6 failed (A-1 x4 incl. the gate-cause fields,
  A-2 x1, record field set x1), 38 passed; the old C-14 test passed Astra's counterexample
  (Astra's reproduction), the new one fails it.
- `pytest tests/unit -k c2_confirmation`: 592 passed.
- `ruff check calibration tests/unit/`: clean; `ruff format --check`: clean.
- `mypy` on the module and the changed test files: clean apart from the 10 pre-existing
  errors in the imported `test_calibration_screen.py`.
- `lint-imports`: 7 kept, 0 broken.
