# Task 29: repair for Sol third re-review S29R3-1

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`)
**Review:** `SOL_REVIEW_0DDDDAE.md` (`98e0910`), verdict FIX

The finding is accepted and repaired as the reviewer proposed. No finding is left unrepaired.

| Finding | Repair |
|---|---|
| S29R3-1 (BLOCKER: a false alarm at the FREEZE/HALT saves) | `save(..., ended=hour)` records `unfinished_from = hour + 1h`. It is used at the three saves that end their command hour: a passed `FREEZE_EXIT` (`leave_freeze`), a failed HALT-override reconciliation, and an accepted HALT override (`end_halt`). Work done after those saves now happens before them, as the reviewer asked. First, the HALT override refused because `FREEZE_EXIT` ran in the same hour is now logged inside `leave_freeze`, before its save. It keeps the same timestamp (`busy_until`). Second, the hour's loss-stop firing (`fire(valuation, busy_until)`) after a failed or refused override now runs inside `end_halt`, before the save. Its condition and timestamp are unchanged: it runs whenever the mode is not RUNNING afterwards. The caller now only ends the hour. Replay behaviour is unchanged: all 95 paper-loop, restart, recovery and forward tests pass unmodified. |

**Crash tests.** Each one fails on the code before this repair and passes after it:
- `test_a_kill_after_an_override_save_names_only_the_skipped_hours[passed, failed]`: the override's reconciliation at hour 1 is delayed to 03:00, and the run is killed right after its save. Hours 2–3 are named; hour 1 is not.
- `test_a_freeze_exit_save_ends_its_hour`: the save of the passed `FREEZE_EXIT` records the next hour as unfinished.

**Validation:**
- `ruff check .` and `ruff format --check .`: pass;
- `mypy src`: no issues in 53 source files;
- `lint-imports`: 6 contracts kept;
- full `pytest`: **1784 passed, 9 skipped**.
