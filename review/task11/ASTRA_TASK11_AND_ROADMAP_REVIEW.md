# Astra Task 11 and roadmap review

Date: 2026-09-14
Reviewer: GPT-6 Astra, high reasoning effort
Mode: independent read-only scientific and roadmap review
Reviewed commit: `0089bfa5b1cfe515079b64127e3ecf3ccb5afc16`

## Task 11 decision

The descriptive-metrics implementation passed substantive review. Segment and
cumulative returns, closing-equity maximum drawdown, turnover, modeled costs,
strictly aligned paired returns, finite-value validation, equity continuity,
cost/equity consistency, and timestamp ordering conform to the authorized Task
11 scope. No advanced statistic, eligibility decision, data access, or frozen
governance change was introduced.

Fresh independent validation passed:

- focused tests: 55 passed;
- full suite: 1000 passed and 4 pre-existing skips;
- Ruff check and format check;
- mypy over 27 source files;
- import-linter with four contracts kept;
- frozen verification for 28/28 trusted files and 14/14 sidecars;
- Task 6 accepted hashes: 6/6.

The review found two extra terminal blank lines when checking the complete Task
11 commit diff from `0d48d88`. They were removed in the follow-up correction,
and the full base-to-working-tree `git diff --check` then passed. The README
status and final Ruff file count were also corrected.

Final Task 11 decision after those corrections: **PASS**.

## Roadmap decision

Tracked repository evidence defines Tasks 1 through 11. It contains no approved
Task 12 specification or complete numbered roadmap beyond Task 11. The next safe
action is a statistical-conventions and scope decision; statistical code remains
**NO-GO** until that decision is owner-approved through the applicable governance
route.

The proposal must define, for any statistic included in scope:

- the paired Sharpe estimand, sampling, risk-free rate, annualizer, standard
  deviation convention, and short/constant-series behavior;
- the Newey-West ESS equation, bandwidth/kernel, bounds, fallback trigger, and
  definition of raw decisions;
- the Politis-White stationary-bootstrap variant, RNG mapping and stream
  separation, block bounds, resampling method, invalid replicates, and quantiles;
- DSR and PBO formulas, effective trial construction, partitions, ties, missing
  trials, and aligned matrices;
- reuse of the Task 11 drawdown sampling convention;
- the exact boundary behavior and stress interpretation for BTC and ETH gates.

Already frozen numerical thresholds include 2,000 bootstrap iterations, a 90%
paired confidence interval, DSR 0.95, PBO 0.30 after 20 family trials with 16
partitions, minimum ESS 120, CPCV activation at 250 effective decisions, fold win
rate 0.60, null percentile 0.95, and 81 trials per family. These values do not
resolve the missing estimator definitions.

No Task 12 implementation was started.
