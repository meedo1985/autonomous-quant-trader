# Adjudication of the Astra review of 6b build B3 (record `ASTRA_REVIEW_B3_E514FFC.md`)

- Adjudicated and repaired by Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-15.
- Astra verdict: FIX (B3-A-1 major, B3-A-2 and B3-A-3 minor); readings B3-R-1..3, 5, 6, 8,
  9 AGREE, B3-R-4 and B3-R-7 CORRECT.

| ID | Decision | Repair |
|---|---|---|
| B3-A-1 major | Accepted | `cycle_ledger` checks every look, closing and termination entry's exact form (`_control_ok`, including a non-empty string `cycle_id`) **before** the cycle filter, whatever cycle it names; a malformed one is a `CycleError`. Well-formed entries of other cycles are still ignored. New test: the 12 cases (missing, `None`, `""`, list `cycle_id` x look, closing, termination) |
| B3-A-2 minor | Accepted | the look entry's `now` must be the strict `YYYY-MM-DDTHH:MM:SSZ` form (`_strict_time`), `ledger_head_before` and `confirmation_module_sha256` 64 lower-case hex, `families` non-empty strings; the closing entry's two record hashes 64 lower-case hex. New tests: `not-a-time`, an unpadded time, `not-a-hash`, upper-case hex, a closing hash `bad` |
| B3-A-3 minor | Accepted | the outcome-before-anchor test now writes (with `append_entry`) an outcome at position 0 and its start after the anchor, so only the outcome's attribution can trigger the refusal; the same ledger passes when the declaration names another cycle |
| B3-R-4 | Correction accepted | as B3-A-1; the B2 split for result entries is kept |
| B3-R-7 | Correction accepted | `check_read` refuses served partitions of one symbol whose manifest windows overlap (`a.end > b.start` after sorting by start), also outside the cut. New test |
| B3-R-2 note | Noted, no change | the reader does not enforce the declared membership or order of `families`; the module is the only writer (`look_entry`), and B5's look writes it from the declaration |

Extra tests Astra named as missing, added: closing entry before the anchor; protocol-hash
mismatch in another family and in the exploration partition; naive and `+01:00` clocks;
day 180 minus one second; a truncated whole partition; changed bars before the cut;
reversed served-insertion order; a lock holder process killed while a waiter blocks (the
waiter then gets the lock). Not added: a "prolonged contention" test; the wait has no
deadline by construction (no timeout in `look_lock`), and a longer sleep would only slow
the suite.

Not repaired: none.

Astra's sandbox could not run the ledger tests (no writable temporary directory); they
were run here.

## Checks after repair

- New tests against the pre-repair module (stashed): 18 failed (B3-A-1 x12, B3-A-2 x5,
  B3-R-7 x1), 42 passed. With the repair: `test_c2_confirmation_look.py` 46 passed,
  `test_c2_confirmation_read.py` 14 passed.
- `pytest tests/unit -k c2_confirmation`: 474 passed.
- `ruff check calibration tests/unit/`: clean; `ruff format --check` on the module and the
  confirmation test files: clean.
- `mypy calibration/c2_confirmation.py` and the two new test files: clean (the 10 errors in
  the imported `test_calibration_screen.py` are pre-existing, unchanged).
- `lint-imports`: 7 kept, 0 broken.
