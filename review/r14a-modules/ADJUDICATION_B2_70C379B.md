# Adjudication of the Astra review of 6b build B2 (record `ASTRA_REVIEW_B2_70C379B.md`)

- Adjudicated and repaired by Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-15.
- Astra verdict: FIX (B2-A-1..4 major, B2-A-5..7 minor); readings B2-R-1..3, 5..7 AGREE,
  B2-R-4 CORRECT.

| ID | Decision | Repair |
|---|---|---|
| B2-A-1 major | Accepted | `family_ledger`: a result entry whose `cycle_id` is not this cycle but whose `attempt_id` is a start of this cycle (any family or partition) is a `CycleError`; only results bound to other cycles' starts are skipped. A result payload that is not a record is a `CycleError` |
| B2-A-2 major | Accepted | `family_attempts` makes one ledger pass: an outcome before its attempt's start is a `CycleError` ("before its start"), separate from "never started" |
| B2-A-3 major | Accepted | `family_attempts`: an `attempt_id` started twice anywhere in the ledger (identical or conflicting) is a `CycleError`; starts are never collapsed |
| B2-A-4 major | Accepted | `nominate`: day alignment is checked before the reason (rule 2 before rules 3-4); the values-length check applies only to available results |
| B2-A-5 minor | Accepted | the crash rewrite (`failed`, `CRASH_NO_ARTIFACT`, `end` = first outcome) applies whenever no result precedes the first outcome, also when a result follows (the breach is reported separately); `breach` marks only an attempt with two results before any outcome |
| B2-A-6 minor | Accepted | new test: a superseded U_proc result (breached attempt, then a later successful attempt) and a post-outcome U_proc result are both recorded with their exact attempt ids and entry hashes |
| B2-A-7 minor | Accepted | `ruff format` on the changed test files; `ruff format --check` now passes on the module and every `test_c2_confirmation_*.py` |
| B2-R-4 | Correction accepted | as B2-A-5; `BUILD_NOTES_SLICE6B_B2.md` B2-R-4 is superseded by this row |

Extra tests Astra named as missing, added: valid-but-wrong `protocol_hash`, `engine_commit`
and `confirmation_module_sha256`; a result bound to a foreign-cycle or exploration start;
every outcome word following a result; breach order opposite to start order.

Not repaired: none.

## Checks after repair

- New tests against the pre-repair module (stashed): 7 failed (B2-A-1, A-2, A-3 x3, A-4,
  A-5), 38 passed; with the repair: `pytest tests/unit/test_c2_confirmation_ledger.py`
  45 passed.
- `pytest tests/unit -k c2_confirmation`: 414 passed.
- `ruff check calibration tests/unit/`: clean; `ruff format --check` on the module and the
  confirmation test files: clean.
- `mypy calibration/c2_confirmation.py`: clean (the 10 errors in the imported
  `test_calibration_screen.py` are pre-existing, unchanged).
- `lint-imports`: 7 kept, 0 broken.
