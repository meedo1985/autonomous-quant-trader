# Codex Sol re-check of D-20 option C revision C3 (415a0de)

Prompt: scratchpad `optc3_sol_prompt.md` (reproduced in section "Prompt" below). Reviewer metadata from the Codex CLI header (2026-10-30): model `gpt-6-sol`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a18ccf-907d-7f23-b159-70105a0557c1`, 64,235 tokens. Reviewed `OPTION_C_PROPOSAL_REV3.md` at `415a0de`. Bitcoin node paused for the runs (stopped at 706,069, restarted after both). Sol and Astra ran sequentially with outputs in the session scratchpad only.

Verdict: **FIX**: 1 BLOCKER (D20C3-S-1), 1 NON-BLOCKING (S-2). Findings D20C3-S-1..2, no gaps.

No finding is left unrepaired by decision yet; dispositions go in revision C4.

## Report (verbatim)

## VERDICT: FIX

C3 remains an **inactive amendment proposal**. Its check-time certificate rule is stated clearly and put to the owner in Q7; neither this review nor the proposed wording accepts that rule on the owner’s behalf. The backstop and pre-release timing claims are substantially narrower and supportable. Two textual inconsistencies remain.

### C3 §1a dispositions

| C3 row | Assessment | Evidence |
|---|---|---|
| D20C2-S-1 / A-3 | **ACCEPT WITH NOTES** | [§1.5a](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV3.md:58>) separates the check at \(t_e<C\) from durability, handles whole and lost entries after C, and gives Q7’s owner choice. The proposed reading of D-12 P-6 remains a decision, not an established frozen meaning. |
| D20C2-S-2 / A-1 | **ACCEPT** | [§1.6](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV3.md:85>) says *attempts*, waits for \(R_0\), retries daily, restores missing outboxes, and leaves reports incomplete through unresolved failure. It promises no completion date. |
| D20C2-A-2 | **ACCEPT** | The reader row and report now expose releases after termination for calendar, revision, and invalidation causes; terminated-cycle requests remain serviceable. |
| D20C2-S-3 | **ACCEPT** | [§1.7](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV3.md:108>) limits immutability to a *released* result and discloses a deadline-induced technical FAIL before release. |
| D20C2-S-4 / A-6 | **FIX** | The six codes and undifferentiated `STOPPED` agree with the request path. The proposed §7 row still omits some records exposed by the reader row; see D20C3-S-1. |
| D20C2-S-5 / A-6 | **ACCEPT** | [§1.5b](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV3.md:72>) appends one terminal VOID on cap or revision refusal without requiring a signer call. A released PASS remains PASS. |
| D20C2-A-4 | **ACCEPT** | §1.5c limits the delivery claim to operation order and makes actual elapsed cooling-off conditional on R3’s clock, including no forward jump. |
| D20C2-S-6 / A-5 | **FIX** | The supersession list addresses the cited old operations, but its T-S2 replacement is false for a permitted test time, and an inherited TC-6 assertion conflicts with terminated-cycle service; see D20C3-S-2. |
| D20C1-A-3 | **ACCEPT** | C2 restores signed `cooling_off_start`; C3 records the previously omitted disposition. This matches [Constitution §13](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/docs/RESEARCH_CONSTITUTION.md:121>) and the [schema](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/schemas/attestation.schema.json>). |

### Findings

- **D20C3-S-1 — BLOCKER — [§1.1 and proposed §7 row](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV3.md:118>).** The reader row exposes rejection, VOID, and invalidation entries, and release entries contain a commitment. Proposed §7(c) lists identity, times, pending/report facts, and *revision* entries, then permits no other visible field or record. **Failure scenario:** the owner reads a pre-read rejection reason accepted under D-12 Q2b, or a VOID reason, although the signed exception would exclude that record or field. **Minimal repair:** align the §7 list and the reader’s public field projection exactly. Include the intended rejection reasons and invalidation/VOID facts, or withhold fields that the exception does not authorize. Keep the six response codes as written.

- **D20C3-S-2 — NON-BLOCKING — [§1.10a and §1.9](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV3.md:126>).** The proposed rev 8 T-S2 replacement says a concurrent `release` waits for a finish and “then shows it.” T-S2 advances the clock only past \(R_0-21{,}600\), where release can still be before \(R_0\) and must refuse. For example, at \(R_0-21{,}599\), it is **21,599 seconds too early**. Also, inherited C2 TC-6 says a closed-cycle ID returns `STOPPED`, while C3 serves terminated-cycle IDs. **Minimal repair:** make T-S2 expect refusal before \(R_0\) and the result at or after \(R_0\); explicitly supersede TC-6’s closed-cycle assertion with C3’s terminated-cycle test.

The certificate boundary is internally consistent under the stated clock and storage assumptions: a check at \(C-1\) followed by fsync at \(C+1\) counts at \(C-1\) under the **draft** Q7 rule, while `PASS_CERTIFIED` is unavailable until durability. A revision cannot pass an attestation append under the same index lock. The owner question states the after-cap cost plainly. No implementation tests, lint, or type checks apply to this read-only proposal review; no files were written.
## Prompt

# Re-check: D-20 option C, revision C3

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. Re-check `review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV3.md` (Claude Opus 5.5, commit 415a0de), a delta on `OPTION_C_PROPOSAL_REV2.md` (which is a delta on `PROPOSAL_REV8.md`). It answers `SOL_OPTION_C2_REVIEW_A56F220.md` (D20C2-S-1..6) and `ASTRA_OPTION_C2_REVIEW_A56F220.md` (D20C2-A-1..6). Context as needed: `PROPOSAL_REV8.md`, `PROPOSAL_REV3.md`, `PROPOSAL_REV4.md`, `PROPOSAL_REV6.md` l.165-170, `../d12-proposal/OWNER_DECISION_D12.md`, `../d12-proposal/PROPOSAL_REV7.md`, `docs/RESEARCH_CONSTITUTION.md` (§5, §6, §7, §13, §26), `schemas/attestation.schema.json`, `protocols/protocol_v1.yaml`.

**Direction:** simplify rather than patch; claim only what is true and testable. This is a focused re-check: prefer flagging a residual for honest disclosure over demanding new mechanism, unless a claim is false or a frozen rule is broken. Do not re-open points both C2 reviews accepted unless C3 broke them.

**IDs:** findings `D20C3-S-n`. Use exactly that prefix even if you cannot see your model variant; the caller verifies the model from the CLI header.

**Check:**
1. For EVERY C3 disposition (§1a), say ACCEPT, ACCEPT WITH NOTES or FIX, with evidence. You may check the other reviewer's rows.
2. §1.5a: check-time versus durability for effectiveness; the proposed P-6 reading routed to Q7; the corrected "nobody can read" statement. Consistent with C2's finishing rule and rev 8's Q7?
3. §1.5b: VOID appended by `sign_permit` at cap/revision; at most one VOID; no PASS becomes FAIL; no certificate effective after C or after a revision.
4. §1.6: backstop "attempts", waiting for `R_0`, daily retries, report visibility for every termination cause, incompleteness, outbox recovery. Any remaining false guarantee or new channel?
5. §1.7 and §1.8: is the §7 row now exactly the interface (six codes, public accounting facts, timing effects including pre-release technical FAIL)? Is `STOPPED` adequately undifferentiated?
6. §1.5c clock qualification; §1.9 rows C3, C12-C15 and tests; §1.10a supersessions (complete?); §3 owner question wording (fair and plain for a non-statistician).

**Findings:** each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
