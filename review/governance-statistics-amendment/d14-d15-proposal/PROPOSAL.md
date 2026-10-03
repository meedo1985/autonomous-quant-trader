# D-14, D-15 proposal (revision 4): the random-exposure null and the delay gates

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting
work, done under the owner's instruction "let agent do the answers all the
time". D-rows are decided only by the owner, after two different-model reviews
(R19-2).

**History:**
- Revisions 1 (`0f16e97`) and 2 (`c872066`) were each rated UNSOUND by both
  reviewers and were withdrawn.
- Revision 3 (`540e773`) adopted the signal-shift construction suggested in
  SN2-1. Fable FN3 and Sol SN3 both rated it SOUND WITH FIXES and both
  verified the core construction exactly.
- Adjudication: `ADJUDICATION_540E773.md`.
- Revision 4 applies every disposition. Nothing has been put to the owner yet.

**Authority:** both rows are `STAT` then `§4`. The G-5 stress question in
§2.3 belongs to a proposed new row, **N-3** (FN3-12).

## 1. D-14: the random-exposure null (G-11)

**Frozen text** (l.134–140, 289):
- construction: "match candidate mean exposure and turnover on BTC; evaluate
  paired delta-Sharpe versus VOL_TARGET_BUY_AND_HOLD";
- "Removes beta/time-in-market advantage";
- `samples: 500`;
- `null_minimum_percentile: 0.95`.

### 1.1 Notation

- **`T`**: the number of complete UTC days in the eligible window. Days are
  indexed `d = 0 … T−1`, and hours are indexed `h = 0 … 24T − 1`.
- **`g`**: `gap_embargo.value_days` (§4 draft §2.1).
- **Scope:** BTC only, at 1x cost, over the eligible window (FN3-6, SN3-2).

### 1.2 Construction: shift the declared signal, keep the trial's own sizing

**Applicability contract** (SN3-1, FN3-3). A trial is **G-11-testable** if its
preregistered exposure mapping (Constitution §8) has this form:

```
a_h = clip( s_h · τ / σ̂_h , 0, 1 )
```

- `s_h >= 0` is a signal computed only from market data and the trial's
  declared model outputs, so never from the trial's own position, P&L or path.
  It may be evaluated hourly (l.55).
- `τ ∈ {0.40, 0.60, 0.80}` is the trial's vol target (l.127).
- `σ̂_h` is its own declared sizing estimator, evaluated at hour `h`.

The interface (signal, units, timing, estimator) is part of the hashed
declaration.

A trial outside this class gets a **preregistered `N/A`** at G-11 (SN3-8),
fixed at declaration. Examples:
- rules with stops, take-profits or hysteresis, which depend on the trial's
  own path;
- the owner's recorded rule (`review/owner-input/TRADING_RULE_2026-09-27.md`),
  which falls outside the class.

The alternative, admitting only testable trials into C2, would restrict
hypothesis eligibility by amendment (owner question Q1b).

**Null draw `i`**, with day shift `k_i`:

```
a'_h = clip( s_((h + 24·k_i) mod 24T) · τ / σ̂_h , 0, 1 )
```

The signal is shifted by whole days, so its time of day is kept. Each draw is
sized by the trial's own estimator at the real hour. Both reviewers verified
with exact examples that this keeps the trial's **σ̂** alignment for any
estimator and vol target (FN3 C1, SN3). It does **not** keep volatility
alignment that sits inside `s` (FN3-4; see §1.3).

**Pure-sizing trials.** A trial whose declared `s` is constant has 500 draws
equal to itself.

| Option (Q2) | Pure-sizing trials at G-11 | Consequence |
|---|---|---|
| **(a) preregistered `N/A`** [recommended] | `N/A`, fixed at declaration | Constitution §12 l.119 says vol management is "de-risking, not alpha". G-11 then tests only timing claims. This needs the S4 gate list's G-11 `na: "never"` changed, and the P18-7 `N/A` exception applied, as for G-14 (FN3-11). |
| (b) always fail | under the rank rules, ties fail (but see §1.6 for type-7) | no pure-sizing trial can be promoted, so the vol family is effectively closed |
| (c) a different null later | — | nothing is designed yet |

