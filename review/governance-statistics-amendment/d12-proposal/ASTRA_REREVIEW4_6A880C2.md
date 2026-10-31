# Codex Astra re-check 4 of D-12 revision 5 (6a880c2)

Prompt: `REREVIEW4_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-26): model `gpt-6-astra`, sandbox read-only, reasoning effort high, session id `01a17716-e8b3-7c52-b370-05ac59a6f460`, 100,331 tokens. Reviewed at `572e45b` (rev 5 plus the Sol re-check 4 record; PROPOSAL_REV5.md unchanged since `6a880c2`).

Verdict: **FIX** (2 BLOCKER, 3 NON-BLOCKING). Findings D12R5-A-1 .. A-5.

## Report (verbatim)

**Verdict: FIX.**

Reviewer: **gpt-6-astra, high effort**, verified from session metadata. Reviewed HEAD `572e45b7f72fe9f78698ccdc7b0a844d01b1831b`. Read-only; no authority or activation implied.

| My re-check-3 finding | Disposition |
|---|---|
| **D12R4-A-1 — recovery timing** | **Partly resolved.** Fixed slots hide staging-duration differences when staging finishes within its window. Recovery after entries are already staged remains incomplete below. |
| **D12R4-A-2 — fractional bounds** | **Resolved.** Both bounds and the worked slack examples reproduce exactly. |
| **D12R4-A-3 — confidentiality assurances** | **Resolved.** Q2a and Q6 use the requested narrower language. |
| **D12R4-A-4 — stale checklist** | **Resolved.** §11 explicitly supersedes the old timestamp instructions. |

1. **D12R5-A-1 — BLOCKER: recovery does not reconcile a new slot with an already-staged certificate.**  
   [REV5 publication rules](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV5.md:38), [retained REV4 recovery](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV4.md:67).

   Example: `T_r = 00:00`; slot 0 is `01:00`. The publisher stages a PASS referencing the `01:00` certificate and sets `RELEASED`, then crashes before writing the marker. It restarts at `01:30`; the new scheduling formula selects `03:00`.

   The existing staged entry still references the `01:00` certificate. Retaining it contradicts `cooling_off_start := V_k`; replacing it needs a rule compatible with append-only records and at most one staged entry per evaluation. Retaining the original slot instead cannot make the result retrospectively visible at `01:00`.

   **Minimal repair:** define recovery across this durable boundary. One candidate is immutable staged result data, with the final slot and matching pre-signed certificate selected atomically by the marker. Specify how abandoned slots become void. Test crashes after staging, before marker commitment, and after marker commitment, including recovery beyond day 255.

2. **D12R5-A-2 — BLOCKER: the replacement cap wording can relabel completed failures as operational expiries.**  
   [REV5 P-6](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV5.md:48).

   “Any other nominee expires unpromoted, recorded with cause U_ops” includes a nominee whose performance FAIL was already published. For example, trend has completed with a performance FAIL while volatility remains unfinished at day 255. The literal rule assigns expiry to both, potentially changing the result accounting behind `NO_EDGE_FOUND` versus `NO_RESULT`.

   The [owner’s O-2 record](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/OWNER_DECISION_O1_O7.md:43) limits expiry to nominees not yet processed.

   **Minimal repair:** apply expiry only to processing or promotion decisions still pending at the cap; expressly preserve previously completed terminal outcomes.

3. **D12R5-A-3 — NON-BLOCKING (wording): “at most 912” is not the signing bound.**  
   [REV5 per-slot signing](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV5.md:42).

   At a day-180 look with `g = 0`, the first family has `T_r = 187`, giving **1,632** hourly slots through day 255. The second family has **912**. An earlier look permits more.

   **Repair:** give the per-evaluation count:
   `max(0, floor((255 − V_s)/Δ) + 1)`.
   Describe 912 as the second-family example. This also makes the cost of per-slot pre-signing honest.

4. **D12R5-A-4 — NON-BLOCKING (wording): §11 retains a timing test contradicted by the admitted residual.**  
   [REV5 checklist](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV5.md:135), [REV4 T-2](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV4.md:122).

   T-2 still requires publication at `V_s` whenever the publisher is up. P-7 now explicitly permits an overrun while it remains up, causing a slot shift.

   **Repair:** qualify T-2 by timely startup and completion within the staging window. Likewise, state the fault assumptions under which T-4 requires equal slots. Keep a separate overrun test for incident recording and correct recovery. T-5 and T-6 are sound requirements, but do not establish recovery correctness by themselves.

5. **D12R5-A-5 — NON-BLOCKING (wording): owner-facing disclosure and the consolidated disclosure bound need the remaining qualifications.**  
   [REV5 disclosure bound](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV5.md:52), [Q6](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV5.md:90).

   The disposition table acknowledges a deliberately faulty signer’s signature-nonce channel, but the enumerated disclosure bound omits it. Q6 mentions a slot shift without explaining that its cause can depend on the data.

   **Repair:** distinguish permitted disclosures from residual faults and trusted-component assumptions. Tell the owner plainly that a fault-driven slot shift may reveal something about the hidden result, and that publisher validation does not eliminate the disclosed faulty-signer channel.

   Also change Q3’s “the alternative would show…” to **“exempting technical failures from the descendant bar would show…”**. Its actual offered alternative—prohibiting related picks—does not cause that disclosure.

The remaining design is sound **at proposal level**: one meaning of “attested” removes the earlier ambiguity; `cooling_off_start = V_k` matches Constitution §13 when publication and certificate selection remain consistent; P-8 improves the publication boundary; and publishing permission correctly requires a threat-model amendment rather than merely §16 review. §11 otherwise captures the delta chain.

Q1, Q2a, Q2b, Q4, Q5 and both Q6 choices are understandable without statistical expertise and disclose the main costs. For neutrality, replace Q2a’s “if you value an honest end label” with “if you want the label to distinguish technical breakdowns.”

Per-slot pre-signing adds considerable machinery. Within this design, atomic selection of the matching certificate at publication is a smaller repair than introducing mutable staged certificates or duplicate release entries.

Validation passed: exact fractional arithmetic; 28 baseline protected files; 14 sidecars; Constitution self-hash; seven manifest and seven protocol bindings; protected inventory and bytes against `f1c17eb`. Git remained clean, with an inaccessible-global-ignore warning.

Implementation tests, lint, types and import checks are N/A to this document review. T-1–T-6 remain proposed tests, not executed implementation evidence. Nothing was written or committed; this response is not yet a committed review record.
