"""Every frozen Cycle-1 feature at every hour of a series, in one pass.

`compute_features` recomputes each feature from the start of the history at
every decision (about 0.2 s per call), which is too slow for runs over tens
of thousands of hours (D-19 screen slice S4). `feature_columns` returns the
same numbers, bit for bit, for every decision bar at once; the unit tests
assert exact equality with `compute_features`. It reads the same history
(every bar from the start of the series) and reproduces each primitive's
float operations:

- returns and `ret_*`: `log_return`, as the factory calls it;
- EMA: seeded with the mean of the first `span` closes, then the same
  recursion over every later close;
- sums the factory takes with `math.fsum` (SMA, ATR, the EMA seed): an exact
  running integer sum at scale 2**1074 (every finite double is an integer
  multiple of 2**-1074), divided by 2**1074 with Python's correctly rounded
  integer true division, which equals the correctly rounded `math.fsum`;
- `rv_*`: `statistics.stdev` is the correctly rounded square root of the
  exact sample variance; exact running integer sums of the values and their
  squares give that variance, rounded by the same
  `statistics._float_sqrt_of_frac` (pinned runtime, DRAFT R-8);
- `ewma_vol_168h`: one pass of `ewma_hourly_volatility_bps_series` over the
  basis-point returns, as `ewma_volatility` does per call;
- `breakout_720`: `max` over the window.

Refusals are the factory's own, no more and no fewer (S4A-R1, S4A-R2): a
non-hourly series or a hole, too short a history, and a non-finite value of
a primitive the factory checks (`log_return`, `true_range`, the EMA, the SMA,
each `rv_*`, `ewma_vol_168h`, the mean true range before it is divided by
the close). Derived ratios the factory does not check (`ema_dist_*`,
`trend_200d`, `breakout_720`, `atr_24`) are returned as computed, even when
not finite; callers decide what that means.
"""

from __future__ import annotations

import statistics
from fractions import Fraction

from aqt.backtest.costs import (
    BPS_PER_UNIT,
    CostModelError,
    ewma_hourly_volatility_bps_series,
)
from aqt.data.bars import BAR_INTERVAL, BarSeries
from aqt.features.factory import (
    _ANNUALIZATION_FACTOR,
    _EMA_ALPHAS,
    ATR_WINDOW,
    BREAKOUT_WINDOW,
    EMA_SPANS,
    FEATURE_NAMES,
    REQUIRED_HISTORY_BARS,
    RV_WINDOWS,
    SMA_WINDOW,
    FeatureFactoryError,
    _require_contiguous_hourly,
    _require_finite,
    log_return,
    true_range,
)

__all__ = ["feature_columns"]

_SCALE_BITS = 1074
_SCALE = 1 << _SCALE_BITS


