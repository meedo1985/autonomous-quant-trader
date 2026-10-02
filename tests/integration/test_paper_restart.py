"""Roadmap 2 Task 27 part b: a paper account that survives restarts."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

import aqt.app.state as state_module
import aqt.execution.safety as safety_module
import aqt.monitoring.alerts as alerts_module
from aqt.app.paper_loop import RunReport, refuse_marker_path
from aqt.app.state import AccountDir, AccountState
from aqt.core.ledger import append_entry, read_entries
from aqt.data.bars import BarSeries
from aqt.execution.safety import IncidentLog, Mode, Trigger
from aqt.execution.simulator import SimulatedExchange
from tests.integration.test_paper_loop import FILTERS, HOUR, T0, _config, _run, _series

START = T0 + 8 * 24 * HOUR
FLATTEN_AT = START + 2 * HOUR


def _venue(series: BarSeries) -> SimulatedExchange:
    config = _config(1)
    return SimulatedExchange(
        {"BTCUSDT": series}, {"BTCUSDT": FILTERS}, dict(config.starting_balances)
    )


def _account(
    account: AccountDir,
    venue: SimulatedExchange,
    series: BarSeries,
    start: datetime,
    end: datetime,
    commands: Mapping[datetime, Trigger] | None = None,
) -> RunReport:
    return _run(
        account.root,
        _config(1, start=start, end=end),
        series,
        incidents=account.incident_log(),
        journal=account.journal,
        venue=venue,
        commands=commands or {},
    )


def _saved(account: AccountDir) -> tuple[AccountState, datetime]:
    loaded = account.journal.load_saved()
    assert loaded is not None
    return loaded


def _starts(account: AccountDir) -> list[dict[str, object]]:
    return [
        e.payload["fields"]
        for e in read_entries(account.operations_path)
        if e.payload.get("kind") == "STARTUP"
    ]


def test_a_run_split_by_a_restart_ends_where_one_run_ends(tmp_path: Path) -> None:
    series = _series(24 * 14)
    end = START + 4 * 24 * HOUR
    whole = _account(AccountDir(tmp_path / "whole"), _venue(series), series, START, end)
    account, venue = AccountDir(tmp_path / "split"), _venue(series)
    middle = START + 2 * 24 * HOUR
    first = _account(account, venue, series, START, middle)
    peak = _saved(account)[0].peak
    second = _account(account, venue, series, middle, end)
    assert first.refused == second.refused == whole.refused == ()
    assert first.orders_sent > 0
    assert second.final_balances == whole.final_balances
    assert _starts(account)[-1]["resumed_mode"] == "RUNNING"
    assert _saved(account)[0].peak >= peak > 0


def test_halt_resumes_as_halt_and_nothing_trades(tmp_path: Path) -> None:
    series = _series(24 * 14)
    account, venue = AccountDir(tmp_path / "a"), _venue(series)
    middle = START + 24 * HOUR
    halt = {START + 2 * HOUR: Trigger.OWNER_HALT}
    assert _account(account, venue, series, START, middle, halt).final_mode == "HALT"
    held = venue.balances()
    again = _account(account, venue, series, middle, middle + 48 * HOUR)
    assert again.refused == ()  # the open incident does not refuse a HALT
    assert again.final_mode == "HALT" and again.orders_sent == 0
    assert venue.balances() == held
    assert _starts(account)[-1]["resumed_mode"] == "HALT"


def test_a_start_not_after_the_last_save_is_refused(tmp_path: Path) -> None:
    series = _series(24 * 14)
    account, venue = AccountDir(tmp_path / "a"), _venue(series)
    middle = START + 24 * HOUR
    _account(account, venue, series, START, middle)
    again = _account(account, venue, series, middle - HOUR, middle + HOUR)
    assert any("not after the saved state" in r for r in again.refused)


def test_a_fresh_venue_for_a_resumed_account_is_refused(tmp_path: Path) -> None:
    series = _series(24 * 14)
    account = AccountDir(tmp_path / "a")
    middle = START + 24 * HOUR
    assert _account(account, _venue(series), series, START, middle).orders_sent > 0
    again = _account(account, _venue(series), series, middle, middle + HOUR)
    assert any("reconciliation failed" in r for r in again.refused)


@pytest.mark.parametrize(
    ("damage", "reason"),
    [
        ("edit", "saved state unreadable"),
        ("truncate_incidents", "incident log is shorter"),
        ("foreign", "unexpected record type"),
    ],
)
def test_a_damaged_or_inconsistent_state_is_refused(
    tmp_path: Path, damage: str, reason: str
) -> None:
    series = _series(24 * 14)
    account, venue = AccountDir(tmp_path / "a"), _venue(series)
    middle = START + 24 * HOUR
    halt = {START + 2 * HOUR: Trigger.OWNER_HALT}
    _account(account, venue, series, START, middle, halt)
    journal = account.journal.path
    if damage == "edit":
        text = journal.read_text("utf-8").replace('"HALT"', '"RUNNING"')
        journal.write_text(text, "utf-8")
    elif damage == "truncate_incidents":
        account.incidents_path.write_text("", "utf-8")
    else:
        append_entry(journal, record_type="other.v1", payload={}, recorded_at_utc=T0)
    again = _account(account, venue, series, middle, middle + HOUR)
    assert any(reason in r for r in again.refused), again.refused
    assert again.orders_sent == 0


def test_an_alarm_recorded_after_the_last_save_is_applied(tmp_path: Path) -> None:
    """A crash between opening an incident and saving the mode: the incident
    log moves the saved RUNNING on, here to FREEZE."""
    series = _series(24 * 14)
    account, venue = AccountDir(tmp_path / "a"), _venue(series)
    middle = START + 24 * HOUR
    _account(account, venue, series, START, middle)
    account.incident_log().open(str(Trigger.AMBIGUOUS_ORDER), "lost", middle)
    again = _account(account, venue, series, middle + HOUR, middle + 3 * HOUR)
    assert again.refused == () and again.final_mode == "FREEZE"
    assert again.orders_sent == 0


class _Killed(Exception):
    """A hard kill: nothing after it is written, not even the marker."""


def _write_count(monkeypatch: pytest.MonkeyPatch, kill_at: int | None) -> list[int]:
    calls = [0]

    def counted(*args: object, **kwargs: object) -> object:
        calls[0] += 1
        if kill_at is not None and calls[0] == kill_at:
            raise _Killed
        return append_entry(*args, **kwargs)  # type: ignore[arg-type]

    for module in (state_module, safety_module, alerts_module):
        monkeypatch.setattr(module, "append_entry", counted)
    return calls


def test_killing_at_every_write_and_restarting_is_safe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Section 5 of the design: kill before every durable write of a run that
    buys, is FLATTENed by the owner in steps, and HALTs; restart at the next
    hour. The startup reconciliation always passes (no order lost or counted
    twice), an open incident is never resumed as RUNNING, and the account
    ends HALTed and matching the venue."""
    series = _series(24 * 9)
    end = START + 16 * HOUR
    commands = {FLATTEN_AT: Trigger.OWNER_FLATTEN}
    with monkeypatch.context() as patch:
        writes = _write_count(patch, None)
        whole = _account(
            AccountDir(tmp_path / "whole"), _venue(series), series, START, end, commands
        )
    assert whole.final_mode == "HALT" and whole.orders_sent >= 3
    for kill_at in range(1, writes[0] + 1):
        account, venue = AccountDir(tmp_path / f"k{kill_at}"), _venue(series)
        with monkeypatch.context() as patch, pytest.raises(_Killed):
            _write_count(patch, kill_at)
            _account(account, venue, series, START, end, commands)
        refuse_marker_path(account.incident_log()).unlink(missing_ok=True)
        loaded = account.journal.load_saved()
        restart = START if loaded is None else loaded[1] + HOUR
        restart = restart.replace(minute=0, second=0)
        opened = IncidentLog(account.incidents_path).open_incidents()
        later = {t: c for t, c in commands.items() if t >= restart}
        stop = max(end, restart + HOUR)  # killed at the last save: one more hour
        report = _account(account, venue, series, restart, stop, later)
        assert report.refused == (), (kill_at, report.refused)
        if opened:
            assert _starts(account)[-1].get("resumed_mode") != "RUNNING", kill_at
        state = _saved(account)[0]
        assert state.record.balances == venue.balances(), kill_at
        assert not state.sent and not state.record.orders, kill_at
        if FLATTEN_AT >= restart or opened or state.mode is not Mode.RUNNING:
            assert report.final_mode == "HALT", (kill_at, report.final_mode)


