"""Task 24: the paper-trading loop, on synthetic bars, offline."""

from __future__ import annotations

import hashlib
import json
import math
import random
import shutil
import socket
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

import aqt.app.paper_loop as loop
from aqt.app.paper_loop import (
    ConfigError,
    HealthLimits,
    Observation,
    PaperConfig,
    load_config,
    nonce_for,
    run_paper,
)
from aqt.backtest.costs import Side as TradeSide
from aqt.data.bars import Bar, BarSeries
from aqt.execution.orders import ExecutorConfig, client_order_id_for
from aqt.execution.reconcile import LocalRecord
from aqt.execution.safety import FlattenBounds, IncidentLog, Trigger
from aqt.execution.simulator import (
    Fault,
    Order,
    OrderStatus,
    Scenario,
    SimulatedExchange,
    SymbolFilters,
)
from aqt.governor.authorization import Authorization, GovernorConfig
from aqt.governor.machine import Governor
from aqt.monitoring.alerts import AlertRouter, LedgerSink
from aqt.monitoring.events import Event, Severity

ROOT = Path(__file__).resolve().parents[2]
T0 = datetime(2020, 1, 1, tzinfo=UTC)
HOUR = timedelta(hours=1)
FILTERS = SymbolFilters(
    step_size=Decimal("0.00001"),
    min_qty=Decimal("0.00001"),
    max_qty=Decimal("9000"),
    min_notional=Decimal("5"),
    tick_size=Decimal("0.01"),
)


@pytest.fixture(autouse=True)
def _no_sockets(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_: object, **__: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)


def _series(hours: int, seed: int = 7, gap_at: int | None = None) -> BarSeries:
    """A seeded random walk, about 60% annual volatility, with tiny hourly
    open gaps so fills sit well inside a 15 bps cap."""
    rng = random.Random(seed)
    price, bars = 10_000.0, []
    for i in range(hours):
        if gap_at is not None and i == gap_at:
            continue
        close = round(price * math.exp(rng.gauss(0.0, 0.0064)), 2)
        high, low = max(price, close) * 1.001, min(price, close) * 0.999
        bars.append(
            Bar(T0 + i * HOUR, price, round(high, 2), round(low, 2), close, 5.0)
        )
        price = close
    return BarSeries("BTCUSDT", tuple(bars))


def _config(days: int, **changes: object) -> PaperConfig:
    base = PaperConfig(
        adapter="simulator",
        run_id="test-run",
        symbol="BTCUSDT",
        start=T0 + 8 * 24 * HOUR,  # after the 169-bar baseline warm-up
        end=T0 + (8 + days) * 24 * HOUR,
        starting_balances={"USDT": Decimal("10000"), "BTC": Decimal("0")},
        filters=FILTERS,
        governor=GovernorConfig(
            max_slippage_bps=Decimal("15"),
            authorization_ttl=timedelta(minutes=2),
            decision_window=timedelta(minutes=5),
        ),
        executor=ExecutorConfig(
            not_found_delay=timedelta(seconds=10), absence_queries=2
        ),
        flatten=FlattenBounds(
            max_step_fraction=Decimal("0.5"), max_slippage_bps=Decimal("100")
        ),
        tolerance={"USDT": Decimal(0), "BTC": Decimal(0)},
        loss_stop_fraction=Decimal("0.20"),
        health=HealthLimits(
            max_data_age=timedelta(hours=2),
            max_clock_skew=timedelta(seconds=5),
            max_loop_lag=timedelta(minutes=5),
        ),
    )
    return replace(base, **changes)


def _run(
    tmp: Path,
    config: PaperConfig,
    series: BarSeries,
    **kwargs: object,
) -> loop.RunReport:
    tmp.mkdir(parents=True, exist_ok=True)
    options: dict[str, object] = {
        "data_manifest_hash": "0" * 64,
        "sinks": [LedgerSink(tmp / "operations.jsonl", Severity.INFO)],
        "incidents": IncidentLog(tmp / "incidents.jsonl"),
        "operations_log": tmp / "operations.jsonl",
        "environ": {},
        "repository_root": ROOT,
    }
    options.update(kwargs)
    return run_paper(config, series, **options)  # type: ignore[arg-type]


