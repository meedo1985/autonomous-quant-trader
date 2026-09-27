"""Task 24: the paper-trading loop, on synthetic bars, offline."""

from __future__ import annotations

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
    PaperConfig,
    load_config,
    nonce_for,
    run_paper,
)
from aqt.data.bars import Bar, BarSeries
from aqt.execution.orders import ExecutorConfig, client_order_id_for
from aqt.execution.reconcile import LocalRecord
from aqt.execution.safety import FlattenBounds, IncidentLog, Trigger
from aqt.execution.simulator import Fault, Scenario, SimulatedExchange, SymbolFilters
from aqt.governor.authorization import Authorization, GovernorConfig
from aqt.governor.machine import Governor
from aqt.monitoring.alerts import LedgerSink
from aqt.monitoring.events import Severity

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
    assert first.orders_sent > 0 and first.final_mode == "RUNNING"
    assert Decimal(first.final_balances["BTC"]) > 0  # orders actually filled
    assert first.digest() == second.digest()
    log_a = (tmp_path / "a" / "operations.jsonl").read_bytes()
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


def test_an_owner_flatten_sells_everything_then_halts(tmp_path: Path) -> None:
    config = _config(12)
    flatten_at = config.start + 5 * 24 * HOUR + 3 * HOUR
    report = _run(
        tmp_path, config, _series(24 * 22), commands={flatten_at: Trigger.OWNER_FLATTEN}
    )
    assert report.final_mode == "HALT"
    assert Decimal(report.final_balances["BTC"]) * 10_000 < FILTERS.min_notional
    assert report.orders_sent > report.authorizations  # the FLATTEN sells


def test_an_owner_halt_stops_all_orders(tmp_path: Path) -> None:
    config = _config(12)
    report = _run(
        tmp_path, config, _series(24 * 22), commands={config.start: Trigger.OWNER_HALT}
    )
    assert report.final_mode == "HALT"
    assert report.orders_sent == 0
