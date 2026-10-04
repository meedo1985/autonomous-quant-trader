"""Roadmap 2 Task 29: forward paper mode (`aqt.app.forward`)."""

from __future__ import annotations

import contextlib
import importlib.util
from dataclasses import replace
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
    unfinished_hours,
)
from aqt.app.paper_loop import RunReport, nonce_for, refuse_marker_path
from aqt.app.state import AccountDir, AccountState, StateJournal
from aqt.core.deployment import approve
from aqt.core.ledger import append_entry, read_entries
from aqt.data.bars import BarSeries
from aqt.execution.orders import ExecutorConfig, client_order_id_for
from aqt.execution.safety import Mode
from aqt.execution.simulator import Fault, Scenario, SimulatedExchange
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
from tests.integration.test_paper_recovery import _probe_authorization, _seed
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


class _Crash(BaseException):
    """The process killed right after a journal save."""


def _crashed(
    tmp: Path, monkeypatch: pytest.MonkeyPatch, after: int | None, hours: int = 6
) -> AccountDir:
    """The account of a run whose order's reconciliation ends two hours
    after its decision hour (A2324R-4), killed after its `after`-th journal
    save (`None`: never). A kill leaves no refuse marker."""
    config = _config(
        1,
        start=START,
        end=START + hours * HOUR,
        executor=ExecutorConfig(not_found_delay=timedelta(hours=2), absence_queries=2),
    )
    first = client_order_id_for(
        replace(_probe_authorization(), nonce=nonce_for(config.run_id, 0))
    )
    account = AccountDir(tmp)
    saves = 0
    original = StateJournal.save

    def save(self: StateJournal, state: AccountState, at: datetime) -> None:
        nonlocal saves
        original(self, state, at)
        saves += 1
        if saves == after:
            raise _Crash

    with monkeypatch.context() as patch, contextlib.suppress(_Crash):
        patch.setattr(StateJournal, "save", save)
        _run(
            account.root,
            config,
            _series(24 * 14),
            incidents=account.incident_log(),
            journal=account.journal,
            scenario=Scenario({first: Fault(timeout=True, not_found_queries=1)}),
        )
    refuse_marker_path(account.incident_log()).unlink(missing_ok=True)
    return account


@pytest.mark.parametrize(
    ("after", "unfinished"),
    [
        # S29R2-1: each save records the first hour not finished, so a kill
        # right after it names exactly the hours not run, and no others.
        (1, (0, 1)),  # the startup save: hour 0 not decided yet
        (2, (0, 1)),  # the pre-send save of hour 0's order
        (3, (1, 3)),  # hour 0 ended at 02:00: hours 1 and 2 not run
        (4, (2, 3)),  # hour 1 skipped while busy; hour 2 not run
        (5, None),  # hour 2 skipped while busy: every hour so far finished
        (None, None),  # the final save: every hour finished
    ],
)
def test_a_kill_after_any_save_names_exactly_the_hours_not_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    after: int | None,
    unfinished: tuple[int, int] | None,
) -> None:
    account = _crashed(tmp_path / "a", monkeypatch, after)
    expected = (
        None
        if unfinished is None
        else (START + unfinished[0] * HOUR, START + unfinished[1] * HOUR)
    )
    assert unfinished_hours(account.journal) == expected


def test_an_interrupted_step_is_reported_with_its_hours(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """S29R2-1: killed after the save that ends hour 0's two-hour
    reconciliation: the next step names hours 1 and 2, before anything
    else, and only once."""
    account = _crashed(tmp_path / "a", monkeypatch, 3)
    _started(account, START, START + 6 * HOUR)
    before = len(read_entries(account.operations_path))
    _step(account, _series(24 * 14), START + 8 * HOUR)
    [found] = _interruptions(account)
    assert {
        k: found[k] for k in ("first_unfinished", "last_unfinished", "resumed_at")
    } == {
        "first_unfinished": (START + HOUR).isoformat(),
        "last_unfinished": (START + 2 * HOUR).isoformat(),
        "resumed_at": (START + 3 * HOUR).isoformat(),
    }
    first = read_entries(account.operations_path)[before].payload
    assert first.get("kind") == "LOOP_LAG" and "interrupted_step" in first["fields"]
    _step(account, _series(24 * 14), START + 9 * HOUR)
    assert len(_interruptions(account)) == 1


def test_a_kill_after_the_final_save_reports_nothing(tmp_path: Path) -> None:
    """S29R2-1: the step finished every hour; only its `END` was lost."""
    account = AccountDir(tmp_path / "a")
    series = _series(24 * 14)
    _step(account, series, START + 3 * HOUR)
    _started(account, START + 2 * HOUR, START + 3 * HOUR)  # the lost END
    report = _step(account, series, START + 4 * HOUR)
    assert report is not None and report.refused == ()
    assert _interruptions(account) == []


def test_an_interrupted_pre_send_is_reported_before_its_refusal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """S29R-1: the order saved as sent has an unknown outcome, which refuses
    the step; the interruption is reported first."""
    account = _crashed(tmp_path / "a", monkeypatch, 2)
    _started(account, START, START + 6 * HOUR)
    with pytest.raises(ForwardError, match="unknown outcome"):
        _step(account, _series(24 * 14), START + 8 * HOUR)
    kinds = [e.payload.get("kind") for e in read_entries(account.operations_path)]
    assert kinds[-2:] == ["LOOP_LAG", "STARTUP"]
    [found] = _interruptions(account)
    assert found["first_unfinished"] == found["last_unfinished"] == START.isoformat()


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


def test_hours_a_running_reconciliation_skips_are_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """S29R-1: a run ending at hour 1 whose reconciliation runs to 02:00
    saves after hours 1 and 2, which it skipped as a replay skips them; they
    are named as a warning."""
    account = _crashed(tmp_path / "a", monkeypatch, None, hours=1)
    skipped = unfinished_hours(account.journal)
    assert skipped == (START + HOUR, START + 3 * HOUR)
    event = skipped_while_busy_event(skipped, START)
    assert event.severity is Severity.WARNING
    assert dict(event.fields) == {
        "skipped_hours": 2,
        "first_skipped": (START + HOUR).isoformat(),
        "last_skipped": (START + 2 * HOUR).isoformat(),
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
