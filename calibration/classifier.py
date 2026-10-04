"""Diagnostic vector of the supported-law classifier (prereg rev 6 §3.5)."""

from __future__ import annotations

import numpy as np


def diagnostics(x: np.ndarray, lengths: list[float]) -> dict[str, float]:
    """Every component, one value each; non-finite means refusal."""
    t, k = x.shape
    c = x - x.mean(axis=0)
    m2 = (c**2).mean(axis=0)
    g1 = (c**3).mean(axis=0) / m2**1.5
    g2 = (c**4).mean(axis=0) / m2**2 - 3
    out = {
        "K": float(k),
        "T": float(t),
        "max_length_ratio": max(lengths) / t,
        "max_excess_kurtosis": float(g2.max()),
        "min_skewness": float(g1.min()),
        "max_skewness": float(g1.max()),
        "max_gph_d": float(_gph(c).max()),
        "max_cusum_squares": float(_cusum(x).max()),
        "max_zero_share": float((x == 0).mean(axis=0).max()),
    }
    if k >= 2:
        r = np.corrcoef(x.T)[np.triu_indices(k, 1)]
        out["min_correlation"], out["max_correlation"] = float(r.min()), float(r.max())
    return out


def _gph(c: np.ndarray) -> np.ndarray:
    """GPH log-periodogram d per column, bandwidth floor(T^0.5)."""
    t = c.shape[0]
    m = int(np.floor(t**0.5))
    j = np.arange(1, m + 1)
    lam = 2 * np.pi * j / t
    periodogram = np.abs(np.fft.rfft(c, axis=0)[1 : m + 1]) ** 2 / (2 * np.pi * t)
    regressor = -2 * np.log(2 * np.sin(lam / 2))
    xr = regressor - regressor.mean()
    y = np.log(periodogram)
    return np.asarray((xr @ (y - y.mean(axis=0))) / (xr @ xr), dtype=float)


def _cusum(x: np.ndarray) -> np.ndarray:
    """max_k |sum_{t<=k} x_t^2 / sum x_t^2 - k/T| per column."""
    t = x.shape[0]
    sq = x**2
    path = np.cumsum(sq, axis=0) / sq.sum(axis=0)
    return np.asarray(np.abs(path - (np.arange(1, t + 1) / t)[:, None]).max(axis=0))


def within(
    values: dict[str, float], upper: dict[str, float], lower: dict[str, float]
) -> bool:
    """Accept iff every component is finite and inside its thresholds."""
    for name, v in values.items():
        if not np.isfinite(v):
            return False
        if name in upper and v > upper[name]:
            return False
        if name in lower and v < lower[name]:
            return False
    return True
