"""Direct unit tests for the deterministic descriptive metrics module."""

import math
from collections.abc import Callable, Sequence
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from aqt.backtest.costs import CostBreakdown
from aqt.backtest.engine import (
    BacktestResult,
    ExposureTarget,
    SegmentRecord,
    run_backtest,
)
from aqt.benchmarks.canonical import RebalanceAction
from aqt.data.bars import BAR_INTERVAL, Bar, BarSeries
from aqt.metrics.descriptive import (
    DescriptiveMetrics,
    MetricsError,
    cumulative_net_return,
    describe,
    equity_path,
    max_drawdown,
    paired_net_returns,
    segment_net_returns,
    total_cost,
    total_turnover,
)

EXECUTION_START = datetime(2020, 1, 2, tzinfo=UTC)

BREAKDOWN = CostBreakdown(
    fee_bps=10.0,
    fee_source="fallback",
    spread_bps=2.0,
    slippage_bps=1.0,
    sigma_hourly_bps=20.0,
    stress_multiplier=1.0,
)


def _segment(
    index: int,
    *,
    equity_before: float,
    equity_after_return: float,
    traded: float = 0.0,
    cost: float = 0.0,
    start: datetime = EXECUTION_START,
) -> SegmentRecord:
    """Build one synthetic segment record with an explicit equity pair."""
    decision_time = start + index * BAR_INTERVAL
    return SegmentRecord(
        index=index,
        decision_time=decision_time,
        execution_time=decision_time,
        segment_end_time=decision_time + BAR_INTERVAL,
        execution_price=100.0,
        gross_return=0.0,
        requested_exposure=1.0,
        clipped_target=1.0,
        held_weight_before=1.0,
        exposure=1.0,
        action=RebalanceAction.HOLD,
        reason="synthetic",
        side=None,
        traded=traded,
        cost_breakdown=BREAKDOWN,
        cost=cost,
        equity_before=equity_before,
        equity_after_cost=equity_before * (1.0 - cost),
        equity_after_return=equity_after_return,
    )


def _result(
    equities: Sequence[float],
    *,
    symbol: str = "BTCUSDT",
    stress_multiplier: float = 1.0,
    traded: Sequence[float] | None = None,
    costs: Sequence[float] | None = None,
    start: datetime = EXECUTION_START,
) -> BacktestResult:
    """Chain `equities` into a synthetic result opening at unit equity."""
    traded_path = tuple(traded) if traded is not None else (0.0,) * len(equities)
    cost_path = tuple(costs) if costs is not None else (0.0,) * len(equities)
    segments: list[SegmentRecord] = []
    equity = 1.0
    for index, after in enumerate(equities):
        segments.append(
            _segment(
                index,
                equity_before=equity,
                equity_after_return=after,
                traded=traded_path[index],
                cost=cost_path[index],
                start=start,
            )
        )
        equity = after
    return BacktestResult(
        symbol=symbol,
        stress_multiplier=stress_multiplier,
        segments=tuple(segments),
    )


def _raw_series(prices: Sequence[float], *, start: datetime) -> BarSeries:
    return BarSeries(
        symbol="BTCUSDT",
        bars=tuple(
            Bar(
                open_time=start + index * BAR_INTERVAL,
                open=price,
                high=price,
                low=price,
                close=price,
                volume=1.0,
            )
            for index, price in enumerate(prices)
        ),
    )


def _series(execution_opens: Sequence[float]) -> BarSeries:
    return _raw_series(
        [97.0, 98.0, 99.0, *execution_opens],
        start=EXECUTION_START - 3 * BAR_INTERVAL,
    )


def _targets(values: Sequence[float]) -> tuple[ExposureTarget, ...]:
    return tuple(
        ExposureTarget(
            decision_time=EXECUTION_START + index * BAR_INTERVAL,
            requested_exposure=value,
        )
        for index, value in enumerate(values)
    )


def test_empty_result_is_a_flat_zero_summary() -> None:
    metrics = describe(_result(()))

    assert metrics == DescriptiveMetrics(
        symbol="BTCUSDT",
        stress_multiplier=1.0,
        segment_count=0,
        initial_equity=1.0,
        final_equity=1.0,
        cumulative_net_return=0.0,
        max_drawdown=0.0,
        total_turnover=0.0,
        total_cost=0.0,
        net_returns=(),
    )
    assert equity_path(_result(())) == (1.0,)
    assert max_drawdown(_result(())) == 0.0


def test_hand_computed_adverse_path() -> None:
    result = _result(
        (0.8, 0.9, 0.5),
        traded=(1.0, 0.25, 0.5),
        costs=(0.001, 0.002, 0.004),
    )
    metrics = describe(result)

    assert metrics.segment_count == 3
    assert equity_path(result) == (1.0, 0.8, 0.9, 0.5)
    assert metrics.net_returns == pytest.approx(
        (-0.2, 0.9 / 0.8 - 1.0, 0.5 / 0.9 - 1.0)
    )
    assert metrics.cumulative_net_return == pytest.approx(-0.5)
    assert metrics.max_drawdown == pytest.approx(0.5)
    assert metrics.total_turnover == pytest.approx(1.75)
    assert metrics.total_cost == pytest.approx(0.007)
    assert metrics.final_equity == 0.5


