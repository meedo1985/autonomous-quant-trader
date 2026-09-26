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
