"""Task 7: the NumPy ``float64`` reference against the exact Task 6 oracle.

This is ``specs/BACKTESTER_SPEC_v1.md`` acceptance item "NumPy reference
implementation matches within tolerance" and the ``NumPy reference`` step of
the ``docs/RESEARCH_CONSTITUTION.md`` section 16 order. Synthetic fixtures
only; no clock, no file, no network, no exchange, no credentials, no random
seed and no import of ``aqt``.

What "within tolerance" means here
----------------------------------

The tolerance is **derived, not chosen**. For every fixture, every cost case
and every quantity, :mod:`reference._error_bounds` walks the same expression
graph the reference evaluates and produces a proven absolute error bound from
the binary64 unit roundoff ``u = 2 ** -53`` and the number of machine
operations. No trading, materiality or performance threshold appears anywhere
in this suite, and
:func:`test_the_derived_bounds_are_not_vacuous` pins that the derived bounds
are far too tight to absorb an economically meaningful discrepancy.

Three layers of agreement are asserted:

1. **Discrete agreement, exactly.** Whether a decision trades at all, and
   which frozen rule decided it, is not a numeric quantity and no tolerance
   can cover it. The reference's decision sequence must equal the exact
   oracle's, and :func:`test_every_band_decision_is_provably_robust` shows the
   agreement is not luck: on every fixture the exact distance from the 10pp
   band exceeds the derived float error, so the branch cannot flip.
2. **Exact agreement where binary64 is exact.** On the flat-or-invested paths
   every exposure, trade size and turnover is an integer, and integers are
   exact in binary64. Those comparisons use ``==``.
3. **Bounded agreement elsewhere.** Every remaining quantity must fall inside
   its own derived bound.

The bound derivation is itself checked rather than trusted: for every fixture
:func:`test_the_bound_walk_reproduces_the_exact_oracle_values` asserts that the
exact rational values the bound walk carries equal the accepted Task 6 oracle's
values term by term. A bound derived from a different computation than the one
under test would be worthless, so this is a precondition, not a nicety.
"""

import math
from datetime import timedelta
from fractions import Fraction
from typing import Final

import numpy as np
from oracles._kernel import (
    BAR_INTERVAL,
    Ledger,
    build_ledger,
    build_target_ledger,
    canonical_record_bytes,
    drifted_exposure,
    record_digest,
)
from oracles._kernel import clip_exposure as exact_clip

from reference._error_bounds import (
    ROUNDOFF_CHARGE_PER_OPERATION,
    UNIT_ROUNDOFF,
    Bounded,
    BoundError,
    PathBounds,
    is_representable,
    path_bounds,
)
from reference._fixtures import (
    CAP_RATE,
    COST_CASES,
    COST_LADDER,
    FIXTURES,
    FLOOR_RATE,
    STRESS_MULTIPLIERS,
    Fixture,
    fixture,
)
from reference._numpy_reference import (
    BARS_PER_DAY,
    MINIMUM_HOLD_BARS_FOR_RISK_INCREASE,
    REBALANCE_BAND_ABSOLUTE,
    REBALANCE_BAND_THRESHOLD,
    REBALANCE_BAND_TOLERANCE,
    SCHEDULED_DECISION_ANCHOR_HOUR_UTC,
    Action,
    ReferenceError,
    ReferencePath,
    additive_gross_pnl,
    additive_net_pnl,
    build_reference_path,
    clip_exposure,
    compounded_gross_equity,
    compounded_net_equity,
    increase_is_eligible,
    net_equity_curve,
    reaches_rebalance_band,
    segment_pnl,
    segment_returns,
    total_cost,
    turnover,
)

_EXACT_ZERO: Final = Fraction(0)
_EXACT_ONE: Final = Fraction(1)
_BAND: Final = Fraction(1, 10)

_ROUNDOFF_SCALE_CEILING: Final = Fraction(1, 10**9)
"""Any derived bound above this would mean the derivation had degenerated.

It is not a comparison threshold: nothing is ever compared against it. It is a
guard on the *derivation*, so that a future change which silently inflates a
bound into an economically meaningful range fails here instead of quietly
weakening every comparison in the file.
"""


def _reference(
    fixture_case: Fixture, rate: Fraction, stress: Fraction
) -> ReferencePath:
    return build_reference_path(
        start_hour_utc=fixture_case.start_hour_utc,
        opens=fixture_case.float_opens,
        targets=fixture_case.float_targets,
        cost_rate=float(rate),
        stress_multiplier=float(stress),
    )


