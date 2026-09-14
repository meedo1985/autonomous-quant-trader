"""Deterministic descriptive metrics over an accepted `BacktestResult`.

This module reports what a completed backtest did. It is pure: no input is
mutated, no clock is read, no randomness is drawn, no file or network is
touched. The same result always produces the same values.

Scope boundary
--------------
`protocols/protocol_v1.yaml` names Sharpe, confidence intervals, dependence
aware effective sample size, bootstrap, deflated Sharpe, and PBO, but does not
fix the return/annualization convention, the Newey-West lag and kernel, the
Politis-White variant, or the DSR/PBO tie and partition rules. Choosing those
here would set scientific policy outside the Constitution's amendment process,
so this module implements descriptive quantities only, as recorded in
`review/task11/SCIENTIFIC_DECISION.md`.

Nothing here emits a verdict, a pass/fail, an eligibility or promotion
decision, or a trial-budget judgement, and nothing here reads confirmation or
lockbox material. `segment_count` counts holding segments; it is *not* a
statistical sample size, because hourly segments are serially dependent
(`docs/RESEARCH_CONSTITUTION.md` section 16: bar count is not sample size).

Conventions
-----------
Every quantity follows the equity equation the accepted Task 8 backtester
already produces, where each segment charges cost before applying the exposed
return (`equity_after_cost = equity_before * (1 - cost)`, then
`equity_after_return = equity_after_cost * (1 + exposure * gross_return)`):

* A segment net return is `equity_after_return / equity_before - 1`, so it is
  net of that segment's modeled cost.
* The equity path is the initial equity followed by each segment's
  `equity_after_return`, in segment order. The intra-segment
  `equity_after_cost` point is not a separate observation.
* Cumulative net return is `final_equity / initial_equity - 1`.
* Maximum drawdown is the largest peak-to-trough fractional loss over that
  equity path, with the initial equity as the first peak candidate. It is
  reported as a nonnegative magnitude; a monotonically rising or flat path
  gives `0.0`.
* Total turnover and total cost are `math.fsum` over the per-segment `traded`
  and `cost` fields, so the summary does not depend on a running-sum rounding
  path. These may therefore differ in the last bits from the plain running
  sums exposed by `BacktestResult.turnover` and `BacktestResult.total_cost`.
* Paired observations are candidate net return minus benchmark net return at
  identical segment timestamps, in the original order.

No silent correction
--------------------
A result whose records are non-finite, non-positive in equity, negative in
turnover or cost, or discontinuous in the equity chain raises `MetricsError`.
Nothing is clamped, dropped, reordered, or defaulted. Pairing fails closed on
any symbol, stress-multiplier, segment-count, execution-time, or segment-end
mismatch rather than aligning or truncating the two paths.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime

from aqt.backtest.engine import BacktestResult, SegmentRecord

__all__ = [
    "DescriptiveMetrics",
    "MetricsError",
    "cumulative_net_return",
    "describe",
    "equity_path",
    "max_drawdown",
    "paired_net_returns",
    "segment_net_returns",
    "total_cost",
    "total_turnover",
]


class MetricsError(ValueError):
    """Raised when a backtest result cannot support a descriptive metric."""


@dataclass(frozen=True, slots=True)
class DescriptiveMetrics:
    """Deterministic descriptive summary of one accepted backtest result."""

    symbol: str
    stress_multiplier: float
    segment_count: int
    """Number of holding segments. Not a statistical sample size."""

    initial_equity: float
    final_equity: float
    cumulative_net_return: float
    max_drawdown: float
    """Nonnegative peak-to-trough magnitude over the segment equity path."""

    total_turnover: float
    total_cost: float
    net_returns: tuple[float, ...]
    """Per-segment net returns in segment order."""


def _require_finite(value: float, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, float | int):
        raise MetricsError(f"{field_name} must be a real number, got {value!r}")
    result = float(value)
    if not math.isfinite(result):
        raise MetricsError(f"{field_name} must be finite, got {value!r}")
    return result


def _require_positive(value: float, field_name: str) -> float:
    result = _require_finite(value, field_name)
    if result <= 0.0:
        raise MetricsError(f"{field_name} must be strictly positive, got {value!r}")
    return result


def _require_non_negative(value: float, field_name: str) -> float:
    result = _require_finite(value, field_name)
    if result < 0.0:
        raise MetricsError(f"{field_name} must be nonnegative, got {value!r}")
    return result


def _validated(result: BacktestResult, field_name: str) -> tuple[SegmentRecord, ...]:
    """Return the segments of `result` after checking every consumed field.

    The equity chain is checked for exact continuity: the first segment must
    open at the initial equity and each later segment must open where the
    previous one closed. A forged or edited record that breaks the chain would
    make the per-segment returns and the cumulative return describe different
    paths, so it is rejected rather than summarized.
    """
    if not isinstance(result, BacktestResult):
        raise MetricsError(f"{field_name} must be a BacktestResult, got {result!r}")
    if not isinstance(result.symbol, str) or not result.symbol:
        raise MetricsError(
            f"{field_name} symbol must be a non-empty string, got {result.symbol!r}"
        )
    _require_finite(result.stress_multiplier, f"{field_name} stress_multiplier")

    segments = result.segments
    if not isinstance(segments, tuple):
        raise MetricsError(f"{field_name} segments must be a tuple, got {segments!r}")

    equity = _require_positive(result.initial_equity, f"{field_name} initial_equity")
    previous_execution: datetime | None = None
    previous_end: datetime | None = None
    for index, segment in enumerate(segments):
        if not isinstance(segment, SegmentRecord):
            raise MetricsError(
                f"{field_name} segment {index} must be a SegmentRecord, got {segment!r}"
            )
        label = f"{field_name} segment {index}"
        if segment.index != index:
            raise MetricsError(
                f"{label} index {segment.index!r} does not match position {index}"
            )
        for timestamp_name in ("execution_time", "segment_end_time"):
            timestamp = getattr(segment, timestamp_name)
            if (
                not isinstance(timestamp, datetime)
                or timestamp.tzinfo is None
                or timestamp.utcoffset() is None
            ):
                raise MetricsError(
                    f"{label} {timestamp_name} must be timezone-aware datetime"
                )
        if segment.execution_time >= segment.segment_end_time:
            raise MetricsError(f"{label} execution_time must precede segment_end_time")
        if (
            previous_execution is not None
            and segment.execution_time <= previous_execution
        ):
            raise MetricsError(f"{label} execution_time is not strictly increasing")
        if previous_end is not None and segment.segment_end_time <= previous_end:
            raise MetricsError(f"{label} segment_end_time is not strictly increasing")
        previous_execution = segment.execution_time
        previous_end = segment.segment_end_time
        before = _require_positive(segment.equity_before, f"{label} equity_before")
        after_cost = _require_positive(
            segment.equity_after_cost, f"{label} equity_after_cost"
        )
        after = _require_positive(
            segment.equity_after_return, f"{label} equity_after_return"
        )
        if before != equity:
            raise MetricsError(
                f"{label} equity_before {segment.equity_before!r} does not "
                f"continue the equity path from {equity!r}"
            )
        _require_non_negative(segment.traded, f"{label} traded")
        cost = _require_non_negative(segment.cost, f"{label} cost")
        expected_after_cost = before * (1.0 - cost)
        if expected_after_cost != after_cost:
            raise MetricsError(
                f"{label} equity_after_cost {segment.equity_after_cost!r} does not "
                f"match equity_before and cost ({expected_after_cost!r})"
            )
        equity = after

    _require_positive(result.final_equity, f"{field_name} final_equity")
    return segments


def _net_return(segment: SegmentRecord, label: str) -> float:
    value = segment.equity_after_return / segment.equity_before - 1.0
    if not math.isfinite(value):
        raise MetricsError(f"{label} net return {value!r} is not finite")
    return value


def _net_returns(
    segments: tuple[SegmentRecord, ...], field_name: str
) -> tuple[float, ...]:
    return tuple(
        _net_return(segment, f"{field_name} segment {index}")
        for index, segment in enumerate(segments)
    )


def _equity_path(
    result: BacktestResult, segments: tuple[SegmentRecord, ...]
) -> tuple[float, ...]:
    return (
        float(result.initial_equity),
        *(float(segment.equity_after_return) for segment in segments),
    )


def _max_drawdown(path: tuple[float, ...]) -> float:
    peak = path[0]
    worst = 0.0
    for equity in path:
        if equity > peak:
            peak = equity
        drop = (peak - equity) / peak
        if drop > worst:
            worst = drop
    return worst


def segment_net_returns(result: BacktestResult) -> tuple[float, ...]:
    """Return per-segment net returns of `result`, in segment order."""
    return _net_returns(_validated(result, "result"), "result")


def equity_path(result: BacktestResult) -> tuple[float, ...]:
    """Return the initial equity followed by each segment's closing equity."""
    return _equity_path(result, _validated(result, "result"))


