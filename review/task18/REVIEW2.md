# Task 18 second adversarial review (repairs at 7483cb1)

Reviewer: Claude Fable 5.1 (`claude-fable-5-1`), requested via the Claude Code Agent tool; the implementer is a different model (Claude Opus 5.5). I read `src/aqt/execution/simulator.py`, the tests, `REVIEW.md`, `ADJUDICATION.md`, `LOCAL_REPORT.md` and `aqt.backtest.costs` at `task18-simulated-exchange` (7483cb1). In a temporary detached worktree, since removed, I ran `pytest -q tests/unit/test_simulator.py` with `PYTHONPATH` set to the worktree's `src`: 27 passed. I also ran a probe script covering the scenarios below. I did not rerun the full suite, ruff, mypy or lint-imports.

## Findings

**F-1 NON-BLOCKING, `src/aqt/execution/simulator.py:94-129` (and the `SymbolFilters` docstring at line 77)**
`filters_from_exchange_info` ignores Binance's `MARKET_LOT_SIZE` filter, which also limits the quantity of a MARKET order. The `SymbolFilters` docstring calls its fields "the Binance Spot filters that govern a market order". So an order the venue would reject for exceeding the market maximum quantity fills in the simulator. Probe: payload with `LOT_SIZE` maxQty `9000` and `MARKET_LOT_SIZE` maxQty `1`; a BUY of `5` BTCUSDT gives `SymbolFilters(... max_qty=Decimal('9000') ...)` and `status FILLED`. `MARKET_LOT_SIZE` is listed in `.agents/skills/binance-quant-review/SKILL.md:26`. `LOCAL_REPORT.md` does not disclose it as a deviation. It does not block this PR, because the tests pass filters explicitly and no committed snapshot has this filter. Before Task 13 filters are fed to an executor, either honour it (take the tighter `maxQty`, ignoring the `0` placeholder values it can hold) or record it as a deviation. The venue behaviour here comes from general knowledge and was not checked against the official Binance docs in this review.

No other defect with a reachable failure scenario was found. Scenarios checked and found correct:
- **Partial fill rounding to zero:** fraction `0.001` of `0.5` with step `0.001` gives `EXPIRED`, executed `0.000`, and balances do not move. That is a consistent terminal outcome. Binance applies filters to the order, not to each fill, so a partial result below `minQty` is not a violation.
- **Caller decimal context (R-3):** under `localcontext(prec=3)`, a partial buy of `0.166` at 101 leaves USDT at `983.2122042` and records `cost_quote` `0.0217958`. Both equal the exact values. The remaining operations outside `_DEC` are comparisons and `Decimal(str)` / `Decimal(repr(float))` constructions, which are exact and do not depend on the context. `trade_cost` works in floats, and its outputs are converted exactly through `repr`.
- **No negative balances (R-2):** the whole-order check at lines 284-286 uses the same `_deltas` as the ledger update. The executed quantity is never more than the requested quantity, and `cost_bps` is at least 0 (enforced by `costs._require_non_negative`). So the executed deltas are never larger than the checked ones. A sell whose cost is larger than its proceeds is caught by the quote-asset check. All costs are charged in the quote asset, so there is no base-fee path.
- **Idempotency and faults:** a rejected order is not stored, so a retry is evaluated fresh. Re-placing after a `timeout` returns the stored order and never fills twice. `not_found_queries` counts per id and cannot create or remove an order. Nothing is random, and `events` are written in a fixed order.
- **Symbols quoted in something other than USDT:** these would be booked wrongly (base taken from `removesuffix("USDT")`), but they cannot occur, because the protocol universe is `BTCUSDT` and `ETHUSDT` (`protocols/protocol_v1.yaml:52`).

## Astra findings

- R-1: REPAIRED. The executed quantity is `divide_int(q*f, step)*step` under `_DEC`. I checked it with a partial fill and with the zero case.
- R-2: REPAIRED. The whole order is checked for both sides before the fault applies, and I found no path that makes a balance negative.
- R-3: REPAIRED. All ledger and rounding arithmetic runs in `_DEC`. The probe at precision 3 reconciled exactly.
- R-4: REPAIRED. `applyToMarket`, `applyMinToMarket` and `applyMaxToMarket` are honoured, and an applicable maximum with no value is refused. The adjacent `MARKET_LOT_SIZE` gap is F-1.

## Verdict

**ACCEPT.** F-1 is non-blocking and should be resolved or disclosed before live-derived filters are used.
