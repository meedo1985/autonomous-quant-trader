# Owner decision: D-01, D-02, D-03, D-04 (estimand naming and paired-gate estimand)

**Date:** 2026-10-03
**Authority:** the owner, in a Claude Code session, after two different-model
reviews per R19-2 (Fable 5.1 `FABLE_REVIEW_5E28376.md`, Codex `gpt-5.6-sol`
`SOL_REVIEW_5E28376.md`; adjudication `ADJUDICATION_5E28376.md`). Asked and
recorded by Claude Opus 5.5 (`claude-opus-5-5`).

## Decided object

`PROPOSAL.md` revision 2, commit `352bb0d`. Revision 2 applied every review
disposition without a further check (recorded as weaker).

## Exchange (verbatim questions and answers)

1. Question: "D-01: Should the project record its two 'delta-Sharpe' measures
   under separate names? E-IMPROV is the candidate's Sharpe minus the
   benchmark's Sharpe. E-DIFF is the Sharpe of the day-by-day difference
   between them. This only adds names; it doesn't change any check. Nothing
   is activated." Options: "Yes (Recommended)", "Keep blocked".
   Answer: **"Yes (Recommended)"**.
2. Question: "D-02, D-03, D-04: Which measure should the ETH check, the
   2x-cost check, the BTC confidence-interval check and the stability
   (plateau) check use? My recommendation is E-IMPROV, the same for all
   three. Be aware: (1) the phrase 'delta-Sharpe' would then mean two
   different things in the rulebook; (2) your 5% limit on false promotions
   covers only the E-DIFF test, so these checks are extra filters with no
   guarantee of their own; (3) if the chosen strategy fails one of these
   checks, it can't be swapped for another, which lowers the chance of
   finding a real edge; (4) the D-19 calibration will also have to simulate
   the benchmark. E-DIFF would match how the candidate is chosen and tested,
   but it would let through a strategy that simply holds a larger multiple of
   the benchmark (for example 1.5x its position). Nothing is activated."
   Options: "E-IMPROV for all three (Recommended)", "E-DIFF for all three",
   "Keep blocked".
   Answer: **"E-IMPROV for all three (Recommended)"**.

## Effect

- **D-01 decided:** `E-IMPROV` and `E-DIFF` are registered as two separately
  named estimands, and every reported paired number is labelled. No gate is bound by this.
- **D-02 decided:** `E-IMPROV` for the ETH sanity gate (G-3, protocol l.42–44,
  279), the 2x-cost stress (G-5, l.283), and therefore the lockbox ETH sanity
  check L-4 (l.91), subject to D-11.
- **D-03 decided:** `E-IMPROV` for the BTC paired 90% CI and its strictly
  positive lower bound (G-1, l.274–275).
- **D-04 decided:** `E-IMPROV` for the parameter plateau rule (G-8,
  l.263–265).
- **Accepted consequences** (PROPOSAL rev 2 §3–§4):
  - the token `paired_delta_sharpe` carries two meanings, and the PBO (l.240)
    stays `E-DIFF`;
  - the false-promotion bound covers only the `E-DIFF` DSR claim, and the
    `E-IMPROV` gates are uncalibrated filters;
  - a nominee that fails them is not replaced (power cost);
  - D-19 must model a benchmark-leg law, and G-1 availability counts toward
    the `U_proc` target;
  - no human statistician reviewed this (R19-2).

## Not changed by this decision

Nothing is activated. No frozen file or `HUMAN_DECISION_MATRIX.md` is edited
(the matrix's D-03 citation issue FE1-13 is left for the owner). G-8 stays
blocked by D-05, G-4 by D-06/D-07, and the intervals need D-20 review. D-05,
D-06..D-15, D-19, D-20, N-1 and N-2 remain open. Promotion stays blocked. No
cycle, trial, confirmation or lockbox access, deployment or trading is
authorized.
