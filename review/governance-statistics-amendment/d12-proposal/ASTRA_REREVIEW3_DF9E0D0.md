# Codex Astra re-check 3 of D-12 revision 4 (df9e0d0)

Prompt: `REREVIEW3_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-26): model `gpt-6-astra`, sandbox read-only, reasoning effort high, session id `01a176ff-f476-7372-9e6d-3c91b11c2c18`, 86,431 tokens. Reviewed at `25e2553` (rev 4 plus the Sol re-check 3 record; PROPOSAL_REV4.md unchanged since `df9e0d0`).

Verdict: **FIX**. Findings D12R4-A-1 .. A-4 (A prefix used by the reviewer).

## Report (verbatim)

**Verdict: FIX.** The pair transaction and deadline guard are repaired. Late recovery still permits outcome-dependent publication timing, and the slack arithmetic needs correction.

Reviewed HEAD: `25e25530c975b9fe1d0bbdd033498b915f2df08f`. Reviewer: **gpt-6-astra, high effort**, verified from this session’s metadata. Findings use the **Astra namespace**.

| My re-check-2 finding | Disposition |
|---|---|
| **D12R3-A-1 — joint R-b decision** | **Resolved at proposal level.** One pair state, completeness and agreement before signing, one certificate, and atomic publication of both results cover the previous counterexample. |
| **D12R3-A-2 — distinguishable publication paths** | **Partly resolved.** The common transaction and normal-operation barrier repair the original extra-write problem. Late recovery remains distinguishable below. |
| **D12R3-A-3 — incomplete Q2 choices** | **Resolved.** Q2a and Q2b independently decide both disclosures. |
| **D12R3-A-4 — delayed-publication cooling-off cost** | **Resolved in substance.** P-5 preserves 72 hours after visibility; P-6 and Q6 disclose expiry. The numerical slack is wrong below. |

Earlier findings **D12R-A-1, -2, -5, -8** and **D12R2-A-3, -4** remain resolved as proposals. The pair repair completes the accounting/reproduction portions of **D12R-A-4, -6**. Disclosure findings **D12R-A-3 / D12R2-A-2** remain partial through recovery timing. **D12R2-A-1** now has a complete audit mechanism, subject to corrected arithmetic. Owner-question finding **D12R-A-7** is substantially resolved, with the wording qualifications below.

1. **D12R4-A-1 — MEDIUM / BLOCKER: the visibility barrier does not hide staging time after an outage.**  
   [Revision 4, lines 44–52](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV4.md:44), recovery at line 68, tests at line 122.

   The text explicitly permits staging time to differ between outcomes. When the publisher restarts **after `V_s`**, the marker follows completion of staging; the scheduled barrier is already past.

   Counterexample: identical outage and restart time, with an ordinary FAIL already `READY` versus a crashed evaluation still `OPEN`. Suppose their staging transactions take respectively 1 ms and 2 ms—permitted by the proposal. Both publish FAIL, but their markers and `published_at` differ by 1 ms. Therefore publication time depends on more than publisher uptime. Making both paths one transaction does not establish equal duration.

   T-1 and T-3 ensure atomic visibility; T-2 tests publication at `V_s` when the publisher is up. None establishes timing equivalence during recovery.

   **Repair:** specify an outcome-independent recovery publication schedule or equivalent timing protection, including overruns. Extend synthetic timing requirements to identical outage/restart schedules across all outcome classes. Until then, withdraw the unconditional independence claim. This remains relevant to Constitution §7 and protocol l.76.

2. **D12R4-A-2 — MEDIUM / correction required: the reported “exact” bounds and slack silently round down.**  
   [Revision 4, line 19](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV4.md:19), P-6 at line 49.

   From the proposal’s own calendar:

   \[
   g_{\text{visibility}}\le 255-217-\tfrac1{24}
   =37+\tfrac{23}{24},
   \]

   \[
   g_{\text{decision}}\le255-220-\tfrac1{24}
   =34+\tfrac{23}{24}.
   \]

   The no-outage allowance before day 255 is therefore **34 days 23 hours − g**, shared between publication delay and any additional owner-response time. For example, `g = 34.5` permits cooling-off to finish at day **254 + 13/24**, contradicting an unrestricted `g ≤ 34` bound.

   **Repair:** give the fractional bounds. If `g` must be an integer number of days, explicitly bind that restriction and identify 37/34 as integer maxima; even then, `34 − g` is conservative whole-day slack, not exact elapsed-time slack.

3. **D12R4-A-3 — NON-BLOCKING: two owner-facing assurances overstate confidentiality.**  
   [Q2a](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV4.md:89) and [Q6](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV4.md:113).

   Q2a’s “Nothing leaks” conflicts with Q1’s independently selectable FAIL-field disclosure. Say **“This removes the additional cycle-label disclosure.”**

   Q6’s separate publisher prevents direct index writes by the worker, but “cannot leak by mistake” is too strong. Worker-produced results and commitments still reach research through the publisher; recovery timing also remains observable under finding A-1. Say that separation **reduces accidental disclosure risk**, with validation and timing controls still required.

   Otherwise Q1, Q2a, Q2b, Q3–Q6 are understandable without statistical expertise and disclose the principal read-budget, descendant, audit, delayed-verification, permission and expiry costs.

4. **D12R4-A-4 — NON-BLOCKING: the retained D-20 checklist contradicts the new certificate timestamp.**  
   [Revision 4, line 119](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV4.md:119) retains revision 3 §9′ except its permission bullet. However, [revision 3 line 142](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV3.md:142) still requires `cooling_off_start := T_r`, whereas revision 4 requires `V_s`.

   **Repair:** explicitly supersede that checklist item with `V_s` and P-5’s actual-visibility rule.

The remaining substantive changes are sound at proposal level. The store-clock deadline prevents late `READY` acceptance even when publication is delayed. P-5/P-6 are explicitly proposed bindings, not requirements proved by the schema. **I accept the correction to my earlier permission discussion:** §16 review cannot grant publishing rights. The signed §4 amendment must change the threat model; Q6 is an appropriate place because both reproduction routes need publication.

Read-only checks passed: 28 protected files against the recorded baseline, 14 sidecars, Constitution self-hash, seven manifest and seven protocol bindings, and frozen Git content against `f1c17eb`. Exact rational arithmetic and all 16 Boolean gate combinations were checked. Git reported no changes; it warned that the global ignore file was inaccessible.

Implementation tests, lint, types and import checks are N/A to this document review. T-1–T-3 remain proposed tests, not executed implementation evidence. Nothing was written or committed; this response is not yet the required committed review record and authorizes nothing.
