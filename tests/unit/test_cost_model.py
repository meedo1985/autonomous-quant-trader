"""Synthetic cost-model tests. No real market data, no network access."""

import math
import statistics
from datetime import UTC, datetime, timedelta

import pytest

from aqt.backtest.costs import (
    BPS_PER_UNIT,
    EWMA_HALF_LIFE_HOURS,
    EXECUTION_DELAY_STRESS_BARS,
    FALLBACK_TAKER_FEE_BPS,
    SLIPPAGE_CAP_BPS,
    SLIPPAGE_FLOOR_BPS,
    SLIPPAGE_VOL_COEFFICIENT,
    SPREAD_ALLOWANCE_BPS,
    STRESS_MULTIPLIERS,
    VOLATILITY_INIT_RETURNS,
    CostModelError,
    FeeQuote,
    FeeSchedule,
    FeeTier,
    Side,
    ewma_hourly_volatility_bps,
    ewma_hourly_volatility_bps_series,
    hourly_log_returns_bps,
    per_side_cost_bps,
    resolve_execution,
    resolve_taker_fee_bps,
    slippage_bps,
    trade_cost,
)
from aqt.data.bars import BAR_INTERVAL, Bar, BarSemanticsError, BarSeries

_ORIGIN = datetime(2024, 1, 1, tzinfo=UTC)


def _ts(hour: int) -> datetime:
    return _ORIGIN + timedelta(hours=hour)


def _bar(hour: int, open_: float, close: float) -> Bar:
    return Bar(
        open_time=_ts(hour),
        open=open_,
        high=max(open_, close) * 1.001,
        low=min(open_, close) * 0.999,
        close=close,
        volume=1.0,
    )


def _series_from_closes(
    closes: tuple[float, ...],
    *,
    hours: tuple[int, ...] | None = None,
    first_open: float = 100.0,
    symbol: str = "TESTUSDT",
) -> BarSeries:
    """Build a series whose bar opens equal the previous bar's close."""
    positions = hours if hours is not None else tuple(range(len(closes)))
    if len(positions) != len(closes):
        raise AssertionError("hours and closes must have the same length")
    bars = []
    previous = first_open
    for hour, close in zip(positions, closes, strict=True):
        bars.append(_bar(hour, previous, close))
        previous = close
    return BarSeries(symbol=symbol, bars=tuple(bars))


def _geometric_closes(count: int, step_bps: float) -> tuple[float, ...]:
    """A deterministic alternating-return price path."""
    closes = []
    price = 100.0
    for index in range(count):
        direction = 1.0 if index % 2 == 0 else -1.0
        price *= math.exp(direction * step_bps / BPS_PER_UNIT)
        closes.append(price)
    return tuple(closes)


def _expected_returns_bps(closes: tuple[float, ...]) -> list[float]:
    return [
        math.log(later / earlier) * BPS_PER_UNIT
        for earlier, later in zip(closes, closes[1:], strict=False)
    ]


# --- frozen constants -------------------------------------------------------


def test_frozen_constants_match_the_specification() -> None:
    assert FALLBACK_TAKER_FEE_BPS == 10.0
    assert SPREAD_ALLOWANCE_BPS == 2.0
    assert SLIPPAGE_VOL_COEFFICIENT == 0.05
    assert SLIPPAGE_FLOOR_BPS == 1.0
    assert SLIPPAGE_CAP_BPS == 15.0
    assert EWMA_HALF_LIFE_HOURS == 168
    assert VOLATILITY_INIT_RETURNS == 168
    assert STRESS_MULTIPLIERS == (1.0, 1.5, 2.0, 3.0)
    assert EXECUTION_DELAY_STRESS_BARS == 1


# --- returns ----------------------------------------------------------------


def test_hourly_log_returns_are_close_to_close_in_bps() -> None:
    closes = (100.0, 101.0, 99.5)
    series = _series_from_closes(closes)
    assert hourly_log_returns_bps(series) == pytest.approx(
        _expected_returns_bps(closes)
    )


