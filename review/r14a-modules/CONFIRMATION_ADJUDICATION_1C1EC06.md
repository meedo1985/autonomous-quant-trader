# Adjudication of the Sol re-check of confirmation slices 1-3 at 1c1ec06 (`SOL_CONFIRMATION_RECHECK_1C1EC06.md`)

Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-07. All four findings accepted and repaired.

| ID | Verdict | Repair |
|---|---|---|
| R14C2-S-1 | AGREE | `family_attempts` now walks the ledger itself and returns each attempt's ledger positions, `start` (start record) and `end` (outcome record, None while absent). `trial_states` gives the family's one re-run slot to the crash whose outcome was recorded first (P18-1 "only the first such crash in the family"), not the attempt that started first, and a second attempt is permitted only for that trial and only if it started after the crash was recorded. Tests: `test_slot_follows_the_order_crashes_were_recorded` (Sol's t1-starts/t2-crashes-first example; re-run for the wrong trial refused; re-run started before the crash record refused); the ledger test now interleaves starts and outcomes and checks the positions. |
| R14C2-S-2 | AGREE | A crash is a trial's first attempt recorded `failed` (`attempts.OUTCOME_FAILED`) with the crash code and an outcome record; the crash code on a `completed` outcome reserves nothing, so a second attempt (and so a second completion) is refused. Test case added to `test_attempt_sequences_outside_p18_1_are_refused`. |
| R14C2-S-3 | AGREE | `nominate` takes `window = (w0, T)` from `check_eligibility`; every trial's day index must equal exactly `[w0 + i days for i in range(T)]`, with one value per day (Annex B §2.1: one row per complete UTC day of the eligible window); otherwise A_f fails with `MISALIGNED_SERIES`, cause U_ops. This subsumes the earlier increasing/identical checks. Tests: identical-but-wrong index (`1..400`) and a one-day-short series now fail. |
| R14C2-S-4 | AGREE | `nominee_outcome` refuses any gate result outside PASS / FAIL / N/A / UNAVAILABLE (Annex C C-0). Test: `Gate("BOGUS")` refused. |

Mutation check (each repair broken on purpose, cycle tests rerun; every mutation caught, 1 failed each): slot chosen by start order; re-run allowed before the crash record; crash code accepted on a success; window days unchecked; result outside the four outcomes allowed.

Validation: see the commit message for the exact commands and results.
