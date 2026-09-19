# Owner authorization — synthetic cross-layer readiness audit only

**Decision ID:** `OD-T12R-001`

**Recorded:** 2026-09-19

**Decision:** `APPROVE_TESTS_ONLY_READINESS_AUDIT`

**Authority:** the owner's project-conversation instructions to continue with
multiple senior-specialist agents and practical tests

**Base commit:** `f235843981ae964b02707904d25d356f453d8b54`

**Governance effect:** none

## Authorized objective

Add and execute one synthetic integration audit that connects canonical
benchmark signals, the production backtester, descriptive metrics, and the
inactive Task 12 statistical primitives. Independent specialists may review and
run the audit. The work tests component plumbing and failure boundaries only; it
does not evaluate a strategy or authorize a research cycle.

## Exact allowlist

- add `tests/integration/test_synthetic_readiness_audit.py`;
- add review and result records under `review/task12-readiness/`;
- run existing synthetic tests, lint, type, import-boundary, frozen-verification,
  and accepted Task 6 hash checks.

No other path may change.

## Explicit exclusions

This authorization does not permit production-source changes, accepted
oracle/canary changes, frozen-file or schema changes, Task 13, DSR/PBO,
calibration or simulation, governed trials, confirmation or lockbox access,
market-data or exchange network access, Binance credentials, orders, trading,
deployment, eligibility, promotion, or a scientific PASS/FAIL verdict.

Synthetic results may prove deterministic software behavior only. They cannot
be described as evidence of trading edge, profitability, Binance parity,
confirmation readiness, or promotion readiness. The existing DSR `DEFER`
decision remains controlling.

## Specialist roles

1. senior quantitative/statistical reviewer;
2. senior software-test and reproducibility reviewer;
3. senior Binance Spot and trading-safety reviewer;
4. senior governance reviewer.

Agent findings are advisory and must be adjudicated with evidence. AI review
does not replace any required human or statistician review.

## Stop conditions

Stop and report `BLOCKED` on frozen/hash drift, an unexpected source-file
change, need for a new estimator or threshold, restricted-data or network
access, a Constitution section 16 protected component, or an unresolved
high-severity finding.

Completion closes this audit only. It does not open Task 13.
