"""Task 23: HALT, FLATTEN, FREEZE and incidents (Constitution sections 14, 22)."""

from __future__ import annotations

import itertools
import socket
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from aqt.core.ledger import LedgerError
from aqt.data.bars import Bar, BarSeries
from aqt.execution.reconcile import LocalRecord, reconcile
from aqt.execution.safety import (
    MODE_TRANSITIONS,
    FlattenBounds,
    HaltOverride,
    IncidentLog,
    Mode,
    OwnerAction,
    SafetyController,
    SafetyError,
    Trigger,
)
from aqt.execution.simulator import SimulatedExchange, SymbolFilters
from aqt.monitoring.alerts import AlertRouter
from aqt.monitoring.events import Event, EventKind, Severity

T0 = datetime(2026, 1, 5, tzinfo=UTC)
HOUR = timedelta(hours=1)
FILTERS = SymbolFilters(
    step_size=Decimal("0.001"),
    min_qty=Decimal("0.001"),
    max_qty=Decimal("100"),
    min_notional=Decimal("10"),
)
BOUNDS = FlattenBounds(max_step_fraction=Decimal("0.5"), max_slippage_bps=Decimal("50"))
TOLERANCE: dict[str, Decimal] = {}


@pytest.fixture(autouse=True)
def _no_sockets(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_: object, **__: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)


@dataclass
class ListSink:
    min_severity: Severity = Severity.INFO
    events: list[Event] = field(default_factory=list)

    def write(self, event: Event) -> None:
        self.events.append(event)


def _series(prices: list[float]) -> BarSeries:
    return BarSeries(
        "BTCUSDT",
        tuple(Bar(T0 + i * HOUR, p, p, p, p, 5.0) for i, p in enumerate(prices)),
    )


def _exchange(btc: str = "1", prices: list[float] | None = None) -> SimulatedExchange:
    series = _series(prices or [100.0] * 16)
    return SimulatedExchange(
        {"BTCUSDT": series},
        {"BTCUSDT": FILTERS},
        {"USDT": Decimal("0"), "BTC": Decimal(btc)},
    )


def _controller(
    tmp_path: Path, mode: Mode
) -> tuple[SafetyController, ListSink, IncidentLog]:
    sink = ListSink()
    incidents = IncidentLog(tmp_path / "incidents.jsonl")
    return (
        SafetyController(AlertRouter([sink]), incidents, T0, mode=mode),
        sink,
        incidents,
    )


