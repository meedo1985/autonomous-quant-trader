# Task 29: repairs for Sol fourth re-review S29R4-1, S29R4-2

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`)
**Review:** `SOL_REVIEW_881CB9C.md` (`391fc5a`), verdict FIX. S29R3-1 resolved at all three saves.

Both findings are accepted and repaired as the reviewer proposed. None is left unrepaired.

| Finding | Repair |
|---|---|
| S29R4-1 (BLOCKER) | `leave_freeze` tries `exit_freeze()` first. On failure it logs the `FREEZE_EXIT` refusal, then the HALT-override refusal for that hour, as before `881cb9c`. On success it logs the HALT-override refusal after the exit transition and replay, and before `save(..., ended=hour)`. The shared helper is `refuse_halt_override`. Timestamps are unchanged (`busy_until`). An alert-write failure can no longer prevent the exit attempt. Test: `test_an_override_in_a_freeze_exit_hour_is_logged_after_the_exit` puts an override on every `FREEZE_EXIT` hour. Up to the passing exit, each exit's refusal or transition is followed by that hour's override refusal. The test fails at `881cb9c` and passes now. |
| S29R4-2 (MINOR) | `test_a_kill_after_a_waited_freeze_exit_names_only_the_skipped_hours`: the passed `FREEZE_EXIT`'s reconciliation is delayed two hours past its hour H, and the run is killed right after its save. `unfinished_hours` returns `[H+1, H+3)`, so H is not named. `test_a_freeze_exit_save_ends_its_hour` stays as a direct check of the saved field; `REPAIRS_0DDDDAE.md` wrongly called it a crash test. |

**Validation:**
- `ruff check .` and `ruff format --check .`: pass;
- `mypy src`: 53 files clean;
- `lint-imports`: 6 contracts kept;
- full `pytest`: **1786 passed, 9 skipped**.