def test_flat_prices_give_zero_returns() -> None:
    series = _series_from_closes((100.0, 100.0, 100.0, 100.0))
    assert hourly_log_returns_bps(series) == (0.0, 0.0, 0.0)


def test_returns_refuse_to_bridge_a_hole() -> None:
    series = _series_from_closes((100.0, 101.0, 102.0), hours=(0, 1, 3))
    with pytest.raises(CostModelError, match="missing"):
        hourly_log_returns_bps(series)


def test_returns_reject_a_non_hourly_series() -> None:
    daily = timedelta(days=1)
    bars = tuple(
        Bar(
            open_time=_ORIGIN + index * daily,
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.0,
            volume=1.0,
            interval=daily,
        )
        for index in range(3)
    )
    series = BarSeries(symbol="TESTUSDT", bars=bars, interval=daily)
    with pytest.raises(CostModelError, match="1:00:00 series"):
        hourly_log_returns_bps(series)


def test_returns_do_not_mutate_the_input_series() -> None:
    series = _series_from_closes((100.0, 101.0, 102.0))
    before = series.bars
    hourly_log_returns_bps(series)
    assert series.bars == before


# --- volatility -------------------------------------------------------------


def test_volatility_initialisation_is_the_sample_standard_deviation() -> None:
    returns = [1.0, -2.0, 3.0, -4.0, 5.0]
    series = ewma_hourly_volatility_bps_series(returns)
    assert len(series) == len(returns) - 1
    for index, estimate in enumerate(series):
        assert estimate == pytest.approx(statistics.stdev(returns[: index + 2]))


def test_volatility_at_exactly_168_returns_is_still_the_sample_deviation() -> None:
    returns = [float((-1) ** index * (index % 7 + 1)) for index in range(168)]
    assert ewma_hourly_volatility_bps(returns) == pytest.approx(
        statistics.stdev(returns)
    )


def test_volatility_switches_to_recursive_ewma_after_168_returns() -> None:
    returns = [float((-1) ** index * (index % 7 + 1)) for index in range(169)]
    decay = 0.5 ** (1.0 / EWMA_HALF_LIFE_HOURS)
    initial_variance = statistics.variance(returns[:168])
    expected = math.sqrt(
        decay * initial_variance + (1.0 - decay) * returns[168] ** 2,
    )
    assert ewma_hourly_volatility_bps(returns) == pytest.approx(expected)


def test_ewma_decay_halves_the_weight_after_one_half_life() -> None:
    quiet = [0.0] * VOLATILITY_INIT_RETURNS
    shocked = [*quiet, 100.0]
    decayed = [*shocked, *([0.0] * EWMA_HALF_LIFE_HOURS)]
    shocked_variance = ewma_hourly_volatility_bps(shocked) ** 2
    decayed_variance = ewma_hourly_volatility_bps(decayed) ** 2
    assert decayed_variance == pytest.approx(shocked_variance * 0.5)


def test_volatility_is_zero_for_a_flat_path() -> None:
    assert ewma_hourly_volatility_bps([0.0, 0.0, 0.0]) == 0.0


def test_volatility_requires_two_returns() -> None:
    with pytest.raises(CostModelError, match="at least 2 hourly returns"):
        ewma_hourly_volatility_bps([1.0])
    with pytest.raises(CostModelError, match="at least 2 hourly returns"):
        ewma_hourly_volatility_bps([])


def test_volatility_rejects_non_finite_returns() -> None:
    with pytest.raises(CostModelError, match=r"returns_bps\[1\]"):
        ewma_hourly_volatility_bps([1.0, math.nan, 2.0])
    with pytest.raises(CostModelError, match=r"returns_bps\[2\]"):
        ewma_hourly_volatility_bps([1.0, 2.0, math.inf])


def test_volatility_does_not_mutate_the_input_sequence() -> None:
    returns = [1.0, -2.0, 3.0]
    ewma_hourly_volatility_bps_series(returns)
    assert returns == [1.0, -2.0, 3.0]


# --- slippage ---------------------------------------------------------------


