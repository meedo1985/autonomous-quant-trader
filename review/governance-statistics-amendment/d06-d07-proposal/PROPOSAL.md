# D-06, D-07 proposal (revision 2): reporting blocks for the paired fold win rate

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting work,
under the owner's instruction "let agent do the answers all the time". D-rows
are decided only by the owner, after two different-model reviews (R19-2).
**History:** revision 1 `abcc2c9`. Reviews: Fable `FABLE_REVIEW_ABCC2C9.md`
(FF1, SOUND WITH FIXES) and Sol `SOL_REVIEW_ABCC2C9.md` (SF1, SOUND WITH
FIXES). Adjudication: `ADJUDICATION_ABCC2C9.md`. Revision 2 applies every
disposition **without a further check** [AI default]; this is weaker than a
further check and is recorded as such.
**Why now:** gate G-4 (`paired_fold_win_rate >= 0.60`, protocol l.280–282) is
blocked by D-06 and D-07. Its availability counts toward the whole-cycle
`U_proc ≤ 1%` qualification target (P18-7), so it must be fixed before D-19
(FA3-12).

## 1. What is missing, mapped to the matrix row (FF1-11)

Frozen text:
- l.201: `reporting_fold_months: 3`.
- l.202–204: the final partial block is "excluded_from_paired_fold_win_rate_but_reported_separately … Avoids changing the denominator with a shorter fold".
- l.280–282: `minimum: 0.60, unit: "complete_3_month_reporting_blocks"`.

Constitution §7a l.92 also sends "3-month fold aggregates" from confirmation
to the sandbox (FF1-4). These blocks are those aggregates.

| Matrix D-06 item | Rule |
|---|---|
| fold anchoring | P6-2 |
| UTC completeness | P6-1, P6-4 |
| minimum days | P6-3: a complete block is a full three calendar months, 89–92 days |

D-07 is the per-block statistic: P7-1 and P7-2.

**What kind of rule each is** (FF1-5, SF1-2):
- P6-1, P6-3, P6-4 and P7-3 complete frozen terms.
- P6-2's anchoring, the month convention, the `E-IMPROV` statistic (P7-1) and the tie and zero-variance rules (P7-2) are **candidate bindings**. The frozen text does not fix them, and they become §4 amendment text in gate G-4.

## 2. Proposal

**P6-1 Observation.** One complete UTC day of the BTC OOS paired series at 1x
cost (FF1-6), as defined in `review/task12/IMPLEMENTATION_CONVENTIONS.md`.
Both legs (candidate and `VOL_TARGET_BUY_AND_HOLD`) share timestamps.

**P6-2 Anchoring and month convention** (SF1-1, FF1-8). Let `s` be the
eligible window's first day (00:00 UTC) and `e` the first excluded day
(00:00 UTC). For C2, `e` = 2025-06-01T00:00Z, so the window is `[s, e)`.

Block `k` (k = 0, 1, …) is `[B_k, B_{k+1})`. Each boundary `B_k` is the date
`3k` calendar months after `s`, computed from `s` directly (never chained from
the previous boundary). If that day of the month does not exist, it is clipped
to the last day of the target month. Every boundary is at 00:00 UTC.

Reason for anchoring at `s`: the frozen text expects only a **final** partial
block (l.202). Calendar-quarter anchoring would create a partial first block
whenever `s` is not a quarter start.

For C2, `s` lies between 1 and 30 January 2022, so clipping never applies
(FF1, verified).

**P6-3 Complete and partial blocks** (FF1-7). A block is complete iff
`B_{k+1} <= e`. If `e` falls exactly on a boundary, there is no partial
block. Otherwise the block containing `e` is the final partial block: it is
excluded from the rate, and its statistic is reported separately through
`metrics.json` / `report.md` (§7a). If that statistic cannot be computed (for
example, fewer than 2 days), the report says so, with no effect on the gate.

**P6-4 Data-integrity failures make the gate unavailable.** If a day inside a
complete block is missing, duplicated, irregular or non-finite, the gate is
`UNAVAILABLE`. Nothing is dropped or repaired: Constitution §6 forbids that,
and l.204 forbids changing the denominator. Task 12 already rejects such a
series as a whole, which disables every paired gate (FF1-10). In operation, the
cause code follows P18-7's precedence: an infrastructure or data-feed cause
is `U_ops`; otherwise it is `U_proc`.

**P6-5 Number of blocks** (SF1-3, FF1-9). No separate block minimum is added.
The rate is computed over all complete blocks. If there are none, the gate is
`UNAVAILABLE`. The eligibility minimum `T_min` (A-B7), which D-19 sets, governs
window length. D-19 should note that the no-edge pass rate does not fall
steadily as blocks are added: it is 5/16 at 4 blocks and 1/2 at 5 blocks
(FF1, exact).

