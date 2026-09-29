"""The paper-trading loop (roadmap Task 24; Constitution sections 11, 19, 23).

Section 19: "predictor → governor → executor → exchange. Alerting before
shadow. Startup reconciliation required. Config/hash mismatch →
REFUSE_START." Each hour of a simulated run goes through the steps in that
order, against the Task 18 simulator only:

1. The safety controller acts first. In FLATTEN it takes one step; in HALT or
   FREEZE nothing trades (Task 23).
2. The predictor proposes the frozen baseline's target (`predictor.py`).
3. The governor authorizes it from the reconciled state, or refuses (Task 21).
4. The executor places at most one capped order under the authorization
   (Task 22). An unclear outcome FREEZEs the controller.
5. Anything sent is reconciled straight away. Only a passed reconciliation
   releases the reservation; a failed one FREEZEs.

`start` refuses (REFUSE_START) before anything runs if any of these holds:
a frozen hash differs; no alert sink is configured; the operations log fails
its chain check; a Binance credential variable is set; the run window is not
inside one unbroken run of bars; the startup reconciliation fails; or an
incident is open. A non-simulator adapter is
refused when the configuration is read. Every refusal is logged.

The run is deterministic: the clock is the bar clock, and governor nonces
come from the run id and a counter, so two runs of one configuration produce
the same report and the same log bytes.
"""

from __future__ import annotations

import hashlib
import json
import tomllib
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Final

from aqt.allocation.predictor import PREDICTOR_BENCHMARK, baseline_proposal
from aqt.core.ledger import LedgerError, verify_ledger
from aqt.data.bars import BarSeries, require_utc
from aqt.data.binance_public import DownloadError, refuse_credentials
from aqt.execution.machine import Executor, State
from aqt.execution.orders import ExecutorConfig
from aqt.execution.reconcile import LocalRecord, reconcile, settle
from aqt.execution.safety import (
    FlattenBounds,
    IncidentLog,
    Mode,
    SafetyController,
    SafetyError,
    Trigger,
    startup_check,
)
from aqt.execution.simulator import Order, Scenario, SimulatedExchange, SymbolFilters
from aqt.governor.authorization import ActualState, GovernorConfig, Refusal, Side
from aqt.governor.machine import Governor
from aqt.monitoring.alerts import AlertConfigError, AlertRouter, Sink
from aqt.monitoring.events import Event, EventKind, Severity
from aqt.monitoring.health import check_clock_skew, check_loop_lag, check_stale_data

__all__ = [
    "ConfigError",
    "HealthLimits",
    "Observation",
    "PaperConfig",
    "RunReport",
    "contiguous_window",
    "frozen_hash_problems",
    "load_config",
    "nonce_for",
    "run_paper",
]

HOUR: Final = timedelta(hours=1)
_QUOTE: Final[str] = "USDT"
_SIMULATOR: Final[str] = "simulator"


class ConfigError(ValueError):
    """The configuration cannot describe a paper run."""


@dataclass(frozen=True, slots=True)
class HealthLimits:
    """Owner setting S-5 (deployment draft section 4 item 9)."""

    max_data_age: timedelta
    max_clock_skew: timedelta
    max_loop_lag: timedelta

    def __post_init__(self) -> None:
        for name in ("max_data_age", "max_clock_skew", "max_loop_lag"):
            if getattr(self, name) <= timedelta(0):
                raise ConfigError(f"{name} must be positive")


@dataclass(frozen=True, slots=True)
class Observation:
    """What the health checks look at for one hour. On a simulated run all
    of it is the bar clock; a live adapter would supply real readings."""

    latest_bar_close: datetime
    local_now: datetime
    reference_now: datetime
    started: datetime


def bar_clock_observation(decision_time: datetime) -> Observation:
    return Observation(decision_time, decision_time, decision_time, decision_time)


