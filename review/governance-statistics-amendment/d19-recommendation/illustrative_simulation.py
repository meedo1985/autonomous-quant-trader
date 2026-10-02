"""Illustrative DSR simulation shown to the owner on 2026-10-02 (D-19).

Made-up data only: independent strategies, normal daily returns. It shows
the idea of deflation; it is not a calibration and closes nothing (see
RECOMMENDATION.md R19-7). Run: python -B illustrative_simulation.py
"""

# ruff: noqa: E501

import math
import random
from statistics import NormalDist, fmean, pstdev, variance

N01 = NormalDist()
G = 0.5772156649015329
T = 1247  # about 3.4 years of daily results
ANN = math.sqrt(365)


def A(n):
    return (1 - G) * N01.inv_cdf(1 - 1 / n) + G * N01.inv_cdf(1 - 1 / (n * math.e))


def sharpe(xs):
    return fmean(xs) / pstdev(xs)


def dsr(sr, n, v):  # normal returns: skew 0, kurtosis 3
    s0 = 0.0 if n == 1 else math.sqrt(v) * A(n)
    return N01.cdf((sr - s0) * math.sqrt(T - 1) / math.sqrt(1 + sr * sr / 2))


rng = random.Random(20261002)


def strategy(true_annual):
    mu = true_annual / ANN * 0.01
    return [rng.gauss(mu, 0.01) for _ in range(T)]


srs = [sharpe(strategy(0.0)) for _ in range(81)]
best = max(srs)
v = variance(srs)
print(
    f"story1 best of 81 no-edge: annual Sharpe {best * ANN:.2f}, DSR {dsr(best, 81, v):.3f}"
)
print(f"story1 same Sharpe as if it were the only one tried: DSR {dsr(best, 1, v):.3f}")
print(f"story1 how many of 81 look >= 1.0 annual: {sum(s * ANN >= 1.0 for s in srs)}")
srs2 = [sharpe(strategy(0.0)) for _ in range(80)] + [sharpe(strategy(2.5))]
b2 = max(srs2)
v2 = variance(srs2)
print(
    f"story2 real-edge strategy: annual Sharpe {srs2[-1] * ANN:.2f}, best is real one: {b2 == srs2[-1]}, DSR {dsr(b2, 81, v2):.3f}"
)
srs3 = [sharpe(strategy(0.0)) for _ in range(80)] + [sharpe(strategy(1.2))]
b3 = max(srs3)
v3 = variance(srs3)
print(
    f"story3 modest real edge: annual Sharpe {srs3[-1] * ANN:.2f}, best is real one: {b3 == srs3[-1]}, best DSR {dsr(b3, 81, v3):.3f}"
)
passes = 0
for _ in range(300):
    s = [sharpe(strategy(0.0)) for _ in range(81)]
    passes += dsr(max(s), 81, variance(s)) >= 0.95
print(f"no-edge best-of-81 passing 0.95: {passes}/300")