def test_slippage_is_linear_between_the_floor_and_the_cap() -> None:
    assert slippage_bps(100.0) == pytest.approx(5.0)
    assert slippage_bps(200.0) == pytest.approx(10.0)


def test_slippage_floor_applies_to_low_volatility() -> None:
    assert slippage_bps(0.0) == SLIPPAGE_FLOOR_BPS
    assert slippage_bps(19.999) == SLIPPAGE_FLOOR_BPS
    assert slippage_bps(20.0) == pytest.approx(SLIPPAGE_FLOOR_BPS)


def test_slippage_cap_applies_to_high_volatility() -> None:
    assert slippage_bps(300.0) == pytest.approx(SLIPPAGE_CAP_BPS)
    assert slippage_bps(1_000.0) == SLIPPAGE_CAP_BPS
    assert slippage_bps(1e9) == SLIPPAGE_CAP_BPS


def test_slippage_is_non_negative_and_monotone_in_volatility() -> None:
    sigmas = [0.0, 5.0, 19.0, 20.0, 21.0, 150.0, 299.0, 300.0, 500.0, 5_000.0]
    values = [slippage_bps(sigma) for sigma in sigmas]
    assert all(value >= 0.0 for value in values)
    assert all(
        later >= earlier for earlier, later in zip(values, values[1:], strict=False)
    )


def test_slippage_rejects_invalid_volatility() -> None:
    with pytest.raises(CostModelError, match="non-negative"):
        slippage_bps(-1.0)
    with pytest.raises(CostModelError, match="finite"):
        slippage_bps(math.nan)


# --- fees -------------------------------------------------------------------


def test_fee_falls_back_to_ten_bps_without_a_schedule() -> None:
    quote = resolve_taker_fee_bps(None, _ts(5))
    assert quote == FeeQuote(fee_bps=FALLBACK_TAKER_FEE_BPS, source="fallback")


def test_supplied_schedule_provides_the_point_in_time_fee() -> None:
    schedule = FeeSchedule(
        tiers=(
            FeeTier(effective_from=_ts(0), taker_fee_bps=7.5),
            FeeTier(effective_from=_ts(10), taker_fee_bps=4.0),
        )
    )
    assert resolve_taker_fee_bps(schedule, _ts(0)) == FeeQuote(7.5, "schedule")
    assert resolve_taker_fee_bps(schedule, _ts(9)) == FeeQuote(7.5, "schedule")
    assert resolve_taker_fee_bps(schedule, _ts(10)) == FeeQuote(4.0, "schedule")
    assert resolve_taker_fee_bps(schedule, _ts(99)) == FeeQuote(4.0, "schedule")


def test_timestamp_before_the_schedule_falls_back_and_says_so() -> None:
    schedule = FeeSchedule(tiers=(FeeTier(effective_from=_ts(10), taker_fee_bps=4.0),))
    quote = resolve_taker_fee_bps(schedule, _ts(9))
    assert quote == FeeQuote(fee_bps=FALLBACK_TAKER_FEE_BPS, source="fallback")


def test_fee_schedule_rejects_invalid_construction() -> None:
    with pytest.raises(CostModelError, match="at least one tier"):
        FeeSchedule(tiers=())
    with pytest.raises(CostModelError, match="strictly increasing"):
        FeeSchedule(
            tiers=(
                FeeTier(effective_from=_ts(10), taker_fee_bps=4.0),
                FeeTier(effective_from=_ts(1), taker_fee_bps=5.0),
            )
        )


def test_fee_tier_rejects_invalid_input() -> None:
    with pytest.raises(CostModelError, match="non-negative"):
        FeeTier(effective_from=_ts(0), taker_fee_bps=-1.0)
    with pytest.raises(BarSemanticsError, match="UTC-aware"):
        FeeTier(effective_from=datetime(2024, 1, 1), taker_fee_bps=1.0)


def test_fee_resolution_rejects_a_naive_timestamp() -> None:
    with pytest.raises(BarSemanticsError, match="UTC-aware"):
        resolve_taker_fee_bps(None, datetime(2024, 1, 1))


