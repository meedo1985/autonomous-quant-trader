"""Synthetic canonical-benchmark tests. No real market data, no network access.

Every expectation is computed independently inside this file, from the closed
form of the synthetic price path or from a hand-written loop, never by calling
the implementation a second time.
"""

import math
import statistics
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime, timedelta, timezone
from functools import cache

import pytest

from aqt.backtest.costs import EWMA_HALF_LIFE_HOURS, VOLATILITY_INIT_RETURNS
from aqt.benchmarks import canonical
from aqt.benchmarks.canonical import (
    ANNUALIZATION_HOURS,
    BENCHMARK_SET,
    HOURS_PER_DAY,
    MAX_EXPOSURE,
    MIN_EXPOSURE,
    MINIMUM_HOLD_FOR_RISK_INCREASE,
    MINIMUM_HOLD_HOURS_FOR_RISK_INCREASE,
    PROMOTION_BENCHMARK,
    REBALANCE_BAND_ABSOLUTE,
    REBALANCE_BAND_TOLERANCE,
    REQUIRED_HISTORY_BARS,
    REQUIRED_HISTORY_BARS_BY_BENCHMARK,
    SCHEDULED_DECISION_ANCHOR_HOUR_UTC,
    SIGNAL_LABELS,
    TREND_SMA_DAYS,
    TREND_SMA_WINDOW,
    TSMOM_LOOKBACK_DAYS,
    TSMOM_LOOKBACK_HOURS,
    VOL_TARGET_ANNUALIZED,
    VOL_TARGET_HALF_LIFE_HOURS,
    BenchmarkId,
    BenchmarkSignal,
    CanonicalBenchmarkError,
    ExposureState,
    RebalanceAction,
    annualized_forecast_volatility,
    benchmark_signal,
    benchmark_signals,
    buy_and_hold_exposure,
    canonical_trend_exposure,
    canonical_tsmom_exposure,
    cash_exposure,
    is_scheduled_decision,
    reaches_rebalance_band,
    rebalance,
    require_canonical_benchmark,
    trend_reference,
    tsmom_lookback_return,
    vol_target_exposure,
)
from aqt.data.bars import BAR_INTERVAL, Bar, BarSemanticsError, BarSeries
from aqt.features.factory import SMA_WINDOW, ewma_volatility, hourly_log_returns

_ORIGIN = datetime(2024, 1, 1, tzinfo=UTC)
_SERIES_BARS = 5000
_LAST = _SERIES_BARS - 1
_SYMBOL = "TESTUSDT"
_APPROX = {"rel": 1e-12, "abs": 1e-15}
_BPS_PER_UNIT = 10_000.0

_Closes = Callable[[int], float]
_Path = Callable[[], BarSeries]


def _ts(hour: int, origin: datetime = _ORIGIN) -> datetime:
    return origin + timedelta(hours=hour)


def _decision(hour: int, origin: datetime = _ORIGIN) -> datetime:
    """Close timestamp of the bar opening at `hour`."""
    return _ts(hour + 1, origin)


def _close_at(hour: int) -> float:
    """A deterministic, strictly positive synthetic close. No randomness."""
    return 100.0 * math.exp(0.00002 * hour + 0.02 * math.sin(hour / 13.0))


def _rising_close(hour: int) -> float:
    return 100.0 * math.exp(0.0001 * hour)


def _falling_close(hour: int) -> float:
    return 100.0 * math.exp(-0.0001 * hour)


def _flat_close(hour: int) -> float:
    return 100.0 + 0.0 * hour


def _volatile_close(hour: int) -> float:
    return 100.0 * math.exp(0.02 * math.sin(hour))


def _bar_from(
    closes: _Closes,
    hour: int,
    volume: float | None = None,
    origin: datetime = _ORIGIN,
) -> Bar:
    close = closes(hour)
    opened = closes(hour - 1)
    resolved = 1.0 + (hour % 7) if volume is None else volume
    return Bar(
        open_time=origin + timedelta(hours=hour),
        open=opened,
        high=max(opened, close) * 1.003,
        low=min(opened, close) * 0.997,
        close=close,
        volume=resolved,
    )


def _series(
    first_hour: int,
    count: int,
    closes: _Closes = _close_at,
    volume: float | None = None,
    origin: datetime = _ORIGIN,
) -> BarSeries:
    bars = tuple(
        _bar_from(closes, hour, volume, origin)
        for hour in range(first_hour, first_hour + count)
    )
    return BarSeries(symbol=_SYMBOL, bars=bars)


def _extreme_bar(hour: int) -> Bar:
    """A wildly out-of-scale bar, used only after a decision timestamp."""
    return Bar(
        open_time=_ts(hour),
        open=1.0,
        high=100_000.0,
        low=0.5,
        close=100_000.0,
        volume=1.0,
    )


@cache
def _base_series() -> BarSeries:
    return _series(0, _SERIES_BARS)


@cache
def _rising_series() -> BarSeries:
    return _series(0, _SERIES_BARS, _rising_close)


@cache
def _falling_series() -> BarSeries:
    return _series(0, _SERIES_BARS, _falling_close)


@cache
def _flat_series() -> BarSeries:
    return _series(0, _SERIES_BARS, _flat_close)


@cache
def _volatile_series() -> BarSeries:
    return _series(0, 400, _volatile_close)


_PATHS: tuple[_Path, ...] = (
    _base_series,
    _rising_series,
    _falling_series,
    _flat_series,
)


def _sig(bench: BenchmarkId, hour: int) -> BenchmarkSignal:
    """Evaluate `bench` on the shared synthetic series at bar `hour`."""
    return benchmark_signal(bench, _base_series(), _decision(hour))


def _sig_on(bench: BenchmarkId, series: BarSeries, hour: int) -> BenchmarkSignal:
    return benchmark_signal(bench, series, _decision(hour))


def _history_closes(hour: int = _LAST) -> tuple[float, ...]:
    """Closes observable at the decision, straight from the closed form."""
    return tuple(_close_at(index) for index in range(0, hour + 1))


def _expected_sma(closes: Sequence[float]) -> float:
    """The 200-day simple moving average, computed here from the definition."""
    width = TREND_SMA_DAYS * HOURS_PER_DAY
    window = closes[-width:]
    assert len(window) == width
    return math.fsum(window) / width


def _expected_tsmom(closes: Sequence[float]) -> float:
    """The trailing 180-day log return, computed here from the definition."""
    lag = TSMOM_LOOKBACK_DAYS * HOURS_PER_DAY
    return math.log(closes[-1] / closes[-(lag + 1)])


