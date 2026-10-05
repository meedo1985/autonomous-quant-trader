"""Supported-law classifier (prereg rev 6 §3.5, as overridden by §13 rev 7g item 4).

L_j/T is dropped. The stochastic tails are exactly the eight in `UPPER` and
`LOWER` (six at K = 1); K and T are exact checks, constant across a cell's
draws (`fit_thresholds` checks it)."""

from __future__ import annotations

import numpy as np

UPPER = (
    "max_excess_kurtosis",
    "max_skewness",
    "max_gph_d",
    "max_cusum_squares",
    "max_zero_share",
    "max_correlation",
)
LOWER = ("min_skewness", "min_correlation")


def diagnostics(x: np.ndarray) -> dict[str, float]:
    """Every component, one value each; non-finite means refusal."""
    t, k = x.shape
    c = x - x.mean(axis=0)
    m2 = (c**2).mean(axis=0)
    g1 = (c**3).mean(axis=0) / m2**1.5
    g2 = (c**4).mean(axis=0) / m2**2 - 3
    out = {
        "K": float(k),
        "T": float(t),
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


def required(k: int) -> frozenset[str]:
    """The exact field set for `K = k`: K, T and the eight tails (six at K = 1)."""
    names = {"K", "T", *UPPER, *LOWER}
    if k < 2:
        names -= {"min_correlation", "max_correlation"}
    return frozenset(names)


def _thresholds_complete(upper: dict[str, float], lower: dict[str, float]) -> None:
    """Refuse an incomplete or non-finite threshold set (D19CR-1): an engine
    fault, never a silent pass."""
    if "K" not in upper:
        raise ValueError("threshold set has no K")
    need = required(int(upper["K"]))
    if set(upper) != need - set(LOWER) or set(lower) != need - set(UPPER):
        raise ValueError("threshold set does not have exactly the required fields")
    if not all(np.isfinite(v) for v in (*upper.values(), *lower.values())):
        raise ValueError("threshold set has a non-finite bound")


def within(
    values: dict[str, float], upper: dict[str, float], lower: dict[str, float]
) -> bool:
    """Accept iff every component is finite and inside its thresholds (ties
    accepted). A non-finite diagnostic or another K or T is a refusal; an
    incomplete diagnostic or threshold set is an error (D19CR-1)."""
    _thresholds_complete(upper, lower)
    if "K" not in values or "T" not in values:
        raise ValueError("diagnostics have no K or T")
    if set(values) != required(int(values["K"])):
        raise ValueError("diagnostics do not have exactly the required fields")
    if not all(np.isfinite(v) for v in values.values()):
        return False
    if values["K"] != upper["K"] or values["T"] != upper["T"]:
        return False
    return all(values[n] <= v for n, v in upper.items()) and all(
        values[n] >= v for n, v in lower.items()
    )


def ranks(n: int) -> tuple[int, int]:
    """1-based order-statistic ranks (upper, lower) in integer arithmetic:
    n - q and q + 1, q = floor(n / 100000); 299,997 and 4 at n = 300,000."""
    q = n // 100000
    return n - q, q + 1


def fit_thresholds(
    draws: list[dict[str, float]],
) -> tuple[dict[str, float], dict[str, float]]:
    """Per-cell (upper, lower) thresholds from the threshold run's draws.
    K and T get upper = lower = their constant value (an exact check).
    Every draw must have exactly the required fields, the cell's K and T, and
    finite values: a non-finite draw stops the fit, because its treatment is
    not settled by the accepted method (D19CR-1)."""
    if not draws:
        raise ValueError("no threshold draws")
    k, t = draws[0].get("K"), draws[0].get("T")
    if k is None or t is None:
        raise ValueError("threshold draw has no K or T")
    need = required(int(k))
    for d in draws:
        if set(d) != need or (d["K"], d["T"]) != (k, t):
            raise ValueError("threshold draws differ in fields, K or T")
        if not all(np.isfinite(v) for v in d.values()):
            raise ValueError("non-finite diagnostic in a threshold draw")
    up, lo = ranks(len(draws))
    upper: dict[str, float] = {}
    lower: dict[str, float] = {}
    for name in sorted(need):
        v = np.sort([d[name] for d in draws])
        if name in UPPER or name in ("K", "T"):
            upper[name] = float(v[up - 1])
        if name in LOWER or name in ("K", "T"):
            lower[name] = float(v[lo - 1])
    return upper, lower
