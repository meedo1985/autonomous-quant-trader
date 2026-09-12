"""Deterministic cost model for Cycle-1 taker-like spot execution.

This module implements `specs/COST_MODEL_v1.md` exactly and nothing else. It
is pure: every function is a total function of its arguments, no input is
mutated, no clock is read, no randomness is drawn, no file or network is
touched. The same arguments always produce the same result.

Frozen sources encoded here:

* `specs/COST_MODEL_v1.md` "Baseline execution": decision at an eligible 1h
  bar close, baseline fill at the next 1h bar open, costs applied after.
* `specs/COST_MODEL_v1.md` "Order style": taker-like only.
* `specs/COST_MODEL_v1.md` "Fee": point-in-time taker fee where a schedule is
  available, otherwise a 10 bps per-side fallback.
* `specs/COST_MODEL_v1.md` "Spread allowance": fixed 2 bps per side.
* `specs/COST_MODEL_v1.md` "Slippage": `min(15, max(1, 0.05 * sigma_bps))`
  over a trailing EWMA hourly volatility with a 168-hour half-life and the
  specified 168-return initialisation.
* `specs/COST_MODEL_v1.md` "Stress"/"Delay stress" and
  `protocols/protocol_v1.yaml` `cost_model.stress_multipliers`
  = `[1.0, 1.5, 2.0, 3.0]`, `validation.execution_delay_stress_bars` = 1.

Volatility conventions
----------------------
`sigma_hourly_bps` is the trailing EWMA standard deviation of hourly log
returns of bar closes, expressed in basis points. Returns are point-in-time:
the return of bar t is known at close(t), which is the decision timestamp of
bar t, so a decision at close(t) may use returns up to and including bar t.

The frozen spec fixes the half-life and the initialisation but not the return
definition or the recursion form; the choices made here are recorded in
`review/task3/LOCAL_REPORT.md`.

No silent correction
--------------------
Invalid input raises `CostModelError`, except that a timestamp which
violates Task 2 bar semantics surfaces the underlying `BarSemanticsError`
unchanged from `aqt.data.bars`; `resolve_execution` and `trade_cost` re-raise
it as `CostModelError` because they resolve a fill rather than a bare
timestamp. Nothing is clamped, defaulted, or
skipped behind the caller's back except the two behaviours the frozen spec
prescribes: the 10 bps fee fallback (always reported through
`FeeQuote.source`) and the 1 bp / 15 bps slippage floor and cap (always
reported alongside the volatility that produced them).

Out of scope for this module, because they belong to later scheduled tasks:
data ingestion, exchange or network access, exposure mapping, the rebalance
band, the minimum-hold rule, turnover accounting, portfolio aggregation, and
backtester orchestration.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Final

from aqt.data.bars import (
    BAR_INTERVAL,
    Bar,
    BarSemanticsError,
    BarSeries,
    ExecutionPoint,
    require_utc,
)

__all__ = [
    "BPS_PER_UNIT",
    "EWMA_HALF_LIFE_HOURS",
    "EXECUTION_DELAY_STRESS_BARS",
    "FALLBACK_TAKER_FEE_BPS",
    "SLIPPAGE_CAP_BPS",
    "SLIPPAGE_FLOOR_BPS",
    "SLIPPAGE_VOL_COEFFICIENT",
    "SPREAD_ALLOWANCE_BPS",
    "STRESS_MULTIPLIERS",
    "VOLATILITY_INIT_RETURNS",
    "CostBreakdown",
    "CostModelError",
    "FeeQuote",
    "FeeSchedule",
    "FeeTier",
    "Side",
    "TradeCost",
    "ewma_hourly_volatility_bps",
    "ewma_hourly_volatility_bps_series",
    "hourly_log_returns_bps",
    "per_side_cost_bps",
    "resolve_execution",
    "resolve_taker_fee_bps",
    "slippage_bps",
    "trade_cost",
]

BPS_PER_UNIT: Final[float] = 10_000.0
"""Basis points in one unit of notional."""

FALLBACK_TAKER_FEE_BPS: Final[float] = 10.0
"""Per-side taker fee used when no point-in-time schedule covers the fill."""

SPREAD_ALLOWANCE_BPS: Final[float] = 2.0
"""Fixed per-side spread allowance."""

SLIPPAGE_VOL_COEFFICIENT: Final[float] = 0.05
SLIPPAGE_FLOOR_BPS: Final[float] = 1.0
SLIPPAGE_CAP_BPS: Final[float] = 15.0

EWMA_HALF_LIFE_HOURS: Final[int] = 168
"""EWMA half-life of the hourly volatility estimator, in hours."""

VOLATILITY_INIT_RETURNS: Final[int] = 168
"""Returns covered by the simple sample-standard-deviation initialisation."""

STRESS_MULTIPLIERS: Final[tuple[float, ...]] = (1.0, 1.5, 2.0, 3.0)
"""Frozen cost stress multipliers."""

EXECUTION_DELAY_STRESS_BARS: Final[int] = 1
"""Additional 1h bars inserted before the fill under delay stress."""

_EWMA_DECAY: Final[float] = 0.5 ** (1.0 / EWMA_HALF_LIFE_HOURS)


class CostModelError(ValueError):
    """Raised when input violates the frozen cost-model rules."""


class Side(StrEnum):
    """Direction of a taker-like trade."""

    BUY = "buy"
    SELL = "sell"


def _require_finite(value: float, name: str) -> float:
    if not math.isfinite(value):
        raise CostModelError(f"{name} must be finite, got {value!r}")
    return float(value)


def _require_non_negative(value: float, name: str) -> float:
    _require_finite(value, name)
    if value < 0.0:
        raise CostModelError(f"{name} must be non-negative, got {value!r}")
    return float(value)


@dataclass(frozen=True, slots=True)
class FeeTier:
    """One point-in-time taker fee, effective from `effective_from` onwards.

    The tier applies to fills at or after `effective_from` and until the next
    tier's `effective_from`, if any.
    """

    effective_from: datetime
    taker_fee_bps: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "effective_from",
            require_utc(self.effective_from, field_name="effective_from"),
        )
        object.__setattr__(
            self,
            "taker_fee_bps",
            _require_non_negative(self.taker_fee_bps, "taker_fee_bps"),
        )


@dataclass(frozen=True, slots=True)
class FeeQuote:
    """A resolved per-side taker fee and where it came from."""

    fee_bps: float
    source: str
    """`"schedule"` for a point-in-time tier, `"fallback"` for the 10 bps rule."""


@dataclass(frozen=True, slots=True)
class FeeSchedule:
    """A point-in-time taker fee schedule, ordered by effective timestamp."""

    tiers: tuple[FeeTier, ...]

    def __post_init__(self) -> None:
        tiers = tuple(self.tiers)
        if not tiers:
            raise CostModelError(
                "fee schedule must contain at least one tier; pass None to use "
                f"the {FALLBACK_TAKER_FEE_BPS} bps fallback instead"
            )
        for previous, current in zip(tiers, tiers[1:], strict=False):
            if current.effective_from <= previous.effective_from:
                raise CostModelError(
                    "fee tiers must be strictly increasing in effective_from: "
                    f"{current.effective_from.isoformat()} follows "
                    f"{previous.effective_from.isoformat()}"
                )
        object.__setattr__(self, "tiers", tiers)

    @property
    def start(self) -> datetime:
        """Effective timestamp of the earliest tier."""
        return self.tiers[0].effective_from

    def quote(self, at: datetime) -> FeeQuote:
        """Return the fee effective at `at`, or the frozen fallback.

        A timestamp before the first tier is not covered by the schedule, so
        the spec's fallback applies and the quote says so.
        """
        moment = require_utc(at, field_name="at")
        resolved: FeeTier | None = None
        for tier in self.tiers:
            if tier.effective_from <= moment:
                resolved = tier
            else:
                break
        if resolved is None:
            return FeeQuote(fee_bps=FALLBACK_TAKER_FEE_BPS, source="fallback")
        return FeeQuote(fee_bps=resolved.taker_fee_bps, source="schedule")


def resolve_taker_fee_bps(fees: FeeSchedule | None, at: datetime) -> FeeQuote:
    """Resolve the per-side taker fee for a fill at `at`.

    With no schedule, or with a schedule that does not cover `at`, the frozen
    10 bps per-side fallback applies and is reported as such.
    """
    if fees is None:
        require_utc(at, field_name="at")
        return FeeQuote(fee_bps=FALLBACK_TAKER_FEE_BPS, source="fallback")
    return fees.quote(at)


def hourly_log_returns_bps(bars: BarSeries | Sequence[Bar]) -> tuple[float, ...]:
    """Return close-to-close hourly log returns, in basis points.

    Bars must be contiguous at the 1h interval: a return computed across a
    hole would not be an hourly return, and holes are never bridged silently.
    """
    if isinstance(bars, BarSeries):
        if bars.interval != BAR_INTERVAL:
            raise CostModelError(
                f"hourly returns require a {BAR_INTERVAL} series, got {bars.interval}"
            )
        try:
            bars.require_contiguous()
        except BarSemanticsError as error:
            raise CostModelError(str(error)) from error
        ordered: tuple[Bar, ...] = bars.bars
    else:
        ordered = tuple(bars)
        _require_contiguous_hourly(ordered)
    return tuple(
        math.log(current.close / previous.close) * BPS_PER_UNIT
        for previous, current in zip(ordered, ordered[1:], strict=False)
    )


def _require_contiguous_hourly(bars: tuple[Bar, ...]) -> None:
    for position, bar in enumerate(bars):
        if bar.interval != BAR_INTERVAL:
            raise CostModelError(
                f"bar {position} at {bar.open_time.isoformat()} has interval "
                f"{bar.interval}, expected {BAR_INTERVAL}"
            )
    for previous, current in zip(bars, bars[1:], strict=False):
        if current.open_time != previous.open_time + BAR_INTERVAL:
            raise CostModelError(
                "hourly returns require contiguous bars: "
                f"{current.open_time.isoformat()} does not follow "
                f"{previous.open_time.isoformat()} by {BAR_INTERVAL}"
            )


def ewma_hourly_volatility_bps_series(
    returns_bps: Iterable[float],
) -> tuple[float, ...]:
    """Return the trailing volatility estimate after each usable return.

    Element `k` is the estimate that uses `returns_bps[0 .. k + 1]`, so the
    result has one element fewer than the input: a sample standard deviation
    needs at least two returns. Per `specs/COST_MODEL_v1.md`, the first 168
    returns use the simple sample standard deviation of the returns available
    so far, and from return 169 onward the estimate is the recursive EWMA
    initialised from the sample variance of the first 168 returns.
    """
    returns = tuple(
        _require_finite(value, f"returns_bps[{index}]")
        for index, value in enumerate(returns_bps)
    )
    if len(returns) < 2:
        raise CostModelError(
            "at least 2 hourly returns are required for a sample standard "
            f"deviation, got {len(returns)}"
        )
    estimates: list[float] = []
    variance = 0.0
    for count in range(2, len(returns) + 1):
        if count <= VOLATILITY_INIT_RETURNS:
            variance = statistics.variance(returns[:count])
        else:
            latest = returns[count - 1]
            variance = _EWMA_DECAY * variance + (1.0 - _EWMA_DECAY) * latest * latest
        estimates.append(math.sqrt(variance))
    return tuple(estimates)


def ewma_hourly_volatility_bps(returns_bps: Iterable[float]) -> float:
    """Return the trailing volatility estimate after the last return."""
    return ewma_hourly_volatility_bps_series(returns_bps)[-1]


def slippage_bps(sigma_hourly_bps: float) -> float:
    """Return the frozen per-side slippage allowance, in basis points."""
    sigma = _require_non_negative(sigma_hourly_bps, "sigma_hourly_bps")
    return min(
        SLIPPAGE_CAP_BPS,
        max(SLIPPAGE_FLOOR_BPS, SLIPPAGE_VOL_COEFFICIENT * sigma),
    )


def _require_stress_multiplier(multiplier: float) -> float:
    _require_finite(multiplier, "stress_multiplier")
    for allowed in STRESS_MULTIPLIERS:
        if multiplier == allowed:
            return allowed
    raise CostModelError(
        f"stress_multiplier {multiplier!r} is not one of the frozen "
        f"multipliers {list(STRESS_MULTIPLIERS)}"
    )


@dataclass(frozen=True, slots=True)
class CostBreakdown:
    """Auditable per-side cost components, in basis points of notional."""

    fee_bps: float
    fee_source: str
    spread_bps: float
    slippage_bps: float
    sigma_hourly_bps: float
    stress_multiplier: float

    @property
    def base_total_bps(self) -> float:
        """Unstressed per-side total: fee + spread + slippage."""
        return self.fee_bps + self.spread_bps + self.slippage_bps

    @property
    def total_bps(self) -> float:
        """Per-side total after the stress multiplier."""
        return self.base_total_bps * self.stress_multiplier

    def cost_quote(self, notional_quote: float) -> float:
        """Return the modeled per-side cost for `notional_quote` of turnover."""
        notional = _require_non_negative(notional_quote, "notional_quote")
        return notional * self.total_bps / BPS_PER_UNIT


def per_side_cost_bps(
    *,
    sigma_hourly_bps: float,
    fee: FeeQuote | None = None,
    stress_multiplier: float = 1.0,
) -> CostBreakdown:
    """Return the per-side cost breakdown for one taker-like fill.

    `fee` defaults to the frozen 10 bps per-side fallback.
    """
    sigma = _require_non_negative(sigma_hourly_bps, "sigma_hourly_bps")
    multiplier = _require_stress_multiplier(stress_multiplier)
    quote = (
        FeeQuote(fee_bps=FALLBACK_TAKER_FEE_BPS, source="fallback")
        if fee is None
        else fee
    )
    _require_non_negative(quote.fee_bps, "fee_bps")
    return CostBreakdown(
        fee_bps=quote.fee_bps,
        fee_source=quote.source,
        spread_bps=SPREAD_ALLOWANCE_BPS,
        slippage_bps=slippage_bps(sigma),
        sigma_hourly_bps=sigma,
        stress_multiplier=multiplier,
    )


def resolve_execution(
    series: BarSeries, decision_time: datetime, *, delay_bars: int = 0
) -> ExecutionPoint:
    """Resolve the fill for a decision at a bar close, with optional delay.

    `delay_bars=0` is the frozen baseline, open(t+1). `delay_bars=1` is the
    frozen delay stress, open(t+2). Raises when the delayed bar does not
    exist or when a hole falls between the decision and the fill; a fill is
    never shifted onto a different bar to make it resolvable.
    """
    if delay_bars < 0:
        raise CostModelError(f"delay_bars must be non-negative, got {delay_bars}")
    try:
        baseline = series.baseline_execution(decision_time)
    except BarSemanticsError as error:
        raise CostModelError(str(error)) from error
    if delay_bars == 0:
        return baseline
    target_time = baseline.execution_time + delay_bars * series.interval
    try:
        bar = series.bar_at(target_time)
    except BarSemanticsError as error:
        raise CostModelError(
            f"delayed execution {delay_bars} bar(s) after "
            f"{baseline.execution_time.isoformat()} is unavailable: {error}"
        ) from error
    baseline_index = series.index_of(baseline.execution_time)
    if series.index_of(target_time) != baseline_index + delay_bars:
        raise CostModelError(
            f"delayed execution at {target_time.isoformat()} crosses a hole in "
            f"{series.symbol}; intermediate 1h bars are missing"
        )
    return ExecutionPoint(
        decision_time=baseline.decision_time,
        execution_time=bar.open_time,
        execution_price=bar.open,
    )


@dataclass(frozen=True, slots=True)
class TradeCost:
    """A cost estimate bound to one decision, fill, and side."""

    decision_time: datetime
    execution_time: datetime
    execution_price: float
    side: Side
    delay_bars: int
    returns_used: int
    breakdown: CostBreakdown

    @property
    def effective_price(self) -> float:
        """Fill price after costs: worse than the raw open on either side."""
        signed = self.breakdown.total_bps / BPS_PER_UNIT
        if self.side is Side.BUY:
            return self.execution_price * (1.0 + signed)
        return self.execution_price * (1.0 - signed)

    def cost_quote(self, notional_quote: float) -> float:
        """Return the modeled per-side cost for `notional_quote` of turnover."""
        return self.breakdown.cost_quote(notional_quote)


def trade_cost(
    series: BarSeries,
    decision_time: datetime,
    side: Side,
    *,
    fees: FeeSchedule | None = None,
    stress_multiplier: float = 1.0,
    delay_bars: int = 0,
) -> TradeCost:
    """Cost one taker-like trade decided at `decision_time`.

    Volatility uses only returns observable at the decision timestamp, that
    is, closes up to and including the decision bar. The fee is resolved at
    the fill timestamp. `series` is read, never modified.
    """
    if not isinstance(side, Side):
        raise CostModelError(f"side must be a Side, got {side!r}")
    multiplier = _require_stress_multiplier(stress_multiplier)
    execution = resolve_execution(series, decision_time, delay_bars=delay_bars)
    observed = _bars_through(series, execution.decision_time)
    returns = hourly_log_returns_bps(observed)
    sigma = ewma_hourly_volatility_bps(returns)
    breakdown = per_side_cost_bps(
        sigma_hourly_bps=sigma,
        fee=resolve_taker_fee_bps(fees, execution.execution_time),
        stress_multiplier=multiplier,
    )
    return TradeCost(
        decision_time=execution.decision_time,
        execution_time=execution.execution_time,
        execution_price=execution.execution_price,
        side=side,
        delay_bars=delay_bars,
        returns_used=len(returns),
        breakdown=breakdown,
    )


def _bars_through(series: BarSeries, decision_time: datetime) -> tuple[Bar, ...]:
    """Return the bars whose close is at or before `decision_time`.

    The result is the point-in-time history a decision at `decision_time` may
    use. It stops at the first hole looking backwards, because returns are
    not computed across holes.
    """
    decision_index = series.index_of(decision_time - series.interval)
    start = decision_index
    while start > 0:
        previous = series.bars[start - 1]
        if previous.open_time + series.interval != series.bars[start].open_time:
            break
        start -= 1
    window = series.bars[start : decision_index + 1]
    if len(window) < 3:
        raise CostModelError(
            f"decision at {decision_time.isoformat()} has {len(window)} "
            "contiguous bar(s) of history; at least 3 are required for two "
            "hourly returns"
        )
    return window
