"""Direct unit tests for the deterministic production backtester."""

import math
import statistics
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

import pytest

from aqt.backtest.costs import FeeSchedule, FeeTier, Side
from aqt.backtest.engine import BacktestError, ExposureTarget, run_backtest
from aqt.benchmarks.canonical import RebalanceAction
from aqt.data.bars import BAR_INTERVAL, Bar, BarSeries

EXECUTION_START = datetime(2020, 1, 2, tzinfo=UTC)


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


def _series_with_closes(
    opens: Sequence[float], closes: Sequence[float], *, start: datetime
) -> BarSeries:
    assert len(opens) == len(closes)
    return BarSeries(
        symbol="BTCUSDT",
        bars=tuple(
            Bar(
                open_time=start + index * BAR_INTERVAL,
                open=opened,
                high=max(opened, closed),
                low=min(opened, closed),
                close=closed,
                volume=1.0,
            )
            for index, (opened, closed) in enumerate(zip(opens, closes, strict=True))
        ),
    )


def _targets(values: Sequence[float]) -> tuple[ExposureTarget, ...]:
    return tuple(
        ExposureTarget(
            decision_time=EXECUTION_START + index * BAR_INTERVAL,
            requested_exposure=value,
        )
        for index, value in enumerate(values)
    )


def test_next_open_timing_clipping_and_intraday_reduction() -> None:
    result = run_backtest(_series([100.0, 110.0, 99.0]), _targets([2.0, -1.0]))

    first, second = result.segments
    assert first.decision_time == EXECUTION_START
    assert first.execution_time == EXECUTION_START
    assert first.segment_end_time == EXECUTION_START + BAR_INTERVAL
    assert first.execution_price == 100.0
    assert first.gross_return == pytest.approx(0.10)
    assert first.requested_exposure == 2.0
    assert first.clipped_target == 1.0
    assert first.held_weight_before == 0.0
    assert first.exposure == 1.0
    assert first.action is RebalanceAction.SCHEDULED_INCREASE
    assert first.side is Side.BUY
    assert first.traded == 1.0

    assert second.requested_exposure == -1.0
    assert second.clipped_target == 0.0
    assert second.held_weight_before == 1.0
    assert second.exposure == 0.0
    assert second.action is RebalanceAction.INTRADAY_REDUCTION
    assert second.side is Side.SELL
    assert second.traded == 1.0


def test_adverse_fractional_drift_holds_intraday_increase() -> None:
    result = run_backtest(_series([100.0, 50.0, 50.0]), _targets([0.5, 0.5]))

    first, second = result.segments
    assert first.exposure == 0.5
    assert first.gross_return == -0.5
    assert second.held_weight_before == pytest.approx(1.0 / 3.0)
    assert second.clipped_target == 0.5
    assert second.exposure == pytest.approx(1.0 / 3.0)
    assert second.action is RebalanceAction.HOLD
    assert second.side is None
    assert second.traded == 0.0


@pytest.mark.parametrize(
    ("second_target", "expected_action", "expected_exposure"),
    [
        (0.4, RebalanceAction.INTRADAY_REDUCTION, 0.4),
        (0.400001, RebalanceAction.HOLD, 0.5),
    ],
)
def test_inclusive_band_and_just_inside_band(
    second_target: float,
    expected_action: RebalanceAction,
    expected_exposure: float,
) -> None:
    result = run_backtest(
        _series([100.0, 100.0, 100.0]),
        _targets([0.5, second_target]),
    )

    second = result.segments[1]
    assert second.action is expected_action
    assert second.exposure == pytest.approx(expected_exposure)


