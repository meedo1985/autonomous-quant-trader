"""Synthetic feature-factory tests. No real market data, no network access.

Every expectation is computed independently inside this file, from the closed
form of the synthetic price path or from a hand-written loop, never by calling
the implementation a second time.
"""

import math
import statistics
from datetime import UTC, datetime, timedelta, timezone
from functools import cache

import pytest

from aqt.backtest.costs import ewma_hourly_volatility_bps
from aqt.data.bars import BAR_INTERVAL, Bar, BarSemanticsError, BarSeries
from aqt.features.factory import (
    ANNUALIZATION_HOURS,
    ATR_WINDOW,
    BREAKOUT_WINDOW,
    EMA_SPANS,
    EWMA_VOL_HALF_LIFE_HOURS,
    FEATURE_NAMES,
    FORBIDDEN_INPUT_KINDS,
    REQUIRED_HISTORY_BARS,
    RETURN_LAGS,
    RV_WINDOWS,
    SMA_WINDOW,
    FeatureFactoryError,
    FeatureRow,
    average_true_range,
    compute_feature_rows,
    compute_features,
    ewma_volatility,
    exponential_moving_average,
    hourly_log_returns,
    log_return,
    realized_volatility,
    require_cycle1_features,
    rolling_maximum,
    simple_moving_average,
    true_range,
)

_ORIGIN = datetime(2024, 1, 1, tzinfo=UTC)
_SERIES_BARS = 5000
_DECISION_HOUR = _SERIES_BARS - 1
_SYMBOL = "TESTUSDT"
_APPROX = {"rel": 1e-12, "abs": 1e-15}


def _ts(hour: int) -> datetime:
    return _ORIGIN + timedelta(hours=hour)


def _decision(hour: int) -> datetime:
    """Close timestamp of the bar opening at `hour`."""
    return _ts(hour + 1)


def _close_at(hour: int) -> float:
    """A deterministic, strictly positive synthetic close. No randomness."""
    return 100.0 * math.exp(0.00002 * hour + 0.02 * math.sin(hour / 13.0))


def _bar_at(
    hour: int, *, volume: float | None = None, origin: datetime = _ORIGIN
) -> Bar:
    close = _close_at(hour)
    open_ = _close_at(hour - 1)
    high = max(open_, close) * 1.003
    low = min(open_, close) * 0.997
    resolved_volume = 1.0 + (hour % 7)
    if volume is not None:
        resolved_volume = volume
    return Bar(
        open_time=origin + timedelta(hours=hour),
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=resolved_volume,
    )


def _series(
    first_hour: int,
    count: int,
    *,
    symbol: str = _SYMBOL,
    volume: float | None = None,
    origin: datetime = _ORIGIN,
) -> BarSeries:
    bars = tuple(
        _bar_at(hour, volume=volume, origin=origin)
        for hour in range(first_hour, first_hour + count)
    )
    return BarSeries(symbol=symbol, bars=bars)


@cache
def _base_series() -> BarSeries:
    return _series(0, _SERIES_BARS)


@cache
def _base_row() -> FeatureRow:
    return compute_features(_base_series(), _decision(_DECISION_HOUR))


def _history_closes(decision_hour: int = _DECISION_HOUR) -> tuple[float, ...]:
    """Closes observable at the decision, straight from the closed form."""
    return tuple(_close_at(hour) for hour in range(0, decision_hour + 1))


def _history_returns(decision_hour: int = _DECISION_HOUR) -> tuple[float, ...]:
    closes = _history_closes(decision_hour)
    return tuple(
        math.log(later / earlier)
        for earlier, later in zip(closes, closes[1:], strict=False)
    )


def _flat_series(count: int = REQUIRED_HISTORY_BARS + 1) -> BarSeries:
    bars = tuple(
        Bar(
            open_time=_ts(hour),
            open=100.0,
            high=100.0,
            low=100.0,
            close=100.0,
            volume=3.0,
        )
        for hour in range(count)
    )
    return BarSeries(symbol=_SYMBOL, bars=bars)


# --- independent reference implementations -------------------------------


