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
inside one unbroken run of bars; the startup reconciliation fails; an
incident is open; or, with the Telegram channel (Task 28), its weekly test
is unacknowledged or overdue. A non-simulator adapter is
refused when the configuration is read. Every refusal is logged.

With a state journal (Task 27, `aqt.app.state`) a run resumes the account
where its last run left it: the saved mode (moved on by any alarm the
incident log recorded after the snapshot), the unsettled orders, the
loss-stop peak. A HALT, FLATTEN or FREEZE resumes as itself, never as
RUNNING. The state is saved after every hour, after an owner command, and
before any order is sent. A damaged or inconsistent journal, or a start not
after the last save, is a REFUSE_START.

The ways back (Task 27 part b2): on the owner's FREEZE_EXIT command the
loop reconciles, and a passed reconciliation leads to HALT (section 22);
nothing leaves FREEZE by itself. HALT ends only on
the owner's section 14 override (`OwnerOverride`, reconciled by the loop at
that hour); ending it resets the loss-stop peak to the equity then (owner
answers Q27-1, Q27-2). Neither trades in the hour it happens. No decision
is taken before a reconciliation that waited has ended (A2324R-4).

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
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Final

from aqt.allocation.predictor import PREDICTOR_BENCHMARK, baseline_proposal
from aqt.app.state import AccountState, StateError, StateJournal
from aqt.backtest.costs import Side as TradeSide
from aqt.core.ledger import LedgerError, read_entries, verify_ledger
from aqt.data.bars import BarSeries, require_utc
from aqt.data.binance_public import DownloadError, refuse_credentials
from aqt.execution.machine import Executor, State
from aqt.execution.orders import ExecutorConfig, client_order_id_for
from aqt.execution.reconcile import (
    AbsenceCheck,
    LocalRecord,
    ReconciliationReport,
    reconcile,
    settle,
)
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
    startup_check,
)
from aqt.execution.simulator import Order, Scenario, SimulatedExchange, SymbolFilters
from aqt.governor.authorization import (
    ActualState,
    Authorization,
    GovernorConfig,
    Refusal,
    Side,
)
from aqt.governor.machine import Governor
from aqt.monitoring.alerts import AlertConfigError, AlertRouter, Sink
from aqt.monitoring.events import Event, EventKind, Severity
from aqt.monitoring.health import check_clock_skew, check_loop_lag, check_stale_data
from aqt.monitoring.telegram import ChannelError, ChannelTests