def _expected_ewma_vol(closes: Sequence[float]) -> float:
    """Annualised EWMA(168h) volatility, transcribed from the frozen rules.

    Hourly close-to-close log returns in basis points; the sample standard
    deviation over the first 168 returns; the zero-mean recursion
    `v = d * v + (1 - d) * r ** 2` with `d = 2 ** (-1 / 168)` from return 169
    onward; then back to a fraction and annualised by `sqrt(8760)`.
    """
    pairs = zip(closes, closes[1:], strict=False)
    returns = [math.log(later / prior) * _BPS_PER_UNIT for prior, later in pairs]
    assert len(returns) >= VOLATILITY_INIT_RETURNS
    decay = 0.5 ** (1.0 / EWMA_HALF_LIFE_HOURS)
    variance = 0.0
    for count in range(2, len(returns) + 1):
        if count <= VOLATILITY_INIT_RETURNS:
            variance = statistics.variance(returns[:count])
        else:
            latest = returns[count - 1]
            variance = decay * variance + (1.0 - decay) * latest * latest
    return (math.sqrt(variance) / _BPS_PER_UNIT) * math.sqrt(ANNUALIZATION_HOURS)


# ---------------------------------------------------------------------------
# Frozen parameters and benchmark-set completeness
# ---------------------------------------------------------------------------


def test_benchmark_set_is_the_five_frozen_benchmarks() -> None:
    assert BENCHMARK_SET == (
        BenchmarkId.CASH,
        BenchmarkId.BUY_AND_HOLD,
        BenchmarkId.VOL_TARGET_BUY_AND_HOLD,
        BenchmarkId.CANONICAL_TREND,
        BenchmarkId.CANONICAL_TSMOM,
    )


def test_benchmark_set_has_nothing_outside_the_enum() -> None:
    assert set(BENCHMARK_SET) == set(BenchmarkId)
    assert len(BENCHMARK_SET) == len(set(BENCHMARK_SET)) == 5


def test_benchmark_names_are_the_frozen_spellings() -> None:
    assert [member.value for member in BENCHMARK_SET] == [
        "CASH",
        "BUY_AND_HOLD",
        "VOL_TARGET_BUY_AND_HOLD",
        "CANONICAL_TREND",
        "CANONICAL_TSMOM",
    ]


def test_every_benchmark_has_a_label_and_a_warm_up() -> None:
    assert set(SIGNAL_LABELS) == set(BENCHMARK_SET)
    assert set(REQUIRED_HISTORY_BARS_BY_BENCHMARK) == set(BENCHMARK_SET)


def test_promotion_benchmark_matches_the_protocol() -> None:
    assert PROMOTION_BENCHMARK is BenchmarkId.VOL_TARGET_BUY_AND_HOLD


def test_frozen_parameters() -> None:
    assert VOL_TARGET_ANNUALIZED == 0.60
    assert VOL_TARGET_HALF_LIFE_HOURS == 168
    assert ANNUALIZATION_HOURS == 8760
    assert TREND_SMA_DAYS == 200
    assert TSMOM_LOOKBACK_DAYS == 180
    assert HOURS_PER_DAY == 24
    assert REBALANCE_BAND_ABSOLUTE == 0.10
    assert MINIMUM_HOLD_HOURS_FOR_RISK_INCREASE == 24
    assert MINIMUM_HOLD_FOR_RISK_INCREASE == timedelta(hours=24)
    assert SCHEDULED_DECISION_ANCHOR_HOUR_UTC == 0
    assert MIN_EXPOSURE == 0.0
    assert MAX_EXPOSURE == 1.0


def test_windows_are_the_frozen_day_counts_in_bars() -> None:
    assert TREND_SMA_WINDOW == TREND_SMA_DAYS * HOURS_PER_DAY == 4800
    assert TSMOM_LOOKBACK_HOURS == TSMOM_LOOKBACK_DAYS * HOURS_PER_DAY == 4320


def test_trend_window_is_the_task4_sma_window() -> None:
    """`200-day SMA` and the `sma_4800` feature must be the same number."""
    assert TREND_SMA_WINDOW == SMA_WINDOW


def test_half_life_matches_the_shared_estimator() -> None:
    assert VOL_TARGET_HALF_LIFE_HOURS == EWMA_HALF_LIFE_HOURS


def test_required_history_per_benchmark() -> None:
    assert REQUIRED_HISTORY_BARS_BY_BENCHMARK == {
        BenchmarkId.CASH: 1,
        BenchmarkId.BUY_AND_HOLD: 1,
        BenchmarkId.VOL_TARGET_BUY_AND_HOLD: 169,
        BenchmarkId.CANONICAL_TREND: 4800,
        BenchmarkId.CANONICAL_TSMOM: 4321,
    }


def test_required_history_is_the_binding_maximum() -> None:
    values = REQUIRED_HISTORY_BARS_BY_BENCHMARK.values()
    assert REQUIRED_HISTORY_BARS == 4800
    assert REQUIRED_HISTORY_BARS == max(values)


def test_all_exported_names_exist() -> None:
    for name in canonical.__all__:
        assert hasattr(canonical, name), name


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_require_benchmark_accepts_members_and_names(bench: BenchmarkId) -> None:
    assert require_canonical_benchmark(bench) is bench
    assert require_canonical_benchmark(bench.value) is bench


@pytest.mark.parametrize(
    "name",
    ["cash", "Cash", "MOMENTUM", "VOL_TARGET", "", "CANONICAL_CARRY"],
)
def test_require_benchmark_rejects_anything_else(name: str) -> None:
    with pytest.raises(CanonicalBenchmarkError, match="canonical Cycle-1"):
        require_canonical_benchmark(name)


# ---------------------------------------------------------------------------
# Benchmark identities
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("hour", [4799, 4800, 4870, 4999])
def test_cash_exposure_is_exactly_zero(hour: int) -> None:
    signal = _sig(BenchmarkId.CASH, hour)
    assert signal.target_exposure == 0.0
    assert signal.signal == 0.0
    assert signal.signal_label == "constant_zero_exposure"


@pytest.mark.parametrize("path", _PATHS)
def test_cash_is_zero_on_every_path(path: _Path) -> None:
    assert _sig_on(BenchmarkId.CASH, path(), _LAST).target_exposure == 0.0


def test_cash_helper_is_zero() -> None:
    assert cash_exposure() == 0.0


@pytest.mark.parametrize("hour", [4799, 4800, 4870, 4999])
def test_buy_and_hold_exposure_is_exactly_one(hour: int) -> None:
    signal = _sig(BenchmarkId.BUY_AND_HOLD, hour)
    assert signal.target_exposure == 1.0
    assert signal.signal == 1.0
    assert signal.signal_label == "constant_full_exposure"


@pytest.mark.parametrize("path", _PATHS)
def test_buy_and_hold_is_one_on_every_path(path: _Path) -> None:
    signal = _sig_on(BenchmarkId.BUY_AND_HOLD, path(), _LAST)
    assert signal.target_exposure == 1.0