def _oracle(fixture_case: Fixture, rate: Fraction, stress: Fraction) -> Ledger:
    return build_target_ledger(
        fixture_case.start,
        fixture_case.opens,
        fixture_case.targets,
        rate,
        stress,
    )


def _bounds(
    fixture_case: Fixture, ledger: Ledger, rate: Fraction, stress: Fraction
) -> PathBounds:
    return path_bounds(
        opens=fixture_case.opens,
        targets=fixture_case.targets,
        cost_rate=rate,
        stress_multiplier=stress,
        traded_flags=[segment.traded != _EXACT_ZERO for segment in ledger.segments],
    )


def _held_weights_before(ledger: Ledger) -> tuple[Fraction, ...]:
    """The exact actual weight entering each execution opportunity.

    Reconstructed from the accepted oracle's own executed record: the path
    starts flat, and thereafter the weight entering segment ``i`` is the
    previous segment's exposure drifted through the previous segment's return.
    """
    held = [_EXACT_ZERO]
    for segment in ledger.segments[:-1]:
        held.append(drifted_exposure(segment.exposure, segment.gross_return))
    return tuple(held)


def _oracle_actions(ledger: Ledger) -> tuple[Action, ...]:
    """Classify each accepted-oracle segment by the rule that decided it.

    Derived from the exact ledger and the exact execution timestamps, with no
    reference-side input, so that comparing it with the reference's own
    classification is a real cross-check rather than a restatement.
    """
    actions: list[Action] = []
    for segment, held in zip(
        ledger.segments, _held_weights_before(ledger), strict=True
    ):
        scheduled = segment.execution_time.hour == SCHEDULED_DECISION_ANCHOR_HOUR_UTC
        if segment.traded == _EXACT_ZERO:
            actions.append(Action.HOLD)
        elif segment.exposure < held:
            actions.append(
                Action.SCHEDULED_REDUCTION if scheduled else Action.INTRADAY_REDUCTION
            )
        else:
            actions.append(Action.SCHEDULED_INCREASE)
    return tuple(actions)


def _assert_within(bounded: Bounded, observed: np.float64, label: str) -> None:
    value = float(observed)
    assert bounded.contains(value), (
        f"{label}: reference {value!r} is outside the derived bound "
        f"{float(bounded.error)!r} around the exact value {bounded.value}"
    )


def _assert_reference_error(action: object, label: str) -> None:
    assert callable(action)
    try:
        action()
    except ReferenceError:
        return
    raise AssertionError(f"{label}: expected a ReferenceError, none was raised")


# --------------------------------------------------------------------------
# Preconditions on the derivation itself
# --------------------------------------------------------------------------


def test_the_reference_reproduces_the_frozen_scheduling_constants() -> None:
    assert BARS_PER_DAY == 24
    assert MINIMUM_HOLD_BARS_FOR_RISK_INCREASE == 24
    assert SCHEDULED_DECISION_ANCHOR_HOUR_UTC == 0
    assert BAR_INTERVAL == timedelta(hours=1)
    assert MINIMUM_HOLD_BARS_FOR_RISK_INCREASE * BAR_INTERVAL == timedelta(hours=24)
    assert Fraction(float(REBALANCE_BAND_ABSOLUTE)) == Fraction(0.10)
    assert float(REBALANCE_BAND_TOLERANCE) == 4.0 * math.ulp(1.0)
    assert float(REBALANCE_BAND_THRESHOLD) == 0.10 - 4.0 * math.ulp(1.0)
    assert FLOOR_RATE == Fraction(13, 10_000)
    assert CAP_RATE == Fraction(27, 10_000)
    assert STRESS_MULTIPLIERS == (
        Fraction(1),
        Fraction(3, 2),
        Fraction(2),
        Fraction(3),
    )


def test_the_derivation_uses_the_binary64_unit_roundoff() -> None:
    assert UNIT_ROUNDOFF == Fraction(1, 2**53)
    assert float(2 * UNIT_ROUNDOFF) == float(np.finfo(np.float64).eps)
    assert ROUNDOFF_CHARGE_PER_OPERATION == 2 * UNIT_ROUNDOFF
    assert is_representable(Fraction(1, 2))
    assert not is_representable(Fraction(1, 10))


