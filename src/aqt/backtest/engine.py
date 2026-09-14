"""Pure deterministic production backtester for the Cycle-1 baseline."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from aqt.backtest.costs import (
    CostBreakdown,
    CostModelError,
    FeeSchedule,
    Side,
    ewma_hourly_volatility_bps_series,
    hourly_log_returns_bps,
    per_side_cost_bps,
    resolve_execution,
    resolve_taker_fee_bps,
)
from aqt.benchmarks.canonical import (
    MAX_EXPOSURE,
    MIN_EXPOSURE,
    CanonicalBenchmarkError,
    ExposureState,
    RebalanceAction,
    rebalance,
)
from aqt.data.bars import (
    BAR_INTERVAL,
    BarSemanticsError,
    BarSeries,
    require_aligned_utc,
)

__all__ = [
    "BacktestError",
    "BacktestResult",
    "ExposureTarget",
    "SegmentRecord",
    "run_backtest",
]


class BacktestError(ValueError):
    """Raised when input violates the frozen backtester semantics."""


@dataclass(frozen=True, slots=True)
class ExposureTarget:
    """One requested exposure known at an hourly bar close."""

    decision_time: datetime
    requested_exposure: float

    def __post_init__(self) -> None:
        try:
            moment = require_aligned_utc(
                self.decision_time,
                BAR_INTERVAL,
                field_name="decision_time",
            )
            requested = float(self.requested_exposure)
        except (BarSemanticsError, TypeError, ValueError) as error:
            raise BacktestError(str(error)) from error

        if not math.isfinite(requested):
            raise BacktestError(
                f"requested_exposure must be finite, got {self.requested_exposure!r}"
            )

        object.__setattr__(self, "decision_time", moment)
        object.__setattr__(self, "requested_exposure", requested)


@dataclass(frozen=True, slots=True)
class SegmentRecord:
    """Auditable execution, cost, exposure, and equity for one holding hour."""

    index: int
    decision_time: datetime
    execution_time: datetime
    segment_end_time: datetime
    execution_price: float
    gross_return: float
    requested_exposure: float
    clipped_target: float
    held_weight_before: float
    exposure: float
    action: RebalanceAction
    reason: str
    side: Side | None
    traded: float
    cost_breakdown: CostBreakdown
    cost: float
    equity_before: float
    equity_after_cost: float
    equity_after_return: float


@dataclass(frozen=True, slots=True)
class BacktestResult:
    """Complete deterministic result for one symbol and target path."""

    symbol: str
    stress_multiplier: float
    segments: tuple[SegmentRecord, ...]

    @property
    def initial_equity(self) -> float:
        return 1.0

    @property
    def final_equity(self) -> float:
        if not self.segments:
            return self.initial_equity
        return self.segments[-1].equity_after_return

    @property
    def turnover(self) -> float:
        total = 0.0
        for segment in self.segments:
            total += segment.traded
        return total

    @property
    def total_cost(self) -> float:
        total = 0.0
        for segment in self.segments:
            total += segment.cost
        return total


def _clip_exposure(requested: float) -> float:
    return min(MAX_EXPOSURE, max(MIN_EXPOSURE, requested))


def _drifted_exposure(exposure: float, gross_return: float) -> float:
    if exposure in (MIN_EXPOSURE, MAX_EXPOSURE):
        return exposure
    return exposure * (1.0 + gross_return) / (1.0 + exposure * gross_return)


def run_backtest(
    series: BarSeries,
    targets: Sequence[ExposureTarget],
    *,
    fees: FeeSchedule | None = None,
    stress_multiplier: float = 1.0,
    delay_bars: int = 0,
) -> BacktestResult:
    """Execute an hourly target path from flat over open-to-open segments.

    Delay stress is refused because the frozen artifacts do not define whether
    decisions occurring before a delayed fill observe pre-fill or post-fill
    exposure.
    """
    if not isinstance(series, BarSeries):
        raise BacktestError(f"series must be a BarSeries, got {series!r}")
    if not isinstance(delay_bars, int) or isinstance(delay_bars, bool):
        raise BacktestError(f"delay_bars must be an integer, got {delay_bars!r}")
    if delay_bars != 0:
        raise BacktestError(
            "delay_bars is unbound for target-path execution: delayed fills "
            "can overlap later hourly decisions, and the frozen artifacts do "
            "not specify whether those decisions observe pre-fill or "
            "post-fill state"
        )
    if isinstance(stress_multiplier, bool):
        raise BacktestError(
            f"stress_multiplier must be numeric, got {stress_multiplier!r}"
        )

    path = tuple(targets)
    if any(not isinstance(target, ExposureTarget) for target in path):
        raise BacktestError("targets must contain only ExposureTarget values")

    try:
        series.require_contiguous()

        per_side_cost_bps(
            sigma_hourly_bps=0.0,
            stress_multiplier=stress_multiplier,
        )

        if not path:
            return BacktestResult(
                symbol=series.symbol,
                stress_multiplier=float(stress_multiplier),
                segments=(),
            )

        for previous, current in zip(path, path[1:], strict=False):
            expected = previous.decision_time + BAR_INTERVAL
            if current.decision_time != expected:
                raise BacktestError(
                    "targets must be a contiguous hourly path: "
                    f"{current.decision_time.isoformat()} does not follow "
                    f"{previous.decision_time.isoformat()}"
                )

        returns_bps = hourly_log_returns_bps(series)
        volatility_bps = ewma_hourly_volatility_bps_series(returns_bps)

        state = ExposureState(current_exposure=MIN_EXPOSURE)
        equity = 1.0
        segments: list[SegmentRecord] = []

        for index, target in enumerate(path):
            execution = resolve_execution(series, target.decision_time)
            execution_index = series.index_of(execution.execution_time)

            if execution_index < 3:
                raise BacktestError(
                    "cost volatility needs at least two hourly close returns "
                    f"observable at {target.decision_time.isoformat()}"
                )
            if execution_index + 1 >= len(series):
                raise BacktestError(
                    f"execution at {execution.execution_time.isoformat()} "
                    "has no following open for its holding-segment return"
                )

            end_bar = series.bars[execution_index + 1]
            gross_return = (
                end_bar.open - execution.execution_price
            ) / execution.execution_price
            if not math.isfinite(gross_return) or gross_return <= -1.0:
                raise BacktestError(
                    f"segment {index} gross_return {gross_return!r} is not a "
                    "finite positive-price return greater than -1"
                )
            clipped = _clip_exposure(target.requested_exposure)
            decision = rebalance(state, clipped, target.decision_time)

            held_before = state.current_exposure
            executed = decision.new_exposure
            traded = abs(executed - held_before)

            side: Side | None = None
            if executed > held_before:
                side = Side.BUY
            elif executed < held_before:
                side = Side.SELL

            breakdown = per_side_cost_bps(
                sigma_hourly_bps=volatility_bps[execution_index - 3],
                fee=resolve_taker_fee_bps(fees, execution.execution_time),
                stress_multiplier=stress_multiplier,
            )
            cost = breakdown.cost_quote(traded)
            if cost >= 1.0:
                raise BacktestError(
                    f"segment {index} cost {cost!r} would consume all equity"
                )

            equity_before = equity
            equity_after_cost = equity_before * (1.0 - cost)
            if not math.isfinite(equity_after_cost) or equity_after_cost <= 0.0:
                raise BacktestError(
                    f"segment {index} equity_after_cost {equity_after_cost!r} "
                    "is not finite and strictly positive"
                )
            equity_after_return = equity_after_cost * (1.0 + executed * gross_return)
            if not math.isfinite(equity_after_return) or equity_after_return <= 0.0:
                raise BacktestError(
                    f"segment {index} equity_after_return "
                    f"{equity_after_return!r} is not finite and strictly positive"
                )

            segments.append(
                SegmentRecord(
                    index=index,
                    decision_time=target.decision_time,
                    execution_time=execution.execution_time,
                    segment_end_time=end_bar.open_time,
                    execution_price=execution.execution_price,
                    gross_return=gross_return,
                    requested_exposure=target.requested_exposure,
                    clipped_target=clipped,
                    held_weight_before=held_before,
                    exposure=executed,
                    action=decision.action,
                    reason=decision.reason,
                    side=side,
                    traded=traded,
                    cost_breakdown=breakdown,
                    cost=cost,
                    equity_before=equity_before,
                    equity_after_cost=equity_after_cost,
                    equity_after_return=equity_after_return,
                )
            )

            equity = equity_after_return
            state = ExposureState(
                current_exposure=_drifted_exposure(executed, gross_return),
                last_risk_increase_time=decision.last_risk_increase_time,
            )

    except BacktestError:
        raise
    except (
        BarSemanticsError,
        CanonicalBenchmarkError,
        CostModelError,
    ) as error:
        raise BacktestError(str(error)) from error

    return BacktestResult(
        symbol=series.symbol,
        stress_multiplier=float(stress_multiplier),
        segments=tuple(segments),
    )
