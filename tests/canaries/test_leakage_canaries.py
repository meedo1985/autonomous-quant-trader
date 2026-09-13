"""Task 6 leakage canaries: future-feature versus causally lagged control.

Synthetic data only, exact rational arithmetic only, no ``aqt`` import. The
canaries encode ``docs/RESEARCH_CONSTITUTION.md`` sections 6 and 18 and the
``BACKTESTER_SPEC_v1.md`` acceptance items "future-return leakage canary
produces absurd performance" and "causally lagged version does not".

"Absurd" is stated as an exact structural claim, not as a threshold: the
leaking path holds no losing segment at all and attains the exhaustive maximum
over every admissible flat-or-invested path. The causal control attains
neither. Nothing here is calibrated to a tolerance, so nothing here can be
tuned.

Wiring these canaries to the NumPy reference or to the production backtester
is **DEFERRED TO THE NEXT ORDERED TASK**: neither exists yet, and the
Constitution fixes the order ``oracle tests -> leakage canaries -> NumPy
reference -> production implementation``. No stub stands in for them.
"""

from collections.abc import Sequence
from fractions import Fraction
from typing import Final

from oracles._kernel import (
    HOURS_PER_DAY,
    ONE,
    ZERO,
    Ledger,
    additive_gross_pnl,
    additive_price_grid,
    binary_exposure_paths,
    build_ledger,
    canonical_record_bytes,
    compounded_gross_equity,
    exact,
    losing_segments,
    record_digest,
    repeat_daily,
    require_admissible,
    segment_returns,
    utc,
)

_START: Final = utc(2020, 1, 1)
_FIRST_OPEN: Final = Fraction(1000)

_ANTI_PERSISTENT: Final = (
    Fraction(1),
    Fraction(-1),
    Fraction(1),
    Fraction(-1),
    Fraction(1),
    Fraction(-1),
)
_PERSISTENT: Final = (
    Fraction(1),
    Fraction(1),
    Fraction(1),
    Fraction(-1),
    Fraction(-1),
    Fraction(1),
)
_GRIDS: Final = {
    "anti_persistent": _ANTI_PERSISTENT,
    "persistent": _PERSISTENT,
}


def _opens(daily_steps: Sequence[Fraction]) -> tuple[Fraction, ...]:
    return additive_price_grid(_FIRST_OPEN, repeat_daily(daily_steps))


def _daily_returns(opens: Sequence[Fraction]) -> tuple[Fraction, ...]:
    days = (len(opens) - 1) // HOURS_PER_DAY
    return tuple(
        (opens[(day + 1) * HOURS_PER_DAY - 1] - opens[day * HOURS_PER_DAY])
        / opens[day * HOURS_PER_DAY]
        for day in range(days)
    )


def _leaking_targets(opens: Sequence[Fraction]) -> tuple[Fraction, ...]:
    """Exposure for day ``k`` set by the return of day ``k`` itself.

    This reads ``open(24 * (k + 1) - 1)``, a price within the future decision
    day that does not exist at the decision. It is the deliberate leak.
    """
    return tuple(ONE if value > ZERO else ZERO for value in _daily_returns(opens))


def _lagged_targets(opens: Sequence[Fraction]) -> tuple[Fraction, ...]:
    """Causal control: exposure for day ``k`` set by the return of day ``k-1``.

    Every price it reads is strictly before the current decision boundary, so
    it is the same rule as the leak with one decision of lag and nothing else
    changed.
    """
    returns = _daily_returns(opens)
    return tuple(
        ZERO if day == 0 else (ONE if returns[day - 1] > ZERO else ZERO)
        for day in range(len(returns))
    )


def _ledger(opens: Sequence[Fraction], targets: Sequence[Fraction]) -> Ledger:
    return build_ledger(
        start=_START,
        opens=opens,
        exposures=repeat_daily(targets),
        cost_rate=ZERO,
    )


def test_the_synthetic_grids_have_constant_sign_inside_each_decision_day() -> None:
    for name, steps in _GRIDS.items():
        opens = _opens(steps)
        returns = segment_returns(opens)
        daily = _daily_returns(opens)
        for day, day_return in enumerate(daily):
            window = returns[day * HOURS_PER_DAY : (day + 1) * HOURS_PER_DAY]
            assert len(window) == HOURS_PER_DAY, name
            assert all((value > ZERO) == (day_return > ZERO) for value in window)
            assert day_return != ZERO


def test_both_signals_produce_admissible_exposure_paths() -> None:
    for steps in _GRIDS.values():
        opens = _opens(steps)
        require_admissible(_START, repeat_daily(_leaking_targets(opens)))
        require_admissible(_START, repeat_daily(_lagged_targets(opens)))


def test_the_leaking_signal_never_holds_a_losing_segment() -> None:
    for name, steps in _GRIDS.items():
        opens = _opens(steps)
        ledger = _ledger(opens, _leaking_targets(opens))
        assert losing_segments(ledger) == (), name
        held = [seg.exposure * seg.gross_return for seg in ledger.segments]
        assert all(value >= ZERO for value in held), name
        assert any(value > ZERO for value in held), name
        expected = sum((max(value, ZERO) for value in segment_returns(opens)), ZERO)
        assert additive_gross_pnl(ledger) == expected, name


def test_the_leaking_signal_has_a_monotone_non_decreasing_equity_curve() -> None:
    for name, steps in _GRIDS.items():
        opens = _opens(steps)
        ledger = _ledger(opens, _leaking_targets(opens))
        equity = ONE
        for segment in ledger.segments:
            following = equity * (ONE + segment.exposure * segment.gross_return)
            assert following >= equity, name
            equity = following
        assert equity == compounded_gross_equity(ledger), name
        assert equity > ONE, name


