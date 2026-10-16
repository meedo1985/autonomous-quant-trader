"""The C-6 event contract (`aqt.backtest.event_contract`), synthetic data only."""

from __future__ import annotations

import math
import random
from datetime import UTC, datetime, timedelta

import pytest

from aqt.backtest.engine import ExposureTarget, run_backtest
from aqt.backtest.event_contract import EventContractError, run_event_contract
from aqt.data.bars import Bar, BarSeries

START = datetime(2024, 1, 1, tzinfo=UTC)  # bar 0 opens at 00:00


def _series(opens: list[float]) -> BarSeries:
    bars = []
    for i, o in enumerate(opens):
        c = opens[i + 1] if i + 1 < len(opens) else o
        bars.append(
            Bar(
                START + timedelta(hours=i),
                o,
                max(o, c) * 1.001,
                min(o, c) * 0.999,
                c,
                1.0,
            )
        )
    return BarSeries("BTCUSDT", tuple(bars))


def _walk(n: int, seed: int = 3, vol: float = 0.01) -> list[float]:
    rng = random.Random(seed)
    p, out = 100.0, []
    for _ in range(n):
        out.append(p)
        p *= math.exp(rng.gauss(0.0, vol))
    return out


def _flat(n: int) -> list[float]:
    return [100.0] * n


def test_delay_zero_equals_the_cycle1_backtester_without_zero_exits() -> None:
    # EC-2: no target is 0, so only the shared rules act
    series = _series(_walk(24 * 20))
    rng = random.Random(9)
    start, n = 30, 24 * 18
    targets = [round(rng.uniform(0.05, 1.0), 2) for _ in range(n)]
    ec = run_event_contract(series, targets, start)
    path = [
        ExposureTarget(series.bars[start + i].open_time, t)
        for i, t in enumerate(targets)
    ]
    bt = run_backtest(series, path)
    assert ec.exposure == tuple(s.exposure for s in bt.segments)
    assert ec.equity == tuple(s.equity_after_return for s in bt.segments)
    assert [f.cost for f in ec.fills] == [s.cost for s in bt.segments if s.traded]
    assert ec.final_equity == bt.final_equity


def test_a_reduction_to_zero_is_never_blocked_by_the_band() -> None:
    # N-4: buy 0.3 at 00:00, cut to 0.19 then 0.09 (each a band move), then
    # target 0 at 03:00: |0 - 0.09| is inside the band, yet it exits; the
    # Cycle-1 backtester holds it
    series = _series(_flat(60))
    targets = [0.3, 0.19, 0.09, 0.0, 0.0]
    ec = run_event_contract(series, targets, 24)
    got = [(f.decision_instant, f.exposure) for f in ec.fills]
    assert got == [(24, 0.3), (25, 0.19), (26, 0.09), (27, 0.0)]
    path = [
        ExposureTarget(series.bars[24 + i].open_time, t) for i, t in enumerate(targets)
    ]
    assert run_backtest(series, path).segments[3].exposure == 0.09
    # a target inside the band that is not 0 is still held
    ec = run_event_contract(series, [0.3, 0.25, 0.25], 24)
    assert [f.exposure for f in ec.fills] == [0.3]


def test_increases_only_at_midnight_after_24h_from_the_decision() -> None:
    series = _series(_flat(24 * 4))
    targets = [0.0] * 3 + [0.5] * 21 + [0.5] + [0.9] * 30
    ec = run_event_contract(series, targets, 21)  # instants 21.. ; 24 is 00:00
    # 0.5 wanted from 00:00 (instant 24 = targets[3]); filled at 24
    first = ec.fills[0]
    assert (first.decision_instant, first.exposure) == (24, 0.5)
    # 0.9 wanted from instant 46 (22:00): not before the next 00:00 (48),
    # and 48 - 24 = 24 h, so it fills at 48
    assert [(f.decision_instant, f.exposure) for f in ec.fills[1:]] == [(48, 0.9)]


