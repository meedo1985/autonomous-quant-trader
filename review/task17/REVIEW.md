# Task 17 independent adversarial review

Reviewer: Claude Fable 5.1 (`claude-fable-5-1`), requested via the Claude Code Agent tool; implementer was Claude Opus 5.5. The review was read-only. I read `git diff main...task17-exploration-joblog` (48f56b3), `ledger.py`, `harness.py` and roadmap Task 17. In a detached scratch worktree, since removed, I ran `pytest tests/unit/test_joblog.py` (10 passed, 18.4 s) and probe scripts on synthetic temp repos and logs only. I did not run the full suite, ruff, mypy or lint-imports, and I did not touch `data/`.

## Findings

**R-1 NON-BLOCKING: a clearance above the job count pre-clears future jobs.** `src/aqt/research/joblog.py:93,120`. `cleared` is never checked against `count`, so `count - cleared` can go negative.
Observed: with 250 jobs and a committed `Cleared through job: 100000`, adding 500 more jobs gave `job_count=750, cleared_through=100000, review_required=False`. A typo such as 2500 for 250 would skip the next nine reviews without any warning. The same thing happens without a typo if a cycle continues in a new or rotated log file after a clearance. The count restarts at 0 while the clearance stays at 250, so the first review in the new file comes at 500 jobs, not 250.
Repair: raise `JobLogError` when `cleared_through > job_count`, because a clearance cannot cover jobs that do not exist yet. Add a test.

**R-2 NON-BLOCKING: two caller choices can keep the trigger from ever firing.** `joblog.py:96-105,143-150`. The count is taken per (`log_path`, `cycle_id`), and the caller picks both freely.
Observed: `review_status(<fresh path>, "cycle-1", repo)` returned `job_count=0`. A script that writes a separate log per experiment directory (a common layout), or uses a new cycle id for each batch, logs every job but never reaches 250. T17-05 covers the cycle id but not the log path.
Repair: give the log a fixed repository path, or require the path in a way that makes per-run logs impossible. If the owner decides otherwise, state that limit next to T17-05.

**R-3 NON-BLOCKING: a clearance file that is not UTF-8 crashes after the job has run.** `joblog.py:92` and `:167`.
Observed: a committed file containing the byte `\xff` raises `UnicodeDecodeError`, not the `JobLogError` that the docstring at `:59` promises. This is a realistic case: a note saved as ANSI/cp1256 Arabic text would trigger it.
- **Fails closed:** the flag is not cleared.
- **Discards the run:** `run_logged` raises only after the job has run and both entries are logged, so the returned result is lost.
- **Keeps failing:** every later `run_logged` fails the same way until the file is fixed.

The same applies to git not being installed (`FileNotFoundError`).
Repair: decode inside a `try` and raise `JobLogError`. Consider computing the status before returning, so that an unreadable clearance does not discard a completed run.

**R-4 QUESTION: "committed" is a weaker guard than it sounds.** `joblog.py:86`. `HEAD` means the checked-out commit of any repo the caller passes in, on any local branch. The coding AI commits to feature branches as a matter of routine (48f56b3 is one), so "committed in HEAD" guards against the AI hardly better than "exists on disk". Reading from the `main` ref would tie clearance to the merged, PR-reviewed record. This remains procedural (T17-03), and the owner should choose.

## Checked and not a defect
- **Error handling:** if `repo_root` is not a repository, has no HEAD, or `git show` fails, the result is "nothing cleared", which is fail-safe.
- **Subdirectory as `repo_root`:** resolves to the same tree path and works correctly.
- **Line endings and formatting:** CRLF clears as expected. A UTF-8 BOM on the first line means the file does not clear, which is fail-safe. Arabic-Indic digits parse to the same integer. Where several lines match, the highest number wins; a clearance cannot be lowered, which is acceptable.
- **Cycle ids:** `"cycle\n"` is rejected. A job entry without `cycle_id` can only come from calling `append_entry` directly, and it raises `KeyError` loudly.
- **Refused partitions:** a manifest for a refused partition (confirmation) is logged and counted before the `HarnessError` is raised. This is conservative, and the partition is recorded in the payload.
- **Concurrency:** the flag is a level computed after the append, so concurrent writers cannot skip job 250.
- **Tests:** none pass vacuously. The mutation test fails if the replacement misses; the 250-job test asserts the exact counts. In the concurrency test, the two spawned writers overlapped in 8 of 8 timed runs.

## Choices T17-01..T06 and question T17-Q1
- **T17-01, agree:** recurring review every 250 jobs is the more conservative reading. It only works if R-1 is repaired.
- **T17-02, agree:** the protocol says "triggered", not "halted". The owner may still choose to block.
- **T17-03, agree:** "human" can only be procedural. See R-4.
- **T17-04, agree:** the Task 16 import boundary forbids anything else. The gap should be recorded where the owner will see it.
- **T17-05, agree, but incomplete:** it should also cover the log path (R-2).
- **T17-06, agree:** the sampled counts include the 249/250 boundary, and each count is checked exactly.
- **T17-Q1, agree:** it should be raised. This enforces a protocol rule, which is arguably "protocol-enforcement logic" under section 16. That is the owner's decision, not the AI's.

## Verdict
FIX. There are no blockers. Repair R-1 and R-3, both small, before merge. The owner should decide R-2 and R-4.