def health_breaches(
    limits: HealthLimits, scheduled: datetime, seen: Observation
) -> list[Event]:
    checks = (
        check_stale_data(
            latest_bar_close=seen.latest_bar_close,
            now=seen.local_now,
            max_age=limits.max_data_age,
            severity=Severity.CRITICAL,
        ),
        check_clock_skew(
            local_now=seen.local_now,
            reference_now=seen.reference_now,
            max_skew=limits.max_clock_skew,
            severity=Severity.CRITICAL,
        ),
        check_loop_lag(
            scheduled=scheduled,
            started=seen.started,
            max_lag=limits.max_loop_lag,
            severity=Severity.CRITICAL,
        ),
    )
    return [event for event in checks if event is not None]


@dataclass(frozen=True, slots=True)
class PaperConfig:
    """Every value is required; the `[OPEN]` ones come from the owner."""

    adapter: str
    run_id: str
    symbol: str
    start: datetime
    end: datetime
    starting_balances: Mapping[str, Decimal]
    filters: SymbolFilters
    governor: GovernorConfig
    executor: ExecutorConfig
    flatten: FlattenBounds
    tolerance: Mapping[str, Decimal]
    loss_stop_fraction: Decimal
    health: HealthLimits

    def __post_init__(self) -> None:
        if not 0 < self.loss_stop_fraction < 1:
            raise ConfigError(f"invalid loss_stop_fraction {self.loss_stop_fraction}")
        if self.adapter != _SIMULATOR:
            # Deployment draft section 4 item 6: paper runs on the simulator only.
            raise ConfigError(f"adapter must be {_SIMULATOR!r}, got {self.adapter!r}")
        require_utc(self.start, field_name="start")
        require_utc(self.end, field_name="end")
        if self.end <= self.start:
            raise ConfigError("end must be after start")
        if not self.run_id:
            raise ConfigError("run_id is required")


def _decimal(value: object, name: str) -> Decimal:
    if not isinstance(value, str):
        raise ConfigError(f"{name} must be a decimal string, got {value!r}")
    return Decimal(value)


