"""Governor inputs and outputs (roadmap Task 21, Constitution section 20).

Section 20: "Authorization binds bounded state transition: proposal hash,
current-state reference, symbol, target/qty bounds, max slippage, expiry,
nonce. Re-evaluate from actual fills."

`ActualState` is what the account actually holds, derived from fills and
balances; there is deliberately no field for an intended or expected state.
Money and quantities are `Decimal`; exposures are `float`, as in the frozen
benchmark rules they are checked against.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Context, Decimal
from enum import StrEnum
from typing import Final

from aqt.data.bars import require_utc

__all__ = [
    "DECIMAL_CONTEXT",
    "MAX_DECIMAL_EXPONENT",
    "MAX_DECISION_WINDOW",
    "PROTOCOL_SYMBOLS",
    "ActualState",
    "Authorization",
    "GovernorConfig",
    "Proposal",
    "Refusal",
    "RefusalCode",
    "Side",
]

PROTOCOL_SYMBOLS: Final[tuple[str, ...]] = ("BTCUSDT", "ETHUSDT")
"""`protocols/protocol_v1.yaml` `scope.symbols`."""

DECIMAL_CONTEXT: Final[Context] = Context(prec=34)
"""Fixed precision, so no result depends on the caller's decimal context."""

MAX_DECISION_WINDOW: Final[timedelta] = timedelta(minutes=5)
"""Upper limit on `GovernorConfig.decision_window` (Astra R2-4).

The frozen rule says risk increases happen "only at 00:00 UTC". A window
as long as a bar would let a 00:00 increase be issued at 00:59. Five
minutes is the coding AI's **proposal**, pending the owner (question
T21-Q1); the owner may confirm it or lower it. It can only tighten the rule.
"""

MAX_DECIMAL_EXPONENT: Final[int] = 20
"""Quantities, balances and prices must have a decimal exponent within
+/-20 and at most 34 significant digits (Astra R2-5): exact arithmetic on
unbounded Decimals can take unbounded time."""


