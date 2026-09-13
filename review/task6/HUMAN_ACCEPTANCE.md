# Task 6 — human decision acceptance

Date: 2026-09-13

The owner explicitly replied `نعم اعتمد` to the proposed revised Task 6
decisions and authorized adding the two exact oracle identities, rerunning
independent review, freezing the accepted suite after a clean gate, and pushing
the completed Task 6 commit.

Accepted conventions:

1. Production uses compounded equity with cost charged at execution before the
   following open-to-open return. Additive fixed-notional PnL remains a
   diagnostic oracle.
2. Decision targets and actual held weights are distinct. On a no-trade segment
   with zero cash return, fractional held weight drifts as
   `w_after = w*(1+r)/(1+w*r)`. PnL uses actual held weight, and the next trade
   is measured from `w_after` to the clipped target.
3. Every evaluation starts flat and charges initial-entry turnover and cost.
4. No forced terminal liquidation is deducted from acceptance PnL; ending
   exposure is marked to the final open. Hypothetical liquidation cost is a
   later reporting diagnostic.
5. The 10pp band is inclusive and applies to the difference between target and
   actual held weight. Float implementations must reuse Task 5's centralized
   ULP-aware comparator. Intraday increases remain forbidden.

The two new exact oracle identities must pass local and different-model review
before the oracle/canary hashes are pinned. No Task 7 work is authorized by
this acceptance.
