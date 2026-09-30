"""Task 23: HALT, FLATTEN, FREEZE and incidents (Constitution sections 14, 22)."""

from __future__ import annotations

import hashlib
import itertools
import socket
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from aqt.core.ledger import LedgerError
from aqt.data.bars import Bar, BarSeries
from aqt.execution.reconcile import AbsenceCheck, LocalRecord, reconcile
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
from aqt.execution.simulator import (
    ExchangeError,
    Fault,
    Order,
    Scenario,
    SimulatedExchange,
    SymbolFilters,
)
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


class FakeClock:
    """A clock that `sleep` advances, as the paper loop's does."""

    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now

    def sleep(self, duration: timedelta) -> None:
        self.now += duration


def _absence(at: datetime) -> AbsenceCheck:
    """Section 21: two NOT_FOUND answers, 10 s apart (owner-set T22-Q1)."""
    clock = FakeClock(at)
    return AbsenceCheck(timedelta(seconds=10), 2, clock.sleep, clock)


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


class FailingSink:
    min_severity = Severity.INFO

    def write(self, event: Event) -> None:
        raise OSError("alert sink failed")


class FailingIncidentLog(IncidentLog):
    def open(self, kind: str, detail: str, at: datetime) -> str:
        raise OSError("incident ledger failed")


class ToggleIncidentLog(IncidentLog):
    fail = True

    def open(self, kind: str, detail: str, at: datetime) -> str:
        if self.fail:
            raise OSError("incident ledger failed")
        return super().open(kind, detail, at)


class RecoveryFailIncidentLog(IncidentLog):
    def open(self, kind: str, detail: str, at: datetime) -> str:
        if kind == "HALT_OVERRIDE_FAILED":
            raise OSError("recovery incident failed")
        return super().open(kind, detail, at)


class ToggleSink:
    min_severity = Severity.INFO
    fail = True

    def write(self, event: Event) -> None:
        if self.fail:
            raise OSError("alert sink failed")


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


def _tick(
    controller: SafetyController,
    venue: object,
    hour: int,
    filters: SymbolFilters = FILTERS,
) -> object:
    return controller.tick(
        venue,  # type: ignore[arg-type]
        "BTCUSDT",
        filters,
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


@pytest.mark.parametrize("alarm", [Trigger.INCIDENT, Trigger.OWNER_HALT])
def test_an_alarm_during_flatten_halts_before_another_order(
    tmp_path: Path, alarm: Trigger
) -> None:
    controller, _, incidents = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_FLATTEN, T0, "owner pressed FLATTEN")

    assert controller.trigger(alarm, T0 + HOUR, "alarm") is Mode.HALT
    assert len(incidents.open_incidents()) == 1
    spy = Spy()
    assert _tick(controller, spy, 1) is None
    assert spy.calls == []


def test_a_failed_alert_cannot_leave_the_controller_running(tmp_path: Path) -> None:
    incidents = IncidentLog(tmp_path / "incidents.jsonl")
    controller = SafetyController(
        AlertRouter([FailingSink()]), incidents, T0, mode=Mode.RUNNING
    )

    with pytest.raises(OSError, match="alert sink failed"):
        controller.trigger(Trigger.OWNER_HALT, T0, "owner pressed HALT")

    assert controller.mode is Mode.FREEZE
    assert not controller.may_trade()
    assert incidents.open_incidents()


def test_a_failed_incident_write_cannot_leave_the_controller_running(
    tmp_path: Path,
) -> None:
    controller = SafetyController(
        AlertRouter([ListSink()]),
        FailingIncidentLog(tmp_path / "incidents.jsonl"),
        T0,
        mode=Mode.RUNNING,
    )

    with pytest.raises(OSError, match="incident ledger failed"):
        controller.trigger(Trigger.OWNER_HALT, T0, "owner pressed HALT")

    assert controller.mode is Mode.FREEZE
    assert not controller.may_trade()


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
    # The final 50% step is below the minimum notional, so the bound wins and
    # the controller HALTs with the unsellable-within-bound remainder.
    assert held[-1] == Decimal("0.155")
    assert controller.mode is Mode.HALT
    # Every submitted step is at most half of the balance before it.
    assert held[1] == Decimal("0.617")
    assert all(
        a - b <= a * BOUNDS.max_step_fraction for a, b in itertools.pairwise(held)
    )


