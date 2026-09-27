"""Task 23: reconciliation and startup against the Task 18 simulator, and the
hand-over from the Task 22 executor (section 19 "Startup reconciliation
required"; section 22 "exit FREEZE only after reconciliation")."""

from __future__ import annotations

import socket
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from aqt.backtest.costs import Side as TradeSide
from aqt.data.bars import Bar, BarSeries
from aqt.execution.machine import Executor, State
from aqt.execution.orders import ExecutorConfig, client_order_id_for
from aqt.execution.reconcile import LocalRecord, reconcile, settle
from aqt.execution.safety import IncidentLog, startup_check
from aqt.execution.simulator import (
    ExchangeError,
    Fault,
    Order,
    Scenario,
    SimulatedExchange,
    SimulatedTimeout,
    SymbolFilters,
)
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
CONFIG = ExecutorConfig(not_found_delay=timedelta(seconds=10), absence_queries=2)
START = {"USDT": Decimal(1000), "BTC": Decimal(0)}


@pytest.fixture(autouse=True)
def _no_sockets(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_: object, **__: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)


def _exchange(scenario: Scenario | None = None) -> SimulatedExchange:
    start = MIDNIGHT - 6 * HOUR
    bars = [Bar(start + i * HOUR, 100.0, 100.0, 100.0, 100.0, 5.0) for i in range(6)]
    bars.append(Bar(MIDNIGHT, 100.1, 100.1, 100.1, 100.1, 5.0))
    return SimulatedExchange(
        {"BTCUSDT": BarSeries("BTCUSDT", tuple(bars))},
        {"BTCUSDT": FILTERS},
        dict(START),
        scenario=scenario,
    )


def test_a_clean_account_starts(tmp_path: Path) -> None:
    incidents = IncidentLog(tmp_path / "incidents.jsonl")
    decision = startup_check(_exchange(), LocalRecord(START), {}, incidents, MIDNIGHT)
    assert decision.start and decision.reasons == ()
    assert incidents.open_incidents() == ()


def test_an_injected_balance_mismatch_refuses_to_start(tmp_path: Path) -> None:
    incidents = IncidentLog(tmp_path / "incidents.jsonl")
    believed = LocalRecord({"USDT": Decimal(1000), "BTC": Decimal("0.5")})
    decision = startup_check(_exchange(), believed, {}, incidents, MIDNIGHT)
    assert not decision.start
    assert "BTC: venue 0, expected 0.5" in decision.reasons[0]
    assert len(incidents.open_incidents()) == 1  # the mismatch is an incident
    # And the open incident alone keeps refusing, even once the record is right.
    again = startup_check(_exchange(), LocalRecord(START), {}, incidents, MIDNIGHT)
    assert not again.start and "open incidents" in again.reasons[0]


def test_a_difference_within_tolerance_passes_and_beyond_it_fails() -> None:
    believed = LocalRecord({"USDT": Decimal("1000.004"), "BTC": Decimal(0)})
    ok = reconcile(_exchange(), believed, {"USDT": Decimal("0.005")}, MIDNIGHT)
    assert ok.passed
    tight = reconcile(_exchange(), believed, {"USDT": Decimal("0.001")}, MIDNIGHT)
    assert not tight.passed


class _WithOpenOrder(SimulatedExchange):
    """A venue showing an order the system never sent."""

    def __init__(self, resting: Order) -> None:
        start = MIDNIGHT - 6 * HOUR
        bars = [
            Bar(start + i * HOUR, 100.0, 100.0, 100.0, 100.0, 5.0) for i in range(7)
        ]
        super().__init__(
            {"BTCUSDT": BarSeries("BTCUSDT", tuple(bars))},
            {"BTCUSDT": FILTERS},
            dict(START),
        )
        self._resting = resting

    def open_orders(self) -> tuple[Order, ...]:
        return (self._resting,)


def test_an_untracked_open_order_refuses_to_start(tmp_path: Path) -> None:
    exchange = _exchange()
    placed = exchange.place_order(
        "stray",
        "BTCUSDT",
        TradeSide.BUY,
        Decimal("1"),
        MIDNIGHT,
        limit_price=Decimal("101"),
    )
    venue = _WithOpenOrder(placed)
    incidents = IncidentLog(tmp_path / "incidents.jsonl")
    decision = startup_check(venue, LocalRecord(START), {}, incidents, MIDNIGHT)
    assert not decision.start
    assert "stray: open on the venue with no local record" in decision.reasons[0]


def test_an_order_whose_status_cannot_be_read_fails_reconciliation() -> None:
    exchange = _exchange(Scenario({"q1": Fault(unknown_queries=5)}))
    report = reconcile(exchange, LocalRecord(START, {"q1": None}), {}, MIDNIGHT)
    assert not report.passed
    assert "q1: unresolved" in report.differences[0]


def test_a_venue_order_that_differs_from_the_local_copy_fails() -> None:
    exchange = _exchange()
    order = exchange.place_order("o1", "BTCUSDT", TradeSide.BUY, Decimal("1"), MIDNIGHT)
    altered = replace(order, executed_qty=Decimal("0.5"))
    after = LocalRecord(START, {"o1": altered})
    report = reconcile(exchange, after, {}, MIDNIGHT)
    assert not report.passed
    assert "o1: venue differs from local copy" in report.differences


