"""Accelerated **bit-identical** implementations of the exact reference.

Every value equals the pure-Python reference exactly, so no computational-
equivalence rule is needed:
- sums use `math.fsum`, whose correctly rounded result does not depend on
  order, over NumPy-gathered values (`.tolist()`);
- element-wise `+ - * /` in NumPy are the same IEEE operations as in Python;
- `x ** 2` in the reference calls C `pow`; NumPy's `power` with an *array*
  exponent calls the same `pow` (its scalar-2 path is `x * x`, which differs
  in about 5 in 10,000 cases on this platform), so `_square` uses the array
  form, and `self_check` refuses to run if that ever stops holding.

Index generation stays the production loop: a vectorised exact
Mersenne-Twister walk matched it draw for draw but was slower (1.20 s against
0.92 s for 2,000 replicates at T = 1247)."""

from __future__ import annotations

import math
import random

import numpy as np


def _square(d: np.ndarray) -> np.ndarray:
    return np.asarray(np.power(d, np.full_like(d, 2.0)))


def self_check() -> None:
    """The `pow` identity this module relies on, on random values."""
    r = random.Random(20261004)
    xs = [r.uniform(-1, 1) * 10 ** r.randint(-8, 3) for _ in range(20000)]
    if _square(np.array(xs)).tolist() != [x**2 for x in xs]:
        raise RuntimeError("NumPy power no longer matches Python ** on this runtime")


def mean_var(values: np.ndarray) -> tuple[float, float]:
    """Reference two-pass mean and (n-1) variance, bit-identical."""
    n = len(values)
    mean = math.fsum(values.tolist()) / n
    return mean, math.fsum(_square(values - mean).tolist()) / (n - 1)


def sharpes(gathered: np.ndarray) -> np.ndarray | None:
    """Sharpe of every column of a gathered T x K replicate; None if a column
    has zero or non-finite variance (INVALID_REPLICATE)."""
    k = gathered.shape[1]
    out = np.empty(k)
    for j in range(k):
        mean, var = mean_var(gathered[:, j])
        if var == 0 or not math.isfinite(var):
            return None
        out[j] = mean / math.sqrt(var)
    return out


def block_length(values: np.ndarray) -> tuple[float | None, bool]:
    """Production `aqt.metrics.statistics.block_length`, bit-identical value
    and UPPER-clipping flag (None on any production failure reason)."""
    n = len(values)
    if n < 16:
        return None, False
    window = max(5, math.floor(math.log10(n)))
    maximum_lag = min(n - 1, math.ceil(math.sqrt(n)) + window)
    critical = 2 * math.sqrt(math.log10(n) / n)
    maximum = min(n, math.ceil(min(3 * math.sqrt(n), n / 3)))
    if (values == values[0]).all():
        return 1.0, False
    mean = math.fsum(values.tolist()) / n
    if not math.isfinite(mean):
        return None, False
    c = values - mean
    if not np.isfinite(c).all():
        return None, False
    gammas = [
        math.fsum((c[k:] * c[: n - k]).tolist()) / n for k in range(maximum_lag + 1)
    ]
    if any(not math.isfinite(g) for g in gammas):
        return None, False
    if gammas[0] == 0:
        return None, False  # production NONFINITE_RESULT (values not constant)
    correlations = [g / gammas[0] for g in gammas]
    cutoff = next(
        (
            k
            for k in range(1, maximum_lag - window + 2)
            if all(abs(correlations[j]) < critical for j in range(k, k + window))
        ),
        None,
    )
    bandwidth = maximum_lag if cutoff is None else min(2 * cutoff, maximum_lag)
    weights = [
        1.0 if k / bandwidth <= 0.5 else 2 * (1 - k / bandwidth)
        for k in range(1, bandwidth + 1)
    ]
    variance = gammas[0] + 2 * math.fsum(
        weight * gammas[k] for k, weight in enumerate(weights, 1)
    )
    capital_g = 2 * math.fsum(
        weight * k * gammas[k] for k, weight in enumerate(weights, 1)
    )
    if not (math.isfinite(variance) and math.isfinite(capital_g)) or variance <= 0:
        return None, False
    denominator = variance**2
    if denominator == 0 or not math.isfinite(denominator):
        return None, False
    raw = (capital_g**2 * n / denominator) ** (1 / 3)
    if not math.isfinite(raw):
        return None, False
    return min(float(maximum), max(1.0, raw)), raw > maximum


def column_lengths(x: np.ndarray) -> list[tuple[float | None, bool]]:
    """Annex B §2.2 L_j = max(L(u_j), L(psi_j)), bit-identical to the
    reference `_column_lengths`."""
    out: list[tuple[float | None, bool]] = []
    for j in range(x.shape[1]):
        col = x[:, j]
        mean, var = mean_var(col)
        sd = math.sqrt(var)
        s = mean / sd
        u = (col - mean) / sd
        psi = u - (s / 2) * (u * u - 1)
        (a, ca), (b, cb) = block_length(u), block_length(psi)
        out.append((None, False) if a is None or b is None else (max(a, b), ca or cb))
    return out