def test_buy_and_hold_helper_is_one() -> None:
    assert buy_and_hold_exposure() == 1.0


def test_vol_target_signal_matches_an_independent_ewma() -> None:
    signal = _sig(BenchmarkId.VOL_TARGET_BUY_AND_HOLD, _LAST)
    expected = _expected_ewma_vol(_history_closes())
    assert signal.signal == pytest.approx(expected, **_APPROX)
    assert signal.signal_label == "annualized_ewma_168h_forecast_vol"


def test_vol_target_reuses_the_task4_feature_estimator() -> None:
    """`EWMA_168h` must be identical to the shared estimator, not just close."""
    history = _base_series().bars[: _LAST + 1]
    shared = ewma_volatility(hourly_log_returns(history))
    assert annualized_forecast_volatility(history) == shared


def test_vol_target_exposure_is_the_frozen_clip() -> None:
    signal = _sig(BenchmarkId.VOL_TARGET_BUY_AND_HOLD, _LAST)
    expected = min(1.0, max(0.0, 0.60 / signal.signal))
    assert signal.target_exposure == pytest.approx(expected, **_APPROX)


def test_vol_target_is_interior_on_a_volatile_path() -> None:
    """A path noisier than the 0.60 target must size strictly below full."""
    signal = _sig_on(BenchmarkId.VOL_TARGET_BUY_AND_HOLD, _volatile_series(), 399)
    expected = VOL_TARGET_ANNUALIZED / signal.signal
    assert signal.signal > VOL_TARGET_ANNUALIZED
    assert 0.0 < signal.target_exposure < 1.0
    assert signal.target_exposure == pytest.approx(expected, **_APPROX)


def test_vol_target_is_full_on_a_zero_volatility_path() -> None:
    signal = _sig_on(BenchmarkId.VOL_TARGET_BUY_AND_HOLD, _flat_series(), 1000)
    assert signal.signal == 0.0
    assert signal.target_exposure == 1.0


@pytest.mark.parametrize(
    ("forecast", "expected"),
    [
        (0.60, 1.0),
        (1.20, 0.5),
        (0.30, 1.0),
        (0.0, 1.0),
        (6.0, 0.1),
        (2.40, 0.25),
        (1e9, 6e-10),
    ],
)
def test_vol_target_exposure_formula(forecast: float, expected: float) -> None:
    assert vol_target_exposure(forecast) == pytest.approx(expected, **_APPROX)


@pytest.mark.parametrize("forecast", [-1e-12, -0.5, -1.0])
def test_vol_target_rejects_negative_forecasts(forecast: float) -> None:
    with pytest.raises(CanonicalBenchmarkError, match="non-negative"):
        vol_target_exposure(forecast)


@pytest.mark.parametrize("forecast", [math.nan, math.inf, -math.inf])
def test_vol_target_rejects_non_finite_forecasts(forecast: float) -> None:
    with pytest.raises(CanonicalBenchmarkError, match="finite"):
        vol_target_exposure(forecast)


@pytest.mark.parametrize("forecast", [1e-9, 0.01, 0.59, 0.6, 0.61, 3.0, 1e6])
def test_vol_target_exposure_stays_in_the_unit_interval(forecast: float) -> None:
    assert 0.0 <= vol_target_exposure(forecast) <= 1.0


def test_trend_matches_an_independent_sma() -> None:
    signal = _sig(BenchmarkId.CANONICAL_TREND, _LAST)
    closes = _history_closes()
    sma = _expected_sma(closes)
    assert signal.signal == pytest.approx(closes[-1] / sma - 1.0, **_APPROX)
    assert signal.target_exposure == (1.0 if closes[-1] > sma else 0.0)
    assert signal.signal_label == "close_over_sma_4800_minus_1"


def test_trend_reference_matches_an_independent_mean() -> None:
    closes = _history_closes()
    expected = _expected_sma(closes)
    assert trend_reference(closes) == pytest.approx(expected, **_APPROX)


def test_trend_is_long_on_a_rising_path() -> None:
    signal = _sig_on(BenchmarkId.CANONICAL_TREND, _rising_series(), _LAST)
    assert signal.target_exposure == 1.0
    assert signal.signal > 0.0


def test_trend_is_flat_on_a_falling_path() -> None:
    signal = _sig_on(BenchmarkId.CANONICAL_TREND, _falling_series(), _LAST)
    assert signal.target_exposure == 0.0
    assert signal.signal < 0.0


def test_trend_is_flat_when_close_equals_the_average() -> None:
    """`close > sma` is strict, so an exactly flat path holds no exposure."""
    signal = _sig_on(BenchmarkId.CANONICAL_TREND, _flat_series(), _LAST)
    assert signal.signal == 0.0
    assert signal.target_exposure == 0.0


@pytest.mark.parametrize(
    ("close", "sma", "expected"),
    [
        (101.0, 100.0, 1.0),
        (100.0, 100.0, 0.0),
        (99.0, 100.0, 0.0),
        (100.0000001, 100.0, 1.0),
    ],
)
def test_trend_exposure_comparison(
    close: float,
    sma: float,
    expected: float,
) -> None:
    assert canonical_trend_exposure(close, sma) == expected


def test_tsmom_matches_an_independent_log_return() -> None:
    signal = _sig(BenchmarkId.CANONICAL_TSMOM, _LAST)
    expected = _expected_tsmom(_history_closes())
    assert signal.signal == pytest.approx(expected, **_APPROX)
    assert signal.target_exposure == (1.0 if expected > 0.0 else 0.0)
    assert signal.signal_label == "trailing_180d_log_return"


def test_tsmom_uses_exactly_the_4320_bar_lag() -> None:
    closes = _history_closes()
    expected = math.log(closes[-1] / closes[-(TSMOM_LOOKBACK_HOURS + 1)])
    assert tsmom_lookback_return(closes) == pytest.approx(expected, **_APPROX)


def test_tsmom_is_long_on_a_rising_path() -> None:
    signal = _sig_on(BenchmarkId.CANONICAL_TSMOM, _rising_series(), _LAST)
    expected = 0.0001 * TSMOM_LOOKBACK_HOURS
    assert signal.target_exposure == 1.0
    assert signal.signal == pytest.approx(expected, **_APPROX)


def test_tsmom_is_flat_on_a_falling_path() -> None:
    signal = _sig_on(BenchmarkId.CANONICAL_TSMOM, _falling_series(), _LAST)
    assert signal.target_exposure == 0.0
    assert signal.signal < 0.0


def test_tsmom_is_flat_on_a_zero_return_path() -> None:
    """`> 0` is strict, so an exactly zero 180-day return holds no exposure."""
    signal = _sig_on(BenchmarkId.CANONICAL_TSMOM, _flat_series(), _LAST)
    assert signal.signal == 0.0
    assert signal.target_exposure == 0.0