def test_hand_computed_peak_then_partial_recovery() -> None:
    result = _result((1.0, 1.25, 1.0, 1.1))

    assert max_drawdown(result) == pytest.approx(0.2)
    assert cumulative_net_return(result) == pytest.approx(0.1)
    assert segment_net_returns(result) == pytest.approx(
        (0.0, 0.25, -0.2, 0.10000000000000009)
    )


def test_drawdown_resets_after_a_new_peak() -> None:
    assert max_drawdown(_result((0.9, 1.5, 1.0))) == pytest.approx(1.0 / 3.0)


def test_flat_path_has_zero_drawdown_and_zero_returns() -> None:
    result = _result((1.0, 1.0, 1.0))

    assert max_drawdown(result) == 0.0
    assert cumulative_net_return(result) == 0.0
    assert segment_net_returns(result) == (0.0, 0.0, 0.0)


def test_monotone_rising_path_has_zero_drawdown() -> None:
    assert max_drawdown(_result((1.1, 1.2, 1.3))) == 0.0


def test_drawdown_measures_from_the_initial_equity_peak() -> None:
    """The initial equity is a peak candidate, so a first-segment loss counts."""
    assert max_drawdown(_result((0.75,))) == pytest.approx(0.25)


def test_additive_summaries_use_fsum_not_a_running_sum() -> None:
    traded = (1e16, 1.0, 1.0)
    costs = (1e-6, 2e-6, 3e-6)
    result = _result((1.0, 1.0, 1.0), traded=traded, costs=costs)

    running = 0.0
    for value in traded:
        running += value
    assert running == 1e16

    assert total_turnover(result) == math.fsum(traded) == 1.0000000000000002e16
    assert total_cost(result) == math.fsum(costs)


def test_net_returns_match_the_backtester_equity_equation() -> None:
    result = run_backtest(_series([100.0, 110.0, 99.0]), _targets([1.0, 1.0]))
    metrics = describe(result)

    assert metrics.segment_count == 2
    expected = tuple(
        (1.0 - segment.cost) * (1.0 + segment.exposure * segment.gross_return) - 1.0
        for segment in result.segments
    )
    assert metrics.net_returns == pytest.approx(expected)
    assert metrics.net_returns[0] < result.segments[0].gross_return

    compounded = 1.0
    for value in metrics.net_returns:
        compounded *= 1.0 + value
    assert compounded == pytest.approx(metrics.final_equity)
    assert metrics.cumulative_net_return == pytest.approx(compounded - 1.0)
    assert metrics.total_turnover == pytest.approx(result.turnover)
    assert metrics.total_cost == pytest.approx(result.total_cost)


def test_zero_turnover_path_still_reports_costs_of_zero() -> None:
    result = run_backtest(_series([100.0, 110.0, 99.0]), _targets([0.0, 0.0]))
    metrics = describe(result)

    assert metrics.total_turnover == 0.0
    assert metrics.total_cost == 0.0
    assert metrics.net_returns == (0.0, 0.0)
    assert metrics.cumulative_net_return == 0.0
    assert metrics.max_drawdown == 0.0


def test_pairing_preserves_order_for_matching_paths() -> None:
    candidate = _result((1.1, 1.05, 1.2))
    benchmark = _result((1.05, 1.05, 1.1))

    paired = paired_net_returns(candidate, benchmark)

    candidate_returns = segment_net_returns(candidate)
    benchmark_returns = segment_net_returns(benchmark)
    assert paired == pytest.approx(
        tuple(
            left - right
            for left, right in zip(candidate_returns, benchmark_returns, strict=True)
        )
    )
    assert paired[0] == pytest.approx(0.05)
    assert paired != pytest.approx(tuple(reversed(paired)))


def test_pairing_a_result_with_itself_is_exactly_zero() -> None:
    candidate = _result((1.1, 0.9, 1.3))

    assert paired_net_returns(candidate, candidate) == (0.0, 0.0, 0.0)


def test_pairing_rejects_symbol_mismatch() -> None:
    candidate = _result((1.1,))
    benchmark = _result((1.1,), symbol="ETHUSDT")

    with pytest.raises(MetricsError, match="symbol mismatch"):
        paired_net_returns(candidate, benchmark)


def test_pairing_rejects_stress_multiplier_mismatch() -> None:
    candidate = _result((1.1,))
    benchmark = _result((1.1,), stress_multiplier=2.0)

    with pytest.raises(MetricsError, match="stress_multiplier mismatch"):
        paired_net_returns(candidate, benchmark)


def test_pairing_rejects_segment_count_mismatch() -> None:
    candidate = _result((1.1, 1.2))
    benchmark = _result((1.1,))

    with pytest.raises(MetricsError, match="segment count mismatch"):
        paired_net_returns(candidate, benchmark)


def test_pairing_rejects_execution_time_mismatch() -> None:
    candidate = _result((1.1, 1.2))
    benchmark = _result((1.1, 1.2), start=EXECUTION_START + BAR_INTERVAL)

    with pytest.raises(MetricsError, match="execution_time mismatch"):
        paired_net_returns(candidate, benchmark)


