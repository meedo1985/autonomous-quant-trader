"""Deterministic, offline simulated Binance Spot exchange (roadmap Task 18).

A test double for the order API the executor will use: place a market order,
query it by `clientOrderId`, cancel, and read balances. It has no network and
no authentication surface (Constitution section 28): nothing here can reach a
real venue.

Semantics
---------
- Bars and costs are the backtester's, not new ones (sections 10 and 18): a
  market order decided at a bar close fills at the next bar's open through
  `aqt.backtest.costs.trade_cost`, and the frozen per-side cost (fee + spread
  + slippage) is charged in the quote asset on the filled notional.
- Spot only (section 2): balances can never go negative, so there is no
  shorting, margin, or leverage. A sell larger than the free base balance, or
  a buy costing more than the free quote balance, is rejected.
- Market orders only: Cycle 1 allows taker-like orders and no passive limits,
  so `PRICE_FILTER` and `PERCENT_PRICE`, which govern limit prices, do not
  apply. `LOT_SIZE`, and the minimum and maximum notional limits flagged as
  applying to market orders, are enforced. The notional check uses
  the decision bar's close, the last price known when the order is placed.
- Quantities and balances are exact decimals, so step-size checks cannot be
  broken by binary rounding.
- Faults are declared up front in a `Scenario`, keyed by `clientOrderId`.
  Nothing is random, so a replay is identical.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Context, Decimal
from enum import StrEnum
from typing import Final, NoReturn

from aqt.backtest.costs import CostModelError, FeeSchedule, Side, trade_cost
from aqt.data.bars import BarSemanticsError, BarSeries

__all__ = [
    "ExchangeError",
    "Fault",
    "Order",
    "OrderStatus",
    "Scenario",
    "SimulatedExchange",
    "SimulatedTimeout",
    "SymbolFilters",
    "filters_from_exchange_info",
]

_DEC: Final = Context(prec=34)
_BPS: Final = Decimal(10_000)
_QUOTE: Final[str] = "USDT"


class ExchangeError(Exception):
    """A rejected request, with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


class SimulatedTimeout(TimeoutError):
    """The request's outcome is unknown to the caller. The exchange may have
    processed it; only a later query by `clientOrderId` can tell."""


class OrderStatus(StrEnum):
    FILLED = "FILLED"
    EXPIRED = "EXPIRED"  # a market order that filled only in part


@dataclass(frozen=True, slots=True)
class SymbolFilters:
    """The Binance Spot filters that govern a market order."""

    step_size: Decimal
    min_qty: Decimal
    max_qty: Decimal
    min_notional: Decimal
    max_notional: Decimal | None = None  # None: no maximum applies to market orders

    def __post_init__(self) -> None:
        if self.step_size <= 0 or self.min_qty < 0 or self.max_qty < self.min_qty:
            raise ValueError(f"inconsistent LOT_SIZE filter: {self}")
        if self.min_notional < 0:
            raise ValueError("min_notional must be non-negative")
        if self.max_notional is not None and self.max_notional < self.min_notional:
            raise ValueError("max_notional must not be below min_notional")


def filters_from_exchange_info(
    payload: Mapping[str, object], symbol: str
) -> SymbolFilters:
    """Read `LOT_SIZE`, `MIN_NOTIONAL` and `NOTIONAL` for `symbol` from an
    `exchangeInfo` response. A Task 13 snapshot shows today's filters, not
    historical ones (T13-01): use it only where today's rules are intended."""
    symbols = payload.get("symbols")
    if not isinstance(symbols, list):
        raise ValueError("exchangeInfo payload has no symbols list")
    entry = next((s for s in symbols if s.get("symbol") == symbol), None)
    if entry is None:
        raise ValueError(f"{symbol} is not in the exchangeInfo payload")
    by_type = {f["filterType"]: f for f in entry["filters"]}
    lot = by_type["LOT_SIZE"]
    # A market order is bound only by the notional limits flagged as applying
    # to market orders. A missing flag is read as "applies", the stricter case.
    min_notional, max_notional = Decimal(0), None
    if "NOTIONAL" in by_type:
        notional = by_type["NOTIONAL"]
        if notional.get("applyMinToMarket", True):
            min_notional = Decimal(notional["minNotional"])
        if notional.get("applyMaxToMarket", True):
            if "maxNotional" not in notional:
                raise ValueError(f"{symbol}: NOTIONAL applies a maximum but gives none")
            max_notional = Decimal(notional["maxNotional"])
    if "MIN_NOTIONAL" in by_type and by_type["MIN_NOTIONAL"].get("applyToMarket", True):
        min_notional = max(
            min_notional, Decimal(by_type["MIN_NOTIONAL"]["minNotional"])
        )
    return SymbolFilters(
        step_size=Decimal(lot["stepSize"]),
        min_qty=Decimal(lot["minQty"]),
        max_qty=Decimal(lot["maxQty"]),
        min_notional=min_notional,
        max_notional=max_notional,
    )


