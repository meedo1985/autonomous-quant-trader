# D-18 proposal (revision 4): selection rule and primary error event

**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). AI proposal only; closes no
D-row, accepts no method, amends no frozen file.
**History:** revision 1 (`690fa97`): Fable UNSOUND, Sol SOUND WITH FIXES,
adjudication `ADJUDICATION_690FA97.md`. Revision 2 (`ffbedad`): Fable
`FABLE_REVIEW_FFBEDAD.md` UNSOUND, Sol `SOL_REVIEW_FFBEDAD.md` SOUND WITH
FIXES, adjudication `ADJUDICATION_FFBEDAD.md`. Revision 3 (`8ff7316`): Fable
`FABLE_REVIEW_8FF7316.md` UNSOUND, Sol `SOL_REVIEW_8FF7316.md` UNSOUND,
adjudication `ADJUDICATION_8FF7316.md`. Revision 1's selection rule was
chosen on an incorrect description by the author (FR-4) and was re-asked.

## 0. Owner directions (2026-10-03)

Directions for this write-up, not the D-18 decision (R19-2: reviews, then
owner decision). Questions and option descriptions are quoted as shown;
**bold** is the owner's selection. (FR2-13)

### Round 2 (after the revision 1 reviews)

1. "D-18 selection rule (re-asked; my earlier description was wrong). Which strategy may be submitted?"
   - **"Top Sharpe, no fallback"** — "Only the best raw-Sharpe strategy is checked; if it fails, the cycle has no candidate. Lets the fewest no-edge strategies through; matches PBO and the penalty formula. Cost: a cycle can fail even when another strategy would pass."
   - "Top DSR score, no fallback" — "Only the best adjusted-score strategy. Slightly more chance of finding a real edge, but more noise also gets through at the same bar; needs its own calibration."
2. "Protocol line 74 allows a second 'replacement candidate' per family. Use it?"
   - **"Never use it"** — "One submission per family. Every later check (lockbox etc.) is used once and keeps its meaning. Written into the amendment."
   - "Keep it" — "Two tries per family; calibration must cover both tries together, so each try faces a higher bar."
3. "There are two strategy families per cycle (trend, volatility). What should the 5% noise limit cover?"
   - **"Whole cycle"** — "Chance that noise passes in either family is held to 5% in total (e.g. 2.5% each). Stricter per family."
   - "Each family separately" — "5% per family, so up to ~10% per cycle that noise passes somewhere."
4. "When is the pick made?"
   - **"Once, at a fixed time"** — "One look, when the family's trial budget is used up or the cycle's 180 days end. No peeking mid-cycle."
   - "Allow checks during the cycle" — "Can stop early on a pass, but every look is another chance for luck; the bar must rise to cover all looks."

Two descriptions shown in round 2 were later found inaccurate by the
reviewers: "Lets the fewest no-edge strategies through" holds for the DSR
stage only (FR2-5, SR2-6), and "keeps its meaning" holds only for the lockbox
(FR2-6, SR2-5). The round-2 "Whole cycle" choice was made without the
feasibility consequence (FR2-2); round 3 question 3 re-asked it with that
consequence.

### Round 3 (after the revision 2 reviews)

1. "Researchers see each strategy's results during the cycle, so they could stop adding strategies after a lucky one (in a simple model this raises the chance noise passes from ~0.2% to as much as ~9%). How do we stop that?"
   - **"Declare all up front"** — "Every strategy of a family is listed and frozen before the first one is tested; nothing can be added later. Simple, needs no change to how results are shown. Cost: no adapting the plan mid-cycle."
   - "Hide results until the pick" — "Researchers can add strategies but see no per-strategy results until the fixed pick. Needs an amendment to the result-sharing rule (§7a)."
   - "Allow stopping, raise the bar" — "Keep flexibility; calibration must cover every possible stopping point, so the bar gets stricter for everyone."