def _independent_mean(values: tuple[float, ...]) -> float:
    total = 0.0
    for value in values:
        total += value
    return total / len(values)


def _independent_stdev(values: tuple[float, ...]) -> float:
    mean = _independent_mean(values)
    squared = 0.0
    for value in values:
        squared += (value - mean) ** 2
    return math.sqrt(squared / (len(values) - 1))


def _independent_ema(values: tuple[float, ...], span: int) -> float:
    alpha = 2.0 / (span + 1.0)
    state = _independent_mean(values[:span])
    for value in values[span:]:
        state = alpha * value + (1.0 - alpha) * state
    return state


def _independent_ewma_vol(returns: tuple[float, ...]) -> float:
    decay = 0.5 ** (1.0 / 168.0)
    variance = _independent_stdev(returns[:168]) ** 2
    for value in returns[168:]:
        variance = decay * variance + (1.0 - decay) * value * value
    return math.sqrt(variance) * math.sqrt(8760.0)


def _independent_true_range(bar: Bar, previous_close: float) -> float:
    return max(
        bar.high - bar.low,
        abs(bar.high - previous_close),
        abs(bar.low - previous_close),
    )


# --- frozen constants -----------------------------------------------------


def test_feature_names_are_exactly_the_frozen_cycle1_set() -> None:
    assert FEATURE_NAMES == (
        "ret_1h",
        "ret_24h",
        "ret_72h",
        "ret_168h",
        "ema_24",
        "ema_72",
        "ema_168",
        "ema_dist_24",
        "ema_dist_72",
        "ema_dist_168",
        "sma_4800",
        "trend_200d",
        "breakout_720",
        "rv_24",
        "rv_168",
        "rv_720",
        "ewma_vol_168h",
        "atr_24",
    )
    assert len(set(FEATURE_NAMES)) == len(FEATURE_NAMES) == 18


def test_frozen_windows_match_the_specification() -> None:
    assert RETURN_LAGS == (1, 24, 72, 168)
    assert EMA_SPANS == (24, 72, 168)
    assert SMA_WINDOW == 4800
    assert BREAKOUT_WINDOW == 720
    assert RV_WINDOWS == (24, 168, 720)
    assert ATR_WINDOW == 24
    assert EWMA_VOL_HALF_LIFE_HOURS == 168
    assert ANNUALIZATION_HOURS == 8760


def test_required_history_is_the_binding_sma_window() -> None:
    assert REQUIRED_HISTORY_BARS == SMA_WINDOW == 4800


# --- formulas against independent calculations ----------------------------


@pytest.mark.parametrize("lag", RETURN_LAGS)
def test_log_returns_match_an_independent_calculation(lag: int) -> None:
    closes = _history_closes()
    expected = math.log(closes[-1] / closes[-1 - lag])
    assert getattr(_base_row(), f"ret_{lag}h") == pytest.approx(expected, **_APPROX)


@pytest.mark.parametrize("span", EMA_SPANS)
def test_ema_matches_an_independent_recursion(span: int) -> None:
    expected = _independent_ema(_history_closes(), span)
    assert getattr(_base_row(), f"ema_{span}") == pytest.approx(expected, **_APPROX)


@pytest.mark.parametrize("span", EMA_SPANS)
def test_ema_distance_matches_an_independent_calculation(span: int) -> None:
    closes = _history_closes()
    expected = closes[-1] / _independent_ema(closes, span) - 1.0
    assert getattr(_base_row(), f"ema_dist_{span}") == pytest.approx(
        expected, **_APPROX
    )


def test_sma_4800_matches_an_independent_mean() -> None:
    expected = _independent_mean(_history_closes()[-SMA_WINDOW:])
    assert _base_row().sma_4800 == pytest.approx(expected, **_APPROX)


def test_trend_200d_matches_an_independent_calculation() -> None:
    closes = _history_closes()
    expected = closes[-1] / _independent_mean(closes[-SMA_WINDOW:]) - 1.0
    assert _base_row().trend_200d == pytest.approx(expected, **_APPROX)


