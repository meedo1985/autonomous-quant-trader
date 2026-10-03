# D-14, D-15 proposal (revision 7): the random-exposure null and the delay gates

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting
work, done under the owner's instruction "let agent do the answers all the
time". D-rows are decided only by the owner, after two different-model reviews
(R19-2).

**History:**
- Revisions 1 and 2 were rated UNSOUND by both reviewers and withdrawn.
- Revision 3 (`540e773`) adopted the signal-shift construction suggested in
  SN2-1. Fable FN3 and Sol SN3 both rated it SOUND WITH FIXES. Their exact
  checks confirm σ̂ alignment for **signals that do not depend on volatility**
  (FN3), and they **do not establish exchangeability** (SN3).
- Revision 4 (`83fc993`) was found NOT READY in focused checks FN4 and SN4.
  Adjudication: `ADJUDICATION_83FC993.md`.
- Revision 5 (`0c16c35`): focused checks FN5 and SN5 both NOT READY. Adjudication
  `ADJUDICATION_0C16C35.md`.
- Revision 6 (`4c8648f`): the focused checks FN6 and SN6 both returned NOT READY.
  Adjudication: `ADJUDICATION_4C8648F.md`.
- Revision 7 applies every disposition **without a further check** [AI default].
  The core construction has been stable since revision 3. What remains are
  owner choices, which are now stated as questions. Going without a further
  check is weaker than another check, and it is recorded as such.

**Authority:** both rows are `STAT` then `§4`. Two proposed new rows:
- **N-3:** the stress semantics of G-5.
- **N-4:** the engine semantics of held exposure and exits. These govern
  **all** runs, baseline included, not only these gates (FN4-2).

## 1. D-14: the random-exposure null (G-11)

**Frozen text** (l.134–140, 289): the construction must "match candidate mean
exposure and turnover on BTC; evaluate paired delta-Sharpe versus
VOL_TARGET_BUY_AND_HOLD". It "Removes beta/time-in-market advantage". It uses
500 samples and `null_minimum_percentile` 0.95.

### 1.1 Notation

- **`T`**: the number of UTC days in the eligible window (FN4-13). An
  incomplete day makes the gate `UNAVAILABLE` (§1.5). Days are `d = 0 … T−1`
  and hours `h = 0 … 24T−1`.
- **`g`**: the declared `gap_embargo.value_days` (§4 draft §2.1). This is fixed
  by the draft and is not an owner question (FN4-12).
- **Scope:** BTC only, at 1x cost.

### 1.2 Construction

**The trial's declared mapping** (Constitution §8 l.97 "exposure mapping …
rebalance rule including band+min hold") has three layers:

```
target_h = overlay( clip( s_h · τ / σ̂_h , 0, 1 ) , own path state )
```

- **`s_h >= 0`** is a signal computed only from market data and the trial's
  declared model outputs. It may be evaluated hourly (l.55).
- **`τ ∈ {0.40, 0.60, 0.80}`** is the vol target (l.127).
- **`σ̂_h`** is the trial's sizing estimator. It is **restricted to the frozen
  set**: `EWMA_168h` by default (l.115), or for the vol family one of l.121.
  It is annualized as in CANONICAL_BENCHMARKS l.23. This closes the route of
  moving the signal into `σ̂` (FN4-4).
- **`overlay`** is an optional declared path-dependent rule (stop,
  take-profit, hysteresis). It acts on the run's **own** price path and
  position.

The three layers are part of the hashed declaration. Whether a trial is
G-11-testable is checked mechanically from the declared interface.

**Null draw `i`** uses `s_((h + 24·k_i) mod 24T)` in place of `s_h`. The
draw is sized by the trial's own `σ̂_h` at the real hour, and then **the
declared overlay is re-run on the draw's own path**, in the same way the engine
already re-simulates held exposure, the band and the clock for every run
(FN4-1).

This keeps the trial's `σ̂` alignment for any frozen estimator and vol target
(FN3, SN3, exact), **for signals that do not depend on volatility**. It does not
keep volatility alignment that sits inside `s` (§1.3).