2. "The cycle can end early (a promotion, a protocol revision, or an invalidation) before the other family gets its pick. What happens then?"
   - **"One shared pick at cycle end"** — "Both families are picked together, once, when both budgets are used up or day 180 arrives. No promotion before that. Simplest; cost: a good result waits until the cycle closes."
   - "Unpicked family just loses" — "Each family keeps its own pick time; a family that never got its pick counts as 'no candidate'. Faster, but adds stopping rules the calibration must cover."
3. "You chose a 5% total noise limit for the whole cycle. The reviewers showed the current 0.95 bar can't meet it in some cases (a family with one strategy: ~5% alone; very similar strategies: ~4.25% per family). What now?"
   - **"Keep 5% total, stricter bar"** — "Calibration sets a per-family bar tight enough (about 2.5% each) in every case. Promotion gets harder; changing the 0.95 bar is part of the amendment."
   - "Keep 0.95, exclude hard cases" — "Forbid one-strategy families and near-duplicate strategies; 0.95 stays. Narrower research, and a rule about what counts as near-duplicate is needed."
   - "5% per family instead" — "0.95 may stay; up to ~10% chance per cycle that noise passes in one of the two families."
4. "If a strategy's score can't be computed (crash, missing data), the family is 'unavailable'. A method that is almost always unavailable would look perfectly safe but be useless. Set a limit?"
   - **"At most 1% unavailable"** — "Calibration must show the method gives a result in at least 99% of no-edge test runs, or it does not qualify. This is the limit already proposed in earlier records (DEC-02)."
   - "At most 5% unavailable" — "Looser; easier for the method to qualify, but more cycles may end with no answer."

Round-3 corrections found by the reviewers: in question 3, "very similar
strategies: ~4.25%" understated the worst case (two near-identical strategies
reach ~5.07% at 0.95; a 2.5% cap needs `z_crit` of about 1.972 before margins,
FR3-4). In question 4, the 1% limit was proposed in DEC-02 only for 16 simple
Gaussian equal-count cells; realistic cells are refused by the current method
(FR3-2). Round 4 re-asked both consequences. Revision 3 also wrote the pick
trigger differently from the round-3 answer (SR3-1); round 4 re-asked it.

### Round 4 (after the revision 3 reviews)

1. "Later cycles test on the same history the researchers already saw, so re-declaring last cycle's lucky strategies can make noise pass 34-87% of the time. How should later cycles be protected?"
   - **"Only unseen data can promote"** — "The guarantee covers a cycle only when its confirmation data has never been seen by any earlier cycle (e.g. new months of market data). Cycles on already-seen data can research but never promote. Strict and simple; promotion after cycle 1 waits for fresh data."
   - "Hide results across cycles" — "Researchers never see per-strategy confirmation results, in any cycle. Needs an amendment to the result-sharing rule (§7a) and makes research blinder."
   - "Ban re-declaring old winners" — "A rule forbidding re-use of earlier strategies. Reviewers warn near-copies can slip past it, so the protection is weak."
2. "The current scoring method refuses to score realistic cases (near-identical strategies, correlated or fat-tailed returns), so the 1% 'almost always gives a result' limit can't be met. What now?"
   - **"Broaden the method"** — "Extend the scoring method so it handles correlated and fat-tailed strategies (crypto returns are fat-tailed). More design work and more reviews before calibration, but the guarantee would then cover real data."
   - "Narrow the claim" — "Keep the method; those cases are 'unsupported' and refused at declaration where detectable. Faster, but real crypto strategies may often be refused, so cycles may never produce a result."
   - "Loosen the 1% limit" — "Allow more 'no result' outcomes. Doesn't fix the refusals; a method that rarely answers could still qualify."
3. "When exactly is the shared pick? (I wrote this differently from the option you chose; re-asking.)"
   - **"Declared plan done, or day 180"** — "Pick when every strategy you declared up front has been tested, or at day 180. Since nothing can be added after declaring, waiting longer gains nothing."
   - "Both 81-trial budgets used, or day 180" — "What you chose last round. If fewer than 81 strategies are declared per family, the budget is never used up, so the pick always waits until day 180."
