# Sol re-check VS2 of the D-20 V binding rev 2 at `8c1cbcc` (engine `ea5b615`): NOT READY

Date: 2026-10-04. This is an R19-2 focused re-check by the different model family. The prompt was the same as Fable VF2's, with the ID prefix `VS2`.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a1079f-4d55-79d2-b738-bb70f957cfeb`. The final message is reproduced below unchanged.

---

**Model:** OpenAI Codex, GPT-5 family; exact serving identifier not exposed  
**Reviewed:** proposal `8c1cbcc`; engine `ea5b615`  
**Verdict:** **NOT READY**

The two-pass V arithmetic is correct and stable for the governed dimensions. Rule 5 now rejects exactly constant draws. The reference-vector contract is an acceptable explicit P18-6 replacement if the owner approves it and the reviewed vectors are frozen before qualification. The runtime enforcement remains a blocker.

| Finding | Status | Note |
|---|---|---|
| VF1-1 | Resolved | Stable two-pass variance and exact constant-draw rejection. |
| VF1-2 | Unresolved | Runtime guard is bypassable; see VS2-1. |
| VF1-3 | Resolved | Annex B interpretation is explicitly put to the owner. |
| VF1-4 | Resolved at proposal stage | Function hash and decided D-20 record are required at freeze. |
| VF1-5 | Resolved | PW implementation identity is stated and tested. |
| VF1-6 | Partial | Constant/cluster tests exist; no end-to-end challenge-cell reason-code comparison yet. |
| VF1-7 | Resolved | Trade-offs and measured cost are stated neutrally. |
| VS1-1 | Resolved | Clarification versus amendment boundary is explicit. |
| VS1-2 | Resolved | Cancellation defect and ordinary finite-output checks are fixed. |
| VS1-3 | Resolved at proposal stage | Frozen vectors make agreement testable; owner approval remains required. |
| VS1-4 | Unresolved | Same runtime blocker as VF1-2/VS2-1. |

### New findings

| ID | Severity | Location | Problem | Fix |
|---|---|---|---|---|
| VS2-1 | **BLOCKER** | `V_BINDING.md` §3; `calibration/dsr.py` `evaluate`, `v_runtime_check`; `scripts/d19_pilot.py:72` | `evaluate()` can run V without the guard. The pilot calls the guard without the frozen expected identity; `runtime_identity()` is not recorded or compared. Thus “runs before any computation” and “full identity compared” are not implemented fail-closed. | Make the frozen expected identity mandatory at every calibration/evaluation entrypoint, prevent V execution until it passes, record the identity in qualification/evaluation artifacts, and test bypass plus identity mismatch. |
| VS2-2 | Non-blocking | `V_BINDING.md` §1 step 1; `_replicates_v` | Extreme but finite float64 inputs can make `math.fsum` raise `OverflowError` instead of returning `INVALID_REPLICATE`; the stated input contract has no magnitude bound. | Catch arithmetic overflow at the boundary or specify and enforce a finite-magnitude domain. |

The canary itself has teeth: fresh processes produced different hashes for 1/2/8 threads and Haswell/Prescott. The defect is mandatory invocation and frozen-identity comparison, not the canary. The owner question is otherwise accurate and balanced, but its automatic-runtime-check claim is presently false.

No files were written and `data/` was not accessed. Per repository policy, this review is not a completed R19-2 record until its findings are committed later.

The fast V calculation now fixes the earlier unstable variance and flat-sample problems.  
The remaining blocker is that V can still run without proving it is on the frozen computer setup.  
Do not choose A yet; make that guard and identity record mandatory, then re-check and put the choice to the owner.
