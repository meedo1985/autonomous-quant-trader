"""Independent NumPy ``float64`` reference for the frozen backtester semantics.

This module is the ``NumPy reference`` layer that
``docs/RESEARCH_CONSTITUTION.md`` section 16 places between the accepted Task 6
oracle/canary suite and the future production implementation. It is a research
validation artefact and nothing else:

* it lives under ``tests/`` and is test-private on purpose,
* it imports nothing from ``src/aqt`` and is never imported by ``aqt``,
* it reuses no code from the exact Task 6 kernel, and
* it is **not** the production backtester, adapter, metrics engine, strategy or
  validation engine. Those belong to later scheduled tasks.

Independence from the exact oracle
----------------------------------

The accepted Task 6 kernel (``tests/oracles/_kernel.py``) transcribes the same
frozen rules into :class:`fractions.Fraction` arithmetic over ``datetime``
timestamps. This module was written separately and differs deliberately:

* every quantity is ``numpy.float64``, not an exact rational,
* scheduling is decided by **bar-index arithmetic** (``(start_hour + i) % 24``
  and a bar count since the last risk increase) instead of ``datetime``
  subtraction and ``timedelta`` comparison,
* the per-segment record is a set of ``numpy`` arrays rather than a tuple of
  frozen dataclasses, and the aggregate reductions are ``numpy`` prefix scans,
* the inclusive 10 percentage-point band is decided by a ULP-aware float
  comparator, which an exact rational oracle does not need at all.

Transcribed frozen semantics
----------------------------

* ``specs/BACKTESTER_SPEC_v1.md`` item 1: input is a timestamped target-exposure
  path plus open prices and the frozen cost-model inputs.
* Item 2: a decision at ``close(t)`` executes at ``open(t+1)``. Segment ``i``
  is the interval ``[open(i), open(i+1))`` and its exposure is what is actually
  held over that interval after the execution at ``open(i)``. Because UTC has
  no daylight offset, ``close(t) == open(t+1)`` and the hour of the execution
  opportunity is ``(start_hour_utc + i) % 24``.
* Item 3: targets are clipped to ``[0, 1]`` (``scope.max_exposure_per_asset``).
* Item 4: cost is charged on the absolute change in exposure, at a per-side
  rate expressed as a fraction of traded notional
  (``specs/COST_MODEL_v1.md``), and is charged at the execution, before the
  exposure earns the following open-to-open return.
* Item 5: risk increases happen only at the ``00:00`` UTC scheduled decision
  and only at least 24h after the previous risk increase
  (``scope.risk_increase_rule``).
* Item 6: intraday hourly actions are allowed only for exposure reductions
  that reach the 10 percentage-point band
  (``scope.intraday_action_rule``). A forbidden increase is **held**, exactly
  as Task 5's ``aqt.benchmarks.canonical.rebalance`` holds it; it is never
  deferred, queued, partially filled or silently retimed.
* Item 7: no partial fills and no passive limits; a permitted change executes
  completely at the next open.
* Item 8: PnL follows the actual simulated exposure after execution, never the
  requested target. ``requested_target``, ``clipped_target``,
  ``held_weight_before`` and ``exposure`` are kept distinct for that reason.

Human-accepted conventions (``review/task6/HUMAN_ACCEPTANCE.md``)
-----------------------------------------------------------------

1. Production accounting compounds equity, with cost charged at the execution
   before the following return. The additive fixed-notional aggregator is kept
   as an independent diagnostic.
2. Decision targets and actual held weights are distinct. On a no-trade
   segment with zero cash return the fractional risky weight drifts as
   ``w * (1 + r) / (1 + w * r)``, and the next trade is measured from the
   drifted weight to the clipped target.
3. Every path starts flat, so entering the market is a charged trade.
4. There is no forced terminal liquidation; a non-zero ending exposure is
   marked to the final open and nothing is charged for holding it.
5. The 10 percentage-point band is inclusive and applies to the difference
   between the clipped target and the actual held weight.

Band tolerance
--------------

:data:`REBALANCE_BAND_TOLERANCE` reproduces the *value* of Task 5's centralized
comparator ``aqt.benchmarks.canonical.REBALANCE_BAND_TOLERANCE``, which is
``4 * math.ulp(1.0)``. It is restated here rather than imported because the
Task 7 authorization forbids this reference from importing ``src/aqt``; the
restated value is asserted against ``4 * math.ulp(1.0)`` by the comparison
suite. See ``review/task7/LOCAL_REPORT.md`` for the recorded assumption.

Nothing here reads a clock, a file, a network socket, an environment variable
or a random generator, and no input is mutated. Invalid input raises
:class:`ReferenceError`; nothing is clamped, defaulted or skipped behind the
caller's back except the clipping that item 3 prescribes.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

import numpy as np
import numpy.typing as npt

Float64Array = npt.NDArray[np.float64]
Int64Array = npt.NDArray[np.int64]

ZERO: Final[np.float64] = np.float64(0.0)
ONE: Final[np.float64] = np.float64(1.0)

MIN_EXPOSURE: Final[np.float64] = ZERO
MAX_EXPOSURE: Final[np.float64] = ONE

BARS_PER_DAY: Final[int] = 24
SCHEDULED_DECISION_ANCHOR_HOUR_UTC: Final[int] = 0
MINIMUM_HOLD_BARS_FOR_RISK_INCREASE: Final[int] = 24

REBALANCE_BAND_ABSOLUTE: Final[np.float64] = np.float64(0.10)
REBALANCE_BAND_TOLERANCE: Final[np.float64] = np.float64(4.0 * math.ulp(1.0))
REBALANCE_BAND_THRESHOLD: Final[np.float64] = (
    REBALANCE_BAND_ABSOLUTE - REBALANCE_BAND_TOLERANCE
)

MACHINE_EPSILON: Final[np.float64] = np.finfo(np.float64).eps
"""``numpy.float64`` machine epsilon, ``2 ** -52``."""

UNIT_ROUNDOFF: Final[np.float64] = np.float64(0.5) * MACHINE_EPSILON
"""Binary64 unit roundoff ``u = 2 ** -53``; the whole comparison bound scale."""


class ReferenceError(ValueError):
    """Raised when an input violates a transcribed frozen backtester rule."""


class Action(StrEnum):
    """Which frozen rule decided one execution opportunity.

    The vocabulary matches Task 5's ``RebalanceAction`` so that the reference
    and the already-reviewed target-path rules can be read side by side. No
    Task 5 code is imported.
    """

    HOLD = "hold"
    SCHEDULED_INCREASE = "scheduled_increase"
    SCHEDULED_REDUCTION = "scheduled_reduction"
    INTRADAY_REDUCTION = "intraday_reduction"


@dataclass(frozen=True, slots=True)
class ReferencePath:
    """One simulated exposure path in ``float64``, segment by segment.

    ``requested_target`` is what the decision asked for, ``clipped_target`` is
    that request after the frozen ``[0, 1]`` clip, ``held_weight_before`` is the
    actual drifted weight entering the execution opportunity, and ``exposure``
    is the actual weight held over ``[open(i), open(i+1))`` after execution.
    """

    start_hour_utc: int
    cost_rate: np.float64
    stress_multiplier: np.float64
    execution_hour: Int64Array
    gross_return: Float64Array
    requested_target: Float64Array
    clipped_target: Float64Array
    held_weight_before: Float64Array
    exposure: Float64Array
    traded: Float64Array
    cost: Float64Array
    action: tuple[Action, ...]

    def __len__(self) -> int:
        """Number of simulated segments."""
        return int(self.exposure.size)


def _as_float64_vector(
    values: Sequence[float] | Float64Array, name: str
) -> Float64Array:
    """Copy ``values`` into a validated one-dimensional ``float64`` vector."""
    array = np.array(values, dtype=np.float64, copy=True)
    if array.ndim != 1:
        raise ReferenceError(f"{name} must be one-dimensional, got {array.ndim} axes")
    if not bool(np.all(np.isfinite(array))):
        raise ReferenceError(f"{name} must contain only finite values")
    return array


def _as_float64_scalar(value: float, name: str) -> np.float64:
    """Validate one finite ``float64`` scalar input."""
    scalar = np.float64(value)
    if not bool(np.isfinite(scalar)):
        raise ReferenceError(f"{name} must be finite, got {value!r}")
    return scalar


def segment_returns(opens: Sequence[float] | Float64Array) -> Float64Array:
    """Simple open-to-open returns ``(P[i+1] - P[i]) / P[i]`` in ``float64``.

    Two roundings per element: one subtraction and one division.
    """
    prices = _as_float64_vector(opens, "opens")
    if prices.size < 2:
        raise ReferenceError("a price grid needs at least two opens")
    if not bool(np.all(prices > 0.0)):
        raise ReferenceError("open prices must be strictly positive")
    returns: Float64Array = (prices[1:] - prices[:-1]) / prices[:-1]
    if not bool(np.all(returns > -1.0)):
        raise ReferenceError("a positive-price segment return must exceed -1")
    return returns


def clip_exposure(target: float) -> np.float64:
    """Clip one decision target to the frozen long-only ``[0, 1]`` range.

    Clipping selects an operand, so it introduces no rounding of its own.
    """
    return np.float64(np.clip(np.float64(target), MIN_EXPOSURE, MAX_EXPOSURE))


def clip_exposures(targets: Sequence[float] | Float64Array) -> Float64Array:
    """Vectorised :func:`clip_exposure` over a whole requested-target path."""
    return np.clip(_as_float64_vector(targets, "targets"), MIN_EXPOSURE, MAX_EXPOSURE)


def drifted_exposure(exposure: np.float64, gross_return: np.float64) -> np.float64:
    """Actual risky weight after a no-trade segment with zero cash return.

    ``w * (1 + r) / (1 + w * r)``, the accepted Task 6 drift identity, in five
    roundings: ``1 + r``, ``w * (1 + r)``, ``w * r``, ``1 + w * r``, divide.
    """
    if not bool(MIN_EXPOSURE <= exposure <= MAX_EXPOSURE):
        raise ReferenceError(f"actual exposure {exposure!r} is outside [0, 1]")
    if bool(gross_return <= -ONE):
        raise ReferenceError("a positive-price segment return must exceed -1")
    return exposure * (ONE + gross_return) / (ONE + exposure * gross_return)


def reaches_rebalance_band(change: np.float64) -> bool:
    """Whether a change reaches the inclusive frozen 10 percentage-point band.

    This is the single place the band threshold is evaluated in the reference.
    A change that is exactly 10 percentage points in exact arithmetic can be
    rendered slightly below ``0.10`` in binary64 -- ``0.6 - 0.5`` is
    ``0.09999999999999998`` -- so the comparison carries the accepted
    :data:`REBALANCE_BAND_TOLERANCE` slack. The slack is a binary-representation
    allowance, not a materiality threshold.
    """
    return bool(abs(change) >= REBALANCE_BAND_THRESHOLD)


def increase_is_eligible(
    execution_hour: int, bars_since_last_increase: int | None
) -> bool:
    """Whether a risk increase may execute at this opportunity.

    ``bars_since_last_increase`` is ``None`` when no risk increase has happened
    yet, in which case the 24h minimum hold cannot block anything. The bound is
    inclusive: exactly 24 bars of 1h is a satisfied minimum hold.
    """
    if execution_hour != SCHEDULED_DECISION_ANCHOR_HOUR_UTC:
        return False
    if bars_since_last_increase is None:
        return True
    if bars_since_last_increase < 0:
        raise ReferenceError(
            f"bars since the last risk increase cannot be negative, got "
            f"{bars_since_last_increase!r}"
        )
    return bars_since_last_increase >= MINIMUM_HOLD_BARS_FOR_RISK_INCREASE


def build_reference_path(
    *,
    start_hour_utc: int,
    opens: Sequence[float] | Float64Array,
    targets: Sequence[float] | Float64Array,
    cost_rate: float,
    stress_multiplier: float = 1.0,
) -> ReferencePath:
    """Simulate one requested-target path under the frozen semantics.

    The loop is sequential because the path is: what a decision may do depends
    on the actual weight the previous segment's drift left behind and on when
    the last risk increase executed. Every arithmetic expression below is
    written once, in a fixed order, so that the comparison suite can derive its
    tolerance from the operation count.
    """
    if not 0 <= start_hour_utc < BARS_PER_DAY:
        raise ReferenceError(
            f"start_hour_utc must be an hour of the day, got {start_hour_utc!r}"
        )
    returns = segment_returns(opens)
    requested = _as_float64_vector(targets, "targets")
    if requested.size != returns.size:
        raise ReferenceError(
            f"{requested.size} targets cannot fill {returns.size} segments"
        )
    rate = _as_float64_scalar(cost_rate, "cost_rate")
    stress = _as_float64_scalar(stress_multiplier, "stress_multiplier")
    if bool(rate < 0.0) or bool(stress < 0.0):
        raise ReferenceError("cost rate and stress multiplier must be non-negative")
    if bool(rate * stress >= 1.0):
        raise ReferenceError("a full-size trade would cost at least its own notional")

    count = int(requested.size)
    bar_index = np.arange(count, dtype=np.int64)
    execution_hour: Int64Array = (start_hour_utc + bar_index) % BARS_PER_DAY
    clipped = np.clip(requested, MIN_EXPOSURE, MAX_EXPOSURE)
    held_weight_before = np.zeros(count, dtype=np.float64)
    exposure = np.zeros(count, dtype=np.float64)
    traded = np.zeros(count, dtype=np.float64)
    cost = np.zeros(count, dtype=np.float64)
    actions: list[Action] = []

    held = MIN_EXPOSURE
    last_increase_index: int | None = None
    for index in range(count):
        hour = int(execution_hour[index])
        target = np.float64(clipped[index])
        held_weight_before[index] = held
        change = target - held
        action = Action.HOLD
        executed = held
        size = ZERO
        if reaches_rebalance_band(change):
            elapsed = (
                None if last_increase_index is None else index - last_increase_index
            )
            if bool(change < ZERO):
                action = (
                    Action.SCHEDULED_REDUCTION
                    if hour == SCHEDULED_DECISION_ANCHOR_HOUR_UTC
                    else Action.INTRADAY_REDUCTION
                )
                executed = target
                size = abs(change)
            elif increase_is_eligible(hour, elapsed):
                action = Action.SCHEDULED_INCREASE
                last_increase_index = index
                executed = target
                size = abs(change)
        actions.append(action)
        exposure[index] = executed
        traded[index] = size
        cost[index] = rate * stress * size
        held = drifted_exposure(executed, np.float64(returns[index]))

    return ReferencePath(
        start_hour_utc=start_hour_utc,
        cost_rate=rate,
        stress_multiplier=stress,
        execution_hour=execution_hour,
        gross_return=returns,
        requested_target=requested,
        clipped_target=clipped,
        held_weight_before=held_weight_before,
        exposure=exposure,
        traded=traded,
        cost=cost,
        action=tuple(actions),
    )


def _sequential_sum(values: Float64Array) -> np.float64:
    """Left-to-right ``float64`` sum.

    ``numpy.cumsum`` is a prefix scan, so it accumulates strictly left to
    right; the pairwise reordering that ``numpy.sum`` is free to use would not
    match the operation order the derived comparison bound models.
    """
    if values.size == 0:
        return ZERO
    return np.float64(np.cumsum(values)[-1])


def _sequential_product(values: Float64Array) -> np.float64:
    """Left-to-right ``float64`` product, for the same reason as the sum."""
    if values.size == 0:
        return ONE
    return np.float64(np.cumprod(values)[-1])


def segment_pnl(path: ReferencePath) -> Float64Array:
    """Per-segment fixed-notional PnL ``exposure_i * return_i``."""
    return path.exposure * path.gross_return


def turnover(path: ReferencePath) -> np.float64:
    """Total absolute change in exposure, the charged initial entry included."""
    return _sequential_sum(path.traded)


def total_cost(path: ReferencePath) -> np.float64:
    """Total cost as a fraction of a fixed unit notional."""
    return _sequential_sum(path.cost)


def additive_gross_pnl(path: ReferencePath) -> np.float64:
    """Diagnostic fixed-notional gross PnL ``sum(exposure_i * return_i)``."""
    return _sequential_sum(segment_pnl(path))


def additive_net_pnl(path: ReferencePath) -> np.float64:
    """Diagnostic fixed-notional PnL net of the charged cost."""
    return additive_gross_pnl(path) - total_cost(path)


def compounded_gross_equity(path: ReferencePath) -> np.float64:
    """Terminal equity from a unit start, ignoring cost."""
    return _sequential_product(ONE + segment_pnl(path))


@dataclass(frozen=True, slots=True)
class NetEquityCurve:
    """The compounded net equity path, resolved *inside* each segment.

    Terminal equity alone cannot distinguish charging cost before the following
    return from charging it after: the two are the same product of the same
    scalars, and multiplication commutes. The distinction is observable only
    part-way through a segment, which is what this curve exposes.

    ``before[i]`` is equity entering execution ``i``. ``after_cost[i]`` is
    equity once that execution's cost has been charged, and ``after_return[i]``
    is equity at the end of segment ``i``. ``charged[i] = before[i] -
    after_cost[i]`` is therefore the cost in currency terms, levied on the
    pre-return equity, which is the accepted Task 6 convention 1.
    """

    before: Float64Array
    after_cost: Float64Array
    after_return: Float64Array
    charged: Float64Array


def net_equity_curve(path: ReferencePath) -> NetEquityCurve:
    """Resolve the compounded net equity path segment by segment.

    The factors alternate ``1 - cost_i`` then ``1 + exposure_i * return_i``, so
    cost is charged at the execution, before the exposure earns the following
    open-to-open return. ``numpy.cumprod`` is a strictly left-to-right prefix
    scan, so its odd and even entries are exactly the two intra-segment states.
    """
    count = len(path)
    factors = np.zeros(2 * count, dtype=np.float64)
    factors[0::2] = ONE - path.cost
    factors[1::2] = ONE + segment_pnl(path)
    running: Float64Array = np.cumprod(factors)
    after_cost: Float64Array = running[0::2]
    after_return: Float64Array = running[1::2]
    before: Float64Array = np.concatenate(
        (np.array([ONE], dtype=np.float64), after_return[:-1])
    )
    return NetEquityCurve(
        before=before,
        after_cost=after_cost,
        after_return=after_return,
        charged=before - after_cost,
    )


def compounded_net_equity(path: ReferencePath) -> np.float64:
    """Terminal equity from a unit start, cost charged at each execution.

    This is the last point of :func:`net_equity_curve`, so the terminal figure
    and the intra-segment path can never describe different accounting.
    """
    if len(path) == 0:
        return ONE
    return np.float64(net_equity_curve(path).after_return[-1])
