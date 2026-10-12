# Sol narrow check of the REG-1/REG-2/O-8 proposal rev 4 at `70cd0fa` — NOT READY

Date: 2026-10-04. This is the OpenAI-family narrow check for R19-2, run with prompt `REVIEW_PROMPT_R2.md`, prefix SR4, and a narrow-scope preamble. It ran in parallel with Fable FR4, without sight of it.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header shows `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a10593-5ce0-7622-8313-c3f82a63ff69`. The final message below is verbatim.

---

Model: **GPT-5 Codex, OpenAI family** (exact serving variant not exposed)  
Commit: `70cd0faa23323f627172a0b0231142a5d8b31266`  
Verdict: **NOT READY**

SR3-1 through SR3-4 are resolved. All three §6 owner questions are neutral, accurate, and sufficiently complete.

| ID | Severity | Location | Evidence | Proposed disposition |
|---|---|---|---|---|
| SR4-1 | BLOCKER | `PROPOSAL.md` §4, lines 187–189; adjudication lines 70–71 | “Default relay allows up to 83 bytes” is stated as a universal present fact. It is client/version-specific relay policy and is ambiguous about script size versus payload size; therefore “the 90-byte message is too long” does not follow without an exact implementation/version and encoding contract. Network verification was prohibited. | Qualify the claim with the exact client/version and byte accounting, or remove it until O-6a’s separate specification and review. |

Owner: All four SR3 findings are repaired.  
Owner: The three §6 decisions are ready as written.  
Owner: Correct the deferred O-6a relay-limit assertion, then the packet is ready; commit this review record before relying on it.