def _time(value: object, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ConfigError(f"{name} must be a UTC offset datetime, got {value!r}")
    return require_utc(value, field_name=name)


def load_config(path: Path) -> PaperConfig:
    """Read a TOML configuration. Nothing is defaulted."""
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    try:
        run, fil, gov, exe, fla = (
            raw["run"],
            raw["filters"],
            raw["governor"],
            raw["executor"],
            raw["flatten"],
        )
        return PaperConfig(
            adapter=str(run["adapter"]),
            run_id=str(run["run_id"]),
            symbol=str(run["symbol"]),
            start=_time(run["start"], "start"),
            end=_time(run["end"], "end"),
            starting_balances={
                k: _decimal(v, k) for k, v in raw["starting_balances"].items()
            },
            filters=SymbolFilters(
                step_size=_decimal(fil["step_size"], "step_size"),
                min_qty=_decimal(fil["min_qty"], "min_qty"),
                max_qty=_decimal(fil["max_qty"], "max_qty"),
                min_notional=_decimal(fil["min_notional"], "min_notional"),
                tick_size=_decimal(fil["tick_size"], "tick_size"),
            ),
            governor=GovernorConfig(
                max_slippage_bps=_decimal(gov["max_slippage_bps"], "max_slippage_bps"),
                authorization_ttl=timedelta(seconds=int(gov["authorization_ttl_s"])),
                decision_window=timedelta(seconds=int(gov["decision_window_s"])),
            ),
            executor=ExecutorConfig(
                not_found_delay=timedelta(seconds=int(exe["not_found_delay_s"])),
                absence_queries=int(exe["absence_queries"]),
            ),
            flatten=FlattenBounds(
                max_step_fraction=_decimal(
                    fla["max_step_fraction"], "max_step_fraction"
                ),
                max_slippage_bps=_decimal(fla["max_slippage_bps"], "flatten slippage"),
            ),
            tolerance={k: _decimal(v, k) for k, v in raw["tolerance"].items()},
            loss_stop_fraction=_decimal(raw["loss_stop"]["fraction"], "loss_stop"),
            health=HealthLimits(
                max_data_age=timedelta(seconds=int(raw["health"]["max_data_age_s"])),
                max_clock_skew=timedelta(
                    seconds=int(raw["health"]["max_clock_skew_s"])
                ),
                max_loop_lag=timedelta(seconds=int(raw["health"]["max_loop_lag_s"])),
            ),
        )
    except KeyError as missing:
        raise ConfigError(f"missing configuration value {missing}") from None


def nonce_for(run_id: str, counter: int) -> str:
    """Governor nonces: deterministic within a run, distinct across runs."""
    return hashlib.sha256(f"{run_id}|{counter}".encode()).hexdigest()[:32]


def contiguous_window(
    series: BarSeries, start: datetime, end: datetime
) -> BarSeries | str:
    """The unbroken run of bars that holds every bar the window needs: the
    decision bar before `start` through the fill bar of the last decision.
    The frozen cost model and baseline both refuse gapped history, so a
    window that crosses a data gap cannot be simulated; it is refused, never
    bridged."""
    bars = series.bars
    try:
        first = series.index_of(start - series.interval)
        last = series.index_of(end - series.interval)
    except Exception as error:  # noqa: BLE001 - a missing bar is a refusal
        return f"run window not covered by the data: {error}"
    for i in range(first + 1, last + 1):
        if bars[i].open_time != bars[i - 1].open_time + series.interval:
            after = bars[i - 1].open_time.isoformat()
            return f"run window crosses a data gap after {after}"
    begin = first
    while (
        begin > 0
        and bars[begin - 1].open_time + series.interval == bars[begin].open_time
    ):
        begin -= 1
    stop = last
    while (
        stop + 1 < len(bars)
        and bars[stop].open_time + series.interval == bars[stop + 1].open_time
    ):
        stop += 1
    return BarSeries(symbol=series.symbol, bars=bars[begin : stop + 1])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


FROZEN_MANIFEST_SHA256: Final = (
    "962bdb5096ae191556933cdde940d34f1548261f2ee9a7be65b523208b26912d"
)
"""`FROZEN_HASHES.json` as frozen, pinned here so that editing a frozen file
and rewriting its hashes to match still needs a reviewed code change (F24-2)."""


def frozen_hash_problems(root: Path) -> list[str]:
    """Compare the frozen files the loop depends on with `FROZEN_HASHES.json`
    and their sidecars (deployment draft section 4 item 1). The manifest
    itself must match `FROZEN_MANIFEST_SHA256`."""
    problems: list[str] = []
    try:
        manifest = root / "FROZEN_HASHES.json"
        if _sha256(manifest) != FROZEN_MANIFEST_SHA256:
            problems.append("FROZEN_HASHES.json: does not match the pinned hash")
        frozen = json.loads(manifest.read_text("utf-8"))
        checks = {
            "protocol_file_sha256": root / "protocols" / "protocol_v1.yaml",
            "cost_model_sha256": root / "specs" / "COST_MODEL_v1.md",
            "benchmark_set_sha256": root / "specs" / "CANONICAL_BENCHMARKS_v1.md",
        }
        for key, path in checks.items():
            actual = _sha256(path)
            sidecar = (
                (path.parent / (path.name + ".sha256")).read_text("utf-8").split()[0]
            )
            if actual != frozen[key] or actual != sidecar:
                problems.append(f"{path.name}: {actual} does not match the frozen hash")
        constitution = root / "docs" / "RESEARCH_CONSTITUTION.md"
        expected = frozen["constitution_content_hash"]
        text = constitution.read_bytes().replace(expected.encode(), b"")
        if hashlib.sha256(text).hexdigest() != expected:
            problems.append("RESEARCH_CONSTITUTION.md: content hash does not match")
    except (OSError, KeyError, ValueError, IndexError) as error:
        problems.append(f"frozen hashes unreadable: {error}")
    return problems


@dataclass(frozen=True, slots=True)
class RunReport:
    """Section 23: what the run did, stated plainly. It is a paper run on
    exploration data against a simulator; it makes no statistical claim."""

    run_id: str
    refused: tuple[str, ...]
    protocol_hash: str
    cost_model_hash: str
    data_manifest_hash: str
    predictor: str
    hours: int
    scheduled_decisions: int
    authorizations: int
    orders_sent: int
    governor_refusals: Mapping[str, int]
    health_breach_hours: int
    final_mode: str
    final_balances: Mapping[str, str]
    events: int
    note: str = (
        "Bar count is not sample size. Paper run on the exploration partition "
        "against the simulator; no edge, Sharpe, or promotion claim is made."
    )

    def as_mapping(self) -> dict[str, object]:
        return {
            "authorizations": self.authorizations,
            "cost_model_hash": self.cost_model_hash,
            "data_manifest_hash": self.data_manifest_hash,
            "events": self.events,
            "final_balances": dict(self.final_balances),
            "final_mode": self.final_mode,
            "governor_refusals": dict(self.governor_refusals),
            "health_breach_hours": self.health_breach_hours,
            "hours": self.hours,
            "note": self.note,
            "orders_sent": self.orders_sent,
            "predictor": self.predictor,
            "protocol_hash": self.protocol_hash,
            "refused": list(self.refused),
            "run_id": self.run_id,
            "scheduled_decisions": self.scheduled_decisions,
        }

    def digest(self) -> str:
        text = json.dumps(self.as_mapping(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


class _Clock:
    """The simulated clock: the bar clock, advanced by the executor's sleeps."""

    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now

    def sleep(self, duration: timedelta) -> None:
        self.now += duration


@dataclass
class _Counts:
    scheduled: int = 0
    authorizations: int = 0
    orders: int = 0
    health: int = 0
    refusals: dict[str, int] = field(default_factory=dict)


class _CountingSink:
    """Counts what the router delivers, for the report."""

    min_severity = Severity.INFO

    def __init__(self) -> None:
        self.count = 0

    def write(self, event: Event) -> None:
        self.count += 1


def run_paper(
    config: PaperConfig,
    series: BarSeries,
    *,
    data_manifest_hash: str,
    sinks: Sequence[Sink],
    incidents: IncidentLog,
    operations_log: Path | None,
    environ: Mapping[str, str],
    repository_root: Path,
    scenario: Scenario | None = None,
    local_record: LocalRecord | None = None,
    commands: Mapping[datetime, Trigger] | None = None,
    observe: Callable[[datetime], Observation] = bar_clock_observation,
) -> RunReport:
    """Run the loop over every hourly decision in `[start, end)`.

    `local_record` is what the system recorded before this start (default: the
    starting balances, nothing outstanding); startup reconciliation checks it
    against the venue. `commands` are owner commands (HALT or FLATTEN) applied
    at the start of the given hour, for drills (Task 25). `observe` gives the
    health-check readings for an hour (default: the bar clock, which never
    breaches); a breach blocks every order that hour, and at start it is a
    REFUSE_START.
    """
    owner = dict(commands or {})
    if any(
        t not in (Trigger.OWNER_HALT, Trigger.OWNER_FLATTEN) for t in owner.values()
    ):
        raise ConfigError("only OWNER_HALT and OWNER_FLATTEN can be commanded")
    frozen = json.loads((repository_root / "FROZEN_HASHES.json").read_text("utf-8"))
    counts = _Counts()
    counter = _CountingSink()
    refused: list[str] = []

    def report(mode: str, balances: Mapping[str, Decimal]) -> RunReport:
        return RunReport(
            run_id=config.run_id,
            refused=tuple(refused),
            protocol_hash=frozen["protocol_file_sha256"],
            cost_model_hash=frozen["cost_model_sha256"],
            data_manifest_hash=data_manifest_hash,
            predictor=str(PREDICTOR_BENCHMARK),
            hours=int((config.end - config.start) / HOUR),
            scheduled_decisions=counts.scheduled,
            authorizations=counts.authorizations,
            orders_sent=counts.orders,
            governor_refusals=dict(sorted(counts.refusals.items())),
            health_breach_hours=counts.health,
            final_mode=mode,
            final_balances={k: str(v) for k, v in sorted(balances.items())},
            events=counter.count,
        )

    # Alerting exists before anything else can happen (section 19).
    try:
        router = AlertRouter([*sinks, counter]) if sinks else AlertRouter([])
    except AlertConfigError as error:
        refused.append(f"no alert sink: {error}")
        return report("REFUSED", config.starting_balances)

    def refuse(reason: str) -> None:
        refused.append(reason)
        try:
            router.emit(
                Event(
                    EventKind.STARTUP,
                    Severity.CRITICAL,
                    config.start,
                    {"decision": "REFUSE_START", "reason": reason},
                )
            )
        except LedgerError as error:
            # A damaged log cannot take the record; the refusal still stands
            # and the report says it went unlogged there.
            refused.append(f"refusal not written to a damaged log: {error}")

    for problem in frozen_hash_problems(repository_root):
        refuse(f"hash mismatch: {problem}")
    if operations_log is not None and not verify_ledger(operations_log).intact:
        refuse("operations log fails its hash-chain check")
    try:
        refuse_credentials(environ)
    except DownloadError as error:
        refuse(f"credential present: {error}")
    marker = refuse_marker_path(incidents)
    if marker.exists():
        refuse(f"an earlier run stopped on an error; see {marker.name}")
    window = contiguous_window(series, config.start, config.end)
    if isinstance(window, str):
        refuse(window)
        return report("REFUSED", config.starting_balances)
    series = window
    exchange = SimulatedExchange(
        {config.symbol: series},
        {config.symbol: config.filters},
        dict(config.starting_balances),
        scenario=scenario,
    )
    local = local_record or LocalRecord(config.starting_balances)
    for breach in health_breaches(config.health, config.start, observe(config.start)):
        refuse(f"health check at start: {breach.kind} {dict(breach.fields)}")
    if not refused:
        decision = startup_check(
            exchange, local, config.tolerance, incidents, config.start
        )
        for reason in decision.reasons:
            refuse(reason)
    if refused:
        return report("REFUSED", config.starting_balances)
    router.emit(
        Event(
            EventKind.STARTUP,
            Severity.INFO,
            config.start,
            {"decision": "START", "run_id": config.run_id, "symbol": config.symbol},
        )
    )

    controller = SafetyController(router, incidents, config.start, mode=Mode.RUNNING)
    issued = iter(range(1 << 62))
    governor = Governor(
        config.governor, nonce_source=lambda: nonce_for(config.run_id, next(issued))
    )
    last_increase: datetime | None = None
    base = config.symbol.removesuffix(_QUOTE)
    peak = Decimal(0)
    stop_armed = True  # L-03 fires once per fall below the line
    zero_fills = 0

    try:
        moment = config.start
        while moment < config.end:
            decision_time, moment = moment, moment + HOUR
            if decision_time in owner:
                try:
                    controller.trigger(
                        owner[decision_time], decision_time, "owner command"
                    )
                except SafetyError as error:
                    router.emit(
                        Event(
                            EventKind.STATE_TRANSITION,
                            Severity.WARNING,
                            decision_time,
                            {
                                "command": str(owner[decision_time]),
                                "refused": str(error),
                            },
                        )
                    )
            breaches = health_breaches(
                config.health, decision_time, observe(decision_time)
            )
            if breaches:
                # Something looks broken: nothing is placed this hour, not even a
                # FLATTEN step, because prices or clocks cannot be trusted.
                counts.health += 1
                for breach in breaches:
                    router.emit(breach)
                continue
            try:
                mark = Decimal(repr(series.bar_at(decision_time - HOUR).close))
            except Exception:  # noqa: BLE001 - no bar for this hour: nothing to decide
                continue
            # L-03 (adopted): 20% below peak equity sells everything (setting S-4).
            held = local.balances.get(base, Decimal(0))
            equity = held * mark + local.balances.get(_QUOTE, Decimal(0))
            peak = max(peak, equity)
            breached = equity < peak * (1 - config.loss_stop_fraction)
            if not breached:
                stop_armed = True
            # Every breach alerts and opens an incident (deployment draft
            # section 5). It sells only from RUNNING: in HALT the owner's HALT
            # wins (OWNER_ANSWERS_2026-09-28.md, F24-1, F24R-1), and an owner
            # FLATTEN simply goes on. FREEZE is left alone until reconciled.
            if (
                breached
                and stop_armed
                and held >= config.filters.min_qty
                and controller.mode is not Mode.FREEZE
            ):
                keep = 1 - config.loss_stop_fraction
                detail = f"equity {equity:.2f} below {keep} x peak {peak:.2f}"
                controller.trigger(Trigger.LOSS_STOP, decision_time, detail)
                stop_armed = False
            if controller.mode is Mode.FLATTEN:
                flat = controller.tick(
                    exchange,
                    config.symbol,
                    config.filters,
                    config.flatten,
                    mark,
                    decision_time,
                    decision_time,
                )
                if flat is not None:
                    counts.orders += 1
                    # Every FLATTEN sell is in the audit log with the holding
                    # it was sized from (T25-01, A25-2).
                    router.emit(
                        Event(
                            EventKind.ORDER,
                            Severity.INFO,
                            decision_time,
                            {
                                "client_order_id": flat.client_order_id,
                                "executed_qty": str(flat.executed_qty),
                                "held_before": str(
                                    local.balances.get(base, Decimal(0))
                                ),
                                "orig_qty": str(flat.orig_qty),
                                "side": str(flat.side),
                                "state": "FLATTEN",
                            },
                        )
                    )
                    zero_fills = _zero_fill_alert(
                        router, zero_fills, flat, decision_time
                    )
                    local = _reconcile_flatten(
                        exchange, local, config, controller, decision_time
                    )
                continue
            if not controller.may_trade():
                continue
            proposal = baseline_proposal(series, decision_time)
            if isinstance(proposal, str):
                counts.refusals["NO_PROPOSAL"] = (
                    counts.refusals.get("NO_PROPOSAL", 0) + 1
                )
                continue
            if proposal.decision_time.hour == 0:
                counts.scheduled += 1
            state = ActualState(
                symbol=config.symbol,
                base_quantity=local.balances.get(base, Decimal(0)),
                quote_balance=local.balances.get(_QUOTE, Decimal(0)),
                mark_price=mark,
                as_of=decision_time,
                last_risk_increase_time=last_increase,
            )
            authorization = governor.decide(proposal, state, decision_time)
            if isinstance(authorization, Refusal):
                code = str(authorization.code)
                counts.refusals[code] = counts.refusals.get(code, 0) + 1
                continue
            counts.authorizations += 1
            clock = _Clock(decision_time)
            executor = Executor(
                governor,
                exchange,
                config.filters,
                config.executor,
                clock=clock,
                sleep=clock.sleep,
            )
            result = executor.execute(authorization, proposal, state)
            router.emit(
                Event(
                    EventKind.ORDER,
                    Severity.CRITICAL
                    if result.state is State.FREEZE
                    else Severity.INFO,
                    clock.now,
                    {
                        "client_order_id": result.client_order_id,
                        "executed_qty": None
                        if result.order is None
                        else str(result.order.executed_qty),
                        "side": str(authorization.side),
                        "state": str(result.state),
                    },
                )
            )
            if result.order is not None:
                zero_fills = _zero_fill_alert(
                    router, zero_fills, result.order, clock.now
                )
            if not result.reconciliation_required:
                continue
            counts.orders += 1
            # The order stays in the record until a passed reconciliation settles
            # it, so a later recovery must resolve it (T23-09).
            local = LocalRecord(
                local.balances, {**local.orders, result.client_order_id: result.order}
            )
            if result.state is State.FREEZE:
                controller.trigger(
                    Trigger.AMBIGUOUS_ORDER,
                    clock.now,
                    f"{result.client_order_id} unknown",
                )
                continue
            check = reconcile(exchange, local, config.tolerance, clock.now)
            if not check.passed:
                controller.trigger(
                    Trigger.RECONCILIATION_FAILED,
                    clock.now,
                    "; ".join(check.differences),
                )
                continue
            settle(check, governor, [authorization])
            filled = result.order is not None and result.order.executed_qty > 0
            if filled and authorization.side is Side.BUY:
                last_increase = proposal.decision_time
            local = check.next_record()

    except BaseException as error:
        # T23-04: an audit write (or anything else) failed mid-run. The mode
        # may not be on record, so no later start is safe until the owner
        # has looked: leave a marker that refuses every start.
        _write_refuse_marker(incidents, config.run_id, error)
        raise
    balances = exchange.balances()
    router.emit(
        Event(
            EventKind.SHUTDOWN,
            Severity.INFO,
            config.end,
            {"mode": str(controller.mode), "run_id": config.run_id},
        )
    )
    return report(str(controller.mode), balances)


ZERO_FILL_ALERT_AFTER: Final = 3
"""Consecutive IOC orders with nothing filled before a CRITICAL alert
(T23-08). Owner-set, alert only (T24-Q1, OWNER_ANSWERS_2026-09-28.md)."""


def _zero_fill_alert(
    router: AlertRouter, streak: int, order: Order, at: datetime
) -> int:
    """The new zero-fill streak; alerts every `ZERO_FILL_ALERT_AFTER`."""
    streak = streak + 1 if order.executed_qty == 0 else 0
    if streak and streak % ZERO_FILL_ALERT_AFTER == 0:
        router.emit(
            Event(
                EventKind.ORDER,
                Severity.CRITICAL,
                at,
                {"client_order_id": order.client_order_id, "zero_fill_streak": streak},
            )
        )
    return streak


def refuse_marker_path(incidents: IncidentLog) -> Path:
    """The file whose presence refuses every start (T23-04). Only the owner
    removes it, after reviewing the error it records."""
    return incidents.path.with_name(incidents.path.name + ".refuse_start")


def _write_refuse_marker(
    incidents: IncidentLog, run_id: str, error: BaseException
) -> None:
    text = f"run {run_id}: {type(error).__name__}: {error}\n"
    try:
        with refuse_marker_path(incidents).open("a", encoding="utf-8") as handle:
            handle.write(text)
    except OSError:
        pass  # the original error is re-raised either way


def _reconcile_flatten(
    exchange: SimulatedExchange,
    local: LocalRecord,
    config: PaperConfig,
    controller: SafetyController,
    at: datetime,
) -> LocalRecord:
    """Reconcile the FLATTEN orders the controller has sent; FREEZE on
    failure. Only a passed check settles them and advances the baseline."""
    record = LocalRecord(local.balances, {**local.orders, **controller.sent})
    check = reconcile(exchange, record, config.tolerance, at)
    if not check.passed:
        controller.trigger(
            Trigger.RECONCILIATION_FAILED, at, "; ".join(check.differences)
        )
        return record
    controller.settle_flatten(check)
    return check.next_record()
