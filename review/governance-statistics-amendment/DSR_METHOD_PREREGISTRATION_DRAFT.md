# DSR method candidate and preregistration worksheet

Date: 2026-09-17
Status: AI PROPOSAL ONLY; not selected, preregistered, calibrated, or active.
Scope: review preparation under the recorded owner decision. This is not the
human-authored final specification or an amendment. No simulation was run.

## Decision requested from scientific and human review

Consider the conventional candidate below as a synthetic calibration baseline.
It is not proposed as a validated solution for dependent trading returns.
Accepting a calibration experiment would not accept its method for promotion.
Complete and review the registration worksheet before any calibration run.
Keep DSR diagnostic-only and the mandatory 0.95 gate unsatisfied throughout.

References: `DSR_CALIBRATION_PLAN.md`, `OWNER_DECISION.md`,
`DRAFT_AMENDMENT_PROPOSAL.md`, and frozen Constitution sections 4, 7a, 9, 16, 27.

## Candidate equation for review

Literature basis: Bailey and Lopez de Prado (2014), equations 1-2, printed
pages 7-9, [author-hosted paper](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf).
Their conventional score uses a normal CDF, selected-series moments, and an
approximate expected maximum based on trial count and Sharpe dispersion.
The expected-maximum derivation assumes independent normal trial Sharpes.

```text
A(N) = (1-gamma) * Phi_inverse(1-1/N)
       + gamma * Phi_inverse(1-1/(N*e))                 [N > 1]
S0 = sqrt(V) * A(N)
D = 1 - skew*S + ((kurtosis-1)/4)*S*S
score = Phi((S-S0)*sqrt(T-1)/sqrt(D))
```

Here gamma is the Euler-Mascheroni constant; Phi is the standard normal CDF.
The equations are a literature baseline, not evidence that 0.95 controls a
family error rate or represents a posterior probability.

## Proposed project-specific contract

Everything in this section is a review proposal, not a claim from the paper.
Candidate identifier: `aqt.dsr.iid_raw_count.proposal.v1`; never substitute it
for the inactive Task 12 implementation identity or an active method identifier.

- Each column is unannualized daily candidate net return minus the fixed
  comparison benchmark's daily net return. Compound each leg before subtraction.
  Follow the existing complete-UTC-day, alignment, asset, cost, and no-repair
  conventions. Difference-series Sharpe is not paired delta-Sharpe.
- For each usable column, `S = mean(x)/s`, with sample variance denominator
  `T-1`. Let `mu_r = sum((x-mean(x))**r)/T`; proposed skew is
  `mu_3/mu_2**1.5` and Pearson kurtosis is `mu_4/mu_2**2`.
- Record `N_cycle`, `N_lifetime`, and `K` separately. Counts include failures,
  evaluated aborts, and actual reruns; event redelivery does not add attempts.
  Never pool previous-cycle returns into the current-cycle matrix.
- Proposed numerical baseline support is deliberately narrow:
  `N_lifetime = N_cycle = K = N`, complete aligned series, no adaptive search,
  and a synthetic design with independent trials and independent daily draws.
  This does not claim independence can be established from sample correlations.
  A practical method for broader histories remains unresolved.
- For `N > 1`, propose sample dispersion
  `V = sum((S_j - mean(S_j))**2)/(K-1)`. No effective-count substitution,
  estimated pairwise-correlation correction, or silent dispersion fallback.
- The baseline selects the largest difference-series Sharpe; break exact ties
  by ascending preregistered trial ID. This is a calibration-only selection rule,
  not a change to project candidate selection. Any other rule needs an explicit
  whole-procedure calibration and method identity.
- The null for this baseline is zero population mean in every difference-series
  column. This does not equate zero difference-series mean with zero paired
  delta-Sharpe. Alternatives and error claims must be registered separately.
- For the single-attempt case `N_cycle=N_lifetime=K=1`, propose `S0=0` with the
  same moment denominator `D`; do not evaluate inverse-normal terms at `N=1`
  or estimate cross-trial dispersion. Calibrate this branch separately.

The proposal combines sample Sharpe, population moments, and estimated
cross-trial dispersion. Independent reference calculations must check that
finite-sample combination; it is not asserted to be exact.

