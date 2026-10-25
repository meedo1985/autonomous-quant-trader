# Codex Astra re-check of D-11 revision 2 (845a516)

Prompt: `REREVIEW_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-astra`, sandbox read-only, reasoning effort high, live web search on, session id `01a17362-d38d-7510-a24d-3033492dfef0`, 117,673 tokens. R19-2 re-check 2 of 2.

Verdict: **FIX**. Findings D11R2-A-1 .. A-4.

## Report (verbatim)

**VERDICT: FIX.** Revision 2 resolves the earlier Astra findings at the proposal level. Two new procedural gaps need correction before treating it as decision-ready.

Reviewer: **`gpt-6-astra`, high effort**, verified from this session’s metadata. Reviewed HEAD: `845a516df8bab6082f793c414b43e28e23e02409`. Read-only; no authority to accept or activate governance.

| Earlier finding | Re-check |
|---|---|
| D11R-A-1 | Resolved: §4 supplies the history, initialization and refit contract and recognizes the required access amendment. See the precedent correction below. |
| D11R-A-2 | Resolved: ψ is explicitly selected; the “literal raw-d” claim is withdrawn; predictive coverage is not claimed. |
| D11R-A-3 | Resolved: E-DIFF availability is separated from leg availability; exact windows and all 2,000 valid attempts are required. |
| D11R-A-4 | Resolved: unsupported “small cost” and daily-win claims are removed; the upstream false-promotion distinction is stated. |
| D11R-A-5 | Resolved as a proposal: retention requires an explicit amendment reading and relinquishes freshness claims. Q3’s alternative-cost account still needs correction below. |
| D11R-A-6 | Resolved: KEEP_BLOCKED prevents signing C2 as drafted. |
| D11R-A-7 | Resolved: assumptions and L-2-only probabilities are clearly distinguished from operational calibration. |

**New findings**

1. **D11R2-A-1 — MEDIUM / BLOCKER: sealing needs an unavailable-family branch.**  
   [§7, line 162](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV2.md:162) requires *both nominees’ prediction artifacts* before the first read. But [Annex A P18-3](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_A_SELECTION_RULE.md:105) permits one family to be unavailable and therefore have **no nominee**. A nominated family can also have an unavailable prediction distribution under §2.

   The sealing rule does not specify how the other family proceeds without that second valid artifact. Read literally, it adds a cross-family failure condition.

   **Minimal correction:** before the first read, seal each family’s terminal status: a fixed nominee and valid prediction artifact, or a recorded no-nominee/ineligible/unavailable outcome. Explicitly preserve the other family’s ability to proceed. The anti-adaptation purpose of sealing is sound.

2. **D11R2-A-2 — MEDIUM / BLOCKER for Q3’s cost comparison: the future-window schedule is incomplete.**  
   [§9, line 210](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV2.md:210) presents 180–225 days as fitting within the existing 255-day arrangement. That omits material scheduling conditions in [DRAFT §2.3](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:228):

   - A first read at day 225 places the second read no earlier than day 255, leaving no processing or attestation margin before processing ends.
   - The owner chose a **75-day post-nomination window**. Nomination happens when the plan completes, potentially well before day 180. For example, a day-30 nomination gives a day-105 expiry under that rule; even a 180-day future window cannot fit.
   - “No earlier than about day 200” is an assumed schedule, not a derived minimum.

   **Minimal correction:** state the assumed nomination date, window start, processing allowance and two-read schedule. Explain whether the 75-day window must change even when the 255-day cap remains. Keep the approximate statistical costs, but do not present the shorter option as already fitting existing timing rules.

3. **D11R2-A-3 — LOW / NON-BLOCKING: both-leg flat starts are a new choice, not the cited CPCV convention.**  
   [§4, line 97](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV2.md:97) cites C-14(3) as precedent. That clause restarts the **candidate**, while the [benchmark is sliced from the window’s existing series](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_C_GATE_DEFINITIONS.md:448).

   Restarting both lockbox legs is coherent, but it changes benchmark holdings, entry costs and drawdown initialization. Label it as a new proposed binding and mention it in Q2’s explanation.

4. **D11R2-A-4 — LOW / NON-BLOCKING: make the owner-facing qualifications consistent.**  
   In [Q1–Q2](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV2.md:253):
   
   - Q1 mentions new code only for Route B, although §8 correctly says **all routes need D-20 work**. Give that shared cost before the options.
   - Q2 promises “only PASS/FAIL comes out,” while §4 says “plus whatever D-12 decides.” Specify the recipient and preserve the unresolved disclosure qualification.

   These are clarity corrections; the questions are otherwise understandable by a non-statistician.

**The substantive checks hold.** The ψ formula matches the accepted Task 12 convention applied to `d`, including population standardization and the sample daily-Sharpe coefficient. Its use does not establish predictive coverage: Politis–White’s basic framework targets the sampling distribution of a mean. [Politis–White, §2](https://public.econ.duke.edu/~ap172/Politis_White_2004.pdf). The revised Gaussian and higher-moment qualifications are appropriate. [Lo, Appendix A](https://traders.berkeley.edu/papers/The-Statistics-of-Sharpe-Ratios.pdf).

The access amendment is necessary under both Constitution §7a and the threat model. The proposed inward data flow is coherent, conditional on enforcing the identity boundary and final D-12 outputs. Separate evaluations can leave the segment continuously EXPOSED; no re-locking is needed. However, §7 should say v1.0 **permits** multiple reads, rather than claiming its maximum budget *requires* them.

R1/R2 expose a real ambiguity. R2 is a defensible owner-adopted amendment reading, not proof of original intent. D11-12, D11-13 and D11-14 are substantiated.

Read-only CPython **3.14.7**, `-B`, importing this checkout’s `src`, confirmed:

| Check | Result |
|---|---|
| Prehistory start | **2022-11-13**, providing 4,800 warm-up hours before 2023-06-01 |
| Target and fits | **457 days / 10,968 hours; 16 fits**, last on **2026-08-25** |
| Quantile boundaries | `0.31900000000000006` and `−0.40099999999999997`; stated comparisons correct |
| Decimal-zero example | Exact decimal mean zero; computed E-DIFF **8.384297404680616e−16** |
| Short-window SD illustrations | **1.4240** at 180 days; **1.2737** at 225; **0.8937** at 457 |

The 27 frozen files/sidecars/manifest matched baseline `421737f`; manifest and canonical Constitution checks passed. Six oracle-file raw hashes differed through existing CRLF conversion; committed blobs matched. Working tree remained clean.

**Local gate: BLOCKED by D11R2-A-1 and A-2.** This response remains uncommitted review evidence; the explicit read-only instruction prevents recording it as the completed R19-2 repository record. Claude status: **NOT SENT**.

Implementation tests, lint, typing and import checks were N/A to this document review. No simulation or restricted-data access occurred; predictive coverage and actual outage availability remain unverified.
