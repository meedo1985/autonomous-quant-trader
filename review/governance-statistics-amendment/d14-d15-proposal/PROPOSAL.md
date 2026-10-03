# D-14, D-15 proposal (revision 5): the random-exposure null and the delay gates

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
- Revision 5 applies every disposition. Nothing has been put to the owner yet.

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

**Path-dependent trials (Q1b; FN4-1, SN4-3).**

| Option | Effect |
|---|---|
| **(a) re-run overlays on each draw** [recommended] | Stateful trials are tested like any other. There is no `N/A` route through overlays, so a never-firing stop cannot be used to escape G-11. |
| (b) preregistered `N/A` for stateful trials | **A trial with `N/A` can be promoted without any G-11 evidence. Any directional trial could opt out by declaring a never-firing stop.** |
| (c) restrict C2 eligibility to non-stateful mappings | This needs amendment wording, and it excludes the owner's recorded rule (`TRADING_RULE_2026-09-27.md`). |

**Pure-sizing trials (Q2).** A declared constant `s` gives 500 draws identical
to the candidate.

| Option | Effect |
|---|---|
| **(a) preregistered `N/A`** [recommended] | Constitution §12 l.119 says vol management is "de-risking, not alpha". This option changes G-11's `na: "never"` in the S4 gate list and uses the P18-7 `N/A` exception (FN3-11). **Gaming:** a trial can no longer escape G-11 by moving its signal into `σ̂` (it is restricted, FN4-4), but it can still declare a constant signal. It then makes no timing claim at all, and G-11 tests only timing. |
| (b) always fail (rank rules) | The vol family is effectively closed. |
| (c) a different null later | Nothing is designed yet. |

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
| (i) drift + band on every change | held exposure drifts with price; any change needs `|target − held| >= band` | **A position below 0.10 can never be closed** (FN4 E1: a 0.10 position after a −0.5% move). The owner's −0.5% stop could never fire. |
| (ii) band against the last filled target | the band is tested against the last filled target, not drifted exposure | Closes the drift trap. Still traps a position reduced to a level in (0, 0.10) (frozen l.60). |
| **(iii) drift, and exits to 0 always allowed** [recommended] | exposure drifts; **a reduction to target 0 is never blocked by the band** | Exits are always possible. This amends l.60 ("safety-direction only", l.61, supports it). |

**At each hourly instant, in this order:**
1. Execute due fills at the open(t+1) price.
2. Evaluate the decision against the held exposure:
   - At 00:00 UTC, a change requires `|target − held| >=` the trial's
     declared band (l.97; l.112 sets 0.10; CANONICAL_BENCHMARKS l.10, l.26;
     FN4-5).
   - A **qualifying increase** also needs the clock to show ≥ 24 h.
   - At any hour, a reduction requires the target to be ≥ the band below the
     held exposure (l.60), except as Q20(iii) allows.
3. A passing decision creates an order. **Baseline:** the order fills at this
   same instant, at the open(t+1) price. **Execution stress:** it is due at the
   next instant. Because step 1 comes first, a pending order is always filled
   before the next decision, so no order is ever replaced.
4. At the window end, unfilled orders are dropped.

**Risk increase: two choices (SN4-2, FN4-7).** A delayed order can change
direction before it fills, because exposure drifts. (A planned increase from
2/5 to 1/2 becomes a reduction if the price doubles; SN4, exact.)
- **What counts (Q10a):**
  - **at fill** [recommended]: a fill counts as a risk increase only if held
    exposure actually rises (frozen l.57, "last risk increase");
  - **at decision.**
- **Clock anchor (Q10b):**
  - **decision time of a qualifying filled increase** [recommended];
  - **fill time:** under execution stress the next 00:00 is then 23 h later,
    so increases happen only every other day, and G-7 becomes a test of a
    48 h hold;
  - **amend l.57.**

**Disclosure (FN4-3).** Under the recommended anchor, the 24 h test never
binds in baseline runs or under execution stress: the gaps are always 24 h,
48 h and so on. In practice that drops l.57's 24 h clause (and l.113
`minimum_holding_hours_for_risk_increase`) for daily decisions. It would bind
only under the fill-time anchor.

### 2.2 Feature delay (SN4-4, FN4-6)

At decision instant `t`, every market-data input (model features at inference,
`σ̂`, the band inputs) takes **the last value emitted at or before `t − 1h`,
under that input's declared emission schedule**. No partial aggregate is ever
built.
- For the hourly trailing features of `FEATURE_FACTORY_v1` (l.5, 20), this is
  exactly a one-bar lag.