**What G-11 can and cannot test (FN6-1).** The null shifts only `s`. The
overlay is re-run on each draw's own path, but its timing comes from the same
price path in every draw, so it cancels out. **G-11 therefore never tests
overlay timing, in any class.** It is not possible to force the gate to bite
on overlays by classifying trials. If a trial times entries with its overlay
and declares any non-constant `s`, however small, it is ranked only on that
`s`, and the rank does not change as `s` shrinks to zero (FN6 E1, exact).

**Declared class (SN6-1).** Every hypothesis declares a field
`g11_class ∈ {signal_timed, constant_signal}` as part of the hashed
interface.
- **Check.** The engine checks in **every** run that a `constant_signal`
  trial's `s` is identical at every hour.
- **Mismatch.** If it is not, the gate is `UNAVAILABLE`, with the reason
  `CLASS_MISMATCH`.
- **Signal-timed trial with constant `s`.** A `signal_timed` trial whose `s`
  turns out constant gives 500 tied draws. An all-tie result is `FAIL`
  **whatever rule Q9 picks**, overriding type-7's pass on ties (FN6-2).

**Overlays (FN6-8) [AI default].** An overlay may only keep the target that
comes from `s·τ/σ̂`, or set it to 0 (stop, take-profit, hysteresis exit).
It may not set or rescale the size. Re-entry follows `s`.

**Q1b. Overlays on signal-timed trials.**
- **(a) Re-run the overlay on each draw** [recommended]. This tests the
  signal's timing given the overlay.
- **(b) Preregistered `N/A` for any trial with an overlay.** **Such trials
  could then be promoted without G-11 evidence.**
- **(c) Restrict C2 eligibility to overlay-free mappings**, by amendment.

**Q2b. Overlay timing: one decision that covers every class (FN6-1).**

| Option | Rule | Consequence |
|---|---|---|
| **(A) Accept and disclose** [recommended] | G-11 tests signal timing only. Every `constant_signal` trial (with or without an overlay) gets a preregistered `N/A`. | **Overlay timing is never tested by G-11.** A trial whose edge lies in its stop or take-profit timing can be promoted without that timing being tested against a null. D-18's false-promotion bound still holds, because it comes from the DSR (P18-7), and the other gates still apply. |
| (B) Fail-closed for market-reading overlays | Any trial whose overlay reads prices, P&L or path state cannot pass G-11 until a separate overlay null (for example, random entry days) is designed and decided. | No such trial can be promoted until that null exists. This includes the owner's recorded rule. |
| (C) Materiality test | Overlays are tested only above some "materiality" level. | Not defined, so it cannot be chosen now. |

Rev 6's recommendation to fail overlay-timed trials only *looked*
fail-closed (FN6-1), so it is withdrawn.

**Q2. Constant-signal trials without an overlay** (pure sizing):
- **(a) preregistered `N/A`** [recommended]. The null keeps `σ̂` aligned, so it
  cannot test `σ̂` timing (FN6-4), and Constitution §12 l.119 calls vol
  management "de-risking, not alpha". This changes G-11's `na: "never"` and
  uses the P18-7 `N/A` exception (FN3-11).
- **(b) always fail.** This closes the vol family.

Under Q2b(A), Q2(a) and the constant-signal-with-overlay case get the same
treatment.

**The owner's recorded rule** (`TRADING_RULE_2026-09-27.md`; FN6-3,
SN6-1). The record fixes the size (10%), the stop (−0.5%) and the
take-profit (+10%), and notes that "a profit needs a real entry signal". It
does not say what triggers entry, so every mapping below is **a reading**.
- **Sizing comes first.** A fixed 10% is not expressible as `s·τ/σ̂` with
  the restricted `σ̂` and a frozen `τ`, and an overlay may not set the size
  (above). Whether a fixed-size rule can be registered at all is a
  hypothesis-registration question for C1/C2, **not** decided here. Until it
  is decided, the outcomes below are conditional.
