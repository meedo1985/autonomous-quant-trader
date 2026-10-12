# Owner decision: D-06, D-07 (reporting blocks and per-block statistic for the fold win rate)

**Date:** 2026-10-03
**Authority:** the owner, in a Claude Code session, after two different-model
reviews per R19-2: Fable 5.1 (`FABLE_REVIEW_ABCC2C9.md`) and Codex
`gpt-5.6-sol` (`SOL_REVIEW_ABCC2C9.md`); adjudication `ADJUDICATION_ABCC2C9.md`.
Asked and recorded by Claude Opus 5.5 (`claude-opus-5-5`).

## Decided object

`PROPOSAL.md` revision 2, commit `63888f9`, P6-1..P7-3, with option (b) of
§3. Revision 2 applied the review dispositions without a further check,
which is recorded as weaker.

## Exchange (verbatim)

Question: "D-06/D-07, the fold win rate check: the strategy must beat the
benchmark's Sharpe in at least 60% of its 3-month blocks. Proposed definition:
blocks start on the first day of the eligible data window and run three
calendar months each; only the last block can be partial, and it is reported
but not counted; cycle 2 has 13 counted blocks, so it needs 8 wins; a tie
counts as not a win; missing or broken data makes the check unavailable. One
choice is needed: what happens to a quarter in which the strategy sat entirely
in cash, so its Sharpe can't be calculated? Note that a strategy with no edge
still passes this check about 29% of the time, so it is a filter, not a
guarantee. No statistician reviewed this. Nothing is activated."

Options:
- "Accept, cash quarter = loss (Recommended)": counts as not a win. It can never make passing easier and protects your 1% no-result limit, but it is harsh on a cautious strategy that sat out a crash quarter (8 of 13 is still reachable with up to 5 such quarters).
- "Accept, cash quarter = unavailable": one cash quarter makes the check unavailable, so that family can't promote this cycle, and each case counts against your 1% no-result limit.
- "Keep blocked": the fold win rate check, and so any promotion, stays blocked.

Answer: **"Accept, cash quarter = loss (Recommended)"**.

## Effect

- **D-06 decided:**
  - Blocks are anchored at the eligible window's first day `s`. Each boundary is `s + 3k` calendar months, computed from `s`, clipped to the end of the target month, at 00:00 UTC.
  - The window is half-open, `[s, e)`. A block is complete iff `B_{k+1} <= e`.
  - The final partial block is reported only (Constitution §7a).
  - A data-integrity failure makes the gate `UNAVAILABLE`, with its cause code assigned under P18-7.
  - No separate block minimum is set: `T_min` governs, and zero complete blocks makes the gate `UNAVAILABLE`.
  - The observation is BTC at 1x cost.
- **D-07 decided:**
  - The per-block statistic is `E-IMPROV`.
  - A block is a win iff `E-IMPROV > 0`; a tie is not a win.
  - **A block whose leg has zero variance (for example, a quarter entirely in cash) counts as not a win.**
  - `PASS` iff wins / complete blocks `>= 0.60`.
- **Accepted consequences** (rev 2 §3–§4):
  - a cautious strategy that sits out a quarter in cash scores that quarter as a loss;
  - with 13 independent, exchangeable blocks, the pass rate under no edge is about 29%, so the check is a filter, not an error-controlled test;
  - data-integrity routes still count toward `U_proc`;
  - no statistician reviewed it.

## Not changed by this decision

Nothing is activated. No frozen file or `HUMAN_DECISION_MATRIX.md` is edited.
The anchoring, month convention, statistic and zero-variance rule become §4
amendment text for gate G-4. D-08..D-15, D-19, D-20, N-1 and N-2 remain open.
Promotion stays blocked. No cycle, trial, confirmation or lockbox access,
deployment or trading is authorized.
