# Owner decision: scope of the 1% no-result target (P18-7), "U-1"

**Date:** 2026-10-04
**Authority:** The owner decided this in a Claude Code session. The question was asked and the answer recorded by Claude Opus 5.5 (`claude-opus-5-5`).

**Why it was raised.** Both review families found that the route-S design in D-19 preregistration rev 2 narrowed decided text (Annex A P18-7). They said this needs an explicit owner decision, not a D-19 drafting choice:
- Fable DF2-5: `FABLE_REVIEW_71357D4.md`, `552af72`.
- Sol DS2-2: `SOL_REVIEW_71357D4.md`, `169985e`.

## Exchange (verbatim)

**Question:**

> "You decided earlier (P18-7): "a cycle may end with no result for technical reasons at most 1% of the time, counting every check." About half the checks (ETH check, cost-stress, delay tests, parameter-plateau, random-timing, shuffled-labels) depend on the specific strategy, so their failure rate cannot be measured in advance without simulating your actual strategies thousands of times per cycle (far beyond this computer). How should the rule read? This changes only how 'no result' is counted; it does not change how often a no-edge strategy can wrongly pass (still at most 2.5% per family, 5% per cycle)."

**Options:**

- **"Narrow it (Recommended)"**

  > "The measured 1% limit covers the checks that depend only on returns (the DSR test, confidence interval, drawdown, win-rate, PBO, effective decisions). The strategy-dependent checks are instead screened: before you declare, your actual strategies are run on simulated data and any set that fails a check cannot be declared (no penalty). If such a check still fails on the real data, the cycle ends with no result, recorded, but with no measured rate. Honest, weaker than your original rule."

- **"Keep the full rule"**

  > "Every check stays inside the measured 1%. That needs a per-cycle simulation of your actual strategies at very large scale (likely rented computing, cost unknown until a pilot is measured). If it cannot be done, cycle C2 cannot promote anything."

- **"Keep blocked"**

  > "Decide later. The amendment cannot be signed until this is decided."

**Answer:** **"Narrow it (Recommended)"**

## Effect (clause A-U1, to be added to Annex A after A-B7)

1. **The calibrated target is narrowed.** P18-7's whole-cycle procedure no-result target of at most 0.01 applies to `U_proc^R`. That is the no-result event of the DSR method, including the supported-law classifier, and of gates G-1, G-2, G-4, G-10, G-12 and G-13, whose availability is either simulated or proved deterministically.
2. **The other gates are screened.** G-3, G-5, G-6, G-7, G-8, G-11 and G-14 are excluded from the calibrated target. Instead, a fail-closed screen runs the actual trial set on simulated null data before the declaration is committed. A set that fails the screen cannot be declared, and no `m` is spent.
3. **A failure on the real window is still recorded.** If one of these gates is unavailable on the real window, that is a procedure no-result event. It is recorded with its cause code, but it has no certified rate.
4. **The error target is unchanged.** `P_0(E_f) ≤ 0.025` per family, and so `≤ 0.05` per cycle.

## Not changed by this decision

- D-19's other values, D-11..D-13 and D-20 remain open.
- Nothing is activated.
- No frozen file and no `HUMAN_DECISION_MATRIX.md` is edited.
- No cycle, trial, data access, build, deployment or trading is authorized.