def test_breakout_720_matches_an_independent_rolling_maximum() -> None:
    closes = _history_closes()
    expected = closes[-1] / max(closes[-BREAKOUT_WINDOW:]) - 1.0
    assert _base_row().breakout_720 == pytest.approx(expected, **_APPROX)


@pytest.mark.parametrize("window", RV_WINDOWS)
def test_realized_volatility_matches_an_independent_calculation(window: int) -> None:
    returns = _history_returns()[-window:]
    expected = _independent_stdev(returns) * math.sqrt(8760.0)
    assert getattr(_base_row(), f"rv_{window}") == pytest.approx(expected, **_APPROX)


def test_ewma_vol_168h_matches_an_independent_recursion() -> None:
    expected = _independent_ewma_vol(_history_returns())
    assert _base_row().ewma_vol_168h == pytest.approx(expected, **_APPROX)


def test_ewma_vol_168h_is_the_task3_estimator_exactly() -> None:
    returns = _history_returns()
    sigma_bps = ewma_hourly_volatility_bps(tuple(value * 10_000.0 for value in returns))
    assert ewma_volatility(returns) == (sigma_bps / 10_000.0) * math.sqrt(8760.0)


def test_atr_24_matches_an_independent_true_range_average() -> None:
    bars = _base_series().bars[: _DECISION_HOUR + 1]
    ranges = tuple(
        _independent_true_range(bars[index], bars[index - 1].close)
        for index in range(len(bars) - ATR_WINDOW, len(bars))
    )
    expected = _independent_mean(ranges) / bars[-1].close
    assert _base_row().atr_24 == pytest.approx(expected, **_APPROX)


def test_row_reports_its_decision_timestamp_and_history_depth() -> None:
    row = _base_row()
    assert row.symbol == _SYMBOL
    assert row.decision_time == _decision(_DECISION_HOUR)
    assert row.decision_time == _base_series().bars[_DECISION_HOUR].close_time
    assert row.close == _close_at(_DECISION_HOUR)
    assert row.history_bars == _DECISION_HOUR + 1


def test_as_dict_exposes_exactly_the_frozen_feature_values() -> None:
    values = _base_row().as_dict()
    assert tuple(values) == FEATURE_NAMES
    assert all(math.isfinite(value) for value in values.values())
    assert "symbol" not in values
    assert "history_bars" not in values


# --- helper formulas on small hand-checked inputs -------------------------


def test_log_return_is_the_natural_log_of_the_price_ratio() -> None:
    assert log_return(110.0, 100.0) == pytest.approx(math.log(1.1), **_APPROX)
    assert log_return(100.0, 100.0) == 0.0


@pytest.mark.parametrize("bad", [0.0, -1.0, float("nan"), float("inf")])
def test_log_return_rejects_non_positive_or_non_finite_prices(bad: float) -> None:
    with pytest.raises(FeatureFactoryError):
        log_return(bad, 100.0)
    with pytest.raises(FeatureFactoryError):
        log_return(100.0, bad)


def test_simple_moving_average_uses_only_the_trailing_window() -> None:
    assert simple_moving_average([1.0, 2.0, 3.0, 4.0], 2) == pytest.approx(3.5)
    assert simple_moving_average([1.0, 2.0, 3.0, 4.0], 4) == pytest.approx(2.5)


def test_exponential_moving_average_matches_a_hand_computation() -> None:
    closes = (10.0, 20.0, 30.0)
    alpha = 2.0 / 3.0
    seed = 15.0
    expected = alpha * 30.0 + (1.0 - alpha) * seed
    assert exponential_moving_average(closes, 2) == pytest.approx(expected, **_APPROX)


def test_exponential_moving_average_of_a_constant_series_is_that_constant() -> None:
    assert exponential_moving_average([50.0] * 100, 24) == pytest.approx(50.0)


def test_rolling_maximum_uses_only_the_trailing_window() -> None:
    assert rolling_maximum([9.0, 1.0, 2.0, 3.0], 3) == 3.0
    assert rolling_maximum([9.0, 1.0, 2.0, 3.0], 4) == 9.0


