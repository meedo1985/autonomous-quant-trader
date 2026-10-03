# D-01..D-04 proposal (revision 2): which estimand the paired gates use

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting work,
under the owner's instruction "let agent do the answers all the time". D-rows
are decided only by the owner, after two different-model reviews (R19-2).
**History:** revision 1 `5e28376`. Reviews: Fable `FABLE_REVIEW_5E28376.md`
(FE1, SOUND WITH FIXES) and Sol `SOL_REVIEW_5E28376.md` (SE1, SOUND WITH
FIXES); both endorse the recommendation and require fixes to its reasons and
disclosures. Adjudication: `ADJUDICATION_5E28376.md`. Revision 2 applies every
disposition **without a further check** [AI default]; this is weaker than a
further check, and is recorded as such.
**Why now:** under the §4 draft (`../s4-amendment-draft/DRAFT_WORDING.md` rev 4,
§6 step 1, FA3-12), the rows that govern gate availability must be decided
before D-19 is frozen. D-02..D-04 govern gates G-1, G-3, G-5 and G-8, and,
through D-02, the lockbox ETH check L-4 (FE1-6).

## 1. The question in plain terms

Several frozen gates test a "paired delta-Sharpe" between the candidate and
the benchmark `VOL_TARGET_BUY_AND_HOLD`. Two different numbers carry that name
(`../external-review-packet/TECHNICAL_APPENDIX.md` §1–§3):

- **`E-IMPROV`** = Sharpe(candidate) − Sharpe(benchmark). It asks whether
  the candidate's risk-adjusted return is better.
- **`E-DIFF`** = Sharpe(candidate − benchmark). This is the risk-adjusted
  return of the active-return stream: does the candidate add return over the
  benchmark, relative to how noisy that addition is? It is a Sharpe ratio,
  not raw added return (SE1-6).

Neither can be computed from the other (appendix §2, §2.1), and they can
disagree in sign on the same data (appendix §3, reproduced exactly by FE1). A
"de-risker", which gives up a little return for much less volatility, has
`E-IMPROV > 0` and `E-DIFF < 0`. An "exposure tilt", which holds a fixed multiple
`k·b` of the benchmark's position, has `E-IMPROV = 0` and `E-DIFF = S(b) > 0`
(exact, FE1-8).

| Row | Gate(s) decided here | Frozen text |
|---|---|---|
| D-01 | none: a naming act only (register both names) | — |
| D-02 | G-3 ETH sanity (l.42–44, 279); G-5 survive 2x cost (l.283); lockbox L-4 ETH sanity (l.91) | `paired_delta_sharpe_point_estimate > 0` |
| D-03 | G-1 BTC paired 90% CI, lower bound > 0 (l.274–275) | `btc_min_sharpe_delta_ci_lower_bound: 0.0` |
| D-04 | G-8 parameter plateau (l.263–265) | "median available-neighbor BTC OOS paired-delta-Sharpe >= 0.5 * selected-point value" |

**Not decided here** (FE1-10): G-11 random-exposure null (l.137–140, D-14);
CPCV diagnostic (l.221, D-13); `oos_is_ratio` (l.247, frozen on the
difference series); lockbox L-1, L-2 and the D-12 sign field (D-11); PBO
(l.240, already `E-DIFF` under D-18 §2, l.187–188; FE1-12).

## 2. What changed since the matrix recommendation

`HUMAN_DECISION_MATRIX.md` recommended `E-IMPROV` for D-02..D-04 before D-18
existed. D-18 (decided) now nominates each family's trial with the highest
`E-DIFF` Sharpe and tests it with the `E-DIFF` DSR (P18-4, P18-6), and D-18 §2
requires D-08 (PBO) to adopt `E-DIFF`. The question is whether the remaining
paired gates follow `E-DIFF`, or test `E-IMPROV` as a second, different claim.

## 3. Recommendation: `E-IMPROV` for D-02, D-03 and D-04 (and D-01 (a))

Both reviewers endorse this conclusion. The reasons, as corrected:

1. **The words, read in context.** "delta-Sharpe" in the gate clauses most
   naturally reads as a difference of two Sharpe ratios. **Frozen usage is
   mixed** (FE1-1): l.240 (`ranking_metric: "paired_delta_sharpe"` on a
   difference matrix) and l.85 ("delta-Sharpe per path" on difference paths)
   can only mean `E-DIFF`. So either choice reads some frozen uses against
   their context. Choosing `E-IMPROV` gives the token `paired_delta_sharpe`
   two meanings in the protocol, and every report must label which one
   (D-01).
