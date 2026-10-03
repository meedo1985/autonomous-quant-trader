# D-18 proposal (revision 2): selection rule and primary error event

**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). AI proposal only; closes no
D-row, accepts no method, amends no frozen file.
**History:** revision 1 (`690fa97`) was reviewed by Fable 5.1
(`FABLE_REVIEW_690FA97.md`, UNSOUND as written) and Sol High
(`SOL_REVIEW_690FA97.md`, SOUND WITH FIXES); adjudication
`ADJUDICATION_690FA97.md`. Revision 1's selection rule (top DSR) was chosen by
the owner on an incorrect description by the author (FR-4) and has been
re-asked.

## 0. Owner directions (2026-10-03, re-asked after the reviews)

Quoted as asked; answers are the owner's selections. These are directions for
this write-up, not the D-18 decision (R19-2: reviews, then owner decision).

| Question | Answer |
|---|---|
| "D-18 selection rule (re-asked; my earlier description was wrong). Which strategy may be submitted?" | **"Top Sharpe, no fallback"** (other option: "Top DSR score, no fallback") |
| "Protocol line 74 allows a second 'replacement candidate' per family. Use it?" | **"Never use it"** (other: "Keep it") |
| "There are two strategy families per cycle (trend, volatility). What should the 5% noise limit cover?" | **"Whole cycle"** (other: "Each family separately") |
| "When is the pick made?" | **"Once, at a fixed time"** (other: "Allow checks during the cycle") |

## 1. Problem (DEC-02)

`HUMAN_DECISION_MATRIX.md:65` marks D-18 BLOCKING with no candidate: the
maximum-Sharpe trial need not have the maximum DSR score, so "the max-Sharpe
trial passes" and "some trial passes" are different events
(`../DSR_CALIBRATION_RECONCILIATION.md` DEC-02). Frozen
`protocols/protocol_v1.yaml:251` says "submitted candidate is one grid point"
without saying which; line 74 allows two lockbox evaluations per family per
cycle ("One primary and one replacement candidate").

## 2. Proposed rule

- **P18-1 Look time.** Each family `f` (trend, volatility) has exactly one
  nomination look, at its close: when its trial budget is exhausted or the
  cycle's 180 calendar days end, whichever is first. No nomination at any
  other time. The trial universe `J_f` is every trial of family `f` registered
  in the current cycle by that look. (FR-1, SR-3)
- **P18-2 Availability.** `A_f` = every trial in `J_f` has an available, finite
  paired-difference Sharpe and DSR score. If `A_f` fails, nothing is nominated
  from `f`, and the family result is `UNAVAILABLE`. Non-finite values are
  converted to unavailable before any maximum is taken. (SR-1, FR-7, FR-8)
- **P18-3 Nomination.** On `A_f`, the nominated trial `J_f*` is the trial with
  the highest full-precision paired-difference Sharpe estimate (the same
  quantity whose expected maximum `S0` models), ties broken by the lowest
  registered trial id. Nomination depends only on that Sharpe vector and the
  trial ids. "Nominated trial" is used instead of "candidate", which §0
  reserves for a hypothesis that has passed eligibility. (FR-5, FR-8, FR-9, SR-4, SR-6)
- **P18-4 No fallback, no replacement.** Only `J_f*` may proceed. If it fails
  any gate, family `f` has no promotable trial this cycle; no other trial of
  `f` is nominated, and the line 74 replacement allowance is not used.
  "No promotable trial" does not by itself end the cycle; frozen
  `cycle_termination` (lines 192–195) still governs. (FR-3, SR-5)
- **P18-5 Primary error event.** Under the all-zero-mean global null,
  `E_f = A_f ∩ { DSR(J_f*) >= 0.95 }`, and the cycle event is
  `E = E_trend ∪ E_vol`. Calibration must show `P_0(E) <= 0.05`; a sufficient
  route is `P_0(E_f) <= 0.025` for each family. Replications where `A_f` fails
  stay in the denominator as non-events; the availability rate is calibrated
  and accepted separately. (FR-2, SR-1, SR-3)

