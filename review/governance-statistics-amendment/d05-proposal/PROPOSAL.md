# D-05 proposal (revision 2): the plateau rule when the selected value is ≤ 0

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting
work, under the owner's instruction "let agent do the answers all the time".
The D-row is decided only by the owner, after two different-model reviews
(R19-2).
**History:** revision 1 `e98adb3`. Reviews: Fable `FABLE_REVIEW_E98ADB3.md`
(FP1, SOUND WITH FIXES), Sol `SOL_REVIEW_E98ADB3.md` (SP1, SOUND WITH FIXES).
Both endorse failing an available non-positive value. Adjudication:
`ADJUDICATION_E98ADB3.md`. Revision 2 applies every disposition **without a
further check** [AI default]; this is weaker than a further check and is
recorded as such.
**Why now:** D-04 is decided as `E-IMPROV`, so the nominee (chosen by
`E-DIFF`) can have a selected plateau value ≤ 0. Gate G-8 stays blocked until
D-05 is decided (§4 draft rev 4, §3).

## 1. The defect, stated precisely (FP1-5, SP1-6)

Frozen rule (protocol l.260–265): if there is no ordered numeric tunable
dimension, the gate is `N/A`. Otherwise it passes iff "median available-neighbor
BTC OOS paired-delta-Sharpe >= 0.5 * selected-point value AND selected point is
not on a boundary of any ordered numeric tunable dimension".

Let `v` be the selected point's `E-IMPROV` (D-04) and `m` the median of its
neighbours' values.

- **`v > 0`:** the median must keep at least half of a positive improvement.
  This is the intended meaning ("Rejects isolated numeric peaks").
- **`v = 0`:** the rule becomes `m >= 0`. The idea of "keeping half" no longer
  means anything.
- **`v < 0`:** the median must beat the selected point by at least `0.5·|v|`.
  Worked case (FP1, exact): `v = −2/5`, threshold `−1/5`. A flat plateau
  (`m = −2/5`) fails. An isolated peak (`m = −1`) fails. A valley
  (`m = −1/10`) passes. So below zero the rule rewards a selected point that
  is worse than its neighbours.

## 2. Options, one consequence each (FP1-8, SP1-1, SP1-7)

| Option | Rule when an available `v <= 0` | Consequence |
|---|---|---|
| (a) fail | G-8 = `FAIL` | No positive improvement exists to protect, so the gate fails. This changes the rule's meaning and needs §4 wording. It adds no `U_proc` event. |
| (b1) unavailable | G-8 = `UNAVAILABLE` | Each such nominee is a `U_proc` event (P18-7). How often that happens depends on the null cell (§3 point 3) and could threaten the 1% target. |
| (b2) not applicable | G-8 = `N/A` | The gate is waived for non-positive nominees. P18-7 excepts frozen `N/A` from `U_proc`, but this would be a **new** `N/A` case, which changes gate applicability. |
| (c) sign-aware rule | a separately justified rule for `v <= 0` | Needs its own justification and calibration. |
| (d) leave as written | as §1 | Below zero the gate passes valleys and fails plateaus. |
| keep blocked | — | G-8, and therefore every promotion, stays blocked. |

## 3. Recommendation: (a), with an explicit order of evaluation

**Proposed G-8 wording** (FP1-1, FP1-2, SP1-2, SP1-4, SP1-5), evaluated in order:

1. If there is no ordered numeric tunable dimension: `N/A` (frozen, l.264).
2. If `v` is not finite, or **any** neighbour present under the frozen
   inclusion rule (l.260–262: ±1 step in each ordered numeric tunable
   dimension that exists in the declared grid) lacks a finite `E-IMPROV`:
   `UNAVAILABLE`. [AI default: "available" means present in the grid; a
   present neighbour with no finite value is not silently dropped.]
3. If `v <= 0`: `FAIL`. `v = 0` is included on purpose: a zero improvement has
   nothing to keep, and `v = 0` can occur structurally, for example when the
   candidate is a fixed multiple of the benchmark (SP1-5, FP1-7).
