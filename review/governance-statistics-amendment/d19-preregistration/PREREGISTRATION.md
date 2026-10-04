# D-19 calibration preregistration for C2 (revision 6 accepted; budget version rev 7g proposed in §13)

**Status:** `ACCEPTED BY THE OWNER (rev 6, OWNER_DECISION_D19_ACCEPT.md, ec35a29) — NOT YET COMPLETE (keys record pending) — NO CALIBRATION RUN`

**Date:** 2026-10-04

**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`). The owner delegated drafting choices on 2026-10-03 and 2026-10-04, so every choice below is an `[AI default]` unless it cites a decided record.

**History:**

| Rev | Commit | Fable review | Sol review |
|---|---|---|---|
| 1 | `aa981d8` | DF1 `f54e84e` | DS1 `90029a4` |
| 2 | `71357d4` | DF2 `552af72` | DS2 `169985e` |
| 3 | `59f5f6c` | DF3 `2c2b11b` | DS3 `807ee4a` |
| 4 | `a841fb3` | DF4 `c26e59e` | DS4 `c518e94` |
| 5 | `327aa3d` | DF5 `df65001` | DS5 (see `SOL_REVIEW_327AA3D.md`) |
| 6 | `e1e4e7e` | DF5 wording fixes applied (`ADJUDICATION_327AA3D.md`) | DS6 READY `0ac488d`; **accepted by the owner** (`ec35a29`) |
| 7 | `af03d00` | draft §13, computational equivalence | Sol DS7 UNSOUND (`77f9593`); **withdrawn** (`PILOT_FINDINGS_3.md`). The text below is rev 6 again. |
| 7b | `c09337f` | §13 budget version (owner direction 3, `30757e8`), with method V (D-20 partial, `b58d1c3`); BF1 UNSOUND `7c7cf49` | BS1 UNSOUND `769f966` |
| 7c | `09b0fb9` | §13 repaired per BF1 and BS1 (`ADJUDICATION_C09337F.md`); run on the owner's server; BF2 SOUND WITH FIXES | BS2 UNSOUND (`aa6caa7`) |
| 7d | `9762781` | §13 repaired per BF2 and BS2 (`ADJUDICATION_09B0FB9.md`); BF3 SOUND WITH FIXES (`ff9eb3a`) | BS3 SOUND WITH FIXES (`564ebea`) |
| 7e | `9d811e6` | §13 repaired per BF3 and BS3 (`ADJUDICATION_9762781.md`); BF4 READY WITH FIXES (`23ce5f4`) | BS4 READY WITH FIXES (`026a23a`) |
| 7f | `02c14e5` | §13 repaired per BF4 and BS4 (`ADJUDICATION_9D811E6.md`); BF5 READY WITH FIXES (`d69fe25`) | BS5 READY WITH FIXES (`d46c870`) |
| 7g | this revision | §13 wording fixes per BF5 and BS5 (`ADJUDICATION_02C14E5.md`) | no further review planned: both fix-checks were READY WITH FIXES, minor only; §1–§12 remain the accepted rev 6 text until the owner accepts §13 |

The adjudications are `ADJUDICATION_AA981D8.md`, `ADJUDICATION_71357D4.md`, `ADJUDICATION_59F5F6C.md` and `ADJUDICATION_A841FB3.md`. The owner decision is U-1, recorded in `OWNER_DECISION_UPROC_SCOPE.md` (`8e04dd8`).

**Authority and limits:**
- `d19-recommendation/OWNER_STEP0_DECISION.md` (R19-1, R19-2) allows the design.
- Building the engine, running a pilot, or producing any result needs the owner's **separate go-ahead** (§12).
- No human statistician is involved; two AI model families review it (R19-2), and this is disclosed.
- Only synthetic data and exploration-partition BTC/ETH data are used. No confirmation or lockbox data is read.

**What it binds:**
- Annex B (`aqt.dsr.bootstrap_max.candidate.v2`);
- Annex A: P18-0..P18-7, A-B7, and A-U1 (U-1);
- Annex C;
- D-18 O18-4 (the calibration grid).

**What it supplies:**
- `T_min`;
- `family_block_rule`;
- `z_crit`;
- the `U_proc^R` allocation;
- the certification route (§11).

**Owner item:** `<<OWNER Q-1>>`, the commitment channel for the qualification object (§4).

## 1. The claim, and its conditions

**The claim.** Under the all-zero-mean global null, in **every** qualifying cell (§3), at family-wise one-sided 95% confidence over every enumerated test and both permitted attempts (§6):

1. **Error.**
   - Per family: the upper bound on `P_0(E_f)` is at most 0.025, where `E_f = A_f ∩ {z_f* ≥ z_crit}` (P18-6).
   - Per cycle: the upper bound on `P_0(E)` is at most 0.05. This is certified directly in the joint cells QJ, and holds by the union bound elsewhere.
2. **No result (A-U1).** The upper bound on `P_0(U_proc^R)` is at most 0.005 per family. Per cycle it is at most 0.01, certified directly in QJ.
   - `U_proc^R` is DSR availability, including the window classifier (§3.5), or `U_G` (§7). The declaration mapping (§3.6) is a deterministic validity check under P18-1 and is not part of `U_proc^R` (DS4-4).

**What is not claimed:**
- **Screened gates have no certified rate.** These are G-3, G-5, G-6, G-7, G-8, G-11 and G-14. They are screened before declaration (§7.2). If one is unavailable on the real window, that is recorded with no certified rate (A-U1).
- **A declared design must fall inside a qualifying cell (O18-4).** This is checked on exploration data before declaration (§3.6). The real-window classifier (§3.5) is a further refusal. Passing both is necessary, not proof, that C2's law is covered.
- **Some cells are uncertified challenge cells.** A cell is a challenge cell if the 90% upper confidence bound (UCB) of its development cap rate exceeds τ_DSR/4. Its availability is reported.
- **Declaration conditions.** The declared `|J_f|` must be in {1, 2, 5, 20, 80}, and C2's `g` must equal the frozen value. Otherwise the declaration is invalid.

**If certification fails,** the method does not qualify and promotion stays blocked.

## 2. One replication

1. **Market and legs.** Generate one market and its legs (§3.1). Every column of `X` has population mean exactly 0. In QJ, both families share this one market.
2. **Annex B rules 1–4.** Apply Annex B §2.5 rules 1–4.
3. **Window classifier.** Apply it (§3.5). A refusal is a `U_proc^R` event.
4. **The rest of Annex B.** Apply rules 5–6, then compute `S0`, `D_j`, `z_j`, the nominee (P18-4) and `E_f`, with `B = 2000`. Store `z_f*`.
5. **`U_G` gates.** Evaluate G-1, G-2, G-4 and G-12 (for each `H` ∈ {24, 72, 168}) on the nominee. Evaluate G-10 over the whole family matrix. This happens whatever the outcomes above (P18-7).
6. **Record.** Record the events, cause codes, `L`, `L/T` and the diagnostics.

## 3. Cells

### 3.1 Market and leg generators (`U_proc^R` and the error test)

**BTC returns.** `r_t = σ_t·ε_t`.
- `σ_t` is either constant at 3.5% per day, or common GARCH(1,1) with α = 0.10, β = 0.85, rescaled to an unconditional 3.5%.
- Every series starts at its unconditional state, with a 500-day burn-in that is discarded.

**Laws of `ε` and of the column innovations.**
- Gaussian.
- t₅.
- Azzalini skew-t with ν = 5 and shape `α_s`. `α_s` is frozen numerically to give a standardised skewness of ±1, and recorded.
- AR(1): `x_t = φ·x_{t−1} + sqrt(1 − φ²)·e_t`.
- GARCH: common `σ_t` with t₅ innovations.

**Benchmark.** `b_t = e_t·r_t`, where `e_t = min(1, 0.40/(σ̂_t·sqrt(365)))`.
- `σ̂_t` is a daily EWMA with a 7-day half-life, using past data only, seeded at 3.5%.
- This is a daily stand-in for the benchmark.

**Columns.** `X_j,t = 0.3·c_j·σ_t·x_j,t`, where the column scale is `c_j = 1` except in the unequal-moments cell (§3.2).
- **Cross-column construction.** `x_·,t = Σ^{1/2}·z_t`, where `z_t` holds independent, standardised draws from the cell's law.
  - `Σ^{1/2}` is the symmetric positive-semidefinite square root from the eigendecomposition, with eigenvalues clipped at 0.
  - This is a linear construction: for non-Gaussian laws it fixes the correlation, not the copula, and the marginals of `x` are mixtures. This is disclosed.
- **`Σ` by dependence level** (DS4-2, DF4-4). Indices are 0-based.
  - Equicorrelated: `Σ = (1 − ρ)I + ρ11ᵀ`.
  - Near-duplicates: `Σ_{2i,2i+1} = Σ_{2i+1,2i} = 0.999` for each pair (0,1), (2,3), …. Every other off-diagonal entry is 0. At odd `K`, the last column is independent.
  - Exact duplicate: column 1 is set equal to column 0. The other columns are independent.
  - Opposites: groups `G1` = the first `floor(K/2)` columns and `G2` = the rest. `ρ = 0.9` within a group and `−0.9` between the groups. This matrix is positive-semidefinite, with minimum eigenvalue 0.1.
  - Unequal clusters: the clusters are consecutive index blocks of the stated sizes. `ρ = 0.9` within a cluster and `0.2` between clusters.
  - One factor: `Σ = λλᵀ + diag(1 − λ²)`.
- **Factor loadings.** These are drawn once per replication from the `"columns"` stream.
- **Candidate legs.** `C_j = b + X_j`, which is about 2.3% per day.
- **Equity.** An equity path at or below 0 is `INVALID_SERIES`.

### 3.2 Qualifying cells (O18-4)

**Declarable size.** `|J_f|` must be one of {1, 2, 5, 20, 80}. This is checked under P18-1.

**Lengths.**
- `T` takes the `T_min` candidates {365, 548, 730}, plus 1095 and `T_C2`.
- `T_C2 = 1247 − g`, with `g` fixed by the frozen gap rule from exploration data before the threshold run. A different `g` at C2 makes the declaration invalid.
- `T` levels below `T_min` are dropped.

**Dependence levels** (`Σ`; integer groups):

| Level | Definition | Applies at |
|---|---|---|
| independent | — | every `K` |
| equicorrelated | `ρ` ∈ {0.5, 0.9, 0.99} | `K ≥ 2` |
| near-duplicates | pairs with `ρ = 0.999` | `K ≥ 2` |
| exact duplicate | one pair of identical columns | `K ≥ 2` |
| opposites | `Σ` as in §3.1: groups `G1` (the first `floor(K/2)` columns) and `G2`; `ρ = 0.9` within a group and `−0.9` between groups; no further negation (DF5-4) | `K ≥ 2` |
| unequal clusters | sizes {1,4} at `K = 5`, {5,15} at 20, {20,60} at 80; `ρ` 0.9 within a cluster, 0.2 between | `K ≥ 5` |
| one factor | loadings uniform on [0.3, 0.99] | `K ≥ 5` |

**Groups.**

| Group | Law | Dependence | `K` | `T` |
|---|---|---|---|---|
| **Q1** core | Gaussian, constant `σ` | every level that applies at that `K` | {1, 2, 5, 20, 80} | every `T` |
| **Q2** laws | t₅; skew-t ±1; GARCH-t₅; AR(1) with `φ` ∈ {0.2, 0.5} | independent; `ρ = 0.9`; opposites | {1, 2, 5, 20, 80} | `T_min`, `T_C2` |
| **Q3** heteroskedastic factor | common GARCH | one factor | {5, 20, 80} | `T_min`, `T_C2` |
| **Q2m** unequal moments | columns `j < ceil(K/2)` are t₅, the rest Gaussian; `c_j = 0.5` for even `j` and `2` for odd `j`, so both laws carry both scales at `K ≥ 5` (at `K = 2` law and scale are confounded, which is accepted; DF5-5, DS5-2) | independent | {2, 5, 20, 80} | `T_min`, `T_C2` |
| **Q4** mixed column | one AR(1) column with `φ = 0.5` among iid columns | — | {2, 5, 20, 80} | `T_min`, `T_C2` |
| **Q5** semi-empirical, family-labelled | §3.4 | — | {1, 2, 5, 20, 80} | `T_min`, `T_C2` |
| **QJ** joint, both families | the trend library and the vol library on **one shared** §3.4 market path, so the BTC benchmark days are shared | — | each family at `K` ∈ {2, 20, 80} | `T_min`, `T_C2` |

**What the groups certify.**
- Q1–Q4 are family-agnostic: each test counts once and certifies both families.
- Q5 is per family.
- QJ certifies the cycle-level bounds.

**Coverage rule (O18-4, DF4-3).** After development, every O18-4 category must keep at least one qualifying cell from its listed cells. Otherwise the method does not qualify.

| O18-4 category | Cells that count |
|---|---|
| one-trial families | any group, `K = 1` |
| two-trial families | any group, `K = 2` |
| high correlation | Q1, `ρ` ∈ {0.9, 0.99} |
| duplicates | Q1, near-duplicates or exact duplicate |
| opposites | Q1 or Q2, opposites |
| unequal clusters | Q1, unequal clusters |
| unequal `T` | cells at two or more `T` levels |
| serial dependence | Q2 AR(1), Q4 |
| cross-trial dependence | Q1 or Q2 with `ρ > 0`; Q3 |
| heavy tails | Q2 t₅ or GARCH-t₅ |
| unequal moments | Q2m |
| joint generator | QJ |

**Cap rule.** A cell whose development cap-rate UCB exceeds τ_DSR/4 is a challenge cell.

### 3.3 Challenge cells (reported only)

- ARFIMA with d = 0.3 in all columns.
- One ARFIMA column among iid columns, at `K` ∈ {2, 5, 20, 80}. It is reported under both block rules.
- A variance break.
- Markov regimes.
- t with ν = 1.8.
- Sparse columns.
- Cells demoted by the cap rule.

### 3.4 Semi-empirical market (Q5, QJ; exploration data only; exact null)

1. **Returns.** Use a joint stationary bootstrap, with mean block length 20, of demeaned daily BTC and ETH returns. These come from the **exploration partition only**, and its manifest hash is in the object.
2. **Exposures.** Trend-rule and vol-rule exposures are computed causally on the BTC path. The benchmark is the stand-in from §3.1. Each raw column is `X̃_j,t = (e_j,t − e^b_t)·r_t`.
3. **Sign flips.** Each geometric block of mean length 20 gets one sign: an iid fair draw of ±1, independent of the resampled path (DS4-2). The signs are shared across all columns, and across both families in QJ. They come from the `"sign"` stream, and the first block starts at day 0. Then `X = s·X̃`, so `E[X] = 0` exactly, and `C = b + X`.
4. **Disclosed side effects.**
   - The marginal skewness is zero in distribution.
   - The implied exposure lies in [−1, 2].
   - The serial sign structure across blocks is lost.

**Sensitivity check.** The whole construction is rerun with mean blocks of 60 and reported.

### 3.5 Window classifier (at evaluation)

**Order.** It runs after Annex B rules 1–4 and before rule 5.

**Diagnostics on `X`:**
- `K` and `T`;
- the maximum `L_j/T`;
- the maximum excess kurtosis `g2`;
- the minimum and maximum skewness `g1`;
- the maximum GPH `d̂`, with bandwidth `floor(T^0.5)`;
- the maximum CUSUM-of-squares statistic;
- the maximum zero-day share;
- the minimum and maximum pairwise Pearson correlation (only when `K ≥ 2`).

**Thresholds (DS3-3, DF3-2).**
1. A **threshold run** draws 10⁶ samples, from the generator only, in **every** enumerated candidate cell. It uses its own namespace and keeps each cell's per-tail order statistic:
   - `ceil(0.99999·n)` for an upper tail;
   - `floor(0.00001·n) + 1` for a lower tail.
2. **Development** uses, per `T` level, the extreme over **all** candidate cells (DF4-5).
3. **Before the freeze,** each threshold is set per `T` level, as the extreme of the stored statistics over the **final** qualifying cells. Held-out refusal can therefore exceed development refusal by up to the per-cell sum over tails, about 1.3·10⁻⁴. Validity rests on the held-out run, which uses the frozen thresholds.

**Refusal.**
- **Rate.** The per-tail refusal rate is at most about 1.1·10⁻⁵ per qualifying cell, so at most about 1.3·10⁻⁴ over all tails. That is within the classifier's 2·10⁻⁴ budget inside the DSR-availability share.
- **Non-finite diagnostics.** A non-finite diagnostic is a refusal.
- **Cause.** The cause code is `UNSUPPORTED_LAW`, a `U_proc^R` event.

### 3.6 Declaration-time design-to-cell mapping (O18-4; DS3-1)

**Inputs.** Before the declaration is committed, each declared family is run, as a declared trial set, on the **exploration partition only**. This uses research data that the sandbox may already see; no window data is touched.

**Diagnostics.** The §3.5 diagnostics are computed on its daily E-DIFF matrix over the **last `T_C2` complete days** of the exploration partition. The length dependence of the diagnostics then matches the `T_C2` thresholds. If the exploration partition holds fewer than `T_C2` days after the trials' warm-up, the design cannot be mapped and is refused.

**Mapping (DS4-1, DF4-1).** The design is accepted if, and only if, at least one **final qualifying cell `c`** with `K_c = K` and `T_c = T_C2` contains **every** diagnostic within `c`'s **own** stored per-tail order statistics. The cell ids that match are recorded in the declaration. A design whose law is exactly some cell's law is accepted with probability about `1 − 1.3·10⁻⁴`. The pooled thresholds of §3.5 are used only by the window classifier.

**Outcome.**
- If any diagnostic falls outside, the design is **refused at declaration**. Under P18-1 that means it cannot be declared, and no `m` is spent.
- The result and the diagnostics are recorded, and their hash goes into the declaration.

**Disclosed limitation.** The exploration-period law can differ from the window's law, so this mapping is deterministic but not proof of coverage. The window classifier is the second check.

## 4. Qualification object and freeze order

**Contents of the object:**
- the method build at a commit hash;
- this preregistration at its accepted hash;
- the generator code and the frozen `α_s`;
- the exploration-data manifest hash;
- the pinned runtime (Python and numpy versions, and the dependency lock);
- the manifest of cells and enumerated tests;
- the threshold-run statistics and the frozen thresholds;
- the exact-binomial script and its outputs;
- `family_block_rule`, `T_min` and `z_crit`;
- the allocation;
- the screen and mapping code;
- the seed specification.

`qualification_object_sha256` is the SHA-256 of the canonical manifest of file hashes.

**Freeze order:**
1. The owner accepts this preregistration and decides `<<OWNER Q-1>>`.
2. The owner gives the go-ahead for the build and a measured pilot. The build goes through §16 review.
3. The threshold run is done over all candidate cells.
4. Development is done (§5).
5. **Freeze.**
   - Recompute the thresholds over the final qualifying cells.
   - Hash and commit the object.
   - The owner posts `qualification_object_sha256` on the attempt's channel.
6. **Held-out certification** (§6) runs after the attempt's O-6a freeze read and the publication of its drand round (§4, §8).
7. **Accept or fail.** After a failure, at most one further attempt is allowed. It needs a recorded change, a new namespace and the next attempt key. Every attempt uses α = 0.025/`M`. No re-tuning on seen held-out data is allowed (P18-6).
   - **Keys run out (DF5-1).** A void attempt also uses up its key. If no key remains, qualification has not been obtained under this preregistration. Any further key needs a new acceptance.

**Channel for `<<OWNER Q-1>>` (by substitution into O-6a SPEC rev 5 `84fca9c` §3–§7):**
- **Prefix.** `AQTQ1`. The scriptPubKey is exactly `6a 25 41 51 54 51 31` followed by the 32-byte `qualification_object_sha256`, 39 bytes in all.
- **Keys and coins.** Attempt `n` ∈ {1, 2} has its own key `A_Qn`, bound coin `F_Qn` and deadline height `D_Qn`. `A_Q1`, `F_Q1`, `D_Q1`, `A_Q2` and `F_Q2` are fixed at the preregistration's acceptance, as `<<ACCEPTANCE: A_Q1, F_Q1, D_Q1, A_Q2, F_Q2>>`. `D_Q2` is fixed only in the attempt-2 record, before its post (DF5-3, DS5-1).
- **Horizons (DF4-2).**
  - O-6a's "after signing" becomes "after acceptance of this preregistration".
  - Both "before C2 ends" and "before C2's evaluation is final" become "before the owner's accept or reject of certification (§12 item 4)".
  - `D_Qn` must be above the acceptance height. `D_Q2` is fixed in the attempt-2 record before its post.
- **Timing.** The held-out run starts only after the O-6a freeze read for `T_Qn` **and** the publication of the drand round.
- **Pre-run record (DF5-2).** Before the held-out run, two records are committed. One is a check of every O-6a invalidation condition for the attempt; the other records the time the run starts. An invalidation that is not listed in that committed check counts as found at or after the start, even if the chain shows it existed earlier.
- **Failure boundary (DS4-3, DF4-2).** An O-6a invalidation found **before** the held-out run starts makes the attempt **void**:
  - no held-out run is made, and the namespace is not burned;
  - the same object may be posted again under the next attempt key and namespace `d19-heldout-v{n+1}`, with no recorded change.

  An invalidation found **at or after** the start is a **failed attempt**:
  - its namespace is burned;
  - P18-6 applies, so there is no retuning;
  - any further attempt needs a recorded change.
- **Cost.** Two Bitcoin network fees per attempt, plus any withdrawal fee.

## 5. Development phase [frozen rules]

**Targets (τ).**
- For each test `i`, τ_i is the largest true rate whose held-out pass probability is at least 0.999. It is computed at α = 0.025/`M_max` with that test's `N_i` (DF3-3).
- `M_max` is the manifest's test count at the smallest `T_min` candidate, which is conservative.
- At `M_max ≈ 1,167`, from 379 cells at `T_min = 365` including Q2m (DS5-3), the targets are:

  | Test | `N` | τ |
  |---|---|---|
  | error | 20k | about 0.01763 |
  | DSR availability | 20k | about 0.00113 |
  | `U_G` | 20k | about 0.000148 |
  | `U_G` | 40k | about 0.000415 |

  At `τ_G(20k)`, a 22k development run must show no `U_G` event. The exact values are printed from the manifest. The quoted τ values and critical counts do not change at this `M` (DS5-3).

**Replications.**
- 22,000 per candidate cell.
- `z_f*` is stored for every replication.

**Choices, in order:**
1. **`family_block_rule`.** Run every candidate cell at every `T` level at `z = 1.96`. Choose largest or median by the smaller worst-cell `P̂_0(E_f)`; a tie goes to largest.
2. **`T_min`.** The smallest candidate at which every cell meets its **availability** tests: the 90% UCB of DSR availability is at most τ_DSR, and the UCB of `U_G` is at most τ_G(20k) or τ_G(40k). `N_i = 40,000` exactly when the `U_G` UCB exceeds τ_G(20k).
3. **`z_crit`.** The smallest decimal on a 0.001 grid at which every qualifying cell's 90% UCB of `P_0(E_f)` is at most τ_err. In QJ, the UCB of `P_0(E)` must also be at most τ for 0.05. This is computed from the stored `z_f*`.
4. **Coverage rule.** Apply §3.2.
5. **Joint diagnostic.** Report a labelled plug-in estimate of the joint held-out pass probability. It is not a certified probability (DS3-6).
6. **No qualifying choice.** If none qualifies, the method does not qualify.

## 6. Held-out certification

**Tests.** The enumerated tests are (cell, family label or `agnostic` or `joint`, bound). The bounds are:
- `P_0(E_f)` ≤ 0.025;
- DSR availability, including the window classifier, ≤ 0.0035;
- `U_G` ≤ 0.0015.

QJ adds two cycle-level bounds:
- `P_0(E)` ≤ 0.05;
- `U_proc^R` ≤ 0.01.

`M` is taken from the manifest.

**Bounds.** One-sided Clopper–Pearson upper bounds at α = 0.025/`M` per attempt, so the family-wise level is at least 95%.

**Replications.**
- `N = 20,000` per cell.
- `N = 40,000` where §5 step 2 sets it.

**Acceptance.** Every test must be within its target.

## 7. No-result routes (A-U1)

**Allocation per family:**
- 0.0035 for DSR availability, with at most 2·10⁻⁴ for the window classifier;
- 0.0015 for `U_G`.

**`U_G`.** `U_G` is the event that any of these is unavailable:
- G-1, G-2 or G-4 on the nominee;
- G-10 over the family matrix;
- G-12 on the nominee for any `H` ∈ {24, 72, 168}.

It is one event with one test per cell (DS3-4).

**G-13.** Route D, by hash comparison.

**Input integrity.** Bars that fail at the input are `DATA_INTEGRITY`, a `U_ops` event. Non-finite derived series are `INVALID_SERIES`, a `U_proc^R` event.

**Screened gates.** G-3, G-5, G-6, G-7, G-8, G-11 and G-14 go through the screen in §7.2.

### 7.2 Declared-strategy screen (A-U1)

**When.** Before the declaration is committed, on the actual trial set.

**Paths.** `n_S = 30` simulated null **hourly** BTC/ETH paths, built as follows:
- **Bootstrap.** A joint hourly stationary bootstrap, with mean block length 168 h, of exploration-partition 1h bars. The manifest hash of those bars is in the object.
- **Signs.** Signs in geometric blocks of mean length 24 h, shared by BTC and ETH.
- **Reconstruction (DS4-5, DF4-4).** Each resampled bar gives its log offsets from its own open: `h = ln(H/O)`, `l = ln(L/O)`, `c = ln(C/O)`.
  - A bar with sign −1 has `(h, l, c)` replaced by `(−l, −h, −c)`.
  - The path is chained: each new bar's open equals the previous new close, and the first open is the first sampled bar's open. Then `H = O·e^h`, `L = O·e^l` and `C = O·e^c`. Any gap between a bar's open and the previous close in the source data is dropped.
  - Volume is kept as sampled.
  - There is no further demeaning. The symmetric, independent signs give zero drift in expectation.
- **Length.** The C2 window length plus the trials' declared warm-up.

**Runs.** Each trial is run under C-6 on every path. Every screened gate is computed at production counts:
- G-11: 500 draws;
- G-14: 500 refits;
- G-5..G-7: their stressed runs.

**Outcome.** Any unavailability makes the set invalid (P18-1). No `m` is spent.

**Seed.** `SHA256(cj({"stream": "screen", "trial_set_sha256": <hex>}))`, with no nonce. Every screen run is recorded and listed in the declaration.

**Power.** 0.96 at a 10% per-path rate, and 0.26 at a 1% rate.

## 8. Seeds (exact)

**`cj`.** UTF-8, sorted keys, no insignificant whitespace, decimal integers, and lowercase hex hashes. `j` and `rep` are **0-based**.

**Namespaces.**
- `"d19-threshold-v1"`;
- `"d19-dev-v1"`;
- `"d19-heldout-v1"`;
- `"d19-heldout-v2"`.

**Outer seed.**

```
seed = SHA256(cj({"anchor": <hex>, "cell_id": <str>, "ns": <str>, "rep": <int>}))
```

**`anchor`.**
- In threshold and development runs: the preregistration hash.
- In held-out attempt `n`:

  ```
  SHA256(cj({"beacon_randomness": <hex>, "qobj": qualification_object_sha256, "round": <int>}))
  ```

  The round is the first round of the C2 drand chain (DRAFT §2.0) whose scheduled time is at or after `T_Qn + 24h`. `T_Qn` is fixed from the attempt's `AQTQ1` post, as in O-6a SPEC §5.

**Streams.**
- `SHA256(cj({"seed": <hex>, "stream": <name>}))`, for each name in `"market"`, `"sign"`, `"columns"`, `"g1_ci"` and `"inner"`.
- The generator is numpy `Philox` (4×64, 10 rounds). Its key is two uint64 values, big-endian, taken from the first 16 bytes of the stream hash. The counter starts at 0. The numpy version is pinned in the object.
- `"g1_ci"` is the trial seed for the production `paired_sharpe_ci` stream.

**Symbol `s`.** `s` denotes the outer seed, as lowercase hex (DS4-5).

**Inner Annex B family seed.** This is the production construction, with synthetic fields:

| Field | Value |
|---|---|
| `protocol_hash` | the preregistration hash |
| `family_id` | the family label, or `"agnostic"` |
| `cycle_id` | `"D19"` |
| `window_id` | the cell id |
| `data_manifest_hash` | the outer seed |
| `trials` | `{"configuration_hash": SHA256(cj({"j": j, "seed": s, "tag": "c"})), "hypothesis_hash": SHA256(cj({"j": j, "seed": s, "tag": "h"})), "trial_id": "t%03d" % j}` |

**R-7.** `round = rep`, and `beacon_randomness = SHA256(cj({"seed": s, "tag": "beacon"}))`.

**Reproducibility.** A result that does not reproduce is void (Constitution §27).

## 9. Reported, not certified

- **Power cells.** One trial has a true annualised Sharpe of 0.5, 1.0 or 2.0, at `K` ∈ {1, 2, 20, 80}, at `T_min` and `T_C2`, under Q1-independent and Q3.
- **Mixed nulls.** `K − 1` trials at −0.5 and one at 0.
- **Challenge cells.** Every challenge cell, with the window classifier's **acceptance rate** on each.
- **Rates.** Cap and failure rates per column, by `K`; `P_0(E_f | A_f)`; and the reach-pick rate.

## 10. Compute

**Main runs.** Development and held-out each use about 20,000 replications per cell. QJ cells cost about twice a single-family cell. The `U_G` gates add their own cost: G-1 at 2,000 replicates, G-10 at 12,870 splits, and G-12 at three horizons.

**Estimate.** About **2,000–7,000 CPU-core-hours** for the calibration. This estimate predates rev 4's roughly 30% larger grid and QJ's doubled cost, and it is not measured; the pilot replaces it (DF4-6). The threshold run is cheap.

**Per-declaration costs.**
- The screen: up to 80 trials × 30 paths × about 1,004 hourly runs.
- The mapping: one exploration run per trial.

**Before go-ahead,** a measured pilot is required. It must cover:
- the largest cell;
- a median cell;
- a QJ cell;
- the threshold run;
- one screen of an 80-trial set;
- a declaration-mapping run of the real trend and vol rule libraries on exploration data, to measure how often real designs are refused.

## 11. Amendment wording proposed for `<<OPEN D-19 route>>` (A-U1, O18-4)

> "P18-7's procedure no-result target of at most 0.01 per cycle applies to U_proc^R: the unavailability of the DSR method, including the supported-law window classifier, and of gates G-1, G-2, G-4, G-10, G-12 and G-13. It is certified as specified in the D-19 preregistration bound here by hash: by simulation in every replication, including joint two-family cells, and, for G-13 and the bounds on T, by written deterministic arguments.
>
> Gates G-3, G-5, G-6, G-7, G-8, G-11 and G-14 are excluded from that target and governed by a fail-closed screen of the actual trial set on simulated null hourly paths before the declaration is committed. Their unavailability on the window is a procedure no-result event recorded with its cause code, without a certified rate.
>
> Each declared family design is mapped deterministically, on exploration data before declaration, to the qualifying cells of its K and T whose own acceptance region contains its full diagnostic vector; a design matched by no such cell is refused, and the matching cell ids are recorded in the declaration. The declared |J_f| must be one of 1, 2, 5, 20 or 80."

## 12. What the owner decides, and when

1. **Accept this preregistration** after its reviews, and decide `<<OWNER Q-1>>`: the qualification-object commitment channel, at two Bitcoin fees per attempt.
2. **Go-ahead for the build and measured pilot.** After the pilot, decide on the full run, local or rented.
   - If the measured screen cost for a set of a given size is infeasible, a set of that size cannot be declared in C2.
3. **The `AQTQ1` post at the freeze,** made by the owner.
4. **Accept or reject the certification result.** A failure leaves promotion blocked.

Nothing here starts a cycle, reads confirmation or lockbox data, or authorizes trading.

## 13. Budget version (rev 7g, proposed; overrides the sections it names)

**Why.** The owner can spend at most $3–10 a month (owner direction 3, `30757e8`). The laptop must be switched off, so the calibration runs on the owner's small rented server, the one that also runs forward paper (about €6 a month, no extra cost). The full plan is about 12,000 core-hours. This version aims at about 4,500. Method V computes the replicate Sharpes (A-V1, owner decision D-20 partial).

**Overridden sections:** §1, §3.2, §3.3, §3.5, §3.6, §4, §5, §6, §9, §10, §11 and §12, as stated item by item below. Everything else is the accepted rev 6 text.

**Overrides:**

1. **Family sizes (§1, §3.2, §9, §10, §11).** The declarable `|J_f|` is one of {1, 2, 5, 20}. Every group runs at the `K` values of {1, 2, 5, 20} where its law is defined. QJ runs each family at `K` ∈ {2, 20}. The §10 screen and pilot items read "up to 20 trials" and "a 20-trial set" in place of 80.
2. **One length; C2 only (§1, §3.2, §5 step 2, §12; A-B7) (BF1-2, BS1-3, BF2-3, BS2-3).**
   - Every qualifying cell has `T = T_C2`. The `T_min` candidates are {`T_C2`}, so `T_min = T_C2`.
   - **What this covers.** This qualification object certifies **C2 only**. Every later cycle needs a new qualification.
   - **Why A-B7 needs no change.** C2's `T` cannot exceed `T_C2`, because a different `g` already makes the declaration invalid (§1). A C2 window with missing complete days has `T < T_C2 = T_min` and is ineligible under A-B7 as decided. So A-B7's floor reading stands unchanged, and rev 7c's `<<OWNER A-B7-EQ>>` is withdrawn.
   - **Owner question (§12 overridden).** Acceptance of §13 needs, besides `<<OWNER Q-1>>`, a separately recorded owner answer to `<<OWNER O18-4-T>>`: drop decided O18-4's "unequal `T`" category from the coverage table. Without an affirmative recorded answer, §13 is not accepted.
3. **Replications (§5, §6) (BF1-1, BS1-1, BF1-8, BF2-1).**
   - **Development:** 12,000 per cell.
   - **Held-out:** 20,000 per cell, or 40,000 where the escape below applies.
   - **§5 step 2 is restated.** A cell passes development availability when its 90% UCB of DSR availability is at most τ_DSR(20k), and its 90% UCB of `U_G` is at most τ_G(20k) or, as an escape, at most τ_G(40k).
     - Where only the escape is met, that cell runs 40,000 held-out replications, and all its tests use `N_i = 40,000`.
     - At 12,000 development replications, the 90% UCB of `U_G` is 1.92·10⁻⁴ at 0 events, 3.24·10⁻⁴ at 1 and 4.43·10⁻⁴ at 2. Against τ_G(20k) ≈ 2.02·10⁻⁴ and τ_G(40k) ≈ 4.51·10⁻⁴ (both at `M ≈ 322–340`), 0 events need 20k, 1–2 events need 40k, and 3 or more fail.
   - **A cell that fails** development availability is **demoted to a challenge cell**, like a cap-demoted cell (§1 and §3.3 overridden: a challenge cell is a cap-demoted or availability-demoted cell).
     - A demoted cell is reported from its development replications and the §9 runs only, and is not certified.
     - The coverage rule (§3.2) then decides whether the method still qualifies.
     - The mapping (§3.6) and the classifier thresholds (§3.5) use only the final qualifying cells, so a declared design that matches only demoted cells is refused at declaration.
     - Demotion happens before the freeze, and held-out runs in its own namespace on the final cells only, so it does not bias the certified claim.
   - **Demotion risk, disclosed (BS3-2).**
     - **Per `U_G` test.** The probability that one `U_G` test demotes its cell by chance (3 or more development events) is 0.002, 0.023, 0.12 and 0.43 at true rates p = 2·10⁻⁵, 5·10⁻⁵, 10⁻⁴ and 2·10⁻⁴. Without the escape it would be 0.21, 0.45, 0.70 and 0.91.
     - **QJ.** A QJ cell has two family `U_G` tests, so its chance is between one and two times the per-test value; at p = 5·10⁻⁵ that is 0.023–0.046.
     - **DSR availability.** This is a separate demotion route (more than 9 development events), and is not in these numbers.
     - **Re-pilot.** Some coverage categories have only 2–3 cells (QJ, Q1 unequal clusters, Q2m). The re-pilot therefore measures `U_G` and DSR-availability rates in those cells before the full run.
   - **Targets.** τ is computed by the frozen script with each test's `N_i` as run, from the actual manifest. Values at `M ≈ 322–340`, checked independently by both reviewers and by the drafter:

     | Test | `N` | Critical count | τ |
     |---|---|---|---|
     | error | 20k | 418 (417 at `M = 340`) | 0.01796 (0.01791) |
     | DSR availability | 20k | 40 | 0.00120 |
     | `U_G` | 20k | 11 | 0.000202 |
     | `U_G` | 40k | 32 | 0.000451 |

   - **Disclosed effect.** `z_crit` is chosen so that the 90% UCB of `P_0(E_f)` at 12,000 development replications is at most τ_err. That UCB is wider than the full plan's at 22,000, so `z_crit` comes out a little higher, and the test has a little less power to pass a real edge. The validity of the false-pass bound is unchanged.
4. **Classifier (§3.5, §3.6) (BF1-3, BS1-2, BF1-7, BF2-6, BS2-5).**
   - **`L_j/T` is dropped** from the diagnostics, in the window classifier (§3.5) and in the declaration-time mapping (§3.6). Fitting its thresholds would need the PW routine on every column of every threshold draw, about 1,000–1,500 core-hours, which the budget cannot carry. The `BLOCK_LENGTH_CAPPED` rule (Annex B §2.5) still refuses capped samples, and GPH `d̂` remains.
   - **Tails.** The stochastic tails are exactly eight: maximum `g2`; minimum and maximum `g1`; maximum GPH `d̂`; maximum CUSUM-of-squares; maximum zero-day share; minimum and maximum pairwise correlation. At `K = 1` there are six, because the two correlation tails apply only when `K ≥ 2`. `K` and `T` are exact checks.
   - **Threshold run (§3.5 overridden: 300,000 draws, not 10⁶).** 300,000 generator draws per cell, in its own namespace.
     - The ranks are bound in integer arithmetic, with `q = floor(n / 100000)`: the upper tail is the order statistic of rank `n − q` = 299,997, and the lower tail is rank `q + 1` = 4.
     - A window value **equal** to a threshold is accepted.
   - **Refusal rate (§3.5 and §3.6 values overridden).**
     - Per tail, the marginal expected exceedance is at most 4/300,001 ≈ 1.33·10⁻⁵, with equality for continuous diagnostics. Over eight tails the expectation is at most about 1.07·10⁻⁴. This is an expected rate, not a bound, and it is within the classifier's 2·10⁻⁴ allocation.
     - The §3.6 sentence about a design whose law is exactly some cell's law now reads "accepted with probability at least about 1 − 1.07·10⁻⁴".
     - Held-out refusal can exceed development refusal by up to about 1.07·10⁻⁴ per cell.
     - A non-finite diagnostic is a refusal. Its rate is measured in development and held-out with the rest of DSR availability.
   - **Cost.** The threshold run's cost is measured in the re-pilot, including the Q5 and QJ generators. It is not assumed.
5. **Reported-only runs (§3.3, §3.4, §9) (BF1-4, BF1-6, BF2-7).** Each runs **2,000** replications per cell, once, at `T_C2`:
   - §9 power cells at a true annualised Sharpe of 0.5, 1.0 and 2.0, at `K` ∈ {1, 20}, under Q1-independent and, at `K = 20`, Q3;
   - §9 mixed nulls at `K` ∈ {2, 20};
   - §3.3 challenge cells, at `K` ∈ {2, 5, 20} where they need `K` (80 removed), plus every availability- or cap-demoted cell;
   - the §3.4 sensitivity rerun with mean blocks of 60, on the Q5 and QJ cells.

   These certify nothing. At 2,000 replications a rate near 0.025 has a standard error of about 0.0035, so a mixed null cannot show an excess smaller than about 0.007. This resolution is disclosed with the results.
6. **Running on the server (§4, §10) (BF1-4, BF1-5, BS1-4, BS1-5, BF2-2, BF2-4, BF2-5, BS2-1, BS2-4). These are preregistered run rules.**
   - **Machine.**
     - The calibration runs on the owner's rented server (2 shared vCPU, 4 GB RAM), with 2 workers.
     - The workers run at the lowest CPU priority (`nice 19`) under a memory cap (a systemd `MemoryMax` of 2.5 GB), so the forward-paper process always comes first.
     - The owner starts and stops the run. The AI never logs in.
   - **Pinned runtime (§4 "pinned runtime" overridden).**
     - The calibration runs inside one container image, pinned by digest. The image holds the whole userland: libc and libm, Python, NumPy and OpenBLAS. Nothing inside the image is updated during the run.
     - The host may install security updates. Automatic reboots are switched off for the run.
     - **Runtime identity, two parts (BF3-2, BS3-1).**
       - The **gating identity** consists of the decided A-V1 identity (interpreter, NumPy and OpenBLAS binaries, platform, CPU dispatch features, environment), the image digest, and the results of both canaries and the reference-vector suite. Chunk acceptance and A-V1's "frozen runtime" compare this part, and only this part.
       - **"Platform"** in the gating identity means the operating system and machine architecture inside the image (as `runtime_identity` already records them: system and machine). It does not include the host kernel release (BF4-3). The image's libc is not a separate field; it is gated through the image digest (BF5-1).
       - **Host provenance** is the CPU model, the microcode and the host kernel release. It is recorded in every chunk and disclosed, and never compared.
     - **Canaries.** A known-answer canary for `pow`, `exp` and `log` is added to the BLAS canary. The laptop's `V_CANARY` is not reused.
     - The runtime can be rebuilt only on a machine with the same CPU dispatch features. **Disclosed to the owner:** C2's real evaluation must run in the same image on such a machine (A-V1). If none is available, the qualification is void and must be redone.
   - **Two hashes, in order (BS2-1).**
     - **Run-definition hash.** Before the threshold run, the run definition is committed. Its SHA-256 is the run-definition hash. Threshold and development chunks are bound to it. The run definition contains:
       - this preregistration and the engine commit;
       - the generator code, the cell manifest and the seed specification;
       - the image digest and the exploration-data manifest;
       - the gating identity, with both canaries' expected values and the reference-vector expected outputs, all recorded on the server before the threshold run (BF3-1).
     - **Qualification-object hash.** At the freeze, the qualification object carries the run definition's runtime values unchanged. That is how they are "recorded at the D-19 freeze" in A-V1's sense. It adds the final chain head of every threshold and development chain, and their reduced results. Held-out chunks are bound to `qualification_object_sha256`.
     - **Changes.** Any later change to the runtime values voids every chunk bound to the run definition.
   - **Chunks.**
     - Work is cut into fixed chunks of 500 replications, one chain per (namespace, cell).
     - A chunk takes about 45 minutes, and about 90 minutes in QJ.
     - Seeds are per replication (§8), so a resumed run gives the same bytes as an uninterrupted one.
   - **Chunk file.** Each finished chunk is one file, written to a temporary name and then renamed. It records:
     - the binding hash (run-definition or qualification-object);
     - the namespace, the cell id and the replication range;
     - the gating identity and the host provenance;
     - the hash of its own content;
     - the hash of the previous chunk in its chain.

     The final chain head of each chain is recorded. Reduction reads the chunks in replication order.
   - **Integrity.**
     - A missing, duplicated, out-of-range or broken-chain chunk stops that chain.
     - On restart, an incomplete or corrupt chunk is deleted unread and recomputed from its seeds.
     - A chunk is accepted only if its recorded gating identity equals the one in the run definition.
   - **Start and resume.** On every start and resume, `v_runtime_check`, both canaries and the full reference-vector suite must pass against the values in the run definition before any chunk runs. A mismatch stops the run.
     - **After a host change.** A change of host provenance only (CPU model or microcode) is recorded and disclosed. The chunks count if the gating identity still matches.
     - If any part of the gating identity changes, the run stops. It resumes only on a machine whose gating identity matches. The chunks already accepted still count.
   - **Held-out visibility (P18-6).** "Access" means any display, export or aggregation of held-out event content before the final reduction. The following are not access: showing progress counts (chunks done per cell); hash-chain verification, which reads bytes but reports only pass or fail; a resume; and deleting and recomputing a corrupt chunk unread.
   - **Before the full run,** a test shows that an interrupted and resumed cell gives byte-identical results to a clean run. The re-pilot, on the server with forward paper running, measures:
     - the speed per replication;
     - the memory with 2 workers;
     - the threshold-run cost;
     - the `U_G` and DSR-availability rates in the thin categories (item 3);
     - a `U_G` rate across all groups, from at least one cell of each of Q1, Q2, Q2m, Q3, Q4, Q5 and QJ, for the escape estimate.
   - **Estimate (not yet measured on the server; BF3-3, BS3-3).** In laptop-core-hours:
     - **Base.** About 104 cells × 32,000 replications × about 4.5 s, about 4,200.
     - **Fixed extras,** about 300 in total: QJ's double cost (about 80), the reported-only runs (about 100), and the threshold run, which is to be measured (about 100 assumed).
     - **Escapes (BS4-1).** Add 25·E[ordinary escapes] + 50·E[QJ escapes].
       - An ordinary cell has one `U_G` test, so it escapes with the per-test probability: 0.21, 0.43 and 0.58 at p = 2·10⁻⁵, 5·10⁻⁵ and 10⁻⁴.
       - A QJ cell has two `U_G` tests on one shared path, so they may be dependent. No independence is assumed: each QJ cell is budgeted at between 0 and 50 hours, so the 2 QJ cells add 0–100 (BS5-1). The re-pilot measures the joint QJ escape rate directly.
       - With 102 ordinary cells (about 540, 1,100 or 1,480) and 2 QJ cells, this adds about 540–640, 1,100–1,200 or 1,480–1,580.
     - **Totals.** A shared server core is assumed about 1.2× slower, and the run uses 2 vCPU that forward paper leaves nearly free. The scenario totals are about **6,000–6,200, 6,700–6,800 or 7,200–7,300 server-core-hours, that is about 4, 4½ or 5 months**. With no escapes at all it would be about 5,400, or about 3½–4 months (BF4-1).
     - **Conditional until measured.** These scenarios are conditional on the assumed rates. The go-ahead estimate uses the measured all-groups `U_G` rate from the re-pilot (BF4-2).
     - A 4-vCPU server would halve the time. Its price is checked before it is offered to the owner.
7. **The cell count** is about 104, taken from the frozen manifest. Of these, Q5 and QJ use exploration-partition data only.
8. **Proposed §11 wording.** The last sentence of the §11 text becomes: "The declared |J_f| must be one of 1, 2, 5 or 20, and the qualification covers C2 only."

**Unchanged:**
- the claim (§1), apart from the `K` and `T` it covers and the challenge-cell definition (item 3);
- the null and the generators;
- seeds;
- the freeze order and the `AQTQ1` commitment, with the two hashes of item 6;
- the attempt rules;
- the screen;
- the mapping (§3.6), now at `K` ∈ {1, 2, 5, 20} and `T_C2`, without `L_j/T`.