4. "The 1% 'no result' limit: per family, or for the whole cycle?"
   - **"Whole cycle"** — "At most 1% chance that either family gives no result (cycles ending before the pick also count as 'no result'). Matches your whole-cycle 5% choice."
   - "Per family" — "1% each, so up to ~2% chance per cycle that one family gives no result."

## 1. Problem (DEC-02)

`HUMAN_DECISION_MATRIX.md:65` marks D-18 BLOCKING with no candidate: the
maximum-Sharpe trial need not have the maximum DSR score, so "the max-Sharpe
trial passes" and "some trial passes" are different events
(`../DSR_CALIBRATION_RECONCILIATION.md` DEC-02). Frozen
`protocols/protocol_v1.yaml:251` says "submitted candidate is one grid point"
without saying which; line 74 allows two lockbox evaluations per family per
cycle ("One primary and one replacement candidate").

## 2. Proposed rule

Estimand: E-DIFF, the BTC candidate-minus-benchmark paired OOS return series;
`S` is its unannualized daily Sharpe (`METHOD_CANDIDATE.md:96`). D-08 must
adopt E-DIFF for the PBO alignment in O18-6. (FR2-7, FR2-8, FR3-8)

- **P18-0 Promotion eligibility (unseen data).** A cycle may nominate and
  promote only if its confirmation data has never been seen by any earlier
  cycle: no per-trial confirmation metric over any part of that window was
  returned to research before this cycle's declaration (§7a line 92), and no
  exposed lockbox data rolled into it (protocol line 96, Constitution §7
  line 81). A cycle on already-seen data may research but has no pick and
  cannot promote. Because frozen partitions are fixed (protocol lines 65–67),
  promotion after the first cycle needs a new, never-seen confirmation window,
  defined by amendment. (FR3-1)
- **P18-1 Declared trial set.** Before the first evaluation of the cycle, each
  family `f` (trend, volatility) declares its complete trial set `J_f` (every
  hypothesis and grid point), frozen by hash. The declaration is valid only if
  `1 <= |J_f| <= 81`, trial ids are unique and stable, and every trial carries
  a complete immutable configuration hash and belongs to `f`; this is checked
  before the cycle starts, and an invalid declaration prevents the cycle from
  starting. No trial may be added, removed, replaced or rerun later; an
  evaluation must match its declared hash or it is a technical failure. A
  declared trial counts from `EVALUATION_STARTED` (Constitution §0 line 13,
  §9 line 102); a declared trial crashed or never started by the pick makes
  `A_f` fail. (FR2-1, FR2-9, SR3-3, FR3-7)
- **P18-2 One shared pick.** There is exactly one nomination look per cycle,
  for both families together, at the earlier of: every declared trial of both
  families has finished evaluation, or day 180. No promotion is possible
  before it. The amendment must define the window after the pick for the
  nominees' gates, lockbox read and attestation (protocol line 300), the order
  in which two nominees are processed, and cycle termination once both are
  processed, resolving the conflict with `cycle_termination` lines 192–195. If
  the cycle ends before the pick (protocol revision, invalidation), there is
  no pick and no promotion, and that cycle counts as **no result** against
  the availability target (P18-7). (SR2-1, FR-1, SR3-1, SR3-2, FR3-6)
- **P18-3 Availability.** `A_f` = for every trial in `J_f`: finite `S`, valid
  `T`, finite positive `D`, and (with a finite shared `S0`) finite pre-Φ `z`.
  The value `Φ(z)` is never used as an availability test. If `A_f` fails,
  nothing is nominated from `f` (family result `UNAVAILABLE`); one unavailable
  non-nominee blocks the family, which matches DEC-02 and is a deliberate cost
  (FR2-12). (SR-1, FR-7, FR3-5, SR3-6)
