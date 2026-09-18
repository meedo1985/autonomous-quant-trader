# DSR calibration reconciliation and unsigned decision record

**Date:** 2026-09-18
**Status:** AI recommendation only; human/statistician acceptance pending
**Simulation decision:** **NO-GO**
**Governed status:** DSR remains diagnostic-only; promotion remains blocked
**Owner decision:** **DEFER** the narrow baseline experiment (2026-09-18)

## Inputs reconciled

- `DSR_METHOD_PREREGISTRATION_DRAFT.md`: committed narrow conventional method
  candidate and arithmetic examples from the other terminal.
- `DSR_AGENT_REVIEW_ADDENDUM.md`: newer review status and unresolved SCI/SEN
  findings for that candidate.
- `CALIBRATION_PREREGISTRATION_DRAFT.md`: local numerical proposal with 148
  primary cells and 7.4 million held-out family replications.
- `DSR_CALIBRATION_PLAN.md`: governing proposal-level calibration requirements.

The method and numerical draft are complementary evidence but are not one
accepted preregistration. Commitment to Git does not grant scientific authority.

## Reconciliation findings

### DEC-01 — Supported domain conflict

The method candidate supports only complete, independent, homogeneous synthetic
difference-series trials with equal current, lifetime, and usable counts. It
returns unavailable for dependent, heterogeneous, adaptive, or incomplete
designs. The numerical draft treats many such designs as primary qualifying
cells and requires family unavailability at or below 1%. Executing both
contracts would guarantee failure by construction.

**Disposition:** retain the 148-cell draft as historical stress-design evidence;
do not execute it against the narrow candidate.

### DEC-02 — Error-event conflict

The method candidate selects the maximum difference-series Sharpe under an
all-zero-mean global null. The numerical draft uses the union of every null
trial's clearance under global and mixed/composite nulls, including
counterfactual nominations. These events are not interchangeable, even in a
complete all-null family; score-order equivalence has not been established.
Candidate-specific skewness and kurtosis change the DSR denominator, so the
maximum-Sharpe trial need not have the maximum DSR score.

**Disposition:** any future baseline registration must name one primary event.
Mixed/composite-null quantities remain secondary challenges unless a broader
method and selection procedure are specified first.

### DEC-03 — Unfinished contracts

Reason-code precedence, duplicate observation versus duplicate-vector semantics,
the joint benchmark/candidate generator, held-out custody, independent
multi-trial references, and actual runtime budget remain unresolved. Numerical
values do not supply those contracts.

**Disposition:** no calibration engine or stochastic run may start.

Decision mapping to the independent review: DEC-01 resolves original REC-03,
DEC-02 resolves original REC-04, and DEC-03 resolves original REC-05. Original
REC-01, REC-02, and REC-06 remain the authority/provenance constraints recorded
in the review result; no original finding ID is reassigned.

## Proposed narrow baseline record

This section is a review target, not an accepted registration.

- **Purpose:** arithmetic/reference experiment only. Success would not qualify a
  practical promotion method or close B1-B5.
- **Supported cells:** independent Gaussian `T={120,365,730,1247}` crossed with
  `N={1,2,20,81}`: 16 cells. Current count, lifetime count, and usable complete
  vectors all equal `N`.
- **Joint generator:** draw benchmark `b_t` independently from `N(0,1)` and each
  difference column `d_jt` independently from `N(0,1)` across `j,t`; define
  candidate `c_jt=b_t+d_jt`. The DSR input is reconstructed `c_jt-b_t=d_jt`.
  This proves independence of difference columns despite a shared benchmark;
  it does not model real trading returns.
- **Selection:** choose the greatest difference-series Sharpe, breaking exact
  ties by ascending preregistered trial ID.
- **Primary event:** among all attempted family replications, the selected trial
  receives an available score `>=0.95` under the all-zero-mean global null.
