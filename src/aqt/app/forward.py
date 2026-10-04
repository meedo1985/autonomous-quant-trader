"""Forward paper mode (roadmap 2, Task 29; owner answer
`review/roadmap/OWNER_ANSWER_QC_2026-10-04.md`: baseline only).

The Task 24 loop runs on the live bar store (Task 26) and the wall clock,
with fills simulated and the account's state in its journal (Task 27).
Nothing here trades real money or reads a credential.

One step processes every decision hour whose fill bar has closed: an hour
`h` fills at the open of bar `h`, which the store holds only once that bar
has closed, at `h + 1h`. So the window is `[first hour after the last save,
next bar the store expects)`, and the same bars give the same decisions as a
replay of that window. An hour that comes due more than one hour before the
step, because the process was down, is reported as a `LOOP_LAG` breach
naming the missed hours, never skipped in silence; it is then run exactly
as a replay would run it.

The simulated venue is rebuilt from the journal for every step: the
reconciled balances plus every order since, which the venue holds again.
An order with an unknown outcome refuses the step; the owner must resolve
it.

`L-02` (`review/pre-deployment/LOSS_BOUND_DEFAULTS.md` section 3) counts
effective decisions of forward paper on daily returns of the account's
equity, valued at each 00:00 UTC from the journal's balances and that hour's
close, with the Task 12 Newey-West estimator; the report names the method
used, `NEWEY_WEST` or the `HORIZON_FALLBACK`.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from aqt.app.paper_loop import Observation, PaperConfig, RunReport, run_paper
from aqt.app.state import AccountDir, AccountState, StateJournal
from aqt.core.ledger import read_entries
from aqt.data.bars import BarSeries
from aqt.execution.reconcile import LocalRecord, expected_balances
from aqt.execution.simulator import SimulatedExchange, SymbolFilters
from aqt.metrics.statistics import effective_sample_size
from aqt.monitoring.alerts import AlertRouter, Sink
from aqt.monitoring.events import Event, EventKind, Severity
from aqt.monitoring.telegram import ChannelTests

__all__ = [
    "DECISION_HORIZON_HOURS",
    "EffectiveDecisions",
    "ForwardError",
    "daily_equity_returns",
    "effective_decisions",
    "l02_count",
    "missed_hours_event",
    "observation",
    "pending_window",
    "resumed_venue",
    "run_step",
    "snapshots",
]

HOUR = timedelta(hours=1)
DAY = timedelta(days=1)
DECISION_HORIZON_HOURS = 24
"""The baseline decides at 00:00 UTC: one decision per day (N-1 reading)."""


class ForwardError(RuntimeError):
    """A forward step that cannot run safely."""


def _floor_hour(moment: datetime) -> datetime:
    return moment.replace(minute=0, second=0, microsecond=0)


def pending_window(
    journal: StateJournal, series: BarSeries, first_start: datetime
) -> tuple[datetime, datetime] | None:
    """The decision hours `[start, end)` ready to run, or `None`.

    `start` is `first_start` for a new account, else the hour after the last
    save; `end` follows the last closed bar, so the last hour's fill bar has
    closed."""
    loaded = journal.load_saved()
    start = first_start if loaded is None else _floor_hour(loaded[1]) + HOUR
    if not series.bars:
        return None
    end = series.bars[-1].open_time + series.interval
    if end <= start:
        return None
    return start, end


def missed_hours_event(start: datetime, end: datetime, now: datetime) -> Event | None:
    """A `LOOP_LAG` breach when hours before the newest one are run late:
    each hour is due when its fill bar closes, and only the newest may be
    new. `None` when nothing was missed."""
    missed = int((end - start) / HOUR) - 1
    if missed <= 0:
        return None
    return Event(
        EventKind.LOOP_LAG,
        Severity.CRITICAL,
        now,
        {
            "missed_hours": missed,
            "first_missed": start.isoformat(),
            "last_missed": (end - 2 * HOUR).isoformat(),
            "note": "run late, as a replay would run them",
        },
    )


def observation(
    end: datetime, now: datetime, reference_now: datetime
) -> Callable[[datetime], Observation]:
    """Health readings for a step: the newest bar closed at `end`, which is
    also when the step was due."""
    seen = Observation(
        latest_bar_close=end,
        local_now=now,
        reference_now=reference_now,
        started=now,
        scheduled=end,
    )
    return lambda _: seen


def _local(state: AccountState) -> LocalRecord:
    return LocalRecord(state.record.balances, {**state.record.orders, **state.sent})


def resumed_venue(
    journal: StateJournal,
    symbol: str,
    series: BarSeries,
    filters: SymbolFilters,
    starting_balances: Mapping[str, Decimal],
) -> SimulatedExchange:
    """The simulated venue the journal describes (a new account: the
    starting balances)."""
    state = journal.load()
    if state is None:
        return SimulatedExchange({symbol: series}, {symbol: filters}, starting_balances)
    local = _local(state)
    if any(order is None for order in local.orders.values()):
        raise ForwardError(
            "an order with an unknown outcome is recorded; resolve it before "
            "forward paper continues"
        )
    orders = {cid: order for cid, order in local.orders.items() if order is not None}
    return SimulatedExchange(
        {symbol: series},
        {symbol: filters},
        expected_balances(local),
        orders=orders,
    )


def snapshots(journal: StateJournal) -> list[tuple[datetime, Mapping[str, Decimal]]]:
    """Every saved snapshot's time and the balances it implies."""
    out: list[tuple[datetime, Mapping[str, Decimal]]] = []
    for entry in read_entries(journal.path):
        state = AccountState.from_mapping(entry.payload)
        at = datetime.fromisoformat(entry.recorded_at_utc.replace("Z", "+00:00"))
        out.append((at, expected_balances(_local(state))))
    return out


