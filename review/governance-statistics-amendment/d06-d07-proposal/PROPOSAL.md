# D-06, D-07 proposal (revision 1): reporting blocks for the paired fold win rate

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting
work, under the owner's instruction "let agent do the answers all the time".
D-rows are decided only by the owner, after two different-model reviews
(R19-2).
**Why now:** gate G-4 (`paired_fold_win_rate >= 0.60`, protocol l.280–282) is
blocked by D-06 and D-07 (§4 draft rev 4, §3). Its availability counts toward
`U_proc`, so it must be defined before D-19 (FA3-12).

## 1. What is missing

Frozen text:
- l.201 `reporting_fold_months: 3`
- l.202–204 "final_partial_reporting_block: excluded_from_paired_fold_win_rate_but_reported_separately … Avoids changing the denominator with a shorter fold."
- l.280–282 `paired_fold_win_rate: {minimum: 0.60, unit: "complete_3_month_reporting_blocks"}`

The text names neither:
- where blocks start (anchoring),
- what makes a block "complete",
- how many blocks are needed,
- what counts as a "win".

D-06 is the block definition. D-07 is the per-block statistic.

## 2. Proposal

**P6-1 Observation.** One complete UTC day of the BTC OOS series, as defined in
`review/task12/IMPLEMENTATION_CONVENTIONS.md` ("Daily observations and
Sharpe"). Both legs (candidate and `VOL_TARGET_BUY_AND_HOLD`) share timestamps.

**P6-2 Anchoring: blocks start at the eligible window's first day.** Block `k`
(k = 0, 1, …) covers `[s + 3k months, s + 3(k+1) months)`, where `s` is the first
day of the eligible window (`partitions.confirmation.start` in the §4 draft).
"+ n months" keeps the day of month; if that day does not exist, the boundary
is the first day of the following month. Reason: the frozen text expects only
a **final** partial block (l.202). Anchoring at calendar quarters would also
create a partial **first** block whenever `s` is not a quarter start, which
the text does not provide for. For C2, `s` is 2022-01-01 plus the gap embargo
(R-3).

**P6-3 Complete block.** A block is complete if its whole calendar span lies
inside the window. The last block, which runs past the window end, is the
"final partial block": it is excluded from the rate and its statistic is
reported separately (l.202–204).

**P6-4 Missing days do not shrink a block.** If any day inside a complete block
is not a valid daily observation, the gate is `UNAVAILABLE`. The block is not
dropped and the day is not repaired: Constitution §6 forbids silent deletion
or correction, and l.204 forbids changing the denominator. (The Task 12 rules
already reject such a series as a whole.)

**P6-5 Minimum blocks.** The rate needs at least `<<D19: B_min>>` complete
blocks; otherwise the gate is `UNAVAILABLE`. D-19 sets `B_min` together with
`T_min`, so that every eligible window has at least `B_min` complete blocks
and this rule never fires on an eligible window. [AI default: `B_min = 4`
as a floor.] For C2, the window is about 1,219 days after a gap of at most 28
days (1,247 days in total), which gives about 13 complete blocks.

**P7-1 Per-block statistic (D-07): `E-IMPROV`.** For each complete block:
the scaled Sharpe of the candidate minus the scaled Sharpe of the benchmark,
over that block's days. This follows D-02/D-03 (decided), as the matrix
proposed.

**P7-2 Win.** A block is a win iff its `E-IMPROV > 0`. Exactly 0 is not a
win. If either leg's Sharpe in a block is unavailable (zero variance, not
finite), the gate is `UNAVAILABLE` (fail-closed; no block is dropped).

**P7-3 Rate.** wins / complete blocks; `PASS` iff `>= 0.60`.
13 blocks need 8 wins (8/13 = 0.615; 7/13 = 0.538).

## 3. Alternatives considered

- **Calendar-quarter anchoring.** Easier to read, and aligned across cycles.
  But it creates a partial first block, which the frozen text does not
  handle; excluding it would be a second, unwritten exclusion.
- **Dropping blocks with missing days.** Rejected: it changes the
  denominator, against l.204 and §6.
- **`E-DIFF` per block.** Rejected for coherence with D-02/D-03 (decided).

## 4. Consequences

- **C-1 Availability (`U_proc`).** A block where the candidate never trades
  can have a zero-variance candidate leg (for example, flat at a fixed
  exposure that tracks the benchmark exactly, or a cash leg). That makes G-4
  `UNAVAILABLE`. D-19 must measure how often this happens, including
  sparse-trading strategies.
- **C-2 Power.** About 13 blocks of 3 months, each with roughly 90 days, give
  a noisy per-block Sharpe. Under no edge, each block is a win about half
  the time, so the gate alone passes about 29% of the time at 13 blocks
  (binomial, assuming independent blocks; `UNVERIFIED` for dependent
  returns). It is a consistency filter, not an error-controlled test, like
  the other `E-IMPROV` gates (D-01..D-04 decision).
- **C-3 Wording.** P6-2..P7-3 are a definition of frozen terms, not a change of
  meaning. The matrix marks D-06 as `STAT` and D-07 as `STAT` (no `§4`
  needed). The §4 draft gate G-4 would carry the text as its definition.

## 5. Proposed owner question (after the reviews)

"D-06/D-07: For the 'fold win rate' check (at least 60% of 3-month blocks
must favour the strategy), define the blocks like this:
- they start on the first day of the eligible data window;
- only the last block can be partial, and it is reported but not counted;
- a block with any missing day makes the check unavailable rather than being
  dropped;
- a block counts as a 'win' when the strategy's Sharpe beats the benchmark's
  over that block.

Accept this, or keep blocked? Nothing is activated."

## 6. Next

[AI default] Two different-model reviews, adjudication, then the owner's
question.
