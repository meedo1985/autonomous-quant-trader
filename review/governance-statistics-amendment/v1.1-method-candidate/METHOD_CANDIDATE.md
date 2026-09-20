# Method candidate — paired Sharpe estimands, DSR, and PBO

**Status:** `NON-BINDING AI METHOD CANDIDATE — NOT AN AMENDMENT — NOT ACCEPTED — NOT ACTIVE`
**Companion to:** `README.md` (authority), `PREREGISTRATION_TEMPLATE.md` (fields),
`HUMAN_DECISION_MATRIX.md` (decisions `D-01`–`D-20`)
**Canonical consumer object:** rows 1–13 of
`review/governance-statistics-amendment/external-review-packet/STATISTICAL_BINDING_CANDIDATE.md` §5.
That table governs every row number used here.

Every item marked **PROPOSED** is a candidate for human decision. Every item
marked **BLOCKING** has no supporting evidence in this repository and is left as
an explicit placeholder rather than a value. No universal binding of
"paired delta-Sharpe" is proposed, asserted, or implied anywhere in this file.

## 1. Estimands (`D-01`)

Two separately named quantities, never interchangeable. Conventions are those of
`review/task12/IMPLEMENTATION_CONVENTIONS.md` §"Daily observations and Sharpe":
one observation is one complete UTC day of exactly 24 contiguous accepted
one-hour segments; `r_t = day_close_equity_t / day_open_equity_t - 1` computed
per leg **before** subtraction; zero risk-free rate; sample variance with
denominator `n - 1`; `A = sqrt(365)`; no repair of missing, duplicated,
irregular, non-finite, or misaligned days.

| Candidate identifier | Symbol | Formula | Required input | Output unit | Domain |
| --- | --- | --- | --- | --- | --- |
| `aqt.estimand.e_improv.candidate.v1_1` | `E-IMPROV` | `A*S(c) - A*S(b)` | **both** daily legs `c`, `b` | annualized-Sharpe | finite reals, any sign |
| `aqt.estimand.e_diff.candidate.v1_1` | `E-DIFF` | `A*S(c - b)` | difference series `d = c - b` only | annualized-Sharpe | finite reals, any sign |

`S(x) = mean(x)/sd(x)`, `sd` with denominator `n - 1`.

**Non-identifiability, both directions (cited, not recomputed).** `E-IMPROV` is
not a function of `d`, and `E-DIFF` is not a function of `(S(c), S(b))`
(`external-review-packet/TECHNICAL_APPENDIX.md` §2, §2.1). They disagree in sign
(§3) and reverse trial rankings (§4). Consequently a binding for one clause
never transfers to another clause by analogy.

**Versioning rule (PROPOSED).** Any change to the observation unit, the variance
denominator, `A`, the leg-compounding order, or the availability rules produces a
new identifier suffix. An identifier is never reused across semantics.

## 2. Proposed consumer bindings, row by row

Narrowest compatible choice means: the choice that adds no stored input, changes
no frozen threshold, and changes the fewest words of frozen text. It is a
proposal for decision, not a resolution.