def test_a_multi_month_run_is_deterministic(tmp_path: Path) -> None:
    series = _series(24 * 70)
    config = _config(60)
    first = _run(tmp_path / "a", config, series)
    second = _run(tmp_path / "b", config, series)
    assert first.refused == ()
    assert first.orders_sent > 0
    # This random path falls more than 20% from its peak, so the L-03 stop
    # sells everything and HALTs; the point here is that both runs agree.
    assert first.final_mode == "HALT"
    assert first.digest() == second.digest()
    log_a = (tmp_path / "a" / "operations.jsonl").read_bytes()
    assert b'"state":"FILLED"' in log_a  # orders actually filled
    assert log_a == (tmp_path / "b" / "operations.jsonl").read_bytes()


def test_the_report_names_the_hashes_and_the_decision_count(tmp_path: Path) -> None:
    report = _run(tmp_path, _config(10), _series(24 * 20))
    mapping = report.as_mapping()
    frozen = (ROOT / "FROZEN_HASHES.json").read_text("utf-8")
    assert mapping["protocol_hash"] in frozen and mapping["cost_model_hash"] in frozen
    assert mapping["data_manifest_hash"] == "0" * 64
    assert mapping["scheduled_decisions"] == 10  # one 00:00 decision a day
    assert "Bar count is not sample size" in str(mapping["note"])
    assert mapping["predictor"] == "VOL_TARGET_BUY_AND_HOLD"


def test_a_non_simulator_adapter_is_refused_at_configuration() -> None:
    with pytest.raises(ConfigError, match="simulator"):
        _config(1, adapter="binance")


def test_the_example_configuration_loads(tmp_path: Path) -> None:
    config = load_config(ROOT / "configs" / "paper_trading.example.toml")
    assert config.adapter == "simulator"
    text = (ROOT / "configs" / "paper_trading.example.toml").read_text("utf-8")
    bad = tmp_path / "bad.toml"
    bad.write_text(text.replace('adapter = "simulator"', 'adapter = "live"'), "utf-8")
    with pytest.raises(ConfigError):
        load_config(bad)
    missing = tmp_path / "missing.toml"
    missing.write_text(text.replace("absence_queries = 2", ""), "utf-8")
    with pytest.raises(ConfigError, match="absence_queries"):
        load_config(missing)


def _copy_frozen(target: Path) -> Path:
    for name in (
        "FROZEN_HASHES.json",
        "protocols/protocol_v1.yaml",
        "protocols/protocol_v1.yaml.sha256",
        "specs/COST_MODEL_v1.md",
        "specs/COST_MODEL_v1.md.sha256",
        "specs/CANONICAL_BENCHMARKS_v1.md",
        "specs/CANONICAL_BENCHMARKS_v1.md.sha256",
        "docs/RESEARCH_CONSTITUTION.md",
    ):
        (target / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target / name)
    return target


@pytest.mark.parametrize(
    "altered",
    [
        "protocols/protocol_v1.yaml",
        "specs/COST_MODEL_v1.md",
        "docs/RESEARCH_CONSTITUTION.md",
    ],
)
def test_refuse_start_on_a_hash_mismatch(tmp_path: Path, altered: str) -> None:
    root = _copy_frozen(tmp_path / "repo")
    with (root / altered).open("ab") as handle:
        handle.write(b"\n")
    report = _run(tmp_path / "run", _config(2), _series(24 * 12), repository_root=root)
    assert any("hash mismatch" in r for r in report.refused)
    assert report.orders_sent == 0


def test_refuse_start_without_an_alert_sink(tmp_path: Path) -> None:
    report = _run(tmp_path, _config(2), _series(24 * 12), sinks=[])
    assert report.refused and "no alert sink" in report.refused[0]


