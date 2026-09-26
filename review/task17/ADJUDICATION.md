# Task 17 review adjudication

Review record: `REVIEW.md`, saved as returned. Reviewer: Claude Fable 5.1
(`claude-fable-5-1`, reported by the reviewer), requested through the Claude
Code Agent tool on 2026-09-26; a different model from the implementer (Claude
Opus 5.5). Reviewed commit: `48f56b3`. Verdict: **FIX**, no blockers.

| ID | Severity | Decision | Evidence and action |
| --- | --- | --- | --- |
| R-1 | NON-BLOCKING | Accepted | Reproduced: 3 jobs and a committed `Cleared through job: 100000` gave no error (`DID NOT RAISE`). Repair: `review_status` raises `JobLogError` when the clearance is beyond the job count. |
| R-2 | NON-BLOCKING | Owner decision; disclosed | Correct: a caller choosing a fresh log path or a fresh cycle id resets the count. Fixing the log path is a design choice for the owner (open question T17-Q2). Until then it is disclosed next to T17-05. |
| R-3 | NON-BLOCKING | Accepted | Reproduced: a committed clearance containing byte `0xff` raised `UnicodeDecodeError`. Repair: decoding and a missing `git` raise `JobLogError`, and `run_logged` checks the status before logging or running, so an unreadable clearance stops the job before anything happens instead of discarding a finished run. |
| R-4 | QUESTION | Owner decision | Correct that `HEAD` is whatever commit is checked out, including an AI feature branch. Reading the clearance from `main` instead is a design choice for the owner (open question T17-Q3). |

The reviewer agreed with T17-01 to T17-06, adding that T17-05 should cover the
log path (R-2). The reviewer supports raising T17-Q1 (section 16); it remains
the owner's decision, and per `review/task16/ADJUDICATION_ASTRA.md` the AI will
ask for the owner's review as a condition of merge, not offer to skip it.
