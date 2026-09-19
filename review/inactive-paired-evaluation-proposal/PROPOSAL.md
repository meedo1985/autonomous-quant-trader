# Inactive Paired-Evaluation Assembly — proposal

**Decision ID:** `OD-PEA-001`
**Status:** `PROPOSAL — NO IMPLEMENTATION OR DATA-ACCESS AUTHORITY`
**Date:** 2026-09-19

This document proposes a possible bounded step after Task 12. It does not start
Task 13, authorize code, amend governance, create a trial, or permit access to
Binance, confirmation data, a lockbox, credentials, or trading.

## Rationale

Task 12 produced independently reviewed, inactive statistical primitives. The
smallest useful follow-up may be a pure assembly layer that exposes their
outputs together while preserving their existing meanings. Its limited benefit
would be one place to enforce both segment-level and complete-UTC-day alignment.

Doing nothing is equally safe and costs nothing. An assembler resembles the
nucleus of a validation engine even without a verdict field, so any future
implementation must receive the Constitution section 16 review required for an
enumerated protected component.

## Proposed bounded behavior

If separately authorized later, one pure function would accept an already
accepted candidate `BacktestResult`, benchmark `BacktestResult`, explicit
`horizon_hours`, optional caller-supplied opaque identity strings, and an
optional caller-supplied `ReplicateStream`.

It would delegate to the existing production primitives and return one frozen,
slotted, in-memory record for one symbol and one stress multiplier containing:

- symbol, multiplier, complete-day count and UTC boundaries;
- optional identity strings echoed verbatim after format validation only;
- per-leg descriptive metrics and maximum-drawdown magnitudes;
- the existing paired Sharpe statistics without changing either estimand;
- per-leg effective-sample-size results, method, fallback reason, and explicit
  series attribution;
- the existing paired bootstrap interval only when a stream was supplied; and
- `status = "INACTIVE_DIAGNOSTIC_ONLY"` plus the existing convention identifier.

The layer would delegate all alignment and arithmetic to existing functions. It
would not recompute, repair, reinterpret, or silently default their inputs.

## Mandatory containment

- No DSR, PBO, folds, CPCV, plateau analysis, null models, trial accounting,
  trial budgets, gates, eligibility, PASS/FAIL, promotion, or decisions.
- No protocol-threshold comparison, including 0.0, 120, 0.95, 0.30, or 0.60.
- No trial-seed derivation or `ReplicateStream` construction. An absent stream
  makes the interval explicitly unavailable and is not an error.
- No module-provided serialization, mapping export, hashing, persistence, filesystem,
  environment, process, network, exchange, credential, or hidden-data access.
- No import from code identity, manifests, ledgers, preregistration, research,
  governor, execution, lockbox, or model modules.
- No BTC/ETH gate-role assignment, cross-multiplier aggregation, delay stress,
  Binance integration, ingestion, model, strategy, order, deployment, or trade.
- No change to frozen v1.0 artifacts, sidecars, schemas, or accepted
  oracle/canary bytes.

Opaque identity strings, if later authorized, would be supplied by the caller,
validated for syntax only, and never resolved or computed. This is necessary
because `BacktestResult` does not carry protocol, data, experiment, or code
identity, while the existing identity helpers perform prohibited I/O or process
work.

## Governance boundary

The result would explicitly be neither a trial nor a Constitution section 23
report. It would carry no verdict and would count against no budget. It could
not satisfy the deferred DSR requirement, authorize governed research, open a
confirmation period, establish Binance parity, demonstrate edge, or support
promotion.

Implementation remains blocked until the owner approves a separate, narrowly
scoped authorization after reviewing this packet. Governed interpretation or
gate binding remains blocked on the qualified human/statistician decisions in
`SCIENTIFIC_DECISION_PACKET.md` and the formal amendment process.
