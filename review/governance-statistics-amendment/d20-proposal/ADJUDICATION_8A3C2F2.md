# Adjudication of VF1 (Fable) and VS1 (Sol) on the D-20 V binding at `8a3c2f2`

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter
**Records:**
- `FABLE_REVIEW_8A3C2F2.md` (`df2bad4`): SOUND WITH FIXES
- `SOL_REVIEW_8A3C2F2.md` (`a39fc39`): SOUND WITH FIXES, with four blockers

**Result:** `V_BINDING.md` revision 2. The engine changes are in commits `dbdc460` and `ea5b615` on `d19-calibration-engine`.

Every finding is accepted.

| Findings | Disposition |
|---|---|
| VS1-1 (BLOCKER), VF1-3 | **Annex B reading.** This is put to the owner **explicitly** as a clarification of decided Annex B §2.3, not as a silent code binding. The `fsum`/two-pass sentence governs `S0` and `var_b`. `S*` and `S°` are computed by V. If the owner rejects that reading, V becomes an Annex B amendment, and the owner question says so. A new R-row carries the clarification. |
| VS1-2 (BLOCKER), VF1-1, VF1-6 | **Numerics.** V is now a counts-weighted **two-pass** variance: each replicate's own mean is subtracted before squaring, in chunks. This removes the cancellation Sol demonstrated. A test covers a tight cluster far from the column mean and checks that V agrees with the Task 12 variance there. **Rule 5 is applied exactly:** a replicate column whose drawn values are all equal is invalid, with the near-zero scale now including the centred level. A test covers an all-zero replicate. **The finite checks are complete and ordered:** `μ`, `Y`, `s1`, `var`, `S*`, `S°`. The conditioning claim is removed. |
| VS1-3 (BLOCKER) | **Reference contract (P18-6).** The P18-6 reference becomes the **frozen reference vectors**: a set of fixed input matrices and index sequences, including near-degenerate and cluster cases, with V's expected outputs and decisions recorded at the freeze. These vectors are also checked against the Task 12 numerics, and must agree on every decision. Every real evaluation first reproduces the vectors bit for bit. The real result is then computed by V. Task 12 exact numerics are also computed and **reported**; a decision difference is recorded as a disclosed numerical-method difference, and V's result governs. This amends P18-6's wording, so it is part of the owner question. |
| VS1-4 (BLOCKER), VF1-2 | **Runtime.** `runtime_identity()` records the following, and `v_runtime_check()` enforces them before any computation, failing closed with a `U_ops` cause: <ul><li>the interpreter, by version and executable hash;</li><li>the NumPy core and OpenBLAS binaries, by hash;</li><li>the platform;</li><li>the CPU dispatch features;</li><li>the environment: `OPENBLAS_NUM_THREADS=1` and `OPENBLAS_CORETYPE=Haswell`, set, not defaulted;</li><li>a known-answer canary.</li></ul>The identity is recorded in the qualification object and in every real-evaluation record. **If the qualified runtime cannot be recreated later,** the evaluation fails closed: the result is void, and a new runtime needs requalification. There is no silent fallback. |
| VF1-4 | V is bound by the **code hash** of `_replicates_v` at the freeze. The R-8 text cites the decided D-20 record, not the proposal. |
| VF1-5 | The PW block length in calibration is computed by `fast.column_lengths`. It is stated as bit-identical to production, on the structural argument (the same IEEE element-wise operations, correctly rounded `fsum`, the same control flow) and by test. |
| VF1-7, VS1 owner wording | **The question is reworded.** It now discloses: <ul><li>that V replaces a plausible reading of Annex B arithmetic;</li><li>that V can change values or availability near degeneracy;</li><li>the frozen-runtime dependency;</li><li>the P18-6 change.</li></ul>Option B states the measured cost instead of "infeasible". |
