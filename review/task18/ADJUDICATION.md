# Task 18 review adjudication

Review: `review/task18/REVIEW.md`, saved unedited from the reviewer's reply.
Reviewer: GPT-6 Astra (`gpt-6-astra`, reasoning effort high), Codex CLI 0.154.0,
session `01a0de28-525d-77f0-981b-309df54ac27c`, read-only sandbox, no tools,
2026-09-26. Input: the full `main...HEAD` diff (including `LOCAL_REPORT.md`),
implementer-run check output at `cbde71d`, the unchanged `trade_cost` source,
and the frozen cost model spec. The reviewer did not rerun the checks.
Verdict: **FIX**. Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the
implementing model.

All four findings were reproduced with a script before being accepted.

| ID | Severity | Adjudication | Reproduction |
|---|---|---|---|
| R-1 | BLOCKER | **Accepted.** | Step `0.00001000`, quantity `0.5`, fill fraction `0.33333333` executed `0.16666666`, not a multiple of `0.00001`. `quantize` rounds to the step's exponent, not to the step. |
| R-2 | BLOCKER | **Accepted.** | BTC balance `0.2`, sell `0.3` with fill fraction `0.5`: accepted, `0.15` sold. The balance check ran only on the executed part. |
| R-3 | BLOCKER | **Accepted.** | The `0.5` buy under a caller context of precision 6 left USDT at `949.434` instead of `949.43435`; the balance no longer reconciles with the recorded notional and cost. |
| R-4 | BLOCKER | **Accepted.** | A `NOTIONAL` filter with `maxNotional` 40 and `applyMaxToMarket` true parsed to a minimum only, and a 50 USDT order filled. |

Deviation assessment: agreed on T18-01, T18-02 and T18-04. On T18-03 the
reviewer is right that calling the decision close a "causal equivalent" of
Binance's recent average price overstates it: it is a causal approximation at
1h resolution, not an equivalent. `LOCAL_REPORT.md` is corrected to say so.

All four are repaired below.

## Repairs (Claude Opus 5.5, 2026-09-26)

| ID | Change | Regression test |
|---|---|---|
| R-1 | The executed quantity is `divide_int(quantity * fraction, step) * step`: a whole number of steps, rounded down. | `test_partial_fills_are_whole_multiples_of_the_step` (step with trailing zeros, plain step, and a non-power-of-ten step `0.005`) |
| R-2 | Balances are checked against the **whole requested** order, before any partial-fill fault applies; only the executed part then moves balances. | `test_an_oversized_sell_is_rejected_even_if_only_part_would_fill` |
| R-3 | All balance arithmetic (`add`, `subtract`, `minus`, and the step rounding) runs in the module's fixed context through `_deltas`; nothing uses the caller's context. | `test_balances_ignore_the_callers_decimal_context` (precision 6, `ROUND_DOWN`): USDT `949.43435`, equal to 1000 minus the recorded notional and cost |
| R-4 | `SymbolFilters` gains `max_notional`. The reader honours `applyToMarket` (`MIN_NOTIONAL`) and `applyMinToMarket` / `applyMaxToMarket` (`NOTIONAL`); a missing flag is read as "applies", and a maximum that applies without a value is refused. Orders above an applicable maximum are rejected with `FILTER_MAX_NOTIONAL`. | `test_filters_are_read_from_an_exchange_info_payload` (4 filter shapes), `test_a_maximum_that_applies_but_is_missing_is_refused`, `test_an_applicable_maximum_notional_is_enforced` |

T18-03 wording in `LOCAL_REPORT.md` corrected from "causal equivalent" to
"causal approximation ... not an equivalent".

Mutation check: with the simulator from `c045b39` restored, 10 of the new tests
fail (every R-1 to R-4 test except the one partial-fill case whose step has no
trailing zeros, which the old rounding happened to get right); with the repair
all pass.

Validation after repair, `.venv` Python 3.14.7: `pytest -q` 1286 passed, 4 skipped in 63.77s (0:01:03);
ruff, format, mypy and `lint-imports` pass; `git diff --check main...HEAD`
clean (after commit); no change under the frozen paths.

These repairs have not been re-reviewed by a different model.
