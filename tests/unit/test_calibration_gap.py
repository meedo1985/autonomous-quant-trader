"""The C2 gap rule (`calibration/gap.py`), on synthetic data only."""

from __future__ import annotations

import math
import random
from datetime import UTC, date, datetime, timedelta

import numpy as np

from aqt.data.bars import Bar, BarSeries
from calibration import gap

START = datetime(2020, 1, 1, tzinfo=UTC)


def _series(prices: list[float], skip: frozenset[int] = frozenset()) -> BarSeries:
    return BarSeries(
        symbol="BTCUSDT",
        bars=tuple(
            Bar(open_time=START + i * timedelta(hours=1), open=p, high=p, low=p,
                close=p, volume=1.0)
            for i, p in enumerate(prices)
            if i not in skip
        ),
    )  # fmt: skip


def _walk(n: int, seed: int = 1) -> list[float]:
    r = random.Random(seed)
    prices = [100.0]
    for _ in range(n - 1):
        prices.append(prices[-1] * math.exp(r.gauss(0, 0.01)))
    return prices


def test_acf_matches_the_textbook_formula_without_missing_days() -> None:
    x = np.random.default_rng(3).standard_normal(200)
    d = x - x.mean()
    expected = [float(d[:-k] @ d[k:] / (d @ d)) for k in range(1, 6)]
    assert np.allclose(gap.acf(list(x), 5), expected, rtol=0, atol=1e-12)


def test_acf_drops_only_the_pairs_with_a_missing_day() -> None:
    # present values 1, 3, 2, 0: mean 1.5, sum of squares 5
    # lag 1 pairs (3, 2), (2, 0): 0.75 - 0.75 = 0
    # lag 2 pairs (1, 3), (3, 0): -0.75 - 2.25 = -3
    r = gap.acf([1.0, None, 3.0, 2.0, 0.0], 2)
    assert math.isclose(r[0], 0.0, abs_tol=1e-15) and math.isclose(r[1], -0.6)


def test_cutoff_is_the_last_significant_lag_under_bartlett_bands() -> None:
    n = 400
    band1 = gap.Z / math.sqrt(n)
    assert gap.cutoff([0.0, 0.0, 0.0], n) == 0
    assert gap.cutoff([band1 * 1.01, 0.0, 0.0], n) == 1
    assert gap.cutoff([band1 * 0.99, 0.0, 0.0], n) == 0
    # lag 3 is significant after a lag-1 spike widens its band; lag 2 is not
    r = [0.5, 0.0, 0.0]
    band3 = gap.Z * math.sqrt((1 + 2 * 0.25) / n)
    assert gap.cutoff([*r[:2], band3 * 1.01], n) == 3
    assert gap.cutoff([*r[:2], band3 * 0.99], n) == 1


def test_a_return_never_spans_a_missing_hour() -> None:
    prices = _walk(400)
    sigma = gap.hourly_volatility(_series(prices, skip=frozenset({300})))
    full = gap.hourly_volatility(_series(prices))
    t300, t301 = (START + i * timedelta(hours=1) for i in (300, 301))
    assert t300 not in sigma and t301 not in sigma  # no return ends there
    t299 = START + 299 * timedelta(hours=1)
    assert sigma[t299] == full[t299]


def test_daily_target_follows_the_protocol_formula() -> None:
    prices = _walk(24 * 20)
    series = _series(prices)
    sigma = gap.hourly_volatility(series)
    targets = gap.daily_targets(series, 72)
    t = START + timedelta(days=5, hours=23)
    i = 5 * 24 + 23
    expected = math.log(prices[i + 72] / prices[i]) / (sigma[t] * math.sqrt(72))
    assert targets[date(2020, 1, 6)] == expected
    # a day whose bar 72 h later does not exist has no target
    assert date(2020, 1, 18) not in targets and date(2020, 1, 17) in targets


def test_g_is_the_largest_gap_and_at_least_the_longest_horizon() -> None:
    result = gap.gap(_series(_walk(24 * 120)))
    horizons = result["horizons"]
    assert isinstance(horizons, dict) and set(horizons) == {"24h", "72h", "168h"}
    for h, v in horizons.items():
        assert v["gap_days"] == max(int(h[:-1]) // 24, v["cutoff"])
        assert 0 <= v["cutoff"] <= v["max_lag"] == 4 * (int(h[:-1]) // 24)
    assert result["g"] == max(v["gap_days"] for v in horizons.values()) >= 7
