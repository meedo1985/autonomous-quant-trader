# D-20 (partial): binding the DSR replicate Sharpes to method V (proposal, revision 1)

**Status:** `AI PROPOSAL — NOT AN OWNER DECISION — NOT ACTIVE`
**Date:** 2026-10-04
**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`)

**Why:** The D-19 measured pilot found that the Task 12 Sharpe numerics are too slow to calibrate inside the DSR bootstrap:
- findings 1–3: `PILOT_FINDINGS_1.md` `efdee6c`, `PILOT_FINDINGS_2.md` `3bd0f10`, `PILOT_FINDINGS_3.md` `37680d0`;
- even a bit-identical acceleration costs about 65 s per replication at `K = 80`.

A computational-equivalence audit was rejected (Sol DS7, `77f9593`). The owner directed that one fast method be bound instead: "Fast method, then decide compute" (`OWNER_DIRECTION_PILOT.md`, `658bc30`).

**Scope.** D-20 (`HUMAN_DECISION_MATRIX.md`) covers the stream identity and the code bindings of bootstrap-backed clauses. This proposal covers **only** the replicate Sharpes of Annex B §2.3:
- `S*_{b,j}`, the Sharpe of the resampled uncentred column;
- `S°_{b,j}`, the Sharpe of the resampled recentred column.

The rest of D-20 stays open.

## 1. Method V (exact definition)

**Inputs:**
- `X`, the `T × K` float64 matrix of Annex B §2.1;
- the replicate index sequences `idx_b`, for `b = 0..B−1`, from the production stationary-bootstrap construction, which is unchanged.

**Steps:**
1. `μ_j = fsum(X[:, j]) / T`, using `math.fsum` in column order. `Y = X − μ`, computed elementwise in IEEE double.
2. `C` is the `B × T` matrix of counts: `C[b, t]` is the number of `i` with `idx_b[i] = t`. It is exact in float64.
3. `s1 = C @ Y` and `s2 = C @ (Y ⊙ Y)`. These are computed as float64 matrix products by the pinned NumPy and BLAS, **single-threaded** (`OPENBLAS_NUM_THREADS=1`).
4. The variance and Sharpes:
   - `var = (s2 − s1 ⊙ s1 / T) / (T − 1)`;
   - `mean° = s1 / T`;
   - `S°_{b,j} = mean°_{b,j} / sqrt(var_{b,j})`;
   - `S*_{b,j} = (mean°_{b,j} + μ_j) / sqrt(var_{b,j})`.
5. **Invalid replicate.** If any `var_{b,j} ≤ 0` or any value is non-finite, the result is `INVALID_REPLICATE` (Annex B §2.5 rule 5).

**What stays exactly as decided:**
- the observed `S_j`, which uses the Task 12 numerics;
- `S0 = fsum_b(max_j S°_{b,j}) / B` and `var_b(S*_j)`, which use `fsum` and two passes in replicate index order (Annex B §2.3);
- the PW block lengths and the indices, which are the production routines;
- every availability rule and the nominee rule;
- `z_j = (S_j − S0) / sd_b(S*_j)`.

**Gate G-1** keeps the production paired-CI routine (R-8). V does not apply to it.

## 2. One definition, no equivalence question

V **is** the method. The calibration (the D-19 engine, `calibration/dsr.py` `_replicates_v`, commit `5250988`) and every real cycle evaluation compute the replicate Sharpes with V, on the same pinned runtime. So there is no fast-versus-exact equivalence to establish, and the issue in DS7 does not arise.

P18-6's exact implementation–reference agreement holds because the reference is V itself on the pinned runtime.

## 3. Determinism and reproduction

**What is pinned.** These are recorded in the qualification object (prereg §4) and used for the real evaluation:
- the Python version;
- the NumPy version and its BLAS build;
- `OPENBLAS_NUM_THREADS=1`;
- the CPU model class.

**Reproducibility.** Results reproduce bit for bit on that runtime: a test checks that V is deterministic. **Bit-identity on different hardware is not claimed**, because BLAS chooses its kernels by CPU (`DYNAMIC_ARCH`). This is disclosed.

**Reproduction (Constitution §27).** The recorded hashes, seeds and runtime reproduce the result. The real evaluation records its runtime identity.

## 4. Evidence

**Agreement with Task 12.** On a GARCH, `ρ = 0.9`, `K = 20`, `T = 365` cell, V and the Task 12 numerics give:
- the same availability reason, nominee and block;
- a `z` within `10⁻⁹` relative.

This is shown by the test `test_method_v_is_deterministic_and_close_to_the_task12_numerics`. It is a check, not a proof; V is its own definition, so the two are not required to be identical.

**Pilot cost with V** (`5250988`, per replication):

| Cell | Time |
|---|---|
| `K = 80`, `T = 1247` | 4.7 s |
| `K = 20`, `T = 730` | 2.3 s |
| `K = 2`, `T = 365` | 0.9 s |
| `K = 1`, `T = 1247` | 3.7 s |

The production G-1 routine and the index loops now dominate. Estimated total for the 379-cell grid: about **11,000 core-hours**.

**Conditioning.** Columns are centred by their exact mean before the sums, so `s2 − s1²/T` does not suffer catastrophic cancellation. Daily E-DIFF scale and `T ≤ 1247` keep counts and sums far from the limits of float64.

## 5. Wording changes

**Draft R-8** (DRAFT_WORDING §2.0) changes from:

> "…the Task 12 Sharpe and ESS code) bind to that code at a hash fixed under <<OPEN D-20>>."

to:

> "…the Task 12 Sharpe and ESS code) bind to that code at a hash fixed under <<OPEN D-20>>, except that the DSR replicate Sharpes S*_{b,j} and S°_{b,j} of Annex B §2.3 are computed by method V (D-20 binding, d20-proposal/V_BINDING.md at its hash), on the runtime pinned in the D-19 qualification object."

**Reference vectors.** D-20 option (a) applies: V gets fresh deterministic reference vectors, generated by the D-19 engine and reviewed.

## 6. Owner question (after the two reviews)

> "Bind the inside-the-bootstrap Sharpe of the DSR method to method V (one fast, fixed calculation, used identically in calibration and real evaluation)?"

The choices are:
- **(A) Bind V**, recommended;
- **(B) Keep the Task 12 numerics**, which makes the calibration infeasible here;
- **keep blocked**.

The compute choice is asked separately, after this decision.
