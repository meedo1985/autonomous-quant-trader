"""R-14a confirmation module (review/r14a-modules/DESIGN.md Ã‚Â§5, Ã‚Â§7.2).

Slice 1: the C2 gate decisions of Annex C (C-1..C-12), as pure functions
over results the frozen code computes (DESIGN Ã‚Â§1: no C2 pass decision is
frozen; owner decision Q-P1 (b) puts them here). The runs, the Annex A
orchestration, seeds, sealing and loading are later slices. Nothing here
binds until its SHA-256 is a row of the signed C2 (R-14a item 1); until then
it is a draft under review.

R-14a item 3: imports only engine-commit modules, the object's `screen.py`,
the standard library and pinned image libraries; never the lockbox module.
Item 4: frozen functions are called, not re-implemented.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import numpy as np

import aqt.metrics.statistics as st
from calibration import gates, screen

PASS, FAIL, NA, UNAVAILABLE = "PASS", "FAIL", "N/A", "UNAVAILABLE"
DD_LIMIT = 0.05  # C-0 drawdown condition (absolute)
G4_RATE = 0.60  # C-4 (6)
G4_MONTHS = 3  # C-4 (1)
PBO_LIMIT = 0.30  # C-9 (5)
PBO_MIN_TRIALS = 20  # C-9 (7)
PBO_BLOCKS = 16  # C-9 (2)
NULL_DRAWS = 500  # C-10, C-12
NULL_BELOW = 476  # C-10 (7), C-12 (7)
ESS_MIN = 120.0  # C-11 (4)
HORIZONS = (24, 72, 168)  # C-11 (2)
DAY = timedelta(days=1)


@dataclass(frozen=True)
class Gate:
    """One gate's outcome (C-0 "Outcomes"); `reason` only for UNAVAILABLE,
    `values` the reported numbers (Constitution Ã‚Â§23)."""

    result: str
    reason: str | None = None
    values: dict[str, Any] = field(default_factory=dict)


def _unavailable(reason: str, **values: Any) -> Gate:
    return Gate(UNAVAILABLE, reason, values)


def _rule(ok: bool, **values: Any) -> Gate:
    return Gate(PASS if ok else FAIL, None, values)


def dd_holds(dd_excess: float) -> bool:
    """C-0: MDD(candidate) - MDD(benchmark) <= 0.05, absolute."""
    return dd_excess <= DD_LIMIT


def _finite(stats: dict[str, float], *keys: str) -> bool:
    return all(type(stats.get(k)) is float and math.isfinite(stats[k]) for k in keys)


# --- C-1 .. C-3, C-5, C-7: rules on `screen.leg_stats` results ---------------
#
# `stats` is `screen.leg_stats(candidate, benchmark)` for the run the rule
# names, or a reason string when that run is unavailable (RunUnavailable).

Stats = dict[str, float] | str


def g1(interval: st.PairedBootstrapInterval) -> Gate:
    """C-1: lower bound of the 90% paired CI of BTC E-IMPROV > 0; any
    unavailability reason of the routine is UNAVAILABLE."""
    if interval.reason is not None:
        return _unavailable(str(interval.reason))
    lower = interval.lower
    if lower is None or not math.isfinite(lower):
        return _unavailable("NONFINITE_RESULT")
    return _rule(lower > 0, lower=lower, upper=interval.upper,
                 point=interval.point_estimate)  # fmt: skip


def g2(btc: Stats) -> Gate:
    """C-2: DD(BTC) on the baseline run."""
    if isinstance(btc, str):
        return _unavailable(btc)
    if not _finite(btc, "dd_excess"):
        return _unavailable("NONFINITE_RESULT")
    return _rule(dd_holds(btc["dd_excess"]), dd_excess=btc["dd_excess"])


def g3(eth: Stats) -> Gate:
    """C-3: ETH E-IMPROV > 0 AND DD(ETH), both on the ETH 1x baseline run."""
    if isinstance(eth, str):
        return _unavailable(eth)
    if not _finite(eth, "e_improv", "dd_excess"):
        return _unavailable("NONFINITE_RESULT")
    ok = eth["e_improv"] > 0 and dd_holds(eth["dd_excess"])
    return _rule(ok, e_improv=eth["e_improv"], dd_excess=eth["dd_excess"])


def survival(btc: Stats, g3_result: Gate) -> Gate:
    """C-5 (G-5 on the 2x run) and C-7 (4) (G-6, G-7 on their stressed runs):
    BTC E-IMPROV > 0, BTC candidate net return > 0, DD(BTC), and G-3 passes
    (ETH at 1x). An unavailable G-3 makes the gate UNAVAILABLE."""
    if isinstance(btc, str):
        return _unavailable(btc)
    if not _finite(btc, "e_improv", "dd_excess", "net_return"):
        return _unavailable("NONFINITE_RESULT")
    if g3_result.result == UNAVAILABLE:
        return _unavailable(f"G-3:{g3_result.reason}")
    ok = (
        btc["e_improv"] > 0
        and btc["net_return"] > 0
        and dd_holds(btc["dd_excess"])
        and g3_result.result == PASS
    )
    return _rule(ok, **btc, g3=g3_result.result)


# --- C-4 G-4: paired fold win rate -------------------------------------------


def g4_boundaries(w0: datetime, w1: datetime) -> list[datetime]:
    """C-4 (1)-(2): B_k = w0 + 3k calendar months, from w0 directly (never
    chained), clipped to the month's last day; complete blocks end <= w1.
    Returns B_0 .. B_n for the n complete blocks."""
    out = [w0]
    while (b := screen.months_before(w0, -G4_MONTHS * len(out))) <= w1:
        out.append(b)
    return out


def g4(
    w0: datetime,
    w1: datetime,
    days: Sequence[datetime],
    candidate: Sequence[float],
    benchmark: Sequence[float],
) -> Gate:
    """C-4 on the BTC 1x paired daily series: `days[i]` is the 00:00 UTC start
    of day i, `candidate[i]`, `benchmark[i]` its two legs' returns."""
    if not len(days) == len(candidate) == len(benchmark):
        return _unavailable("MISALIGNED_SERIES")
    bounds = g4_boundaries(w0, w1)
    n = len(bounds) - 1
    if n == 0:
        return _unavailable("NO_COMPLETE_BLOCK")
    index = {d: i for i, d in enumerate(days)}
    if len(index) != len(days):
        return _unavailable("DUPLICATED_DAY")
    wins = 0
    blocks = []
    for a, b in zip(bounds, bounds[1:], strict=False):
        want = [a + k * DAY for k in range((b - a) // DAY)]
        if any(d not in index for d in want):
            return _unavailable("MISSING_DAY")
        rows = [index[d] for d in want]
        if rows != list(range(rows[0], rows[0] + len(rows))):
            return _unavailable("IRREGULAR_DAY")
        left = [candidate[i] for i in rows]
        right = [benchmark[i] for i in rows]
        if not all(map(math.isfinite, left + right)):
            return _unavailable("NONFINITE_DAY")
        paired = st.paired_sharpe_statistics(left, right)
        e = paired.paired_sharpe_improvement
        zero = "ZERO_VARIANCE" in (paired.candidate.reason, paired.benchmark.reason)
        if e is None and not zero:
            return _unavailable(str(paired.reason or "E_IMPROV_UNAVAILABLE"))
        win = e is not None and e > 0  # C-4 (5): 0 and zero variance not a win
        wins += win
        blocks.append({"start": a.isoformat(), "e_improv": e, "win": win})
    rate = wins / n
    # C-4 (2): the final partial block is reported only, never in the rate
    tail = [i for i, d in enumerate(days) if bounds[-1] <= d < w1]
    partial: float | str | None = None
    if bounds[-1] < w1:
        try:
            p = st.paired_sharpe_statistics(
                [candidate[i] for i in tail], [benchmark[i] for i in tail]
            )
            e = p.paired_sharpe_improvement
            partial = e if e is not None else str(p.reason or "NOT_COMPUTED")
        except (st.StatisticsError, ValueError):
            partial = "NOT_COMPUTED"
    return _rule(rate >= G4_RATE, wins=wins, n=n, rate=rate, blocks=blocks,
                 partial_block_e_improv=partial)  # fmt: skip


# --- C-8 G-8: parameter plateau ----------------------------------------------


def g8(
    trial: dict[str, Any], v: float | None, neighbours: Sequence[float | None]
) -> Gate:
    """C-8 steps 1-4. `v` is the selected trial's BTC E-IMPROV, `neighbours`
    the present +/-1-step neighbours' (`screen.plateau_neighbours` order);
    None for a run that is unavailable."""
    dims = screen.plateau_dimensions(trial)
    if not dims:
        return Gate(NA)
    values = [v, *neighbours]
    if not all(x is not None and math.isfinite(x) for x in values):
        return _unavailable("NONFINITE_E_IMPROV")
    assert v is not None
    if v <= 0:
        return _rule(False, v=v)
    m = float(np.median(np.array(neighbours, dtype=float)))  # even: mean of middle
    point = trial["parameter_point"]
    boundary = any(
        screen._typed(point[name]) in (screen._typed(o[0]), screen._typed(o[-1]))
        for name, o in dims.items()
    )
    return _rule(m >= 0.5 * v and not boundary, v=v, m=m, boundary=boundary)


# --- C-9 G-10: PBO -----------------------------------------------------------


def pbo(x: np.ndarray) -> Gate:
    """C-9 on the T x N matrix of daily BTC E-DIFF columns in declared order.
    Sharpe is `st.sharpe` (C-0); a trial without a Sharpe on any IS or OOS
    half makes the gate UNAVAILABLE."""
    t, k = x.shape
    if k < PBO_MIN_TRIALS:
        return Gate(NA)
    if t < PBO_BLOCKS:
        return _unavailable("INSUFFICIENT_OBSERVATIONS")
    blocks = np.array_split(np.arange(t), PBO_BLOCKS)  # remainder to earliest
    columns = [x[:, j].tolist() for j in range(k)]
    every = frozenset(range(PBO_BLOCKS))

    def sharpes(half: Sequence[int]) -> list[float] | None:
        rows = [i for b in sorted(half) for i in blocks[b]]
        out = []
        for c in columns:
            s = st.sharpe([c[i] for i in rows]).scaled
            if s is None:
                return None
            out.append(s)
        return out

    scores = []
    for split in gates.SPLITS:
        inside = sharpes(split.tolist())
        outside = sharpes(sorted(every - set(split.tolist())))
        if inside is None or outside is None:
            return _unavailable("NO_SHARPE_ON_HALF")
        best = max(inside)
        tied = [j for j in range(k) if inside[j] == best]
        ranks = screen.midranks(outside)
        # logit(r/(N+1)) < 0 iff 2r < N+1; midranks are halves, so exact
        per = [1.0 if 2 * ranks[j] < k + 1 else 0.5 if 2 * ranks[j] == k + 1 else 0.0
               for j in tied]  # fmt: skip
        scores.append(math.fsum(per) / len(per))
    phi = math.fsum(scores) / len(scores)
    return _rule(phi <= PBO_LIMIT, phi=phi, splits=len(scores))


# --- C-10 G-11, C-12 G-14: null pass rules -----------------------------------


def null_rule(observed: float | None, draws: Sequence[float | None]) -> Gate:
    """C-10 (7) / C-12 (7): PASS iff at least 476 of the 500 draws are strictly
    below the observed statistic (ties not below; all 500 tied is FAIL). Any
    missing statistic is UNAVAILABLE; the denominator stays 500."""
    if len(draws) != NULL_DRAWS:
        return _unavailable("DRAW_COUNT")
    if observed is None or not all(d is not None for d in draws):
        return _unavailable("STATISTIC_UNAVAILABLE")
    values = [observed, *draws]
    if not all(math.isfinite(x) for x in values if x is not None):
        return _unavailable("NONFINITE_RESULT")
    below = sum(d < observed for d in draws if d is not None)
    return _rule(below >= NULL_BELOW, observed=observed, below=below)


# --- C-11 G-12: effective decisions ------------------------------------------


def g12(returns: Sequence[float], horizon_hours: int) -> Gate:
    """C-11 at the nominee's declared horizon; every validation exception is
    UNAVAILABLE (C-11 (3))."""
    if horizon_hours not in HORIZONS:
        return _unavailable("INVALID_HORIZON")
    try:
        ess = st.effective_sample_size(returns, horizon_hours=horizon_hours)
    except (st.StatisticsError, ValueError, TypeError) as e:
        return _unavailable(type(e).__name__)
    if ess.reason is not None or ess.value is None:
        return _unavailable(str(ess.reason))
    return _rule(ess.value >= ESS_MIN, decisions=len(returns), h=ess.horizon_days,
                 ess=ess.value, method=ess.method)  # fmt: skip


# --- R-10 G-9, G-13 ----------------------------------------------------------


def g9(z_star: float | None, z_crit: str) -> Gate:
    """A P18-6: z* >= z_crit, z_crit parsed from its decimal string to the
    nearest binary64 (`float` rounds correctly)."""
    crit = float(z_crit)
    if z_star is None or not math.isfinite(z_star):
        return _unavailable("NONFINITE_Z")
    return _rule(z_star >= crit, z=z_star, z_crit=crit)


def g13(benchmark_sha256: str, canonical_sha256: str) -> Gate:
    """R-10: the benchmark's hash equals the v1.1 canonical benchmark hash."""
    return _rule(benchmark_sha256 == canonical_sha256, sha256=benchmark_sha256)
