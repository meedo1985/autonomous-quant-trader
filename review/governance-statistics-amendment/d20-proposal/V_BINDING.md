# D-20 (partial): binding the DSR replicate Sharpes to method V (proposal, revision 2)

**Status:** `AI PROPOSAL — NOT AN OWNER DECISION — NOT ACTIVE`
**Date:** 2026-10-04
**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`)

**History:**
- Rev 1 `8a3c2f2` was reviewed by Fable VF1 (SOUND WITH FIXES, `df2bad4`) and Sol VS1 (SOUND WITH FIXES with four blockers, `a39fc39`).
- Rev 2 applies `ADJUDICATION_8A3C2F2.md`. The engine at `ea5b615` implements it.

**Why.** The D-19 measured pilot (`PILOT_FINDINGS_1`–`3`) found that the Task 12 Sharpe numerics are too costly inside the DSR bootstrap. The cheapest version that is still bit-exact takes about 65 s per replication at `K = 80`, which puts the full grid at tens of thousands of core-hours.

A computational-equivalence audit was rejected (Sol DS7, `77f9593`). The owner then directed: "Fast method, then decide compute" (`OWNER_DIRECTION_PILOT.md`, `658bc30`).

**Scope.** This proposal covers only the replicate Sharpes `S*_{b,j}` and `S°_{b,j}` of Annex B §2.3. Everything else in D-20 stays open.

**Three parts need the owner's decision:**
- a clarification of decided Annex B §2.3 (§2);
- a change to the P18-6 reference contract (§4);
- the binding itself (§1).

## 1. Method V (exact definition)

**Inputs.**
- `X`: the `T × K` float64 matrix of Annex B §2.1.
- The replicate index sequences, from the production stationary-bootstrap construction. These are unchanged.

**Steps.**
1. Compute `μ_j = fsum(X[:, j]) / T` and `Y = X − μ`. If either is non-finite, the replicate is `INVALID_REPLICATE`.
2. Build `C[b, t]`, the count of day `t` in replicate `b`. It is exact.
3. Compute `s1 = C @ Y` and `m = s1 / T`.
4. Compute the **two-pass** sum of squares `ss[b, j] = Σ_t C[b, t]·(Y[t, j] − m[b, j])²`, in chunks of 64 replicates, using NumPy `einsum`. Then `var = ss / (T − 1)`. If `s1` or `var` is non-finite, the replicate is invalid.
5. **Rule 5, applied exactly.** A replicate column whose drawn values are all equal is invalid, even when rounding leaves `var` above 0. The equality is checked wherever `var ≤ 10⁻²⁰·(m² + (m + μ)²)`. Any `var ≤ 0` is also invalid.
6. Compute `S*_{b,j} = (m + μ)/sqrt(var)` and `S°_{b,j} = m/sqrt(var)`. If either is non-finite, the replicate is invalid.

The two-pass form avoids the cancellation that the one-pass form of rev 1 suffered on tight clusters far from the column mean (VS1-2). A test covers that case.

**What V binds.** V is fixed by the code hash of `_replicates_v` at the freeze, together with the runtime of §3.

**What stays as decided:**
- the observed `S_j` (Task 12 numerics);
- `S0` and `var_b`, computed with `fsum` and two passes in replicate index order;
- the PW block lengths. Calibration computes them with `fast.column_lengths`, which is bit-identical to production by construction (the same IEEE element-wise operations, correctly rounded `fsum`, the same control flow) and by test;
- the indices;
- every availability rule and the nominee rule;
- `z_j`;
- gate G-1, which keeps the production routine.

## 2. Clarification of Annex B §2.3 (owner decision)

Annex B §2.3 says: "`var_b` uses `B − 1`. Means and variances are computed with `math.fsum` and the two-pass algorithm, in replicate index order".

**Proposed clarification** (a new R-row):

> "Annex B §2.3's fsum/two-pass sentence governs S0 and var_b, the statistics across replicates in replicate index order; the replicate Sharpes S*_{b,j} and S°_{b,j} are computed by method V (D-20)."

**Disclosed.** Earlier records (`PILOT_FINDINGS_1`–`3`) read the sentence as also covering the per-replicate Sharpe. Both readings are possible. If the owner rejects this clarification, V is an **amendment of Annex B**, not a clarification.

## 3. Runtime: pinned, checked, fail-closed

**What is recorded.** `runtime_identity()` records:
- the interpreter version and its executable SHA-256;
- the SHA-256 of the NumPy core and OpenBLAS binaries;
- the platform;
- the CPU dispatch features;
- the environment: `OPENBLAS_NUM_THREADS=1` and `OPENBLAS_CORETYPE=Haswell`. These are set, not defaulted.

**What is checked.** `v_runtime_check()` runs before any computation. It enforces the environment and a known-answer canary: a fixed matrix product hashed against a recorded value. It also compares the full identity with the identity recorded at the freeze. Any difference is a `U_ops` refusal.

Measured on this computer, the canary hash differs when the environment is not pinned, so the check has teeth.

**Where it is recorded.** The identity goes into the qualification object and into every real-evaluation record.

**If the runtime cannot be recreated** for a later evaluation, the evaluation fails closed: the result is void, and a new runtime needs requalification. There is no silent fallback.

## 4. Reference contract (P18-6 change, owner decision)

P18-6 requires the implementation and the reference to agree exactly on the pass/fail decision. With V as the definition, the reference becomes **frozen reference vectors**:
- fixed matrices and index sequences, including near-degenerate, cluster and sparse cases;
- V's expected outputs and decisions for each, recorded at the freeze.

Every vector is also checked against the Task 12 numerics, and the two must agree on every decision.

**Every real evaluation:**
1. reproduces the vectors bit for bit;
2. computes its result with V;
3. also computes the Task 12 exact numerics once and reports both.

If the two decisions differ, the difference is recorded as a disclosed numerical-method difference, and **V's result governs**.

## 5. Evidence (engine `ea5b615`)

**Tests:**
- V is deterministic.
- V agrees with Task 12 on availability, nominee and block, with `z` within `10⁻⁹`, on a benign cell.
- V matches Task 12 on the cluster-cancellation case.
- V refuses an all-zero replicate.
- The runtime check accepts the pinned runtime and refuses without it.
- The PW block length and G-1 availability are bit-identical to production.

**Cost per replication, with two-pass V:**

| Cell | Seconds per replication |
|---|---|
| `K = 80`, `T = 1247` | 6.7 |
| `K = 20`, `T = 730` | 2.3 |
| `K = 2`, `T = 365` | 0.9 |
| `K = 1`, `T = 1247` | 3.4 |

The full 379-cell grid comes to roughly **12,000 core-hours** (estimate).

## 6. Wording

**Draft R-8** (DRAFT_WORDING §2.0) appends:

> ", except that the DSR replicate Sharpes S*_{b,j} and S°_{b,j} of Annex B §2.3 are computed by method V at the code hash and on the runtime identity recorded in the decided D-20 record and the D-19 qualification object"

The clarification row of §2 is added.

**P18-6** gains the reference-vector contract of §4.

**Reference vectors:** D-20 option (a) applies. New deterministic reference vectors are reviewed.

## 7. Owner question (after the re-check)

> "Adopt method V for the inside-the-bootstrap Sharpe of the DSR test? This (1) reads one sentence of Annex B as covering only the averages across the 2,000 replicates, not each replicate's Sharpe — if you disagree, it is a change to Annex B; (2) makes V, run on one pinned computer setup with automatic checks, the official calculation for both calibration and real evaluation (if that setup can't be recreated later, the result is void and must be requalified); (3) makes frozen test cases the reference for exact agreement, with the original calculation also run and reported on every real evaluation. V can give slightly different numbers or availability than the original method in rare near-degenerate cases."

The options are:
- **(A) Adopt V**, recommended. The full calibration is about 12,000 CPU-hours.
- **(B) Keep the original Task 12 calculation inside the bootstrap.** The measured cost is about 65 s per replication at the largest cell, which is tens of thousands of CPU-hours. That means a larger rented-compute budget or a much longer local run.
- **Keep blocked.**