- **With no entry signal** (always enter when flat): the trial is
  `constant_signal` with an overlay. Under Q2b(A) it gets `N/A` at G-11;
  under (B) it cannot be promoted.
- **With an entry signal:** the trial is `signal_timed`. G-11 ranks the
  timing of that entry signal; the stop and take-profit timing goes untested
  under (A), and under (B) the trial cannot be promoted.

### 1.3 Variance timing inside the signal (Q3)

A signal that reacts only to volatility can beat its shifted copies with no
directional information (FN3 C2, exact).
- **(a) credit it** [recommended].
- **(b) treat as sizing**, giving a preregistered `N/A` when every declared
  signal input is a volatility feature.

The gaming argument applies to both. Under (a), G-11 can be passed through
volatility timing alone. Under (b), the classification depends on how the
inputs are labelled at declaration.

### 1.4 "Match" (l.137; Q4)

- **(a) reword** [recommended]: "shift the declared signal by whole days,
  re-size with the trial's own estimator and re-run its overlay; realised mean
  exposure and turnover of every draw are reported, not matched."
- **(b) match within a tolerance**, rejecting draws outside it.

### 1.5 Domain, state and shifts

**`UNAVAILABLE`, with a reason code, and no replacement** if any of the
following hold:
- any `s_h` is non-finite or negative;
- any `σ̂_h` is non-finite or ≤ 0;
- any pre-clip product is non-finite;
- any day is incomplete;
- the statistic for the candidate or for any draw is unavailable (zero
  variance or insufficient observations, `statistics.py:173–200`).

The denominator stays 500.

**State.** Every run starts at the window start with exposure 0, no pending
order, an unset clock and a fresh overlay state.

**Warm-up (Q5).** Warm-up may read the `g` gap days, which are engine-reachable
under `excluded_days_status`.
- **(a) yes** [recommended].
- **(b) no**, in which case estimator state is `g` days stale at the start.

**Wrap.** The wrap is an ordinary day boundary, and it is reported.

**Shift set:** `{m, …, T − m}`, with `m = max(g, f)`.
- **Floor `f` (Q6):** recommended 30 days, an AI default with no basis in
  how persistent signals are. Near shifts of slow signals cost power.
- Availability requires `T − 2m >= 499`, and D-19 sets `T_min` accordingly.

**How the shifts are drawn (Q7):**
- **(a) seeded random** [recommended]: 500 shifts drawn without replacement,
  using the trial seed (l.266) with purpose `"random_exposure_null"`. The
  sampling mechanics depend on D-20.
- **(b) deterministic:** `k_i = m + floor(i·(T−2m)/499)` for `i = 0 … 499`.

### 1.6 Statistic (Q8) and pass rule (Q9)

**Statistic (Q8):**
- **`E-IMPROV`** [recommended]. All draws share one benchmark leg, so this
  ranks exactly by the trial's own Sharpe (Lemma L-1).
- **`E-DIFF`**, which ranks the departure P&L.

**Pass rule (Q9):**

| Rule | Pass iff | When all 500 draws tie |
|---|---|---|
| **plus-one** [recommended] | at least 476 of 500 draws are strictly below the candidate (as N-2) | fails |
| rank 475 | at least 475 strictly below | fails |
| type-7 (matrix PROPOSED (a), l.56) | the candidate is ≥ the type-7 quantile | **passes** |

No error rate is claimed; 25/501 assumes exchangeability, which is not
established.

## 2. D-15: the delay gates (G-6, G-7)

### 2.1 Event contract (Q19 accepts the whole contract; SN4-5)

These semantics govern **every** run: baseline, stressed and null.

**Time.** Timestamps are instants: close(t) = open(t+1).

**Orders.** An order stores an absolute target exposure.

**Fills.** **Every fill atomically updates** the position, equity, held
exposure and, where applicable, the clock, including a same-instant baseline
fill (SN4-1, FN4-8).

**Held exposure (Q20, N-4; FN4-2).** Held exposure is the position value divided by
equity. This interacts with the band:

