# Codex Astra re-check 2 of D-12 revision 3 (0b18a41)

Prompt: `REREVIEW2_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-26): model `gpt-6-astra`, sandbox read-only, reasoning effort high, session id `01a176eb-b1ab-79c1-bed3-8a1e5d181231`, 81,842 tokens. (The report says model metadata was not exposed inside the session; the CLI header above is the verified source.) Reviewed at `04c9cf1` (rev 3 plus the Sol re-check 2 record; PROPOSAL_REV3.md unchanged since `0b18a41`).

Verdict: **FIX**. Findings D12R3-A-1 .. A-4. This report uses the A prefix itself and re-checks Astra's own D12R-A-1..8 and D12R2-A-1..4.

## Report (verbatim)

**Verdict: FIX.** Revision 3 repairs most earlier findings, but R-b still lacks a complete joint publication contract, and the publisher’s claimed timing equivalence does not follow from its state machine.

Reviewed commit: `04c9cf1bb531f0ab45efc32dd0c7b1b5e2736b82`. **Astra lineage; IDs use `A`.** Exact runtime model metadata is not exposed here; verify launcher metadata when recording this review.

| My earlier finding | Re-check |
|---|---|
| D12R-A-1 — schema versus issuance | **Resolved.** P-1/P-2 are proposed bindings, not schema guarantees. |
| D12R-A-2 — cycle-label exception | **Resolved as a proposal.** The exception and data-dependent unavailability are explicit; owner acceptance remains required. |
| D12R-A-3 — index disclosure | **Partly resolved.** Readers, commitment, envelope and timestamps are addressed; publisher timing remains below. |
| D12R-A-4 — accounting/publication | **Partly resolved.** Durable pre-access accounting and default failure records are sound; R-b publication remains incomplete. |
| D12R-A-5 — descendants | **Resolved as a proposal.** P-3 explicitly includes technical FAIL and explains its cost. |
| D12R-A-6 — audit budget | **Partly resolved.** Budget and schedule costs are corrected; the paired transaction needs completion. |
| D12R-A-7 — owner choices | **Substantially resolved.** Q2 still leaves one choice unspecified. |
| D12R-A-8 — upside logging | **Resolved.** P-4 supplies the consumer, verified vector and unavailable representation. |
| D12R2-A-1 — R-b timing/publication | **Partly resolved.** Arithmetic and amendment requirements are correct; joint publication remains unresolved. |
| D12R2-A-2 — published timing/envelope | **Partly resolved.** Scheduled timestamps and crash commitments are fixed; timing independence is not established. |
| D12R2-A-3 — unavailable upside | **Resolved.** Nonfinite/unavailable `T_L` produces `NOT_COMPUTED`, not false numerical results. |
| D12R2-A-4 — technical FAIL consequence | **Resolved.** Q3 plainly describes losing a descendant’s read after a crash. |

1. **D12R3-A-1 — HIGH / BLOCKER: R-b needs a joint decision before signing and publication.**  
   [Revision 3, lines 70–98](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV3.md:70)

   The state machine and index entries are **per evaluation**, but R-b requires agreement between two evaluations. Steps 5–7 can make a primary PASS signed and READY while its audit remains OPEN. At `T_r`, applying those steps independently publishes primary PASS and audit FAIL. That contradicts the intended pre-certificate audit and exposes technical disagreement.

   The pair rules say differing scientific bytes cause failure, but do not define the joint completeness barrier, missing-audit case, or how both release entries obtain one final decision.

   **Repair:** require both completed, matching runs before signing or either evaluation becoming publishable as PASS. Bind missing, late, unavailable and disagreeing audits to the pair’s terminal FAIL; define both public entries, the single certificate, and recovery without a partially published PASS. The linked audit ID alone does not supply that transaction.

2. **D12R3-A-2 — MEDIUM / BLOCKER: the publisher’s two FAIL paths do different work.**  
   [Revision 3, lines 79–82](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV3.md:79)

   An ordinary performance FAIL already in READY goes directly to the append. A crashed evaluation still OPEN first needs `OPEN → CLOSED`, then the append. Both subsequently transition to RELEASED. Thus the crashed path has an additional durable operation **before public visibility**, contrary to “both branches do the same work.”

   With otherwise equal storage latency, research polling the index can distinguish the two FAIL publication times. Writing `released_at = T_r` does not conceal when an entry actually appears.

   **Repair:** specify a common publication transaction or release barrier that removes this distinction, including recovery. Carry an observable-timing requirement into D-20; equal field shapes and a separate scheduled job alone do not establish it.

3. **D12R3-A-3 — NON-BLOCKING / owner-question completeness: Q2’s second option leaves disclosure (b) undecided.**  
   [Revision 3, lines 119–122](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV3.md:119)

   “Allow both” answers the cycle-label and pre-read-reason questions. “Count a technical breakdown as a plain FAIL” answers only the cycle-label question. Selecting it does not authorize—or reject—the public pre-read reason code.

   **Repair:** separate the two decisions, or state explicitly whether option two also permits (b). This is a missing policy answer, not a statistical question.

4. **D12R3-A-4 — NON-BLOCKING / operational cost: disclose the consequence of delayed publication for cooling-off.**  
   [Revision 3, lines 55 and 82](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV3.md:55)

   A publisher outage lasting over 72 hours means the certificate first becomes accessible after its scheduled cooling-off has already expired. The proposal explicitly permits this chronology but does not explain its consequence to the owner.

   **Repair:** disclose that cost and bind late-publication handling, including interaction with C2’s processing cap. I am not asserting that frozen wording already requires 72 hours after visibility; that distinction needs an explicit decision.

The substantive checks otherwise hold:

- **Schedule:** strict sequential reads at `180+g, 210+g, 240+g, 270+g` yield final release `277+g`, outside day 255. Concurrent pairs yield final release `217+g`, hence `g ≤ 38`; including cooling-off gives `g ≤ 35`. Both proposed additional C2 bindings are necessary.
- **P-3:** honestly identified as a new binding. Q3 explains the lost opportunity after technical failure.
- **P-4:** sound at proposal level. Exact type-7 positions are `99.95` and `1899.05`; unavailable values remain sealed and introduce no rejection gate.
- **Q1, Q3–Q5:** understandable and substantially honest about costs, subject to the findings above.
- **Authority:** the publisher uses the existing `lockbox_eval` identity, introducing no additional reader. Its precise permission remains an explicit D-20/§16 condition, not an established authorization.

Validation: read-only arithmetic and all 16 Boolean gate combinations checked. Frozen inventory/Git bytes match `f1c17eb`; 14 sidecars, seven manifest bindings, seven protocol bindings and the Constitution self-hash pass. The only working-byte difference is existing CRLF conversion in `docs/README.md`.

Implementation tests, lint, types and import checks are N/A to this document-only review. No restricted data, simulation, writes or commits occurred. This response is not yet a committed R19-2 record and activates nothing.
