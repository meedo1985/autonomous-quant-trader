"""Synthetic tests for the simulated Binance Spot exchange. Offline only."""

from __future__ import annotations

import json
import socket
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from aqt.backtest.costs import Side
from aqt.data.bars import Bar, BarSeries
from aqt.execution.simulator import (
    ExchangeError,
    Fault,
    OrderStatus,
    Scenario,
    SimulatedExchange,
    SimulatedTimeout,
    SymbolFilters,
    filters_from_exchange_info,
)

T0 = datetime(2020, 3, 2, tzinfo=UTC)
HOUR = timedelta(hours=1)
DECISION = T0 + 6 * HOUR  # close of bar 5; the fill is bar 6's open
FILTERS = SymbolFilters(
    step_size=Decimal("0.001"),
    min_qty=Decimal("0.001"),
    max_qty=Decimal("100"),
    min_notional=Decimal("10"),
)


@pytest.fixture(autouse=True)
def _no_sockets(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_: object, **__: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)


def _series() -> BarSeries:
    """Six flat bars at 100 (zero returns, so slippage sits at its 1 bp
    floor), then bars opening at 101 and 102."""
    bars = [Bar(T0 + i * HOUR, 100.0, 100.0, 100.0, 100.0, 5.0) for i in range(6)]
    bars.append(Bar(T0 + 6 * HOUR, 101.0, 101.0, 101.0, 101.0, 5.0))
    bars.append(Bar(T0 + 7 * HOUR, 102.0, 102.0, 102.0, 102.0, 5.0))
    return BarSeries("BTCUSDT", tuple(bars))


def _exchange(
    scenario: Scenario | None = None, usdt: str = "1000", btc: str = "0"
) -> SimulatedExchange:
    return SimulatedExchange(
        {"BTCUSDT": _series()},
        {"BTCUSDT": FILTERS},
        {"USDT": Decimal(usdt), "BTC": Decimal(btc)},
        scenario=scenario,
    )


def test_market_buy_fills_at_next_open_with_the_frozen_cost() -> None:
    exchange = _exchange()
    order = exchange.place_order("b1", "BTCUSDT", Side.BUY, Decimal("0.5"), DECISION)

    # Independent expectation: open(t+1) = 101; frozen cost per side is
    # 10 bps fallback fee + 2 bps spread + 1 bp slippage floor = 13 bps.
    notional = Decimal("0.5") * Decimal("101")
    cost = notional * Decimal("13") / Decimal("10000")
    assert order.status is OrderStatus.FILLED
    assert order.fill_time == DECISION  # open(t+1) is the bar opening at close(t)
    assert order.fill_price == Decimal("101.0")
    assert order.cost_bps == Decimal("13.0")
    assert order.cost_quote == cost
    assert exchange.balances() == {
        "USDT": Decimal("1000") - notional - cost,
        "BTC": Decimal("0.5"),
    }


def test_sell_credits_quote_net_of_cost() -> None:
    exchange = _exchange(usdt="0", btc="1")
    order = exchange.place_order("s1", "BTCUSDT", Side.SELL, Decimal("1"), DECISION)
    proceeds = Decimal("101") - Decimal("101") * Decimal("13") / Decimal("10000")
    assert order.executed_qty == Decimal("1")
    assert exchange.balances() == {"USDT": proceeds, "BTC": Decimal("0")}


@pytest.mark.parametrize(
    ("quantity", "code"),
    [
        (Decimal("0.05"), "FILTER_MIN_NOTIONAL"),  # 0.05 * close(t) 100 = 5 < 10
        (Decimal("0.1005"), "FILTER_LOT_SIZE"),  # not a multiple of the step
        (Decimal("0.0005"), "FILTER_LOT_SIZE"),  # below min_qty
        (Decimal("101"), "FILTER_LOT_SIZE"),  # above max_qty
    ],
)
def test_filter_violations_are_rejected_with_stable_codes(
    quantity: Decimal, code: str
) -> None:
    exchange = _exchange(usdt="100000")
    with pytest.raises(ExchangeError) as caught:
        exchange.place_order("f1", "BTCUSDT", Side.BUY, quantity, DECISION)
    assert caught.value.code == code
    assert exchange.balances() == {"USDT": Decimal("100000"), "BTC": Decimal("0")}
    with pytest.raises(ExchangeError, match="NOT_FOUND"):
        exchange.query_order("f1")


