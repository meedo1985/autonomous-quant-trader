# D-08, D-09, D-10 proposal (revision 1): the PBO gate

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting
work, under the owner's instruction "let agent do the answers all the time".
D-rows are decided only by the owner, after two different-model reviews
(R19-2).
**Why now:** gate G-10 (PBO ≤ 0.30, protocol l.234–241, 288) is blocked by
D-08..D-10 (§4 draft rev 4, §3). It is mandatory when a family has ≥ 20
trials, and its availability counts toward `U_proc` (FA3-12).

## 1. What PBO does here

PBO (probability of backtest overfitting) asks: if you pick the best trial on
one half of the data, how often does it rank in the bottom half on the other
half? The candidate construction
(`../v1.1-method-candidate/METHOD_CANDIDATE.md` §4) is:

- 16 chronological blocks;
- all 12,870 ways to choose 8 blocks as in-sample (IS), with the other 8 out-of-sample (OOS);
- pick the IS-best trial;
- score its OOS rank;
- `phi` = the mean score.

The gate passes iff `phi <= 0.30`. Three details are open.

## 2. D-08: which measure ranks trials — recommend (a) `E-DIFF`

The stored matrix is "family trial paired-difference return matrix" (l.238),
while the ranking metric is `paired_delta_sharpe` (l.240).

- **The matrix can only produce `E-DIFF`.** A difference matrix cannot
  give `E-IMPROV` (`TECHNICAL_APPENDIX.md` §2). Ranking by `E-IMPROV` would
  mean storing both legs, which changes a frozen input and its schema. With a
  shared benchmark, it also reduces to ranking by the candidate's own Sharpe
  (`METHOD_CANDIDATE.md` Lemma L-1). That contradicts the frozen justification
  "Keeps PBO on the same incremental objective as DSR" (l.239).
- **It matches D-18.** D-18 nominates the top-`E-DIFF` trial (P18-4), and
  D-18 §2 (l.187–188) states that "D-08 must adopt E-DIFF for the PBO
  alignment". PBO then measures the overfitting of the very selection that
  produced the nominee. The ranking order differs between the two measures
  (appendix §4), so this matters.
- **Wording:** l.240 is read as "difference-series Sharpe (`E-DIFF`, D-01)".
  Under D-01, the token `paired_delta_sharpe` here means `E-DIFF`, while the
  gate clauses decided in D-02..D-04 mean `E-IMPROV`. Matrix authority:
  `§4`, because it amends the wording of one clause.

## 3. D-09: observation unit and minimum length — recommend daily, no extra minimum

- **Unit:** one complete UTC day, as for every Sharpe in the project
  (`review/task12/IMPLEMENTATION_CONVENTIONS.md`). Remainder days go to the
  earliest blocks.
- **Minimum:** a Sharpe is computed on each **half** (8 blocks joined), not
  on each block. The rule is: every trial must have a defined Sharpe (finite,
  `n >= 2`, non-zero variance) on every IS and OOS half; otherwise `phi` is
  `UNAVAILABLE`, with no trial omitted and no imputation. No separate block
  minimum is added. D-19's `T_min` sets the length; at `T` of about 1,219
  days, each block is about 76 days and each half about 610 days. [AI
  default: if D-19 sets `T_min` below 160 days, add a floor of 10 days per
  block.]
- **Enablement:** "family trials ≥ 20" (l.235) counts the declared trials
  `|J_f|` (D-18 P18-1). Each has exactly one completed evaluation under
  `A_f`. Below 20, the gate is frozen `N/A`.

## 4. D-10: exact IS ties — recommend (a) uniform average

When two or more trials tie exactly for IS-best, the split score is averaged
uniformly over the tied trials, rather than taken from the lowest trial id.

- **For duplicate trials, both rules give the same `phi`.** In practice exact
  float ties come from duplicate columns (Annex B allows duplicates). Duplicate
  columns also tie out of sample, get the same midrank, and so score the same.
  Averaging and lowest-id therefore agree exactly.
- **For coincidental ties of different trials** (probability near zero),
  averaging does not depend on how trials were named, while lowest-id does.
- **Consistency with D-18:** D-18 breaks nomination ties by the lowest id
  because one trial must be chosen. PBO is a statistic over splits and does
  not need to choose. The two rules serve different purposes, and the matrix
  noted this tension.

## 5. Consequences

- **C-1 Availability (`U_proc`).** A trial that is flat (zero variance in the
  difference) on any half makes `phi` unavailable. Since the benchmark is
  `VOL_TARGET_BUY_AND_HOLD`, a trial identical to the benchmark has a zero
  difference series everywhere. Such a trial is also unavailable under Annex
  B (`ZERO_VARIANCE_COLUMN`), so this adds no new failure. A sparse
  difference column that is zero on a whole half is new, and D-19 must
  measure it.
- **C-2 What PBO is.** `phi <= 0.30` is a filter, not an error-controlled
  test. It is computed on the same window as the DSR. The 2.5% / 5% bound of
  D-18 covers only the DSR event.
- **C-3 Compute.** 12,870 splits × `K` ≤ 80 Sharpe pairs per family. This is
  small.
- **C-4 Wording.** D-08 needs `§4` wording (one clause); D-09 and D-10 are
  definitions (`STAT`).

## 6. Proposed owner question (after the reviews)

"D-08..D-10, the overfitting check (PBO):
- rank trials by the same measure used to pick the nominee (E-DIFF), as your
  D-18 decision already requires;
- measure on daily data, and make the check unavailable rather than dropping
  any trial that lacks a usable Sharpe on some half;
- when two trials tie exactly, average over them (for duplicate trials this
  gives the same answer as picking one).

Accept, or keep blocked? Nothing is activated."

## 7. Next

[AI default] Two different-model reviews, adjudication, then the owner's
question.
