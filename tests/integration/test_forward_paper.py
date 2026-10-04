"""Roadmap 2 Task 29: forward paper mode (`aqt.app.forward`)."""

from __future__ import annotations

import importlib.util
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import ModuleType

import pytest

from aqt.app.forward import (
    CURSOR,
    CURSOR_RECORD,
    ForwardError,
    daily_equity_returns,
    effective_decisions,
    run_step,
    skipped_while_busy_event,
)
from aqt.app.paper_loop import RunReport
from aqt.app.state import AccountDir
from aqt.core.deployment import approve
from aqt.core.ledger import append_entry, read_entries
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


def _step(
    account: AccountDir,
    series: BarSeries,
    end: datetime,
    environ: dict[str, str] | None = None,
) -> RunReport | None:
    now = end + timedelta(minutes=1)
    return run_step(
        _config(1, start=START),
        _upto(series, end),
        account,
        now=now,
        reference_now=now,
        sinks=[LedgerSink(account.operations_path, Severity.INFO)],
        data_manifest_hash="0" * 64,
        environ={} if environ is None else environ,
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


def _interruptions(account: AccountDir) -> list[dict[str, object]]:
    return [lag for lag in _lags(account) if "interrupted_step" in lag]


def _started(account: AccountDir, start: datetime, end: datetime) -> None:
    """The cursor of a step that began and never ended."""
    append_entry(
        account.root / CURSOR,
        record_type=CURSOR_RECORD,
        payload={"step": "START", "start": start.isoformat(), "end": end.isoformat()},
        recorded_at_utc=start,
    )


BALANCES = {"USDT": Decimal("10000"), "BTC": Decimal("0")}


@pytest.mark.parametrize(
    ("saved", "cut"),
    [
        # Every save site of the loop is at an hour's end (startup, the
        # hour's own save, the final save) or within one hour (owner
        # command, pre-send, FREEZE or HALT reconciliation): only that hour
        # is named, never the finished hours before it (S29R-1).
        (START + 2 * HOUR, START + 2 * HOUR),
        (START + 2 * HOUR + timedelta(minutes=20), START + 2 * HOUR),
        (START + 4 * HOUR, START + 4 * HOUR),  # the step's final save
        (START - HOUR, None),  # stopped before it saved anything
    ],
)
def test_an_interrupted_step_names_only_the_hour_of_its_last_save(
    tmp_path: Path, saved: datetime, cut: datetime | None
) -> None:
    account = AccountDir(tmp_path / "a")
    _started(account, START, START + 5 * HOUR)
    _seed(account, saved, Mode.RUNNING, BALANCES, "10000")
    report = _step(account, _series(24 * 14), START + 8 * HOUR)
    assert report is not None and report.refused == ()
    [found] = _interruptions(account)
    assert (
        found["interrupted_step"]
        == f"{START.isoformat()} to {(START + 5 * HOUR).isoformat()}"
    )
    assert found["hour_maybe_cut_short"] == (None if cut is None else cut.isoformat())
    assert found["resumed_at"] == (_floor(saved) + HOUR).isoformat()
    _step(account, _series(24 * 14), START + 9 * HOUR)
    assert len(_interruptions(account)) == 1  # the next step ended: reported once


def _floor(moment: datetime) -> datetime:
    return moment.replace(minute=0, second=0, microsecond=0)


def test_an_interrupted_pre_send_is_reported_before_its_refusal(tmp_path: Path) -> None:
    """S29R-1: the order saved as sent has an unknown outcome, which refuses
    the step; the interruption is reported first."""
    account = AccountDir(tmp_path / "a")
    _started(account, START, START + 5 * HOUR)
    _seed(
        account, START + 2 * HOUR, Mode.RUNNING, BALANCES, "10000", orders={"x": None}
    )
    with pytest.raises(ForwardError, match="unknown outcome"):
        _step(account, _series(24 * 14), START + 8 * HOUR)
    kinds = [e.payload.get("kind") for e in read_entries(account.operations_path)]
    assert kinds == ["LOOP_LAG", "STARTUP"]
    [found] = _interruptions(account)
    assert found["hour_maybe_cut_short"] == (START + 2 * HOUR).isoformat()


def test_a_refused_step_is_not_an_interruption(tmp_path: Path) -> None:
    account = AccountDir(tmp_path / "a")
    series = _series(24 * 14)
    refused = _step(account, series, START + 2 * HOUR, {"BINANCE_API_KEY": "x"})
    assert refused is not None and refused.refused
    report = _step(account, series, START + 3 * HOUR)
    assert report is not None and report.refused == ()
    assert _interruptions(account) == []
    steps = [e.payload["step"] for e in read_entries(account.root / CURSOR)]
    assert steps == ["START", "END", "START", "END"]


def test_hours_a_running_reconciliation_skips_are_reported() -> None:
    """S29R-1: the loop's last save after `end` (busy until then) means the
    hours from `end` are skipped, as a replay skips them; they are named."""
    end = START + 3 * HOUR
    assert skipped_while_busy_event(end, end, end) is None
    event = skipped_while_busy_event(end, end + 2 * HOUR, end)
    assert event is not None and event.severity is Severity.WARNING
    assert dict(event.fields) == {
        "skipped_hours": 2,
        "first_skipped": end.isoformat(),
        "last_skipped": (end + HOUR).isoformat(),
        "note": "a reconciliation was running; as in a replay, no decision "
        "is made in these hours",
    }


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


def _script() -> ModuleType:
    path = ROOT / "scripts" / "run_forward_paper.py"
    spec = importlib.util.spec_from_file_location("run_forward_paper", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _args(tmp: Path, *extra: str) -> list[str]:
    return [
        "--config", str(ROOT / "configs" / "forward_paper.example.toml"),
        "--store", str(tmp / "store.jsonl"), "--account", str(tmp / "account"),
        *extra,
    ]  # fmt: skip


@pytest.mark.parametrize(
    ("codes", "once", "expected", "steps"),
    [
        ([1, 0, 2], False, 2, 3),  # a failed fetch is retried; a refusal stops
        ([1], True, 1, 1),
        ([0], True, 0, 1),
    ],
)
def test_the_script_retries_a_failed_fetch_and_stops_on_a_refusal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    codes: list[int],
    once: bool,
    expected: int,
    steps: int,
) -> None:
    """S29R-3: exit codes 1 (retried next hour) and 2 (never retried)."""
    script = _script()
    pending = iter(codes)
    calls: list[int] = []
    monkeypatch.setattr(script, "step", lambda *_: calls.append(1) or next(pending))
    monkeypatch.setattr(script.time, "sleep", lambda _: None)
    assert script.main(_args(tmp_path, *(["--once"] if once else []))) == expected
    assert len(calls) == steps


def test_the_script_checks_the_deployment_before_anything_else(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """S29R-3: an unapproved checkout is refused, logged and exits 2 before
    the configuration (here unparsable), the store or the network."""
    script = _script()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(script, "step", lambda *_: pytest.fail("stepped"))
    record = tmp_path / "deployments.jsonl"
    at = datetime(2026, 10, 2, 12, tzinfo=UTC)
    approve(record, commit="0" * 40, approved_by="Owner", statement="ok", at=at)
    broken = tmp_path / "broken.toml"
    broken.write_text("[[[ not toml")
    args = ["--config", str(broken), "--store", "s", "--account", "a",
            "--deployment-record", str(record), "--telegram"]  # fmt: skip
    assert script.main(args) == 2
    log = (tmp_path / script.REFUSALS).read_text()
    assert "REFUSE_START" in log and "deployment: " in log
    assert not (tmp_path / "a").exists() and not (tmp_path / "s").exists()
