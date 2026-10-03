# Broadened DSR method — design proposal (revision 1)

**Status:** `NON-BINDING AI DESIGN PROPOSAL — NOT AN AMENDMENT — NOT ACCEPTED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). Design work only, under the
owner's step-0 decision R19-1 ("work may go ahead on designing ... Each build
step still needs your separate go-ahead"). No code, no simulation, no
calibration run.
**Requested by:** the owner, "start the broadened method design" (2026-10-03),
after `../d18-proposal/OWNER_DECISION_D18.md` (O18-2: "Broaden the method").
**Drafting choices:** made by the author as **AI defaults**, per the owner's
standing instruction "let agent do the answers all the time"; each is marked
`[AI default]`. They are not owner decisions. D-16 and D-17 are decided only
by the owner, after two different-model reviews (R19-2).

## 1. What must be broadened, and why

The decided D-18 definition (`../d18-proposal/PROPOSAL.md` rev. 7, `9718fdc`)
nominates the top-Sharpe trial `J_f*` of each declared family and passes it
iff `z_f* = (S − S0)·sqrt(T−1)/sqrt(D) >= z_crit`, with `P_0(E_f) <= 0.025`
in every qualifying cell and the procedure no-result rate `U_proc <= 1%`.

The current candidate (`../v1.1-method-candidate/METHOD_CANDIDATE.md` §3)
cannot meet that:

| Defect | Evidence | Effect |
|---|---|---|
| `S0 = sqrt(V)·A(N)` is the expected maximum only for equally correlated Gaussian trials | Astra AS-1 (80 copies + 1 independent: ratio 0.546) | penalty can be half of what it should be under realistic clustering |
| Lifetime `N` with current `K` has no justification | AS-2; Fable FR4-13 (under P18-0 the lifetime count adds no per-cycle control, only cost) | wrong penalty either way |
| Small `N`, `K = 1`, `V = 0`, duplicates, `K < N` | AS-3, P-7, DEC-02 lines 88–91, 113–115 | `UNAVAILABLE` in the realistic cells, so the 1% no-result target fails (FR3-2) |
| `D = 1 − gS + ((k−1)/4)S²` assumes independent daily returns | METHOD_CANDIDATE.md:91; strategies hold positions up to 168 h (protocol line 207) | serial dependence makes `Var(S)` larger than `D/(T−1)`, so `z` is too large and false passes rise; the size of the error differs by strategy |
| Heavy tails | sample `g`, `k` are noisy under fat tails | `D` is unstable |

## 2. Proposed method: `aqt.dsr.bootstrap_max.candidate.v2`

One idea fixes all five rows: **estimate the null distribution of the family
maximum directly from the family's own return matrix, with a resampling
scheme that keeps the dependence between trials and across days.** This is
the Reality Check construction (White 2000; Hansen 2005; Romano and Wolf
2005), used here only to supply `S0` and `D` inside the D-18 formula.

### 2.1 Inputs

- `X`: the `T × K` matrix of daily E-DIFF difference returns of the declared
  family `J_f` on the eligible confirmation window, `K = |J_f|`, one column per
  declared trial, one row per complete UTC day (IMPLEMENTATION_CONVENTIONS.md
  §"Daily observations and Sharpe"). Every column covers the identical day
  index. Available only on `A_f` (D-18 P18-3).
- `S_j = mean(X_j)/sd(X_j)` (unannualized, `sd` with `n − 1`), and the
  nominee `J_f* = argmax(S_j, −id_j)` (D-18 P18-4).

### 2.2 Null recentring

`Y_j = X_j − mean(X_j)` for every column. Each recentred column has sample
mean exactly zero, so every trial is null by construction while its variance,
tails, serial dependence and correlation with every other column are kept.

### 2.3 Joint stationary block bootstrap

- Block length `L` [AI default]: the **largest** Politis–White length over the
  `K` columns, each computed from that column's Sharpe influence process
  `psi = u − (S/2)(u² − 1)` with the existing `block_length` routine
  (`src/aqt/metrics/statistics.py:368`; IMPLEMENTATION_CONVENTIONS.md
  §"Paired-Sharpe influence and PPW block length"). The largest is the
  conservative choice: longer blocks keep more dependence.
- `B = 2000` replicates (frozen `validation.bootstrap.iterations`, protocol
  line 226). Each replicate draws **one** stationary-bootstrap day-index
  sequence of length `T` (existing `bootstrap_indices`, line 535) and applies
  it to **all** columns at once, so cross-trial correlation and duplicate
  columns are preserved exactly.
- Seeds: the existing deterministic replicate stream (`replicate_seed`,
  line 518) with a new purpose token `"dsr_family_max_null"`, so no stream is
  shared with the paired interval (METHOD_CANDIDATE.md §5, I-10).

### 2.4 The two quantities

For replicate `b`, compute `S*_{b,j}` on the resampled recentred columns and
`M*_b = max_j S*_{b,j}`. Then:

```text
S0 = mean_b( M*_b )                                   # expected null maximum
D  = (T − 1) · var_b( S*_{b,J_f*} )                   # nominee's Sharpe variance
z_f* = (S_{J_f*} − S0) · sqrt(T − 1) / sqrt(D)        # D-18 formula, unchanged
```

`var_b` uses denominator `B − 1`. With `D` defined this way,
`sqrt(D/(T−1))` is the bootstrap standard error of the nominee's Sharpe, which
includes serial dependence and fat tails; the D-18 formula is kept literally,
and only the meaning of `D` changes (see §4, B-3).

### 2.5 What this does in the hard cases

| Case | Current candidate | This method |
|---|---|---|
| 80 near-copies + 1 independent (AS-1) | `S0` about half the true expected maximum | the resampled maximum is the maximum of the two distinct behaviours; `S0` tracks it |
| exact duplicate columns | `UNSUPPORTED_DESIGN` | duplicates add nothing to `M*`; available |
| `K = 1` | `S0 = 0` special branch, separately calibrated (AS-3) | `S0 = mean_b S*_b` ≈ 0; one branch for all `K` |
| `V = 0` | `DISPERSION_UNAVAILABLE` | `V` is not used |
| lifetime `N` ≠ current `K` | `UNSUPPORTED_LIFETIME_HISTORY` | the score uses only the declared set; see §3 |
| autocorrelated returns | `D` too small | bootstrap SE includes it |
| fat tails | noisy `g`, `k` | not used |

These are design claims. Whether the method meets `P_0(E_f) <= 0.025` and
`U_proc <= 1%` in every qualifying cell is for the D-19 calibration, not this
document.

### 2.6 Availability (reason codes, fail-closed)

In order, each making the family `UNAVAILABLE` with the code
(METHOD_CANDIDATE.md §6.1 contract kept):

1. `INVALID_SERIES`: a non-finite value, or a misaligned or missing day.
2. `INSUFFICIENT_OBSERVATIONS`: `T < T_min`. `T_min` = 365 days
   [AI default]; the Task 12 floor `n >= 16` is far too small for a block
   bootstrap of a maximum. To be confirmed by calibration.
3. `ZERO_VARIANCE_COLUMN`: some `sd(X_j) = 0`.
4. `BLOCK_LENGTH_UNAVAILABLE`: `block_length` fails for some column, or
   `L > T/4` [AI default] (too few blocks to resample).
5. `INVALID_REPLICATE`: any replicate has a column with zero variance or a
   non-finite value. Replicates are never dropped or replaced (the existing
   "any invalid replicate" rule, IMPLEMENTATION_CONVENTIONS.md line 104).
6. `INVALID_ARITHMETIC`: `D <= 0` or a non-finite `S0`, `D` or `z`.

All six are `U_proc` events (D-18 P18-7) and count against the 1% target.

## 3. D-16 and D-17 under this method (the count revisit)

The owner chose (2026-10-03, round 5 Q4) to revisit the D-17 count here.

- **D-16 (effective trial count): proposed answer — no effective count.** The
  method never computes `N_eff`, an eigenvalue spectrum or `A(N)`. The frozen
  primary (`eigenvalue_effective_number...`, protocol line 232) and fallback
  (`raw_trial_count`, line 233) are both replaced by "expected null maximum by
  joint block bootstrap of the declared family". Amendment required.
- **D-17 (which count enters the score): proposed answer — the declared
  current-cycle family, implicitly.** The maximum is taken over exactly the
  `K = |J_f|` declared columns. `N_cycle` and `N_lifetime` are still recorded
  (Constitution §5, line 12; protocol line 190) and reported with every
  result, but do not enter the score [AI default]. Reason: under P18-0 every
  eligible window is new data, declared before evaluation, so earlier attempts
  ran on other data and cannot have selected on this window through the
  engine (Fable FR4-13). The residual — choosing what to declare from
  knowledge of public prices — is the disclosed C2 weakness, and no count can
  repair it.
- **This would change the owner's earlier choice** (2026-10-03,
  `../d16-d17-proposal/OWNER_CHOICE_CANDIDATE_COUNT.md`: lifetime count as
  the candidate). He asked for the revisit; the change is his to confirm.
- **Cross-cycle risk stays open** (O18-3): each eligible cycle carries its own
  5%. Over several eligible cycles the chance that at least one passes by
  luck accumulates (about 1 − 0.95^m for m cycles if independent). Proposed
  [AI default]: report it with every promotion request rather than spend
  alpha across cycles, because eligible cycles are expected to be years apart.

## 4. Points that need more than an AI default

| ID | Point | Why it is not a drafting choice | Proposed handling |
|---|---|---|---|
| B-1 | D-16 answer (no effective count) | a D-row; owner decides after two reviews | review, then owner |
| B-2 | D-17 answer (declared set; lifetime count reported only) | a D-row, and reverses the owner's 2026-10-03 choice | review, then owner |
| B-3 | `D` redefined as bootstrap variance | D-18 cites the `z` formula at METHOD_CANDIDATE.md:92 but not line 91, so the formula is kept; still, the decided text's `D` meant line 91's moment formula | reviewers say whether this is within D-18 or reopens it; if it reopens it, the owner is asked |
| B-4 | Bootstrap mean-correction plus global `z_crit` versus a bootstrap p-value | a direct p-value (`share of M*_b >= S_nominee`) controls the tail per family and might make calibration trivial, but it changes D-18's comparator | recorded as the alternative; not proposed, since D-18 is decided |
| B-5 | Recentring imposes the global null only | mixed-null behaviour is not controlled (O18-1) | challenge cells in D-19, as already decided |

## 5. What the calibration (D-19) must then test

The qualifying grid of D-18 O18-4 applies unchanged: one- and two-trial
families, near-duplicate and duplicate trials, opposites, unequal clusters,
serial dependence up to the 168-hour horizon, cross-trial dependence, heavy
tails (including tails with infinite fourth moment, where the bootstrap of a
Sharpe is not guaranteed), a joint two-family generator sharing the BTC
benchmark days, and the seen/fresh boundary. Added by this method:

- the bootstrap's own Monte-Carlo error at `B = 2000` in `S0` and `D`;
- the block-length rule (largest PW length, `L <= T/4`);
- `T_min` = 365.

`z_crit` is then fixed from development replications and certified on
held-out replications (D-18 P18-6). The figure of about 1.972 applies to the
old candidate only and must be recomputed (FR4-9).

## 6. Reuse, cost and build scope (for later, not now)

- Reuses existing code: `block_length`, `bootstrap_indices`,
  `replicate_seed`, `type_seven_quantile` (`src/aqt/metrics/statistics.py`).
  New code would be one function computing `S0`, `D` and `z` from a `T × K`
  matrix, plus the reason codes. Building it needs the owner's separate
  go-ahead and is §16-protected (promotion gate).
- Cost: `B × K` Sharpe evaluations per family, at most 2000 × 80 = 160,000
  per family. Trivial at run time; the calibration multiplies it by the
  replication count.

## 7. Not changed by this proposal

D-18 as decided (except B-3 if reviewers find it reopens D-18); the E-DIFF
estimand; the PBO, CI, plateau and lockbox clauses (D-05, D-06, D-11, D-14,
D-15 remain open); every frozen file. Promotion stays blocked.

## 8. Next

Two different-model reviews of this design (R19-2), records committed; then
the owner decides D-16 and D-17 (B-1, B-2) and, if needed, B-3.