def test_notional_check_uses_the_price_known_at_decision() -> None:
    """With a 9.95 minimum, 0.099 * close(t) 100 = 9.9 fails while 0.099 * the
    fill price 101 = 9.999 would pass: the rejection proves the check never
    uses the future fill price."""
    filters = SymbolFilters(
        step_size=Decimal("0.001"),
        min_qty=Decimal("0.001"),
        max_qty=Decimal("100"),
        min_notional=Decimal("9.95"),
    )
    exchange = SimulatedExchange(
        {"BTCUSDT": _series()}, {"BTCUSDT": filters}, {"USDT": Decimal("1000")}
    )
    with pytest.raises(ExchangeError) as caught:
        exchange.place_order("n1", "BTCUSDT", Side.BUY, Decimal("0.099"), DECISION)
    assert caught.value.code == "FILTER_MIN_NOTIONAL"
    order = exchange.place_order("n2", "BTCUSDT", Side.BUY, Decimal("0.1"), DECISION)
    assert order.status is OrderStatus.FILLED  # 0.1 * 100 = 10 >= 9.95


def test_replacing_a_client_order_id_never_fills_twice() -> None:
    exchange = _exchange()
    first = exchange.place_order("d1", "BTCUSDT", Side.BUY, Decimal("0.5"), DECISION)
    after_first = exchange.balances()
    again = exchange.place_order("d1", "BTCUSDT", Side.BUY, Decimal("0.5"), DECISION)
    assert again is first
    assert exchange.balances() == after_first
    with pytest.raises(ExchangeError) as caught:
        exchange.place_order("d1", "BTCUSDT", Side.BUY, Decimal("0.6"), DECISION)
    assert caught.value.code == "DUPLICATE_CLIENT_ORDER_ID"
    assert exchange.balances() == after_first


def test_timeout_resolves_to_the_same_terminal_outcome_on_query() -> None:
    exchange = _exchange(Scenario({"t1": Fault(timeout=True, not_found_queries=2)}))
    with pytest.raises(SimulatedTimeout):
        exchange.place_order("t1", "BTCUSDT", Side.BUY, Decimal("0.5"), DECISION)
    for _ in range(2):  # a lagging book first reports the order as unknown
        with pytest.raises(ExchangeError, match="NOT_FOUND"):
            exchange.query_order("t1")
    resolved = exchange.query_order("t1")
    assert resolved.status is OrderStatus.FILLED
    assert exchange.query_order("t1") == resolved
    retried = exchange.place_order("t1", "BTCUSDT", Side.BUY, Decimal("0.5"), DECISION)
    assert retried == resolved  # a blind retry after the timeout does not refill
    assert exchange.balances()["BTC"] == Decimal("0.5")


def test_partial_fill_expires_the_remainder_rounded_to_the_step() -> None:
    exchange = _exchange(Scenario({"p1": Fault(fill_fraction=Decimal("0.3333"))}))
    order = exchange.place_order("p1", "BTCUSDT", Side.BUY, Decimal("0.5"), DECISION)
    assert order.status is OrderStatus.EXPIRED
    assert order.executed_qty == Decimal("0.166")  # 0.16665 down to the step
    assert exchange.balances()["BTC"] == Decimal("0.166")