def test_a_hidden_fill_is_found_and_only_then_released() -> None:
    """The Task 22 hand-over (Astra R-2): the executor ended without seeing
    its fill and kept the reservation. Reconciliation finds the fill, the
    balances agree with it, and only then is the reservation released; the
    next decision starts from the reconciled holdings."""
    nonce = "h" * 32
    auth_probe = Authorization(
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
        nonce=nonce,
    )
    order_id = client_order_id_for(auth_probe)
    exchange = _exchange(Scenario({order_id: Fault(timeout=True, not_found_queries=2)}))
    nonces = iter([nonce, "k" * 32])
    governor = Governor(GOVERNOR, nonce_source=lambda: next(nonces))
    state = ActualState("BTCUSDT", Decimal(0), Decimal(1000), Decimal(100), MIDNIGHT)
    proposal = Proposal("BTCUSDT", 0.5, MIDNIGHT)
    authorization = governor.decide(proposal, state, MIDNIGHT)
    assert isinstance(authorization, Authorization)
    now = [MIDNIGHT]

    def sleep(duration: timedelta) -> None:
        now[0] += duration + GOVERNOR.authorization_ttl

    executor = Executor(
        governor, exchange, FILTERS, CONFIG, clock=lambda: now[0], sleep=sleep
    )
    result = executor.execute(authorization, proposal, state)
    assert result.state is State.NEW_AUTHORIZATION_REQUIRED
    assert result.order is None and not result.released

    local = LocalRecord(START, {order_id: result.order})
    report = reconcile(exchange, local, {}, now[0])
    assert report.passed, report.differences
    found = report.resolved[order_id]
    assert found is not None and found.executed_qty == Decimal("5.000")
    assert report.next_record().balances["BTC"] == Decimal("5.000")

    assert settle(report, governor, [authorization]) == (nonce,)
    held = ActualState(
        "BTCUSDT",
        report.actual_balances["BTC"],
        report.actual_balances["USDT"],
        Decimal("100.1"),
        now[0],
        last_risk_increase_time=MIDNIGHT,
    )
    # No longer blocked by the reservation; the next refusal is the governor's
    # own rule (at most one increase a day), judged on the real holdings.
    later = governor.decide(Proposal("BTCUSDT", 0.9, MIDNIGHT), held, now[0])
    assert getattr(later, "code", None) is not RefusalCode.OUTSTANDING_AUTHORIZATION


def test_a_failed_reconciliation_releases_nothing() -> None:
    exchange = _exchange()
    report = reconcile(exchange, LocalRecord({"BTC": Decimal(9)}), {}, MIDNIGHT)
    governor = Governor(GOVERNOR)
    with pytest.raises(ValueError, match="only a passed"):
        settle(report, governor, [])
    with pytest.raises(ValueError, match="no record"):
        report.next_record()


def test_an_unreadable_venue_fails_reconciliation() -> None:
    class Broken(SimulatedExchange):
        def balances(self) -> dict[str, Decimal]:
            raise SimulatedTimeout("no answer")

    start = MIDNIGHT - 6 * HOUR
    bars = [Bar(start + i * HOUR, 100.0, 100.0, 100.0, 100.0, 5.0) for i in range(7)]
    venue = Broken(
        {"BTCUSDT": BarSeries("BTCUSDT", tuple(bars))},
        {"BTCUSDT": FILTERS},
        dict(START),
    )
    report = reconcile(venue, LocalRecord(START), {}, MIDNIGHT)
    assert not report.passed
    assert report.differences[0].startswith("venue unreadable")


def test_a_server_error_on_the_query_is_unresolved_not_absent() -> None:
    class Busy(SimulatedExchange):
        def query_order(self, client_order_id: str) -> Order:
            raise ExchangeError("SERVER_BUSY", "try later")

    start = MIDNIGHT - 6 * HOUR
    bars = [Bar(start + i * HOUR, 100.0, 100.0, 100.0, 100.0, 5.0) for i in range(7)]
    venue = Busy(
        {"BTCUSDT": BarSeries("BTCUSDT", tuple(bars))},
        {"BTCUSDT": FILTERS},
        dict(START),
    )
    report = reconcile(venue, LocalRecord(START, {"b1": None}), {}, MIDNIGHT)
    assert not report.passed
    assert report.differences == ("b1: unresolved (SERVER_BUSY: try later)",)


def test_a_fill_the_venue_still_hides_fails_on_the_balances() -> None:
    """NOT_FOUND counts as absent, but a hidden fill still moved the
    balances, so the reconciliation fails instead of passing blind."""
    exchange = _exchange(Scenario({"h1": Fault(not_found_queries=9)}))
    exchange.place_order("h1", "BTCUSDT", TradeSide.BUY, Decimal("1"), MIDNIGHT)
    report = reconcile(exchange, LocalRecord(START, {"h1": None}), {}, MIDNIGHT)
    assert not report.passed
    assert any(d.startswith("BTC: venue 1") for d in report.differences)
