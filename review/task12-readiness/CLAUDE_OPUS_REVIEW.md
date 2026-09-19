# Claude Opus adversarial review — synthetic readiness audit

Date: 2026-09-19

Base commit: `f235843981ae964b02707904d25d356f453d8b54`

Reviewed test hash before adjudication:
`e0e6fef4f4ad8911f010138f95d0dd7a4acc931182019b48f8ac2e52275c046f`

Observed model: `claude-opus-5`, medium effort, read-only

The requested `opus` alias resolved to `claude-opus-5`, not an Opus 5.1 model
identifier. Claude inspected the authorization, test, governing Task 12 records,
and every production API exercised by the test. It had no shell access and took
the reported validation outputs as evidence rather than rerunning them.

## Decision

**PASS — no blockers.** Claude found no frozen drift, source change, new
estimator or threshold, restricted-data/network access, Constitution section 16
component, or high-severity defect.

## Findings

| ID | Severity | Summary |
|---|---|---|
| T12R-01 | NON-BLOCKING | Input-preservation assertions held aliases rather than independent value snapshots. |
| T12R-02 | NON-BLOCKING | Equal OHLC values could not distinguish next-open execution from use of close/high/low. |
| T12R-03 | NON-BLOCKING | The original low-volatility fixture saturated vol-target at 1.0, duplicating buy-and-hold and not exercising the rebalance band. |
| T12R-04 | NON-BLOCKING | Replay assertions did not inspect action/trade scheduling invariants. |
| T12R-05 | NON-BLOCKING | The 16-day interval sat at the PPW minimum and lacked diagnostic assertions for long-run variance and block selection. |
| T12R-06 | NON-BLOCKING | The future-mutation canary lacked a positive control proving bytes actually changed. |
| T12R-07 | NON-BLOCKING | The external-access test name was broader than its post-import tripwires. |
| T12R-08 | NON-BLOCKING | Several failure injections lacked message matching; the missing-next-open and invalid stream-identity branches were absent. |
| T12R-09 | NON-BLOCKING | Some Task 12 assertions repeat existing unit coverage; the new value is the upstream cross-layer chain. |
| T12R-10 | NON-BLOCKING | The audit adds runtime to CI and initially had Windows-only timing evidence. |
| T12R-11 | NON-BLOCKING | Validation and review evidence still needed repository records. |
| T12R-12 | QUESTION | Decision ID `OD-T12R-002` had no preceding repository record. |
| T12R-13 | NON-BLOCKING | API-mandated `BTCUSDT` and 2020 labels could be misread as real market data without a disclaimer. |
| T12R-14 | NON-BLOCKING | One hardcoded count and candidate/benchmark variable names weakened clarity. |
| T12R-15 | QUESTION | Claude could not independently execute the reported commands in its read-only session. |

Claude explicitly confirmed that the original test applied benchmark policy
once, used the correct close(t) to open(t+1) timing, kept the cost-volatility
path causal, and made no promotion, trading, Binance-parity, or activation
claim. Dispositions and the final reviewed state are in `ADJUDICATION.md`.
