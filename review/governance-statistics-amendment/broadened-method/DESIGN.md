# Broadened DSR method — design proposal (revision 3)

**Status:** `NON-BINDING AI DESIGN PROPOSAL — NOT AN AMENDMENT — NOT ACCEPTED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). Design work only, under the
owner's step-0 decision R19-1 ("work may go ahead on designing ... Each build
step still needs your separate go-ahead"). No code, no simulation, no
calibration run.
**Requested by:** the owner, "start the broadened method design" (2026-10-03),
after `../d18-proposal/OWNER_DECISION_D18.md` (O18-2).
**History:** revision 1 (`6481f28`): Sol `SOL_REVIEW_6481F28.md` UNSOUND as
written (SB1-1..SB1-9), Fable `FABLE_REVIEW_6481F28.md` SOUND WITH FIXES
(FB1-1..FB1-17); adjudication `ADJUDICATION_6481F28.md`. Revision 2
(`020c8d0`), focused check: Sol `SOL_REVIEW_020C8D0.md` NOT READY (SB2-1),
Fable `FABLE_REVIEW_020C8D0.md` READY (FB2-1..FB2-10). Revision 3 applies both
reviewers' proposed dispositions without a further check [AI default]; this
is weaker than a further check and is recorded as such.
**Drafting choices** are **AI defaults** (owner's standing instruction "let
agent do the answers all the time"), marked `[AI default]`. They are not owner
decisions. D-16, D-17 and the other B-rows of §5 are decided only by the
owner after two different-model reviews (R19-2).

## 1. What must be broadened, and why

The decided D-18 definition (`../d18-proposal/PROPOSAL.md` rev. 7, `9718fdc`)
nominates the top-Sharpe trial `J_f*` of each declared family and passes it
iff `z_f* = (S − S0)·sqrt(T−1)/sqrt(D) >= z_crit`, with `P_0(E_f) <= 0.025`
in every qualifying cell and the procedure no-result rate `U_proc <= 1%`.
D-18 O18-2 leaves "equation, count and dispersion" to this method.

The current candidate (`../v1.1-method-candidate/METHOD_CANDIDATE.md` §3)
cannot meet that:

| Defect | Evidence | Effect |
|---|---|---|
| `S0 = sqrt(V)·A(N)` is the expected maximum only for equally correlated Gaussian trials | Astra AS-1 (80 copies + 1 independent: ratio 0.546) | penalty can be half of what it should be under realistic clustering |
| Lifetime `N` with current `K` has no justification | AS-2; Fable FR4-13 | wrong penalty either way |
| Small `N`, `K = 1`, `V = 0`, duplicates, `K < N` | AS-3, P-7; DEC-02 classification (cited as `DSR_CALIBRATION_RECONCILIATION.md` lines 88–91, 113–115, inherited from D-18 O18-2; FB1-13 iii) | `UNAVAILABLE` in realistic cells, so the 1% target fails (FR3-2) |
| `D = 1 − gS + ((k−1)/4)S²` assumes independent daily returns | METHOD_CANDIDATE.md:91; strategy horizons up to 168 h (protocol line 109) | serial dependence makes `Var(S)` larger than `D/(T−1)`; `z` too large, by a strategy-dependent amount |
| Heavy tails | sample `g`, `k` noisy under fat tails | `D` unstable |

## 2. Proposed method: `aqt.dsr.bootstrap_max.candidate.v2`

**Idea:** estimate the null distribution of the family maximum from the
family's own return matrix, resampling days in blocks with one shared index
sequence for all trials, so dependence between trials and across days is
kept. This is the Reality Check construction (White 2000; Hansen 2005;
Romano and Wolf 2005), used only to supply `S0` and `D` inside the D-18
formula.

### 2.1 Inputs

- `X`: the `T × K` matrix of daily E-DIFF difference returns of the declared
  family `J_f` on the eligible confirmation window, `K = |J_f|`, one column per
  declared trial, one row per complete UTC day (IMPLEMENTATION_CONVENTIONS.md
  §"Daily observations and Sharpe"); identical day index for every column.
- `S_j = mean(X_j)/sd(X_j)` (unannualized, `sd` with `n − 1`).

### 2.2 One index sequence, two uses

- **Block length `L`.** Per column `j`, two Politis–White lengths: `L(u_j)`
  from the null influence `u_j` (standardised `X_j`), which targets the null
  mean behind `S0`, and `L(psi_j)` from the observed-law Sharpe influence
  `psi_j = u_j − (S_j/2)(u_j² − 1)`, which targets `D_j` and sees volatility
  clustering that `u_j` can miss (Sol SB2-1: a variance-regime series gave
  `L(u) = 1` but `L(psi) = 15.76`; Fable FB2-2). The column length is
  `L_j = max(L(u_j), L(psi_j))`. The family `L` combines the `K` column
  lengths by a rule fixed in the D-19 **development** phase from two
  preregistered candidates, **largest** or **median** (for even `K`, the mean
  of the two middle values; `bootstrap_indices` accepts a non-integer length),
  chosen as the candidate with the smaller worst-cell estimated `P_0(E_f)`
  over the development cells, ties to **largest**; then frozen before any
  held-out replication (SB1-3, SB1-9, FB2-4). The development cells must
  include a single dependent column among independent ones, where the median
  is anti-conservative (Fable FB2-4: AR(1) φ = 0.5 among two iid columns,
  `T = 365`, false pass 5.73% under the median vs 1.04% under the largest,
  first-order), and volatility-clustering (GARCH-type) columns. Neither is claimed conservative: a longer `L` biases the
  bootstrap variance **down** by order `L/T` (Fable FB1-1: at `T = 365`,
  `L = 58`, the iid variance ratio is 0.734, and a `K = 1` nominee passes
  about 4.6% instead of 2.5% at 1.96), while a shorter `L` misses dependence.
  Both candidates are calibrated heuristics, not theorems.
- **Cap and support.** The existing routine caps `L` at
  `min(T, ceil(min(3·sqrt(T), T/3)))` (`src/aqt/metrics/statistics.py:378`; FB1 cited 375).
  If the cap binds for any column (`clipping = "UPPER"`), the family is
  refused at the sample level (reason `BLOCK_LENGTH_CAPPED`, §2.5, a `U_proc`
  event). This is a sample check only; it does not detect every law outside
  the supported domain (§2.6). The realised `L/T` is reported and is a
  covariate of the D-19 cell classifier (FB1-1, FB1-4, FB2-6). Revision 1's
  `L > T/4` rule is deleted: it could never fire for `T >= 148` (FB1-4,
  SB1-3).
- **Replicates.** `B = 2000` (protocol line 226). Each replicate draws one
  stationary-bootstrap day-index sequence of length `T` and applies it to all
  columns of both `X` (uncentred) and `Y = X − column means` (recentred).

### 2.3 The quantities

For replicate `b` and column `j`:

- `S°_{b,j}` = Sharpe of the resampled **recentred** column (null);
- `S*_{b,j}` = Sharpe of the resampled **uncentred** column (observed law).

```text
S0  = mean_b( max_j S°_{b,j} )               # expected null maximum (null law)
D_j = (T − 1) · var_b( S*_{b,j} )            # every column, at its observed Sharpe
z_j = (S_j − S0) · sqrt(T − 1) / sqrt(D_j)   # every column; T − 1 cancels: z_j = (S_j − S0)/sd_b(S*_j)
z_f* = z_{J_f*}                              # D-18 formula, nominee per P18-4
```

- `S0` uses the recentred law: under the global null every trial has zero
  mean (rev. 1 §2.2 kept; FB2-10).
- `D_j` uses the **uncentred** law, so it is the sampling variance of the
  Sharpe at the observed Sharpe, as the decided `D` is
  (`METHOD_CANDIDATE.md:91`). The reason is fidelity to the decided formula
  and correct labelling. Sol's example (SB1-1: shifted negative-exponential
  returns, `S = 0.5`, moment scale 2.5 vs null scale 1, `z` inflated 1.58)
  has a nonzero true Sharpe, so it concerns power; under the global null the
  two scales share a limit and differ at order `T^{-1/2}` by a skew-dependent
  term whose effect on size is not derived (FB2-1, `UNVERIFIED`); D-19 must
  include positive- and negative-skew cells. Sharing one index sequence is
  coherent: on the same indices `S*_{b,j} = S°_{b,j} + mean(X_j)/sd(Y*_{b,j})`
  exactly (FB2 §2(a)).
- `D_j` and `z_j` are computed for **every** column, at no extra resampling
  cost, so availability (P18-3: "for each … finite positive `D` … finite
  pre-Φ `z`") does not depend on nomination (FB1-2).
- `var_b` uses `B − 1`. Means and variances are computed with `math.fsum`
  and the two-pass algorithm, in replicate index order; the recentred column
  means are zero up to rounding, not exactly (FB1-9).

### 2.4 Seeds and conventions

A **family seed** is fixed at declaration: SHA-256 of a canonical JSON
object (UTF-8, keys sorted, no whitespace, arrays in declared trial-id order)
with fields `protocol_hash`, `family_id`, `cycle_id`, `window_id`,
`data_manifest_hash` and `trials` (each `{trial_id, hypothesis_hash,
configuration_hash}`), extending the frozen per-trial rule
`SHA256(protocol_hash, hypothesis_hash, trial_index)` (protocol line 266).
The purpose token `"dsr_family_max_null"` enters **once**, as the stream's
`purpose` field, not inside the family seed; the stream's `asset` is BTC and
`cost_multiplier` 1 (the E-DIFF series). Replicate `b` draws from it by the
existing replicate-seed construction. Results must reproduce from the
recorded hashes and seeds or are void (Constitution §27 line 194). Seeds are
fixed before any data exists (P18-0, P18-1), so seed choice cannot be gamed
(FB2-7, SB2-2). The current
`ReplicateStream` accepts only `"paired_sharpe_ci"` and a per-trial seed
(`statistics.py` ~443–466; protocol line 266), so the build would extend the
conventions (IMPLEMENTATION_CONVENTIONS.md), the stream, and regenerate and
review reference vectors (I-10). (SB1-4, FB1-8)

### 2.5 Availability (reason codes, fail-closed, in order)

Checked before computation, **not** `U_proc` (FB1-7), in this order
(SB2-3):

1. Declaration validity, ids, hashes and counts (D-18 P18-1): an invalid
   declaration prevents the cycle from starting.
2. Window eligibility (D-18 P18-0), extended by `T >= T_min`, where `T_min`
   is chosen in the D-19 development phase and frozen (SB1-4). This adds a
   condition to the owner-decided P18-0 (FB2-8; §5 B-7).

Computed, in order; each makes the family `UNAVAILABLE` and is a `U_proc`
event (D-18 P18-7) unless its cause is infrastructure, which is `U_ops`
(P18-7 precedence; FB1-7):

1. `INVALID_SERIES`: a non-finite value, or a misaligned or missing day.
2. `ZERO_VARIANCE_COLUMN`: some `sd(X_j) = 0`.
3. `BLOCK_LENGTH_UNAVAILABLE`: the PW routine fails for some column, for
   `u_j` or `psi_j` (e.g. `NONPOSITIVE_LONG_RUN_VARIANCE` under negative
   autocorrelation).
4. `BLOCK_LENGTH_CAPPED`: the cap binds for some column (sample-level
   refusal). Rules 3–4 trigger on any column even under the median rule;
   this is fail-closed, and its availability cost grows with `K` (Fable FB2
   §2(c): per-column failure must stay below about 1.26e-4 at `K = 80` for a
   1% family rate). D-19 reports per-column cap and failure rates by `K`
   (FB2-5).
5. `INVALID_REPLICATE`: any replicate has a column with zero variance or a
   non-finite value, in either the recentred or uncentred matrix. Replicates
   are never dropped or replaced (IMPLEMENTATION_CONVENTIONS.md lines
   104–105). Checking one matrix suffices, since the recentred and uncentred
   replicates have identical variances (FB2-10). Sparse columns make this
   likely (Fable FB1-6: one 18-day active run in `T = 365`, `L >= 5`, fails
   almost surely). Sparse-column families are **challenge** cells, not
   qualifying [AI default; FB2-9]: the method is expected to refuse them, and
   that refusal is reported, not certified.
6. `INVALID_ARITHMETIC`: a non-finite `S0`, or any `D_j <= 0` or non-finite,
   or any non-finite `z_j`.

### 2.6 Supported domain

Stationary, short-memory daily difference returns, with **finite variance for
the null error claim** (`P_0`) and **finite fourth moment for power**, and the
cap not binding (SB1-2, FB2-3). Long memory, structural breaks or regime
changes, infinite-variance laws and sparse columns are **challenge** cells in
D-19, not qualifying cells. At the recentred null the Sharpe is a
self-normalised mean needing only finite variance, and the skew and kurtosis
terms in `D_j` vanish at order `T^{-1/2}` (heuristic;
`UNVERIFIED_EXTERNAL_ASSUMPTION`, FB1 Q1, FB2-3). **Residual, disclosed:** the
domain is a property of the unknown law and is checked only through the
sample cap, so long memory below the cap, breaks and infinite variance are
still scored without a calibration guarantee (FB2-6). A full support
classifier before D-19 (D-18 O18-2) is not supplied here; D-19 specifies it
(owner-visible, §5 B-7). High-dimensional validity
of the bootstrap maximum at `K = 80`, `T = 365` is unverified and is a
calibration question.

### 2.7 What this does in the hard cases (design claims, for calibration)

| Case | Current candidate | This method |
|---|---|---|
| 80 near-copies + 1 independent (AS-1) | `S0` about half the expected maximum | the resampled maximum follows the actual dependence; finite-sample shrinkage of order `L/T` remains (FB1-1) |
| exact duplicate columns | `UNSUPPORTED_DESIGN` | duplicates add nothing to the maximum; available |
| `K = 1` | separate `S0 = 0` branch (AS-3) | one branch for all `K` |
| `V = 0` | `DISPERSION_UNAVAILABLE` | `V` not used |
| lifetime `N` ≠ current `K` | `UNSUPPORTED_LIFETIME_HISTORY` | scope changed, not solved (§3; SB1 table) |
| autocorrelated returns | `D` too small | `D_j` includes it, within the supported domain |
| fat tails | noisy `g`, `k` | not used; finite fourth moment still needed for `D_j` |

Known non-monotonicity (FB1-15): declaring one extra long-memory column can
raise the family `L`, shrink the nominee's `D` and `S0`, and raise `z`. It is
a declaration-time lever; D-19 must include it, and the block rule chosen in
development must be checked against it.

## 3. D-16, D-17 and lifetime risk

- **D-16, proposed answer: no effective count.** The method never computes
  `N_eff`, a spectrum or `A(N)`. It replaces the frozen primary and fallback
  (protocol lines 232–233) **and** conflicts with Constitution §9 line 106
  ("If no frozen effective-count method exists, raw count is used"), so it
  needs a Constitution §4 amendment of §9, not only of the protocol (FB1-3).
- **D-17, proposed answer: the declared current-cycle family, implicitly.**
  `N_cycle` and `N_lifetime` are still recorded and reported with every
  result (Constitution §0 line 12 "current-cycle and lifetime trial
  accounting"; §5 line 67 and §9 line 104 "lifetime ... persists"; protocol
  line 190), but do not enter the score. Whether "persist" permits "recorded
  and reported only" is the owner's reading (FB1-3). This reverses his
  2026-10-03 choice (`../d16-d17-proposal/OWNER_CHOICE_CANDIDATE_COUNT.md`),
  as he asked to revisit.
- **What is claimed:** per eligible cycle, conditional on the declared set
  and the supported law (SB1-5). **Not claimed:** any lifetime error control,
  protection against declaration choices shaped by public prices (C2), or a
  score penalty for earlier searches.
- **Cross-cycle accumulation** (O18-3): with `m` eligible cycles each at 5%,
  the assumption-free bound is `min(1, 0.05m)` (50% at `m = 10`); the
  independence illustration `1 − 0.95^m` gives 9.75% at 2, 14.26% at 3,
  22.6% at 5, 40.13% at 10, and cycles are not exactly independent (shared
  regimes, re-declaration) (SB1-8, FB1-12). Removing the lifetime count from
  the score removes the only mechanism that raised the bar across cycles.
  Whether to report only, spend alpha across cycles, or cap the number of
  eligible cycles is the owner's (B-5 below).

## 4. Calibration consequences (inputs to the D-19 preregistration)

D-19 must be a complete preregistration, not a list of cells (SB1-9):
supported-law classifier and domination rule; location-shift null; `K/T`
boundary; long-memory and regime-change disposition (challenge); freeze order
(development replications choose the block rule, `T_min` and any margin;
then the whole qualification object is frozen; then held-out seeds); family
seed derivation; nested-bootstrap randomness; simultaneous confidence family;
outer replication budget; separate power and mixed-null reporting. The
inner 2000-replicate algorithm, including seeds, block selection and invalid
replicates, is rerun exactly inside every outer replication (SB1-7; B = 2000
gives about 1.6% relative error in `sqrt(D)`). Cells added by this method:
realised `L/T`, heterogeneous dependence across columns, sparse columns, the
`K` non-monotonicity lever, `D` for every column (FB1-16). Compute: one
replication is about 2000 × 80 × 365 ≈ 5.8e7 day-operations per family;
about 10⁴ outer replications per cell gives about 5.8e11 per cell, which
belongs in the D-19 compute plan (FB1-17). `z_crit` is fixed from
development replications and certified on held-out ones (D-18 P18-6); the
1.972 figure applies only to the old candidate.

## 5. Decisions for the owner (after two reviews)

| ID | Decision | Notes |
|---|---|---|
| B-1 | D-16: no effective count | needs a Constitution §9 amendment (line 106) |
| B-2 | D-17: declared set in the score; lifetime counts recorded and reported only | reverses his 2026-10-03 choice; his reading of "persist" (§5 l.67, §9 l.104) |
| B-3 | `D` defined by bootstrap (uncentred, every column; block length from both `u` and `psi`) | within D-18 because O18-2 left dispersion to this method (FB1-10, SB1-6); the numerical meaning of `D` changes. Rejected alternative: the null-scale `D` of rev. 1. The choice is for fidelity to the decided formula and labelling; its effect on size is settled by calibration (FB2-1) |
| B-4 | Alternative not proposed: a bootstrap p-value (`share of max_j S°_b >= S_nominee`) | changes D-18's comparator; it has the same `L/T` distortion, so it would not make calibration easy (FB1-14) |
| B-5 | Cross-cycle accumulation: report only [AI default], or alpha spending, or a cap on eligible cycles | an error-budget question, not a drafting choice (FB1-12) |
| B-7 | Changes to decided D-18 text: `T >= T_min` added to P18-0 (FB2-8); the support classifier deferred from the method (O18-2) to D-19 (FB2-6) | owner confirms or rejects |
| B-6 | `z` null distribution differs by cell (Fable FB1-11: `K = 1` 2.5% vs `K = 2` independent 1.156% at 1.96), so one global `z_crit` is set by the worst cell and costs power in large families; an alternative scale `D = (T−1)·var_b(max_j S°_b)` would change D-18's per-nominee `D` | question for the owner; [AI default] keep D-18's per-nominee `D` |

## 6. Reuse, cost and build scope (later, not now)

Reuses `block_length`, `bootstrap_indices`, the replicate-seed construction
and `type_seven_quantile` (`src/aqt/metrics/statistics.py`), extended per
§2.4. New code: one function computing `S0`, every `D_j`, every `z_j` from a
`T × K` matrix, plus the reason codes. Building needs the owner's separate
go-ahead and is §16-protected (promotion gate: different-model review and the
owner's PR review). Run-time cost is small; calibration cost is not (§4).

## 7. Amendment scope added to D-18 O18-7

Protocol lines 223–233 (bootstrap purpose, DSR method and fallback) and 266
(family seed); Constitution §27 line 194 (reproduction from recorded seeds);
Constitution §9 line 106 (and §5 line 67 / §9 line 104 if "persist" is read
as requiring the count in the score); IMPLEMENTATION_CONVENTIONS.md stream
purposes and family seeds.

## 8. Not changed

D-18 as decided; the E-DIFF estimand; the PBO, CI, plateau and lockbox
clauses (D-05, D-06, D-11, D-14, D-15 remain open); every frozen file.
Promotion stays blocked.

## 9. Next

A focused check by both model families (R19-2) was done for revision 2;
revision 3 applies their proposed dispositions without a further check
[AI default]. Next, the owner decides B-1..B-7.

**Update 2026-10-03:** decided; see `OWNER_DECISION_B.md` (B-5 is halving
alpha spending, not the report-only AI default in the table above).
