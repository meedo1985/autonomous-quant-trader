# D-19 calibration preregistration for C2 (revision 5)

**Status:** `AI PROPOSAL — NOT AN OWNER DECISION — NOT FROZEN — NOTHING BUILT OR RUN`

**Date:** 2026-10-04

**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`). The owner delegated drafting choices on 2026-10-03 and 2026-10-04, so every choice below is an `[AI default]` unless it cites a decided record.

**History:**

| Rev | Commit | Fable review | Sol review |
|---|---|---|---|
| 1 | `aa981d8` | DF1 `f54e84e` | DS1 `90029a4` |
| 2 | `71357d4` | DF2 `552af72` | DS2 `169985e` |
| 3 | `59f5f6c` | DF3 `2c2b11b` | DS3 `807ee4a` |
| 4 | `a841fb3` | DF4 `c26e59e` | DS4 `c518e94` |
| 5 | this revision | not yet re-checked | not yet re-checked |

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
| opposites | the first `floor(K/2)` columns are negated; `ρ = −0.9` between groups | `K ≥ 2` |
| unequal clusters | sizes {1,4} at `K = 5`, {5,15} at 20, {20,60} at 80; `ρ` 0.9 within a cluster, 0.2 between | `K ≥ 5` |
| one factor | loadings uniform on [0.3, 0.99] | `K ≥ 5` |

**Groups.**

| Group | Law | Dependence | `K` | `T` |
|---|---|---|---|---|
| **Q1** core | Gaussian, constant `σ` | every level that applies at that `K` | {1, 2, 5, 20, 80} | every `T` |
| **Q2** laws | t₅; skew-t ±1; GARCH-t₅; AR(1) with `φ` ∈ {0.2, 0.5} | independent; `ρ = 0.9`; opposites | {1, 2, 5, 20, 80} | `T_min`, `T_C2` |
| **Q3** heteroskedastic factor | common GARCH | one factor | {5, 20, 80} | `T_min`, `T_C2` |
| **Q2m** unequal moments | half the columns t₅, half Gaussian; scales `c_j` alternate 0.5 and 2 | independent | {2, 5, 20, 80} | `T_min`, `T_C2` |
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

**Channel for `<<OWNER Q-1>>` (by substitution into O-6a SPEC rev 5 `84fca9c` §3–§7):**
- **Prefix.** `AQTQ1`. The scriptPubKey is exactly `6a 25 41 51 54 51 31` followed by the 32-byte `qualification_object_sha256`, 39 bytes in all.
- **Keys and coins.** Attempt `n` ∈ {1, 2} has its own key `A_Qn`, bound coin `F_Qn` and deadline height `D_Qn`. These values are fixed at the preregistration's acceptance, as `<<ACCEPTANCE: A_Q1, F_Q1, D_Q1, A_Q2, F_Q2, D_Q2>>`.
- **Horizons (DF4-2).**
  - O-6a's "after signing" becomes "after acceptance of this preregistration".
  - Both "before C2 ends" and "before C2's evaluation is final" become "before the owner's accept or reject of certification (§12 item 4)".
  - `D_Qn` must be above the acceptance height. `D_Q2` is fixed in the attempt-2 record before its post.
- **Timing.** The held-out run starts only after the O-6a freeze read for `T_Qn` **and** the publication of the drand round.
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
- At `M_max ≈ 1,143`, which is Fable's count of 371 cells at `T_min = 365` (DF4-6), the targets are:

  | Test | `N` | τ |
  |---|---|---|
  | error | 20k | about 0.01763 |
  | DSR availability | 20k | about 0.00113 |
  | `U_G` | 20k | about 0.000148 |
  | `U_G` | 40k | about 0.000415 |

  At `τ_G(20k)`, a 22k development run must show no `U_G` event. The exact values are printed from the manifest. Q2m adds about 8 cells.

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