- **P18-4 Nomination.** On `A_f`, the nominated trial `J_f*` is the trial with
  the highest `S`, ties broken by lowest declared trial id; nomination depends
  only on the `S` vector and the ids. The reference implementation's exact
  float64 result decides near-ties, and the implementation must agree with
  the reference on the nominee's identity exactly (extends
  reconciliation lines 118–119). (FR2-10, SR-4)
- **P18-5 No fallback, no replacement.** Only `J_f*` may proceed. If it fails,
  or any gate is `UNAVAILABLE` or technically invalid, family `f` has no
  promotable trial this cycle; no other trial is nominated, and the line 74
  replacement allowance is not used. A technical failure is never a reason to
  nominate or re-read another trial. (FR-3, SR-5, SR2-8)
- **P18-6 DSR comparison.** The DSR pass test compares the pre-Φ statistic
  `z_f* = (S − S0)·sqrt(T−1)/sqrt(D)` (`METHOD_CANDIDATE.md:92`) of the
  nominee with **one global** decimal threshold `z_crit`, as `z_f* >= z_crit`
  in the reference implementation, with `z_crit` parsed from its decimal
  string to the nearest binary64; implementation and reference must agree on
  this pass/fail decision exactly. `z_crit` is fixed before qualification,
  analytically or from development replications only, then certified on
  held-out replications at that frozen value; if certification fails, there
  is no re-tuning against the same held-out set. It replaces
  `dsr.minimum: 0.95` (protocol lines 231, 287) by amendment. Known lower
  bound: about 1.972 before margins (FR3-4). (SR2-2, FR2-2, FR3-3, FR3-5, SR3-4)
- **P18-7 Error and availability targets.** Under the all-zero-mean global
  null, `E_f = A_f ∩ {z_f* >= z_crit}` and `E = E_trend ∪ E_vol`. The
  calibration must show, in **every** preregistered qualifying cell, at a
  preregistered simultaneous confidence level covering every cell, family and
  bound:
  - a one-sided upper bound of `P_0(E_f) <= 0.025` for each family (so
    `P_0(E) <= 0.05` for any dependence between them); and
  - a one-sided upper bound `<= 0.01` on the **whole-cycle** no-result rate:
    either family `UNAVAILABLE`, or no pick (P18-2).

  A method failing either does not qualify; error control cannot pass on
  unavailability. No-result replications stay in the denominator as
  non-events; `P_0(E_f | A_f)` and the reach-pick rate are also reported.
  (FR2-2, FR2-3, FR2-4, SR2-3, SR2-7, SR3-2, SR3-5)

## 3. Why this bounds false promotion

A promotion from `f` requires an eligible cycle (P18-0), the shared pick,
`A_f`, nomination of `J_f*`, `z_f* >= z_crit`, and every other gate `H_f`.
Hence `F_f ⊆ E_f` and `F ⊆ E_trend ∪ E_vol = E`; under the global null every
promotion is false, so
`P_0(false promotion in the cycle) <= P_0(E_trend) + P_0(E_vol) <= 0.05`.
Within an eligible cycle, `J_f` is fixed before any result on that cycle's
confirmation data exists (P18-0, P18-1) and the pick happens once, so each
calibration cell is a fixed design; no stopping rule enters `E`. The bound is
a statement, at the preregistered confidence, over the qualifying cells; it
covers a realised cycle only if that cycle's design is dominated by some
qualifying cell, which cannot be fully checked at declaration. (FR3-1, FR3-10)

The bound comes from requiring the nominee to pass DSR, not from the
no-fallback rule (FR-4). No fallback and no replacement limit discretionary
repetition and lockbox use; the lockbox, on fresh data, is applied once. The
selected-point interval, null percentile and plateau are still post-selection
quantities on confirmation data and do not have single-test coverage
(e.g. 81 null trials: a nominal 90% interval excludes zero after max-Sharpe
selection with probability 1−0.95^81 ≈ 98.4%). (FR2-6, SR2-5)

Compared with nominating the top-DSR trial: for the **DSR stage only**,
`E_S ⊆ E_DSR` (strictly in some cases, Fable Example 3). The full promotion
events are not nested, because the two rules can nominate different trials
with different plateau and interval results. (FR2-5, SR2-6)