@dataclass(frozen=True, slots=True)
class Fault:
    """Scripted behavior for one `clientOrderId`.

    - `timeout`: the order is processed, then `place_order` raises
      `SimulatedTimeout`, so the caller does not learn the outcome.
    - `not_found_queries`: the first N queries raise `NOT_FOUND` although the
      order exists, as a lagging order book can.
    - `fill_fraction`: only this share of the quantity fills (rounded down to
      the step size); the rest expires.
    """

    timeout: bool = False
    not_found_queries: int = 0
    fill_fraction: Decimal = Decimal(1)

    def __post_init__(self) -> None:
        if self.not_found_queries < 0 or not 0 < self.fill_fraction <= 1:
            raise ValueError(f"invalid fault: {self}")


@dataclass(frozen=True, slots=True)
class Scenario:
    faults: Mapping[str, Fault] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Order:
    client_order_id: str
    symbol: str
    side: Side
    orig_qty: Decimal
    executed_qty: Decimal
    status: OrderStatus
    decision_time: datetime
    fill_time: datetime
    fill_price: Decimal
    quote_amount: Decimal  # executed_qty * fill_price
    cost_quote: Decimal  # frozen per-side cost, charged in USDT
    cost_bps: Decimal

    def as_mapping(self) -> dict[str, str]:
        return {
            "client_order_id": self.client_order_id,
            "cost_bps": str(self.cost_bps),
            "cost_quote": str(self.cost_quote),
            "decision_time": self.decision_time.isoformat(),
            "executed_qty": str(self.executed_qty),
            "fill_price": str(self.fill_price),
            "fill_time": self.fill_time.isoformat(),
            "orig_qty": str(self.orig_qty),
            "quote_amount": str(self.quote_amount),
            "side": str(self.side),
            "status": str(self.status),
            "symbol": self.symbol,
        }