def test_refuse_start_on_a_damaged_operations_log(tmp_path: Path) -> None:
    tmp_path.mkdir(exist_ok=True)
    (tmp_path / "operations.jsonl").write_text("not a ledger\n", "utf-8")
    report = _run(tmp_path, _config(2), _series(24 * 12))
    assert any("hash-chain" in r for r in report.refused)


def test_refuse_start_when_a_credential_is_set(tmp_path: Path) -> None:
    report = _run(
        tmp_path, _config(2), _series(24 * 12), environ={"BINANCE_API_KEY": "x" * 64}
    )
    assert any("credential" in r for r in report.refused)
    assert all("x" * 64 not in r for r in report.refused)  # never echoed


def test_refuse_start_when_the_window_crosses_a_data_gap(tmp_path: Path) -> None:
    report = _run(tmp_path, _config(3), _series(24 * 14, gap_at=24 * 9))
    assert any("data gap" in r for r in report.refused)


def test_refuse_start_on_a_reconciliation_mismatch(tmp_path: Path) -> None:
    believed = LocalRecord({"USDT": Decimal("10000"), "BTC": Decimal("0.5")})
    report = _run(tmp_path, _config(2), _series(24 * 12), local_record=believed)
    assert any("reconciliation failed" in r for r in report.refused)


def test_refuse_start_with_an_open_incident(tmp_path: Path) -> None:
    incidents = IncidentLog(tmp_path / "incidents.jsonl")
    incidents.open("OWNER_HALT", "left open on purpose", T0)
    report = _run(tmp_path, _config(2), _series(24 * 12), incidents=incidents)
    assert any("open incidents" in r for r in report.refused)


def test_no_order_is_placed_without_a_live_unexpired_authorization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    redeemed: dict[str, Authorization] = {}
    clocks: list[loop._Clock] = []
    placed: list[tuple[str, datetime]] = []
    real_redeem, real_place = Governor.redeem, SimulatedExchange.place_order
    real_init = loop._Clock.__init__

    def redeem(
        self: Governor, auth: Authorization, state: object, now: datetime
    ) -> object:
        outcome = real_redeem(self, auth, state, now)  # type: ignore[arg-type]
        if outcome is None:
            redeemed[client_order_id_for(auth)] = auth
        return outcome

    def place(
        self: SimulatedExchange, client_order_id: str, *args: object, **kw: object
    ) -> object:
        placed.append((client_order_id, clocks[-1].now))
        return real_place(self, client_order_id, *args, **kw)  # type: ignore[arg-type]

    def init(self: loop._Clock, now: datetime) -> None:
        real_init(self, now)
        clocks.append(self)

    monkeypatch.setattr(Governor, "redeem", redeem)
    monkeypatch.setattr(SimulatedExchange, "place_order", place)
    monkeypatch.setattr(loop._Clock, "__init__", init)
    report = _run(tmp_path, _config(10), _series(24 * 20))
    assert report.orders_sent == len(placed) > 0
    for client_order_id, at in placed:
        auth = redeemed[client_order_id]
        assert auth.issued_at <= at < auth.expires_at


def test_a_mid_run_fault_ends_in_freeze_not_in_an_order(tmp_path: Path) -> None:
    series = _series(24 * 20)
    config = _config(10)
    clean = _run(tmp_path / "clean", config, series)
    assert clean.authorizations >= 1 and clean.final_mode == "RUNNING"
    # The first authorization's order times out and its query cannot be read;
    # the run goes on for the remaining days of the window.
    faulty_id = client_order_id_for(
        replace(_probe_authorization(), nonce=nonce_for(config.run_id, 0))
    )
    scenario = Scenario({faulty_id: Fault(timeout=True, unknown_queries=5)})
    report = _run(tmp_path / "fault", config, series, scenario=scenario)
    assert report.final_mode == "FREEZE"
    assert report.authorizations == 1 and report.orders_sent == 1
    incidents = IncidentLog(tmp_path / "fault" / "incidents.jsonl")
    assert len(incidents.open_incidents()) == 1
    # The freeze came from the section 21 path itself: the order's outcome
    # was unknown to the executor, not merely caught later.
    events = [
        json.loads(line)["payload"]
        for line in (tmp_path / "fault" / "operations.jsonl").read_text().splitlines()
    ]
    states = [e["fields"]["state"] for e in events if e["kind"] == "ORDER"]
    assert states == ["FREEZE"]
    assert report.hours == clean.hours  # it ran to the end, placing nothing more
    triggers = [
        e["fields"].get("trigger") for e in events if e["kind"] == "STATE_TRANSITION"
    ]
    assert triggers == ["AMBIGUOUS_ORDER"]


