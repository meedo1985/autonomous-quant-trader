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
import math
from dataclasses import dataclass
from datetime import timedelta
from decimal import ROUND_CEILING, ROUND_FLOOR, Context, Decimal
from fractions import Fraction
from typing import Final

from aqt.backtest.costs import (
    FALLBACK_TAKER_FEE_BPS,
    SLIPPAGE_CAP_BPS,
    SPREAD_ALLOWANCE_BPS,
)
from aqt.backtest.costs import Side as TradeSide
from aqt.execution.simulator import SymbolFilters
from aqt.governor.authorization import Authorization, Side

__all__ = [
    "WORST_CASE_COST_BPS",
    "ExecutorConfig",
    "affordable_quantity",
    "client_order_id_for",
    "limit_price_for",
    "order_quantity",
    "trade_side",
]

_DEC: Final = Context(prec=34)
_ID_PREFIX: Final[str] = "aqt-"

WORST_CASE_COST_BPS: Final[Decimal] = Decimal(
    repr(FALLBACK_TAKER_FEE_BPS + SPREAD_ALLOWANCE_BPS + SLIPPAGE_CAP_BPS)
)
"""The frozen cost model's largest per-side charge at the fallback fee:
10 bps fee + 2 bps spread + 15 bps slippage cap = 27 bps. A fee schedule
above the fallback could still leave a buy unaffordable; the venue then
rejects it, which ends the run safely as REJECTED."""


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
) -> Decimal | None:
    """The worst price the authorization accepts (owner answer T22-Q3), or
    `None` when no positive price on the tick lies within the bound.

    `max_slippage_bps` from the mark price: above it for a buy, below it for
    a sell. The bound is computed exactly, and every rounding (to the tick,
    then to a Decimal) goes toward the mark, so the cap is never looser than
    the bound (Astra R3-1).
    """
    buy = authorization.side is Side.BUY
    ratio = Fraction(authorization.max_slippage_bps) / 10_000
    bound = Fraction(mark_price) * (1 + ratio if buy else 1 - ratio)
    tick = filters.tick_size
    if tick is not None:
        steps = bound / Fraction(tick)
        bound = (math.floor(steps) if buy else math.ceil(steps)) * Fraction(tick)
    toward_mark = Context(prec=34, rounding=ROUND_FLOOR if buy else ROUND_CEILING)
    cap = toward_mark.divide(Decimal(bound.numerator), Decimal(bound.denominator))
    return cap if cap > 0 else None


def affordable_quantity(
    quote_balance: Decimal, limit_price: Decimal, filters: SymbolFilters
) -> Decimal:
    """The largest step-multiple quantity whose cost at the cap, plus the
    worst-case charge, fits in `quote_balance` (exact, rounded down)."""
    unit = Fraction(limit_price) * (1 + Fraction(WORST_CASE_COST_BPS) / 10_000)
    steps = math.floor(Fraction(quote_balance) / unit / Fraction(filters.step_size))
    return _DEC.multiply(Decimal(max(steps, 0)), filters.step_size)


def trade_side(side: Side) -> TradeSide:
    return TradeSide.BUY if side is Side.BUY else TradeSide.SELL
