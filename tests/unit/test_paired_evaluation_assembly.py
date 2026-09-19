"""Synthetic evidence for the inactive paired-evaluation assembler."""

from __future__ import annotations

import builtins
import io
import json
import math
import os
import random
import socket
import subprocess
import urllib.request
from dataclasses import FrozenInstanceError, fields, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from aqt.backtest.costs import CostBreakdown
from aqt.backtest.engine import BacktestResult, SegmentRecord
from aqt.benchmarks.canonical import RebalanceAction
from aqt.metrics.assembly import (
    AssemblyError,
    OpaqueIdentities,
    assemble_inactive_paired_evaluation,
)
from aqt.metrics.descriptive import MetricsError, describe
from aqt.metrics.statistics import (
    CONVENTION_DOCUMENT_SHA256,
    ReplicateStream,
    paired_daily_returns,
    paired_sharpe_improvement_interval,
    paired_sharpe_statistics,
)

START = datetime(2020, 1, 1, tzinfo=UTC)
HOUR = timedelta(hours=1)
BREAKDOWN = CostBreakdown(10.0, "fallback", 2.0, 1.0, 20.0, 1.0)


def _result(
    daily_returns: tuple[float, ...],
    *,
    symbol: str = "BTCUSDT",
    multiplier: float = 1.0,
) -> BacktestResult:
    equity = 1.0
    segments = []
    for index in range(24 * len(daily_returns)):
        moment = START + index * HOUR
        gross = daily_returns[index // 24] if index % 24 == 0 else 0.0
        after = equity * (1.0 + gross)
        segments.append(
            SegmentRecord(
                index,
                moment,
                moment,
                moment + HOUR,
                100.0,
                gross,
                1.0,
                1.0,
                1.0,
                1.0,
                RebalanceAction.HOLD,
                "synthetic",
                None,
                0.0,
                BREAKDOWN,
                0.0,
                equity,
                equity,
                after,
            )
        )
        equity = after
    return BacktestResult(symbol, multiplier, tuple(segments))


def _stream(days: int, **changes: str) -> ReplicateStream:
    end = START + timedelta(days=days)
    window = json.dumps(
        [START.strftime("%Y-%m-%dT%H:%M:%SZ"), end.strftime("%Y-%m-%dT%H:%M:%SZ")],
        separators=(",", ":"),
    )
    return replace(
        ReplicateStream(
            "a" * 64,
            CONVENTION_DOCUMENT_SHA256,
            "BTCUSDT",
            "1.0",
            window,
        ),
        **changes,
    )


def test_assembly_is_an_immutable_exact_passthrough() -> None:
    candidate = _result((0.01, -0.02, 0.03, 0.005))
    benchmark = _result((0.002, 0.004, -0.001, 0.003))
    original_candidate, original_benchmark = candidate, benchmark
    rng = random.getstate()

    result = assemble_inactive_paired_evaluation(
        candidate,
        benchmark,
        horizon_hours=24,
        identities=OpaqueIdentities(protocol_hash="b" * 64),
    )
    daily = paired_daily_returns(candidate, benchmark)

    assert result.status == "INACTIVE_DIAGNOSTIC_ONLY"
    assert result.day_count == 4
    assert result.evaluation_start == START
    assert result.evaluation_end == START + timedelta(days=4)
    assert result.candidate_descriptive == describe(candidate)
    assert result.benchmark_descriptive == describe(benchmark)
    assert result.paired_statistics == paired_sharpe_statistics(
        daily.candidate.returns, daily.benchmark.returns
    )
    assert result.interval is None
    assert result.interval_absence_reason == "STREAM_NOT_SUPPLIED"
    assert result.candidate_effective_sample_size.horizon_days == 1
    assert result.benchmark_effective_sample_size.horizon_days == 1
    assert result == assemble_inactive_paired_evaluation(
        candidate,
        benchmark,
        horizon_hours=24,
        identities=OpaqueIdentities(protocol_hash="b" * 64),
    )
    assert (candidate, benchmark) == (original_candidate, original_benchmark)
    assert random.getstate() == rng
    with pytest.raises(FrozenInstanceError):
        result.day_count = 5  # type: ignore[misc]


def test_no_verdict_fields_and_fail_closed_boundaries() -> None:
    names = {
        field.name
        for field in fields(
            assemble_inactive_paired_evaluation(
                _result((0.01, 0.02)), _result((0.0, 0.01)), horizon_hours=72
            )
        )
    }
    prohibited = (
        "pass",
        "fail",
        "eligible",
        "promot",
        "gate",
        "verdict",
        "decision",
        "approve",
        "reject",
    )
    assert not any(token in name for name in names for token in prohibited)

    with pytest.raises(AssemblyError, match="INVALID_HORIZON"):
        assemble_inactive_paired_evaluation(
            _result((0.01, 0.02)), _result((0.0, 0.01)), horizon_hours=48
        )
    with pytest.raises(AssemblyError, match="INVALID_IDENTITY"):
        OpaqueIdentities(data_hash="A" * 64)
    with pytest.raises(MetricsError, match="symbol mismatch"):
        assemble_inactive_paired_evaluation(
            _result((0.01, 0.02)),
            _result((0.0, 0.01), symbol="ETHUSDT"),
            horizon_hours=24,
        )


def test_swap_negates_paired_estimands() -> None:
    candidate = _result((0.01, -0.02, 0.03, 0.005))
    benchmark = _result((0.002, 0.004, -0.001, 0.003))
    forward = assemble_inactive_paired_evaluation(
        candidate, benchmark, horizon_hours=168
    )
    reverse = assemble_inactive_paired_evaluation(
        benchmark, candidate, horizon_hours=168
    )

    assert forward.candidate_descriptive == reverse.benchmark_descriptive
    assert forward.benchmark_descriptive == reverse.candidate_descriptive
    assert forward.paired_statistics.paired_sharpe_improvement == pytest.approx(
        -reverse.paired_statistics.paired_sharpe_improvement
    )
    assert forward.paired_statistics.difference_series_sharpe.mean == pytest.approx(
        -reverse.paired_statistics.difference_series_sharpe.mean
    )


def test_hand_calculated_sharpe_estimands_and_ess_attribution() -> None:
    candidate = _result((0.1, -0.1))
    benchmark = _result((0.0, 0.1))
    result = assemble_inactive_paired_evaluation(candidate, benchmark, horizon_hours=72)

    assert result.evaluation_start == START
    assert result.evaluation_end == START + timedelta(days=2)
    assert result.paired_statistics.candidate.mean == pytest.approx(0.0)
    assert result.paired_statistics.candidate.variance == pytest.approx(0.02)
    assert result.paired_statistics.benchmark.mean == pytest.approx(0.05)
    assert result.paired_statistics.benchmark.variance == pytest.approx(0.005)
    assert result.paired_statistics.paired_sharpe_improvement == pytest.approx(
        -math.sqrt(365 / 2)
    )
    assert result.paired_statistics.difference_series_sharpe.mean == pytest.approx(
        -0.05
    )
    assert result.paired_statistics.difference_series_sharpe.variance == pytest.approx(
        0.045
    )
    assert result.candidate_effective_sample_size.horizon_days == 3
    assert result.benchmark_effective_sample_size.horizon_days == 3
    assert result.candidate_effective_sample_size.method == "NEWEY_WEST"
    assert result.benchmark_effective_sample_size.method == "NEWEY_WEST"


def test_ess_explicit_fallback_is_attributed_to_each_leg() -> None:
    result = assemble_inactive_paired_evaluation(
        _result((0.0, 0.0)), _result((0.0, 0.0)), horizon_hours=168
    )
    for effective in (
        result.candidate_effective_sample_size,
        result.benchmark_effective_sample_size,
    ):
        assert effective.horizon_days == 7
        assert effective.method == "HORIZON_FALLBACK"
        assert effective.fallback_reason == "ZERO_VARIANCE"


def test_caller_stream_is_checked_and_interval_is_exact_passthrough() -> None:
    candidate_returns = tuple(0.001 * ((index % 7) - 2) for index in range(16))
    benchmark_returns = tuple(0.0005 * ((index % 5) - 1) for index in range(16))
    candidate = _result(candidate_returns)
    benchmark = _result(benchmark_returns)
    stream = _stream(16)

    assembled = assemble_inactive_paired_evaluation(
        candidate, benchmark, horizon_hours=24, stream=stream
    )
    daily = paired_daily_returns(candidate, benchmark)
    assert assembled.interval == paired_sharpe_improvement_interval(
        daily.candidate.returns, daily.benchmark.returns, stream=stream
    )
    assert assembled.interval_absence_reason is None

    mismatches = (
        _stream(17),
        _stream(16, asset="ETHUSDT"),
        _stream(16, cost_multiplier="2.0"),
    )
    for mismatch in mismatches:
        with pytest.raises(AssemblyError, match="STREAM_IDENTITY_MISMATCH"):
            assemble_inactive_paired_evaluation(
                candidate,
                benchmark,
                horizon_hours=24,
                stream=mismatch,
            )

    with pytest.raises(AssemblyError, match="INVALID_STREAM"):
        assemble_inactive_paired_evaluation(
            candidate,
            benchmark,
            horizon_hours=24,
            stream=object(),  # type: ignore[arg-type]
        )


def test_off_protocol_multiplier_cannot_bind_to_rounded_stream() -> None:
    with pytest.raises(AssemblyError, match="STREAM_IDENTITY_MISMATCH"):
        assemble_inactive_paired_evaluation(
            _result(tuple(0.001 * index for index in range(16)), multiplier=1.04),
            _result(tuple(0.0005 * index for index in range(16)), multiplier=1.04),
            horizon_hours=24,
            stream=_stream(16),
        )


def test_stream_path_uses_no_selected_external_entry_points(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _result(tuple(0.001 * ((index % 7) - 2) for index in range(16)))
    benchmark = _result(tuple(0.0005 * ((index % 5) - 1) for index in range(16)))
    stream = _stream(16)
    rng = random.getstate()

    def denied(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("external access attempted")

    monkeypatch.setattr(builtins, "open", denied)
    monkeypatch.setattr(io, "open", denied)
    monkeypatch.setattr(Path, "open", denied)
    monkeypatch.setattr(os, "open", denied)
    monkeypatch.setattr(os, "getenv", denied)
    monkeypatch.setattr(subprocess, "run", denied)
    monkeypatch.setattr(subprocess, "Popen", denied)
    monkeypatch.setattr(socket, "socket", denied)
    monkeypatch.setattr(urllib.request, "urlopen", denied)

    result = assemble_inactive_paired_evaluation(
        candidate, benchmark, horizon_hours=24, stream=stream
    )
    assert result.status == "INACTIVE_DIAGNOSTIC_ONLY"
    assert result.interval is not None
    assert result.interval_absence_reason is None
    assert result.interval.stream == stream
    assert random.getstate() == rng
