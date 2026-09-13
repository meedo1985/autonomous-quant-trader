Answer now from the supplied facts; do not inspect files and do not announce a
plan. We need a final decision on four conventions for a long-only `[0,1]`
crypto spot backtester with close(t) decisions, open(t+1) execution, costs on
absolute exposure changes, 00:00 UTC risk increases, 24h minimum hold, and a
10-percentage-point rebalance band.

Proposals:

1. Canonical production equity compounds as
   `E_next = E * (1-cost_rate*abs(delta_exposure)) * (1+clipped_exposure*return)`.
   Cost is charged at execution before the following open-to-open return.
   Additive fixed-notional PnL remains a diagnostic oracle.
2. Start every evaluation flat and charge initial-entry turnover/cost.
3. Do not force terminal liquidation; mark ending exposure to the final open.
   A cash-liquidation objective must declare and test liquidation separately.
4. Apply the Task-5-approved uniform band as `abs(change) >= 0.10` for an
   actionable change. Below 0.10 is HOLD. Intraday increases remain forbidden.

For each proposal output `D1/D2/D3/D4: ACCEPT`, `REVISE`, or `REJECT`, with a
short evidence-based reason. Check cost ordering, end-of-sample gaming,
`>=0.10` versus `>0.10`, and retaining additive diagnostics. Suggest a change
only if materially better and consistent with the stated frozen rules. End
with exactly `CURRENT_DECISIONS_BEST` or `BETTER_DECISIONS_AVAILABLE`, followed
by the exact recommended set. No preamble and no chain-of-thought.
