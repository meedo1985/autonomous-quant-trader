# D-14, D-15 proposal (revision 2): the random-exposure null and the delay gates

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting
work, done under the owner's instruction "let agent do the answers all the
time". D-rows are decided only by the owner, after two different-model reviews
(R19-2).
**History:** revision 1 (`0f16e97`) was rated UNSOUND by both reviewers:
Fable `FABLE_REVIEW_0F16E97.md` (FN1) and Sol `SOL_REVIEW_0F16E97.md` (SN1).
It was withdrawn, and nothing was put to the owner. This revision is a redesign
that follows the brief in `ADJUDICATION_0F16E97.md`.
**Why now:** G-6, G-7 and G-11 are mandatory pre-lockbox gates. Their
availability counts toward `U_proc` (P18-7).
**Authority:** both rows are `STAT` then `§4` in the matrix. Each one adds
semantics that the frozen text does not contain.

## 1. D-14: the random-exposure null (G-11)

**Frozen text** (l.134–140, 289):
- construction: "match candidate mean exposure and turnover on BTC; evaluate
  paired delta-Sharpe versus VOL_TARGET_BUY_AND_HOLD";
- justification: "Removes beta/time-in-market advantage";
- `samples: 500`;
- `null_minimum_percentile: 0.95`.

### 1.1 Why revision 1 failed, and the design principle

Shifting the candidate's sized exposure moved vol-scaled positions into the
wrong volatility regimes. The benchmark keeps that alignment, so the null
draws were penalised for misalignment and not only for losing timing. As a
result, a vol-targeting candidate with no skill beats its own shifts. FN1
showed this exactly (Sharpe² 1 vs 25/43). **Principle:** a null draw must break
only the timing of the candidate's *departures from the benchmark*. It must
keep the benchmark's volatility alignment.

### 1.2 Proposal: shift the ratio to the benchmark (option A)

Let `a_h` be the candidate's hourly target exposure and `b_h` the benchmark's
hourly target exposure, over the eligible window's `24T` hours. The benchmark
is vol-targeted buy-and-hold at a positive target, so `b_h > 0` whenever its
vol estimate is finite. Define the ratio `r_h = a_h / b_h`.

Null draw `i`, with day shift `k_i`, uses this target path:

```
a'_h = clip( b_h · r_((h + 24·k_i) mod 24T), 0, 1 )
```

That is, the candidate's ratio is shifted and then applied to the benchmark's
own exposure **at each hour**. The path is then run through the frozen
backtester, with all of its rules (band reductions, 24 h risk-increase rule,
costs at 1x, BTC), from the same initial state and over the same window as the
candidate's own run.

- **What it keeps:**
  - the benchmark's volatility alignment;
  - the multiset of hourly ratios, so the candidate's pattern of departures
    from the benchmark is preserved;
  - all serial structure of the ratio, except at one wrap point.
- **What it breaks:** only *when* those departures happen relative to prices.
- **Edge cases:**
  - A candidate identical to the benchmark has `r ≡ 1`. Every draw then
    equals the candidate, all 500 tie, and the gate **fails** under the tie
    rule (§1.5). That is correct for a candidate with no timing.
  - The same holds for any candidate that is a constant multiple of the
    benchmark (the "exposure tilt" of D-01..D-04).
- **Both families.** For a vol-family trial, `r_h` is the ratio of its sized
  exposure to the benchmark's, and this is where its estimator and vol target
  differ from the benchmark. The null therefore asks whether *when* the trial
  deviates from the benchmark adds value, which answers FN1-1's question for
  that family. [AI default]
- **"Match" (SN1-1).** The draws keep the candidate's ratio distribution. They
  do **not** exactly reproduce its realised mean exposure or turnover, because
  clipping, bands and the minimum hold interact with prices. So the frozen word
  "match" would be read as "preserve the candidate's exposure pattern relative
  to the benchmark", with realised mean exposure and turnover reported for every
  draw. **This is an amendment to the wording of l.136, and the owner decides
  it.**

