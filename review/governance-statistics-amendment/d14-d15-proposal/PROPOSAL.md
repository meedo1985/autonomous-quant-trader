# D-14, D-15 proposal (revision 1): the random-exposure null and the delay gates

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting
work, under the owner's instruction "let agent do the answers all the time".
D-rows are decided only by the owner, after two different-model reviews
(R19-2).
**Why now:** gates G-11 (random-exposure null), G-6 and G-7 (feature- and
execution-delay hard gates) are blocked by D-14 and D-15 (§4 draft rev 4, §3).
All three are mandatory pre-lockbox gates, and their availability counts
toward `U_proc` (P18-7), so they must be defined before D-19 (FA3-12).
**Authority:** the matrix marks both rows `STAT` then `§4`. Each adds a pass
event that the frozen text lacks.

## 1. What is missing

- **D-14** (protocol l.134–140, 289): the null "match[es] candidate mean
  exposure and turnover on BTC; evaluate paired delta-Sharpe versus
  VOL_TARGET_BUY_AND_HOLD", `samples: 500`, and
  `promotion.null_minimum_percentile: 0.95`. Missing: **how the 500 random
  exposure paths are generated**, and the **pass event**.
- **D-15** (l.267–268, 284–285): `feature_delay_stress_bars: 1`,
  `execution_delay_stress_bars: 1`, and `feature_delay_hard_gate: true`,
  `execution_delay_hard_gate: true`. The cost model defines execution delay:
  "Shift the baseline fill by one additional 1h bar, then apply the same cost
  model" (`specs/COST_MODEL_v1.md`). Missing: **what statistic passes** each
  gate, and what "feature delay" does.

## 2. D-14 proposal

**P14-1 Construction: random circular shifts of the candidate's own
decision path.** Let `x_t` be the candidate's daily target-exposure decision
series over the eligible window (`T` days, one value per 00:00 UTC
decision). Null draw `i` takes a shift `k_i` and uses the decision series
`x_{(t + k_i) mod T}`. That series is then run through the frozen backtester,
with all its rules (band reductions, 24h minimum hold, costs at 1x, BTC), and
compared with `VOL_TARGET_BUY_AND_HOLD`.

- **Why shifts.** A circular shift keeps the multiset of exposure decisions,
  so mean target exposure matches exactly. It also keeps every day-to-day
  change except the one at the wrap point, so target turnover matches
  except for one transition. What it destroys is the alignment between the
  decisions and the prices, which is exactly the timing the null tests.
  It is deterministic and needs no model of how exposures are generated.
- **Shift set.** Shifts are drawn without replacement from
  `{k : g <= k <= T − g}`, where `g = gap_embargo.value_days` (§4 draft §2.1).
  Shifts close to 0 would nearly reproduce the candidate's timing. If fewer
  than 500 shifts are allowed (`T < 500 + 2g − 1`), the gate is
  `UNAVAILABLE`. That cannot happen in C2 (`T` ≈ 1,219).
- **Seeds.** The shifts are drawn from a stream seeded from the trial's frozen
  seed (protocol l.266) with purpose `"random_exposure_null"`. This is a new
  stream purpose under D-20.
- **Reported match.** Because band reductions depend on prices, the realised
  exposure of a shifted run can differ slightly from the candidate's. The mean
  realised exposure and turnover of the draws versus the candidate are
  reported, not gated. [AI default]

**P14-2 Statistic per draw: `E-IMPROV`** versus `VOL_TARGET_BUY_AND_HOLD`,
over the eligible window, at 1x cost. This follows D-02/D-03 (decided);
"paired delta-Sharpe" in l.137 reads as in those gates.

**P14-3 Pass event.** `null_minimum_percentile: 0.95` is read as "the
candidate's percentile within the null distribution is at least 0.95":
`PASS` iff at least 475 of the 500 null values are **strictly below** the
candidate's `E-IMPROV`. Ties count as not below. Reasons:
- this is the literal meaning of a percentile;
- it is an exact integer count, with no interpolation;
- it is slightly stricter than the type-7 quantile rule of
  `METHOD_CANDIDATE.md` §6.2, which interpolates between the 475th and 476th
  ordered values.

