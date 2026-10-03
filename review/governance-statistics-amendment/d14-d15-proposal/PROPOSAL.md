# D-14, D-15 proposal (revision 3): the random-exposure null and the delay gates

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting
work, done under the owner's instruction "let agent do the answers all the
time". D-rows are decided only by the owner, after two different-model reviews
(R19-2).

**History:**
- Revision 1 (`0f16e97`) and revision 2 (`c872066`) were each rated UNSOUND
  by both reviewers. Revision 1: Fable FN1 and Sol SN1, adjudication
  `ADJUDICATION_0F16E97.md`. Revision 2: Fable FN2 and Sol SN2, adjudication
  `ADJUDICATION_C872066.md`.
- Nothing has been put to the owner.
- Revision 3 adopts the construction that both revision-2 reviewers
  suggested: shift the declared **pre-sizing signal**, and size each draw with
  the trial's **own** volatility estimate at the real date. It also makes the
  open choices explicit questions for the owner.

**Authority:** both rows are `STAT` then `§4` in the matrix.

## 1. D-14: the random-exposure null (G-11)

**Frozen text** (l.134–140, 289):
- construction: "match candidate mean exposure and turnover on BTC; evaluate
  paired delta-Sharpe versus VOL_TARGET_BUY_AND_HOLD";
- "Removes beta/time-in-market advantage";
- `samples: 500`;
- `null_minimum_percentile: 0.95`.

### 1.1 What failed before

- **Revision 1 shifted the sized exposure.** That moves volatility-scaled
  positions into the wrong volatility regimes (FN1-1).
- **Revision 2 shifted the ratio to the benchmark.** That still breaks a
  trial's *own* estimator alignment whenever its estimator or clipping differs
  from the benchmark's (FN2-1, SN2-1, exact).

In both cases a trial with no skill beats its own shifted copies, so the gate
becomes inert.

### 1.2 Construction: shift the declared signal, keep the trial's own sizing

**Declaration requirement.** Every hypothesis declares its exposure mapping
(Constitution §8 field) in this form:

```
a_h = clip( s_d(h) · τ / σ̂_h , 0, 1 )
```

- `s_d >= 0` is the trial's **daily pre-sizing signal**, decided at 00:00
  UTC for day `d`.
- `τ` is its vol target.
- `σ̂_h` is its **own** declared sizing estimator, evaluated each hour.

A hypothesis whose mapping cannot be written in this form cannot be declared
in C2. [AI default; this changes §8 practice and needs §4 wording.]

**Null draw `i`** with day shift `k_i`:

```
a'_h = clip( s_((d(h) + k_i) mod T) · τ / σ̂_h , 0, 1 )
```

Only the signal's dates move. Each draw is sized by the trial's own estimator
at the real hour, so it keeps the trial's own volatility alignment, whatever
estimator or target the trial uses.

A trend trial identical to the benchmark has `s ≡ 1`, `τ = 0.60` and
EWMA_168h. Its draws then equal the candidate, all 500 tie, and the gate
**fails** under the tie rule (§1.6). That is correct for a trial with no
timing.

**Pure-sizing trials (owner choice, FN2-1).** A trial whose declared signal
is constant (`s ≡ c`), as in many vol-family trials, has 500 draws identical
to itself and **always fails** G-11. Its claim is better risk sizing, not
timing, and Constitution §12 l.119 says vol management is "de-risking, not
alpha".

| Option | Pure-sizing trials at G-11 | Consequence |
|---|---|---|
| **(a) frozen `N/A`** [recommended] | `N/A`, fixed at declaration from the declared constant signal | the timing null tests only trials that make timing claims; a pure-sizing trial must still pass every other gate |
| (b) always fail | as computed | no pure-sizing trial can ever be promoted, so the vol family is effectively closed |
| (c) a different null for sizing | to be designed | more work, and nothing proposed yet |
| keep blocked | — | the amendment cannot be signed |

**"Match" (l.137; SN2-2, FN2-4).** This construction holds the trial's signal
distribution and sizing rule fixed. It does **not** reproduce realised mean
exposure or turnover: shifting moves the signal against different volatility,
and clipping, bands and the minimum hold interact with prices. Proposed
amendment wording for l.137: "shift the declared daily pre-sizing signal by
whole days, re-size with the trial's own estimator at each hour; realised mean
exposure and turnover of every draw are reported, not matched." The
alternative, matching within a tolerance and rejecting draws outside it, is
offered to the owner. It changes the draw population and needs a tolerance
value.

