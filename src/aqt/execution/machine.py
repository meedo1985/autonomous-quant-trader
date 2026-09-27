"""The executor state machine (roadmap Task 22, Constitution sections 20-21).

The executor consumes one governor authorization and places at most one
order under it. Section 21, verbatim: "Timeout → query clientOrderId.
NOT_FOUND → wait protocol delay → query again. Confirmed absence may resend
only with same clientOrderId and unexpired authorization; otherwise get new
authorization. UNKNOWN → reconcile/FREEZE."

How that reads here:

* The one `clientOrderId` comes from the authorization (`orders.py`), so a
  resend is the same order to the venue, never a second one.
* A placement whose outcome is not known (timeout or any error that is not
  a definite rejection) is queried by `clientOrderId`.
* NOT_FOUND is followed by `not_found_delay` and another query;
  `absence_queries` NOT_FOUND answers in a row are confirmed absence.
* After confirmed absence the same order is resent only while the
  authorization is unexpired; otherwise the run ends asking for a new one.
* UNKNOWN (a query whose answer is not known, a found order that does not
  match what was sent, or a clock that did not advance) ends in FREEZE. The
  executor never places anything after that, and never releases the
  governor's reservation: that waits for reconciliation (Task 23).

Every transition is looked up in `TRANSITIONS`. A (state, event) pair that is
not listed raises `IllegalTransition`; there is no fallthrough.

The reservation is released (`Governor.release`) only once the order's end
is confirmed by the venue's own answer: filled, expired after a partial
fill, rejected, or confirmed absent with no resend allowed. Account-level
reconciliation is Task 23; the next decision must start from a freshly read
`ActualState`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Context, Decimal
from enum import StrEnum
from typing import Final, Protocol

from aqt.backtest.costs import Side as TradeSide
from aqt.data.bars import require_utc
from aqt.execution.orders import (
    ExecutorConfig,
    client_order_id_for,
    order_quantity,
    trade_side,
)
from aqt.execution.simulator import ExchangeError, Order, OrderStatus, SymbolFilters
from aqt.governor.authorization import (
    ActualState,
    Authorization,
    Proposal,
    Refusal,
    RefusalCode,
    Side,
)
from aqt.governor.machine import Governor

__all__ = [
    "TERMINAL",
    "TRANSITIONS",
    "Event",
    "ExecutionResult",
    "Executor",
    "IllegalTransition",
    "OrderVenue",
    "State",
    "Transition",
]

_DEC: Final = Context(prec=34)
_BPS: Final = Decimal(10_000)


class State(StrEnum):
    READY = "READY"
    SUBMITTING = "SUBMITTING"
    QUERYING = "QUERYING"
    AWAITING_RECHECK = "AWAITING_RECHECK"
    CONFIRMED_ABSENT = "CONFIRMED_ABSENT"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    REJECTED = "REJECTED"
    NEW_AUTHORIZATION_REQUIRED = "NEW_AUTHORIZATION_REQUIRED"
    REFUSED = "REFUSED"
    FREEZE = "FREEZE"


class Event(StrEnum):
    REDEEMED = "REDEEMED"
    REDEEM_REFUSED = "REDEEM_REFUSED"
    NO_QUANTITY = "NO_QUANTITY"
    FILL_CONFIRMED = "FILL_CONFIRMED"
    PARTIAL_FILL_CONFIRMED = "PARTIAL_FILL_CONFIRMED"
    OUTCOME_UNKNOWN = "OUTCOME_UNKNOWN"
    PLACE_REJECTED = "PLACE_REJECTED"
    NOT_FOUND = "NOT_FOUND"
    ABSENCE_CONFIRMED = "ABSENCE_CONFIRMED"
    QUERY_UNKNOWN = "QUERY_UNKNOWN"
    ORDER_MISMATCH = "ORDER_MISMATCH"
    CLOCK_FAULT = "CLOCK_FAULT"
    AUTHORIZATION_VALID = "AUTHORIZATION_VALID"
    AUTHORIZATION_EXPIRED = "AUTHORIZATION_EXPIRED"


_S, _E = State, Event
_FOUND: Final = {
    _E.FILL_CONFIRMED: _S.FILLED,
    _E.PARTIAL_FILL_CONFIRMED: _S.PARTIALLY_FILLED,
    _E.ORDER_MISMATCH: _S.FREEZE,
}

TRANSITIONS: Final[dict[tuple[State, Event], State]] = {
    (_S.READY, _E.REDEEMED): _S.SUBMITTING,
    (_S.READY, _E.REDEEM_REFUSED): _S.REFUSED,
    (_S.READY, _E.NO_QUANTITY): _S.REFUSED,
    **{(_S.SUBMITTING, event): state for event, state in _FOUND.items()},
    (_S.SUBMITTING, _E.OUTCOME_UNKNOWN): _S.QUERYING,
    (_S.SUBMITTING, _E.PLACE_REJECTED): _S.REJECTED,
    **{(_S.QUERYING, event): state for event, state in _FOUND.items()},
    (_S.QUERYING, _E.NOT_FOUND): _S.AWAITING_RECHECK,
    (_S.QUERYING, _E.QUERY_UNKNOWN): _S.FREEZE,
    **{(_S.AWAITING_RECHECK, event): state for event, state in _FOUND.items()},
    (_S.AWAITING_RECHECK, _E.NOT_FOUND): _S.AWAITING_RECHECK,
    (_S.AWAITING_RECHECK, _E.ABSENCE_CONFIRMED): _S.CONFIRMED_ABSENT,
    (_S.AWAITING_RECHECK, _E.QUERY_UNKNOWN): _S.FREEZE,
    (_S.AWAITING_RECHECK, _E.CLOCK_FAULT): _S.FREEZE,
    (_S.CONFIRMED_ABSENT, _E.AUTHORIZATION_VALID): _S.SUBMITTING,
    (_S.CONFIRMED_ABSENT, _E.AUTHORIZATION_EXPIRED): _S.NEW_AUTHORIZATION_REQUIRED,
}
"""Every allowed transition. Anything else is `IllegalTransition`."""

TERMINAL: Final[frozenset[State]] = frozenset(
    {
        _S.FILLED,
        _S.PARTIALLY_FILLED,
        _S.REJECTED,
        _S.NEW_AUTHORIZATION_REQUIRED,
        _S.REFUSED,
        _S.FREEZE,
    }
)

_NOT_A_REJECTION: Final[frozenset[str]] = frozenset(
    {"NOT_FOUND", "DUPLICATE_CLIENT_ORDER_ID"}
)
"""Placement errors that do not say the order is absent: the id may already
name an order, so the outcome is unknown and is queried."""

_RELEASE_AFTER: Final[frozenset[State]] = frozenset(
    {_S.FILLED, _S.PARTIALLY_FILLED, _S.REJECTED, _S.NEW_AUTHORIZATION_REQUIRED}
)
"""Ends confirmed by the venue's own answer. FREEZE is deliberately absent."""