## Proposed unavailable outcomes

Return no numeric score for the following conditions. Record all applicable
reason codes in the fixed table order; do not discard an evaluated attempt.

| Condition | Proposed reason |
| --- | --- |
| Noninteger, negative, zero, or inconsistent counts; `K > N_cycle`; `N_cycle > N_lifetime` | `INVALID_COUNTS` |
| Missing, nonfinite, duplicated, irregular, or misaligned daily data | `INVALID_SERIES` |
| Any column has `T < 4` | `INSUFFICIENT_OBSERVATIONS` |
| Any column has nonpositive variance or undefined moments | `INVALID_MOMENTS` |
| Incomplete trial vectors, including `N_cycle > 1, K = 1` | `INCOMPLETE_HISTORY` |
| Prior-cycle attempts exist, even if current-cycle vectors are complete | `UNSUPPORTED_LIFETIME_HISTORY` |
| Known dependent, adaptive, heterogeneous, or otherwise unregistered design | `UNSUPPORTED_DESIGN` |
| `N > 1` and `V` is missing, nonfinite, or nonpositive | `DISPERSION_UNAVAILABLE` |
| `D <= 0`, nonfinite intermediate, invalid quantile, or overflow | `INVALID_ARITHMETIC` |

Check structural validity before arithmetic; dependent values need not be
evaluated after their prerequisites fail. No epsilon, clipping, absolute-value
repair, row deletion, imputation, replacement trial, or ESS-for-T substitution.
In particular, duplicated trials with zero dispersion do not imply no selection
bias. The `X` versus `-X` design is outside the baseline's independence support;
it must not collapse into a one-trial success.

Unsupported-design stress experiments may record the formula's raw output only
under an explicitly separate diagnostic field. Such output is not an available
method score and cannot enter acceptance or promotion as a valid supported case.

## Preregistration worksheet — all unresolved entries block execution

No value below is implicitly supplied by the 0.95 frozen score threshold.
An independent reviewer and human must resolve these entries before simulation.

| Required registration item | Current state / decision needed |
| --- | --- |
| Method identity, equations, counts, dispersion, selection, unavailable branches | Candidate above; accept or revise explicitly |
| Scientific claim at score 0.95 | OPEN: define precise null, event, and population |
| Supported domain | OPEN: exact sample sizes, trial counts, distributions, moments, dependence and selection rules |
| Error measure and tolerance | OPEN: name measure, target, and allowed deviation; do not infer 5% from 0.95 |
| Monte Carlo confidence procedure | OPEN: confidence level, bound calculation and simultaneous scenario control |
| Replication budget and stopping | OPEN: fixed counts by scenario, failures and rerun rules; no stopping when results look favorable |
| Development versus held-out scenarios | OPEN: disjoint scenario/seed manifests and custodian for held-out execution |
| RNG and deterministic computation | OPEN: generator/version, seed derivation, ordering, precision, reductions and threading |
| Environment and code | OPEN: exact runtime/dependency versions, OS/architecture and code hashes |
| Independent numerical references | OPEN: separately derived inputs, expected outputs, tolerances and reviewer |
| Registration authority | OPEN: human reviewer, record identity/hash, date and signature before execution |

An unresolved entry is not a default or permission to start. This worksheet is
not itself a completed preregistration. Revising a method after held-out results
requires a new identity and a new independent validation set; preserve failures.

## Scenario and reference coverage required in that registration

Carry forward all seven scenario groups in `DSR_CALIBRATION_PLAN.md`.
Distinguish supported calibration cells from unsupported-design challenge cells.
Include one trial, the 20-trial PBO boundary and the 81-trial family boundary;
daily sample sizes must be specified rather than replacing them with ESS 120.
Explicitly cover positive and negative serial dependence, 24/72/168-hour overlap,
identical/opposite/near-duplicate columns, unequal variances, heavy tails,
volatility clustering, ties, non-Sharpe selection, adaptation, missing attempts,
and lifetime counts larger than current-cycle counts.