def _probe_authorization() -> Authorization:
    return Authorization(
        proposal_hash="",
        state_reference="",
        symbol="BTCUSDT",
        side=None,  # type: ignore[arg-type]
        current_exposure=0.0,
        target_exposure=0.0,
        max_base_quantity=Decimal(0),
        max_slippage_bps=Decimal(0),
        issued_at=T0,
        expires_at=T0,
        nonce="",
    )


def _assert_flatten_remainder_is_unsellable(btc: str, series: BarSeries) -> None:
    """FLATTEN ends when half of what is left is below the notional minimum,
    so the remainder is under twice the minimum at any price in the run."""
    lowest = min(Decimal(str(bar.close)) for bar in series.bars)
    assert Decimal(btc) < 2 * FILTERS.min_notional / lowest + FILTERS.step_size


def test_an_owner_flatten_sells_everything_then_halts(tmp_path: Path) -> None:
    config = _config(12)
    flatten_at = config.start + 5 * 24 * HOUR + 3 * HOUR
    series = _series(24 * 22)
    report = _run(
        tmp_path, config, series, commands={flatten_at: Trigger.OWNER_FLATTEN}
    )
    assert report.final_mode == "HALT"
    _assert_flatten_remainder_is_unsellable(report.final_balances["BTC"], series)
    assert report.orders_sent > report.authorizations  # the FLATTEN sells
    # T25-01: every FLATTEN sell is logged with the holding it was sized from.
    events = [
        json.loads(line)["payload"]
        for line in (tmp_path / "operations.jsonl").read_text().splitlines()
    ]
    sells = [e["fields"] for e in events if e["fields"].get("state") == "FLATTEN"]
    assert len(sells) == report.orders_sent - report.authorizations
    assert all(
        Decimal(s["orig_qty"]) <= Decimal(s["held_before"]) * Decimal("0.5")
        for s in sells
    )


def test_an_owner_halt_stops_all_orders(tmp_path: Path) -> None:
    config = _config(12)
    report = _run(
        tmp_path, config, _series(24 * 22), commands={config.start: Trigger.OWNER_HALT}
    )
    assert report.final_mode == "HALT"
    assert report.orders_sent == 0


def _crash_series(hours: int, crash_at: int) -> BarSeries:
    """Quiet random walk, then a steady 1%-an-hour fall for 40 hours."""
    rng = random.Random(3)
    price, bars = 10_000.0, []
    for i in range(hours):
        step = -0.01 if crash_at <= i < crash_at + 40 else rng.gauss(0.0, 0.003)
        close = round(price * math.exp(step), 2)
        high, low = max(price, close) * 1.0005, min(price, close) * 0.9995
        bars.append(
            Bar(T0 + i * HOUR, price, round(high, 2), round(low, 2), close, 5.0)
        )
        price = close
    return BarSeries("BTCUSDT", tuple(bars))


