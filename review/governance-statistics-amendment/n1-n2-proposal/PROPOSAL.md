# N-1, N-2 proposal (revision 2): the effective-decisions gate and the shuffled-labels null

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting
work, done under the owner's instruction "let agent do the answers all the
time". N-1 and N-2 are proposed **new** decision rows. Adding them to the
matrix is the owner's act, and they are decided only by the owner after two
different-model reviews (R19-2).

**History:**
- Revision 1 (`f8da1b0`) was reviewed by Fable (`FABLE_REVIEW_F8DA1B0.md`,
  FQ1, SOUND WITH FIXES) and Sol (`SOL_REVIEW_F8DA1B0.md`, SQ1, SOUND WITH
  FIXES).
- The adjudication is `ADJUDICATION_F8DA1B0.md`.
- Revision 2 applies every disposition **without a further check** [AI
  default]. That is weaker than a further check, and it is recorded as such.

**Why now:** gates G-12 and G-14 are mandatory pre-lockbox gates. Their
availability counts toward `U_proc` (P18-7).

## 1. N-1: the effective-decisions gate (G-12)

**Frozen text:**
- l.242–244: `newey_west_autocorrelation_adjusted_ESS_on_BTC_OOS_strategy_returns`,
  with the fallback `raw_decisions / ceil(horizon_hours/24)`.
- l.290: `minimum_effective_decisions: 120`.
- l.216: CPCV is enabled at ESS ≥ 250.
- Constitution §23 l.182: reports state raw decisions, the overlap factor,
  and the ESS with its method.

**Proposal N1** binds the Task 12 convention
(`review/task12/IMPLEMENTATION_CONVENTIONS.md`), which was approved for
inactive use only, as the governed definition. Under R19-2 this replaces the
statistician step in decision packet R3 ("never compare with 120"); this
supersession is disclosed (FQ1-10).

- **Series.** The nominee's BTC OOS daily net returns at 1x cost, over the
  eligible window, candidate leg only. "Decisions" is read as one decision
  per complete UTC day, because cycle hypotheses decide at 00:00 UTC. This
  reading is an **interpretation** of `raw_decisions`: a hypothesis declares
  its decision frequency (Constitution l.97), and intraday reductions are
  allowed (l.55, 59) (FQ1-7).
- **Formula** (Task 12):
  - `h = ceil(H/24)`, where `H ∈ {24, 72, 168}` is the trial's declared
    horizon;
  - Bartlett weights with `L = min(n−1, max(h−1, floor(4·(n/100)^(2/9))))`;
  - `ESS = clamp(n·γ0/Ω, 1, n)`.
- **Fallback.** The fallback `n/h` is used for an otherwise-valid constant
  series. The `Ω <= 0` branch is only a numerical guard: exactly, `Ω > 0`
  for any non-constant series (FQ1-8).
- **Unavailability.** A non-constant series that rounds to `γ0 = 0` is
  `UNAVAILABLE` (SQ1-1).
- **Caller duties** (SQ1-1, FQ1-8). The governed caller checks complete UTC
  days and `H ∈ {24, 72, 168}`, and it maps every validation exception to
  `UNAVAILABLE`. The library alone accepts `H = 48` and raises on non-finite
  input.
- **Gate.** `PASS` iff `ESS >= 120`, otherwise `FAIL`.
- **Report** (§23). Raw decisions, the overlap factor `h`, the ESS, and the
  method used.

**The gate cannot fail in C2** (FQ1-1, SQ1-2; exact). For Bartlett weights,
`n(L+1)·Ω` is a sum of squares, and by Cauchy–Schwarz `Ω <= (L+1)·γ0`. So
`ESS >= n/(L+1)` for every series.
- At `n` = 1,219, `L = 6` for all three horizons, so `ESS >= 174.1`.
- G-12 can fail only for windows of **839 days or fewer**.
- If D-19 sets `T_min >= 840`, G-12 is always `PASS` on an eligible window.
- The cause is the fixed Task 12 bandwidth. A data-dependent bandwidth (for
  example, Andrews 1991) would behave differently; that is
  `UNVERIFIED_EXTERNAL_ASSUMPTION`, and it would change the Task 12
  convention.

**The same definition also feeds the CPCV switch at 250** (l.216; FQ1-9,
SQ1-2). There it is **not** inert: at `n` = 1,219, ESS lies anywhere in
(174, 1219]. CPCV is diagnostic-only (l.219–221). Its role is D-13, but its
ESS input is this definition.

**Availability** (FQ1-4). G-12 is available whenever the candidate series is
valid with `n >= 2`, because the fallback covers constant series. This is a
deterministic argument that D-19 may use, if the amendment allows it (§3).

**An all-cash nominee** (FQ1-5) takes the fallback and passes G-12. Among its
other gates:
- G-4 is a `FAIL` (D-07: a zero-variance block is not a win);
- G-9 and G-10 are computable (its `E-DIFF` equals minus the benchmark);
- G-1 and G-11 are `UNAVAILABLE`.

## 2. N-2: the shuffled-labels null (G-14)

**Frozen text:** l.141–145 (500 samples; `gate_metric`: OOS Spearman IC
between the model prediction and the vol-scaled target) and l.289
(`null_minimum_percentile: 0.95`, which is unqualified). Constitution §18
l.161 already requires a shuffled-label null as a **backtester trust test**,
so that canary exists under every option (FQ1-7).

