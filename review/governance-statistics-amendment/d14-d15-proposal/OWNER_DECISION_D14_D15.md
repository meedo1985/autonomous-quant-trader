# Owner decision: D-14, D-15, N-3, N-4 (random-exposure null, delay gates, G-5 stress, held exposure and exits)

**Date:** 2026-10-03
**Authority:** the owner, in a Claude Code session. This followed reviews of
seven revisions by two different model families under R19-2: Fable 5.1 and
Codex `gpt-5.6-sol`. The records are FN1–FN6 and SN1–SN6 in this folder, with
one adjudication per round. Claude Opus 5.5 (`claude-opus-5-5`) asked the
questions and recorded the answers.

N-3 and N-4 are proposed new rows. The owner was told that N-4 affects all
backtests. By answering, the owner adds and decides these rows.
`HUMAN_DECISION_MATRIX.md` itself is not edited.

## Decided object

`PROPOSAL.md` revision 7, commit `411e1af`.
- Revisions 1 and 2 were withdrawn as UNSOUND.
- Revisions 3–6 were checked by both families.
- Revision 7 applied the FN6 and SN6 dispositions **without a further check**,
  which is recorded as weaker.

## Exchange (verbatim)

### First batch: four separate questions

1. **Q2b.**
   - Question: "Q2b (D-14). The random-timing check can only test a
     strategy's entry SIGNAL. It can never test the timing of its stop-loss or
     take-profit rules, because those react to the same prices in every slid
     copy. What should happen to that untested timing? This also decides your
     recorded rule (10%, −0.5% stop, +10% take-profit): under (A) it skips
     this check; under (B) it can't be promoted until a new test is designed.
     Your 5% false-promotion limit comes from the main test (DSR), so it holds
     either way. Nothing is activated."
   - Options: "(A) Accept and disclose (Recommended)" / "(B) Fail-closed" /
     "Keep blocked".
   - Answer: **"(A) Accept and disclose (Recommended)"**.
2. **Q2.**
   - Question: "Q2 (D-14). Pure-sizing strategies have a constant signal and
     no stop rule; they only scale positions by volatility. Slid copies of
     them are identical, so the check can't test them. What should happen?"
   - Options: "Not applicable (Recommended)" / "Always fail".
   - Answer: **"Not applicable (Recommended)"**.
3. **Q20 (N-4).**
   - Question: "Q20 (new row N-4, affects ALL backtests, not just these
     checks). Rulebook trades must move exposure by at least 0.10. A
     position's exposure drifts with price, so a 10% position that has lost
     0.5% sits at about 9.95%, and the rule blocks selling it. Your −0.5% stop
     could then never fire. What should happen?"
   - Options: "Exits to zero always allowed (Recommended)" / "Test against
     last fill" / "Leave drift trap".
   - Answer: **"Exits to zero always allowed (Recommended)"**.
4. **Q10.**
   - Question: "Q10 (D-15). The rulebook allows adding risk only once per 24
     hours, measured from the last increase. Under the one-hour-delay test,
     the increase fills at 01:00, so the next day's 00:00 is only 23 hours
     later and is blocked. What should the 24-hour clock measure from?"
   - Options: "Decision time (Recommended)" / "Fill time (as frozen)".
   - Answer: **"Decision time (Recommended)"**.

### Second batch: one question listing the 18 remaining items

The question text listed every item exactly as follows:

> Random-timing check (D-14):
> - Q1: slide only the declared signal, re-sized with the strategy's own approved volatility estimate; stop/take-profit rules may only keep a position or exit, not resize it.
> - Q1b: re-run stop/take-profit rules on every slid copy.
> - Q3: a signal that reacts to volatility counts as timing.
> - Q4: reword 'match' to 'report average exposure and turnover, don't force them equal'.
> - Q5: the start-up calculations may use the gap days.
> - Q6: never slide by less than 30 days.
> - Q7: slide amounts drawn at random from a recorded seed.
> - Q8: measure Sharpe improvement (E-IMPROV).
> - Q9: pass only if it beats at least 476 of 500 copies.
>
> Delay checks (D-15) and 2x cost (N-3):
> - Q11: 'one hour late' means each input's value as of one clock hour earlier.
> - Q12/Q13: 2x cost applies to the benchmark too; ETH drawdown stays at 1x as frozen.
> - Q14/Q15: under fill delay, the benchmark and ETH are delayed too.
> - Q16/Q17: under input delay, the benchmark is not delayed; ETH strategy inputs are.
> - Q18: a delay check passes if the strategy stays positive (same test as the 2x cost check).
> - Q19: the step-by-step order-and-fill rules (fills before decisions, a planned cut can never fill as a buy).
>
> No statistician reviewed this. Nothing is activated.

- Options: "Accept all (Recommended)" / "Go one by one" / "Keep blocked".
- Answer: **"Accept all (Recommended)"**.

## Effect

Every item takes the recommended option of revision 7.

**D-14 (G-11).**
- **Construction.** Only the declared signal is shifted. The shift is a seeded
  random draw of 500 whole-day shifts, at least `max(g, 30)` days. Each draw
  is re-sized with the trial's own `σ̂`, restricted to l.115/l.121.
- **Overlays.** An overlay is re-run on each draw. It may only keep the target
  or exit to 0.
- **Declaration.** Each trial declares a `g11_class`, which is checked in every
  run.
- **`N/A` cases.** `constant_signal` trials get a preregistered `N/A`,
  whether or not they have an overlay (Q2, Q2b(A)). **Overlay timing is never
  tested by G-11, and this is disclosed.**
- **Credit.** Variance timing inside the signal is credited.
- **Match.** "Match" in l.137 is reworded to report-only.
- **Warm-up.** Warm-up may read the gap days.
- **Statistic and pass rule.** The statistic is `E-IMPROV`. The gate passes if
  at least 476 of 500 draws are strictly below. An all-tie result fails.

**D-15 (G-6, G-7).**
- **Event contract.** Timestamps are instants. Fills come first, and baseline
  orders fill at the same instant. Fills are atomic. Held exposure drifts with
  price. The declared band also applies at 00:00. Direction is classified at
  decision time, and a reduction is clamped so it can never fill as an
  increase.
- **Clock (Q10).** The clock is anchored at **decision time**. This amends
  l.57/l.113, BACKTESTER l.9 and CANONICAL l.11, and in effect the 24 h clause
  becomes inert for daily decisions.
- **Feature delay.** Inputs use a one-clock-hour cutoff. Its effect on coarser
  inputs depends on phase; this is a reading of l.267.
- **Benchmark under stress.** Under execution delay, the benchmark and ETH are
  delayed. Under feature delay, the benchmark is not lagged and ETH candidate
  inputs are lagged.
- **Pass rule.** Survival.

**N-3 (G-5 stress).**
- The BTC and ETH benchmarks run at 2x.
- The ETH candidate point estimate runs at 2x.
- The ETH drawdown stays at 1x. This reads `_at_1x_cost` as applying to the
  drawdown only.

**N-4 (all runs).** Held exposure drifts with price, and **an exit to 0 is
never blocked by the band**. This amends l.60, BACKTESTER l.10 and CANONICAL
l.12.

**Accepted consequences:**
- the overlay timing gap;
- the owner's recorded rule would get `N/A` at G-11 if read with no entry
  signal; whether a fixed 10% size can be registered is a **separate,
  undecided** registration question;
- the 24 h clause becomes inert;
- the delay gates test survival, not limited degradation;
- the gates are filters with no error rate of their own;
- the workload in D-19;
- no statistician reviewed any of this.

## Not changed by this decision

Nothing is activated. No frozen file or matrix is edited. Every item above
needs §4 amendment text, and the D-20 stream mechanics stay open. O-1..O-7,
D-11..D-13, D-19 and D-20 remain open. Promotion stays blocked. No cycle,
trial, confirmation or lockbox access, deployment or trading is authorized.
