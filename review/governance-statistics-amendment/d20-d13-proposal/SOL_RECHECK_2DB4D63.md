# Sol re-check of the D-20 (rest) and D-13 proposal, revision 2, at 2db4d63

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a13414-bfca-73c3-9bac-c2b75b8833bb)
- Date: 2026-10-13
- Reviewed: revision 2, the adjudication, both rev 1 reviews and supporting code (packet)
- Limitation (the reviewer's own): its shell failed, and GitHub did not have 2db4d63 (public main was 4070f0e), so it cited an earlier public snapshot for the code checks.
- Findings: DC2-R1..DC2-R4 (blocking); DC2-R5..DC2-R7 (notes). Verdicts: Q1-Q3 NOT READY, Q4 READY WITH FIXES.
- The reviewer's final output follows verbatim.

---

## Re-check verdict

**Revision 2 is not ready to adopt as a whole.** It repairs much of the wording from revision 1, but the proposed `screen.py` binding does not match the existing qualification checks, G-14’s scikit-learn rule cannot be implemented as written, and the calibration argument for the new G-1 seed is insufficient.

| Owner question | Verdict |
|---|---|
| 1. Code bindings and R-7 encoding | **NOT READY** |
| 2. Null streams and `s_inputs` | **NOT READY** |
| 3. Beacon-protected C2 trial seed | **NOT READY** |
| 4. D-13 reporting of both estimands | **READY WITH FIXES** |

### New findings

- **DC2-R1 — blocking — two different code-binding times are conflated (§§1, 3, 5).** The D-19 object lists `screen.py` as a *later*, separately reviewed file. The existing `mapping.check_engine` checks loaded modules against the earlier `engine_commit` and makes a special allowance for `mapping.py`, but not `screen.py`; `rundef.loaded_outside` checks whether a module is in the hashed code area, not whether its bytes match the object. Thus “import the object’s copy” and “verify it against `engine_commit` by the same check” do not establish the claimed binding. Bind existing routines to the engine commit and `screen.py` to its reviewed object hash, then require a C2 check of the loaded bytes. This also limits the claimed repairs of DC-R7, DF-R2, DF-R12 and DF-R14. Evidence: [qualification object](https://github.com/meedo1985/autonomous-quant-trader/blob/main/calibration/qobj.py), [engine check](https://github.com/meedo1985/autonomous-quant-trader/blob/main/calibration/mapping.py), [loaded-module check](https://github.com/meedo198/autonomous-quant-trader/blob/main/calibration/rundef.py).

- **DC2-R2 — blocking — G-14’s model-seed instruction is impossible for `linear` (§3 B4).** The proposal requires `random_state=model_seed` for *every* scikit-learn class, including linear regression. `LinearRegression` has no `random_state` parameter. Specify that deterministic estimators receive no seed, while every stochastic estimator and permitted random pipeline step receives a controlled seed. Test each allowed class and solver. This is a new defect in the attempted DC-R3/DF-R5 repair. [Scikit-learn’s `LinearRegression` API](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html).

- **DC2-R3 — blocking — the proposed model runtime conflicts with the D-19 runtime (§3 B4).** The accessible D-19 image locks NumPy as its only third-party package, while the accepted preregistration says C2’s real evaluation must run in the *same image*. Merely recording scikit-learn and LightGBM in a later “evaluation runtime identity” does not add them to that image. A new image changes its digest and requires the applicable run-definition, review and qualification consequences to be resolved. As written, the promise that LightGBM trials can later be enabled by recording a reviewed runtime is incomplete; the same issue applies to scikit-learn-backed trials. The fixed LightGBM seed and deterministic settings otherwise address the documented seed-priority problem. [D-19 preregistration](https://github.com/meedo1985/autonomous-quant-trader/blob/main/review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md), [runtime lock](https://github.com/meedo1985/autonomous-quant-trader/blob/main/deploy/calibration/requirements.lock), [LightGBM parameters](https://lightgbm.readthedocs.io/en/latest/Parameters.html).

- **DC2-R4 — blocking — DC-R6’s calibration objection remains (§4).** The scoped override of l.266, beacon dependency, audit requirement and residual C-13 disclosure are good repairs. The assertion that D-19 certification is *unaffected* does not follow from “both seeds are independent of the data.” D-19 measures **G-1 availability** using its specified synthetic stream; option (b) changes that stream’s seed construction in C2. Data independence alone does not prove equal finite-bootstrap availability rates: two fixed, data-independent seeds can produce different replicate outcomes. The DSR error event itself may be unchanged, but the certified `U_G` claim includes G-1. Establish an applicable invariance bound or qualify the new seed procedure. The proposed fallback to (a) is not automatically “safe”: (a) retains the acknowledged pre-post seed search. [D-19 claim and G-1 measurement](https://github.com/meedo1985/autonomous-quant-trader/blob/main/review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md).

- **DC2-R5 — note — DC-R5 is repaired for one committed cycle, but “no new route opens” is too broad (§4).** P18-1/P18-3 account for the declared trials, the first post commits the declaration, and P18-2 prevents an early nomination. Those citations support the adjudication’s narrower answer. They do not establish that post-beacon invalidation and reuse of the still-eligible window cannot be selected after observing a seed or an offline result. Spending `m` prices an attempt; it is not a statistical correction for selective retries. State and enforce the permitted invalidation causes and the across-attempt claim, or limit “no new route” to a single valid cycle. I could not determine from the supplied excerpts whether an actor can induce an invalidation at will.

- **DC2-R6 — note — B6 inherits a visible pre-post search surface (§3).** B6 is consistent with the accepted §7.2 screen seed and correctly avoids claiming a beacon before the post. Its path and null seeds are functions of the declarer-controlled trial-set hash and trial ID. Recording every *submitted* screen run cannot establish that no candidate hashes were tested offline. The screen has no certified error rate, so this does not overturn D-19’s stated bound; disclose the limit when describing what beacon protection closes. [D-19 §7.2](https://github.com/meedo1985/autonomous-quant-trader/blob/main/review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md).

- **DC2-R7 — note — D-13 still needs a reproducible path assembly (§6).** Both labelled estimands, type-7 quantiles, and fail-closed unavailable summaries repair DC-R10/DF-R13. Yet 28 two-group splits can be assembled into seven CPCV paths in more than one way. Different assemblies can yield different path Sharpes and therefore different 5th percentiles. Bind the path assignment and chronological aggregation before generating the report. This does not change its diagnostic-only role. The supplied [frozen CPCV clause](https://github.com/meedo1985/autonomous-quant-trader/blob/main/protocols/protocol_v1.yaml) fixes the counts, not that assignment.

### Earlier findings and markers

DC-R1, R2, R4, R8, R9 and R10 have adequate **proposal-level** repairs. DC-R3 has a better seed and LightGBM rule but is still blocked by DC2-R2/R3. DC-R7 fixes the intended freeze timing but not the loaded-code verification (DC2-R1). The partial adjudications of DC-R5 and R6 are sound only to the narrower extent stated above; DC-R6’s certification conclusion is not established. The Fable findings are largely reflected in the draft requirements, with the same code-binding and runtime exceptions.

**No additional literal D-20 or D-13 marker is silently omitted from revision 2’s M1–M12 inventory** in the accessible draft: G-9 is included, and lockbox bindings are expressly reserved. The markers remain in the S4 draft by revision 2’s stated plan; no replacement has been made. DC2-R1 and DC2-R7 identify substantive bindings still to settle.

### What I could not check

The local shell repeatedly failed during process setup, and GitHub did not have commit `2db4d63`; the accessible public `main` was `4070f0e`. I therefore could not verify the exact target commit, local diff or status, reference-vector results, installed skill bytes, frozen hashes, or a completed C2 evaluator. The repository code cited above is an earlier accessible snapshot; findings about its checks require confirmation against `2db4d63`. No edits, tests, or committed review record were made.
