"""Availability of the U_G gates (prereg rev 6 §7): G-1, G-2, G-4, G-10, G-12.

Only availability enters U_proc^R, so each function returns the reason a gate
would be UNAVAILABLE, or None. G-1 and G-12 call the production routines."""

from __future__ import annotations

import itertools

import numpy as np

from aqt.metrics import statistics as st
from calibration.seeds import sha

WINDOW = '["2022-01-01T00:00:00Z","2025-06-01T00:00:00Z"]'
SPLITS = np.array(list(itertools.combinations(range(16), 8)))  # 12,870


def g1(candidate: np.ndarray, benchmark: np.ndarray, seed: str) -> str | None:
    """Annex C C-1: the production paired-CI routine's own reason."""
    stream = st.ReplicateStream(
        sha({"seed": seed, "stream": "g1_ci"}),
        st.CONVENTION_DOCUMENT_SHA256,
        "BTCUSDT",
        "1.0",
        WINDOW,
    )
    result = st.paired_sharpe_improvement_interval(
        candidate.tolist(), benchmark.tolist(), stream=stream
    )
    return None if result.reason is None else str(result.reason)


def g2(candidate: np.ndarray, benchmark: np.ndarray) -> str | None:
    """Annex C C-2: MDD of both legs must be finite (equity above 0)."""
    for leg in (candidate, benchmark):
        equity = np.cumprod(1 + leg)
        if not np.isfinite(equity).all() or (equity <= 0).any():
            return "INVALID_SERIES"
    return None


def g4(t: int) -> str | None:
    """Annex C C-4: UNAVAILABLE only if n = 0 complete 3-month blocks; any
    T >= 365 has at least one. Integrity is input integrity (U_ops)."""
    return None if t >= 92 else "NO_COMPLETE_BLOCK"


def g10(x: np.ndarray) -> str | None:
    """Annex C C-9 availability: T >= 16 and every trial has a Sharpe on every
    IS and OOS half of all 12,870 splits. Enabled only when K >= 20."""
    t, k = x.shape
    if k < 20:
        return None  # frozen N/A
    if t < 16:
        return "INSUFFICIENT_OBSERVATIONS"
    bounds = np.array_split(np.arange(t), 16)  # remainder to earliest blocks
    s1 = np.stack([x[b].sum(axis=0) for b in bounds])
    s2 = np.stack([(x[b] ** 2).sum(axis=0) for b in bounds])
    n = np.array([len(b) for b in bounds], dtype=float)
    for halves in (SPLITS, np.array([sorted(set(range(16)) - set(s)) for s in SPLITS])):
        m = n[halves].sum(axis=1)[:, None]
        a, b = s1[halves].sum(axis=1), s2[halves].sum(axis=1)
        var = (b - a * a / m) / (m - 1)
        if (var <= 0).any() or not np.isfinite(var).all():
            return "NO_SHARPE_ON_HALF"
    return None


def g12(candidate: np.ndarray) -> str | None:
    """Annex C C-11 for every declared horizon H in {24, 72, 168} (DS2-7)."""
    values = candidate.tolist()
    for hours in (24, 72, 168):
        result = st.effective_sample_size(values, horizon_hours=hours)
        if result.reason is not None:
            return f"{result.reason}@H{hours}"
    return None


def u_g(x: np.ndarray, candidates: np.ndarray, benchmark: np.ndarray,
        nominee: int, seed: str) -> str | None:  # fmt: skip
    """The single U_G event (DS3-4): the first unavailable gate, or None."""
    cand = candidates[:, nominee]
    for reason in (
        g1(cand, benchmark, seed),
        g2(cand, benchmark),
        g4(x.shape[0]),
        g10(x),
        g12(cand),
    ):
        if reason is not None:
            return reason
    return None