def test_the_fixture_matrix_is_the_documented_shape() -> None:
    names = [case.name for case in FIXTURES]
    assert len(names) == len(set(names))
    required = {
        "binary.rising_then_falling.cash",
        "binary.rising_then_falling.buy_and_hold",
        "binary.rising_then_falling.alternating",
        "binary.rising_then_falling.late_entry",
        "fractional_drift",
        "adverse_drift_hold",
        "clipping",
        "band_boundary_exact_10pp",
        "band_boundary_just_inside",
        "scheduled_increase",
        "intraday_increase_held",
        "offset_start_hour",
        "causal_lagged.anti_persistent",
        "leaking.anti_persistent",
    }
    assert required <= set(names)
    assert fixture("offset_start_hour").start_hour_utc == 17
    for case in FIXTURES:
        assert len(case.targets) == len(case.opens) - 1, case.name
        assert all(isinstance(price, Fraction) for price in case.opens), case.name


def test_the_bound_walk_reproduces_the_exact_oracle_values() -> None:
    """The bound walk must model the accepted oracle's computation exactly.

    A tolerance derived from a different expression graph than the one under
    test would prove nothing, so every exact rational the walk carries is
    checked term by term against the accepted Task 6 oracle before any bound
    derived from it is used.
    """
    for case in FIXTURES:
        for label, rate, stress in COST_CASES:
            ledger = _oracle(case, rate, stress)
            bounds = _bounds(case, ledger, rate, stress)
            tag = f"{case.name}/{label}"
            held = _held_weights_before(ledger)
            assert len(bounds.exposure) == len(ledger.segments), tag
            for index, segment in enumerate(ledger.segments):
                assert bounds.gross_return[index].value == segment.gross_return, tag
                assert bounds.held_weight_before[index].value == held[index], tag
                assert bounds.exposure[index].value == segment.exposure, tag
                assert bounds.traded[index].value == segment.traded, tag
                assert bounds.cost[index].value == segment.cost, tag
                assert bounds.change[index].value == (
                    exact_clip(case.targets[index]) - held[index]
                ), tag


# --------------------------------------------------------------------------
# Discrete agreement
# --------------------------------------------------------------------------


def test_the_reference_takes_exactly_the_oracle_decisions() -> None:
    for case in FIXTURES:
        for label, rate, stress in COST_CASES:
            ledger = _oracle(case, rate, stress)
            path = _reference(case, rate, stress)
            tag = f"{case.name}/{label}"
            assert len(path) == len(ledger.segments), tag
            assert path.action == _oracle_actions(ledger), tag
            for index, segment in enumerate(ledger.segments):
                traded_exactly = segment.traded != _EXACT_ZERO
                traded_in_float = path.action[index] is not Action.HOLD
                assert traded_in_float == traded_exactly, f"{tag}[{index}]"
                assert int(path.execution_hour[index]) == segment.execution_time.hour, (
                    f"{tag}[{index}]"
                )


def test_every_band_decision_is_provably_robust() -> None:
    """No fixture sits inside the zone where roundoff could flip the branch.

    The reference acts when ``|change| >= REBALANCE_BAND_THRESHOLD``; the exact
    oracle acts when ``|change| >= 1/10``. Agreement is only meaningful if the
    exact change is farther from the reference's threshold than the derived
    error on the float change. That is asserted here for every segment of every
    fixture, so the decision agreement above cannot be an accident of the
    chosen numbers.
    """
    threshold = Fraction(float(REBALANCE_BAND_THRESHOLD))
    assert threshold < _BAND
    checked = 0
    for case in FIXTURES:
        for label, rate, stress in COST_CASES:
            ledger = _oracle(case, rate, stress)
            bounds = _bounds(case, ledger, rate, stress)
            for index, change in enumerate(bounds.change):
                magnitude = abs(change.value)
                tag = f"{case.name}/{label}[{index}]"
                if magnitude >= _BAND:
                    assert magnitude - change.error >= threshold, tag
                else:
                    assert magnitude + change.error < threshold, tag
                checked += 1
    assert checked > 0


def test_the_exact_10pp_boundary_is_admitted_and_a_hair_less_is_refused() -> None:
    exact_case = fixture("band_boundary_exact_10pp")
    inside_case = fixture("band_boundary_just_inside")

    # 0.6 - 0.5 is 0.09999999999999998: the case Task 5's comparator exists for.
    assert 0.5 - 0.4 < 0.10
    assert reaches_rebalance_band(np.float64(0.5 - 0.4))
    assert reaches_rebalance_band(np.float64(0.10))
    assert not reaches_rebalance_band(np.float64(0.10 - 1e-6))

    exact_path = _reference(exact_case, FLOOR_RATE, _EXACT_ONE)
    assert exact_path.action == (
        Action.SCHEDULED_INCREASE,
        Action.INTRADAY_REDUCTION,
        Action.HOLD,
    )
    assert float(exact_path.exposure[1]) == 0.4

    inside_path = _reference(inside_case, FLOOR_RATE, _EXACT_ONE)
    assert inside_path.action == (Action.SCHEDULED_INCREASE, Action.HOLD, Action.HOLD)
    assert float(inside_path.exposure[1]) == 0.5
    assert float(inside_path.traded[1]) == 0.0


