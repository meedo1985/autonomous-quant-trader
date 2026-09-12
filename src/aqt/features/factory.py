"""Causal deterministic feature factory for the frozen Cycle-1 features.

This module implements every feature in `specs/FEATURE_FACTORY_v1.md` and
nothing else. It is pure: no input is mutated, no clock is read, no randomness
is drawn, no file, network, or exchange is touched. The same arguments always
produce the same result.

Frozen sources encoded here:

* `specs/FEATURE_FACTORY_v1.md` "Returns", "Trend", "Volatility" — the
  complete Cycle-1 feature list and each formula and window.
* `specs/FEATURE_FACTORY_v1.md` closing rule: no volume-derived alpha, spread,
  order-book, trade-imbalance, or seasonality features in Cycle 1.
* `protocols/protocol_v1.yaml` `scope.bar_interval` = `1h` and
  `feature_factory.frozen` = `true`.
* `docs/RESEARCH_CONSTITUTION.md` section 6: causal time semantics, no future
  leakage, no silent deletion or correction, UTC only, one tested
  bar-semantics module (`aqt.data.bars`, Task 2).

Causality
---------
A feature row is computed *at a decision timestamp*, which is a bar close in
the Task 2 sense: `decision_time == bar.open_time + 1h` for the decision bar
`t`. Only bars whose close is at or before `decision_time` are read, so bar
`t` is the last observation used and no later bar can influence the row.
Appending future bars to the series cannot change an already-computed row.

Warm-up and gaps
----------------
`REQUIRED_HISTORY_BARS` contiguous 1h bars ending at the decision bar are
required; the binding constraint is `sma_4800`. Insufficient history raises
rather than producing a partial, shortened, or padded value. Any hole in the
supplied history up to and including the decision bar raises as well, matching
the approved Task 3 convention in `review/task3/SCIENTIFIC_DECISION.md` item
4: history is never deleted, forward-filled, interpolated, or silently sliced
to a post-gap segment. Duplicate open times, non-UTC timestamps, unaligned
timestamps, and internally inconsistent OHLC bars are rejected earlier, by
`aqt.data.bars`.

Forbidden inputs
----------------
The Cycle-1 feature set is closed. Only `open_time`, `high`, `low` and `close`
are read: `Bar.volume` is never an input to any formula, and no timestamp is
ever decomposed into hour-of-day, day-of-week, or any other calendar term.
`require_cycle1_features` rejects any requested name outside the frozen list,
including the explicitly forbidden families in `FORBIDDEN_INPUT_KINDS`.

Conventions the frozen spec leaves open
---------------------------------------
These are documented, not silently taken; they are listed again in
`review/task4/LOCAL_REPORT.md`.

1. `EMA(close, span=N)` uses `alpha = 2 / (N + 1)`, seeded with the simple
   mean of the first `N` closes of the supplied history and then recursed
   forward over every later close. `EMA` and `EWMA_std` are therefore
   functions of the whole supplied contiguous history, not of a fixed trailing
   slice; `FeatureRow.history_bars` records how many bars produced the row.
2. `std(...)` for `rv_24`, `rv_168`, `rv_720` is the sample standard deviation
   (`ddof = 1`) of the trailing hourly log returns, consistent with the Task 3
   estimator.
3. `EWMA_std(ret_1h, halflife=168)` reuses the Task 3 estimator
   (`aqt.backtest.costs.ewma_hourly_volatility_bps`) unchanged, so the
   `EWMA_168h` label is identical by construction rather than by claim, as
   `review/task3/SCIENTIFIC_DECISION.md` item 5 requires. The feature is
   stricter in one respect: it requires the full 168-return initialisation and
   refuses the partial-seed regime the cost model tolerates.
4. `ATR(high, low, close, window=24)` is the simple arithmetic mean of the
   last 24 true ranges, where
   `TR_t = max(high_t - low_t, |high_t - close_{t-1}|, |low_t - close_{t-1}|)`.
   A trailing simple average is used rather than Wilder smoothing because the
   frozen spec names a window, not a smoothing constant.
5. Annualisation uses `sqrt(8760)` exactly as written in the frozen spec.

Out of scope for this module, because they belong to later scheduled tasks:
data ingestion, exchange or network access, credentials, trading or execution,
strategies, portfolio or allocation logic, ML or LLM models, backtester
orchestration, canonical benchmarks, the governor, and all Task 5+ work.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Final

from aqt.backtest.costs import (
    BPS_PER_UNIT,
    EWMA_HALF_LIFE_HOURS,
    VOLATILITY_INIT_RETURNS,
    CostModelError,
    ewma_hourly_volatility_bps,
)
from aqt.data.bars import (
    BAR_INTERVAL,
    Bar,
    BarSemanticsError,
    BarSeries,
    require_aligned_utc,
)

__all__ = [
    "ANNUALIZATION_HOURS",
    "ATR_WINDOW",
    "BREAKOUT_WINDOW",
    "EMA_SPANS",
    "EWMA_VOL_HALF_LIFE_HOURS",
    "FEATURE_NAMES",
    "FORBIDDEN_INPUT_KINDS",
    "REQUIRED_HISTORY_BARS",
    "RETURN_LAGS",
    "RV_WINDOWS",
    "SMA_WINDOW",
    "FeatureFactoryError",
    "FeatureRow",
    "average_true_range",
    "compute_features",
    "compute_feature_rows",
    "ewma_volatility",
    "exponential_moving_average",
    "hourly_log_returns",
    "log_return",
    "realized_volatility",
    "require_cycle1_features",
    "rolling_maximum",
    "simple_moving_average",
    "true_range",
]

ANNUALIZATION_HOURS: Final[int] = 8760
"""Hours per year used by the frozen `* sqrt(8760)` annualisation."""

RETURN_LAGS: Final[tuple[int, ...]] = (1, 24, 72, 168)
"""Lags in hours for `ret_1h`, `ret_24h`, `ret_72h`, `ret_168h`."""

EMA_SPANS: Final[tuple[int, ...]] = (24, 72, 168)
"""Spans in hours for `ema_24`, `ema_72`, `ema_168` and their distances."""

SMA_WINDOW: Final[int] = 4800
"""Window of `sma_4800`: 200 days of 1h bars."""

BREAKOUT_WINDOW: Final[int] = 720
"""Window of `breakout_720`: 30 days of 1h bars."""

RV_WINDOWS: Final[tuple[int, ...]] = (24, 168, 720)
"""Trailing hourly-return counts for `rv_24`, `rv_168`, `rv_720`."""

ATR_WINDOW: Final[int] = 24
"""Window of `atr_24`, in true ranges."""

EWMA_VOL_HALF_LIFE_HOURS: Final[int] = EWMA_HALF_LIFE_HOURS
"""Half-life of `ewma_vol_168h`, reused from the Task 3 estimator."""

REQUIRED_HISTORY_BARS: Final[int] = max(
    max(RETURN_LAGS) + 1,
    max(EMA_SPANS),
    SMA_WINDOW,
    BREAKOUT_WINDOW,
    max(RV_WINDOWS) + 1,
    VOLATILITY_INIT_RETURNS + 1,
    ATR_WINDOW + 1,
)
"""Contiguous 1h bars required through the decision bar; `sma_4800` binds."""

FEATURE_NAMES: Final[tuple[str, ...]] = (
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
"""The closed Cycle-1 feature set, in `specs/FEATURE_FACTORY_v1.md` order."""

FORBIDDEN_INPUT_KINDS: Final[tuple[str, ...]] = (
    "quote_volume",
    "volume",
    "trade_count",
    "spread",
    "order_book",
    "depth",
    "trade_imbalance",
    "order_flow",
    "seasonality",
    "hour_of_day",
    "day_of_week",
    "month_of_year",
)
"""Input families `specs/FEATURE_FACTORY_v1.md` excludes from Cycle 1."""

_EMA_ALPHAS: Final[dict[int, float]] = {s: 2.0 / (s + 1.0) for s in EMA_SPANS}

_ANNUALIZATION_FACTOR: Final[float] = math.sqrt(ANNUALIZATION_HOURS)


class FeatureFactoryError(ValueError):
    """Raised when input violates the frozen feature-factory rules."""


def require_cycle1_features(names: Sequence[str]) -> tuple[str, ...]:
    """Return `names` unchanged after checking each is a frozen Cycle-1 feature.

    Any other name raises, including the volume, order-book, and seasonality
    families the frozen spec excludes. `FORBIDDEN_INPUT_KINDS` is ordered
    most-specific-first so the reported family is the narrowest match. The set
    is closed: a new name would change the feature-factory hash and end the
    active cycle, which no code path here is allowed to do.
    """
    requested = tuple(names)
    for name in requested:
        if name in FEATURE_NAMES:
            continue
        lowered = name.lower()
        for forbidden in FORBIDDEN_INPUT_KINDS:
            if forbidden in lowered:
                raise FeatureFactoryError(
                    f"feature {name!r} uses the forbidden Cycle-1 input family "
                    f"{forbidden!r}; specs/FEATURE_FACTORY_v1.md allows no "
                    "volume-derived alpha, spread, order-book, trade-imbalance, "
                    "or seasonality features"
                )
        raise FeatureFactoryError(
            f"{name!r} is not a frozen Cycle-1 feature; the allowed set is "
            f"{list(FEATURE_NAMES)}"
        )
    return requested


def _require_finite(value: float, name: str) -> float:
    if not math.isfinite(value):
        raise FeatureFactoryError(f"{name} must be finite, got {value!r}")
    return float(value)


def _require_price(value: float, name: str) -> float:
    if not math.isfinite(value) or value <= 0.0:
        raise FeatureFactoryError(
            f"{name} must be a finite, strictly positive price, got {value!r}"
        )
    return float(value)


def _require_window(
    values: Sequence[float], window: int, name: str
) -> tuple[float, ...]:
    if window < 1:
        raise FeatureFactoryError(f"{name} window must be positive, got {window}")
    observations = tuple(values)
    if len(observations) < window:
        raise FeatureFactoryError(
            f"{name} needs {window} observation(s), got {len(observations)}"
        )
    return observations[-window:]


def log_return(current_close: float, past_close: float) -> float:
    """Return `log(current_close / past_close)` for two positive closes."""
    current = _require_price(current_close, "current_close")
    past = _require_price(past_close, "past_close")
    return _require_finite(math.log(current / past), "log_return")


def hourly_log_returns(bars: Sequence[Bar]) -> tuple[float, ...]:
    """Return close-to-close hourly log returns over contiguous 1h bars.

    A return is never computed across a hole, because that would not be an
    hourly return.
    """
    ordered = tuple(bars)
    _require_contiguous_hourly(ordered)
    if len(ordered) < 2:
        raise FeatureFactoryError(
            f"hourly returns need at least 2 bars, got {len(ordered)}"
        )
    return tuple(
        log_return(current.close, previous.close)
        for previous, current in zip(ordered, ordered[1:], strict=False)
    )


def simple_moving_average(closes: Sequence[float], window: int) -> float:
    """Return the mean of the last `window` closes."""
    observations = _require_window(closes, window, "simple_moving_average")
    for index, value in enumerate(observations):
        _require_price(value, f"closes[{index}]")
    return _require_finite(math.fsum(observations) / window, "simple_moving_average")


def exponential_moving_average(closes: Sequence[float], span: int) -> float:
    """Return the EMA of `closes` with `alpha = 2 / (span + 1)`.

    The recursion is seeded with the simple mean of the first `span` closes
    and then advanced over every later close, so the result depends on the
    whole supplied history rather than on a trailing slice.
    """
    if span < 1:
        raise FeatureFactoryError(
            f"exponential_moving_average span must be positive, got {span}"
        )
    observations = tuple(closes)
    if len(observations) < span:
        raise FeatureFactoryError(
            f"exponential_moving_average needs {span} close(s) to seed, got "
            f"{len(observations)}"
        )
    for index, value in enumerate(observations):
        _require_price(value, f"closes[{index}]")
    alpha = _EMA_ALPHAS.get(span, 2.0 / (span + 1.0))
    state = math.fsum(observations[:span]) / span
    for value in observations[span:]:
        state = alpha * value + (1.0 - alpha) * state
    return _require_finite(state, "exponential_moving_average")


def rolling_maximum(closes: Sequence[float], window: int) -> float:
    """Return the maximum of the last `window` closes."""
    observations = _require_window(closes, window, "rolling_maximum")
    for index, value in enumerate(observations):
        _require_price(value, f"closes[{index}]")
    return max(observations)


def realized_volatility(returns: Sequence[float], window: int) -> float:
    """Return the annualised sample standard deviation of trailing returns."""
    if window < 2:
        raise FeatureFactoryError(
            f"realized_volatility needs a window of at least 2, got {window}"
        )
    observations = _require_window(returns, window, "realized_volatility")
    for index, value in enumerate(observations):
        _require_finite(value, f"returns[{index}]")
    return _require_finite(
        statistics.stdev(observations) * _ANNUALIZATION_FACTOR,
        "realized_volatility",
    )


def ewma_volatility(returns: Sequence[float]) -> float:
    """Return the annualised EWMA volatility of hourly log returns.

    Delegates to the Task 3 estimator so the `EWMA_168h` label is identical by
    construction; the returns are passed in basis points and the result is
    converted back to a fraction before annualisation. The full 168-return
    initialisation is required here, unlike in the cost model.
    """
    observations = tuple(returns)
    if len(observations) < VOLATILITY_INIT_RETURNS:
        raise FeatureFactoryError(
            f"ewma_vol_168h needs {VOLATILITY_INIT_RETURNS} hourly returns to "
            f"complete its initialisation, got {len(observations)}"
        )
    for index, value in enumerate(observations):
        _require_finite(value, f"returns[{index}]")
    try:
        sigma_bps = ewma_hourly_volatility_bps(
            tuple(value * BPS_PER_UNIT for value in observations)
        )
    except CostModelError as error:
        raise FeatureFactoryError(str(error)) from error
    return _require_finite(
        (sigma_bps / BPS_PER_UNIT) * _ANNUALIZATION_FACTOR, "ewma_vol_168h"
    )


def true_range(bar: Bar, previous_close: float) -> float:
    """Return the true range of `bar` given the previous bar's close."""
    previous = _require_price(previous_close, "previous_close")
    return _require_finite(
        max(
            bar.high - bar.low,
            abs(bar.high - previous),
            abs(bar.low - previous),
        ),
        "true_range",
    )


