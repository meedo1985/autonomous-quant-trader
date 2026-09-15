# Local review of statistical amendment proposal

**Status:** internal preparation; this is not the required independent review.
**Reviewer:** Codex local review
**Date:** 2026-09-15

## Findings

- **BLOCKER — DSR activation path is unresolved.** Every candidate DSR procedure,
  including a conventional i.i.d. method, requires complete independent
  calibration. The owner must select a calibrated active path or keep DSR
  diagnostic-only with promotion blocked.
- **BLOCKER — ETH 2x rule requires an explicit owner decision.** The proposal
  makes the stricter ETH stress requirement conditional, so it cannot be treated
  as active until accepted in the signed decision record.
- **NON-BLOCKING — Versioned artifacts are illustrative only.** The proposed
  v1.1 names must be replaced by the human-authored final paths and included in
  the new manifest and sidecars; v1.0 hashes must remain unchanged.
- **BLOCKER — Calibration evidence must be reproducible.** The whole selected
  DSR procedure needs fixed calibration inputs, seed/runtime information, oracle
  expectations, finite-sample boundary behavior, and an independently reviewed
  acceptance criterion before the method can affect promotion.
- **BLOCKER — Lockbox estimand is unresolved.** The final C2 specification must
  define joint-leg resampling and the exact prediction statistic; a return-
  difference series cannot reconstruct a difference of two Sharpe ratios.
- **BLOCKER — Final specification/code/hash migration is unresolved.** A changed
  convention binding changes deterministic bootstrap streams and therefore needs
  a reviewed implementation binding and refreshed reference vectors.
- **QUESTION — C1 status must be recorded.** The owner checklist asks whether
  C1 started; the signed decision must state its outcome and confirm no result is
  being carried retroactively into C2.

## Constitution check

The draft is proposal-only, preserves v1.0, requires cycle termination, a version
bump, owner signature/date, pre-C2 activation, preserved history, and no
retroactive effect. It does not edit frozen governance artifacts.

## Verdict

**SCIENTIFIC CALIBRATION REQUIRED** before activation. The draft is suitable for
owner decision and independent review, but it is not an active amendment.
