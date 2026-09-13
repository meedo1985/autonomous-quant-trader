"""Task 6 shuffled-label null: exactly centred by exhaustive symmetry.

``BACKTESTER_SPEC_v1.md`` requires a "shuffled-label OOS null centered near
zero". "Near zero" cannot be tested without inventing a tolerance, and an
invented tolerance is a tunable scientific threshold, which this task is not
authorised to create. The null is therefore made **exactly** zero instead:

* the label permutation is enumerated exhaustively, so there is no sampler, no
  seed and no Monte-Carlo error, and
* the mean over all ``n!`` permutations is an exact rational identity,
  ``mean = (sum of exposures) * (sum of labels) / n`` for the PnL statistic and
  ``mean = 0`` for the Spearman statistic of
  ``protocol_v1.yaml benchmarks.null_models.shuffled_labels.gate_metric``.

Both identities are asserted as exact equalities, with the zero-sum label
vector making the PnL null exactly zero by construction.

The protocol's 500-sample sampled null over real confirmation data is a
property of the validation engine, not of these oracles, and is **DEFERRED TO
THE NEXT ORDERED TASKS**: no model, no prediction series and no validation
engine exists yet, and section 16 places them after the backtester.
"""

from collections.abc import Sequence
from fractions import Fraction
from itertools import permutations
from math import factorial
from typing import Final

from oracles._kernel import (
    ONE,
    ZERO,
    OracleError,
    canonical_record_bytes,
    cost_rate_from_bps,
    exact,
    per_side_cost_bps,
    record_digest,
    repeat_daily,
    require_admissible,
    spearman_rho,
    utc,
)

_START: Final = utc(2020, 1, 1)

_ZERO_SUM_LABELS: Final = (
    Fraction(3, 100),
    Fraction(-1, 100),
    Fraction(2, 100),
    Fraction(-4, 100),
    Fraction(1, 100),
    Fraction(-1, 100),
)
_DRIFTING_LABELS: Final = (
    Fraction(3, 100),
    Fraction(-1, 100),
    Fraction(2, 100),
    Fraction(-4, 100),
    Fraction(1, 100),
    Fraction(5, 100),
)
_EXPOSURES: Final = (ONE, ONE, ZERO, ONE, ZERO, ZERO)
_PREDICTIONS: Final = tuple(Fraction(value, 10) for value in (4, 1, 6, 2, 5, 3))

_COST_RATE: Final = cost_rate_from_bps(per_side_cost_bps(ZERO))


def _pnl(exposures: Sequence[Fraction], labels: Sequence[Fraction]) -> Fraction:
    return sum(
        (a * b for a, b in zip(exposures, labels, strict=True)),
        ZERO,
    )


def _turnover(exposures: Sequence[Fraction]) -> Fraction:
    total = ZERO
    previous = ZERO
    for exposure in exposures:
        total += abs(exposure - previous)
        previous = exposure
    return total


def _permutation_pnls(
    exposures: Sequence[Fraction], labels: Sequence[Fraction]
) -> list[Fraction]:
    return [_pnl(exposures, shuffled) for shuffled in permutations(labels)]


def test_the_null_inputs_are_the_intended_exact_objects() -> None:
    assert sum(_ZERO_SUM_LABELS, ZERO) == ZERO
    assert sum(_DRIFTING_LABELS, ZERO) != ZERO
    assert len(_EXPOSURES) == len(_ZERO_SUM_LABELS) == len(_DRIFTING_LABELS)
    assert len(set(_PREDICTIONS)) == len(_PREDICTIONS)
    require_admissible(_START, repeat_daily(_EXPOSURES))


def test_the_exhaustive_shuffled_label_null_is_exactly_zero() -> None:
    values = _permutation_pnls(_EXPOSURES, _ZERO_SUM_LABELS)
    assert len(values) == factorial(len(_ZERO_SUM_LABELS))
    assert sum(values, ZERO) == ZERO
    assert sum(values, ZERO) / len(values) == ZERO


