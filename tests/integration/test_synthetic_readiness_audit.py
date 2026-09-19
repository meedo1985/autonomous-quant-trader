"""Synthetic plumbing audit from canonical benchmarks through Task 12 metrics.

This test makes no research, eligibility, promotion, exchange, or trading claim.
"""

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
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from aqt.backtest.engine import (
    BacktestError,
    BacktestResult,
    ExposureTarget,
    run_backtest,
)
from aqt.benchmarks.canonical import (
    BENCHMARK_SET,
    REQUIRED_HISTORY_BARS,
    BenchmarkId,
    BenchmarkSignal,
    CanonicalBenchmarkError,
    RebalanceAction,
    benchmark_signals,
)
from aqt.data.bars import BAR_INTERVAL, Bar, BarSemanticsError, BarSeries
from aqt.metrics.descriptive import describe, paired_net_returns
from aqt.metrics.statistics import (
    CONVENTION_DOCUMENT_SHA256,
    ReplicateStream,
    StatisticsError,
    daily_net_returns,
    paired_daily_returns,
    paired_sharpe_improvement_interval,
    paired_sharpe_statistics,
)

_START = datetime(2020, 1, 1, tzinfo=UTC)
_DAYS = 16
_DECISION_COUNT = 24 * _DAYS
_EVALUATION_START = _START + REQUIRED_HISTORY_BARS * BAR_INTERVAL
_EVALUATION_END = _EVALUATION_START + timedelta(days=_DAYS)
_BAR_COUNT = REQUIRED_HISTORY_BARS + _DECISION_COUNT + 1


def _price(index: int) -> float:
    return (
        100.0
        + 5.0 * math.sin(2.0 * math.pi * index / 120.0)
        + 5.0 * math.sin(2.0 * math.pi * index / 17.0)
        + 0.002 * index
    )


def _bar(index: int, *, price: float | None = None) -> Bar:
    value = _price(index) if price is None else price
    close = value * (1.0 + 0.0001 * math.sin(2.0 * math.pi * index / 7.0))
    return Bar(
        open_time=_START + index * BAR_INTERVAL,
        open=value,
        high=max(value, close) + 0.01,
        low=min(value, close) - 0.01,
        close=close,
        volume=1.0,
    )


def _series(*, mutate_after: int | None = None) -> BarSeries:
    return BarSeries(
        symbol="BTCUSDT",
        bars=tuple(
            _bar(
                index,
                price=(
                    _price(index) + 25.0
                    if mutate_after is not None and index >= mutate_after
                    else None
                ),
            )
            for index in range(_BAR_COUNT)
        ),
    )


def _decision_times(count: int = _DECISION_COUNT) -> tuple[datetime, ...]:
    return tuple(_EVALUATION_START + index * BAR_INTERVAL for index in range(count))


def _targets(signals: tuple[BenchmarkSignal, ...]) -> tuple[ExposureTarget, ...]:
    return tuple(
        ExposureTarget(signal.decision_time, signal.target_exposure)
        for signal in signals
    )


@dataclass(frozen=True, slots=True)
class _AuditFixture:
    series: BarSeries
    signals: dict[BenchmarkId, tuple[BenchmarkSignal, ...]]
    targets: dict[BenchmarkId, tuple[ExposureTarget, ...]]
    results: dict[BenchmarkId, BacktestResult]


@pytest.fixture(scope="module")
def audit() -> _AuditFixture:
    series = _series()
    signals = {
        benchmark: benchmark_signals(benchmark, series, _decision_times())
        for benchmark in BENCHMARK_SET
    }
    targets = {benchmark: _targets(path) for benchmark, path in signals.items()}
    results = {
        benchmark: run_backtest(series, targets[benchmark])
        for benchmark in BENCHMARK_SET
    }
    return _AuditFixture(series, signals, targets, results)


def _stream() -> ReplicateStream:
    window = json.dumps(
        [
            _EVALUATION_START.strftime("%Y-%m-%dT%H:%M:%SZ"),
            _EVALUATION_END.strftime("%Y-%m-%dT%H:%M:%SZ"),
        ],
        separators=(",", ":"),
    )
    return ReplicateStream(
        trial_seed_hex="0" * 64,
        statistical_convention_hash=CONVENTION_DOCUMENT_SHA256,
        asset="BTCUSDT",
        cost_multiplier="1.0",
        evaluation_window_id=window,
    )


