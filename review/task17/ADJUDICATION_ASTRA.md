# Task 17 Astra review adjudication

Review record: `REVIEW_ASTRA.md`, saved as returned. Reviewer: GPT-6 Astra
(`gpt-6-astra`, reasoning effort high, Codex CLI, read-only, session
`01a0de8d-2f82-7ca1-8c98-789dd25454d3`), run on 2026-09-26 at the owner's
request ("after fable let astra do the review"). Packet: the diff
`main...dd1fe6d`, recorded check output (not rerun), `ledger.py` excerpts,
`harness.py` lines 170-200, `protocol_v1.yaml` lines 60-72 and Constitution
sections 3, 4, 16 and 26. Verdict: **FIX**.

| ID | Severity | Decision | Evidence and action |
| --- | --- | --- | --- |
| A-1 | BLOCKER | Accepted | Confirmed by reading: `run_exploration` is public and never touches the log, so 250 jobs through it leave `job_count` at 0. This goes beyond T17-04, which only disclosed the gap. Repair: `run_exploration` takes a required keyword `log_job` callback, called before anything else, so every call must supply one; `run_logged` supplies the ledger writer. The harness still does not import the ledger (the Task 16 boundary test stands). A caller can still pass a do-nothing callback on purpose; that remains procedural and is disclosed. |
| A-2 | BLOCKER | Accepted | Reproduced: with 249 jobs, a job whose loader raises becomes job 250, and the exception carried no review status (`'RuntimeError' object has no attribute '__notes__'`). Repair: `run_logged` attaches the review status as a note on the original exception and re-raises it unchanged. |
| A-3 | NON-BLOCKING | Accepted | Reproduced: job 250 appended and cleared between the count and the clearance read raised `JobLogError ... beyond the 249 jobs`. Repair: read the clearance first, then count. Jobs only grow, so a clearance read earlier can never exceed a count taken later unless it really is beyond the log. |
| A-4 | NON-BLOCKING | Accepted | Correct: `Pool(2)` may run both batches in one worker. Repair: two explicit `spawn` processes that start writing together through a shared barrier, each with a distinct PID. |
