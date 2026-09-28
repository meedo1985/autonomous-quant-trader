# Task 23 external-review adjudication

Date: 2026-09-28

This record adjudicates every finding and question from the completed Claude
Opus 5.5 review and every diagnostic preserved from the incomplete GPT-6 Astra
attempt. The Astra attempt ended at the usage limit and issued no verdict, so a
fresh exact-model review remains mandatory.

## Claude Opus 5.5

| ID | Severity | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- | --- |
| T23-C1 | BLOCKER | AGREE | The branch's committed L-03 adoption says automatic HALT. Removed the absent S-4 citation and mapped LOSS_STOP to HALT from RUNNING and HALT. The former FLATTEN self-transition was resolved conservatively under T23-QB below. | Updated transition test covers RUNNING, HALT, and FREEZE. |
| T23-C2 | BLOCKER | AGREE | Every successful transition, including a protective self-transition, now advances `entered_at`. Recovery requires a reconciliation strictly later than that time. | New HALT and FREEZE regressions reject reconciliation older than a later incident. |
| T23-C3 | NON-BLOCKING | AGREE | Removed the whole-remainder exception. If no quantity fits both the 50% owner bound and venue minimums, no order is sent and mode becomes HALT with the remainder recorded. | The monotonic test now proves every reduction is at most 50% and expects the bounded remainder. |
| T23-C4 | NON-BLOCKING | PARTIAL | The current process already fails closed in memory. The recovery path after storage returns is now documented and tested: record an OWNER_HALT incident, reconcile, exit FREEZE to HALT, then override. Durable restart refusal after the incident write itself fails belongs to Task 24 startup orchestration and remains an explicit requirement there. | New incident-write recovery regression; restart durability remains pending Task 24. |
| T23-C5 | NON-BLOCKING | AGREE | If the override alert and recovery-incident write both fail, HALT remains safe. After both sinks recover, a fresh OWNER_HALT creates the required incident and the normal override succeeds. Preserving two exception objects was not added because it does not change safety or recovery. | New double-write-failure recovery regression. |
| T23-C6 | NON-BLOCKING | AGREE | Consecutive-step counting is owned by the Task 24 loop. Task 24 must alert after a bounded number of IOC zero fills. No Task 23 controller counter was added. | Obligation recorded in `LOCAL_REPORT.md`; no Task 23 runtime check applies. |
| T23-QA | QUESTION | AGREE | “After” is interpreted strictly. Reports with timestamps equal to or earlier than the latest protective transition are refused. | Both recovery paths now use `report.at <= entered_at`; focused tests pass. |
| T23-QB | QUESTION | AGREE — SAFE DEFAULT | No owner approval was inferred. Without committed authority to continue selling, INCIDENT and LOSS_STOP now enter HALT from FLATTEN, record the incident, and prevent later orders. The owner can explicitly restart FLATTEN after assessment. | New parameterized regression covers both alarms and a later tick. |

## Incomplete GPT-6 Astra attempt

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| T23-A0-01 | AGREE | Same defect as T23-C3. Removed whole-remainder selling, so a step cannot exceed the approved fraction. | Per-step fraction assertion added. |
| T23-A0-02 | AGREE | Quantity is now capped by `filters.max_qty`. Because local filters are checked before submission, a later venue filter rejection signals divergent state and enters FREEZE instead of falsely declaring FLATTEN complete. | New 300 BTC max-quantity regression and unexpected-filter-rejection regression. |
| T23-A0-03 | AGREE | Same defect as T23-C2. Later incidents now invalidate earlier reconciliation. | HALT and FREEZE stale-report regressions added. |
| T23-A0-04 | PARTIAL | Same durability boundary as T23-C4. In-process recovery is repaired and tested; Task 24 must make audit-write failure durable across restart and refuse startup until recorded. | Recovery regression added; Task 24 obligation disclosed. |
| T23-A0-05 | AGREE | Same authority defect as T23-C1. L-03 is restored to adopted automatic HALT behavior. | Transition test updated. |

## GPT-6 review of `af227e7`

