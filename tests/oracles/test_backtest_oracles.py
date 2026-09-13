"""Task 6 backtester oracles: exact identities, synthetic data only.

Every identity here is closed-form and exact. No tolerance, no threshold, no
random seed, no clock, no I/O, no market data, and no import of ``aqt``: the
suite is deliberately independent of the production backtester, which
``docs/RESEARCH_CONSTITUTION.md`` section 16 forbids writing before these tests
are reviewed and accepted.

Not covered here, by the mandated order:

* the NumPy reference implementation comparison
  (``BACKTESTER_SPEC_v1.md`` acceptance item 8), and
* any adapter that runs the production engine against these identities
  (section 18 "backtester trust"),

are **DEFERRED TO THE NEXT ORDERED TASK**. Concrete reason: neither NumPy
reference nor production engine exists in this repository yet, the mandated
order places both after this task, and a test that imports a module which does
not exist cannot pass. No skipped or stubbed test pretends otherwise.
"""

from collections.abc import Callable, Mapping, Sequence
from fractions import Fraction
from typing import Final

from oracles._kernel import (
    BAR_INTERVAL,
    HOURS_PER_DAY,
    MINIMUM_HOLDING_FOR_RISK_INCREASE,
    ONE,
    SLIPPAGE_CAP_BPS,
    SLIPPAGE_FLOOR_BPS,
    STRESS_MULTIPLIERS,
    ZERO,
    Ledger,
    OracleError,
    additive_gross_pnl,
    additive_net_pnl,
    additive_price_grid,
    binary_exposure_paths,
    build_ledger,
    build_target_ledger,
    canonical_record_bytes,
    clip_exposure,
    compounded_gross_equity,
    compounded_net_equity,
    cost_rate_from_bps,
    drifted_exposure,
    exact,
    exposure_change_to_target,
    per_side_cost_bps,
    reaches_rebalance_band,
    record_digest,
    repeat_daily,
    require_admissible,
    segment_returns,
    slippage_bps,
    total_cost,
    turnover,
    utc,
)

_START: Final = utc(2020, 1, 1)
_FIRST_OPEN: Final = Fraction(1000)
_DAILY_STEPS: Final = (Fraction(1), Fraction(-1), Fraction(2), Fraction(-1))
_ALTERNATE_STEPS: Final = (Fraction(-1), Fraction(3), Fraction(-2), Fraction(1))

_FLOOR_RATE: Final = cost_rate_from_bps(per_side_cost_bps(ZERO))
_CAP_RATE: Final = cost_rate_from_bps(per_side_cost_bps(Fraction(10_000)))
_RATES: Final = (ZERO, _FLOOR_RATE, _CAP_RATE)

_SCENARIOS: Final[Mapping[str, tuple[Fraction, ...]]] = {
    "cash": (ZERO, ZERO, ZERO, ZERO),
    "buy_and_hold": (ONE, ONE, ONE, ONE),
    "alternating": (ONE, ZERO, ONE, ZERO),
    "late_entry": (ZERO, ONE, ONE, ZERO),
}

_GRIDS: Final[Mapping[str, tuple[Fraction, ...]]] = {
    "rising_then_falling": _DAILY_STEPS,
    "falling_then_rising": _ALTERNATE_STEPS,
}


def _opens(daily_steps: Sequence[Fraction]) -> tuple[Fraction, ...]:
    return additive_price_grid(_FIRST_OPEN, repeat_daily(daily_steps))


def _ledger(
    daily_targets: Sequence[Fraction],
    daily_steps: Sequence[Fraction] = _DAILY_STEPS,
    cost_rate: Fraction = _FLOOR_RATE,
    stress_multiplier: Fraction = ONE,
) -> Ledger:
    return build_ledger(
        start=_START,
        opens=_opens(daily_steps),
        exposures=repeat_daily(daily_targets),
        cost_rate=cost_rate,
        stress_multiplier=stress_multiplier,
    )


