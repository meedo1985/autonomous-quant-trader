# D-08, D-09, D-10 proposal (revision 2): the PBO gate

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting
work, under the owner's instruction "let agent do the answers all the time".
D-rows are decided only by the owner, after two different-model reviews
(R19-2).
**History:** revision 1 `cd1e552`. Reviews: Fable `FABLE_REVIEW_CD1E552.md`
(FB8, SOUND WITH FIXES) and Sol `SOL_REVIEW_CD1E552.md` (SB8, SOUND WITH
FIXES). Both endorse the three recommendations. Adjudication:
`ADJUDICATION_CD1E552.md`. Revision 2 applies every disposition **without a
further check** [AI default]; this is weaker than a further check, and is
recorded as such.
**Why now:** gate G-10 (PBO ≤ 0.30, protocol l.234–241, 288) is blocked by
D-08..D-10. Its availability counts toward the whole-cycle `U_proc` target
(P18-7).
**Authority** (FB8-7, SB8-2): D-08 is `§4` (it amends the wording of l.240).
D-09 is `STAT` then `§4`. D-10 is `STAT`. All three become amendment text for
G-10.

## 1. What PBO does here

PBO (probability of backtest overfitting) asks: if you pick the best trial on
one half of the data, how often does it rank in the bottom half on the other
half? The construction (`../v1.1-method-candidate/METHOD_CANDIDATE.md` §4):

1. split the data into 16 chronological blocks;
2. take all 12,870 ways to choose 8 blocks as in-sample (IS), with the other 8 out-of-sample (OOS);
3. on each split, pick the IS-best trial;
4. score its OOS rank (midranks, `omega = r/(N+1)`, score 1, 0.5 or 0 by the sign of `logit(omega)`);
5. take `phi` = the mean score.

The gate passes iff `phi <= 0.30`.

**Series** (FB8-6): each declared trial's daily `E-DIFF` series on the
eligible window, the same as Annex B's column `X_j`. Every column covers the
identical ordered day index, with the same benchmark, symbol and cost
multiplier (`METHOD_CANDIDATE.md` l.222–224). Sharpe uses the n−1 variance
convention (`statistics.py:173–200`).

## 2. D-08: which measure ranks trials — recommend `E-DIFF`

- **The stored matrix can only produce `E-DIFF`.** It holds differences
  (l.238), and `E-IMPROV` cannot be recovered from differences
  (`TECHNICAL_APPENDIX.md` §2). Ranking by `E-IMPROV` would require storing
  both legs, which changes a frozen input. With a shared benchmark, it would
  also reduce to ranking by the candidate's own Sharpe (Lemma L-1).
- **It uses the same ranking rule as nomination** (FB8-5). D-18 nominates the
  top-`E-DIFF` trial on the full window (P18-4). PBO applies that rule to
  half-length IS sets, and the two orders differ (appendix §4). The DSR series
  (l.228–229) is the same `E-DIFF` series.
- **Status of the D-18 link** (FB8-1, SB8-3). D-18's text says D-08 "must
  adopt E-DIFF" (§2 l.187–188) but also "if D-08 adopts E-DIFF" (O18-6
  l.436–437); this inconsistency is inherited from owner-decided text. D-18
  directs `E-DIFF`, and the D-01..D-04 record lists "PBO (l.240) stays E-DIFF"
  as an accepted consequence. **D-08 is still a separate decision, and it
  needs an owner-signed §4 wording change to l.240.**
- **Alternative (b):** store both legs and rank by `E-IMPROV`. Rejected: it
  changes a frozen input and its schema, it reduces to the candidate's own
  Sharpe, and it no longer measures the selection rule actually used.
- **Predecessor draft** (FB8-8). `DRAFT_AMENDMENT_PROPOSAL.md` l.124–132
  (never accepted) proposed ranking by "paired Sharpe improvement" on a
  "candidate/common-comparison matrix". This proposal departs from that
  draft, for the reasons above.

## 3. D-09: observation unit, minimum length and enablement

- **Unit:** one complete UTC day. Remainder days go to the earliest blocks.
- **Minimum** (SB8-1, FB8-3): `T >= 16` (so every block is non-empty), and
  every trial has a defined Sharpe (finite, `n >= 2`, non-zero variance) on
  every IS and OOS half. Otherwise `phi` is `UNAVAILABLE`, with no trial
  omitted and no imputation. There is no per-block Sharpe minimum, and the
  revision-1 conditional 10-day floor is deleted. D-19 sets `T_min` well above
  16. At the C2 window of about 1,219 days (the D-06/D-07 decision: 1,247 days
  less the gap), each block is about 76 days and each half 608–611 days (FB8).
