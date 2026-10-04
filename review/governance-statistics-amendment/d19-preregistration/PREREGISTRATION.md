# D-19 calibration preregistration for C2 (revision 3)

**Status:** `AI PROPOSAL — NOT AN OWNER DECISION — NOT FROZEN — NOTHING BUILT OR RUN`
**Date:** 2026-10-04
**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`). The owner delegated drafting choices on 2026-10-03 and 2026-10-04, so every choice below is an `[AI default]` unless it cites a decided record.

**History:**

| Rev | Commit | Fable review | Sol review | Adjudication |
|---|---|---|---|---|
| 1 | `aa981d8` | DF1, SOUND WITH FIXES (`f54e84e`) | DS1, UNSOUND (`90029a4`) | |
| 2 | `71357d4` | DF2, SOUND WITH FIXES (`552af72`) | DS2, UNSOUND (`169985e`) | |
| 3 | this file | not yet re-reviewed | not yet re-reviewed | applies `ADJUDICATION_71357D4.md` and owner decision U-1 (`OWNER_DECISION_UPROC_SCOPE.md`, `8e04dd8`) |

**Authority and limits:**
- `d19-recommendation/OWNER_STEP0_DECISION.md` (R19-1, R19-2) allows designing the calibration.
- Building, a pilot, or any simulation result needs the owner's **separate go-ahead** (§12).
- No human statistician reviews this. Two AI model families do (R19-2), which is weaker, and that is disclosed.
- Only synthetic data and exploration-partition BTC/ETH data are used. No confirmation or lockbox data is read.

**What it binds:**
- Annex B (`aqt.dsr.bootstrap_max.candidate.v2`);
- Annex A: P18-0..P18-7, A-B7, and A-U1 (U-1);
- Annex C: the gates.

**What it supplies:**
- `T_min`;
- `family_block_rule`;
- `z_crit`;
- the `U_proc^R` allocation;
- the certification route (§11).

## 1. The claim, and its conditions

Under the all-zero-mean global null, in **every** qualifying cell (§3), the claim holds at a family-wise one-sided 95% confidence. That confidence covers every enumerated test and both permitted attempts (§6).

1. **Error.** For each declared family `f`, the upper bound on `P_0(E_f)` is at most 0.025, where `E_f = A_f ∩ {z_f* ≥ z_crit}` (P18-6). It follows that `P_0(E) ≤ 0.05` per cycle, for any dependence between the two families.
2. **No result.** The upper bound on `P_0(U_proc^R)` is at most 0.005 per family, so at most 0.01 per cycle (A-U1).
   - `U_proc^R` covers DSR availability, including the classifier (§3.5), and gates G-1, G-2, G-4, G-10, G-12 and G-13.
   - Each of these is either simulated in every replication or proved deterministically (§7.1).

**What is *not* claimed:**
- **No certified rate for the screened gates.** Gates G-3, G-5, G-6, G-7, G-8, G-11 and G-14 have no certified no-result rate. They are screened before declaration (§7.2), and an unavailability on the real window is recorded without a rate (A-U1).
- **The classifier is a minimum condition.** Passing it (§3.5) is necessary, not proof, that C2's law is covered.
- **Some cells are not certified.** A cell whose cap rate in development is above τ_DSR/4 is a challenge cell, so it is not certified. Its availability is reported.
- **Only listed sizes and gaps are covered.** The declared `|J_f|` must be in {1, 5, 20, 80}, and C2's `g` must equal the frozen value. Otherwise the declaration is invalid.

**Failure.** If the held-out certification fails, the method does not qualify, and promotion stays blocked. That is a valid result.

## 2. One replication

1. **Market and legs.** Generate one market and its legs (§3.1). Every column of `X` has population mean exactly 0.
2. **Annex B rules 1–4.** Apply Annex B §2.5 rules 1–4. These need the block lengths.
3. **Classifier.** Apply the classifier (§3.5). A refusal is a `U_proc^R` event.
4. **The rest of Annex B.** Apply Annex B rules 5–6, then `S0`, `D_j`, `z_j`, the nominee (P18-4) and `E_f`, with `B = 2000`. The inner algorithm is the frozen build code. Store `z_f*`.
5. **Route-R gates.** Evaluate every route-R gate on the nominee, whatever the DSR or other outcomes are (P18-7). G-12 is evaluated for each `H` ∈ {24, 72, 168} (DS2-7).
6. **Record.** Record events, cause codes, `L`, `L/T`, and the diagnostics.

Crashes are not modelled (P18-7).

## 3. Cells

### 3.1 Market and leg generators (route R)

**BTC returns.** `r_t = σ_t·ε_t`.
- `σ_t` is either constant at 3.5% per day, or common GARCH(1,1) with α = 0.10 and β = 0.85, scaled so its unconditional value is 3.5%.
- `ε_t` follows the cell's marginal law, standardised.
- Every series is started at its unconditional state, with a 500-day burn-in that is discarded.

**Marginal laws.**
- Gaussian.
- Student-t with ν = 5.
- **Skew-t:** the Azzalini skew-t with ν = 5 and shape `α_s`. `α_s` is frozen numerically so the standardised skewness is ±1. It is computed by the frozen generator code, and its value is recorded in the manifest.
- **AR(1):** `x_t = φ·x_{t−1} + sqrt(1 − φ²)·e_t`.
- **GARCH:** the common `σ_t`, with t₅ innovations.

**Benchmark leg.** `b_t = e_t·r_t`, where `e_t = min(1, 0.40/(σ̂_t·sqrt(365)))`.
- `σ̂_t` is a daily EWMA with a 7-day half-life, from past returns only.
- It is seeded at 3.5%.
- It is a daily stand-in, not the canonical hourly benchmark.

**E-DIFF columns.** `X_j,t = 0.3·σ_t·x_j,t`.
- `x_j,t` follows the cell's cross-column and serial law, with mean 0 and unit variance.
- Factor loadings are drawn once per replication from the `"columns"` stream.

**Candidate legs.** `C_j = b + X_j`, about 2.3% per day.

**Equity.** A path at or below 0 is `INVALID_SERIES`, a `U_proc^R` event. No probability of that is claimed.

**ETH.** ETH legs are not generated for route R. G-3 is screened (§7.2).

### 3.2 Qualifying cells

**Declarable family size.** `|J_f|` must be one of {1, 5, 20, 80}. This is checked under P18-1 (DF2-4).

**`T` levels.** The `T_min` candidates are {365, 548, 730}, plus 1095 and `T_C2`.
- `T_C2 = 1247 − g`. `g` is fixed by the frozen gap rule from exploration data before the threshold run.
- A different `g` at C2 makes the declaration invalid.
- Levels below `T_min` are dropped.

**Dependence levels for `x`** (O18-4, DF2-3):
- independent;
- equicorrelated with `ρ` ∈ {0.5, 0.9, 0.99};
- **near-duplicates:** pairs with `ρ = 0.999`;
- **exact duplicate:** one pair of identical columns;
- **opposites:** half the columns negated, with `ρ = −0.9` between the halves;
- **unequal clusters:** clusters of sizes `K/4` and `3K/4`, with `ρ = 0.9` within a cluster and `0.2` between them;
- **one factor:** loadings uniform on [0.3, 0.99].

At `K = 1` only "independent" applies. Pair and cluster levels need `K ≥ 5`.

**Groups.** All groups are family-agnostic except Q5.

| Group | Law | Dependence | `K` | `T` |
|---|---|---|---|---|
| Q1 core | Gaussian iid, constant `σ` | every level | every allowed `K` | every `T` |
| Q2 laws | t₅; skew-t ±1; GARCH-t₅; AR(1) `φ` ∈ {0.2, 0.5} | independent; `ρ = 0.9`; opposites | every allowed `K` | `T_min`, `T_C2` |
| Q3 factor and heteroskedasticity | common GARCH `σ_t` | one factor | {5, 20, 80} | `T_min`, `T_C2` |
| Q4 mixed column | one AR(1) `φ = 0.5` column among iid columns | none | {5, 20, 80} | `T_min`, `T_C2` |
| Q5 semi-empirical, family-labelled | §3.4, with trend-rule and vol-rule libraries | none | {5, 20, 80} | `T_min`, `T_C2` |

**Qualifying rule.** A cell is qualifying only if its development cap rate is at most τ_DSR/4. Otherwise it is a challenge cell (§1).

**Two families.** The joint two-family generator of O18-4 is replaced by P18-7's per-family allocation option [AI default, shown to the owner].

**Manifest.** The frozen manifest script enumerates every cell.

### 3.3 Challenge cells (reported, never certified)

- Long memory: ARFIMA with d = 0.3, in all columns.
- One ARFIMA column among iid columns, at `K` ∈ {5, 20, 80}. Both block rules are reported.
- A structural break: the variance doubles at `T/2`.
- A two-state Markov volatility regime.
- Infinite variance: t with ν = 1.8.
- Sparse columns: active on 5% of days.
- Any cell whose development cap rate is above τ_DSR/4.

### 3.4 Q5 semi-empirical cell (exploration data only; exact null)

1. **Returns.** Draw a joint stationary bootstrap (mean block 20) of demeaned daily BTC and ETH returns from the **exploration partition only**.
2. **Exposures.** `K` trend-rule or vol-rule exposures, according to the family label. They are applied causally to the BTC path. The benchmark is the §3.1 stand-in. The raw columns are `X̃_j,t = (e_j,t − e^b_t)·r_t`.
3. **Signs.** Draw `s_t ∈ {−1, +1}`, constant within geometric blocks of mean 20. The signs are shared across columns and drawn from the `"sign"` stream independently of the path. The first block starts at day 1 with a fresh sign. Set `X = s·X̃`, so `E[X] = 0` exactly. Then `C_j = b + X_j`.
4. **Disclosed side effects:**
   - each column's skewness becomes zero in distribution;
   - the implied candidate exposure ranges over [−1, 2];
   - serial sign structure across blocks is lost.
5. **Sensitivity.** A run with mean blocks of 60 is reported.

### 3.5 Supported-law classifier (D-18 O18-2, A-B7)

**Order.** The classifier runs after Annex B rules 1–4 and before rule 5. Its diagnostics, computed on `X`, are:

| Diagnostic | Estimator | Tail(s) |
|---|---|---|
| `K` | declared, must be allowed | exact |
| `T` | complete days | exact |
| maximum over columns of `L_j/T` | `L_j` from Annex B §2.2 | upper |
| maximum excess kurtosis | sample `g2 = m4/m2² − 3` | upper |
| skewness | `g1 = m3/m2^1.5`; per column minimum and maximum | lower (minimum), upper (maximum) |
| long memory | GPH `d̂`, bandwidth `floor(T^0.5)`; maximum over columns | upper |
| variance break | CUSUM of squares, `max_k \|Σ_{t≤k} x_t² / Σ x_t² − k/T\|`; maximum over columns | upper |
| zero days | share of days with `X_j,t = 0`; maximum over columns | upper |
| pairwise correlation (`K ≥ 5`) | Pearson; minimum and maximum over pairs | lower (minimum), upper (maximum) |

**Thresholds** (DF2-2).
- A separate **threshold run** uses the generator only (no Annex B inner bootstrap), with 10⁶ draws per qualifying cell, from its own namespace (§8).
- It is run for each `T_min` candidate before the §5 choices.
- **Per cell and tail,** the threshold is the order statistic `ceil(0.99999·n)` (upper tail) or `floor(0.00001·n) + 1` (lower tail). The frozen threshold is the extreme of these over qualifying cells.
- With at most 12 tails at 10⁻⁵ each, each cell's refusal rate is designed to be at most about 1.2·10⁻⁴. This sits inside a classifier budget of 2·10⁻⁴ per cell, within the DSR-availability share, and is checked again in development and in held-out runs.

**Refusal.** A non-finite diagnostic is a refusal. A refusal is cause `UNSUPPORTED_LAW`, a `U_proc^R` event.

## 4. Qualification object and freeze order

**What the object contains:**
- the method build (Annex B code at a commit hash, with the `<<OPEN D-20>>` bindings);
- this preregistration at its accepted hash;
- the generator code and its hash, and the frozen `α_s`;
- the manifest, with its cells and enumerated tests;
- the threshold-run outputs and the classifier thresholds;
- the exact-binomial target script and its outputs;
- `family_block_rule`, `T_min` and `z_crit`;
- the allocation;
- the screen code and its settings;
- the seed specification.

`qualification_object_sha256` is the SHA-256 of the canonical JSON manifest of the object's file hashes.

**Freeze order:**
1. The owner accepts this preregistration after its reviews.
2. The owner gives the go-ahead for the build and a measured pilot. The build is reviewed under §16.
3. The threshold run (§3.5) is done.
4. Development is done (§5).
5. **Freeze and commit.**
   - The owner posts `qualification_object_sha256` once, using the O-6a mechanism on a dedicated key `A_Q` with prefix `AQTQ1` (§8).
   - Held-out seeds mix in the drand round that follows the post.
6. Held-out certification is run (§6).
7. **Accept or fail.**
   - After a failure, at most **one** further attempt is allowed. It needs a recorded change to the object, a new namespace and a new post.
   - Every attempt uses α = 0.025/`M`.
   - No re-tuning against a seen held-out set is allowed (P18-6).

## 5. Development phase [frozen rules]

**Targets.**
- For each test `i`, a frozen script computes τ_i. τ_i is the largest true rate whose probability of passing held-out at α = 0.025/`M` is at least 0.999, given that test's `N_i` and target.
- Illustrative values at `M = 1000` and `N = 20,000` (Fable DF2-1): about 0.0177 for the error test, and about 0.00113 for a 0.0035 share. For the 0.0015 share the target is about 0.00041, at `N = 40,000`.

**Replications.**
- Every qualifying cell gets **22,000** development replications. There is no conditional stage, which closes DS2-5.
- `z_f*` is stored for every replication.

**Choices, in order:**
1. **`family_block_rule`.** Choose largest or median, by the smaller worst-cell `P̂_0(E_f)` at a provisional `z = 1.96`. Ties go to largest. The one-ARFIMA challenge cells are reported under both rules.
2. **`T_min`.** The smallest candidate at which every qualifying cell at that `T` meets every τ_i. Test `i` is met when its development **90% one-sided upper confidence bound** is at most τ_i. This guards against the winner's curse (DF2-8).
3. **`z_crit`.** The smallest decimal on a 0.001 grid at which every qualifying cell's 90% upper bound on `P_0(E_f)` is at most its τ_i. It is computed from the stored `z_f*`.
4. **Joint pass probability.** Report the probability that all held-out tests pass jointly, computed from the 90% upper bounds, before the freeze.
5. **No qualifying choice.** If no choice meets every τ_i, the method does not qualify.

## 6. Held-out certification and the confidence family

**Tests.**
- Every test is enumerated as a (cell, family-or-agnostic, bound) triple. The bounds are:
  - `P_0(E_f)` ≤ 0.025;
  - DSR availability including the classifier ≤ 0.0035;
  - the other `U_proc^R` gates ≤ 0.0015.
- Q1–Q4 tests count once and certify both families. Q5 tests count once per family.
- `M` is the count from the manifest. The estimate is 700–1,000.

**Bounds.** Each bound is the one-sided Clopper–Pearson upper bound at α = 0.025/`M`, for every attempt. Over at most two attempts, the family-wise level is at least 95%.

**Replications.** `N = 20,000` per cell. Where the 0.0015 share is the binding test, as identified in development and frozen in the manifest, `N = 40,000`.

**Acceptance.** Every test must be within its target.

## 7. No-result routes (A-U1)

**Per-family `U_proc^R` allocation:**

| Share | Covers |
|---|---|
| 0.0035 | DSR availability, including at most 2·10⁻⁴ for the classifier |
| 0.0015 | gates G-1, G-2, G-10 and G-12 (all three `H`) |
| 0 | route D |

The total is 0.005 per family and 0.01 per cycle.

### 7.1 Gate-by-cause matrix

| Gate | Cause | Route |
|---|---|---|
| DSR | Annex B rules 1–6; `UNSUPPORTED_LAW` | R |
| G-1 | no Sharpe on a leg; block-length failure; invalid replicate | R |
| G-2 | non-finite MDD (`INVALID_SERIES`) | R |
| G-4 | `n = 0` (impossible when `T ≥ 365`) | D |
| G-10 | `T < 16` (impossible); a trial with no Sharpe on a half | D; R |
| G-12 | `γ0` rounds to 0; validation; any `H` | R |
| G-13 | benchmark hash mismatch | D |
| G-3, G-5, G-6, G-7, G-8, G-11, G-14 | every cause | screened (§7.2), excluded from the target (A-U1) |

**Route D** is proved by written arguments.

**Input integrity** (DF2-12) is checked by the engine at evaluation start: complete hourly bars, finite values, and the manifest hash.
- A failure in the **input bars** is `DATA_INTEGRITY`, a `U_ops` event.
- A non-finite value in a **derived** series is `INVALID_SERIES`, a `U_proc^R` event.

### 7.2 The declared-strategy screen (A-U1)

**When.** It runs before the declaration is committed, on the actual intended trial set.

**Paths.** It uses `n_S = 30` simulated null **hourly** BTC/ETH paths (DS2-3, DF2-6). They are built as follows:
- A joint hourly stationary bootstrap (mean block 168 h) of exploration-partition 1h bars, from their demeaned hourly log returns.
- Signs, shared between BTC and ETH, are applied in geometric blocks of mean 24 h, so the paths have exactly zero drift.
- Prices are rebuilt from the signed returns. Volume is resampled with the bars and not sign-flipped.

**What is evaluated.** Each trial is run under the event contract C-6 on each path. Every screened gate is evaluated in full, at production draw counts: 500 for G-11, 500 for G-14, and stressed runs for G-5..G-7.

**Outcome.** Any unavailability makes the set invalid (P18-1). No `m` is spent.

**Seed.** The seed is `SHA256(cj({"stream": "screen", "trial_set_sha256": <hex>}))`, with no nonce. Every screen run is recorded, and the declaration lists all of them.

**Detection power, disclosed.** A per-path unavailability rate of 10% is caught with probability 0.96, and a rate of 1% with probability 0.26.

## 8. Seeds (exact)

**Canonical JSON (`cj`).**
- UTF-8, keys sorted, and no insignificant whitespace.
- Integers in decimal.
- Hashes as lowercase hex strings.

**Namespaces.**
- `"d19-threshold-v1"` for the threshold run;
- `"d19-dev-v1"` for development;
- `"d19-heldout-v1"` and `"d19-heldout-v2"` for the held-out attempts.

**Outer seed.**

```
seed = SHA256(cj({"anchor": <hex>, "cell_id": <str>, "ns": <str>, "rep": <int>}))
```

The `anchor` depends on the run:
- threshold and development runs use the preregistration hash;
- held-out runs use `SHA256(cj({"beacon_randomness": <hex>, "qobj": qualification_object_sha256, "round": <int>}))`. The round is the first drand round scheduled at or after `T_Q + 24h`, where `T_Q` is fixed from the `AQTQ1` post exactly as in O-6a SPEC §5. The drand chain is the one fixed for C2 (DRAFT §2.0) (DF2-7).

**Streams.**

```
stream = SHA256(cj({"seed": <hex>, "stream": <name>}))
```

- `<name>` is one of `"market"`, `"sign"`, `"columns"`, `"g1_ci"` or `"inner"`.
- Philox key: the first 16 bytes of the stream hash, big-endian.
- `"g1_ci"` enters the production `paired_sharpe_ci` stream as its trial seed.

**Inner Annex B family seed.** It is built by the production construction, with these synthetic fields:
- `protocol_hash`: the preregistration hash;
- `family_id`: the cell's family label, or `"agnostic"`;
- `cycle_id`: `"D19"`;
- `window_id`: the cell id;
- `data_manifest_hash`: the outer seed;
- `trials`: for each `j`, `{"configuration_hash": SHA256(cj({"j": j, "seed": s, "tag": "c"})), "hypothesis_hash": SHA256(cj({"j": j, "seed": s, "tag": "h"})), "trial_id": "t%03d" % j}`.

**R-7 extension.** The extension uses `round = rep` and `beacon_randomness = SHA256(cj({"seed": s, "tag": "beacon"}))`.

**Reproducibility.** A result that cannot be reproduced is void (Constitution §27).

## 9. Reported, not certified

- **Power cells.** One trial has a true annualised E-DIFF Sharpe of 0.5, 1.0 or 2.0. They are run at `K` ∈ {1, 20, 80}, `T` ∈ {`T_min`, `T_C2`}, for laws Q1-independent and Q3.
- **Mixed nulls.** `K − 1` trials have an annualised Sharpe of −0.5, and one has 0. They use the same grid.
- **The rest:**
  - the challenge cells;
  - the classifier refusal rates;
  - the cap and failure rates per column, by `K`;
  - `P_0(E_f | A_f)`;
  - the reach-pick rate.

## 10. Compute

**What drives the cost:**
- Development and held-out each run about 20,000 replications per cell, so development costs about as much as held-out (DF2-8).
- The route-R gates add cost: G-1 runs 2,000 replicates per nominee, G-10 runs 12,870 splits at `K ≥ 20`, and G-12 runs three horizons.
- The threshold run is cheap, because it has no inner bootstrap.
- The screen runs per declaration. It covers up to 80 trials × 30 paths × (1 + 500 + 500 + 3) hourly runs, which is heavy. It is measured in the pilot.

**Estimate.** About **2,000–6,000 CPU-core-hours** for the calibration, before the screen. It has not been measured.

**Before the go-ahead,** a measured pilot is required. It covers the largest cell, a median cell, the threshold run, and one screen of an 80-trial set. The owner then chooses:
- local or rented compute, with a quoted price;
- whether to reduce `N`, with the targets recomputed.

## 11. Amendment wording proposed for `<<OPEN D-19 route>>` (A-U1)

> "P18-7's procedure no-result target of at most 0.01 per cycle applies to U_proc^R. U_proc^R is the unavailability of the DSR method, including the supported-law classifier, and of gates G-1, G-2, G-4, G-10, G-12 and G-13. It is certified as specified in the D-19 preregistration bound here by hash: by simulation in every replication, and by written deterministic arguments for G-4, G-13 and the bounds on T.
>
> Gates G-3, G-5, G-6, G-7, G-8, G-11 and G-14 are excluded from that target. They are governed by a fail-closed screen of the actual trial set on simulated null hourly paths, run before the declaration is committed. Their unavailability on the window is a procedure no-result event, recorded with its cause code, without a certified rate.
>
> The declared |J_f| must be one of 1, 5, 20 or 80."

## 12. What the owner decides, and when

1. **Accept this preregistration** after its reviews. This freezes the claim, cells, rules and acceptance before any result exists (Constitution §1 line 31).
2. **Go-ahead** for the build and the measured pilot. After the pilot, decide whether to run in full, and on local or rented compute.
3. **The `AQTQ1` post at freeze.** It costs two Bitcoin fees and is made by the owner (§4, §8).
4. **Accept or reject the certification result.** A failure leaves promotion blocked.

Nothing here starts a cycle, reads confirmation or lockbox data, or authorizes trading.