__all__ = [
    "ConfigError",
    "HealthLimits",
    "Observation",
    "OwnerOverride",
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


@dataclass(frozen=True, slots=True)
class OwnerOverride:
    """The owner's part of a section 14 HALT override, for one hour. The loop
    adds the reconciliation it takes at that hour; `SafetyController.
    override_halt` refuses anything missing. `incident_ids` must name every
    open incident."""

    incident_ids: tuple[str, ...]
    written_record: str
    cause: str
    owner_action: OwnerAction
    timestamp: datetime


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
                # Optional; never silently dropped (A2324-3).
                max_notional=(
                    _decimal(fil["max_notional"], "max_notional")
                    if "max_notional" in fil
                    else None
                ),
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
    except (
        OSError,
        KeyError,
        ValueError,
        IndexError,
        TypeError,
        AttributeError,
    ) as error:
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
    journal: StateJournal | None = None,
    venue: SimulatedExchange | None = None,
    overrides: Mapping[datetime, OwnerOverride] | None = None,
    channel: ChannelTests | None = None,
) -> RunReport:
    """Run the loop over every hourly decision in `[start, end)`.

    `local_record` is what the system recorded before this start (default: the
    starting balances, nothing outstanding); startup reconciliation checks it
    against the venue. `commands` are owner commands (HALT or FLATTEN) applied
    at the start of the given hour, for drills (Task 25). `observe` gives the
    health-check readings for an hour (default: the bar clock, which never
    breaches); a breach blocks every order that hour, and at start it is a
    REFUSE_START.

    `journal` holds the account's saved state (Task 27); `incidents` must be
    the same account's incident log. `venue` is the exchange to trade
    against (default: a new simulator holding the starting balances); a
    resumed account must be given the venue its state describes, or the
    startup reconciliation refuses. `overrides` are the owner's HALT
    overrides, applied at the given hour.

    `channel` is the Telegram channel's weekly test (Task 28), given when
    the run uses the channel: its sink must be among `sinks`. An unacknowledged
    or overdue test refuses the start. During the run, at most once per
    wall-clock hour, a due test is sent and an overdue one raises a CRITICAL
    alert; the mode is unchanged (owner answer Q28-2).
    """
    if journal is not None and local_record is not None:
        raise ConfigError("a resumed account's record comes from its journal")
    if venue is not None and scenario is not None:
        raise ConfigError("a scenario configures a new simulator, not a given venue")
    owner = dict(commands or {})
    commandable = (Trigger.OWNER_HALT, Trigger.OWNER_FLATTEN, Trigger.FREEZE_EXIT)
    if any(t not in commandable for t in owner.values()):
        raise ConfigError(
            "only OWNER_HALT, OWNER_FLATTEN and FREEZE_EXIT can be commanded"
        )
    try:
        frozen = json.loads((repository_root / "FROZEN_HASHES.json").read_text("utf-8"))
    except (OSError, ValueError):
        # `frozen_hash_problems` refuses the start, logged (A2324-4).
        frozen = {}
    if not isinstance(frozen, dict):
        frozen = {}  # valid JSON but not an object: refused below (F35-2)
    counts = _Counts()
    counter = _CountingSink()
    refused: list[str] = []

    def report(mode: str, balances: Mapping[str, Decimal]) -> RunReport:
        return RunReport(
            run_id=config.run_id,
            refused=tuple(refused),
            protocol_hash=str(frozen.get("protocol_file_sha256", "unreadable")),
            cost_model_hash=str(frozen.get("cost_model_sha256", "unreadable")),
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

    def refuse(reason: str, at: datetime | None = None) -> None:
        refused.append(reason)
        try:
            router.emit(
                Event(
                    EventKind.STARTUP,
                    Severity.CRITICAL,
                    config.start if at is None else at,
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
    if channel is not None and (untested := channel.problem()) is not None:
        refuse(untested)
    marker = refuse_marker_path(incidents)
    if marker.exists():
        refuse(f"an earlier run stopped on an error; see {marker.name}")
    resumed: AccountState | None = None
    saved_at = config.start
    mode, entered = Mode.RUNNING, config.start
    if journal is not None:
        try:
            loaded = journal.load_saved()
            if loaded is not None:
                resumed, saved_at = loaded
                if config.start <= saved_at:
                    refuse(f"start is not after the saved state ({saved_at})")
                place = _resume(resumed, incidents)
                if isinstance(place, str):
                    refuse(place)
                else:
                    mode, entered = place
        except (LedgerError, StateError, OSError) as error:
            refuse(f"saved state unreadable: {error}")
    history = series  # every bar given, for recovery across a data gap (A27-21)
    window = contiguous_window(series, config.start, config.end)
    if isinstance(window, str):
        refuse(window)
        return report("REFUSED", config.starting_balances)
    series = window
    if venue is not None:
        exchange = venue
    else:
        exchange = SimulatedExchange(
            {config.symbol: series},
            {config.symbol: config.filters},
            dict(config.starting_balances),
            scenario=scenario,
        )
    local = local_record or LocalRecord(config.starting_balances)
    if resumed is not None:
        # Unsettled FLATTEN orders are resolved by the startup reconciliation.
        record = resumed.record
        local = LocalRecord(record.balances, {**record.orders, **resumed.sent})
    for breach in health_breaches(config.health, config.start, observe(config.start)):
        refuse(f"health check at start: {breach.kind} {dict(breach.fields)}")
    if not refused:
        decision = startup_check(
            exchange,
            local,
            config.tolerance,
            incidents,
            config.start,
            _absence(config, _Clock(config.start)),
            resuming=mode,
        )
        for reason in decision.reasons:
            # Stamped when the check ended, after any waits (A2324R-5).
            refuse(reason, decision.report.at)
    if refused:
        return report("REFUSED", config.starting_balances)
    started: dict[str, str | int | bool | None] = {
        "decision": "START",
        "run_id": config.run_id,
        "symbol": config.symbol,
    }
    if resumed is not None:
        started["resumed_mode"] = str(mode)
    router.emit(Event(EventKind.STARTUP, Severity.INFO, decision.report.at, started))

    ready = decision.report.at  # after any section 21 waits (A2324R-2, F35-4)
    local = decision.report.next_record()
    controller = SafetyController(
        router, incidents, ready if resumed is None else entered, mode=mode
    )
    if mode in (Mode.HALT, Mode.FREEZE) and not incidents.open_incidents():
        # The section 14 way out needs an open incident to close: a crash can
        # fall between closing the incidents and saving RUNNING.
        incidents.open("STATE_RESUMED", f"resumed {mode}, no incident open", ready)

    def apply_owner(hour: datetime, at: datetime) -> None:
        """Apply the owner's command for `hour` at `at`; a refusal is logged.
        FREEZE_EXIT waits for the hour's reconciliation (`leave_freeze`)."""
        if owner[hour] is Trigger.FREEZE_EXIT:
            return
        try:
            controller.trigger(owner[hour], at, "owner command")
        except SafetyError as error:
            router.emit(
                Event(
                    EventKind.STATE_TRANSITION,
                    Severity.WARNING,
                    at,
                    {"command": str(owner[hour]), "refused": str(error)},
                )
            )

    ends = dict(overrides or {})

    def refuse_command(command: Trigger, at: datetime, reason: str) -> None:
        router.emit(
            Event(
                EventKind.STATE_TRANSITION,
                Severity.WARNING,
                at,
                {"command": str(command), "refused": reason},
            )
        )

    def skip_recovery(hour: datetime, at: datetime, reason: str) -> None:
        """Log the owner's HALT override or FREEZE_EXIT for `hour` that was
        not applied, so no command is lost silently."""
        if hour in ends:
            refuse_command(Trigger.HALT_OVERRIDE, at, reason)
        if owner.get(hour) is Trigger.FREEZE_EXIT:
            refuse_command(Trigger.FREEZE_EXIT, at, reason)

    issued = iter(range(1 << 62))
    # A resumed run's nonces differ from every earlier run's, since its start
    # is after all of them: no client order id is reused.
    seed = config.run_id if resumed is None else f"{config.run_id}|{ready.isoformat()}"
    governor = Governor(
        config.governor, nonce_source=lambda: nonce_for(seed, next(issued))
    )
    last_increase: datetime | None = None
    base = config.symbol.removesuffix(_QUOTE)
    peak = Decimal(0)
    stop_armed = True  # L-03 fires once per fall below the line
    valued: datetime | None = None
    """The last decision hour `peak` and the latch include, valued with
    reconciled holdings. An hour valued while orders are unresolved would
    use holdings the venue may contradict: it is left for the next passed
    reconciliation to value (A27-18)."""
    zero_fills = 0
    if resumed is not None:
        peak, stop_armed = resumed.peak, resumed.stop_armed
        last_increase, zero_fills = resumed.last_increase, resumed.zero_fills
        # Hours valued after the last save were lost with the process: run
        # them again as the loop would have, peak and latch (A27-3, A27-10),
        # from the hour after the last one the snapshot valued (A27-13), with
        # the holdings the startup check confirmed, which include any order
        # sent just before the crash (A27-9).
        peak, stop_armed, valued, missed = _replay(
            history,
            local.balances,
            base,
            (resumed.valued_through, saved_at, config.start),
            (peak, stop_armed),
            config.loss_stop_fraction,
            fires=controller.mode is not Mode.FREEZE,
        )
        # A buy that filled before the crash, found by the startup check,
        # is a risk increase all the same (A27-2).
        last_increase = _last_increase(decision.report, last_increase)
        # A firing the incident log holds after the snapshot happened before
        # the crash (A27-20); only the hours without one are missed. Matched
        # by decision hour, not counted: the bars given may not reach back
        # to the hour a logged firing was for (A27-24).
        logged = [
            str(entry.payload.get("detail", ""))
            for entry in read_entries(incidents.path)[resumed.incidents_seen :]
            if entry.record_type == IncidentLog.OPEN
            and entry.payload.get("kind") == str(Trigger.LOSS_STOP)
        ]
        for hour in missed:
            if any(_fired_for(hour) in detail for detail in logged):
                continue
            # A breach in an hour the process was down still alerts, opens
            # its incident and, from RUNNING, sells (S-4), now: one each, as
            # the running loop would have (A27-22).
            controller.trigger(
                Trigger.LOSS_STOP,
                ready,
                f"{_fired_for(hour)} missed while the process was down",
            )
            # The latch stays as the replay left it: a later missed hour
            # back above the line re-armed it (A27-14).
    unsettled: list[Authorization] = []
    """Authorizations whose orders a failed or unclear outcome left
    unreconciled; their reservations wait for a passed reconciliation."""
    busy_until = ready

    def save(at: datetime, record: LocalRecord | None = None) -> None:
        """Append the account's state to the journal, if there is one."""
        if journal is None:
            return
        seen = len(read_entries(incidents.path)) if incidents.path.exists() else 0
        sent = dict(controller.sent)
        journal.save(
            AccountState(
                mode=controller.mode,
                entered_at=controller.entered_at,
                record=local if record is None else record,
                sent=sent,
                attempts={k: controller.attempts[k] for k in sent},
                peak=peak,
                stop_armed=stop_armed,
                last_increase=last_increase,
                valued_through=valued,
                zero_fills=zero_fills,
                incidents_seen=seen,
            ),
            at,
        )

    def recover(hour: datetime) -> tuple[LocalRecord, ReconciliationReport]:
        """Reconcile everything outstanding at `hour`, as recovery needs."""
        nonlocal busy_until
        record = LocalRecord(local.balances, {**local.orders, **controller.sent})
        check = reconcile(
            exchange, record, config.tolerance, hour, _absence(config, _Clock(hour))
        )
        busy_until = max(busy_until, check.at)
        return record, check

    def recovered(check: ReconciliationReport) -> None:
        """Carry a recovery's passed reconciliation forward."""
        nonlocal local, unsettled
        nonlocal last_increase
        released = set(settle(check, governor, unsettled))
        unsettled = [a for a in unsettled if a.nonce not in released]
        last_increase = _last_increase(check, last_increase)
        local = check.next_record()

    def mark_at(hour: datetime) -> Decimal | None:
        """The close the decision at `hour` sees, if its bar exists."""
        try:
            return Decimal(repr(series.bar_at(hour - HOUR).close))
        except Exception:  # noqa: BLE001 - no bar for this hour
            return None

    def value(
        hour: datetime, mark: Decimal | None
    ) -> tuple[datetime, Decimal, bool] | None:
        """L-03 bookkeeping for `hour`, once, in every hour with a bar, as a
        restart replays it (A27-17): the hour, the equity and whether it is
        below the line. Nothing for an hour already valued (one a HALT override reset
        covers, A27-16) or while orders are unresolved (A27-18)."""
        nonlocal peak, stop_armed, valued
        if mark is None or (valued is not None and hour <= valued):
            return None
        if local.orders or controller.sent:
            return None
        held = local.balances
        equity = held.get(base, Decimal(0)) * mark + held.get(_QUOTE, Decimal(0))
        peak = max(peak, equity)
        valued = hour
        breached = equity < peak * (1 - config.loss_stop_fraction)
        if not breached:
            stop_armed = True
        return hour, equity, breached

    def fire(result: tuple[datetime, Decimal, bool] | None, at: datetime) -> None:
        """The L-03 stop for a valued hour. Every breach alerts and opens an
        incident (deployment draft section 5). It sells only from RUNNING:
        in HALT the owner's HALT wins (OWNER_ANSWERS_2026-09-28.md, F24-1,
        F24R-1), and an owner FLATTEN simply goes on. FREEZE is left alone
        until reconciled (T27-13). Even a holding too small to sell alerts
        (A2324-2)."""
        nonlocal stop_armed
        if result is None or not result[2] or not stop_armed:
            return
        if controller.mode is Mode.FREEZE:
            return
        keep = 1 - config.loss_stop_fraction
        detail = (
            f"{_fired_for(result[0])} equity {result[1]:.2f} below {keep}"
            f" x peak {peak:.2f}"
        )
        controller.trigger(Trigger.LOSS_STOP, at, detail)
        stop_armed = False

    def leave_freeze(hour: datetime) -> None:
        """FREEZE to HALT on a passed reconciliation (section 22). A failed
        one leaves FREEZE as it is; its incident is already open. The hours
        left unvalued while orders were unresolved are valued now, with the
        confirmed holdings, as a restart would (A27-18)."""
        nonlocal peak, stop_armed, valued
        _, check = recover(hour)
        try:
            controller.exit_freeze(check, check.at)
        except SafetyError as error:
            refuse_command(Trigger.FREEZE_EXIT, check.at, str(error))
            return
        recovered(check)
        peak, stop_armed, valued, _ = _replay(
            history,
            local.balances,
            base,
            (valued, hour, hour + HOUR),
            (peak, stop_armed),
            config.loss_stop_fraction,
            fires=False,
        )
        save(check.at)

    def end_halt(hour: datetime, mark: Decimal) -> bool:
        """The owner's section 14 override at `hour`. True when it was tried
        (a reconciliation ran), whether HALT ended or not; False when it was
        refused at once because the account is not in HALT."""
        nonlocal peak, stop_armed, valued
        if controller.mode is not Mode.HALT:
            refuse_command(
                Trigger.HALT_OVERRIDE, hour, f"not in HALT ({controller.mode})"
            )
            return False
        _, check = recover(hour)
        if not check.passed:
            # A mismatch found in HALT is a new safety event: FREEZE, as any
            # failed reconciliation does.
            refuse_command(Trigger.HALT_OVERRIDE, check.at, "reconciliation failed")
            controller.trigger(
                Trigger.RECONCILIATION_FAILED, check.at, "; ".join(check.differences)
            )
            save(check.at)
            return True
        wanted = ends[hour]
        override = HaltOverride(
            incident_ids=wanted.incident_ids,
            written_record=wanted.written_record,
            cause=wanted.cause,
            reconciliation=check,
            owner_action=wanted.owner_action,
            timestamp=wanted.timestamp,
        )
        try:
            controller.override_halt(override, check.at)
        except SafetyError as error:
            refuse_command(Trigger.HALT_OVERRIDE, check.at, str(error))
            return True
        recovered(check)
        # Q27-1, Q27-2: ending a HALT re-arms the loss stop from the equity
        # now, so it fires on the next 20% fall from here: at the last close
        # before the reconciliation ended, which may have waited (A27-1).
        closed = check.at.replace(minute=0, second=0, microsecond=0) - HOUR
        try:
            mark = Decimal(repr(series.bar_at(closed).close))
        except Exception:  # noqa: BLE001 - no newer bar: the hour's mark
            pass
        balances = local.balances
        peak = balances.get(base, Decimal(0)) * mark + balances.get(_QUOTE, Decimal(0))
        stop_armed = True
        # The reset is the valuation of the hour it took effect in: no hour
        # up to it is valued again, now or on a restart (A27-16).
        valued = max(hour, closed + HOUR)
        save(check.at)
        return True

    reminded: datetime | None = None

    def check_channel(at: datetime) -> None:
        """Q28-2: send a due test; alert while the test is overdue. At most
        once per wall-clock hour; never changes the mode, and nothing it
        meets stops the loop (A28-4), not even a bad clock, which is then
        reported every decision hour (A28-11). A clock set back starts a new
        hour at once (A28-6)."""
        nonlocal reminded
        if channel is None:
            return
        try:
            now = channel.now()
            if reminded is not None and reminded <= now < reminded + HOUR:
                return
            reminded = now
            if channel.due():
                channel.send_test()
            problem = channel.problem()
        except ChannelError as error:  # its text holds no secret
            problem = f"channel test: {error}"
        except Exception as error:  # noqa: BLE001 - reported, never raised
            problem = f"channel test failed: {type(error).__name__}"
        if problem is not None:
            router.emit(
                Event(
                    EventKind.ALERT_CHANNEL,
                    Severity.CRITICAL,
                    at,
                    {"channel": "telegram", "problem": problem},
                )
            )

    try:
        moment = config.start
        # A startup check that waited (section 21) ends after `start`: no
        # decision may be stamped before it (A2324R-2). An owner command for a
        # skipped hour still applies, as soon as the check ends (F35-1).
        while moment < ready:
            if moment in owner:
                apply_owner(moment, ready)
            skip_recovery(moment, ready, "the startup check was still running")
            fire(value(moment, mark_at(moment)), ready)  # valued all the same
            moment += HOUR
        save(ready)
        decision_time = ready
        # A FLATTEN sell is saved as sent before it is placed (Task 27).
        controller.before_send = lambda: save(decision_time)
        done: datetime | None = None
        while moment < config.end:
            if done is not None:
                # The hour just finished, never before work it waited for
                # (A27-1).
                save(max(done, busy_until))
            decision_time, moment = moment, moment + HOUR
            check_channel(decision_time)
            done = max(decision_time, busy_until)
            mark = mark_at(decision_time)
            if decision_time < busy_until:
                # A reconciliation that waited (section 21) ends after this
                # hour began: nothing is decided before it (A2324R-4). An owner
                # command still applies, as soon as it ends; the hour is still
                # valued for the loss stop, as a restart would (A27-17).
                if decision_time in owner:
                    apply_owner(decision_time, busy_until)
                skip_recovery(decision_time, busy_until, "a reconciliation was running")
                fire(value(decision_time, mark), busy_until)
                continue
            if decision_time in owner:
                apply_owner(decision_time, decision_time)
                save(decision_time)
            breaches = health_breaches(
                config.health, decision_time, observe(decision_time)
            )
            if breaches:
                # Something looks broken: nothing is placed this hour, not even a
                # FLATTEN step, because prices or clocks cannot be trusted.
                counts.health += 1
                for breach in breaches:
                    router.emit(breach)
                skip_recovery(decision_time, decision_time, "health check breach")
                # Valued all the same, as a restart would (A27-17); the stop
                # may alert, but nothing is placed this hour.
                fire(value(decision_time, mark), decision_time)
                continue
            if mark is None:  # no bar for this hour: nothing to decide
                skip_recovery(decision_time, decision_time, "no bar for the hour")
                continue
            # L-03 (adopted): 20% below peak equity sells everything (setting S-4).
            valuation = value(decision_time, mark)
            # FREEZE is left alone until the owner asks for a reconciliation.
            # Outside FREEZE the command is refused and the hour goes on.
            if owner.get(decision_time) is Trigger.FREEZE_EXIT:
                if controller.mode is Mode.FREEZE:
                    leave_freeze(decision_time)
                    if decision_time in ends:
                        refuse_command(
                            Trigger.HALT_OVERRIDE, busy_until, "FREEZE_EXIT this hour"
                        )
                    continue
                refuse_command(
                    Trigger.FREEZE_EXIT,
                    decision_time,
                    f"not in FREEZE ({controller.mode})",
                )
            if decision_time in ends and end_halt(decision_time, mark):
                # The hour ends with its override attempt, ended or not:
                # nothing after it may be stamped before its reconciliation
                # ended (A27-8). A refused override authorizes nothing, so
                # the hour's breach is still recorded, when it ended (A27-20);
                # an accepted one reset the line (Q27-1, Q27-2).
                if controller.mode is not Mode.RUNNING:
                    fire(valuation, busy_until)
                continue
            fire(valuation, decision_time)
            if controller.mode is Mode.FLATTEN:
                # The venue balance `tick` sizes from, for the audit log.
                sized_from = exchange.balances().get(base, Decimal(0))
                pending = set(controller.sent)
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
                                "held_before": str(sized_from),
                                "orig_qty": str(flat.orig_qty),
                                "side": str(flat.side),
                                "state": "FLATTEN",
                            },
                        )
                    )
                    zero_fills = _zero_fill_alert(
                        router, zero_fills, flat, decision_time
                    )
                    local, finished = _reconcile_flatten(
                        exchange, local, config, controller, decision_time
                    )
                    busy_until = max(busy_until, finished)
                for lost in (
                    set(controller.sent)
                    - pending
                    - {flat.client_order_id if flat else ""}
                ):
                    # A sell whose outcome is unknown is sent all the same
                    # (A25R-4); the controller is in FREEZE.
                    counts.orders += 1
                    router.emit(
                        Event(
                            EventKind.ORDER,
                            Severity.CRITICAL,
                            decision_time,
                            {
                                "client_order_id": lost,
                                "held_before": str(sized_from),
                                **_attempt(controller, lost),
                                "side": "SELL",
                                "state": "FLATTEN_UNKNOWN",
                            },
                        )
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
            # Saved as sent before it is placed: after a crash in between, the
            # startup reconciliation must resolve it (Task 27).
            unsent = {client_order_id_for(authorization): None}
            save(decision_time, LocalRecord(local.balances, {**local.orders, **unsent}))
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
            busy_until = max(busy_until, clock.now)
            if result.state is State.FREEZE:
                unsettled.append(authorization)
                controller.trigger(
                    Trigger.AMBIGUOUS_ORDER,
                    clock.now,
                    f"{result.client_order_id} unknown",
                )
                continue
            check = reconcile(
                exchange, local, config.tolerance, clock.now, _absence(config, clock)
            )
            busy_until = max(busy_until, check.at)
            if not check.passed:
                unsettled.append(authorization)
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
        if done is not None:
            save(max(done, busy_until))

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
            max(config.end, busy_until),
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


def _resume(saved: AccountState, incidents: IncidentLog) -> tuple[Mode, datetime] | str:
    """The mode to resume and when it began: the saved mode, moved on by every
    alarm the incident log recorded after the snapshot (a crash can fall
    between an alarm and its save). A reason to refuse if they disagree."""
    entries = read_entries(incidents.path) if incidents.path.exists() else ()
    if len(entries) < saved.incidents_seen:
        return "the incident log is shorter than the saved state recorded"
    mode, at = saved.mode, saved.entered_at
    for entry in entries[saved.incidents_seen :]:
        if entry.record_type != IncidentLog.OPEN:
            continue
        kind = str(entry.payload.get("kind"))
        # HALT_OVERRIDE_FAILED is opened in HALT and leaves HALT (safety.py);
        # STATE_RESUMED is opened in HALT or FREEZE and leaves it (A27-7).
        target = Mode.HALT if kind == "HALT_OVERRIDE_FAILED" else None
        if kind == "STATE_RESUMED" and mode in (Mode.HALT, Mode.FREEZE):
            target = mode
        if kind in Trigger.__members__:
            target = MODE_TRANSITIONS.get((mode, Trigger(kind)))
        if target is None:
            return f"incident {kind} cannot follow the saved mode {mode}"
        stamp = datetime.strptime(entry.recorded_at_utc, "%Y-%m-%dT%H:%M:%SZ")
        mode, at = target, max(at, stamp.replace(tzinfo=UTC))
    return mode, at


def _replay(
    series: BarSeries,
    holdings: Mapping[str, Decimal],
    base: str,
    window: tuple[datetime | None, datetime, datetime],
    latch: tuple[Decimal, bool],
    fraction: Decimal,
    *,
    fires: bool,
) -> tuple[Decimal, bool, datetime | None, list[datetime]]:
    """The loop's loss-stop bookkeeping for every decision hour the snapshot
    has not valued, until the start, for the bars present: the peak, the
    latch, the last hour valued, and every hour the stop would have fired.
    `window` is the snapshot's `valued_through`, its save time and the
    start; with nothing valued yet the saved hour is the first.
    `holdings` are those the startup check confirmed. In FREEZE (`fires`
    false) the stop neither fires nor disarms, as in the loop."""
    valued, saved_at, start = window
    peak, armed = latch
    missed: list[datetime] = []
    if valued is None:
        hour = saved_at.replace(minute=0, second=0, microsecond=0)
    else:
        hour = valued + HOUR
    while hour < start:
        try:
            mark = Decimal(repr(series.bar_at(hour - HOUR).close))
        except Exception:  # noqa: BLE001 - no bar: that hour valued nothing
            hour += HOUR
            continue
        equity = holdings.get(base, Decimal(0)) * mark + holdings.get(
            _QUOTE, Decimal(0)
        )
        peak = max(peak, equity)
        valued = hour
        if equity >= peak * (1 - fraction):
            armed = True
        elif armed and fires:
            missed.append(hour)
            armed = False
        hour += HOUR
    return peak, armed, valued, missed


def _fired_for(hour: datetime) -> str:
    """The tag naming the decision hour a LOSS_STOP incident is for, so a
    restart can tell which replayed firings the log already holds (A27-24)."""
    return f"[decision hour {hour.isoformat()}]"


def _last_increase(
    report: ReconciliationReport, current: datetime | None
) -> datetime | None:
    """`current`, moved to the decision of any filled buy `report` resolved."""
    for order in report.resolved.values():
        if order is not None and order.side is TradeSide.BUY and order.executed_qty:
            if current is None or order.decision_time > current:
                current = order.decision_time
    return current


def _attempt(controller: SafetyController, client_order_id: str) -> dict[str, str]:
    """What the controller sent for `client_order_id`, if it recorded it."""
    attempt = controller.attempts.get(client_order_id)
    if attempt is None:
        return {}
    quantity, cap = attempt
    return {"orig_qty": str(quantity), "limit_price": str(cap)}


def _absence(config: PaperConfig, clock: _Clock) -> AbsenceCheck:
    """Section 21 absence confirmation with the executor's owner-set delay
    and answer count (T22-Q1), on the simulated clock (A2324-1)."""
    return AbsenceCheck(
        config.executor.not_found_delay,
        config.executor.absence_queries,
        clock.sleep,
        clock,
    )


def _reconcile_flatten(
    exchange: SimulatedExchange,
    local: LocalRecord,
    config: PaperConfig,
    controller: SafetyController,
    at: datetime,
) -> tuple[LocalRecord, datetime]:
    """Reconcile the FLATTEN orders the controller has sent; FREEZE on
    failure. Only a passed check settles them and advances the baseline.
    Also returns when the check ended, after any waits (A2324R-4)."""
    record = LocalRecord(local.balances, {**local.orders, **controller.sent})
    check = reconcile(
        exchange, record, config.tolerance, at, _absence(config, _Clock(at))
    )
    if not check.passed:
        controller.trigger(
            Trigger.RECONCILIATION_FAILED, check.at, "; ".join(check.differences)
        )
        return record, check.at
    controller.settle_flatten(check)
    return check.next_record(), check.at
