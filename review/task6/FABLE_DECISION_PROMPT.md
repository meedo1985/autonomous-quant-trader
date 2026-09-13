You are the independent Claude side of an evidence-aware architecture decision
review for Task 6 of a crypto spot research backtester. Review only the four
human decisions below. Do not write code, invent strategy logic, or assume
leverage, shorting, partial fills, or passive orders.

Frozen facts:

- Target exposures are clipped to `[0,1]`.
- Decision is at `close(t)` and execution at `open(t+1)`.
- Costs apply to absolute exposure change using the frozen cost model.
- Risk increases occur only at scheduled 00:00 UTC and obey a 24-hour minimum
  hold.
- Intraday hourly actions are only exposure reductions when the 10
  percentage-point band is crossed.
- PnL uses actual simulated exposure after execution.
- The frozen spec does not choose additive fixed-notional PnL versus compounded
  equity and does not bind initial holdings or forced terminal liquidation.
- Exact oracle tests cover both aggregators. The corrected suite passes 52
  focused tests and 777 full tests; frozen governance hashes are unchanged.

Current proposed decisions:

D1. Production canonical accounting is compounded equity. For segment `i`,
`E_(i+1) = E_i * (1 - c_i) * (1 + x_i * r_i)`, where `x_i` is clipped actual
exposure, `r_i` is the open-to-open simple return, and `c_i` is the cost rate
times absolute exposure change. Additive fixed-notional PnL remains a diagnostic
oracle only.

D2. Every evaluation starts flat (`x_before_0=0`), so initial entry turnover
and cost are charged.

D3. No forced terminal liquidation cost; ending exposure is marked to the final
open. Any later objective requiring cash liquidation must declare and test that
separately.

D4. Carry forward Task 5's already approved uniform 10pp materiality convention:
changes below 10pp are HOLD; scheduled increases and intraday reductions must
cross the same band, while intraday increases remain forbidden.

Evaluate each decision for scientific defensibility, cost realism,
comparability, ambiguity, and resistance to backtest gaming. For each, return
ACCEPT, REVISE, or REJECT with exact reasoning. Propose an alternative only if
it is materially better now and consistent with the frozen facts. Explicitly
examine whether costs should be applied before or after the segment return;
whether no terminal liquidation creates exploitable end-of-sample bias; whether
the 10pp threshold boundary means `>=10pp` or `>10pp`; and whether compounded
production accounting should retain additive diagnostics.

End with exactly one of `CURRENT_DECISIONS_BEST` or
`BETTER_DECISIONS_AVAILABLE`, then provide a concise final recommended decision
set. Provide conclusions and supporting evidence only, without chain-of-thought.