## 3. Why this bounds false promotion

A promotion from family `f` requires `A_f`, nomination of `J_f*`, and
`DSR(J_f*) >= 0.95`, plus every other gate `H_f`. Hence
`F_f = E_f ∩ H_f ⊆ E_f` and, across the cycle, `F ⊆ E_trend ∪ E_vol = E`.
Under the global null every promotion is false, so
`P_0(false promotion in the cycle) <= P_0(E) <= P_0(E_trend) + P_0(E_vol)`.

The bound follows from requiring the nominated trial to pass DSR; it does not
come from the no-fallback rule (FR-4). No fallback and no replacement instead
ensure every downstream gate (intervals, null percentile, lockbox) is applied
once, to one trial fixed in advance, so each keeps its single-test meaning.

Compared with nominating the top-DSR trial: `E_S ⊆ E_DSR` for each family
(if the top-Sharpe trial clears 0.95 then the maximum DSR does), strictly in
some cases (Fable Example 3). Top-Sharpe therefore passes no more null
families, at some loss of power: a family fails when its top-Sharpe trial
misses 0.95 even though another trial would clear it. Unlike top-DSR,
`DSR(J_f*) >= 0.95` is not the same event as "some trial clears 0.95"; the
calibration targets `E_f` itself.

## 4. Open items (for reviewers and the owner)

- **O18-1 Null.** Only the all-zero-mean global null is claimed. No bound is
  claimed for mixed nulls; mixed-null challenge cells use the event
  {nominated trial has non-positive true mean and passes every gate}. (FR-6, SR-2)
- **O18-2 Availability under lifetime counts.** With the owner's lifetime
  count (`../d16-d17-proposal/OWNER_CHOICE_CANDIDATE_COUNT.md`) and the method
  candidate's equal-count support (DEC-01), any abort or prior-cycle attempt
  may make `A_f` fail permanently. To bind with AS-3 and P-7. (FR-7)
- **O18-3 Lifetime.** `E` is per cycle. The lifetime count raises the hurdle
  but is not shown to bound the lifetime probability over repeated cycles
  (Astra review `../d16-d17-proposal/ASTRA_REVIEW_597DDC8.md:208`). (FR-11)
- **O18-4 Threshold versus 2.5%.** Frozen `dsr.minimum` is 0.95. Whether
  `P_0(E_f) <= 0.025` holds at that threshold is for calibration; changing
  the threshold would be a D-19/amendment matter.
- **O18-5 Calibration cells.** The DEC-02 baseline generator is Gaussian and
  independent, where top-Sharpe and top-DSR almost always coincide. Option C
  needs qualifying non-Gaussian, correlated cells. (FR-12)
- **O18-6 Gate list.** The gates `H_f` are listed from protocol lines 90–91
  and 270–292 in the amendment text; "OOS/IS ratio" has no frozen threshold.
  (FR-10)
- **O18-7 PBO.** PBO is a family-level filter ranked by `paired_delta_sharpe`
  (line 240), consistent with top-Sharpe nomination; it adds a conjunct and
  does not break the bound. (FR-5, SR-5)
- **O18-8 Amendment scope.** Adoption needs the owner-authored Constitution
  section 4 amendment for the successor cycle C2, covering lines 74, 192–195
  and 251, together with D-16, D-17, D-19 and the other blocking rows. Any code
  implementing this is section 16 protected. (FR-3, SR-5)
- **O18-9 Matrix and order.** `HUMAN_DECISION_MATRIX.md:65` lists `STAT` as
  D-18's authority (superseded by R19-2) and says D-18 requires D-16. The
  definition of `E` does not depend on D-16; its calibration does. Owner to
  confirm deciding D-18 first. (FR-13, FR-14)

## 5. Next

Re-review of this revision by the same two model families (R19-2), records
committed, then the owner's D-18 decision. Calibration design (option C)
waits for D-18.
