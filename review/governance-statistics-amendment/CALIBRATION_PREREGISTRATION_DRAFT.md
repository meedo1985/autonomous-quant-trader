# DSR calibration preregistration draft

**Status:** HISTORICAL AI PROPOSAL — NOT EXECUTABLE OR APPROVED
**Prepared:** 2026-09-15
**Proposing model:** `gpt-6-astra`
**Simulation status:** not started

Reconciliation on 2026-09-18 found that this 148-cell qualification design is
incompatible with the narrow candidate in `DSR_METHOD_PREREGISTRATION_DRAFT.md`:
that candidate must return unavailable for several dependent and heterogeneous
cells that this draft requires to have at most 1% unavailability. Do not execute
this draft. See `DSR_CALIBRATION_RECONCILIATION.md`.

This draft makes the numerical choices in `DSR_CALIBRATION_PLAN.md` reviewable
before any simulation output exists. It preserves the frozen DSR score threshold
of 0.95 and permits the final conclusion that no proposed DSR method qualifies.

## B1-C01 — Primary error claim

For every preregistered primary scenario, the probability that any
current-family trial with population unannualized difference-series Sharpe at or
below zero receives an available DSR score at or above 0.95 must be at most 0.05.

For family replication `r`:

```text
I_r = 1 if any null trial j has available DSR_j >= 0.95; otherwise 0
```

The evaluated procedure includes count, dispersion, correlations, selection,
and nomination. If it scores only a nominated trial, calibration repeats the
complete procedure for every possible nominee and uses the union event.

This is a finite-scenario, one-terminal-family-snapshot claim. It is not a
posterior probability, not a claim about paired Sharpe improvement, and not a
guarantee across repeated looks, cycles, families, lifetime searches, or all
return distributions. Proposed error-rate slack is zero.

## B1-C02 — Primary scenario manifest

`T` is the number of daily observations and `N=K` is the number of complete
current-cycle trial vectors. The initial qualifying domain has one terminal
family snapshot, complete histories, no prior-cycle matrix pooling, and equal
current/lifetime counts.

| Block | Fixed grid | Cells |
| --- | --- | ---: |
| A: independent Gaussian | `T={120,365,730,1247}`, `N={1,2,20,81}` | 16 |
| B: cross-trial structure | `T={120,1247}`, `N={2,20,81}`, six structures | 36 |
| C: dependence/nonnormality | `T={120,1247}`, `N={2,81}`, two cross structures, seven processes | 56 |
| D: mixed true/false nulls | `T={120,1247}`, `N={20,81}`, two cross structures, two signal counts, two sizes | 32 |
| E: negative/composite nulls | `T={120,1247}`, `N={2,81}`, two mean patterns | 8 |

Total: **148 primary cells**. This sparse stress grid is not a full Cartesian
grid and provides no automatic interpolation to untested settings.

Block B uses: identical trials; exact and alternating opposite trials including
`X,-X`; common-factor correlation 0.50; near-duplicates at 0.99; alternating
signed factor loadings with squared magnitude 0.80 and residual variance 0.20;
and independent trials whose standard deviations cycle through 1, 2, and 4.

Block C crosses independent and 0.50 common-factor structures with: stationary
Gaussian AR(1) coefficients +0.50 and -0.50; standardized overlapping MA(3) and
MA(7); standardized independent Student `t_5`; analytically centered/scaled
`exp(N(0,1))`; and ARCH(1) with `h_t=0.5+0.5*x[t-1]^2`, deterministic initial
`h=1`, Gaussian innovations, and 10,000 discarded initialization steps.

Block D uses independent Gaussian and signed-common-factor Gaussian designs.
The first `1` or `floor(N/2)` trial IDs have scaled true difference-series Sharpe
0.50 or 1.00; every clearance among the remaining zero-mean trials is an error.

Block E uses independent Gaussian innovations with all trials at scaled true
Sharpe -0.50, or alternating trial IDs at 0 and -0.50.

## B1-C03 — Replications and acceptance

- Development: exactly **2,000 family replications per primary cell**.
- Held-out validation: exactly **50,000 per primary cell**.
- Total held-out primary workload: **7.4 million family replications**.

For `x` events among `R=50,000`, calculate the one-sided exact
Clopper-Pearson upper bound:

```text
U = BetaInverse(1-alpha_star; x+1, R-x)
alpha_star = 0.01 / 296
```