4. Otherwise `PASS` iff `m >= 0.5·v` AND the selected point is not on a
   boundary of any ordered numeric tunable dimension; else `FAIL`.

`m` is the median over all present neighbours, pooled across dimensions; with
an even count it is the mean of the two middle values. [AI default; FP1-6.]
The reference implementation's exact float64 result decides `v > 0` and the
comparisons, as in P18-4 and P18-6 (FP1-7). Step 2 comes before step 3, so a
failure that could already be decided never hides an unavailable value
(SP1-2).

Reasons:

1. **It keeps the rule's meaning where the meaning exists.** "Rejects isolated
   numeric peaks" presupposes a positive improvement to protect.
2. **It is fail-closed without adding `U_proc` events.** `FAIL` is a result,
   not unavailability. (b1) adds a `U_proc` event per non-positive nominee.
3. **How often `v <= 0` occurs is unknown.** (Correcting rev 1, FP1-3 and
   SP1-1.) The D-18 null constrains `E-DIFF`, not `E-IMPROV`. The share of
   nominees with `v <= 0` depends on the benchmark law and on how it moves with
   the difference series. FP1 computed that with an independent difference and
   a positive benchmark mean, `E-IMPROV < 0` for every trial, while a de-risker
   null can make the share small. The 1% target must hold in every qualifying
   cell, so (b1) is risky wherever the share is large. D-19 measures it.
4. **Relation to G-1 is an untested hypothesis** (FP1-4, SP1-3). G-1 needs
   the lower 5% bootstrap endpoint of `E-IMPROV` above 0, which takes at least
   1,900 of 2,000 replicates above 0 (FP1, exact). Nothing in the code forces
   that endpoint below a non-positive point estimate
   (`statistics.py:591–651`), and the condition holds only if G-1 and G-8 use
   the same BTC OOS series. So G-1 may often fail where `v <= 0`, but this is
   not assumed. **Where G-1 passes with `v <= 0`, option (a) newly blocks
   promotion, and P18-5 allows no replacement.**

## 4. Consequences

- **C-1 It is a change of rule meaning** and needs §4 wording (G-8 in the
  draft).
- **C-2 Neighbour availability is a binding, not a frozen fact** (FP1-6,
  SP1-4). Step 2 reads "available" as "present in the grid". Under the
  alternative reading ("has a finite value"), invalid neighbours would be
  dropped and the median would come from partial evidence. The strict reading
  can raise `U_proc`, for example when a neighbour's candidate leg is constant.
  D-19 measures it.
- **C-3 The other parts of the rule are unchanged:** the boundary condition
  and the frozen `N/A` case (l.264).
- **C-4 Peak semantics** (FP1-10, inherited from D-04). The nominee is the
  `E-DIFF` peak, while G-8 measures the `E-IMPROV` surface around it. So the
  selected point need not be an `E-IMPROV` peak even when `v > 0`, and the
  gate does not check the surface the selection searched. This follows from
  D-04 and is disclosed here.
- **C-5 No statistician** reviewed this (R19-2).

## 5. Proposed owner question

"D-05: the plateau check compares the neighbouring settings with the selected
strategy's own Sharpe-ratio improvement over the benchmark (E-IMPROV). When
that improvement is zero or negative, the rule as written stops making sense:
it lets 'valleys' pass and fails 'plateaus'. What should happen then?
- (a) the check fails [recommended]: no improvement to protect; changes the
  rule's meaning; adds no 'no result' cases;
- (b1) 'unavailable': each such case counts against your 1% no-result limit;
- (b2) 'not applicable': the check is skipped for such strategies;
- (c) a separately justified new rule for negative values;
- (d) leave as written;
- keep blocked: the check, and so any promotion, stays blocked.

With (a), a value that cannot be calculated, or a neighbouring setting with
no usable value, makes the check unavailable (it does not count as a fail).
No statistician reviewed this. Nothing is activated."