def test_the_journal_is_readable_json_lines(tmp_path: Path) -> None:
    series = _series(24 * 14)
    account = AccountDir(tmp_path / "a")
    _account(account, _venue(series), series, START, START + 3 * HOUR)
    lines = account.journal.path.read_text("utf-8").splitlines()
    assert lines and all(json.loads(line)["payload"]["mode"] for line in lines)
    assert _saved(account)[0].record.balances.keys() == {"USDT", "BTC"}
    assert Decimal(0) < _saved(account)[0].peak


def test_every_hour_is_saved(tmp_path: Path) -> None:
    series = _series(24 * 14)
    account = AccountDir(tmp_path / "a")
    _account(account, _venue(series), series, START, START + 6 * HOUR)
    saved = {e.recorded_at_utc for e in read_entries(account.journal.path)}
    hours = {(START + i * HOUR).strftime("%Y-%m-%dT%H:%M:%SZ") for i in range(6)}
    assert hours <= saved


def test_a_restart_keeps_the_loss_stop_peak(tmp_path: Path) -> None:
    """The saved peak, not the equity at restart, sets the 20% line: with a
    saved peak far above today's equity the stop fires at once."""
    series = _series(24 * 14)
    account, venue = AccountDir(tmp_path / "a"), _venue(series)
    middle = START + 24 * HOUR
    _account(account, venue, series, START, middle)
    state, saved_at = _saved(account)
    assert state.mode is Mode.RUNNING and state.stop_armed
    account.journal.save(replace(state, peak=state.peak * 2), saved_at)
    again = _account(account, venue, series, middle, middle + 2 * HOUR)
    assert again.refused == () and again.final_mode in ("FLATTEN", "HALT")
    kinds = [
        e.payload["kind"]
        for e in read_entries(account.incidents_path)
        if e.record_type == IncidentLog.OPEN
    ]
    assert kinds == [str(Trigger.LOSS_STOP)]