def _assert_oracle_error(action: Callable[[], object]) -> OracleError:
    try:
        action()
    except OracleError as error:
        return error
    raise AssertionError("expected an OracleError, none was raised")


def test_synthetic_grids_have_the_expected_exact_shape() -> None:
    for steps in _GRIDS.values():
        opens = _opens(steps)
        assert len(opens) == len(steps) * HOURS_PER_DAY + 1
        assert all(price > 0 for price in opens)
        assert all(isinstance(price, Fraction) for price in opens)
    for targets in _SCENARIOS.values():
        assert len(repeat_daily(targets)) == len(_DAILY_STEPS) * HOURS_PER_DAY


def test_zero_exposure_gives_exactly_zero_trading_pnl() -> None:
    for steps in _GRIDS.values():
        for rate in _RATES:
            for multiplier in STRESS_MULTIPLIERS:
                ledger = _ledger(_SCENARIOS["cash"], steps, rate, multiplier)
                assert turnover(ledger) == ZERO
                assert total_cost(ledger) == ZERO
                assert additive_gross_pnl(ledger) == ZERO
                assert additive_net_pnl(ledger) == ZERO
                assert compounded_gross_equity(ledger) == ONE
                assert compounded_net_equity(ledger) == ONE


def test_zero_exposure_touches_no_segment() -> None:
    ledger = _ledger(_SCENARIOS["cash"])
    assert ledger.segments
    for segment in ledger.segments:
        assert segment.exposure == ZERO
        assert segment.traded == ZERO
        assert segment.cost == ZERO
        assert segment.gross_return != ZERO


def test_buy_and_hold_compounded_gross_equity_is_the_price_ratio() -> None:
    for steps in _GRIDS.values():
        opens = _opens(steps)
        ledger = _ledger(_SCENARIOS["buy_and_hold"], steps, ZERO)
        assert compounded_gross_equity(ledger) == opens[-1] / opens[0]


def test_buy_and_hold_additive_gross_pnl_is_the_sum_of_returns() -> None:
    for steps in _GRIDS.values():
        opens = _opens(steps)
        ledger = _ledger(_SCENARIOS["buy_and_hold"], steps, ZERO)
        assert additive_gross_pnl(ledger) == sum(segment_returns(opens), ZERO)


def test_buy_and_hold_charges_exactly_one_entry_trade() -> None:
    targets = _SCENARIOS["buy_and_hold"]
    for rate in _RATES:
        for multiplier in STRESS_MULTIPLIERS:
            ledger = _ledger(targets, _DAILY_STEPS, rate, multiplier)
            assert turnover(ledger) == ONE
            assert total_cost(ledger) == rate * multiplier
            assert ledger.segments[0].traded == ONE
            assert all(segment.traded == ZERO for segment in ledger.segments[1:])


def test_buy_and_hold_net_identity_holds_under_both_aggregators() -> None:
    for steps in _GRIDS.values():
        opens = _opens(steps)
        gross_sum = sum(segment_returns(opens), ZERO)
        ratio = opens[-1] / opens[0]
        for rate in _RATES:
            for multiplier in STRESS_MULTIPLIERS:
                ledger = _ledger(_SCENARIOS["buy_and_hold"], steps, rate, multiplier)
                charged = rate * multiplier
                assert additive_net_pnl(ledger) == gross_sum - charged
                assert compounded_net_equity(ledger) == (ONE - charged) * ratio


def test_buy_and_hold_enters_at_the_first_scheduled_decision() -> None:
    ledger = _ledger(_SCENARIOS["buy_and_hold"])
    require_admissible(_START, repeat_daily(_SCENARIOS["buy_and_hold"]))
    entry = ledger.segments[0]
    assert entry.execution_time == _START
    assert entry.execution_time.hour == 0
    assert ledger.segments[1].execution_time - entry.execution_time == BAR_INTERVAL


