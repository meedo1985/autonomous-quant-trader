# Task 29: repair for Sol second re-review S29R2-1

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`)
**Review:** `SOL_REVIEW_DA27588.md` (`fbffd0b`), verdict FIX

The finding is accepted and repaired as the reviewer proposed. No finding is left unrepaired.

| Finding | Repair |
|---|---|
| S29R2-1 (BLOCKER) | Progress is now stored in the same journal record that advances the restart time. `AccountState` gains `unfinished_from`: the first decision hour the run had not finished when the snapshot was saved. For a save made within an hour it is that hour (owner command, pre-send, FREEZE/HALT reconciliation). For a save at an hour's end it is the next hour (startup, each hour's save, the final save). The loop sets it at the two points where an hour begins and ends. The field is omitted when `None`, so snapshots written before it still parse exactly; such a snapshot counts from the interrupted step's start, else from the hour of its save. `unfinished_hours(journal)` returns `[unfinished_from, resume)`: exactly the hours the next run will not run. After an interruption (a `START` with no `END`) these hours are reported as a CRITICAL `LOOP_LAG` before anything else. When the range is empty the step had finished every hour, and nothing is reported; this removes the final-save/pre-`END` false alarm. After a step that ran, the same range gives the hours a reconciliation still running at its end made the loop skip, reported as a WARNING. The step-level claim of "only the hour of the last save" is withdrawn. |

**Crash tests.** These run at real save sites, by killing the run right after its *n*-th journal save. The scenario is the reviewer's: hour 0's order is reconciled two hours later (A2324R-4).

`test_a_kill_after_any_save_names_exactly_the_hours_not_run`:

| Killed after | Hours reported |
|---|---|
| Startup save | 0 |
| Pre-send save | 0 |
| The 02:00 save ending hour 0 (the reviewer's case) | 1–2 |
| Busy-skip save of hour 1 | 2 |
| Busy-skip save of hour 2 | none |
| Final save (run not killed) | none |

The other new or reworked tests:
- `test_an_interrupted_step_is_reported_with_its_hours`: the report is the first event of the next step, and is given once.
- `test_a_kill_after_the_final_save_reports_nothing`.
- `test_an_interrupted_pre_send_is_reported_before_its_refusal`: a real pre-send kill.
- `test_hours_a_running_reconciliation_skips_are_reported`: a real run ending at hour 1 whose reconciliation runs to 02:00. Hours 1–2 are reported as a WARNING.
- `test_a_snapshot_round_trips_exactly`: with and without the new field.

**Scope note.** `paper_loop.py` and `state.py` are protected (§16). The change adds one saved field and two assignments; replay behaviour is unchanged, and the full suite passes.

**Validation:** `ruff check .`, `ruff format --check .`, `mypy src`, `lint-imports` and the full `pytest` suite. Results:
- ruff: pass;
- mypy: no issues in 53 source files;
- lint-imports: 6 contracts kept;
- pytest: **1780 passed, 9 skipped** before the round-trip parametrization, which adds 1 more; the unit file passes, 24 tests.
