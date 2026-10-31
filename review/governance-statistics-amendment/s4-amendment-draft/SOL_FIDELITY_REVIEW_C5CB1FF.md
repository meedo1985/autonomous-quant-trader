# Codex Sol fidelity review of the S4 fold-in (c5cb1ff)

Prompt: reproduced in section "Prompt" below. Reviewer metadata from the Codex CLI header (2026-10-31): model `gpt-6-sol`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a192ab-0a1a-7362-b39b-524212cc0917`, 146,200 tokens. Reviewed `ANNEX_D_LOCKBOX.md` and the `DRAFT_WORDING.md` changes at `c5cb1ff`. This is attempt 2; attempt 1 is `FIDELITY_REVIEW_C5CB1FF_ATTEMPT_1.md`, with no report.

Verdict: **FIX**: 9 BLOCKER (S4F-S-1..9), 2 QUESTION (S4F-S-10..11). No gaps in numbering.

Disposition: none repaired yet. Owner choices are needed on D11-15, the history-read endpoint, the A7 `code` shape and the lineage precedence; the rest is to be repaired in Annex D rev 2 and the draft.

## Report (verbatim)

## Verdict: FIX

The D-11 pass rule, option C release flow, C5 replacements, and the §7 exception are largely faithful. The following omissions and unresolved choices prevent a faithful signing text. This was a read-only review; no files were changed.

- **S4F-S-1 — BLOCKER — DRAFT §4, lines 352–358; Annex D §D-2.4.** The draft makes the 75-day post-nomination window “informative” and treats day 255 as governing. Both owner records explicitly leave **D11-15 open** ([D-11 decision:28](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/OWNER_DECISION_D11.md:28), [D-20 decision:28](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OWNER_DECISION_D20_LOCKBOX.md:28)). A look before day 180 makes its 75-day endpoint earlier than day 255. The adopted detail also anchors the cap to archive time `T` ([D-20 rev. 3:208–209](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md:208)), which Annex D does not state. **Repair:** retain D11-15 as an owner choice, state the provisional earlier-of-two cap and its `T` anchor, then insert the owner’s resolution.

- **S4F-S-2 — BLOCKER — DRAFT R-14a, line 159.** The row refers to proposal items and promises to inline them later, but does not itself carry the adopted verification chain, import limits, module contracts, independent seed verification, and data boundary. Those are conditions of the owner’s R-14a decision ([rev. 2:26–54](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/r14-exception/PROPOSAL_REV2.md:26), [rev. 3:15–30](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/r14-exception/PROPOSAL_REV3.md:15)). **Repair:** inline the complete amended row before fidelity review and signing; keep an explicit blocking marker until then.

- **S4F-S-3 — BLOCKER — Annex D §D-2.10, line 294.** It says D-12 residual R1 “no longer exists.” Option C **changes** R1: signing faults can leave certification pending and cause `U_ops` near the cap, potentially hinting at PASS ([option C2 crosswalk:332](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV2.md:332)). **Repair:** describe the changed residual; only the daily missed-release mechanism was removed.

- **S4F-S-4 — BLOCKER — Annex D §D-3.6.** The adopted key rules are missing: private-key custody, no replacement during C2, treatment of a lost key, and the incident and reconciliation rules for suspected compromise. Option C also replaces the compromise rule’s second test ([D-20 rev. 2:241–245](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV2.md:241), [rev. 3:193–205](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md:193), [option C2:311](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV2.md:311)). **Repair:** carry these rules and their replacement test into §D-3.6.

- **S4F-S-5 — BLOCKER — Annex D §D-3.7, line 422.** The `aqt.lockbox.no_read.v1` shape omits `visible_from`. The adopted record has that field; under option C a barred descendant is visible from **its own insert**, replacing the ancestor-release value ([D-20 rev. 3:307–311](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md:307), [option C2:314](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV2.md:314)). **Repair:** restore the field and its current insert-time rule.

- **S4F-S-6 — BLOCKER — Annex D §D-3.7, lines 501–503.** Replay omits two decided failure paths: a bundle/commitment mismatch returns `MISMATCH` **and logs a §26 incident**; inability to load manifest-bound bars also yields `MISMATCH`. The corresponding tests are absent ([D-20 rev. 3:313–322](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md:313)). **Repair:** include both branches and tests.

- **S4F-S-7 — BLOCKER — Annex D §D-2.2 and §D-3.7.** The upside record lacks `k`’s strict-below counting rule, the `T_L > p95` comparison, and the `NOT_COMPUTED` null/reason values. The bundle restatement also omits the DEFAULT’s value and reason requirements and the sorted, unique reason format ([D-20 rev. 2:261–265](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV2.md:261), [rev. 3:269–274, 303](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md:269)). **Repair:** restore those field rules.

- **S4F-S-8 — BLOCKER — Annex D §D-3.8.** Its test list carries store and option C tests by reference but omits adopted A1a artifact retrieval tests, A1b seed vectors including a legitimate zero, A6 agreement and final-hour tests, and B1 signing, access-control and compromise tests ([D-20 rev. 2:121–123, 198–200, 252–256](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV2.md:121), [rev. 4:79–86](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV4.md:79), [rev. 3:201–205](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md:201)). **Repair:** enumerate the surviving obligations, including the crash-row outcomes, in the signed annex or a hash-bound test contract.

- **S4F-S-9 — BLOCKER — DRAFT THREAT_MODEL row, line 119.** The added permission names the history read but omits permission for `lockbox_eval` to **run the registered strategy itself**, expressly required by D-11 Q2 ([owner decision:11](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/OWNER_DECISION_D11.md:11)). **Repair:** state that execution permission in the threat-model row.

- **S4F-S-10 — QUESTION — Annex D §D-3.1, line 315.** The four-field A7 `code` object is an AI choice. R-14a rev. 3 delegates that choice to S4 text; it does not decide the fields ([rev. 3:28–30](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/r14-exception/PROPOSAL_REV3.md:28)). **Repair:** retain the `[AI default]` label and obtain explicit owner attention to this exact shape before signing.

- **S4F-S-11 — QUESTION — Annex D §D-3.7, line 487.** Placing lineage **after budget** can return `BUDGET_EXHAUSTED` where the adopted P-3 rule calls a failed ancestor’s nominee `BARRED_DESCENDANT` ([D-12 rev. 7:73](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV7.md:73), [option C2:211](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV2.md:211)). **Repair:** specify reason-code precedence for simultaneous budget and lineage conditions; seek owner attention if it changes the recorded reason.

The changed §0 wording and R-14b–R-14d rows appear consistent with their decisions, subject to the R-14a completion above. Annex D’s explicit “D11-15 not decided” at §D-3.9 conflicts with DRAFT §4’s claimed resolution.
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

This is a FIDELITY check, not a redesign. For each row of Annex D and each changed DRAFT row:
1. Does it restate the decided rule correctly (no omission, distortion, strengthening or weakening)? Is every superseded clause (option C replacing P-5/P-7 and rev 8's state/guard_state/insert_release/visible_from; C3/C4/C5 replacements) applied, and none resurrected?
2. Is anything decided missing (e.g. a test obligation, record field, reason code, crash row, residual, condition carried forward)?
3. Every item marked `[AI wording]`, `[AI default]` or `[derived]` (notably: the Constitution §0 l.20 and §7a l.90 rows, THREAT_MODEL l.9, the A7 `code` field in §D-3.1, the lineage step placement in §D-3.7 begin_read, R-14a "to be inlined verbatim", R-14b..R-14d, the D11-15 reading in §4): is it faithful to the decisions, or does it decide something the owner did not? Say which need owner attention.
4. Internal consistency between Annex D and DRAFT (cross-references, marker list, precedence list).

Findings: `S4F-S-n`. Use exactly that prefix; the caller verifies the model from the CLI header. Each: severity (BLOCKER = misstates or omits a decided rule / NON-BLOCKING / QUESTION), place, the source line it conflicts with, minimal repair. Verdict: FAITHFUL, FAITHFUL WITH NOTES, or FIX.
