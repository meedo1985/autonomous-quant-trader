# D-14, D-15 proposal (revision 6): the random-exposure null and the delay gates

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
- Revision 6 applies every disposition. Nothing has been put to the owner yet.

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

**Three classes of trial (FN5-1, SN5-1).** The class is fixed mechanically at
declaration from the hashed interface:
- **signal-timed:** `s` is not constant. The null shifts `s` and re-runs the
  overlay on each draw's own path.
- **timing-free:** `s` is constant and there is **no** overlay.
- **overlay-timed:** `s` is constant and an overlay reads prices, P&L or
  path state.

Shifting a constant `s` changes nothing. So for an overlay-timed trial every
draw equals the candidate (FN5 E1, exact), and the null cannot test its timing.
Rev 5 wrongly said that overlays offered "no `N/A` route", and that a
constant-`s` trial "makes no timing claim at all". Both claims are withdrawn.

**Signal-timed trials with an overlay (Q1b).**

| Option | Effect |
|---|---|
| **(a) re-run the overlay on each draw** [recommended] | The trial is tested on the timing of its signal. The overlay acts on each draw's own path. |
| (b) preregistered `N/A` for any trial with an overlay | **Promotion would then be possible without G-11 evidence, and any trial could opt out by declaring a stop that never fires.** |
| (c) restrict C2 eligibility to mappings without overlays | This needs amendment wording. |

**Timing-free trials (Q2):**
- **(a) preregistered `N/A`** [recommended]. Constitution §12 l.119 calls vol
  management "de-risking, not alpha". This option changes G-11's
  `na: "never"` and uses the P18-7 `N/A` exception (FN3-11). It applies only
  when `s` is constant **and** there is no overlay, so no timing exists to
  test.
- **(b) always fail.** Under the rank rules all draws tie, which closes the
  vol family.
- **(c) a different null later.**

**Overlay-timed trials (Q2b):**

| Option | Effect |
|---|---|
| **(a) fail** [recommended] | All draws tie, so the rank rules fail. This is fail-closed, and **such a trial can never be promoted** unless it declares a non-constant entry signal `s`. |
| (b) preregistered `N/A` | **Promotion without G-11 evidence.** Any trial could move its timing into an overlay to opt out. |
| (c) a different null that perturbs overlay timing (for example, random entry days) | Not designed yet. Until it exists, (a) applies. |
| (α) limit overlays to the run's own position and its entry-relative P&L | All market-data timing must then sit in `s`. The trial is still overlay-timed if `s` is constant, so this does not change its outcome; it only narrows what an overlay may be. |

**The owner's recorded rule** (`TRADING_RULE_2026-09-27.md`) is a fixed
10% entry when flat, with a −0.5% stop and a +10% take-profit, and no
entry signal:
- **Sizing.** A fixed 10% cannot be written as `s·τ/σ̂` with the restricted
  `σ̂` and a frozen `τ` unless volatility enters `s`, and that would mis-size
  every draw (FN5 E2). Whether a fixed-size rule fits the frozen
  `vol_target` parameter point (l.126–128, 182) is a separate,
  hypothesis-registration question and is **not** settled here.
- **Timing.** Read as declared, with constant `s`, the rule is overlay-timed.
  Under Q2b(a) it **fails G-11**, and so cannot be promoted. Under Q2b(b) it
  would skip G-11.

The owner should know this before answering Q2b.

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

**Clock anchor (Q10).**
- **(b) the decision time of that order** [recommended]. Stress then isolates
  the one-bar delay.
- **(a) the fill time.** Under execution stress the next 00:00 is then 23 h
  later, so increases are possible only every other day, and G-7 becomes a
  48 h-hold test.
- **(c) amend l.57.**

**Disclosure (FN4-3, FN5-2).** Under (b), with the clamp, every clock anchor is
a 00:00 decision, so the 24 h test never binds in baseline or stressed runs:
the gaps are 24 h, 48 h and so on. In practice that drops l.57's 24 h clause
(and l.113 `minimum_holding_hours_for_risk_increase`) for daily decisions.
Under (a) the clause binds under stress.

### 2.2 Feature delay (SN4-4, FN4-6, FN5-3, FN5-4)

**Lagged inputs.** At decision instant `t`, every **market-data input of the
strategy** takes the last value emitted at or before `t − 1h`, under that
input's declared emission schedule. No partial aggregate is ever built. The
inputs are:

