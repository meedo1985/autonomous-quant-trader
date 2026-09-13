"""Canonical benchmark signal and exposure definitions for Cycle 1.

This module implements every benchmark in `specs/CANONICAL_BENCHMARKS_v1.md`
and nothing else. It is pure: no input is mutated, no clock is read, no
randomness is drawn, no file, network, or exchange is touched. The same
arguments always produce the same result.

Frozen sources encoded here:

* `specs/CANONICAL_BENCHMARKS_v1.md` — the five benchmarks `CASH`,
  `BUY_AND_HOLD`, `VOL_TARGET_BUY_AND_HOLD`, `CANONICAL_TREND`,
  `CANONICAL_TSMOM`, their signals, their exposure targets, and the shared
  rules: 1h bars, the same bar-semantics module as candidates, the same cost
  model, the same scheduled 00:00 UTC evaluation, the same 10 percentage-point
  rebalance band, the 24h minimum-holding rule for risk increases, and
  intraday band-triggered actions only in the exposure-reducing direction.
* `protocols/protocol_v1.yaml` `scope.bar_interval` = `1h`,
  `scope.scheduled_decision_anchor_utc` = `00:00`,
  `scope.hourly_signal_evaluation` = `true`,
  `scope.risk_increase_rule`, `scope.intraday_action_rule`,
  `scope.max_exposure_per_asset` = `1.0`, `scope.market` = `spot`,
  `exposure_mapping.rebalance_band_absolute` = `0.10`,
  `exposure_mapping.minimum_holding_hours_for_risk_increase` = `24`,
  `exposure_mapping.canonical_baseline_vol_target` = `0.60`,
  `exposure_mapping.default_sizing_vol_estimator` = `EWMA_168h`,
  `benchmarks.deployable_baseline` and `comparison.promotion_benchmark`
  = `VOL_TARGET_BUY_AND_HOLD`.
* `specs/BACKTESTER_SPEC_v1.md` items 2, 3, 5, 6 — decision at close(t),
  exposure clipped to `[0, 1]`, scheduled-only risk increases under the 24h
  minimum hold, intraday actions only for reductions across the 10pp band.
* `docs/RESEARCH_CONSTITUTION.md` section 6 — causal time semantics, no future
  leakage, no silent deletion or correction, UTC only, one tested
  bar-semantics module (`aqt.data.bars`, Task 2).

Causality
---------
A benchmark signal is computed *at a decision timestamp*, which is a bar close
in the Task 2 sense: `decision_time == bar.open_time + 1h` for the decision
bar `t`. Only bars whose close is at or before `decision_time` are read, so
bar `t` is the last observation used and no later bar can influence the
signal. Appending future bars to the series cannot change an already-computed
signal. Nothing here resolves a fill: baseline execution at open(t+1) stays in
`aqt.data.bars` and `aqt.backtest.costs`, where Tasks 2 and 3 put it.

Shared semantics are reused, not re-derived
-------------------------------------------
`CANONICAL_TREND` uses `aqt.features.factory.simple_moving_average` with the
Task 4 `sma_4800` window, so "200-day simple moving average" is the same
number as the `sma_4800` feature by construction. `CANONICAL_TSMOM` uses
`aqt.features.factory.log_return`. `VOL_TARGET_BUY_AND_HOLD` uses
`aqt.features.factory.ewma_volatility`, which delegates to the Task 3
estimator `aqt.backtest.costs.ewma_hourly_volatility_bps`; the frozen
benchmark's "EWMA of hourly log returns, half-life 168, annualised by
sqrt(8760)" is therefore identical to the `ewma_vol_168h` feature and to the
protocol's `EWMA_168h` sizing estimator by identity rather than by claim, as
`review/task3/SCIENTIFIC_DECISION.md` item 5 requires.

Warm-up and gaps
----------------
Each benchmark declares its own warm-up in `REQUIRED_HISTORY_BARS_BY_BENCHMARK`
and `REQUIRED_HISTORY_BARS` is the binding maximum over the whole set;
`CANONICAL_TREND` binds at 4800 bars. Insufficient history raises rather than
producing a partial, shortened, or padded value. Any hole in the supplied
history up to and including the decision bar raises as well, matching the
approved Task 3 convention in `review/task3/SCIENTIFIC_DECISION.md` item 4:
history is never deleted, forward-filled, interpolated, or silently sliced to
a post-gap segment. Duplicate open times, non-UTC timestamps, unaligned
timestamps, and internally inconsistent OHLC bars are rejected earlier, by
`aqt.data.bars`.

No silent correction
--------------------
Invalid input raises `CanonicalBenchmarkError`. Every function that takes a
`decision_time` resolves a decision, so it re-raises the underlying
`BarSemanticsError` from `aqt.data.bars` as `CanonicalBenchmarkError`, the
same way Tasks 3 and 4 do. `ExposureState.last_risk_increase_time` is validated
as a bare timestamp rather than as a decision, so a naive, non-UTC, or
unaligned value raises `BarSemanticsError` unchanged; the separate canonical
requirement that it sit on the scheduled `00:00` UTC anchor raises
`CanonicalBenchmarkError`. Exposure outside `[0, 1]` supplied by a caller is
rejected, never clipped; the only clip performed is the one the frozen
`clip(0.60 / vol, 0, 1)` prescribes.

Conventions the frozen spec leaves open
---------------------------------------
These are documented, not silently taken; they are listed again in
`review/task5/LOCAL_REPORT.md`.

1. The 10 percentage-point rebalance band is applied to **every** rebalance,
   scheduled and intraday, not only to intraday reductions. The frozen
   benchmark document lists the band among the shared rules ("the same 10
   percentage-point rebalance band where relevant") while
   `protocols/protocol_v1.yaml` `scope.intraday_action_rule` fixes it
   explicitly only for intraday reductions. Applying it uniformly is the
   lower-turnover reading and never manufactures a trade the narrower reading
   would forbid. It binds only for `VOL_TARGET_BUY_AND_HOLD`: every other
   benchmark targets exactly 0 or 1, so any change it ever requests is 1.0.
2. When a rebalance is allowed, exposure moves to the target in full rather
   than to the near edge of the band. The frozen documents name a band, not a
   partial-adjustment rule.
3. A zero annualised forecast volatility yields the full exposure
   `MAX_EXPOSURE`, which is the limit of the frozen
   `clip(0.60 / vol, 0, 1)` as `vol -> 0+`. The division is not performed, so
   no `ZeroDivisionError` and no silently defaulted value occurs; the case is
   reported through `BenchmarkSignal.signal` as a zero forecast.
4. `CANONICAL_TREND` maps `close > sma_4800` by direct comparison, and
   `CANONICAL_TSMOM` maps `log(close_t / close_{t-4320}) > 0` by direct
   comparison, both strict as written. `BenchmarkSignal.signal` carries the
   comparable scalar (`close / sma_4800 - 1` and the 180-day log return
   respectively) for audit, but the exposure never depends on that derived
   scalar's floating-point sign.
5. The 24h minimum-holding rule gates risk *increases* only. Reductions are
   never blocked by it, consistent with `protocols/protocol_v1.yaml`
   `owner_change_control.risk_decrease_immediate` = `true`, and a reduction
   does not restart the minimum-hold clock.
6. "200-day" and "180-day" are read as 4800 and 4320 1h bars, using the same
   `200 days x 24 bars` arithmetic `specs/FEATURE_FACTORY_v1.md` already uses
   for `sma_4800`.
7. The contiguity check covers the *whole* supplied history through the
   decision bar, not just the trailing window a benchmark reads. A hole
   therefore also refuses `CASH` and `BUY_AND_HOLD`, whose exposure needs no
   history at all. That is deliberate: silently accepting a series known to be
   broken, or quietly reading only the post-gap tail, is exactly what
   `review/task3/SCIENTIFIC_DECISION.md` item 4 forbids.
8. The 10 percentage-point band is a threshold on the *decimal* change the
   frozen documents describe, not on its binary rendering. A change stated as
   exactly 10 percentage points therefore reaches the band even when the
   subtraction yields `0.09999999999999998`, as `0.3 - 0.2` and `1.0 - 0.9`
   both do. `reaches_rebalance_band` is the one place this is decided, and
   `REBALANCE_BAND_TOLERANCE` bounds the slack at four units in the last place
   of `1.0`. The alternative — a literal `>= 0.10` — would make canonical
   exposure depend on floating-point representation.
9. The exported lookup tables `SIGNAL_LABELS` and
   `REQUIRED_HISTORY_BARS_BY_BENCHMARK` are read-only mappings. The benchmark
   set is frozen and hash-bound, so its behaviour must not be changeable at
   runtime without a code change.
10. A non-null `ExposureState.last_risk_increase_time` must be a timestamp at
    which the frozen rules permit a risk increase: 1h-aligned, UTC, at the
    scheduled `00:00` anchor. Anything else is a state the rules cannot
    produce, and it would give the 24h minimum-hold clock a noncanonical
    origin, so it is rejected rather than accepted or normalised.

Out of scope for this module, because they belong to later scheduled tasks:
the backtester itself, PnL, turnover, cost application, performance metrics,
promotion or eligibility logic, null models, allocation, data ingestion,
exchange or network access, credentials, trading or execution, ML or LLM
models, the research engine, the lockbox, the governor, and all Task 6+ work.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from aqt.data.bars import (
    BAR_INTERVAL,
    Bar,
    BarSemanticsError,
    BarSeries,
    require_aligned_utc,
)
from aqt.features.factory import (
    ANNUALIZATION_HOURS,
    SMA_WINDOW,
    FeatureFactoryError,
    ewma_volatility,
    hourly_log_returns,
    log_return,
    simple_moving_average,
)

__all__ = [
    "ANNUALIZATION_HOURS",
    "BENCHMARK_SET",
    "HOURS_PER_DAY",
    "MAX_EXPOSURE",
    "MIN_EXPOSURE",
    "MINIMUM_HOLD_FOR_RISK_INCREASE",
    "MINIMUM_HOLD_HOURS_FOR_RISK_INCREASE",
    "PROMOTION_BENCHMARK",
    "REBALANCE_BAND_ABSOLUTE",
    "REBALANCE_BAND_TOLERANCE",
    "REQUIRED_HISTORY_BARS",
    "REQUIRED_HISTORY_BARS_BY_BENCHMARK",
    "SCHEDULED_DECISION_ANCHOR_HOUR_UTC",
    "SIGNAL_LABELS",
    "TREND_SMA_DAYS",
    "TREND_SMA_WINDOW",
    "TSMOM_LOOKBACK_DAYS",
    "TSMOM_LOOKBACK_HOURS",
    "VOL_TARGET_ANNUALIZED",
    "VOL_TARGET_HALF_LIFE_HOURS",
    "BenchmarkId",
    "BenchmarkSignal",
    "CanonicalBenchmarkError",
    "ExposureState",
    "RebalanceAction",
    "RebalanceDecision",
    "annualized_forecast_volatility",
    "benchmark_signal",
    "benchmark_signals",
    "buy_and_hold_exposure",
    "canonical_trend_exposure",
    "canonical_tsmom_exposure",
    "cash_exposure",
    "is_scheduled_decision",
    "reaches_rebalance_band",
    "rebalance",
    "require_canonical_benchmark",
    "trend_reference",
    "tsmom_lookback_return",
    "vol_target_exposure",
]

HOURS_PER_DAY: Final[int] = 24
"""1h bars in one day; the frozen `200 days` / `180 days` conversion factor."""

MIN_EXPOSURE: Final[float] = 0.0
"""Long-only floor: `protocols/protocol_v1.yaml` `scope.market` = `spot`."""

MAX_EXPOSURE: Final[float] = 1.0
"""Unlevered cap: `protocol_v1.yaml` `scope.max_exposure_per_asset` = `1.0`."""

REBALANCE_BAND_ABSOLUTE: Final[float] = 0.10
"""Shared 10 percentage-point rebalance band."""

REBALANCE_BAND_TOLERANCE: Final[float] = 4.0 * math.ulp(MAX_EXPOSURE)
"""Binary-representation slack allowed when comparing a change with the band.