def test_the_loss_stop_sells_everything_then_halts(tmp_path: Path) -> None:
    """Adopted L-03 with owner setting S-4: 20% below peak equity enters
    FLATTEN, which sells the holding and ends in HALT."""
    config = _config(12)
    series = _crash_series(24 * 22, crash_at=24 * 12)
    report = _run(tmp_path, config, series)
    events = [
        json.loads(line)["payload"]
        for line in (tmp_path / "operations.jsonl").read_text().splitlines()
    ]
    triggers = [
        e["fields"].get("trigger") for e in events if e["kind"] == "STATE_TRANSITION"
    ]
    # Fires once: the unsellable remainder left after FLATTEN does not
    # re-trigger the stop every hour.
    assert triggers.count("LOSS_STOP") == 1
    assert triggers[-1] == "FLATTEN_DONE"
    assert report.final_mode == "HALT"
    _assert_flatten_remainder_is_unsellable(report.final_balances["BTC"], series)


def test_no_loss_stop_without_a_drawdown(tmp_path: Path) -> None:
    report = _run(tmp_path, _config(10), _series(24 * 20))
    assert report.final_mode == "RUNNING"


def test_refuse_start_when_a_health_check_fails(tmp_path: Path) -> None:
    def stale(at: datetime) -> Observation:
        return Observation(at - 3 * HOUR, at, at, at)

    report = _run(tmp_path, _config(2), _series(24 * 12), observe=stale)
    assert any(
        "health check at start" in r and "STALE_DATA" in r for r in report.refused
    )


def test_a_health_breach_blocks_orders_for_that_hour(tmp_path: Path) -> None:
    config = _config(3)
    bad = {config.start + h * HOUR for h in range(1, 30)}  # includes day 2's 00:00

    def skewed(at: datetime) -> Observation:
        off = timedelta(seconds=9) if at in bad else timedelta(0)
        return Observation(at, at + off, at, at)

    clean = _run(tmp_path / "clean", config, _series(24 * 14))
    report = _run(tmp_path / "skew", config, _series(24 * 14), observe=skewed)
    assert report.health_breach_hours == len(bad)
    events = [
        json.loads(line)["payload"]
        for line in (tmp_path / "skew" / "operations.jsonl").read_text().splitlines()
    ]
    skews = [e for e in events if e["kind"] == "CLOCK_SKEW"]
    assert len(skews) == len(bad) and all(e["severity"] == "CRITICAL" for e in skews)
    assert report.scheduled_decisions == clean.scheduled_decisions - 1


class _ListSink:
    min_severity = Severity.INFO

    def __init__(self) -> None:
        self.events: list[Event] = []

    def write(self, event: Event) -> None:
        self.events.append(event)


def _filled_order() -> Order:
    return Order(
        client_order_id="aqt-test",
        symbol="BTCUSDT",
        side=TradeSide.SELL,
        orig_qty=Decimal("0.1"),
        executed_qty=Decimal("0.1"),
        status=OrderStatus.FILLED,
        decision_time=T0,
        fill_time=T0,
        fill_price=Decimal("100"),
        quote_amount=Decimal("10"),
        cost_quote=Decimal("0"),
        cost_bps=Decimal("0"),
    )


class _BrokenIncidentLog(IncidentLog):
    def open(self, kind: str, detail: str, at: datetime) -> str:
        raise OSError("incident ledger failed")


def test_a_failed_audit_write_refuses_every_later_start(tmp_path: Path) -> None:
    """T23-04: a crash mid-run leaves a marker that refuses the next start."""
    config = _config(2)
    broken = _BrokenIncidentLog(tmp_path / "incidents.jsonl")
    with pytest.raises(OSError, match="incident ledger failed"):
        _run(
            tmp_path,
            config,
            _series(24 * 12),
            incidents=broken,
            commands={config.start + HOUR: Trigger.OWNER_HALT},
        )
    marker = loop.refuse_marker_path(broken)
    assert "incident ledger failed" in marker.read_text("utf-8")

    report = _run(tmp_path, config, _series(24 * 12))
    assert report.final_mode == "REFUSED"
    assert any("stopped on an error" in r for r in report.refused)


