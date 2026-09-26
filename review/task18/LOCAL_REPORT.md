# Task 18 local implementation and gate report

Date: 2026-09-26
Base commit: `ae0862d` (`main`)
Branch: `task18-simulated-exchange`
Author and reviewer: Claude Opus 5.5 (`claude-opus-5-5`), coding AI. This is a
**self-review**, not an independent one.

## Authority, and the order of tasks

Task 18 is authorized by the owner's roadmap approval
(`review/roadmap/OWNER_APPROVAL.md`), which authorizes Tasks 13-20 "in order".
Task 16 is blocked by roadmap question Q1 (the section 25 acknowledgment is
unsigned), and Task 17 builds on Task 16. The roadmap's dependency diagram
shows Task 18 as independent of Tasks 16-17.

On 2026-09-26 the coding AI recommended fixing the statistics skill header,
then doing Task 18 before Task 16, and said that reordering needed the owner's
OK. The owner replied, verbatim: "go ahead". This task relies on that reply
for the change of order. It does not change what Task 16 or 17 require.

## Scope

- `src/aqt/execution/simulator.py` (new): `SimulatedExchange`, with market
  orders, query by `clientOrderId`, cancel, balances, scripted faults, and an
  `exchangeInfo` filter reader.
- `tests/unit/test_simulator.py` (new): 18 synthetic tests, sockets blocked.

No existing module, frozen artifact, or import contract changed. Size: 572
added lines, about 300 of them tests.

## Design

- **Costs and bars are the backtester's.** Every fill goes through
  `aqt.backtest.costs.trade_cost`: a decision at close(t) fills at open(t+1)
  and the frozen per-side cost (fee + spread + slippage, with the frozen
  fallback fee unless a `FeeSchedule` is given) is charged in USDT on the
  filled notional. The simulator defines no cost model of its own.
- **Spot only.** Balances can never go negative: a sell above the free base
  balance or a buy costing more than the free quote balance is rejected
  (`INSUFFICIENT_BALANCE`). There is no margin, leverage, or shorting surface.
- **No authentication surface and no network.** The class takes bar series,
  filters, and balances; it has no key, signature, or transport parameter.
- **Exact decimals** for quantities, prices, costs, and balances.
- **Stable rejection codes:** `FILTER_LOT_SIZE`, `FILTER_MIN_NOTIONAL`,
  `INSUFFICIENT_BALANCE`, `DUPLICATE_CLIENT_ORDER_ID`, `UNKNOWN_SYMBOL`,
  `INVALID_SIDE`, `INVALID_DECISION_TIME`, `NO_FILL_BAR`, `NOT_FOUND`,
  `ORDER_NOT_OPEN`.
- **Faults are declared up front** per `clientOrderId`: timeout after
  processing, N initial `NOT_FOUND` queries, partial fill (remainder expires).

### Deliberate differences from the roadmap's design points

- **T18-01. `PRICE_FILTER` and `PERCENT_PRICE` are not enforced.** The roadmap
  lists them, but they govern limit prices, and Cycle 1 allows taker-like
  market orders only (`specs/COST_MODEL_v1.md`: "No passive-limit assumptions
  in Cycle 1"). `LOT_SIZE` and `MIN_NOTIONAL`/`NOTIONAL` are enforced.
- **T18-02. Filters are an input, not read from the Task 13 snapshot by
  default.** `filters_from_exchange_info` reads a snapshot, but the only
  snapshot is from 2026 (T13-01), so applying it to 2017-2021 bars would mix
  eras. The caller chooses.
- **T18-03. `MIN_NOTIONAL` is checked at the decision bar's close**, the last
  price known when the order is placed, not at the fill price, which lies in
  the future. Binance uses a recent average price; the decision close is the
  causal equivalent at 1h resolution.
- **T18-04. A reused `clientOrderId` returns the existing order if the
  parameters match, and is rejected if they differ.** It never fills twice.
  External fact, **not verified in this session:** real Binance enforces
  `newClientOrderId` uniqueness among open orders, and its behavior for ids of
  already-filled orders should be verified against official documentation
  before the executor relies on deduplication by the venue.

## Acceptance criteria (roadmap Task 18)

| # | Criterion | Evidence |
|---|---|---|
| 1 | Market buy fills at open(t+1) with the frozen fee, matching an independent value | `test_market_buy_fills_at_next_open_with_the_frozen_cost`: expected cost computed by hand as 0.5 × 101 × 13 bps (10 fee + 2 spread + 1 slippage floor); also `test_sell_credits_quote_net_of_cost` |
| 2 | `MIN_NOTIONAL` violation rejected with a stable code | `test_filter_violations_are_rejected_with_stable_codes` (4 cases), `test_notional_check_uses_the_price_known_at_decision` |
| 3 | Re-placing a `clientOrderId` is idempotent, never a second fill | `test_replacing_a_client_order_id_never_fills_twice` |
| 4 | Timeout resolves by query to the same terminal outcome | `test_timeout_resolves_to_the_same_terminal_outcome_on_query` (with two lagging `NOT_FOUND` queries and a blind retry) |
| 5 | Sell above the base balance rejected | `test_no_shorting_and_no_spending_beyond_the_balance` |
| 6 | Scenario replay byte-identical | `test_scenario_replay_is_byte_identical` |

Mutation checks, each run against a deliberately broken copy of the module
and then restored:

| Planted bug | Tests that fail |
|---|---|
| Notional check uses the future fill price | `test_notional_check_uses_the_price_known_at_decision` and one other |
| Duplicate ids fill again | the idempotency test and the timeout test |
| Costs not charged | the buy, sell and balance tests |

**T18-05, implementer error caught in-session.** The first version of the
notional test used a quantity that failed the minimum at both prices
(0.099 × 101 = 9.999 < 10), so it could not detect a future-price check; the
first mutation run showed this. The test now uses a 9.95 minimum, where the
two prices disagree.

## Validation

Environment: Windows 11, `.venv` Python 3.14.7.

| Command | Exit | Result |
|---|---|---|
| `python -m pytest -q` | 0 | 1277 passed, 4 pre-existing skips |
| `ruff check .` | 0 | all checks passed |
| `ruff format --check .` | 0 | 74 files already formatted |
| `mypy src scripts/download_market_data.py scripts/build_manifests.py scripts/data_quality_report.py` | 0 | no issues in 37 source files |
| `lint-imports` | 0 | 5 kept, 0 broken |
| `git diff --check main...HEAD` | 0 | clean (run after commit) |

Frozen verification: `git diff main` over `docs/`, `protocols/`, `schemas/`,
`specs/`, `FROZEN_HASHES.json` and its sidecar is empty.

## Findings (self-review)

T18-01 to T18-05 above. T18-04 carries an unverified external fact about real
Binance behavior; it matters for the executor (Task 22), not for this test
double.

## Gate

LOCAL GATE: PASS. Independent review status: `NOT SENT`. `binance-quant-review`
applies to this task (orders, fills, fees, exchange rules); this self-review
followed its checklist but is not independent.
