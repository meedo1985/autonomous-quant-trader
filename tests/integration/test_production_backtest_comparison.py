"""Task 8 production engine against the accepted Task 6 and Task 7 layers."""

from datetime import datetime
from fractions import Fraction

import numpy as np
from oracles._kernel import build_target_ledger
from reference._error_bounds import Bounded, path_bounds
from reference._fixtures import CAP_RATE, COST_LADDER, FIXTURES, Fixture
from reference._numpy_reference import (
    ReferencePath,
    build_reference_path,
    compounded_net_equity,
    total_cost,
    turnover,
)

from aqt.backtest.engine import ExposureTarget, run_backtest
from aqt.data.bars import BAR_INTERVAL, Bar, BarSeries


def _production_series(case: Fixture, *, capped_slippage: bool) -> BarSeries:
    first_open = float(case.opens[0])
    opens = [first_open, first_open, first_open, *case.float_opens]
    if capped_slippage:
        closes = [100.0 if index % 2 == 0 else 200.0 for index in range(len(opens))]
    else:
        closes = [100.0] * len(opens)
    start = case.start - 3 * BAR_INTERVAL
    return BarSeries(
        symbol="BTCUSDT",
        bars=tuple(
            Bar(
                open_time=start + index * BAR_INTERVAL,
                open=opened,
                high=max(opened, closed),
                low=min(opened, closed),
                close=closed,
                volume=1.0,
            )
            for index, (opened, closed) in enumerate(zip(opens, closes, strict=True))
        ),
    )


def _targets(case: Fixture) -> tuple[ExposureTarget, ...]:
    return tuple(
        ExposureTarget(
            decision_time=case.start + index * BAR_INTERVAL,
            requested_exposure=float(target),
        )
        for index, target in enumerate(case.targets)
    )


def _assert_bound(bound: Bounded, observed: float, label: str) -> None:
    assert bound.contains(observed), (
        f"{label}: {observed!r} lies outside {float(bound.error)!r} around "
        f"exact {bound.value}"
    )


def _reference(case: Fixture, rate: Fraction, stress: Fraction) -> ReferencePath:
    return build_reference_path(
        start_hour_utc=case.start_hour_utc,
        opens=case.float_opens,
        targets=case.float_targets,
        cost_rate=float(rate),
        stress_multiplier=float(stress),
    )


def _decision_times(case: Fixture) -> tuple[datetime, ...]:
    return tuple(
        case.start + index * BAR_INTERVAL for index in range(len(case.targets))
    )


def test_production_matches_exact_oracle_and_numpy_reference_matrix() -> None:
    for case in FIXTURES:
        for label, rate, stress in COST_LADDER:
            oracle = build_target_ledger(
                case.start,
                case.opens,
                case.targets,
                rate,
                stress,
            )
            reference = _reference(case, rate, stress)
            bounds = path_bounds(
                opens=case.opens,
                targets=case.targets,
                cost_rate=rate,
                stress_multiplier=stress,
                traded_flags=[segment.traded != 0 for segment in oracle.segments],
            )
            result = run_backtest(
                _production_series(case, capped_slippage=rate == CAP_RATE),
                _targets(case),
                stress_multiplier=float(stress),
            )
            tag = f"{case.name}/{label}"

            assert len(result.segments) == len(oracle.segments) == len(reference), tag
            assert tuple(segment.decision_time for segment in result.segments) == (
                _decision_times(case)
            ), tag
            for index, (production, exact) in enumerate(
                zip(result.segments, oracle.segments, strict=True)
            ):
                assert production.execution_time == exact.execution_time, tag
                assert production.action.value == reference.action[index].value, tag
                assert production.requested_exposure == float(
                    reference.requested_target[index]
                ), tag
                assert production.clipped_target == float(
                    reference.clipped_target[index]
                ), tag
                assert (production.traded != 0.0) == (exact.traded != 0), tag
                _assert_bound(
                    bounds.gross_return[index],
                    production.gross_return,
                    f"{tag}.gross_return[{index}]",
                )
                _assert_bound(
                    bounds.held_weight_before[index],
                    production.held_weight_before,
                    f"{tag}.held_weight_before[{index}]",
                )
                _assert_bound(
                    bounds.exposure[index],
                    production.exposure,
                    f"{tag}.exposure[{index}]",
                )
                _assert_bound(
                    bounds.traded[index],
                    production.traded,
                    f"{tag}.traded[{index}]",
                )
                _assert_bound(
                    bounds.cost[index],
                    production.cost,
                    f"{tag}.cost[{index}]",
                )
                assert bounds.gross_return[index].contains(
                    float(reference.gross_return[index])
                ), tag
                assert bounds.exposure[index].contains(
                    float(reference.exposure[index])
                ), tag
                assert bounds.cost[index].contains(float(reference.cost[index])), tag

            _assert_bound(bounds.turnover, result.turnover, f"{tag}.turnover")
            _assert_bound(bounds.total_cost, result.total_cost, f"{tag}.total_cost")
            _assert_bound(
                bounds.compounded_net_equity,
                result.final_equity,
                f"{tag}.compounded_net_equity",
            )
            assert bounds.turnover.contains(float(turnover(reference))), tag
            assert bounds.total_cost.contains(float(total_cost(reference))), tag
            assert bounds.compounded_net_equity.contains(
                float(compounded_net_equity(reference))
            ), tag


def test_cost_regime_adapter_reaches_the_frozen_floor_and_cap() -> None:
    case = FIXTURES[0]
    target = _targets(case)[:1]
    floor = run_backtest(
        _production_series(case, capped_slippage=False),
        target,
    ).segments[0]
    cap = run_backtest(
        _production_series(case, capped_slippage=True),
        target,
    ).segments[0]

    assert floor.cost_breakdown.slippage_bps == 1.0
    assert floor.cost_breakdown.total_bps == 13.0
    assert cap.cost_breakdown.slippage_bps == 15.0
    assert cap.cost_breakdown.total_bps == 27.0
    assert np.isfinite(cap.cost_breakdown.sigma_hourly_bps)
