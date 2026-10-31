# Codex Sol re-check 5 of D-12 revision 6 (884b75b)

Prompt: `REREVIEW5_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-26): model `gpt-6-sol`, sandbox read-only, reasoning effort high, session id `01a1772d-839a-7361-9da9-fbc4299ad3e2`, 72,178 tokens.

Verdict: **FIX** (1 BLOCKER, 2 NON-BLOCKING). Findings D12R6-S-1 .. S-3.

## Report (verbatim)

**Reviewer:** Codex `gpt-6-sol`, verified from this session’s local metadata. Read-only review at `884b75b`.

**Verdict: FIX.** Rev 6 removes the late-marker and crash-after-staging defects by using one store-timed release row and a certificate signed for that release. My re-check-4 findings **S-1** and **S-4** are resolved subject to the stated C2 wording; **S-2** is removed by construction, and **S-3** is moot. The §7 route is sound: signed C2 can amend Constitution v1.1 through an explicit Constitution-table row. The inherited [C2 §5 row](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:82>) still needs the Q2a choice reconciled before signing. The day-255 arithmetic, including `35 − g − j` days for a cooled-off decision, is correct.

| ID | Class | Finding |
|---|---|---|
| **D12R6-S-1** | **BLOCKER** | The [cap rule](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV6.md:86>) still assigns `U_ops` if an owner decision is unrecorded. A visible FAIL has no PASS attestation and needs no owner promotion decision, so it satisfies that condition even though the next sentence says it remains a FAIL. Restrict decision-pending expiry to an attested PASS awaiting a required decision; preserve completed FAIL and other terminal outcomes without an expiry cause. |
| **D12R6-S-2** | **NON-BLOCKING (wording)** | [P-8](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV6.md:89>) tells the publisher to compare “every field” with step-2 values. Step 2 precedes the read and has no computed test fields; the publisher also cannot read sealed values. Specify the pre-read identities it checks, leaving scientific-value checks with the signer and checks of the fixed PASS fields with the publisher. |
| **D12R6-S-3** | **NON-BLOCKING (wording)** | The [signer residual and timing tests](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV6.md:113>) conflict. An outage after the common reachability check can delay PASS alone, so T-4 cannot require every outcome to move alike for every signer outage. A signature mismatch can also turn a finished PASS into a published technical FAIL under P-8; an incident can identify that fault, contrary to R1’s categorical assurance about FAIL types. Bound that residual plainly in R1 and Q6, and limit T-4 to an outage before the common check. Repeated missed releases can extend the hint beyond one day. |

Q1–Q5 and both parts of Q6 are otherwise answerable without statistical expertise and state their principal costs. R2–R4 are disclosed as trust or fault limits. No implementation tests apply to this document review. **Nothing was written or committed**; under the repository’s rule, this response alone is not a completed, committed R19-2 review record.