| Option | Rule | Consequence |
|---|---|---|
| (i) drift + band on every change | held exposure drifts with price; any change needs `|target − held| >= band` | **A 0.10 position cannot be closed while the price is below entry** (it can be closed only once held exposure drifts back to ≥ 0.10, exactly when price ≥ entry; FN4 E1, FN5 E5). So the owner's −0.5% stop could never fire. |
| (ii) band against the last filled target | the band is tested against the last filled target, not drifted exposure | Closes the drift trap. Still traps a position reduced to a level in (0, 0.10) (frozen l.60). |
| **(iii) drift, and exits to 0 always allowed** [recommended] | exposure drifts; **a reduction to target 0 is never blocked by the band**, at 00:00 or at any hour | Exits are always possible. This amends l.60, BACKTESTER_SPEC l.10 and CANONICAL_BENCHMARKS l.12 (FN5-5); l.61, "safety-direction only", supports it. |

**At each hourly instant, in this order:**
1. Execute due fills at the open(t+1) price.
2. Evaluate the decision against the held exposure:
   - At 00:00 UTC, a change requires `|target − held| >=` the trial's
     declared band (l.97; l.112 sets 0.10; CANONICAL_BENCHMARKS l.10, l.26;
     FN4-5), except as Q20(iii) allows.
   - The direction of an order is classified **here, at decision time**, by
     comparing its target with the held exposure. An increase needs the clock to
     show ≥ 24 h and is allowed only at 00:00 (l.57).
   - At any hour, a reduction requires the target to be ≥ the band below the
     held exposure (l.60), except as Q20(iii) allows.
3. A passing decision creates an order. **Baseline:** the order fills at this
   same instant, at the open(t+1) price. **Execution stress:** it is due at the
   next instant. Because step 1 comes first, a pending order is always filled
   before the next decision, so no order is ever replaced.
4. At the window end, unfilled orders are dropped.

**Direction flips and the clock (SN5-2, FN5-2, FN4-7).** Exposure drifts with
price, so an order can change direction before it fills. A planned cut from
3/5 to 1/2 fills as an increase if the price falls by more than a third within
the hour (FN5 E3). The rule:

- **Eligibility is decided at decision time** (step 2) and is never
  re-judged later. No future price is used.
- **A reduction order never fills as an increase.** At fill, the executed
  target is `min(order target, held exposure at fill)`. If the order would now
  raise exposure, it executes as no change. [AI default: clamp]
- **An increase order fills as ordered.** If it now lowers exposure, that is a
  safety-direction change and it stands.
- **The clock is set only at the fill of an order that actually raised held
  exposure.** Because of the clamp, only 00:00 increase orders can do that.

**Clock anchor (Q10; SN6-2).** The two choices are mutually exclusive.
- **(a) Fill time, as frozen** (l.57: "24h since last risk increase"; l.113).
  Under execution stress a 00:00 increase fills at 01:00, so the next 00:00
  is 23 h later and is blocked. Increases then happen at most every other day,
  and G-7 becomes in effect a 48-hour-hold test.
- **(b) Decision time** [recommended]. The clock is anchored at the 00:00
  decision of an order whose fill actually raised exposure. **This amends
  l.57 and l.113**, and the same 24 h clause in BACKTESTER_SPEC l.9 and
  CANONICAL_BENCHMARKS l.11 (FN6-7). Under stress it permits a new increase
  23 h after the actual fill. In return, the stress then isolates the one-hour
  delay.

**Disclosure (FN4-3, FN6-7).**
- **Under (b), with the clamp:** every anchor is a 00:00 decision, so the
  24 h test never binds; the gaps are 24 h, 48 h and so on. In effect this
  drops the 24 h clause for daily decisions.
- **Under (a):** the clause binds under stress.

### 2.2 Feature delay (SN4-4, FN4-6, FN5-3, FN5-4, FN6-6, SN6-3, SN6-4)

