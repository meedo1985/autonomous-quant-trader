# Task 29: repairs for Sol §16 review S29-1..S29-6

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`)
**Review:** `SOL_REVIEW_37A9D1B.md` (`275e41b`), verdict FIX

Every finding is accepted, and none is left unrepaired.

| Finding | Repair |
|---|---|
| S29-1 (BLOCKER) | A step that saved state and then crashed cannot be re-run, because the loop refuses a start that is not after its last save (Task 27). Each completed, non-refused step now appends a cursor (`forward_cursor.jsonl`, hash-chained) recording the hour it completed through: the later of its `end` and the hour after its last save, because a run can be busy past `end`. If the journal shows a save beyond the cursor, a step was interrupted. The next step then emits one CRITICAL `LOOP_LAG` event naming those hours (`interrupted_from`, `resumed_at`) before it continues, so the hours are reported rather than skipped silently. Test: `test_a_step_interrupted_after_a_save_is_reported`. This covers a save at any point in the hour (startup, owner command, pre-send, FREEZE/HALT, `busy_until`), because detection compares only the journal's last save with the cursor. |
| S29-2 (MAJOR) | `run_step` now creates the alert router before any journal or cursor read. `LedgerError`, `StateError`, `OSError`, `ValueError` and `ForwardError` become a logged CRITICAL `REFUSE_START`, then `ForwardError`, and the script stops with exit code 2. A Telegram setup refusal is now emitted to the operations ledger as well, not only printed. Test: `test_a_damaged_journal_is_a_logged_refusal`. |
| S29-3 (MAJOR) | Already fixed in `d40e34d`: a refused step stops the loop with exit code 2, which systemd does not retry, while a failed fetch is retried at the next hour. The --once exit codes are 0, 1 (fetch failed) and 2 (refused). |
| S29-4 (MINOR) | Valuation now starts at the first midnight at or after the first snapshot, so an aligned first snapshot is counted. The hand-computed test gains that case. |
| S29-5 (MAJOR) | The wording is corrected to "no exchange credential". With `--telegram`, the module and script text now say that only the owner's Telegram token is read (D-8). |
| S29-6 (BLOCKER, environment) | The reviewer's sandbox had no writable temporary directory. The full suite was run here with the commands and results listed below, after the repairs. CI runs it again on the PR. |

**Validation after the repairs:** `ruff format --check .`, `ruff check .`,
`mypy src`, `lint-imports` and the full `pytest` suite. Results:
- ruff format and ruff check: pass;
- mypy: no issues in 53 source files;
- lint-imports: 6 contracts kept, 0 broken;
- pytest: **1766 passed, 9 skipped** (5 min 41 s).