def cumulative_net_return(result: BacktestResult) -> float:
    """Return `final_equity / initial_equity - 1` for `result`."""
    _validated(result, "result")
    return result.final_equity / result.initial_equity - 1.0


def max_drawdown(result: BacktestResult) -> float:
    """Return the nonnegative maximum drawdown magnitude of `result`."""
    return _max_drawdown(_equity_path(result, _validated(result, "result")))


def total_turnover(result: BacktestResult) -> float:
    """Return the total absolute traded weight of `result`."""
    segments = _validated(result, "result")
    return math.fsum(segment.traded for segment in segments)


def total_cost(result: BacktestResult) -> float:
    """Return the fsum of per-segment modeled cost fractions."""
    segments = _validated(result, "result")
    return math.fsum(segment.cost for segment in segments)


def describe(result: BacktestResult) -> DescriptiveMetrics:
    """Return every descriptive metric of `result` in one deterministic pass."""
    segments = _validated(result, "result")
    return DescriptiveMetrics(
        symbol=result.symbol,
        stress_multiplier=float(result.stress_multiplier),
        segment_count=len(segments),
        initial_equity=float(result.initial_equity),
        final_equity=float(result.final_equity),
        cumulative_net_return=result.final_equity / result.initial_equity - 1.0,
        max_drawdown=_max_drawdown(_equity_path(result, segments)),
        total_turnover=math.fsum(segment.traded for segment in segments),
        total_cost=math.fsum(segment.cost for segment in segments),
        net_returns=_net_returns(segments, "result"),
    )