- **Enablement** (FB8-2). "Family trials ≥ 20" (l.235) is read as the
  declared count `|J_f|` (D-18 P18-1). On `A_f`, every declared trial has
  exactly one completed evaluation, so a re-run does not add to the count
  (SB8). This is an **interpretation**. The supporting reasons: the matrix
  columns are the declared current-cycle trials; Constitution l.67 forbids
  pooling prior-cycle matrices; Constitution l.12 gives a family both
  current-cycle and lifetime accounting; and under B-2 lifetime counts are
  recorded and reported only. The §4 draft's l.61 override, which limits
  lifetime counts to reporting for the DSR, should be extended to PBO
  enablement. Below 20 declared trials, the gate is frozen `N/A`.

## 4. D-10: exact IS ties — recommend uniform average

On an exact IS-best tie, the split score is averaged uniformly over the tied
trials. The alternative is to use the lowest declared trial id, which matches
the tie rule of Annex A P18-4 (and the DSR draft).

- **When the two rules agree** (SB8-4, FB8). They agree when every tied trial
  gets the same OOS score. Exact duplicates always do, because they share
  their OOS midrank. In the exact toy, a duplicate-only tie gives the same
  `phi` under both rules. A **mixed** tie (duplicates plus a different trial
  with the same IS Sharpe) can differ: 5/36 versus 1/12 (SB8, exact).
- **Why averaging.** It does not depend on how trials were named. Under the
  lowest-id rule, renaming moved `phi` from 0 to 1/6 in FB8's exact example,
  while averaging gave 1/12 either way.
- **Why the other rule exists.** D-18 must choose one nominee, so it breaks
  ties by id. PBO is a statistic over splits and does not need to choose.
- An "exact tie" means equal values in the reference implementation's
  float64 result (FB8-6).

## 5. Consequences

- **C-1 Availability (`U_proc`).** If any trial's `E-DIFF` series is zero on a
  whole half, `phi` is unavailable. A trial identical to the benchmark is
  already unavailable under Annex B (`ZERO_VARIANCE_COLUMN`). A sparse column
  that is zero for a whole half is a new route. D-19 must certify these
  routes inside the whole-cycle 1% bound, not merely report them.
- **C-2 What PBO controls** (SB8-5). `phi <= 0.30` has no calibrated error
  rate of its own. It is an extra filter after the DSR, so it cannot inflate
  D-18's false-promotion bound. It can reduce power and add `U_proc` events.
- **C-3 Duplicates move `phi`** (FB8-4). In the exact toy, adding a copy of
  one trial moved `phi` from 7/12 to 1/3. The declared set is therefore a
  lever on `phi`, as it is for the DSR (FB1-15). D-19 PBO cells must include
  families with duplicates and near-duplicates.
- **C-4 Compute.** 12,870 splits × up to 80 trials per family is small.
- **C-5 No statistician** reviewed this (R19-2).

## 6. Proposed owner questions (neutral; FB8-1, SB8-3)

"D-08..D-10, the overfitting check (PBO). It asks how often the best strategy
on half the data does badly on the other half; it must be ≤ 30%.
- **D-08 ranking:** rank strategies by the same measure used to pick the
  nominee (E-DIFF). Your D-18 text points this way, but it is a separate
  decision that needs a one-line rulebook amendment you sign. The alternative
  (better-Sharpe, E-IMPROV) would need data the rules don't store.
  [recommended: E-DIFF]
- **D-09 data:**
  - use daily data;
  - the check is unavailable (counts against your 1% limit), rather than
    dropping a strategy, if any strategy has no usable Sharpe on some half;
  - it switches on at 20 declared strategies, and re-runs don't count;
  - no extra minimum block length.
- **D-10 ties:** when strategies tie exactly, average over them
  [recommended]. Or use the lowest ID (matches how the nominee is picked,
  but renaming strategies can change the result).

Adding duplicate strategies changes the score, so the declared list matters.
The check has no error guarantee of its own. No statistician reviewed this.
Nothing is activated."
