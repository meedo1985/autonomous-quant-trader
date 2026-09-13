"""The reference's band comparator must agree with Task 5's centralized one.

``review/task6/HUMAN_ACCEPTANCE.md`` decision 5 states that float
implementations "must reuse Task 5's centralized ULP-aware comparator". The
Task 7 authorization simultaneously forbids the NumPy reference from importing
``src/aqt``, so the reference restates the tolerance value instead of importing
it.

Restating a constant is only safe if something detects the two drifting apart.
That is this module's whole job, and it is the only place in the Task 7
reference layer that imports ``aqt``:
:mod:`reference._numpy_reference` itself never does, so the reference stays
independent of production while the accepted convention stays enforced.

If Task 5's tolerance is ever changed, this file fails and the reference has to
be updated deliberately rather than silently disagreeing with production.
"""

import math
from fractions import Fraction
from typing import Final

import numpy as np

from aqt.benchmarks.canonical import MAX_EXPOSURE
from aqt.benchmarks.canonical import (
    REBALANCE_BAND_ABSOLUTE as TASK5_BAND_ABSOLUTE,
)
from aqt.benchmarks.canonical import (
    REBALANCE_BAND_TOLERANCE as TASK5_BAND_TOLERANCE,
)
from aqt.benchmarks.canonical import (
    reaches_rebalance_band as task5_reaches_rebalance_band,
)
from reference._numpy_reference import (
    REBALANCE_BAND_ABSOLUTE,
    REBALANCE_BAND_THRESHOLD,
    REBALANCE_BAND_TOLERANCE,
    reaches_rebalance_band,
)

_PROBE_CHANGES: Final[tuple[float, ...]] = (
    0.0,
    1e-18,
    -1e-18,
    0.05,
    -0.05,
    0.09,
    0.0999999,
    0.09999999999999998,  # 0.5 - 0.4 and 0.6 - 0.5 both land here
    0.5 - 0.4,
    0.6 - 0.5,
    0.3 - 0.2,
    0.1,
    -0.1,
    0.1 + 1e-17,
    0.1 - 1e-6,
    -(0.1 - 1e-6),
    0.10000000000000003,
    0.2,
    -0.2,
    0.8 - 0.5,
    1.0,
    -1.0,
    float(Fraction(29, 105)),
    float(Fraction(1, 2) - Fraction(11, 21)),
)


def test_the_reference_restates_task5_band_constants_exactly() -> None:
    assert float(REBALANCE_BAND_ABSOLUTE) == TASK5_BAND_ABSOLUTE
    assert float(REBALANCE_BAND_TOLERANCE) == TASK5_BAND_TOLERANCE
    assert TASK5_BAND_TOLERANCE == 4.0 * math.ulp(MAX_EXPOSURE)
    assert float(REBALANCE_BAND_TOLERANCE) == 4.0 * math.ulp(1.0)
    assert float(REBALANCE_BAND_THRESHOLD) == (
        TASK5_BAND_ABSOLUTE - TASK5_BAND_TOLERANCE
    )


def test_the_reference_comparator_agrees_with_task5_on_every_probe() -> None:
    for change in _PROBE_CHANGES:
        assert reaches_rebalance_band(np.float64(change)) == (
            task5_reaches_rebalance_band(change)
        ), change


def test_the_reference_comparator_agrees_with_task5_on_a_dense_sweep() -> None:
    """A dense sweep straight through the band, plus its ULP neighbourhood."""
    changes: list[float] = []
    for step in range(-400, 401):
        changes.append(step / 2000.0)
    threshold = float(REBALANCE_BAND_THRESHOLD)
    neighbour = threshold
    for _ in range(64):
        neighbour = math.nextafter(neighbour, -math.inf)
        changes.append(neighbour)
    neighbour = threshold
    for _ in range(64):
        neighbour = math.nextafter(neighbour, math.inf)
        changes.append(neighbour)
    for change in changes:
        for signed in (change, -change):
            assert reaches_rebalance_band(np.float64(signed)) == (
                task5_reaches_rebalance_band(signed)
            ), signed


def test_the_band_slack_is_a_representation_allowance_not_a_materiality_rule() -> None:
    """The slack is four units in the last place, nothing economic."""
    assert 0.0 < TASK5_BAND_TOLERANCE < 1e-15
    assert Fraction(TASK5_BAND_TOLERANCE) == Fraction(4, 2**52)
    # Anything a trader would call "nearly 10pp" is still refused.
    assert not reaches_rebalance_band(np.float64(0.0999))
    assert not task5_reaches_rebalance_band(0.0999)
