# Codex Astra re-check 2 of D-11 revision 3 (6ce228c)

Prompt: `REREVIEW2_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-astra`, sandbox read-only, reasoning effort high, live web search on, session id `01a1736f-7d98-7d30-b15c-122d7ba04bbc`, 67,842 tokens.

Verdict: **FIX**. Findings D11R3-A-1 .. A-3.

## Report (verbatim)

**VERDICT: FIX** — the arithmetic is correct, but Q3 still misstates the available timing choices.

Reviewer: **`gpt-6-astra`, high effort**, verified from this session’s metadata. Reviewed HEAD: `6ce228cc78317a1fb700361ad2d94b4f7fe20b3b`. Read-only; this review accepts or activates nothing.

| My previous finding | Re-check |
|---|---|
| **D11R2-A-1** | **Resolved.** Terminal-status sealing covers unavailable and ineligible families and explicitly lets the other family proceed. |
| **D11R2-A-2** | **Partially resolved.** §9’s calculations and timing assumptions are explicit and correct. Its conclusion and Q3 still overstate when timing changes are necessary; see A-1 below. |
| **D11R2-A-3** | **Resolved as a proposal.** Both-flat is identified as a new binding, and the incorrect CPCV precedent is withdrawn. |
| **D11R2-A-4** | **Resolved.** Q1 states the shared implementation cost; Q2 distinguishes research output from attestation disclosure and preserves D-12. |
| Astra “permits” note | **Resolved.** |

**New findings**

1. **D11R3-A-1 — MEDIUM / BLOCKER: Q3 contradicts §9’s conditional schedule.**  
   [Q3, lines 176–177](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV3.md:176) says approximately seven months fits *only* with nomination at day 180. But §9 explicitly allows the fixed-day-255 reading. Under that reading, nomination at **day 120**, a **215-day** window, reads at **222 and 252**, and completion at **255** satisfy the stated constraints.

   Also, [§9, line 131](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV3.md:131) broadly says an early look under reading (ii) requires changing nomination timing or O-2. A shorter window need not: **L=60, m=95**, reads at **102 and 132**, completion at **135=L+75**, works under its assumptions.

   **Minimal correction:** preserve both interpretations in Q3. Under reading (ii), timing changes are required **if retaining a window longer than `L+35` days**, assuming two families, `s=0`, and `p=7`. Partition and other necessary amendments remain separate. This matters because the current wording overstates the cost of the future-window alternative.

2. **D11R3-A-2 — LOW / NON-BLOCKING: Q2 drops D11-16’s qualification.**  
   [Q2, line 167](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV3.md:167) presents “matching how the confirmation runs started” as established. D11-16 correctly says that compatibility depends on accepting EC-3 for the confirmation baseline.

   **Minimal correction:** tell the owner that the proposal also requires binding the confirmation baseline to the same start convention through D-20/Annex C. Keep that dependency explicit rather than presenting it as already decided.

3. **D11R3-A-3 — LOW / NON-BLOCKING: starting flat does not guarantee entry costs on day one.**  
   [§4 item 6](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV3.md:70) and Q2 say both legs pay entry costs at L0/day one. A candidate whose registered target is zero at L0 remains flat and pays no entry cost then. The event contract charges costs on actual fills.

   **Minimal correction:** say each leg starts flat and pays its entry cost **when its first permitted entry occurs**. Do not imply compulsory entry.

The remaining changed provisions are sound **at proposal level**: §2 correctly labels float64 handling as proposed; §4 supplies an immutable lookup and verification contract; §7 repairs sealing and accounting. **D11-15 is substantiated** by the conflicting timing formulations. **D11-16 is substantiated** by C-10’s draw-specific scope and EC-3’s proposed status. Q1 is decision-ready; Q2 needs the qualifications above; Q3 needs correction.

Read-only CPython **3.14.7**, with `-B`, confirmed:

| Calculation | Result |
|---|---:|
| Two-family maximum under day-255 cap | **215 days** |
| One-family maximum | **245 days** |
| Two families, look-relative expiry | **m ≤ L+35** |
| Cap for a 457-day window, two families | **497 days** |
| Illustrative SD at 215 / 245 / 155 / 457 days | **1.302948 / 1.220572 / 1.534548 / 0.893693** |

Frozen verification passed: **28 protected files** matched baseline `421737f`, **14 sidecars** matched, and canonical Constitution, manifest and protocol bindings passed. An initial inline protocol check had a shell-quoting error; its corrected check passed. Working tree and staged/unstaged diffs remained clean.

**Local gate: BLOCKED by D11R3-A-1.** All findings remain unapplied under the read-only instruction. This response must be committed by the authorized recorder before counting as the repository’s completed R19-2 record; Claude status: **NOT SENT**.

Implementation tests, lint, typing and import checks are N/A to this document review. Registry storage, predictive coverage and restricted-data availability were not verified.
