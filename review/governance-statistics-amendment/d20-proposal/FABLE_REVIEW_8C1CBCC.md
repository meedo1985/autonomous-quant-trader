# Fable re-check VF2 of the D-20 V binding rev 2 at `8c1cbcc`: READY WITH FIXES

Date: 2026-10-04. R19-2 focused re-check, run as a Claude Code subagent with the `fable` model. The drafter is Claude Opus 5.5. The subagent's final report is reproduced below unchanged.

---

Reviewer: Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family. Review R19-2 (VF2), a focused re-check.
Commit: 8c1cbcc (V_BINDING.md rev 2, ADJUDICATION_8A3C2F2.md). Engine: d19-calibration-engine ea5b615. This review was read-only. I ran small in-memory checks with the repo .venv. No files were written and data/ was not opened.

Verdict: **READY WITH FIXES**

**Status of the last round's findings**

| ID | Status | Note |
|---|---|---|
| VF1-1 | Resolved | Constant replicate columns are refused. In 3,000 synthetic constant columns (T = 30/365/1247, levels 1e-8 to 7), none was accepted. The largest var/scale was 9e-32, against a 1e-20 threshold, so the margin is about 11 orders of magnitude. |
| VF1-2 | Resolved in design; the code wiring is incomplete (VF2-1) | The canary refused every unpinned case I tried: threads 2, 3, 4 and 8, CORETYPE=Prescott, and the environment set after NumPy import. SkylakeX crashes on this CPU, which also fails closed. |
| VF1-3 | Resolved | §2 states the clarification and the amendment fallback. |
| VF1-4 | Resolved in text | The binding is the code hash at the freeze and cites the decided D-20 record. |
| VF1-5 | Resolved | §1 gives the structural argument plus the test. |
| VF1-6 | Partly resolved | Cluster and constant-replicate tests were added. A sparse or heavy-tail reason-code comparison is deferred to the §4 reference vectors, which is acceptable. |
| VF1-7 | Resolved | One residual is VF2-5. |
| VS1-1 | Resolved | The Annex B reading is put to the owner explicitly. |
| VS1-2 | Resolved | Two-pass V checked against Task 12: on benign t(3) data the largest relative error in S* was 1.1e-13. On clusters it stays ≤ 5e-5 down to a spread of 1e-14 at level 0.05. It degrades only when the Sharpe exceeds about 1e14, which is meaningless. The finite checks run in order: μ, Y, s1, var, S*, S°. |
| VS1-3 | Resolved | Frozen vectors plus a Task 12 cross-check plus Task 12 reported on every evaluation is an acceptable replacement for the P18-6 reference. One wording conflict remains (VF2-4). |
| VS1-4 | Resolved in design; wiring gaps (VF2-1, VF2-3) | — |

**Answers**
- (2) The two-pass V is correct and stable. Rule 5 is exact in one direction only (VF2-2). The runtime check is adequate as a mechanism, but it is not yet mandatory (VF2-1).
- (3) The reference contract is acceptable. The owner question is accurate and close to neutral (VF2-5).
- (4) No blocker.

**New findings**

- **VF2-1 (MAJOR): enforcement is not wired.**
  - Location: `calibration/dsr.py` `v_runtime_check` and the `numerics="v"` path; V_BINDING §3.
  - Problem: §3 says the check "runs before any computation" and "compares the full identity". In code, `expected=None` skips the identity comparison by default. Nothing in the V path calls the check. Its only caller is `scripts/d19_pilot.py:72`, which passes no identity. No test covers refusal on an identity mismatch.
  - Fix: make `expected` a required argument. Call the check from the calibration driver and the evaluation entry, or inside the V path, using the frozen identity from the qualification object. Add an identity-mismatch refusal test.

- **VF2-2 (MINOR): rule 5 is exact in one direction only.**
  - Location: V_BINDING §1 step 5, "Rule 5, applied exactly"; `_replicates_v`.
  - Problem: Every constant column is refused. But distinct drawn values that are 1–2 ulp apart can merge when Y = X − μ is formed, which gives var = 0 and makes the replicate invalid where Task 12 is valid. This happened in 27 of 2,000 synthetic cases. These cases are unrealistic for real returns, but the "exactly" claim overstates.
  - Fix: for columns flagged by the threshold, compute var with the Task 12 two-pass on the drawn values. These columns are rare, so this is cheap, and it makes rule 5 exact both ways. Alternatively, reword step 5 to "a constant column is always invalid; a column with distinct values within rounding of each other may also be".

- **VF2-3 (MINOR): the interpreter hash does not cover the interpreter.**
  - Location: `runtime_identity` `python_executable_sha256`.
  - Problem: In a Windows venv, `sys.executable` is the launcher copy, not the interpreter binary or `python3xx.dll`. Only `sys.version` binds the interpreter.
  - Fix: hash `sys._base_executable` and the Python DLL or shared library, or state the limitation in §3.

- **VF2-4 (MINOR): §4 contradicts §7 on decision agreement.**
  - Location: V_BINDING §4.
  - Problem: §4 says every vector "must agree" with Task 12 on every decision, and the vectors include near-degenerate cases. §7 and VF2-2 say V can legitimately differ there.
  - Fix: record the Task 12 decision for each vector. Require agreement except on vectors designated near-degenerate before the freeze, where any difference is recorded and disclosed.

- **VF2-5 (MINOR): the owner question omits which result governs.**
  - Location: V_BINDING §7, owner question item (3).
  - Problem: It says the original calculation is "also run and reported" but not that V's result governs if the two disagree.
  - Fix: append "if they disagree, V's result counts and the difference is disclosed".

**For the owner**
1. The fast method V is now numerically sound: it matches the original calculation except in absurd edge cases, and it correctly refuses flat resamples.
2. The pinned computer setup is checked by a test that catches every wrong setting I tried, but the code must be made to run that check every time, not only when someone remembers to call it.
3. After the small fixes above, the question is fair to put to you. Its real trade-off is about 12,000 CPU-hours with V against tens of thousands with the original calculation, plus a dependency on one frozen computer setup.
