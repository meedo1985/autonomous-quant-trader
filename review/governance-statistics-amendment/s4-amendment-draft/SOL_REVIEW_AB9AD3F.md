# Sol fidelity review of §4 draft rev 5 and Annex C at `ab9ad3f` — SOUND WITH FIXES

Date: 2026-10-04. This is the OpenAI-family review for R19-2. It used prompt `REVIEW_PROMPT_R5.md` (`fc0a44b`) with prefix SA5, and ran in parallel with the Fable review FA5 without sight of it.

It was run with `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high` (Codex v0.157.1). The CLI header shows `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a10566-a794-7031-8192-4f0a6c64e9cb`. The final message is recorded verbatim below. Its local file links are shortened from absolute paths to repo-relative ones; nothing else is changed.

---

Model: **GPT-5, OpenAI GPT family** (exact serving suffix is not exposed)  
Commit checked: **`ab9ad3f0cf2a57d29f6fd798ffeb1a51cceae582`**  
Verdict: **SOUND WITH FIXES**

## Findings

| ID | Severity | Location | Scenario and evidence | Proposed disposition |
|---|---|---|---|---|
| **SA5-1** | **BLOCKER** | [Annex C C-6](</review/governance-statistics-amendment/s4-amendment-draft/ANNEX_C_GATE_DEFINITIONS.md:114>); [Draft §§1a, 2.0](</review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:83>) | Annex C and R-10 say the full Q19 event contract governs baseline, stressed and null runs. The governing addendum explicitly classifies “Q19’s event contract also governs baseline runs” as **recorded, not presented** to the owner ([addendum](</review/governance-statistics-amendment/d14-d15-proposal/OWNER_DECISION_D14_D15_ADDENDUM.md:96>)). N-4’s exit rule does govern all runs, but that does not authorize every Q19 rule for baseline. | Split the universally decided N-4/global amendments from the rest of Q19. Mark baseline application of the full event contract as an owner item and ask it explicitly. |
| **SA5-2** | **BLOCKER** | [Annex C C-10(1)](</review/governance-statistics-amendment/s4-amendment-draft/ANNEX_C_GATE_DEFINITIONS.md:240>); [Draft §7](</review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:380>) | Both say the owner’s fixed 10% cannot be expressed as `s·τ/σ̂`. The governing addendum says the opposite: fixed 10% **can** be written in the required form, while registration and whether `s` may depend on `σ̂` remain open ([addendum](</review/governance-statistics-amendment/d14-d15-proposal/OWNER_DECISION_D14_D15_ADDENDUM.md:37>)). | Remove “cannot express.” State that algebraic representability depends on the still-open `s`/`σ̂` binding, while REG-1 separately decides whether it may be registered. No re-asking of the corrected fact is needed. |
| **SA5-3** | **BLOCKER** | [Draft §2.0 seed procedure](</review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:125>) | The procedure prevents ordinary offline hash grinding only if several unstated assumptions hold. The channel timestamp is not yet required to be immutable/trusted; authorized posters and the canonical C2 message are undefined; a declarer chooses the beacon chain; edits/deletions/mirrors and hostile duplicate posts are unspecified; “published” does not require cryptographic verification or resolve forks/conflicting values; and invalidation does not expressly consume the declaration/window so that a fresh-beacon retry is impossible. | As part of O-6a, bind an authenticated append-only channel/account, immutable timestamp and canonical message. Fix the exact trusted chain in the protocol, or define a closed allowlist that excludes declarer-controlled chains. Define signature verification, conflicting-output/failure rules, no fallback, and explicitly burn C2/the eligible window after the first valid post. |
| **SA5-4** | **BLOCKER** | [Draft §1a protocol l.113](</review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:89>); [Draft §2 shape rule](</review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:103>) | Frozen protocol l.113 is the scalar `minimum_holding_hours_for_risk_increase: 24`. Section 1a says a justification key is added, while §2 promises every leaf shape is preserved except two named DSR exceptions. Both cannot be true. | Prefer preserving l.113 as scalar and put the anchor meaning in the existing l.57 rule/justification and Annex C. Otherwise list l.113 explicitly as a third leaf-shape exception and show its exact new object. |
| **SA5-5** | **NON-BLOCKING** | [Annex C C-1](</review/governance-statistics-amendment/s4-amendment-draft/ANNEX_C_GATE_DEFINITIONS.md:67>) | The chosen D-03 proposal records G-1 as unavailable not only when either leg lacks Sharpe, but also when block selection fails with fewer than 16 observations or any of the 2,000 replicates is invalid. C-1 states only the first route. The future D-20 code binding plus the general technical-invalid rule probably preserves the result, but the restatement is incomplete. | Add those two explicit unavailability cases. This is a fidelity correction, not a new owner decision. |
| **SA5-6** | **NON-BLOCKING** | [Annex C C-0 numerics](</review/governance-statistics-amendment/s4-amendment-draft/ANNEX_C_GATE_DEFINITIONS.md:64>) | Exact float64 comparison was accepted for specific gates in D-05, D-07, D-10 and D-18. C-0 silently extends it to every comparison, including gates whose owner record did not choose that numerical convention. This is defensible, but it is an unmarked drafting default. | Mark the global extension `[AI default]`, or scope it only to gates whose decided text states it and bind the rest through D-20. |
| **SA5-7** | **NON-BLOCKING** | [Draft §0](</review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:32>); [R-10](</review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:123>) | Section 0 says “two annexes” but lists three. It and R-10 say Annex C defines G-1 through G-14, while G-9 is defined by Annex A and G-13 inline; Annex C has no G-9 or G-13 section. The gate table itself is operationally clear. | Say “three annexes” and describe Annex C as defining G-1–G-8, G-10–G-12 and G-14, plus the event contract. |
| **SA5-8** | **NON-BLOCKING** | [Draft marker legend](</review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:23>); [checklist](</review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:334>) | The legend defines owner markers only as `REG-n`, but the draft also uses O-6a; `<<OPEN D-19 route>>` is outside the documented marker forms. “Every row that governs gate availability” is called done even though D-20 and the D-19 route remain open. G-5’s status also omits D-15 Q18, which supplies its survival event. | Expand the legend, qualify “done” as owner-choice rows only, and add D-15 Q18 to G-5’s provenance. Add the owner marker required by SA5-1. |

