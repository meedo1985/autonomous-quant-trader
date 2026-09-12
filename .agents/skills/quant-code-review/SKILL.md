---
name: quant-code-review
description: Review autonomous-quant-trader tasks involving data, backtesting, validation, benchmarks, features, models, or promotion gates for scientific and temporal correctness. Do not invent strategy logic.
---

# Quant code review

Read root `AGENTS.md`, the Constitution, protocol, and applicable frozen specs. Review the actual code paths and task acceptance criteria; do not design strategies, tune parameters, change statistical thresholds, or broaden the task. Use synthetic or exploration evidence only and respect restricted-data identities.

Follow a representative observation from availability time through features, labels, fitting, decisions, fills, returns, costs, metrics, and eligibility. Check relevant callers and tests, not only the changed lines.

- Look-ahead and label leakage: future inputs, centered windows, negative shifts, globally fit preprocessing, feature selection using OOS results, and labels entering their own predictors.
- Time semantics: UTC and timestamp meaning, availability versus event time, inclusive boundaries, joins/resampling, decision at close(t), and baseline fill at open(t+1). Features must exist by the decision timestamp; PnL must use actual simulated exposure.
- Sampling assumptions: survivorship, delistings/venue status, point-in-time universe/fees/filters, outages, missing/duplicate bars, silent dropping or correction, and untradeable intervals.
- Partition integrity: exploration/confirmation/lockbox boundaries, training/OOS separation, rolling fit windows, purge/embargo, overlapping labels, dependence-aware ESS, and fold aggregates. Bar count is not sample size; BTC/ETH agreement is not independent replication.
- Selection bias: hidden retries, excluded failures, per-fold reselection, implicit parameter tuning, unregistered grids, multiple comparisons, family/lifetime trial accounting, and post-result benchmark or acceptance-criterion changes.
- Transaction costs: traded-notional units, per-side charging, turnover, spread/slippage/fees, cost stress and delay stress, and agreement with the frozen cost model. Verify applicable analytic/oracle identities.
- Benchmark consistency: fixed identities and parameters, same bar/execution/cost semantics and applicable scheduling/band/min-hold rules, paired series alignment, and the predeclared comparison benchmark.
- Exposure constraints: accidental shorting or leverage, clipping and bounds, initial holdings, cash/accounting, scheduled risk increases, intraday reductions, and minimum holding periods.
- Determinism: seeds, data ordering, unstable joins, parallel reductions, serialization, reproducible outputs, and explicit handling of numerical edge cases without undocumented fallbacks.

For each applicable area, report evidence or a precise gap. Classify findings as `BLOCKER`, `NON-BLOCKING`, or `QUESTION`, with file/line, triggering example, governing rule, impact, and proposed minimal correction. Do not invent missing financial conventions to close a finding. Missing mandatory tests or violated scientific/safety invariants are blockers. Preserve `NO_EDGE_FOUND` as a valid result. Return findings to `task-gate-review`; never apply frozen-governance or scientific changes automatically.