### 1.3 Numerical domain and state (SN2-3)

`UNAVAILABLE`, with a reason code, is returned if:
- any `s_d` is not finite or is negative;
- any `σ̂_h` is not finite or is ≤ 0;
- any pre-clip product is not finite.

Every null run, like the candidate's own run, starts at the window start with
exposure 0, no pending order and an unset risk-increase clock. Its
estimator and feature warm-up uses data before the window, from the sources
permitted by R-9 (§4 draft). [AI default]

The wrap (day `T` followed by day 1 of the shifted signal) is an ordinary day
boundary in the null path. It is reported.

### 1.4 Shifts (FN2-7, SN2-4)

| Option | Shifts | Note |
|---|---|---|
| **seeded random** [recommended] | 500 distinct shifts drawn without replacement from `{m, …, T − m}`, using a stream seeded from the trial seed (l.266), purpose `"random_exposure_null"` | consistent with the frozen names "random_exposure" and "samples" (l.135, 139), the seed policy, and N-2's seeded shifts; a D-20 stream |
| deterministic, evenly spaced | `k_i = m + floor(i·(T − 2m)/499)` | needs no stream; departs from those names |

In both cases `m = max(g, 30)`. The 30 days is an AI default with no
persistence basis: slow signals have near-identical shifts close to `m`, which
costs power. The draws are available iff `T − 2m >= 499`. N-1 does not fix `T`;
D-19 must set `T_min >= 499 + 2m` (that is, ≥ 559 when `g <= 30`) (FN2-8).

### 1.5 Statistic (FN2-6)

| Option | Ranks by | Note |
|---|---|---|
| **`E-IMPROV`** [recommended] | candidate minus benchmark Sharpe | All draws share one benchmark leg, so this **ranks exactly by the trial's own Sharpe** (Lemma L-1). The test is "does my Sharpe beat shifted copies of me?" |
| `E-DIFF` | Sharpe of candidate minus benchmark | ranks the departure P&L, and is aligned with the DSR |

### 1.6 Pass rule

| Rule | Pass iff |
|---|---|
| **plus-one** [recommended] | at least 476 of 500 strictly below; matches N-2 (decided) |
| rank 475 | at least 475 strictly below |
| type-7 | candidate ≥ type-7 0.95 quantile; this was the matrix's PROPOSED option (a), l.56 |

Ties count as not below. Under genuine exchangeability, the plus-one rule's
level is 25/501. This shift design is **not** shown to be exchangeable, so no
rate is claimed (SN2-4).

## 2. D-15: the delay gates (G-6, G-7)

### 2.1 Event contract, which applies to baseline and stressed runs alike (FN2-2, SN2-5)

At every hourly timestamp the engine runs these steps in order:
1. Execute every fill that is due, at that bar's open price, with the
   frozen cost model.
2. Update the held exposure. The risk-increase clock is set **only when a
   risk increase is actually filled**; this is the frozen "last risk
   increase" (l.57). A cancelled order never sets the clock.
3. Evaluate the decision rule against the **held** exposure:
   - at 00:00 UTC, an increase is allowed if 24 h have passed since the
     last filled increase;
   - at any hour, a reduction is allowed if the target is at least 0.10
     below the held exposure (l.57, 60).
4. Only a decision that passes step 3 creates an order. An order replaces a
   pending one only if it was created in step 3 at this timestamp.
5. The order is due after the delay. In the baseline that is the next open;
   under execution stress it is one 1 h bar later.

At the window start there is no pending order. At the window end, unfilled
orders are dropped. Because fills come first (step 1), an hourly evaluation can
never cancel a due daily increase.

### 2.2 Feature delay (SN2-6, FN2-12)

At decision timestamp `t`, every strategy input that depends on market data
takes **the value the baseline engine had at `t − 1h`**: the last value
emitted at or before `t − 1h`. This covers:
- model features at inference;
- the sizing estimator `σ̂`;
- the hourly band inputs.

A feature built on daily aggregates keeps its last emitted value, which can be
up to 25 h old.