An exposure change of exactly 10 percentage points is frequently *not* the
float `0.10`: `0.3 - 0.2` and `1.0 - 0.9` both evaluate to
`0.09999999999999998`, because neither operand is exactly its decimal value.
The error in such a difference is bounded by the rounding error of the two
operands plus that of the subtraction, so for exposures in `[0, 1]` it cannot
exceed a small multiple of `ulp(1.0)`; four units of last place covers it with
room to spare. The slack is about `9e-16` in exposure units, roughly `1e-13`
percentage points: many orders of magnitude below any change the frozen
documents could intend to distinguish, so it widens no economically meaningful
behaviour — it only stops the frozen band from depending on binary
representation.
"""

MINIMUM_HOLD_HOURS_FOR_RISK_INCREASE: Final[int] = 24
"""Frozen minimum holding period before another risk increase, in hours."""

MINIMUM_HOLD_FOR_RISK_INCREASE: Final[timedelta] = timedelta(
    hours=MINIMUM_HOLD_HOURS_FOR_RISK_INCREASE
)
"""`MINIMUM_HOLD_HOURS_FOR_RISK_INCREASE` as a duration."""

SCHEDULED_DECISION_ANCHOR_HOUR_UTC: Final[int] = 0
"""`protocol_v1.yaml` `scope.scheduled_decision_anchor_utc` = `00:00`."""

VOL_TARGET_ANNUALIZED: Final[float] = 0.60
"""Annualised volatility target of `VOL_TARGET_BUY_AND_HOLD`."""

VOL_TARGET_HALF_LIFE_HOURS: Final[int] = 168
"""EWMA half-life of the benchmark volatility forecast, in hours."""

TREND_SMA_DAYS: Final[int] = 200
"""Simple-moving-average window of `CANONICAL_TREND`, in days."""

TREND_SMA_WINDOW: Final[int] = SMA_WINDOW
"""`CANONICAL_TREND` window in 1h bars; the Task 4 `sma_4800` window."""

TSMOM_LOOKBACK_DAYS: Final[int] = 180
"""Trailing log-return window of `CANONICAL_TSMOM`, in days."""

TSMOM_LOOKBACK_HOURS: Final[int] = TSMOM_LOOKBACK_DAYS * HOURS_PER_DAY
"""`CANONICAL_TSMOM` window in 1h bars: 180 days x 24."""


class CanonicalBenchmarkError(ValueError):
    """Raised when input violates the frozen canonical-benchmark rules."""


class BenchmarkId(StrEnum):
    """The five benchmarks in `specs/CANONICAL_BENCHMARKS_v1.md`.

    The set is closed: `protocol_v1.yaml` `benchmarks.benchmark_set_hash` and
    `promotion.benchmark_hash_must_match` mean adding, removing, or renaming a
    member changes the frozen benchmark set, which no code path here may do.
    """

    CASH = "CASH"
    BUY_AND_HOLD = "BUY_AND_HOLD"
    VOL_TARGET_BUY_AND_HOLD = "VOL_TARGET_BUY_AND_HOLD"
    CANONICAL_TREND = "CANONICAL_TREND"
    CANONICAL_TSMOM = "CANONICAL_TSMOM"


BENCHMARK_SET: Final[tuple[BenchmarkId, ...]] = (
    BenchmarkId.CASH,
    BenchmarkId.BUY_AND_HOLD,
    BenchmarkId.VOL_TARGET_BUY_AND_HOLD,
    BenchmarkId.CANONICAL_TREND,
    BenchmarkId.CANONICAL_TSMOM,
)
"""The complete benchmark set, in `specs/CANONICAL_BENCHMARKS_v1.md` order."""

PROMOTION_BENCHMARK: Final[BenchmarkId] = BenchmarkId.VOL_TARGET_BUY_AND_HOLD
"""`protocol_v1.yaml` `comparison.promotion_benchmark` / `deployable_baseline`.

