"""Roadmap 2 Task 29: forward paper mode (`aqt.app.forward`)."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from aqt.app.forward import (
    ForwardError,
    daily_equity_returns,
    effective_decisions,
    run_step,
)
from aqt.app.paper_loop import RunReport
from aqt.app.state import AccountDir
from aqt.core.ledger import read_entries
from aqt.data.bars import BarSeries
from aqt.execution.safety import Mode
from aqt.execution.simulator import SimulatedExchange
from aqt.monitoring.alerts import LedgerSink
from aqt.monitoring.events import Severity
from tests.integration.test_paper_loop import (
    FILTERS,
    HOUR,
    ROOT,
    _config,
    _run,
    _series,
)
from tests.integration.test_paper_recovery import _seed
from tests.integration.test_paper_restart import START

HOURS = 30  # two 00:00 decisions: START and START + 24h


def _upto(series: BarSeries, end: datetime) -> BarSeries:
    """The bars closed by `end`: what the live store holds then."""
    return BarSeries(series.symbol, tuple(b for b in series.bars if b.open_time < end))


def _step(account: AccountDir, series: BarSeries, end: datetime) -> RunReport | None:
    now = end + timedelta(minutes=1)
    return run_step(
        _config(1, start=START),
        _upto(series, end),
        account,
        now=now,
        reference_now=now,
        sinks=[LedgerSink(account.operations_path, Severity.INFO)],
        data_manifest_hash="0" * 64,
        environ={},
        repository_root=ROOT,
    )


def _replay(tmp: Path, series: BarSeries) -> tuple[RunReport, AccountDir]:
    account = AccountDir(tmp)
    config = _config(1, start=START, end=START + HOURS * HOUR)
    venue = SimulatedExchange(
        {"BTCUSDT": series}, {"BTCUSDT": FILTERS}, dict(config.starting_balances)
    )
    report = _run(
        account.root,
        config,
        series,
        incidents=account.incident_log(),
        journal=account.journal,
        venue=venue,
    )
    assert report.refused == ()
    return report, account


def test_hourly_forward_steps_end_where_one_replay_ends(tmp_path: Path) -> None:
    series = _series(24 * 14)
    whole, replayed = _replay(tmp_path / "replay", series)
    account = AccountDir(tmp_path / "forward")
    assert _step(account, series, START) is None  # the first fill bar is not closed
    orders = 0
    for k in range(1, HOURS + 1):
        report = _step(account, series, START + k * HOUR)
        assert report is not None and report.refused == ()
        orders += report.orders_sent
    assert orders == whole.orders_sent > 0
    assert report.final_balances == whole.final_balances
    forward, replay = account.journal.load(), replayed.journal.load()
    assert forward is not None and replay is not None
    assert (forward.peak, forward.mode) == (replay.peak, replay.mode)
    assert _lags(account) == []  # on time and never interrupted: no breach


def _lags(account: AccountDir) -> list[dict[str, object]]:
    return [
        e.payload["fields"]
        for e in read_entries(account.operations_path)
        if e.payload.get("kind") == "LOOP_LAG"
    ]


def test_a_step_interrupted_after_a_save_is_reported(tmp_path: Path) -> None:
    """S29-1: a crash after the start-of-run save at START + 2h, before the
    step completed: the next step reports the hours from the cursor (none
    yet: the first hour) up to where the loop resumes."""
    account = AccountDir(tmp_path / "a")
    balances = {"USDT": Decimal("10000"), "BTC": Decimal("0")}
    _seed(account, START + 2 * HOUR, Mode.RUNNING, balances, "10000")
    report = _step(account, _series(24 * 14), START + 5 * HOUR)
    assert report is not None and report.refused == ()
    interrupted = [lag for lag in _lags(account) if "interrupted_from" in lag]
    assert [(i["interrupted_from"], i["resumed_at"]) for i in interrupted] == [
        (START.isoformat(), (START + 3 * HOUR).isoformat())
    ]
    again = _step(account, _series(24 * 14), START + 6 * HOUR)
    assert again is not None
    assert len([lag for lag in _lags(account) if "interrupted_from" in lag]) == 1


def test_a_damaged_journal_is_a_logged_refusal(tmp_path: Path) -> None:
    """S29-2."""
    account = AccountDir(tmp_path / "a")
    account.journal.path.write_text("not a ledger", encoding="utf-8")
    with pytest.raises(ForwardError):
        _step(account, _series(24 * 14), START + 2 * HOUR)
    starts = [
        e.payload["fields"]
        for e in read_entries(account.operations_path)
        if e.payload.get("kind") == "STARTUP"
    ]
    assert starts[-1]["decision"] == "REFUSE_START"


def test_missed_hours_are_a_breach_then_run_as_a_replay(tmp_path: Path) -> None:
    series = _series(24 * 14)
    whole, _ = _replay(tmp_path / "replay", series)
    account = AccountDir(tmp_path / "forward")
    _step(account, series, START + 3 * HOUR)
    report = _step(account, series, START + HOURS * HOUR)  # down for 26 hours
    assert report is not None and report.refused == ()
    assert report.final_balances == whole.final_balances
    lags = _lags(account)
    assert lags[0]["missed_hours"] == 2  # the first step also started late
    assert lags[1:] == [
        {
            "first_missed": (START + 3 * HOUR).isoformat(),
            "last_missed": (START + (HOURS - 2) * HOUR).isoformat(),
            "missed_hours": HOURS - 4,
            "note": "run late, as a replay would run them",
        }
    ]


def test_an_order_with_an_unknown_outcome_refuses_the_step(tmp_path: Path) -> None:
    account = AccountDir(tmp_path / "a")
    balances = {"USDT": Decimal("10000"), "BTC": Decimal("0")}
    _seed(account, START, Mode.FREEZE, balances, "10000", orders={"lost": None})
    with pytest.raises(ForwardError, match="unknown outcome"):
        _step(account, _series(24 * 14), START + 2 * HOUR)


def test_l02_counts_a_hand_computed_example() -> None:
    """Snapshots: 1000 USDT on day 0, then 0.1 BTC from day 1 05:00. Closes at
    the next three midnights 10000, 11000, 9900 give equity 1000, 1100, 990:
    returns +0.10 and -0.10. Newey-West with n = 2, h = 1: lag
    min(1, max(0, floor(4 * 0.02 ** (2/9)))) = 1; mean 0; gamma0 =
    (0.01 + 0.01) / 2 = 0.01; gamma1 = (0.1 * -0.1) / 2 = -0.005; omega =
    0.01 + 2 * (1 - 1/2) * -0.005 = 0.005; ESS = 2 * 0.01 / 0.005 = 4,
    clamped to n = 2."""
    day0 = datetime.fromisoformat("2026-10-01T10:00:00+00:00")
    midnight = day0.replace(hour=0) + timedelta(days=1)
    saved = [
        (day0, {"USDT": Decimal("1000"), "BTC": Decimal("0")}),
        (midnight + timedelta(hours=5), {"USDT": Decimal("0"), "BTC": Decimal("0.1")}),
    ]
    closes = {
        midnight: Decimal("10000"),
        midnight + timedelta(days=1): Decimal("11000"),
        midnight + timedelta(days=2): Decimal("9900"),
    }
    returns = daily_equity_returns(saved, closes, "BTC")
    assert returns == pytest.approx([0.10, -0.10])
    count = effective_decisions(returns)
    assert (count.raw_decisions, count.value, count.method) == (2, 2.0, "NEWEY_WEST")
    # S29-4: a first snapshot exactly at midnight values that midnight too.
    aligned = [(midnight, saved[0][1])]
    assert daily_equity_returns(aligned, closes, "BTC") == [0.0, 0.0]
    flat = effective_decisions([0.0, 0.0, 0.0])
    assert (flat.value, flat.method) == (3.0, "HORIZON_FALLBACK")