def test_realized_volatility_matches_a_hand_computed_sample_stdev() -> None:
    returns = (0.01, -0.01, 0.02, -0.02)
    expected = statistics.stdev(returns) * math.sqrt(8760.0)
    assert realized_volatility(returns, 4) == pytest.approx(expected, **_APPROX)
    assert realized_volatility(returns, 4) == pytest.approx(
        _independent_stdev(returns) * math.sqrt(8760.0), **_APPROX
    )


def test_realized_volatility_of_constant_returns_is_zero() -> None:
    assert realized_volatility([0.001] * 24, 24) == 0.0


def test_true_range_selects_each_of_its_three_candidates() -> None:
    bar = _bar_at(500)
    assert true_range(bar, bar.close) == pytest.approx(bar.high - bar.low)
    gap_down_previous = bar.low * 0.5
    assert true_range(bar, gap_down_previous) == pytest.approx(
        bar.high - gap_down_previous
    )
    gap_up_previous = bar.high * 2.0
    assert true_range(bar, gap_up_previous) == pytest.approx(gap_up_previous - bar.low)


def test_average_true_range_matches_a_hand_computation() -> None:
    bars = tuple(_bar_at(hour) for hour in range(100, 104))
    expected = _independent_mean(
        tuple(
            _independent_true_range(bars[index], bars[index - 1].close)
            for index in range(1, 4)
        )
    )
    assert average_true_range(bars, 3) == pytest.approx(expected, **_APPROX)


def test_hourly_log_returns_match_an_independent_calculation() -> None:
    bars = tuple(_bar_at(hour) for hour in range(200, 206))
    expected = tuple(
        math.log(bars[index].close / bars[index - 1].close)
        for index in range(1, len(bars))
    )
    assert hourly_log_returns(bars) == pytest.approx(expected, **_APPROX)


# --- causality and no future leakage --------------------------------------


def test_row_is_unchanged_when_the_series_is_truncated_at_the_decision_bar() -> None:
    decision_hour = 4_800
    full = compute_features(_base_series(), _decision(decision_hour))
    truncated = compute_features(
        _series(0, decision_hour + 1), _decision(decision_hour)
    )
    assert full == truncated


def test_future_bars_cannot_change_an_already_computed_row() -> None:
    decision_hour = 4_799
    base = _series(0, decision_hour + 1)
    baseline = compute_features(base, _decision(decision_hour))
    extended_bars = list(base.bars)
    for hour in range(decision_hour + 1, decision_hour + 25):
        close = _close_at(hour) * 10.0
        extended_bars.append(
            Bar(
                open_time=_ts(hour),
                open=close,
                high=close * 1.5,
                low=close * 0.5,
                close=close,
                volume=99.0,
            )
        )
    extended = BarSeries(symbol=_SYMBOL, bars=tuple(extended_bars))
    assert compute_features(extended, _decision(decision_hour)) == baseline


def test_a_hole_after_the_decision_bar_does_not_affect_the_row() -> None:
    decision_hour = 4_799
    base = _series(0, decision_hour + 1)
    baseline = compute_features(base, _decision(decision_hour))
    later = (_bar_at(decision_hour + 5), _bar_at(decision_hour + 6))
    gapped = BarSeries(symbol=_SYMBOL, bars=base.bars + later)
    assert compute_features(gapped, _decision(decision_hour)) == baseline


def test_the_decision_bar_itself_is_included_in_the_history() -> None:
    earlier = compute_features(_base_series(), _decision(_DECISION_HOUR - 1))
    later = _base_row()
    assert later.history_bars == earlier.history_bars + 1
    assert later.close == _close_at(_DECISION_HOUR)
    assert earlier.close == _close_at(_DECISION_HOUR - 1)


def test_ret_1h_of_the_next_decision_uses_the_previous_close() -> None:
    row = _base_row()
    expected = math.log(_close_at(_DECISION_HOUR) / _close_at(_DECISION_HOUR - 1))
    assert row.ret_1h == pytest.approx(expected, **_APPROX)


# --- warm-up and insufficient history -------------------------------------


