# Astra design review — DSR calibration and lockbox prediction

**Model:** `gpt-6-astra`
**Mode:** independent read-only scientific design review
**Date:** 2026-09-15
**Verdict:** **SCIENTIFIC CALIBRATION REQUIRED**

Astra proposed the calibration structure and joint-leg lockbox estimand recorded
in `DSR_CALIBRATION_PLAN.md` and `LOCKBOX_PREDICTION_PROPOSAL.md`. It confirmed
that these documents can form a review target but resolve none of B1-B5.

Key conclusions:

- DSR calibration must test the complete selection procedure, not only HAC
  uncertainty, and must preregister the claim attached to the 0.95 score.
- Squared-correlation effective count remains unvalidated, especially for
  perfectly opposite trials.
- Diagnostic-only DSR cannot satisfy promotion.
- Lockbox prediction should jointly resample both daily legs to an independently
  prebound target length `m` and calculate the difference of their Sharpes.
- Current Task 12 code cannot do this because it restricts stream purpose and
  forces output length equal to source length.
- Deterministic migration and independent reference vectors must be reviewed
  before any future implementation is accepted.

No files were changed by Astra, and no confirmation or lockbox data was accessed.

## Synthesis verification

Astra re-read the synthesized plan and returned **PASS WITH CONDITIONS** for the
blocked proposal documents. It verified the separate-leg Sharpe equation,
distinct source/output lengths, modulo-source indexing, 2,000-attempt rule, and
type-7 lower quantile arithmetic. Its requested clarifications were incorporated:
explicit fresh-index draws on restart, explicit definitions of `n` and `m`,
current-cycle versus lifetime trial-history restrictions, and the exact
PASS/FAIL-only research output. B1-B5 remain open.
