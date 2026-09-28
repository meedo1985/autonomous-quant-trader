"""The paper loop's target source (roadmap Task 24, owner answer Q5).

Only the frozen deployable baseline, `VOL_TARGET_BUY_AND_HOLD` (Constitution
section 11), computed by `aqt.benchmarks.canonical`. No model is trained or
implemented, and no other benchmark can be selected
(`review/task24/OWNER_ANSWER_Q5.md`).
"""

from __future__ import annotations

from datetime import datetime
from typing import Final

from aqt.benchmarks.canonical import (
    PROMOTION_BENCHMARK,
    BenchmarkId,
    CanonicalBenchmarkError,
    benchmark_signal,
)
from aqt.data.bars import BarSemanticsError, BarSeries
from aqt.governor.authorization import Proposal

__all__ = ["PREDICTOR_BENCHMARK", "baseline_proposal"]

PREDICTOR_BENCHMARK: Final[BenchmarkId] = BenchmarkId.VOL_TARGET_BUY_AND_HOLD
# protocol_v1.yaml names one benchmark as both promotion comparator and
# deployable baseline; `canonical` records it as PROMOTION_BENCHMARK.
assert PREDICTOR_BENCHMARK is PROMOTION_BENCHMARK


def baseline_proposal(series: BarSeries, decision_time: datetime) -> Proposal | str:
    """The baseline's target at `decision_time`, or the reason there is none.

    The history is the unbroken run of bars ending at the decision bar, as
    in the research harness (`_contiguous_runs`): after a data gap the
    history starts again, and a run still too short for the frozen window
    gives no proposal. Nothing is filled or guessed.
    """
    try:
        end = series.index_of(decision_time - series.interval)
    except BarSemanticsError as error:
        return str(error)
    bars = series.bars
    start = end
    while (
        start > 0
        and bars[start - 1].open_time + series.interval == bars[start].open_time
    ):
        start -= 1
    run = BarSeries(symbol=series.symbol, bars=bars[start : end + 1])
    try:
        signal = benchmark_signal(PREDICTOR_BENCHMARK, run, decision_time)
    except CanonicalBenchmarkError as error:
        return str(error)
    return Proposal(series.symbol, signal.target_exposure, signal.decision_time)
