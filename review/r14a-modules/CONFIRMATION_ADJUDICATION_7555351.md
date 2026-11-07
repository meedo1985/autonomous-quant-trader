# Adjudication of the Sol re-check 2 of confirmation slices 1-3 at 7555351 (`SOL_CONFIRMATION_RECHECK2_7555351.md`)

Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-07. All three findings accepted and repaired.

| ID | Verdict | Repair |
|---|---|---|
| R14C3-S-1 | AGREE | A crash is now a trial's first attempt recorded with any non-completed outcome the ledger allows (`NOT_COMPLETED` = `failed`, `aborted`) plus the crash code; P18-1 keys the re-run to "ended without any result artifact" and the fixed crash code, not to the `failed` label. Test: `test_aborted_crash_takes_the_slot`. |
| R14C3-S-2 | AGREE | `trial_states` refuses to assign the slot ("re-run slot undetermined") while any trial's first attempt that started before the first recorded crash's outcome record has no outcome: it may be an earlier crash that was never recorded, and P18-1 gives the slot to the first such crash. Recovery must record that attempt's outcome first. An attempt started after the crash record does not block. Test: `test_slot_is_undetermined_while_an_earlier_attempt_has_no_outcome` (Sol's t1-unresolved/t2-crash example, with and without a re-run; a later start does not block). The ledger test was reordered so its running attempt starts after the crash record. [DESIGN] consequence: if trials run concurrently, a re-run waits until every attempt started before the crash record has an outcome; the strict "first crash" reading needs that. |
| R14C3-S-3 | AGREE | Test added: every trial on the same valid UTC datetimes shifted by one day fails A_f with `MISALIGNED_SERIES` (an agreement-only implementation would pass the earlier integer case). |

Mutation check (cycle tests rerun; every mutation caught): `aborted` not treated as a crash (1 failed); unresolved earlier attempt ignored (1); any unresolved attempt blocks, including one started after the crash record (2).

Validation: see the commit message for the exact commands and results.
