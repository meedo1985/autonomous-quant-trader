# D-05 proposal (revision 1): the plateau rule when the selected value is ≤ 0

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting
work, under the owner's instruction "let agent do the answers all the time".
The D-row is decided only by the owner, after two different-model reviews
(R19-2).
**Why now:** D-04 is decided as `E-IMPROV`
(`../d02-d04-proposal/OWNER_DECISION_D01_D04.md`). Under `E-IMPROV`, the
nominee chosen by `E-DIFF` can have a selected plateau value ≤ 0, so the
inversion is live (proposal rev 2, C-4). Gate G-8 is blocked until D-05 is
decided (§4 draft rev 4, §3).

## 1. The defect

Frozen rule (protocol l.263–265): if there is no ordered numeric tunable
dimension, the gate is `N/A`. Otherwise it passes iff "median available-neighbor
BTC OOS paired-delta-Sharpe >= 0.5 * selected-point value AND selected point is
not on a boundary of any ordered numeric tunable dimension".

With `v` the selected point's `E-IMPROV` (D-04) and `m` the median of its
neighbours:

- `v > 0`: neighbours must keep at least half of a positive improvement.
  This is the intended meaning (l.265 "Rejects isolated numeric peaks").
- `v = 0`: the condition is `m >= 0`.
- `v < 0`: `0.5·v > v`, so neighbours must be **better** than the selected
  point (`TECHNICAL_APPENDIX.md` §3). The rule then rewards a selected point
  that is worse than its neighbours, which is the opposite of its purpose.

## 2. Options (matrix row D-05)

| Option | Rule when `v <= 0` | Effect |
|---|---|---|
| (a) fail | G-8 = `FAIL` | No isolated "peak" exists to protect, and the gate fails closed |
| (b) unavailable / N/A | G-8 = `UNAVAILABLE` (or `N/A`) | `UNAVAILABLE` counts toward `U_proc` (P18-7), whose bound is 1%; `N/A` would let a non-positive nominee skip the gate |
| (c) restate on a sign-invariant scale | e.g. `m >= v − 0.5·|v|` | A new rule with a new meaning, which needs its own justification |
| (d) leave as written | inversion | Incoherent with the rule's own justification |

## 3. Recommendation: (a) fail when `v <= 0`

Proposed wording for the amendment (G-8): "If no ordered numeric tunable
dimension: `N/A`. Otherwise `PASS` iff the selected-point value `v` (BTC OOS
`E-IMPROV`) is > 0 AND the median available-neighbour value is >= `0.5·v` AND
the selected point is not on a boundary of any ordered numeric tunable
dimension; otherwise `FAIL`."

Reasons:

1. **It keeps the rule's stated meaning.** "Rejects isolated numeric peaks"
   presupposes a positive peak. A non-positive selected value has no
   improvement for a plateau to protect.
2. **It changes almost no promotion outcome.** A nominee with `v <= 0` has a
   point estimate of `E-IMPROV` at or below zero. G-1 requires the lower 5%
   percentile endpoint of the bootstrap `E-IMPROV` to be > 0
   (`statistics.py:591–660`). That endpoint lies above a non-positive point
   estimate only if the bootstrap distribution is shifted well above the
   estimate, which is unusual but not impossible (bootstrap bias). So under
   (a), G-8 almost always fails exactly where G-1 already fails.
   `UNVERIFIED`: D-19 can report how often the two disagree.
3. **It adds nothing to `U_proc`.** `FAIL` is a result, not unavailability.
   (b) would add a `U_proc` event for every non-positive nominee. Under the
   global null, that is close to half of all nominees, which would make the
   1% target unreachable.
4. **(c) is not needed.** Any sign-invariant restatement invents a new
   threshold for negative values, where the gate cannot pass G-1 anyway.
5. **(d) is incoherent** (§1).

## 4. Costs and consequences

- **C-1 It is a change of rule meaning**, so it needs §4 amendment wording.
  The draft gate list G-8 would carry the wording above.
- **C-2 `v = 0` exactly** fails under (a). That boundary has probability near
  zero for continuous returns.
- **C-3 The other half of the rule is unchanged.** The boundary condition and
  the frozen `N/A` case (no ordered numeric tunable dimension, l.264) stay as
  written. So does the neighbour inclusion rule (l.260–262).
- **C-4 Neighbour values can be unavailable.** If a neighbour's `E-IMPROV` is
  not finite, the median over "available" neighbours uses the rest. If none
  is available and an ordered numeric dimension exists, the gate is
  `UNAVAILABLE`, and that counts toward `U_proc`. This is not new; it is the
  frozen "available" wording, and D-19 must measure it.

## 5. Proposed owner question (after the reviews)

"D-05: When the selected strategy's own improvement over the benchmark is
zero or negative, the plateau check as written turns upside down: it would
require the neighbouring settings to be better than the selected one.
Should the check simply fail in that case? (a) fail [recommended]; (b) count it
as unavailable, which would make your 1% no-result target very hard to meet;
(c) invent a new rule for negative values; (d) leave as written; or keep it
blocked. Nothing is activated."

## 6. Next

[AI default] Two different-model reviews of this proposal (Fable 5.1 and
Codex `gpt-5.6-sol` high), then adjudication, then the owner's question.
