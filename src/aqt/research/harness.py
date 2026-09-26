"""Exploration-only research harness (roadmap Task 16).

Runs one fixed configuration end to end on an exploration partition:
canonical benchmark exposure mapping -> backtest -> descriptive metrics.

What this is not
----------------
A run here is free-form exploration and is **not a registered trial**
(`docs/RESEARCH_CONSTITUTION.md` section 9). It never starts an attempt,
writes no ledger entry, and computes no DSR, PBO, CPCV, ESS, bootstrap,
paired or promotion statistic: those bindings (`D-16`, `D-17`) are open.

Partition boundary
------------------
Only an exploration manifest is accepted (section 7a, section 15). A manifest
is refused before the loader is called unless it is labelled `exploration`
**and** its declared window lies inside the protocol exploration window
(`aqt.data.klines.WINDOW_START` to `WINDOW_END_EXCLUSIVE`); the label alone
proves nothing about the dates. The loaded bars are then checked against the
manifest, which confines them to its window and binds them to its parsed hash,
so no confirmation or lockbox bar is read.

Gaps
----
Bars are never filled, trimmed or corrected (section 6). The backtester and
the benchmarks both require contiguous history, so each contiguous run of
bars is backtested on its own, starting flat. A run too short to produce one
decision is reported in `skipped_runs`, not dropped silently.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Final

from aqt.backtest.engine import ExposureTarget, run_backtest
from aqt.benchmarks.canonical import (
    REQUIRED_HISTORY_BARS_BY_BENCHMARK,
    BenchmarkId,
    benchmark_signals,
    require_canonical_benchmark,
)
from aqt.data.bars import BAR_INTERVAL, Bar, BarSeries
from aqt.data.klines import WINDOW_END_EXCLUSIVE, WINDOW_START
from aqt.data.manifest import PartitionManifest, verify_partition_manifest
from aqt.metrics.descriptive import DescriptiveMetrics, describe

__all__ = [
    "EXPLORATION_PARTITION",
    "HarnessConfig",
    "HarnessError",
    "HarnessResult",
    "RunResult",
    "SkippedRun",
    "run_exploration",
]

EXPLORATION_PARTITION: Final[str] = "exploration"
TRIAL_STATUS: Final[str] = "NOT_A_REGISTERED_TRIAL"

# The backtester needs three earlier bars for its cost volatility (execution
# index >= 3) and one bar after the execution bar for the holding return.
_MIN_DECISION_INDEX: Final[int] = 2
_BARS_AFTER_DECISION: Final[int] = 2


class HarnessError(ValueError):
    """Raised when a run would leave the exploration boundary."""


@dataclass(frozen=True, slots=True)
class HarnessConfig:
    """One fixed configuration: a canonical benchmark and a cost stress."""

    benchmark: BenchmarkId
    stress_multiplier: float = 1.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "benchmark", require_canonical_benchmark(self.benchmark)
        )


@dataclass(frozen=True, slots=True)
class RunResult:
    """Descriptive metrics for one contiguous run of bars."""

    first_decision_time: datetime
    last_decision_time: datetime
    metrics: DescriptiveMetrics


@dataclass(frozen=True, slots=True)
class SkippedRun:
    """A contiguous run too short to produce a single decision."""

    start: datetime
    end: datetime
    bar_count: int
    reason: str


@dataclass(frozen=True, slots=True)
class HarnessResult:
    """Everything one exploration run produced. Descriptive only."""

    manifest_sha256: str
    symbol: str
    config: HarnessConfig
    runs: tuple[RunResult, ...]
    skipped_runs: tuple[SkippedRun, ...]
    trial_status: str = TRIAL_STATUS

    def as_mapping(self) -> dict[str, object]:
        """A JSON-ready view; floats are kept as their exact `float.hex`."""

        def metrics(m: DescriptiveMetrics) -> dict[str, object]:
            return {
                "cumulative_net_return": m.cumulative_net_return.hex(),
                "final_equity": m.final_equity.hex(),
                "initial_equity": m.initial_equity.hex(),
                "max_drawdown": m.max_drawdown.hex(),
                "net_returns": [value.hex() for value in m.net_returns],
                "segment_count": m.segment_count,
                "total_cost": m.total_cost.hex(),
                "total_turnover": m.total_turnover.hex(),
            }

        return {
            "benchmark": self.config.benchmark.value,
            "manifest_sha256": self.manifest_sha256,
            "runs": [
                {
                    "first_decision_time": run.first_decision_time.isoformat(),
                    "last_decision_time": run.last_decision_time.isoformat(),
                    "metrics": metrics(run.metrics),
                }
                for run in self.runs
            ],
            "skipped_runs": [
                {
                    "bar_count": skipped.bar_count,
                    "end": skipped.end.isoformat(),
                    "reason": skipped.reason,
                    "start": skipped.start.isoformat(),
                }
                for skipped in self.skipped_runs
            ],
            "stress_multiplier": float(self.config.stress_multiplier).hex(),
            "symbol": self.symbol,
            "trial_status": self.trial_status,
        }

    def digest(self) -> str:
        """SHA-256 of the sorted-key JSON of `as_mapping()`."""
        text = json.dumps(self.as_mapping(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _contiguous_runs(series: BarSeries) -> tuple[tuple[Bar, ...], ...]:
    runs: list[list[Bar]] = []
    for bar in series.bars:
        if runs and bar.open_time == runs[-1][-1].open_time + BAR_INTERVAL:
            runs[-1].append(bar)
        else:
            runs.append([bar])
    return tuple(tuple(run) for run in runs)


def run_exploration(
    manifest: PartitionManifest,
    load: Callable[[PartitionManifest], BarSeries],
    config: HarnessConfig,
) -> HarnessResult:
    """Run `config` on the bars `load` returns for an exploration `manifest`.

    The partition is checked before `load` is called. The loaded bars must
    reproduce the manifest's parsed hash, or the run is refused.
    """
    if manifest.partition != EXPLORATION_PARTITION:
        raise HarnessError(
            f"the research harness runs on the {EXPLORATION_PARTITION!r} "
            f"partition only; {manifest.partition!r} is refused before any "
            "data is read"
        )
    if (
        manifest.window_start_utc < WINDOW_START
        or manifest.window_end_exclusive_utc > WINDOW_END_EXCLUSIVE
    ):
        raise HarnessError(
            f"manifest window [{manifest.window_start_utc.isoformat()}, "
            f"{manifest.window_end_exclusive_utc.isoformat()}) leaves the "
            f"exploration window [{WINDOW_START.isoformat()}, "
            f"{WINDOW_END_EXCLUSIVE.isoformat()}); refused before any data is read"
        )
    series = load(manifest)
    verify_partition_manifest(manifest, series=series)

    required = REQUIRED_HISTORY_BARS_BY_BENCHMARK[config.benchmark]
    first_index = max(required - 1, _MIN_DECISION_INDEX)
    runs: list[RunResult] = []
    skipped: list[SkippedRun] = []
    for bars in _contiguous_runs(series):
        last_index = len(bars) - 1 - _BARS_AFTER_DECISION
        if last_index < first_index:
            skipped.append(
                SkippedRun(
                    start=bars[0].open_time,
                    end=bars[-1].close_time,
                    bar_count=len(bars),
                    reason=(
                        f"{len(bars)} contiguous bars; {config.benchmark.value} "
                        f"needs at least {first_index + 1 + _BARS_AFTER_DECISION}"
                    ),
                )
            )
            continue
        run_series = BarSeries(symbol=series.symbol, bars=bars)
        decision_times = [
            bars[i].close_time for i in range(first_index, last_index + 1)
        ]
        targets = [
            ExposureTarget(signal.decision_time, signal.target_exposure)
            for signal in benchmark_signals(
                config.benchmark, run_series, decision_times
            )
        ]
        result = run_backtest(
            run_series, targets, stress_multiplier=config.stress_multiplier
        )
        runs.append(
            RunResult(
                first_decision_time=decision_times[0],
                last_decision_time=decision_times[-1],
                metrics=describe(result),
            )
        )
    return HarnessResult(
        manifest_sha256=manifest.manifest_sha256,
        symbol=series.symbol,
        config=config,
        runs=tuple(runs),
        skipped_runs=tuple(skipped),
    )