def test_alternating_exposure_gives_exact_turnover_and_cost() -> None:
    for name, targets in _SCENARIOS.items():
        expected_turnover = ZERO
        previous = ZERO
        for target in targets:
            expected_turnover += abs(target - previous)
            previous = target
        for rate in _RATES:
            for multiplier in STRESS_MULTIPLIERS:
                ledger = _ledger(targets, _DAILY_STEPS, rate, multiplier)
                assert turnover(ledger) == expected_turnover, name
                assert total_cost(ledger) == rate * multiplier * expected_turnover
    alternating = _ledger(_SCENARIOS["alternating"])
    assert turnover(alternating) == Fraction(4)


def test_trades_occur_only_at_scheduled_decision_boundaries() -> None:
    ledger = _ledger(_SCENARIOS["alternating"])
    for segment in ledger.segments:
        if segment.index % HOURS_PER_DAY == 0:
            assert segment.traded == ONE
            assert segment.execution_time.hour == 0
        else:
            assert segment.traded == ZERO
            assert segment.cost == ZERO


def test_every_scenario_path_is_admissible_under_the_frozen_rules() -> None:
    for targets in _SCENARIOS.values():
        require_admissible(_START, repeat_daily(targets))


def test_the_admissibility_oracle_rejects_forbidden_paths() -> None:
    hourly_flip = tuple(
        ONE if index % 2 == 0 else ZERO
        for index in range(len(_DAILY_STEPS) * HOURS_PER_DAY)
    )
    _assert_oracle_error(lambda: require_admissible(_START, hourly_flip))

    intraday_increase = (ZERO,) * 5 + (ONE,) * 5
    _assert_oracle_error(lambda: require_admissible(_START, intraday_increase))

    intraday_regain = (ONE,) * 2 + (ZERO,) * 10 + (ONE,) * 12
    _assert_oracle_error(lambda: require_admissible(_START, intraday_regain))

    inside_band = (Fraction(1, 2),) * 24 + (Fraction(11, 20),) * 24
    _assert_oracle_error(lambda: require_admissible(_START, inside_band))

    _assert_oracle_error(lambda: require_admissible(utc(2020, 1, 1, 5), (ONE,) * 24))


def test_a_risk_increase_at_exactly_24_hours_is_admissible() -> None:
    require_admissible(_START, (ONE,) * 12 + (ZERO,) * 12 + (ONE,) * 24)


def test_the_scheduled_anchor_already_spaces_risk_increases_by_24_hours() -> None:
    path = repeat_daily(_SCENARIOS["alternating"])
    increases = [
        index
        for index, exposure in enumerate(path)
        if exposure > (path[index - 1] if index else ZERO)
    ]
    assert increases == [0, 48]
    for lower, higher in zip(increases, increases[1:], strict=False):
        assert (higher - lower) * BAR_INTERVAL >= MINIMUM_HOLDING_FOR_RISK_INCREASE


def test_pnl_follows_the_executed_path_not_the_intended_one() -> None:
    intended = (ZERO,) * 5 + (ONE,) * 91
    executed = repeat_daily(_SCENARIOS["late_entry"])
    _assert_oracle_error(lambda: require_admissible(_START, intended))
    require_admissible(_START, executed)
    opens = _opens(_DAILY_STEPS)
    intended_ledger = build_ledger(_START, opens, intended, _FLOOR_RATE)
    executed_ledger = build_ledger(_START, opens, executed, _FLOOR_RATE)
    assert additive_net_pnl(intended_ledger) != additive_net_pnl(executed_ledger)
    intended_equity = compounded_net_equity(intended_ledger)
    executed_equity = compounded_net_equity(executed_ledger)
    assert intended_equity != executed_equity
    assert turnover(intended_ledger) != turnover(executed_ledger)


