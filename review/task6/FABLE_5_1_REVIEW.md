# Task 6 — Claude Fable 5.1 independent review

Date: 2026-09-13

**Verdict at review time: PASS, with no blocking defect.**

This verdict was later superseded by Sol High's discovery that out-of-range
targets were rejected instead of clipped. The defect was corrected and sent
for a fresh different-model review; this record is retained as an honest
account of what Fable did and did not catch.

Claude Fable 5.1 reviewed the Task 6 oracle and leakage-canary suite in
read-only mode. It confirmed the corrected exact Spearman calculation, the
synthetic shuffled-label null symmetry, the frozen cost-model transcription,
the timing rules, the 49 focused tests, and the absence of changes to frozen
governance files.

## Findings and disposition

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| T6-N1 | Non-blocking | The private-kernel module docstring claimed every acceptance identity supported both aggregators, while the shuffled-label PnL null uses the additive ledger. | Fixed by narrowing the statement to ledger identities. |
| T6-N2 | Non-blocking | The lagged-control return ended at the current decision open, which weakened the claim that the control used strictly prior information. | Fixed by ending the return at the preceding hourly open; the future-perturbation boundary test moved with it. |
| T6-N3 | Non-blocking | The exact-24-hour test exercised a later 48-hour increase, and one null-test name described reversal although the test negated values. | Fixed with a 24-hour boundary fixture and accurate test name. |
| T6-N4 | Non-blocking | Determinism was checked across repeated calls in one process, but accepted digests were not yet pinned. | Deferred intentionally to the human acceptance/freeze step. |
| T6-N5 | Non-blocking | The canary import path relies on pytest exposing the tests directory. | Accepted for this test-only package; it does not affect production imports. |
| T6-Q1 | Human decision | Frozen documents do not select additive fixed-notional PnL or compounded equity as the production canonical ledger. | Must be decided before the NumPy reference implementation. |
| T6-Q2 | Human decision | The fallback Opus call was interrupted, so its completion-model metadata is unavailable. | Preserve honest provenance; independent inspection and reviews provide the acceptance evidence. |
| T6-Q3 | Human decision | Task 5's approved uniform 10-percentage-point materiality convention also governs exposure increases. | Carry forward the already approved Task 5 convention unless the owner directs an amendment. |

After the fixes, the coordinator reran the focused and full suites plus static,
formatting, import-boundary, whitespace, and frozen-baseline checks. All passed.

## Model evidence

The outer tool response identified the reviewer as `claude-fable-5-1`, session
`51d078de`, with reported cost USD 2.4879345. The review made no edits and had
no permission denials. This evidence concerns the Fable review only; it does
not retroactively establish metadata for the interrupted Opus implementation
call.