| # | Queue | Consumer | Frozen source | Candidate | Basis for narrowness | Falsifier |
| ---: | :---: | --- | --- | --- | --- | --- |
| 1 | — | DSR input series | `protocol_v1.yaml:227–231` | `E-DIFF` — **CONFIRM ONLY** | Frozen text names the paired difference series; this is a confirmation, not a binding | Frozen text is shown to name a difference of two Sharpes |
| 2 | — | OOS/IS in-sample statistic | `protocol_v1.yaml:245–248` | `E-DIFF` — **CONFIRM ONLY** | Same; "Sharpe … on the paired-difference series" is explicit | As row 1 |
| 3 | I | ETH sanity gate | `42–44`, `279` | **PROPOSED** `E-IMPROV` (`D-02`) | Both legs exist at evaluation time, so the literal reading of "delta-Sharpe" as a delta of Sharpes is computable and adds no stored input; no frozen word changes | A showing that the clause's purpose ("directional consistency", line 44) is better served by the sign of the difference-series Sharpe |
| 4 | I | BTC 2x cost stress | `283`, `cost_model.stress_multipliers:150` | **PROPOSED** `E-IMPROV` (`D-02`) | Same clause family and same sign test as row 3; a split between rows 3 and 4 would make the ETH and BTC legs of one joint trial incomparable (`trial_accounting.trial_unit:178–180`) | Any evidence that rows 3 and 4 must differ |
| 5 | I | Paired CI, BTC CI lower bound | `274–275` | **PROPOSED** `E-IMPROV` (`D-03`) | The only existing estimator, inactive, already targets `E-IMPROV` (`src/aqt/metrics/statistics.py:208–233`), and its Politis–White block length is derived from the **improvement** influence process `z = psi_c - psi_b` (`IMPLEMENTATION_CONVENTIONS.md` §"Paired-Sharpe influence"). Binding `E-DIFF` here would discard that estimator and require a new block-length derivation — see `I-10` | A demonstration that the inactive estimator targets the wrong quantity for this clause |
| 6 | I | Parameter plateau | `263–265` | **PROPOSED** `E-IMPROV` (`D-04`), **plus BLOCKING `D-05`** | Consistency with rows 3–5 across the same grid. Separately, the `0.5 *` rule is not sign-invariant: for a negative selected value `v`, `0.5*v > v`, so the rule silently inverts into demanding neighbours *beat* the selected point (`TECHNICAL_APPENDIX.md` §3). That defect exists under **either** estimand and is not resolved here | A stated intended behaviour for `v <= 0` that makes the rule well-posed |
| 7 | I | Three-month fold wins | `280–282`, `202–204` | **PROPOSED** `E-IMPROV` per fold (`D-07`), **plus BLOCKING `D-06`** | Consistency with rows 3–6. The estimand is moot until fold anchoring, UTC completeness, and minimum days per fold are fixed (packet `README.md` §4.1 M5) | As rows 3–5 |
| 8 | II | PBO ranking metric | `237–240` | **PROPOSED** `E-DIFF` (`D-08`), **AMENDMENT-REQUIRED** | The stored matrix is a difference matrix and cannot yield `E-IMPROV` (`TECHNICAL_APPENDIX.md` §2). Reading line 240 as `E-DIFF` amends one clause's wording; ranking by `E-IMPROV` amends the stored input at `237–239`, changes the matrix schema, and — by Lemma L-1 below — reduces to ranking by the candidate's own Sharpe, contradicting the frozen justification at line 239 ("keeps PBO on the same incremental objective as DSR") | A showing that `E-IMPROV` ranking preserves the incremental objective, or that a joint-leg matrix is required for another reason |
| 9 | II | Lockbox prediction and pass rule | `83–86`, `90–91` | **BLOCKING `D-11`** — no statistic proposed | The clause resamples a difference series and then asks for a delta of Sharpes; those are incompatible as written (Astra `B4`). Any repair fixes at least seven separate things (§6.3), each a distinct decision | — |
| 10 | II | Lockbox coarse attestation sign | `77–78` | **BLOCKING `D-12`**, dependent on `D-11` | A sign taken from a different statistic is not a substitute (`TECHNICAL_APPENDIX.md` §3) | — |
| 11 | III | CPCV diagnostic paths | `215–222` | **PROPOSED** (`D-13`): report **both** `E-IMPROV` and `E-DIFF` per path, separately labelled | `role: diagnostic_only` with "no independent promotion gate" (line 220–221). Dual labelled reporting is strictly narrower than choosing one, because it binds nothing and gates nothing | A requirement that the CPCV report feed a gate, which would forbid dual reporting |
| 12 | III | Random-exposure null | `134–140`, `289` | **PROPOSED** `E-IMPROV` per draw (both legs exist per draw); pass event **PROPOSED** in §6.2 (`D-14`); **AMENDMENT-REQUIRED** | The null construction matches exposure and turnover on BTC and evaluates "paired delta-Sharpe versus VOL_TARGET_BUY_AND_HOLD" (line 137), so both legs are generated by construction; but no clause states the pass event, so the event text must be added | A clause already fixing the percentile event |
| 13 | III | Feature / execution delay hard gates | `284–285`, `267–268` | **BLOCKING `D-15`** — no statistic proposed | The clauses are mandatory booleans naming no statistic. Inventing one would author governance | — |

