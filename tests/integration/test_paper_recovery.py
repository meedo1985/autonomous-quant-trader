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
from aqt.app.forward import unfinished_hours
from aqt.app.paper_loop import OwnerOverride, RunReport, nonce_for
from aqt.app.state import AccountDir, AccountState, StateJournal
from aqt.backtest.costs import Side as TradeSide
from aqt.core.ledger import read_entries
from aqt.data.bars import BarSeries
from aqt.execution.orders import ExecutorConfig, client_order_id_for
from aqt.execution.reconcile import LocalRecord
from aqt.execution.safety import IncidentLog, Mode, OwnerAction, Trigger
from aqt.execution.simulator import Fault, Order, OrderStatus, Scenario
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
    # A fall the stop already recorded: spent, far below the line.
    account.journal.save(
        replace(state, peak=state.peak * 3, stop_armed=False), saved_at
    )
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
            valued_through=prior,
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
        valued_through=None,
    )
    incidents.open("STATE_RESUMED", "resumed HALT, no incident open", START + HOUR)
    assert loop._resume(saved, incidents) == (Mode.HALT, START + HOUR)


class _Venue:
    """A venue whose balances and orders are given; nothing trades."""

    def __init__(
        self, balances: dict[str, Decimal], orders: dict[str, Order] | None = None
    ) -> None:
        self._balances, self._orders = balances, orders or {}

    def balances(self) -> dict[str, Decimal]:
        return dict(self._balances)

    def open_orders(self) -> tuple[()]:
        return ()

    def query_order(self, client_order_id: str) -> Order:
        return self._orders[client_order_id]


def _priced(prices: dict[datetime, float], default: float = 100.0) -> BarSeries:
    bars = []
    for bar in _series(24 * 14).bars:
        price = prices.get(bar.open_time, default)
        bars.append(replace(bar, open=price, high=price, low=price, close=price))
    return BarSeries(symbol="BTCUSDT", bars=tuple(bars))


def _seed(
    account: AccountDir,
    at: datetime,
    mode: Mode,
    balances: dict[str, Decimal],
    peak: str,
    armed: bool = True,
    orders: dict[str, Order | None] | None = None,
    valued: datetime | None = None,
) -> None:
    """A snapshot saved at `at` that has valued up to `valued` (default: the
    hour `at` itself, as an hour-end or pre-send snapshot has)."""
    incidents = account.incident_log()
    if mode is Mode.HALT:
        incidents.open(str(Trigger.OWNER_HALT), "owner halt", at)
    if mode is Mode.FREEZE:
        incidents.open(str(Trigger.AMBIGUOUS_ORDER), "lost", at)
    if not armed:
        incidents.open(str(Trigger.LOSS_STOP), "earlier fall", at)
    seen = len(read_entries(incidents.path)) if incidents.path.exists() else 0
    account.journal.save(
        AccountState(
            mode=mode,
            entered_at=at,
            record=LocalRecord(balances, orders or {}),
            sent={},
            attempts={},
            peak=Decimal(peak),
            stop_armed=armed,
            last_increase=None,
            valued_through=at if valued is None else valued,
            incidents_seen=seen,
        ),
        at,
    )


def _one_hour(
    account: AccountDir, venue: _Venue, series: BarSeries, start: datetime, **kw: object
) -> RunReport:
    report = _run(
        account.root,
        _config(1, start=start, end=start + HOUR),
        series,
        incidents=account.incident_log(),
        journal=account.journal,
        venue=venue,
        **kw,
    )
    assert report.refused == ()
    return report


def _losses(account: AccountDir) -> int:
    return sum(
        e.record_type == IncidentLog.OPEN
        and e.payload["kind"] == str(Trigger.LOSS_STOP)
        for e in read_entries(account.incidents_path)
    )


ONE_BTC = {"BTC": Decimal(1), "USDT": Decimal(0)}