**Alternatives for the owner:**

| Option | Shifted object | Problem |
|---|---|---|
| **A ratio to the benchmark** [recommended] | `r_h` | "match" must be reworded, and realised exposure differs slightly |
| B pre-sizing signal | each hypothesis must declare its mapping as signal × sizing | a vol-family trial with a constant signal gets 500 identical draws and always fails; the hypothesis schema must change |
| C full sized exposure (rev 1) | `a_h` | penalises vol misalignment, so a no-skill candidate passes (FN1-1) |

### 1.3 The shifts (SN1-2, FN1-10, FN1-14)

There are 500 **deterministic, evenly spaced** day shifts, so no random-number
stream is needed and D-20 has no new stream for this gate:

```
k_i = m + floor( i · (T − 2m) / 499 ),   i = 0 … 499
m   = max(g, 30)   [AI default: 30 days so that slow signals are not nearly reproduced]
```

Here `g = gap_embargo.value_days` and `T` is the eligible window length in
days, both known at declaration. The shifts are distinct and avoid both the
identity and near-identity iff `T − 2m >= 499`. Otherwise the gate is
`UNAVAILABLE`. D-19 can rule that out by setting `T_min >= 499 + 2m`; with
`m <= 30` and N-1's `T >= 840` that already holds.

### 1.4 Statistic (fresh choice; SN1-3, FN1-11)

The proposal is `E-IMPROV` of each draw and of the candidate against
`VOL_TARGET_BUY_AND_HOLD`, over the eligible window, at 1x cost. This is a new
choice for row 12: D-02/D-03 do not bind it. The reason is coherence with the
other paired filters (D-02..D-07). The alternative is `E-DIFF`, which matches
the DSR.

### 1.5 Pass rule (SN1-4, FN1-3, FN1-4)

| Rule | Pass iff | Level under ideal exchangeability |
|---|---|---|
| **plus-one rank** [recommended] | at least **476** of 500 null values are strictly below the candidate | 25/501 ≈ 4.99% |
| rank 475 | at least 475 strictly below | 26/501 ≈ 5.19% |
| type-7 | candidate ≥ the type-7 0.95 quantile of the 500 | not nested with the rank rules (FN1) |

Under every rule, ties count as not below. The plus-one rule is the one N-2
already uses (decided), which keeps the two nulls consistent. No error rate is
claimed, because shift-exchangeability is not established (SN1-8).

### 1.6 Availability

If the candidate's or any draw's `E-IMPROV` is not finite, or if `T − 2m <
499`, the gate is `UNAVAILABLE`. Nothing is replaced. If the benchmark's
`b_h = 0` or is not finite at some hour, the ratio is undefined and the gate is
`UNAVAILABLE`.

## 2. D-15: the delay gates (G-6, G-7)

### 2.1 Execution delay (G-7): temporal contract (SN1-5, FN1-7)

- **Baseline:** a decision at close(t) is filled at open(t+1) (backtester
  spec item 2).
- **Stressed:** every fill is executed one additional 1 h bar later, at
  open(t+2), at that bar's price, with the same cost model (`COST_MODEL_v1.md`,
  "Delay stress"). This covers scheduled 00:00 changes and intraday band
  reductions alike.
- **Pending orders:** at most one target is pending. A newer decision
  replaces a pending one, and the latest target wins.
- **Risk-increase clock:** the 24 h rule (l.57) is measured from **decision**
  times, not fill times, so the stress does not by itself block daily
  increases. [AI default]
- **Window end:** a fill that would fall after the window end is not
  executed. Returns use the exposure actually held.

### 2.2 Feature delay (G-6): temporal contract (FN1-6)

- **At decision time t,** every strategy input computed from market data is
  replaced by its value computed one 1 h bar earlier. This covers model
  features at inference, the sizing volatility estimate, and the hourly
  band-evaluation inputs.
