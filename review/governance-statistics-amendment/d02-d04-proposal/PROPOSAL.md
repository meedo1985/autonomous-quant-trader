# D-02, D-03, D-04 proposal (revision 1): which estimand the paired gates use

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting work,
done under the owner's instruction "let agent do the answers all the time".
D-rows are decided only by the owner, after two different-model reviews (R19-2).
**Why now:** under the §4 draft (`../s4-amendment-draft/DRAFT_WORDING.md` rev 4,
§6 step 1, FA3-12), the rows that govern gate availability must be decided
before D-19 is frozen. D-02, D-03 and D-04 govern gates G-1, G-3, G-5 and G-8.

## 1. The question in plain terms

Several frozen gates test a "paired delta-Sharpe" between the candidate and
the benchmark `VOL_TARGET_BUY_AND_HOLD`. There are two different numbers with
that name (`../external-review-packet/TECHNICAL_APPENDIX.md` §1–§3):

- **`E-IMPROV`** = Sharpe(candidate) − Sharpe(benchmark): "is the candidate's
  risk-adjusted return better?"
- **`E-DIFF`** = Sharpe(candidate − benchmark), the Sharpe of the daily
  difference series: "does the candidate add return over the benchmark,
  relative to how noisy that addition is?"

Neither can be computed from the other (appendix §2, §2.1). They can disagree
in sign on the same data. A candidate that gives up a little return for much
less volatility (a "de-risker") has `E-IMPROV > 0` but `E-DIFF < 0` (appendix
§3).

| Row | Gate(s) | Frozen text |
|---|---|---|
| D-02 | G-3 ETH sanity (protocol l.42–44, 279); G-5 survive 2x cost (l.283) | `paired_delta_sharpe_point_estimate > 0` |
| D-03 | G-1 BTC paired 90% CI, lower bound > 0 (l.274–275) | `btc_min_sharpe_delta_ci_lower_bound: 0.0` |
| D-04 | G-8 parameter plateau (l.263–265) | "median available-neighbor BTC OOS paired-delta-Sharpe >= 0.5 * selected-point value" |

## 2. What changed since the matrix recommendation

`HUMAN_DECISION_MATRIX.md` recommended `E-IMPROV` for all three rows before
D-18 existed. Since then:

- **D-18 (decided)** nominates each family's trial with the highest `E-DIFF`
  Sharpe and tests it with the `E-DIFF` DSR (P18-4, P18-6).
- **D-18 O18-6** requires D-08 (PBO) to adopt `E-DIFF`.

So the selection rule and the DSR already use `E-DIFF`. The question is
whether the remaining paired gates should follow it, or keep testing
`E-IMPROV`.

## 3. Recommendation: `E-IMPROV` for D-02, D-03 and D-04

1. **The frozen words.** "delta-Sharpe" (l.43, 275, 279, 283, 264) most
   naturally reads as a difference of two Sharpe ratios. Choosing `E-IMPROV`
   changes no frozen word. Choosing `E-DIFF` means reading the words against
   their plain sense.
2. **The project's stated purpose.** Constitution §12: vol management is
   "de-risking, not alpha". Protocol l.93–95 removed the net-return tolerance
   because "a de-risker may legitimately trail on absolute return while
   improving risk-adjusted behavior". `E-IMPROV` is the quantity those clauses
   describe.
3. **An estimator already exists.** `paired_sharpe_improvement_interval`
   (`src/aqt/metrics/statistics.py:591`) targets `E-IMPROV`, with block length
   from the improvement influence function (l.325). It is inactive, and it
   would need its own D-20 review before use.
4. **`E-DIFF` would make G-1 nearly redundant.** A DSR pass already needs
   `S − S0 >= z_crit·sd`, with `S0 > 0` the expected null maximum. A 90% CI on
   the nominee's `E-DIFF` Sharpe whose lower bound must be > 0 needs only
   `S >= 1.645·sd`, roughly. For a family with `K >= 2` and `z_crit` near 2,
   the DSR bound is the tighter of the two, so G-1 would almost never decide
   anything (heuristic, `UNVERIFIED`; D-19 can measure how often the two
   disagree). Under `E-IMPROV`, G-1 tests a different claim.
5. **It does not loosen the error bound.** D-18 defines the false-promotion
   event by the DSR pass alone (`E_f = A_f ∩ {z_f* >= z_crit}`). Every other
   gate is an extra filter, so its estimand cannot raise `P_0(E_f)`. What it
   can change is availability (`U_proc`) and power (§4).

## 4. Costs and consequences the owner should know

- **C-1 Promotion requires both kinds of edge.** Under D-18 plus this
  proposal, a nominee must have the best `E-DIFF` in its family, pass the
  `E-DIFF` DSR, **and** pass the `E-IMPROV` gates. A pure de-risker
  (`E-IMPROV > 0`, `E-DIFF <= 0`) still cannot be promoted: it fails the DSR.
  That is a consequence of D-18, not of this row. It is disclosed here because
  it narrows what the project can find. Choosing `E-DIFF` here would not
  change it.
- **C-2 Availability.** `E-IMPROV` needs both legs, each with a finite,
  positive-variance Sharpe. The benchmark leg is the same for every trial, so a
  degenerate benchmark makes every nominee unavailable. D-19 must report the
  availability of G-1 (the interval and its block length) for each nominee
  (P18-7, `U_proc`).
- **C-3 Two estimands, one report.** Results must label every paired number
  as `E-IMPROV` or `E-DIFF` (D-01 option (a), naming only). This proposal
  assumes D-01 (a). D-01 is itself a `STAT` row and is listed for the owner
  together with these rows.
- **C-4 Plateau sign defect.** Under `E-IMPROV`, the plateau rule still
  inverts when the selected value is ≤ 0 (appendix §3). That is D-05, which
  stays open and blocks G-8.
- **C-5 Rows that follow.** D-07 (fold statistic) follows D-02 once D-06
  defines the fold unit. The lockbox components L-2 and L-4 and the D-12
  sign field depend on D-11, whose frozen construction stores only the
  difference series, so it can produce only `E-DIFF` (appendix §7). If
  pre-lockbox ETH sanity (G-3) uses `E-IMPROV` while lockbox ETH sanity (L-4)
  can use only `E-DIFF`, the two checks of the same idea disagree in meaning.
  D-11 must either supply both legs or record the difference explicitly.

## 5. The alternative: `E-DIFF` everywhere

Its strength is one estimand throughout, matching D-18 and D-08. Its costs:
it reads "delta-Sharpe" against its plain sense; it makes G-1 nearly redundant
(§3 point 4); it discards the existing estimator, and a CI would have to come
from the Annex B bootstrap, which needs its own review; and it measures
additive return rather than the de-risking the Constitution names. It is a
coherent choice, not a wrong one.

## 6. Proposed owner question (after the reviews)

"D-01 to D-04: name the two estimands separately (D-01), and use `E-IMPROV`
(Sharpe of candidate minus Sharpe of benchmark) for the ETH sanity, 2x cost,
BTC confidence-interval and plateau gates (D-02, D-03, D-04)? The DSR and the
choice of nominee keep using `E-DIFF` as you decided in D-18. Nothing is
activated."

## 7. Next

[AI default] Two different-model reviews of this proposal (Fable 5.1 and Codex
`gpt-5.6-sol` high), then adjudication, then the owner's question.
