"""Availability of the U_G gates (prereg rev 6 §7): G-1, G-2, G-4, G-10, G-12.

Only availability enters U_proc^R, so each function returns the reason a gate
would be UNAVAILABLE, or None. G-1 and G-12 call the production routines."""

from __future__ import annotations

import itertools
import math

import numpy as np

import aqt.metrics.statistics as st
from calibration import fast
from calibration.seeds import sha

WINDOW = '["2022-01-01T00:00:00Z","2025-06-01T00:00:00Z"]'
SPLITS = np.array(list(itertools.combinations(range(16), 8)))  # 12,870


def g1(
    candidate: np.ndarray,
    benchmark: np.ndarray,
    seed: str,
    *,
    reference: bool = False,
    trace: list[object] | None = None,
) -> str | None:
    """Annex C C-1 availability. `reference` runs the production paired-CI
    routine; the default repeats its steps with bit-identical accelerated
    replicate Sharpes (`calibration.fast`) on the production indices."""
    stream = st.ReplicateStream(
        sha({"seed": seed, "stream": "g1_ci"}),
        st.CONVENTION_DOCUMENT_SHA256,
        "BTCUSDT",
        "1.0",
        WINDOW,
    )
    left, right = candidate.tolist(), benchmark.tolist()
    if reference:
        result = st.paired_sharpe_improvement_interval(left, right, stream=stream)
        return None if result.reason is None else str(result.reason)
    observed = st.paired_sharpe_statistics(left, right)
    influence = st.paired_sharpe_improvement_influence(left, right)
    if observed.reason or influence.reason or influence.values is None:
        return str(observed.reason or influence.reason)
    selected = st.block_length(influence.values)
    if selected.reason or selected.value is None:
        return str(selected.reason)
    if trace is not None:
        trace.append(("g1_block", selected.value))
    for i in range(st.BOOTSTRAP_ATTEMPTS):
        idx = st.bootstrap_indices(
            stream, observations=len(left), replicate_index=i, block=selected.value
        )
        scaled = []
        for leg in (candidate, benchmark):
            values = leg[list(idx)]
            if (values == values[0]).all():
                return "INVALID_REPLICATE"
            mean, var = fast.mean_var(values)
            if var == 0 or not math.isfinite(var):
                return "INVALID_REPLICATE"
            scaled.append(st.SCALE * (mean / math.sqrt(var)))
        if not math.isfinite(scaled[0] - scaled[1]):
            return "INVALID_REPLICATE"
        if trace is not None:
            trace.append(("g1_replicate", scaled[0], scaled[1]))
    return None


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


def g10(x: np.ndarray, trace: list[object] | None = None) -> str | None:
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
        if trace is not None:
            trace.append(("g10_var", var.tobytes().hex()))
        if (var <= 0).any() or not np.isfinite(var).all():
            return "NO_SHARPE_ON_HALF"
    return None


def g12(candidate: np.ndarray, trace: list[object] | None = None) -> str | None:
    """Annex C C-11 for every declared horizon H in {24, 72, 168} (DS2-7)."""
    values = candidate.tolist()
    for hours in (24, 72, 168):
        result = st.effective_sample_size(values, horizon_hours=hours)
        if trace is not None:
            trace.append(("g12_ess", hours, result.value))
        if result.reason is not None:
            return f"{result.reason}@H{hours}"
    return None


def u_g(x: np.ndarray, candidates: np.ndarray, benchmark: np.ndarray,
        nominee: int, seed: str, *, reference: bool = False,
        trace: list[object] | None = None) -> str | None:  # fmt: skip
    """The single U_G event (DS3-4): the first unavailable gate, or None.
    `trace` collects the gates' intermediate numbers (reference vectors)."""
    cand = candidates[:, nominee]
    # Every gate runs (RR-1): an engine fault in a later gate is never hidden
    # by an earlier refusal; the event is the first unavailable gate.
    reasons = (
        g1(cand, benchmark, seed, reference=reference, trace=trace),
        g2(cand, benchmark),
        g4(x.shape[0]),
        g10(x, trace),
        g12(cand, trace),
    )
    return next((r for r in reasons if r is not None), None)