**P14-4 Availability.** If the candidate's `E-IMPROV` or any null draw's
`E-IMPROV` is not finite, the gate is `UNAVAILABLE`. The denominator stays
500, and no draw is replaced. A shifted path that is all cash for the whole
window (only if the candidate is) gives a zero-variance leg. That case
already makes the candidate itself unavailable.

## 3. D-15 proposal

**P15-1 What each stress does.**
- *Execution delay:* every baseline fill is shifted one additional 1h bar
  later, with the same cost model (`COST_MODEL_v1.md`, "Delay stress").
- *Feature delay:* every decision at close(t) uses features computed only
  from data up to close(t − 1 bar), one extra 1h bar of feature lag. The
  decision times and the execution are unchanged. [AI default reading of
  `feature_delay_stress_bars: 1`.]

Each stress is one deterministic re-run of the nominee, BTC and ETH, at 1x
cost.

**P15-2 Pass statistic: the same test as the 2x-cost stress.** Each delay
gate passes iff, on its stressed run, at 1x cost:
- BTC `E-IMPROV` point estimate > 0;
- BTC candidate net return > 0;
- the BTC drawdown constraint holds;
- the ETH sanity rule holds.

This mirrors the frozen `survive_2x_cost_rule` (l.283), the only existing
frozen precedent for a robustness stress in the promotion block.
`E-IMPROV` is the D-02 measure.

Alternatives considered:
- a degradation ratio (stressed `E-IMPROV` ≥ half the unstressed value, like
  the plateau rule). It inherits the sign problems of D-05 and has no frozen
  precedent;
- `E-IMPROV > 0` alone. It is weaker than the 2x-cost precedent, with no
  reason to treat delay more leniently than cost.

**P15-3 Availability.** If any statistic of a stressed run is not finite, that
gate is `UNAVAILABLE`, which counts toward `U_proc`.

## 4. Consequences

- **C-1 These are filters, not error-controlled tests.** The D-18 bound covers
  only the DSR event. Under no edge, the null-percentile gate passes with
  probability about 5% for one nominee before selection, but the nominee is
  chosen by `E-DIFF` and the null tests `E-IMPROV`, so no rate is claimed.
  They cannot inflate the DSR bound.
- **C-2 Compute.** D-14 needs 500 backtests per nominee, and D-15 needs 2 per
  nominee. In D-19, every simulated nominee needs them too, because P18-7
  computes every gate. That is about 500 backtests × replications, a
  material cost that the D-19 compute plan must include.
- **C-3 The shift null keeps the candidate's own exposure pattern.** It tests
  timing, not the choice of exposure levels. A candidate whose edge is simply
  holding less BTC than the benchmark, at a good average level, can pass the
  shift null without timing skill. The `E-IMPROV` gates do not catch that
  either. This is a limit of the frozen design ("Removes beta/time-in-market
  advantage", l.138), not of the shift method.
- **C-4 Feature delay is a reading.** If the owner reads
  `feature_delay_stress_bars` differently (for example, lagging only some
  features), P15-1 changes.
- **C-5 No statistician** reviewed this (R19-2).

## 5. Proposed owner questions (after the reviews)

1. "D-14, random-timing check: the strategy's own daily exposure plan is
   slid in time to 500 random start points (keeping its average exposure and
   trading pattern, but breaking its timing). It passes if it beats at least
   475 of the 500 slid copies on Sharpe improvement. If any copy can't be
   calculated, the check is unavailable. Accept / revise / keep blocked?"
2. "D-15, delay checks: re-run the strategy with fills one hour later, and
   separately with its inputs one hour older. Each must still pass the same
   test as the 2x-cost check (better Sharpe than the benchmark, positive
   return, drawdown limit, ETH sanity). Accept / revise / keep blocked?"

Both are filters with no error guarantee of their own. No statistician
reviewed this. Nothing is activated.

## 6. Next

[AI default] Two different-model reviews, adjudication, then the owner's
questions.
