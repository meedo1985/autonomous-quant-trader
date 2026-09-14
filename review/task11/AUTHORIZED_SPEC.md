# Task 11 — deterministic descriptive metrics

Authorization: owner requested continuation after Task 10. The protocol and
frozen metrics schema do not yet fix the statistical conventions needed for
Sharpe, confidence intervals, ESS, bootstrap, DSR, or PBO. This task therefore
implements descriptive metrics only; it does not amend frozen governance.

## Scope

Add a pure `aqt.metrics` module that consumes an accepted `BacktestResult` and
returns deterministic descriptive values:

- per-segment net-return observations derived from equity-before and
  equity-after-return;
- cumulative net return from initial and final equity;
- nonnegative maximum drawdown magnitude (a fractional loss, not percentage
  points) from the equity path including the initial equity point;
- total absolute turnover and total modeled cost;
- segment count, with no claim that it is a statistical sample size;
- strict timestamp alignment and candidate-minus-benchmark paired net-return
  observations for two otherwise matching backtest results.

Use `math.fsum` for additive summaries, preserve observation order, validate
finite values, and fail closed on mismatched symbols, stress multipliers,
segment counts, or timestamps. Do not mutate backtest inputs.

## Bound conventions

- A segment net return is `equity_after_return / equity_before - 1`.
- Cumulative net return is `final_equity / initial_equity - 1`.
- Maximum drawdown is the largest nonnegative peak-to-trough percentage loss;
  the initial equity is the first peak candidate.
- Paired observations are candidate net return minus benchmark net return at
  identical segment execution/end timestamps and in the original order.

## Exclusions

Do not implement Sharpe, any annualization or risk-free convention, confidence
intervals, bootstrap, Newey-West ESS, DSR, PBO, fold win rates, pass/fail,
metrics-schema expansion, promotion/eligibility, trial-budget checks, data
ingestion, confirmation or lockbox access, strategy/model logic, network,
governor, execution, or any frozen artifact amendment. Do not start Task 12.

## Acceptance criteria

1. Empty and non-empty backtest results produce deterministic descriptive
   metrics using the conventions above.
2. Net-return observations agree with the backtester's equity equation and
   include costs before returns.
3. Drawdown, cumulative return, turnover, cost, and segment count are tested
   against hand-computed synthetic paths, including adverse and flat paths.
4. Pairing rejects every symbol, stress, count, execution-time, and segment-end
   mismatch and preserves exact order for matching paths.
5. Non-finite or invalid forged records are rejected; inputs remain unchanged.
6. Focused/full tests, Ruff, mypy, import contracts, Git whitespace, frozen
   verification, and Task 6 drift verification pass.
7. A different-model adversarial review is adjudicated before commit and push.