def test_flatten_never_sells_more_than_is_held(tmp_path: Path) -> None:
    exchange = _exchange(btc="0.0015")
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_FLATTEN, T0)
    order = _tick(controller, exchange, 1)
    # 0.001 BTC at 100 is under the 10 USDT notional minimum: nothing sold.
    assert order is None
    assert exchange.balances()["BTC"] == Decimal("0.0015")
    assert controller.mode is Mode.HALT


def test_flatten_caps_each_step_at_the_venue_maximum(tmp_path: Path) -> None:
    exchange = _exchange(btc="300")
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_FLATTEN, T0)

    order = _tick(controller, exchange, 1)

    assert order is not None and order.orig_qty == FILTERS.max_qty
    assert exchange.balances()["BTC"] == Decimal("200")
    assert controller.mode is Mode.FLATTEN


def test_flatten_caps_each_step_at_the_venue_maximum_notional(
    tmp_path: Path,
) -> None:
    filters = replace(FILTERS, max_notional=Decimal("20"))
    exchange = SimulatedExchange(
        {"BTCUSDT": _series([100.0] * 16)},
        {"BTCUSDT": filters},
        {"USDT": Decimal(0), "BTC": Decimal(1)},
    )
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_FLATTEN, T0)

    order = _tick(controller, exchange, 1, filters)

    assert order is not None and order.orig_qty == Decimal("0.2")
    assert exchange.balances()["BTC"] == Decimal("0.8")
    assert controller.mode is Mode.FLATTEN


def test_an_unexpected_flatten_filter_reject_freezes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exchange = _exchange()

    def reject(*args: object, **kwargs: object) -> Order:
        raise ExchangeError("FILTER_LOT_SIZE", "venue filters changed")

    monkeypatch.setattr(exchange, "place_order", reject)
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_FLATTEN, T0)

    assert _tick(controller, exchange, 1) is None
    assert controller.mode is Mode.FREEZE
    assert exchange.balances()["BTC"] == Decimal("1")


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


def test_a_failed_override_alert_keeps_halt_recoverable(tmp_path: Path) -> None:
    incidents = IncidentLog(tmp_path / "incidents.jsonl")
    original = incidents.open(str(Trigger.OWNER_HALT), "drill", T0)
    controller = SafetyController(
        AlertRouter([FailingSink()]), incidents, T0, mode=Mode.HALT
    )
    override = _override(controller, incidents, T0 + HOUR)

    with pytest.raises(OSError, match="alert sink failed"):
        controller.override_halt(override, T0 + HOUR)

    assert controller.mode is Mode.HALT
    open_incidents = incidents.open_incidents()
    assert original not in open_incidents
    assert len(open_incidents) == 1


def test_a_failed_override_invalidates_its_earlier_reconciliation(
    tmp_path: Path,
) -> None:
    incidents = IncidentLog(tmp_path / "incidents.jsonl")
    incidents.open(str(Trigger.OWNER_HALT), "drill", T0)
    sink = ToggleSink()
    sink.fail = False
    controller = SafetyController(AlertRouter([sink]), incidents, T0, mode=Mode.HALT)
    exchange = _exchange()
    old = reconcile(exchange, LocalRecord(exchange.balances()), TOLERANCE, T0 + HOUR)
    first = replace(_override(controller, incidents, T0 + 2 * HOUR), reconciliation=old)

    sink.fail = True
    with pytest.raises(OSError, match="alert sink failed"):
        controller.override_halt(first, T0 + 2 * HOUR)
    assert controller.entered_at == T0 + 2 * HOUR

    sink.fail = False
    stale = replace(_override(controller, incidents, T0 + 3 * HOUR), reconciliation=old)
    with pytest.raises(SafetyError, match="predates"):
        controller.override_halt(stale, T0 + 3 * HOUR)
    assert (
        controller.override_halt(
            _override(controller, incidents, T0 + 3 * HOUR), T0 + 3 * HOUR
        )
        is Mode.RUNNING
    )


def test_a_later_halt_incident_invalidates_an_older_reconciliation(
    tmp_path: Path,
) -> None:
    controller, _, incidents = _controller(tmp_path, Mode.RUNNING)
    exchange = _exchange()
    controller.trigger(Trigger.OWNER_HALT, T0, "drill")
    old = reconcile(exchange, LocalRecord(exchange.balances()), TOLERANCE, T0 + HOUR)
    controller.trigger(Trigger.INCIDENT, T0 + 2 * HOUR, "later incident")
    override = replace(
        _override(controller, incidents, T0 + 3 * HOUR), reconciliation=old
    )

    with pytest.raises(SafetyError, match="predates"):
        controller.override_halt(override, T0 + 3 * HOUR)

    assert controller.mode is Mode.HALT