@pytest.mark.parametrize(
    ("momentum", "expected"),
    [(0.5, 1.0), (1e-15, 1.0), (0.0, 0.0), (-1e-15, 0.0), (-0.5, 0.0)],
)
def test_tsmom_exposure_comparison(momentum: float, expected: float) -> None:
    assert canonical_tsmom_exposure(momentum) == expected


# ---------------------------------------------------------------------------
# Causal decision timing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_decision_time_is_the_decision_bar_close(bench: BenchmarkId) -> None:
    signal = _sig(bench, _LAST)
    decision_bar = _base_series().bars[_LAST]
    assert signal.decision_time == decision_bar.close_time
    assert signal.decision_time == decision_bar.open_time + BAR_INTERVAL
    assert signal.decision_time == _decision(_LAST)


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_the_decision_bar_is_included(bench: BenchmarkId) -> None:
    signal = _sig(bench, _LAST)
    assert signal.close == _close_at(_LAST)
    assert signal.history_bars == _LAST + 1


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_only_bars_at_or_before_the_decision_are_read(bench: BenchmarkId) -> None:
    """A signal at an earlier decision must ignore everything after it."""
    hour = 4820
    truncated = _series(0, hour + 1)
    assert _sig(bench, hour) == _sig_on(bench, truncated, hour)


@pytest.mark.parametrize(
    ("hour", "scheduled"),
    [(23, True), (0, False), (11, False), (47, True), (4799, True)],
)
def test_only_midnight_utc_is_a_scheduled_decision(
    hour: int,
    scheduled: bool,
) -> None:
    signal = _sig(BenchmarkId.CASH, hour)
    assert signal.scheduled is scheduled
    assert signal.decision_time.hour == (hour + 1) % 24


@pytest.mark.parametrize("hour", [0, 1, 12, 23, 24, 4799])
def test_is_scheduled_decision_is_midnight_utc(hour: int) -> None:
    moment = _ts(hour)
    assert is_scheduled_decision(moment) is (moment.hour == 0)


def test_is_scheduled_decision_rejects_unaligned_input() -> None:
    with pytest.raises(CanonicalBenchmarkError, match="aligned"):
        is_scheduled_decision(_ORIGIN + timedelta(minutes=30))


def test_is_scheduled_decision_rejects_naive_input() -> None:
    with pytest.raises(CanonicalBenchmarkError, match="UTC-aware"):
        is_scheduled_decision(datetime(2024, 1, 1))


# ---------------------------------------------------------------------------
# No future leakage
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_extreme_future_bars_change_nothing(bench: BenchmarkId) -> None:
    hour = 4850
    bars = _base_series().bars
    tail = tuple(_extreme_bar(h) for h in range(hour + 1, hour + 49))
    extended = BarSeries(symbol=_SYMBOL, bars=bars[: hour + 1] + tail)
    assert _sig_on(bench, extended, hour) == _sig(bench, hour)


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_a_hole_after_the_decision_is_irrelevant(bench: BenchmarkId) -> None:
    hour = 4830
    bars = _base_series().bars
    gapped = BarSeries(symbol=_SYMBOL, bars=bars[: hour + 1] + bars[hour + 5 :])
    assert _sig_on(bench, gapped, hour) == _sig(bench, hour)


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_truncation_at_the_decision_bar_changes_nothing(
    bench: BenchmarkId,
) -> None:
    bars = _base_series().bars[: _LAST + 1]
    truncated = BarSeries(symbol=_SYMBOL, bars=bars)
    assert _sig_on(bench, truncated, _LAST) == _sig(bench, _LAST)


# ---------------------------------------------------------------------------
# Exposure bounds and no shorting
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bench", BENCHMARK_SET)
@pytest.mark.parametrize("hour", [4799, 4830, 4901, 4999])
def test_exposure_is_long_only_and_unlevered(bench: BenchmarkId, hour: int) -> None:
    signal = _sig(bench, hour)
    assert MIN_EXPOSURE <= signal.target_exposure <= MAX_EXPOSURE


@pytest.mark.parametrize("path", _PATHS)
@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_exposure_stays_in_bounds_on_every_path(
    path: _Path,
    bench: BenchmarkId,
) -> None:
    signal = _sig_on(bench, path(), _LAST)
    assert 0.0 <= signal.target_exposure <= 1.0


@pytest.mark.parametrize("exposure", [-1e-9, -0.5, -1.0, 1.0000001, 2.0])
def test_signal_rejects_out_of_bounds_exposure(exposure: float) -> None:
    with pytest.raises(CanonicalBenchmarkError, match=r"\[0.0, 1.0\]"):
        BenchmarkSignal(
            benchmark=BenchmarkId.CASH,
            symbol=_SYMBOL,
            decision_time=_ORIGIN,
            close=100.0,
            history_bars=1,
            signal=0.0,
            signal_label="constant_zero_exposure",
            target_exposure=exposure,
            scheduled=True,
        )


@pytest.mark.parametrize("exposure", [-1e-9, -0.5, 1.0000001, 2.0])
def test_state_rejects_shorts_and_leverage(exposure: float) -> None:
    with pytest.raises(CanonicalBenchmarkError, match="current_exposure"):
        ExposureState(current_exposure=exposure)


@pytest.mark.parametrize("exposure", [math.nan, math.inf, -math.inf])
def test_state_rejects_non_finite_exposure(exposure: float) -> None:
    with pytest.raises(CanonicalBenchmarkError, match="finite"):
        ExposureState(current_exposure=exposure)


@pytest.mark.parametrize("target", [-0.5, 1.5, math.nan])
def test_rebalance_rejects_out_of_bounds_targets(target: float) -> None:
    state = ExposureState(current_exposure=0.5)
    with pytest.raises(CanonicalBenchmarkError, match="target_exposure"):
        rebalance(state, target, _ts(24))


# ---------------------------------------------------------------------------
# Determinism and purity
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_repeated_evaluation_is_identical(bench: BenchmarkId) -> None:
    assert _sig(bench, _LAST) == _sig(bench, _LAST)


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_a_rebuilt_series_gives_the_same_signal(bench: BenchmarkId) -> None:
    rebuilt = _series(0, _SERIES_BARS)
    assert _sig_on(bench, rebuilt, _LAST) == _sig(bench, _LAST)


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_volume_never_enters_a_benchmark(bench: BenchmarkId) -> None:
    quiet = _series(0, _SERIES_BARS, _close_at, 0.0)
    loud = _series(0, _SERIES_BARS, _close_at, 1e9)
    assert _sig_on(bench, quiet, _LAST) == _sig_on(bench, loud, _LAST)


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_no_calendar_term_enters_a_benchmark(bench: BenchmarkId) -> None:
    """Shifting the whole series in time must not move any signal value."""
    origin = _ORIGIN + timedelta(hours=4321)
    shifted = _series(0, _SERIES_BARS, _close_at, None, origin)
    moved = benchmark_signal(bench, shifted, _decision(_LAST, origin))
    base = _sig(bench, _LAST)
    assert moved.signal == base.signal
    assert moved.target_exposure == base.target_exposure
    assert moved.close == base.close
    assert moved.history_bars == base.history_bars


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_benchmark_signals_are_order_independent(bench: BenchmarkId) -> None:
    hours = [4799, 4850, 4901, 4999]
    times = [_decision(hour) for hour in hours]
    forward = benchmark_signals(bench, _base_series(), times)
    backward = benchmark_signals(bench, _base_series(), times[::-1])
    assert forward == tuple(reversed(backward))
    assert [signal.decision_time for signal in forward] == times


