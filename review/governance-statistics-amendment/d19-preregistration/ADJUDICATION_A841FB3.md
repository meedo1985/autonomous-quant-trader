# Adjudication of DF4 (Fable) and DS4 (Sol) on the D-19 preregistration rev 4 at `a841fb3`

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter
**Records:**
- `FABLE_REVIEW_A841FB3.md` (`c26e59e`): SOUND WITH FIXES
- `SOL_REVIEW_A841FB3.md` (`c518e94`): UNSOUND

**Result:** `PREREGISTRATION.md` revision 5.

The two families agree on both main defects, so every finding is accepted with the reviewers' proposed fixes.

| Findings | Disposition | Rev 5 |
|---|---|---|
| DS4-1 (BLOCKER), DF4-1 | **Design-to-cell mapping.** A design is accepted only if some final qualifying cell with its `K` and `T_C2` contains the full diagnostic vector within that cell's own stored order statistics. The matching cell ids are recorded. The pooled thresholds are kept for the window classifier only. §11 is reworded to match. | §3.6, §11 |
| DS4-3 (BLOCKER), DF4-2 | **Failure boundary.** An invalidation found before the held-out run starts voids the attempt: the namespace is not burned, and the same object may be posted again under the next attempt key and namespace. An invalidation found at or after the start is a failed attempt: the namespace is burned, P18-6 applies, and any further attempt needs a recorded change.<br>**Horizon substitutions:** "acceptance of this preregistration" replaces "signing", and "the owner's accept or reject of certification" replaces "C2 ends" and "C2's evaluation is final". `D_Qn` must be above the acceptance height. `D_Q2` is fixed in the attempt-2 record.<br>**Start of the held-out run:** only after the O-6a freeze read and the round's publication. | §4 |
| DS4-4 | The declaration mapping is removed from `U_proc^R`. It is a deterministic P18-1 validity check, and it costs no `m`. | §1, §6 |
| DS4-2, DF4-4 | **Generators.** Every `Σ` is written out: equicorrelated, near-duplicate pairing (with the leftover column independent at odd `K`), exact duplicate, opposites (within-group `ρ = 0.9`, minimum eigenvalue 0.1), clusters, and the factor `λλᵀ + diag(1 − λ²)`. The symmetric PSD square root is used, with eigenvalues clipped at 0. Signs are iid fair ±1 per block, independent of the path. | §3.1, §3.4 |
| DS4-5, DF4-4 | **Hourly paths.** Bars are reconstructed by log offsets from their own open, reflected for sign −1, and chained with open equal to the previous close. Source gaps are dropped, there is no further demeaning, and volume is kept. `s` is defined as the outer seed. | §7.2, §8 |
| DF4-3 | **Coverage.** A category-to-cell table is added. A Q2m unequal-moments cell is added (half t₅ and half Gaussian, scales 0.5 and 2). | §3.2 |
| DF4-5 | Development uses the all-candidate envelope. The difference from held-out refusal is stated. | §3.5 |
| DF4-6 | τ is quoted at `M_max ≈ 1,143`, with τ_G(20k) ≈ 0.000148. The compute estimate is marked as predating rev 4. The pilot adds a mapping run of the real libraries. | §5, §10 |
