# CANONICAL_BENCHMARKS_v1.md

Status: Cycle-1 canonical benchmark specification.

Shared rules for candidate-comparable benchmarks:
- 1h bars.
- Same bar-semantics module as candidates.
- Same cost model and baseline execution assumption as candidates.
- Same scheduled 00:00 UTC evaluation.
- Same 10 percentage-point rebalance band where relevant.
- Risk increases respect the 24h minimum-holding rule.
- Intraday band-triggered actions are allowed only to reduce exposure.

## CASH
Exposure = 0.

## BUY_AND_HOLD
Enter 100% exposure at the first eligible execution and hold.

## VOL_TARGET_BUY_AND_HOLD
- Volatility estimator: EWMA of hourly log returns.
- EWMA half-life: 168 hours.
- Annualization factor: sqrt(8760).
- Annualized volatility target: 0.60.
- Target exposure = clip(0.60 / annualized_forecast_vol, 0, 1).
- Rebalance under the shared scheduling/band/min-hold rules.

## CANONICAL_TREND
- Trend signal: close > 200-day simple moving average.
- Exposure target: 1 if true, else 0.
- Rebalance under the shared scheduling/band/min-hold rules.

## CANONICAL_TSMOM
- Momentum signal: trailing 180-day log return > 0.
- Exposure target: 1 if true, else 0.
- Rebalance under the shared scheduling/band/min-hold rules.

These parameters are fixed and not tunable in Cycle 1.