def test_a_forbidden_intraday_increase_is_held_not_deferred() -> None:
    case = fixture("intraday_increase_held")
    path = _reference(case, FLOOR_RATE, _EXACT_ONE)

    assert path.action[0] is Action.SCHEDULED_INCREASE
    # Every intraday bar of the first day re-requests 0.9 and is refused.
    for index in range(1, BARS_PER_DAY):
        assert path.action[index] is Action.HOLD, index
        assert float(path.traded[index]) == 0.0, index
        assert float(path.clipped_target[index]) == 0.9, index
    # The next 00:00 UTC decision executes it in full, in one bar.
    assert path.action[BARS_PER_DAY] is Action.SCHEDULED_INCREASE
    assert float(path.exposure[BARS_PER_DAY]) == 0.9
    for index in range(BARS_PER_DAY + 1, len(path)):
        assert path.action[index] is Action.HOLD, index
    assert path.action == _oracle_actions(_oracle(case, FLOOR_RATE, _EXACT_ONE))


def test_adverse_drift_never_triggers_an_intraday_risk_increase() -> None:
    case = fixture("adverse_drift_hold")
    path = _reference(case, _EXACT_ZERO, _EXACT_ONE)
    ledger = _oracle(case, _EXACT_ZERO, _EXACT_ONE)

    assert path.action == (Action.SCHEDULED_INCREASE, Action.HOLD)
    assert float(path.exposure[0]) == 0.5
    assert ledger.segments[1].exposure == Fraction(1, 3)
    assert float(path.exposure[1]) == float(Fraction(1, 3))
    assert float(path.traded[1]) == 0.0
    # The refused change is well outside the band: it is refused by the
    # scheduling rule, not by the band.
    assert reaches_rebalance_band(np.float64(0.5) - path.exposure[1])


def test_requested_targets_are_clipped_before_anything_else() -> None:
    assert float(clip_exposure(-1.0)) == 0.0
    assert float(clip_exposure(2.0)) == 1.0
    assert float(clip_exposure(0.25)) == 0.25

    case = fixture("clipping")
    path = _reference(case, FLOOR_RATE, _EXACT_ONE)
    assert tuple(float(value) for value in path.requested_target) == (2.0, -1.0)
    assert tuple(float(value) for value in path.clipped_target) == (1.0, 0.0)
    assert tuple(float(value) for value in path.exposure) == (1.0, 0.0)
    assert tuple(float(value) for value in path.traded) == (1.0, 1.0)
    assert path.action == (Action.SCHEDULED_INCREASE, Action.INTRADAY_REDUCTION)


def test_the_next_trade_is_measured_from_the_drifted_weight() -> None:
    case = fixture("scheduled_increase")
    path = _reference(case, _EXACT_ZERO, _EXACT_ONE)
    ledger = _oracle(case, _EXACT_ZERO, _EXACT_ONE)

    assert ledger.segments[24].traded == Fraction(29, 105)
    assert path.action[24] is Action.SCHEDULED_INCREASE
    assert int(path.execution_hour[24]) == 0
    # From the drifted 11/21, not from the previous 1/2 target.
    assert abs(float(path.held_weight_before[24]) - float(Fraction(11, 21))) < 1e-15
    assert abs(float(path.traded[24]) - float(Fraction(29, 105))) < 1e-15
    assert float(path.traded[24]) != abs(0.8 - 0.5)


def test_targets_and_actual_held_weights_stay_distinct() -> None:
    case = fixture("fractional_drift")
    path = _reference(case, _EXACT_ZERO, _EXACT_ONE)

    assert float(path.clipped_target[1]) == 0.5
    assert float(path.held_weight_before[1]) != 0.5
    assert float(path.exposure[1]) == float(path.held_weight_before[1])
    assert float(path.traded[1]) == 0.0
    assert abs(float(path.exposure[1]) - float(Fraction(11, 21))) < 1e-15


# --------------------------------------------------------------------------
# Numeric agreement
# --------------------------------------------------------------------------


