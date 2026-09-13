"""Derived float64 comparison bounds for the Task 7 reference comparison.

The tolerance used to compare the ``float64`` reference with the exact Task 6
oracle is **not chosen**. It is derived, per fixture and per quantity, from the
binary64 unit roundoff and the number of arithmetic operations the reference
performs. Nothing in this module is a trading, materiality or performance
threshold, and nothing in it can be tuned to make a comparison pass: raising
the bound requires claiming more roundings than the reference actually
executes, which the comparison suite pins independently.

Derivation
----------

Binary64 arithmetic rounds to nearest, so for a single operation on
representable operands

    ``fl(x) = x * (1 + delta)``, ``|delta| <= u``, ``u = 2 ** -53``,

with ``u`` the unit roundoff, one half of
``numpy.finfo(numpy.float64).eps = 2 ** -52``. Every fixture keeps magnitudes
inside the normal range -- prices of order ``10 ** 3``, weights in ``[0, 1]``,
cost rates of order ``10 ** -3`` -- so no subnormal, overflow or underflow case
arises and the relative form above applies to every operation.

A :class:`Bounded` value carries the **exact rational value** the oracle
computes together with a proven **absolute** error bound on the ``float64``
value the reference computes. Bounds compose by the standard forward rules,
one :func:`_rounded` call per modeled machine operation:

* ``a + b`` and ``a - b``: propagated ``= A + B``
* ``a * b``: propagated ``= |a| * B + |b| * A + A * B``
* ``a / b``: propagated ``= (|a| * B + |b| * A) / (|b| * (|b| - B))``,
  which requires ``|b| > B``, i.e. the bound must exclude a zero divisor
* ``abs(a)``: exact, the bound is unchanged
* clipping to ``[0, 1]``: an operand selection, so the bound is unchanged when
  the target stays strictly inside the interval and becomes exactly zero when
  the target is clipped onto an endpoint

and each rounding then adds ``charge * (|value| + propagated)``.

Two deliberate conservatisms
----------------------------

1. :data:`ROUNDOFF_CHARGE_PER_OPERATION` charges **two** units of roundoff per
   modeled operation instead of one. An off-by-one in the modeled operation
   count of any single expression therefore cannot invalidate a bound. This
   only doubles a roundoff-scale quantity; it introduces no free parameter and
   no economic scale.
2. Correlated operands -- the same price appearing in both the numerator and
   the denominator of a return, for instance -- are bounded as if they were
   independent, which can only widen the bound.

The reference's reductions are prefix scans, so they accumulate strictly left
to right, and :func:`sequential_sum` and :func:`sequential_product` model that
same order starting from an exact ``0`` and ``1``. Charging those two identity
steps is a third conservatism, since ``numpy.cumsum`` and ``numpy.cumprod``
start from the first element.

Input representation
--------------------

Fixture values are exact rationals handed to the reference as
``float(value)``. That conversion error is not bounded by ``u``; it is
*computed exactly* by :func:`rounded_input` as
``abs(Fraction(float(value)) - value)``, which is zero for every value that is
already a binary64 number.

Bookkeeping size
----------------

Exact error bounds would grow unbounded denominators over a ninety-six segment
path, so every produced bound is rounded **up** to a binary64 number by
:func:`_coarsen`. ``float()`` rounds to nearest, so it is wrong by less than
one unit in the last place, and one step of ``math.nextafter`` toward infinity
therefore lands at or above the exact bound. This can only widen a bound, never
narrow it.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from typing import Final

ZERO: Final[Fraction] = Fraction(0)
ONE: Final[Fraction] = Fraction(1)

SIGNIFICAND_BITS: Final[int] = 53
"""Binary64 significand width, including the implicit leading bit."""

UNIT_ROUNDOFF: Final[Fraction] = Fraction(1, 2**SIGNIFICAND_BITS)
"""``u = 2 ** -53``, one half of the binary64 machine epsilon."""

ROUNDOFF_CHARGE_PER_OPERATION: Final[Fraction] = 2 * UNIT_ROUNDOFF
"""Two units of roundoff per modeled operation. See the module docstring."""


class BoundError(ValueError):
    """Raised when a bound cannot be derived without an unproven assumption."""


@dataclass(frozen=True, slots=True)
class Bounded:
    """An exact rational value plus a proven absolute error bound."""

    value: Fraction
    error: Fraction

    def __post_init__(self) -> None:
        if self.error < ZERO:
            raise BoundError(f"error bound {self.error} is negative")

    def contains(self, observed: float) -> bool:
        """Whether ``observed`` lies within the derived bound of the value."""
        return abs(Fraction(observed) - self.value) <= self.error


def is_representable(value: Fraction) -> bool:
    """Whether ``value`` is exactly a binary64 number."""
    return Fraction(float(value)) == value


def _coarsen(error: Fraction) -> Fraction:
    """Round an exact bound up to a binary64 number, keeping the rationals small."""
    if error == ZERO:
        return ZERO
    return Fraction(math.nextafter(float(error), math.inf))


def constant(value: Fraction) -> Bounded:
    """A literal the reference holds exactly, so it carries no error."""
    if not is_representable(value):
        raise BoundError(f"{value} is not exactly representable in binary64")
    return Bounded(value, ZERO)


def rounded_input(value: Fraction) -> Bounded:
    """A fixture rational handed to the reference as ``float(value)``."""
    return Bounded(value, _coarsen(abs(Fraction(float(value)) - value)))


def _rounded(value: Fraction, propagated: Fraction) -> Bounded:
    """Charge one modeled binary64 operation on top of the propagated error."""
    charge = ROUNDOFF_CHARGE_PER_OPERATION * (abs(value) + propagated)
    return Bounded(value, _coarsen(propagated + charge))


def add(left: Bounded, right: Bounded) -> Bounded:
    """Bound one ``float64`` addition."""
    return _rounded(left.value + right.value, left.error + right.error)


def sub(left: Bounded, right: Bounded) -> Bounded:
    """Bound one ``float64`` subtraction."""
    return _rounded(left.value - right.value, left.error + right.error)


def mul(left: Bounded, right: Bounded) -> Bounded:
    """Bound one ``float64`` multiplication."""
    propagated = (
        abs(left.value) * right.error
        + abs(right.value) * left.error
        + left.error * right.error
    )
    return _rounded(left.value * right.value, propagated)


def div(left: Bounded, right: Bounded) -> Bounded:
    """Bound one ``float64`` division, refusing a divisor that may be zero."""
    magnitude = abs(right.value)
    if magnitude <= right.error:
        raise BoundError("the divisor's error bound does not exclude zero")
    numerator = magnitude * left.error + abs(left.value) * right.error
    denominator = magnitude * (magnitude - right.error)
    return _rounded(left.value / right.value, numerator / denominator)


def absolute(value: Bounded) -> Bounded:
    """``abs`` is exact in binary64 and never widens an error bound."""
    return Bounded(abs(value.value), value.error)


def clip_exposure(target: Bounded) -> Bounded:
    """Bound the frozen ``[0, 1]`` clip, refusing an undecidable branch.

    Clipping selects an operand rather than computing one. When the target is
    clipped onto an endpoint the result is exactly ``0`` or ``1``, so the bound
    collapses to zero; when the target is strictly inside the interval the
    bound is carried through unchanged. A target whose bound straddles an
    endpoint would make the branch itself undecided, which no tolerance can
    cover, so it is rejected instead of guessed.
    """
    if target.value <= ZERO:
        if target.error > -target.value:
            raise BoundError(f"clipping {target.value} at 0 is not decided")
        return constant(ZERO)
    if target.value >= ONE:
        if target.error > target.value - ONE:
            raise BoundError(f"clipping {target.value} at 1 is not decided")
        return constant(ONE)
    if target.error >= min(target.value, ONE - target.value):
        raise BoundError(f"target {target.value} may be clipped by roundoff")
    return target


def drifted_exposure(exposure: Bounded, gross_return: Bounded) -> Bounded:
    """Bound ``w * (1 + r) / (1 + w * r)`` as the reference evaluates it."""
    one = constant(ONE)
    numerator = mul(exposure, add(one, gross_return))
    denominator = add(one, mul(exposure, gross_return))
    return div(numerator, denominator)


def sequential_sum(terms: Sequence[Bounded]) -> Bounded:
    """Bound a left-to-right ``float64`` sum."""
    total = constant(ZERO)
    for term in terms:
        total = add(total, term)
    return total


def sequential_product(factors: Sequence[Bounded]) -> Bounded:
    """Bound a left-to-right ``float64`` product."""
    product = constant(ONE)
    for factor in factors:
        product = mul(product, factor)
    return product


def segment_return_bounds(opens: Sequence[Fraction]) -> tuple[Bounded, ...]:
    """Bound ``(P[i+1] - P[i]) / P[i]`` for a whole price grid."""
    if len(opens) < 2:
        raise BoundError("a price grid needs at least two opens")
    prices = [rounded_input(price) for price in opens]
    return tuple(
        div(sub(prices[index + 1], prices[index]), prices[index])
        for index in range(len(prices) - 1)
    )


@dataclass(frozen=True, slots=True)
class PathBounds:
    """Derived bounds for every quantity the comparison suite checks."""

    gross_return: tuple[Bounded, ...]
    held_weight_before: tuple[Bounded, ...]
    change: tuple[Bounded, ...]
    exposure: tuple[Bounded, ...]
    traded: tuple[Bounded, ...]
    cost: tuple[Bounded, ...]
    turnover: Bounded
    total_cost: Bounded
    additive_gross_pnl: Bounded
    additive_net_pnl: Bounded
    compounded_gross_equity: Bounded
    compounded_net_equity: Bounded

    def widest_error(self) -> Fraction:
        """The largest derived bound in this path, for a scale diagnostic."""
        per_segment = (
            *self.gross_return,
            *self.held_weight_before,
            *self.change,
            *self.exposure,
            *self.traded,
            *self.cost,
        )
        aggregates = (
            self.turnover,
            self.total_cost,
            self.additive_gross_pnl,
            self.additive_net_pnl,
            self.compounded_gross_equity,
            self.compounded_net_equity,
        )
        return max(bounded.error for bounded in (*per_segment, *aggregates))


def path_bounds(
    *,
    opens: Sequence[Fraction],
    targets: Sequence[Fraction],
    cost_rate: Fraction,
    stress_multiplier: Fraction,
    traded_flags: Sequence[bool],
) -> PathBounds:
    """Derive every comparison bound for one fixture and one cost case.

    ``traded_flags`` is the exact oracle's decision sequence. Whether a
    decision trades at all is discrete, so no tolerance can cover a flipped
    decision; the comparison suite asserts decision equality separately and
    this walk consumes the exact decisions rather than re-deriving them.
    """
    returns = segment_return_bounds(opens)
    if len(targets) != len(returns):
        raise BoundError(f"{len(targets)} targets cannot fill {len(returns)} segments")
    if len(traded_flags) != len(returns):
        raise BoundError("the decision sequence does not cover every segment")

    one = constant(ONE)
    charge = mul(rounded_input(cost_rate), rounded_input(stress_multiplier))
    held = constant(ZERO)
    held_weight_before: list[Bounded] = []
    changes: list[Bounded] = []
    exposure: list[Bounded] = []
    traded: list[Bounded] = []
    cost: list[Bounded] = []
    for index, gross_return in enumerate(returns):
        clipped = clip_exposure(rounded_input(targets[index]))
        change = sub(clipped, held)
        held_weight_before.append(held)
        changes.append(change)
        if traded_flags[index]:
            executed = clipped
            size = absolute(change)
        else:
            executed = held
            size = constant(ZERO)
        exposure.append(executed)
        traded.append(size)
        cost.append(mul(charge, size))
        held = drifted_exposure(executed, gross_return)

    segment_pnl = [
        mul(weight, gross) for weight, gross in zip(exposure, returns, strict=True)
    ]
    charged = sequential_sum(cost)
    gross = sequential_sum(segment_pnl)
    net_factors: list[Bounded] = []
    for index in range(len(returns)):
        net_factors.append(sub(one, cost[index]))
        net_factors.append(add(one, mul(exposure[index], returns[index])))
    return PathBounds(
        gross_return=returns,
        held_weight_before=tuple(held_weight_before),
        change=tuple(changes),
        exposure=tuple(exposure),
        traded=tuple(traded),
        cost=tuple(cost),
        turnover=sequential_sum(traded),
        total_cost=charged,
        additive_gross_pnl=gross,
        additive_net_pnl=sub(gross, charged),
        compounded_gross_equity=sequential_product(
            [add(one, term) for term in segment_pnl]
        ),
        compounded_net_equity=sequential_product(net_factors),
    )