### 1.3 Variance timing inside the signal (FN3-4; Q3)

A signal that reacts only to volatility, with no directional information, can
beat its shifted copies (FN3 C2, exact: 6 of 7 below, 1 tie). The same
economic content placed in `σ̂` would be pure sizing, and so `N/A` under Q2(a).

| Option (Q3) | Effect |
|---|---|
| **(a) credit it** [recommended] | no special case: variance timing carried in `s` counts as timing |
| (b) treat as sizing | a trial whose declared signal inputs are all volatility features gets a preregistered `N/A`, like pure sizing |

The recommendation is (a) because the classification in (b) is hard to fix at
declaration and is open to gaming. The consequence is disclosed: G-11 can be
passed through volatility timing alone.

### 1.4 "Match" (l.137; Q4)

The construction keeps the trial's signal distribution and sizing rule. It
does not reproduce realised mean exposure or turnover.
- **(a)** [recommended] Reword l.137: "shift the declared signal by whole
  days and re-size with the trial's own estimator at each hour; realised mean
  exposure and turnover of every draw are reported, not matched."
- **(b)** Match within a tolerance and reject draws outside it. This changes
  the population of draws and needs a tolerance value.

### 1.5 Domain, state and shifts (SN3-2, FN3-6, FN3-10, SN3-4)

**`UNAVAILABLE`, with a reason code, and no replacement**, if any of these
holds:
- any `s_h` is not finite or is < 0;
- any `σ̂_h` is not finite or is ≤ 0;
- any pre-clip product is not finite;
- a day in the window is not a complete UTC day (Task 12 conventions);
- **the candidate's or any draw's statistic is unavailable**, for example
  through zero variance or insufficient observations (`statistics.py:173–200`).
  In that case the denominator stays 500.

**State.** Every run, including the candidate's own, starts at the window start
with exposure 0, no pending order and an unset clock.

**Warm-up.** Estimators and features need data from before the window. The
question is whether that warm-up may read the `g` excluded gap days. Those days
are "reachable only through the engine" under the `excluded_days_status` clause
(§4 draft §2.1), not under R-9 (FN3-10). Warm-up is engine computation, not
evaluation output.
- **(a)** [recommended] yes;
- **(b)** no, in which case estimator state at the window start is `g` days
  stale (Q5).

**Wrap.** Day `T−1` of the shifted signal is followed by day 0. This is an
ordinary day boundary, and it is reported.

**Shift set.** `{m, …, T − m}` with `m = max(g, f)`, where `f` is a floor
(Q6). [rec: `f` = 30 days, an AI default with no basis in persistence. Near
shifts of slow signals cost power.] 500 distinct shifts exist iff
`T − 2m >= 499`. D-19 must set `T_min` so that this holds.

**How the shifts are drawn (Q7):**
- **(a)** [recommended] seeded random: 500 shifts without replacement, from
  a stream seeded from the trial seed (l.266), purpose
  `"random_exposure_null"`. This is consistent with "random_exposure",
  "samples" and N-2. The sampling mechanics are a D-20 matter.
- **(b)** deterministic: `k_i = m + floor(i·(T − 2m)/499)`,
  `i = 0 … 499`.

### 1.6 Statistic (Q8) and pass rule (Q9)

**Statistic (Q8).**
- **`E-IMPROV`** [recommended]. Because every draw shares one benchmark leg,
  this ranks exactly by the trial's own Sharpe (Lemma L-1).
- **`E-DIFF`**. This ranks the departure P&L, in line with the DSR.

**Pass rule (Q9).** Each rule gives a different consequence when all draws tie
(FN3-5, SN3-3):