def test_every_reference_quantity_lies_inside_its_derived_bound() -> None:
    for case in FIXTURES:
        for label, rate, stress in COST_CASES:
            ledger = _oracle(case, rate, stress)
            bounds = _bounds(case, ledger, rate, stress)
            path = _reference(case, rate, stress)
            tag = f"{case.name}/{label}"
            for index in range(len(path)):
                _assert_within(
                    bounds.gross_return[index],
                    path.gross_return[index],
                    f"{tag}.gross_return[{index}]",
                )
                _assert_within(
                    bounds.held_weight_before[index],
                    path.held_weight_before[index],
                    f"{tag}.held_weight_before[{index}]",
                )
                _assert_within(
                    bounds.exposure[index],
                    path.exposure[index],
                    f"{tag}.exposure[{index}]",
                )
                _assert_within(
                    bounds.traded[index], path.traded[index], f"{tag}.traded[{index}]"
                )
                _assert_within(
                    bounds.cost[index], path.cost[index], f"{tag}.cost[{index}]"
                )
            _assert_within(bounds.turnover, turnover(path), f"{tag}.turnover")
            _assert_within(bounds.total_cost, total_cost(path), f"{tag}.total_cost")
            _assert_within(
                bounds.additive_gross_pnl,
                additive_gross_pnl(path),
                f"{tag}.additive_gross_pnl",
            )
            _assert_within(
                bounds.additive_net_pnl,
                additive_net_pnl(path),
                f"{tag}.additive_net_pnl",
            )
            _assert_within(
                bounds.compounded_gross_equity,
                compounded_gross_equity(path),
                f"{tag}.compounded_gross_equity",
            )
            _assert_within(
                bounds.compounded_net_equity,
                compounded_net_equity(path),
                f"{tag}.compounded_net_equity",
            )


def test_the_derived_bounds_stay_at_roundoff_scale() -> None:
    widest = _EXACT_ZERO
    for case in FIXTURES:
        for label, rate, stress in COST_CASES:
            ledger = _oracle(case, rate, stress)
            bounds = _bounds(case, ledger, rate, stress)
            observed = bounds.widest_error()
            assert observed < _ROUNDOFF_SCALE_CEILING, f"{case.name}/{label}"
            widest = max(widest, observed)
    assert widest > _EXACT_ZERO
    # Roundoff scale, not a trading scale: well under a hundredth of a basis
    # point on a unit-notional path.
    assert widest < Fraction(1, 10**10)


def test_the_derived_bounds_are_not_vacuous() -> None:
    """A bound that could absorb a real error would prove nothing.

    Each derived bound is shown to reject a perturbation far below any
    economically meaningful size, so "matches within tolerance" cannot be
    satisfied by a wrong implementation.
    """
    probe = Fraction(1, 10**9)
    for case in FIXTURES:
        for label, rate, stress in COST_CASES:
            ledger = _oracle(case, rate, stress)
            bounds = _bounds(case, ledger, rate, stress)
            tag = f"{case.name}/{label}"
            for name in (
                "turnover",
                "total_cost",
                "additive_gross_pnl",
                "additive_net_pnl",
                "compounded_gross_equity",
                "compounded_net_equity",
            ):
                bounded: Bounded = getattr(bounds, name)
                assert bounded.error < probe, f"{tag}.{name}"
                assert not bounded.contains(float(bounded.value) + float(probe)), (
                    f"{tag}.{name}"
                )


def test_binary_paths_agree_with_the_oracle_exactly() -> None:
    """Flat-or-invested paths are integer-valued, so binary64 is exact here."""
    for case in FIXTURES:
        if not case.binary_executed:
            continue
        for label, rate, stress in COST_CASES:
            ledger = _oracle(case, rate, stress)
            path = _reference(case, rate, stress)
            tag = f"{case.name}/{label}"
            held = _held_weights_before(ledger)
            for index, segment in enumerate(ledger.segments):
                assert segment.exposure in (_EXACT_ZERO, _EXACT_ONE), tag
                assert float(path.exposure[index]) == float(segment.exposure), tag
                assert float(path.traded[index]) == float(segment.traded), tag
                assert float(path.held_weight_before[index]) == float(held[index]), tag
            assert float(turnover(path)) == float(
                sum((segment.traded for segment in ledger.segments), _EXACT_ZERO)
            ), tag


def test_the_target_reference_matches_the_executed_state_oracle_on_binary_paths() -> (
    None
):
    """On admissible binary paths the target ledger and the executed-state
    ledger describe the same path, so the reference is compared against both
    accepted Task 6 constructors, not only the sequential one."""
    checked = 0
    for case in FIXTURES:
        if not case.binary_executed or case.name.startswith("clipping"):
            continue
        for label, rate, stress in COST_CASES:
            executed = build_ledger(case.start, case.opens, case.targets, rate, stress)
            target = _oracle(case, rate, stress)
            assert executed.segments == target.segments, f"{case.name}/{label}"
            path = _reference(case, rate, stress)
            for index, segment in enumerate(executed.segments):
                assert float(path.exposure[index]) == float(segment.exposure)
                assert float(path.traded[index]) == float(segment.traded)
            checked += 1
    assert checked > 0


