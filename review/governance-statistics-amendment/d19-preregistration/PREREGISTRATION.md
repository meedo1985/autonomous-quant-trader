# D-19 calibration preregistration for C2 (revision 1)

**Status:** `AI PROPOSAL — NOT AN OWNER DECISION — NOT FROZEN — NOTHING BUILT OR RUN`
**Date:** 2026-10-04
**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`). The owner delegated drafting choices on 2026-10-03 and 2026-10-04, so every choice below is an `[AI default]` unless it cites a decided record.
**Authority and limits:**
- `d19-recommendation/OWNER_STEP0_DECISION.md` (R19-1, R19-2) allows designing the calibration. Building the engine or generating any simulation result needs the owner's **separate go-ahead** (§12).
- No human statistician reviews this. Two different AI model families do (R19-2), which is weaker and disclosed.
- Data: synthetic, and exploration-partition BTC/ETH data only (§3.4). No confirmation or lockbox data is read, by the design or by the run.

**What it binds:** the decided method (Annex B, `aqt.dsr.bootstrap_max.candidate.v2`), the selection rule (Annex A, P18-0..P18-7 and A-B7), and the gates (Annex C). It supplies the `<<D19>>` values of DRAFT_WORDING:
- `T_min`;
- `family_block_rule`;
- `z_crit`;
- the `U_proc` allocation;
- the certification route (`<<OPEN D-19 route>>`, §7).

## 1. The claim to certify (Annex A P18-7)

Under the all-zero-mean global null, in **every** qualifying cell (§3), at a simultaneous one-sided confidence of 95% over every cell, family and bound (§6):
1. **Error bound.** For each declared family `f`, an upper bound on `P_0(E_f)` of at most 0.025, where `E_f = A_f ∩ {z_f* ≥ z_crit}` (P18-6). This gives `P_0(E) ≤ 0.05` for the cycle under any dependence between the families.
2. **No-result bound.** An upper bound on `P_0(U_proc)` of at most 0.01 for the whole cycle, allocated per §7.

**If either fails in any qualifying cell, the method does not qualify,** and promotion stays blocked (the 2026-09-15 decision stands). That is a valid result; it is not tuned away.

**Also reported, not certified:**
- `P_0(E_f | A_f)`;
- the rate of reaching the pick;
- availability, power and mixed-null rates (§9);
- every challenge cell (§3.3).

## 2. The procedure simulated in one replication

One outer replication of a cell:
1. **Generate the legs.** For each family, generate the `T × K` candidate legs `C`, the shared benchmark leg `b`, and their E-DIFF matrix `X = C − b·1ᵀ` (Annex B §2.1). The cell's generator (§3) sets the population mean of every column of `X` to exactly 0. This is the location-shift null (Annex B §2.3).
2. **Apply Annex B in full,** with `B = 2000` inner replicates:
   - the availability checks of §2.5, in order;
   - the block length from the frozen `family_block_rule`;
   - `S0`, `D_j` and `z_j`;
   - the nominee by highest `S`, with ties to the lowest id (P18-4);
   - `E_f`.

   Inner randomness follows §8. The inner algorithm, including invalid-replicate handling, is the frozen build code, rerun exactly.
3. **Evaluate the return-level gates** (route R, §7) on the nominee, whatever the DSR or any other gate outcome (P18-7).
4. **Record the events and reason codes:** `A_f`, `E_f`, each route-R gate's availability, and the realised `L` and `L/T`.

Crashes and infrastructure faults are not modelled; every simulated trial completes (P18-7). Two-family cells (§7) run the two families on one shared generated market.

## 3. Cells

### 3.1 Dimensions [AI default]

| Dimension | Levels |
|---|---|
| `T` (complete days) | `T_min` candidates {365, 548, 730} (§5); 1095; and `T_C2` |
| `K = \|J_f\|` | 1, 2, 5, 20, 80 |
| Cross-column dependence | independent; equicorrelated ρ ∈ {0.5, 0.9, 0.99}; one factor with heterogeneous loadings (uniform on [0.3, 0.99]) |
| Marginal / serial law (location 0, unit scale) | Gaussian iid; Student-t ν = 5; skew-t, positive and negative skew (skewness ±1); GARCH(1,1) (α = 0.10, β = 0.85, t₅ innovations); AR(1) with φ ∈ {0.2, 0.5}; **mixed**: one AR(1) φ = 0.5 column among iid columns (FB2-4) |
| Semi-empirical E-DIFF | §3.4 |

**`T_C2`.** `T_C2 = 1247 − g`, where `g = gap_embargo.value_days`. The frozen gap rule computes `g` from exploration data alone (P18-0 (iii)). `g` is computed and recorded **before** the qualification object is frozen.
- If the value declared at C2 differs, the certification does not cover C2, and C2 cannot promote.
- If `g` cannot be fixed before the freeze, `T_C2` becomes the declared grid {1095, 1247}. C2 is then covered only if its `T` equals a certified grid value.

### 3.2 Qualifying cells (the certified set) [AI default]

Testing every combination of levels is too costly (§10). Instead, the qualifying set is the union of the following groups. T values below `T_min` are dropped after §5.
- **Q1 (core grid):** Gaussian iid, every `K`, every `T`, with every cross-dependence level.
- **Q2 (marginal laws):** each non-Gaussian law of §3.1, at `K` ∈ {1, 20, 80}, at `T` ∈ {`T_min`, `T_C2`}, with independent and ρ = 0.9 dependence.
- **Q3 (the mixed column):** the mixed AR column at `K` ∈ {2, 3, 20}, at `T` ∈ {365, `T_C2`}, independent.
- **Q4 (semi-empirical):** §3.4 at `K` ∈ {5, 20, 80} and `T` ∈ {`T_min`, `T_C2`}.

That is about 140–180 cells after `T_min` is fixed (`K = 1` has a single dependence level). The exact list is generated by a frozen script whose output, the cell manifest, is hashed into the qualification object (§4).

### 3.3 Challenge cells (reported, never certified) [Annex B §2.6]

These cells lie outside the supported domain. The method is expected to refuse them or to lose control; that is reported, with no target. They are:
- long memory (ARFIMA, d = 0.3);
- a structural break (mean-zero variance doubling at `T/2`);
- a regime switch (two-state Markov volatility);
- infinite variance (Student-t ν = 1.8);
- sparse columns (active on 5% of days in runs; FB1-6);
- `K = 80` at `T = 365`.

### 3.4 Semi-empirical cell (exploration data only) [AI default]

- **Returns.** BTC and ETH daily close-to-close returns are drawn from the **exploration partition only**, by a stationary bootstrap with mean block length 20. They are demeaned before resampling.
- **Exposures.** The candidate exposures come from `K` simple trend or volatility rules: moving-average crossovers on lookback grids, and volatility-target variants. The rules are applied causally to the resampled path. The benchmark is `VOL_TARGET_BUY_AND_HOLD` (`canonical.py`), run on the same path.
- **Null.** Each column's population mean is estimated from a pilot of 10⁶ path-days and subtracted. This approximates the zero-mean null. The residual error is reported and must be below 1% of a column's standard deviation, or the cell is moved to challenge.
- **Purpose.** This cell carries realistic E-DIFF structure: the strong common factor, heteroskedasticity, and exposure-driven sparsity. Its result is conditional on the rule library, which is disclosed.

## 4. The qualification object and the freeze order

The **qualification object** is everything P18-6 requires, plus:
- the method build (Annex B code at a commit hash, with the `<<OPEN D-20>>` bindings);
- this preregistration at its accepted hash;
- the generator code and the cell manifest (§3.2), with their hashes;
- the classifier (§3.5 below);
- the confidence family and acceptance rule (§6);
- `family_block_rule`, `T_min`, `z_crit` and the `U_proc` allocation (§5, §7);
- the route-S supplementary simulation and its reference library (§7);
- the seed namespaces (§8).

### 3.5 Supported-law classifier (D-18 O18-2, A-B7)

The classifier is a **cell rule**: a cell qualifies if and only if its law is stationary, has short memory and finite variance, has no breaks, has no sparse column, and the cap binds in fewer than 1% of its development replications. Otherwise it is a challenge cell.

For a real window there is **no** classifier beyond the frozen sample-level refusals (Annex B §2.5). The window's diagnostics are reported but not used to decide anything (Annex B §2.6 residual, disclosed):
- realised `L/T`;
- excess kurtosis;
- the Hurst exponent estimate;
- a test for a variance break.

### Freeze order

1. This preregistration is reviewed (R19-2) and accepted by the owner.
2. The owner gives the build go-ahead (§12). The engine is built and reviewed under §16, with reference tests.
3. **Development phase** (development seed namespace only): choose `family_block_rule`, `T_min`, `z_crit` and the allocation (§5).
4. **Freeze.** The qualification object is hashed and committed with its record (R19-2). No held-out replication exists before this point.
5. **Held-out certification** (held-out namespace): §6.
6. Accept or fail. Any change after held-out results are seen needs a **new** held-out namespace, never a re-run on the same one (P18-6).

## 5. Development phase: choosing the free values [AI default rules, fixed now]

All development runs use the development namespace (§8) and 2,000 outer replications per qualifying cell.
1. **`family_block_rule`.** Choose largest or median by the smaller worst-cell estimated `P_0(E_f)` at a provisional `z = 1.96`. Ties go to largest (Annex B §2.2). The development cells must include the mixed column and GARCH cells, as they do (Q2, Q3).
2. **`T_min`.** The smallest of {365, 548, 730} for which every qualifying cell at that `T` meets both development targets below under the chosen rule.
3. **`z_crit`.** The smallest decimal on a 0.001 grid such that, in every qualifying cell, the development estimate is `P̂_0(E_f) ≤ 0.018`. This margin is sized in §6 so that a true rate at the development estimate passes held-out certification with high probability. It is written as a decimal string, parsed to the nearest binary64 (P18-6).
4. **`U_proc` allocation.** §7 fixes it now; the development phase only checks that each route-R estimate is at most 40% of its allocated share. That margin is sized in §6.
5. If no rule, `T_min` and `z_crit` meet these targets, the method does not qualify. D-19 ends without promotion, and that is recorded.

## 6. Held-out certification and the confidence family [AI default]

- **Bounds.** For each test, the bound is the one-sided Clopper–Pearson upper bound.
- **Family.** One family covers every qualifying cell × each family's `P_0(E_f)` bound × each allocated `U_proc` bound. It is controlled by Bonferroni at simultaneous 95%, so each test uses `α = 0.05/M`. `M` is counted from the frozen manifest. With three tests per cell (the error bound, DSR availability and route-R availability), that is about 400–550 tests.
- **Replications.** `N = 20,000` outer replications per qualifying cell.
  - With `M = 550` (`α ≈ 9·10⁻⁵`), a true error rate of 0.018 gives a Clopper–Pearson bound below 0.025 with probability above 0.99. The margin is thin: about 0.024 at the 99th percentile, by normal approximation.
  - A true availability rate at 40% of its allocated share gives a bound below that share with probability above 0.99. For example, a true rate of 0.0012 gives about 0.0027 against the 0.003 share.
  - The exact power table is computed and frozen with the object.
- **Acceptance rule.** Every test's bound must be within its target. A single miss fails certification.

## 7. `U_proc` and the certification route (`<<OPEN D-19 route>>`)

P18-7 requires every pre-lockbox mandatory gate to be computed for every nominee in every replication, unless the amendment authorises another route (DRAFT §4). This preregistration proposes three routes. The amendment wording is in §11.

| Route | Gates | How their unavailability enters `U_proc` |
|---|---|---|
| **R** (return level, every replication) | DSR availability (Annex B §2.5); G-1; G-2; G-4; G-10 when enabled; G-12 | Computed in every outer replication from the generated legs. G-12 uses the candidate leg. G-10's matrix is `X`. |
| **D** (deterministic argument) | G-8; data-integrity parts of G-1, G-4, G-6, G-7 | Proved unavailable-free whenever the window's data are complete and finite, which is checked from the data manifest before declaration without evaluating anything. Each argument is written per gate and reviewed (§11). |
| **S** (strategy-level supplementary simulation) | G-3, G-5, G-6, G-7, G-11, G-14, and every gate's zero-variance-leg case (a candidate flat for the whole window has no Sharpe, so `E-IMPROV` is undefined) | Estimated on a frozen **reference library** of strategies representative of the trend and volatility families (§3.4 rules plus model-based examples for G-14), run on simulated BTC/ETH price paths from the exploration-only bootstrap. Each family's reference library has 1,000 outer replications. The bound is a Clopper–Pearson upper bound. **Conditional on the library:** a declared strategy unlike the library is not covered, and this is disclosed. |

**Allocation** (summing to 0.01 for the cycle, per family) [AI default]:

| Share | Route |
|---|---|
| 0.0030 | DSR availability |
| 0.0010 | the other route-R gates |
| 0.0010 | route S |
| 0 | route D (proved, not estimated) |

That is 0.005 per family, so 0.01 for the cycle by the union bound. No joint two-family cells are needed (P18-7).

**Declaration-time requirement** (route S coverage): each declared trial must state the library rule it most resembles, and why. A trial that resembles none is declared outside route-S coverage. The family's no-result guarantee then does not cover it, and that is recorded at declaration.

## 8. Seeds and randomness [AI default]

- **Namespaces.** `ns ∈ {"d19-dev-v1", "d19-heldout-v1"}`. A new held-out namespace is `"d19-heldout-v2"`, and so on.
- **Outer seed.** The outer seed of cell `c`, replication `r` is `SHA256(canonical_json({"ns", "cell_id", "rep": r, "prereg_sha256"}))`. Generator draws use a counter-based generator (numpy `Philox`) keyed by that seed.
- **Inner seed.** The inner Annex B stream uses its own family-seed rule (Annex B §2.4). The family seed's fields are filled with synthetic values derived from the outer seed (`protocol_hash` = the prereg hash, `cycle_id` = `"D19"`, `window_id` = cell id, `data_manifest_hash` = outer seed). Inner randomness therefore runs through exactly the production construction.
- **Record.** Every result is reproducible from the recorded hashes and seeds. Results that are not reproducible are void (Constitution §27).

## 9. Reported, not certified [AI default]

- **Power cells.** One trial with a true annualised E-DIFF Sharpe of 0.5, 1.0 or 2.0, the others null, at `K` ∈ {1, 20, 80} and `T` ∈ {`T_min`, `T_C2`}. Report: pass rate, nominee identity, availability.
- **Mixed nulls.** Several trials with negative true Sharpe and one at zero.
- **Every challenge cell** (§3.3).
- **Per-column rates.** Cap and failure rates by `K` (Annex B §2.5, FB2-5).
- **The rest:** `P_0(E_f | A_f)` and the reach-pick rate.

## 10. Compute plan [estimate, for the go-ahead decision]

- **Cost of one outer replication:** about `B·K·T` resampled values: 2000 × 80 × 1247 ≈ 2·10⁸ at the largest cell.
- **Whole run:** development (2,000 replications) plus held-out (20,000) over about 140–180 cells, mostly smaller `K`, is of order 10¹⁴ value-operations. That is roughly 300–1,000 CPU-core-hours with vectorised NumPy (estimate, not measured).
- **Where it runs:** on this computer it is days to weeks. A rented multi-core machine would cost money, which needs the owner's decision.
- **Route S** adds a smaller strategy-level simulation, estimated at 10–50 core-hours.
- **Reduction if needed:** cut `N` to 10,000 with a stricter development margin (0.016), which roughly halves the cost. The owner chooses at go-ahead.

## 11. Amendment wording proposed for `<<OPEN D-19 route>>`

> "U_proc is certified by three routes, as specified in the D-19 preregistration (hash bound here):
> - (R) the availability of the DSR method and of gates G-1, G-2, G-4, G-10 and G-12 is computed in every simulated replication;
> - (D) gate G-8 and the data-integrity conditions of G-1, G-4, G-6 and G-7 are certified by written deterministic arguments, given a complete and finite window data manifest checked before declaration;
> - (S) gates G-3, G-5, G-6, G-7, G-11 and G-14, and every zero-variance-leg case, are certified on a frozen reference library of strategies.
>
> The S route's guarantee covers a declared trial only if the trial is declared as resembling a library rule. The sum of the allocated bounds is at most 0.01 per cycle."

## 12. What the owner decides, and when

1. **Accept this preregistration** after its two reviews. This freezes the claim, cells, rules and acceptance before any result exists (Constitution §1 line 31).
2. **Go-ahead to build and run** (a separate step, per R19-1): build the engine under §16; choose local or rented compute (§10).
3. **After certification:** accept or reject the result. A failure ends with promotion still blocked.

Nothing here starts a cycle, reads confirmation or lockbox data, or authorizes trading.