class IllegalTransition(RuntimeError):
    """A (state, event) pair `TRANSITIONS` does not define."""


def step(state: State, event: Event) -> State:
    try:
        return TRANSITIONS[(state, event)]
    except KeyError:
        raise IllegalTransition(f"{event} is not allowed in {state}") from None


class OrderVenue(Protocol):
    """The order API the executor needs; the Task 18 simulator provides it."""

    def place_order(
        self,
        client_order_id: str,
        symbol: str,
        side: TradeSide,
        quantity: Decimal,
        decision_time: datetime,
    ) -> Order: ...

    def query_order(self, client_order_id: str) -> Order: ...


@dataclass(frozen=True, slots=True)
class Transition:
    at: datetime
    source: State
    event: Event
    target: State
    detail: str

    def as_mapping(self) -> dict[str, str]:
        return {
            "at": self.at.isoformat(),
            "detail": self.detail,
            "event": str(self.event),
            "source": str(self.source),
            "target": str(self.target),
        }


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """How one authorization ended.

    `adverse_move_bps` is how far the fill price moved against the order
    from `ActualState.mark_price`, in basis points (fees and the frozen cost
    model's charge are separate, in `order.cost_bps`). `slippage_breach` is
    whether it exceeds the authorization's `max_slippage_bps`. A market order
    cannot be stopped from moving; the breach is reported, not prevented.
    """

    state: State
    client_order_id: str
    order: Order | None
    refusal: Refusal | None
    released: bool
    adverse_move_bps: Decimal | None
    slippage_breach: bool
    transitions: tuple[Transition, ...]