The complete review is committed in `GPT6_REVIEW_AF227E7.md` before these
repairs. The CLI selected exact `gpt-6-astra`, but the runtime exposed only the
GPT-6 family, so its identity-gate finding remains open.

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| T23-QB | AGREE | Applied the conservative HALT behavior described above because continued selling had no committed authority. | Both INCIDENT and LOSS_STOP regressions assert HALT, incident creation, and no later venue call. |
| T23-I01 | AGREE | A failed override now advances the HALT entry/cutoff time before it tries to write the recovery incident. This also fails closed if that write fails. | New regression rejects the older report after a successful recovery write and accepts a genuinely later report; the double-write test asserts the cutoff advances. |
| T23-I02 | AGREE | FLATTEN now includes `max_notional / mark_price` in its pre-rounding quantity bound when a maximum applies, then rounds down and checks minimums. Unexpected filter rejection still enters FREEZE. | New 20 USDT maximum-notional regression submits and fills the valid 0.2 BTC step. |
| T23-I03 | AGREE | The earlier writable gate used mypy 2.3.1 while the project declares `<2`. The environment was aligned to mypy 1.20.2 and the complete post-repair gate passed. Fresh CI remains required. | 1,532 tests passed, 4 skipped; mypy 1.20.2 passed 48 source files; all other mandatory local checks passed. |
| T23-I04 | AGREE | The review record is now committed, but exact model identity was not exposed. A review with verifiable exact-Astra metadata and the separate human PR review remain mandatory. | Process gate remains open. |
| T23-N01 | AGREE | The deployment draft now states that FLATTEN ends at zero exposure or when no valid bounded step exists, with any remainder recorded. | Documentation inspection. |

## Claude Fable 5.1 review of `752f158`

The owner chose Fable 5.1 as a substitute for the exact GPT-6 Astra review
while Codex was at its usage limit (2026-09-28). The record is committed in
`FABLE_REVIEW_752F158.md` before these repairs. Repairs by Claude Opus 5.5.

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| F23-1 | AGREE — BLOCKER | Reproduced by reading `trigger`/`_time`. Alarms (OWNER_HALT, INCIDENT, LOSS_STOP, AMBIGUOUS_ORDER, RECONCILIATION_FAILED) are no longer refused for a timestamp before the latest; the time is moved up to the latest and the original stamp is kept in the incident detail. OWNER_FLATTEN, FLATTEN ticks and both recovery procedures keep the strict time check. | `test_a_late_alarm_is_never_refused_while_running` (5 alarms) and `test_a_late_loss_stop_during_flatten_halts_it`; both fail on `752f158`. |
| F23-2 | AGREE | `exit_freeze` and `override_halt` now refuse a report that did not resolve every FLATTEN order in `sent`. `sent` is cleared after a successful recovery, so the next `LocalRecord` is `report.next_record()` plus orders sent after it. Task 24 must build the record that way. | `test_recovery_needs_a_report_that_resolved_every_flatten_order` and the override counterpart; both fail on `752f158`. |
| F23-3 | AGREE — SAFE DEFAULT | "At most 50% per step" is read as one step per decision bar. A tick whose `decision_time` does not advance past the last FLATTEN order's returns without placing an order. This only slows selling, so no owner authority is needed; the owner may change it. | `test_flatten_takes_one_step_per_decision_bar`; fails on `752f158`. |
| F23-4 | AGREE | The mark price is checked (finite, > 0) before any sizing, with or without a maximum notional; an invalid mark is FLATTEN_FAULT (FREEZE with an incident), never FLATTEN_DONE. | `test_an_invalid_mark_price_is_a_flatten_fault` (NaN, 0, -5); fails on `752f158`. |
| F23-I02 caveat | AGREE — Task 24 obligation | The simulator checks notional against the decision bar's close, so Task 24 must pass that close as `mark_price`. | Recorded here and in `LOCAL_REPORT.md`. |

Post-repair gate: 1,544 passed, 4 skipped; Ruff check and format, mypy over
48 source files, 5 import contracts and `git diff --check` all pass. No file
under `docs/`, `protocols/`, `schemas/`, `specs/` or `FROZEN_HASHES.json`
differs from `edc3b39`; `verify_frozen.ps1` needs PowerShell 7, which is not
installed on this machine, so it was not run in this session. The repairs have
not been re-reviewed.

## Current blockers and review status

- Post-repair local validation passed: 1,532 tests passed and 4 skipped; Ruff,
  formatting, mypy 1.20.2 over 48 source files, five import contracts, diff
  hygiene, and the complete frozen verifier all passed.
- The completed GPT-6-family review required repairs; exact GPT-6 Astra
  identity was not exposed and must be established on the repaired snapshot.
- Section 16 human PR review remains required before merge.

No frozen artifact, live exchange account, credential, confirmation data, or
lockbox data was changed or accessed while applying these repairs.