def test_zero_exposure_produces_exactly_zero_everywhere() -> None:
    for grid in ("rising_then_falling", "falling_then_rising"):
        case = fixture(f"binary.{grid}.cash")
        for label, rate, stress in COST_LADDER:
            path = _reference(case, rate, stress)
            tag = f"{case.name}/{label}"
            assert float(turnover(path)) == 0.0, tag
            assert float(total_cost(path)) == 0.0, tag
            assert float(additive_gross_pnl(path)) == 0.0, tag
            assert float(additive_net_pnl(path)) == 0.0, tag
            assert float(compounded_gross_equity(path)) == 1.0, tag
            assert float(compounded_net_equity(path)) == 1.0, tag
            assert not np.any(path.exposure)
            assert not np.any(path.traded)
            assert set(path.action) == {Action.HOLD}


def test_zero_cost_leaves_net_exactly_equal_to_gross() -> None:
    for case in FIXTURES:
        path = _reference(case, _EXACT_ZERO, _EXACT_ONE)
        assert float(total_cost(path)) == 0.0, case.name
        assert float(additive_net_pnl(path)) == float(additive_gross_pnl(path)), (
            case.name
        )
        assert float(compounded_net_equity(path)) == float(
            compounded_gross_equity(path)
        ), case.name


def test_compounded_cost_is_charged_before_the_following_return() -> None:
    path = _reference(
        fixture("binary.rising_then_falling.buy_and_hold"), FLOOR_RATE, _EXACT_ONE
    )
    curve = net_equity_curve(path)

    assert float(path.cost[0]) > 0.0
    assert float(curve.before[0]) == 1.0
    assert float(curve.after_cost[0]) == 1.0 - float(path.cost[0])
    assert float(curve.after_return[0]) == float(curve.after_cost[0]) * (
        1.0 + float(path.exposure[0] * path.gross_return[0])
    )


def test_higher_cost_never_improves_net_performance() -> None:
    """The frozen stress ladder, ordered by the charge it actually applies.

    ``COST_LADDER`` interleaves two per-side rates with four stress multipliers,
    so its declaration order is not charge order: ``floor x3`` charges 39 bps
    and ``cap x1`` charges 27. Sorting by ``rate * multiplier`` makes the
    monotonicity claim exact instead of skipping the inversions.
    """
    ladder = sorted(COST_LADDER, key=lambda case: case[1] * case[2])
    charges = [rate * stress for _, rate, stress in ladder]
    assert charges == sorted(charges)
    assert charges[0] < charges[-1]

    for case in FIXTURES:
        free = _reference(case, _EXACT_ZERO, _EXACT_ONE)
        ordered = [_reference(case, rate, stress) for _, rate, stress in ladder]
        for path, (label, _, _) in zip(ordered, ladder, strict=True):
            tag = f"{case.name}/{label}"
            assert float(additive_net_pnl(path)) <= float(additive_net_pnl(free)), tag
            assert float(compounded_net_equity(path)) <= float(
                compounded_gross_equity(free)
            ), tag
        for lower, higher in zip(ordered, ordered[1:], strict=False):
            assert float(total_cost(higher)) >= float(total_cost(lower)), case.name
            assert float(additive_net_pnl(higher)) <= float(additive_net_pnl(lower)), (
                case.name
            )
            assert float(compounded_net_equity(higher)) <= float(
                compounded_net_equity(lower)
            ), case.name


def test_turnover_and_cost_are_proportional_within_a_cost_case() -> None:
    for case in FIXTURES:
        for label, rate, stress in COST_LADDER:
            path = _reference(case, rate, stress)
            charge = float(rate) * float(stress)
            expected = float(turnover(path)) * charge
            observed = float(total_cost(path))
            assert abs(observed - expected) <= 1e-12 * max(1.0, abs(expected)), (
                f"{case.name}/{label}"
            )


# --------------------------------------------------------------------------
# Causality and leakage, wired to the reference
# --------------------------------------------------------------------------