Counts, for audit against the canonical object: `2 confirm-only + 5 Queue I +
3 Queue II + 3 Queue III = 13`.

**Lemma L-1 (exact).** Within any fixed evaluation window with a single shared
benchmark leg `b`, `E-IMPROV_j = A*S(c_j) - A*S(b)` differs from `A*S(c_j)` by
the constant `A*S(b)`, so ranking trials by `E-IMPROV` is identical to ranking
them by the candidate's own Sharpe. `E-DIFF_j = A*S(c_j - b)` has no such
reduction. Verified against `TECHNICAL_APPENDIX.md` §4: there
`S(c_1) = 4.5*sqrt(3) > S(c_2) = (13/62)*sqrt(3)` and
`E-IMPROV_1 > E-IMPROV_2`, in the same order, while the `E-DIFF` order is the
reverse. **L-1 is a ranking fact only.** It must never be used to substitute
`A*S(c)` for any gate statistic (`I-12`).

## 3. DSR candidate

**Identifier (PROPOSED):** `aqt.dsr.candidate.v1_1`. It is a *successor
candidate* to `aqt.dsr.iid_raw_count.proposal.v1`
(`DSR_METHOD_PREREGISTRATION_DRAFT.md`), not a replacement of it and not an
active method. DSR remains diagnostic-only and the `dsr_minimum: 0.95` gate
remains unsatisfied under the owner decision of 2026-09-18
(`OWNER_DSR_DEFER_DECISION.md`).

### 3.1 Equation (unchanged literature baseline, cited not re-derived)

```text
A(N) = (1 - gamma) * Phi^-1(1 - 1/N) + gamma * Phi^-1(1 - 1/(N*e))     [N > 1]
S0   = sqrt(V) * A(N)
D    = 1 - g*S + ((k - 1)/4) * S^2
DSR  = Phi( (S - S0) * sqrt(T - 1) / sqrt(D) )
```

Bailey and López de Prado (2014), eqs. 1–2, as recorded in
`DSR_METHOD_PREREGISTRATION_DRAFT.md`. `S` is the **unannualized daily** Sharpe
of one difference column (row 1 binding); `g = mu_3/mu_2^1.5`;
`k = mu_4/mu_2^2` with `mu_r = sum((x - mean)^r)/T`;
`V = sum((S_j - mean(S))^2)/(K - 1)`; `gamma` is Euler–Mascheroni. Output is
dimensionless in `[0,1]`. No claim is made that `0.95` controls any family error
rate: that is `D-19`, deferred.

### 3.2 Trial-count event definition (PROPOSED, supportable)

`aqt.trialcount.event.v1_1` — an **attempt** begins at the durable
`EVALUATION_STARTED` record, immediately before evaluation-data access or
computation. Attempts include failures, evaluated aborts, and actual reruns;
event redelivery is idempotent and adds no attempt; each actual new attempt
receives a new identifier. BTC and ETH are one joint attempt
(`protocol_v1.yaml:178–180`). Three counts are recorded separately and never
merged: `N_cycle` (current-cycle attempts), `N_lifetime` (lifetime attempts,
which persist across cycles), `K` (usable complete current-cycle difference
vectors). Prior-cycle return matrices are never pooled
(`RESEARCH_CONSTITUTION.md` §5, line 67). Supported by frozen text plus
`DRAFT_AMENDMENT_PROPOSAL.md` lines 139–144; the definition is stated here only
so that the decisions below have a fixed referent.

### 3.3 Effective-trial-count construction — **BLOCKING**

Three mutually distinct constructs are currently in play, and the repository
does not adjudicate them:

| Construct | Source | Authority |
| --- | --- | --- |
| Eigenvalue effective number from the trial-return correlation matrix | `protocol_v1.yaml:232` | **Frozen primary method** |
| `raw_trial_count` | `protocol_v1.yaml:233` | **Frozen fallback**; the protocol states **no trigger condition**, and the only frozen trigger text is Constitution §9 line 106 (see `F-1`) |
| `N_eff = N^2 / sum(R_ij^2)` | `DRAFT_AMENDMENT_PROPOSAL.md:101` | Unaccepted AI candidate, explicitly warned against |

Three findings follow, and each is a decision rather than a value here:

- **F-1 (`D-16`).** The existing DSR candidate is named `iid_raw_count` and uses
  the raw count. That is the frozen **fallback**, adopted without the frozen
  **primary** method ever being evaluated and without any stated fallback
  trigger. The protocol defines no trigger. The only frozen trigger text is
  `RESEARCH_CONSTITUTION.md` §9, line 106 — "If no frozen effective-count
  method exists, raw count is used" — and whether the method *named but not
  defined* at `protocol_v1.yaml:232` counts as an existing frozen method is
  itself undecided, so the trigger remains part of `D-16` rather than a settled
  fact in either direction.
- **F-2 (`D-16`).** The eigenvalue effective number and the participation-ratio
  expression `N^2 / sum(R_ij^2)` are different functions of the correlation
  matrix and are not interchangeable. Neither is validated for maxima: perfectly
  opposite trials collapse to one effective trial while selection over their
  maximum still biases (Astra `B1`).
- **F-3 (`D-17`).** Which count enters `A(N)` — `N_cycle`, `N_lifetime`, or `K`
  — is **not** determined by any source read. `A` is monotone in `N`, so the
  choice moves `S0` and therefore every score. No value is supplied here.

`<<UNRESOLVED: D-16, D-17 — effective trial count method, fallback trigger, and
the count entering A(N). No default is implied by dsr_minimum: 0.95.>>`

### 3.4 Selection and error event — **BLOCKING**

`DEC-02` (`DSR_CALIBRATION_RECONCILIATION.md`) records that "the selected trial
clears 0.95" and "some null trial clears 0.95" are different events, and
`TECHNICAL_APPENDIX.md` §5 shows by exact arithmetic that the
maximum-difference-Sharpe trial need not be the maximum-DSR trial. One primary
event must be named before any score is interpretable.
`<<UNRESOLVED: D-18 — primary selection rule, primary error event, denominator.>>`

### 3.5 Finite-sample and availability branches

Carried forward unchanged from `DSR_METHOD_PREREGISTRATION_DRAFT.md` (reason
codes and their precedence order 1–9 in `DSR_CALIBRATION_RECONCILIATION.md`
"Proposed result contract"): `INVALID_COUNTS`, `INVALID_SERIES`,
`INSUFFICIENT_OBSERVATIONS`, `UNSUPPORTED_LIFETIME_HISTORY`,
`INCOMPLETE_HISTORY`, `UNSUPPORTED_DESIGN`, `INVALID_MOMENTS`,
`DISPERSION_UNAVAILABLE`, `INVALID_ARITHMETIC`. Structural validity is checked
before arithmetic; no epsilon, clipping, imputation, row deletion, replacement
trial, or ESS-for-`T` substitution. The single-attempt branch
(`N_cycle = N_lifetime = K = 1`, `S0 = 0`) remains separately calibrated.
This candidate proposes **no change** to any of it.

## 4. PBO candidate

**Identifier (PROPOSED):** `aqt.pbo.candidate.v1_1`. Output `phi`,
dimensionless, domain `[0,1]`, gated at `<= 0.30`, activated only at
`>= 20` current-family evaluated trials (`protocol_v1.yaml:234–241`).

### 4.1 Construction