class Executor:
    """Runs one authorization to a terminal state against one venue.

    `clock` returns the current UTC time; `sleep` waits a duration and must
    advance `clock` by at least that much, or the run FREEZEs.
    """

    def __init__(
        self,
        governor: Governor,
        venue: OrderVenue,
        filters: SymbolFilters,
        config: ExecutorConfig,
        *,
        clock: Callable[[], datetime],
        sleep: Callable[[timedelta], None],
    ) -> None:
        self._governor = governor
        self._venue = venue
        self._filters = filters
        self._config = config
        self._clock = clock
        self._sleep = sleep

    def _now(self) -> datetime:
        return require_utc(self._clock(), field_name="clock")

    def execute(
        self, authorization: Authorization, proposal: Proposal, state: ActualState
    ) -> ExecutionResult:
        if proposal.proposal_hash() != authorization.proposal_hash:
            raise ValueError("proposal does not match the authorization")
        client_order_id = client_order_id_for(authorization)
        run = _Run(self, authorization, proposal, state, client_order_id)
        return run.go()


class _Run:
    """The mutable part of one `Executor.execute` call."""

    def __init__(
        self,
        executor: Executor,
        authorization: Authorization,
        proposal: Proposal,
        state: ActualState,
        client_order_id: str,
    ) -> None:
        self.x = executor
        self.auth = authorization
        self.proposal = proposal
        self.actual = state
        self.client_order_id = client_order_id
        self.state = State.READY
        self.transitions: list[Transition] = []
        self.order: Order | None = None
        self.refusal: Refusal | None = None
        self.quantity = Decimal(0)
        self.release_unredeemed = False

    def fire(self, event: Event, detail: str = "") -> None:
        target = step(self.state, event)
        self.transitions.append(
            Transition(self.x._now(), self.state, event, target, detail)
        )
        self.state = target

    def go(self) -> ExecutionResult:
        self.quantity = order_quantity(self.auth, self.x._filters)
        if self.quantity == 0:
            self.release_unredeemed = True
            self.fire(Event.NO_QUANTITY, f"bound {self.auth.max_base_quantity}")
        else:
            refusal = self.x._governor.redeem(self.auth, self.actual, self.x._now())
            if refusal is None:
                self.fire(Event.REDEEMED)
            else:
                self.refusal = refusal
                # An unredeemed authorization whose state moved can never be
                # used; abandon it so the next decision is not blocked.
                self.release_unredeemed = refusal.code is RefusalCode.STATE_CHANGED
                self.fire(Event.REDEEM_REFUSED, f"{refusal.code}: {refusal.detail}")
        while self.state not in TERMINAL:
            self._advance()
        return self._finish()

    def _advance(self) -> None:
        if self.state is State.SUBMITTING:
            self._place()
        elif self.state is State.QUERYING:
            self._query()
        elif self.state is State.AWAITING_RECHECK:
            before = self.x._now()
            self.x._sleep(self.x._config.not_found_delay)
            if self.x._now() - before < self.x._config.not_found_delay:
                self.fire(Event.CLOCK_FAULT, "sleep did not advance the clock")
            else:
                self._query()
        elif self.state is State.CONFIRMED_ABSENT:
            now = self.x._now()
            if now < self.auth.expires_at:
                self.fire(Event.AUTHORIZATION_VALID, "resend, same clientOrderId")
            else:
                self.fire(Event.AUTHORIZATION_EXPIRED, self.auth.expires_at.isoformat())
        else:  # pragma: no cover - the loop only calls this for non-terminal states
            raise IllegalTransition(f"no action for {self.state}")

    def _place(self) -> None:
        try:
            order = self.x._venue.place_order(
                self.client_order_id,
                self.auth.symbol,
                trade_side(self.auth.side),
                self.quantity,
                self.proposal.decision_time,
            )
        except ExchangeError as error:
            if error.code in _NOT_A_REJECTION:
                self.fire(Event.OUTCOME_UNKNOWN, str(error))
            else:
                self.fire(Event.PLACE_REJECTED, str(error))
            return
        except Exception as error:  # noqa: BLE001 - any other failure: outcome unknown
            self.fire(Event.OUTCOME_UNKNOWN, f"{type(error).__name__}: {error}")
            return
        self._found(order)

    def _query(self) -> None:
        try:
            order = self.x._venue.query_order(self.client_order_id)
        except ExchangeError as error:
            if error.code != "NOT_FOUND":
                self.fire(Event.QUERY_UNKNOWN, str(error))
                return
            answers = self._not_found_answers() + 1
            if answers >= self.x._config.absence_queries:
                self.fire(Event.ABSENCE_CONFIRMED, f"NOT_FOUND x{answers}")
            else:
                self.fire(Event.NOT_FOUND, f"NOT_FOUND x{answers}")
            return
        except Exception as error:  # noqa: BLE001 - the answer is not known
            self.fire(Event.QUERY_UNKNOWN, f"{type(error).__name__}: {error}")
            return
        self._found(order)

    def _not_found_answers(self) -> int:
        """NOT_FOUND answers since the last placement attempt."""
        count = 0
        for transition in reversed(self.transitions):
            if transition.event is not Event.NOT_FOUND:
                break
            count += 1
        return count

    def _found(self, order: Order) -> None:
        expected = (
            self.client_order_id,
            self.auth.symbol,
            trade_side(self.auth.side),
            self.quantity,
            self.proposal.decision_time,
        )
        actual = (
            order.client_order_id,
            order.symbol,
            order.side,
            order.orig_qty,
            order.decision_time,
        )
        if actual != expected or order.executed_qty > self.quantity:
            self.order = order
            self.fire(Event.ORDER_MISMATCH, f"sent {expected}, venue has {actual}")
            return
        self.order = order
        if order.status is OrderStatus.FILLED and order.executed_qty == self.quantity:
            self.fire(
                Event.FILL_CONFIRMED, f"{order.executed_qty} @ {order.fill_price}"
            )
        elif order.status is OrderStatus.EXPIRED:
            self.fire(
                Event.PARTIAL_FILL_CONFIRMED,
                f"{order.executed_qty} of {order.orig_qty} @ {order.fill_price}",
            )
        else:
            self.fire(Event.ORDER_MISMATCH, f"status {order.status} inconsistent")

    def _finish(self) -> ExecutionResult:
        released = False
        if self.state in _RELEASE_AFTER or (
            self.state is State.REFUSED and self.release_unredeemed
        ):
            released = self.x._governor.release(self.auth, self.x._now()) is None
        move = self._adverse_move_bps()
        return ExecutionResult(
            state=self.state,
            client_order_id=self.client_order_id,
            order=self.order,
            refusal=self.refusal,
            released=released,
            adverse_move_bps=move,
            slippage_breach=move is not None and move > self.auth.max_slippage_bps,
            transitions=tuple(self.transitions),
        )

    def _adverse_move_bps(self) -> Decimal | None:
        if self.order is None or self.order.executed_qty == 0:
            return None
        mark = self.actual.mark_price
        move = _DEC.subtract(self.order.fill_price, mark)
        if self.auth.side is Side.SELL:
            move = _DEC.minus(move)
        return _DEC.divide(_DEC.multiply(move, _BPS), mark)
