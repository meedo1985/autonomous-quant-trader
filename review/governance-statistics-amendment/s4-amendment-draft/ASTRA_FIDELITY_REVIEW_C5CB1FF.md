# Codex Astra fidelity review of the S4 fold-in (c5cb1ff)

Prompt: reproduced in section "Prompt" below. Reviewer metadata from the Codex CLI header (2026-10-31): model `gpt-6-astra`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a192b0-d200-75a1-9168-5d3a464787a0`, 187,264 tokens. Reviewed `ANNEX_D_LOCKBOX.md` and the `DRAFT_WORDING.md` changes at `c5cb1ff`. This is attempt 2; attempt 1 is `FIDELITY_REVIEW_C5CB1FF_ATTEMPT_1.md`, with no report.

Verdict: **FIX**: 10 BLOCKER (S4F-A-1..10), 2 QUESTION (S4F-A-11..12), 1 NON-BLOCKING (S4F-A-13). No gaps in numbering. Run after Sol's review, which was not in the repository.

Disposition: none repaired yet. Owner choices are needed on D11-15, the history-read endpoint, the A7 `code` shape and the lineage precedence; the rest is to be repaired in Annex D rev 2 and the draft.

## Report (verbatim)

**Verdict: FIX.** The core statistical and option-C mechanisms are substantially faithful, but the consolidation omits decided requirements and introduces two substantive changes.

Reviewed on `freeze-sheet`; both target files are byte-identical to `c5cb1ff`. Below, **Annex** means `ANNEX_D_LOCKBOX.md`, **DRAFT** means `DRAFT_WORDING.md`, **D20 Rn** means `d20-lockbox-proposal/PROPOSAL_REVn.md`, and **Cn** means its `OPTION_C_PROPOSAL_REVn.md`.

1. **S4F-A-1 — BLOCKER — D11-15 is resolved without authority.**  
   **Place:** DRAFT lines 352–358, 495; Annex lines 166, 116, 523.  
   **Source:** `OWNER_DECISION_D20_LOCKBOX.md` lines 12, 28 expressly leave D11-15 open. D20 R3 lines 208–209 retain `A = T` and provisional `C = min(A + 255 days, look + 75 days)`; C2 line 312 expressly preserves those rows.  
   Calling the 75-day window “informative” changes the rule: a day-120 look gives day 195 under the provisional cap, versus day 255 in this draft. The archive-time anchor is also absent from the consolidated definition.  
   **Minimal repair:** restore the provisional formula and anchor, mark D11-15 unresolved, and obtain an owner decision before replacing it.

2. **S4F-A-2 — BLOCKER — R-14d broadens the flat-start decision.**  
   **Place:** DRAFT line 162, “Both legs of every such run start flat.”  
   **Source:** D20 R2 lines 138–145 bind the **confirmation source** start; R4 lines 216–219 concern runs feeding and comprising the lockbox test. R3 lines 147–148 extend the **end-price rule**, specifically, to every confirmation run.  
   R-14d extends both-leg restarts to every confirmation run. That can override Annex C C-14’s sliced benchmark convention through the new precedence list. D-11 R3 lines 67–71 explicitly distinguish the lockbox convention from CPCV.  
   **Minimal repair:** retain the universal end-price rule, but scope flat starts to the decided source baseline and lockbox runs.

3. **S4F-A-3 — BLOCKER — Signing-key rules are missing.**  
   **Place:** Annex §D-3.6; DRAFT signing-marker inventory.  
   **Source:** D20 R2 lines 240–245; R3 lines 193–200; C2 line 311.  
   Missing requirements include private-key custody/no backup, publisher verification using the protocol’s public key and the same pinned library/version, no mid-cycle replacement, and lost/compromised-key dispositions. C2 replaces only the compromise rule’s second reconciliation test; it does not delete the remaining rules.  
   **Minimal repair:** carry these rules forward with C2’s ATTESTATION-delivery replacement, and list the lockbox public key among signing values.

4. **S4F-A-4 — BLOCKER — The worker’s duplicate computation disappears.**  
   **Place:** Annex §D-1.8 and §D-3 read/finish workflow.  
   **Source:** D-12 `PROPOSAL_REV7.md` line 82: “The worker reads and computes twice”; agreement establishes determinism only. Option C does not replace step 3.  
   **Minimal repair:** restore this obligation and distinguish it from the later R-a replay.

5. **S4F-A-5 — BLOCKER — Record contracts lose decided content.**  
   **Place:** Annex lines 147, 381–408, 433, 438–445, 489.  
   **Sources:** D20 R2 lines 98–103, 261–265, 298, 312–314; R3 lines 154–156, 269–283; R4 line 117; D-12 rev 7 line 81.  
   The consolidation omits, among other things:
   - shared time/float encodings and typed `block.value/raw/clipping`;
   - `k`’s strict-less-than definition, tie handling and exact unavailable-upside record;
   - sealed reason-code enums, PASS’s null `cause_class`, and DEFAULT field/null requirements;
   - the full pre-read-check payload and one-record-per-evaluation restriction;
   - deterministic evaluation-ID format and the 256-bit nonce requirement.

   Merely naming records or fields does not restate these contracts.  
   **Minimal repair:** restore the effective schemas and encoding rules, applying later replacements explicitly.

6. **S4F-A-6 — BLOCKER — A retained internal timestamp is deleted.**  
   **Place:** Annex line 422, rejection-record shape.  
   **Source:** C5 line 44 expressly retains rev 8’s internal `visible_from` insert timestamp; it is withheld from readers, not removed from storage. See D20 R8 line 99.  
   **Minimal repair:** restore `visible_from = t1` internally while retaining the C4 reader projection.

7. **S4F-A-7 — BLOCKER — A superseded vector-check obligation is resurrected.**  
   **Place:** Annex lines 376–377.  
   **Source:** D20 R3 lines 102, 115, 134 replace A5’s “checked every run” bullet with a check once per process startup.  
   Annex requires both every-computation reproduction and startup checking. This strengthens the decided requirement.  
   **Minimal repair:** delete the every-computation requirement; retain startup evidence and the separate pre-read P-4 checks.

8. **S4F-A-8 — BLOCKER — The test inventory is incomplete.**  
   **Place:** Annex §D-3.8.  
   **Sources:** D20 R2 lines 121–123, 198–200, 252–256, 320–325; R3 lines 149, 201–205, 319–322; R4 lines 79–86; C3 line 160.  
   The listed store/crash tests do not carry forward the artifact-kind tests, seed reproduction/re-derivation tests, runner/metric agreement and interval tests, signing vectors/wrong-key tests, role-denial tests, compromise reconciliation cases, or replay-tampering tests. Nor does the replacement T-S1 text explicitly retain its admission-deadline/error cases.  
   **Minimal repair:** consolidate the complete effective test list, including C3’s `sign_permit` replacement; preserve T-S1’s boundary cases alongside C5’s corrected concurrency assertion.

9. **S4F-A-9 — BLOCKER — Pre-freeze conditions are abbreviated away.**  
   **Place:** Annex line 311; DRAFT §8.  
   **Source:** `OWNER_DECISION_D20_LOCKBOX.md` line 25 requires both changes **in the same reviewed change**, a freeze built from the containing commit, and C2 remaining blocked pending formal amendment if freezing happens first.  
   “Merged before step G” does not preserve the complete condition.  
   **Minimal repair:** carry all three conditions into the consolidated prerequisites.

10. **S4F-A-10 — BLOCKER — R-14a’s accepted residual disclosure is missing.**  
    **Place:** Annex §D-3.1; DRAFT R-14a.  
    **Source:** `r14-exception/PROPOSAL_REV2.md` lines 58–69 and `PROPOSAL_REV3.md` line 34.  
    The fold-in references operative items 1–8 but omits the disclosure that the earlier qualification post does not cover these implementations, reuse of qualified primitives does not qualify their composition, later code can reflect public prices, and the later anchor does not prove absence of earlier protected reads.  
    **Minimal repair:** include these accepted limitations. General historical-price disclosure does not cover the implementation/provenance limitations.

11. **S4F-A-11 — QUESTION — The history-access endpoint conflicts within the authority chain.**  
    **Place:** DRAFT lines 88, 119; Annex line 98.  
    **Source:** `OWNER_DECISION_D11.md` line 11 writes `[2022-11-13, 2025-05-31)`, whereas its adopted rev 3 §4, line 57, authorizes `[S_pre, L1)`, including the final confirmation day.  
    The draft follows the detailed execution contract, but silently resolves the owner record’s differing endpoint.  
    **Minimal repair:** obtain owner clarification of the endpoint; do not present the extra day as an uncontested restatement.

12. **S4F-A-12 — QUESTION — Two marked S4 choices remain choices.**  
    **Place:** Annex lines 315 and 487.  
    **Sources:** R-14a rev 3 line 30 expressly leaves A7’s code-hash representation to S4; C2 line 211 specifies lineage refusal but does not fix its priority against every other admission check.  
    The two-hash `code` object is compatible with the decision, but not itself decided. Likewise, step-6 lineage placement chooses observable rejection precedence.  
    **Minimal repair:** retain proposal labels and obtain owner attention to the schema and ordering. Each module contract must also name the producer of every A7 field.

13. **S4F-A-13 — NON-BLOCKING — Several descriptions need synchronization.**  
    **Places and sources:**
    - Annex line 237 equates “visible” with “released”; C4 line 41 and Annex line 268 delay reader visibility until delivery or termination. Use the actual visibility rule.
    - Annex line 294 says R1 no longer exists; C2 line 332 says it **changes** to certification delay and possible expiry. Preserve that distinction.
    - Annex line 29 retains the old metric APIs; D20 R2 lines 363–364 explain their replacement by the validated `screen.daily_returns` adapter.
    - DRAFT R-14a’s “inlined verbatim at signing” should mean the effective amended text is inlined **before final-wording review**.
    - DRAFT’s literal `added_purposes` list and §6 checklist lag behind R-14c and §8. Precedence resolves the purpose addition, but the presentation remains inconsistent.

    **Minimal repair:** synchronize these descriptions without changing policy.

The Constitution §0 wording faithfully captures Q3. The publisher-permission addition is faithful apart from the history-endpoint question. R-14b and R-14c correctly carry the selected bindings. The principal C2–C5 replacements—including final certificate/VOID handling, reader projection, terminated-cycle service, backstop limitations, and revised lock inventory—are preserved. The crash-row references retain the effective replacements.

No files were written. Validation was documentary comparison plus read-only arithmetic; implementation tests, lint, typing and import checks were N/A. This report is uncommitted, as requested.
## Prompt

# Fidelity review: S4 fold-in of D-11, D-12, D-20 lockbox and R-14a (c5cb1ff)

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. Checkout: branch `freeze-sheet`. Review, under `review/governance-statistics-amendment/s4-amendment-draft/`:
- `ANNEX_D_LOCKBOX.md` (new; Claude Opus 5.5; commits 96af47b, 79066c0, b3da3a2, c5cb1ff), a consolidated restatement of decided records;
- the changes to `DRAFT_WORDING.md` in `git diff b3da3a2 c5cb1ff -- review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md`.

Sources of truth (the owner decisions govern; proposals only as each decision adopts them):
- `../d11-proposal/OWNER_DECISION_D11.md` with `PROPOSAL_REV2.md` §2-3 and `PROPOSAL_REV3.md` §2, §4, §7;
- `../d12-proposal/OWNER_DECISION_D12.md` with `PROPOSAL_REV7.md` §3;
- `../d20-lockbox-proposal/OWNER_DECISION_D20_LOCKBOX.md` with `PROPOSAL_REV2.md`..`PROPOSAL_REV8.md` and `OPTION_C_PROPOSAL_REV2.md`..`_REV5.md` (C2 replaces C1; each later revision is a delta naming what it replaces);
- `../r14-exception/OWNER_DECISION_R14A.md` with `PROPOSAL_REV2.md` and `PROPOSAL_REV3.md`;
- frozen: `docs/RESEARCH_CONSTITUTION.md`, `docs/THREAT_MODEL_v1.md`, `protocols/protocol_v1.yaml`, `schemas/attestation.schema.json`.

Review independently of any other review of this fold-in; none is in the repository. This is a FIDELITY check, not a redesign. For each row of Annex D and each changed DRAFT row:
1. Does it restate the decided rule correctly (no omission, distortion, strengthening or weakening)? Is every superseded clause (option C replacing P-5/P-7 and rev 8's state/guard_state/insert_release/visible_from; C3/C4/C5 replacements) applied, and none resurrected?
2. Is anything decided missing (e.g. a test obligation, record field, reason code, crash row, residual, condition carried forward)?
3. Every item marked `[AI wording]`, `[AI default]` or `[derived]` (notably: the Constitution §0 l.20 and §7a l.90 rows, THREAT_MODEL l.9, the A7 `code` field in §D-3.1, the lineage step placement in §D-3.7 begin_read, R-14a "to be inlined verbatim", R-14b..R-14d, the D11-15 reading in §4): is it faithful to the decisions, or does it decide something the owner did not? Say which need owner attention.
4. Internal consistency between Annex D and DRAFT (cross-references, marker list, precedence list).

Findings: `S4F-A-n`. Use exactly that prefix; the caller verifies the model from the CLI header. Each: severity (BLOCKER = misstates or omits a decided rule / NON-BLOCKING / QUESTION), place, the source line it conflicts with, minimal repair. Verdict: FAITHFUL, FAITHFUL WITH NOTES, or FIX.