1. **Observation unit (PROPOSED).** `aqt.pbo.obs.v1_1` = one complete UTC day,
   identical to every other Sharpe-bearing statistic in the project. The frozen
   clause names a return matrix without a frequency (`237–239`); daily is the
   narrowest choice consistent with the ranking metric being a Sharpe.
   *Falsifier:* a frozen or owner-accepted statement setting a different matrix
   frequency.
2. **Blocks.** 16 chronological balanced blocks over the shared day index;
   remainder observations are placed in the earliest blocks.
3. **Splits.** All `C(16,8) = 12,870` oriented in-sample selections. Exactly
   `12,870 = 2 * 6,435`: each of the 6,435 unordered half-partitions is used
   twice, once in each orientation (IS/OOS then OOS/IS). Both orientations are
   required; using 6,435 would halve the sample and bias `phi`.
4. **Ranking metric.** `E-DIFF` per trial per half — **PROPOSED**, and
   **amendment-required** (row 8).
5. **Per split.** Select the IS-best trial by the ranking metric; compute
   ascending OOS midranks over all `N` trials; `omega = rank/(N + 1)`; score the
   split `1` if `logit(omega) < 0`, `0` if `> 0`, `0.5` if `= 0`.
6. **Scalar.** `phi` = arithmetic mean of the 12,870 split scores. No weighting,
   no trimming.

**Exact check (new, hand-verifiable).** With `N = 2` and no ties, the IS-best
trial lands at OOS rank 1 or 2, giving `omega in {1/3, 2/3}` and
`logit(omega) in {-ln 2, +ln 2}`, so the split scores are exactly `1` and `0`.
With an exact two-way OOS tie, both midranks are `1.5`, `omega = 0.5`,
`logit(0.5) = 0`, and the split scores exactly `0.5`. The `0.5` branch is
therefore reachable and is not dead code.

### 4.2 Ties, missing trials, alignment

- **IS ties (PROPOSED, `D-10`).** On an exact tie for IS-best, average the split
  score uniformly over the tied trials rather than breaking the tie by identifier
  (`DRAFT_AMENDMENT_PROPOSAL.md:129`). Rationale: identifier order is an
  arbitrary artefact of registration and would let trial naming move `phi`.
  Recorded as a decision because an alternative — ascending preregistered trial
  ID, matching the DSR draft's tie rule — is defensible and would make the two
  procedures consistent with each other instead.
- **OOS ties.** Midranks, as in step 5. No randomization.
- **Missing or invalid trial, split, or observation.** `phi` is **unavailable**,
  with a reason code. Never omit a trial, never impute, never change the
  denominator, never substitute a shorter matrix.
- **Alignment.** Every trial column must cover the identical ordered day index
  with the identical benchmark, symbol, and cost multiplier. A single
  misaligned, duplicated, or non-finite day makes the whole matrix unavailable.
- **Minimum block length — BLOCKING.** A Sharpe must exist in each half for each
  trial. `<<UNRESOLVED: D-09 — minimum observations per block and the behaviour
  when a block is shorter than that minimum.>>`

## 5. CPCV, ESS, and bootstrap interaction

- **ESS is not a paired statistic.** `validation.effective_decisions`
  (`242–244`) is a Newey–West ESS on **BTC OOS strategy returns**, not on any
  paired or difference series. No estimand binding changes it. It gates CPCV
  activation at `>= 250` (line 216) and promotion at `>= 120` (line 290). Units:
  days. Domain: `[1, n]`, per `IMPLEMENTATION_CONVENTIONS.md` §"Newey-West ESS".
  The documented fallback `n/h` applies only to otherwise-valid zero variance or
  non-positive `Omega`.
- **ESS must never substitute for `T`.** The DSR `T` and the PBO matrix length
  are counts of actual daily observations. Substituting ESS is forbidden
  (`DSR_METHOD_PREREGISTRATION_DRAFT.md`, "no … ESS-for-T substitution").
- **CPCV consumes, never gates.** 8 groups, 2 test groups, purge and embargo,
  `role: diagnostic_only` (`215–222`). Under row 11 it reports both estimands
  per path. Its median and 5th-percentile path summaries are descriptive and
  enter no gate.
