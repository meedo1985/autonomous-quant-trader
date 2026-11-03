# Codex Astra re-check of R-14a rev 2 (f1be832)

Prompt: reproduced in section "Prompt" below. Reviewer metadata from the Codex CLI header (2026-10-31): model `gpt-6-astra`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a191e4-9c96-7a31-917d-bbd1ed58c6d5`, 92,515 tokens. Reviewed `review/governance-statistics-amendment/r14-exception/PROPOSAL_REV2.md` at `f1be832`, independently (run after Sol's re-check; Sol's report was not in the repository).

Verdict: **ACCEPT WITH NOTES**: 0 BLOCKER, 2 NON-BLOCKING (R14A2-A-1..2). No gaps in numbering.

Disposition: both to be applied in a text-only rev 3 erratum; none left unrepaired.

## Report (verbatim)

**Verdict: ACCEPT WITH NOTES.** No blockers to the owner deciding on this narrow exception. Reviewed `f1be832` on `freeze-sheet`, independently of any other rev 2 re-check. This is advice on an inactive proposal, not approval to sign C2, implement, merge, or access data.

All ten prior findings are addressed, with the qualifications below.

| §1a disposition | Re-check | Evidence |
|---|---|---|
| R14A-S-1 / R14A-A-2: input handling can change statistics | **ACCEPT** | Items 4–5 replace the “only calls” assurance with requirements covering timestamps, pairing, transformations, availability and outputs. Consumer-boundary tests are required; their success is not claimed. |
| R14A-A-1: A4 needs later statistical implementation | **ACCEPT** | Item 4 expressly permits A4’s `m ≠ n` generator; item 8 names the R-8 extension. §2 correctly distinguishes qualified primitives from unqualified composition. D-20 A6’s full primitive bindings must still appear in signed C2. |
| R14A-S-2 / R14A-A-5: execution identities and access | **ACCEPT WITH NOTES** | Item 6 preserves Constitution §§7–7a and D-11’s read gate and handoff restrictions. Removing cross-imports does not itself enforce those boundaries. A7’s placement needs clarification below. |
| R14A-S-3: copied beacon seeds could pass | **ACCEPT** | Item 7 requires independent verification of the accepted post, selected round, signature and derived seeds before gates run. It retains C2’s `seed_disclosure` failure rule. FP3’s D-19-only indefinite waiting rule is not imported. |
| R14A-S-4 / R14A-A-3: tuning and review guarantees | **ACCEPT** | §2 now discloses public-history influence, changes before signing, implementation errors and the limits of qualification. Review and tests are correctly described as controls. |
| R14A-S-5 / R14A-A-4: timing evidence | **ACCEPT WITH NOTES** | The proposed hash chain is supported, subject to the precise containment requirement and chronology limit below. |

The item 2 hash-chain claim is valid **if the two hash rows are contained in the protocol identified by the declaration’s `protocol_hash`**. [Annex B §2.4](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_B_DSR_METHOD.md:95) includes that field; DRAFT §2.0 posts the canonical declaration’s digest; the frozen canonicalization rule hashes the structured content, excluding its self-referential hash. Thus the complete chain is:

`accepted post → declaration digest → declaration.protocol_hash → protocol containing module hashes → loaded bytes`

Merely putting module hashes elsewhere in the signed commit would not establish that chain. Read as the proposed **protocol row**, R-14a establishes the necessary requirement and refuses an unverifiable link. No additional timestamp system is needed. No actual C2 anchor is established by this proposal alone.

**R14A2-A-1 — NON-BLOCKING**

**Place:** [PROPOSAL_REV2.md items 3–6](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/r14-exception/PROPOSAL_REV2.md:30), against D-20 A7.

**Failure scenario:** A builder places A4’s forecast computation only in the lockbox module, following its name and A7’s `code.lockbox_module_sha256` field. But A7 requires the experiment engine to recompute the confirmation source and seal its prediction artifact. Rev 2 forbids importing the other module and assigns the lockbox entry point exclusively to `lockbox_eval`. That implementation would leave the authorised sealing path unavailable.

This is an allocation ambiguity, not an unavoidable contradiction: item 4 permits the confirmation module to implement the signed forecast rules.

**Minimal repair:** In the already-required contract, explicitly allocate A7’s confirmation-side forecast and sealing work, including its stored artifact, to the experiment-engine path. Identify the actual producing code and clarify the meaning of A7’s module-hash field. No additional module or broader data access is necessary.

**R14A2-A-2 — NON-BLOCKING**

**Place:** [PROPOSAL_REV2.md item 2 and §2](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/r14-exception/PROPOSAL_REV2.md:29).

**Failure scenario:** A valid later declaration anchor is treated as proof that nobody previously read protected data. The chain establishes committed content and supports verification before an authorised evaluation; it cannot establish the absence of earlier unauthorised reads or external public-history use. Rev 2 no longer expressly makes that guarantee, but the earlier chronology concern deserves an explicit residual.

**Minimal repair:** Add: “The later public anchor fixes these bytes; it does not independently prove that no protected-data access occurred earlier.” Retain existing access records and read gates; add no new mechanism.

Independent exact checks reproduced the substantive input-handling examples:

- `[-8,1,2,3]`: mean `−1/2`, sample variance `77/3`; dropping the first observation gives mean `2`, variance `1`.
- `[3,0,0]`: mean `1`, variance `3`; re-pairing to `[1,1,1]` gives zero variance and unavailable Sharpe.

Read-only validation used `rtk proxy python -I -B -`: 14 raw-file sidecars, seven manifest file bindings and the Constitution canonical self-hash passed. Frozen artifacts showed no changes against `23300c4`; `docs/README.md` differed only by checkout CRLF conversion. Git working/index diffs were empty. Runtime tests, lint, typing and import checks are N/A to this wording-only review; no implementation was validated.

The owner can decide on the exception with these notes disclosed. Complete contracts, builds, required reviews and formal activation remain prerequisites. Nothing was written; the caller must preserve this report and observed CLI model metadata before counting it as a committed review record.
## Prompt

# Re-check: proposed C2 row R-14a, rev 2

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. The checkout is on branch `freeze-sheet`. Re-check `review/governance-statistics-amendment/r14-exception/PROPOSAL_REV2.md` (Claude Opus 5.5, commit f1be832), a full replacement of `PROPOSAL.md` (23300c4). It answers `SOL_REVIEW_23300C4.md` (R14A-S-1..5) and `ASTRA_REVIEW_23300C4.md` (R14A-A-1..5); read both. Context as before: `review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md` (§2.0, R-7, R-8, R-13, R-14, seed_disclosure) and `ANNEX_B_DSR_METHOD.md` §2.4, `ANNEX_C_GATE_DEFINITIONS.md` (C-0, C-6); `d20-lockbox-proposal/PROPOSAL_REV3.md` (A4, A6, A7), `OWNER_DECISION_D20_LOCKBOX.md`; `d11-proposal/` owner decision; `docs/RESEARCH_CONSTITUTION.md` (§6, §7, §7a, §16, §27); `review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE.md`.

Review independently of any other rev 2 re-check; none is in the repository. Direction: simplify rather than patch; claim only what is true and testable. Focused re-check: prefer flagging a residual for honest disclosure over demanding new mechanism, unless a claim is false or a frozen rule is broken. Check: 1. every §1a disposition (ACCEPT / ACCEPT WITH NOTES / FIX, with evidence), including the claim in item 2 that the accepted C2 declaration post's `protocol_hash` covers the two module hashes; 2. anything rev 2 broke or still overclaims; 3. is it ready for the owner's decision?

IDs: `R14A2-A-n`. Use exactly that prefix; the caller verifies the model from the CLI header. Each finding: severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario, minimal repair. Verdict: ACCEPT, ACCEPT WITH NOTES, or FIX.