# --- per-side cost ----------------------------------------------------------


def test_per_side_total_is_fee_plus_spread_plus_slippage() -> None:
    breakdown = per_side_cost_bps(sigma_hourly_bps=100.0)
    assert breakdown.fee_bps == FALLBACK_TAKER_FEE_BPS
    assert breakdown.fee_source == "fallback"
    assert breakdown.spread_bps == SPREAD_ALLOWANCE_BPS
    assert breakdown.slippage_bps == pytest.approx(5.0)
    assert breakdown.base_total_bps == pytest.approx(17.0)
    assert breakdown.total_bps == pytest.approx(17.0)


def test_per_side_cost_uses_a_supplied_fee_quote() -> None:
    breakdown = per_side_cost_bps(
        sigma_hourly_bps=100.0, fee=FeeQuote(fee_bps=4.0, source="schedule")
    )
    assert breakdown.fee_source == "schedule"
    assert breakdown.base_total_bps == pytest.approx(11.0)


def test_cost_quote_converts_bps_to_notional() -> None:
    breakdown = per_side_cost_bps(sigma_hourly_bps=100.0)
    assert breakdown.cost_quote(1_000_000.0) == pytest.approx(1_700.0)
    assert breakdown.cost_quote(0.0) == 0.0
    with pytest.raises(CostModelError, match="notional_quote"):
        breakdown.cost_quote(-1.0)


@pytest.mark.parametrize("multiplier", STRESS_MULTIPLIERS)
def test_stress_multiplies_the_total_modeled_cost(multiplier: float) -> None:
    base = per_side_cost_bps(sigma_hourly_bps=100.0)
    stressed = per_side_cost_bps(sigma_hourly_bps=100.0, stress_multiplier=multiplier)
    assert stressed.fee_bps == base.fee_bps
    assert stressed.spread_bps == base.spread_bps
    assert stressed.slippage_bps == base.slippage_bps
    assert stressed.base_total_bps == pytest.approx(base.base_total_bps)
    assert stressed.total_bps == pytest.approx(base.base_total_bps * multiplier)


def test_unlisted_stress_multiplier_is_refused() -> None:
    for multiplier in (0.0, 1.25, 2.5, 4.0, -1.0):
        with pytest.raises(CostModelError, match="not one of the frozen"):
            per_side_cost_bps(sigma_hourly_bps=100.0, stress_multiplier=multiplier)


def test_per_side_cost_rejects_invalid_input() -> None:
    with pytest.raises(CostModelError, match="sigma_hourly_bps"):
        per_side_cost_bps(sigma_hourly_bps=-0.1)
    with pytest.raises(CostModelError, match="fee_bps"):
        per_side_cost_bps(
            sigma_hourly_bps=1.0, fee=FeeQuote(fee_bps=-1.0, source="schedule")
        )
    with pytest.raises(CostModelError, match="stress_multiplier"):
        per_side_cost_bps(sigma_hourly_bps=1.0, stress_multiplier=math.nan)


# --- execution resolution ---------------------------------------------------


def test_baseline_execution_is_the_next_bar_open() -> None:
    series = _series_from_closes((100.0, 101.0, 102.0, 103.0))
    point = resolve_execution(series, _ts(2))
    assert point.decision_time == _ts(2)
    assert point.execution_time == _ts(2)
    assert point.execution_price == series.bars[2].open


def test_delay_stress_shifts_the_fill_by_one_bar() -> None:
    series = _series_from_closes((100.0, 101.0, 102.0, 103.0))
    delayed = resolve_execution(series, _ts(2), delay_bars=EXECUTION_DELAY_STRESS_BARS)
    assert delayed.decision_time == _ts(2)
    assert delayed.execution_time == _ts(3)
    assert delayed.execution_price == series.bars[3].open


def test_delayed_execution_beyond_the_series_is_refused() -> None:
    series = _series_from_closes((100.0, 101.0, 102.0))
    with pytest.raises(CostModelError, match="unavailable"):
        resolve_execution(series, _ts(2), delay_bars=1)