def test_consecutive_zero_fills_raise_a_critical_alert() -> None:
    """T23-08: every third IOC order in a row with nothing filled alerts."""
    sink = _ListSink()
    router = AlertRouter([sink])
    empty = replace(_filled_order(), executed_qty=Decimal(0))
    streak = 0
    for _ in range(3):
        streak = loop._zero_fill_alert(router, streak, empty, T0)
    assert streak == 3
    assert [e.fields["zero_fill_streak"] for e in sink.events] == [3]
    assert sink.events[0].severity is Severity.CRITICAL
    assert loop._zero_fill_alert(router, streak, _filled_order(), T0) == 0


def test_rewriting_a_frozen_file_and_its_hashes_is_still_refused(
    tmp_path: Path,
) -> None:
    """F24-2: the manifest is pinned in code, so rewritten hashes do not hide
    an edit."""
    root = _copy_frozen(tmp_path / "repo")
    protocol = root / "protocols" / "protocol_v1.yaml"
    with protocol.open("ab") as handle:
        handle.write(b"\n")
    digest = hashlib.sha256(protocol.read_bytes()).hexdigest()
    (root / "protocols" / "protocol_v1.yaml.sha256").write_text(
        f"{digest}  protocol_v1.yaml\n", "utf-8"
    )
    manifest = root / "FROZEN_HASHES.json"
    frozen = json.loads(manifest.read_text("utf-8"))
    frozen["protocol_file_sha256"] = digest
    manifest.write_text(json.dumps(frozen), "utf-8")
    assert loop.frozen_hash_problems(root) == [
        "FROZEN_HASHES.json: does not match the pinned hash"
    ]


def test_the_loss_stop_never_overrides_an_owner_halt(tmp_path: Path) -> None:
    """F24-1: the owner pressed FLATTEN, then HALT, during the fall. The L-03
    stop must not restart selling."""
    config = _config(12)
    series = _crash_series(24 * 22, crash_at=24 * 12)
    flatten_at = datetime(2020, 1, 13, 21, tzinfo=UTC)
    commands = {
        flatten_at: Trigger.OWNER_FLATTEN,
        flatten_at + HOUR: Trigger.OWNER_HALT,
    }
    report = _run(tmp_path, config, series, commands=commands)
    events = [
        json.loads(line)["payload"]
        for line in (tmp_path / "operations.jsonl").read_text().splitlines()
    ]
    moves = [
        (e["fields"].get("from"), e["fields"].get("to"))
        for e in events
        if e["kind"] == "STATE_TRANSITION" and "to" in e["fields"]
    ]
    assert ("FLATTEN", "HALT") in moves
    assert ("HALT", "FLATTEN") not in moves
    # F24S-2: the breach during the owner's FLATTEN alerts, FLATTEN goes on.
    stops = [
        (e["fields"]["from"], e["fields"]["to"], e["severity"])
        for e in events
        if e["kind"] == "STATE_TRANSITION" and e["fields"].get("trigger") == "LOSS_STOP"
    ]
    assert stops == [("FLATTEN", "FLATTEN", "CRITICAL")]
    assert report.final_mode == "HALT"


def test_a_loss_stop_breach_after_an_owner_halt_alerts_but_sells_nothing(
    tmp_path: Path,
) -> None:
    """F24R-1: the owner's HALT wins, but the breach is still an incident and
    a CRITICAL alert."""
    config = _config(12)
    series = _crash_series(24 * 22, crash_at=24 * 12)
    halt_at = datetime(2020, 1, 10, 5, tzinfo=UTC)
    report = _run(tmp_path, config, series, commands={halt_at: Trigger.OWNER_HALT})
    events = [
        json.loads(line)["payload"]
        for line in (tmp_path / "operations.jsonl").read_text().splitlines()
    ]
    stops = [
        e
        for e in events
        if e["kind"] == "STATE_TRANSITION" and e["fields"].get("trigger") == "LOSS_STOP"
    ]
    assert len(stops) == 1
    assert (stops[0]["fields"]["from"], stops[0]["fields"]["to"]) == ("HALT", "HALT")
    assert stops[0]["severity"] == "CRITICAL"
    incidents = IncidentLog(tmp_path / "incidents.jsonl")
    assert len(incidents.open_incidents()) == 2  # the owner HALT and the stop
    orders_after = [
        e for e in events if e["kind"] == "ORDER" and e["at"] > halt_at.isoformat()
    ]
    assert orders_after == []
    assert report.final_mode == "HALT"