def test_a_later_freeze_incident_invalidates_an_older_reconciliation(
    tmp_path: Path,
) -> None:
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    exchange = _exchange()
    controller.trigger(Trigger.AMBIGUOUS_ORDER, T0, "unknown order")
    old = reconcile(exchange, LocalRecord(exchange.balances()), TOLERANCE, T0 + HOUR)
    controller.trigger(Trigger.RECONCILIATION_FAILED, T0 + 2 * HOUR, "later mismatch")

    with pytest.raises(SafetyError, match="does not follow"):
        controller.exit_freeze(old, T0 + 3 * HOUR)

    assert controller.mode is Mode.FREEZE


def test_a_failed_incident_write_can_be_recorded_then_recovered(
    tmp_path: Path,
) -> None:
    incidents = ToggleIncidentLog(tmp_path / "incidents.jsonl")
    controller = SafetyController(
        AlertRouter([ListSink()]), incidents, T0, mode=Mode.RUNNING
    )
    with pytest.raises(OSError, match="incident ledger failed"):
        controller.trigger(Trigger.OWNER_HALT, T0, "owner pressed HALT")
    assert controller.mode is Mode.FREEZE

    incidents.fail = False
    controller.trigger(Trigger.OWNER_HALT, T0 + HOUR, "record failed HALT")
    exchange = _exchange()
    report = reconcile(
        exchange, LocalRecord(exchange.balances()), TOLERANCE, T0 + 2 * HOUR
    )
    assert controller.exit_freeze(report, T0 + 2 * HOUR) is Mode.HALT
    assert incidents.open_incidents()
    assert (
        controller.override_halt(
            _override(controller, incidents, T0 + 3 * HOUR), T0 + 3 * HOUR
        )
        is Mode.RUNNING
    )


def test_a_failed_override_recovery_write_can_be_recorded_then_retried(
    tmp_path: Path,
) -> None:
    incidents = RecoveryFailIncidentLog(tmp_path / "incidents.jsonl")
    incidents.open(str(Trigger.OWNER_HALT), "drill", T0)
    sink = ToggleSink()
    controller = SafetyController(AlertRouter([sink]), incidents, T0, mode=Mode.HALT)

    with pytest.raises(OSError, match="recovery incident failed"):
        controller.override_halt(_override(controller, incidents, T0 + HOUR), T0 + HOUR)
    assert controller.mode is Mode.HALT
    assert controller.entered_at == T0 + HOUR
    assert incidents.open_incidents() == ()

    sink.fail = False
    controller.trigger(Trigger.OWNER_HALT, T0 + 2 * HOUR, "record failed override")
    assert (
        controller.override_halt(
            _override(controller, incidents, T0 + 3 * HOUR), T0 + 3 * HOUR
        )
        is Mode.RUNNING
    )


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
        controller.trigger(Trigger.OWNER_FLATTEN, T0)
    assert controller.mode is Mode.HALT


@pytest.mark.parametrize(
    ("alarm", "target"),
    [
        (Trigger.OWNER_HALT, Mode.HALT),
        (Trigger.INCIDENT, Mode.HALT),
        (Trigger.LOSS_STOP, Mode.FLATTEN),
        (Trigger.AMBIGUOUS_ORDER, Mode.FREEZE),
        (Trigger.RECONCILIATION_FAILED, Mode.FREEZE),
    ],
)
def test_a_late_alarm_is_never_refused_while_running(
    tmp_path: Path, alarm: Trigger, target: Mode
) -> None:
    """F23-1: a stale timestamp must not leave the controller RUNNING."""
    controller, _, incidents = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_HALT, T0 + 2 * HOUR, "drill")
    controller.override_halt(
        _override(controller, incidents, T0 + 3 * HOUR), T0 + 3 * HOUR
    )
    assert controller.mode is Mode.RUNNING

    assert controller.trigger(alarm, T0 + 2 * HOUR, "late") is target
    assert not controller.may_trade()
    assert controller.entered_at == T0 + 3 * HOUR
    assert len(incidents.open_incidents()) == 1


