# Task 16 review adjudication

Review record: `REVIEW.md`, saved as returned. Reviewer: Claude Fable 5.1
(`claude-fable-5-1`, reported by the reviewer), requested through the Claude
Code Agent tool on 2026-09-26; a different model from the implementer (Claude
Opus 5.5). Reviewed commit: `b9e7580`. Verdict: **FIX**.

| ID | Severity | Decision | Evidence and action |
| --- | --- | --- | --- |
| R-1 | BLOCKER | Accepted | Reproduced before repair: a new test builds self-consistent manifests labelled `exploration` whose windows lie in 2023 (confirmation dates), run past 2022-01-01, or start before 2017-08-17, with a loader returning the matching bars. On `b9e7580` all three cases ran (`DID NOT RAISE`). Repair: refuse any manifest whose window leaves `[aqt.data.klines.WINDOW_START, WINDOW_END_EXCLUSIVE)` before the loader is called. |

Deviations T16-01 to T16-04: the reviewer agreed with all four. No change.

T16-Q1 (whether the harness is section 16 "protocol-enforcement logic"): the
reviewer supports the cautious reading (protected). This remains the owner's
decision; the AI records the reviewer's view and does not decide it.

Implementer error recorded: the first draft of the R-1 test was set up wrongly
(one window too short for its bars, and a loader returning unrelated bars), so
it failed for the wrong reason. It was corrected to the reviewer's exact
scenario before being used as the reproduction.

## Repair

`run_exploration` now refuses, before the loader is called, any manifest whose
declared window leaves `[2017-08-17T00:00:00Z, 2022-01-01T00:00:00Z)`
(`aqt.data.klines.WINDOW_START` / `WINDOW_END_EXCLUSIVE`, which match
`protocols/protocol_v1.yaml` line 65). Together with `verify_partition_manifest`,
which confines the loaded bars to the manifest window, no out-of-window bar
reaches the backtest. The module docstring now states this.

Test: `test_a_window_outside_the_exploration_partition_is_refused` (3 cases:
confirmation-dated, past the end, before the start), each asserting the loader
is never called. Mutation check: all 3 fail on `b9e7580` (`DID NOT RAISE`) and
pass after the repair.

Validation after repair, `.venv` Python 3.14.7: `pytest -q` 1370 passed, 4
skipped in 134.46s; `ruff check .` and `ruff format --check .` pass; `mypy src
scripts` no issues in 41 files; `lint-imports` 5 kept, 0 broken; no change under
the frozen paths.

This repair has not been re-reviewed by a different model.