class Spy:
    """A venue that records every call and must not be used."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def __getattr__(self, name: str) -> object:
        def record(*_: object, **__: object) -> object:
            self.calls.append(name)
            raise AssertionError(f"venue.{name} called")

        return record


def _tick(controller: SafetyController, venue: object, hour: int) -> object:
    return controller.tick(
        venue,  # type: ignore[arg-type]
        "BTCUSDT",
        FILTERS,
        BOUNDS,
        Decimal("100"),
        T0 + (hour + 3) * HOUR,  # the cost model needs 3 bars of history
        T0 + (hour + 3) * HOUR,
    )


def test_halt_while_holding_exposure_places_no_order(tmp_path: Path) -> None:
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_HALT, T0, "owner pressed HALT")
    assert controller.mode is Mode.HALT
    assert not controller.may_trade()
    spy = Spy()
    for hour in range(1, 6):
        assert _tick(controller, spy, hour) is None
    assert spy.calls == []


def test_flatten_reduces_monotonically_and_never_crosses_zero(tmp_path: Path) -> None:
    exchange = _exchange(btc="1.234")
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_FLATTEN, T0, "owner pressed FLATTEN")
    held = [exchange.balances()["BTC"]]
    for hour in range(1, 11):
        if controller.mode is not Mode.FLATTEN:
            break
        _tick(controller, exchange, hour)
        held.append(exchange.balances()["BTC"])
    assert all(b <= a for a, b in itertools.pairwise(held))
    assert all(b >= 0 for b in held)
    # Only an unsellable remainder may be left: none here, since 1.234 BTC
    # halves to 0.155 and then sells whole.
    assert held[-1] == 0
    assert controller.mode is Mode.HALT
    # Halves: 1.234 -> 0.617 -> ... every step is a sell.
    assert held[1] == Decimal("0.617")


def test_flatten_never_sells_more_than_is_held(tmp_path: Path) -> None:
    exchange = _exchange(btc="0.0015")  # below twice the minimum: sells all
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_FLATTEN, T0)
    order = _tick(controller, exchange, 1)
    # 0.001 BTC at 100 is under the 10 USDT notional minimum: nothing sold.
    assert order is None
    assert exchange.balances()["BTC"] == Decimal("0.0015")
    assert controller.mode is Mode.HALT


def test_flatten_with_the_price_beyond_its_cap_sells_nothing(tmp_path: Path) -> None:
    exchange = _exchange(prices=[100.0] * 3 + [90.0] * 3)  # 10% gap down
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_FLATTEN, T0)
    order = _tick(controller, exchange, 0)
    assert order is not None and order.executed_qty == 0
    assert exchange.balances()["BTC"] == Decimal("1")
    assert controller.mode is Mode.FLATTEN  # tries again next time


def test_freeze_takes_no_action_while_prices_move(tmp_path: Path) -> None:
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.AMBIGUOUS_ORDER, T0, "order aqt-x unknown")
    spy = Spy()
    for hour in range(1, 10):
        assert _tick(controller, spy, hour) is None
    assert spy.calls == []
    assert controller.mode is Mode.FREEZE
    with pytest.raises(SafetyError):
        controller.trigger(Trigger.OWNER_FLATTEN, T0 + HOUR)
    assert controller.mode is Mode.FREEZE


def test_exiting_freeze_needs_a_passed_reconciliation_after_it(tmp_path: Path) -> None:
    exchange = _exchange()
    early = reconcile(exchange, LocalRecord(exchange.balances()), TOLERANCE, T0)
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.AMBIGUOUS_ORDER, T0 + HOUR)
    wrong = LocalRecord({"USDT": Decimal("0"), "BTC": Decimal("2")})
    failed = reconcile(exchange, wrong, TOLERANCE, T0 + 2 * HOUR)
    with pytest.raises(SafetyError, match="reconciliation failed"):
        controller.exit_freeze(failed, T0 + 2 * HOUR)
    with pytest.raises(SafetyError, match="does not follow"):
        controller.exit_freeze(early, T0 + 2 * HOUR)
    assert controller.mode is Mode.FREEZE
    passed = reconcile(
        exchange, LocalRecord(exchange.balances()), TOLERANCE, T0 + 3 * HOUR
    )
    assert controller.exit_freeze(passed, T0 + 3 * HOUR) is Mode.HALT


def _override(
    controller: SafetyController, incidents: IncidentLog, at: datetime
) -> HaltOverride:
    exchange = _exchange()
    report = reconcile(exchange, LocalRecord(exchange.balances()), TOLERANCE, at)
    return HaltOverride(
        incident_ids=incidents.open_incidents(),
        written_record="HALT pressed to test the procedure; nothing traded.",
        cause="owner drill",
        reconciliation=report,
        owner_action=OwnerAction(actor="owner", statement="resume trading"),
        timestamp=at,
    )


@pytest.mark.parametrize(
    ("missing", "message"),
    [
        ("written_record", "written incident record"),
        ("cause", "identified or bounded cause"),
        ("reconciliation", "successful reconciliation"),
        ("owner_action", "explicit owner action"),
        ("timestamp", "timestamp"),
    ],
)
def test_a_halt_override_missing_any_artifact_is_refused(
    tmp_path: Path, missing: str, message: str
) -> None:
    controller, _, incidents = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_HALT, T0, "drill")
    override = replace(_override(controller, incidents, T0 + HOUR), **{missing: None})
    with pytest.raises(SafetyError, match=message):
        controller.override_halt(override, T0 + HOUR)
    assert controller.mode is Mode.HALT
    assert len(incidents.open_incidents()) == 1


@pytest.mark.parametrize(
    "bad",
    [
        {"written_record": "   "},
        {"cause": ""},
        {"owner_action": OwnerAction(actor="", statement="go")},
        {"owner_action": OwnerAction(actor="owner", statement=" ")},
        {"incident_ids": ()},
        {"incident_ids": ("not-an-incident",)},
        {"timestamp": T0 - HOUR},
    ],
)
def test_empty_or_wrong_artifacts_are_refused_too(
    tmp_path: Path, bad: dict[str, object]
) -> None:
    controller, _, incidents = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_HALT, T0, "drill")
    override = replace(_override(controller, incidents, T0 + HOUR), **bad)
    with pytest.raises(SafetyError):
        controller.override_halt(override, T0 + HOUR)
    assert controller.mode is Mode.HALT


def test_a_failed_or_stale_reconciliation_refuses_the_override(tmp_path: Path) -> None:
    controller, _, incidents = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_HALT, T0 + HOUR, "drill")
    exchange = _exchange()
    stale = reconcile(exchange, LocalRecord(exchange.balances()), TOLERANCE, T0)
    failed = reconcile(
        exchange, LocalRecord({"BTC": Decimal(5)}), TOLERANCE, T0 + 2 * HOUR
    )
    base = _override(controller, incidents, T0 + 2 * HOUR)
    for report in (stale, failed):
        with pytest.raises(SafetyError):
            controller.override_halt(
                replace(base, reconciliation=report), T0 + 2 * HOUR
            )
    assert controller.mode is Mode.HALT


def test_a_complete_override_closes_every_incident_and_resumes(tmp_path: Path) -> None:
    controller, sink, incidents = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_HALT, T0, "drill")
    controller.trigger(Trigger.INCIDENT, T0, "second alarm while halted")
    assert len(incidents.open_incidents()) == 2
    override = _override(controller, incidents, T0 + HOUR)
    assert controller.override_halt(override, T0 + HOUR) is Mode.RUNNING
    assert incidents.open_incidents() == ()
    assert controller.may_trade()
    kinds = [(e.fields["from"], e.fields["to"], e.severity) for e in sink.events]
    assert kinds == [
        ("RUNNING", "HALT", Severity.CRITICAL),
        ("HALT", "HALT", Severity.CRITICAL),
        ("HALT", "RUNNING", Severity.WARNING),
    ]
    assert all(e.kind is EventKind.STATE_TRANSITION for e in sink.events)


def test_every_protective_entry_opens_an_incident_and_is_critical(
    tmp_path: Path,
) -> None:
    controller, sink, incidents = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.RECONCILIATION_FAILED, T0, "mismatch")
    assert len(incidents.open_incidents()) == 1
    assert sink.events[-1].severity is Severity.CRITICAL
    assert sink.events[-1].fields["incident_id"] == incidents.open_incidents()[0]


def test_a_tampered_incident_log_cannot_hide_an_open_incident(tmp_path: Path) -> None:
    controller, _, incidents = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_HALT, T0, "drill")
    data = incidents.path.read_bytes().replace(b"OWNER_HALT", b"OWNER_HALX")
    incidents.path.write_bytes(data)
    with pytest.raises(LedgerError):
        incidents.open_incidents()


def test_time_cannot_go_backwards(tmp_path: Path) -> None:
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_HALT, T0 + HOUR)
    with pytest.raises(SafetyError, match="backwards"):
        controller.trigger(Trigger.INCIDENT, T0)


def test_procedures_cannot_be_triggered_directly(tmp_path: Path) -> None:
    controller, _, _ = _controller(tmp_path, Mode.FREEZE)
    for trigger in (Trigger.FREEZE_EXIT, Trigger.HALT_OVERRIDE):
        with pytest.raises(SafetyError, match="procedure"):
            controller.trigger(trigger, T0)
    assert controller.mode is Mode.FREEZE


def test_every_mode_trigger_pair_is_defined_or_refused(tmp_path: Path) -> None:
    for mode, trigger in itertools.product(Mode, Trigger):
        controller, _, _ = _controller(tmp_path / f"{mode}-{trigger}", Mode.RUNNING)
        (tmp_path / f"{mode}-{trigger}").mkdir()
        controller.mode = mode
        if trigger in (Trigger.FREEZE_EXIT, Trigger.HALT_OVERRIDE):
            continue
        if (mode, trigger) in MODE_TRANSITIONS:
            assert controller.trigger(trigger, T0) is MODE_TRANSITIONS[(mode, trigger)]
        else:
            with pytest.raises(SafetyError, match="not allowed"):
                controller.trigger(trigger, T0)
            assert controller.mode is mode


def test_no_trigger_leaves_freeze_except_reconciliation() -> None:
    out_of_freeze = {
        trigger
        for (mode, trigger), target in MODE_TRANSITIONS.items()
        if mode is Mode.FREEZE and target is not Mode.FREEZE
    }
    assert out_of_freeze == {Trigger.FREEZE_EXIT}
    into_running = {
        t for (_, t), target in MODE_TRANSITIONS.items() if target is Mode.RUNNING
    }
    assert into_running == {Trigger.HALT_OVERRIDE}


def test_flatten_bounds_are_required_values() -> None:
    for fraction in ("0", "1.5", "-0.1"):
        with pytest.raises(ValueError):
            FlattenBounds(
                max_step_fraction=Decimal(fraction), max_slippage_bps=Decimal(1)
            )
    with pytest.raises(ValueError):
        FlattenBounds(max_step_fraction=Decimal("0.5"), max_slippage_bps=Decimal(-1))