def test_a_late_alarm_during_flatten_halts_it(tmp_path: Path) -> None:
    exchange = _exchange()
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_FLATTEN, T0)
    assert _tick(controller, exchange, 1) is not None
    assert controller.trigger(Trigger.INCIDENT, T0, "late") is Mode.HALT
    spy = Spy()
    assert _tick(controller, spy, 2) is None
    assert spy.calls == []


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


def test_the_loss_stop_flattens_and_opens_an_incident(tmp_path: Path) -> None:
    """Owner setting S-4: the L-03 stop sells in FLATTEN steps, then HALTs,
    but never out of HALT: the owner's HALT wins (F24-1)."""
    for start, target in ((Mode.RUNNING, Mode.FLATTEN), (Mode.HALT, Mode.HALT)):
        controller, _, incidents = _controller(tmp_path / str(start), start)
        (tmp_path / str(start)).mkdir()
        assert controller.trigger(Trigger.LOSS_STOP, T0, "20% below peak") is target
        assert not controller.may_trade()
        assert len(incidents.open_incidents()) == 1
    frozen, _, _ = _controller(tmp_path / "frozen", Mode.FREEZE)
    (tmp_path / "frozen").mkdir()
    assert (
        frozen.trigger(Trigger.LOSS_STOP, T0) is Mode.FREEZE
    )  # no exit before reconciliation


def test_flatten_takes_one_step_per_decision_bar(tmp_path: Path) -> None:
    """F23-3: repeated ticks for one bar must not compound the 50% bound."""
    exchange = _exchange()
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_FLATTEN, T0)
    assert _tick(controller, exchange, 1) is not None
    for _ in range(3):
        assert _tick(controller, exchange, 1) is None
    assert exchange.balances()["BTC"] == Decimal("0.5")
    assert _tick(controller, exchange, 2) is not None
    assert exchange.balances()["BTC"] == Decimal("0.25")


@pytest.mark.parametrize("mark", [Decimal("NaN"), Decimal("0"), Decimal("-5")])
def test_an_invalid_mark_price_is_a_flatten_fault(
    tmp_path: Path, mark: Decimal
) -> None:
    """F23-4: validated even without a maximum notional; never FLATTEN_DONE."""
    controller, _, incidents = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_FLATTEN, T0)
    spy = Spy()
    order = controller.tick(
        spy,  # type: ignore[arg-type]
        "BTCUSDT",
        FILTERS,
        BOUNDS,
        mark,
        T0 + 4 * HOUR,
        T0 + 4 * HOUR,
    )
    assert order is None
    assert spy.calls == []
    assert controller.mode is Mode.FREEZE
    assert len(incidents.open_incidents()) == 1


def _frozen_with_unknown_flatten_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[SafetyController, IncidentLog, SimulatedExchange, str]:
    exchange = _exchange()
    controller, _, incidents = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_FLATTEN, T0)

    def timeout(*args: object, **kwargs: object) -> Order:
        raise TimeoutError("no response")

    with monkeypatch.context() as patch:
        patch.setattr(exchange, "place_order", timeout)
        assert _tick(controller, exchange, 1) is None
    assert controller.mode is Mode.FREEZE
    [cid] = controller.sent
    assert controller.sent[cid] is None
    return controller, incidents, exchange, cid