def test_exactly_the_required_history_is_accepted() -> None:
    series = _series(0, REQUIRED_HISTORY_BARS)
    row = compute_features(series, _decision(REQUIRED_HISTORY_BARS - 1))
    assert row.history_bars == REQUIRED_HISTORY_BARS


def test_one_bar_short_of_the_required_history_is_rejected() -> None:
    series = _series(0, REQUIRED_HISTORY_BARS - 1)
    with pytest.raises(FeatureFactoryError) as error:
        compute_features(series, _decision(REQUIRED_HISTORY_BARS - 2))
    assert str(REQUIRED_HISTORY_BARS) in str(error.value)
    assert "4799 bar(s) of history" in str(error.value)


def test_an_early_decision_inside_a_long_series_is_rejected() -> None:
    with pytest.raises(FeatureFactoryError):
        compute_features(_base_series(), _decision(100))


@pytest.mark.parametrize("span", EMA_SPANS)
def test_ema_rejects_a_history_shorter_than_its_span(span: int) -> None:
    with pytest.raises(FeatureFactoryError):
        exponential_moving_average([100.0] * (span - 1), span)


def test_sma_rejects_a_history_shorter_than_its_window() -> None:
    with pytest.raises(FeatureFactoryError):
        simple_moving_average([100.0] * (SMA_WINDOW - 1), SMA_WINDOW)


@pytest.mark.parametrize("window", RV_WINDOWS)
def test_realized_volatility_rejects_a_short_window(window: int) -> None:
    with pytest.raises(FeatureFactoryError):
        realized_volatility([0.001] * (window - 1), window)


def test_ewma_volatility_rejects_an_incomplete_initialisation() -> None:
    with pytest.raises(FeatureFactoryError) as error:
        ewma_volatility([0.001] * 167)
    assert "168" in str(error.value)


def test_average_true_range_rejects_too_few_bars() -> None:
    bars = tuple(_bar_at(hour) for hour in range(300, 300 + ATR_WINDOW))
    with pytest.raises(FeatureFactoryError):
        average_true_range(bars, ATR_WINDOW)


def test_rolling_maximum_rejects_a_short_history() -> None:
    with pytest.raises(FeatureFactoryError):
        rolling_maximum([100.0] * (BREAKOUT_WINDOW - 1), BREAKOUT_WINDOW)


# --- gaps, duplicates, and invalid bars -----------------------------------


def test_a_hole_in_the_history_is_rejected_not_bridged() -> None:
    hours = [hour for hour in range(0, _SERIES_BARS) if hour != 2_000]
    bars = tuple(_bar_at(hour) for hour in hours)
    series = BarSeries(symbol=_SYMBOL, bars=bars)
    with pytest.raises(FeatureFactoryError) as error:
        compute_features(series, _decision(_DECISION_HOUR))
    assert "contiguous" in str(error.value)


def test_a_hole_immediately_before_the_decision_bar_is_rejected() -> None:
    hours = [hour for hour in range(0, _SERIES_BARS) if hour != _DECISION_HOUR - 1]
    series = BarSeries(symbol=_SYMBOL, bars=tuple(_bar_at(hour) for hour in hours))
    with pytest.raises(FeatureFactoryError):
        compute_features(series, _decision(_DECISION_HOUR))


def test_hourly_log_returns_are_never_computed_across_a_hole() -> None:
    bars = (_bar_at(10), _bar_at(11), _bar_at(13))
    with pytest.raises(FeatureFactoryError):
        hourly_log_returns(bars)


def test_duplicate_open_times_are_rejected_by_bar_semantics() -> None:
    with pytest.raises(BarSemanticsError):
        BarSeries(symbol=_SYMBOL, bars=(_bar_at(5), _bar_at(5)))


def test_an_inconsistent_ohlc_bar_is_rejected_by_bar_semantics() -> None:
    with pytest.raises(BarSemanticsError):
        Bar(
            open_time=_ts(1),
            open=100.0,
            high=99.0,
            low=95.0,
            close=98.0,
            volume=1.0,
        )


def test_a_naive_decision_timestamp_is_rejected() -> None:
    naive = _decision(_DECISION_HOUR).replace(tzinfo=None)
    with pytest.raises(FeatureFactoryError):
        compute_features(_base_series(), naive)


