# Owner decision: D-05 (plateau rule when the selected value is ≤ 0)

**Date:** 2026-10-03
**Authority:** the owner, in a Claude Code session, after two different-model
reviews per R19-2: Fable 5.1 (`FABLE_REVIEW_E98ADB3.md`) and Codex
`gpt-5.6-sol` (`SOL_REVIEW_E98ADB3.md`); adjudication `ADJUDICATION_E98ADB3.md`.
Asked and recorded by Claude Opus 5.5 (`claude-opus-5-5`).

## Decided object

`PROPOSAL.md` revision 2, commit `2eba91c`, §3: the ordered G-8 wording
(steps 1–4) and its AI defaults (an available neighbour is one present in the
grid; the median is pooled across dimensions, with the mean of the two middle
values for an even count; the reference float64 result decides). Revision 2
applied the review dispositions without a further check, which is recorded
as weaker.

## Exchange (verbatim)

Question: "D-05: The plateau check compares neighbouring settings with the
chosen strategy's own Sharpe-ratio improvement over the benchmark (E-IMPROV).
When that improvement is zero or negative, the rule as written stops making
sense: it lets 'valleys' pass and fails 'plateaus'. What should happen then?
Whatever you choose, a value that can't be calculated (for the strategy or
any neighbouring setting) makes the check 'unavailable', not 'failed'. No
statistician reviewed this. Nothing is activated."

Options:
- "(a) Fail (Recommended)": there's no improvement to protect, so the check fails. This changes the rule's meaning (it needs amendment wording) but adds no 'no result' cases to your 1% limit.
- "(b1) Unavailable": each such case counts against your 1% no-result limit; if it happens often, the limit can't be met.
- "(b2) Not applicable": the check is skipped for such strategies, which means a new exemption from a mandatory check.
- "Keep blocked": the plateau check, and so any promotion, stays blocked. (A new sign-aware rule, or leaving the text as written, are also possible: choose 'Other'.)

Answer: **"(a) Fail (Recommended)"**.

## Effect

- **D-05 is decided as option (a)**, with the ordered wording of PROPOSAL rev 2 §3:
  1. no ordered numeric dimension: `N/A`;
  2. a selected or present-neighbour value that is not finite: `UNAVAILABLE`;
  3. `v <= 0`: `FAIL`;
  4. otherwise the frozen threshold and boundary test.
- **Accepted consequences** (rev 2 §4):
  - it changes the rule's meaning, so the amendment needs wording for it;
  - the strict reading of "available neighbour" can raise `U_proc`;
  - where G-1 passes with `v <= 0`, option (a) newly blocks promotion, with no replacement;
  - the peak-semantics consequence of D-04;
  - no statistician reviewed it.

## Not changed by this decision

Nothing is activated. No frozen file or `HUMAN_DECISION_MATRIX.md` is edited.
G-8 still needs the §4 amendment wording. D-06..D-15, D-19, D-20, N-1 and N-2
remain open. Promotion stays blocked. No cycle, trial, confirmation or lockbox
access, deployment or trading is authorized.
