"""Trend and vol rule libraries of the D-19 semi-empirical cells (Q5, QJ),
as accepted by the owner on 2026-10-11
(`review/d19-engine/ITEM2B_RULE_LIBRARY_PROPOSAL.md` revision 3, R-2..R-6;
`OWNER_DECISION_ITEM2B_RULE_LIBRARIES.md`).

Every exposure is computed on the resampled path's BTC daily returns r:
row t is the exposure held on day t, decided at the start of day t from
r_0 .. r_{t-1} only. Estimators start from `v_bar`, the population variance
of the source's BTC column (r_s^2 = v_bar for s < 0). The frozen 0.10 band
of the canonical benchmarks gates every rebalance, starting from 0.
"""

from __future__ import annotations

import numpy as np

from aqt.benchmarks.canonical import reaches_rebalance_band
from calibration.generator import SEMI_LAWS, Cell, Legs, generate
from calibration.seeds import stream
from calibration.semi import Exposures, Source, reference_variance, semi_empirical

__all__ = ["reference_variance"]  # re-exported: R-5's v_bar lives in semi

FAMILIES = ("trend", "vol")
RULES = 27
TAUS = (0.60, 0.40, 0.80)
HORIZONS = (1, 3, 7)  # days: the frozen 24 / 72 / 168 h
SMA_DAYS = (200, 100, 50)
TREND_EWMA_HALF_LIFE = 7  # EWMA_168h, the default sizing estimator
ESTIMATORS = ("EWMA", "HAR_RV", "GARCH_1_1")
EWMA_HALF_LIVES = (7, 3, 14)  # EWMA_168h, EWMA_72h, EWMA_336h
EWMA_NAMES = ("EWMA_168h", "EWMA_72h", "EWMA_336h")
GARCH_ALPHA, GARCH_BETA = 0.10, 0.85
HAR_BETAS = (0.35, 0.35, 0.20)  # daily, weekly (5), monthly (22)
HAR_C = 0.10  # times v_bar
HAR_LAGS = 22
WARMUP = 250  # R-5