def test_a_non_utc_decision_timestamp_is_rejected() -> None:
    shifted = _decision(_DECISION_HOUR).astimezone(timezone(timedelta(hours=3)))
    with pytest.raises(FeatureFactoryError):
        compute_features(_base_series(), shifted)


def test_an_unaligned_decision_timestamp_is_rejected() -> None:
    unaligned = _decision(_DECISION_HOUR) + timedelta(minutes=30)
    with pytest.raises(FeatureFactoryError):
        compute_features(_base_series(), unaligned)


def test_a_decision_timestamp_outside_the_series_is_rejected() -> None:
    with pytest.raises(FeatureFactoryError):
        compute_features(_base_series(), _decision(_SERIES_BARS + 10))


def test_a_non_hourly_series_is_rejected() -> None:
    interval = timedelta(minutes=15)
    bars = tuple(
        Bar(
            open_time=_ORIGIN + index * interval,
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.5,
            volume=1.0,
            interval=interval,
        )
        for index in range(10)
    )
    series = BarSeries(symbol=_SYMBOL, bars=bars, interval=interval)
    with pytest.raises(FeatureFactoryError) as error:
        compute_features(series, _ORIGIN + 10 * interval)
    assert "1:00:00" in str(error.value)


# --- determinism and purity -----------------------------------------------


def test_repeated_computation_is_bit_identical() -> None:
    series = _base_series()
    first = compute_features(series, _decision(_DECISION_HOUR))
    second = compute_features(series, _decision(_DECISION_HOUR))
    assert first == second
    assert first.as_dict() == second.as_dict()


def test_an_independently_rebuilt_series_produces_an_identical_row() -> None:
    rebuilt = _series(0, _SERIES_BARS)
    assert compute_features(rebuilt, _decision(_DECISION_HOUR)) == _base_row()


def test_rows_do_not_depend_on_the_order_they_are_requested_in() -> None:
    first, second = _decision(4_850), _decision(4_900)
    forward = compute_feature_rows(_base_series(), (first, second))
    backward = compute_feature_rows(_base_series(), (second, first))
    assert forward[0] == backward[1]
    assert forward[1] == backward[0]


def test_compute_feature_rows_preserves_the_requested_order() -> None:
    times = (_decision(4_900), _decision(4_850), _decision(4_999))
    rows = compute_feature_rows(_base_series(), times)
    assert tuple(row.decision_time for row in rows) == times


def test_the_input_series_is_not_mutated() -> None:
    series = _series(0, REQUIRED_HISTORY_BARS)
    before = series.bars
    compute_features(series, _decision(REQUIRED_HISTORY_BARS - 1))
    assert series.bars is before
    assert series.bars == before


# --- forbidden inputs -----------------------------------------------------


def test_volume_is_never_an_input_to_any_feature() -> None:
    zero_volume = _series(0, _SERIES_BARS, volume=0.0)
    huge_volume = _series(0, _SERIES_BARS, volume=1e9)
    left = compute_features(zero_volume, _decision(_DECISION_HOUR))
    right = compute_features(huge_volume, _decision(_DECISION_HOUR))
    assert left.as_dict() == right.as_dict()
    assert left.as_dict() == _base_row().as_dict()


def test_no_calendar_or_seasonality_term_enters_any_feature() -> None:
    shifted_origin = _ORIGIN + timedelta(hours=4_321)
    shifted = _series(0, _SERIES_BARS, origin=shifted_origin)
    row = compute_features(shifted, shifted_origin + timedelta(hours=_SERIES_BARS))
    assert row.decision_time != _base_row().decision_time
    assert row.as_dict() == _base_row().as_dict()


def test_feature_row_declares_no_forbidden_field() -> None:
    fields = set(FeatureRow.__dataclass_fields__)
    for forbidden in FORBIDDEN_INPUT_KINDS:
        assert not any(forbidden in name.lower() for name in fields)


def test_require_cycle1_features_accepts_the_frozen_set() -> None:
    assert require_cycle1_features(FEATURE_NAMES) == FEATURE_NAMES
    assert require_cycle1_features(()) == ()