def _ops(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)["payload"]
        for line in (path / "operations.jsonl").read_text().splitlines()
    ]


def test_a_breach_on_a_holding_too_small_to_sell_still_alerts(tmp_path: Path) -> None:
    """A2324-2: an account of dust below the minimum quantity, halted by the
    owner, falls more than 20%: the stop alerts CRITICAL with an incident."""
    config = _config(
        12, starting_balances={"USDT": Decimal(0), "BTC": Decimal("0.000009")}
    )
    series = _crash_series(24 * 22, crash_at=24 * 12)
    report = _run(tmp_path, config, series, commands={config.start: Trigger.OWNER_HALT})
    stops = [
        e
        for e in _ops(tmp_path)
        if e["kind"] == "STATE_TRANSITION" and e["fields"].get("trigger") == "LOSS_STOP"  # type: ignore[union-attr]
    ]
    assert len(stops) == 1 and stops[0]["severity"] == "CRITICAL"
    assert report.orders_sent == 0 and report.final_mode == "HALT"


def test_the_configuration_reads_the_maximum_notional(tmp_path: Path) -> None:
    """A2324-3: a configured maximum is never silently dropped."""
    text = (ROOT / "configs" / "paper_trading.example.toml").read_text("utf-8")
    path = tmp_path / "config.toml"
    path.write_text(text.replace("[filters]", '[filters]\nmax_notional = "20"', 1))
    assert load_config(path).filters.max_notional == Decimal(20)
    assert (
        load_config(
            ROOT / "configs" / "paper_trading.example.toml"
        ).filters.max_notional
        is None
    )


def test_a_malformed_frozen_manifest_is_a_logged_refusal(tmp_path: Path) -> None:
    """A2324-4: a damaged FROZEN_HASHES.json refuses the start through the
    normal, logged REFUSE_START path instead of raising."""
    root = _copy_frozen(tmp_path / "repo")
    (root / "FROZEN_HASHES.json").write_text("{", "utf-8")
    report = _run(tmp_path / "run", _config(2), _series(24 * 12), repository_root=root)
    assert report.final_mode == "REFUSED" and report.orders_sent == 0
    assert report.protocol_hash == "unreadable"
    refusals = [e for e in _ops(tmp_path / "run") if e["kind"] == "STARTUP"]
    assert refusals and all(
        e["fields"]["decision"] == "REFUSE_START"  # type: ignore[index]
        for e in refusals
    )


def test_a_flatten_sell_with_a_lost_reply_is_logged_and_counted(
    tmp_path: Path,
) -> None:
    """A25R-4: the sell reached the venue and filled, its reply was lost; the
    loop logs it as FLATTEN_UNKNOWN, counts it, and ends in FREEZE."""
    config = _config(12)
    flatten_at = config.start + 5 * 24 * HOUR + 3 * HOUR
    step_id = (
        "aqt-flat-"
        + hashlib.sha256(f"BTCUSDT|{flatten_at.isoformat()}|1".encode()).hexdigest()[
            :27
        ]
    )
    report = _run(
        tmp_path,
        config,
        _series(24 * 22),
        commands={flatten_at: Trigger.OWNER_FLATTEN},
        scenario=Scenario({step_id: Fault(timeout=True)}),
    )
    lost = [
        e["fields"]
        for e in _ops(tmp_path)
        if e["kind"] == "ORDER" and e["fields"].get("state") == "FLATTEN_UNKNOWN"  # type: ignore[union-attr]
    ]
    assert [f["client_order_id"] for f in lost] == [step_id]  # type: ignore[index]
    assert report.final_mode == "FREEZE"
    assert report.orders_sent == report.authorizations + 1