def average_true_range(bars: Sequence[Bar], window: int = ATR_WINDOW) -> float:
    """Return the mean of the last `window` true ranges of contiguous bars.

    `window + 1` bars are required: the earliest one only supplies the close
    that the first true range needs.
    """
    if window < 1:
        raise FeatureFactoryError(
            f"average_true_range window must be positive, got {window}"
        )
    ordered = tuple(bars)
    _require_contiguous_hourly(ordered)
    if len(ordered) < window + 1:
        raise FeatureFactoryError(
            f"average_true_range needs {window + 1} bars for a {window}-bar "
            f"window, got {len(ordered)}"
        )
    ranges = [
        true_range(ordered[index], ordered[index - 1].close)
        for index in range(len(ordered) - window, len(ordered))
    ]
    return _require_finite(math.fsum(ranges) / window, "average_true_range")


def _require_contiguous_hourly(bars: tuple[Bar, ...]) -> None:
    for position, bar in enumerate(bars):
        if bar.interval != BAR_INTERVAL:
            raise FeatureFactoryError(
                f"bar {position} at {bar.open_time.isoformat()} has interval "
                f"{bar.interval}, expected {BAR_INTERVAL}"
            )
    for previous, current in zip(bars, bars[1:], strict=False):
        if current.open_time != previous.open_time + BAR_INTERVAL:
            raise FeatureFactoryError(
                "features require contiguous 1h bars: "
                f"{current.open_time.isoformat()} does not follow "
                f"{previous.open_time.isoformat()} by {BAR_INTERVAL}"
            )


