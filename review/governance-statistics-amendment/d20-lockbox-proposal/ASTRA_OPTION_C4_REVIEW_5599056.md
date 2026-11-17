# Codex Astra re-check of D-20 option C revision C4 (5599056)

Prompt: scratchpad `optc4_astra_prompt.md`, the same as Sol's (`SOL_OPTION_C4_REVIEW_5599056.md` section "Prompt") except the ID prefix `D20C4-A-n` and the sentence "Review independently of any other C4 review: do not open `SOL_OPTION_C4_REVIEW_5599056.md` or `ASTRA_OPTION_C4_REVIEW_ATTEMPT_1.md`." (reproduced below). Reviewer metadata from the Codex CLI header (2026-10-31): model `gpt-6-astra`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a19185-64f0-74c3-a053-b70368cb1505`, 104,061 tokens. Second attempt; attempt 1 is `ASTRA_OPTION_C4_REVIEW_ATTEMPT_1.md`. Bitcoin node kept running for this run (owner choice).

Verdict: **ACCEPT WITH NOTES**: 0 BLOCKER, 2 NON-BLOCKING (D20C4-A-1, D20C4-A-2). No gaps in numbering.

No finding is left unrepaired by decision yet; D20C4-A-1 and D20C4-A-2 go in the C5 erratum together with D20C4-S-1.

## Report (verbatim)

**VERDICT: ACCEPT WITH NOTES.** No blocking defect found in C4’s operating rules. Two non-blocking wording issues remain in item 6. C2+C3+C4 is ready for the owner questions, subject to the required independent review and the owner/S4 decisions already routed. Binding status remains **AMENDMENT_REQUIRED**.

C4 matches commit `5599056` byte-for-byte. I did not open either excluded C4 review.

| Authority | Status |
|---|---|
| Constitution, protocol and attestation schema | Frozen and controlling |
| D-12 owner decisions | Recorded; binding only through the signed amendment |
| C2+C3+C4 | Inactive proposals; this review grants no activation or acceptance authority |

Every C4 §1a disposition:

| Disposition | Assessment | Evidence |
|---|---|---|
| **D20C3-A-1** | **ACCEPT** | [Item 1](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md:28) puts the terminal-state check first in both operations, under `L_store`. Neither can append VOID after effectiveness or append ATTESTATION after VOID. |
| **D20C3-S-1 / D20C3-A-2** | **ACCEPT** | [Items 2–4](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md:35) align the field projection with §7(c), scope §7(b) to release requests, and delete the extra warning. Consumer checks below. |
| **D20C3-A-3** | **ACCEPT** | [Item 5](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md:62) limits immutability to released results. C3’s disclosure that pre-release delay can cause technical FAIL remains intact. |
| **D20C3-S-2 / D20C3-A-4** | **ACCEPT WITH NOTES** | [Item 6](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md:69) explicitly replaces the four cited passages. Its test wording needs the qualifications below; one inherited operation list still names removed calls. |

The final-state repair holds for both call orders. Starting with an effective certificate, either operation called after C or after revision returns without mutation. Starting with VOID, either operation also returns without mutation—even if an earlier permit or signature remains available. Serialization prevents concurrent calls from producing both terminal entries. This preserves certification state; it does not waive the separate promotion deadline or other governing incident/replay rules.

The disclosure and consumer cross-check is consistent:

| Consumer | Result |
|---|---|
| §7(b), release-request response | Exactly the six fixed responses; no cap warning remains. |
| §7(c), reader projection | Covers identity/exposure/`R_0`; Q2b rejection reasons including `ANCESTOR_UNRELEASED`; release times/results; delivery kinds/times; CAP/REVISION VOID reasons; revision **and invalidation** entries; pending IDs; complete/incomplete cycle reports. Item 2 supplies the exact fields and visibility rules. |
| §7(d), residual disclosure | Covers timing, undifferentiated refusal, unbounded delay, cap expiry and pre-release deadline FAIL. It does not authorize diagnostic payloads. |
| P-8 and signer | Publisher retains privileged pre-read identities and attestation validation inputs. Signer retains the sealed-reference/commitment verification. Neither depends on the reader receiving a commitment or release-entry hash. |
| Owner delivery and §13 attestation | RESULT becomes the three-field file. C2 §1.4 still hashes the actual copied bytes and checks the returned hash; embedding `release_entry_hash` is unnecessary for that check. The owner still receives the signed attestation with its required hashes and `cooling_off_start`. |

Thus “withheld” concerns the reader’s accounting projection, not a claim that the owner never possesses hashes: the prediction-artifact hash is expressly allowed, and the attestation remains a separate, preserved delivery.

