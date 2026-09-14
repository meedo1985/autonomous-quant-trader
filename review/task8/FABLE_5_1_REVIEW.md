# Task 8 independent Fable 5.1 review

Reviewer: Claude Code canonical model `claude-fable-5-1`, medium effort
Date: 2026-09-14
Mode: read-only adversarial review
Verdict: **PASS**

The model identity came from Claude Code's returned `modelUsage` metadata. The
reviewer confirmed that all six attachment hashes matched the adversarial
packet. Its attempts to execute tests and ad-hoc probes were denied by its
read-only sandbox, so it relied on the recorded local validation for execution
evidence. It read the implementation, production dependencies, exact oracle,
NumPy reference, derived bounds, frozen backtester/cost specifications, and
the approved Task 3 decision.

## BLOCKER

None.

## NON-BLOCKING

### T8-NB-1 — Matrix checks terminal equity, while the direct unit test pins intra-segment cost order

The 160-path integration matrix compares final compounded equity. Since the
same multiplication factors commute at the terminal point, that comparison
alone cannot distinguish cost-before-return from cost-after-return. The direct
unit test does assert `equity_after_cost` and `equity_after_return`, and the
implementation visibly charges cost first. Suggested optional improvement:
compare per-segment equity states with the reference curve.

### T8-NB-2 — Extreme drift rounding is fail-loud

For a held weight within a few ULPs of 1 and a very large positive return, the
reviewer reasoned that the drift computation could theoretically round above
1. If so, `ExposureState` rejects it and the engine returns `BacktestError`.
The exact oracle and NumPy reference also reject out-of-range actual exposure.
The reviewer could not run a numeric probe, so it explicitly marked this as a
reasoned scenario rather than a demonstrated defect. No code change required.

### T8-NB-3 — Full-series continuity intentionally gates the run

The engine validates the complete supplied series, so a hole after the final
decision also rejects the run. Values remain causal because the volatility
offset selects only returns observable at each decision. This is consistent
with the approved no-silent-slicing convention. No correction required.

### T8-NB-4 — Boolean stress was accepted as 1.0

Python equality makes `True == 1.0`; the reused cost validator therefore
accepted `stress_multiplier=True`, unlike the explicit Boolean rejection for
`delay_bars`. Suggested correction: reject Boolean stress explicitly.

## QUESTION

### T8-Q-1 — Delay-stress state during overlapping decisions

The reviewer concluded that rejecting nonzero delay is the correct minimal
treatment. Frozen text binds the one-bar fill shift and Task 3 binds the
volatility cutoff, but nothing binds whether a decision taken before a delayed
fill observes pre-fill state, a pending clipped target, or post-fill state, or
whether a later reduction may supersede a pending increase. Neither accepted
reference implements delay. This remains an owner policy question for a later
authorized decision and is not a Task 8 baseline defect.

## Reviewer conclusion

The reviewer found no future-value influence, accounting-unit error,
target/held-state confusion, invented tolerance, scope expansion, secret/data
access, or deterministic hazard. It confirmed next-open execution, canonical
return order, actual fractional drift, cost before return, the minimum-hold
clock, no terminal liquidation, and the independence structure of the matrix.
It returned **PASS** for the Task 8 baseline engine.