The following are unchanged:
- model refit times and training data;
- labels;
- decision times;
- execution timing;
- held exposure and the clock, which are non-market state;
- the cost model's slippage inputs, which belong to the market at execution.

Warm-up uses the same pre-window data as §1.3. A lagged input that is missing
or not finite makes the gate `UNAVAILABLE`. [AI default: inference-only lag.]

### 2.3 Benchmark and ETH under each stress (separate questions; SN2-7, FN2-3)

Constitution §10 l.111 requires benchmarks to be evaluated under "identical
bar semantics, comparison benchmark, cost model, execution baseline, and
applicable band/min-hold rules". It is evidence for these questions, but it
does not settle them. Protocol l.42 and l.279 fix ETH sanity at
`drawdown_constraint_holds_at_1x_cost`, and l.283 imports it into G-5.

| Gate | Question | Options |
|---|---|---|
| G-5 (2x cost) | Is the benchmark leg also at 2x? | (i) yes, which compares relative cost robustness and fits §10's "cost model" / (ii) no, which degrades against a fixed baseline. The ETH drawdown part stays at 1x as frozen (l.279); changing that would be an amendment. |
| G-7 (execution delay) | Is the benchmark leg also delayed? | (i) yes, which fits §10's "execution baseline" read as shared semantics / (ii) no, with "execution baseline" read as the fixed baseline |
| G-6 (feature delay) | Is the benchmark's `σ̂` also lagged? | (i) yes, which makes the comparator also latency-stressed / (ii) no, so the comparator is unchanged. §10 does not list features. |
| G-6, G-7 ETH legs | Is ETH stressed, or kept at 1x baseline? | stressed / baseline |

### 2.4 Pass statistic (SN2-9)

| Option | Each delay gate passes iff, on its stressed run |
|---|---|
| **survival** [recommended] | BTC `E-IMPROV` > 0, BTC candidate net return > 0, the BTC drawdown constraint holds, and the ETH sanity rule holds. This mirrors l.283. A large degradation can still pass. |
| bounded degradation | survival AND stressed BTC `E-IMPROV` ≥ θ × unstressed. θ is a separate choice; l.264's 0.5 is a partial precedent. |

The drawdown parts take whatever O-7 decides for G-2. A stressed statistic that
is not finite makes the gate `UNAVAILABLE`.

## 3. Workload (gross runs per nominee, before caching; SN2-8, FN2-10)

| Gate | Gross runs |
|---|---|
| G-11 | 500 null backtests + candidate + benchmark = 502; the marginal count is 500 if the base runs are cached |
| G-7 | 2 assets × 2 legs = 4 under (i), 2 under (ii) |
| G-6 | the same counts, **plus** model re-inference on lagged features in every fold |
| G-5 | 4 under (i), 2 under (ii) |
| G-14 (N-2) | 500 model refits for target-model trials |

D-19 multiplies these by nominees × cells × replications. See the N-1/N-2
decision on how D-19 computes or certifies the gates.

## 4. Consequences

- **C-1** These are filters, with no calibrated error rate of their own. They
  cannot inflate the DSR bound, and they can lower power and add `U_proc`
  events.
- **C-2** G-11 tests the timing of the trial's declared signal, given its own
  sizing. It does not test whether the sizing rule is good.
- **C-3** The declaration form in §1.2 changes how hypotheses are written (§8)
  and needs §4 wording.
- **C-4** No statistician reviewed this (R19-2).

## 5. Owner questions (each with revise or keep-blocked)

1. G-11 construction: shift the declared signal with the trial's own sizing
   [rec] / keep blocked.
2. Pure-sizing trials at G-11: frozen `N/A` [rec] / always fail / a different
   null later.
3. "Match" (l.137): report-only rewording [rec] / match within a tolerance.
4. Shifts: seeded random [rec] / deterministic.
5. G-11 statistic: `E-IMPROV` [rec] / `E-DIFF`.
6. G-11 pass rule: ≥ 476 [rec] / ≥ 475 / type-7.
7. The execution-delay contract (§2.1).
8. The feature-delay contract (§2.2).
9. The benchmark leg under G-5 / G-7 / G-6, and the ETH legs (§2.3), as
   separate answers.
10. Delay statistic: survival [rec] / bounded degradation (with θ).
