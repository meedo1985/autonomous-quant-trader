This is negotiation round 2, limited to D1/D4 and the terminal diagnostic.
Your first review proposed exposure drift and returned
`BETTER_DECISIONS_AVAILABLE`. We accept that as a potentially material defect,
but need to settle the exact minimal convention without inventing policy.

Additional repository evidence:

- Frozen BACKTESTER_SPEC input is a timestamped *target-exposure* path plus
  prices; PnL must use actual simulated exposure after execution.
- Frozen protocol says intraday reduction only if target is at least 0.10 below
  current exposure. It does not define whether "current" is the last target or
  the drifted portfolio weight.
- Frozen BUY_AND_HOLD says enter 100% and hold. VOL_TARGET produces fractional
  target exposure and rebalances under shared schedule/band rules.
- Task 5's pure `rebalance(state,target,time)` returns either prior state or the
  full target and intentionally contains no PnL/portfolio engine. Its approved
  threshold helper already uses inclusive `>=0.10` with a fixed
  `4*ulp(1.0)` representation-only tolerance and exhaustive boundary tests.
- Task 6's current private ledger treats its supplied exposure for each segment
  as actual held exposure. All current analytic paths are binary 0/1, so drift
  would not change their results. The future production engine does not exist.

Questions:

1. Is it scientifically better to declare now that the future engine must
   distinguish decision target from actual drifted portfolio weight, with
   `w_after_return = w*(1+r)/(1+w*r)` on a no-trade segment, and compute the
   next traded amount from target minus that drifted weight?
2. Should Task 6 tests be expanded now with a fractional no-trade drift identity
   and a later rebalance turnover identity, or should this wait for the NumPy
   reference task? Choose one and explain why under the mandated order.
3. Confirm that Task 5's existing centralized ULP-aware comparator is preferable
   to adding a new 1e-9 tolerance or integer-bps quantization.
4. Is hypothetical terminal liquidation cost required for acceptance now, or a
   non-blocking diagnostic for the later performance/reporting layer?
5. Give exact equations and the smallest revised decision set. Identify which
   parts are interpretations of frozen text and which are new human conventions.

Return `MAINTAIN_ORIGINAL` or `ADOPT_REVISED`, then the final D1-D4 decisions.
No preamble and no chain-of-thought.
