# Codex Sol re-check of D-20 option C revision C4 (5599056)

Prompt: scratchpad `optc4_sol_prompt.md` (reproduced in section "Prompt" below). Reviewer metadata from the Codex CLI header (2026-10-30): model `gpt-6-sol`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a18cdf-6960-7ea1-882d-4e9b68da9ca6`, 72,253 tokens. Reviewed `OPTION_C_PROPOSAL_REV4.md` at `5599056`. Bitcoin node paused for the run (stopped at 708,104, restarted after).

Verdict: **ACCEPT WITH NOTES**: 0 BLOCKER, 1 NON-BLOCKING (D20C4-S-1). Findings D20C4-S-1, no gaps.

No finding is left unrepaired by decision yet; D20C4-S-1 goes in the next revision or erratum.

## Report (verbatim)

## Verdict: ACCEPT WITH NOTES

C4 is an **inactive amendment proposal**. It repairs the C3 blockers and is ready to put to the owner with the stated Q7 and S4 decisions still open. This review accepts no binding and changes no frozen rule.

| C4 disposition | Assessment | Evidence |
|---|---|---|
| D20C3-A-1 | **ACCEPT** | [C4 item 1](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md:27>) checks for an existing ATTESTATION delivery or VOID before cap and revision checks in both operations. At `C−1`, a certificate entry that survives and becomes durable at `C+1` remains effective under the *proposed* Q7 rule; later calls write nothing. A prior VOID likewise stays VOID. |
| D20C3-S-1 | **ACCEPT** | [Items 2 and 4](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md:35>) align the §7(c) accounting categories with the projected fields and visibility rules, including the pending list and complete or incomplete cycle report. |
| D20C3-A-2 | **ACCEPT** | The row now covers Q2b rejection reasons, CAP/REVISION VOID reasons, and revision/invalidation entries; §7(b) applies to the six `request_release` responses. [Item 3](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md:52>) deletes the extra cap warning. Withholding the commitment and record hashes from the **reader** leaves the publisher’s release entry and P-8 checks available; the owner still receives the §13 attestation fields. |
| D20C3-A-3 | **ACCEPT** | [Item 5](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md:60>) limits the immutability claim to a *released* result and tells the owner about the added bookkeeping. |
| D20C3-S-2 | **ACCEPT WITH NOTES** | [Item 6](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md:70>) fixes the before-`R_0` T-S2 call and the terminated-cycle TC-6 assertion. The inherited T-S6 wording still needs the correction below. |
| D20C3-A-4 | **ACCEPT WITH NOTES** | Item 6 also replaces the incident-specific `STOPPED` claim and the named `state`/`guard_state` calls. Its remaining test-shape inconsistency is below. |

**D20C4-S-1 — NON-BLOCKING — inherited C3 §1.10a T-S6 supersession.** [C3 says](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV3.md:162>) the release entry and RESULT delivery file have “identical shape.” [C4 item 2](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md:50>) now makes the file `{evaluation_id, result, released_at}`, while [C2 §1.3](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV2.md:107>) retains `commitment` in the release entry. **Failure scenario:** a literal T-S6 shape assertion fails on a correct implementation. **Minimal repair:** say that each record type has one fixed shape across every FAIL cause, and that their shared result and time fields agree. No new mechanism is needed.

Subject to that wording correction, C2+C3+C4 supports the owner questions. Q7’s check-time rule remains a proposed owner choice, and the channel, clock, reconciliation, and governance-action details remain for S4. No implementation tests, lint, or type checks apply to this read-only proposal review; no files were written.
## Prompt

# Re-check: D-20 option C, revision C4

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. Re-check `review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md` (Claude Opus 5.5, commit 5599056), a delta on `OPTION_C_PROPOSAL_REV3.md`, which is a delta on `OPTION_C_PROPOSAL_REV2.md`, itself a delta on `PROPOSAL_REV8.md`. It answers `SOL_OPTION_C3_REVIEW_415A0DE.md` (D20C3-S-1..2) and `ASTRA_OPTION_C3_REVIEW_415A0DE.md` (D20C3-A-1..4). Context as needed: `PROPOSAL_REV8.md`, `PROPOSAL_REV3.md`, `../d12-proposal/OWNER_DECISION_D12.md`, `../d12-proposal/PROPOSAL_REV7.md`, `docs/RESEARCH_CONSTITUTION.md` (§5, §6, §7, §13, §26), `schemas/attestation.schema.json`, `protocols/protocol_v1.yaml`.

**Direction:** simplify rather than patch; claim only what is true and testable. This is a focused re-check: prefer flagging a residual for honest disclosure over demanding new mechanism, unless a claim is false or a frozen rule is broken. Do not re-open points both C3 reviews accepted unless C4 broke them.

**IDs:** findings `D20C4-S-n`. Use exactly that prefix even if you cannot see your model variant; the caller verifies the model from the CLI header.

**Check:**
1. For EVERY C4 disposition (§1a), say ACCEPT, ACCEPT WITH NOTES or FIX, with evidence.
2. Item 1: the "already final" first step of `sign_permit` and `record_delivery(ATTESTATION)`; can an effective certificate or a VOID still change?
3. Items 2-4: does the reader projection table match exactly the proposed §7 row (b)-(d), including Q2b reason codes, VOID reasons, revision/invalidation entries, the cycle report and pending list? Is withholding the commitment and hashes from the reader consistent with every consumer (P-8, owner delivery, attestation fields)? Is the deleted cap warning safe?
4. Item 5 QC3 wording; item 6 supersessions (complete? anything still naming `state`, `guard_state`, `visible_from` or the closed-cycle refusal?).
5. Overall: with C2+C3+C4 read together, is option C now internally consistent and ready for the owner questions, apart from the owner/S4 decisions it routes?
**Findings:** each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
