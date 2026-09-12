"""UTC bar semantics for timestamped OHLCV bars.

This is the single bar-semantics module required by
`docs/RESEARCH_CONSTITUTION.md` section 6 ("UTC only; one tested
bar-semantics module"). Candidates and canonical benchmarks share it.

Frozen sources encoded here:

* `protocols/protocol_v1.yaml` `scope.bar_interval` = `1h`.
* `specs/BACKTESTER_SPEC_v1.md` item 2: decision at close(t), baseline
  execution at open(t+1).
* `specs/COST_MODEL_v1.md` "Baseline execution": the decision timestamp is an
  eligible 1h bar close and the baseline fill price is the next 1h bar open.
* `specs/CANONICAL_BENCHMARKS_v1.md`: benchmarks use the same bar-semantics
  module as candidates.

Timestamp convention
--------------------
A `Bar` is labelled by `open_time`, the inclusive start of the half-open
interval `[open_time, open_time + interval)` that it covers. `close_time` is
the exclusive end of that interval and is therefore the decision timestamp of
the bar. Because the series is aligned to a fixed interval, `close_time` of
bar t equals `open_time` of bar t+1, so the baseline fill is the open of the
bar whose `open_time` is the decision timestamp itself.

All timestamps must be timezone-aware with a zero UTC offset. Naive
timestamps and non-zero offsets are rejected rather than assumed; accepted
timestamps are normalised to `datetime.UTC` so stored values are canonical.
Every `open_time` must also sit exactly on an interval boundary measured from
the Unix epoch.

Missing data
------------
Nothing is forward-filled, interpolated, or dropped, per the Constitution's
"no silent deletion/correction" rule. A `BarSeries` accepts a series with
holes but reports them exactly via `BarSeries.missing_open_times`. The
functions that claim complete bars, `contiguous_bar_series` and
`BarSeries.require_contiguous`, raise instead. `BarSeries.baseline_execution`
refuses to execute across a hole, because open(t+1) does not exist there.

Out of scope for this module: exposure mapping, the 00:00 UTC decision
schedule, the rebalance band, minimum-hold rules, cost application, and
execution-delay stress. Those belong to their own scheduled tasks.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Final

__all__ = [
    "BAR_INTERVAL",
    "BAR_INTERVAL_LABEL",
    "Bar",
    "BarSemanticsError",
    "BarSeries",
    "ExecutionPoint",
    "contiguous_bar_series",
    "require_aligned_utc",
    "require_utc",
]

BAR_INTERVAL: Final[timedelta] = timedelta(hours=1)
"""Frozen Cycle-1 bar interval (`protocol_v1.yaml` `scope.bar_interval`)."""

BAR_INTERVAL_LABEL: Final[str] = "1h"

_EPOCH: Final[datetime] = datetime(1970, 1, 1, tzinfo=UTC)
_ZERO: Final[timedelta] = timedelta(0)


class BarSemanticsError(ValueError):
    """Raised when input violates the frozen bar-semantics rules."""


def require_utc(value: datetime, *, field_name: str = "timestamp") -> datetime:
    """Return `value` normalised to `datetime.UTC`.

    Naive timestamps and non-zero UTC offsets are rejected; a local time is
    never silently reinterpreted as UTC.
    """
    offset = value.utcoffset()
    if offset is None:
        raise BarSemanticsError(f"{field_name} must be UTC-aware, got naive value")
    if offset != _ZERO:
        raise BarSemanticsError(
            f"{field_name} must have a zero UTC offset, got {offset}"
        )
    return value.astimezone(UTC)


def require_aligned_utc(
    value: datetime, interval: timedelta, *, field_name: str = "timestamp"
) -> datetime:
    """Return a UTC `value` that sits exactly on an `interval` boundary."""
    _require_positive_interval(interval)
    normalised = require_utc(value, field_name=field_name)
    if (normalised - _EPOCH) % interval != _ZERO:
        raise BarSemanticsError(
            f"{field_name} {normalised.isoformat()} is not aligned to a "
            f"{interval} boundary from the Unix epoch"
        )
    return normalised


def _require_positive_interval(interval: timedelta) -> None:
    if interval <= _ZERO:
        raise BarSemanticsError(f"interval must be positive, got {interval}")


def _require_price(value: float, name: str) -> None:
    if not math.isfinite(value) or value <= 0.0:
        raise BarSemanticsError(
            f"{name} must be a finite, strictly positive price, got {value!r}"
        )


@dataclass(frozen=True, slots=True)
class Bar:
    """One OHLCV bar covering `[open_time, open_time + interval)`."""

    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    interval: timedelta = BAR_INTERVAL

    def __post_init__(self) -> None:
        normalised = require_aligned_utc(
            self.open_time, self.interval, field_name="open_time"
        )
        object.__setattr__(self, "open_time", normalised)
        for name, price in (
            ("open", self.open),
            ("high", self.high),
            ("low", self.low),
            ("close", self.close),
        ):
            _require_price(price, name)
        if not math.isfinite(self.volume) or self.volume < 0.0:
            raise BarSemanticsError(
                f"volume must be finite and non-negative, got {self.volume!r}"
            )
        opened = normalised.isoformat()
        if self.high < max(self.open, self.close, self.low):
            raise BarSemanticsError(
                f"high {self.high!r} is below open/low/close "
                f"({self.open!r}, {self.low!r}, {self.close!r}) at {opened}"
            )
        if self.low > min(self.open, self.close, self.high):
            raise BarSemanticsError(
                f"low {self.low!r} is above open/high/close "
                f"({self.open!r}, {self.high!r}, {self.close!r}) at {opened}"
            )

    @property
    def close_time(self) -> datetime:
        """Exclusive end of the bar; the decision timestamp for this bar."""
        return self.open_time + self.interval


@dataclass(frozen=True, slots=True)
class ExecutionPoint:
    """Baseline execution resolved from a decision at a bar close.

    `execution_price` is the raw next-bar open. Fees, spread, and slippage
    from `specs/COST_MODEL_v1.md` are applied by the cost model, not here.
    """

    decision_time: datetime
    execution_time: datetime
    execution_price: float


@dataclass(frozen=True, slots=True)
class BarSeries:
    """Bars for one symbol, strictly increasing and interval-aligned.

    Construction enforces UTC, uniqueness, strict ordering, alignment, and a
    uniform interval. It does not enforce completeness: use
    `missing_open_times`, `require_contiguous`, or `contiguous_bar_series` to
    handle holes explicitly.
    """

    symbol: str
    bars: tuple[Bar, ...]
    interval: timedelta = BAR_INTERVAL
    _positions: dict[datetime, int] = field(
        init=False, repr=False, compare=False, default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.symbol:
            raise BarSemanticsError("symbol must be a non-empty string")
        _require_positive_interval(self.interval)
        bars = tuple(self.bars)
        if not bars:
            raise BarSemanticsError(f"{self.symbol} must contain at least one bar")
        for position, bar in enumerate(bars):
            if bar.interval != self.interval:
                opened = bar.open_time.isoformat()
                raise BarSemanticsError(
                    f"bar {position} at {opened} has interval {bar.interval}, "
                    f"expected {self.interval}"
                )
        for previous, current in zip(bars, bars[1:], strict=False):
            opened = current.open_time.isoformat()
            previous_opened = previous.open_time.isoformat()
            if current.open_time == previous.open_time:
                raise BarSemanticsError(
                    f"duplicate open_time {opened} in series {self.symbol}"
                )
            if current.open_time < previous.open_time:
                raise BarSemanticsError(
                    f"open_time must strictly increase in {self.symbol}: "
                    f"{opened} follows {previous_opened}"
                )
        positions = {bar.open_time: index for index, bar in enumerate(bars)}
        object.__setattr__(self, "bars", bars)
        self._positions.update(positions)

    def __len__(self) -> int:
        return len(self.bars)

    @property
    def start(self) -> datetime:
        """Inclusive open time of the first bar."""
        return self.bars[0].open_time

    @property
    def end(self) -> datetime:
        """Exclusive close time of the last bar."""
        return self.bars[-1].close_time

    def index_of(self, open_time: datetime) -> int:
        """Return the position of the bar opening at `open_time`."""
        target = require_aligned_utc(open_time, self.interval, field_name="open_time")
        position = self._positions.get(target)
        if position is None:
            raise BarSemanticsError(
                f"{self.symbol} has no bar with open_time {target.isoformat()}"
            )
        return position

    def bar_at(self, open_time: datetime) -> Bar:
        """Return the bar opening at `open_time`."""
        return self.bars[self.index_of(open_time)]

    def missing_open_times(self) -> tuple[datetime, ...]:
        """Return the open times absent between the first and last bar.

        Holes are reported, never filled. An empty result means the series is
        complete over its own span; it says nothing about data outside it.
        """
        missing: list[datetime] = []
        for previous, current in zip(self.bars, self.bars[1:], strict=False):
            expected = previous.open_time + self.interval
            while expected < current.open_time:
                missing.append(expected)
                expected += self.interval
        return tuple(missing)

    @property
    def is_contiguous(self) -> bool:
        """True when no `interval` step is missing inside the series span."""
        return not self.missing_open_times()

    def require_contiguous(self) -> None:
        """Raise unless the span is covered without any missing interval."""
        missing = self.missing_open_times()
        if missing:
            raise BarSemanticsError(
                f"{self.symbol} is missing {len(missing)} interval(s) of "
                f"{self.interval} between {self.start.isoformat()} and "
                f"{self.end.isoformat()}; first missing open_time is "
                f"{missing[0].isoformat()}"
            )

    def baseline_execution(self, decision_time: datetime) -> ExecutionPoint:
        """Resolve a decision at close(t) to the baseline fill at open(t+1).

        `decision_time` is a bar close timestamp. The fill is the open of the
        immediately following bar, which by construction opens at
        `decision_time`. Raises if the decision bar is unknown, if it is the
        final bar, or if the next interval is missing.
        """
        target = require_aligned_utc(
            decision_time, self.interval, field_name="decision_time"
        )
        execution_index = self.index_of(target - self.interval) + 1
        if execution_index >= len(self.bars):
            raise BarSemanticsError(
                f"decision at {target.isoformat()} is the final bar close of "
                f"{self.symbol}; open(t+1) does not exist"
            )
        execution_bar = self.bars[execution_index]
        if execution_bar.open_time != target:
            raise BarSemanticsError(
                f"decision at {target.isoformat()} cannot execute in "
                f"{self.symbol}: the next bar opens at "
                f"{execution_bar.open_time.isoformat()}, so open(t+1) is missing"
            )
        return ExecutionPoint(
            decision_time=target,
            execution_time=execution_bar.open_time,
            execution_price=execution_bar.open,
        )


def contiguous_bar_series(
    symbol: str, bars: Iterable[Bar], *, interval: timedelta = BAR_INTERVAL
) -> BarSeries:
    """Build a series claiming complete bars; raise on any missing interval."""
    series = BarSeries(symbol=symbol, bars=tuple(bars), interval=interval)
    series.require_contiguous()
    return series
