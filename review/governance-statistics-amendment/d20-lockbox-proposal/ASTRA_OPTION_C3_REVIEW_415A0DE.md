# Codex Astra re-check of D-20 option C revision C3 (415a0de)

Prompt: scratchpad `optc3_astra_prompt.md` (reproduced in section "Prompt" below). Reviewer metadata from the Codex CLI header (2026-10-30): model `gpt-6-astra`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a18cd1-937d-71a3-9857-bb779f073f21`, 82,109 tokens. Reviewed `OPTION_C_PROPOSAL_REV3.md` at `415a0de`. Bitcoin node paused for the runs (stopped at 706,069, restarted after both). Sol and Astra ran sequentially with outputs in the session scratchpad only.

Verdict: **FIX** (REVISION_REQUIRED): 3 BLOCKER (D20C3-A-1..3), 1 NON-BLOCKING (A-4). Findings D20C3-A-1..4, no gaps. Astra notes none requires new machinery.

No finding is left unrepaired by decision yet; dispositions go in revision C4.

## Report (verbatim)

**VERDICT: FIX.** Binding status: **REVISION_REQUIRED**. Three blocking text inconsistencies remain; none requires new machinery.

Reviewed C3 byte-for-byte against `415a0de`, independently of any other C3 review. Frozen governance controls; the D-12 decision requires its signed amendment; C3 remains inactive. This review grants no acceptance or activation.

Every §1a disposition is assessed below. References are to C3 unless stated otherwise.

| Disposition | Assessment | Evidence |
|---|---|---|
| D20C2-S-1 / D20C2-A-3 | **ACCEPT WITH NOTES** | §1.5a distinguishes check-time effectiveness from durability, acknowledges the owner already holds certificate bytes, and routes the proposed P-6 meaning to Q7. Physical completion before C is expressly **not** guaranteed. |
| D20C2-S-2 / D20C2-A-1 | **ACCEPT** | §1.6 specifies attempts, waiting for `R_0`, daily retries, indefinite blockage, incomplete reports and missing-outbox recovery. |
| D20C2-A-2 | **ACCEPT** | §1.1 and §1.6 allow report visibility from termination for every cause, including subsequent releases; terminated-cycle requests remain serviceable. |
| D20C2-S-3 | **FIX** | §1.7 correctly discloses pre-release technical FAIL, but QC3 expressly retains the contradictory closing sentence. A-3 below. |
| D20C2-S-4 / D20C2-A-6 | **FIX** | Six codes and undifferentiated `STOPPED` are correctly defined. The proposed §7 exception still does not cover the complete interface. A-2; inherited wording also needs A-4. |
| D20C2-S-5 / D20C2-A-6 | **FIX** | Cap/revision refusal can now create VOID without signing, but the new append predicate omits protection for an already effective certificate. A-1. |
| D20C2-A-4 | **ACCEPT** | §1.5c correctly distinguishes operation order from timestamp accuracy and explicitly discloses forward-clock jumps. |
| D20C2-S-6 / D20C2-A-5 | **ACCEPT WITH NOTES** | Listed signer clauses, replay role, T-S2/T-S6 references and errata are addressed. Supersession remains incomplete or ambiguous in the places identified by A-4. |
| D20C1-A-3 | **ACCEPT** | The missing disposition is restored; C2 §1.5 still binds signed `cooling_off_start` to RESULT delivery, consistent with Constitution §13 and the frozen schema. |

**D20C3-A-1 — BLOCKER — [§1.5b, lines 74–78](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV3.md:74>): VOID predicate includes already effective certificates.**

Scenario: a PASS has RESULT and ATTESTATION delivery entries. After C—or after a subsequent revision—the publisher calls `sign_permit`. C2’s permit conditions refuse it, but C3’s replacement refusal rule now instructs the store to append VOID: PASS, RESULT delivery and cap/revision conditions all hold. Both terminal records can then exist. Refusing a *second VOID* does not prevent this.

The ordinary request path skips already effective certificates, but the store operation’s stated contract contradicts C2’s “VOID and effective are final” invariant and P-6’s preservation of already attested nominees.

**Minimal repair:** before evaluating cap/revision refusal, return/refuse without mutation when an ATTESTATION delivery or VOID entry already exists. Test this after both C and revision. No new record or operation is needed.

**D20C3-A-2 — BLOCKER — [§1.8, lines 122–124](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV3.md:122>): the exception is not exactly the interface.**

Scenario: the reader receives a pre-read rejection and its reason, permitted by §1.1 and the decided D-12 Q2b. Paragraph (c) does not enumerate rejection facts/reasons, while the closing sentence forbids every other visible field/message/record. Newly explicit reader access to VOID entries and their CAP/REVISION reason is likewise not expressly covered. The retained `request_release` warning at C2 line 203 is also outside the six fixed answers.

**Minimal repair:** scope paragraph (b) to the **response code of `request_release`**; explicitly include the permitted rejection and VOID accounting facts in (c), preserving Q2b. Delete the convenience warning or expressly enumerate it. Do not add diagnostics.

**D20C3-A-3 — BLOCKER — [§3, line 181](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV3.md:181>): QC3 retains the false reassurance it was meant to repair.**

C3 says the closing sentence is unchanged. [C2 line 390](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV2.md:390>) therefore remains: “None of this can change a result.”

Scenario: resource contention delays a would-be PASS finish beyond `D*`, producing technical FAIL. C3 now explains that correctly, then preserves an unqualified reassurance immediately below it.

**Minimal repair:** replace the first sentence with “Once a result is released, these delays cannot change it.” Preserve the amendment explanation and options.

**D20C3-A-4 — NON-BLOCKING — §1.10a and inherited residual/tests: finish the supersession explicitly.**

An implementer still encounters:

- C2 line 232: `STOPPED` establishes that an incident occurred, contrary to C3’s deliberately undifferentiated refusal.
- C2 TC-6 line 296: closed-cycle IDs return `STOPPED`, contrary to C3’s terminated-cycle service rule. “TC-6 changed” should explicitly replace this assertion.
- Retained rev-8 T-S1’s `begin_read` concurrency test still names removed `state` and `guard_state` operations.
- T-S2’s replacement `release` needs an explicit `≥ R_0` call time. A call at the old `R_0 − 21,600` threshold must refuse, not show the finish.

**Minimal repair:** list these narrow replacements. They require no architectural change.

The remaining boundary checks support C3:

| Consumer / quantity | Assessment |
|---|---|
| Effectiveness: `t_e < C`, host-clock seconds | Consistent with C2’s finish convention and rev-8 Q7. A check at `C−1` and durability at `C+1` counts by the proposed convention, despite a two-second boundary crossing. |
| Revision ordering | An earlier revision prevents new effectiveness; later revisions preserve earlier effectiveness, subject to repairing A-1. |
| Release: `R_0 = start + 604,800 s` | A revision one day after start leaves six days before release is permissible. C15 correctly records pending status. |
| Cooling-off: `259,200 s` | Correctly equals 72 hours under the disclosed accurate-clock assumption. TC-3 establishes order only. |
| Promotion cap | Check-time effectiveness does not waive the separate owner-decision deadline. |
| Backstop/report | C3 and C12–C15 cover the identified recovery cases. No bounded-completion claim remains. Added automatic work creates contention within the disclosed timing residual; accounting exposes no new sealed diagnostic. |

QC1 and Q7 are otherwise fair and plain. `STOPPED` is adequately undifferentiated in the new definition and TC-6 bytes test; it does not promise timing indistinguishability.

Read-only validation confirmed C3’s commit identity, clean working/staged diffs, 14 frozen sidecars, manifest bindings and Constitution canonical hash. Protected-file comparison found only the existing CRLF/LF checkout difference in `docs/README.md`; C3 changes only its proposal file. Exact commands/results are in the tool transcript.

Implementation tests, lint, typing and import checks are N/A for this proposal-only review. Platform durability remains unverified. Nothing was written or committed; this response is not a committed repository review record.
## Prompt

# Re-check: D-20 option C, revision C3

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. Re-check `review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV3.md` (Claude Opus 5.5, commit 415a0de), a delta on `OPTION_C_PROPOSAL_REV2.md` (which is a delta on `PROPOSAL_REV8.md`). It answers `SOL_OPTION_C2_REVIEW_A56F220.md` (D20C2-S-1..6) and `ASTRA_OPTION_C2_REVIEW_A56F220.md` (D20C2-A-1..6). Review independently of any other C3 review; none is in the repository. Context as needed: `PROPOSAL_REV8.md`, `PROPOSAL_REV3.md`, `PROPOSAL_REV4.md`, `PROPOSAL_REV6.md` l.165-170, `../d12-proposal/OWNER_DECISION_D12.md`, `../d12-proposal/PROPOSAL_REV7.md`, `docs/RESEARCH_CONSTITUTION.md` (§5, §6, §7, §13, §26), `schemas/attestation.schema.json`, `protocols/protocol_v1.yaml`.

**Direction:** simplify rather than patch; claim only what is true and testable. This is a focused re-check: prefer flagging a residual for honest disclosure over demanding new mechanism, unless a claim is false or a frozen rule is broken. Do not re-open points both C2 reviews accepted unless C3 broke them.

**IDs:** findings `D20C3-A-n`. Use exactly that prefix even if you cannot see your model variant; the caller verifies the model from the CLI header.

**Check:**
1. For EVERY C3 disposition (§1a), say ACCEPT, ACCEPT WITH NOTES or FIX, with evidence. You may check the other reviewer's rows.
2. §1.5a: check-time versus durability for effectiveness; the proposed P-6 reading routed to Q7; the corrected "nobody can read" statement. Consistent with C2's finishing rule and rev 8's Q7?
3. §1.5b: VOID appended by `sign_permit` at cap/revision; at most one VOID; no PASS becomes FAIL; no certificate effective after C or after a revision.
4. §1.6: backstop "attempts", waiting for `R_0`, daily retries, report visibility for every termination cause, incompleteness, outbox recovery. Any remaining false guarantee or new channel?
5. §1.7 and §1.8: is the §7 row now exactly the interface (six codes, public accounting facts, timing effects including pre-release technical FAIL)? Is `STOPPED` adequately undifferentiated?
6. §1.5c clock qualification; §1.9 rows C3, C12-C15 and tests; §1.10a supersessions (complete?); §3 owner question wording (fair and plain for a non-statistician).

**Findings:** each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
