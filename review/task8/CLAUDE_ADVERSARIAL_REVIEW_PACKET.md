# Task 8 adversarial review packet

Review status: completed by canonical model `claude-fable-5-1`; verdict PASS.
This packet preserves the pre-adjudication hashes that reviewer inspected.
The final two-file correction and current hashes are recorded in
`REVIEW_ADJUDICATION.md` and `LOCAL_REPORT.md`.

Review the uncommitted Task 8 snapshot based on commit
`5e03693457a50b830c65da1c5d8f5e3ccaf6ce23`. This is a read-only adversarial
review. Do not edit, commit, push, or begin Task 9.

## Scope and acceptance

The task adds a deterministic production backtester for an hourly target path:
flat initial state, next-open execution, `[0, 1]` clipping, actual fractional
weight drift, the accepted ULP-aware 10pp comparator, midnight-only risk
increases with the 24-hour minimum hold, intraday reductions, absolute
turnover, per-side cost before the following return, compounded equity, no
terminal liquidation, and complete segment audit fields.

Read the complete new files directly; they are the review attachments:

- `src/aqt/backtest/engine.py`
- `tests/unit/test_backtest_engine.py`
- `tests/integration/test_production_backtest_comparison.py`
- `tests/integration/__init__.py`
- `review/task8/AUTHORIZED_SPEC.md`
- `review/task8/LOCAL_REPORT.md`

Also inspect the reused production modules, accepted Task 6 exact oracle and
Task 7 NumPy/bound layers. Plain `git diff` omits these untracked files, so use
`git status --untracked-files=all` and read them explicitly.

## Snapshot hashes

```text
61ad9f0abc6ae1641b47a39fe4f04693a745c75ccc9c723f196492c5e63b181b  review/task8/AUTHORIZED_SPEC.md
c890d2a2d7605de15fced390491a4e058c0403be4c524247c67ff5d64a37432b  review/task8/OPUS_PROMPT.md
df397a6d6cace628231add7c5a62fe66091af6f3df41ca9b60c4e6f69880cbed  src/aqt/backtest/engine.py
362061e08071be4f8b91167c2a071fbcbcf633580034f75bf77f07bec9bf3d0f  tests/unit/test_backtest_engine.py
449160eeaf2ca8bdc6d146170b5d7463389891d9485d0a75115bea19128c1b9f  tests/integration/__init__.py
f3f0b9486e5e77e5d1ee79666e35a260d5888aabe126abeddb07d9828323b231  tests/integration/test_production_backtest_comparison.py
```

## Validation already completed

- Focused Task 8 suite: 22 passed.
- Full suite: 842 passed, 4 documented pre-existing skips.
- Ruff check and format check: passed.
- Mypy: 21 source files passed.
- Import contracts: 4 kept, 0 broken.
- `git diff --check`: passed.
- Frozen audit: 28/28 trusted bytes, 14/14 sidecars, every binding passed.
- Accepted Task 6 hashes: 6/6 passed.

## Targeted review questions

1. Can any future close/open influence a decision, exposure, or cost input?
2. Does every execution/cost/return/equity step implement the frozen timing and
   units, including fractional drift and cost-before-return?
3. Can requested targets be confused with actual drifted holdings, especially
   for HOLD decisions, later turnover, the band, or the minimum-hold clock?
4. Does the 160-path comparison independently constrain production against
   both the exact oracle and NumPy reference without inventing a tolerance?
5. Are any invalid inputs, determinism hazards, scope expansions, secret/data
   accesses, or missing mandatory checks material to Task 8 acceptance?
6. Is rejecting nonzero delay with the documented policy question the correct
   minimal treatment under the authorized spec, or does a frozen artifact bind
   the overlapping-decision state unambiguously?

Return stable finding IDs under `BLOCKER`, `NON-BLOCKING`, or `QUESTION`. Each
finding must cite file/line, triggering scenario, evidence, impact, and the
smallest correction or clarifying question. State missing evidence rather than
guessing. Finish with `PASS` or `FAIL`. Do not propose strategy logic or a
frozen-governance amendment.