def test_all_canonical_benchmarks_replay_through_production_engine(
    audit: _AuditFixture,
) -> None:
    for benchmark in BENCHMARK_SET:
        signals = audit.signals[benchmark]
        targets = audit.targets[benchmark]
        result = audit.results[benchmark]
        assert len(signals) == len(targets) == len(result.segments) == _DECISION_COUNT
        assert result == run_backtest(audit.series, targets)
        for signal, target, segment in zip(
            signals, targets, result.segments, strict=True
        ):
            assert signal.decision_time == target.decision_time
            assert signal.target_exposure == target.requested_exposure
            assert (
                segment.decision_time == segment.execution_time == target.decision_time
            )
            assert segment.segment_end_time == segment.execution_time + BAR_INTERVAL
            assert (
                segment.execution_price
                == audit.series.bar_at(segment.execution_time).open
            )
            assert all(
                0.0 <= exposure <= 1.0
                for exposure in (
                    target.requested_exposure,
                    segment.clipped_target,
                    segment.exposure,
                )
            )
            if segment.action is RebalanceAction.SCHEDULED_INCREASE:
                assert segment.decision_time.hour == 0
                assert segment.exposure > segment.held_weight_before
            if segment.action is RebalanceAction.INTRADAY_REDUCTION:
                assert segment.exposure < segment.held_weight_before

    assert all(
        segment.traded == 0.0 for segment in audit.results[BenchmarkId.CASH].segments
    )
    vol_targets = audit.targets[BenchmarkId.VOL_TARGET_BUY_AND_HOLD]
    buy_hold_targets = audit.targets[BenchmarkId.BUY_AND_HOLD]
    assert vol_targets != buy_hold_targets
    assert any(0.0 < target.requested_exposure < 1.0 for target in vol_targets)
    assert any(
        segment.action is RebalanceAction.HOLD
        and 0.0 < abs(segment.clipped_target - segment.held_weight_before) < 0.1
        for segment in audit.results[BenchmarkId.VOL_TARGET_BUY_AND_HOLD].segments
    )


def test_canonical_paths_reach_inactive_statistical_primitives(
    audit: _AuditFixture,
) -> None:
    assert _DAYS >= 16
    vol_target = audit.results[BenchmarkId.VOL_TARGET_BUY_AND_HOLD]
    buy_and_hold = audit.results[BenchmarkId.BUY_AND_HOLD]
    vol_target_summary = describe(vol_target)
    buy_and_hold_summary = describe(buy_and_hold)
    hourly_difference = paired_net_returns(vol_target, buy_and_hold)
    paired = paired_daily_returns(vol_target, buy_and_hold)
    statistics = paired_sharpe_statistics(
        paired.candidate.returns, paired.benchmark.returns
    )
    interval = paired_sharpe_improvement_interval(
        paired.candidate.returns,
        paired.benchmark.returns,
        stream=_stream(),
    )

    assert (
        vol_target_summary.segment_count
        == buy_and_hold_summary.segment_count
        == _DECISION_COUNT
    )
    assert len(hourly_difference) == _DECISION_COUNT
    assert len(paired.candidate.returns) == len(paired.benchmark.returns) == _DAYS
    assert statistics.candidate.available and statistics.benchmark.available
    assert statistics.paired_sharpe_improvement is not None
    assert interval.available and interval.attempts_executed == 2000
    assert not interval.invalid_replicates
    assert interval.reason is None
    assert interval.block.long_run_variance is not None
    assert interval.block.long_run_variance > 0.0
    assert interval.block.value is not None


def test_future_suffix_cannot_change_prefix_evidence() -> None:
    count = 48
    original = _series()
    changed = _series(mutate_after=REQUIRED_HISTORY_BARS + count + 1)
    times = _decision_times(count)
    first_signals = benchmark_signals(BenchmarkId.CANONICAL_TREND, original, times)
    second_signals = benchmark_signals(BenchmarkId.CANONICAL_TREND, changed, times)
    first = run_backtest(original, _targets(first_signals))
    second = run_backtest(changed, _targets(second_signals))

    assert changed.bars != original.bars
    assert first_signals == second_signals
    assert first == second
    assert describe(first) == describe(second)
    assert daily_net_returns(first) == daily_net_returns(second)


