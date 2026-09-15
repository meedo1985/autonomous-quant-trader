# Statistical governance amendment proposal

Status: **AI PROPOSAL ONLY — NOT AN AMENDMENT — NOT SIGNED — NOT ACTIVE**

Date prepared: 2026-09-15
Current frozen protocol: version 1.0, cycle C1
Current Constitution: version 1.0, unchanged by this proposal

## Purpose

The frozen protocol names Sharpe, paired delta-Sharpe, Newey-West ESS,
stationary bootstrap, DSR, and PBO, but does not fully define their estimators and
finite-sample behavior. Task 12 therefore remains inactive for governed research.
This proposal supplies a complete review target; it does not author, merge,
freeze, or activate an amendment.

## Recorded owner choices

On 2026-09-15, the owner approved preparation on this basis:

- C1 never started;
- DSR remains diagnostic-only and promotion remains blocked until a complete
  method is independently calibrated and formally accepted;
- the proposed ETH 2x tightening is rejected, preserving the frozen ETH 1x rule.

These choices resolve proposal branches only. They do not satisfy scientific
calibration or Constitution section 4 activation requirements.

## Proposed change-control outcome

If accepted after independent scientific and human review:

- preserve every v1.0/C1 artifact and hash without modification;
- terminate C1 before any result under the new conventions;
- create cycle C2 with protocol version 1.1;
- bind a versioned statistical-conventions specification and accepted statistics
  code hash before the first C2 equity curve or evaluated trial;
- create new sidecars and a versioned frozen manifest rather than rewriting the
  v1.0 manifest;
- apply no new convention retroactively to C1 or an open promotion;
- retain Constitution version 1.0 because this is a protocol-level scientific
  change;
- activate only through an owner-of-record signed and dated commit before C2.

Illustrative future artifact names, requiring human authorship:

```text
specs/STATISTICAL_CONVENTIONS_v1.md
protocols/protocol_v1_1.yaml
FROZEN_HASHES_v1_1.json
```

## Proposed statistical semantics

### Daily observations and paired Sharpe

- Use complete UTC days of exactly 24 contiguous accepted one-hour segments.
- Compound candidate and comparison separately before subtracting returns.
- Reject partial, missing, duplicated, irregular, nonfinite, or misaligned data.
- Use zero risk-free return and sample variance with denominator `n - 1`.
- Report daily Sharpe and `sqrt(365)` scaled daily Sharpe.
- Define paired improvement as scaled candidate Sharpe minus scaled comparison
  Sharpe; name Sharpe of their return differences separately.
- Zero variance, insufficient observations, or invalid arithmetic is unavailable;
  never apply epsilon floors, silent trimming, or outcome-dependent repair.

### Newey-West ESS

Use daily BTC strategy returns. With `h = ceil(horizon_hours / 24)`:

```text
gamma_k = sum(e[t] * e[t-k]) / n
L = min(n-1, max(h-1, floor(4 * (n/100)^(2/9))))
w_k = 1 - k/(L+1)
Omega = gamma_0 + 2 * sum(w_k * gamma_k)
ESS = clamp(n * gamma_0 / Omega, 1, n)
```

For otherwise-valid zero variance or nonpositive `Omega`, use the frozen
fallback `n/h` and record its reason. Other invalid inputs are unavailable.

### Stationary bootstrap

- Use the corrected Patton-Politis-White 2009 convention and exact formulas in
  `review/task12/IMPLEMENTATION_CONVENTIONS.md`.
- Resample candidate and comparison jointly with one index sequence.
- Use exactly 2,000 attempted replicates in index order.
- Derive private MT19937 streams from the full Task 10 seed, convention hash,
  purpose, asset, cost multiplier, evaluation window, length, and replicate.
- Record the Python runtime and use unbiased integer rejection sampling.
- Any invalid replicate makes the interval unavailable without replacement.
- Use an unrecentered percentile interval with type-7 5th/95th percentiles.

### DSR proposal

- Keep unannualized daily candidate-minus-comparison returns as DSR input.
- Require at least four finite, nonconstant observations.
- Use population central moments for skewness and Pearson kurtosis.
- Build family-trial Pearson correlations from complete aligned current-cycle
  series.
- Treat `N_eff = N^2 / sum(R_ij^2)` only as an unvalidated candidate estimator.
  It must not drive promotion: squared correlation can collapse perfectly
  opposite trials to one effective trial even though choosing their maximum
  still creates selection bias.
- Require calibration of the complete DSR procedure, including the
  expected-maximum approximation, trial dependence, trial dispersion, failed or
  incomplete attempts, and finite-sample behavior. HAC calibration alone is not
  sufficient.