@pytest.mark.parametrize(
    ("name", "family"),
    [
        ("volume_zscore_24", "volume"),
        ("quote_volume_168", "quote_volume"),
        ("trade_count_24", "trade_count"),
        ("spread_bps_24", "spread"),
        ("order_book_imbalance", "order_book"),
        ("depth_5bps", "depth"),
        ("trade_imbalance_1h", "trade_imbalance"),
        ("order_flow_toxicity", "order_flow"),
        ("seasonality_weekly", "seasonality"),
        ("hour_of_day_sin", "hour_of_day"),
        ("day_of_week_dummy", "day_of_week"),
        ("month_of_year_effect", "month_of_year"),
    ],
)
def test_require_cycle1_features_rejects_forbidden_families(
    name: str, family: str
) -> None:
    with pytest.raises(FeatureFactoryError) as error:
        require_cycle1_features([name])
    assert family in str(error.value)
    assert "FEATURE_FACTORY_v1" in str(error.value)


def test_require_cycle1_features_rejects_an_unknown_name() -> None:
    with pytest.raises(FeatureFactoryError) as error:
        require_cycle1_features(["ret_12h"])
    assert "not a frozen Cycle-1 feature" in str(error.value)


def test_require_cycle1_features_rejects_a_forbidden_name_in_a_valid_batch() -> None:
    with pytest.raises(FeatureFactoryError):
        require_cycle1_features(["ret_1h", "volume_ma_24", "rv_24"])


# --- analytic identities ---------------------------------------------------


def test_a_constant_price_series_produces_the_analytic_zero_row() -> None:
    series = _flat_series()
    row = compute_features(series, _decision(REQUIRED_HISTORY_BARS))
    for lag in RETURN_LAGS:
        assert getattr(row, f"ret_{lag}h") == 0.0
    for span in EMA_SPANS:
        assert getattr(row, f"ema_{span}") == pytest.approx(100.0, rel=1e-12)
        assert getattr(row, f"ema_dist_{span}") == pytest.approx(0.0, abs=1e-12)
    assert row.sma_4800 == pytest.approx(100.0, rel=1e-12)
    assert row.trend_200d == pytest.approx(0.0, abs=1e-12)
    assert row.breakout_720 == 0.0
    for window in RV_WINDOWS:
        assert getattr(row, f"rv_{window}") == 0.0
    assert row.ewma_vol_168h == 0.0
    assert row.atr_24 == 0.0


def test_breakout_is_never_positive_and_is_zero_at_a_new_high() -> None:
    assert _base_row().breakout_720 <= 0.0
    rising = BarSeries(
        symbol=_SYMBOL,
        bars=tuple(
            Bar(
                open_time=_ts(hour),
                open=100.0 + hour,
                high=101.0 + hour,
                low=99.0 + hour,
                close=100.0 + hour,
                volume=1.0,
            )
            for hour in range(REQUIRED_HISTORY_BARS + 1)
        ),
    )
    row = compute_features(rising, _decision(REQUIRED_HISTORY_BARS))
    assert row.breakout_720 == 0.0
    for lag in RETURN_LAGS:
        assert getattr(row, f"ret_{lag}h") > 0.0
    for span in EMA_SPANS:
        assert getattr(row, f"ema_dist_{span}") > 0.0
    assert row.trend_200d > 0.0


def test_volatility_features_are_non_negative() -> None:
    row = _base_row()
    assert row.rv_24 >= 0.0
    assert row.rv_168 >= 0.0
    assert row.rv_720 >= 0.0
    assert row.ewma_vol_168h >= 0.0
    assert row.atr_24 >= 0.0


def test_every_feature_is_finite_on_the_synthetic_path() -> None:
    assert all(math.isfinite(value) for value in _base_row().as_dict().values())
    assert len(_base_row().as_dict()) == len(FEATURE_NAMES)


def test_the_bar_interval_used_is_the_frozen_one_hour() -> None:
    assert BAR_INTERVAL == timedelta(hours=1)
    assert _base_series().interval == BAR_INTERVAL
