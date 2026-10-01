"""Roadmap 2 Task 27 part b2: the ways back from FREEZE and HALT inside the
loop (owner FREEZE_EXIT, the section 14 override with Q27-1/Q27-2), and the
A2324R-4/A2324R-5 timestamps."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

import aqt.app.paper_loop as loop
from aqt.app.paper_loop import OwnerOverride, RunReport, nonce_for
from aqt.app.state import AccountDir, AccountState, StateJournal
from aqt.core.ledger import read_entries
from aqt.data.bars import BarSeries
from aqt.execution.orders import ExecutorConfig, client_order_id_for
from aqt.execution.reconcile import LocalRecord
from aqt.execution.safety import IncidentLog, Mode, OwnerAction, Trigger
from aqt.execution.simulator import Fault, Scenario
from aqt.monitoring.events import Event
from tests.integration.test_paper_loop import (
    HOUR,
    _config,
    _probe_authorization,
    _run,
    _series,
)
from tests.integration.test_paper_restart import START, _account, _saved, _venue

FROZEN_AT = datetime(2020, 1, 9, tzinfo=UTC)
"""When the scenario below FREEZEs: its first order, at the first daily
decision, times out and stays unreadable for five queries."""


def _scenario() -> Scenario:
    first = client_order_id_for(
        replace(_probe_authorization(), nonce=nonce_for("test-run", 0))
    )
    return Scenario({first: Fault(timeout=True, unknown_queries=5)})


def _frozen_run(
    account: AccountDir,
    series: BarSeries,
    commands: dict[datetime, Trigger],
    overrides: dict[datetime, OwnerOverride] | None = None,
) -> RunReport:
    return _run(
        account.root,
        _config(4),
        series,
        incidents=account.incident_log(),
        journal=account.journal,
        scenario=_scenario(),
        commands=commands,
        overrides=overrides or {},
    )


def _transitions(account: AccountDir) -> list[dict[str, object]]:
    return [
        e.payload["fields"]
        for e in read_entries(account.operations_path)
        if e.payload.get("kind") == "STATE_TRANSITION"
    ]


def _exits(hours: int) -> dict[datetime, Trigger]:
    return {FROZEN_AT + i * HOUR: Trigger.FREEZE_EXIT for i in range(1, hours + 1)}


def _override(ids: tuple[str, ...], at: datetime) -> OwnerOverride:
    return OwnerOverride(
        incident_ids=ids,
        written_record="the order timed out; the venue shows it filled",
        cause="simulated timeout and unreadable queries",
        owner_action=OwnerAction("owner", "resume trading"),
        timestamp=at,
    )


def test_freeze_exit_needs_a_passed_reconciliation_and_leads_to_halt(
    tmp_path: Path,
) -> None:
    """While the order cannot be read, FREEZE_EXIT is refused with the reason
    and the account stays frozen; the first passed reconciliation leads to
    HALT, never RUNNING, and the incident stays open."""
    account = AccountDir(tmp_path / "a")
    report = _frozen_run(account, _series(24 * 14), _exits(6))
    assert report.final_mode == "HALT" and report.orders_sent == 1
    moves = _transitions(account)
    refused = [m for m in moves if m.get("command") == "FREEZE_EXIT"]
    assert all("unresolved" in str(m["refused"]) for m in refused[:4])
    assert [m["trigger"] for m in moves if "trigger" in m] == [
        "AMBIGUOUS_ORDER",
        "FREEZE_EXIT",
    ]
    assert len(account.incident_log().open_incidents()) == 1
    state = _saved(account)[0]
    assert not state.record.orders and not state.sent


def test_nothing_leaves_freeze_without_the_command(tmp_path: Path) -> None:
    account = AccountDir(tmp_path / "a")
    report = _frozen_run(account, _series(24 * 14), {})
    assert report.final_mode == "FREEZE" and report.orders_sent == 1


def test_the_override_after_freeze_resumes_trading(tmp_path: Path) -> None:
    """FREEZE_EXIT, then the owner's override naming the open incident:
    RUNNING again, and the governor decides again with the frozen order's
    reservation released (never OUTSTANDING_AUTHORIZATION)."""
    series = _series(24 * 14)
    first = AccountDir(tmp_path / "probe")
    _frozen_run(first, series, _exits(6))
    (incident,) = first.incident_log().open_incidents()
    at = FROZEN_AT + 7 * HOUR
    account = AccountDir(tmp_path / "a")
    report = _frozen_run(account, series, _exits(6), {at: _override((incident,), at)})
    assert report.final_mode == "RUNNING"
    assert account.incident_log().open_incidents() == ()
    assert report.governor_refusals.get("INSIDE_REBALANCE_BAND", 0) > 0
    assert "OUTSTANDING_AUTHORIZATION" not in report.governor_refusals


def test_an_override_that_misses_an_incident_is_refused(tmp_path: Path) -> None:
    series = _series(24 * 14)
    at = FROZEN_AT + 7 * HOUR
    account = AccountDir(tmp_path / "a")
    report = _frozen_run(account, series, _exits(6), {at: _override(("x",), at)})
    assert report.final_mode == "HALT" and report.orders_sent == 1
    refusals = [m for m in _transitions(account) if m.get("command") == "HALT_OVERRIDE"]
    assert len(refusals) == 1 and "every open incident" in str(refusals[0]["refused"])
    assert len(account.incident_log().open_incidents()) == 1


def test_ending_a_halt_rearms_the_loss_stop_from_equity_now(tmp_path: Path) -> None:
    """Q27-1, Q27-2: a HALT ended while equity is far below the saved peak
    does not fire the loss stop; the peak is reset to the equity at the
    override and the stop is armed."""
    series = _series(24 * 14)
    account, venue = AccountDir(tmp_path / "a"), _venue(series)
    middle = START + 24 * HOUR
    _account(
        account, venue, series, START, middle, {START + 2 * HOUR: Trigger.OWNER_HALT}
    )
    state, saved_at = _saved(account)
    account.journal.save(replace(state, peak=state.peak * 3), saved_at)
    ids = account.incident_log().open_incidents()
    at = middle  # before the loss check of that hour, in the first hour

    report = _run(
        account.root,
        _config(1, start=middle, end=at + HOUR),
        series,
        incidents=account.incident_log(),
        journal=account.journal,
        venue=venue,
        overrides={at: _override(ids, at)},
    )
    assert report.refused == () and report.final_mode == "RUNNING"
    kinds = [
        e.payload["kind"]
        for e in read_entries(account.incidents_path)
        if e.record_type == IncidentLog.OPEN
    ]
    assert str(Trigger.LOSS_STOP) not in kinds
    stamp = at.strftime("%Y-%m-%dT%H:%M:%SZ")
    snapshot = [
        e.payload
        for e in read_entries(account.journal.path)
        if e.recorded_at_utc == stamp
    ][-1]
    mark = Decimal(repr(series.bar_at(at - HOUR).close))
    held = {k: Decimal(v) for k, v in snapshot["record"]["balances"].items()}
    assert Decimal(snapshot["peak"]) == held["BTC"] * mark + held["USDT"]
    assert snapshot["stop_armed"] is True and snapshot["mode"] == "RUNNING"


def test_a_refusal_after_a_waiting_startup_check_is_stamped_after_it(
    tmp_path: Path,
) -> None:
    """A2324R-5 (the reviewer's scenario): one unknown order confirmed
    absent after a 10 s wait, and a balance mismatch. The REFUSE_START is
    stamped when the check ended, not at the configured start."""
    config = _config(1)
    record = LocalRecord(
        {"USDT": Decimal("10000"), "BTC": Decimal("1")}, {"unknown": None}
    )
    report = _run(tmp_path, config, _series(24 * 10), local_record=record)
    assert report.refused
    stamps = {
        e.recorded_at_utc
        for e in read_entries(tmp_path / "operations.jsonl")
        if e.payload.get("kind") == "STARTUP"
    }
    after = config.start + timedelta(seconds=10)
    assert stamps == {after.strftime("%Y-%m-%dT%H:%M:%SZ")}


def test_saves_never_go_back_after_a_long_reconciliation(tmp_path: Path) -> None:
    """A2324R-4: an order whose first query lags behind a two-hour protocol
    delay ends its reconciliation after the next hour began. That hour is
    skipped: the owner's HALT for it applies when the reconciliation ends,
    and the journal and the operations log never step back."""
    config = _config(
        3,
        executor=ExecutorConfig(not_found_delay=timedelta(hours=2), absence_queries=2),
    )
    first = client_order_id_for(
        replace(_probe_authorization(), nonce=nonce_for(config.run_id, 0))
    )
    account = AccountDir(tmp_path / "a")
    report = _run(
        account.root,
        config,
        _series(24 * 14),
        incidents=account.incident_log(),
        journal=account.journal,
        scenario=Scenario({first: Fault(timeout=True, not_found_queries=1)}),
        commands={FROZEN_AT + HOUR: Trigger.OWNER_HALT},
    )
    assert report.refused == () and report.orders_sent == 1
    assert report.final_mode == "HALT"
    for path in (account.journal.path, account.operations_path):
        stamps = [e.recorded_at_utc for e in read_entries(path)]
        assert stamps == sorted(stamps), path.name


def test_freeze_exit_outside_freeze_is_refused_and_the_hour_goes_on(
    tmp_path: Path,
) -> None:
    """A FREEZE_EXIT during an owner FLATTEN is refused, and that hour's
    FLATTEN step is still taken: the account ends where it ends without it."""
    series = _series(24 * 14)
    flatten = START + 2 * HOUR
    end = START + 12 * HOUR
    plain, venue = AccountDir(tmp_path / "plain"), _venue(series)
    _account(plain, venue, series, START, end, {flatten: Trigger.OWNER_FLATTEN})
    account, other = AccountDir(tmp_path / "a"), _venue(series)
    commands = {flatten: Trigger.OWNER_FLATTEN, flatten + HOUR: Trigger.FREEZE_EXIT}
    report = _account(account, other, series, START, end, commands)
    assert other.balances() == venue.balances() and report.orders_sent >= 2
    refused = [m for m in _transitions(account) if m.get("command") == "FREEZE_EXIT"]
    assert len(refused) == 1 and "not in FREEZE (FLATTEN)" in str(refused[0]["refused"])


def test_a_failed_reconciliation_at_the_override_freezes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A mismatch found when the owner ends a HALT is a new safety event: the
    override is refused and the account FREEZEs with a new incident."""
    series = _series(24 * 14)
    account, venue = AccountDir(tmp_path / "a"), _venue(series)
    middle = START + 24 * HOUR
    _account(
        account, venue, series, START, middle, {START + 2 * HOUR: Trigger.OWNER_HALT}
    )
    ids = account.incident_log().open_incidents()
    real = loop.reconcile

    def failing(*args: object, **kwargs: object) -> object:
        report = real(*args, **kwargs)  # type: ignore[arg-type]
        if report.at >= middle + HOUR:
            return replace(report, passed=False, differences=("forced mismatch",))
        return report

    monkeypatch.setattr(loop, "reconcile", failing)
    at = middle + HOUR
    report = _run(
        account.root,
        _config(1, start=middle, end=at + HOUR),
        series,
        incidents=account.incident_log(),
        journal=account.journal,
        venue=venue,
        overrides={at: _override(ids, at)},
    )
    assert report.final_mode == "FREEZE"
    assert len(account.incident_log().open_incidents()) == len(ids) + 1
    assert _saved(account)[0].mode.value == "FREEZE"


def test_saves_follow_a_recovery_that_waited(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A27-1 (the reviewer's scenario): the override's reconciliation ends
    two hours after it began. No later save and no SHUTDOWN is stamped
    before it."""
    series = _series(24 * 14)
    account, venue = AccountDir(tmp_path / "a"), _venue(series)
    _account(account, venue, series, START, START + HOUR, {START: Trigger.OWNER_HALT})
    at = START + HOUR
    real = loop.reconcile

    def delayed(*args: object, **kwargs: object) -> object:
        report = real(*args, **kwargs)  # type: ignore[arg-type]
        return replace(report, at=report.at + 2 * HOUR)

    monkeypatch.setattr(loop, "reconcile", delayed)
    ids = account.incident_log().open_incidents()
    _run(
        account.root,
        _config(1, start=at, end=at + HOUR),
        series,
        incidents=account.incident_log(),
        journal=account.journal,
        venue=venue,
        overrides={at: _override(ids, at)},
    )
    for path in (account.journal.path, account.operations_path):
        stamps = [e.recorded_at_utc for e in read_entries(path)]
        assert stamps == sorted(stamps), path.name


class _Killed(BaseException):
    """A hard kill: nothing after it runs."""


def test_a_buy_filled_before_a_crash_keeps_its_risk_increase(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A27-2 (the reviewer's scenario): killed after the buy filled, before
    its bookkeeping. The restart finds the fill and restores the governor's
    last risk increase from it."""
    series = _series(24 * 14)
    account, venue = AccountDir(tmp_path / "a"), _venue(series)
    real = loop.AlertRouter.emit

    def kill_after_buy(self: loop.AlertRouter, event: Event) -> None:
        fields = event.fields
        if str(event.kind) == "ORDER" and fields.get("side") == "BUY":
            if fields.get("executed_qty") not in (None, "0"):
                raise _Killed
        real(self, event)

    with monkeypatch.context() as patch, pytest.raises(_Killed):
        patch.setattr(loop.AlertRouter, "emit", kill_after_buy)
        _account(account, venue, series, START, START + HOUR)
    loop.refuse_marker_path(account.incident_log()).unlink()
    report = _account(account, venue, series, START + HOUR, START + 2 * HOUR)
    assert report.refused == ()
    assert _saved(account)[0].last_increase == START


def test_a_peak_valued_but_not_saved_is_valued_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A27-3 (the reviewer's scenario): saved peak 100, an hour values 120,
    the process dies before saving it. The restart values that hour again
    from the bars, so the peak is 120 and the 20% line 96, not 80."""
    bars = []
    for bar in _series(24 * 14).bars:
        price = 120.0 if bar.open_time == START else 100.0
        if bar.open_time == START + HOUR:
            price = 90.0
        bars.append(replace(bar, open=price, high=price, low=price, close=price))
    series = BarSeries(symbol="BTCUSDT", bars=tuple(bars))

    class Venue:
        def balances(self) -> dict[str, Decimal]:
            return {"BTC": Decimal("1"), "USDT": Decimal("0")}

        def open_orders(self) -> tuple[()]:
            return ()

        def query_order(self, client_order_id: str) -> None:
            raise AssertionError(client_order_id)

    account, venue = AccountDir(tmp_path / "a"), Venue()
    prior = START - HOUR
    account.incident_log().open(str(Trigger.OWNER_HALT), "owner halt", prior)
    account.journal.save(
        AccountState(
            mode=Mode.HALT,
            entered_at=prior,
            record=LocalRecord(venue.balances()),
            sent={},
            attempts={},
            peak=Decimal("100"),
            stop_armed=True,
            last_increase=None,
            incidents_seen=1,
        ),
        prior,
    )
    real = StateJournal.save

    def killed_save(self: StateJournal, state: AccountState, at: datetime) -> None:
        if state.peak == Decimal("120"):
            raise _Killed
        real(self, state, at)

    with monkeypatch.context() as patch, pytest.raises(_Killed):
        patch.setattr(StateJournal, "save", killed_save)
        _account(account, venue, series, START + HOUR, START + 2 * HOUR)  # type: ignore[arg-type]
    loop.refuse_marker_path(account.incident_log()).unlink()
    report = _account(account, venue, series, START + 2 * HOUR, START + 3 * HOUR)  # type: ignore[arg-type]
    assert report.refused == ()
    assert _saved(account)[0].peak == Decimal("120")
    kinds = [
        e.payload["kind"]
        for e in read_entries(account.incidents_path)
        if e.record_type == IncidentLog.OPEN
    ]
    assert str(Trigger.LOSS_STOP) in kinds  # 90 is below 96: recorded in HALT


def test_a_resumed_state_incident_is_replayed(tmp_path: Path) -> None:
    """A27-7: a crash after STATE_RESUMED is opened but before it is saved;
    replaying it keeps HALT instead of refusing the start."""
    incidents = IncidentLog(tmp_path / "incidents.jsonl")
    saved = AccountState(
        mode=Mode.HALT,
        entered_at=START,
        record=LocalRecord({"USDT": Decimal(1)}),
        sent={},
        attempts={},
        peak=Decimal(1),
        stop_armed=True,
        last_increase=None,
    )
    incidents.open("STATE_RESUMED", "resumed HALT, no incident open", START + HOUR)
    assert loop._resume(saved, incidents) == (Mode.HALT, START + HOUR)