def test_the_exhaustive_null_mean_follows_the_structural_identity() -> None:
    for labels in (_ZERO_SUM_LABELS, _DRIFTING_LABELS):
        values = _permutation_pnls(_EXPOSURES, labels)
        size = len(labels)
        expected = sum(_EXPOSURES, ZERO) * sum(labels, ZERO) / size
        assert sum(values, ZERO) / len(values) == expected


def test_the_shuffled_label_null_is_not_degenerate() -> None:
    values = _permutation_pnls(_EXPOSURES, _ZERO_SUM_LABELS)
    assert max(values) > ZERO
    assert min(values) < ZERO
    assert len(set(values)) > 1
    assert _pnl(_EXPOSURES, _ZERO_SUM_LABELS) in values


def test_the_linear_null_is_mirrored_by_label_negation() -> None:
    negated = tuple(-value for value in _ZERO_SUM_LABELS)
    forward = sorted(_permutation_pnls(_EXPOSURES, _ZERO_SUM_LABELS))
    mirrored = sorted(-value for value in _permutation_pnls(_EXPOSURES, negated))
    assert forward == mirrored


def test_costs_shift_the_null_by_an_exactly_known_amount() -> None:
    charged = _COST_RATE * _turnover(_EXPOSURES)
    values = _permutation_pnls(_EXPOSURES, _ZERO_SUM_LABELS)
    net = [value - charged for value in values]
    assert charged > ZERO
    assert sum(net, ZERO) / len(net) == -charged
    assert sum(values, ZERO) / len(values) == ZERO


def test_the_exhaustive_spearman_null_is_exactly_zero() -> None:
    for size in (4, 5, 6):
        predictions = _PREDICTIONS[:size]
        labels = _DRIFTING_LABELS[:size]
        values = [
            spearman_rho(predictions, shuffled) for shuffled in permutations(labels)
        ]
        assert len(values) == factorial(size)
        assert sum(values, ZERO) == ZERO
        assert sum(values, ZERO) / len(values) == ZERO
        assert max(values) == ONE
        assert min(values) == -ONE


def test_spearman_is_transcribed_exactly() -> None:
    assert spearman_rho(_PREDICTIONS, _PREDICTIONS) == ONE
    inverse_ranks = tuple(-value for value in _PREDICTIONS)
    assert spearman_rho(_PREDICTIONS, inverse_ranks) == -ONE
    one_swap = spearman_rho((ZERO, ONE, Fraction(2)), (ZERO, Fraction(2), ONE))
    assert one_swap == Fraction(1, 2)
    try:
        spearman_rho((ZERO, ZERO, ONE), (ZERO, ONE, Fraction(2)))
    except OracleError:
        pass
    else:
        raise AssertionError("tied values must be rejected, not silently ranked")


def _null_record() -> dict[str, str]:
    record: dict[str, str] = {}
    for name, labels in (
        ("zero_sum", _ZERO_SUM_LABELS),
        ("drifting", _DRIFTING_LABELS),
    ):
        values = _permutation_pnls(_EXPOSURES, labels)
        record[f"{name}.count"] = str(len(values))
        record[f"{name}.mean"] = exact(sum(values, ZERO) / len(values))
        record[f"{name}.max"] = exact(max(values))
        record[f"{name}.min"] = exact(min(values))
        record[f"{name}.observed"] = exact(_pnl(_EXPOSURES, labels))
    spearman = [
        spearman_rho(_PREDICTIONS, shuffled)
        for shuffled in permutations(_DRIFTING_LABELS)
    ]
    record["spearman.count"] = str(len(spearman))
    record["spearman.mean"] = exact(sum(spearman, ZERO) / len(spearman))
    return record


def test_the_null_record_is_byte_identical_across_reruns() -> None:
    first = canonical_record_bytes(_null_record())
    second = canonical_record_bytes(_null_record())
    assert first == second
    assert record_digest(first) == record_digest(second)


def test_the_null_record_states_the_exact_centre() -> None:
    record = _null_record()
    assert record["zero_sum.mean"] == exact(ZERO)
    assert record["spearman.mean"] == exact(ZERO)
    assert Fraction(record["drifting.mean"]) != ZERO
    assert int(record["zero_sum.count"]) == factorial(len(_ZERO_SUM_LABELS))