- **Unchanged:** model training (same fitted models; only the inference inputs
  lag), labels, decision times, execution timing, and the cost model's
  slippage inputs, which belong to the market at execution, not to the
  strategy. [AI default: inference-only lag, which tests latency robustness
  without retraining.]

### 2.3 Benchmark under stress: one §10 decision for G-5, G-6, G-7 (FN1-5)

Constitution §10 l.111 requires benchmarks to be "evaluated under identical bar
semantics, comparison benchmark, cost model, execution baseline, and applicable
band/min-hold rules".

| Option | Benchmark leg in each stress | Consequence |
|---|---|---|
| **(i) stressed identically** [recommended] | 2x cost (G-5), delayed fills (G-7), and lagged vol inputs (G-6) apply to the benchmark too | follows §10; each gate measures *relative* robustness |
| (ii) unstressed | the benchmark keeps 1x cost and baseline timing | harsher on the candidate; departs from §10's "identical" |

This also fixes the open stress semantics of the already-decided G-5. D-02
decided its estimand, not this. ETH legs are treated the same way as BTC legs.

### 2.4 Pass statistic (SN1-6)

| Option | Each delay gate passes iff, on its stressed run | Consequence |
|---|---|---|
| **survival** [recommended] | BTC `E-IMPROV` > 0, BTC candidate net return > 0, the BTC drawdown constraint holds, and the ETH sanity rule holds (mirrors the frozen 2x-cost rule, l.283) | Frozen precedent. **A large degradation can still pass** if the result stays positive. |
| bounded degradation | survival AND stressed BTC `E-IMPROV` ≥ 0.5 × unstressed | Also limits damage. New rule, with no frozen precedent. |

The BTC drawdown constraint depends on owner item O-7 (G-2) (FN1-12). If any
stressed statistic is not finite, the gate is `UNAVAILABLE`.

## 3. Workload and D-19 (SN1-8, FN1-8)

Per nominee, per evaluation:

| Gate | Runs |
|---|---|
| G-11 | 500 BTC backtests of null paths, plus the candidate's run |
| G-6, G-7 | 2 stresses × 2 assets × 2 legs = 8 backtests under (i) |
| G-5 | 2 assets × 2 legs = 4 backtests under (i) |
| G-14 (decided N-2) | 500 model refits for trials with a target model |

In D-19, each simulated eligible cycle has up to two nominees, so these counts
multiply by 2 × cells × replications. As recorded in
`../n1-n2-proposal/PROPOSAL.md` §3, D-19 must either compute every gate in every
replication or have the §4 amendment authorise a certification route. These
gates are the main cost driver.

## 4. Consequences

- **C-1** These are filters with no calibrated error rate of their own. They
  cannot inflate the DSR bound, and they can lower power and add `U_proc`
  events.
- **C-2** The ratio null tests the timing of departures from the benchmark,
  given the candidate's own pattern of departures. It does not test whether
  that pattern of exposure levels is a good choice (SN1-7).
- **C-3** Dependencies:
  - the l.136 wording ("match") is amended;
  - the §10 benchmark decision also fixes G-5;
  - O-7 governs the drawdown part of D-15;
  - N-2 and D-14 share the plus-one rule.
- **C-4** No statistician reviewed this (R19-2).

## 5. Proposed owner questions (separate; SN1-9, FN1-13)

1. Null object: ratio to the benchmark (rewording "match") [rec] / pre-sizing
   signal / full exposure / keep blocked.
2. D-14 statistic: `E-IMPROV` [rec] / `E-DIFF` / keep blocked.
3. D-14 pass rule: ≥ 476 of 500 [rec] / ≥ 475 / type-7 / keep blocked.
4. Delay contracts §2.1–§2.2: accept [rec] / revise / keep blocked.
5. Benchmark under stress for G-5, G-6, G-7: stressed identically, per §10
   [rec] / unstressed / keep blocked.
6. D-15 statistic: survival [rec] / bounded degradation / keep blocked.

## 6. Next

[AI default] Two different-model reviews, then adjudication, then the owner's
questions.
