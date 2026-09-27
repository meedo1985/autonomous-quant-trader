"""Order identity and sizing for the executor (roadmap Task 22).

One authorization maps to exactly one `clientOrderId`, derived from its
nonce, so every placement and every resend under that authorization is the
same order to the venue (Constitution section 21: "resend only with same
clientOrderId"). That holds only on a venue that never accepts a second
order under an id it has already filled, as the Task 18 simulator does.
Binance allows reusing a `clientOrderId` once the earlier order is filled
(Astra R-6), so a real adapter needs its own guard before a resend.
Quantities are rounded down to the step size, so an order
never exceeds the authorized bound (section 20).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import timedelta
from decimal import ROUND_CEILING, ROUND_FLOOR, Context, Decimal
from typing import Final

from aqt.backtest.costs import Side as TradeSide
from aqt.execution.simulator import SymbolFilters
from aqt.governor.authorization import Authorization, Side

__all__ = [
    "ExecutorConfig",
    "client_order_id_for",
    "limit_price_for",
    "order_quantity",
    "trade_side",
]

_DEC: Final = Context(prec=34)
_ID_PREFIX: Final[str] = "aqt-"
_BPS: Final = Decimal(10_000)


@dataclass(frozen=True, slots=True)
class ExecutorConfig:
    """The section 21 values the frozen text leaves open; both are required.

    `not_found_delay` is the "protocol delay" between NOT_FOUND answers.
    `absence_queries` is how many NOT_FOUND answers, each after that delay,
    count as confirmed absence. The frozen text names two (query, wait, query
    again), so fewer is refused. Both are `[OPEN]` in the deployment protocol
    draft section 7, so neither is defaulted.
    """

    not_found_delay: timedelta
    absence_queries: int

    def __post_init__(self) -> None:
        if self.not_found_delay <= timedelta(0):
            raise ValueError(f"invalid not_found_delay {self.not_found_delay}")
        if self.absence_queries < 2:
            raise ValueError(
                f"absence_queries must be >= 2, got {self.absence_queries}"
            )


def client_order_id_for(authorization: Authorization) -> str:
    """The one `clientOrderId` for `authorization`.

    A digest of the nonce: 36 characters from `[a-z0-9-]`, inside Binance's
    `^[a-zA-Z0-9-_]{1,36}$`, whatever the nonce source produces.
    """
    digest = hashlib.sha256(authorization.nonce.encode("utf-8")).hexdigest()
    return _ID_PREFIX + digest[:32]


def order_quantity(authorization: Authorization, filters: SymbolFilters) -> Decimal:
    """The largest valid quantity not above the authorized bound, or 0.

    Rounded down to a whole number of steps and capped at `max_qty`; 0 when
    that falls below `min_qty`, meaning no order can be placed.
    """
    bound = min(authorization.max_base_quantity, filters.max_qty)
    steps = _DEC.divide_int(bound, filters.step_size)
    quantity = _DEC.multiply(steps, filters.step_size)
    if quantity <= 0 or quantity < filters.min_qty:
        return Decimal(0)
    return quantity


def limit_price_for(
    authorization: Authorization, mark_price: Decimal, filters: SymbolFilters
) -> Decimal:
    """The worst price the authorization accepts (owner answer T22-Q3).

    `max_slippage_bps` from the mark price: above it for a buy, below it for
    a sell, rounded to the tick size toward the mark, so the cap is never
    looser than the bound.
    """
    ratio = _DEC.divide(authorization.max_slippage_bps, _BPS)
    if authorization.side is Side.BUY:
        cap, rounding = _DEC.multiply(mark_price, _DEC.add(1, ratio)), ROUND_FLOOR
    else:
        cap, rounding = (
            _DEC.multiply(mark_price, _DEC.subtract(1, ratio)),
            ROUND_CEILING,
        )
    tick = filters.tick_size
    if tick is not None:
        steps = _DEC.divide(cap, tick).to_integral_value(rounding=rounding)
        cap = _DEC.multiply(steps, tick)
    if cap <= 0:
        raise ValueError(f"no positive price within the bound: {cap}")
    return cap


def trade_side(side: Side) -> TradeSide:
    return TradeSide.BUY if side is Side.BUY else TradeSide.SELL
