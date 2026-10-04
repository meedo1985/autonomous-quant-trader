# Annex C — promotion gate definitions for cycle C2

**Status:** `AI WORDING PROPOSAL — NOT AN AMENDMENT — NOT SIGNED — NOT ACTIVE`
**Date:** 2026-10-04, revision 2 (applies `ADJUDICATION_AB9AD3F.md`)
**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`). This annex restates
owner-decided rows as operative text. It decides nothing.

**Why a consolidated annex.** Annexes A and B are verbatim, because their
decided texts contain no alternatives. The decided gate proposals are
different: each one sets out options alongside the chosen one. Copying them
verbatim would need a key saying which option was chosen for every
question. This annex states only the chosen options instead. Each clause
cites its source. Two kinds of reference are used:
- Bracketed source tags (`[D-xx]`, `[O-n]`, `[Qn]`) are informative.
- In-text line references (`l.n` and named spec lines) are **normative**. They
  are read against the v1.0 files at their frozen hashes. (FA5-11)

**Fidelity rule.** Before signing, any difference between this annex and a
cited owner decision record is a drafting defect, to be corrected here. It is
not a new decision. After activation, this annex is the operative text, read
under DRAFT_WORDING §0 precedence.

## Sources (decided objects)

| Rows | Owner record | Decided text |
|---|---|---|
| D-01..D-04 | `d02-d04-proposal/OWNER_DECISION_D01_D04.md` | PROPOSAL rev 2 `352bb0d` |
| D-05 | `d05-proposal/OWNER_DECISION_D05.md` | PROPOSAL rev 2 `2eba91c` §3 |
| D-06, D-07 | `d06-d07-proposal/OWNER_DECISION_D06_D07.md` | PROPOSAL rev 2 `63888f9` P6-1..P7-3, §3 option (b) |
| D-08..D-10 | `d08-d10-proposal/OWNER_DECISION_D08_D10.md` | PROPOSAL rev 2 `8a9b807` |
| N-1, N-2 | `n1-n2-proposal/OWNER_DECISION_N1_N2.md` | PROPOSAL rev 2 `82a6495` §1, §2 option (a) |
| D-14, D-15, N-3, N-4 | `d14-d15-proposal/OWNER_DECISION_D14_D15.md` plus `OWNER_DECISION_D14_D15_ADDENDUM.md` (governs) | PROPOSAL rev 7 `411e1af` §1–§2: every recommended option, except Q13 (b), Q15 (b) and Q17 (b) per the addendum |
| O-7 | `s4-amendment-draft/OWNER_DECISION_O1_O7.md` | absolute reading of l.276–278 |

"l.n" means a line of `protocols/protocol_v1.yaml` v1.0, unless another file
is named.

## C-0 Common definitions

- **Window.** The eligible confirmation window is `[w0, w1)`. `w0` is
  `partitions.confirmation.start` at 00:00 UTC, and `w1` is the first excluded
  day at 00:00 UTC; for C2, `w1` = 2025-06-01T00:00Z. (The D-06 record calls
  these `s` and `e`. They are renamed here because `s` is the signal in C-10;
  FA5-12.) "Day" means a complete
  UTC day. [D-06 P6-2]
- **Legs.** The candidate leg is the trial. The benchmark leg is
  `VOL_TARGET_BUY_AND_HOLD` on the same symbol, cost multiplier and day index.
  Unless stated otherwise, a run is the baseline run at 1x cost under the
  event contract C-6.
- **Code bindings.** The code paths named in this annex bind to that code at a
  hash fixed under `<<OPEN D-20>>`, as DRAFT §2.0 R-8 says. (FA5-10)
- **Sharpe.** Sharpe is the scaled Sharpe of a daily return series, with the
  n−1 variance convention, as in `review/task12/IMPLEMENTATION_CONVENTIONS.md`.
  The code binding is `<<OPEN D-20>>`. A series with zero variance or fewer
  than 2 observations has no Sharpe. [D-08 §1; D-07 P7-2]
- **Estimands.** [D-01]
  - `E-IMPROV` = Sharpe(candidate) − Sharpe(benchmark).
  - `E-DIFF` = Sharpe(candidate − benchmark).
  - Both are registered estimands. Every reported paired number names which
    one it is.
- **Drawdown condition `DD(asset)`.** It holds iff
  `MDD(candidate) − MDD(benchmark) ≤ 0.05`. Here `MDD` is the nonnegative
  maximum-drawdown fraction of the leg's equity path over the window
  (`src/aqt/metrics/descriptive.py` `max_drawdown`), and the difference is
  absolute: 0.05 means 5 percentage points. [O-7]
- **Outcomes.** A gate's result is `PASS`, `FAIL`, `N/A` or `UNAVAILABLE`.
  - `N/A` exists only where this annex fixes it at preregistration.
  - "Not computed" and "technically invalid" both mean `UNAVAILABLE`, and the
    cause code is assigned under Annex A P18-7.
  - Nothing is dropped, repaired or imputed (Constitution §6).
- **Numerics.** The exact float64 result of the reference implementation
  decides every comparison. [D-05; D-07 P7-2; D-10; D-18. The extension to
  the other gates is an AI default (SA5-6).]

## C-1 G-1: BTC paired confidence interval (l.274–275) [D-03]

`PASS` iff the lower bound of the two-sided 90% paired block-bootstrap
confidence interval of BTC `E-IMPROV` is `> 0`, computed by the existing
paired-CI routine (`statistics.py:591–651`; binding `<<OPEN D-20>>`). The
result is `UNAVAILABLE` if the routine returns any unavailability reason,
including these:
- either leg has no Sharpe on the window;
- block-length selection fails, for example with fewer than 16
  observations;
- any of the 2,000 replicates is invalid.

[derived; FA5-13, SA5-5]

## C-2 G-2: BTC drawdown (l.276–278) [O-7]

`PASS` iff `DD(BTC)` holds on the baseline run.

## C-3 G-3: ETH sanity (l.42–44, 279) [D-02; N-3]

`PASS` iff ETH `E-IMPROV` (point estimate) `> 0` AND `DD(ETH)` holds, both
on the ETH baseline run at 1x cost. The whole rule is at 1x.

## C-4 G-4: paired fold win rate (l.201–204, 280–282) [D-06, D-07]

1. **Blocks.** Block `k` is `[B_k, B_{k+1})`. `B_k` is the date `3k`
   calendar months after `w0`, computed from `w0` directly and never chained.
   A day that does not exist in the target month is clipped to that month's
   last day. Every boundary is at 00:00 UTC.
2. **Complete blocks.** A block is complete iff `B_{k+1} ≤ w1`. The final
   partial block, if any, is excluded from the rate. Its statistic is
   reported only (Constitution §7a); if it cannot be computed, the report says
   so.
3. **Observation.** One day of the BTC paired series at 1x cost, with both
   legs on shared timestamps.
4. **Integrity.** A missing, duplicated, irregular or non-finite day inside a
   complete block makes the gate `UNAVAILABLE`.
5. **Win.** A complete block is a win iff its `E-IMPROV > 0`. Exactly 0 is
   not a win. **A block in which either leg has zero variance counts as not a
   win.**
6. **Rate.** `PASS` iff `wins / n ≥ 0.60`, where `n` is the number of
   complete blocks. If `n = 0`: `UNAVAILABLE`. No separate block minimum is
   set; `T_min` governs.

## C-5 G-5: 2x-cost stress (l.283) [D-02; N-3, addendum]

On a re-run in which the BTC candidate and the **BTC benchmark both run at
2x cost**, `PASS` iff all of the following hold:
- BTC `E-IMPROV > 0`;
- BTC candidate net return `> 0`;
- `DD(BTC)` holds;
- G-3 passes, with the ETH rule evaluated entirely at 1x. **ETH is not run
  at 2x.** This keeps the 2026-09-15 decision.

## C-6 Event contract [D-15 Q19, Q10 (b); N-4 Q20 (iii)]

**Scope.** The contract governs gate, stressed and null runs.
- N-4 (exits to 0, held exposure drifting) and Q10 (the clock anchor) were
  decided for every run, baseline and benchmark included.
- Applying the **rest** of this contract to baseline and benchmark runs was
  recorded but never presented to the owner (addendum).
  - It covers same-instant fills, atomic fills, the 00:00 band tested against
    drifted exposure, decision-time direction, the clamp, and the unset-clock
    rule.
  - That application is `<<OWNER O-8>>` (FA5-2, SA5-1).

1. **Time.** Timestamps are instants, and close(t) = open(t+1). An order
   stores an absolute target exposure.
2. **Fills are atomic.** Every fill updates the position, equity and held
   exposure together, and the clock where (5) says so.
3. **Held exposure** = position value / equity. It drifts with price between
   fills.
4. **At each hourly instant, in order:**
   1. Execute due fills at the open(t+1) price.
   2. Evaluate the decision against held exposure:
      - At 00:00 UTC, a change requires `|target − held| ≥` the declared band.
        The declared band is the l.112 value, 0.10 (l.97). [AI default; FA5-16]
      - The direction of the order is classified now, at decision time, by
        comparing target with held exposure.
      - An increase is allowed only at 00:00, and only if the clock shows at
        least 24 h or is unset. An unset clock permits the first increase.
        [AI default; FA5-16]
      - At any hour, a reduction requires the target to be at least the band
        below held exposure.
      - **A reduction to target 0 is never blocked by the band, at any
        hour.** [N-4]
   3. A passing decision creates an order. At baseline, it fills at this same
      instant at the open(t+1) price. Under execution stress, it is due at
      the next instant.
   4. At the window end, unfilled orders are dropped.
5. **Clamp and clock.**
   - Eligibility is decided at decision time and is never re-judged.
   - A reduction order fills at `min(order target, held exposure at fill)`, so
     it never fills as an increase.
   - An increase order fills as ordered.
   - The clock is set only at the fill of an order that actually raised held
     exposure, and it is **anchored at that order's 00:00 decision time**.
     [Q10 (b)]
6. **Amended frozen text.** This contract amends l.57 and l.60 (l.113 keeps its scalar value; its meaning follows l.57), plus
   `specs/BACKTESTER_SPEC_v1.md` l.9–l.10 and
   `specs/CANONICAL_BENCHMARKS_v1.md` l.11–l.12 (DRAFT_WORDING §1a).
   Disclosed consequence: with decision-time anchoring and the clamp, the
   24 h clause never binds for daily decisions.

## C-7 G-6 feature delay, G-7 execution delay (l.267–268, 284–285) [D-15]

1. **G-7 (execution delay).** Every BTC candidate order is due one instant
   later (C-6 step 4.3). The BTC benchmark leg is delayed in the same way.
2. **G-6 (feature delay).**
   - At decision instant `t`, every market-data input of the strategy takes
     its value as of `t − 1h`: the last emission at or before `t − 1h`. This
     covers:
     - the direct inputs of `s`;
     - the model's input features;
     - the inputs of `σ̂`;
     - every price or return the overlay reads.
   - `s`, `σ̂`, model outputs and overlay outputs are recomputed from the
     lagged inputs.
   - Model outputs are re-inferred at the model's own emission times, and the
     decision uses the last output at or before `t`.
   - The following are not lagged:
     - refits and training data;
     - labels;
     - decision times;
     - execution;
     - slippage inputs;
     - held exposure;
     - the clock;
     - the overlay's own position state;
     - the BTC benchmark leg.
   - The one-clock-hour cutoff gives coarser inputs a phase-dependent delay.
     This is accepted. A missing or non-finite lagged input makes the gate
     `UNAVAILABLE`.
3. **ETH** runs entirely at baseline in both gates. [addendum, Q15 (b), Q17 (b)]
4. **Pass rule (survival), for each gate on its stressed run.** `PASS` iff:
   - BTC `E-IMPROV > 0`;
   - BTC candidate net return `> 0`;
   - `DD(BTC)` holds;
   - G-3 passes.

   No limit on degradation is applied.

## C-8 G-8: parameter plateau (l.260–265, 286) [D-04, D-05]

**Dimensions.** The ordered numeric tunable dimensions are those defined by
the frozen inclusion rule, l.254–262. [derived; FA5-14]

`v` is the selected trial's BTC `E-IMPROV`. A neighbour is a point at ±1 step
in an ordered numeric tunable dimension that is **present in the declared
grid**. `m` is the median of the present neighbours' `E-IMPROV`, pooled across
dimensions; with an even count, it is the mean of the two middle values.
Evaluate in order:

1. If there is no ordered numeric tunable dimension: `N/A`.
2. If `v`, or any present neighbour's `E-IMPROV`, is not finite: `UNAVAILABLE`.
3. If `v ≤ 0`: `FAIL`.
4. Otherwise `PASS` iff `m ≥ 0.5·v` AND the selected point lies on no boundary
   of any ordered numeric tunable dimension; otherwise `FAIL`.

## C-9 G-10: PBO (l.234–241, 288) [D-08, D-09, D-10]

1. **Matrix.** Each declared trial's daily BTC `E-DIFF` series (the
   column `X_j` of Annex B), on the window's identical ordered day index.
   **l.240's `ranking_metric` is `E-DIFF`.**
2. **Blocks.** The `T` days form 16 chronological blocks. Remainder days go to
   the earliest blocks.
3. **Splits.** All 12,870 splits into 8 in-sample (IS) blocks and 8
   out-of-sample (OOS) blocks.
4. **Score per split.**
   - Find the IS-best trial by Sharpe.
   - Compute its OOS midrank `r` and `omega = r/(N+1)`.
   - The score is 1, 0.5 or 0 according as `logit(omega)` is < 0, = 0 or > 0.
   - On an exact IS-best tie, the score is the uniform average over the tied
     trials.
5. **Result.** `phi` = the mean score. `PASS` iff `phi ≤ 0.30`.
6. **Availability.** The gate is `UNAVAILABLE` unless `T ≥ 16` and every trial
   has a Sharpe on every IS and OOS half. No trial is omitted. There is no
   per-block minimum.
7. **Enablement.** "Family trials ≥ 20" (l.235) means the declared count
   `|J_f|`; re-runs and lifetime counts do not count. Below 20, the gate is a
   frozen `N/A`.

## C-10 G-11: random-exposure null (l.134–140, 289) [D-14]

1. **Declared mapping.** Each trial declares, in its hashed interface,
   `target_h = overlay( clip( s_h · τ / σ̂_h, 0, 1 ), own path state )`, where:
   - `s_h ≥ 0` is computed only from market data and the trial's declared
     model outputs;
   - `τ ∈ {0.40, 0.60, 0.80}` (l.127);
   - `σ̂_h` is restricted to `EWMA_168h` (l.115) or, in the vol family, one
     of l.121, annualised as in CANONICAL_BENCHMARKS l.23;
   - the overlay may only keep the target or set it to 0. It may not set or
     rescale size, and re-entry follows `s`.
   - Whether `s` may depend on `σ̂`: `<<OWNER REG-2>>`.
   - Whether a fixed-size rule can be registered, for example the owner's
     fixed 10%: `<<OWNER REG-1>>`. In this form a fixed size is written
     `s_h = 0.10·σ̂_h/τ`, so it is expressible only if REG-2 allows `s` to
     depend on `σ̂`. (SA5-2, correcting rev 1)
   - Both questions were left open by the D-14/D-15 addendum.
2. **Class.** Each trial declares `g11_class ∈ {signal_timed,
   constant_signal}`.
   - The engine checks in every run that a `constant_signal` trial's `s` is
     identical at every hour. A mismatch makes the gate `UNAVAILABLE`, with
     reason `CLASS_MISMATCH`.
   - **`constant_signal` trials, with or without an overlay, are a frozen
     `N/A`.**
3. **Shifts.** `g` = `gap_embargo.value_days`, and `m = max(g, 30)`.
   - The 500 shifts `k_i` are drawn without replacement from
     `{m, …, T − m}` days, from the trial seed (l.266) with purpose
     `"random_exposure_null"`. The sampling mechanics are `<<OPEN D-20>>`.
   - The gate is available only if `T − 2m ≥ 499`.
4. **Draw `i`.**
   - Use `s_((h + 24·k_i) mod 24T)` in place of `s_h`.
   - Re-size with the trial's own `σ̂_h` at the real hour.
   - Re-run the declared overlay on the draw's own path, under C-6.
   - Every run starts at `w0` with exposure 0, no pending order, an unset clock
     and a fresh overlay state.
   - Warm-up may read the `g` gap days. The wrap is an ordinary day boundary,
     and it is reported.
5. **Statistic.** BTC `E-IMPROV` at 1x, against the shared benchmark leg.
   Each draw's realised mean exposure and turnover are reported, not matched.
   This rewords l.137's "match".
6. **Availability.** The gate is `UNAVAILABLE`, with a reason code, no
   replacement and the denominator kept at 500, if:
   - any `s_h` is non-finite or negative;
   - any `σ̂_h` is non-finite or ≤ 0;
   - any pre-clip product is non-finite;
   - any day is incomplete;
   - the statistic is unavailable for the candidate or for any draw.
7. **Pass rule.** `PASS` iff at least 476 of the 500 draws are strictly below
   the candidate. If all 500 tie: `FAIL`.
8. **Disclosed.**
   - Overlay timing is never tested by G-11.
   - Variance timing inside `s` is credited.
   - The 30-day floor has no empirical basis.
   - No error rate is claimed.

## C-11 G-12: effective decisions (l.242–244, 290) [N-1]

1. **Series.** The nominee's BTC OOS daily net returns at 1x cost, candidate
   leg only, with one decision per day.
2. **Formula** (Task 12). With `h = ceil(H/24)`, where `H ∈ {24, 72, 168}`
   is the declared horizon:
   - Bartlett weights with `L = min(n−1, max(h−1, floor(4·(n/100)^(2/9))))`;
   - `ESS = clamp(n·γ0/Ω, 1, n)`;
   - for an otherwise valid constant series, the fallback `n/h`.
3. **Unavailability.** A non-constant series that rounds to `γ0 = 0` is
   `UNAVAILABLE`. The governed caller checks complete days and
   `H ∈ {24, 72, 168}`, and maps every validation exception to `UNAVAILABLE`.
4. **Pass rule.** `PASS` iff `ESS ≥ 120`. Report the raw decisions, `h`, the
   ESS and the method (Constitution §23).
5. **CPCV switch.** The same definition feeds the CPCV switch at l.216. The
   role of CPCV is `<<OPEN D-13>>`.

## C-12 G-14: shuffled-labels null (l.141–145, 289) [N-2 (a)]

1. **Applicability.** The gate is mandatory for trials that fit a model of
   the vol-scaled target (l.103–105). For every other trial it is a frozen
   `N/A`, fixed at preregistration from the hypothesis fields (l.97).
2. **Rows.** BTC, one per 00:00 UTC decision, taken from the trial's own
   walk-forward (l.198–200) after purge and embargo (l.205–214).
3. **Null label.**
   - After purge and embargo, within each training window's retained rows,
     the label sequence is circularly shifted.
   - The offset is drawn per draw and per window. It lies in
     `[horizon_days, window_length − horizon_days]`.
4. **Refit.** The whole label-dependent pipeline is refitted at the same
   `parameter_point`, with no retuning.
5. **Seeds.** Model seeds and offsets come from a stream seeded by the trial
   seed (l.266), with purpose `"shuffled_labels_null"`, per draw and per
   window. The binding is `<<OPEN D-20>>`.
6. **Statistic.** The Spearman IC, with midranks, over all OOS rows in the
   window whose target realisation also lies inside the window.
7. **Pass rule.**
   - `PASS` iff at least 476 of 500 null ICs are strictly below the nominee's
     IC. Ties count as not below.
   - A constant prediction or a constant target, for the nominee or any draw:
     `UNAVAILABLE`.
8. **Model classes.** These are set in DRAFT §2.5 (FA5-15).
9. **No error rate is claimed.**

## C-13 Accepted consequences (informative)

- **Not covered by the bound.** The false-promotion bound covers only the
  `E-DIFF` DSR claim. Every gate here is a filter with no calibrated error
  rate of its own.
- **Gates that cannot fail, and gates that can be avoided.**
  - G-12 cannot fail on windows longer than 839 days.
  - G-14 can be avoided by not fitting a target model.
  - Overlay timing and constant-signal trials go untested by G-11.
- **Effect of cash.** A quarter held entirely in cash counts as a loss in G-4.
- **Workload for D-19.** D-19 must compute every gate per replication, or the
  amendment must authorise a certification route (DRAFT_WORDING §4).
  - G-11 needs 500 re-runs per nominee.
  - G-14 needs 500 refits per nominee.
- **Seeds.** The G-1 bootstrap, the G-11 shifts and the G-14 offsets use
  streams from the l.266 trial seed, which the public beacon does not
  protect. A declarer could vary that seed with cosmetic hypothesis edits
  before the post, and check the effect offline. (FA5-6)
- **Review.** No statistician reviewed any of this.