class SimulatedExchange:
    """An in-memory spot exchange over fixed bar series. No network, no keys."""

    def __init__(
        self,
        series: Mapping[str, BarSeries],
        filters: Mapping[str, SymbolFilters],
        balances: Mapping[str, Decimal],
        *,
        scenario: Scenario | None = None,
        fees: FeeSchedule | None = None,
    ) -> None:
        if set(series) != set(filters):
            raise ValueError("every symbol needs both a bar series and filters")
        if any(amount < 0 for amount in balances.values()):
            raise ValueError("balances cannot start negative")
        self._series = dict(series)
        self._filters = dict(filters)
        self._balances = {asset: Decimal(amount) for asset, amount in balances.items()}
        self._scenario = scenario or Scenario()
        self._fees = fees
        self._orders: dict[str, Order] = {}
        self._queries: dict[str, int] = {}
        self.events: list[dict[str, str]] = []

    def balances(self) -> dict[str, Decimal]:
        return dict(self._balances)

    def place_order(
        self,
        client_order_id: str,
        symbol: str,
        side: Side,
        quantity: Decimal,
        decision_time: datetime,
    ) -> Order:
        """Place a market order decided at a bar close; it fills at the next open.

        Re-placing an existing `clientOrderId` with identical parameters
        returns the existing order and never fills twice; with different
        parameters it is rejected.
        """
        existing = self._orders.get(client_order_id)
        if existing is not None:
            same = (existing.symbol, existing.side, existing.orig_qty) == (
                symbol,
                side,
                quantity,
            ) and existing.decision_time == decision_time
            if not same:
                self._reject(client_order_id, "DUPLICATE_CLIENT_ORDER_ID", "differs")
            self._log("duplicate", client_order_id)
            return existing

        series = self._series.get(symbol)
        if series is None:
            self._reject(client_order_id, "UNKNOWN_SYMBOL", symbol)
        if not isinstance(side, Side):
            self._reject(client_order_id, "INVALID_SIDE", repr(side))
        filters = self._filters[symbol]
        if quantity < filters.min_qty or quantity > filters.max_qty:
            self._reject(client_order_id, "FILTER_LOT_SIZE", f"quantity {quantity}")
        if _DEC.remainder(quantity, filters.step_size) != 0:
            self._reject(
                client_order_id, "FILTER_LOT_SIZE", f"step {filters.step_size}"
            )
        try:
            decision_bar = series.bar_at(decision_time - series.interval)
        except BarSemanticsError as error:
            self._reject(client_order_id, "INVALID_DECISION_TIME", str(error))
        known_price = Decimal(repr(decision_bar.close))
        known_notional = _DEC.multiply(quantity, known_price)
        if known_notional < filters.min_notional:
            self._reject(client_order_id, "FILTER_MIN_NOTIONAL", f"quantity {quantity}")
        if filters.max_notional is not None and known_notional > filters.max_notional:
            self._reject(client_order_id, "FILTER_MAX_NOTIONAL", f"quantity {quantity}")

        fault = self._scenario.faults.get(client_order_id, Fault())
        # A whole number of steps, rounded down: quantize() would round to the
        # step's exponent, which is not the same as a multiple of the step.
        steps = _DEC.divide_int(
            _DEC.multiply(quantity, fault.fill_fraction), filters.step_size
        )
        executed = _DEC.multiply(steps, filters.step_size)
        try:
            cost = trade_cost(series, decision_time, side, fees=self._fees)
        except CostModelError as error:
            self._reject(client_order_id, "NO_FILL_BAR", str(error))
        price = Decimal(repr(cost.execution_price))
        cost_bps = Decimal(repr(cost.breakdown.total_bps))
        base = symbol.removesuffix(_QUOTE)
        # The whole requested order must be affordable before any partial-fill
        # fault applies, as on the venue: a sell above the free base balance,
        # or a buy the quote balance cannot cover, is rejected outright.
        for asset, delta in self._deltas(side, base, quantity, price, cost_bps).items():
            if _DEC.add(self._balances.get(asset, Decimal(0)), delta) < 0:
                self._reject(client_order_id, "INSUFFICIENT_BALANCE", asset)
        deltas = self._deltas(side, base, executed, price, cost_bps)
        for asset, delta in deltas.items():
            self._balances[asset] = _DEC.add(
                self._balances.get(asset, Decimal(0)), delta
            )
        notional = _DEC.multiply(executed, price)
        cost_quote = _DEC.divide(_DEC.multiply(notional, cost_bps), _BPS)

        order = Order(
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            orig_qty=quantity,
            executed_qty=executed,
            status=OrderStatus.FILLED if executed == quantity else OrderStatus.EXPIRED,
            decision_time=decision_time,
            fill_time=cost.execution_time,
            fill_price=price,
            quote_amount=notional,
            cost_quote=cost_quote,
            cost_bps=cost_bps,
        )
        self._orders[client_order_id] = order
        self.events.append({"event": "fill", **order.as_mapping()})
        if fault.timeout:
            self._log("timeout", client_order_id)
            raise SimulatedTimeout(f"no response for {client_order_id}")
        return order

    @staticmethod
    def _deltas(
        side: Side, base: str, quantity: Decimal, price: Decimal, cost_bps: Decimal
    ) -> dict[str, Decimal]:
        """Balance changes for `quantity` filled at `price`, all in the fixed
        decimal context so the caller's context can never change a balance."""
        notional = _DEC.multiply(quantity, price)
        cost = _DEC.divide(_DEC.multiply(notional, cost_bps), _BPS)
        if side is Side.BUY:
            return {_QUOTE: _DEC.minus(_DEC.add(notional, cost)), base: quantity}
        return {base: _DEC.minus(quantity), _QUOTE: _DEC.subtract(notional, cost)}

    def query_order(self, client_order_id: str) -> Order:
        seen = self._queries.get(client_order_id, 0)
        self._queries[client_order_id] = seen + 1
        fault = self._scenario.faults.get(client_order_id, Fault())
        order = self._orders.get(client_order_id)
        if order is None or seen < fault.not_found_queries:
            self._log("query_not_found", client_order_id)
            raise ExchangeError("NOT_FOUND", client_order_id)
        self._log("query", client_order_id)
        return order

    def cancel_order(self, client_order_id: str) -> None:
        """Market orders are terminal as soon as they exist, so a cancel is
        always refused: unknown ids with `NOT_FOUND`, others with
        `ORDER_NOT_OPEN`."""
        code = "ORDER_NOT_OPEN" if client_order_id in self._orders else "NOT_FOUND"
        self._log(f"cancel_{code.lower()}", client_order_id)
        raise ExchangeError(code, client_order_id)

    def _log(self, event: str, client_order_id: str) -> None:
        self.events.append({"client_order_id": client_order_id, "event": event})

    def _reject(self, client_order_id: str, code: str, detail: str) -> NoReturn:
        self.events.append(
            {"client_order_id": client_order_id, "code": code, "event": "reject"}
        )
        raise ExchangeError(code, detail)