- **Bootstrap is estimand-coupled (`I-10`).** The Task 12 stationary bootstrap
  fixes block length from the **improvement** influence process
  `z = psi_c - psi_b` with `psi = u - (S/2)*(u^2 - 1)`, requires `n >= 16`, and
  binds the stream identity to purpose `"paired_sharpe_ci"` with output length
  equal to source length and exactly 2,000 attempts
  (`IMPLEMENTATION_CONVENTIONS.md` §§"Paired-Sharpe influence", "RNG,
  resampling, and interval"). Therefore: binding any bootstrap-backed clause to
  `E-DIFF` changes the influence process, hence the Politis–White block length,
  hence every resample and every interval endpoint. That is Astra `B5` — it
  requires a reviewed migration and refreshed deterministic reference vectors,
  and it cannot be done silently (`D-20`).
- **Two bootstraps, not one.** Row 5 (confirmation CI, `n -> n`) and row 9
  (lockbox prediction, `n -> m`) are different procedures. The existing stream
  cannot serve row 9: its purpose token and its `output_length = n` are both
  fixed.

## 6. Failure behaviour, domains, and open constructions

### 6.1 Fail-closed contract

An unavailable mandatory statistic yields `INDETERMINATE` or `BLOCKED`, never
`PASS` (`I-7`). `NO_EDGE_FOUND` and `KEEP_BLOCKED` are valid scientific
outcomes. Every unavailable result carries a reason code; no statistic is
repaired, floored, clipped, rounded, or back-filled. Fewer than two
observations, zero variance, or non-finite arithmetic is unavailable, not zero.

### 6.2 Random-exposure null pass event (PROPOSED, row 12)

Draw the 500 null samples specified at line 139, matching candidate mean
exposure and turnover on BTC. Compute `E-IMPROV` for each draw against
`VOL_TARGET_BUY_AND_HOLD`. The candidate passes iff its realized `E-IMPROV`
is `>=` the `0.95` quantile of the 500 null values, using the same linear
(type-7) quantile convention already fixed for the paired interval
(`IMPLEMENTATION_CONVENTIONS.md` §"RNG, resampling, and interval"). Any
unavailable null draw makes the gate unavailable; the denominator stays 500.
This is **amendment-required**: the frozen text supplies the metric name and the
`0.95` threshold but no pass event, so adding the event changes frozen text.
*Falsifier:* a frozen clause that already states the event.

### 6.3 Lockbox — the seven things a repair must fix (no candidate offered)

Listed so the decision is scoped, not resolved: (1) source representation —
difference series or joint legs; (2) joint-leg resampling with one shared index
sequence; (3) target length `m` versus source length `n`, and whether `m` is a
decision count, an hourly-bar count, a trade count, or a complete-day count
(`83–86` says decision count; every Sharpe convention in the project says
complete days); (4) the prediction statistic itself; (5) prediction-quantile
semantics for the one-sided lower 5th percentile (`87–89`); (6) the information
boundary and stream identity; (7) the pass rule at `90–91`, which additionally
requires `BTC delta-Sharpe > 0` from the same undefined statistic.
`<<UNRESOLVED: D-11 — all seven. No partial binding is proposed, because fixing
any subset changes the meaning of the rest.>>`

## 7. Invariants any accepted method must preserve

`I-1` … `I-9` are carried forward verbatim in substance from
`external-review-packet/STATISTICAL_BINDING_CANDIDATE.md` §6 and are not
restated here. **Label mapping:** that source presents its invariants as an
unlabelled numbered list; `I-n` here denotes item `n` of that list, in its
order. The identifiers are introduced by this file and do not appear in the
source, so a reviewer should read `I-7` as "§6 item 7". This candidate adds
three:

- **`I-10`.** Changing the estimand of any bootstrap-backed clause changes the
  influence process, the block length, and every resample. Deterministic
  reference vectors must be regenerated and independently reviewed in the same
  change (Astra `B5`).
- **`I-11`.** No single estimand is bound across rows 3–13. A per-row candidate
  is a per-row proposal; citing one row's candidate as precedent for another is
  invalid.
- **`I-12`.** Lemma `L-1` is a statement about *rankings only*. `A*S(c)` is
  never a substitute for any gate statistic, sign test, interval, or attestation
  field.

## 8. Traceability

| Section here | Source | Location |
| --- | --- | --- |
| §1 conventions, units | `review/task12/IMPLEMENTATION_CONVENTIONS.md` | §"Daily observations and Sharpe", lines 9–23 |
| §1 non-identifiability | `.../external-review-packet/TECHNICAL_APPENDIX.md` | §2, §2.1, §3, §4 (lines 49–178) |
| §1 code identity | `src/aqt/metrics/statistics.py` | `PairedSharpeStatistics`, lines 208–233 |
| §2 canonical rows 1–13 | `.../external-review-packet/STATISTICAL_BINDING_CANDIDATE.md` | §5, lines 96–148 |
| §2 rows 1–2 | `protocols/protocol_v1.yaml` | 227–231, 245–248 |
| §2 rows 3–7 | `protocols/protocol_v1.yaml` | 42–44, 263–265, 274–275, 279–283, 202–204 |
| §2 rows 8–10 | `protocols/protocol_v1.yaml` | 77–78, 83–86, 90–91, 237–240 |
| §2 rows 11–13 | `protocols/protocol_v1.yaml` | 134–140, 215–222, 267–268, 284–285, 289 |
| §3.1 equation | `.../DSR_METHOD_PREREGISTRATION_DRAFT.md` | "Candidate equation for review", lines 19–38 |
| §3.2 trial counts | `protocols/protocol_v1.yaml` 177–190; `docs/RESEARCH_CONSTITUTION.md` §5 line 67; `.../DRAFT_AMENDMENT_PROPOSAL.md` 139–144 | as listed |
| §3.3 effective count | `protocols/protocol_v1.yaml` 232–233; `docs/RESEARCH_CONSTITUTION.md` §9 line 106; `.../DRAFT_AMENDMENT_PROPOSAL.md` 101–104; `.../ASTRA_REVIEW.md` B1 | as listed |
| §3.4 event | `.../DSR_CALIBRATION_RECONCILIATION.md` DEC-02, lines 37–48; `TECHNICAL_APPENDIX.md` §5 | as listed |
| §3.5 reason codes | `.../DSR_CALIBRATION_RECONCILIATION.md` "Proposed result contract", lines 97–116 | as listed |
| §4 PBO construction | `protocols/protocol_v1.yaml` 234–241; `.../DRAFT_AMENDMENT_PROPOSAL.md` 123–133 | as listed |
| §5 ESS, bootstrap | `protocols/protocol_v1.yaml` 216, 223–226, 242–244, 290; `IMPLEMENTATION_CONVENTIONS.md` §§"Newey-West ESS", "Paired-Sharpe influence", "RNG, resampling, and interval" | as listed |
| §5 migration | `.../ASTRA_REVIEW.md` B5, lines 26–29 | as listed |
| §6.3 lockbox | `protocols/protocol_v1.yaml` 83–91; `.../ASTRA_REVIEW.md` B4; `TECHNICAL_APPENDIX.md` §7 | as listed |
| §7 invariants | `.../external-review-packet/STATISTICAL_BINDING_CANDIDATE.md` §6, lines 150–173 | as listed |
| Governance authority | `docs/RESEARCH_CONSTITUTION.md` | §4 lines 47–56, §5 lines 58–67, §16 |
| Owner decisions | `.../OWNER_DECISION.md`, `.../OWNER_DSR_DEFER_DECISION.md` | 2026-09-15, 2026-09-18 |
| Reviewer role limits | `.agents/skills/statistical-binding-review/SKILL.md` | "Output contract", lines 92–108 |

Line numbers are as read at the repository HEAD recorded in `README.md` §5 and
are provided for navigation, not as a hash-equivalent binding.
