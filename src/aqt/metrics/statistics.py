"""Inactive Task 12 primitives; see review/task12/IMPLEMENTATION_CONVENTIONS.md.

No research access, policy verdict, or governance activation. Inputs are supplied
objects; no files, environment, clock, network, or global RNG are read. Invalid
inputs raise StatisticsError(code); undefined arithmetic returns immutable results
with a reason. All reductions use fsum and preserve observation order.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from typing import Final

from aqt.backtest.engine import BacktestResult
from aqt.metrics.descriptive import MetricsError, segment_net_returns

CONVENTION: Final = "aqt.statistics.inactive.v1"
CONVENTION_DOCUMENT_SHA256: Final = (
    "f3ba9362c5f1512fd24600775df2aa048a7e701c8f40c8cb00e97c2c644f515c"
)
SEED_DOMAIN: Final = "aqt.statistics.stream.v1"
BOOTSTRAP_ATTEMPTS: Final = 2000
SCALE: Final = math.sqrt(365)
HOUR: Final = timedelta(hours=1)


class StatisticsError(ValueError):
    """Malformed input, carrying a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _finite(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise StatisticsError("INVALID_NUMBER", "expected a finite real number")
    try:
        result = float(value)
    except OverflowError as exc:
        raise StatisticsError(
            "INVALID_NUMBER", "not representable as binary64"
        ) from exc
    if not math.isfinite(result):
        raise StatisticsError("INVALID_NUMBER", "expected a finite real number")
    return result


def _series(values: Sequence[float]) -> tuple[float, ...]:
    if isinstance(values, str | bytes) or not isinstance(values, Sequence):
        raise StatisticsError("INVALID_SERIES", "expected a sequence of real numbers")
    return tuple(_finite(value) for value in values)


def _positive_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise StatisticsError("INVALID_ARGUMENT", "expected a positive integer")
    return value


def _pair(
    candidate: Sequence[float], benchmark: Sequence[float]
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    left, right = _series(candidate), _series(benchmark)
    if len(left) != len(right):
        raise StatisticsError("MISALIGNED_PAIR", "different observation counts")
    return left, right


def _computed(value: float) -> float:
    if not math.isfinite(value):
        raise ArithmeticError("nonfinite computed value")
    return value


@dataclass(frozen=True, slots=True)
class DailySeries:
    symbol: str
    cost_multiplier: float
    days: tuple[datetime, ...]
    returns: tuple[float, ...]
    convention: str = CONVENTION


@dataclass(frozen=True, slots=True)
class PairedDailyReturns:
    candidate: DailySeries
    benchmark: DailySeries
    difference: tuple[float, ...]
    convention: str = CONVENTION


def daily_net_returns(result: BacktestResult) -> DailySeries:
    """Require whole UTC days of 24 contiguous accepted holding segments."""
    try:
        segment_net_returns(result)
    except (MetricsError, ArithmeticError) as exc:
        raise StatisticsError("INVALID_RESULT", str(exc)) from exc
    segments = result.segments
    if not segments:
        raise StatisticsError("INSUFFICIENT_OBSERVATIONS", "empty hourly path")
    start = segments[0].execution_time
    if start.time().isoformat() != "00:00:00" or len(segments) % 24:
        raise StatisticsError("PARTIAL_DAY", "whole UTC days required")
    for index, segment in enumerate(segments):
        if any(
            stamp.utcoffset() != timedelta(0)
            for stamp in (segment.execution_time, segment.segment_end_time)
        ):
            raise StatisticsError("INVALID_TIMESTAMP", "UTC required on every segment")
        if segment.segment_end_time - segment.execution_time != HOUR:
            raise StatisticsError("IRREGULAR_SEGMENT", "one holding hour required")
        if segment.execution_time != start + index * HOUR:
            raise StatisticsError(
                "NONCONTIGUOUS_SEGMENTS", "missing or overlapping hour"
            )
    returns = []
    for index in range(0, len(segments), 24):
        value = (
            segments[index + 23].equity_after_return / segments[index].equity_before - 1
        )
        if not math.isfinite(value) or value <= -1:
            raise StatisticsError("NONFINITE_RESULT", "unrepresentable daily return")
        returns.append(value)
    return DailySeries(
        result.symbol,
        float(result.stress_multiplier),
        tuple(s.execution_time for s in segments[::24]),
        tuple(returns),
    )


def paired_daily_returns(
    candidate: BacktestResult, benchmark: BacktestResult
) -> PairedDailyReturns:
    left, right = daily_net_returns(candidate), daily_net_returns(benchmark)
    if (left.symbol, left.cost_multiplier, left.days) != (
        right.symbol,
        right.cost_multiplier,
        right.days,
    ):
        raise StatisticsError(
            "MISALIGNED_PAIR", "different identity or hourly boundaries"
        )
    difference = tuple(a - b for a, b in zip(left.returns, right.returns, strict=True))
    if any(not math.isfinite(value) for value in difference):
        raise StatisticsError("NONFINITE_RESULT", "unrepresentable paired difference")
    return PairedDailyReturns(left, right, difference)


@dataclass(frozen=True, slots=True)
class SharpeResult:
    observations: int
    reason: str | None = None
    mean: float | None = None
    variance: float | None = None
    daily: float | None = None
    scaled: float | None = None
    convention: str = CONVENTION

    @property
    def available(self) -> bool:
        return self.reason is None


def _sharpe(values: tuple[float, ...]) -> SharpeResult:
    n = len(values)
    if n < 2:
        return SharpeResult(n, "INSUFFICIENT_OBSERVATIONS")
    if any(not math.isfinite(x) for x in values):
        return SharpeResult(n, "NONFINITE_RESULT")
    if all(x == values[0] for x in values):
        return SharpeResult(n, "ZERO_VARIANCE")
    try:
        mean = _computed(math.fsum(values) / n)
        variance = _computed(math.fsum((x - mean) ** 2 for x in values) / (n - 1))
        if variance == 0:
            reason = (
                "ZERO_VARIANCE"
                if all(x == values[0] for x in values)
                else "NONFINITE_RESULT"
            )
            return SharpeResult(n, reason)
        daily = _computed(mean / math.sqrt(variance))
        return SharpeResult(
            n,
            mean=mean,
            variance=variance,
            daily=daily,
            scaled=_computed(SCALE * daily),
        )
    except (ArithmeticError, ValueError):
        return SharpeResult(n, "NONFINITE_RESULT")


def sharpe(values: Sequence[float]) -> SharpeResult:
    """Zero risk-free rate, sample variance, sqrt(365) scaled daily Sharpe."""
    return _sharpe(_series(values))


@dataclass(frozen=True, slots=True)
class PairedSharpeStatistics:
    candidate: SharpeResult
    benchmark: SharpeResult
    difference_series_sharpe: SharpeResult
    paired_sharpe_improvement: float | None
    reason: str | None
    convention: str = CONVENTION


def paired_sharpe_statistics(
    candidate: Sequence[float], benchmark: Sequence[float]
) -> PairedSharpeStatistics:
    left, right = _pair(candidate, benchmark)
    a, b = _sharpe(left), _sharpe(right)
    difference = tuple(x - y for x, y in zip(left, right, strict=True))
    d = _sharpe(difference)
    reason = a.reason or b.reason
    improvement = None
    if a.scaled is not None and b.scaled is not None:
        value = a.scaled - b.scaled
        if math.isfinite(value):
            improvement = value
        else:
            reason = "NONFINITE_RESULT"
    return PairedSharpeStatistics(a, b, d, improvement, reason)


def _autocovariance(centered: tuple[float, ...], lag: int) -> float:
    return _computed(
        math.fsum(centered[i] * centered[i - lag] for i in range(lag, len(centered)))
        / len(centered)
    )


@dataclass(frozen=True, slots=True)
class EffectiveSampleSize:
    observations: int
    horizon_days: int
    lag: int | None = None
    gamma_zero: float | None = None
    omega: float | None = None
    value: float | None = None
    method: str | None = None
    fallback_reason: str | None = None
    reason: str | None = None
    convention: str = CONVENTION

    @property
    def available(self) -> bool:
        return self.reason is None


def effective_sample_size(
    returns: Sequence[float], *, horizon_hours: int
) -> EffectiveSampleSize:
    """NW on supplied daily strategy returns; caller identifies the BTC series."""
    values = _series(returns)
    n, h = len(values), (_positive_int(horizon_hours) + 23) // 24
    result = EffectiveSampleSize(n, h)
    if n < 2:
        return replace(result, reason="INSUFFICIENT_OBSERVATIONS")
    lag = min(n - 1, max(h - 1, math.floor(4 * (n / 100) ** (2 / 9))))
    result = replace(result, lag=lag)
    try:
        mean = _computed(math.fsum(values) / n)
        centered = tuple(_computed(x - mean) for x in values)
        if all(x == values[0] for x in values):
            centered = (0.0,) * n
        gamma = _autocovariance(centered, 0)
        omega = _computed(
            gamma
            + 2
            * math.fsum(
                (1 - k / (lag + 1)) * _autocovariance(centered, k)
                for k in range(1, lag + 1)
            )
        )
        result = replace(result, gamma_zero=gamma, omega=omega)
        if gamma == 0 and any(x != values[0] for x in values):
            return replace(result, reason="NONFINITE_RESULT")
        if gamma == 0 or omega <= 0:
            return replace(
                result,
                value=n / h,
                method="HORIZON_FALLBACK",
                fallback_reason="ZERO_VARIANCE"
                if gamma == 0
                else "NONPOSITIVE_LONG_RUN_VARIANCE",
            )
        raw = _computed(n * gamma / omega)
        return replace(result, value=max(1.0, min(float(n), raw)), method="NEWEY_WEST")
    except (ArithmeticError, ValueError):
        return replace(result, reason="NONFINITE_RESULT")


@dataclass(frozen=True, slots=True)
class InfluenceSeries:
    values: tuple[float, ...] | None
    reason: str | None = None
    convention: str = CONVENTION


def _influence(values: tuple[float, ...], result: SharpeResult) -> tuple[float, ...]:
    assert (
        result.mean is not None
        and result.variance is not None
        and result.daily is not None
    )
    population_variance = _computed(
        math.fsum((x - result.mean) ** 2 for x in values) / len(values)
    )
    scale = math.sqrt(population_variance)
    standardized = tuple(_computed((x - result.mean) / scale) for x in values)
    return tuple(_computed(u - result.daily / 2 * (u * u - 1)) for u in standardized)


def paired_sharpe_improvement_influence(
    candidate: Sequence[float], benchmark: Sequence[float]
) -> InfluenceSeries:
    """Population-centered scale, sample Sharpe coefficient; no annual multiplier."""
    left, right = _pair(candidate, benchmark)
    a, b = _sharpe(left), _sharpe(right)
    if a.reason or b.reason:
        return InfluenceSeries(None, a.reason or b.reason)
    try:
        return InfluenceSeries(
            tuple(
                _computed(x - y)
                for x, y in zip(_influence(left, a), _influence(right, b), strict=True)
            )
        )
    except (ArithmeticError, ValueError):
        return InfluenceSeries(None, "NONFINITE_RESULT")


@dataclass(frozen=True, slots=True)
class BlockLength:
    observations: int
    value: float | None = None
    reason: str | None = None
    window: int | None = None
    maximum_lag: int | None = None
    critical_value: float | None = None
    cutoff: int | None = None
    bandwidth: int | None = None
    gamma_zero: float | None = None
    long_run_variance: float | None = None
    capital_g: float | None = None
    maximum: int | None = None
    raw: float | None = None
    clipping: str | None = None
    degenerate: bool = False
    convention: str = CONVENTION

    @property
    def restart_probability(self) -> float | None:
        return None if self.value is None else 1 / self.value


def block_length(influence: Sequence[float]) -> BlockLength:
    """Owner-approved PPW-2009 constant and explicit gamma/n pilot convention."""
    values = _series(influence)
    n = len(values)
    result = BlockLength(n)
    if n < 16:
        return replace(result, reason="INSUFFICIENT_OBSERVATIONS")
    window = max(5, math.floor(math.log10(n)))
    maximum_lag = min(n - 1, math.ceil(math.sqrt(n)) + window)
    critical = 2 * math.sqrt(math.log10(n) / n)
    maximum = min(n, math.ceil(min(3 * math.sqrt(n), n / 3)))
    result = replace(
        result,
        window=window,
        maximum_lag=maximum_lag,
        critical_value=critical,
        maximum=maximum,
    )
    if all(x == values[0] for x in values):
        return replace(result, value=1.0, raw=0.0, gamma_zero=0.0, degenerate=True)
    try:
        mean = _computed(math.fsum(values) / n)
        centered = tuple(_computed(x - mean) for x in values)
        gammas = tuple(_autocovariance(centered, k) for k in range(maximum_lag + 1))
        result = replace(result, gamma_zero=gammas[0])
        if gammas[0] == 0:
            if any(x != values[0] for x in values):
                return replace(result, reason="NONFINITE_RESULT")
            return replace(result, value=1.0, raw=0.0, degenerate=True)
        correlations = tuple(_computed(g / gammas[0]) for g in gammas)
        cutoff = next(
            (
                k
                for k in range(1, maximum_lag - window + 2)
                if all(abs(correlations[j]) < critical for j in range(k, k + window))
            ),
            None,
        )
        bandwidth = maximum_lag if cutoff is None else min(2 * cutoff, maximum_lag)
        weights = tuple(
            1.0 if k / bandwidth <= 0.5 else 2 * (1 - k / bandwidth)
            for k in range(1, bandwidth + 1)
        )
        variance = _computed(
            gammas[0]
            + 2 * math.fsum(weight * gammas[k] for k, weight in enumerate(weights, 1))
        )
        capital_g = _computed(
            2 * math.fsum(weight * k * gammas[k] for k, weight in enumerate(weights, 1))
        )
        result = replace(
            result,
            cutoff=cutoff,
            bandwidth=bandwidth,
            long_run_variance=variance,
            capital_g=capital_g,
        )
        if variance <= 0:
            return replace(result, reason="NONPOSITIVE_LONG_RUN_VARIANCE")
        denominator = variance**2
        if denominator == 0:
            return replace(result, reason="NONFINITE_RESULT")
        raw = _computed((_computed(capital_g**2 * n) / denominator) ** (1 / 3))
        return replace(
            result,
            raw=raw,
            value=min(float(maximum), max(1.0, raw)),
            clipping="LOWER" if raw < 1 else "UPPER" if raw > maximum else None,
        )
    except (ArithmeticError, ValueError):
        return replace(result, reason="NONFINITE_RESULT")


@dataclass(frozen=True, slots=True)
class ReplicateStream:
    trial_seed_hex: str
    statistical_convention_hash: str
    asset: str
    cost_multiplier: str
    evaluation_window_id: str
    purpose: str = "paired_sharpe_ci"

    def __post_init__(self) -> None:
        for value in (self.trial_seed_hex, self.statistical_convention_hash):
            if (
                not isinstance(value, str)
                or len(value) != 64
                or any(c not in "0123456789abcdef" for c in value)
            ):
                raise StatisticsError("INVALID_IDENTITY", "lowercase SHA-256 required")
        if self.statistical_convention_hash != CONVENTION_DOCUMENT_SHA256:
            raise StatisticsError(
                "INVALID_IDENTITY", "unrecognized statistical convention hash"
            )
        if (
            self.asset not in ("BTCUSDT", "ETHUSDT")
            or self.cost_multiplier not in ("1.0", "1.5", "2.0", "3.0")
            or self.purpose != "paired_sharpe_ci"
        ):
            raise StatisticsError("INVALID_IDENTITY", "unknown asset, cost or purpose")
        try:
            window = json.loads(self.evaluation_window_id)
            if not isinstance(window, list) or len(window) != 2:
                raise ValueError("expected window pair")
            dates = tuple(datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ") for x in window)
            if dates[0] >= dates[1] or any(
                d.time().isoformat() != "00:00:00" for d in dates
            ):
                raise ValueError("ordered midnight boundaries required")
            canonical = json.dumps(
                [d.strftime("%Y-%m-%dT%H:%M:%SZ") for d in dates], separators=(",", ":")
            )
            if canonical != self.evaluation_window_id:
                raise ValueError("noncanonical window")
        except (TypeError, ValueError) as exc:
            raise StatisticsError(
                "INVALID_IDENTITY", "canonical UTC evaluation window required"
            ) from exc


def replicate_seed_material(
    stream: ReplicateStream, *, output_length: int, replicate_index: int
) -> bytes:
    if not isinstance(stream, ReplicateStream):
        raise StatisticsError("INVALID_IDENTITY", "ReplicateStream required")
    length = _positive_int(output_length)
    if (
        isinstance(replicate_index, bool)
        or not isinstance(replicate_index, int)
        or not 0 <= replicate_index < BOOTSTRAP_ATTEMPTS
    ):
        raise StatisticsError("INVALID_ARGUMENT", "replicate index must be 0..1999")
    return json.dumps(
        [
            SEED_DOMAIN,
            stream.trial_seed_hex,
            stream.statistical_convention_hash,
            stream.purpose,
            stream.asset,
            stream.cost_multiplier,
            stream.evaluation_window_id,
            length,
            replicate_index,
        ],
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def replicate_seed(
    stream: ReplicateStream, *, output_length: int, replicate_index: int
) -> str:
    return hashlib.sha256(
        replicate_seed_material(
            stream, output_length=output_length, replicate_index=replicate_index
        )
    ).hexdigest()


def _uniform_index(generator: random.Random, count: int) -> int:
    drawn = generator.getrandbits(count.bit_length())
    while drawn >= count:
        drawn = generator.getrandbits(count.bit_length())
    return drawn


def bootstrap_indices(
    stream: ReplicateStream, *, observations: int, replicate_index: int, block: float
) -> tuple[int, ...]:
    n = _positive_int(observations)
    length = _finite(block)
    if not 1 <= length <= n:
        raise StatisticsError("INVALID_ARGUMENT", "block must lie in [1, observations]")
    seed = replicate_seed(stream, output_length=n, replicate_index=replicate_index)
    generator = random.Random(int.from_bytes(bytes.fromhex(seed), "big"))
    indices = [_uniform_index(generator, n)]
    for _ in range(1, n):
        indices.append(
            _uniform_index(generator, n)
            if generator.random() < 1 / length
            else (indices[-1] + 1) % n
        )
    return tuple(indices)


def type_seven_quantile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(_series(values))
    q = _finite(probability)
    if not ordered or not 0 <= q <= 1:
        raise StatisticsError(
            "INVALID_ARGUMENT", "nonempty sample and probability in [0,1] required"
        )
    position = (len(ordered) - 1) * q
    j = math.floor(position)
    if j == len(ordered) - 1:
        return ordered[j]
    fraction = position - j
    return (1 - fraction) * ordered[j] + fraction * ordered[j + 1]


@dataclass(frozen=True, slots=True)
class PairedBootstrapInterval:
    observations: int
    stream: ReplicateStream
    block: BlockLength
    python_runtime: str
    reason: str | None = None
    point_estimate: float | None = None
    lower: float | None = None
    upper: float | None = None
    attempts: int = BOOTSTRAP_ATTEMPTS
    attempts_executed: int = 0
    invalid_replicates: tuple[tuple[int, str], ...] = ()
    replicate_statistics: tuple[float | None, ...] = ()
    confidence_level: float = 0.90
    convention: str = CONVENTION

    @property
    def available(self) -> bool:
        return self.reason is None


def paired_sharpe_improvement_interval(
    candidate: Sequence[float], benchmark: Sequence[float], *, stream: ReplicateStream
) -> PairedBootstrapInterval:
    """Exactly 2000 attempts after valid original statistics/block selection.

    Invalid attempts retain index/reason; no replacements, early stop or policy
    decision. Original-input failure executes zero replicates and records that.
    """
    left, right = _pair(candidate, benchmark)
    if not isinstance(stream, ReplicateStream):
        raise StatisticsError("INVALID_IDENTITY", "ReplicateStream required")
    n = len(left)
    observed = paired_sharpe_statistics(left, right)
    influence = paired_sharpe_improvement_influence(left, right)
    selected = (
        block_length(influence.values)
        if influence.values is not None
        else BlockLength(n, reason=influence.reason)
    )
    runtime = f"{sys.implementation.name} {sys.version}"
    result = PairedBootstrapInterval(
        n,
        stream,
        selected,
        runtime,
        reason=observed.reason or influence.reason or selected.reason,
        point_estimate=observed.paired_sharpe_improvement,
    )
    if result.reason:
        return result
    assert selected.value is not None
    statistics: list[float | None] = []
    invalid: list[tuple[int, str]] = []
    for i in range(BOOTSTRAP_ATTEMPTS):
        indices = bootstrap_indices(
            stream, observations=n, replicate_index=i, block=selected.value
        )
        a, b = (
            _sharpe(tuple(left[j] for j in indices)),
            _sharpe(tuple(right[j] for j in indices)),
        )
        value = None if a.scaled is None or b.scaled is None else a.scaled - b.scaled
        if value is None or not math.isfinite(value):
            invalid.append((i, a.reason or b.reason or "NONFINITE_RESULT"))
            statistics.append(None)
        else:
            statistics.append(value)
    result = replace(
        result,
        attempts_executed=BOOTSTRAP_ATTEMPTS,
        invalid_replicates=tuple(invalid),
        replicate_statistics=tuple(statistics),
    )
    if invalid:
        return replace(result, reason="INVALID_REPLICATE")
    finite = tuple(x for x in statistics if x is not None)
    return replace(
        result,
        lower=type_seven_quantile(finite, 0.05),
        upper=type_seven_quantile(finite, 0.95),
    )
