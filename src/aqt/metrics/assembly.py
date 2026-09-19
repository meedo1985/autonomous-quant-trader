"""Pure assembly of existing inactive paired-evaluation diagnostics.

This module is not a trial, report, gate, verdict, or promotion mechanism. It
only validates alignment and groups outputs from already-reviewed primitives.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Final

from aqt.backtest.engine import BacktestResult
from aqt.metrics.descriptive import DescriptiveMetrics, describe, paired_net_returns
from aqt.metrics.statistics import (
    CONVENTION,
    EffectiveSampleSize,
    PairedBootstrapInterval,
    PairedSharpeStatistics,
    ReplicateStream,
    effective_sample_size,
    paired_daily_returns,
    paired_sharpe_improvement_interval,
    paired_sharpe_statistics,
)

__all__ = [
    "AssemblyError",
    "InactivePairedEvaluation",
    "OpaqueIdentities",
    "assemble_inactive_paired_evaluation",
]

STATUS: Final = "INACTIVE_DIAGNOSTIC_ONLY"
_HORIZONS: Final = frozenset((24, 72, 168))


class AssemblyError(ValueError):
    """Invalid assembly-only input with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


@dataclass(frozen=True, slots=True)
class OpaqueIdentities:
    """Caller-supplied hashes that are checked for syntax and never resolved."""

    protocol_hash: str | None = None
    data_hash: str | None = None
    experiment_hash: str | None = None
    backtester_hash: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "protocol_hash",
            "data_hash",
            "experiment_hash",
            "backtester_hash",
        ):
            value = getattr(self, name)
            if value is not None and (
                not isinstance(value, str)
                or len(value) != 64
                or any(character not in "0123456789abcdef" for character in value)
            ):
                raise AssemblyError(
                    "INVALID_IDENTITY", f"{name} must be a lowercase SHA-256"
                )


@dataclass(frozen=True, slots=True)
class InactivePairedEvaluation:
    """Diagnostic grouping; neither ESS field is protocol effective decisions."""

    status: str
    convention: str
    symbol: str
    stress_multiplier: float
    day_count: int
    evaluation_start: datetime
    evaluation_end: datetime
    identities: OpaqueIdentities
    candidate_descriptive: DescriptiveMetrics
    benchmark_descriptive: DescriptiveMetrics
    paired_statistics: PairedSharpeStatistics
    candidate_effective_sample_size: EffectiveSampleSize
    benchmark_effective_sample_size: EffectiveSampleSize
    interval: PairedBootstrapInterval | None
    interval_absence_reason: str | None


def _expected_window(start: datetime, end: datetime) -> str:
    return json.dumps(
        [
            start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        ],
        separators=(",", ":"),
    )


def assemble_inactive_paired_evaluation(
    candidate: BacktestResult,
    benchmark: BacktestResult,
    *,
    horizon_hours: int,
    identities: OpaqueIdentities | None = None,
    stream: ReplicateStream | None = None,
) -> InactivePairedEvaluation:
    """Return an inactive in-memory view over existing production primitives."""
    if isinstance(horizon_hours, bool) or horizon_hours not in _HORIZONS:
        raise AssemblyError("INVALID_HORIZON", "horizon_hours must be 24, 72, or 168")
    if identities is not None and not isinstance(identities, OpaqueIdentities):
        raise AssemblyError("INVALID_IDENTITY", "OpaqueIdentities required")
    if stream is not None and not isinstance(stream, ReplicateStream):
        raise AssemblyError("INVALID_STREAM", "ReplicateStream required")

    # Enforce segment alignment before the stricter complete-day statistics.
    paired_net_returns(candidate, benchmark)
    daily = paired_daily_returns(candidate, benchmark)
    start = daily.candidate.days[0].astimezone(UTC)
    end = daily.candidate.days[-1].astimezone(UTC) + timedelta(days=1)

    interval = None
    interval_absence_reason: str | None = "STREAM_NOT_SUPPLIED"
    if stream is not None:
        if (
            stream.asset != daily.candidate.symbol
            or float(stream.cost_multiplier) != daily.candidate.cost_multiplier
            or stream.evaluation_window_id != _expected_window(start, end)
        ):
            raise AssemblyError(
                "STREAM_IDENTITY_MISMATCH",
                "stream asset, multiplier, or evaluation window differs from inputs",
            )
        interval = paired_sharpe_improvement_interval(
            daily.candidate.returns,
            daily.benchmark.returns,
            stream=stream,
        )
        interval_absence_reason = None

    return InactivePairedEvaluation(
        status=STATUS,
        convention=CONVENTION,
        symbol=daily.candidate.symbol,
        stress_multiplier=daily.candidate.cost_multiplier,
        day_count=len(daily.candidate.days),
        evaluation_start=start,
        evaluation_end=end,
        identities=identities or OpaqueIdentities(),
        candidate_descriptive=describe(candidate),
        benchmark_descriptive=describe(benchmark),
        paired_statistics=paired_sharpe_statistics(
            daily.candidate.returns, daily.benchmark.returns
        ),
        candidate_effective_sample_size=effective_sample_size(
            daily.candidate.returns, horizon_hours=horizon_hours
        ),
        benchmark_effective_sample_size=effective_sample_size(
            daily.benchmark.returns, horizon_hours=horizon_hours
        ),
        interval=interval,
        interval_absence_reason=interval_absence_reason,
    )