def test_benchmark_signals_returns_one_signal_per_decision() -> None:
    times = [_decision(hour) for hour in (4799, 4800, 4801)]
    signals = benchmark_signals(
        BenchmarkId.CANONICAL_TREND,
        _base_series(),
        times,
    )
    assert len(signals) == 3


def test_benchmark_signals_accepts_an_empty_schedule() -> None:
    assert benchmark_signals(BenchmarkId.CASH, _base_series(), []) == ()


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_the_input_series_is_never_mutated(bench: BenchmarkId) -> None:
    series = _series(0, _SERIES_BARS)
    snapshot = tuple(series.bars)
    _sig_on(bench, series, _LAST)
    assert series.bars == snapshot
    assert series.symbol == _SYMBOL


# ---------------------------------------------------------------------------
# Warm-up, gaps, and malformed input
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_exactly_the_required_history_is_accepted(bench: BenchmarkId) -> None:
    required = REQUIRED_HISTORY_BARS_BY_BENCHMARK[bench]
    series = _series(0, required)
    assert _sig_on(bench, series, required - 1).history_bars == required


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_one_bar_short_of_the_warm_up_is_rejected(bench: BenchmarkId) -> None:
    required = REQUIRED_HISTORY_BARS_BY_BENCHMARK[bench]
    if required < 2:
        pytest.skip("a constant benchmark needs only the decision bar")
    series = _series(0, required - 1)
    with pytest.raises(CanonicalBenchmarkError, match="contiguous 1h bars"):
        _sig_on(bench, series, required - 2)


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_an_early_decision_in_a_long_series_is_rejected(bench: BenchmarkId) -> None:
    required = REQUIRED_HISTORY_BARS_BY_BENCHMARK[bench]
    if required < 2:
        pytest.skip("a constant benchmark needs only the decision bar")
    with pytest.raises(CanonicalBenchmarkError, match=r"bar\(s\) of history"):
        _sig(bench, required - 2)


def test_the_reported_shortfall_names_the_actual_count() -> None:
    series = _series(0, 4799)
    with pytest.raises(CanonicalBenchmarkError, match=r"has 4799 bar\(s\)"):
        _sig_on(BenchmarkId.CANONICAL_TREND, series, 4798)


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_a_hole_before_the_decision_is_rejected(bench: BenchmarkId) -> None:
    bars = _base_series().bars
    gapped = BarSeries(symbol=_SYMBOL, bars=bars[:2000] + bars[2001:])
    with pytest.raises(CanonicalBenchmarkError, match="contiguous 1h bars"):
        _sig_on(bench, gapped, _LAST)


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_a_hole_just_before_the_decision_is_rejected(bench: BenchmarkId) -> None:
    bars = _base_series().bars
    gapped = BarSeries(symbol=_SYMBOL, bars=bars[: _LAST - 1] + bars[_LAST:])
    with pytest.raises(CanonicalBenchmarkError, match="does not follow"):
        _sig_on(bench, gapped, _LAST)


def test_a_gap_is_never_bridged_or_back_filled() -> None:
    """A post-gap segment is refused, not silently selected as the history."""
    bars = _base_series().bars
    gapped = BarSeries(symbol=_SYMBOL, bars=bars[:100] + bars[110:])
    with pytest.raises(CanonicalBenchmarkError):
        _sig_on(BenchmarkId.VOL_TARGET_BUY_AND_HOLD, gapped, _LAST)


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_an_unknown_decision_timestamp_is_rejected(bench: BenchmarkId) -> None:
    with pytest.raises(CanonicalBenchmarkError, match="no bar with open_time"):
        _sig(bench, _SERIES_BARS + 10)


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_an_unaligned_decision_timestamp_is_rejected(bench: BenchmarkId) -> None:
    moment = _decision(_LAST) + timedelta(minutes=17)
    with pytest.raises(CanonicalBenchmarkError, match="aligned"):
        benchmark_signal(bench, _base_series(), moment)


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_a_naive_decision_timestamp_is_rejected(bench: BenchmarkId) -> None:
    moment = _decision(_LAST).replace(tzinfo=None)
    with pytest.raises(CanonicalBenchmarkError, match="UTC-aware"):
        benchmark_signal(bench, _base_series(), moment)


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_a_non_utc_decision_timestamp_is_rejected(bench: BenchmarkId) -> None:
    offset = timezone(timedelta(hours=3))
    moment = _decision(_LAST).astimezone(offset)
    with pytest.raises(CanonicalBenchmarkError, match="zero UTC offset"):
        benchmark_signal(bench, _base_series(), moment)


def test_a_non_hourly_series_is_rejected() -> None:
    day = timedelta(days=1)
    bars = tuple(
        Bar(
            open_time=_ORIGIN + index * day,
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.0,
            volume=1.0,
            interval=day,
        )
        for index in range(5)
    )
    daily = BarSeries(symbol=_SYMBOL, bars=bars, interval=day)
    with pytest.raises(CanonicalBenchmarkError, match="benchmarks require a"):
        benchmark_signal(BenchmarkId.CASH, daily, _ORIGIN + day)


def test_duplicate_open_times_are_rejected_by_bar_semantics() -> None:
    bar = _bar_from(_close_at, 5)
    with pytest.raises(BarSemanticsError, match="duplicate open_time"):
        BarSeries(symbol=_SYMBOL, bars=(bar, bar))


def test_trend_reference_rejects_short_history() -> None:
    with pytest.raises(CanonicalBenchmarkError, match="needs 4800"):
        trend_reference([100.0] * (TREND_SMA_WINDOW - 1))


def test_tsmom_lookback_rejects_short_history() -> None:
    with pytest.raises(CanonicalBenchmarkError, match="needs 4321 closes"):
        tsmom_lookback_return([100.0] * TSMOM_LOOKBACK_HOURS)


def test_forecast_volatility_rejects_short_history() -> None:
    with pytest.raises(CanonicalBenchmarkError, match="168"):
        annualized_forecast_volatility(_base_series().bars[:100])


