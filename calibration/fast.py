"""Accelerated **bit-identical** implementations of the exact reference.

Every value equals the pure-Python reference exactly, so no computational-
equivalence rule is needed:
- sums use `math.fsum`, whose correctly rounded result does not depend on
  order, over NumPy-gathered values (`.tolist()`);
- element-wise `+ - * /` in NumPy are the same IEEE operations as in Python;
- `x ** 2` in the reference is Python's float power, so `_squares` applies
  that same operation to each value. NumPy's `power` is not used: with
  AVX-512 dispatch it differs from `**` in about 27 of 1,000 values, and
  `x * x` differs from `**` as well (FD-1, CRD-1). `self_check` compares
  `mean_var` with the pure-Python reference and refuses on any difference.

Index generation stays the production loop: a vectorised exact
Mersenne-Twister walk matched it draw for draw but was slower (1.20 s against
0.92 s for 2,000 replicates at T = 1247)."""

from __future__ import annotations

import math
import random

import numpy as np


def _squares(d: np.ndarray) -> list[float]:
    """Each value squared with Python's `**`, the reference's operation."""
    return [v**2 for v in d.tolist()]


def self_check() -> None:
    """`mean_var` equals the pure-Python reference on random values, or
    RuntimeError (a U_ops cause in the start gate)."""
    r = random.Random(20261004)
    for _ in range(50):
        xs = [r.uniform(-1, 1) * 10 ** r.randint(-8, 3) for _ in range(400)]
        mean = math.fsum(xs) / len(xs)
        expected = mean, math.fsum((x - mean) ** 2 for x in xs) / (len(xs) - 1)
        if mean_var(np.array(xs)) != expected:
            raise RuntimeError("fast.mean_var differs from the reference")


def mean_var(values: np.ndarray) -> tuple[float, float]:
    """Reference two-pass mean and (n-1) variance, bit-identical."""
    n = len(values)
    mean = math.fsum(values.tolist()) / n
    return mean, math.fsum(_squares(values - mean)) / (n - 1)


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