- A feature or model output emitted less often (for example daily) is up to
  one of its own periods old. The owner should know that G-6 is then a
  one-period delay for that input.

The following are unchanged: model refits and training data, labels, decision
times, execution, non-market state (held exposure, clock, overlay state), and
the slippage inputs. A missing or non-finite lagged input makes the gate
`UNAVAILABLE`. Q11 asks whether to accept this rule.

### 2.3 Benchmark and ETH under each stress (SN4-6, FN4-10, FN4-11)

Every leg is at 1x cost unless stated. Constitution §10 l.111 is evidence for
these choices, not a decision. Protocol l.42–43 and l.279 fix the ETH sanity
drawdown at 1x cost.

| Q | Gate | Benchmark legs (BTC and ETH alike) | ETH candidate leg |
|---|---|---|---|
| Q12 / Q13 (N-3) | G-5, 2x cost | (i) both benchmark legs at 2x [rec] / (ii) unchanged | the ETH point estimate is at 2x. **This is a reading:** `_at_1x_cost` (l.43, 279) is taken to bind the drawdown only. The ETH drawdown stays at 1x as frozen. |
| Q14 / Q15 | G-7, execution delay | (i) delayed [rec] / (ii) unchanged | (a) delayed, with the drawdown on the delayed path [rec] / (b) ETH entirely at baseline |
| Q16 / Q17 | G-6, feature delay | (i) the benchmark's `σ̂` is lagged / (ii) unchanged [rec] | (a) the ETH candidate's inputs are lagged, with the drawdown on the lagged path [rec] / (b) ETH entirely at baseline |

The benchmark choice for each gate applies to the BTC and ETH legs alike, so
an ETH candidate-only stress is a combination that can be chosen.

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

## 3. Workload: stressed runs only, per nominee, gross (FN4-9, SN4-7)

| Gate | BTC runs | ETH runs |
|---|---|---|
| G-11 | 500 null runs (plus the cached candidate and benchmark). A pure-sizing trial with `N/A` needs 0. | 0 |
| G-5 | 2 under Q12(i), 1 under (ii) | 2 under (i), 1 under (ii) |
| G-7 | 2 under Q14(i), 1 under (ii) | 0 under Q15(b); otherwise 2 under Q14(i), 1 under Q14(ii) |
| G-6 | 2 under Q16(i), 1 under (ii) | 0 under Q17(b); otherwise 2 under Q16(i), 1 under Q16(ii) |

G-6 also needs model re-inference on lagged features in every fold. G-14 (N-2)
needs 500 refits for each target-model trial. D-19 multiplies all of these by
nominees × cells × replications.

## 4. Consequences

- **C-1 Filters.** These are filters, with no calibrated error rate. They
  cannot inflate the DSR bound. They can lower power and add `U_proc`.
- **C-2 What G-11 tests.** G-11 tests the timing of the declared signal, given
  the trial's own sizing and overlay. It credits variance timing in `s` (Q3).
- **C-3 Wording and new rows.** These need §4 wording:
  - the three-layer declaration and the restricted `σ̂`;
  - the overlay re-run;
  - the pure-sizing `N/A`, with the G-11 `na` field;
  - the l.137 rewording;
  - the event contract;
  - N-4 (held exposure and exits; this amends l.60 under (iii));
  - the risk-increase reading and anchor (the 24 h clause in effect becomes
    inert, l.57 and l.113);
  - N-3.
- **C-4 Review.** No statistician has reviewed this (R19-2).

## 5. Owner questions (each also allows "revise" or "keep blocked")

| Q | Topic | Recommended |
|---|---|---|
| Q1 | G-11 construction (§1.2) | accept |
| Q1b | path-dependent trials | re-run overlays on each draw |
| Q2 | pure-sizing trials | preregistered `N/A` |
| Q3 | variance timing in `s` | credit it |
| Q4 | "match" | report-only rewording |
| Q5 | warm-up on gap days | yes |
| Q6 | shift floor `f` | 30 days |
| Q7 | shift draws | seeded random |
| Q8 | G-11 statistic | `E-IMPROV` |
| Q9 | pass rule | at least 476 |
| Q10a | what counts as a risk increase | at fill |
| Q10b | clock anchor | decision time of a qualifying filled increase |
| Q11 | feature-lag rule (§2.2) | accept |
| Q12–Q17 | benchmark and ETH legs per stress | as in §2.3 |
| Q18 | delay statistic | survival |
| Q19 | event contract (§2.1) | accept |
| Q20 (N-4) | held exposure and exits | drift, with exits to 0 always allowed |
