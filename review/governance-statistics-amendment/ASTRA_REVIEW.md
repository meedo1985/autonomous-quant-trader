# Summary of Astra independent review

**Model:** `gpt-6-astra`
**Mode:** read-only
**Date:** 2026-09-15
**Verdict:** **REVISION REQUIRED**

## Blocking findings

1. **B1 — DSR effective trial count.** The proposed effective DSR trial count is
   not generally valid for maxima.
   Perfectly opposite trial series collapse to one effective trial under squared
   correlation even though selecting their maximum still creates positive
   selection bias. The complete DSR procedure requires calibration.
2. **B2 — DSR finite-sample behavior.** Behavior was incomplete for `N=1`,
   `K=1`, missing trial
   Sharpes, and zero or missing cross-trial dispersion.
3. **B3 — DSR promotion semantics.** Diagnostic-only DSR conflicted with
   preserving the mandatory 0.95 promotion
   gate. Diagnostic-only must leave promotion blocked unless a later amendment
   supplies an accepted active method.
4. **B4 — Lockbox estimand.** The lockbox “paired-difference series” cannot
   reconstruct the difference of
   two Sharpe ratios. Joint-leg resampling and exact prediction semantics must be
   frozen before promotion becomes available.
5. **B5 — Specification/code/hash migration.** The final statistical
   specification cannot automatically reuse the inactive
   Task 12 implementation. Its accepted hash and deterministic bootstrap vectors
   must be migrated and reviewed together.

## Other findings

- ETH 2x is an optional deliberate tightening. Rejection preserves ETH 1x;
  acceptance adds ETH 2x alongside it.
- The Constitution section 4 framework and proposed versioned-artifact approach
  are feasible. Keeping Constitution v1.0 is reasonable if its requirements are
  unchanged.
- The review did not independently establish historical frozen-byte preservation
  against a trusted external baseline.

No files were modified by the reviewer.