- **Availability event:** one or more of the `N` required trial scores is
  unavailable. Denominator is every attempted family replication.
- **Proposed qualification evidence:** 2,000 development and 50,000 held-out
  replications per supported cell; one-sided exact Clopper-Pearson upper bounds;
  simultaneous 99% Bonferroni coverage over 32 bounds (error plus availability
  for 16 cells); `U_error<=0.05` and proposed `U_unavailable<=0.01` in every cell.
- **Challenge cells:** dependence, opposite/duplicate trials, heterogeneous
  variance, serial dependence, heavy tails, mixed nulls, adaptive search,
  missing attempts, and lifetime/current-count mismatch are non-qualifying
  diagnostics expected to expose the candidate's limited support.

The proposed budgets and 1% availability ceiling require human/statistician and
compute-budget acceptance. No development or held-out samples have been drawn.

## Proposed result contract

Use one stable primary reason code: the first failed prerequisite in this order.
Later arithmetic is not evaluated after a prerequisite fails.

1. `INVALID_COUNTS`
2. `INVALID_SERIES`
3. `INSUFFICIENT_OBSERVATIONS`
4. `UNSUPPORTED_LIFETIME_HISTORY`
5. `INCOMPLETE_HISTORY`
6. `UNSUPPORTED_DESIGN`
7. `INVALID_MOMENTS`
8. `DISPERSION_UNAVAILABLE`
9. `INVALID_ARITHMETIC`

Duplicate observation keys or timestamps are `INVALID_SERIES`; repeated numeric
values at distinct valid timestamps are not duplicates. Constructed identical
trial vectors violate the narrow independence support and return
`UNSUPPORTED_DESIGN` before dispersion arithmetic. Calibration diagnostics may
record additional detected conditions separately, but they do not alter the
primary contract.

Reference and implementation must agree exactly on the `score>=0.95` decision.
Numerical closeness that changes the decision is unresolved. Deterministic
multi-trial, tie, combined-invalid, single-trial, and unavailable-branch
references must be independently completed before stochastic work.

## Compute and custody gate

If a human later accepts the narrow baseline experiment:

1. freeze method, generator, scenario, seed, environment, reference, and result
   contracts;
2. assign a held-out custodian and freeze separate development/validation seed
   namespaces;
3. approve only a 32-replication-per-cell development prefix;
4. benchmark runtime and memory from that prefix;
5. obtain explicit approval before completing development or generating any
   held-out sample.

No early success stop, appended rescue replications, discarded failure, or
development/validation pooling is allowed. Failed attempts and unavailable
outcomes remain in their fixed denominators.

## Human/statistician acceptance fields

```text
Decision: ACCEPT NARROW BASELINE / REVISE / REJECT / DEFER
Purpose acknowledged as reference-only: YES / NO
Primary event and denominator accepted: YES / NO
Supported 16-cell grid accepted: YES / NO
Error and availability bounds accepted: YES / NO
Budgets and compute pilot accepted: YES / NO
Reason-code contract accepted: YES / NO
Held-out custodian:
Independent numerical reviewer:
Owner/statistician name and signature:
Date/time UTC:
Commit:
```

The owner selected `DEFER` in the project conversation on 2026-09-18. The other
fields remain intentionally incomplete because no simulation is authorized.

Until every applicable field is completed through the required human process,
the decision is NO-GO. Do not implement a calibration engine, run simulations,
activate DSR, start a governed cycle, access confirmation/lockbox data, or open
promotion.

## Review provenance

The reconciliation was independently reviewed read-only by `gpt-6-astra` after
fetching GitHub commit `3e0244bb3b11c9a1b324b3142249e6a3abb4855a` and comparing
the committed and local proposals. It reported REC-01 through REC-06 and
recommended this unsigned record. The frozen 28-file inventory and hashes,
14 sidecars, Constitution self-hash, manifest bindings, and protocol bindings
passed; no protected path changed.
