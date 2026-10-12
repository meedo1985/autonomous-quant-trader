# Sol narrow re-check VS3 of the D-20 V binding rev 3 at `309f75b` (engine `e021207`): READY WITH FIXES

Date: 2026-10-04. This is an R19-2 narrow re-check by the different model family.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a107a7-fdee-7831-8c29-49e2da4573dc`. The final message is reproduced below unchanged.

---

Model: OpenAI Codex, GPT-5 family; exact serving identifier not exposed  
Reviewed commits: proposal `309f75b`; engine `e021207`  
Verdict: **READY WITH FIXES**

| Finding | Status | Basis |
|---|---|---|
| VS2-1 | Resolved at proposal stage | `expected` is mandatory; unchecked V refuses; identity mismatch and missing environment refuse. The future driver contract is sufficient at this stage. |
| VS2-2 | Resolved | `fsum` overflow is caught and returns `INVALID_REPLICATE`; focused check passed. |
| VF2-1 | Resolved at proposal stage | Same mandatory, fail-closed runtime mechanism as VS2-1. |
| VF2-2 | Resolved in code | Flagged distinct-value columns use Task 12 two-pass variance. |
| VF2-3 | Resolved | Runtime identity includes the base executable and `python314.dll` on the reviewed machine. |
| VF2-4 | Resolved | Near-degenerate exceptions are designated before freeze and disclosed. |
| VF2-5 | Resolved | Owner question states that V governs disagreements. |

New findings:

- **VS3-1 — NON-BLOCKING:** `ADJUDICATION_8C1CBCC.md:16` and commit `e021207` claim the pilot prints/records its runtime identity, but `scripts/d19_pilot.py:72-94` only checks it and prints cell rows. Print/store the identity once, or narrow those claims.
- **VS3-2 — NON-BLOCKING:** `V_BINDING.md:107` claims Rule 5 is tested in both directions, but no regression reproduces VF2-2’s distinct raw values merging after centering. Add that focused case or narrow the evidence statement.

Validation: both focused in-memory checks passed; engine diff check passed. No network, restricted data, edits, commits, or pushes.

Method V’s arithmetic and runtime refusal are ready for your decision.  
The missing full-run driver is acceptable now because V itself refuses unchecked execution and the driver contract is explicit.  
Before presenting it, correct the pilot-identity claim and add the missing near-degenerate regression test.