@dataclass(frozen=True, slots=True)
class FeatureRow:
    """The frozen Cycle-1 features at one decision timestamp.

    Every value is causal at `decision_time`. `history_bars` is the number of
    contiguous 1h bars, ending at the decision bar, that produced the row; it
    is provenance, not a feature, and is not part of `FEATURE_NAMES`.
    """

    symbol: str
    decision_time: datetime
    close: float
    history_bars: int
    ret_1h: float
    ret_24h: float
    ret_72h: float
    ret_168h: float
    ema_24: float
    ema_72: float
    ema_168: float
    ema_dist_24: float
    ema_dist_72: float
    ema_dist_168: float
    sma_4800: float
    trend_200d: float
    breakout_720: float
    rv_24: float
    rv_168: float
    rv_720: float
    ewma_vol_168h: float
    atr_24: float

    def as_dict(self) -> dict[str, float]:
        """Return the feature values only, keyed by frozen feature name."""
        return {name: float(getattr(self, name)) for name in FEATURE_NAMES}


def compute_features(series: BarSeries, decision_time: datetime) -> FeatureRow:
    """Compute the frozen Cycle-1 features at a bar close.

    `decision_time` is the close timestamp of the decision bar, so the bar
    opening at `decision_time - 1h` is the last observation used. `series` is
    read, never modified. Raises `FeatureFactoryError` on insufficient or
    gapped history rather than filling, trimming, or dropping anything.
    """
    history = _history_through(series, decision_time)
    closes = tuple(bar.close for bar in history)
    returns = hourly_log_returns(history)
    close = closes[-1]

    ema_values = {span: exponential_moving_average(closes, span) for span in EMA_SPANS}
    sma_4800 = simple_moving_average(closes, SMA_WINDOW)
    breakout_reference = rolling_maximum(closes, BREAKOUT_WINDOW)
    rv_values = {window: realized_volatility(returns, window) for window in RV_WINDOWS}
    atr = average_true_range(history, ATR_WINDOW)

    return FeatureRow(
        symbol=series.symbol,
        decision_time=history[-1].close_time,
        close=close,
        history_bars=len(history),
        ret_1h=log_return(close, closes[-2]),
        ret_24h=log_return(close, closes[-25]),
        ret_72h=log_return(close, closes[-73]),
        ret_168h=log_return(close, closes[-169]),
        ema_24=ema_values[24],
        ema_72=ema_values[72],
        ema_168=ema_values[168],
        ema_dist_24=close / ema_values[24] - 1.0,
        ema_dist_72=close / ema_values[72] - 1.0,
        ema_dist_168=close / ema_values[168] - 1.0,
        sma_4800=sma_4800,
        trend_200d=close / sma_4800 - 1.0,
        breakout_720=close / breakout_reference - 1.0,
        rv_24=rv_values[24],
        rv_168=rv_values[168],
        rv_720=rv_values[720],
        ewma_vol_168h=ewma_volatility(returns),
        atr_24=atr / close,
    )