def test_higher_cost_multiplier_never_improves_net_pnl() -> None:
    for steps in _GRIDS.values():
        for name, targets in _SCENARIOS.items():
            for rate in _RATES:
                ordered = [
                    _ledger(targets, steps, rate, multiplier)
                    for multiplier in STRESS_MULTIPLIERS
                ]
                traded = turnover(ordered[0])
                for lower, higher in zip(ordered, ordered[1:], strict=False):
                    low_additive = additive_net_pnl(lower)
                    high_additive = additive_net_pnl(higher)
                    low_equity = compounded_net_equity(lower)
                    high_equity = compounded_net_equity(higher)
                    assert high_additive <= low_additive, name
                    assert high_equity <= low_equity, name
                    if traded > ZERO and rate > ZERO:
                        assert high_additive < low_additive, name
                        assert high_equity < low_equity, name
                    else:
                        assert high_additive == low_additive, name
                        assert high_equity == low_equity, name


def test_higher_cost_rate_never_improves_net_pnl() -> None:
    for name, targets in _SCENARIOS.items():
        ordered = [_ledger(targets, _DAILY_STEPS, rate) for rate in _RATES]
        for lower, higher in zip(ordered, ordered[1:], strict=False):
            assert additive_net_pnl(higher) <= additive_net_pnl(lower), name
            assert compounded_net_equity(higher) <= compounded_net_equity(lower), name


def test_cost_never_improves_net_pnl_on_any_enumerated_daily_path() -> None:
    opens = _opens(_DAILY_STEPS)
    for path in binary_exposure_paths(len(_DAILY_STEPS)):
        exposures = repeat_daily(path)
        free = build_ledger(_START, opens, exposures, ZERO)
        charged = build_ledger(_START, opens, exposures, _CAP_RATE, Fraction(3))
        assert additive_net_pnl(charged) <= additive_gross_pnl(free)
        assert compounded_net_equity(charged) <= compounded_gross_equity(free)


def test_zero_cost_leaves_net_equal_to_gross() -> None:
    for targets in _SCENARIOS.values():
        ledger = _ledger(targets, _DAILY_STEPS, ZERO)
        assert additive_net_pnl(ledger) == additive_gross_pnl(ledger)
        assert compounded_net_equity(ledger) == compounded_gross_equity(ledger)


def test_frozen_cost_model_constants_are_transcribed_exactly() -> None:
    assert slippage_bps(ZERO) == SLIPPAGE_FLOOR_BPS
    assert slippage_bps(Fraction(20)) == SLIPPAGE_FLOOR_BPS
    assert slippage_bps(Fraction(40)) == Fraction(2)
    assert slippage_bps(Fraction(300)) == SLIPPAGE_CAP_BPS
    assert slippage_bps(Fraction(10_000)) == SLIPPAGE_CAP_BPS
    assert per_side_cost_bps(ZERO) == Fraction(13)
    assert per_side_cost_bps(Fraction(10_000)) == Fraction(27)
    assert _FLOOR_RATE == Fraction(13, 10_000)
    assert _CAP_RATE == Fraction(27, 10_000)
    assert STRESS_MULTIPLIERS == (Fraction(1), Fraction(3, 2), Fraction(2), Fraction(3))


def test_slippage_is_monotone_bounded_and_non_negative() -> None:
    sigmas = [Fraction(value) for value in range(0, 400, 7)]
    values = [slippage_bps(sigma) for sigma in sigmas]
    for lower, higher in zip(values, values[1:], strict=False):
        assert lower <= higher
    for value in values:
        assert SLIPPAGE_FLOOR_BPS <= value <= SLIPPAGE_CAP_BPS
    _assert_oracle_error(lambda: slippage_bps(Fraction(-1)))