def test_forecast_volatility_rejects_gapped_bars() -> None:
    bars = _base_series().bars[:400]
    with pytest.raises(CanonicalBenchmarkError, match="contiguous"):
        annualized_forecast_volatility(bars[:200] + bars[201:])


# ---------------------------------------------------------------------------
# Shared scheduling, band, and minimum-hold rules
# ---------------------------------------------------------------------------

_MIDNIGHT = _ts(24)
_INTRADAY = _ts(29)


def test_scheduled_risk_increase_from_a_cold_start() -> None:
    decision = rebalance(ExposureState(current_exposure=0.0), 1.0, _MIDNIGHT)
    assert decision.action is RebalanceAction.SCHEDULED_INCREASE
    assert decision.new_exposure == 1.0
    assert decision.last_risk_increase_time == _MIDNIGHT
    assert decision.traded is True
    assert decision.scheduled is True


def test_buy_and_hold_enters_at_the_first_eligible_decision() -> None:
    target = _sig(BenchmarkId.BUY_AND_HOLD, 4799).target_exposure
    state = ExposureState(current_exposure=0.0)
    intraday = rebalance(state, target, _decision(4800))
    scheduled = rebalance(state, target, _decision(4799))
    assert intraday.action is RebalanceAction.HOLD
    assert intraday.new_exposure == 0.0
    assert scheduled.action is RebalanceAction.SCHEDULED_INCREASE
    assert scheduled.new_exposure == 1.0


def test_buy_and_hold_then_holds() -> None:
    state = ExposureState(current_exposure=1.0, last_risk_increase_time=_MIDNIGHT)
    later = rebalance(state, 1.0, _ts(240))
    assert later.action is RebalanceAction.HOLD
    assert later.new_exposure == 1.0


def test_intraday_risk_increase_is_refused() -> None:
    decision = rebalance(ExposureState(current_exposure=0.2), 0.9, _INTRADAY)
    assert decision.action is RebalanceAction.HOLD
    assert decision.new_exposure == 0.2
    assert "scheduled" in decision.reason
    assert decision.last_risk_increase_time is None


def test_intraday_reduction_across_the_band_is_allowed() -> None:
    state = ExposureState(current_exposure=0.9, last_risk_increase_time=_MIDNIGHT)
    decision = rebalance(state, 0.4, _INTRADAY)
    assert decision.action is RebalanceAction.INTRADAY_REDUCTION
    assert decision.new_exposure == 0.4
    assert decision.last_risk_increase_time == _MIDNIGHT


def test_intraday_reduction_inside_the_band_is_refused() -> None:
    decision = rebalance(ExposureState(current_exposure=0.5), 0.45, _INTRADAY)
    assert decision.action is RebalanceAction.HOLD
    assert decision.new_exposure == 0.5


def test_scheduled_reduction_across_the_band_is_allowed() -> None:
    decision = rebalance(ExposureState(current_exposure=0.8), 0.3, _MIDNIGHT)
    assert decision.action is RebalanceAction.SCHEDULED_REDUCTION
    assert decision.new_exposure == 0.3


def test_scheduled_change_inside_the_band_is_refused() -> None:
    decision = rebalance(ExposureState(current_exposure=0.5), 0.55, _MIDNIGHT)
    assert decision.action is RebalanceAction.HOLD
    assert decision.new_exposure == 0.5
    assert "band" in decision.reason


def test_a_change_exactly_at_the_band_is_acted_on() -> None:
    increase = rebalance(ExposureState(current_exposure=0.0), 0.1, _MIDNIGHT)
    reduction = rebalance(ExposureState(current_exposure=0.1), 0.0, _INTRADAY)
    assert increase.action is RebalanceAction.SCHEDULED_INCREASE
    assert reduction.action is RebalanceAction.INTRADAY_REDUCTION


def test_a_change_just_inside_the_band_is_refused() -> None:
    decision = rebalance(ExposureState(current_exposure=0.0), 0.09, _MIDNIGHT)
    assert decision.action is RebalanceAction.HOLD


# ---------------------------------------------------------------------------
# Band threshold semantics (regression for the floating-point boundary)
# ---------------------------------------------------------------------------

_TENTHS: tuple[float, ...] = tuple(step / 10.0 for step in range(11))
_ADJACENT_TENTHS: tuple[tuple[float, float], ...] = tuple(
    (_TENTHS[index], _TENTHS[index + 1]) for index in range(len(_TENTHS) - 1)
)


def test_the_floating_point_band_hazard_still_exists() -> None:
    """Guard the guard: some tenth steps really do render below `0.10`.

    If binary floating point ever stopped misrendering these differences this
    test would fail, signalling that the regressions below no longer exercise
    the hazard they were written for.
    """
    misrendered = [
        (lower, upper)
        for lower, upper in _ADJACENT_TENTHS
        if abs(upper - lower) < REBALANCE_BAND_ABSOLUTE
    ]
    assert misrendered, "a literal >= 0.10 comparison would now be safe"


@pytest.mark.parametrize(("lower", "upper"), _ADJACENT_TENTHS)
def test_every_adjacent_tenth_step_increase_reaches_the_band(
    lower: float, upper: float
) -> None:
    decision = rebalance(ExposureState(current_exposure=lower), upper, _MIDNIGHT)
    assert decision.action is RebalanceAction.SCHEDULED_INCREASE
    assert decision.new_exposure == upper


@pytest.mark.parametrize(("lower", "upper"), _ADJACENT_TENTHS)
@pytest.mark.parametrize("hour", [24, 29])
def test_every_adjacent_tenth_step_reduction_reaches_the_band(
    lower: float, upper: float, hour: int
) -> None:
    moment = _ts(hour)
    decision = rebalance(ExposureState(current_exposure=upper), lower, moment)
    expected = (
        RebalanceAction.SCHEDULED_REDUCTION
        if moment.hour == SCHEDULED_DECISION_ANCHOR_HOUR_UTC
        else RebalanceAction.INTRADAY_REDUCTION
    )
    assert decision.action is expected
    assert decision.new_exposure == lower


def test_the_representable_neighbour_just_below_the_band_reaches_it() -> None:
    """One ULP below `0.10` is `0.10` as far as the frozen band is concerned."""
    target = math.nextafter(REBALANCE_BAND_ABSOLUTE, 0.0)
    decision = rebalance(ExposureState(current_exposure=0.0), target, _MIDNIGHT)
    assert target < REBALANCE_BAND_ABSOLUTE
    assert decision.action is RebalanceAction.SCHEDULED_INCREASE


def test_the_representable_neighbour_just_above_the_band_reaches_it() -> None:
    target = math.nextafter(REBALANCE_BAND_ABSOLUTE, 1.0)
    decision = rebalance(ExposureState(current_exposure=0.0), target, _MIDNIGHT)
    assert target > REBALANCE_BAND_ABSOLUTE
    assert decision.action is RebalanceAction.SCHEDULED_INCREASE