def test_intraday_increase_waits_until_next_scheduled_decision() -> None:
    result = run_backtest(
        _series([100.0] * 26),
        _targets([0.5, *([0.9] * 24)]),
    )

    assert result.segments[0].action is RebalanceAction.SCHEDULED_INCREASE
    assert result.segments[1].action is RebalanceAction.HOLD
    assert result.segments[23].action is RebalanceAction.HOLD
    assert result.segments[24].decision_time.hour == 0
    assert result.segments[24].action is RebalanceAction.SCHEDULED_INCREASE
    assert result.segments[24].traded == pytest.approx(0.4)
    assert result.turnover == pytest.approx(0.9)


def test_reduction_at_midnight_is_scheduled_and_not_hold_blocked() -> None:
    result = run_backtest(
        _series([100.0] * 26),
        _targets([0.5, *([0.5] * 23), 0.0]),
    )

    final = result.segments[-1]
    assert final.decision_time.hour == 0
    assert final.action is RebalanceAction.SCHEDULED_REDUCTION
    assert final.side is Side.SELL
    assert final.traded == 0.5
    assert final.exposure == 0.0


def test_cost_is_charged_before_return_with_fee_source_and_stress() -> None:
    series = _series([100.0, 110.0])
    targets = _targets([1.0])

    fallback = run_backtest(series, targets)
    scheduled = run_backtest(
        series,
        targets,
        fees=FeeSchedule(
            tiers=(
                FeeTier(
                    effective_from=EXECUTION_START,
                    taker_fee_bps=4.0,
                ),
            )
        ),
    )
    stressed = run_backtest(series, targets, stress_multiplier=3.0)

    segment = fallback.segments[0]
    assert segment.cost_breakdown.fee_source == "fallback"
    assert segment.cost_breakdown.fee_bps == 10.0
    assert segment.cost == pytest.approx(segment.cost_breakdown.total_bps / 10_000.0)
    assert segment.equity_after_cost == pytest.approx(1.0 - segment.cost)
    assert segment.equity_after_return == pytest.approx(
        segment.equity_after_cost * 1.10
    )

    scheduled_segment = scheduled.segments[0]
    assert scheduled_segment.cost_breakdown.fee_source == "schedule"
    assert scheduled_segment.cost_breakdown.fee_bps == 4.0
    assert scheduled_segment.cost < segment.cost

    assert stressed.segments[0].cost == pytest.approx(3.0 * segment.cost)
    assert stressed.final_equity < fallback.final_equity


def test_first_cost_uses_only_close_returns_known_at_the_decision() -> None:
    opens = [100.0, 100.0, 100.0, 100.0, 110.0]
    prefix_closes = [100.0, 120.0, 90.0]
    first = _series_with_closes(
        opens,
        [*prefix_closes, 10.0, 1_000.0],
        start=EXECUTION_START - 3 * BAR_INTERVAL,
    )
    mutated_future = _series_with_closes(
        opens,
        [*prefix_closes, 1_000.0, 10.0],
        start=EXECUTION_START - 3 * BAR_INTERVAL,
    )

    observed_returns = [
        math.log(current / previous) * 10_000.0
        for previous, current in zip(prefix_closes, prefix_closes[1:], strict=False)
    ]
    expected_sigma = statistics.stdev(observed_returns)

    first_segment = run_backtest(first, _targets([1.0])).segments[0]
    mutated_segment = run_backtest(mutated_future, _targets([1.0])).segments[0]
    assert first_segment.cost_breakdown.sigma_hourly_bps == pytest.approx(
        expected_sigma
    )
    assert first_segment.cost_breakdown == mutated_segment.cost_breakdown
    assert first_segment.cost == mutated_segment.cost


def test_zero_exposure_has_no_cost_or_trading_pnl() -> None:
    result = run_backtest(_series([100.0, 125.0]), _targets([0.0]))

    segment = result.segments[0]
    assert segment.exposure == 0.0
    assert segment.traded == 0.0
    assert segment.cost == 0.0
    assert segment.equity_after_return == 1.0
    assert result.final_equity == 1.0


def test_terminal_exposure_is_not_liquidated() -> None:
    result = run_backtest(_series([100.0, 100.0]), _targets([0.5]))

    assert len(result.segments) == 1
    assert result.segments[0].exposure == 0.5
    assert result.turnover == 0.5


