"""Exact binomial targets of prereg §5 and §6 (§13 rev 7g item 3): the
Clopper-Pearson upper bound, the held-out critical count and the
development target tau. Standard library only, deterministic.

- `upper(x, n, confidence)`: one-sided Clopper-Pearson upper bound, the p
  at which P(X <= x | n, p) = 1 - confidence.
- `critical(n, bound, alpha)`: the largest event count whose held-out bound
  at level 1 - alpha is within `bound` (prereg §6), or -1 if none is.
- `tau(n, c)`: the largest true rate whose held-out pass probability
  P(X <= c) is at least 0.999 (prereg §5)."""

from __future__ import annotations

import math

PASS_PROBABILITY = 0.999  # prereg §5
DEVELOPMENT_CONFIDENCE = 0.90  # prereg §5, §13 item 3: 90% UCB
FAMILY_ALPHA = 0.025  # prereg §6: alpha = 0.025 / M per attempt
_ITERATIONS = 200  # bisection on [0, 1]: far below one ulp of any result


def cdf(c: int, n: int, p: float) -> float:
    """P(X <= c) for X ~ Binomial(n, p), summed in log space with fsum."""
    if c < 0:
        return 0.0
    if c >= n or p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    log_p, log_q = math.log(p), math.log1p(-p)
    base = math.lgamma(n + 1)
    return min(
        1.0,
        math.fsum(
            math.exp(
                base - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                + i * log_p + (n - i) * log_q
            )
            for i in range(c + 1)
        ),
    )  # fmt: skip


def _solve(c: int, n: int, target: float) -> float:
    """The largest p with cdf(c, n, p) >= target (cdf falls as p rises)."""
    lo, hi = 0.0, 1.0
    for _ in range(_ITERATIONS):
        mid = (lo + hi) / 2
        if mid in (lo, hi):
            break
        if cdf(c, n, mid) >= target:
            lo = mid
        else:
            hi = mid
    return lo


def upper(x: int, n: int, confidence: float) -> float:
    """One-sided Clopper-Pearson upper bound for x events in n."""
    if not 0 <= x <= n or n < 1:
        raise ValueError("need 0 <= x <= n and n >= 1")
    return 1.0 if x == n else _solve(x, n, 1 - confidence)


def critical(n: int, bound: float, alpha: float) -> int:
    """The largest x with upper(x, n, 1 - alpha) <= bound, or -1."""
    if upper(0, n, 1 - alpha) > bound:
        return -1
    lo, hi = 0, n  # upper() rises with x: binary search
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if upper(mid, n, 1 - alpha) <= bound:
            lo = mid
        else:
            hi = mid - 1
    return lo


def tau(n: int, c: int) -> float:
    """The largest true rate passing with probability >= PASS_PROBABILITY."""
    if c < 0:
        return 0.0
    return _solve(c, n, PASS_PROBABILITY)


def targets(m: int, bounds: dict[str, float], n: int) -> dict[str, dict[str, float]]:
    """Critical count and tau per test kind at `M = m` tests and `N = n`."""
    alpha = FAMILY_ALPHA / m
    out = {}
    for name, bound in sorted(bounds.items()):
        c = critical(n, bound, alpha)
        out[name] = {"bound": bound, "n": n, "critical": c, "tau": tau(n, c)}
    return out