def _exact(x: float) -> int:
    """`x` times 2**1074, exactly."""
    n, d = x.as_integer_ratio()
    return n * (_SCALE // d)


def _fsum_value(total: int) -> float:
    """The correctly rounded value of `total / 2**1074` (as `math.fsum`)."""
    return total / _SCALE


def _stdev(count: int, s1: int, s2: int) -> float:
    """`statistics.stdev` from exact sums at scale 2**1074 (values) and
    2**2148 (squares)."""
    mss = Fraction(count * s2 - s1 * s1, count * (count - 1) * _SCALE * _SCALE)
    root: float = statistics._float_sqrt_of_frac(  # type: ignore[attr-defined]
        mss.numerator, mss.denominator
    )
    return root


def feature_columns(series: BarSeries) -> tuple[int, dict[str, tuple[float, ...]]]:
    """`(first, columns)`: `columns[name][k]` is `compute_features(series,
    t).<name>` for the decision at the close of bar `first + k`, for every
    bar with the factory's required history."""
    if series.interval != BAR_INTERVAL:
        raise FeatureFactoryError(
            f"features require a {BAR_INTERVAL} series, got {series.interval}"
        )
    bars = series.bars
    n = len(bars)
    first = REQUIRED_HISTORY_BARS - 1
    if n <= first:
        raise FeatureFactoryError(
            f"{series.symbol} has {n} bars; {REQUIRED_HISTORY_BARS} are required"
        )
    _require_contiguous_hourly(bars)  # the factory's check, after the length
    closes = [b.close for b in bars]
    returns = [log_return(closes[i + 1], closes[i]) for i in range(n - 1)]
    try:
        sigma_bps = ewma_hourly_volatility_bps_series(
            [r * BPS_PER_UNIT for r in returns]
        )
    except CostModelError as error:
        raise FeatureFactoryError(str(error)) from error
    ranges = [0.0] + [true_range(bars[i], closes[i - 1]) for i in range(1, n)]
    exact_close = [_exact(c) for c in closes]
    exact_ret = [_exact(r) for r in returns]
    exact_range = [_exact(r) for r in ranges]

    out: dict[str, list[float]] = {name: [] for name in FEATURE_NAMES}
    ema = {}
    for span in EMA_SPANS:  # state after close `first`, as the factory's loop
        alpha = _EMA_ALPHAS[span]
        state = _fsum_value(sum(exact_close[:span])) / span
        for value in closes[span : first + 1]:
            state = alpha * value + (1.0 - alpha) * state
        ema[span] = state
    sma = sum(exact_close[first + 1 - SMA_WINDOW : first + 1])
    atr = sum(exact_range[first + 1 - ATR_WINDOW : first + 1])
    rv = {
        w: (
            sum(exact_ret[first - w : first]),
            sum(x * x for x in exact_ret[first - w : first]),
        )
        for w in RV_WINDOWS
    }

    for i in range(first, n):
        if i > first:  # advance every running quantity to bar i
            for span in EMA_SPANS:
                alpha = _EMA_ALPHAS[span]
                ema[span] = alpha * closes[i] + (1.0 - alpha) * ema[span]
            sma += exact_close[i] - exact_close[i - SMA_WINDOW]
            atr += exact_range[i] - exact_range[i - ATR_WINDOW]
            new = exact_ret[i - 1]
            for w in RV_WINDOWS:
                old = exact_ret[i - 1 - w]
                s1, s2 = rv[w]
                rv[w] = (s1 + new - old, s2 + new * new - old * old)
        close = closes[i]
        for span in EMA_SPANS:
            _require_finite(ema[span], "exponential_moving_average")
        sma_value = _require_finite(
            _fsum_value(sma) / SMA_WINDOW, "simple_moving_average"
        )
        atr_value = _require_finite(_fsum_value(atr) / ATR_WINDOW, "average_true_range")
        ewma_value = _require_finite(
            (sigma_bps[i - 2] / BPS_PER_UNIT) * _ANNUALIZATION_FACTOR, "ewma_vol_168h"
        )
        row = {
            "ret_1h": log_return(close, closes[i - 1]),
            "ret_24h": log_return(close, closes[i - 24]),
            "ret_72h": log_return(close, closes[i - 72]),
            "ret_168h": log_return(close, closes[i - 168]),
            "ema_24": ema[24],
            "ema_72": ema[72],
            "ema_168": ema[168],
            "ema_dist_24": close / ema[24] - 1.0,
            "ema_dist_72": close / ema[72] - 1.0,
            "ema_dist_168": close / ema[168] - 1.0,
            "sma_4800": sma_value,
            "trend_200d": close / sma_value - 1.0,
            "breakout_720": close / max(closes[i + 1 - BREAKOUT_WINDOW : i + 1]) - 1.0,
            "ewma_vol_168h": ewma_value,
            "atr_24": atr_value / close,
        }
        for w in RV_WINDOWS:
            row[f"rv_{w}"] = _require_finite(
                _stdev(w, *rv[w]) * _ANNUALIZATION_FACTOR, "realized_volatility"
            )
        for name in FEATURE_NAMES:
            out[name].append(row[name])
    return first, {name: tuple(v) for name, v in out.items()}
