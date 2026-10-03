# Owner decision: N-1, N-2 (new rows: effective-decisions gate, shuffled-labels null)

**Date:** 2026-10-03
**Authority:** the owner, in a Claude Code session, after two different-model
reviews per R19-2: Fable 5.1 (`FABLE_REVIEW_F8DA1B0.md`) and Codex
`gpt-5.6-sol` (`SOL_REVIEW_F8DA1B0.md`). Adjudication: `ADJUDICATION_F8DA1B0.md`.
Asked and recorded by Claude Opus 5.5 (`claude-opus-5-5`). In each question
the owner was told that adding the row to the decision list is the owner's
act. By answering, the owner both adds and decides N-1 and N-2.
`HUMAN_DECISION_MATRIX.md` itself is not edited.

## Decided object

`PROPOSAL.md` revision 2, commit `82a6495`. Revision 2 applied the review
dispositions without a further check, which is recorded as weaker.

## Exchange (verbatim)

1. **N-1.**
   Question: "N-1, the 'minimum 120 effective decisions' check: should the
   existing, tested effective-sample-size formula (Newey-West, from Task 12)
   become a real pass/fail check? It is proven mathematically that it can't
   fail in cycle 2. It can fail only on data windows of 839 days or fewer.
   The same formula also decides when the CPCV diagnostic switches on, at
   250, and there it does matter. This lifts the earlier 'never compare with
   120' caution. Adding N-1 to the decision list is also your act. No
   statistician reviewed this. Nothing is activated."
   Options:
   - "Accept (Recommended)"
   - "Keep blocked"
   Answer: **"Accept (Recommended)"**.
2. **N-2.**
   Question: "N-2, the shuffled-labels test: should it be a promotion check?
   Under (a), strategies trained to predict the scaled return must beat at
   least 476 of 500 copies retrained on time-shifted labels. Strategies with
   no such model skip it by a fixed rule set before the cycle starts. It is
   costly: 500 retrains per strategy, and far more in the D-19 calibration. A
   strategy can also avoid it by not using a return model. It has no error
   guarantee of its own. Adding N-2 to the decision list is your act. No
   statistician reviewed this. Nothing is activated."
   Options:
   - "(a) Required for model strategies (Recommended)"
   - "(b) Sanity check only"
   - "(c) Required for all"
   - "Keep blocked"
   Answer: **"(a) Required for model strategies (Recommended)"**.

## Effect

- **N-1 decided.** The Task 12 Newey-West ESS convention is the governed
  definition for l.242–244, including the series, the caller duties, the
  fallback and the reporting set out in rev 2 §1. G-12 passes iff ESS ≥ 120.
  The same definition feeds the CPCV switch at l.216; the CPCV role itself
  stays with D-13. Decision packet R3's "never compare with 120" caution is
  lifted for this governed use.
- **N-2 decided as (a).** G-14 is a mandatory gate for trials that fit a model
  of the vol-scaled target. It is a frozen `N/A`, fixed at preregistration,
  for all other trials. The recipe is rev 2 §2: BTC daily decision rows; purge
  and embargo first, then a circular label shift within each window; a full
  refit at the same parameter point; per-draw and per-window seeds from a new
  stream (a D-20 dependency); a Spearman IC; and `PASS` iff at least 476 of
  500 null ICs are strictly below the nominee's IC.
- **Accepted consequences:**
  - G-12 cannot fail on C2-length windows.
  - G-14 can be avoided by not fitting a target model.
  - G-14 costs 500 refits per nominee.
  - D-19 must either compute every gate or have the amendment authorise a
    certification route (rev 2 §3).
  - No statistician reviewed this.

## Not changed by this decision

Nothing is activated. No frozen file or `HUMAN_DECISION_MATRIX.md` is edited.
G-12 and G-14 still need §4 amendment text, including the frozen `N/A` for
G-14. D-11..D-15, D-19 and D-20 remain open. Promotion stays blocked. No cycle,
trial, confirmation or lockbox access, deployment or trading is authorized.
