# Sol narrow re-check of the D-20 (rest) and D-13 proposal, revision 3, at dba31fb

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a1343b-f833-7422-947c-98cc4fc3f6ba)
- Date: 2026-10-13
- Reviewed: both rev 2 re-check records, `ADJUDICATION_2DB4D63.md`, the diff rev 2 -> rev 3 and the full rev 3 (packet)
- Limitation (the reviewer's own): its shell failed intermittently; it cross-checked code against an earlier accessible snapshot.
- Findings: DC3-R1..DC3-R4 (blocking). Verdicts: Q1 NOT READY, Q2 READY WITH FIXES (conditional on Q1), Q2b NOT READY for (a), (b) coherent, Q3 NOT READY, Q4 NOT READY.
- The reviewer's final output follows verbatim.

---

## Re-check verdict

**Revision 3 is not ready to adopt as a whole.** The adjudication identifies the right problems, and most wording repairs are present. Four substantive points remain, including an invalid CPCV path assignment.

| Owner question | Verdict |
|---|---|
| 1. Code bindings and R-7 encoding | **NOT READY** |
| 2. Null streams and `s_inputs` | **READY WITH FIXES**, conditional on the Q1 code-binding repair |
| 2b. Model libraries | **NOT READY** for recommended option (a); option (b) is coherent |
| 3. C2 seed source | **NOT READY** |
| 4. D-13 reporting | **NOT READY** |

### New findings

- **DC3-R1 — blocking — §1 still gives incompatible byte checks.** “Every `calibration` and `aqt` module” must match an engine-commit file, followed by “each object file” must match the object copy. `screen.py` is a *later* file, so those are not generally the same bytes; it may have no engine-commit entry at all. `heldout.py` is a `scripts/` entry point, outside the stated module set. Specify disjoint checks: engine files against the recorded commit; each later file against the verified object manifest; the held-out entry point explicitly. The existing [mapping check](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/mapping.py) illustrates the special case, but does not implement the proposed C2 check.

- **DC3-R2 — blocking — §3a promises a model-runtime identity that the stated mechanism does not record.** The current [`dsr.runtime_identity`](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/dsr.py) covers Python and NumPy/BLAS, while the accepted D-19 preregistration defines the gating identity narrowly and carries it unchanged into the object. Adding scikit-learn and LightGBM versions and binary hashes requires an explicit record *and C2 verification rule*, with its governance effect stated. Pin transitive dependencies too. “The engine never imports them, so its numbers are unchanged” is a hypothesis to check on the rebuilt image, not an established effect. Option (a) must occur before the run definition and qualification on that image; an already qualified old image cannot be carried over by launcher canaries alone.

- **DC3-R3 — blocking — §4 does not finish the DC2-R4 calibration question for selected cycles.** The adjudication is right that data independence alone proves no finite-rate invariance, that (a) is no safe fallback, and that an ideal-hash transfer can be stated as a **modelling assumption for an ex ante attempt**. Revision 3 then permits outcome-dependent invalidation and another seed. Charging `m` is expressly not a statistical correction. For example, if an actor can retain either of two independent attempts according to G-1 availability, an event with per-attempt probability \(p\) can have selected probability \(2p-p^2\), rather than \(p\). The proposal must say whether the D-19 `U_G` claim is being asserted for such selected C2 cycles and, if so, supply the applicable argument or qualification. It also says “the owner accepts” the assumption while the document remains an unanswered owner proposal. Change that to an explicit decision sought.

- **DC3-R4 — blocking — §6’s seven paths are not CPCV paths assembled from whole splits.** Under the proposed rank rule, split `{0,2}` is the second split testing group 0 but the first testing group 2. Its two test groups therefore go to different paths. Path 0 uses `{0,1}` for groups 0 and 1, then `{0,2}`, `{0,3}`, … for groups 2–7: seven splits rather than four two-group splits. The resulting path Sharpes and quantiles depend on this erroneous assembly. Bind seven perfect matchings of the eight groups, using each of the 28 splits once and both test groups of a split in the same path. Pairing group `g` with `g XOR p` for path numbers `p = 1…7` is one deterministic candidate, subject to the owner’s decision.

### Earlier re-check findings

| Findings | Rev 3 disposition |
|---|---|
| DC2-R1 | **Partly repaired:** two binding times are recognised; DC3-R1 remains. |
| DC2-R2 / DF2-R3 | **Repaired:** deterministic `LinearRegression` receives no `random_state`; the exact class map and reproducibility tests are required of `screen.py`. |
| DC2-R3 / DF2-R2 | **Partly repaired:** same-image timing and the no-later-addition rule are explicit; DC3-R2 remains for option (a). |
| DC2-R4 | **Partly repaired:** the overclaim and “safe fallback” are removed; DC3-R3 remains. |
| DC2-R5 / DF2-R6 | **Repaired as disclosure:** one-cycle and across-attempt claims are separated, and the `m` price is not called a correction. |
| DC2-R6 / DF2-R5 | **Repaired:** B6 is identified as a prereg §7.2 clarification, its window and code binding are stated, and offline trial-set search is disclosed. |
| DC2-R7 / DF2-R8 | **Attempted but incorrect:** DC3-R4 remains. |
| DF2-R1 | **Repaired at proposal level:** G-9 binds to `dsr._replicate_seed` and `indices` with the fixed `WINDOW`; M13 expressly proposes replacing Annex B §2.4’s stream and I-10 sentence. That supersession is not active before owner acceptance. |
| DF2-R4 / DF2-R7 | **Repaired:** both R-7 formula locations, C2-only round validation, and the limited coverage of D-19 vectors are stated. |

**Limits of this check:** I reviewed the supplied full revision and diff and cross-checked relevant code and preregistration against an accessible earlier repository snapshot. The local shell intermittently failed during process setup, so I could not independently establish that HEAD is `dba31fb`, inspect its exact tree or installed skill bytes, run checks, or verify reference-vector and Task 12 results at that commit. No files were edited, no review record was committed, and this read-only feedback does not activate an owner or statistician decision.