def test_recovery_needs_a_report_that_resolved_every_flatten_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F23-2: a passed report that never queried the order is refused."""
    controller, incidents, exchange, cid = _frozen_with_unknown_flatten_order(
        tmp_path, monkeypatch
    )
    at = T0 + 5 * HOUR
    blind = reconcile(exchange, LocalRecord(exchange.balances()), TOLERANCE, at)
    assert blind.passed
    with pytest.raises(SafetyError, match="did not resolve"):
        controller.exit_freeze(blind, at)
    assert controller.mode is Mode.FREEZE

    record = LocalRecord(exchange.balances(), controller.sent)
    full = reconcile(exchange, record, TOLERANCE, at, _absence(at))
    assert full.passed and cid in full.resolved
    assert controller.exit_freeze(full, full.at) is Mode.HALT  # after the waits
    assert controller.sent == {}


def test_the_override_needs_a_report_that_resolved_every_flatten_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    controller, incidents, exchange, cid = _frozen_with_unknown_flatten_order(
        tmp_path, monkeypatch
    )
    # OWNER_HALT is absorbed by FREEZE; reach HALT without resolving `cid`.
    controller.mode = Mode.HALT
    at = T0 + 5 * HOUR
    with pytest.raises(SafetyError, match="HALT override refused: .*did not resolve"):
        controller.override_halt(_override(controller, incidents, at), at)
    assert controller.mode is Mode.HALT

    record = LocalRecord(exchange.balances(), controller.sent)
    checked = reconcile(exchange, record, TOLERANCE, at, _absence(at))
    full = replace(_override(controller, incidents, checked.at), reconciliation=checked)
    assert controller.override_halt(full, checked.at) is Mode.RUNNING
    assert controller.sent == {}


def test_a_future_decision_time_is_a_flatten_fault(tmp_path: Path) -> None:
    """F23R-3: a future decision bar must not silently stall FLATTEN."""
    controller, _, incidents = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_FLATTEN, T0)
    spy = Spy()
    order = controller.tick(
        spy,  # type: ignore[arg-type]
        "BTCUSDT",
        FILTERS,
        BOUNDS,
        Decimal("100"),
        T0 + 10 * HOUR,
        T0 + 4 * HOUR,
    )
    assert order is None
    assert spy.calls == []
    assert controller.mode is Mode.FREEZE
    assert len(incidents.open_incidents()) == 1


def test_the_loss_stop_sells_everything_then_halts(tmp_path: Path) -> None:
    """S-4 end to end: bounded steps, a repeat stop keeps selling, then HALT."""
    exchange = _exchange(btc="1")
    controller, _, incidents = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.LOSS_STOP, T0, "20% below peak")
    held = [exchange.balances()["BTC"]]
    for hour in range(1, 12):
        if controller.mode is not Mode.FLATTEN:
            break
        _tick(controller, exchange, hour)
        held.append(exchange.balances()["BTC"])
        if hour == 1:
            late = controller.trigger(Trigger.LOSS_STOP, T0 + 4 * HOUR, "again")
            assert late is Mode.FLATTEN
    assert held[1] == Decimal("0.5")
    assert all(b >= 0 for b in held)
    assert all(
        a - b <= a * BOUNDS.max_step_fraction for a, b in itertools.pairwise(held)
    )
    assert controller.mode is Mode.HALT
    assert held[-1] < Decimal("0.2")
    assert len(incidents.open_incidents()) == 3  # two stops and the HALT


def test_only_a_passed_reconciliation_settles_flatten_orders(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F23R-1: settling removes exactly the resolved ids, never on failure."""
    controller, _, exchange, cid = _frozen_with_unknown_flatten_order(
        tmp_path, monkeypatch
    )
    wrong = LocalRecord({"BTC": Decimal(5)}, controller.sent)
    failed = reconcile(exchange, wrong, TOLERANCE, T0 + 5 * HOUR)
    with pytest.raises(SafetyError, match="settles nothing"):
        controller.settle_flatten(failed)
    assert cid in controller.sent
    record = LocalRecord(exchange.balances(), controller.sent)
    controller.settle_flatten(
        reconcile(exchange, record, TOLERANCE, T0 + 5 * HOUR, _absence(T0 + 5 * HOUR))
    )
    assert controller.sent == {}