def test_the_leaking_signal_attains_the_exhaustive_optimum() -> None:
    for name, steps in _GRIDS.items():
        opens = _opens(steps)
        leak = _leaking_targets(opens)
        additive = {}
        compounded = {}
        for path in binary_exposure_paths(len(steps)):
            ledger = _ledger(opens, path)
            additive[path] = additive_gross_pnl(ledger)
            compounded[path] = compounded_gross_equity(ledger)
        best_additive = max(additive.values())
        best_compounded = max(compounded.values())
        assert additive[leak] == best_additive, name
        assert compounded[leak] == best_compounded, name
        winners = [path for path, value in additive.items() if value == best_additive]
        assert winners == [leak], name
        winners = [
            path for path, value in compounded.items() if value == best_compounded
        ]
        assert winners == [leak], name


def test_the_causal_lagged_control_is_not_absurd() -> None:
    for name, steps in _GRIDS.items():
        opens = _opens(steps)
        leak = _ledger(opens, _leaking_targets(opens))
        lagged = _ledger(opens, _lagged_targets(opens))
        assert losing_segments(lagged) != (), name
        assert additive_gross_pnl(lagged) < additive_gross_pnl(leak), name
        assert compounded_gross_equity(lagged) < compounded_gross_equity(leak), name
        best = max(
            additive_gross_pnl(_ledger(opens, path))
            for path in binary_exposure_paths(len(steps))
        )
        assert additive_gross_pnl(lagged) < best, name


def test_the_lagged_control_is_exactly_worst_on_an_anti_persistent_path() -> None:
    opens = _opens(_ANTI_PERSISTENT)
    lagged = _ledger(opens, _lagged_targets(opens))
    worst = min(
        additive_gross_pnl(_ledger(opens, path))
        for path in binary_exposure_paths(len(_ANTI_PERSISTENT))
    )
    assert additive_gross_pnl(lagged) == worst
    assert additive_gross_pnl(lagged) < ZERO
    assert compounded_gross_equity(lagged) < ONE


def test_buy_and_hold_is_flat_on_the_anti_persistent_path() -> None:
    opens = _opens(_ANTI_PERSISTENT)
    assert opens[-1] == opens[0]
    hold = _ledger(opens, (ONE,) * len(_ANTI_PERSISTENT))
    leak = _ledger(opens, _leaking_targets(opens))
    lagged = _ledger(opens, _lagged_targets(opens))
    assert compounded_gross_equity(hold) == ONE
    assert compounded_gross_equity(leak) > ONE
    assert compounded_gross_equity(lagged) < ONE


def test_the_leaking_exposure_reads_a_price_from_the_future() -> None:
    opens = _opens(_PERSISTENT)
    assert opens[2 * HOURS_PER_DAY - 1] == Fraction(1047)
    perturbed = (
        opens[: 2 * HOURS_PER_DAY - 1] + (Fraction(900),) + opens[2 * HOURS_PER_DAY :]
    )
    base_leak = _leaking_targets(opens)
    base_lagged = _lagged_targets(opens)
    moved_leak = _leaking_targets(perturbed)
    moved_lagged = _lagged_targets(perturbed)

    assert base_leak[1] == ONE
    assert moved_leak[1] == ZERO
    assert moved_leak != base_leak

    assert moved_lagged[:2] == base_lagged[:2]
    assert base_lagged[1] == ONE
    assert base_lagged[2] == ONE
    assert moved_lagged[2] == ZERO


def test_the_lagged_exposure_ignores_every_strictly_future_price() -> None:
    opens = _opens(_PERSISTENT)
    base = _lagged_targets(opens)
    for day in range(1, len(_PERSISTENT)):
        boundary = day * HOURS_PER_DAY
        for offset in (1, HOURS_PER_DAY // 2, HOURS_PER_DAY):
            index = boundary + offset
            if index >= len(opens):
                continue
            perturbed = opens[:index] + (opens[index] / 2,) + opens[index + 1 :]
            moved = _lagged_targets(perturbed)
            assert moved[: day + 1] == base[: day + 1]


def _canary_record() -> dict[str, str]:
    record: dict[str, str] = {}
    for name, steps in _GRIDS.items():
        opens = _opens(steps)
        for label, targets in (
            ("leaking", _leaking_targets(opens)),
            ("lagged", _lagged_targets(opens)),
            ("buy_and_hold", (ONE,) * len(steps)),
        ):
            ledger = _ledger(opens, targets)
            key = f"{name}.{label}"
            record[f"{key}.additive_gross"] = exact(additive_gross_pnl(ledger))
            record[f"{key}.compounded_gross"] = exact(compounded_gross_equity(ledger))
            record[f"{key}.losing_segments"] = str(len(losing_segments(ledger)))
            record[f"{key}.targets"] = ",".join(exact(value) for value in targets)
    return record


def test_the_canary_record_is_byte_identical_across_reruns() -> None:
    first = canonical_record_bytes(_canary_record())
    second = canonical_record_bytes(_canary_record())
    assert first == second
    assert record_digest(first) == record_digest(second)
    assert b"leaking" in first and b"lagged" in first


def test_the_canary_record_separates_the_leak_from_the_control() -> None:
    record = _canary_record()
    for name in _GRIDS:
        assert record[f"{name}.leaking.losing_segments"] == "0"
        assert record[f"{name}.lagged.losing_segments"] != "0"
        leak = Fraction(record[f"{name}.leaking.additive_gross"])
        lagged = Fraction(record[f"{name}.lagged.additive_gross"])
        assert leak > lagged
        assert record[f"{name}.leaking.targets"] != record[f"{name}.lagged.targets"]
