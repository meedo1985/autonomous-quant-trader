# Proposed DSR calibration plan

**Status:** AI proposal only; not calibrated, accepted, frozen, or active
**Date:** 2026-09-15
**Current decision:** DSR is diagnostic-only and cannot satisfy promotion

## Purpose

Define the evidence a future DSR method must supply before the frozen 0.95 score
can affect promotion. The threshold is a score threshold; it must not be
described as a validated 5% family-wise error rate or posterior probability
unless calibration establishes that exact claim.

## Pre-calibration registration

Before simulation, a human-reviewed record must freeze:

- method identifier, exact equations, null and benchmark meaning;
- difference-series Sharpe input and candidate-selection rule;
- treatment of current-cycle and lifetime trial counts;
- cross-trial dependence and dispersion estimators;
- supported sample-size, trial-count, moment, and dependence domain;
- the scientific error claim attached to 0.95;
- target error measure, acceptance tolerance, Monte Carlo confidence level,
  simultaneous scenario-control rule, and replication budget;
- separate development and held-out validation scenarios and seeds.

Acceptance values may not be selected after seeing calibration performance. A
failed held-out validation is reported as failure. A revised method receives a
new identity and a new independent validation set.

## Whole-procedure scenarios

Calibration must evaluate candidate selection as well as the final score:

1. independent normal null returns with analytic or high-accuracy references;
2. identical, opposite, near-duplicate, mixed-correlation, and unequal-variance
   trials, including the explicit `X` versus `-X` adversarial case;
3. positive and negative serial dependence and overlap associated with 24, 72,
   and 168-hour horizons;
4. skewness, finite-fourth-moment heavy tails, volatility clustering, and
   changing dependence;
5. unequal true performance, heterogeneous uncertainty, exact ties, and
   selection by a statistic different from difference-series Sharpe;
6. adaptive search, evaluated failures and aborts, reruns, and incomplete
   histories within the claimed support;
7. unsupported moments and structural breaks, reported as limits rather than
   repaired into a pass.

Cover one trial, the PBO activation boundary at 20, the family budget at 81, and
the complete proposed daily-sample domain. ESS 120 is not treated as 120
independent observations.

## Required outputs

For every scenario, record the score distribution, selected-candidate rejection
frequency and confidence bounds, unavailable frequency and reasons,
expected-maximum bias, and power under preregistered alternatives. Report
unavailable results separately so failure-prone methods cannot appear safe by
omitting difficult cases.

## Finite-sample contract to freeze

`T` means daily observations, `N` counted evaluated attempts, and `K` usable
complete current-cycle trial vectors.

Lifetime trial counts persist, but prior-cycle return matrices must not be pooled
into current-cycle DSR or PBO matrices. Raw trial count remains the fallback when
no effective-count method is frozen; a raw count alone supplies neither missing
cross-trial dispersion nor dependence information.

| Case | Proposed fail-closed behavior |
| --- | --- |
| `T < 4`, nonfinite, misaligned, or zero-variance series | Unavailable; no trimming, epsilon, or replacement |
| `N = 0`, `K = 0`, or invalid counts | Invalid/unavailable |
| `N = 1`, `K = 1` | Separately calibrated no-selection boundary; never evaluate an undefined expected-maximum quantile |
| `N > 1`, `K = 1` | Unavailable unless an accepted method supplies the missing selection information |
| Missing trial Sharpes or incomplete vectors | Preserve counted attempts; unavailable unless the method explicitly supports them |
| Zero or missing cross-trial dispersion | Defined calibrated branch or unavailable; never infer no selection bias |
| Nonpositive variance denominator or long-run variance | Unavailable; no absolute value, clipping, or fallback |
| Unsupported moments/dependence or invalid arithmetic | Unsupported/unavailable with stable reason |

Any future HAC method must use the influence process for the difference-series
Sharpe, not the existing paired-improvement influence process. Adjusting serial
uncertainty alone does not validate the selection benchmark.

## Acceptance boundary

This plan selects no DSR equation and invents no calibration thresholds. B1-B3
remain open until independent statistical calibration, different-model review,
human acceptance, and formal governance activation are complete. Until then,
DSR remains diagnostic-only and promotion remains blocked.
