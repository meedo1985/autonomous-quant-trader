# Owner decision: D-08, D-09, D-10 (the PBO gate)

**Date:** 2026-10-03
**Authority:** the owner, in a Claude Code session, after two different-model
reviews per R19-2: Fable 5.1 (`FABLE_REVIEW_CD1E552.md`) and Codex
`gpt-5.6-sol` (`SOL_REVIEW_CD1E552.md`); adjudication `ADJUDICATION_CD1E552.md`.
Asked and recorded by Claude Opus 5.5 (`claude-opus-5-5`).

## Decided object

`PROPOSAL.md` revision 2, commit `8a9b807`. Revision 2 applied the review
dispositions without a further check, which is recorded as weaker.

## Exchange (verbatim)

1. **D-08**

   Question: "D-08, ranking for the overfitting check (PBO). The check asks how often the best strategy on half the data does badly on the other half; it must be 30% or less. Should it rank strategies by E-DIFF, the same measure used to pick the nominee? Your D-18 text points this way, but it's a separate decision that needs a one-line rulebook amendment you'd sign. The alternative, ranking by better Sharpe (E-IMPROV), needs data the rules don't store. Nothing is activated."

   Options:
   - "E-DIFF (Recommended)"
   - "Keep blocked"

   Answer: **"E-DIFF (Recommended)"**.

2. **D-09**

   Question: "D-09, data for the overfitting check. Proposal: use daily data. If any strategy has no usable Sharpe on some half of the data, the whole check becomes 'unavailable' (it counts against your 1% no-result limit) instead of that strategy being dropped. The check switches on at 20 declared strategies, and re-runs don't count toward the 20. There's no extra minimum block length. Nothing is activated."

   Options:
   - "Accept (Recommended)"
   - "Keep blocked"

   Answer: **"Accept (Recommended)"**.

3. **D-10**

   Question: "D-10, exact ties in the overfitting check. When two strategies tie exactly on the first half of the data, how should the check score them? Note that adding duplicate strategies changes the score, so the list you declare matters. The check has no error guarantee of its own. No statistician reviewed this. Nothing is activated."

   Options:
   - "Average over tied (Recommended)"
   - "Lowest ID wins"
   - "Keep blocked"

   Answer: **"Average over tied (Recommended)"**.

## Effect

- **D-08 decided:** PBO ranks trials by `E-DIFF`. Line 240 is reworded in the
  §4 amendment, which the owner signs.
- **D-09 decided:**
  - the unit is one complete UTC day, with remainder days assigned to the earliest blocks;
  - `T >= 16` is required, and every trial must have a defined Sharpe on every half, otherwise the result is `UNAVAILABLE`;
  - there is no per-block minimum;
  - enablement is read as the declared count `|J_f|` (re-runs do not count), and the l.61 lifetime-reporting override is to be extended to PBO enablement.
- **D-10 decided:** exact IS ties are scored by the uniform average over the tied trials.
- **Accepted consequences** (rev 2 §5):
  - PBO has no calibrated error rate of its own, but it cannot inflate the DSR bound;
  - the `U_proc` routes it adds must be certified in D-19;
  - duplicates in the declared set move `phi`;
  - no statistician reviewed this.

## Not changed by this decision

Nothing is activated. No frozen file or `HUMAN_DECISION_MATRIX.md` is edited.
G-10 needs §4 amendment text. D-11..D-15, D-19, D-20, N-1 and N-2 remain open.
Promotion stays blocked. No cycle, trial, confirmation or lockbox access,
deployment or trading is authorized.
