# Adjudication of the Astra review of 6b build B5a (record `ASTRA_REVIEW_B5A_53A4550.md`)

- Adjudicated and repaired by Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-15.
- Astra verdict: FIX (B5A-A-1 blocker, B5A-A-2 medium); readings B5A-R-1..5 AGREE,
  B5A-R-6 AGREE with a clarification.

| ID | Decision | Repair |
|---|---|---|
| B5A-A-1 blocker | Accepted | Root cause in the shared `of_cycle`: a result entry now belongs to the cycle when it names the cycle **or** one of the cycle's attempts (whatever `cycle_id` it claims), as `family_ledger` already refuses such an entry. This also covers `cycle_ledger`'s anchor rule (such a result before the anchor is refused). New test: a result naming our attempt under another cycle, slipped in before the look entry, stops the look; the look entry stays |
| B5A-A-2 medium | Accepted | The concurrency test now holds the first opener inside the locked section (blocked in the classifier step), proves the second cannot reach its ledger read (read counter stays 1, thread alive), then releases: one look, one refusal. Without the lock it fails 3 of 3 runs |
| B5A-R-6 note | Accepted | Build-note clarification: the re-read also validates the cycle structure (`cycle_ledger`) and that the appended entry is the cycle's one look |

Missing tests Astra named, added: late result after the look entry is not intervening;
an outcome of another cycle's attempt may intervene; exactly one clock read; per-family
bounds `(T, K_f)` from the verified report object; a second family's classifier refusal
writes nothing.

Not repaired: none.

## Found while repairing (B5b, recorded here and in the B5b/B5c notes)

The existing test `test_c2_confirmation_cpcv.py::test_no_code_path_reads_the_report`
forbade every reference to `cpcv_report`; B5b's `evaluate_families` computes the C-14
report to write it to the record, which the test's own comment allows ("slice 6 only
writes it to the record"). The test is narrowed to that intent (reading B5B-R-4): the only
allowed references are the producer call in `evaluate_families`, the
`FamilyEvaluation.cpcv` field and its one reader `evaluation_record`; any other reference
fails (checked by adding a reader in `evaluate_look`: the test fails).

## Checks after repair

- New B5a tests against the pre-repair module: 1 failed (B5A-A-1), 18 passed; the
  contention test fails without the look lock (3 of 3 runs).
- `pytest tests/unit -k c2_confirmation`: 581 passed.
- `ruff check calibration tests/unit/`: clean; `ruff format`: clean.
- `mypy` on the module and the B5 test files: clean apart from the 10 pre-existing errors
  in the imported `test_calibration_screen.py`.
- `lint-imports`: 7 kept, 0 broken.