For C2: there are exactly **13** complete blocks for every gap from 0 to 29
days (FF1, verified). The gap comes from the declared embargo rule (§4 draft
§2.1); no 28-day cap is assumed (SF1-5).

**P7-1 Per-block statistic (D-07): `E-IMPROV`.** For each complete block: the
scaled Sharpe of the candidate minus the scaled Sharpe of the benchmark, over
that block's days. This follows D-02/D-03 (decided).

**P7-2 Win, ties and zero variance.**
- A block is a win iff its `E-IMPROV > 0`. Exactly 0 is not a win.
- **A block where a leg has zero variance** (in practice, a full quarter spent
  entirely in cash): see the choice in §3. Data-integrity failures remain
  `UNAVAILABLE` (P6-4).
- The reference implementation's float64 result decides.

**P7-3 Rate.** wins / complete blocks; `PASS` iff `wins/n >= 0.60`, which
equals the exact test `5·wins >= 3·n` for every `n < 2000` (FF1). With 13
blocks, 8 wins are needed.

## 3. The open choice: a zero-variance block (FF1-3, SF1-4)

A long-only trend strategy that holds only cash for a whole quarter has a
constant daily return in that quarter, so its Sharpe for that block is
undefined (`statistics.py:179`). The 2022 bear market in the C2 window makes
such a quarter plausible for cautious strategies, not rare (FF1-1). (Rev 1's
example of a strategy "tracking the benchmark exactly" was wrong: such a
strategy still varies with BTC.)

| Option | Rule | Consequence |
|---|---|---|
| (a) unavailable | the gate is `UNAVAILABLE` | One cash quarter blocks the family (no replacement, P18-5), and the event counts toward `U_proc ≤ 1%`. With 13 blocks, a per-block chance of only 0.077% already uses the whole 1% (SF1-4). |
| **(b) non-win** [recommended] | the block counts as not a win | Nothing is dropped, and the denominator is unchanged (l.204). It can only make passing harder, so it never "passes on unavailability" (P18-7). It uses no `U_proc`. **Cost:** a cautious strategy that sits out a crash quarter in cash scores that quarter as a loss, against the spirit of Constitution §12 ("de-risking"). |
| (c) Sharpe 0 for a constant leg | a constant leg counts as Sharpe 0 | Changes the Task 12 convention ("no epsilon floor"), so it is a statistical change, not a definition. |

Recommendation (b). The cost is real but bounded: 8 of 13 wins are still
reachable with up to 5 cash quarters. Option (a) can make the 1% target
unreachable in cells with cash-heavy strategies.

## 4. Consequences

- **C-1 Availability.** After (b), G-4 becomes `UNAVAILABLE` only through a
  data-integrity failure (P6-4) or zero complete blocks. Both are `U_proc`
  routes that D-19 must certify inside the whole-cycle 1% bound; reporting
  them is not enough (FE1-5).
- **C-2 Power and the no-edge pass rate** (SF1-5, FF1-9). If blocks are
  independent and each is won with probability 1/2, passing at 13 blocks has
  probability 2380/8192 = 0.2905. That is an illustration only: "won with
  probability 1/2" needs the two legs to be symmetric (exchangeable) under the
  null, and blocks of serially dependent returns are not independent. G-4 is
  a consistency filter, not an error-controlled test, like the other
  `E-IMPROV` gates. Under (b), cash quarters lower the pass rate further.
- **C-3 Information to the sandbox** (FF1-4). `s` is fixed once before
  declaration, so every trial shares the same block boundaries, and offset
  blocks cannot be differenced to recover finer confirmation returns.
- **C-4 No statistician** reviewed this (R19-2).

## 5. Proposed owner question

"D-06/D-07, the fold win rate check: the strategy must beat the benchmark's
Sharpe in at least 60% of its 3-month blocks. Proposed definition:
- blocks start on the first day of the eligible data window and run three
  calendar months each (day clipped to month end where needed);
- only the last block can be partial; it is reported but not counted;
- cycle 2 has 13 counted blocks, so 8 wins are needed;
- a tie counts as not a win;
- missing or broken data makes the check unavailable;
- no separate minimum number of blocks: the data-window minimum decides.

One choice is needed: a quarter in which the strategy sat entirely in cash
(its Sharpe can't be calculated). Should that quarter count as a loss
(recommended: protects your 1% limit, but is harsh on cautious strategies) or
make the check unavailable (counts against your 1% limit)?

Even a strategy with no edge would pass this check about 29% of the time,
so it is a filter, not a guarantee. No statistician reviewed this.

Options: accept with 'loss'; accept with 'unavailable'; revise; reject; keep
blocked. Nothing is activated."