def test_delayed_execution_across_a_hole_is_refused() -> None:
    series = _series_from_closes((100.0, 101.0, 102.0, 103.0), hours=(0, 1, 2, 4))
    with pytest.raises(CostModelError, match="unavailable"):
        resolve_execution(series, _ts(2), delay_bars=1)


def test_multi_bar_delay_across_a_hole_is_refused() -> None:
    series = _series_from_closes((100.0, 101.0, 102.0, 103.0), hours=(0, 1, 2, 4))
    with pytest.raises(CostModelError, match="crosses a hole"):
        resolve_execution(series, _ts(2), delay_bars=2)


def test_negative_delay_is_refused() -> None:
    series = _series_from_closes((100.0, 101.0, 102.0))
    with pytest.raises(CostModelError, match="delay_bars"):
        resolve_execution(series, _ts(1), delay_bars=-1)


# --- end-to-end trade cost --------------------------------------------------


def test_trade_cost_matches_an_independently_computed_expectation() -> None:
    closes = (100.0, 101.0, 100.5, 102.0, 101.0)
    series = _series_from_closes(closes)
    cost = trade_cost(series, _ts(4), Side.BUY)

    # A decision at close(4) may use closes 0..3 only; the first bar has no
    # predecessor, so four closes yield three hourly returns.
    expected_returns = _expected_returns_bps(closes[:4])
    expected_sigma = statistics.stdev(expected_returns)
    expected_slippage = min(15.0, max(1.0, 0.05 * expected_sigma))
    expected_total = FALLBACK_TAKER_FEE_BPS + SPREAD_ALLOWANCE_BPS + expected_slippage

    assert cost.decision_time == _ts(4)
    assert cost.execution_time == _ts(4)
    assert cost.execution_price == series.bars[4].open
    assert cost.side is Side.BUY
    assert cost.delay_bars == 0
    assert cost.returns_used == len(expected_returns)
    assert cost.breakdown.sigma_hourly_bps == pytest.approx(expected_sigma)
    assert cost.breakdown.slippage_bps == pytest.approx(expected_slippage)
    assert cost.breakdown.total_bps == pytest.approx(expected_total)


def test_trade_cost_uses_only_information_available_at_the_decision() -> None:
    """Appending later bars must not change a past decision's cost."""
    closes = _geometric_closes(12, 40.0)
    short = _series_from_closes(closes[:6])
    long = _series_from_closes((*closes, 999.0))
    assert trade_cost(short, _ts(5), Side.BUY).breakdown == trade_cost(
        long, _ts(5), Side.BUY
    ).breakdown


def test_trade_cost_is_deterministic_across_repeated_calls() -> None:
    series = _series_from_closes(_geometric_closes(200, 25.0))
    first = trade_cost(series, _ts(180), Side.SELL, stress_multiplier=2.0)
    second = trade_cost(series, _ts(180), Side.SELL, stress_multiplier=2.0)
    assert first == second


def test_trade_cost_applies_a_supplied_point_in_time_fee() -> None:
    series = _series_from_closes((100.0, 101.0, 100.5, 102.0, 101.0))
    schedule = FeeSchedule(tiers=(FeeTier(effective_from=_ts(0), taker_fee_bps=4.0),))
    cost = trade_cost(series, _ts(4), Side.BUY, fees=schedule)
    assert cost.breakdown.fee_bps == 4.0
    assert cost.breakdown.fee_source == "schedule"


def test_trade_cost_falls_back_when_the_schedule_starts_later() -> None:
    series = _series_from_closes((100.0, 101.0, 100.5, 102.0, 101.0))
    schedule = FeeSchedule(tiers=(FeeTier(effective_from=_ts(99), taker_fee_bps=4.0),))
    cost = trade_cost(series, _ts(4), Side.BUY, fees=schedule)
    assert cost.breakdown.fee_bps == FALLBACK_TAKER_FEE_BPS
    assert cost.breakdown.fee_source == "fallback"


