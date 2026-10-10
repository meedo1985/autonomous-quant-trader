"""D-19 generators of engine item 2a (prereg §3.1-§3.2): skew-t +-1 (Q2),
unequal moments (Q2m) and one AR(1) column among iid columns (Q4).
Synthetic data only."""

from __future__ import annotations

import math

import numpy as np
import pytest

from calibration import generator
from calibration.generator import Cell, cells_from_manifest, generate
from calibration.seeds import outer_seed, stream


def _x(cell: Cell) -> np.ndarray:
    seed = outer_seed("0" * 64, cell.cell_id, "unit", 0)
    return generate(cell, stream(seed, "market"), stream(seed, "columns")).x


def test_alpha_s_gives_standardised_skewness_plus_and_minus_one() -> None:
    """§3.1: the frozen shape, re-derived by bisection on delta."""
    assert generator.skew_t_moments(generator.ALPHA_S)[2] == pytest.approx(1, abs=1e-12)
    assert generator.skew_t_moments(-generator.ALPHA_S)[2] == pytest.approx(
        -1, abs=1e-12
    )
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        alpha = mid / math.sqrt(1 - mid**2)
        if generator.skew_t_moments(alpha)[2] < 1:
            lo = mid
        else:
            hi = mid
    assert lo / math.sqrt(1 - lo**2) == pytest.approx(generator.ALPHA_S, rel=1e-12)


def test_the_exact_moments_match_simulation_where_skewness_is_estimable() -> None:
    """The product-moment formula, checked by simulation at nu = 30 (sample
    skewness needs a finite sixth moment, which nu = 5 lacks)."""
    rng = np.random.default_rng(7)
    n, nu, alpha = 2_000_000, 30, 3.0
    delta = alpha / math.sqrt(1 + alpha**2)
    z = delta * np.abs(rng.standard_normal(n)) + math.sqrt(1 - delta**2) * (
        rng.standard_normal(n)
    )
    x = z * np.sqrt(nu / rng.chisquare(nu, n))
    mean, var, skew = generator.skew_t_moments(alpha, nu)
    sample_skew = float(np.mean((x - x.mean()) ** 3) / x.var() ** 1.5)
    assert x.mean() == pytest.approx(mean, abs=4 * math.sqrt(var / n))
    assert x.var() == pytest.approx(var, rel=0.01)
    assert sample_skew == pytest.approx(skew, abs=0.02)


@pytest.mark.parametrize("law", ["skewt+", "skewt-"])
def test_skew_t_draws_are_standardised(law: str) -> None:
    """Mean 0 and variance 1 at nu = 5, so every column has mean exactly 0."""
    rng = np.random.default_rng(11)
    draws = generator._skew_t(rng, generator.SKEW[law], (2_000_000,))
    assert abs(float(draws.mean())) < 4 / math.sqrt(2_000_000)
    assert float(draws.var()) == pytest.approx(1, rel=0.01)
    third = float(np.mean(draws**3))
    assert (third > 0) is (law == "skewt+")


def test_unequal_moments_put_t5_and_both_scales_where_declared() -> None:
    """Q2m: columns j < ceil(K/2) are t5; c_j = 0.5 for even j, 2 for odd j."""
    x = _x(Cell("q2m", 5, 40_000, "unequal", "independent"))
    sd = x.std(axis=0)
    assert sd[1] / sd[0] == pytest.approx(4, rel=0.05)  # scale 2 vs 0.5
    assert sd[3] / sd[2] == pytest.approx(4, rel=0.05)
    kurt = ((x - x.mean(axis=0)) ** 4).mean(axis=0) / x.var(axis=0) ** 2 - 3
    assert all(kurt[:3] > 1.5) and all(abs(kurt[3:]) < 0.3)  # t5: 6 in theory


def test_mixed_ar_has_one_ar_column_among_iid_columns() -> None:
    """Q4: column 0 is AR(1) with phi = 0.5, the others are iid."""
    x = _x(Cell("q4", 5, 40_000, "mixed_ar", "independent"))
    lag1 = [float(np.corrcoef(x[1:, j], x[:-1, j])[0, 1]) for j in range(5)]
    assert lag1[0] == pytest.approx(0.5, abs=0.03)
    assert all(abs(r) < 0.03 for r in lag1[1:])


@pytest.mark.parametrize(
    ("law", "k", "dependence"),
    [("unequal", 1, "independent"), ("mixed_ar", 2, "equi0.5"),
     ("unequal", 5, "factor")],
)  # fmt: skip
def test_q2m_and_q4_need_two_independent_columns(
    law: str, k: int, dependence: str
) -> None:
    entry = {"cell_id": "c", "k": k, "t": 60, "law": law, "dependence": dependence}
    with pytest.raises(ValueError, match="needs K >= 2, independent"):
        cells_from_manifest({"cells": [entry]})


def test_the_new_laws_are_accepted_in_a_manifest() -> None:
    cells = [
        {"cell_id": f"c{i}", "k": 2, "t": 60, "law": law, "dependence": "independent"}
        for i, law in enumerate(("skewt+", "skewt-", "unequal", "mixed_ar"))
    ]
    assert len(cells_from_manifest({"cells": cells})) == 4