def test_the_leaking_signal_is_absurd_and_the_causal_control_is_not() -> None:
    for grid in ("anti_persistent", "persistent"):
        leaking = _reference(fixture(f"leaking.{grid}"), _EXACT_ZERO, _EXACT_ONE)
        causal = _reference(fixture(f"causal_lagged.{grid}"), _EXACT_ZERO, _EXACT_ONE)

        leaking_pnl = segment_pnl(leaking)
        causal_pnl = segment_pnl(causal)
        assert not bool(np.any(leaking_pnl < 0.0)), grid
        assert bool(np.any(leaking_pnl > 0.0)), grid
        assert bool(np.any(causal_pnl < 0.0)), grid
        assert float(additive_gross_pnl(causal)) < float(additive_gross_pnl(leaking)), (
            grid
        )
        assert float(compounded_gross_equity(causal)) < float(
            compounded_gross_equity(leaking)
        ), grid
        assert float(compounded_gross_equity(leaking)) > 1.0, grid


def test_the_reference_reads_no_future_price_within_a_segment() -> None:
    """Segment ``i``'s exposure is decided before segment ``i``'s return exists.

    Truncating the price grid one open early leaves every earlier segment's
    decision, exposure, trade size and cost bit-identical. A reference that
    peeked at a later open could not satisfy this.
    """
    for case in FIXTURES:
        full = _reference(case, FLOOR_RATE, _EXACT_ONE)
        shorter = build_reference_path(
            start_hour_utc=case.start_hour_utc,
            opens=case.float_opens[:-1],
            targets=case.float_targets[:-1],
            cost_rate=float(FLOOR_RATE),
            stress_multiplier=1.0,
        )
        assert len(shorter) == len(full) - 1, case.name
        assert shorter.action == full.action[:-1], case.name
        assert shorter.exposure.tobytes() == full.exposure[:-1].tobytes(), case.name
        assert shorter.traded.tobytes() == full.traded[:-1].tobytes(), case.name
        assert shorter.cost.tobytes() == full.cost[:-1].tobytes(), case.name


# --------------------------------------------------------------------------
# Determinism
# --------------------------------------------------------------------------


def _canonical_record() -> dict[str, str]:
    record: dict[str, str] = {}
    for case in FIXTURES:
        for label, rate, stress in COST_CASES:
            path = _reference(case, rate, stress)
            key = f"{case.name}.{label}"
            record[f"{key}.actions"] = ",".join(action.value for action in path.action)
            for name, value in (
                ("turnover", turnover(path)),
                ("total_cost", total_cost(path)),
                ("additive_gross", additive_gross_pnl(path)),
                ("additive_net", additive_net_pnl(path)),
                ("compounded_gross", compounded_gross_equity(path)),
                ("compounded_net", compounded_net_equity(path)),
            ):
                record[f"{key}.{name}"] = float(value).hex()
    return record


def test_a_deterministic_rerun_is_bit_identical() -> None:
    for case in FIXTURES:
        first = _reference(case, FLOOR_RATE, Fraction(3, 2))
        second = _reference(case, FLOOR_RATE, Fraction(3, 2))
        assert first.action == second.action, case.name
        for name in (
            "gross_return",
            "requested_target",
            "clipped_target",
            "held_weight_before",
            "exposure",
            "traded",
            "cost",
        ):
            left: np.ndarray = getattr(first, name)
            right: np.ndarray = getattr(second, name)
            assert left.dtype == np.float64, f"{case.name}.{name}"
            assert left.tobytes() == right.tobytes(), f"{case.name}.{name}"


def test_the_canonical_reference_record_is_byte_identical_across_reruns() -> None:
    first = canonical_record_bytes(_canonical_record())
    second = canonical_record_bytes(_canonical_record())
    assert first == second
    assert record_digest(first) == record_digest(second)
    assert len(record_digest(first)) == 64


def test_the_canonical_reference_record_holds_lossless_hex_floats() -> None:
    record = _canonical_record()
    assert record
    for key, value in record.items():
        if key.endswith(".actions"):
            assert set(value.split(",")) <= {action.value for action in Action}, key
            continue
        assert float.fromhex(value).hex() == value, key


def test_the_reference_does_not_mutate_its_inputs() -> None:
    case = fixture("scheduled_increase")
    opens = case.float_opens
    targets = case.float_targets
    opens_before = list(opens)
    targets_before = list(targets)
    build_reference_path(
        start_hour_utc=case.start_hour_utc,
        opens=opens,
        targets=targets,
        cost_rate=float(FLOOR_RATE),
    )
    assert opens == opens_before
    assert targets == targets_before


# --------------------------------------------------------------------------
# The reference's own guards
# --------------------------------------------------------------------------