def test_pairing_rejects_segment_end_time_mismatch() -> None:
    candidate = _result((1.1, 1.2))
    head, tail = candidate.segments
    benchmark = BacktestResult(
        symbol="BTCUSDT",
        stress_multiplier=1.0,
        segments=(
            head,
            replace(tail, segment_end_time=tail.segment_end_time + timedelta(hours=2)),
        ),
    )

    with pytest.raises(MetricsError, match="segment_end_time mismatch"):
        paired_net_returns(candidate, benchmark)


def test_pairing_rejects_non_datetime_timestamps() -> None:
    candidate = _result((1.1,))
    segment = replace(candidate.segments[0], execution_time="not-a-timestamp")
    forged = BacktestResult(
        symbol="BTCUSDT", stress_multiplier=1.0, segments=(segment,)
    )

    with pytest.raises(MetricsError, match="execution_time must be timezone-aware"):
        paired_net_returns(candidate, forged)


@pytest.mark.parametrize(
    "consumer",
    [
        describe,
        segment_net_returns,
        cumulative_net_return,
        max_drawdown,
        total_turnover,
        total_cost,
        equity_path,
    ],
)
def test_every_consumer_rejects_a_non_finite_forged_equity(
    consumer: Callable[[BacktestResult], object],
) -> None:
    forged = BacktestResult(
        symbol="BTCUSDT",
        stress_multiplier=1.0,
        segments=(_segment(0, equity_before=1.0, equity_after_return=math.nan),),
    )

    with pytest.raises(MetricsError, match="equity_after_return must be finite"):
        consumer(forged)


@pytest.mark.parametrize(
    ("segments", "message"),
    [
        (
            (_segment(0, equity_before=0.0, equity_after_return=1.0),),
            "equity_before must be strictly positive",
        ),
        (
            (_segment(0, equity_before=1.0, equity_after_return=-1.0),),
            "equity_after_return must be strictly positive",
        ),
        (
            (_segment(0, equity_before=1.0, equity_after_return=math.inf),),
            "equity_after_return must be finite",
        ),
        (
            (_segment(0, equity_before=1.0, equity_after_return=1.0, traded=-1.0),),
            "traded must be nonnegative",
        ),
        (
            (_segment(0, equity_before=1.0, equity_after_return=1.0, cost=math.nan),),
            "cost must be finite",
        ),
        (
            (
                _segment(0, equity_before=1.0, equity_after_return=1.1),
                _segment(1, equity_before=2.0, equity_after_return=2.2),
            ),
            "does not continue the equity path",
        ),
        (
            (_segment(0, equity_before=1.5, equity_after_return=1.6),),
            "does not continue the equity path",
        ),
    ],
)
def test_forged_records_are_rejected(
    segments: tuple[SegmentRecord, ...], message: str
) -> None:
    forged = BacktestResult(symbol="BTCUSDT", stress_multiplier=1.0, segments=segments)

    with pytest.raises(MetricsError, match=message):
        describe(forged)


@pytest.mark.parametrize(
    ("result", "message"),
    [
        (object(), "must be a BacktestResult"),
        (
            BacktestResult(symbol="", stress_multiplier=1.0, segments=()),
            "symbol must be a non-empty string",
        ),
        (
            BacktestResult(symbol="BTCUSDT", stress_multiplier=math.nan, segments=()),
            "stress_multiplier must be finite",
        ),
    ],
)
def test_invalid_result_envelopes_are_rejected(result: object, message: str) -> None:
    with pytest.raises(MetricsError, match=message):
        describe(result)  # type: ignore[arg-type]


def test_pairing_validates_both_sides_before_comparing() -> None:
    candidate = _result((1.1,))
    forged = BacktestResult(
        symbol="BTCUSDT",
        stress_multiplier=1.0,
        segments=(_segment(0, equity_before=1.0, equity_after_return=math.nan),),
    )

    with pytest.raises(MetricsError, match="benchmark segment 0"):
        paired_net_returns(candidate, forged)
    with pytest.raises(MetricsError, match="candidate segment 0"):
        paired_net_returns(forged, candidate)


def test_inputs_are_not_mutated() -> None:
    result = run_backtest(_series([100.0, 110.0, 99.0]), _targets([1.0, -1.0]))
    before = (
        result.symbol,
        result.stress_multiplier,
        tuple(
            (
                segment.index,
                segment.execution_time,
                segment.segment_end_time,
                segment.traded,
                segment.cost,
                segment.equity_before,
                segment.equity_after_cost,
                segment.equity_after_return,
            )
            for segment in result.segments
        ),
    )

    first = describe(result)
    paired_net_returns(result, result)
    second = describe(result)

    assert first == second
    assert (
        result.symbol,
        result.stress_multiplier,
        tuple(
            (
                segment.index,
                segment.execution_time,
                segment.segment_end_time,
                segment.traded,
                segment.cost,
                segment.equity_before,
                segment.equity_after_cost,
                segment.equity_after_return,
            )
            for segment in result.segments
        ),
    ) == before