Deleting the warning is safe: the promotion guard still requires `cooling_off_start + 259,200 ≤ t_dec ≤ C`; signing/effectiveness retain their own cap checks. The warning supplied no authorization or enforcement.

**D20C4-A-1 — NON-BLOCKING — Item 6’s replacement test assertions.**

**Place:** [C4 lines 73 and 76](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md:73).

**Failure scenarios:**

- “Called before `R_0`” does not necessarily mean refused. All quantities here are integer host-clock seconds. Let `R_0=604800`, `D*=561600`, and a valid finish check occur at `561599`. If that finish holds `L_store` until `604801`, a direct `release` invoked at `604799` waits, then checks the clock at `604801` and may release. C2 checks the clock **under the lock**, not at invocation.
- After a pre-read append, `sign_permit` can correctly refuse because no released PASS/RESULT delivery exists. It therefore cannot necessarily “show” the appended entry as T-S1’s replacement says.

**Minimal repair:** describe T-S2 refusal by the clock check after lock acquisition. For T-S1, say calls wait until durability and then evaluate the durable state according to their own return contracts. No mechanism change.

**D20C4-A-2 — NON-BLOCKING — Supersession list is not completely explicit.**

**Place:** retained [rev 8 “One lock” paragraph](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV8.md:75).

**Failure scenario:** an implementer copying the retained `L_store` inventory still encounters `state`, `guard_state` and `insert_release`, although C2/C3 remove those interfaces.

**Minimal repair:** explicitly replace that inventory with the current operations during consolidation. This is documentation cleanup; the newer capability contracts already control. The remaining no-read `visible_from` at rev 8 line 99 is an internal insert timestamp, withheld by C4’s projection—not an operative reader visibility rule. The closed-cycle refusal is explicitly deleted and its test replaced.

Read-only validation passed: clean worktree/staging; C4 commit changes only its proposal; all 14 frozen sidecars, manifest bindings and Constitution canonical hash verified. Protected inventory matches; `docs/README.md` has only the existing CRLF/LF checkout difference. Checks used Git and `rtk proxy python -I -B -X utf8`; successful verification commands exited 0.

Implementation tests, lint, typing and import checks are N/A for this text-only review. Storage-platform assumptions remain unverified. Nothing was written or committed; this response is not a committed review record.
## Prompt

# Re-check: D-20 option C, revision C4

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. Re-check `review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md` (Claude Opus 5.5, commit 5599056), a delta on `OPTION_C_PROPOSAL_REV3.md`, which is a delta on `OPTION_C_PROPOSAL_REV2.md`, itself a delta on `PROPOSAL_REV8.md`. It answers `SOL_OPTION_C3_REVIEW_415A0DE.md` (D20C3-S-1..2) and `ASTRA_OPTION_C3_REVIEW_415A0DE.md` (D20C3-A-1..4). Review independently of any other C4 review: do not open `SOL_OPTION_C4_REVIEW_5599056.md` or `ASTRA_OPTION_C4_REVIEW_ATTEMPT_1.md`. Context as needed: `PROPOSAL_REV8.md`, `PROPOSAL_REV3.md`, `../d12-proposal/OWNER_DECISION_D12.md`, `../d12-proposal/PROPOSAL_REV7.md`, `docs/RESEARCH_CONSTITUTION.md` (§5, §6, §7, §13, §26), `schemas/attestation.schema.json`, `protocols/protocol_v1.yaml`.

**Direction:** simplify rather than patch; claim only what is true and testable. This is a focused re-check: prefer flagging a residual for honest disclosure over demanding new mechanism, unless a claim is false or a frozen rule is broken. Do not re-open points both C3 reviews accepted unless C4 broke them.

**IDs:** findings `D20C4-A-n`. Use exactly that prefix even if you cannot see your model variant; the caller verifies the model from the CLI header.

**Check:**
1. For EVERY C4 disposition (§1a), say ACCEPT, ACCEPT WITH NOTES or FIX, with evidence.
2. Item 1: the "already final" first step of `sign_permit` and `record_delivery(ATTESTATION)`; can an effective certificate or a VOID still change?
3. Items 2-4: does the reader projection table match exactly the proposed §7 row (b)-(d), including Q2b reason codes, VOID reasons, revision/invalidation entries, the cycle report and pending list? Is withholding the commitment and hashes from the reader consistent with every consumer (P-8, owner delivery, attestation fields)? Is the deleted cap warning safe?
4. Item 5 QC3 wording; item 6 supersessions (complete? anything still naming `state`, `guard_state`, `visible_from` or the closed-cycle refusal?).
5. Overall: with C2+C3+C4 read together, is option C now internally consistent and ready for the owner questions, apart from the owner/S4 decisions it routes?
**Findings:** each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