- the model's input features;
- `σ̂`;
- every price or return the overlay reads, including its stop and take-profit
  triggers [AI default];
- the target used in the band test, computed from the lagged `s` and `σ̂`.

For the hourly trailing features of `FEATURE_FACTORY_v1` (l.5, l.20), this is
exactly a one-bar lag.

**Model outputs (FN5-3).** Model outputs are **not** lagged separately. The
model is re-inferred at its own declared emission times on the lagged features.
The decision then uses the last output emitted at or before `t`. So a daily
model output carries only the one-bar lag of its inputs.

A **market-data feature** emitted less often than hourly is taken at its last
emission at or before `t − 1h`, so it can be up to one of its own periods old.
This applies `feature_delay_stress_bars: 1` (l.267) to features as "one bar for
hourly inputs, one emission for coarser ones". **It is a reading of l.267,
labelled as such.**

**Unchanged.** Model refits and training data, labels, decision times,
execution, and the slippage inputs do not change. Held exposure, the clock and
the overlay's own position state also do not change. Held exposure is position
accounting at the current price; it is not a strategy input.

A missing or non-finite lagged input makes the gate `UNAVAILABLE`. Q11 asks
whether to accept this rule.

### 2.3 Benchmark and ETH under each stress (SN4-6, FN4-10, FN4-11)

Every leg is at 1x cost unless stated. Constitution §10 l.111 is evidence for
these choices, not a decision. Protocol l.42–43 and l.279 fix the ETH sanity
drawdown at 1x cost.

| Q | Gate | BTC benchmark leg | ETH legs |
|---|---|---|---|
| Q12 | G-5, 2x cost (N-3) | (i) at 2x [rec] / (ii) unchanged | — |
| Q13 | G-5 ETH (N-3) | — | (a) the ETH point estimate (candidate and benchmark, following Q12) at 2x, with the drawdown at 1x [rec]. This reads `_at_1x_cost` (l.43, l.279) as binding the drawdown only. **It is a reading.** / (b) the whole ETH sanity rule at 1x, reading the suffix as binding the whole rule. |
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
| G-11 | 500 null runs (the candidate and benchmark base runs are cached). A timing-free `N/A` trial needs 0; an overlay-timed trial still runs its 500 identical draws, or the engine may short-circuit them as ties. | 0 |
| G-5 | 1 | 1 |
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
  It cannot test timing that lives only in an overlay (Q2b).
- **C-3 Wording and new rows.** These need §4 wording:
  - the three-layer declaration and the restricted `σ̂`;
  - the overlay re-run;
  - the three trial classes, the timing-free `N/A` with the G-11 `na` field, and the overlay-timed rule (Q2b);
  - the l.137 rewording;
  - the event contract;
  - N-4 (held exposure and exits; this amends l.60, BACKTESTER_SPEC l.10 and
    CANONICAL_BENCHMARKS l.12 under (iii));
  - the direction clamp and the clock anchor (the 24 h clause in effect becomes
    inert, l.57 and l.113);
  - the l.267 reading for coarser features.
  - N-3.
- **C-4 Review.** No statistician has reviewed this (R19-2).

## 5. Owner questions (each also allows "revise" or "keep blocked")

| Q | Topic | Recommended |
|---|---|---|
| Q1 | G-11 construction (§1.2) | accept |
| Q1b | signal-timed trials with an overlay | re-run the overlay on each draw |
| Q2 | timing-free trials (constant `s`, no overlay) | preregistered `N/A` |
| Q2b | overlay-timed trials (constant `s` with a market-reading overlay) | fail |
| Q3 | variance timing in `s` | credit it |
| Q4 | "match" | report-only rewording |
| Q5 | warm-up on gap days | yes |
| Q6 | shift floor `f` | 30 days |
| Q7 | shift draws | seeded random |
| Q8 | G-11 statistic | `E-IMPROV` |
| Q9 | pass rule | at least 476 |
| Q10 | clock anchor | decision time of an increase that actually raised exposure at fill |
| Q11 | feature-lag rule (§2.2) | accept |
| Q12–Q17 | benchmark and ETH legs per stress | as in §2.3 |
| Q18 | delay statistic | survival |
| Q19 | event contract (§2.1) | accept |
| Q20 (N-4) | held exposure and exits | drift, with exits to 0 always allowed |