## Annex C fidelity, C-0 through C-12

| Section | Assessment |
|---|---|
| **C-0** | Common window, legs, Sharpe, estimands, drawdown and outcome definitions are defensible `[derived]` consolidations. The global float64 rule is a defensible but unmarked `[AI default]` (SA5-6). Its baseline-event-contract assumption needs owner input (SA5-1). |
| **C-1** | The D-03 estimand, interval and strict threshold are correct. Two decided unavailability routes are omitted (SA5-5). |
| **C-2** | Exact match to O-7: nonnegative MDD fractions, absolute 0.05 difference, equality passes. |
| **C-3** | Exact match to D-02 and the N-3 addendum: ETH `E-IMPROV > 0` plus drawdown, entirely at 1x. |
| **C-4** | Exact match to D-06/D-07, including anchored calendar blocks, final partial-block handling, integrity failures, cash/zero-variance as a non-win, ties and 0.60 threshold. |
| **C-5** | Exact match to D-02 and the governing N-3 addendum: both BTC legs at 2x; ETH remains entirely at 1x. |
| **C-6** | The mechanics match Q10(b), N-4 and the Q19 construction. Applying all of Q19 to baseline runs was not owner-presented and needs an explicit decision (SA5-1). |
| **C-7** | Exact match to D-15 plus the addendum: BTC-only stresses, one-clock-hour cutoff, ETH baseline, and survival rather than bounded degradation. |
| **C-8** | Exact match to D-04/D-05, including ordered evaluation, present-neighbour rule, nonpositive failure and boundary test. |
| **C-9** | Exact match to D-08/D-09/D-10: daily `E-DIFF`, 16 blocks, all splits, midrank score, uniform IS-tie averaging and declared-count enablement. |
| **C-10** | Construction, class rules, shifts, statistic, availability and 476/500 event match D-14. The fixed-10% representation sentence contradicts the governing addendum (SA5-2). |
| **C-11** | Exact match to N-1, including the Task 12 formula, constant-series fallback, caller checks, reporting and CPCV input. |
| **C-12** | Exact match to N-2(a). Carrying the C1 model classes into C2 is a defensible and correctly marked `[AI default]`. |

## Revision 5 and coherence conclusions

- O-1 through O-7 are otherwise carried over correctly in §§1, 2.0 and 2.3. O-6’s chosen principle is correct; only its AI-drafted mechanics remain insufficiently closed.
- The §1a line inventory includes every line explicitly identified by the D-14/D-15/N-4 decisions, plus the D-14 and D-08 wording changes. Its frozen quotations are accurate. The l.113 shape statement is the sole material table defect.
- The §3 gate mappings agree with Annex C’s operative results. The discrepancies are coverage/provenance wording, not differing pass thresholds.
- D-18 and B-1/B-2/B-5/B-7 remain coherent with the draft: current-cycle score, reported lifetime counts, C2 allowance `m=1`, `T_min`, no fallback and `U_proc` remain intact.
- G-13 correctly changes to the v1.1 canonical-benchmark hash because the canonical specification’s bytes and semantics change. That is a defensible `[derived]` consequence.
- R-7 correctly makes Annex B’s “fixed at declaration/cannot be gamed” sentence informative for C2 and delays family-seed fixation until after commitment. D-20 correctly remains open for encoding and stream bindings.
- Working and staged diffs were empty. No tests were applicable to this documentary fidelity review. Full frozen-file/hash verification was not performed because the authorized scope limited frozen inspection to cited lines.

## Five-line owner summary

- Your O-1 through O-7 choices were mostly carried over correctly.
- Do not approve this version yet: baseline use of the full event contract was never presented to you.
- The fixed-10% statement and protocol-l.113 schema contradiction need correction.
- The public-beacon seed idea works only after the channel, chain, authentication, failure and no-retry rules are tightened.
- After those fixes and the smaller marker/provenance cleanups, the draft is sound enough to continue with REG-1, REG-2, O-6a and D-19.
