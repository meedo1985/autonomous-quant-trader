# Codex Astra re-check 5 of D-12 revision 6 (884b75b)

Prompt: `REREVIEW5_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-26): model `gpt-6-astra`, sandbox read-only, reasoning effort high, session id `01a17732-7a13-7500-9afe-344df7fda8fd`, 60,703 tokens. Reviewed at `c3762cc` (rev 6 plus the Sol re-check 5 record; PROPOSAL_REV6.md unchanged since `884b75b`).

Verdict: **FIX** (2 BLOCKER, 2 NON-BLOCKING). Findings D12R6-A-1 .. A-4.

## Report (verbatim)

**Verdict: FIX — 2 BLOCKER, 2 NON-BLOCKING findings.**

Reviewer: **`gpt-6-astra`, high effort**, verified from session metadata. Reviewed HEAD `c3762cc`; revision 6 is unchanged from `884b75b`. Independent advisory review only.

| My re-check-4 finding | Disposition |
|---|---|
| **D12R5-A-1 — crash after staging** | **Superseded.** The atomic row removes the staged-entry/marker inconsistency. Before commitment there is no release; after commitment publisher recovery need not alter it. Store unavailability remains a separate issue below. |
| **D12R5-A-2 — cap relabels completed outcomes** | **Resolved.** P-6 expressly preserves completed FAILs, rejections and descendant bars. |
| **D12R5-A-3 — certificate count** | **Moot.** Enumerated advance certificates are gone. |
| **D12R5-A-4 — contradictory timing tests** | **Partly resolved.** The old checklist is superseded, but T-3/T-4 still overclaim. |
| **D12R5-A-5 — disclosure wording** | **Largely resolved.** Permitted disclosures and residuals are separated; Q2a/Q3 are corrected. The signing residual still needs the qualifications below. |

1. **D12R6-A-1 — BLOCKER: commitment before the deadline does not guarantee actual visibility at that deadline.**

   [P-7/P-5](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV6.md:78) equate `visible_from` with the exact moment the result became visible.

   Counterexample: a PASS row commits at 05:00 for release at 06:00. The store becomes unavailable to every reader from 05:30 until 07:00. The row survives correctly, but first becomes accessible at 07:00 with `cooling_off_start = 06:00`. Approval at 06:00 three days later permits only **71 hours after actual availability**.

   R3 trusts the clock, late-insert refusal and visibility filter; it does not state an availability assumption. T-4 explicitly includes store outages. The atomic design removes the old marker defect, but does not establish the stronger visibility claim under this fault.

   **Minimal correction:** distinguish scheduled visibility from actual publication availability and resolve this case explicitly. If continuous store availability at release is a required assumption, state it and define the consequence when it fails. Retaining “exact moment” and a full post-publication cooling-off requires handling this case; the existing outage rule cannot simply move an already committed, uniquely keyed row.

2. **D12R6-A-2 — BLOCKER: a release-time technical FAIL does not follow the common FAIL path.**

   [P-7](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV6.md:75), [P-8](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV6.md:89), and [the timing argument](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV6.md:100) conflict.

   A finished performance FAIL uses reachability-check → insert. A finished PASS whose certificate fails P-8 uses reachability-check → signing → validation → technical FAIL → insert. Those are different publisher calls, contrary to T-3.

   Consequently, a fault or overrun during signing can delay an outcome that **ultimately publishes FAIL**. For example, the first signing attempt times out; the next day's attempt returns a certificate with a mismatched field, which P-8 converts to FAIL. R1's statement that this channel affects only a PASS and cannot distinguish technical from performance FAIL is too narrow. P-8 also contradicts the unqualified claim that the published result was fixed at `D_w`.

   **Minimal correction:** reconcile release-time validation failures with the fixed-result/common-FAIL contract. Either arrange terminal failure classification consistently with that contract, or explicitly disclose the wider signing-path residual and obtain the owner's acceptance. The currently described, narrower residual does not cover it.

3. **D12R6-A-3 — NON-BLOCKING (wording): T-4 needs preconditions.**

   [T-4](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV6.md:130) says an outage “over `R_j`” moves every outcome to the next day.

   A publisher outage beginning **after commitment** must leave the scheduled release intact under T-5. An outage occurring only during the PASS signing operation need not affect a FAIL already committed. An outage continuing through the next window need not produce release at `R_{j+1}`.

   Qualify the test: no row committed, the relevant common operation prevented before the deadline, and recovery in time for the next window. Test post-commit publisher failure separately. T-3 also needs correction alongside A-2.

4. **D12R6-A-4 — NON-BLOCKING (wording): the signing residual has no one-day upper bound.**

   [R1](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV6.md:114) and [Q6](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV6.md:170) describe a one-day delay and an early hint bounded by one day. Repeated failed attempts can delay release across several days and exhaust promotion time.

   Say **“one day per missed release; repeated failures can extend the delay and cause expiry.”** No additional machinery is requested.

The **§7 answer is correct**. C2 expressly includes Constitution v1.1 changes, so an explicit Constitution-table row can carry the exception through the existing §4 amendment process. Protocol wording alone cannot. D12-30 correctly identifies the inherited §5-label/§7 conflict; either Q2a choice requires corresponding final wording before signing.

The **day-255 arithmetic is correct** for the stated day-180, second-family example: release by the cap requires `g + j ≤ 38`; cooling-off completed by it requires `g + j ≤ 35`. At `g = 34.5`, zero misses leave half a day; one miss loses half a day. The revised cap preserves completed outcomes and makes the proposed owner-decision deadline explicit through Q6(ii), consistently with O-2's hard-stop intent.

The D-11 statistic, PASS-field implication, descendant treatment and carried-forward D-20 conditions are consistent with the cited sources. R2 and R4 are candid residuals; I request no additional machinery to eliminate them.

**Owner questions:** Q1, Q2a, Q2b, Q3 and Q4 are understandable and disclose their principal costs. Q5 appropriately permits deferral; its disclosure alternative still requires identifying the applicable Constitution and threat-model exceptions in final wording. Q6(i) correctly identifies publishing permission as an amendment issue. Q6's timing assurances need the corrections above. Otherwise the questions are sufficiently complete for a proposal-stage owner decision.

Validation: exact arithmetic passed; 28 frozen files matched baseline `f1c17eb`; all 14 sidecars, Constitution self-hash, seven manifest bindings and seven protocol bindings passed. Git remained clean. Implementation tests, lint, types and import checks are N/A to this document review; T-1–T-6 were not executed.

Nothing was written or committed. This response is not yet a committed review record and authorizes no activation.
