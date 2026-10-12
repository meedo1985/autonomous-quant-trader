# Annex B — DSR method `aqt.dsr.bootstrap_max.candidate.v2` (normative text for the amendment)

**Status:** AI-extracted copy for the §4 draft; not an amendment until the owner authors it.
Source: `broadened-method/DESIGN.md` at `a3d2c59` (rev. 3; B-1..B-7 decided in `OWNER_DECISION_B.md`), §2 (from "## 2. Proposed method" through §2.6, lines 42–204), copied verbatim. Section 2.7 (design claims) is omitted because it is not normative. Free parameters (family block rule, `T_min`, `z_crit`) are fixed by the D-19 preregistration.

---

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

