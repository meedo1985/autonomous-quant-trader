"""Task 22: governor -> executor -> Task 18 simulator, offline, synthetic bars.

Each section 21 scenario is scripted as a simulator `Fault`; the balances
show how many orders actually filled.
"""

from __future__ import annotations

import socket
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from aqt.data.bars import Bar, BarSeries
from aqt.execution.machine import Event, ExecutionResult, Executor, State
from aqt.execution.orders import ExecutorConfig, client_order_id_for
from aqt.execution.simulator import Fault, Scenario, SimulatedExchange, SymbolFilters
from aqt.governor.authorization import (
    ActualState,
    Authorization,
    GovernorConfig,
    Proposal,
    RefusalCode,
)
from aqt.governor.machine import Governor

MIDNIGHT = datetime(2026, 1, 5, tzinfo=UTC)
HOUR = timedelta(hours=1)
SECOND = timedelta(seconds=1)
FILTERS = SymbolFilters(
    step_size=Decimal("0.001"),
    min_qty=Decimal("0.001"),
    max_qty=Decimal("100"),
    min_notional=Decimal("10"),
)
GOVERNOR = GovernorConfig(
    max_slippage_bps=Decimal("15"),
    authorization_ttl=timedelta(minutes=2),
    decision_window=timedelta(minutes=5),
)
CONFIG = ExecutorConfig(not_found_delay=10 * SECOND, absence_queries=2)
# Governor nonces are fixed so each test knows the clientOrderId in advance.
NONCE = "n" * 32
ORDER_ID = client_order_id_for(
    Authorization(
        proposal_hash="",
        state_reference="",
        symbol="BTCUSDT",
        side=None,  # type: ignore[arg-type]
        current_exposure=0.0,
        target_exposure=0.0,
        max_base_quantity=Decimal(0),
        max_slippage_bps=Decimal(0),
        issued_at=MIDNIGHT,
        expires_at=MIDNIGHT,
        nonce=NONCE,
    )
)


@pytest.fixture(autouse=True)
def _no_sockets(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_: object, **__: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)


class Clock:
    def __init__(self) -> None:
        self.now = MIDNIGHT

    def __call__(self) -> datetime:
        return self.now

    def sleep(self, duration: timedelta) -> None:
        self.now += duration


def _series() -> BarSeries:
    """Flat bars at 100 up to the 00:00 decision; the fill bar opens at 101."""
    start = MIDNIGHT - 6 * HOUR
    bars = [Bar(start + i * HOUR, 100.0, 100.0, 100.0, 100.0, 5.0) for i in range(6)]
    bars.append(Bar(MIDNIGHT, 101.0, 101.0, 101.0, 101.0, 5.0))
    return BarSeries("BTCUSDT", tuple(bars))


def _run(
    fault: Fault | None = None, *, sleep_extra: timedelta = timedelta(0)
) -> tuple[ExecutionResult, SimulatedExchange, Governor, ActualState, Clock]:
    faults = {} if fault is None else {ORDER_ID: fault}
    exchange = SimulatedExchange(
        {"BTCUSDT": _series()},
        {"BTCUSDT": FILTERS},
        {"USDT": Decimal(1000), "BTC": Decimal(0)},
        scenario=Scenario(faults),
    )
    clock = Clock()
    nonces = iter([NONCE, "m" * 32])
    governor = Governor(GOVERNOR, nonce_source=lambda: next(nonces))
    state = ActualState(
        symbol="BTCUSDT",
        base_quantity=Decimal(0),
        quote_balance=Decimal(1000),
        mark_price=Decimal(100),
        as_of=MIDNIGHT,
    )
    proposal = Proposal("BTCUSDT", 0.5, MIDNIGHT)
    authorization = governor.decide(proposal, state, MIDNIGHT)
    assert isinstance(authorization, Authorization)
    assert client_order_id_for(authorization) == ORDER_ID

    def sleep(duration: timedelta) -> None:
        clock.sleep(duration + sleep_extra)

    executor = Executor(governor, exchange, FILTERS, CONFIG, clock=clock, sleep=sleep)
    return (
        executor.execute(authorization, proposal, state),
        exchange,
        governor,
        state,
        clock,
    )


def result_authorization(governor: Governor) -> Authorization:
    return governor._issued[NONCE]  # noqa: SLF001 - the test's own nonce


def _fills(exchange: SimulatedExchange) -> list[dict[str, str]]:
    return [event for event in exchange.events if event["event"] == "fill"]


