# Codex Sol re-check of R-14a rev 2 (f1be832)

Prompt: reproduced in section "Prompt" below. Reviewer metadata from the Codex CLI header (2026-10-31): model `gpt-6-sol`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a191e2-1521-7042-89e2-7523255454fa`, 77,071 tokens. Reviewed `review/governance-statistics-amendment/r14-exception/PROPOSAL_REV2.md` at `f1be832`.

Verdict: **ACCEPT WITH NOTES**: 0 BLOCKER, 1 NON-BLOCKING (R14A2-S-1). No gaps in numbering.

Disposition: R14A2-S-1 to be applied in a text-only rev 3 erratum; none left unrepaired.

## Report (verbatim)

**Verdict: ACCEPT WITH NOTES.** Rev 2 is ready for the owner’s decision as an **inactive proposal**. It does not authorize evaluation, data access, or a C2 signature. The signed C2 must still contain the complete module contracts and hashes, and the required human review must occur.

| Prior finding | §1a disposition | Re-check evidence |
|---|---|---|
| R14A-S-1 | ACCEPT | Items 4–5 bind pairing, complete windows, transformations, availability, and consumer-boundary tests; §2 acknowledges that implementation errors can change results. |
| R14A-A-1 | ACCEPT | Item 4 permits implementation of signed rules, including A4’s `m ≠ n` bootstrap; item 8 extends R-8; §2 discloses the later freeze. |
| R14A-S-2 | ACCEPT | Items 3 and 6 remove mutual imports and bind each entry point to its identity, read boundary, and output boundary. |
| R14A-A-2 | ACCEPT | Item 5 requires the ordered paired series to be checked at the consumer boundary. For example, `[-3, 1, 2]` has mean zero; silently dropping the first day makes `[1, 2]` positive. The contract forbids that drop. |
| R14A-S-3 | ACCEPT | Item 7 requires the confirmation module to verify the post, round, signature, derived seeds, window, and `g` before any gate. |
| R14A-S-4 | ACCEPT | §2 now discloses public-price influence and later code changes. |
| R14A-A-3 | ACCEPT | §2 treats review and tests as controls, and explicitly leaves implementation errors as a residual. |
| R14A-S-5 | ACCEPT WITH NOTES | Item 2 requires verification before evaluation, but abbreviates the actual commitment chain. |
| R14A-A-4 | ACCEPT WITH NOTES | The later public anchor is a sound content commitment if the full chain below is verified; it does not prove the first protected-data read. |
| R14A-A-5 | ACCEPT | Items 3 and 6 make the exception one of code placement; D-11 and Constitution §§7–7a still control reads and handoff. |

**R14A2-S-1 — NON-BLOCKING.** **Place:** [PROPOSAL_REV2.md](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/r14-exception/PROPOSAL_REV2.md:22), §1a and item 2. **Failure scenario:** The accepted post contains `declaration_sha256`, not a `protocol_hash` field. A verifier that checks only a presented protocol hash and module bytes has not established that those hashes were committed by the post. The two module hashes are covered **only if** `protocol_hash` is verified against the complete signed C2 protocol bytes containing their rows. **Minimal repair:** State the chain explicitly: accepted post → declaration bytes matching `declaration_sha256` → declaration’s `protocol_hash` → complete signed C2 bytes containing both module hash rows → loaded bytes. Say “before any protected-data read,” since verification itself reads public records and code. The post and pre-read logs establish the required ordering for authorized evaluations; they cannot independently prove that no earlier unauthorized read occurred. [DRAFT §2.0](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:154) and [O-6a §3](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/o6a-channel/SPEC.md:37) support this narrower chain.

No files were written. This was a wording and authority review; runtime tests, lint, type, and import checks are N/A. The checkout was clean on `freeze-sheet`.
## Prompt

# Re-check: proposed C2 row R-14a, rev 2

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. The checkout is on branch `freeze-sheet`. Re-check `review/governance-statistics-amendment/r14-exception/PROPOSAL_REV2.md` (Claude Opus 5.5, commit f1be832), a full replacement of `PROPOSAL.md` (23300c4). It answers `SOL_REVIEW_23300C4.md` (R14A-S-1..5) and `ASTRA_REVIEW_23300C4.md` (R14A-A-1..5); read both. Context as before: `review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md` (§2.0, R-7, R-8, R-13, R-14, seed_disclosure) and `ANNEX_B_DSR_METHOD.md` §2.4, `ANNEX_C_GATE_DEFINITIONS.md` (C-0, C-6); `d20-lockbox-proposal/PROPOSAL_REV3.md` (A4, A6, A7), `OWNER_DECISION_D20_LOCKBOX.md`; `d11-proposal/` owner decision; `docs/RESEARCH_CONSTITUTION.md` (§6, §7, §7a, §16, §27); `review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE.md`.

Direction: simplify rather than patch; claim only what is true and testable. Focused re-check: prefer flagging a residual for honest disclosure over demanding new mechanism, unless a claim is false or a frozen rule is broken. Check: 1. every §1a disposition (ACCEPT / ACCEPT WITH NOTES / FIX, with evidence), including the claim in item 2 that the accepted C2 declaration post's `protocol_hash` covers the two module hashes; 2. anything rev 2 broke or still overclaims; 3. is it ready for the owner's decision?

IDs: `R14A2-S-n`. Use exactly that prefix; the caller verifies the model from the CLI header. Each finding: severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario, minimal repair. Verdict: ACCEPT, ACCEPT WITH NOTES, or FIX.