def test_no_shorting_and_no_spending_beyond_the_balance() -> None:
    exchange = _exchange(usdt="1000", btc="0.2")
    with pytest.raises(ExchangeError) as caught:
        exchange.place_order("x1", "BTCUSDT", Side.SELL, Decimal("0.3"), DECISION)
    assert caught.value.code == "INSUFFICIENT_BALANCE"
    with pytest.raises(ExchangeError) as caught:
        exchange.place_order("x2", "BTCUSDT", Side.BUY, Decimal("9.9"), DECISION)
    assert caught.value.code == "INSUFFICIENT_BALANCE"  # 9.9 * 101 > 1000
    assert exchange.balances() == {"USDT": Decimal("1000"), "BTC": Decimal("0.2")}


@pytest.mark.parametrize(
    ("symbol", "decision", "code"),
    [
        ("SOLUSDT", DECISION, "UNKNOWN_SYMBOL"),
        ("BTCUSDT", DECISION + timedelta(minutes=30), "INVALID_DECISION_TIME"),
        ("BTCUSDT", T0 + 8 * HOUR, "NO_FILL_BAR"),  # close of the last bar
    ],
)
def test_requests_the_exchange_cannot_serve_are_rejected(
    symbol: str, decision: datetime, code: str
) -> None:
    with pytest.raises(ExchangeError) as caught:
        _exchange().place_order("r1", symbol, Side.BUY, Decimal("0.5"), decision)
    assert caught.value.code == code


def test_cancel_is_refused_for_terminal_and_unknown_orders() -> None:
    exchange = _exchange()
    exchange.place_order("c1", "BTCUSDT", Side.BUY, Decimal("0.5"), DECISION)
    with pytest.raises(ExchangeError, match="ORDER_NOT_OPEN"):
        exchange.cancel_order("c1")
    with pytest.raises(ExchangeError, match="NOT_FOUND"):
        exchange.cancel_order("nope")


def _replay() -> bytes:
    scenario = Scenario(
        {"a": Fault(fill_fraction=Decimal("0.5")), "b": Fault(timeout=True)}
    )
    exchange = _exchange(scenario, usdt="1000", btc="1")
    exchange.place_order("a", "BTCUSDT", Side.BUY, Decimal("0.5"), DECISION)
    with pytest.raises(SimulatedTimeout):
        exchange.place_order("b", "BTCUSDT", Side.SELL, Decimal("0.4"), DECISION)
    exchange.query_order("b")
    with pytest.raises(ExchangeError):
        exchange.place_order("c", "BTCUSDT", Side.BUY, Decimal("0.01"), DECISION)
    with pytest.raises(ExchangeError):
        exchange.cancel_order("a")
    balances = {k: str(v) for k, v in sorted(exchange.balances().items())}
    return json.dumps(
        {"balances": balances, "events": exchange.events}, sort_keys=True
    ).encode()


def test_scenario_replay_is_byte_identical() -> None:
    first, second = _replay(), _replay()
    assert first == second
    assert b'"event": "timeout"' in first and b'"event": "reject"' in first


@pytest.mark.parametrize("notional_filter", ["MIN_NOTIONAL", "NOTIONAL"])
def test_filters_are_read_from_an_exchange_info_payload(notional_filter: str) -> None:
    payload = {
        "symbols": [
            {
                "symbol": "BTCUSDT",
                "filters": [
                    {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
                    {
                        "filterType": "LOT_SIZE",
                        "stepSize": "0.00001000",
                        "minQty": "0.00001000",
                        "maxQty": "9000.00000000",
                    },
                    {"filterType": notional_filter, "minNotional": "5.00000000"},
                ],
            }
        ]
    }
    assert filters_from_exchange_info(payload, "BTCUSDT") == SymbolFilters(
        step_size=Decimal("0.00001"),
        min_qty=Decimal("0.00001"),
        max_qty=Decimal("9000"),
        min_notional=Decimal("5"),
    )
    with pytest.raises(ValueError, match="not in the exchangeInfo"):
        filters_from_exchange_info(payload, "ETHUSDT")
