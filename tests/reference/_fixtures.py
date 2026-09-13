"""Deterministic synthetic fixture matrix for the Task 7 reference comparison.

Every fixture here is an exact rational description of one simulated path:
a UTC start hour, a grid of open prices, a requested-target path, and the
scenario label the comparison suite reports failures under. Nothing in this
module reads a clock, a file, a network socket, an environment variable or a
random generator, and nothing here is market data. The prices are small exact
additive grids, so the exact oracle can evaluate them in closed rational form
and the ``float64`` reference can be compared against that value.

The price-grid and daily-expansion helpers, the frozen cost rates and the
target paths are taken from the accepted Task 6 suite on purpose: the Task 7
authorization allows reusing the accepted **fixtures and expected values**,
and reusing them is what makes the comparison a comparison rather than two
independent guesses. No Task 6 *backtest kernel* logic is reused to produce a
reference result: :mod:`reference._numpy_reference` transcribes the frozen
rules independently, and :mod:`reference._error_bounds` derives the tolerance
independently.

Coverage
--------

``binary.*``
    The four accepted Task 6 binary scenarios (``cash``, ``buy_and_hold``,
    ``alternating``, ``late_entry``) over both accepted price grids. Every
    executed exposure is ``0`` or ``1``, which is exactly representable in
    binary64, so these fixtures carry exact-equality expectations.
``fractional_drift``
    The accepted no-trade drift identity: a ``1/2`` weight held through a
    ``+10%`` and then a ``+10%`` segment drifts to ``11/21`` and is not
    rebalanced for free.
``adverse_drift_hold``
    A ``1/2`` weight halved by a ``-50%`` segment drifts down to ``1/3``. The
    restoring change is an increase, and an increase is forbidden intraday, so
    the reference must **hold** it exactly as Task 5 does.
``clipping``
    Requested targets outside ``[0, 1]`` on both sides, both of which execute.
``band_boundary_*``
    A change of exactly ``10`` percentage points, which the inclusive band
    admits, and a change one part per million below it, which it refuses.
    ``0.6 - 0.5`` is ``0.09999999999999998`` in binary64, so the first case is
    precisely the one Task 5's ULP-aware comparator exists for.
``scheduled_increase``
    The accepted 25-segment path whose second trade is measured from the
    drifted ``11/21`` weight, not from the previous ``1/2`` target.
``intraday_increase_held``
    An increase requested at 01:00 UTC and re-requested every hour. It is held
    until the next 00:00 UTC scheduled decision and then executes in full. It
    is never queued, partially filled or retimed to some other bar.
``offset_start_hour``
    The same rules from a 17:00 UTC start, so that the reference's modular
    ``(start_hour + i) % 24`` scheduling is checked against the oracle's
    ``datetime`` arithmetic rather than against itself.
``causal_lagged`` / ``leaking``
    The accepted Task 6 leakage-canary signals: exposure for day ``k`` set by
    the return of day ``k`` itself (the deliberate leak) versus by the return
    of day ``k-1`` (the causal control). Wiring these to the NumPy reference is
    the step ``docs/RESEARCH_CONSTITUTION.md`` section 18 asks for.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from fractions import Fraction
from typing import Final

from oracles._kernel import (
    HOURS_PER_DAY,
    ONE,
    ZERO,
    additive_price_grid,
    cost_rate_from_bps,
    per_side_cost_bps,
    repeat_daily,
    utc,
)

START: Final[datetime] = utc(2020, 1, 1)
"""Midnight UTC, the scheduled decision anchor, as in the Task 6 suite."""

OFFSET_START: Final[datetime] = utc(2020, 1, 1, 17)
"""A deliberately unaligned start, so hour 0 first recurs at bar index 7."""

FIRST_OPEN: Final[Fraction] = Fraction(1000)

FLOOR_RATE: Final[Fraction] = cost_rate_from_bps(per_side_cost_bps(ZERO))
"""``13 bps`` per side: the frozen fallback fee, spread and slippage floor."""

CAP_RATE: Final[Fraction] = cost_rate_from_bps(per_side_cost_bps(Fraction(10_000)))
"""``27 bps`` per side: the same, with slippage at its frozen 15 bp cap."""

STRESS_MULTIPLIERS: Final[tuple[Fraction, ...]] = (
    Fraction(1),
    Fraction(3, 2),
    Fraction(2),
    Fraction(3),
)
"""The frozen ``COST_MODEL_v1.md`` stress ladder."""

RISING_THEN_FALLING: Final = (Fraction(1), Fraction(-1), Fraction(2), Fraction(-1))
FALLING_THEN_RISING: Final = (Fraction(-1), Fraction(3), Fraction(-2), Fraction(1))

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

_BINARY_SCENARIOS: Final[tuple[tuple[str, tuple[Fraction, ...]], ...]] = (
    ("cash", (ZERO, ZERO, ZERO, ZERO)),
    ("buy_and_hold", (ONE, ONE, ONE, ONE)),
    ("alternating", (ONE, ZERO, ONE, ZERO)),
    ("late_entry", (ZERO, ONE, ONE, ZERO)),
)

_BINARY_GRIDS: Final[tuple[tuple[str, tuple[Fraction, ...]], ...]] = (
    ("rising_then_falling", RISING_THEN_FALLING),
    ("falling_then_rising", FALLING_THEN_RISING),
)


class FixtureError(ValueError):
    """Raised when a fixture is not the deterministic shape it claims to be."""


@dataclass(frozen=True, slots=True)
class Fixture:
    """One synthetic path: exact prices, exact requested targets, exact start.

    ``binary_executed`` records whether every exposure the frozen rules end up
    holding on this path is ``0`` or ``1``. Those two values, their differences
    and their sums are exact in binary64, so the comparison suite demands exact
    equality for the affected quantities instead of a derived bound.
    """

    name: str
    start: datetime
    opens: tuple[Fraction, ...]
    targets: tuple[Fraction, ...]
    binary_executed: bool

    def __post_init__(self) -> None:
        if len(self.opens) < 2:
            raise FixtureError(f"{self.name}: a price grid needs at least two opens")
        if len(self.targets) != len(self.opens) - 1:
            raise FixtureError(
                f"{self.name}: {len(self.targets)} targets cannot fill "
                f"{len(self.opens) - 1} segments"
            )
        if any(price <= 0 for price in self.opens):
            raise FixtureError(f"{self.name}: open prices must be strictly positive")

    @property
    def start_hour_utc(self) -> int:
        """The UTC hour the reference's modular bar arithmetic starts from."""
        return self.start.hour

    @property
    def float_opens(self) -> list[float]:
        """The price grid as the ``float64`` reference receives it."""
        return [float(price) for price in self.opens]

    @property
    def float_targets(self) -> list[float]:
        """The requested-target path as the ``float64`` reference receives it."""
        return [float(target) for target in self.targets]


