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