## 4. Open items

- **O18-1 Null.** Only the all-zero-mean global null (E-DIFF) is claimed.
  Mixed-null challenge cells use the event {nominee has non-positive E-DIFF
  mean and passes every gate}; no bound is claimed. (FR-6, SR-2, FR2-8)
- **O18-2 Broadened method (owner direction, round 4).** The current method
  candidate refuses duplicates, dependent or heavy-tailed trials and lifetime
  mismatch (DEC-02 lines 88–91, 113–115; DEC-01), so it cannot meet the 1%
  no-result target on the realistic grid of O18-4; with the owner's lifetime
  count (`../d16-d17-proposal/OWNER_CHOICE_CANDIDATE_COUNT.md`), any abort or
  prior-cycle attempt makes `A_f` fail. The owner chose to broaden the method
  so it handles correlated and fat-tailed trials. That is a method
  specification change (D-16/D-17, AS-3, P-7: `K=1`, `V=0`, `K<N`), proposed
  and reviewed separately; calibration cannot be designed until it exists.
  The DEC-02 qualifying/challenge classification must be revised to match.
  (FR-7, SR2-3, FR3-2)
- **O18-3 Lifetime.** `E` is per eligible cycle. P18-0 removes reuse of seen
  confirmation data; no bound over the number of eligible cycles is shown
  (Astra `../d16-d17-proposal/ASTRA_REVIEW_597DDC8.md:208`).
- **O18-4 Calibration grid (D-19).** The qualifying cells must include
  one-trial and two-trial families, high within-family correlation (e.g. grid
  siblings differing only in `vol_target`; the worst known cell is two
  near-identical trials), duplicates and opposites, unequal clusters and `T`,
  serial and cross-trial dependence, heavy tails and unequal moments, and a
  joint two-family generator sharing the BTC benchmark days. A deterministic
  classifier maps each declared family design to a qualifying cell; designs
  outside every cell are refused at declaration. Seeds, custody, replication
  budget, the simultaneous confidence construction and a no-rescue stopping
  rule belong to the D-19 preregistration; the DEC-02 per-cell
  `U_error <= 0.05` record needs revising to 0.025. (FR2-2, FR2-3, FR2-11,
  SR2-4, FR3-4, SR3-4)
- **O18-5 Gate list.** The amendment enumerates every `H_f` component from
  protocol lines 90–91 and 270–292 with its `PASS`/`FAIL`/`N/A`/`UNAVAILABLE`
  behaviour, including PBO enablement (20 trials, line 235); "OOS/IS ratio" has
  no frozen threshold. (FR-10, SR2-8)
- **O18-6 PBO.** PBO ranks by `paired_delta_sharpe` (line 240), consistent with
  top-`S` nomination if D-08 adopts E-DIFF. (FR-5, FR2-7)
- **O18-7 Amendment scope.** Owner-authored Constitution §4 amendment for C2
  covering protocol lines 65–67 (a never-seen confirmation window for later
  cycles), 74, 192–195, 231, 251, 287, 300 and the declared-trial-set,
  shared-pick and eligibility rules (which constrain §8 hypothesis
  registration timing), together with D-16, D-17, D-19 and the other blocking
  rows. Code implementing it is §16 protected (promotion gate).
- **O18-8 Matrix and order.** `HUMAN_DECISION_MATRIX.md:65` still lists `STAT`
  (superseded by R19-2); "D-18 requires D-16" is at
  `HUMAN_DECISION_MATRIX.md:79`. The definition of `E` does not depend on
  D-16; `z_crit` and the calibration do. Owner to confirm deciding D-18 first.
  (FR-13, FR-14, FR3-9)

## 5. Next

Re-review of revision 4 by the two model families (R19-2), records committed,
then the owner's D-18 decision. The broadened method (O18-2) is the next
design task; calibration design (option C, D-19) follows it.