def test_a_change_clear_of_the_band_tolerance_is_refused() -> None:
    """The slack is representation noise only; a real shortfall still holds."""
    target = REBALANCE_BAND_ABSOLUTE - 1e-12
    decision = rebalance(ExposureState(current_exposure=0.0), target, _MIDNIGHT)
    assert decision.action is RebalanceAction.HOLD
    assert decision.new_exposure == 0.0


@pytest.mark.parametrize(
    "change",
    [
        REBALANCE_BAND_ABSOLUTE,
        0.3 - 0.2,
        0.2 - 0.3,
        1.0 - 0.9,
        0.7 - 0.6,
        0.5,
        -0.5,
        1.0,
    ],
)
def test_reaches_rebalance_band_accepts_changes_at_or_past_the_band(
    change: float,
) -> None:
    assert reaches_rebalance_band(change) is True
    assert reaches_rebalance_band(-change) is True


@pytest.mark.parametrize("change", [0.0, 0.09, -0.09, 1e-9, 0.05, -0.0999])
def test_reaches_rebalance_band_refuses_changes_inside_the_band(
    change: float,
) -> None:
    assert reaches_rebalance_band(change) is False


@pytest.mark.parametrize("change", [math.nan, math.inf, -math.inf])
def test_reaches_rebalance_band_rejects_a_nonfinite_change(change: float) -> None:
    with pytest.raises(CanonicalBenchmarkError, match="finite"):
        reaches_rebalance_band(change)


def test_rebalance_band_tolerance_is_representation_noise_only() -> None:
    assert REBALANCE_BAND_TOLERANCE == 4.0 * math.ulp(MAX_EXPOSURE)
    assert 0.0 < REBALANCE_BAND_TOLERANCE < 1e-14


def test_minimum_hold_blocks_a_second_increase_at_the_same_decision() -> None:
    """Zero elapsed hours is the only reachable state the 24h hold can block.

    Risk rises only at the 00:00 UTC scheduled decision, so a valid
    `last_risk_increase_time` is always a midnight and the gap to any later
    scheduled decision is a whole multiple of 24h. The one shorter gap the
    rules can produce is a second increase attempt at the very decision that
    already raised risk, which is exactly what a re-applied `next_state` does.
    """
    state = ExposureState(current_exposure=0.3, last_risk_increase_time=_MIDNIGHT)
    decision = rebalance(state, 0.9, _MIDNIGHT)
    assert decision.action is RebalanceAction.HOLD
    assert decision.new_exposure == 0.3
    assert "minimum" in decision.reason
    assert decision.last_risk_increase_time == _MIDNIGHT


@pytest.mark.parametrize("elapsed_hours", [24, 48, 72, 1008])
def test_minimum_hold_permits_a_later_increase(elapsed_hours: int) -> None:
    last = _MIDNIGHT - timedelta(hours=elapsed_hours)
    state = ExposureState(current_exposure=0.3, last_risk_increase_time=last)
    decision = rebalance(state, 0.9, _MIDNIGHT)
    assert decision.action is RebalanceAction.SCHEDULED_INCREASE
    assert decision.new_exposure == 0.9
    assert decision.last_risk_increase_time == _MIDNIGHT


def test_minimum_hold_never_blocks_a_reduction() -> None:
    """The hold is active (zero elapsed) yet a reduction still goes through."""
    state = ExposureState(current_exposure=0.9, last_risk_increase_time=_MIDNIGHT)
    decision = rebalance(state, 0.2, _MIDNIGHT)
    assert decision.action is RebalanceAction.SCHEDULED_REDUCTION
    assert decision.new_exposure == 0.2
    assert decision.last_risk_increase_time == _MIDNIGHT


def test_a_reduction_does_not_restart_the_hold_clock() -> None:
    last = _ts(0)
    state = ExposureState(current_exposure=0.9, last_risk_increase_time=last)
    reduced = rebalance(state, 0.2, _ts(10)).next_state
    assert reduced.last_risk_increase_time == last
    assert reduced.current_exposure == 0.2


def test_next_state_round_trips_into_the_next_decision() -> None:
    first = rebalance(ExposureState(current_exposure=0.0), 1.0, _ts(24))
    second = rebalance(first.next_state, 0.2, _ts(30))
    third = rebalance(second.next_state, 1.0, _ts(40))
    fourth = rebalance(third.next_state, 1.0, _ts(48))
    assert first.action is RebalanceAction.SCHEDULED_INCREASE
    assert second.action is RebalanceAction.INTRADAY_REDUCTION
    assert third.action is RebalanceAction.HOLD
    assert fourth.action is RebalanceAction.SCHEDULED_INCREASE
    assert fourth.new_exposure == 1.0


def test_hold_reports_the_unchanged_exposure_and_target() -> None:
    decision = rebalance(ExposureState(current_exposure=0.4), 0.42, _MIDNIGHT)
    assert decision.current_exposure == 0.4
    assert decision.target_exposure == 0.42
    assert decision.new_exposure == 0.4
    assert decision.traded is False


def test_rebalance_rejects_a_future_last_risk_increase() -> None:
    state = ExposureState(current_exposure=0.5, last_risk_increase_time=_ts(96))
    with pytest.raises(CanonicalBenchmarkError, match="after the decision"):
        rebalance(state, 1.0, _ts(48))


def test_rebalance_rejects_an_unaligned_decision_timestamp() -> None:
    state = ExposureState(current_exposure=0.0)
    with pytest.raises(CanonicalBenchmarkError, match="aligned"):
        rebalance(state, 1.0, _MIDNIGHT + timedelta(minutes=5))


def test_rebalance_rejects_a_naive_decision_timestamp() -> None:
    state = ExposureState(current_exposure=0.0)
    with pytest.raises(CanonicalBenchmarkError, match="UTC-aware"):
        rebalance(state, 1.0, datetime(2024, 1, 2))


def test_state_rejects_a_naive_last_risk_increase() -> None:
    with pytest.raises(BarSemanticsError, match="UTC-aware"):
        ExposureState(current_exposure=0.5, last_risk_increase_time=datetime.min)


@pytest.mark.parametrize("current", [0.0, 0.25, 0.5, 0.75, 1.0])
@pytest.mark.parametrize("target", [0.0, 0.25, 0.5, 0.75, 1.0])
@pytest.mark.parametrize("hour", [24, 29])
def test_rebalance_never_leaves_the_unit_interval(
    current: float,
    target: float,
    hour: int,
) -> None:
    state = ExposureState(current_exposure=current)
    decision = rebalance(state, target, _ts(hour))
    assert 0.0 <= decision.new_exposure <= 1.0
    assert decision.new_exposure in (current, target)


