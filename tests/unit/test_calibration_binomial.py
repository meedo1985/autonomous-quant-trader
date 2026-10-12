"""D-19 exact binomial targets (prereg §5, §6, §13 rev 7g item 3): the
values the preregistration states, checked independently by both reviewers
and by the drafter, are reproduced."""

from __future__ import annotations

import math
from fractions import Fraction

import pytest

from calibration import binomial

BOUNDS = {"error": 0.025, "dsr": 0.0035, "u_g": 0.0015}


@pytest.mark.parametrize(
    ("m", "error_critical", "error_tau"), [(322, 418, 0.01796), (340, 417, 0.01791)]
)
def test_the_section_13_targets_are_reproduced(
    m: int, error_critical: int, error_tau: float
) -> None:
    at_20k = binomial.targets(m, BOUNDS, 20_000)
    assert at_20k["error"]["critical"] == error_critical
    assert round(at_20k["error"]["tau"], 5) == error_tau
    assert at_20k["dsr"]["critical"] == 40
    assert round(at_20k["dsr"]["tau"], 5) == 0.00120
    assert at_20k["u_g"]["critical"] == 11
    assert round(at_20k["u_g"]["tau"], 6) == 0.000202
    at_40k = binomial.targets(m, {"u_g": 0.0015}, 40_000)["u_g"]
    assert (at_40k["critical"], round(at_40k["tau"], 6)) == (32, 0.000451)


def test_the_development_upper_bounds_of_section_13_are_reproduced() -> None:
    """90% UCB of U_G at 12,000: 1.92e-4, 3.24e-4, 4.43e-4 at 0, 1, 2."""
    got = [round(binomial.upper(x, 12_000, 0.90), 6) for x in (0, 1, 2)]
    assert got == [0.000192, 0.000324, 0.000443]
    assert binomial.upper(0, 12_000, 0.90) == pytest.approx(1 - 0.1 ** (1 / 12_000))


def test_the_cdf_equals_exact_rational_arithmetic() -> None:
    n, p = 40, Fraction(3, 100)
    for c in (0, 1, 5, 39, 40):
        exact = sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(c + 1))
        assert binomial.cdf(c, n, 0.03) == pytest.approx(float(exact), rel=1e-12)


def test_edges() -> None:
    assert binomial.upper(5, 5, 0.9) == 1.0
    assert binomial.critical(10, 1e-9, 0.01) == -1
    assert binomial.tau(10, -1) == 0.0
    with pytest.raises(ValueError):
        binomial.upper(6, 5, 0.9)