@pytest.mark.parametrize(
    "moment",
    [
        datetime(2020, 1, 2),
        EXECUTION_START + timedelta(minutes=1),
    ],
)
def test_target_rejects_invalid_decision_timestamp(moment: datetime) -> None:
    with pytest.raises(BacktestError):
        ExposureTarget(moment, 0.5)


@pytest.mark.parametrize("requested", [math.nan, math.inf, -math.inf])
def test_target_rejects_nonfinite_exposure(requested: float) -> None:
    with pytest.raises(BacktestError):
        ExposureTarget(EXECUTION_START, requested)


def test_engine_rejects_unbound_delay_invalid_stress_and_target_gap() -> None:
    series = _series([100.0, 100.0, 100.0, 100.0])

    with pytest.raises(BacktestError, match="unbound"):
        run_backtest(series, _targets([0.5]), delay_bars=1)

    with pytest.raises(BacktestError):
        run_backtest(series, _targets([0.5]), stress_multiplier=1.2)

    with pytest.raises(BacktestError, match="stress_multiplier must be numeric"):
        run_backtest(series, _targets([0.5]), stress_multiplier=True)

    gapped_targets = (
        ExposureTarget(EXECUTION_START, 0.5),
        ExposureTarget(EXECUTION_START + 2 * BAR_INTERVAL, 0.0),
    )
    with pytest.raises(BacktestError, match="contiguous hourly path"):
        run_backtest(series, gapped_targets)


@pytest.mark.parametrize("invalid", [None, ()])
def test_engine_rejects_non_bar_series_with_public_error(invalid: object) -> None:
    with pytest.raises(BacktestError, match="series must be a BarSeries"):
        run_backtest(invalid, _targets([0.5]))  # type: ignore[arg-type]


def test_engine_rejects_missing_history_terminal_return_and_bar_gap() -> None:
    insufficient = _raw_series(
        [98.0, 99.0, 100.0, 101.0],
        start=EXECUTION_START - 2 * BAR_INTERVAL,
    )
    with pytest.raises(BacktestError, match="at least two hourly close returns"):
        run_backtest(insufficient, _targets([0.5]))

    with pytest.raises(BacktestError, match="no following open"):
        run_backtest(_series([100.0]), _targets([0.5]))

    complete = _series([100.0, 100.0])
    gapped = BarSeries(
        symbol=complete.symbol,
        bars=complete.bars[:2] + complete.bars[3:],
    )
    with pytest.raises(BacktestError):
        run_backtest(gapped, ())


@pytest.mark.parametrize(
    "execution_opens",
    [
        (1e-300, 1e300),
        (1.0, 1e-20),
    ],
)
def test_engine_rejects_unrepresentable_positive_price_returns(
    execution_opens: tuple[float, float],
) -> None:
    opens = (97.0, 98.0, 99.0, *execution_opens)
    series = _series_with_closes(
        opens,
        (100.0,) * len(opens),
        start=EXECUTION_START - 3 * BAR_INTERVAL,
    )
    with pytest.raises(BacktestError, match="gross_return"):
        run_backtest(series, _targets([0.0]))


def test_engine_rejects_cumulative_equity_overflow() -> None:
    execution_opens = tuple(10.0 ** (-300 + 2 * index) for index in range(301))

    with pytest.raises(BacktestError, match="equity_after_return"):
        run_backtest(_series(execution_opens), _targets([1.0] * 300))


def test_reruns_are_identical_and_inputs_are_not_mutated() -> None:
    series = _series([100.0, 110.0, 105.0])
    targets = list(_targets([0.5, 0.2]))
    bars_before = series.bars
    targets_before = tuple(targets)

    first = run_backtest(series, targets)
    second = run_backtest(series, targets)

    assert first == second
    assert series.bars == bars_before
    assert tuple(targets) == targets_before
