"""Task 16: the exploration-only research harness, end to end."""

from __future__ import annotations

import ast
import dataclasses
import functools
import math
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

import aqt.core.attempts
import aqt.core.ledger
from aqt.benchmarks.canonical import BenchmarkId
from aqt.data.bars import Bar, BarSeries
from aqt.data.manifest import (
    Gap,
    ManifestError,
    PartitionManifest,
    RawArtifact,
    build_partition_manifest,
    unavailable,
)
from aqt.research import harness
from aqt.research.harness import (
    HarnessConfig,
    HarnessError,
    HarnessResult,
    run_exploration,
)

HOUR = timedelta(hours=1)
START = datetime(2018, 1, 1, tzinfo=UTC)
ROOT = Path(__file__).parents[2]


def _series(hours: int, *, skip: range = range(0)) -> BarSeries:
    bars = []
    for index in range(hours):
        if index in skip:
            continue
        close = 100.0 * math.exp(0.01 * math.sin(index / 7.0) + index * 1e-4)
        opened = 100.0 * math.exp(0.01 * math.sin((index - 1) / 7.0) + index * 1e-4)
        bars.append(
            Bar(
                open_time=START + index * HOUR,
                open=opened,
                high=max(opened, close) * 1.001,
                low=min(opened, close) * 0.999,
                close=close,
                volume=1.0,
            )
        )
    return BarSeries(symbol="BTCUSDT", bars=tuple(bars))


def _manifest(series: BarSeries, partition: str = "exploration") -> PartitionManifest:
    end = START + 300 * HOUR
    present = {bar.open_time for bar in series.bars}
    gaps = []
    moment = START
    while moment < end:
        if moment not in present:
            gaps.append(Gap(moment, moment + HOUR))
        moment += HOUR
    return build_partition_manifest(
        partition=partition,
        series=series,
        raw_artifacts=[RawArtifact("synthetic.zip", b"synthetic")],
        parser_code_sha256="0" * 64,
        window_start_utc=START,
        window_end_exclusive_utc=end,
        fees=unavailable("synthetic"),
        exchange_filters=unavailable("synthetic"),
        symbol_status=unavailable("synthetic"),
        gaps=gaps,
    )


SERIES = _series(300, skip=range(190, 192))
MANIFEST = _manifest(SERIES)
VOL = HarnessConfig(BenchmarkId.VOL_TARGET_BUY_AND_HOLD)


def _run(config: HarnessConfig = VOL) -> HarnessResult:
    return run_exploration(MANIFEST, lambda _: SERIES, config)


@functools.cache
def _cached() -> HarnessResult:
    return _run()


def test_a_run_is_deterministic_across_runs_and_processes() -> None:
    first = _run()
    assert first.digest() == _run().digest()
    code = (
        "from tests.integration.test_research_harness import _run;"
        "print(_run().digest())"
    )
    other = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert other.stdout.strip() == first.digest()


def test_each_contiguous_run_is_backtested_and_short_runs_are_reported() -> None:
    result = _cached()
    # Bars 0-189 (190 bars) and 192-299 (108 bars): the vol target needs 169
    # bars of history, so the second run cannot produce a decision.
    assert len(result.runs) == 1
    assert result.runs[0].first_decision_time == START + 169 * HOUR
    assert result.runs[0].last_decision_time == START + 188 * HOUR
    assert result.runs[0].metrics.segment_count == 20
    assert [(s.start, s.bar_count) for s in result.skipped_runs] == [
        (START + 192 * HOUR, 108)
    ]
    both = _run(HarnessConfig(BenchmarkId.BUY_AND_HOLD))
    assert len(both.runs) == 2
    assert both.skipped_runs == ()


@pytest.mark.parametrize("partition", ["confirmation", "lockbox"])
def test_other_partitions_are_refused_before_data_is_read(partition: str) -> None:
    manifest = dataclasses.replace(MANIFEST, partition=partition)
    calls: list[PartitionManifest] = []

    def load(requested: PartitionManifest) -> BarSeries:
        calls.append(requested)
        return SERIES

    with pytest.raises(HarnessError, match="refused before any data is read"):
        run_exploration(manifest, load, VOL)
    assert calls == []


def test_bars_that_do_not_match_the_manifest_are_refused() -> None:
    bars = list(SERIES.bars)
    bars[10] = dataclasses.replace(bars[10], volume=2.0)
    altered = BarSeries(symbol="BTCUSDT", bars=tuple(bars))
    with pytest.raises(ManifestError, match="parsed"):
        run_exploration(MANIFEST, lambda _: altered, VOL)


def test_no_attempt_or_ledger_entry_is_written(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("the harness must not register a trial")

    monkeypatch.setattr(aqt.core.attempts, "start_attempt", forbidden)
    monkeypatch.setattr(aqt.core.ledger, "append_entry", forbidden)
    assert _run().trial_status == "NOT_A_REGISTERED_TRIAL"

    tree = ast.parse(Path(harness.__file__).read_text(encoding="utf-8"))
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    } | {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert not any(
        name.startswith(("aqt.core", "aqt.validation", "aqt.lockbox_eval"))
        for name in imported
    ), imported


PROMOTION_TERMS = (
    "sharpe",
    "dsr",
    "deflated",
    "pbo",
    "cpcv",
    "ess",
    "bootstrap",
    "paired",
    "promotion",
    "p_value",
    "trial_count",
)


def _keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {k for v in value.values() for k in _keys(v)}
    if isinstance(value, list):
        return {k for v in value for k in _keys(v)}
    return set()


def test_the_result_exposes_descriptive_metrics_only() -> None:
    keys = _keys(_cached().as_mapping())
    assert "max_drawdown" in keys
    leaked = {
        key
        for key in keys
        for term in PROMOTION_TERMS
        if term in key.lower().split("_") or ("_" in term and term in key.lower())
    }
    assert leaked == set()
    fields = {f.name for f in dataclasses.fields(HarnessResult)}
    assert fields == {
        "manifest_sha256",
        "symbol",
        "config",
        "runs",
        "skipped_runs",
        "trial_status",
    }
