# Sol review VS1 of the D-20 V-binding proposal at `8a3c2f2`: SOUND WITH FIXES (four blockers)

Date: 2026-10-04. This is an R19-2 independent review by the different model family. The prompt was the same as Fable VF1's, with the ID prefix `VS1`. The run's log contains two "usage limit" lines from mid-run; the final message completed and is reproduced below unchanged.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a10793-fc19-7ef3-a22e-c998e31e7915`.

---

Model: OpenAI Codex, GPT-5 family; exact serving identifier not exposed  
Commit: `8a3c2f2336115a2d45174c0c398bc1f86d4014c3`; engine `5250988e6270e8df60300b6d72e602cd05e30d28`  
Verdict: **SOUND WITH FIXES** — conceptually sound, but not ready for owner acceptance.

**VS1-1 — BLOCKER — Annex B §2.3 lines 91–93; V_BINDING §§5–6**  
Problem: The across-replicate interpretation is plausible—“replicate index order” naturally describes `S0` and `var_b`—but not unambiguous. “Means and variances” is unqualified, and prior pilot records explicitly treated Task 12 `fsum`/two-pass arithmetic as the exact Annex B per-replicate method.  
Evidence: Annex B line 91 begins with `var_b`, but PILOT_FINDINGS_1–3 consistently describe Task 12 arithmetic as binding inside each replicate.  
Fix: Treat D-20 as an explicit owner-approved Annex B override/clarification, not merely a code binding. State that V replaces Task 12/`fsum` arithmetic only inside `S*` and `S°`, while `S0` and `var_b` retain `fsum`/two-pass. D-20 can carry that amendment if the owner question says so expressly.

**VS1-2 — BLOCKER — V_BINDING §1 step 5 and §4; `calibration/dsr.py:227–238`**  
Problem: Global centring improves ordinary cases but does not prevent catastrophic cancellation when a replicate has a large local mean and very small local variance. The “does not suffer catastrophic cancellation” claim is false. The invalid rule is also incomplete: the proposal says any non-finite value is invalid, while the code checks only `var`.  
Evidence: An in-memory `T=365` finite, positive-variance example with observations near ±0.001 and a possible resample containing only the positive cluster gave:

- Task 12 variance `2.506849295e-23`; V variance `−4.467866095e-22` → V invalid, Task 12 valid.
- With slightly smaller within-cluster spread, V produced a positive variance about **594×** Task 12, materially changing the Sharpes.

Fix: Remove the conditioning claim; define the exact finite-check order for `μ`, `Y`, `s1`, `s2`, `var`, `sd`, `S*`, and `S°`; add near-degenerate deterministic vectors. Prefer a stable variance calculation or a preregistered fail-closed conditioning bound, then recalibrate it.

**VS1-3 — BLOCKER — V_BINDING §2 line 49; Annex A P18-6**  
Problem: Using V for both calibration and evaluation does remove DS7’s fast-versus-exact equivalence problem. However, saying “the reference is V itself” makes P18-6 implementation/reference agreement tautological. Repeating the same function and self-generated vectors tests determinism, not independent agreement.  
Fix: Either explicitly amend P18-6 to require identity with the frozen V code/runtime artifact, or retain a separately reviewed reference harness and frozen expected decisions/vectors. Exact pass/fail agreement must remain testable.

**VS1-4 — BLOCKER — V_BINDING §3; `scripts/d19_pilot.py:19`**  
Problem: Single-threaded BLAS is necessary but insufficient for §27 reproduction. Python/NumPy/BLAS versions plus “CPU model class” do not fully bind executable binaries, BLAS dispatch, OS/architecture, CPU features, or floating-point environment. The pilot uses `setdefault`, so an existing non-1 thread setting is silently retained. Recording the real runtime after evaluation is not enforcement.  
Fix: Hash the Python executable, NumPy wheel and BLAS binary/config; bind OS/architecture and CPU feature/dispatch identity; verify one thread before computation; record and compare the evaluation environment to qualification. If that runtime later cannot be recreated, fail closed: the result is void and a new runtime requires requalification—no silent fallback.

**R-8/owner wording:** Not yet neutral. The question should disclose that V replaces a plausible Annex arithmetic requirement, may change values or availability near degeneracy, and creates a frozen-runtime dependency. Option B should say “retain Task 12 and accept/fund the larger compute requirement,” not simply “infeasible.”

Using one method V everywhere does remove the rejected 1%-audit equivalence problem.  
The present draft still needs explicit Annex authority, complete/stable edge-case arithmetic, a meaningful reference contract, and a fully frozen runtime.  
Do not choose A yet; revise and re-review the binding, then ask the owner with the numerical and reproducibility trade-offs stated plainly.
