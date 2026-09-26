# Task 17 independent adversarial review

Model: GPT-6 Astra.
Checks were not rerun by me. The supplied check output was produced by the implementer, Claude Opus 5.5. This review uses only the supplied diff and context.

## Findings

**A-1 — BLOCKER — `src/aqt/research/harness.py:174`; `review/task17/LOCAL_REPORT.md` (T17-04): exploration logging remains optional.**
A caller can execute 250 successful jobs through the existing public `run_exploration` API without creating any job entries. `review_status` then reports zero jobs and no review requirement. This bypass needs neither a new cycle nor a changed log path, so it is distinct from R-2. The import boundary explains the wrapper design but does not satisfy “all jobs logged.”
Repair: make logging mandatory at the supported exploration execution boundary while preserving the import contract.

**A-2 — BLOCKER — `src/aqt/research/joblog.py:173`: failed jobs can cross the threshold without reporting the trigger.**
Starting with 249 uncleared jobs, call `run_logged` with a loader that raises. The preliminary status is false and discarded; job 250 is appended; the exception skips the final status return. If subsequent jobs also fail, their preliminary true statuses are likewise discarded, and no call reports the review requirement. An explicit separate status query would discover it, but the advertised execution wrapper never delivers the trigger in this reachable workflow.
Repair: expose the due-review status on failure as well as success, while preserving the original failure.

**A-3 — NON-BLOCKING — `src/aqt/research/joblog.py:125`: R-1 can reject a legitimate concurrent clearance.**
Process A counts 249 jobs and pauses. Process B appends job 250, and a human reviews and commits clearance through 250. A resumes, reads that clearance, and raises because its earlier count was 249. The clearance covers existing jobs; the two observations describe different moments. At the final status call, this can also prevent a completed result from being returned.
Repair: refresh the verified count before rejecting a clearance that exceeds the initially observed count. Retain rejection when it still exceeds the refreshed count.

**A-4 — NON-BLOCKING — `tests/unit/test_joblog.py:216`: the concurrency test can pass without two processes writing.**
`Pool(2)` does not guarantee that its two tasks run on distinct workers. If one spawned worker starts slowly, the other can finish both batches. The test then passes with 30 valid entries even if cross-process serialization is broken. Fable’s reported overlap observations do not make this a guaranteed regression check.
Repair: use explicitly coordinated writer processes, assert distinct participating PIDs, and test lock contention.

## Repair and decision assessment

R-1 correctly rejects a future clearance against a stable log; A-3 identifies its concurrent exception. Refusing a rotated incomplete log is consistent with that guard.
R-3 correctly translates the supplied decoding and process-launch failures and rejects a pre-existing unreadable clearance before execution.

T17-01 and T17-06 present no additional concrete defect. T17-02 needs A-2 addressed; T17-04 needs A-1 addressed. T17-03/T17-05 and T17-Q2/Q3 retain the already disclosed R-2/R-4 limitations.
T17-Q1 does not replace section 16’s required human PR review for protocol-enforcement logic.

## Verdict

**FIX.** Address A-1 and A-2 before acceptance; repair A-3 and strengthen the concurrency evidence in A-4.