**Inputs that are lagged.** At decision instant `t`, every **market-data
input of the strategy** is lagged:
- the **direct market-data inputs of `s`**: prices, returns and any series
  `s` reads without going through the model;
- the model's input features;
- the inputs of `σ̂`;
- every price or return the overlay reads, including stop and take-profit
  triggers.

**How lagged values are used.** `s`, `σ̂`, the model outputs and the overlay
outputs are then **recomputed from the lagged inputs**, rather than taken as
earlier emitted values. The order target and the band-test target are formed
from those recomputed values.

**What "lagged" means (Q11; SN6-4).**

| Option | Each input takes | Consequence |
|---|---|---|
| **(a) one-clock-hour cutoff** [recommended] | its value as of `t − 1h`, meaning the last emission at or before `t − 1h` | This is literally "1 bar" on the 1h bar interval (l.53, l.267). For hourly inputs (FEATURE_FACTORY_v1 l.5, l.20) it is exactly a one-bar lag. **For an input emitted less often, the delay depends on phase:** a daily input emitted at 00:00 and read at 12:00 gets **no** extra delay, but read at 00:00 it gets the previous day's value. |
| (b) the immediately preceding emission | the emission before the one the baseline uses | A uniform one-emission delay for every input: one hour for hourly inputs, one day for daily inputs. This departs from "1 bar" for coarser inputs, and is a reading of l.267. |

**Model outputs.** These are re-inferred on the lagged inputs at the model's
own emission times. The decision uses the last output at or before `t`. A
model output therefore inherits the lag of its inputs. It is one bar only
when every input of the model is hourly; with coarse inputs it is as the table
above describes (FN6-6).

**Unchanged.** The following are not lagged:
- model refits and training data;
- labels;
- decision times;
- execution;
- slippage inputs;
- held exposure (position accounting at the current price);
- the clock;
- the overlay's own position state.

A missing or non-finite lagged input makes the gate `UNAVAILABLE`.

### 2.3 Benchmark and ETH under each stress (SN4-6, FN4-10, FN4-11)

Every leg is at 1x cost unless stated. Constitution §10 l.111 is evidence for
these choices, not a decision. Protocol l.42–43 and l.279 fix the ETH sanity
drawdown at 1x cost.

| Q | Gate | BTC benchmark leg | ETH legs |
|---|---|---|---|
| Q12 | G-5, 2x cost (N-3) | (i) at 2x [rec] / (ii) unchanged | — |
| Q13 | G-5 ETH (N-3) | — | (a) [rec]: **ETH candidate** at 2x for the point estimate; **ETH benchmark** at 2x under Q12(i), at 1x under Q12(ii); **ETH drawdown** at 1x as frozen. This reads `_at_1x_cost` (l.43, l.279) as binding the drawdown only, **which is a reading**. / (b): the whole ETH sanity rule at 1x, reading the suffix as binding the whole rule. |
| Q14 | G-7, execution delay | (i) delayed [rec] / (ii) unchanged | — |
| Q15 | G-7 ETH | — | (a) the ETH candidate is delayed, the ETH benchmark follows Q14, and the drawdown is measured on the delayed path [rec] / (b) **ETH entirely at baseline**: both ETH legs and the drawdown are unstressed, which **overrides Q14 for ETH** |
| Q16 | G-6, feature delay | (i) `σ̂` lagged / (ii) unchanged [rec] | — |
| Q17 | G-6 ETH | — | (a) the ETH candidate's inputs are lagged, the ETH benchmark follows Q16, and the drawdown is on the lagged path [rec] / (b) **ETH entirely at baseline**, which overrides Q16 for ETH |

Under option (a), the BTC and ETH benchmark legs are treated alike. Under (b),
ETH is not stressed at all (SN5-3, FN5-7).

### 2.4 Pass statistic (Q18)

- **Survival** [recommended]. The gate passes iff, on its stressed run:
  - BTC `E-IMPROV` > 0;
  - BTC candidate net return > 0;
  - the BTC drawdown holds;
  - ETH sanity holds (mirroring l.283).

  A large degradation can still pass.