def test_ledger_construction_rejects_malformed_input() -> None:
    opens = _opens(_DAILY_STEPS)
    _assert_oracle_error(lambda: build_ledger(_START, opens, (ONE,), _FLOOR_RATE))
    _assert_oracle_error(
        lambda: build_ledger(_START, opens, repeat_daily(_SCENARIOS["cash"]), ONE)
    )
    _assert_oracle_error(
        lambda: build_ledger(
            utc(2020, 1, 1).replace(tzinfo=None),
            opens,
            repeat_daily(_SCENARIOS["cash"]),
            ZERO,
        )
    )
    _assert_oracle_error(lambda: additive_price_grid(Fraction(10), (Fraction(-20),)))


def test_exposure_targets_are_clipped_before_ledger_accounting() -> None:
    opens = (Fraction(100), Fraction(110), Fraction(99))
    ledger = build_ledger(
        _START,
        opens,
        (Fraction(-1), Fraction(2)),
        _FLOOR_RATE,
    )

    assert clip_exposure(Fraction(-1)) == ZERO
    assert clip_exposure(Fraction(2)) == ONE
    assert tuple(segment.exposure for segment in ledger.segments) == (ZERO, ONE)
    assert tuple(segment.traded for segment in ledger.segments) == (ZERO, ONE)
    assert tuple(segment.cost for segment in ledger.segments) == (ZERO, _FLOOR_RATE)


def test_admissibility_uses_clipped_exposure_targets() -> None:
    require_admissible(_START, (Fraction(2), Fraction(-1)))


def test_fractional_exposure_drifts_exactly_on_a_no_trade_segment() -> None:
    starting_exposure = Fraction(1, 2)
    gross_return = Fraction(1, 10)

    assert starting_exposure * gross_return == Fraction(1, 20)
    assert drifted_exposure(starting_exposure, gross_return) == Fraction(11, 21)
    assert drifted_exposure(ZERO, gross_return) == ZERO
    assert drifted_exposure(ONE, gross_return) == ONE


def test_next_turnover_uses_drifted_weight_not_the_prior_target() -> None:
    prior_target = Fraction(1, 2)
    drifted = drifted_exposure(prior_target, Fraction(1, 10))
    next_target = Fraction(4, 5)
    change = exposure_change_to_target(next_target, drifted)

    assert drifted == Fraction(11, 21)
    assert change == Fraction(29, 105)
    assert abs(change) != abs(next_target - prior_target)
    assert reaches_rebalance_band(change)
    assert reaches_rebalance_band(Fraction(1, 10))
    assert not reaches_rebalance_band(Fraction(1, 10) - Fraction(1, 1_000_000))


def test_fractional_target_path_does_not_rebalance_for_free() -> None:
    ledger = build_target_ledger(
        _START,
        (Fraction(100), Fraction(110), Fraction(121)),
        (Fraction(1, 2), Fraction(1, 2)),
        ZERO,
    )

    assert tuple(segment.exposure for segment in ledger.segments) == (
        Fraction(1, 2),
        Fraction(11, 21),
    )
    assert tuple(segment.traded for segment in ledger.segments) == (
        Fraction(1, 2),
        ZERO,
    )
    assert compounded_gross_equity(ledger) == Fraction(221, 200)


def test_adverse_drift_does_not_trigger_an_intraday_risk_increase() -> None:
    ledger = build_target_ledger(
        _START,
        (Fraction(100), Fraction(50), Fraction(50)),
        (Fraction(1, 2), Fraction(1, 2)),
        ZERO,
    )

    assert tuple(segment.exposure for segment in ledger.segments) == (
        Fraction(1, 2),
        Fraction(1, 3),
    )
    assert tuple(segment.traded for segment in ledger.segments) == (
        Fraction(1, 2),
        ZERO,
    )
    assert compounded_gross_equity(ledger) == Fraction(3, 4)


def test_later_rebalance_turnover_starts_from_drifted_weight() -> None:
    opens = (Fraction(100), Fraction(110), *((Fraction(110),) * 24))
    targets = (Fraction(1, 2),) * 24 + (Fraction(4, 5),)
    ledger = build_target_ledger(_START, opens, targets, ZERO)

    assert ledger.segments[24].execution_time == _START + 24 * BAR_INTERVAL
    assert ledger.segments[24].exposure == Fraction(4, 5)
    assert ledger.segments[24].traded == Fraction(29, 105)