- The final human-authored specification must freeze the exact DSR equation and
  define `N=1`, `K=1`, zero/missing cross-trial dispersion, unavailable trial
  Sharpes, moment conventions, and every fail-closed outcome against independent
  numerical references.
- A conventional i.i.d. method may be considered only as a separately named,
  calibrated method with its limitations stated. A HAC-adjusted method must use
  a distinct identifier, the Sharpe influence process, independent calibration,
  and separate owner approval.

This proposal activates no DSR method. Until the complete selected procedure is
independently calibrated and accepted, governed DSR is unavailable and the
mandatory 0.95 promotion gate remains unsatisfied. Choosing diagnostic-only DSR
therefore keeps promotion blocked; it does not remove or waive the gate.

### PBO proposal

- Activate only at 20 current-family evaluated trials.
- Use 16 chronological balanced blocks and all 12,870 oriented 8/8 splits.
- Preserve remainder observations in the earliest blocks.
- Require a complete aligned candidate/common-comparison matrix.
- Rank by paired Sharpe improvement and average uniformly across exact IS ties.
- Use ascending OOS midranks, `omega = rank/(N+1)`, and `logit(omega)`;
  score negative/positive/zero logit as 1/0/0.5.
- Any missing or invalid trial/split makes PBO unavailable; never omit, impute,
  or change the denominator.

### Drawdown, trial accounting, and gates

- Reuse Task 11 drawdown: initial equity plus every hourly closing equity,
  expressed as nonnegative fractional peak-to-trough magnitude.
- Begin an evaluated attempt at durable `EVALUATION_STARTED`, immediately before
  evaluation-data access or computation.
- Count failures, evaluated aborts, and reruns; event redelivery is idempotent but
  each actual new attempt has a new ID.
- BTC and ETH remain one joint attempt. Preserve current-cycle and lifetime totals
  separately; never pool prior-cycle DSR/PBO matrices.
- Unavailable mandatory statistics produce `INDETERMINATE/BLOCKED`, never PASS.
- BTC CI lower endpoint must be strictly greater than zero.
- DSR passes at `>=0.95` only under an approved active method; PBO passes at
  `<=0.30`; ESS at `>=120`; fold wins require strict positive paired improvement
  and the fraction remains `>=0.60`.
- Drawdown passes when candidate minus comparison MDD is `<=0.05`.
- ETH 1x sanity requires positive paired improvement and the same drawdown rule.
- Proposed 2x stress reruns both candidate and comparison on both assets. BTC
  requires positive paired improvement, positive net return, and drawdown pass;
  ETH requires positive paired improvement and drawdown pass at 2x. This ETH 2x
  tightening needs explicit owner acceptance.

### Lockbox prediction distribution

The frozen phrase “paired-difference series” is insufficient to calculate a
difference of two Sharpe ratios. Before promotion can become available, the
human-authored C2 specification must define joint candidate/comparison leg
resampling, the lockbox-length unit, deterministic stream identity, the exact
prediction statistic, and prediction-quantile semantics. Until those semantics
and independent reference vectors are accepted, the lockbox stage remains
blocked.

### Specification and implementation binding

The inactive Task 12 implementation accepts only the raw hash of its current
conventions document and identifies itself as `aqt.statistics.inactive.v1`.
Before C2 activation, a reviewed migration must bind the final human-authored
statistical specification to an accepted implementation. Any changed stream
binding requires refreshed deterministic reference vectors because it changes
bootstrap samples. Schema validation alone is not evidence that these bindings
or methods are correct.

## Frozen values preserved

No proposed change to: 2,000 bootstrap attempts; 90% paired interval; DSR 0.95;
PBO 0.30; PBO activation at 20 trials; 16 partitions; ESS 120; CPCV at 250;
fold-win fraction 0.60; null percentile 0.95; or 81 trials per family.

## Blockers before activation

The owner must choose a candidate DSR path for calibration:

1. calibrate a separately named conventional i.i.d. procedure, including its
   complete selection-bias and finite-sample behavior;
2. calibrate and approve a separately named dependence-aware procedure;
3. keep DSR diagnostic-only and keep promotion blocked until a validated method
   exists.

The owner must also explicitly accept or reject the ETH 2x tightening. Rejection
preserves the frozen ETH 1x rule; acceptance adds ETH 2x alongside ETH 1x. No AI
should make either decision without independent scientific review.

Before activation, the lockbox estimand and the final specification/code/hash
migration must also be frozen and independently verified as described above.

Nothing here changes v1.0, starts C2, authorizes real data, opens confirmation or
lockbox access, permits a trial, or creates a promotion path.