def _grid(daily_steps: Sequence[Fraction]) -> tuple[Fraction, ...]:
    """One exact additive hourly price grid, expanded from daily steps."""
    return additive_price_grid(FIRST_OPEN, repeat_daily(daily_steps))


def _flat_grid(segments: int, price: Fraction = FIRST_OPEN) -> tuple[Fraction, ...]:
    """A constant price grid: every segment return is exactly zero, so weights
    do not drift and a scheduling fixture isolates scheduling alone."""
    return (price,) * (segments + 1)


def daily_returns(opens: Sequence[Fraction]) -> tuple[Fraction, ...]:
    """Exact within-day return of each decision day, as the canaries define it.

    Day ``k`` runs from ``open(24k)`` to ``open(24(k + 1) - 1)``. This is
    fixture construction, not backtest accounting.
    """
    days = (len(opens) - 1) // HOURS_PER_DAY
    return tuple(
        (opens[(day + 1) * HOURS_PER_DAY - 1] - opens[day * HOURS_PER_DAY])
        / opens[day * HOURS_PER_DAY]
        for day in range(days)
    )


def leaking_targets(opens: Sequence[Fraction]) -> tuple[Fraction, ...]:
    """Day ``k``'s exposure set by day ``k``'s own return: the deliberate leak."""
    return tuple(ONE if value > ZERO else ZERO for value in daily_returns(opens))


def lagged_targets(opens: Sequence[Fraction]) -> tuple[Fraction, ...]:
    """Day ``k``'s exposure set by day ``k-1``'s return: the causal control."""
    returns = daily_returns(opens)
    return tuple(
        ZERO if day == 0 else (ONE if returns[day - 1] > ZERO else ZERO)
        for day in range(len(returns))
    )