@pytest.mark.parametrize("current", [0.0, 0.3, 0.6, 1.0])
@pytest.mark.parametrize("target", [0.0, 0.3, 0.6, 1.0])
@pytest.mark.parametrize("hour", [24, 25, 30, 47, 48])
def test_risk_never_rises_outside_a_scheduled_decision(
    current: float,
    target: float,
    hour: int,
) -> None:
    moment = _ts(hour)
    state = ExposureState(current_exposure=current)
    decision = rebalance(state, target, moment)
    if decision.new_exposure > current:
        assert moment.hour == SCHEDULED_DECISION_ANCHOR_HOUR_UTC
        assert decision.action is RebalanceAction.SCHEDULED_INCREASE


@pytest.mark.parametrize("bench", BENCHMARK_SET)
def test_walking_a_benchmark_obeys_the_shared_rules(bench: BenchmarkId) -> None:
    """Step the rules over 48 consecutive hourly decisions, with no backtester."""
    state = ExposureState(current_exposure=0.0)
    increases: list[datetime] = []
    for hour in range(4951, 4999):
        target = _sig(bench, hour).target_exposure
        decision = rebalance(state, target, _decision(hour))
        assert 0.0 <= decision.new_exposure <= 1.0
        if decision.new_exposure > state.current_exposure:
            assert decision.decision_time.hour == 0
            if increases:
                gap = decision.decision_time - increases[-1]
                assert gap >= MINIMUM_HOLD_FOR_RISK_INCREASE
            increases.append(decision.decision_time)
        elif decision.new_exposure < state.current_exposure:
            drop = state.current_exposure - decision.new_exposure
            assert reaches_rebalance_band(drop)
        state = decision.next_state


# ---------------------------------------------------------------------------
# Exported lookup tables are immutable
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "mapping",
    [SIGNAL_LABELS, REQUIRED_HISTORY_BARS_BY_BENCHMARK],
    ids=["SIGNAL_LABELS", "REQUIRED_HISTORY_BARS_BY_BENCHMARK"],
)
def test_exported_lookup_mappings_reject_assignment(
    mapping: Mapping[BenchmarkId, object],
) -> None:
    with pytest.raises(TypeError):
        mapping[BenchmarkId.CASH] = "tampered"


@pytest.mark.parametrize(
    "mapping",
    [SIGNAL_LABELS, REQUIRED_HISTORY_BARS_BY_BENCHMARK],
    ids=["SIGNAL_LABELS", "REQUIRED_HISTORY_BARS_BY_BENCHMARK"],
)
def test_exported_lookup_mappings_reject_deletion(
    mapping: Mapping[BenchmarkId, object],
) -> None:
    with pytest.raises(TypeError):
        del mapping[BenchmarkId.CASH]


@pytest.mark.parametrize(
    "mapping",
    [SIGNAL_LABELS, REQUIRED_HISTORY_BARS_BY_BENCHMARK],
    ids=["SIGNAL_LABELS", "REQUIRED_HISTORY_BARS_BY_BENCHMARK"],
)
def test_exported_lookup_mappings_expose_no_mutators(
    mapping: Mapping[BenchmarkId, object],
) -> None:
    for mutator in ("clear", "update", "pop", "popitem", "setdefault"):
        assert not hasattr(mapping, mutator)


def test_a_refused_signal_label_mutation_leaves_output_unchanged() -> None:
    series = _base_series()
    labels: Mapping[BenchmarkId, object] = SIGNAL_LABELS
    before = benchmark_signal(BenchmarkId.CASH, series, _decision(_LAST))
    with pytest.raises(TypeError):
        labels[BenchmarkId.CASH] = "tampered"
    after = benchmark_signal(BenchmarkId.CASH, series, _decision(_LAST))
    assert before.signal_label == after.signal_label
    assert after.signal_label == "constant_zero_exposure"


def test_a_refused_warmup_mutation_leaves_validation_unchanged() -> None:
    warmups: Mapping[BenchmarkId, object] = REQUIRED_HISTORY_BARS_BY_BENCHMARK
    required = REQUIRED_HISTORY_BARS_BY_BENCHMARK[BenchmarkId.CANONICAL_TREND]
    with pytest.raises(TypeError):
        warmups[BenchmarkId.CANONICAL_TREND] = 1
    assert REQUIRED_HISTORY_BARS_BY_BENCHMARK[BenchmarkId.CANONICAL_TREND] == required
    with pytest.raises(CanonicalBenchmarkError, match="contiguous 1h bars"):
        benchmark_signal(
            BenchmarkId.CANONICAL_TREND, _base_series(), _decision(required - 2)
        )


# ---------------------------------------------------------------------------
# `ExposureState.last_risk_increase_time` must be a reachable risk-increase time
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("hour", [0, 24, 48, 4800])
def test_state_accepts_a_scheduled_midnight_risk_increase(hour: int) -> None:
    state = ExposureState(current_exposure=0.5, last_risk_increase_time=_ts(hour))
    assert state.last_risk_increase_time == _ts(hour)
    assert state.last_risk_increase_time is not None
    assert state.last_risk_increase_time.hour == SCHEDULED_DECISION_ANCHOR_HOUR_UTC


@pytest.mark.parametrize("hour", [1, 5, 12, 23, 29])
def test_state_rejects_a_risk_increase_away_from_the_scheduled_anchor(
    hour: int,
) -> None:
    with pytest.raises(CanonicalBenchmarkError, match="scheduled 00:00 UTC"):
        ExposureState(current_exposure=0.5, last_risk_increase_time=_ts(hour))


@pytest.mark.parametrize("minutes", [1, 30, 59])
def test_state_rejects_an_unaligned_risk_increase(minutes: int) -> None:
    with pytest.raises(BarSemanticsError, match="aligned"):
        ExposureState(
            current_exposure=0.5,
            last_risk_increase_time=_MIDNIGHT + timedelta(minutes=minutes),
        )


def test_state_rejects_a_non_utc_risk_increase() -> None:
    elsewhere = _MIDNIGHT.astimezone(timezone(timedelta(hours=2)))
    with pytest.raises(BarSemanticsError, match="zero UTC offset"):
        ExposureState(current_exposure=0.5, last_risk_increase_time=elsewhere)


@pytest.mark.parametrize("hour", list(range(24, 48)))
def test_every_decision_hour_leaves_a_constructible_next_state(hour: int) -> None:
    """`rebalance` can only ever record a scheduled 00:00 UTC risk increase."""
    decision = rebalance(ExposureState(current_exposure=0.0), 1.0, _ts(hour))
    recorded = decision.next_state.last_risk_increase_time
    if recorded is not None:
        assert recorded.hour == SCHEDULED_DECISION_ANCHOR_HOUR_UTC
