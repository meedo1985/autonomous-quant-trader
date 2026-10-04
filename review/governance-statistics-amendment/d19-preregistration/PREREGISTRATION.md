# D-19 calibration preregistration for C2 (revision 2)

**Status:** `AI PROPOSAL — NOT AN OWNER DECISION — NOT FROZEN — NOTHING BUILT OR RUN`
**Date:** 2026-10-04

**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`). The owner delegated drafting choices on 2026-10-03 and 2026-10-04. Every choice below is therefore an `[AI default]` unless it cites a decided record.

**History:**
- Rev 1 `aa981d8` was reviewed twice:
  - Fable DF1: SOUND WITH FIXES (`f54e84e`);
  - Sol DS1: UNSOUND (`90029a4`).
- Rev 2 applies `ADJUDICATION_AA981D8.md` and has not yet been re-reviewed.

**Authority and limits:**
- `d19-recommendation/OWNER_STEP0_DECISION.md` (R19-1, R19-2) allows designing the calibration.
- Building the engine, running a pilot, or generating any simulation result needs the owner's **separate go-ahead** (§12).
- No human statistician reviews this. Two AI model families do (R19-2), which is weaker, and this is disclosed.
- Only synthetic data and exploration-partition BTC/ETH data are used. No confirmation or lockbox data is read, by the design or by the run.

**What it binds:**
- Annex B: the method `aqt.dsr.bootstrap_max.candidate.v2`.
- Annex A: P18-0..P18-7 and A-B7.
- Annex C: the gates.

**What it supplies to DRAFT_WORDING:**
- `T_min`;
- `family_block_rule`;
- `z_crit`;
- the `U_proc` allocation;
- the certification route (§7, §11).

## 1. The claim, and its conditions

**The claim.** Under the all-zero-mean global null, in **every** qualifying cell (§3), at simultaneous one-sided 95% confidence over every enumerated test (§6):

1. **Error.** For each declared family `f`, the upper bound on `P_0(E_f)` is at most 0.025, where `E_f = A_f ∩ {z_f* ≥ z_crit}` (P18-6). Then `P_0(E) ≤ 0.05` holds for any dependence between the two families.
2. **No result.** For each family, the upper bound on the `U_proc` share computed in simulation is at most 0.005, so the cycle's bound is at most 0.01 by the union bound. Here `U_proc` covers DSR availability, the classifier and the route-R gates (§7).

**The claim holds only under all of these conditions, stated openly:**
- The real window passes the classifier (§3.5). Passing is necessary, not proof, that C2's law is covered by the cells.
- Gates in route S are guaranteed by a **screen** of the declared strategies (§7), not by a probability bound. The amendment must authorise this (§11), and it departs from P18-7's "calibrated" wording for those gates.
- Cells in which the block-length cap binds in at least 1% of development replications are challenge cells, not qualifying cells (Annex B §2.6). Their availability is reported but not certified.
- The declared family size `|J_f|` must be a certified `K` (§3.2).

**If any held-out test fails,** the method does not qualify and promotion stays blocked (the 2026-09-15 decision stands). That outcome is valid and is not tuned away.

## 2. One replication

1. **Market and legs.** Generate one market (§3.1): BTC and ETH daily returns on one day index. From it, build:
   - the benchmark legs;
   - the candidate legs `C_j = b + X_j`;
   - the E-DIFF matrix `X`.

   Every column of `X` has population mean exactly 0. This is the location-shift null.
2. **Classifier.** Apply the classifier (§3.5) to the generated window. A refusal is a `U_proc` event.
3. **Annex B.** Apply Annex B in full with `B = 2000`:
   - the §2.5 checks, in order;
   - the frozen block rule;
   - `S0`, `D_j` and `z_j`;
   - the nominee (P18-4);
   - the event `E_f`.

   The inner algorithm is the frozen build code.
4. **Route-R gates.** Evaluate every route-R gate (§7.1) on the nominee, regardless of the DSR or other outcomes (P18-7).
5. **Record.** Record `A_f`, `E_f`, every gate's availability with its cause code, `L` and `L/T`, and the classifier's diagnostics.

Crashes and infrastructure faults are not modelled (P18-7).

## 3. Cells

### 3.1 Market and leg generators [AI default]

All laws are daily, at realistic scale.

- **BTC return.** `r_t = σ_t·ε_t`.
  - `σ_t` is either constant, at 3.5% per day, or common GARCH(1,1) (α = 0.10, β = 0.85, unconditional 3.5%), as the cell sets.
  - `ε_t` follows the cell's marginal law, standardised to mean 0 and variance 1.
- **ETH return.** `r^E_t = 1.1·r_t + 0.5·σ_t·η_t`, where `η_t` is iid and standardised, with the same marginal law.
- **Benchmark leg.** `b_t = e_t·r_t`.
  - `e_t = min(1, 0.40/(σ̂_t·sqrt(365)))`, where `σ̂_t` is the `EWMA_168h` estimator at daily resolution: a half-life of 7 days, computed from past returns only.
  - This is a daily stand-in for `VOL_TARGET_BUY_AND_HOLD`, used for the gates' leg algebra. It is not the canonical hourly benchmark.
  - The ETH benchmark is built the same way on `r^E`.
- **E-DIFF columns.** `X_j,t = s_x·σ_t·x_j,t`, with scale `s_x = 0.3`, where:
  - `x_j,t` follows the cell's cross-column and serial law;
  - every column has mean 0;
  - in common-factor cells, `x_j,t = λ_j·ε_t + sqrt(1 − λ_j²)·u_j,t`.
- **Candidate legs.**
  - `C_j = b + X_j`, giving daily standard deviations of about 1–2%.
  - Equity paths `Π(1 + C)` stay positive with probability above `1 − 10⁻⁹` at this scale. Any path at or below 0 is recorded as `INVALID_SERIES`, a `U_proc` event.
- **ETH candidate legs.** `C^E_j = b^E + X^E_j`, where `X^E` uses the same column law as `X`, on `σ_t`.
- **G-12.** The decision horizon is `H = 24`.

### 3.2 Qualifying cells [AI default]

**Levels.** `K` ∈ {1, 2, 3, 5, 10, 20, 40, 80}.
- **The declared family size must be one of these values.** This is a validity check under P18-1 (DF1-6).
- `P_0(E_f)` is not monotone in `K` (FB1-16), so the claim covers only these `K`.
- No such restriction is possible for `ρ` or the law. That residual is disclosed in §1 through the classifier.

**`T` levels.**
- The `T_min` candidates are {365, 548, 730}; 1095 and `T_C2` are also levels.
- `T_C2 = 1247 − g`, where `g = gap_embargo.value_days`, computed by the frozen gap rule from exploration data before the freeze.
- If the `g` declared at C2 differs from this value, C2 is not covered.
- Levels below `T_min` are dropped after §5.

**Groups.** Each group is one family-labelled set; a cell belongs to exactly one group.

- **Q1 (core grid).** Gaussian iid `ε`, constant `σ`.
  - **Levels:** every `K` and every `T`.
  - **Dependence** `x`: independent, or equicorrelated with `ρ` ∈ {0.5, 0.9, 0.99}.
  - `K = 1` has a single dependence level.
- **Q2 (laws).** The laws are:
  - Student-t, ν = 5;
  - skew-t with skewness +1, and with skewness −1;
  - GARCH, meaning common `σ_t` with t₅ innovations;
  - AR(1) with `φ` ∈ {0.2, 0.5}.

  **Levels:** `K` ∈ {1, 5, 20, 80} and `T` ∈ {`T_min`, `T_C2`}, under independent dependence and under `ρ = 0.9`.
- **Q3 (factor with heteroskedasticity, DF1-8).** Common GARCH `σ_t`, a common-factor `x`, and loadings `λ_j` uniform on [0.3, 0.99].
  - **Levels:** `K` ∈ {5, 20, 80} and `T` ∈ {`T_min`, `T_C2`}.
- **Q4 (mixed column).** One AR(1) column with `φ = 0.5` among iid columns.
  - **Levels:** `K` ∈ {2, 3, 20} and `T` ∈ {`T_min`, `T_C2`}.
- **Q5 (semi-empirical).** See §3.4.
  - **Levels:** `K` ∈ {5, 20, 80} and `T` ∈ {`T_min`, `T_C2`}.

**Cell count and costliest cell.**
- After `T_min` is fixed, there are roughly 200–260 cells.
- The frozen manifest script enumerates them exactly.
- The largest-`K`, shortest-`T` cell, `K = 80` at `T = 365`, qualifies only if `T_min = 365` (DS1-6).

### 3.3 Challenge cells (reported, never certified)

These cells are reported with every rate, but no target applies to them:
- long memory: ARFIMA with d = 0.3, in all columns;
- **one** ARFIMA column among iid columns, at `K` ∈ {2, 20, 80} (FB1-15, DF1-7). The block-rule choice in §5 reports its rate under both candidate rules;
- a structural break: the variance doubles at `T/2`, with mean 0;
- a regime switch: two-state Markov volatility;
- infinite variance: Student-t with ν = 1.8;
- sparse columns, active on 5% of days in runs (FB1-6);
- any cell in which the cap binds in at least 1% of development replications. Its availability is reported (DF1-13).

### 3.4 Semi-empirical cell Q5 (exploration data only; exact null)

1. **Returns.**
   - BTC and ETH daily returns are taken **from the exploration partition only**.
   - A joint stationary bootstrap with mean block length 20 is applied, keeping BTC and ETH on the same days.
   - The returns are demeaned before resampling.
2. **Exposures.**
   - The `K` candidate exposures are trend and volatility rules on lookback grids. They are applied causally to the resampled BTC path.
   - The benchmark is the daily stand-in of §3.1.
   - The raw differences are `X̃_j,t = (e_j,t − e^b_t)·r_t`.
3. **Exact null (DS1-3, DF1-4).**
   - Draw signs `s_t ∈ {−1, +1}`, constant within geometric blocks of mean length 20, shared by all columns, and drawn from a stream independent of the path. Set `X_j,t = s_t·X̃_j,t`.
   - Then `E[X_j,t] = E[s_t]·E[X̃_j,t] = 0` exactly.
   - Magnitudes, heteroskedasticity, the cross-column structure and serial structure within blocks are kept. Serial sign structure across blocks is lost; this is disclosed.
   - The legs are rebuilt as `C_j = b + X_j`.
4. **Sensitivity.** The cell is also run with mean block length 60, for both the bootstrap and the signs. This run is reported, not certified (DF1-8).

### 3.5 Supported-law classifier (D-18 O18-2, A-B7; DS1-1)

**Rule.** The engine computes a diagnostic vector on the real window's `X` at evaluation, before Annex B §2.5 rule 1. If any component lies outside its frozen threshold, the family is refused with cause `UNSUPPORTED_LAW`. That refusal is a `U_proc` event and a family result of `UNAVAILABLE`.

**Diagnostic vector:**
- `K` and `T`;
- the maximum over columns of realised `L/T`;
- the maximum over columns of excess kurtosis;
- the minimum and maximum over columns of skewness;
- the maximum over columns of the GPH long-memory estimate `d̂`;
- the maximum over columns of a CUSUM-of-squares variance-break statistic;
- the share of zero days, maximum over columns;
- the mean pairwise correlation.

**Thresholds.**
- Each threshold is the maximum, over qualifying cells, of that cell's 99.99th percentile of the component in its **development** replications. A pooled percentile could refuse far more often in particular cells, so it is not used. With 10 components, each cell's refusal rate is then about 0.001 at most, inside the 0.0035 share.
- The thresholds are frozen with the qualification object.
- In held-out runs, the refusal rate is measured in every replication, inside the DSR-availability share.

**Cell rule.** A cell is qualifying if, and only if:
- its law is stationary, short-memory and finite-variance, with no break and no sparse column;
- the block-length cap binds in less than 1% of its development replications.

## 4. Qualification object and freeze order

**The qualification object** contains:
- the method build (Annex B code at a commit hash, with the `<<OPEN D-20>>` bindings);
- this preregistration, at its accepted hash;
- the generator code and its hash;
- the cell manifest with its hash, including the enumerated test list (§6);
- the classifier's code and thresholds;
- the exact-binomial target script and its outputs (§5);
- `family_block_rule`, `T_min` and `z_crit`;
- the allocation (§7);
- the screen code and its parameters (§7);
- the seed specification (§8).

`qualification_object_sha256` is the SHA-256 of the object's canonical JSON manifest of file hashes.

**Freeze order:**
1. This preregistration is reviewed (R19-2) and accepted by the owner.
2. The owner gives the go-ahead for the build and a measured pilot (§10). The engine is built and reviewed under §16.
3. The development phase runs (§5), in the development namespace only.
4. Freeze. The object is hashed and committed with its record. No held-out seed can exist before this point, because held-out seeds include `qualification_object_sha256` (§8).
5. Held-out certification runs (§6).
6. The result is accepted or fails.
   - After a failure, at most **one** more held-out attempt is allowed, with a new namespace, and only after a recorded change to the object.
   - Each attempt uses α = 0.025/`M`.
   - Every attempt is recorded (DF1-12).
   - Certification failure is never followed by re-tuning against the same held-out set (P18-6).

## 5. Development phase [frozen rules]

**Targets.** For each enumerated test `i` (§6), a frozen script computes the development target `τ_i` from the exact binomial. `τ_i` is the largest true rate whose probability of passing held-out certification is at least 0.999, given the test's held-out `N_i`, the per-attempt α and the target.
- These are illustrative values at `M ≈ 1000` and per-test pass probability 0.99. The frozen script uses 0.999, which gives lower targets.
  - For the error target 0.025 at `N = 20,000`, the target is about 0.0185.
  - For a 0.0035 share at `N = 20,000`, it is about 0.0013.
  - For a 0.0015 share at `N = 40,000`, it is about 0.0005.

**Two stages (DF1-3).**
1. Run 2,000 development replications in every cell.
2. Run 20,000 more in every cell whose estimate exceeds `τ_i/2` for any of its tests.

The decision uses the stage-2 estimate where one exists.

**Choices, in order:**
1. **`family_block_rule`.** Choose largest or median by the smaller worst-cell estimated `P_0(E_f)` at a provisional `z = 1.96`. A tie goes to largest. The rates for the one-ARFIMA-column cells are reported for both rules (Annex B §2.2).
2. **`T_min`.** The smallest of {365, 548, 730} at which every qualifying cell with that `T` meets every `τ_i` under the chosen rule and `z_crit`.
3. **`z_crit`.** The smallest decimal on a 0.001 grid at which every qualifying cell meets its error `τ_i`. It is written as a decimal string (P18-6).
4. **Report** the expected probability that all held-out tests pass jointly, computed from the development estimates, before freezing.
5. If no choice meets every target, the method does not qualify. This is recorded.

## 6. Held-out certification and confidence family

**Tests (DS1-6, DF1-11).** The frozen manifest enumerates every test as (cell, family label, bound). The bounds are:
- `P_0(E_f)` ≤ 0.025;
- DSR availability, including the classifier, ≤ 0.0035;
- other route-R gates ≤ 0.0015.

`M` is the count of these tests: roughly 750–1,000 [estimate].

**Bounds.** Each bound is the one-sided Clopper–Pearson upper bound at α = 0.05/`M`, or 0.025/`M` on a second attempt. Bonferroni then gives simultaneous one-sided 95% coverage per attempt.

**Replication counts.**
- `N = 20,000` per cell.
- `N = 40,000` in cells where the route-R share is the binding test, which the development phase identifies and the frozen manifest records.

**Acceptance.** Every test's bound must be within its target. One miss fails the attempt.

## 7. `U_proc` routes, allocation and the screen

**Per-family allocation** (0.005; the cycle total is 0.01 by the union bound):

| Share | Route |
|---|---|
| 0.0035 | DSR availability, including `UNSUPPORTED_LAW` |
| 0.0015 | the other route-R gates |
| 0 | route D (proved) |
| 0 | route S (screened) |

### 7.1 Gate-by-cause matrix (DS1-7, DF1-10)

| Gate | Unavailability cause | Route |
|---|---|---|
| DSR | Annex B §2.5 rules 1–6; `UNSUPPORTED_LAW` | R |
| G-1 | no Sharpe on a leg; block-length failure; invalid replicate | R |
| G-2 | non-finite MDD (equity at or below 0: `INVALID_SERIES`) | R |
| G-3 | ETH leg with no Sharpe (flat candidate); non-finite MDD | S |
| G-4 | `n = 0` (impossible for `T ≥ 365`: D); integrity (D) | D |
| G-5, G-6, G-7 | stressed-run legs with no Sharpe; missing lagged input | S; integrity D |
| G-8 | non-finite neighbour `E-IMPROV` | S |
| G-10 | `T < 16` (impossible: D); a trial with no Sharpe on a half | R |
| G-11 | `s`, `σ̂` or product invalid; a draw with no Sharpe; `CLASS_MISMATCH` | S |
| G-12 | `γ0` rounds to 0; validation | R |
| G-13 | benchmark hash mismatch | D |
| G-14 | constant prediction or target, for the nominee or any draw | S |

**Route D** is proved by written deterministic arguments: the T bounds, G-13's hash comparison, and data integrity.

**Data integrity** is an engine-only check at evaluation start: complete days, finite values, the manifest hash. Its failure has cause `DATA_INTEGRITY`, which is a `U_ops` infrastructure or data cause. Nothing is read before declaration.

**Route S, the declared-strategy screen (DS1-4, DF1-1, DF1-9).**
- **Inputs.** It runs before the declaration is committed and posted, on the actual intended trial set, on `n_S = 50` simulated null BTC/ETH paths from the Q5 generator, with signs. No window data is used.
- **Per trial and path,** it computes the availability of every route-S gate:
  - G-11 with 20 draws instead of 500;
  - G-14 with 5 refits instead of 500;
  - the other gates in full.
- **Failure.** Any unavailability makes the trial set invalid (P18-1). It cannot be declared, and no `m` is spent.
- **Record.** The screen record's hash enters the declaration.
- **What it is.** The screen is a fail-closed **screen, not a bound**. A strategy may still be unavailable on the real window, and that is then a `U_proc` event with no certified rate. This residual is disclosed in §1.

## 8. Seeds (DS1-8, DF1-14)

**Canonical JSON.** UTF-8, keys sorted, no insignificant whitespace, integers in decimal, and strings exact.

**Namespaces.**
- Development: `"d19-dev-v1"`.
- Held-out attempts: `"d19-heldout-v1"` and `"d19-heldout-v2"`.

**Outer seed.** `seed(c, r) = SHA256(cj({"ns", "cell_id", "rep": r, "anchor"}))`, where `anchor` is:
- the preregistration hash in development;
- `qualification_object_sha256` in held-out runs.

**Domain-separated streams.** Each stream is `SHA256(cj({"seed": hex, "stream": name}))`, where `name` is one of:
- `"market"`;
- `"sign"`;
- `"columns"`;
- `"g1_ci"`, which enters the production `paired_sharpe_ci` stream as its trial seed;
- `"screen"`.

A stream's Philox key is the first 16 bytes of its digest, big-endian.

**Inner Annex B stream.** It is the production construction, with synthetic fields:
- `protocol_hash` is the preregistration hash;
- `family_id` is the cell's family label;
- `cycle_id` is `"D19"`;
- `window_id` is the cell id;
- `data_manifest_hash` is the outer seed;
- `trials` is `{trial_id: "t%03d" % j, hypothesis_hash: SHA256(seed‖"h"‖j), configuration_hash: SHA256(seed‖"c"‖j)}` for each `j`.

The R-7 extension is applied with `round = r` and `beacon_randomness = SHA256(seed‖"beacon")`, so every step of the production derivation is exercised.

**Reproducibility.** A result that does not reproduce from these values is void (Constitution §27).

## 9. Reported, not certified

**Power cells.** One trial has a true annualised E-DIFF Sharpe of 0.5, 1.0 or 2.0, and the other columns are null.
- They run at `K` ∈ {1, 20, 80}, `T` ∈ {`T_min`, `T_C2`}, under laws Q1-independent and Q3.
- Reported: pass rate, nominee identity, availability.

**Mixed nulls.** `K − 1` trials at a true annualised Sharpe of −0.5, and one trial at 0. They run at the same `K`, `T` and laws.

**Also reported:**
- every challenge cell;
- the classifier's refusal rates per cell;
- per-column cap and failure rates by `K`;
- `P_0(E_f | A_f)`;
- the reach-pick rate.

## 10. Compute (DS1-9, DF1-15)

**Estimate.** The order of magnitude is 10¹⁴ value operations, plus the route-R gates: G-1 runs 2,000 replicates per nominee, and G-10 runs 12,870 splits at `K ≥ 20`. Doubling the replications in binding cells adds more. The estimate is about **1,000–3,000 CPU-core-hours**. It is not measured.

**Before the go-ahead,** a measured pilot of the largest cell and of a median cell is required, including one route-S screen of an 80-trial set. It produces the real figures for:
- the cost on this computer, or on rented compute at a quoted price, chosen by the owner;
- whether to reduce `N` with recomputed targets.

## 11. Amendment wording proposed for `<<OPEN D-19 route>>`

> "U_proc is certified, as specified in the D-19 preregistration bound here by hash, by:
> - (R) simulation in every replication of DSR availability (including the supported-law classifier) and of gates G-1, G-2, G-10 and G-12;
> - (D) written deterministic arguments for G-4, G-13 and the bounds on T, with data integrity checked by the engine at evaluation start (a U_ops cause);
> - (S) a fail-closed screen, before the declaration is committed, of the actual trial set on simulated null paths, for gates G-3, G-5, G-6, G-7, G-8, G-11 and G-14.
>
> Route S is a screen, not a calibrated bound; a route-S gate unavailable on the real window is a U_proc event without a certified rate. The declared |J_f| must be a certified K."

## 12. What the owner decides, and when

1. **Accept this preregistration**, after its reviews. This freezes the claim, cells, rules and acceptance before any result exists (Constitution §1 line 31).
2. **Give the go-ahead** for the build and the measured pilot (§10). Then decide on the full run and on compute, local or rented.
3. **Accept or reject the certification result.** A failure leaves promotion blocked.

Nothing here starts a cycle, reads confirmation or lockbox data, or authorizes trading.