def daily_equity_returns(
    saved: Sequence[tuple[datetime, Mapping[str, Decimal]]],
    closes: Mapping[datetime, Decimal],
    base: str,
    quote: str = "USDT",
) -> list[float]:
    """Simple returns of equity between consecutive 00:00 UTC valuations.

    At each midnight after the first snapshot, the balances are those of the
    last snapshot saved at or before it, valued at the close of the bar that
    closes then (`closes` is keyed by close time). Valuation stops at the
    first midnight with no close: a gap is never bridged."""
    if not saved:
        return []
    ordered = sorted(saved, key=lambda pair: pair[0])
    midnight = _floor_hour(ordered[0][0]).replace(hour=0) + DAY
    values: list[Decimal] = []
    i = 0
    while midnight in closes:
        while i + 1 < len(ordered) and ordered[i + 1][0] <= midnight:
            i += 1
        balances = ordered[i][1]
        values.append(
            balances.get(quote, Decimal(0))
            + balances.get(base, Decimal(0)) * closes[midnight]
        )
        midnight += DAY
    return [float(b / a - 1) for a, b in zip(values, values[1:], strict=False)]


@dataclass(frozen=True, slots=True)
class EffectiveDecisions:
    """The `L-02` count, with the method that produced it."""

    raw_decisions: int
    value: float | None
    method: str | None
    reason: str | None

    def as_mapping(self) -> dict[str, object]:
        return {
            "raw_decisions": self.raw_decisions,
            "effective_decisions": self.value,
            "method": self.method,
            "reason": self.reason,
            "target": 240,
        }


def effective_decisions(returns: Sequence[float]) -> EffectiveDecisions:
    """Newey-West effective decisions of daily returns (Task 12 estimator)."""
    result = effective_sample_size(returns, horizon_hours=DECISION_HORIZON_HOURS)
    return EffectiveDecisions(len(returns), result.value, result.method, result.reason)


def run_step(
    config: PaperConfig,
    series: BarSeries,
    account: AccountDir,
    *,
    now: datetime,
    reference_now: datetime,
    sinks: Sequence[Sink],
    data_manifest_hash: str,
    environ: Mapping[str, str],
    repository_root: Path,
    channel: ChannelTests | None = None,
    deployment: Path | None = None,
) -> RunReport | None:
    """Run every pending decision hour of `series` for `account`; `None`
    when no hour is ready. `config.start` is the account's first decision
    hour; its `end` is not used. Each step gets its own run id, so order ids
    never repeat across steps."""
    window = pending_window(account.journal, series, config.start)
    if window is None:
        return None
    start, end = window
    router = AlertRouter(list(sinks))
    late = missed_hours_event(start, end, now)
    if late is not None:
        router.emit(late)
    try:
        venue = resumed_venue(
            account.journal,
            config.symbol,
            series,
            config.filters,
            config.starting_balances,
        )
    except ForwardError as error:
        refusal = {"decision": "REFUSE_START", "reason": str(error)}
        router.emit(Event(EventKind.STARTUP, Severity.CRITICAL, now, refusal))
        raise
    return run_paper(
        replace(
            config, run_id=f"{config.run_id}-{start:%Y%m%dT%H%MZ}", start=start, end=end
        ),
        series,
        data_manifest_hash=data_manifest_hash,
        sinks=sinks,
        incidents=account.incident_log(),
        operations_log=account.operations_path,
        environ=environ,
        repository_root=repository_root,
        observe=observation(end, now, reference_now),
        journal=account.journal,
        venue=venue,
        channel=channel,
        deployment=deployment,
    )


def l02_count(journal: StateJournal, series: BarSeries) -> EffectiveDecisions:
    """`L-02` effective decisions so far for the account in `journal`."""
    closes = {
        bar.open_time + bar.interval: Decimal(str(bar.close)) for bar in series.bars
    }
    base = series.symbol.removesuffix("USDT")
    return effective_decisions(daily_equity_returns(snapshots(journal), closes, base))
