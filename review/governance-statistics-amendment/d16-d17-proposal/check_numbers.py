# ruff: noqa: E501 - printed lines quote the packet values side by side
"""Independent recheck of the D-16/D-17 proposal packet's numbers (b18c02c).
Exact values by numerical integration; key claims also by simulation."""

import math
from statistics import NormalDist

import numpy as np

N01 = NormalDist()
GAMMA = 0.5772156649015329


def A(n):
    return (1 - GAMMA) * N01.inv_cdf(1 - 1 / n) + GAMMA * N01.inv_cdf(
        1 - 1 / (n * math.e)
    )


# vectorised normal cdf without scipy; E[max of n iid N(0,1)] below is
# the integral of x n phi(x) Phi(x)^(n-1) dx
def ncdf(x):
    return 0.5 * (1 + np.array([math.erf(v / math.sqrt(2)) for v in x]))


X = np.linspace(-12, 12, 200001)
PHI = np.exp(-X * X / 2) / math.sqrt(2 * math.pi)
CDF = ncdf(X)


def EM(n):
    return np.trapezoid(X * n * PHI * CDF ** (n - 1), X)


def c4(n):
    return math.sqrt(2 / (n - 1)) * math.exp(
        math.lgamma(n / 2) - math.lgamma((n - 1) / 2)
    )


print("== closed-form sanity: E[M2]=1/sqrt(pi), E[M3]=3/(2 sqrt(pi))")
print(f"E[M2] {EM(2):.12f} vs {1 / math.sqrt(math.pi):.12f}")
print(f"E[M3] {EM(3):.12f} vs {3 / (2 * math.sqrt(math.pi)):.12f}")

print(
    "\n== Lemma 1 ratio c4(N)A(N)/E[M_N]  (packet: .735 .893 .964 .995 .9989 1.0002 1.0045 1.006 1.0068 1.0061)"
)
for n in (2, 3, 5, 10, 12, 13, 20, 27, 81, 162):
    print(f"N={n:4d} ratio={c4(n) * A(n) / EM(n):.4f}")

print(
    "\n== A(N) strictly increasing 2..2000:",
    all(A(n + 1) > A(n) for n in range(2, 2000)),
)
print(
    "smallest N with ratio >= 1:",
    next(n for n in range(2, 100) if c4(n) * A(n) / EM(n) >= 1),
)

print("\n== small-N guard E[M_N]/c4(N) (packet: .7071 .9549 1.2372 1.5820 1.6666)")
for n in (2, 3, 5, 10, 12):
    print(f"N={n:3d} {EM(n) / c4(n):.4f}  A(N)={A(n):.4f}")

print("\n== simulation of Lemma 1 (ratio does not depend on rho, any sign)")
rng = np.random.default_rng(20261002)
for n, rho in ((5, 0.0), (5, 0.6), (5, -0.2), (13, 0.5), (13, -0.07), (81, 0.3)):
    reps = 200_000
    # equicorrelated N(0,1) with correlation rho, valid for rho >= -1/(n-1)
    e = rng.standard_normal((reps, n))
    w = rng.standard_normal((reps, 1))
    b = math.sqrt(max(0.0, (1 + (n - 1) * rho) / n))
    x = math.sqrt(1 - rho) * (e - e.mean(axis=1, keepdims=True)) + b * w
    emax = x.max(axis=1).mean()
    esq = x.std(axis=1, ddof=1).mean()
    print(
        f"N={n:3d} rho={rho:+.2f} simulated ratio={esq * A(n) / emax:.4f}  exact={c4(n) * A(n) / EM(n):.4f}"
    )

print("\n== sign flip (N=2): E[max]=sigma*sqrt((1-rho)/pi) (packet: .178 and .778)")
for rho in (0.9, -0.9):
    z = rng.standard_normal((1_000_000, 2))
    x1 = z[:, 0]
    x2 = rho * z[:, 0] + math.sqrt(1 - rho * rho) * z[:, 1]
    print(
        f"rho={rho:+.1f} exact={math.sqrt((1 - rho) / math.pi):.4f} simulated={np.maximum(x1, x2).mean():.4f}"
    )

print(
    "\n== three 'effective N' readings of one matrix (N=3, rho=1/2): packet 2, 2.5, 2.381"
)
lam = np.linalg.eigvalsh(np.array([[1, 0.5, 0.5], [0.5, 1, 0.5], [0.5, 0.5, 1]]))
print("eigenvalues", np.round(lam, 6))
print("participation", lam.sum() ** 2 / (lam**2).sum())
print("Nyholt", 1 + 2 * (1 - lam.var(ddof=1) / 3))
p = lam / lam.sum()
print("entropy rank", math.exp(-(p * np.log(p)).sum()))

print(
    "\n== double counting example N=100 rho=0.3 using N_eff=32 (packet: 1.75 vs 2.10)"
)
s = math.sqrt(0.7)
print(
    f"E[max]={s * EM(100):.3f}  S0 with N=100: {s * c4(100) * A(100):.3f}  S0 with N_eff=32: {s * c4(100) * A(32):.3f}"
)
print(
    f"rho=0.9: E[max]={math.sqrt(0.1) * EM(100):.3f}  S0 with N_eff from same rule? packet .25 vs .79"
)

print("\n== 3 clusters x 27 identical trials (packet: E[S0]=1.788, E[max]=0.846)")
z = rng.standard_normal((400_000, 3))
vals = np.repeat(z, 27, axis=1)
print(
    f"E[max]={z.max(axis=1).mean():.3f}  E[S0]={vals.std(axis=1, ddof=1).mean() * A(81):.3f}"
)

print("\n== hurdle: annualised Sharpe needed for DSR>=0.95, T=1247, normal returns")
z95 = N01.inv_cdf(0.95)


def hurdle(n, v, T=1247):
    s0 = 0.0 if n == 1 else math.sqrt(v / (T - 1)) * A(n)
    lo, hi = 0.0, 1.0
    for _ in range(200):  # solve (S - s0) sqrt(T-1) / sqrt(1 + S^2/2) = z95
        mid = (lo + hi) / 2
        if (mid - s0) * math.sqrt(T - 1) / math.sqrt(1 + mid * mid / 2) < z95:
            lo = mid
        else:
            hi = mid
    return hi * math.sqrt(365)


print(
    "packet v=1: .89 1.35 1.74 1.99 2.22 2.35 2.43 ; v=2: .89 1.54 2.10 2.45 2.77 2.96 3.06"
)
for v in (1, 2):
    print(
        f"v={v}:", " ".join(f"{hurdle(n, v):.2f}" for n in (1, 3, 10, 27, 81, 162, 243))
    )
print(f"T=730 v=1 N=81 (packet 2.91): {hurdle(81, 1, 730):.2f}")