Recorded here as the predeclared comparator. Eligibility, promotion, and
lockbox comparisons that use it belong to later scheduled tasks.
"""

_SIGNAL_LABELS: Final[dict[BenchmarkId, str]] = {
    BenchmarkId.CASH: "constant_zero_exposure",
    BenchmarkId.BUY_AND_HOLD: "constant_full_exposure",
    BenchmarkId.VOL_TARGET_BUY_AND_HOLD: "annualized_ewma_168h_forecast_vol",
    BenchmarkId.CANONICAL_TREND: "close_over_sma_4800_minus_1",
    BenchmarkId.CANONICAL_TSMOM: "trailing_180d_log_return",
}

SIGNAL_LABELS: Final[Mapping[BenchmarkId, str]] = MappingProxyType(_SIGNAL_LABELS)
"""What `BenchmarkSignal.signal` holds, per benchmark.

Exported read-only. The benchmark set and its definitions are frozen and
hash-bound, so a caller must not be able to alter what an identically named
benchmark reports without a code change; a mutable mapping would let the fixed
identity drift at runtime. The backing `dict` is module-private and is never
written after construction.
"""

_REQUIRED_HISTORY_BARS_BY_BENCHMARK: Final[dict[BenchmarkId, int]] = {
    BenchmarkId.CASH: 1,
    BenchmarkId.BUY_AND_HOLD: 1,
    BenchmarkId.VOL_TARGET_BUY_AND_HOLD: VOL_TARGET_HALF_LIFE_HOURS + 1,
    BenchmarkId.CANONICAL_TREND: TREND_SMA_WINDOW,
    BenchmarkId.CANONICAL_TSMOM: TSMOM_LOOKBACK_HOURS + 1,
}

REQUIRED_HISTORY_BARS_BY_BENCHMARK: Final[Mapping[BenchmarkId, int]] = MappingProxyType(
    _REQUIRED_HISTORY_BARS_BY_BENCHMARK
)
"""Contiguous 1h bars each benchmark needs through its decision bar.