2. **The project's purpose, both sides** (FE1-2). For `E-IMPROV`: l.93–95
   removed the net-return tolerance because "a de-risker may legitimately
   trail on absolute return while improving risk-adjusted behavior". For
   `E-DIFF`: l.229 ("incremental evidence rather than BTC beta"), l.239 ("same
   incremental objective as DSR") and l.247 ("incremental OOS evidence").
   Constitution §1 is neutral between them. The purpose text does not settle it.
3. **It filters exposure tilts** (FE1-8). Nomination and the DSR use
   `E-DIFF`, which can favour a trial that simply holds more of the benchmark
   (`E-DIFF = S(b) > 0`, `E-IMPROV = 0`) whenever the vol-target benchmark runs
   below full exposure. `E-IMPROV` gates reject such a trial; `E-DIFF` gates
   would not. This is the strongest reason.
4. **It tests a different claim from the DSR.** Under `E-DIFF`, G-1 would test
   the same series and the same direction as the DSR, so it would add little
   information. Whether it would often be redundant is **an untested
   hypothesis**: G-1 uses its own block-bootstrap dispersion and percentile
   endpoints, which can be materially wider than the DSR's scale under serial
   dependence (SE1-1, FE1-3). It is not assumed here, and D-19 may report
   how often the two disagree.
5. **What it does to the error bound** (SE1-2, FE1-4). With D-18's nomination
   fixed, no gate's estimand can change `P_0(E_f)` or its upper bound,
   because `E_f = A_f ∩ {z_f* >= z_crit}` contains no other gate. A gate can
   change the actual false-promotion probability `P_0(F_f)` (always ≤ the
   bound), power, mixed-null behaviour, and availability. **The 2.5% / 5%
   bound covers only the `E-DIFF` claim. The `E-IMPROV` gates are filters with
   no calibrated error rate of their own**: computed after selection on a
   correlated statistic, G-1 has no nominal 90% coverage for the nominee
   (D-18 §3), and the all-zero-mean `E-DIFF` null does not fix `E-IMPROV`.

## 4. Costs and consequences

- **C-1 Two objectives, no fallback** (SE1-4, FE1-4). A nominee is chosen by
  `E-DIFF` alone (P18-4). If it then fails an `E-IMPROV` gate, the family has
  no promotable trial this cycle, even if another declared trial would have
  passed, because D-18 forbids fallback (P18-5). This costs power. D-19 power
  and mixed-null cells must report failures gate by gate. A pure de-risker
  still cannot be promoted, because it fails the `E-DIFF` DSR; that is a
  consequence of D-18, not of this row.
- **C-2 Availability is a qualification target, not a report** (SE1-3,
  FE1-5). Under P18-7 every gate is computed for every nominee, and the
  whole-cycle `U_proc` must have an upper bound ≤ 1%, or the method does not
  qualify. G-1 under `E-IMPROV` is `UNAVAILABLE` if either leg has zero
  variance, if block selection fails (fewer than 16 observations), or if any
  of the 2000 replicates is invalid (`statistics.py:644–645`); its frozen
  N/A is "never". Also:
  - (a) Annex B simulates only the difference matrix, so D-19 must also
    simulate a benchmark-leg law. That is an extra nuisance input in the
    frozen qualification object.
  - (b) Both families share the benchmark, so their failures are correlated,
    which matters for the joint cells.
  - (c) `E-DIFF` has its own requirement (a difference series with usable
    variance). Neither availability profile is automatically better.
- **C-3 Two names, one report.** Every paired number is labelled `E-IMPROV`
  or `E-DIFF` (D-01 (a), naming only, binds no gate).
- **C-4 Plateau sign defect is live under `E-IMPROV`** (FE1-7). Under
  `E-DIFF`, a DSR pass forces the plateau's selected value above zero, so the
  D-05 inversion could not affect a promotable nominee (it could still affect
  `U_proc`). Under `E-IMPROV`, the selected value can be ≤ 0 and the inversion
  is live. D-05 stays open and blocks G-8 either way.
- **C-5 Lockbox** (FE1-6, SE1-5). Only L-1's frozen bootstrap construction
  (l.85) is limited to `E-DIFF` (appendix §7). L-4 is the ETH sanity rule
  applied to lockbox data, where both legs exist, so it follows D-02. L-2 and
  the D-12 sign field need explicit D-11 bindings. Line 91 uses
  "delta-Sharpe" twice in one rule (L-1 and L-2); D-11 must say whether both
  uses mean the same thing.
- **C-6 Rows that follow.** D-07 follows D-02 once D-06 defines the fold
  unit. G-8 stays blocked by D-05, and G-4 by D-06. The intervals need D-20
  review under either choice.

## 5. The alternative: `E-DIFF` everywhere

**Benefits** (SE1-6): one estimand throughout, aligned with nomination, the
DSR and PBO; no mismatch between how the nominee is chosen and how it is
tested (C-1 does not arise); the plateau inversion cannot affect a promotable
nominee (C-4); D-19 needs no benchmark-leg model.

**Costs:** it reads the gate clauses' "delta-Sharpe" as the Sharpe of the
difference; it lets exposure tilts through every gate (§3 point 3); G-1 adds
little information beyond the DSR (§3 point 4).

**Implementation is symmetric** (FE1-9). Both point estimators already exist
(`paired_sharpe_statistics`, `statistics.py:218–233`). Both interval routes
need D-20 review: `E-IMPROV` through the inactive Task 12 interval (l.591),
and `E-DIFF` through the same machinery with single-series influence (l.311)
or the Annex B bootstrap. It is a coherent choice, not a wrong one.

## 6. Proposed owner questions (neutral, separate; SE1-7, FE1-11)

1. **D-01:** "Register `E-IMPROV` and `E-DIFF` as two separately named
   measures? This is naming only and binds no gate." Recommendation: yes.
2. **D-02, D-03, D-04:** "For the ETH sanity and 2x-cost checks (D-02), the
   BTC confidence interval (D-03) and the plateau check (D-04): `E-IMPROV`,
   `E-DIFF`, or keep blocked?" Recommendation: `E-IMPROV` for all three,
   because one common choice keeps them coherent. The owner should know:
   - the phrase "delta-Sharpe" then carries two meanings in the protocol;
   - your 5% bound covers only the `E-DIFF` claim, and the `E-IMPROV` checks
     carry no guarantee of their own;
   - a nominee that fails an `E-IMPROV` check cannot be replaced (power cost);
   - D-19 must also simulate the benchmark;
   - G-8 stays blocked by D-05, G-4 by D-06, and the intervals need D-20
     review.

   The alternative (`E-DIFF`) aligns with nomination and the DSR, but lets
   exposure tilts through. Nothing is activated either way.

## 7. Next

The owner's answers, then `OWNER_DECISION_D01_D04.md`. D-05 (plateau sign)
is the natural next proposal, because C-4 makes it live under `E-IMPROV`.