def _binary_fixtures() -> tuple[Fixture, ...]:
    return tuple(
        Fixture(
            name=f"binary.{grid_name}.{scenario}",
            start=START,
            opens=_grid(steps),
            targets=repeat_daily(targets),
            binary_executed=True,
        )
        for grid_name, steps in _BINARY_GRIDS
        for scenario, targets in _BINARY_SCENARIOS
    )


def _leakage_fixtures() -> tuple[Fixture, ...]:
    fixtures: list[Fixture] = []
    for grid_name, steps in (
        ("anti_persistent", _ANTI_PERSISTENT),
        ("persistent", _PERSISTENT),
    ):
        opens = _grid(steps)
        fixtures.append(
            Fixture(
                name=f"causal_lagged.{grid_name}",
                start=START,
                opens=opens,
                targets=repeat_daily(lagged_targets(opens)),
                binary_executed=True,
            )
        )
        fixtures.append(
            Fixture(
                name=f"leaking.{grid_name}",
                start=START,
                opens=opens,
                targets=repeat_daily(leaking_targets(opens)),
                binary_executed=True,
            )
        )
    return tuple(fixtures)


def _fractional_fixtures() -> tuple[Fixture, ...]:
    half = Fraction(1, 2)
    return (
        Fixture(
            name="fractional_drift",
            start=START,
            opens=(Fraction(100), Fraction(110), Fraction(121)),
            targets=(half, half),
            binary_executed=False,
        ),
        Fixture(
            name="adverse_drift_hold",
            start=START,
            opens=(Fraction(100), Fraction(50), Fraction(50)),
            targets=(half, half),
            binary_executed=False,
        ),
        Fixture(
            name="clipping",
            start=START,
            opens=(Fraction(100), Fraction(110), Fraction(99)),
            targets=(Fraction(2), Fraction(-1)),
            binary_executed=True,
        ),
        Fixture(
            name="band_boundary_exact_10pp",
            start=START,
            opens=_flat_grid(3),
            targets=(half, Fraction(2, 5), Fraction(2, 5)),
            binary_executed=False,
        ),
        Fixture(
            name="band_boundary_just_inside",
            start=START,
            opens=_flat_grid(3),
            targets=(
                half,
                Fraction(2, 5) + Fraction(1, 1_000_000),
                Fraction(2, 5) + Fraction(1, 1_000_000),
            ),
            binary_executed=False,
        ),
        Fixture(
            name="scheduled_increase",
            start=START,
            opens=(Fraction(100), Fraction(110), *((Fraction(110),) * 24)),
            targets=(half,) * 24 + (Fraction(4, 5),),
            binary_executed=False,
        ),
        Fixture(
            name="intraday_increase_held",
            start=START,
            opens=_grid((Fraction(1), Fraction(-1))),
            targets=(half,) + (Fraction(9, 10),) * 47,
            binary_executed=False,
        ),
        Fixture(
            name="offset_start_hour",
            start=OFFSET_START,
            opens=_grid((Fraction(1), Fraction(-1))),
            targets=(half,) * 12 + (Fraction(9, 10),) * 12 + (Fraction(1, 4),) * 24,
            binary_executed=False,
        ),
    )


FIXTURES: Final[tuple[Fixture, ...]] = (
    *_binary_fixtures(),
    *_fractional_fixtures(),
    *_leakage_fixtures(),
)
"""The whole deterministic fixture matrix, in a fixed order."""

COST_CASES: Final[tuple[tuple[str, Fraction, Fraction], ...]] = (
    ("free", ZERO, ONE),
    ("floor_x1", FLOOR_RATE, Fraction(1)),
    ("floor_x3", FLOOR_RATE, Fraction(3)),
    ("cap_x1", CAP_RATE, Fraction(1)),
    ("cap_x3", CAP_RATE, Fraction(3)),
)
"""Cost cases carried through the full per-quantity bound derivation."""

COST_LADDER: Final[tuple[tuple[str, Fraction, Fraction], ...]] = tuple(
    (f"{label}_x{multiplier.numerator}_{multiplier.denominator}", rate, multiplier)
    for label, rate in (("floor", FLOOR_RATE), ("cap", CAP_RATE))
    for multiplier in STRESS_MULTIPLIERS
)
"""The full frozen stress ladder, used for the cost-monotonicity checks."""


def fixture(name: str) -> Fixture:
    """Look one fixture up by name, refusing an unknown label."""
    for candidate in FIXTURES:
        if candidate.name == name:
            return candidate
    raise FixtureError(f"no fixture named {name!r}")