def test_a_refused_override_after_a_wait_ends_its_hour(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A27-8 (the reviewer's scenario): an override refused after a two-hour
    reconciliation; the loss stop of that hour is not stamped before it."""
    account = AccountDir(tmp_path / "a")
    _seed(account, START - HOUR, Mode.HALT, ONE_BTC, "120")
    invalid = replace(
        _override(account.incident_log().open_incidents(), START), written_record=""
    )
    real = loop.reconcile

    def delayed(*args: object, **kwargs: object) -> object:
        report = real(*args, **kwargs)  # type: ignore[arg-type]
        return replace(report, at=report.at + 2 * HOUR)

    monkeypatch.setattr(loop, "reconcile", delayed)
    _one_hour(
        account, _Venue(ONE_BTC), _priced({}, 90.0), START, overrides={START: invalid}
    )
    stamps = [e.recorded_at_utc for e in read_entries(account.operations_path)]
    assert stamps == sorted(stamps)


def test_missed_hours_are_valued_with_the_confirmed_holdings(tmp_path: Path) -> None:
    """A27-9 (the reviewer's scenario): a buy sent just before the crash
    fills; while the process is down BTC closes at 120, then 90. The restart
    values those hours with the bought BTC: peak 120, and the fall below 96
    is recorded."""
    buy = Order(
        client_order_id="recovered-buy",
        symbol="BTCUSDT",
        side=TradeSide.BUY,
        orig_qty=Decimal(1),
        executed_qty=Decimal(1),
        status=OrderStatus.FILLED,
        decision_time=START,
        fill_time=START,
        fill_price=Decimal(100),
        quote_amount=Decimal(100),
        cost_quote=Decimal(0),
        cost_bps=Decimal(0),
        limit_price=None,
    )
    account = AccountDir(tmp_path / "a")
    cash = {"BTC": Decimal(0), "USDT": Decimal(100)}
    _seed(account, START, Mode.RUNNING, cash, "100", orders={buy.client_order_id: None})
    restart = START + 3 * HOUR
    series = _priced({START + HOUR: 120.0, START + 2 * HOUR: 90.0})
    venue = _Venue(ONE_BTC, {buy.client_order_id: buy})
    _one_hour(account, venue, series, restart, commands={restart: Trigger.OWNER_HALT})
    saved = account.journal.load()
    assert saved is not None and saved.last_increase == START
    assert saved.peak == Decimal(120) and _losses(account) == 1


def test_missed_hours_rearm_the_loss_stop(tmp_path: Path) -> None:
    """A27-10 (the reviewer's scenario): a spent stop re-arms in a missed hour
    back at the peak, and the next missed fall is recorded."""
    account = AccountDir(tmp_path / "a")
    _seed(account, START, Mode.HALT, ONE_BTC, "100", armed=False)
    before = _losses(account)
    series = _priced({START - HOUR: 70.0, START: 100.0, START + HOUR: 70.0})
    _one_hour(account, _Venue(ONE_BTC), series, START + 2 * HOUR)
    assert _losses(account) == before + 1


def test_a_freeze_records_no_loss_stop(tmp_path: Path) -> None:
    """T27-13: FREEZE is left alone until reconciled: a fall during it, live
    or missed, opens no LOSS_STOP incident and leaves the stop armed."""
    account = AccountDir(tmp_path / "a")
    _seed(account, START, Mode.FREEZE, ONE_BTC, "100")
    series = _priced({START: 70.0, START + HOUR: 70.0, START + 2 * HOUR: 70.0})
    report = _one_hour(account, _Venue(ONE_BTC), series, START + 2 * HOUR)
    assert report.final_mode == "FREEZE" and _losses(account) == 0
    assert _saved(account)[0].stop_armed is True


def test_an_hour_end_snapshot_is_not_valued_again(tmp_path: Path) -> None:
    """A27-13 (the reviewer's scenario): the hour-end snapshot of a buy
    already holds the BTC. Its hour is not valued again with those holdings
    at the earlier mark, so no peak of 120 is invented and no stop fires."""
    account = AccountDir(tmp_path / "a")
    _seed(account, START, Mode.RUNNING, ONE_BTC, "100")
    restart = START + HOUR
    series = _priced({START - HOUR: 120.0, START: 90.0})
    _one_hour(
        account,
        _Venue(ONE_BTC),
        series,
        restart,
        commands={restart: Trigger.OWNER_HALT},
    )
    saved = account.journal.load()
    assert saved is not None and saved.peak == Decimal(100) and _losses(account) == 0


def test_a_missed_firing_keeps_the_replayed_latch(tmp_path: Path) -> None:
    """A27-14 (the reviewer's scenario): a missed fall at H, a missed return
    at H+1, then a new fall in the first live hour: two LOSS_STOP incidents."""
    account = AccountDir(tmp_path / "a")
    _seed(account, START, Mode.HALT, ONE_BTC, "100", valued=START - HOUR)
    series = _priced({START - HOUR: 70.0, START: 100.0, START + HOUR: 70.0})
    _one_hour(account, _Venue(ONE_BTC), series, START + 2 * HOUR)
    assert _losses(account) == 2


def test_a_waited_override_reset_is_not_undone_by_a_restart(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A27-16 (the reviewer's scenario): the override's reconciliation ends
    two hours later and resets the peak to 90 then. A restart does not
    value the hours before the reset again: peak stays 90, no stop fires."""
    account = AccountDir(tmp_path / "a")
    _seed(account, START - HOUR, Mode.HALT, ONE_BTC, "100")
    series = _priced(
        {START - HOUR: 100.0, START: 120.0, START + HOUR: 90.0, START + 2 * HOUR: 90.0}
    )
    wanted = _override(account.incident_log().open_incidents(), START)
    real = loop.reconcile

    def delayed(*args: object, **kwargs: object) -> object:
        report = real(*args, **kwargs)  # type: ignore[arg-type]
        return replace(report, at=report.at + 2 * HOUR)

    with monkeypatch.context() as patch:
        patch.setattr(loop, "reconcile", delayed)
        _one_hour(account, _Venue(ONE_BTC), series, START, overrides={START: wanted})
    before = account.journal.load()
    assert before is not None and before.peak == Decimal(90)
    restart = START + 3 * HOUR
    _one_hour(
        account,
        _Venue(ONE_BTC),
        series,
        restart,
        commands={restart: Trigger.OWNER_HALT},
    )
    saved = account.journal.load()
    assert saved is not None and saved.peak == Decimal(90) and _losses(account) == 0


def test_a_waiting_startup_values_its_hours_as_a_restart_would(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A27-17 (the reviewer's scenario): the startup check ends two hours
    late. Running on, or stopping after the first save and restarting,
    leaves the same peak and the same LOSS_STOP incidents."""
    series = _priced(
        {START - HOUR: 120.0, START: 90.0, START + HOUR: 90.0, START + 2 * HOUR: 90.0},
        default=90.0,
    )
    real = loop.startup_check

    def delayed(*args: object, **kwargs: object) -> object:
        decision = real(*args, **kwargs)  # type: ignore[arg-type]
        later = replace(decision.report, at=decision.report.at + 2 * HOUR)
        return replace(decision, report=later)

    continuous, restarted = AccountDir(tmp_path / "c"), AccountDir(tmp_path / "r")
    for account in (continuous, restarted):
        _seed(account, START - HOUR, Mode.HALT, ONE_BTC, "100", valued=START - HOUR)
    with monkeypatch.context() as patch:
        patch.setattr(loop, "startup_check", delayed)
        report = _run(
            continuous.root,
            _config(1, start=START, end=START + 4 * HOUR),
            series,
            incidents=continuous.incident_log(),
            journal=continuous.journal,
            venue=_Venue(ONE_BTC),
        )
        assert report.refused == ()
        _one_hour(restarted, _Venue(ONE_BTC), series, START)
    _one_hour(restarted, _Venue(ONE_BTC), series, START + 3 * HOUR)
    a, b = continuous.journal.load(), restarted.journal.load()
    assert a is not None and b is not None
    assert (a.peak, _losses(continuous)) == (b.peak, _losses(restarted))
    assert a.peak == Decimal(120)


def test_hours_with_unresolved_orders_are_valued_after_the_recovery(
    tmp_path: Path,
) -> None:
    """A27-18: while an order is unresolved in FREEZE no hour is valued, so
    the snapshot's watermark stays at the order's hour; FREEZE_EXIT then
    values those hours with the confirmed holdings."""
    series = _series(24 * 14)
    frozen = AccountDir(tmp_path / "f")
    _frozen_run(frozen, series, {})
    state = _saved(frozen)[0]
    assert state.mode is Mode.FREEZE and state.valued_through == FROZEN_AT
    exited = AccountDir(tmp_path / "e")
    _frozen_run(exited, series, _exits(6))
    state = _saved(exited)[0]
    assert state.mode is Mode.HALT and state.valued_through is not None
    assert state.valued_through > FROZEN_AT + 5 * HOUR


def _hours_run(
    account: AccountDir, series: BarSeries, start: datetime, end: datetime, **kw: object
) -> RunReport:
    report = _run(
        account.root,
        _config(1, start=start, end=end),
        series,
        incidents=account.incident_log(),
        journal=account.journal,
        venue=_Venue(ONE_BTC),
        **kw,
    )
    assert report.refused == ()
    return report


def test_a_refused_override_still_records_the_hours_breach(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A27-20 (the reviewer's scenario): an invalid override in an hour below
    the line. The breach is recorded once, running on or killed before the
    hour-end save and restarted."""
    series = _priced({START - HOUR: 70.0, START: 100.0})
    continuous, restarted = AccountDir(tmp_path / "c"), AccountDir(tmp_path / "r")
    for account in (continuous, restarted):
        _seed(account, START - HOUR, Mode.HALT, ONE_BTC, "100")

    def invalid(account: AccountDir) -> OwnerOverride:
        ids = account.incident_log().open_incidents()
        return replace(_override(ids, START), written_record="")

    _hours_run(
        continuous,
        series,
        START,
        START + 2 * HOUR,
        overrides={START: invalid(continuous)},
    )
    real = StateJournal.save

    def kill(self: StateJournal, state: AccountState, at: datetime) -> None:
        if state.valued_through == START:
            raise _Killed
        real(self, state, at)

    with monkeypatch.context() as patch, pytest.raises(_Killed):
        patch.setattr(StateJournal, "save", kill)
        _hours_run(
            restarted,
            series,
            START,
            START + HOUR,
            overrides={START: invalid(restarted)},
        )
    loop.refuse_marker_path(restarted.incident_log()).unlink()
    _hours_run(restarted, series, START + HOUR, START + 2 * HOUR)
    assert (_losses(continuous), _losses(restarted)) == (1, 1)


def test_a_restart_values_bars_before_a_data_gap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A27-21 (the reviewer's scenario): the peak of 120 was valued but not
    saved; the restart's window starts after a missing bar. The replay still
    sees the earlier bar: peak 120 and the fall to 90 recorded."""
    priced = _priced({START - HOUR: 120.0, START: 90.0}, default=90.0)
    series = BarSeries(
        symbol=priced.symbol,
        bars=tuple(b for b in priced.bars if b.open_time != START + HOUR),
    )
    account = AccountDir(tmp_path / "a")
    _seed(account, START - HOUR, Mode.HALT, ONE_BTC, "100")
    real = StateJournal.save

    def kill(self: StateJournal, state: AccountState, at: datetime) -> None:
        if state.peak == Decimal(120):
            raise _Killed
        real(self, state, at)

    with monkeypatch.context() as patch, pytest.raises(_Killed):
        patch.setattr(StateJournal, "save", kill)
        _hours_run(account, series, START, START + HOUR)
    loop.refuse_marker_path(account.incident_log()).unlink()
    _hours_run(account, series, START + 3 * HOUR, START + 4 * HOUR)
    saved = account.journal.load()
    assert saved is not None and saved.peak == Decimal(120) and _losses(account) == 1


def test_every_missed_firing_is_recorded(tmp_path: Path) -> None:
    """A27-22 (the reviewer's scenario): two separate falls while down give
    two LOSS_STOP incidents, as running through them does."""
    series = _priced(
        {START - HOUR: 70.0, START: 100.0, START + HOUR: 70.0, START + 2 * HOUR: 100.0}
    )
    continuous, restarted = AccountDir(tmp_path / "c"), AccountDir(tmp_path / "r")
    for account in (continuous, restarted):
        _seed(account, START - HOUR, Mode.HALT, ONE_BTC, "100")
    _hours_run(continuous, series, START, START + 4 * HOUR)
    _hours_run(restarted, series, START + 4 * HOUR, START + 5 * HOUR)
    assert (_losses(continuous), _losses(restarted)) == (2, 2)


def test_a_logged_firing_does_not_hide_a_different_missed_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A27-24 (the reviewer's scenario): the fall at START is logged, then
    the process dies before saving. The restart is given bars from START on
    only, so its replay sees just the later fall at START + 2h; that one is
    still recorded, matched by decision hour rather than by count."""
    series = _priced({START - HOUR: 70.0, START: 100.0, START + HOUR: 70.0})
    account = AccountDir(tmp_path / "a")
    _seed(account, START - HOUR, Mode.HALT, ONE_BTC, "100")
    real = StateJournal.save

    def kill(self: StateJournal, state: AccountState, at: datetime) -> None:
        if state.valued_through == START:
            raise _Killed
        real(self, state, at)

    with monkeypatch.context() as patch, pytest.raises(_Killed):
        patch.setattr(StateJournal, "save", kill)
        _hours_run(account, series, START, START + HOUR)
    assert _losses(account) == 1
    loop.refuse_marker_path(account.incident_log()).unlink()
    shorter = BarSeries(
        symbol=series.symbol,
        bars=tuple(b for b in series.bars if b.open_time >= START),
    )
    _hours_run(account, shorter, START + 3 * HOUR, START + 4 * HOUR)
    assert _losses(account) == 2


def test_a_fall_in_a_health_breach_hour_fires_but_trades_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A27-23, owner answer "Fire as usual": a breach in a health-breach hour
    is recorded and RUNNING enters FLATTEN; no order is placed that hour."""
    account = AccountDir(tmp_path / "a")
    _seed(account, START - 2 * HOUR, Mode.RUNNING, ONE_BTC, "100")
    config = _config(1, start=START - HOUR, end=START + HOUR)

    def observe(at: datetime) -> loop.Observation:
        observation = loop.bar_clock_observation(at)
        if at != START:  # only the second hour is unhealthy
            return observation
        stale = at - config.health.max_data_age - timedelta(seconds=1)
        return replace(observation, latest_bar_close=stale)

    monkeypatch.setattr(loop, "baseline_proposal", lambda *_: "synthetic hold")
    report = _run(
        account.root,
        config,
        _priced({START - HOUR: 70.0}),
        incidents=account.incident_log(),
        journal=account.journal,
        venue=_Venue(ONE_BTC),
        observe=observe,
    )
    assert report.final_mode == "FLATTEN" and report.orders_sent == 0
    assert report.health_breach_hours == 1 and _losses(account) == 1


def _delayed_by_two_hours(failing: bool) -> object:
    real = loop.reconcile

    def delayed(*args: object, **kwargs: object) -> object:
        report = real(*args, **kwargs)  # type: ignore[arg-type]
        if failing:
            report = replace(report, passed=False, differences=("forced mismatch",))
        return replace(report, at=report.at + 2 * HOUR)

    return delayed


@pytest.mark.parametrize("failing", [False, True])
def test_a_kill_after_an_override_save_names_only_the_skipped_hours(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failing: bool
) -> None:
    """S29R3-1: the override's reconciliation at hour 1 ends at 03:00,
    passed or failed, and its save ends hour 1. Killed right after it, hours
    2 and 3 were not run; hour 1 was finished, so it is not named."""
    series = _series(24 * 14)
    account, venue = AccountDir(tmp_path / "a"), _venue(series)
    _account(account, venue, series, START, START + HOUR, {START: Trigger.OWNER_HALT})
    at = START + HOUR
    original = StateJournal.save

    def save(self: StateJournal, state: AccountState, when: datetime) -> None:
        original(self, state, when)
        if when >= at + 2 * HOUR:
            raise _Killed

    with monkeypatch.context() as patch, pytest.raises(_Killed):
        patch.setattr(loop, "reconcile", _delayed_by_two_hours(failing))
        patch.setattr(StateJournal, "save", save)
        _run(
            account.root,
            _config(1, start=at, end=at + 6 * HOUR),
            series,
            incidents=account.incident_log(),
            journal=account.journal,
            venue=venue,
            overrides={at: _override(account.incident_log().open_incidents(), at)},
        )
    state = account.journal.load()
    assert state is not None
    assert state.mode is (Mode.FREEZE if failing else Mode.RUNNING)
    assert unfinished_hours(account.journal) == (at + HOUR, at + 3 * HOUR)


def test_a_freeze_exit_save_ends_its_hour(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """S29R3-1: the save of a passed FREEZE_EXIT is the end of its hour, and
    the HALT override refused for that hour is logged before it."""
    saves: list[AccountState] = []
    original = StateJournal.save

    def save(self: StateJournal, state: AccountState, when: datetime) -> None:
        saves.append(state)
        original(self, state, when)

    monkeypatch.setattr(StateJournal, "save", save)
    account = AccountDir(tmp_path / "a")
    commands = _exits(6)
    _frozen_run(account, _series(24 * 14), commands)
    exit_save = next(s for s in saves if s.mode is Mode.HALT)
    hour = exit_save.entered_at.replace(minute=0, second=0, microsecond=0)
    assert hour in commands
    assert exit_save.unfinished_from == hour + HOUR


def test_a_kill_after_a_waited_freeze_exit_names_only_the_skipped_hours(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """S29R4-2: the passed FREEZE_EXIT's reconciliation ends two hours after
    its hour H; killed right after its save, hours H+1 and H+2 were not run,
    and H, which it finished, is not named."""
    real = loop.reconcile

    def delayed(*args: object, **kwargs: object) -> object:
        report = real(*args, **kwargs)  # type: ignore[arg-type]
        return replace(report, at=report.at + 2 * HOUR) if report.passed else report

    original = StateJournal.save

    def save(self: StateJournal, state: AccountState, when: datetime) -> None:
        original(self, state, when)
        if state.mode is Mode.HALT:
            raise _Killed

    account = AccountDir(tmp_path / "a")
    commands = _exits(6)
    with monkeypatch.context() as patch, pytest.raises(_Killed):
        patch.setattr(loop, "reconcile", delayed)
        patch.setattr(StateJournal, "save", save)
        _frozen_run(account, _series(24 * 14), commands)
    state = account.journal.load()
    assert state is not None
    hour = state.entered_at.replace(minute=0, second=0, microsecond=0) - 2 * HOUR
    assert hour in commands
    assert unfinished_hours(account.journal) == (hour + HOUR, hour + 3 * HOUR)


def test_an_override_in_a_freeze_exit_hour_is_logged_after_the_exit(
    tmp_path: Path,
) -> None:
    """S29R4-1: in an hour with both FREEZE_EXIT and an override, the exit's
    refusal or transition is logged first, then the override's refusal, as
    before S29R3-1."""
    account = AccountDir(tmp_path / "a")
    commands = _exits(6)
    overrides = {hour: _override(("x",), hour) for hour in commands}
    _frozen_run(account, _series(24 * 14), commands, overrides)
    moves = [
        m
        for m in _transitions(account)
        if m.get("trigger") == "FREEZE_EXIT" or "command" in m
    ]
    passed = next(i for i, m in enumerate(moves) if m.get("trigger"))
    moves = moves[: passed + 2]  # until the exit passed: then out of FREEZE
    halt = {"command": "HALT_OVERRIDE", "refused": "FREEZE_EXIT this hour"}
    exits = [m for m in moves if m != halt]
    assert moves == [m for e in exits for m in (e, halt)]
    assert len(exits) > 1 and all("refused" in e for e in exits[:-1])