def test_a_clean_order_fills_once_at_the_next_open() -> None:
    result, exchange, _, _, _ = _run()
    assert result.state is State.FILLED
    assert result.order is not None and result.order.fill_price == Decimal("101.0")
    assert exchange.balances()["BTC"] == Decimal("5.000")
    assert len(_fills(exchange)) == 1
    # The open gapped 1% above the mark: reported as a breach, not hidden.
    assert result.adverse_move_bps == Decimal("100")
    assert result.slippage_breach


def test_timeout_is_resolved_by_query_without_a_second_order() -> None:
    result, exchange, _, _, _ = _run(Fault(timeout=True))
    assert result.state is State.FILLED
    assert Event.OUTCOME_UNKNOWN in [t.event for t in result.transitions]
    assert len(_fills(exchange)) == 1


def test_not_found_then_found_does_not_resend() -> None:
    result, exchange, _, _, _ = _run(Fault(timeout=True, not_found_queries=1))
    assert result.state is State.FILLED
    assert [t.event for t in result.transitions].count(Event.NOT_FOUND) == 1
    assert len(_fills(exchange)) == 1
    assert not [e for e in exchange.events if e["event"] == "duplicate"]


def test_a_lost_order_confirmed_absent_is_resent_under_the_same_id() -> None:
    result, exchange, _, _, _ = _run(Fault(lost_placements=1))
    assert result.state is State.FILLED
    assert Event.ABSENCE_CONFIRMED in [t.event for t in result.transitions]
    placements = [e for e in exchange.events if e["event"] in {"lost", "fill"}]
    assert [e["client_order_id"] for e in placements] == [ORDER_ID, ORDER_ID]
    assert len(_fills(exchange)) == 1
    assert exchange.balances()["BTC"] == Decimal("5.000")


def test_a_lost_order_after_expiry_needs_a_new_authorization() -> None:
    result, exchange, governor, state, clock = _run(
        Fault(lost_placements=1), sleep_extra=GOVERNOR.authorization_ttl
    )
    assert result.state is State.NEW_AUTHORIZATION_REQUIRED
    assert _fills(exchange) == []
    assert exchange.balances() == {"USDT": Decimal(1000), "BTC": Decimal(0)}
    assert result.released
    # The old authorization is spent; a new one, with a new id, is needed.
    old = governor.redeem(result_authorization(governor), state, clock.now)
    assert old is not None and old.code is RefusalCode.ALREADY_USED
    fresh = governor.decide(Proposal("BTCUSDT", 0.5, MIDNIGHT), state, clock.now)
    assert isinstance(fresh, Authorization)
    assert client_order_id_for(fresh) != ORDER_ID


def test_an_unknown_query_freezes_and_keeps_the_reservation() -> None:
    result, exchange, governor, state, clock = _run(
        Fault(timeout=True, unknown_queries=1)
    )
    assert result.state is State.FREEZE
    assert not result.released
    # The order did fill on the venue; the executor did not guess either way.
    assert len(_fills(exchange)) == 1
    blocked = governor.decide(Proposal("BTCUSDT", 0.4, MIDNIGHT), state, clock.now)
    assert blocked.code is RefusalCode.OUTSTANDING_AUTHORIZATION  # type: ignore[union-attr]


def test_a_partial_fill_is_recorded_and_released() -> None:
    result, exchange, _, _, _ = _run(Fault(fill_fraction=Decimal("0.5")))
    assert result.state is State.PARTIALLY_FILLED
    assert result.order is not None
    assert result.order.executed_qty == Decimal("2.500")
    assert result.released


def test_a_venue_rejection_ends_rejected() -> None:
    # The venue holds too little quote to afford the order.
    exchange = SimulatedExchange(
        {"BTCUSDT": _series()},
        {"BTCUSDT": FILTERS},
        {"USDT": Decimal(10), "BTC": Decimal(0)},
    )
    clock = Clock()
    governor = Governor(GOVERNOR, nonce_source=lambda: NONCE)
    state = ActualState(
        symbol="BTCUSDT",
        base_quantity=Decimal(0),
        quote_balance=Decimal(1000),
        mark_price=Decimal(100),
        as_of=MIDNIGHT,
    )
    proposal = Proposal("BTCUSDT", 0.5, MIDNIGHT)
    authorization = governor.decide(proposal, state, MIDNIGHT)
    assert isinstance(authorization, Authorization)
    executor = Executor(
        governor, exchange, FILTERS, CONFIG, clock=clock, sleep=clock.sleep
    )
    rejected = executor.execute(authorization, proposal, state)
    assert rejected.state is State.REJECTED
    assert rejected.released
    assert _fills(exchange) == []