def test_delay_stress_changes_only_the_fill_not_the_volatility() -> None:
    series = _series_from_closes(_geometric_closes(10, 30.0))
    baseline = trade_cost(series, _ts(5), Side.BUY)
    delayed = trade_cost(
        series, _ts(5), Side.BUY, delay_bars=EXECUTION_DELAY_STRESS_BARS
    )
    assert delayed.execution_time == baseline.execution_time + BAR_INTERVAL
    assert delayed.execution_price == series.bars[6].open
    assert delayed.breakdown == baseline.breakdown
    assert delayed.delay_bars == 1


def test_effective_price_is_worse_than_the_open_on_both_sides() -> None:
    series = _series_from_closes((100.0, 101.0, 100.5, 102.0, 101.0))
    buy = trade_cost(series, _ts(4), Side.BUY)
    sell = trade_cost(series, _ts(4), Side.SELL)
    raw = series.bars[4].open
    assert buy.effective_price > raw
    assert sell.effective_price < raw
    assert buy.effective_price - raw == pytest.approx(raw - sell.effective_price)
    assert buy.effective_price == pytest.approx(
        raw * (1.0 + buy.breakdown.total_bps / BPS_PER_UNIT)
    )


def test_trade_cost_scales_with_the_stress_multiplier() -> None:
    series = _series_from_closes(_geometric_closes(20, 30.0))
    base = trade_cost(series, _ts(10), Side.BUY)
    for multiplier in STRESS_MULTIPLIERS:
        stressed = trade_cost(series, _ts(10), Side.BUY, stress_multiplier=multiplier)
        assert stressed.breakdown.total_bps == pytest.approx(
            base.breakdown.base_total_bps * multiplier
        )
        assert stressed.cost_quote(10_000.0) == pytest.approx(
            base.cost_quote(10_000.0) * multiplier
        )


def test_trade_cost_refuses_a_decision_without_enough_history() -> None:
    series = _series_from_closes((100.0, 101.0, 102.0))
    with pytest.raises(CostModelError, match="contiguous bar"):
        trade_cost(series, _ts(1), Side.BUY)


def test_trade_cost_refuses_history_truncated_by_a_hole() -> None:
    series = _series_from_closes(
        (100.0, 101.0, 102.0, 103.0, 104.0), hours=(0, 1, 3, 4, 5)
    )
    with pytest.raises(CostModelError, match="contiguous bar"):
        trade_cost(series, _ts(4), Side.BUY)


def test_trade_cost_refuses_a_final_bar_decision() -> None:
    series = _series_from_closes((100.0, 101.0, 102.0, 103.0))
    with pytest.raises(CostModelError, match="final bar close"):
        trade_cost(series, _ts(4), Side.BUY)


def test_trade_cost_refuses_an_unknown_decision_timestamp() -> None:
    series = _series_from_closes((100.0, 101.0, 102.0, 103.0))
    with pytest.raises(CostModelError, match="no bar with open_time"):
        trade_cost(series, _ts(99), Side.BUY)


def test_trade_cost_refuses_a_misaligned_decision_timestamp() -> None:
    series = _series_from_closes((100.0, 101.0, 102.0, 103.0))
    with pytest.raises(CostModelError, match="not aligned"):
        trade_cost(series, _ts(2) + timedelta(minutes=30), Side.BUY)


def test_trade_cost_refuses_a_non_side_argument() -> None:
    series = _series_from_closes((100.0, 101.0, 102.0, 103.0))
    with pytest.raises(CostModelError, match="side must be a Side"):
        trade_cost(series, _ts(3), "buy")  # type: ignore[arg-type]


def test_trade_cost_does_not_mutate_the_series() -> None:
    series = _series_from_closes((100.0, 101.0, 100.5, 102.0, 101.0))
    snapshot = series.bars
    trade_cost(series, _ts(4), Side.BUY, stress_multiplier=3.0)
    assert series.bars == snapshot
    assert series.bars is snapshot