Before Monte Carlo calibration, independent deterministic references should
cover each unavailable branch, the separately defined single-trial branch,
`S=S0` giving score 0.5 when otherwise valid, positive scale invariance, and
the distinction between paired delta-Sharpe and difference-series Sharpe.
These are requested reference properties, not results already demonstrated.
For independent standard normal trial statistics, compare the expected-maximum
approximation with independent high-accuracy integration or another accepted
oracle. Record approximation error, especially at small trial counts.

For each supported scenario, retain the distribution of scores, selected-null
threshold-crossing frequency over all attempted replications, its registered
confidence bounds, unavailable frequency/reasons, expected-maximum bias, and
power under registered alternatives. Also report valid-only frequencies with
their denominator; unavailable-heavy methods cannot pass by shrinking the set
of reported outcomes. Freeze the availability acceptance rule before results.

## Proposed evidence handoff and remaining boundary

A later calibration submission needs the signed registration, exact method and
scenario manifests, environment/code hashes, complete synthetic results,
independent references, independent rerun evidence, and a claim-by-claim review.
No confirmation or lockbox returns enter this preparation or calibration.

B1-B3 remain open: a literature candidate and explicit branches do not establish
calibration, practical support, or an accepted DSR gate. B4 (lockbox semantics)
and B5 (human-authored specification and implementation/hash migration) remain
unchanged. The conventional candidate may fail or prove too narrow; preserve
that result instead of changing acceptance criteria. Task 13 and promotion
remain blocked under the recorded project gate.

## Proposed arithmetic reference examples

These are author-prepared algebra examples for review, not independent accepted
reference vectors or calibration evidence. No random sampling is involved.
The return vectors below represent four aligned complete synthetic UTC days;
these vectors test arithmetic only and do not establish a supported stochastic
design. An independent reviewer must check them before accepting any oracle.

For the single-trial branch set `N_cycle=N_lifetime=K=1`, hence `S0=0`.

| Example | Daily difference returns | Exact expected intermediate values | Proposed score |
| --- | --- | --- | --- |
| R1: zero mean | `[-0.03,-0.01,0.01,0.03]` | mean `0`; sample variance `1/1500`; skew `0`; Pearson kurtosis `41/25`; `S=0`, `D=1` | `Phi(0)=0.5` |
| R2: positive mean | `[-0.02,0,0.02,0.04]` | mean `1/100`; sample variance `1/1500`; skew `0`; kurtosis `41/25`; `S=sqrt(3/20)`; `D=128/125` | `Phi(15/(16*sqrt(2)))`, approximately `0.746306736608969` |
| R3: positive rescaling | Multiply every R2 return by `2` | mean doubles; variance quadruples; `S`, skew, kurtosis and `D` unchanged | Same as R2 |

Derivation: R1 and centered R2 have population second moment `1/2000`
and population fourth moment `41/100000000`; their third moment is zero.
For R2, `D=1+(4/25)*(3/20)=128/125` and the squared CDF argument
is `(T-1)*S^2/D=225/512`. The displayed decimal is descriptive, not a frozen
numerical tolerance. The exact identities are the proposed review targets.

Boundary examples (no numeric score):

- R4: a constant four-day column has zero variance: `INVALID_MOMENTS`.
- R5: one usable R2 column with `N_cycle=N_lifetime=2,K=1`:
  `INCOMPLETE_HISTORY`; count both attempts and do not invent dispersion.
- R6: one usable R2 column with `N_cycle=K=1,N_lifetime=2`:
  `UNSUPPORTED_LIFETIME_HISTORY`; do not import prior-cycle vectors.
- R7: two identical R2 columns, counts all `2`, deliberately constructed as
  duplicates: `UNSUPPORTED_DESIGN` and `DISPERSION_UNAVAILABLE` in that order.
- R8: R2 and its negative, counts all `2`, deliberately paired:
  `UNSUPPORTED_DESIGN`; the squared-correlation effective count must not turn
  this into the single-trial branch. Their Sharpes are opposite and selecting
  their maximum gives `abs(S)`, illustrating the selection issue directly.

These examples cover only some branches. Multi-trial score oracles, selection
and tie cases, invalid timestamps/counts, unsupported moments, and numerical
failure controls remain outstanding; this appendix is not a complete test suite.
