"""Reconciliation: the account as the venue reports it, explained or not
(roadmap Task 23; Constitution sections 19, 21, 22).

`reconcile` compares the venue with the local record:

1. every order sent since the last successful reconciliation is queried by
   its `clientOrderId`, and must resolve to a terminal order equal to the
   local copy, or, when the local record never learned its outcome, be
   confirmed absent by the section 21 protocol: `AbsenceCheck.queries`
   NOT_FOUND answers, each after `AbsenceCheck.delay`. Without an
   `AbsenceCheck`, a NOT_FOUND for such an order is unresolved (A2324-1);
2. every open order on the venue must be one of those orders, and none may
   still be open;
3. every balance must equal the last reconciled balance plus the exact
   effect of the resolved orders, within a per-asset tolerance.

Any difference fails the whole reconciliation; nothing is corrected or
guessed. A failed result opens an incident at the caller (`safety.py`).
Only a passed result may release governor reservations (`settle`), which is
the release contract of Tasks 21 and 22.

The tolerance is `[OPEN]` in the deployment protocol draft section 3. An
asset missing from it has tolerance zero, the strict reading.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Context, Decimal
from types import MappingProxyType
from typing import Final, Protocol

from aqt.backtest.costs import Side as TradeSide
from aqt.data.bars import require_utc
from aqt.execution.orders import client_order_id_for
from aqt.execution.simulator import ExchangeError, Order, OrderStatus
from aqt.governor.authorization import Authorization
from aqt.governor.machine import Governor

__all__ = [
    "AbsenceCheck",
    "LocalRecord",
    "ReconciliationReport",
    "ReconcilingVenue",
    "expected_balances",
    "reconcile",
    "settle",
]

_DEC: Final = Context(prec=34)
_QUOTE: Final[str] = "USDT"
_TERMINAL: Final = frozenset({OrderStatus.FILLED, OrderStatus.EXPIRED})


@dataclass(frozen=True, slots=True)
class AbsenceCheck:
    """Section 21 absence confirmation for an order whose outcome is
    unknown: `queries` NOT_FOUND answers in a row, `delay` apart (owner-set
    T22-Q1: 10 s, 2 answers). `sleep` waits `delay` on the caller's clock,
    and `clock` must show that it did (A2324R-1), as the executor requires."""

    delay: timedelta
    queries: int
    sleep: Callable[[timedelta], None]
    clock: Callable[[], datetime]

    def __post_init__(self) -> None:
        if self.delay <= timedelta(0) or self.queries < 2:
            raise ValueError(f"invalid absence check: {self.delay}, {self.queries}")


class ReconcilingVenue(Protocol):
    def balances(self) -> dict[str, Decimal]: ...

    def query_order(self, client_order_id: str) -> Order: ...

    def open_orders(self) -> tuple[Order, ...]: ...


@dataclass(frozen=True, slots=True)
class LocalRecord:
    """What the system believes, from its own records only.

    `balances` are those of the last successful reconciliation. `orders` maps
    every `clientOrderId` sent since then to the order as last seen, or to
    `None` when its outcome was never learned (an executor FREEZE).
    """

    balances: Mapping[str, Decimal]
    orders: Mapping[str, Order | None] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "balances", MappingProxyType(dict(self.balances)))
        object.__setattr__(self, "orders", MappingProxyType(dict(self.orders)))


@dataclass(frozen=True, slots=True)
class ReconciliationReport:
    at: datetime
    passed: bool
    differences: tuple[str, ...]
    resolved: Mapping[str, Order | None]
    expected_balances: Mapping[str, Decimal]
    actual_balances: Mapping[str, Decimal]

    def next_record(self) -> LocalRecord:
        """The local record to carry forward. Only a passed report has one."""
        if not self.passed:
            raise ValueError("a failed reconciliation establishes no record")
        return LocalRecord(self.actual_balances)

    def digest(self) -> str:
        text = json.dumps(
            {
                "actual": {k: str(v) for k, v in self.actual_balances.items()},
                "at": self.at.isoformat(),
                "differences": list(self.differences),
                "expected": {k: str(v) for k, v in self.expected_balances.items()},
                "passed": self.passed,
                "resolved": {
                    k: None if v is None else v.as_mapping()
                    for k, v in self.resolved.items()
                },
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


def expected_balances(local: LocalRecord) -> dict[str, Decimal]:
    """The balances a venue should hold for `local`: its reconciled balances
    plus the effect of every known order since (as `reconcile` expects)."""
    if any(order is None for order in local.orders.values()):
        raise ValueError("an order with an unknown outcome has no expected balance")
    expected = dict(local.balances)
    for order in local.orders.values():
        if order is not None:
            _apply(expected, order)
    return expected


def _apply(balances: dict[str, Decimal], order: Order) -> None:
    """Add the exact balance effect of `order`, as the venue books it."""
    base = order.symbol.removesuffix(_QUOTE)
    if order.side is TradeSide.BUY:
        changes = {
            base: order.executed_qty,
            _QUOTE: _DEC.minus(_DEC.add(order.quote_amount, order.cost_quote)),
        }
    else:
        changes = {
            base: _DEC.minus(order.executed_qty),
            _QUOTE: _DEC.subtract(order.quote_amount, order.cost_quote),
        }
    for asset, change in changes.items():
        balances[asset] = _DEC.add(balances.get(asset, Decimal(0)), change)


def _query(
    venue: ReconcilingVenue,
    client_order_id: str,
    known: Order | None,
    absence: AbsenceCheck | None,
    latest: datetime,
) -> tuple[Order | None | str, datetime]:
    """The venue's order, `None` when absent, or why it is unresolved; and
    the latest accepted clock reading, which never moves back (A2324R-3)."""
    answers = 0
    while True:
        try:
            return venue.query_order(client_order_id), latest
        except ExchangeError as error:
            if error.code != "NOT_FOUND":
                return f"unresolved ({error})", latest
        except Exception as error:  # noqa: BLE001 - any failure is unresolved
            return f"unresolved ({type(error).__name__}: {error})", latest
        answers += 1
        if known is not None:
            return None, latest  # a known order that vanished: the caller sees it
        if absence is None:
            return "unresolved (NOT_FOUND, absence not confirmed)", latest
        if answers >= absence.queries:
            return None, latest  # confirmed absent (section 21)
        before = require_utc(absence.clock(), field_name="clock")
        if before < latest:
            return "unresolved (the clock moved backwards)", latest
        absence.sleep(absence.delay)
        after = require_utc(absence.clock(), field_name="clock")
        if after - before < absence.delay:
            return "unresolved (the clock did not advance by the protocol delay)", max(
                latest, before, after
            )
        latest = after


def reconcile(
    venue: ReconcilingVenue,
    local: LocalRecord,
    tolerance: Mapping[str, Decimal],
    at: datetime,
    absence: AbsenceCheck | None = None,
) -> ReconciliationReport:
    at = require_utc(at, field_name="at")
    if any(not value.is_finite() or value < 0 for value in tolerance.values()):
        raise ValueError("tolerances must be finite and non-negative")
    differences: list[str] = []
    resolved: dict[str, Order | None] = {}
    latest = at
    for client_order_id, known in sorted(local.orders.items()):
        found, latest = _query(venue, client_order_id, known, absence, latest)
        if isinstance(found, str):
            differences.append(f"{client_order_id}: {found}")
            continue
        if known is not None and found != known:
            differences.append(f"{client_order_id}: venue differs from local copy")
        if found is not None and found.status not in _TERMINAL:
            differences.append(f"{client_order_id}: not terminal ({found.status})")
        resolved[client_order_id] = found

    if absence is not None:
        # The report is as of the end of any waits, never before (A2324R-2),
        # and a clock that moved back fails it rather than backdating it
        # (A2324R-3).
        now = require_utc(absence.clock(), field_name="clock")
        if now < latest:
            differences.append("clock moved backwards during reconciliation")
        at = max(latest, now)
    readable = True
    try:
        open_orders = venue.open_orders()
        actual = venue.balances()
    except Exception as error:  # noqa: BLE001 - the account cannot be read
        differences.append(f"venue unreadable ({type(error).__name__}: {error})")
        open_orders, actual, readable = (), {}, False
    for resting in open_orders:
        tracked = resting.client_order_id in local.orders
        differences.append(
            f"{resting.client_order_id}: open on the venue"
            + ("" if tracked else " with no local record")
        )

    expected = dict(local.balances)
    for order in resolved.values():
        if order is not None:
            _apply(expected, order)
    if readable:
        for asset in sorted(set(expected) | set(actual)):
            gap = abs(
                _DEC.subtract(
                    actual.get(asset, Decimal(0)), expected.get(asset, Decimal(0))
                )
            )
            if gap > tolerance.get(asset, Decimal(0)):
                differences.append(
                    f"{asset}: venue {actual.get(asset, Decimal(0))}, "
                    f"expected {expected.get(asset, Decimal(0))}"
                )
    return ReconciliationReport(
        at=at,
        passed=not differences,
        differences=tuple(differences),
        resolved=MappingProxyType(resolved),
        expected_balances=MappingProxyType(expected),
        actual_balances=MappingProxyType(dict(actual)),
    )


def settle(
    report: ReconciliationReport,
    governor: Governor,
    authorizations: Iterable[Authorization],
) -> tuple[str, ...]:
    """Release the reservation of every authorization whose order the passed
    `report` resolved. Returns the released nonces.

    This is the only place a reservation held after sending is released
    (Task 22, Astra R-2).
    """
    if not report.passed:
        raise ValueError("only a passed reconciliation may release reservations")
    released = []
    for authorization in authorizations:
        if client_order_id_for(authorization) not in report.resolved:
            continue
        if governor.release(authorization, report.at) is None:
            released.append(authorization.nonce)
    return tuple(released)
