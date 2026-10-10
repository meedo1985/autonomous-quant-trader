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


def test_garch_variance_is_driven_by_the_observed_return() -> None:
    """I2A-2: sigma_{t+1}^2 = omega + a (sigma_t eps_t)^2 + b sigma_t^2 with
    the same eps_t that makes r_t."""
    sigma, eps = generator.market(np.random.default_rng(3), "garch", 400)
    a, b = 0.10, 0.85
    omega = generator.SIGMA**2 * (1 - a - b)
    expected = omega + a * (sigma[:-1] * eps[:-1]) ** 2 + b * sigma[:-1] ** 2
    np.testing.assert_allclose(sigma[1:] ** 2, expected, rtol=1e-12)


def test_an_ar_market_is_ar1() -> None:
    """I2A-1: AR(1) is a law of eps too (§3.1), unit variance."""
    sigma, eps = generator.market(np.random.default_rng(5), "ar0.5", 60_000)
    assert np.all(sigma == generator.SIGMA)
    assert float(np.corrcoef(eps[1:], eps[:-1])[0, 1]) == pytest.approx(0.5, abs=0.02)
    assert float(eps.var()) == pytest.approx(1, rel=0.03)


@pytest.mark.parametrize("law", ["gaussian", "t5", "skewt+", "unequal", "mixed_ar"])
def test_iid_markets_discard_the_burn_in(law: str) -> None:
    """I2A-3: the emitted series are draws 500 onward of the market stream."""
    _, eps = generator.market(np.random.default_rng(9), law, 50)
    burned = generator._innovations(
        np.random.default_rng(9), law, (50 + generator.BURN,)
    )
    np.testing.assert_array_equal(eps, burned[generator.BURN :])


@pytest.mark.parametrize("law", ["unequal", "mixed_ar"])
def test_q2m_and_q4_markets_are_gaussian_with_constant_sigma(law: str) -> None:
    """I2A-5: interpretation 1, asserted directly."""
    sigma, eps = generator.market(np.random.default_rng(13), law, 200_000)
    assert np.all(sigma == generator.SIGMA)
    kurt = float(((eps - eps.mean()) ** 4).mean() / eps.var() ** 2 - 3)
    assert abs(kurt) < 0.05 and abs(float(eps.mean())) < 0.01


def test_q4_columns_are_mutually_independent() -> None:
    x = _x(Cell("q4", 5, 40_000, "mixed_ar", "independent"))
    corr = np.corrcoef(x.T)
    assert np.all(np.abs(corr[~np.eye(5, dtype=bool)]) < 0.03)


def test_skew_t_draw_order_is_u0_u1_w() -> None:
    """I2A-5: the draws, reproduced from a controlled generator."""
    got = generator._skew_t(np.random.default_rng(17), generator.ALPHA_S, (4,))
    rng = np.random.default_rng(17)
    u0, u1, w = rng.standard_normal(4), rng.standard_normal(4), rng.chisquare(5, 4)
    delta = generator.ALPHA_S / math.sqrt(1 + generator.ALPHA_S**2)
    x = (delta * np.abs(u0) + math.sqrt(1 - delta**2) * u1) * np.sqrt(5 / w)
    mean, var, _ = generator.skew_t_moments(generator.ALPHA_S)
    np.testing.assert_array_equal(got, (x - mean) / math.sqrt(var))


def test_alpha_s_by_independent_quadrature() -> None:
    """I2A-5: skewness of the Azzalini skew-t at alpha_s computed by
    numerical integration of the skew-normal and chi-square densities, not
    by the closed forms in skew_t_moments."""
    alpha, nu = generator.ALPHA_S, 5
    z = np.linspace(-14, 14, 400_001)
    erf = np.vectorize(math.erf)
    sn = (
        2
        * np.exp(-(z**2) / 2)
        / math.sqrt(2 * math.pi)
        * 0.5
        * (1 + erf(alpha * z / math.sqrt(2)))
    )
    w = np.linspace(1e-9, 400, 2_000_001)
    chi = w ** (nu / 2 - 1) * np.exp(-w / 2) / (2 ** (nu / 2) * math.gamma(nu / 2))
    mz = [float(np.trapezoid(sn * z**k, z)) for k in (1, 2, 3)]
    mv = [float(np.trapezoid(chi * (nu / w) ** (k / 2), w)) for k in (1, 2, 3)]
    m1, m2, m3 = (mz[i] * mv[i] for i in range(3))
    var = m2 - m1**2
    assert (m3 - 3 * m1 * m2 + 2 * m1**3) / var**1.5 == pytest.approx(1, abs=2e-4)