def paired_net_returns(
    candidate: BacktestResult, benchmark: BacktestResult
) -> tuple[float, ...]:
    """Return candidate-minus-benchmark net returns on a strictly aligned path.

    Both results must describe the same symbol under the same stress
    multiplier, with the same number of segments and identical execution and
    segment-end timestamps at every position. Any mismatch raises
    `MetricsError`; nothing is aligned, reordered, or truncated.
    """
    candidate_segments = _validated(candidate, "candidate")
    benchmark_segments = _validated(benchmark, "benchmark")

    if candidate.symbol != benchmark.symbol:
        raise MetricsError(
            f"symbol mismatch: candidate {candidate.symbol!r} versus benchmark "
            f"{benchmark.symbol!r}"
        )
    if candidate.stress_multiplier != benchmark.stress_multiplier:
        raise MetricsError(
            "stress_multiplier mismatch: candidate "
            f"{candidate.stress_multiplier!r} versus benchmark "
            f"{benchmark.stress_multiplier!r}"
        )
    if len(candidate_segments) != len(benchmark_segments):
        raise MetricsError(
            f"segment count mismatch: candidate {len(candidate_segments)} "
            f"versus benchmark {len(benchmark_segments)}"
        )

    paired: list[float] = []
    for index, (left, right) in enumerate(
        zip(candidate_segments, benchmark_segments, strict=True)
    ):
        if left.execution_time != right.execution_time:
            raise MetricsError(
                f"segment {index} execution_time mismatch: candidate "
                f"{left.execution_time!r} versus benchmark "
                f"{right.execution_time!r}"
            )
        if left.segment_end_time != right.segment_end_time:
            raise MetricsError(
                f"segment {index} segment_end_time mismatch: candidate "
                f"{left.segment_end_time!r} versus benchmark "
                f"{right.segment_end_time!r}"
            )
        delta = _net_return(left, f"candidate segment {index}") - _net_return(
            right, f"benchmark segment {index}"
        )
        if not math.isfinite(delta):
            raise MetricsError(f"segment {index} paired net return is not finite")
        paired.append(delta)

    return tuple(paired)
