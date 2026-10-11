# D-19 item 2b step 2: implementation plan

**Drafted by:** a Claude Opus subagent (Plan, read-only), 2026-10-11. Claude Opus 5.5 (`claude-opus-5-5`) spot-checked the citations against the accepted preregistration (`git show fff4e5f:review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md`, cited as P:n). This is a plan, not a decision. The owner's answers to the interpretation questions are recorded separately.

**Where QJ and Q5 are refused today**
- `calibration/generator.py:83-84` refuses `semi-joint`.
- `scripts/d19_choose.py:37-43, 93-95` refuses every non-agnostic law, Q5 included.
- `calibration/rundef.py:251-259` refuses qualification runs.

**Order:** (a), then (c), then (b). Each slice can be tested and reviewed on its own.

## Slice 1: (a) test count M (P:52, P:145-147, P:284, P:310-319)

`d19_choose.py:117` uses `3 * len(cells)`. The change:
- Add `choices.test_count(cells)`: 3 per agnostic or Q5 cell, and 8 per QJ cell (3 trend, 3 vol, 2 joint).
- Shrink the guard so it refuses only `semi-joint`.

Tests:
- Counts per law.
- `d19_choose` accepts a pilot manifest that has Q5 cells.

## Slice 2: (c) coverage rule (P:149-164, P:304, P:477 O18-4-T)

Today `choices` reports only `qualifies_before_coverage`. The change:
- Add `choices.categories(cell)`, a pure function of law, dependence and K.
- Add `choices.coverage(cells, results)`.
- `report["qualifies"]` = qualifies before coverage AND every category non-empty.

Tests:
- One case per table row.
- Demoted cells do not count.
- Losing the last cell in a category gives `qualifies = False`.

## Slice 3: (b) QJ cells and cycle-level tests (P:142, P:182, P:56-57, P:303, P:472, P:487-491; R-6)

The change:
- **Generator:** accept `semi-joint` at K in {2, 20}.
- **`rules.draw`:** QJ calls `semi_empirical(..., joint(k, v_bar))`, then splits into a trend half and a vol half with one shared benchmark.
- **Driver:** writes per-family records `{"trend", "vol"}`.
- **`choices`:**
  - Bounds `error_joint` 0.05 and `u_proc_joint` 0.01.
  - If either family needs the escape, the whole cell runs 40k. If either family fails, the cell is demoted.
  - `z_crit` also meets the joint limit.

Tests:
- The QJ halves are bit-identical to the Q5 draws, which shows the path and signs are shared.
- The generator refuses QJ at K = 1 or 5.
- Synthetic cases cover joint `z_crit`, escape and demotion.

## Interpretation questions (for the owner)
- Q1: M is cycle-wide (P:52, P:310-319 say "every enumerated test"; "M is taken from the manifest"). The text is clear here, so this is not an owner question.
- Q2: the QJ classifier works per family, each family on its own K columns. The alternative is 2K joint diagnostics.
- Q3: the QJ `U_G` uses the shared outer seed.
- Q4: in development, joint `U_proc^R` is checked and the cell is demoted if it fails. The alternative is to report it only.
- Q5: the readings of the coverage table.