`CASH` and `BUY_AND_HOLD` need only the decision bar itself, because their
exposure is constant; the bar is still required so the decision timestamp is
resolved against real data rather than accepted blindly.

Exported read-only, for the same reason as `SIGNAL_LABELS`: these warm-up
requirements decide what history a benchmark refuses to run on, so mutating
them at runtime would change validation behaviour without a code change.
"""

REQUIRED_HISTORY_BARS: Final[int] = max(REQUIRED_HISTORY_BARS_BY_BENCHMARK.values())
"""Bars required to evaluate the whole set; `CANONICAL_TREND` binds at 4800."""


def require_canonical_benchmark(benchmark: BenchmarkId | str) -> BenchmarkId:
    """Return `benchmark` as a `BenchmarkId`, rejecting anything outside the set.

    A string is accepted only if it is exactly a frozen benchmark name. The set
    is closed, so an unknown name is an error rather than an extension point.
    """
    if isinstance(benchmark, BenchmarkId):
        return benchmark
    for member in BENCHMARK_SET:
        if member.value == benchmark:
            return member
    raise CanonicalBenchmarkError(
        f"{benchmark!r} is not a canonical Cycle-1 benchmark; the frozen set is "
        f"{[member.value for member in BENCHMARK_SET]}"
    )


def _require_finite(value: float, name: str) -> float:
    if not math.isfinite(value):
        raise CanonicalBenchmarkError(f"{name} must be finite, got {value!r}")
    return float(value)


def _require_exposure(value: float, name: str) -> float:
    """Return `value` after checking it is a valid spot exposure in `[0, 1]`.

    Out-of-bounds exposure is rejected, not clipped: a caller asking for
    leverage or a short has a defect that must surface, and the frozen clip in
    `specs/BACKTESTER_SPEC_v1.md` item 3 constrains the benchmark's own target,
    which is in bounds by construction here.
    """
    _require_finite(value, name)
    if value < MIN_EXPOSURE or value > MAX_EXPOSURE:
        raise CanonicalBenchmarkError(
            f"{name} must lie in [{MIN_EXPOSURE}, {MAX_EXPOSURE}] for unlevered "
            f"long-only spot, got {value!r}"
        )
    return float(value)


def _clip_exposure(value: float) -> float:
    """Return `value` clipped into `[0, 1]`, as the frozen documents specify."""
    return min(MAX_EXPOSURE, max(MIN_EXPOSURE, _require_finite(value, "exposure")))


def reaches_rebalance_band(exposure_change: float) -> bool:
    """True when `exposure_change` reaches the frozen 10 percentage-point band.

    This is the single place the band threshold is evaluated, so every caller
    classifies the same change the same way. The comparison is representation-
    aware: a change the frozen documents describe as exactly 10 percentage
    points reaches the band even when binary floating point renders it as
    `0.09999999999999998`. See `REBALANCE_BAND_TOLERANCE` for the bound.
    """
    magnitude = abs(_require_finite(exposure_change, "exposure_change"))
    return magnitude >= REBALANCE_BAND_ABSOLUTE - REBALANCE_BAND_TOLERANCE


def is_scheduled_decision(decision_time: datetime) -> bool:
    """True when `decision_time` is the 00:00 UTC scheduled decision.

    Every 1h bar close is a decision timestamp, because
    `protocol_v1.yaml` `scope.hourly_signal_evaluation` is `true`; only the
    00:00 UTC one is *scheduled*, and only a scheduled decision may increase
    risk.
    """
    try:
        target = require_aligned_utc(
            decision_time, BAR_INTERVAL, field_name="decision_time"
        )
    except BarSemanticsError as error:
        raise CanonicalBenchmarkError(str(error)) from error
    return target.hour == SCHEDULED_DECISION_ANCHOR_HOUR_UTC


def cash_exposure() -> float:
    """Return the `CASH` exposure: 0 at every decision, without exception."""
    return MIN_EXPOSURE


def buy_and_hold_exposure() -> float:
    """Return the `BUY_AND_HOLD` target exposure: 100%.

    The frozen text is "enter 100% exposure at the first eligible execution and
    hold". The target is therefore constant; *when* it may first be acted on is
    decided by the shared scheduling rules in `rebalance`, not here.
    """
    return MAX_EXPOSURE


def annualized_forecast_volatility(bars: Sequence[Bar]) -> float:
    """Return the annualised EWMA forecast volatility of hourly log returns.

    The estimator is the Task 3 / Task 4 `EWMA_168h`: an EWMA of hourly close-
    to-close log returns with a 168-hour half-life, annualised by
    `sqrt(8760)`. It is reused rather than re-derived, so the benchmark and
    the `ewma_vol_168h` feature are the same number.
    """
    ordered = tuple(bars)
    try:
        return ewma_volatility(hourly_log_returns(ordered))
    except FeatureFactoryError as error:
        raise CanonicalBenchmarkError(str(error)) from error


def vol_target_exposure(annualized_forecast_vol: float) -> float:
    """Return `clip(0.60 / annualized_forecast_vol, 0, 1)`.

    A zero forecast returns `MAX_EXPOSURE`, the limit of the frozen expression
    as the forecast approaches zero from above; the division is not performed.
    A negative forecast is impossible from a standard deviation and is
    rejected rather than clipped.
    """
    forecast = _require_finite(annualized_forecast_vol, "annualized_forecast_vol")
    if forecast < 0.0:
        raise CanonicalBenchmarkError(
            f"annualized_forecast_vol must be non-negative, got {forecast!r}"
        )
    if forecast == 0.0:
        return MAX_EXPOSURE
    return _clip_exposure(VOL_TARGET_ANNUALIZED / forecast)


def trend_reference(closes: Sequence[float]) -> float:
    """Return the 200-day simple moving average of the trailing closes."""
    try:
        return simple_moving_average(closes, TREND_SMA_WINDOW)
    except FeatureFactoryError as error:
        raise CanonicalBenchmarkError(str(error)) from error


def canonical_trend_exposure(close: float, sma: float) -> float:
    """Return 1 if `close > sma`, else 0, as `CANONICAL_TREND` specifies."""
    latest = _require_finite(close, "close")
    reference = _require_finite(sma, "sma")
    return MAX_EXPOSURE if latest > reference else MIN_EXPOSURE


def tsmom_lookback_return(closes: Sequence[float]) -> float:
    """Return the trailing 180-day log return of the supplied closes."""
    observations = tuple(closes)
    if len(observations) < TSMOM_LOOKBACK_HOURS + 1:
        raise CanonicalBenchmarkError(
            f"tsmom_lookback_return needs {TSMOM_LOOKBACK_HOURS + 1} closes for "
            f"a {TSMOM_LOOKBACK_DAYS}-day window, got {len(observations)}"
        )
    try:
        return log_return(observations[-1], observations[-(TSMOM_LOOKBACK_HOURS + 1)])
    except FeatureFactoryError as error:
        raise CanonicalBenchmarkError(str(error)) from error


def canonical_tsmom_exposure(lookback_log_return: float) -> float:
    """Return 1 if the trailing 180-day log return is positive, else 0."""
    momentum = _require_finite(lookback_log_return, "lookback_log_return")
    return MAX_EXPOSURE if momentum > 0.0 else MIN_EXPOSURE


@dataclass(frozen=True, slots=True)
class BenchmarkSignal:
    """One canonical benchmark evaluated at one decision timestamp.

    `signal` is the benchmark's own comparable scalar, described by
    `SIGNAL_LABELS`; `target_exposure` is the frozen mapping of that signal and
    always lies in `[0, 1]`. `history_bars` is the number of contiguous 1h bars,
    ending at the decision bar, that produced the signal; it is provenance.
    """

    benchmark: BenchmarkId
    symbol: str
    decision_time: datetime
    close: float
    history_bars: int
    signal: float
    signal_label: str
    target_exposure: float
    scheduled: bool

    def __post_init__(self) -> None:
        _require_exposure(self.target_exposure, "target_exposure")


def benchmark_signal(
    benchmark: BenchmarkId | str,
    series: BarSeries,
    decision_time: datetime,
) -> BenchmarkSignal:
    """Evaluate one canonical benchmark at a bar close.

    `decision_time` is the close timestamp of the decision bar, so the bar
    opening at `decision_time - 1h` is the last observation used. `series` is
    read, never modified. Raises `CanonicalBenchmarkError` on insufficient or
    gapped history rather than filling, trimming, or dropping anything.
    """
    resolved = require_canonical_benchmark(benchmark)
    history = _history_through(
        series, decision_time, REQUIRED_HISTORY_BARS_BY_BENCHMARK[resolved]
    )
    decision_bar = history[-1]
    close = decision_bar.close

    signal: float
    target: float
    if resolved is BenchmarkId.CASH:
        signal = 0.0
        target = cash_exposure()
    elif resolved is BenchmarkId.BUY_AND_HOLD:
        signal = MAX_EXPOSURE
        target = buy_and_hold_exposure()
    elif resolved is BenchmarkId.VOL_TARGET_BUY_AND_HOLD:
        signal = annualized_forecast_volatility(history)
        target = vol_target_exposure(signal)
    elif resolved is BenchmarkId.CANONICAL_TREND:
        sma = trend_reference([bar.close for bar in history])
        signal = close / sma - 1.0
        target = canonical_trend_exposure(close, sma)
    else:
        lookback = tsmom_lookback_return([bar.close for bar in history])
        signal = lookback
        target = canonical_tsmom_exposure(lookback)

    return BenchmarkSignal(
        benchmark=resolved,
        symbol=series.symbol,
        decision_time=decision_bar.close_time,
        close=close,
        history_bars=len(history),
        signal=_require_finite(signal, "signal"),
        signal_label=SIGNAL_LABELS[resolved],
        target_exposure=target,
        scheduled=is_scheduled_decision(decision_bar.close_time),
    )


def benchmark_signals(
    benchmark: BenchmarkId | str,
    series: BarSeries,
    decision_times: Sequence[datetime],
) -> tuple[BenchmarkSignal, ...]:
    """Evaluate one benchmark at each decision timestamp, in the order given.

    Each signal is independent and causal at its own timestamp; no state
    carries between them, so the result is unchanged by the order of the input.
    """
    return tuple(
        benchmark_signal(benchmark, series, decision_time)
        for decision_time in decision_times
    )


class RebalanceAction(StrEnum):
    """What the shared scheduling/band/min-hold rules allow at one decision."""

    HOLD = "hold"
    SCHEDULED_INCREASE = "scheduled_increase"
    SCHEDULED_REDUCTION = "scheduled_reduction"
    INTRADAY_REDUCTION = "intraday_reduction"


@dataclass(frozen=True, slots=True)
class ExposureState:
    """Exposure held going into a decision, plus the minimum-hold clock.

    `last_risk_increase_time` is the decision timestamp of the most recent
    risk increase, or `None` when no risk increase has happened yet, in which
    case the 24h minimum hold cannot block anything.

    A non-null `last_risk_increase_time` must be a timestamp at which a risk
    increase could actually have occurred: a UTC bar close aligned to the 1h
    interval, at the scheduled `00:00` UTC anchor. The frozen rules let risk
    rise only at the scheduled decision, so any other value describes a state
    the rules cannot reach, and `rebalance` would then run its 24h minimum-hold
    clock off a noncanonical origin. Such a state is rejected rather than
    normalised, so a reconstructed or resumed path cannot silently adopt it.
    """

    current_exposure: float
    last_risk_increase_time: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "current_exposure",
            _require_exposure(self.current_exposure, "current_exposure"),
        )
        if self.last_risk_increase_time is not None:
            moment = require_aligned_utc(
                self.last_risk_increase_time,
                BAR_INTERVAL,
                field_name="last_risk_increase_time",
            )
            if moment.hour != SCHEDULED_DECISION_ANCHOR_HOUR_UTC:
                raise CanonicalBenchmarkError(
                    f"last_risk_increase_time {moment.isoformat()} is not the "
                    f"scheduled {SCHEDULED_DECISION_ANCHOR_HOUR_UTC:02d}:00 UTC "
                    "decision; risk increases happen only there, so no risk "
                    "increase can have occurred at this timestamp"
                )
            object.__setattr__(self, "last_risk_increase_time", moment)


@dataclass(frozen=True, slots=True)
class RebalanceDecision:
    """The outcome of applying the shared rules to one target exposure."""

    decision_time: datetime
    scheduled: bool
    current_exposure: float
    target_exposure: float
    new_exposure: float
    action: RebalanceAction
    reason: str
    last_risk_increase_time: datetime | None

    @property
    def traded(self) -> bool:
        """True when the decision changes exposure."""
        return self.action is not RebalanceAction.HOLD

    @property
    def next_state(self) -> ExposureState:
        """The exposure state this decision leaves behind."""
        return ExposureState(
            current_exposure=self.new_exposure,
            last_risk_increase_time=self.last_risk_increase_time,
        )


def rebalance(
    state: ExposureState,
    target_exposure: float,
    decision_time: datetime,
) -> RebalanceDecision:
    """Apply the shared scheduling, band, and minimum-hold rules to one decision.

    The rules, all from `specs/CANONICAL_BENCHMARKS_v1.md` and
    `protocols/protocol_v1.yaml` `scope`:

    * exposure never leaves `[0, 1]`;
    * a risk increase happens only at the 00:00 UTC scheduled decision and only
      when at least 24h have passed since the last risk increase;
    * an intraday action is allowed only to reduce exposure, and only when the
      target is at least 10 percentage points below the current exposure;
    * a change smaller than the 10 percentage-point band is not acted on.

    This decides a target path only. It computes no fill, no cost, no turnover
    and no PnL: those belong to the backtester, which is a later task.
    """
    target = _require_exposure(target_exposure, "target_exposure")
    try:
        moment = require_aligned_utc(
            decision_time, BAR_INTERVAL, field_name="decision_time"
        )
    except BarSemanticsError as error:
        raise CanonicalBenchmarkError(str(error)) from error
    if (
        state.last_risk_increase_time is not None
        and state.last_risk_increase_time > moment
    ):
        raise CanonicalBenchmarkError(
            f"last_risk_increase_time {state.last_risk_increase_time.isoformat()} "
            f"is after the decision at {moment.isoformat()}; a decision cannot "
            "look back on a future risk increase"
        )
    scheduled = is_scheduled_decision(moment)
    current = state.current_exposure
    delta = target - current

    def hold(reason: str) -> RebalanceDecision:
        return RebalanceDecision(
            decision_time=moment,
            scheduled=scheduled,
            current_exposure=current,
            target_exposure=target,
            new_exposure=current,
            action=RebalanceAction.HOLD,
            reason=reason,
            last_risk_increase_time=state.last_risk_increase_time,
        )

    if not reaches_rebalance_band(delta):
        return hold(
            f"|target - current| = {abs(delta)!r} is inside the "
            f"{REBALANCE_BAND_ABSOLUTE} rebalance band"
        )

    if delta < 0.0:
        if scheduled:
            action = RebalanceAction.SCHEDULED_REDUCTION
            reason = "scheduled 00:00 UTC reduction across the rebalance band"
        else:
            action = RebalanceAction.INTRADAY_REDUCTION
            reason = "intraday reduction: the target is below the band"
        return RebalanceDecision(
            decision_time=moment,
            scheduled=scheduled,
            current_exposure=current,
            target_exposure=target,
            new_exposure=target,
            action=action,
            reason=reason,
            last_risk_increase_time=state.last_risk_increase_time,
        )

    if not scheduled:
        return hold(
            "risk increases happen only at the "
            f"{SCHEDULED_DECISION_ANCHOR_HOUR_UTC:02d}:00 UTC scheduled "
            "decision; intraday actions may only reduce exposure"
        )
    if state.last_risk_increase_time is not None:
        elapsed = moment - state.last_risk_increase_time
        if elapsed < MINIMUM_HOLD_FOR_RISK_INCREASE:
            return hold(
                f"only {elapsed} has passed since the risk increase at "
                f"{state.last_risk_increase_time.isoformat()}; the minimum "
                f"holding period is {MINIMUM_HOLD_FOR_RISK_INCREASE}"
            )
    return RebalanceDecision(
        decision_time=moment,
        scheduled=scheduled,
        current_exposure=current,
        target_exposure=target,
        new_exposure=target,
        action=RebalanceAction.SCHEDULED_INCREASE,
        reason="scheduled 00:00 UTC risk increase past the minimum holding period",
        last_risk_increase_time=moment,
    )


def _history_through(
    series: BarSeries, decision_time: datetime, required_bars: int
) -> tuple[Bar, ...]:
    """Return the contiguous bars whose close is at or before `decision_time`.

    Raises when the decision bar is unknown, when the history through it is
    shorter than `required_bars`, or when it contains a hole. Nothing is
    filled, trimmed, or reset; an unresolved history is refused outright.
    """
    if series.interval != BAR_INTERVAL:
        raise CanonicalBenchmarkError(
            f"benchmarks require a {BAR_INTERVAL} series, got {series.interval}"
        )
    try:
        target = require_aligned_utc(
            decision_time, series.interval, field_name="decision_time"
        )
        decision_index = series.index_of(target - series.interval)
    except BarSemanticsError as error:
        raise CanonicalBenchmarkError(str(error)) from error
    history = series.bars[: decision_index + 1]
    if len(history) < required_bars:
        raise CanonicalBenchmarkError(
            f"decision at {target.isoformat()} has {len(history)} bar(s) of "
            f"history in {series.symbol}; {required_bars} contiguous 1h bars "
            "are required by the frozen canonical-benchmark windows"
        )
    _require_contiguous_hourly(history)
    return history


def _require_contiguous_hourly(bars: tuple[Bar, ...]) -> None:
    for position, bar in enumerate(bars):
        if bar.interval != BAR_INTERVAL:
            raise CanonicalBenchmarkError(
                f"bar {position} at {bar.open_time.isoformat()} has interval "
                f"{bar.interval}, expected {BAR_INTERVAL}"
            )
    for previous, current in zip(bars, bars[1:], strict=False):
        if current.open_time != previous.open_time + BAR_INTERVAL:
            raise CanonicalBenchmarkError(
                "benchmarks require contiguous 1h bars: "
                f"{current.open_time.isoformat()} does not follow "
                f"{previous.open_time.isoformat()} by {BAR_INTERVAL}"
            )