def test_fractional_drift_helper_boundaries_are_explicit() -> None:
    assert drifted_exposure(Fraction(1, 2), Fraction(-999, 1000)) == Fraction(1, 1001)
    assert exposure_change_to_target(Fraction(2), Fraction(1, 2)) == Fraction(1, 2)
    assert exposure_change_to_target(Fraction(-1), Fraction(1, 2)) == Fraction(-1, 2)
    _assert_oracle_error(lambda: drifted_exposure(Fraction(-1, 10), ZERO))
    _assert_oracle_error(lambda: drifted_exposure(Fraction(11, 10), ZERO))
    _assert_oracle_error(lambda: drifted_exposure(Fraction(1, 2), -ONE))
    _assert_oracle_error(
        lambda: exposure_change_to_target(Fraction(1, 2), Fraction(-1, 10))
    )


def _oracle_record() -> dict[str, str]:
    record: dict[str, str] = {}
    for grid_name, steps in _GRIDS.items():
        for scenario, targets in _SCENARIOS.items():
            for multiplier in STRESS_MULTIPLIERS:
                ledger = _ledger(targets, steps, _FLOOR_RATE, multiplier)
                key = f"{grid_name}.{scenario}.x{exact(multiplier)}"
                record[f"{key}.turnover"] = exact(turnover(ledger))
                record[f"{key}.cost"] = exact(total_cost(ledger))
                record[f"{key}.additive_gross"] = exact(additive_gross_pnl(ledger))
                record[f"{key}.additive_net"] = exact(additive_net_pnl(ledger))
                record[f"{key}.compounded_gross"] = exact(
                    compounded_gross_equity(ledger)
                )
                record[f"{key}.compounded_net"] = exact(compounded_net_equity(ledger))
    return record


def test_canonical_oracle_record_is_byte_identical_across_reruns() -> None:
    first = canonical_record_bytes(_oracle_record())
    second = canonical_record_bytes(_oracle_record())
    assert first == second
    assert record_digest(first) == record_digest(second)
    assert len(record_digest(first)) == 64
    assert set(record_digest(first)) <= set("0123456789abcdef")


def test_canonical_oracle_record_uses_compact_utf8_and_sorted_keys() -> None:
    assert canonical_record_bytes({"z": "قيمة", "a": "1/1"}) == (
        '{"a":"1/1","z":"قيمة"}'.encode()
    )


def test_canonical_oracle_record_is_independent_of_insertion_order() -> None:
    record = _oracle_record()
    reversed_record = dict(reversed(list(record.items())))
    assert list(reversed_record) != list(record)
    assert canonical_record_bytes(reversed_record) == canonical_record_bytes(record)


def test_canonical_oracle_record_holds_only_exact_rationals() -> None:
    record = _oracle_record()
    assert record
    for key, value in record.items():
        numerator, separator, denominator = value.partition("/")
        assert separator == "/", key
        assert int(numerator) == Fraction(value).numerator
        assert int(denominator) > 0
        assert "." not in value and "e" not in value


def test_canonical_oracle_record_detects_a_single_changed_value() -> None:
    record = _oracle_record()
    baseline = canonical_record_bytes(record)
    for key in sorted(record)[:5]:
        mutated = dict(record)
        mutated[key] = exact(Fraction(record[key]) + Fraction(1, 10**12))
        assert canonical_record_bytes(mutated) != baseline
        assert record_digest(canonical_record_bytes(mutated)) != record_digest(baseline)


def test_canonical_oracle_record_is_stable_under_rebuilt_inputs() -> None:
    rebuilt = {
        key: value
        for key, value in sorted(_oracle_record().items(), key=lambda item: item[1])
    }
    assert canonical_record_bytes(rebuilt) == canonical_record_bytes(_oracle_record())
