# Task 8 — production backtester v0

Authorization: owner approved continuation after Task 7 passed independent Sol
High review on 2026-09-13.

## Scope

Implement the smallest deterministic production backtester under
`src/aqt/backtest/` that executes a timestamped target-exposure path over an
hourly `BarSeries` using the frozen bar semantics and Cycle-1 cost model. The
engine starts flat, clips requested targets to `[0, 1]`, keeps requested target
and actual held weight distinct, drifts fractional held weight after returns,
uses the inclusive Task 5 ULP-aware 10pp comparator, permits risk increases
only at the scheduled 00:00 UTC decision and after the 24-hour minimum hold,
permits intraday reductions only, executes at the next open, charges absolute
turnover cost before the following return, compounds equity, and does not force
terminal liquidation.

Reuse the existing production modules for bar resolution, cost quotes, and
rebalance eligibility. Do not copy the Task 6 exact kernel or Task 7 NumPy
implementation into production. Preserve auditable per-segment records,
including decision/execution timestamps, requested/clipped/held/executed
exposure, action, turnover, cost inputs/source, gross return, and equity states.

## Required evidence

- Production tests compare baseline results against the frozen Task 6 oracle
  and independent Task 7 NumPy reference across the accepted synthetic matrix.
- Direct tests cover next-open timing, target clipping, fractional/adverse
  drift HOLD, inclusive band behavior, scheduled/minimum-hold actions,
  cost-before-return, fee fallback/source, stress multipliers, invalid input,
  deterministic reruns, and no mutation of inputs.
- Delay stress may be implemented only if its exposure-path timing follows
  unambiguously from the frozen artifacts and approved Task 3 convention. If a
  required scheduling interaction is unbound, report the exact policy question
  and keep the baseline engine complete without guessing.
- Record exact environment, commands, exits, scope, assumptions, and hashes in
  `review/task8/LOCAL_REPORT.md`.

## Exclusions and gate

Do not add data ingestion, strategy/model logic, metrics beyond the backtester
record/equity outputs, portfolio aggregation, validation/promotion, governor,
executor, exchange/network access, credentials, live or paper trading, Task 9,
or any frozen-governance amendment. Do not modify frozen governance artifacts,
the accepted Task 6 suite/hash manifest, or Task 7 reference files.

Run focused and full tests, Ruff check and format check, mypy, import contracts,
`git diff --check`, frozen verification, and accepted Task 6 hashes. Do not
commit or push. Stop after Task 8 implementation and local report so the
coordinator can run independent review.
