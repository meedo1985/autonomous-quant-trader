# Task 5 — Sol High external review

Reviewer: `gpt-5.6-sol`, high reasoning, independently dispatched read-only.
Reviewed state: `b98d9a0`, base `c5b5d6c`.
Verdict: **LOCAL GATE BLOCKED**. No code changes were applied.

## BLOCKER B1 — exact 10 percentage-point changes can be ignored

- Location: `src/aqt/benchmarks/canonical.py:657`; incomplete boundary test at `tests/unit/test_canonical_benchmarks.py:954`.
- Evidence: decimal transitions such as `0.3 -> 0.2` and `0.2 -> 0.3` produce binary floating deltas of about `0.09999999999999998`, so a literal comparison with `0.10` classifies them as inside the band. An independent sweep found 12 of 20 adjacent tenth-step pairs misclassified.
- Impact: canonical exposure, turnover and later costs depend on floating representation.
- Minimal correction: centralize an ULP-aware threshold comparison and test adjacent tenth-step pairs plus values immediately inside/outside the boundary.

## BLOCKER B2 — frozen benchmark behavior is mutable at runtime

- Location: `src/aqt/benchmarks/canonical.py:276,285`, consumed at `:486,518`.
- Evidence: exported `Final[dict]` objects remain mutable. Mutating `SIGNAL_LABELS[CASH]` changes identical-call output; mutating `REQUIRED_HISTORY_BARS_BY_BENCHMARK[CASH]` changes validation behavior.
- Impact: fixed benchmark identity can drift without a code/hash change, contradicting the fixed/deterministic requirement.
- Minimal correction: expose immutable mappings or keep lookup tables private and immutable; add mutation-rejection tests.

## BLOCKER B3 — impossible minimum-hold states are accepted

- Location: `src/aqt/benchmarks/canonical.py:567-575`.
- Evidence: public `ExposureState` accepts `last_risk_increase_time` at `00:30 UTC` or `05:00 UTC`, despite risk increases being permitted only at scheduled `00:00 UTC`; rebalance then uses that timestamp for its 24h clock.
- Impact: reconstructed/resumed paths can use a noncanonical minimum-hold clock.
- Minimal correction: require hourly alignment and the 00:00 UTC anchor for non-null risk-increase timestamps; correct impossible test fixtures and add rejection cases.

## Positive findings

Benchmark identities and formula constants, UTC decision causality, no-future-data behavior, gap/warm-up rejection, exposure bounds, shared Task 3/4 EWMA semantics and scope boundaries otherwise passed inspection. Cost application and fills remain deferred as authorized.

## Reviewer validation

- Whole suite: 630 passed, 4 skipped.
- Task 5 suite: 424 passed, 4 skipped.
- Targeted Ruff format/check and diff check: pass.
- Task 5 diff contains four authorized files and no frozen-file changes.
- Fourteen raw sidecars, manifest bindings and Constitution canonical self-hash verified.

This is an external code/scientific review, not authorization for trading or Task 6.