- **Bounded degradation.** Survival, and also stressed BTC `E-IMPROV` ≥ θ ×
  unstressed, with `0 ≤ θ ≤ 1`. If the unstressed statistic is unavailable,
  the gate is `UNAVAILABLE`.

The drawdown parts follow O-7.

## 3. Workload: stressed runs, gross (FN4-9, SN4-7, FN5-8, SN5-3)

**Per nominee** (the candidate legs):

| Gate | BTC | ETH |
|---|---|---|
| G-11 | 500 null runs (the candidate and benchmark base runs are cached). A `constant_signal` trial with a preregistered `N/A` needs 0. | 0 |
| G-5 | 1 | 1 under Q13(a), 0 under (b) |
| G-7 | 1 | 1 under Q15(a), 0 under (b) |
| G-6 | 1, plus model re-inference on lagged features in every fold | 1 under Q17(a), 0 under (b) |

**Shared per cell.** The stressed benchmark legs are the same for every
nominee, so they run once:

| Gate | BTC | ETH |
|---|---|---|
| G-5 | 1 under Q12(i), else 0 | 1 under Q12(i) with Q13(a), else 0 |
| G-7 | 1 under Q14(i), else 0 | 1 under Q14(i) with Q15(a), else 0 |
| G-6 | 1 under Q16(i), else 0 | 1 under Q16(i) with Q17(a), else 0 |

G-14 (N-2) needs 500 refits for each target-model trial. D-19 multiplies the
per-nominee runs by nominees × cells × replications, and the shared runs by
cells × replications.

## 4. Consequences

- **C-1 Filters.** These are filters, with no calibrated error rate. They
  cannot inflate the DSR bound. They can lower power and add `U_proc`.
- **C-2 What G-11 tests.** G-11 tests the timing of the declared signal, given
  the trial's own sizing and overlay. It credits variance timing in `s` (Q3).
  **It never tests overlay timing, in any class** (Q2b).
- **C-3 Wording and new rows.** These need §4 wording:
  - the three-layer declaration and the restricted `σ̂`;
  - the overlay re-run;
  - the declared `g11_class` field and its check; the overlay limits; the constant-signal `N/A` with the G-11 `na` field (Q2/Q2b);
  - the l.137 rewording;
  - the event contract;
  - N-4 (held exposure and exits; this amends l.60, BACKTESTER_SPEC l.10 and
    CANONICAL_BENCHMARKS l.12 under (iii));
  - the direction clamp; under Q10(b), the amendment of l.57, l.113,
    BACKTESTER_SPEC l.9 and CANONICAL_BENCHMARKS l.11;
  - the l.267 readings (Q11).
  - N-3.
- **C-4 Review.** No statistician has reviewed this (R19-2).

## 5. Owner questions (each also allows "revise" or "keep blocked")

| Q | Topic | Recommended |
|---|---|---|
| Q1 | G-11 construction (§1.2) | accept |
| Q1b | signal-timed trials with an overlay | re-run the overlay on each draw |
| Q2 | constant-signal trials without an overlay | preregistered `N/A` |
| Q2b | overlay timing (all classes) | (A) accept and disclose: untested; constant-signal trials `N/A` |
| Q3 | variance timing in `s` | credit it |
| Q4 | "match" | report-only rewording |
| Q5 | warm-up on gap days | yes |
| Q6 | shift floor `f` | 30 days |
| Q7 | shift draws | seeded random |
| Q8 | G-11 statistic | `E-IMPROV` |
| Q9 | pass rule | at least 476 |
| Q10 | clock anchor | (b) decision time, which amends l.57/l.113 (alternative (a) is the frozen fill time) |
| Q11 | feature lag | (a) one-clock-hour cutoff |
| Q12–Q17 | benchmark and ETH legs per stress | as in §2.3 |
| Q18 | delay statistic | survival |
| Q19 | event contract (§2.1) | accept |
| Q20 (N-4) | held exposure and exits | drift, with exits to 0 always allowed |
