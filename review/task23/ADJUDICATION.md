# Task 23 external-review adjudication

Date: 2026-09-28

This record adjudicates every finding and question from the completed Claude
Opus 5.5 review and every diagnostic preserved from the incomplete GPT-6 Astra
attempt. The Astra attempt ended at the usage limit and issued no verdict, so a
fresh exact-model review remains mandatory.

## Claude Opus 5.5

| ID | Severity | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- | --- |
| T23-C1 | BLOCKER | AGREE | The branch's committed L-03 adoption says automatic HALT. Removed the absent S-4 citation and mapped LOSS_STOP to HALT from RUNNING and HALT. The existing FLATTEN self-transition remains a separate owner question below. | Updated transition test covers RUNNING, HALT, and FREEZE. |
| T23-C2 | BLOCKER | AGREE | Every successful transition, including a protective self-transition, now advances `entered_at`. Recovery requires a reconciliation strictly later than that time. | New HALT and FREEZE regressions reject reconciliation older than a later incident. |
| T23-C3 | NON-BLOCKING | AGREE | Removed the whole-remainder exception. If no quantity fits both the 50% owner bound and venue minimums, no order is sent and mode becomes HALT with the remainder recorded. | The monotonic test now proves every reduction is at most 50% and expects the bounded remainder. |
| T23-C4 | NON-BLOCKING | PARTIAL | The current process already fails closed in memory. The recovery path after storage returns is now documented and tested: record an OWNER_HALT incident, reconcile, exit FREEZE to HALT, then override. Durable restart refusal after the incident write itself fails belongs to Task 24 startup orchestration and remains an explicit requirement there. | New incident-write recovery regression; restart durability remains pending Task 24. |
| T23-C5 | NON-BLOCKING | AGREE | If the override alert and recovery-incident write both fail, HALT remains safe. After both sinks recover, a fresh OWNER_HALT creates the required incident and the normal override succeeds. Preserving two exception objects was not added because it does not change safety or recovery. | New double-write-failure recovery regression. |
| T23-C6 | NON-BLOCKING | AGREE | Consecutive-step counting is owned by the Task 24 loop. Task 24 must alert after a bounded number of IOC zero fills. No Task 23 controller counter was added. | Obligation recorded in `LOCAL_REPORT.md`; no Task 23 runtime check applies. |
| T23-QA | QUESTION | AGREE | “After” is interpreted strictly. Reports with timestamps equal to or earlier than the latest protective transition are refused. | Both recovery paths now use `report.at <= entered_at`; focused tests pass. |
| T23-QB | QUESTION | OPEN — OWNER | While already in FLATTEN, INCIDENT or LOSS_STOP currently records the incident and continues bounded reduction. The committed material does not settle this behavior. The owner must accept T23-01 or choose HALT/FREEZE before merge. | No approval is inferred from AI review. |

## Incomplete GPT-6 Astra attempt

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| T23-A0-01 | AGREE | Same defect as T23-C3. Removed whole-remainder selling, so a step cannot exceed the approved fraction. | Per-step fraction assertion added. |
| T23-A0-02 | AGREE | Quantity is now capped by `filters.max_qty`. Because local filters are checked before submission, a later venue filter rejection signals divergent state and enters FREEZE instead of falsely declaring FLATTEN complete. | New 300 BTC max-quantity regression and unexpected-filter-rejection regression. |
| T23-A0-03 | AGREE | Same defect as T23-C2. Later incidents now invalidate earlier reconciliation. | HALT and FREEZE stale-report regressions added. |
| T23-A0-04 | PARTIAL | Same durability boundary as T23-C4. In-process recovery is repaired and tested; Task 24 must make audit-write failure durable across restart and refuse startup until recorded. | Recovery regression added; Task 24 obligation disclosed. |
| T23-A0-05 | AGREE | Same authority defect as T23-C1. L-03 is restored to adopted automatic HALT behavior. | Transition test updated. |

## Current blockers and review status

- Local implementation validation is pending its post-repair full gate.
- Exact GPT-6 Astra review is incomplete and must be rerun on the repaired
  snapshot. The incomplete diagnostic run is not approval.
- T23-QB/T23-01 requires the owner's protected behavioral decision.
- Section 16 human PR review remains required before merge.

No frozen artifact, live exchange account, credential, confirmation data, or
lockbox data was changed or accessed while applying these repairs.
