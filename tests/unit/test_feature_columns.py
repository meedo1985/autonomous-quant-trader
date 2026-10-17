"""`feature_columns` equals the frozen `compute_features`, bit for bit."""

from __future__ import annotations

import math
import random
from datetime import UTC, datetime, timedelta

import pytest

from aqt.data.bars import Bar, BarSeries
from aqt.features.columns import feature_columns
from aqt.features.factory import (
    FEATURE_NAMES,
    REQUIRED_HISTORY_BARS,
    FeatureFactoryError,
    compute_features,
)

START = datetime(2021, 1, 1, tzinfo=UTC)


def _series(n: int, seed: int) -> BarSeries:
    rng = random.Random(seed)
    price, bars = 30000.0, []
    for i in range(n):
        o = price
        c = o * math.exp(rng.gauss(0.0, 0.008))
        h = max(o, c) * math.exp(abs(rng.gauss(0.0, 0.003)))
        lo = min(o, c) * math.exp(-abs(rng.gauss(0.0, 0.003)))
        bars.append(Bar(START + timedelta(hours=i), o, h, lo, c, 1.0))
        price = c
    return BarSeries("BTCUSDT", tuple(bars))


@pytest.mark.parametrize("seed", [1, 2])
def test_columns_equal_compute_features_exactly(seed: int) -> None:
    series = _series(REQUIRED_HISTORY_BARS + 400, seed)
    first, columns = feature_columns(series)
    assert first == REQUIRED_HISTORY_BARS - 1
    count = len(series) - first
    assert all(len(columns[name]) == count for name in FEATURE_NAMES)
    rng = random.Random(seed)
    for k in sorted({0, 1, 2, count - 1, *rng.sample(range(count), 6)}):
        bar = series.bars[first + k]
        row = compute_features(series, bar.open_time + bar.interval).as_dict()
        for name in FEATURE_NAMES:
            assert columns[name][k] == row[name], (name, k)  # exact, not approx


def test_too_short_or_gapped_series_are_refused() -> None:
    with pytest.raises(FeatureFactoryError):
        feature_columns(_series(REQUIRED_HISTORY_BARS - 1, 3))
    s = _series(REQUIRED_HISTORY_BARS + 5, 3)
    gapped = BarSeries("BTCUSDT", s.bars[:100] + s.bars[101:])
    with pytest.raises(Exception):  # noqa: B017 - the series refuses a hole
        feature_columns(gapped)


def test_a_value_the_factory_returns_unchecked_is_returned() -> None:
    # S4A-R1: closes at the smallest subnormal, one high at the largest float:
    # the mean true range is finite, atr_24 = it / close is inf, and the
    # factory returns that row rather than refusing
    tiny, huge = 5e-324, 1.7976931348623157e308
    bars = [
        Bar(START + timedelta(hours=i), tiny, tiny, tiny, tiny, 1.0)
        for i in range(REQUIRED_HISTORY_BARS)
    ]
    k = REQUIRED_HISTORY_BARS - 2
    bars[k] = Bar(bars[k].open_time, tiny, huge, tiny, tiny, 1.0)
    series = BarSeries("BTCUSDT", tuple(bars))
    row = compute_features(series, bars[-1].open_time + bars[-1].interval).as_dict()
    first, columns = feature_columns(series)
    assert math.isinf(row["atr_24"]) and math.isinf(columns["atr_24"][0])
    for name in FEATURE_NAMES:
        assert columns[name][0] == row[name] or (
            math.isnan(columns[name][0]) and math.isnan(row[name])
        ), name


def test_a_non_hourly_series_is_refused() -> None:
    # S4A-R2: the factory refuses any interval but 1h
    bars = tuple(
        Bar(START + timedelta(hours=2 * i), 1.0, 1.0, 1.0, 1.0, 1.0, timedelta(hours=2))
        for i in range(REQUIRED_HISTORY_BARS + 2)
    )
    series = BarSeries("BTCUSDT", bars, interval=timedelta(hours=2))
    with pytest.raises(FeatureFactoryError, match="1:00:00 series"):
        feature_columns(series)