| Option | Rule | Consequence |
|---|---|---|
| **(a) gate for target-predicting trials** [recommended] | `PASS` iff the nominee's IC beats the null by the rule below. The gate is a **frozen `N/A`**, fixed at preregistration from the hypothesis fields (Constitution l.97), for trials that fit no model of the vol-scaled target (l.103–105). | This is the literal reading of `gate_metric` and the unqualified l.289 (FQ1); it is one interpretation, not compelled (SQ1-3). The `N/A` must be written into the §4 text as frozen, otherwise it counts toward `U_proc` like (c) (FQ1-6). A hypothesis can avoid G-14 by not fitting a target model. The frozen `N/A` precedents for gates are G-8 (l.264) and G-10 (l.235). It costs 500 walk-forward refits per nominee, and in D-19 more (§3). |
| (b) canary only | Not a promotion gate. It is reported, and it remains the §18 trust test. | Cheap. It reads l.289 as applying only to the random-exposure null, which the text does not say. |
| (c) gate for every nominee | As (a), with no `N/A`. | A trial with no target model (for example, a volatility forecaster) has no IC, so the gate is `UNAVAILABLE` there and counts toward `U_proc`. |
| keep blocked | — | G-14 stays blocked, and the amendment cannot be signed (draft §6 step 1). |

**Recipe for (a)** (FQ1-2, SQ1-4):
- **Rows.** BTC, one row per 00:00 UTC daily decision. The training and OOS
  rows are those of the trial's own walk-forward (l.198–200), after purge and
  embargo (l.205–214).
- **Null label.** Purge and embargo are applied **first**. Then, within each
  training window's retained rows, the label sequence is **circularly shifted**
  by an offset drawn per draw and per window. A circular shift keeps the
  serial dependence of overlapping 72 h and 168 h labels, which an i.i.d.
  permutation destroys. A permutation's null would be too narrow and would
  pass no-skill models too often (FQ1-3, SQ1-4). The offset is at least the
  horizon in days, and at most the window length minus that.
- **Refit.** The whole label-dependent pipeline is refitted per window, with
  the same `parameter_point`: preprocessing, feature selection, calibration,
  early stopping and the logistic sign objective (l.161). There is no
  retuning.
- **Seeds.** Model seeds and offsets come from a stream seeded from the trial
  seed (l.266), with purpose `"shuffled_labels_null"`, per draw and per window.
  This is new code under §16, and it is a new dependency on D-20 (the
  stream conventions).
- **IC.** Spearman correlation with midranks, over all OOS rows in the eligible
  window whose target realisation also lies inside the window.
- **Pass rule.** `PASS` iff **at least 476** of the 500 null ICs are strictly
  below the nominee's IC. Under ideal exchangeability, that level is 25/501 ≈
  4.99%, whereas "475" gives 5.19% (FN1-4, exact). This rule is stated here
  independently. D-14 is undecided, and the matrix's D-14 row prefers a
  type-7 quantile (FQ1-11).
- **Ties.** Valid ties, for example from intercept-only refits, count as not
  below.
- **Availability.** A constant prediction or a constant target, for the
  nominee or any draw, makes the gate `UNAVAILABLE`. There is no replacement.
- **No error-rate claim.** The shifted-label null is a diagnostic filter. Its
  exchangeability is approximate, so no 5% rate is claimed (SQ1-4).
- **Model classes.** The `allowed_classes_cycle_1` (l.154–155) carry over to
  C2 only if the amendment says so (FQ1-11).

## 3. D-19 must compute every gate (SQ1-5, FQ1-4, FN1-8)

P18-7, as decided, computes every pre-lockbox gate for every simulated nominee,
and an uncomputed gate counts as `UNAVAILABLE`. Several gates need more than the
Annex B return matrix of `E-DIFF` differences:

| Gate | Needs |
|---|---|
| G-1, G-2, G-4 | both legs (`E-IMPROV`) |
| G-3, L-4 | ETH |
| G-5 | a 2x-cost re-run and ETH |
| G-6, G-7 | delayed re-runs |
| G-11 | exposure paths and the backtester |
| G-12 | the candidate leg |
| G-14 | model refits |

D-19 therefore needs a **per-gate input and availability matrix**, and it
must either:
- **(i)** simulate at the level of prices, positions and models, and
  compute every gate in every replication. With option (a) this costs
  500 refits × nominees × replications, which may be infeasible; or
- **(ii)** have the §4 amendment **explicitly authorise** a defined
  certification route for named gates, for example a deterministic
  availability argument like G-12's, and state how it enters the joint 1% bound.

A deterministic assertion is not computation under the current P18-7 wording
(SQ1-5). This choice belongs to the D-19 design and is recorded here.

## 4. Proposed owner questions

1. **N-1** (minimum 120 effective decisions):
   - **Accept** [recommended]. Use the existing, tested formula as a real check.
     It **cannot fail in cycle 2** (it can fail only on windows of 839 days or
     fewer). The same formula also decides when the CPCV diagnostic switches
     on. This lifts the earlier "never compare with 120" caution.
   - **Revise.** Use a data-dependent formula, which changes the tested
     convention.
   - **Keep blocked.** The amendment cannot be signed.
2. **N-2** (shuffled-labels test):
   - **(a)** [recommended]. Required for strategies trained to predict the
     scaled return, and skipped by fixed rule for the others. It must beat at
     least 476 of 500 copies trained on time-shifted labels. It is costly:
     500 retrains per nominee, and more in the calibration. A strategy can
     avoid it by not using a return model.
   - **(b)** A software sanity check only.
   - **(c)** Required for all, and unavailable where there is no model.
   - **Keep blocked.**

Both are filters with no error guarantee of their own. No statistician
reviewed this. Nothing is activated.