def test_the_reference_rejects_malformed_input() -> None:
    case = fixture("scheduled_increase")
    opens = case.float_opens
    targets = case.float_targets

    def call(**overrides: object) -> object:
        arguments: dict[str, object] = {
            "start_hour_utc": 0,
            "opens": opens,
            "targets": targets,
            "cost_rate": float(FLOOR_RATE),
            "stress_multiplier": 1.0,
        }
        arguments.update(overrides)
        return build_reference_path(**arguments)  # type: ignore[arg-type]

    _assert_reference_error(lambda: call(start_hour_utc=24), "hour out of range")
    _assert_reference_error(lambda: call(start_hour_utc=-1), "negative hour")
    _assert_reference_error(lambda: call(targets=targets[:-1]), "short target path")
    _assert_reference_error(lambda: call(cost_rate=-1e-4), "negative cost rate")
    _assert_reference_error(lambda: call(stress_multiplier=-1.0), "negative stress")
    _assert_reference_error(lambda: call(cost_rate=1.0), "cost exceeds notional")
    _assert_reference_error(lambda: call(opens=[100.0]), "single open")
    _assert_reference_error(lambda: call(opens=[100.0, 0.0]), "non-positive open")
    _assert_reference_error(
        lambda: call(opens=[100.0, float("nan")]), "non-finite open"
    )
    _assert_reference_error(lambda: segment_returns([[100.0, 110.0]]), "two axes")


def test_the_reference_helpers_guard_their_own_domains() -> None:
    _assert_reference_error(
        lambda: increase_is_eligible(0, -1), "negative elapsed bars"
    )
    assert increase_is_eligible(0, None)
    assert increase_is_eligible(0, 24)
    assert not increase_is_eligible(0, 23)
    assert not increase_is_eligible(1, None)
    assert not increase_is_eligible(23, 1_000)


def test_the_bound_derivation_refuses_an_undecidable_branch() -> None:
    """A tolerance cannot cover a discrete branch, so the derivation refuses.

    A divisor whose bound straddles zero, and a clip whose bound straddles an
    endpoint, are rejected outright instead of being papered over.
    """
    from reference._error_bounds import Bounded as RawBounded
    from reference._error_bounds import clip_exposure as bounded_clip
    from reference._error_bounds import div as bounded_div

    for action, label in (
        (
            lambda: bounded_div(
                RawBounded(_EXACT_ONE, _EXACT_ZERO),
                RawBounded(Fraction(1, 100), Fraction(1, 10)),
            ),
            "divisor straddling zero",
        ),
        (
            lambda: bounded_clip(RawBounded(Fraction(1, 10**6), Fraction(1, 10**3))),
            "clip straddling 0",
        ),
        (
            lambda: bounded_clip(
                RawBounded(_EXACT_ONE + Fraction(1, 10**6), Fraction(1, 10**3))
            ),
            "clip straddling 1",
        ),
    ):
        try:
            action()
        except BoundError:
            continue
        raise AssertionError(f"{label}: expected a BoundError, none was raised")


def test_the_comparison_covers_the_whole_fixture_matrix() -> None:
    """Guard against a fixture silently dropping out of the matrix.

    The literals are written out so that deleting a fixture, a cost case or a
    whole scenario family fails here instead of quietly shrinking every
    comparison in the file.
    """
    assert len(FIXTURES) == 20
    assert len(COST_CASES) == 5
    assert len(COST_LADDER) == 8
    # 8 binary x 96 + 4 leakage x 144 + 133 across the eight rule fixtures.
    assert sum(len(case.targets) for case in FIXTURES) == 1_477
    assert sum(1 for case in FIXTURES if case.binary_executed) == 13
    assert sum(1 for case in FIXTURES if not case.binary_executed) == 7


def test_every_fixture_starts_flat_and_is_never_force_liquidated() -> None:
    terminal_holdings = 0
    for case in FIXTURES:
        path = _reference(case, FLOOR_RATE, _EXACT_ONE)
        assert float(path.held_weight_before[0]) == 0.0, case.name
        assert float(path.exposure[0]) == 0.0 or path.action[0] is not Action.HOLD, (
            case.name
        )
        # A non-zero terminal exposure is marked to the final open and nothing
        # is charged for holding it: the final cost is the final trade's cost.
        if float(path.exposure[-1]) > 0.0 and path.action[-1] is Action.HOLD:
            assert float(path.cost[-1]) == 0.0, case.name
            terminal_holdings += 1
    assert terminal_holdings > 0, "no fixture exercises a non-zero terminal exposure"
