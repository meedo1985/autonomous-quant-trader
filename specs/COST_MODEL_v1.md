# COST_MODEL_v1.md

Status: Cycle-1 frozen cost-model specification.

## Baseline execution
Decision timestamp = eligible 1h bar close.
Baseline fill price = next 1h bar open, then costs are applied.

## Order style
Taker-like only.

## Fee
- Use point-in-time Binance spot taker fee where a reliable historical schedule is available.
- Fallback taker fee when unavailable: 10 basis points per traded notional, per side.

## Spread allowance
- Fixed allowance: 2 basis points per traded notional, per side.

## Slippage
Let `sigma_hourly_bps` be trailing EWMA hourly volatility expressed in basis points.
- EWMA half-life: 168 hours.
- Initialization: for the first 168 available hourly returns, use the simple sample standard deviation of available returns; from bar 169 onward use the recursive EWMA initialized from the simple sample standard deviation of the first 168 returns.
Per-side slippage in basis points:

`slippage_bps = min(15.0, max(1.0, 0.05 * sigma_hourly_bps))`

Properties:
- non-negative,
- monotone in volatility,
- floor 1 bp,
- cap 15 bps.

## Total modeled per-side cost
`fee_bps + spread_bps + slippage_bps`

## Stress
1.0x, 1.5x, 2.0x, 3.0x multiply total modeled trading cost.

## Delay stress
Shift the baseline fill by one additional 1h bar, then apply the same cost model.

No passive-limit assumptions in Cycle 1.