def test_cross_layer_faults_fail_closed_at_the_owning_boundary(
    audit: _AuditFixture,
) -> None:
    with pytest.raises(BarSemanticsError, match="UTC-aware"):
        Bar(datetime(2020, 1, 1), 1.0, 1.0, 1.0, 1.0, 1.0)

    gap = BarSeries(
        symbol="BTCUSDT",
        bars=audit.series.bars[:100] + audit.series.bars[101:],
    )
    with pytest.raises(CanonicalBenchmarkError, match="contiguous"):
        benchmark_signals(BenchmarkId.CASH, gap, _decision_times(1))
    with pytest.raises(BacktestError, match="missing 1 interval"):
        run_backtest(gap, audit.targets[BenchmarkId.CASH][:1])

    truncated = BarSeries(
        symbol="BTCUSDT",
        bars=audit.series.bars[: REQUIRED_HISTORY_BARS + 1],
    )
    with pytest.raises(BacktestError, match="no following open"):
        run_backtest(truncated, audit.targets[BenchmarkId.CASH][:1])

    result = audit.results[BenchmarkId.BUY_AND_HOLD]
    other_symbol = replace(result, symbol="ETHUSDT")
    with pytest.raises(StatisticsError, match="MISALIGNED_PAIR"):
        paired_daily_returns(result, other_symbol)

    damaged = replace(
        result,
        segments=(
            replace(result.segments[0], equity_after_return=math.nan),
            *result.segments[1:],
        ),
    )
    with pytest.raises(StatisticsError, match="INVALID_RESULT"):
        daily_net_returns(damaged)

    with pytest.raises(StatisticsError, match="INVALID_IDENTITY"):
        replace(_stream(), evaluation_window_id="not-canonical")


def test_post_import_pipeline_avoids_guarded_external_access_and_preserves_inputs(
    audit: _AuditFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    bars_before = tuple(
        (
            bar.open_time,
            bar.open,
            bar.high,
            bar.low,
            bar.close,
            bar.volume,
            bar.interval,
        )
        for bar in audit.series.bars
    )
    targets = audit.targets[BenchmarkId.CANONICAL_TREND]
    targets_before = tuple(
        (target.decision_time, target.requested_exposure) for target in targets
    )
    rng_before = random.getstate()

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("external access is forbidden in the readiness audit")

    with monkeypatch.context() as patch:
        patch.setattr(builtins, "open", forbidden)
        patch.setattr(io, "open", forbidden)
        patch.setattr(Path, "open", forbidden)
        patch.setattr(Path, "read_text", forbidden)
        patch.setattr(Path, "read_bytes", forbidden)
        patch.setattr(socket, "socket", forbidden)
        patch.setattr(socket, "create_connection", forbidden)
        patch.setattr(socket, "getaddrinfo", forbidden)
        patch.setattr(urllib.request, "urlopen", forbidden)
        patch.setattr(subprocess, "run", forbidden)
        patch.setattr(subprocess, "Popen", forbidden)
        patch.setattr(os, "getenv", forbidden)
        patch.setattr(os, "system", forbidden)
        patch.setattr(os, "popen", forbidden)

        signals = benchmark_signals(
            BenchmarkId.CANONICAL_TREND, audit.series, _decision_times()
        )
        result = run_backtest(audit.series, _targets(signals))
        summary = describe(result)
        paired = paired_daily_returns(result, audit.results[BenchmarkId.BUY_AND_HOLD])
        interval = paired_sharpe_improvement_interval(
            paired.candidate.returns,
            paired.benchmark.returns,
            stream=_stream(),
        )

    assert signals == audit.signals[BenchmarkId.CANONICAL_TREND]
    assert result == audit.results[BenchmarkId.CANONICAL_TREND]
    assert summary == describe(result)
    assert interval == paired_sharpe_improvement_interval(
        paired.candidate.returns,
        paired.benchmark.returns,
        stream=_stream(),
    )
    assert (
        tuple(
            (
                bar.open_time,
                bar.open,
                bar.high,
                bar.low,
                bar.close,
                bar.volume,
                bar.interval,
            )
            for bar in audit.series.bars
        )
        == bars_before
    )
    assert (
        tuple((target.decision_time, target.requested_exposure) for target in targets)
        == targets_before
    )
    assert random.getstate() == rng_before
