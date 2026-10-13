# §16 different-model review of the §3.6 mapping at d93e498

- Reviewer: Codex CLI, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a1318e-a7da-7ba0-90b7-cbc2f8bd200c)
- Date: 2026-10-12
- Reviewed: `git diff main...d19-mapping` at d93e498 (calibration/mapping.py, tests/unit/test_calibration_mapping.py), with prereg §3.6 and §13 rev 7g items 3, 4
- Findings: MP-R1 (blocking), MP-R2 (blocking), MP-R3 (note). Verdict: CHANGES REQUESTED.
- The reviewer's output follows verbatim.

---

The cell comparison itself follows the preregistration: it uses the last `T_C2` rows, filters for final qualifying units, and uses each unit’s own bounds. `classifier.within` enforces exact `K` and `T`, all required tails, finite values, and acceptance at a threshold tie.

### Findings

- **MP-R1 — blocking.** [mapping.py](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/mapping.py>) exposes `map_design(e_diff, report)` with an arbitrary mutable report; the verified `load()` call is optional. [The test](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_calibration_mapping.py>) obtains an accepted record from a hand-built report. The record hash therefore does not establish that the statuses and bounds came from the posted qualification object. **Repair:** make the public mapping path require the object path and posted hash, verify them before comparison, and bind that object hash to the record. Keep a separate internal seam for synthetic unit tests.

- **MP-R2 — blocking.** The mapping imports the ambient `calibration.classifier`; neither `load()` nor `map_design()` checks its source or runtime identity against the threshold run. The [Dockerfile](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/deploy/calibration/Dockerfile>) states that code is mounted outside the pinned image, so using that image alone cannot establish identical diagnostic code. A changed classifier could alter a declaration decision against unchanged stored bounds. **Repair:** make the declaration runner verify the classifier’s pinned engine source and runtime identity before mapping, and test refusal when either differs.

- **MP-R3 — note.** `np.asarray(e_diff)` carries no day or partition identity. MP-1 is a reasonable boundary for this file because the declaration pipeline does not yet exist, but this function cannot establish that rows are complete, ordered exploration days after warm-up. **Repair:** require the later pipeline to validate those properties and bind its input identity to the declaration.

### Proposed readings

| Reading | Decision |
|---|---|
| MP-1 | **Accept**, subject to the later pipeline check in MP-R3. |
| MP-2 | **Accept.** The qualification report treats a QJ family as a unit, and §3.6 imposes no group-label restriction. |
| MP-3 | **Accept as a requirement; implementation does not enforce it** (MP-R1). |
| MP-4 | **Reject as written.** The pinned image does not pin the mounted classifier code (MP-R2). |

This was a static review. The local shell failed before commands could run, so I could not run tests, lint, or type checks. I made no edits; under the repository’s review-record rule, this response still needs to be committed as a review record before it counts as a completed §16 check.

**Verdict: CHANGES REQUESTED.**