def index(i: int) -> tuple[int, int, int]:
    """R-4: rule i -> (model point, second index, tau index); one-to-one."""
    if not 0 <= i < RULES:
        raise ValueError(f"rule index {i} outside 0..{RULES - 1}")
    a, b, c = i % 3, (i // 3) % 3, i // 9
    return a, (a + b) % 3, (a + 2 * b + c) % 3


def trial(family: str, i: int) -> tuple[str, tuple[object, ...], int]:
    """The frozen trial unit (hypothesis, parameter point, horizon hours)."""
    m, s, k = index(i)
    tau = TAUS[k]
    if family == "trend":
        return "trend", (f"SMA_{SMA_DAYS[m]}", tau), 24 * HORIZONS[s]
    if family != "vol":
        raise ValueError(f"unknown family {family!r}")
    if m == 0:
        return "vol", (EWMA_NAMES[s], tau), 24
    return "vol", (ESTIMATORS[m], tau), 24 * HORIZONS[s]


def _size(v: np.ndarray, tau: float) -> np.ndarray:
    """min(1, tau / sqrt(365 v)), 1 where v == 0."""
    with np.errstate(divide="ignore"):
        return np.where(v > 0, np.minimum(1.0, tau / np.sqrt(365 * v)), 1.0)


def _lagged_squares(r: np.ndarray, v_bar: float, lags: int) -> np.ndarray:
    """L[t, j] = r_{t-1-j}^2, with v_bar for indices < 0."""
    sq = np.concatenate([np.full(lags, v_bar), r**2])
    n = len(r)
    return np.stack([sq[lags - 1 - j : lags - 1 - j + n] for j in range(lags)], 1)


def ewma_variance(r: np.ndarray, v_bar: float, half_life: int) -> np.ndarray:
    """v_0 = v_bar, v_t = lam v_{t-1} + (1 - lam) r_{t-1}^2."""
    lam = 0.5 ** (1 / half_life)
    v = np.empty(len(r))
    v[0] = v_bar
    for t in range(1, len(r)):
        v[t] = lam * v[t - 1] + (1 - lam) * r[t - 1] ** 2
    return v


def garch_variance(r: np.ndarray, v_bar: float, h: int) -> np.ndarray:
    """g_0 = v_bar, g_t = omega + alpha r_{t-1}^2 + beta g_{t-1}; the H-day
    forecast is v_bar + (g_t - v_bar) mean_{h<H} (alpha + beta)^h."""
    omega = (1 - GARCH_ALPHA - GARCH_BETA) * v_bar
    g = np.empty(len(r))
    g[0] = v_bar
    for t in range(1, len(r)):
        g[t] = omega + GARCH_ALPHA * r[t - 1] ** 2 + GARCH_BETA * g[t - 1]
    decay = np.mean([(GARCH_ALPHA + GARCH_BETA) ** k for k in range(h)])
    return v_bar + (g - v_bar) * decay


def har_variance(r: np.ndarray, v_bar: float, h: int) -> np.ndarray:
    """f_t = c + b_d RV_{t-1} + b_w mean RV_{t-5..t-1} + b_m mean
    RV_{t-22..t-1}, iterated forward with forecasts in place of unobserved
    RV and averaged over the H days."""
    lags = _lagged_squares(r, v_bar, HAR_LAGS)
    b_d, b_w, b_m = HAR_BETAS
    total = np.zeros(len(r))
    for _ in range(h):
        f = (
            HAR_C * v_bar
            + b_d * lags[:, 0]
            + b_w * lags[:, :5].mean(axis=1)
            + b_m * lags.mean(axis=1)
        )
        total += f
        lags = np.concatenate([f[:, None], lags[:, :-1]], axis=1)
    return total / h


def trend_targets(r: np.ndarray, v_bar: float, i: int) -> np.ndarray:
    """1[P_{t-1} > mean P_{t-L..t-1}] x size, read on days t = 0 mod H and
    held between; 0 until L prices exist."""
    m, s, k = index(i)
    days, h = SMA_DAYS[m], HORIZONS[s]
    with np.errstate(over="ignore"):  # checked on the next line
        price = np.cumprod(1 + r)
    if not np.all(np.isfinite(price)):
        raise ValueError("non-finite price index")
    size = _size(ewma_variance(r, v_bar, TREND_EWMA_HALF_LIFE), TAUS[k])
    csum = np.concatenate([[0.0], np.cumsum(price)])
    out = np.zeros(len(r))
    for t in range(len(r)):
        if t % h:
            out[t] = out[t - 1]
        elif t >= days:
            sma = (csum[t] - csum[t - days]) / days
            out[t] = size[t] if price[t - 1] > sma else 0.0
    return out


def vol_targets(r: np.ndarray, v_bar: float, i: int) -> np.ndarray:
    m, s, k = index(i)
    if m == 0:
        v = ewma_variance(r, v_bar, EWMA_HALF_LIVES[s])
    elif m == 1:
        v = har_variance(r, v_bar, HORIZONS[s])
    else:
        v = garch_variance(r, v_bar, HORIZONS[s])
    return _size(v, TAUS[k])


def held(targets: np.ndarray) -> np.ndarray:
    """The frozen band: move fully to the target when the change reaches
    0.10, else keep the held exposure; the state before day 0 is 0."""
    out = np.empty(len(targets))
    current = 0.0
    for t, target in enumerate(targets):
        if reaches_rebalance_band(float(target) - current):
            current = float(target)
        out[t] = current
    return out


def library(family: str, k: int, v_bar: float) -> Exposures:
    """The fixed first-K rules of a family (R-4), as an `Exposures`."""
    if family not in FAMILIES or not 1 <= k <= RULES:
        raise ValueError(f"no library {family!r} with K = {k}")
    targets = trend_targets if family == "trend" else vol_targets

    def exposures(path: np.ndarray) -> np.ndarray:
        r = np.asarray(path, dtype=float)[:, 0]
        return np.column_stack([held(targets(r, v_bar, i)) for i in range(k)])

    return exposures


def joint(k: int, v_bar: float) -> Exposures:
    """QJ (R-6): the first K trend rules, then the first K vol rules, on one
    path; `semi_empirical` gives them one shared set of block signs."""
    trend, vol = library("trend", k, v_bar), library("vol", k, v_bar)
    return lambda path: np.hstack([trend(path), vol(path)])


def family_label(cell: Cell) -> str:
    """The §8 family id: the family of a Q5 cell, else "agnostic". A QJ cell
    has two; see `families`."""
    if cell.law == "semi-joint":
        raise ValueError(f"{cell.cell_id}: a QJ cell has one label per family")
    return cell.law.removeprefix("semi-") if cell.law in SEMI_LAWS else "agnostic"


def families(cell: Cell, legs: Legs) -> dict[str, Legs]:
    """Per §8 family label, that family's legs: one entry, except for QJ,
    whose first K columns are the trend rules and the next K the vol rules,
    on the one shared path, benchmark and signs (R-6)."""
    if cell.law != "semi-joint":
        return {family_label(cell): legs}
    k = cell.k
    return {
        family: Legs(legs.x[:, cols], legs.benchmark, legs.candidates[:, cols])
        for family, cols in (("trend", slice(0, k)), ("vol", slice(k, 2 * k)))
    }


def draw(cell: Cell, seed: str, source: Source | None) -> Legs:
    """One replication's legs from outer seed `seed` (§8 streams): a Q5
    cell from the exploration source ("market" path, "sign" flips), any
    other cell from the synthetic generator ("market", "columns")."""
    if cell.law not in SEMI_LAWS:
        return generate(cell, stream(seed, "market"), stream(seed, "columns"))
    if source is None:
        raise ValueError(f"{cell.cell_id}: a Q5 cell needs the exploration source")
    exposures = (
        joint(cell.k, source.v_bar)
        if cell.law == "semi-joint"
        else library(family_label(cell), cell.k, source.v_bar)
    )
    return semi_empirical(source.returns, exposures, stream(seed, "market"),
                          stream(seed, "sign"), cell.t, WARMUP)  # fmt: skip
