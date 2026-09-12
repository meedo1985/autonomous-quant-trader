# BACKTESTER_SPEC_v1.md

Status: pre-implementation specification.

1. Input is a timestamped target-exposure path plus prices and frozen cost-model inputs.
2. Bar semantics: decision at close(t); baseline execution at open(t+1).
3. Exposure changes are clipped to [0,1].
4. Costs are charged on absolute change in exposure using COST_MODEL_v1.
5. Risk increases occur only at the scheduled 00:00 UTC decision and are subject to the 24h minimum-hold rule.
6. Intraday hourly actions are allowed only for exposure reductions when the 10pp band is crossed.
7. No partial fills or passive limits in backtester v0.
8. PnL is computed from actual simulated exposure after execution, never intended exposure.

Pre-existing acceptance tests:
- zero exposure => zero trading PnL,
- buy-and-hold analytic identity,
- known alternating exposure => exact turnover/cost,
- higher cost never improves identical-path net PnL,
- future-return leakage canary produces absurd performance,
- causally lagged version does not,
- shuffled-label OOS null centered near zero,
- NumPy reference implementation matches within tolerance,
- deterministic rerun produces identical canonical metrics.

Oracle/canary tests are frozen after human acceptance.