def test_one_not_found_never_resolves_an_unknown_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A2324-1: a single NOT_FOUND is not absence. Without the section 21
    check the order stays unresolved, and FREEZE cannot be left."""
    controller, _, exchange, cid = _frozen_with_unknown_flatten_order(
        tmp_path, monkeypatch
    )
    at = T0 + 5 * HOUR
    record = LocalRecord(exchange.balances(), controller.sent)
    once = reconcile(exchange, record, TOLERANCE, at)
    assert not once.passed and cid not in once.resolved
    assert "absence not confirmed" in once.differences[0]
    with pytest.raises(SafetyError, match="reconciliation failed"):
        controller.exit_freeze(once, at)
    assert controller.mode is Mode.FREEZE and cid in controller.sent


def test_a_lagging_not_found_is_queried_again_after_the_delay(
    tmp_path: Path,
) -> None:
    """A2324-1 (the reviewer's scenario): a FLATTEN sell that expired
    unfilled, whose reply was lost, and whose first query lags with
    NOT_FOUND. The delayed second query finds it, so it resolves to the real
    order, not to absence."""
    at = T0 + 4 * HOUR
    step_id = (
        "aqt-flat-"
        + hashlib.sha256(f"BTCUSDT|{at.isoformat()}|1".encode()).hexdigest()[:27]
    )
    exchange = SimulatedExchange(
        {"BTCUSDT": _series([100.0] * 4 + [90.0] * 4)},  # gap below the cap
        {"BTCUSDT": FILTERS},
        {"USDT": Decimal("0"), "BTC": Decimal("1")},
        scenario=Scenario({step_id: Fault(timeout=True, not_found_queries=1)}),
    )
    controller, _, _ = _controller(tmp_path, Mode.RUNNING)
    controller.trigger(Trigger.OWNER_FLATTEN, at)
    assert _tick(controller, exchange, 1) is None
    assert controller.mode is Mode.FREEZE and step_id in controller.sent
    slept: list[timedelta] = []
    clock = FakeClock(at + HOUR)

    def sleep(duration: timedelta) -> None:
        slept.append(duration)
        clock.sleep(duration)

    check = AbsenceCheck(timedelta(seconds=10), 2, sleep, clock)
    record = LocalRecord({"USDT": Decimal("0"), "BTC": Decimal("1")}, controller.sent)
    report = reconcile(exchange, record, TOLERANCE, at + HOUR, check)
    found = report.resolved[step_id]
    assert found is not None and found.executed_qty == 0
    assert slept == [timedelta(seconds=10)]
    assert report.passed


@pytest.mark.parametrize("drift", [timedelta(0), timedelta(seconds=-5)])
def test_absence_needs_the_clock_to_advance_by_the_delay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, drift: timedelta
) -> None:
    """A2324R-1: a sleep that does not move the clock forward by the delay
    confirms nothing; the order stays unresolved."""
    controller, _, exchange, cid = _frozen_with_unknown_flatten_order(
        tmp_path, monkeypatch
    )
    at = T0 + 5 * HOUR
    clock = FakeClock(at)
    check = AbsenceCheck(timedelta(seconds=10), 2, lambda _: clock.sleep(drift), clock)
    record = LocalRecord(exchange.balances(), controller.sent)
    report = reconcile(exchange, record, TOLERANCE, at, check)
    assert not report.passed and cid not in report.resolved
    assert "did not advance" in report.differences[0]


def test_the_report_is_stamped_after_the_waits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A2324R-2: an absence check that waited stamps its report at the end
    of the waits, not before."""
    controller, _, exchange, _ = _frozen_with_unknown_flatten_order(
        tmp_path, monkeypatch
    )
    at = T0 + 5 * HOUR
    record = LocalRecord(exchange.balances(), controller.sent)
    report = reconcile(exchange, record, TOLERANCE, at, _absence(at))
    assert report.passed and report.at == at + timedelta(seconds=10)


def test_a_clock_that_moves_back_fails_instead_of_backdating(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A2324R-3 (the reviewer's scenario): the delay is honoured, but the
    clock read for the report is back at the start. The report fails and is
    stamped no earlier than the last accepted reading."""
    controller, _, exchange, _ = _frozen_with_unknown_flatten_order(
        tmp_path, monkeypatch
    )
    at = T0 + 5 * HOUR
    readings = iter((at, at + timedelta(seconds=10), at))
    check = AbsenceCheck(
        timedelta(seconds=10), 2, lambda _: None, lambda: next(readings)
    )
    record = LocalRecord(exchange.balances(), controller.sent)
    report = reconcile(exchange, record, TOLERANCE, at, check)
    assert not report.passed
    assert report.at == at + timedelta(seconds=10)
    assert "clock moved backwards" in report.differences[-1]


def test_a_clock_behind_the_start_confirms_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A2324R-3: a first reading before `at` is a backward clock; the order
    stays unresolved."""
    controller, _, exchange, cid = _frozen_with_unknown_flatten_order(
        tmp_path, monkeypatch
    )
    at = T0 + 5 * HOUR
    clock = FakeClock(at - timedelta(seconds=1))
    check = AbsenceCheck(timedelta(seconds=10), 2, clock.sleep, clock)
    record = LocalRecord(exchange.balances(), controller.sent)
    report = reconcile(exchange, record, TOLERANCE, at, check)
    assert not report.passed and cid not in report.resolved
    assert "moved backwards" in report.differences[0]