def _digest(mapping: dict[str, str | None]) -> str:
    text = json.dumps(mapping, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _iso(moment: datetime | None) -> str | None:
    return None if moment is None else moment.isoformat()


class Side(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class RefusalCode(StrEnum):
    UNKNOWN_SYMBOL = "UNKNOWN_SYMBOL"
    SYMBOL_MISMATCH = "SYMBOL_MISMATCH"
    TARGET_OUT_OF_RANGE = "TARGET_OUT_OF_RANGE"
    NO_EQUITY = "NO_EQUITY"
    DECISION_IN_FUTURE = "DECISION_IN_FUTURE"
    INVALID_DECISION_TIME = "INVALID_DECISION_TIME"
    CLOCK_WENT_BACKWARDS = "CLOCK_WENT_BACKWARDS"
    ZERO_QUANTITY = "ZERO_QUANTITY"
    NOT_RESERVED = "NOT_RESERVED"
    OUTSTANDING_AUTHORIZATION = "OUTSTANDING_AUTHORIZATION"
    STALE_DECISION = "STALE_DECISION"
    INVALID_STATE = "INVALID_STATE"
    STATE_FROM_FUTURE = "STATE_FROM_FUTURE"
    INSIDE_REBALANCE_BAND = "INSIDE_REBALANCE_BAND"
    INCREASE_NOT_SCHEDULED = "INCREASE_NOT_SCHEDULED"
    MINIMUM_HOLD = "MINIMUM_HOLD"
    NOT_ISSUED_HERE = "NOT_ISSUED_HERE"
    ALREADY_USED = "ALREADY_USED"
    EXPIRED = "EXPIRED"
    STATE_CHANGED = "STATE_CHANGED"


@dataclass(frozen=True, slots=True)
class Refusal:
    code: RefusalCode
    detail: str


@dataclass(frozen=True, slots=True)
class GovernorConfig:
    """Bounds the frozen documents leave open; all are required.

    Their values are `[OPEN]` in the deployment protocol draft, so none is
    defaulted here. `decision_window` is how long after its `decision_time` a
    decision may still be authorized and redeemed; it caps the TTL, so a
    00:00 decision cannot be carried later into the hour. It may not exceed
    one bar.
    """

    max_slippage_bps: Decimal
    authorization_ttl: timedelta
    decision_window: timedelta

    def __post_init__(self) -> None:
        if not self.max_slippage_bps.is_finite() or self.max_slippage_bps < 0:
            raise ValueError(f"invalid max_slippage_bps {self.max_slippage_bps}")
        if self.authorization_ttl <= timedelta(0):
            raise ValueError(f"invalid authorization_ttl {self.authorization_ttl}")
        if not timedelta(0) < self.decision_window <= MAX_DECISION_WINDOW:
            raise ValueError(f"invalid decision_window {self.decision_window}")


@dataclass(frozen=True, slots=True)
class Proposal:
    """A requested target exposure, known at a bar close `decision_time`."""

    symbol: str
    target_exposure: float
    decision_time: datetime

    def __post_init__(self) -> None:
        require_utc(self.decision_time, field_name="decision_time")

    def proposal_hash(self) -> str:
        return _digest(
            {
                "decision_time": _iso(self.decision_time),
                "symbol": self.symbol,
                "target_exposure": float(self.target_exposure).hex()
                if math.isfinite(self.target_exposure)
                else repr(self.target_exposure),
            }
        )


@dataclass(frozen=True, slots=True)
class ActualState:
    """The account as it actually is, from fills and balances.

    `base_quantity` and `quote_balance` include locked amounts. `mark_price`
    is the reference price used for exposure and quantity bounds.
    `last_risk_increase_time` is the decision time of the last filled risk
    increase, or `None`.
    """

    symbol: str
    base_quantity: Decimal
    quote_balance: Decimal
    mark_price: Decimal
    as_of: datetime
    last_risk_increase_time: datetime | None = None

    def __post_init__(self) -> None:
        require_utc(self.as_of, field_name="as_of")
        if self.last_risk_increase_time is not None:
            require_utc(
                self.last_risk_increase_time, field_name="last_risk_increase_time"
            )
        for name in ("base_quantity", "quote_balance", "mark_price"):
            value = getattr(self, name)
            if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
                raise ValueError(f"{name} must be a finite Decimal >= 0, got {value!r}")
            if value != 0 and (
                abs(value.adjusted()) > MAX_DECIMAL_EXPONENT
                or len(value.as_tuple().digits) > 34
            ):
                raise ValueError(f"{name} {value!r} is outside the supported range")
        if self.mark_price == 0:
            raise ValueError("mark_price must be positive")

    @property
    def equity(self) -> Decimal:
        return DECIMAL_CONTEXT.add(
            DECIMAL_CONTEXT.multiply(self.base_quantity, self.mark_price),
            self.quote_balance,
        )

    @property
    def exposure(self) -> float:
        """Base value over equity, in `[0, 1]`; 0 when there is no equity."""
        equity = self.equity
        if equity == 0:
            return 0.0
        held = DECIMAL_CONTEXT.multiply(self.base_quantity, self.mark_price)
        return float(DECIMAL_CONTEXT.divide(held, equity))

    def state_reference(self) -> str:
        return _digest(
            {
                "as_of": _iso(self.as_of),
                "base_quantity": str(self.base_quantity),
                "last_risk_increase_time": _iso(self.last_risk_increase_time),
                "mark_price": str(self.mark_price),
                "quote_balance": str(self.quote_balance),
                "symbol": self.symbol,
            }
        )


@dataclass(frozen=True, slots=True)
class Authorization:
    """A bounded, single-use permission for one state transition."""

    proposal_hash: str
    state_reference: str
    symbol: str
    side: Side
    current_exposure: float
    target_exposure: float
    max_base_quantity: Decimal
    max_slippage_bps: Decimal
    issued_at: datetime
    expires_at: datetime
    nonce: str