def compute_feature_rows(
    series: BarSeries,
    decision_times: Sequence[datetime],
) -> tuple[FeatureRow, ...]:
    """Compute one `FeatureRow` per decision timestamp, in the order given.

    Each row is independent and causal at its own timestamp; no state carries
    between rows, so the result is unchanged by the order of the input.
    """
    return tuple(
        compute_features(series, decision_time) for decision_time in decision_times
    )


def _history_through(series: BarSeries, decision_time: datetime) -> tuple[Bar, ...]:
    """Return the contiguous bars whose close is at or before `decision_time`.

    Raises when the decision bar is unknown, when the history through it is
    shorter than `REQUIRED_HISTORY_BARS`, or when it contains a hole. Nothing
    is filled, trimmed, or reset; an unresolved history is refused outright.
    """
    if series.interval != BAR_INTERVAL:
        raise FeatureFactoryError(
            f"features require a {BAR_INTERVAL} series, got {series.interval}"
        )
    try:
        target = require_aligned_utc(
            decision_time, series.interval, field_name="decision_time"
        )
        decision_index = series.index_of(target - series.interval)
    except BarSemanticsError as error:
        raise FeatureFactoryError(str(error)) from error
    history = series.bars[: decision_index + 1]
    if len(history) < REQUIRED_HISTORY_BARS:
        raise FeatureFactoryError(
            f"decision at {target.isoformat()} has {len(history)} bar(s) of "
            f"history in {series.symbol}; {REQUIRED_HISTORY_BARS} contiguous "
            "1h bars are required by the frozen Cycle-1 windows"
        )
    _require_contiguous_hourly(history)
    return history