| Rule | Pass iff | All 500 draws tie the candidate |
|---|---|---|
| **plus-one** [recommended] | ≥ 476 of 500 strictly below. This matches N-2. | fails |
| rank 475 | ≥ 475 strictly below | fails |
| type-7 (the matrix's PROPOSED (a), l.56) | candidate ≥ type-7 0.95 quantile | **passes**. A benchmark clone would pass, so a strict `>` or an explicit tie rejection would be needed. |

Under genuine exchangeability, the plus-one rule's level is 25/501. This design
is not shown to be exchangeable, so no rate is claimed.

## 2. D-15: the delay gates (G-6, G-7)

### 2.1 Event contract, for the baseline and stressed runs alike (FN3-1, FN3-2, FN3-7, FN3-8, SN3-5)

**Time and state.**
- Timestamps are **instants**: close(t) = open(t+1).
- An order stores an **absolute target exposure**.
- Held exposure is position value divided by equity, and it **drifts with
  price** between fills [AI default, FN3-8].
- The risk-increase clock starts **unset**. An unset clock permits the first
  increase.

**At each hourly instant, in order:**
1. Execute every fill that is due at this instant, at the open(t+1) price, at
   the frozen cost.
2. Update the held exposure and the clock (the anchor is Q10).
3. Evaluate the decision against the held exposure:
   - at 00:00 UTC, a change is allowed if `|target − held| >= 0.10`. This is
     l.112 `rebalance_band_absolute`, applied to increases as well
     [AI default, FN3-7];
   - an increase also requires the clock to show **≥ 24 h**;
   - at any hour, a reduction is allowed if the target is at least 0.10
     below held (l.60).
4. A decision that passes step 3 creates an order.
5. **Baseline:** the order fills **at this same instant**, at the open(t+1)
   price.
   **Execution stress:** the order is due at the next instant, open(t+2).
   Because step 1 runs first at that instant, a pending order is always
   filled before any new decision, so no order is ever replaced.
6. At the window end, unfilled orders are dropped.

**Clock anchor (Q10; FN3-1).** Under execution stress, a 00:00 increase fills
at 01:00. If the clock counts from the fill, the next 00:00 is 23 h later, so
increases are possible only every other day. G-7 would then test a 48 h hold,
not a one-hour delay.

| Option | Clock measured from | Consequence |
|---|---|---|
| **(b) decision time of an increase that was later filled** [recommended] | the 00:00 decision, counted only once its fill happens; cancelled orders never count | stress isolates the one-bar delay |
| (a) fill time | the fill | 23 h block, so G-7 tests a 48 h hold |
| (c) amend l.57 | — | owner wording |

### 2.2 Feature delay (Q11; FN3-9)

At decision instant `t`, every strategy input that depends on market data
(model features at inference, `σ̂`, the hourly band inputs) is lagged by one
bar. There are two readings:
- **(a) recompute with cutoff `t − 1h`** [recommended]. Each input is computed
  exactly as the baseline would compute it at `t − 1h`. A daily aggregate is
  then built from data up to 23:00, which is a true one-bar delay.
- **(b) last emitted.** Take the last value the baseline pipeline emitted at or
  before `t − 1h`. A daily feature emitted at 00:00 is then up to **24 h**
  old (FN3 C5), so G-6 becomes a one-day delay for trials built on daily
  features.

The following are unchanged: model refit times and training data, labels,
decision times, execution timing, held exposure and the clock (non-market
state), and the cost model's slippage inputs. Warm-up follows Q5. A missing or
non-finite lagged input makes the gate `UNAVAILABLE`.

### 2.3 Benchmark and ETH under each stress (separate questions; SN3-6, FN3-12, FN3-15)

Constitution §10 l.111 is evidence here, not a decision. Protocol l.42–43 and
l.279 fix the ETH sanity drawdown at 1x cost, and l.283 imports that into G-5.

| Q | Gate and leg | Options |
|---|---|---|
| Q12 (N-3) | G-5 BTC benchmark at 2x? | (i) yes, relative cost robustness [rec] / (ii) no |
| Q13 (N-3) | G-5 ETH point estimate: candidate and benchmark at 2x? | (i) both at 2x [rec] / (ii) candidate only. The ETH drawdown part stays at 1x as frozen; changing it is an amendment. |
| Q14 | G-7 BTC benchmark delayed? | (i) yes [rec] / (ii) no |
| Q15 | G-7 ETH: candidate and benchmark delayed, drawdown on the delayed path? | (i) all stressed [rec] / (ii) ETH kept at baseline |
| Q16 | G-6 BTC benchmark `σ̂` lagged? | (i) yes / (ii) no [rec: §10 does not list features; leaving the comparator unchanged isolates the candidate's latency] |
| Q17 | G-6 ETH: candidate inputs lagged, benchmark as Q16, drawdown on the lagged path? | (i) yes [rec] / (ii) ETH kept at baseline |

### 2.4 Pass statistic (Q18; SN3-7)

| Option | Each delay gate passes iff, on its stressed run |
|---|---|
| **survival** [recommended] | BTC `E-IMPROV` > 0, BTC candidate net return > 0, the BTC drawdown constraint holds, and the ETH sanity rule holds (mirrors l.283). A large degradation can still pass. |
| bounded degradation | survival AND stressed BTC `E-IMPROV` ≥ θ × unstressed, with `0 ≤ θ ≤ 1` chosen separately (l.264's 0.5 is a partial precedent). If the unstressed statistic is unavailable, the gate is `UNAVAILABLE`. |

The drawdown parts follow O-7 (G-2). A stressed statistic that is not finite
makes the gate `UNAVAILABLE`.

## 3. Workload (gross runs per nominee, before caching; FN3-13)

| Gate | Gross runs |
|---|---|
| G-11 | 502: 500 null runs, the candidate and the benchmark. The marginal count is 500. A trial with a preregistered `N/A` needs 0. |
| G-7 | 4, or 2 if the benchmark is not delayed. Add 0, 2 or 4 ETH runs depending on Q15. |
| G-6 | as G-7, plus model re-inference on lagged features in every fold |
| G-5 | 4, or 2 if the benchmark is not stressed |
| G-14 (N-2) | 500 model refits for target-model trials |

D-19 multiplies these by nominees × cells × replications.

## 4. Consequences

- **C-1** These are filters with no calibrated error rate. They cannot inflate
  the DSR bound, and they can lower power and add `U_proc` events.
- **C-2** G-11 tests the timing of the declared signal, given the trial's own
  sizing. It credits variance timing that sits in `s` (Q3), and it does not
  judge the sizing rule.
- **C-3** The following need §4 wording:
  - the applicability contract;
  - the preregistered `N/A` cases, with the G-11 `na` field;
  - the l.137 rewording;
  - the l.112 reading;
  - the clock anchor;
  - new row N-3.
- **C-4** No statistician reviewed this (R19-2).

## 5. Owner questions (each also allows revise or keep blocked)

| Q | Topic | Recommended |
|---|---|---|
| Q1 | G-11 construction (§1.2) | accept |
| Q1b | non-testable trials | preregistered `N/A` (not a C2 eligibility restriction) |
| Q2 | pure-sizing trials | preregistered `N/A` |
| Q3 | variance timing in `s` | credit it |
| Q4 | "match" | report-only rewording |
| Q5 | warm-up on gap days | yes |
| Q6 | minimum shift floor | 30 days |
| Q7 | shift draws | seeded random |
| Q8 | G-11 statistic | `E-IMPROV` |
| Q9 | pass rule | ≥ 476 |
| Q10 | clock anchor | decision time of a filled increase |
| Q11 | feature lag | recompute with cutoff `t − 1h` |
| Q12–Q17 | benchmark and ETH legs per stress | as in §2.3 |
| Q18 | delay statistic | survival |