Use `U=1` when `x=R`. The 296 simultaneous bounds comprise an error bound and
an all-required-scores-unavailable bound for each primary cell. Bonferroni gives
at least 99% simultaneous Monte Carlo coverage.

Every primary cell must satisfy both:

- `U_error <= 0.05`;
- `U_unavailable <= 0.01`.

The proposed 1% unavailability tolerance is a method-applicability requirement,
not error-rate slack. Failed cells may only narrow a later method's declared
domain through a new preregistration; they cannot be removed retrospectively.

## B1-C04 — Deterministic seed separation

Use exact UTF-8 namespaces:

```text
aqt.dsr.calibration.development.v1.2026-09-15
aqt.dsr.calibration.validation.v1.2026-09-15
aqt.dsr.calibration.power.v1.2026-09-15
```

Derive each full seed digest from canonical compact JSON:

```text
[namespace, calibration_manifest_hash, method_spec_hash,
 scenario_id, replication_index, stream_purpose]
```

Use the complete SHA-256 digest. Freeze generator implementation, distribution
algorithms, runtime, initialization, and draw ordering before stochastic work.
Validation outputs remain ungenerated and unseen until the method, code,
manifest, and rules are fixed. A revised method gets a new identity, namespace,
and validation set; failed records are retained.

## B2-C01 — Boundary and unsupported-domain fixtures

Before Monte Carlo work, independently check `T={0,1,2,3,4,119,120}`;
`N={0,1,2,20,81}`; `K=0`, `K<N`, and impossible counts; duplicates and opposite
vectors; zero/missing dispersion; constant, malformed, and nonfinite inputs;
failed/aborted attempts; outcome-dependent missingness; and prior-cycle counts
without matrix pooling.

Adaptive search, repeated looks, incomplete histories, unequal current/lifetime
counts, and unsupported moments are outside the first qualifying domain. Their
fixtures must return unavailable/unsupported without deleting counted attempts.

## B1-C05 — Power reporting

Use **18 descriptive power cells**: `T={120,1247}`, `N={1,20,81}`, and all trials
at scaled true difference-series Sharpe `{0.25,0.50,1.00}` with independent
Gaussian innovations. Run exactly 10,000 replications per cell after method
freeze, plus report power from mixed-null Block D.

Report family and per-trial true clearance, null clearance, unavailable rate,
and descriptive 95% binomial intervals. These intervals are not simultaneous
acceptance bounds. No minimum power threshold is proposed; weak power is
published without relaxing false-clearance control.

## B5-C01 — Numerical agreement

- Use independent reference arithmetic at 80 decimal digits where tractable.
- Proposed ordinary finite-scalar envelope:
  `abs(error) <= 1e-12 + 1e-10*abs(reference)`.
- Require exact seed bytes, indices, identities, counts, unavailable reasons, and
  ordering.
- Compute binomial bounds with verified bracket width at most `1e-12` and use the
  conservative upper endpoint.
- Add no tolerance to 0.95 or 0.05. A reference enclosure that straddles a
  decision threshold remains unresolved.

The floating-point envelope itself requires numerical-analysis approval before
simulation and never permits variance floors or repair of undefined inputs.

## B1-C06 — Compute stages and stopping

1. Freeze the candidate method, generators, fixtures, and reference results.
2. Run 32 development replications per cell as the prefix of the final 2,000.
3. Complete 2,000 development replications per cell; revise only here.
4. Benchmark projected runtime and memory, then obtain compute-budget approval.
5. Complete exactly 50,000 held-out replications per cell in deterministic
   1,000-replication batches with reproducible checkpoints.
6. Complete the separate 180,000 power replications.

Do not stop early for success, append replications to rescue a bound, or pool
development and validation. Operational interruption is `INCOMPLETE`. A
predeclared impossibility stop may save work only when even zero future errors at
the fixed final denominator cannot pass; the cell is then failed/incomplete.

The frozen 2,000 inner bootstrap attempts, if used by a future method, are
separate from outer calibration replications and cannot be silently reduced.

## Decision required before simulation

A human/statistician must accept the error claim, 148-cell manifest, 50,000
held-out replications, 99% simultaneous confidence, 1% unavailability ceiling,
seed contract, numerical tolerance policy, domain exclusions, and compute budget.
This draft selects no DSR equation, authorizes no simulation, and resolves none
of B1-B5.