def test_after_an_exit_the_next_increase_waits_for_midnight() -> None:
    series = _series(_flat(24 * 3))
    # 0.3 at day-1 00:00, exit at 06:00; 0.6 wanted from 12:00 fills at the
    # next 00:00, 24 h after the last increase decision
    targets = [0.3] * 6 + [0.0] * 6 + [0.6] * 30
    ec = run_event_contract(series, targets, 24)
    got = [(f.decision_instant, f.exposure) for f in ec.fills]
    assert got == [(24, 0.3), (30, 0.0), (48, 0.6)]


def test_execution_delay_fills_at_the_next_instant_and_drops_at_the_end() -> None:
    series = _series(_flat(60))
    ec = run_event_contract(series, [0.5, 0.5, 0.0, 0.0], 24, delay=1)
    got = [(f.decision_instant, f.fill_instant, f.exposure) for f in ec.fills]
    assert got == [(24, 25, 0.5), (26, 27, 0.0)]
    assert ec.exposure == (0.0, 0.5, 0.5, 0.0)
    ec = run_event_contract(series, [0.0, 0.0, 0.0, 0.5], 21, delay=1)
    assert ec.fills == () and ec.dropped == 1  # 00:00 order due after the end


def test_a_delayed_reduction_never_fills_as_an_increase() -> None:
    # held 0.5; the reduction to 0.35 is decided at 01:00; the price then
    # falls so held drifts below 0.35 before the fill: fill at held (clamp)
    opens = _flat(26) + [100.0, 50.0] + _flat(20)
    series = _series(opens)
    ec = run_event_contract(series, [0.5, 0.5, 0.35, 0.35], 24, delay=1)
    held_at_fill = ec.fills[1].held_before
    assert held_at_fill < 0.35
    assert ec.fills[1].exposure == held_at_fill and ec.fills[1].cost == 0.0


def test_a_delayed_increase_fills_as_ordered() -> None:
    # 0.4 at day-1 00:00 (filled 01:00); 0.5 decided at day-2 00:00 while the
    # price quadruples in bar 48, so held drifts above 0.5 before the 01:00
    # fill: it fills as ordered (C-6 (5)), a cut, charged on the difference.
    # (With decision-time anchoring the 24 h clause never binds for daily
    # decisions, as C-6 (6) discloses, so the clock rule is not observable.)
    opens = _flat(49) + [400.0] + _flat(30)
    series = _series(opens)
    targets = [0.4] * 24 + [0.5] * 4
    ec = run_event_contract(series, targets, 24, delay=1)
    second = ec.fills[1]
    assert (second.decision_instant, second.fill_instant) == (48, 49)
    assert second.held_before > 0.5 and second.exposure == 0.5
    assert second.cost > 0.0


def test_costs_scale_with_the_stress_multiplier() -> None:
    series = _series(_walk(24 * 3))
    base = run_event_contract(series, [0.6] * 30, 24)
    stressed = run_event_contract(series, [0.6] * 30, 24, stress_multiplier=2.0)
    assert stressed.fills[0].cost == pytest.approx(2 * base.fills[0].cost, rel=1e-12)
    assert stressed.final_equity < base.final_equity


def test_zero_exposure_earns_nothing() -> None:
    ec = run_event_contract(_series(_walk(80)), [0.0] * 50, 24)
    assert ec.equity == (1.0,) * 50 and ec.fills == ()


@pytest.mark.parametrize(
    "kwargs",
    [{"delay": 2}, {"delay": True}, {"stress_multiplier": 2.5}],
)
def test_invalid_runs_are_refused(kwargs: dict[str, object]) -> None:
    with pytest.raises((EventContractError, ValueError)):
        run_event_contract(_series(_flat(60)), [0.5] * 5, 24, **kwargs)  # type: ignore[arg-type]


def test_targets_are_clipped_and_non_finite_targets_refused() -> None:
    ec = run_event_contract(_series(_flat(60)), [1.7], 24)
    assert ec.fills[0].exposure == 1.0
    with pytest.raises(EventContractError, match="not finite"):
        run_event_contract(_series(_flat(60)), [float("nan")], 24)
    with pytest.raises(EventContractError):
        run_event_contract(_series(_flat(30)), [0.5] * 10, 24)  # no following open
