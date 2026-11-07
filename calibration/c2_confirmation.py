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

import hashlib
import json
import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import numpy as np

import aqt.core.attempts as attempts
import aqt.metrics.statistics as st
from aqt.backtest.costs import (
    CostModelError,
    ewma_hourly_volatility_bps_series,
    hourly_log_returns_bps,
)
from aqt.backtest.event_contract import (
    EventContractError,
    EventResult,
    run_event_contract,
)
from aqt.data.bars import BarSeries
from aqt.features.columns import feature_columns
from aqt.features.factory import FeatureFactoryError
from calibration import dsr, gates, screen
from calibration.seeds import sha

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


# --- Slice 2: the nominee's runs, keeping their statistics -------------------
#
# `screen_gates` (frozen, screen.py l.1060) performs these same runs but
# reports availability only. `nominee_gates` repeats its run glue in the same
# order with the same frozen building blocks and per-run checks (prepare,
# inputs, contract, run, g11_check, g14_check), keeping each run's numbers
# for the slice 1 rules. A test pins that every gate is UNAVAILABLE exactly
# when `screen_gates` gives a reason, with that reason, and N/A exactly where
# it gives N/A.
#
# C2 seeds (R-13): `trial_seed` is the beacon-protected trial_seed_j, used
# for the G-1 stream (the Task 12 `paired_sharpe_ci` stream, BTCUSDT, cost
# 1.0, the C-0 window id), the G-11 shifts and the G-14 offsets;
# `model_seed` is the nominee's `estimator_seed` (D-20 A1b). G-9, G-10 and
# G-13 are family-level and come from the orchestration (slice 3).

NOMINEE_GATES = ("G-1", "G-2", "G-3", "G-4", "G-5", "G-6", "G-7", "G-8",
                 "G-11", "G-12", "G-14")  # fmt: skip
Prepared = tuple[BarSeries, int, dict[str, tuple[float, ...]]]


@dataclass(frozen=True)
class _Run:
    candidate: EventResult
    benchmark: EventResult
    signals: list[float]


def _stats(run: _Run | str) -> Stats:
    if isinstance(run, str):
        return run
    try:
        return screen.leg_stats(run.candidate, run.benchmark)
    except screen.RunUnavailable as e:
        return e.reason


def nominee_gates(
    trial: dict[str, Any],
    path: np.ndarray,
    w0: datetime,
    window_hours: int,
    trial_seed: str,
    window_id: str,
    g_days: int,
    model_seed: int,
) -> dict[str, Gate]:
    """Annex C gates of one nominee on its confirmation path (DESIGN §5.2
    step 6); every gate is computed whatever the others give (P18-7)."""
    screen.check_trial(trial)
    if type(model_seed) is not int or not 0 <= model_seed < 2**31:
        raise screen.TrialError("model_seed must be an int in [0, 2**31)")
    warmup = trial["warmup_hours"]
    if window_hours < 48 or window_hours % 24 or len(path) != warmup + window_hours + 1:
        raise screen.TrialError(
            "path length must be warmup + whole window days + 1 hour"
        )
    if trial["model"] is not None and warmup < screen.model_warmup_hours(w0):
        raise screen.TrialError(
            f"a model trial needs warmup_hours >= {screen.model_warmup_hours(w0)}"
        )
    g8_na = not screen.plateau_dimensions(trial)
    g11_na = trial["g11_class"] == "constant_signal"
    g14_na = not screen.g14_applies(trial)
    nas = {"G-8": g8_na, "G-11": g11_na, "G-14": g14_na}
    if trial["sigma"] != screen.DEFAULT_SIGMA:
        return {
            g: Gate(NA) if nas.get(g) else _unavailable("SIGMA_UNBOUND")
            for g in NOMINEE_GATES
        }
    start = w0 - timedelta(hours=warmup)
    days = window_hours // 24
    prepared: dict[int, Prepared] = {}
    emissions: dict[tuple[int, int, str], list[float]] = {}
    sigmas: dict[int, tuple[float, ...]] = {}
    mismatched: list[int] = []

    def prepare(s: int) -> Prepared:
        if s not in prepared:  # features and cost volatility once per symbol
            series = screen.path_series(path, s, start)
            try:
                prepared[s] = (series, *feature_columns(series))
                sigmas[s] = ewma_hourly_volatility_bps_series(
                    hourly_log_returns_bps(series)
                )
            except (FeatureFactoryError, CostModelError) as e:
                raise screen.RunUnavailable("FEATURES_UNAVAILABLE") from e
        return prepared[s]

    def inputs(s: int, lag: int, at: dict[str, Any]) -> Prepared:
        series, first, columns = prepare(s)
        if at["model"] is not None:
            key = (s, lag, json.dumps(screen.model_params(at), sort_keys=True))
            if key not in emissions:
                emissions[key] = screen.model_column(
                    at, series, first, columns, warmup, window_hours, lag,
                    model_seed=model_seed,
                )  # fmt: skip
            columns = {**columns, f"model:{at['model']['id']}": tuple(emissions[key])}
        return series, first, columns

    def contract(
        series: BarSeries, s: int, targets: list[float], **kw: Any
    ) -> EventResult:
        try:
            return run_event_contract(
                series, targets, warmup, sigma_bps=sigmas[s], **kw
            )
        except (EventContractError, CostModelError) as e:
            raise screen.RunUnavailable("RUN_INVALID") from e

    def run(s: int, cost: float = 1.0, delay: int = 0, lag: int = 0,
            at: dict[str, Any] = trial) -> _Run | str:  # fmt: skip
        try:
            series, first, columns = inputs(s, lag, at)
            closes = [b.close for b in series.bars]
            signal = screen.load(at["signal"], at["signal_sha256"])  # fresh per run
            overlay = (
                None if at["overlay"] is None
                else screen.load(at["overlay"], at["overlay_sha256"])
            )  # fmt: skip
            candidate, signals = screen.leg_targets(
                at, signal, overlay, columns, first, closes, warmup, window_hours, lag
            )
            if screen.class_mismatch(at, np.asarray(signals)):
                mismatched.append(s)
            legs = [
                contract(series, s, targets, stress_multiplier=cost, delay=delay)
                for targets in (
                    candidate,
                    screen.benchmark_targets(columns, first, warmup, window_hours),
                )
            ]
        except screen.RunUnavailable as e:
            return e.reason
        return _Run(legs[0], legs[1], signals)

    out: dict[str, Gate] = {}
    out["G-3"] = g3(_stats(run(1)))
    base = run(0)
    btc = _stats(base)
    stressed: tuple[tuple[str, dict[str, Any]], ...] = (
        ("G-5", {"cost": screen.STRESS_COST}),
        ("G-6", {"lag": 1}),
        ("G-7", {"delay": 1}),
    )
    for gate, kwargs in stressed:
        out[gate] = survival(_stats(run(0, **kwargs)), out["G-3"])
    out["G-2"] = g2(btc)
    if isinstance(base, str):
        for gate in ("G-1", "G-4", "G-12"):
            out[gate] = _unavailable(base)
    else:
        cand = screen.daily_returns(base.candidate)
        bench = screen.daily_returns(base.benchmark)
        stream = st.ReplicateStream(
            trial_seed, st.CONVENTION_DOCUMENT_SHA256, "BTCUSDT", "1.0", window_id
        )
        out["G-1"] = g1(
            st.paired_sharpe_improvement_interval(cand, bench, stream=stream)
        )
        out["G-4"] = g4(w0, w0 + timedelta(hours=window_hours),
                        [w0 + k * DAY for k in range(days)], cand, bench)  # fmt: skip
        out["G-12"] = g12(cand, trial["horizon_hours"])
    if g8_na:
        out["G-8"] = Gate(NA)
    else:  # C-8: baseline E-IMPROV of the point and every present neighbour
        reasons: list[str] = []

        def e_improv(r: Stats) -> float | None:
            if isinstance(r, str):
                reasons.append(r)
                return None
            return r["e_improv"]

        v = e_improv(btc)
        near = [
            e_improv(_stats(run(0, at=nb))) for nb in screen.plateau_neighbours(trial)
        ]
        plateau = g8(trial, v, near)
        out["G-8"] = _unavailable(reasons[0]) if reasons else plateau
    if g11_na:
        out["G-11"] = Gate(NA)
    else:
        out["G-11"] = _g11(trial, base, btc, inputs, contract, trial_seed, window_id,
                           days, g_days, warmup, window_hours)  # fmt: skip
    if g14_na:
        out["G-14"] = Gate(NA)
    else:
        out["G-14"] = _g14(trial, prepare, w0, warmup, window_hours, trial_seed,
                           window_id, model_seed)  # fmt: skip
    if mismatched:
        out["G-11"] = _unavailable("CLASS_MISMATCH")
    return {g: out[g] for g in NOMINEE_GATES}


def _g11(
    trial: dict[str, Any],
    base: _Run | str,
    btc: Stats,
    inputs: Callable[[int, int, dict[str, Any]], Prepared],
    contract: Callable[..., EventResult],
    trial_seed: str,
    window_id: str,
    days: int,
    g_days: int,
    warmup: int,
    window_hours: int,
) -> Gate:
    """C-10 (3)-(7): the screen's g11_check, keeping each draw's E-IMPROV."""
    if isinstance(btc, str) or isinstance(base, str):
        return _unavailable(btc if isinstance(btc, str) else str(base))
    try:
        shifts = screen.g11_shifts(trial_seed, window_id, days, g_days)
    except screen.GateUnavailable as e:
        return _unavailable(e.reason)
    draws: list[float | None] = []
    try:
        series, first, columns = inputs(0, 0, trial)
        closes = [b.close for b in series.bars]
        for k in shifts:
            fresh = (
                None if trial["overlay"] is None
                else screen.load(trial["overlay"], trial["overlay_sha256"])
            )  # fmt: skip
            targets = screen.g11_targets(trial, fresh, base.signals, columns, first,
                                         closes, warmup, window_hours, k)  # fmt: skip
            stats = screen.leg_stats(contract(series, 0, targets), base.benchmark)
            draws.append(stats["e_improv"])
    except screen.RunUnavailable as e:
        return _unavailable(e.reason)
    gate = null_rule(btc["e_improv"], draws)
    return Gate(
        gate.result,
        gate.reason,
        {**gate.values, "shifts_sha256": screen.g11_shifts_sha256(shifts)},
    )


def _g14(
    trial: dict[str, Any],
    prepare: Callable[[int], Prepared],
    w0: datetime,
    warmup: int,
    window_hours: int,
    trial_seed: str,
    window_id: str,
    model_seed: int,
) -> Gate:
    """C-12: the screen's g14_check, keeping the nominee's and every draw's IC."""
    try:
        series, first, columns = prepare(0)
        bars = series.bars
        hours = trial["horizon_hours"]
        w1 = w0 + timedelta(hours=window_hours)
        ics: list[float] = []
        ys: list[float] = []
        draws = [None, *((trial_seed, window_id, d) for d in range(screen.G14_DRAWS))]
        for draw in draws:
            window, preds = screen.walk_forward(
                trial, series, first, columns, warmup, window_hours, 0, draw, model_seed
            )
            keep = [i for i, j in enumerate(window)
                    if bars[j].open_time + timedelta(hours=hours) < w1]  # fmt: skip
            if not ys:
                sigma = ewma_hourly_volatility_bps_series(
                    hourly_log_returns_bps(series)
                )
                ys = screen.labels(series, sigma, [window[i] for i in keep], hours)
            ics.append(screen.spearman_ic([preds[i] for i in keep], ys))
    except screen.RunUnavailable as e:
        return _unavailable(e.reason)
    return null_rule(ics[0], list(ics[1:]))


# --- Slice 3: the Annex A orchestration (DESIGN §2) --------------------------
#
# Pure checks over the cycle's records. The record layouts (declaration,
# attempt, look) are the module's [DESIGN] reading until the S4 format
# bindings fix them; every bound value (z_crit, T_min, g, the family block
# rule, the classifier) is passed in from the signed C2, never defaulted here.

FAMILIES = ("trend", "vol")
# P18-1 allows 1..80, but A-U1 needs a screen record and the frozen screen
# accepts at most 20 trials: refused here (owner decision R14C-S-5, 2026-11-07)
MAX_DECLARED = screen.MAX_TRIALS
GATES = tuple(f"G-{i}" for i in range(1, 15))
NA_GATES = frozenset({"G-8", "G-10", "G-11", "G-14"})  # Annex C C-8, C-9, C-10, C-12
LOOK_DAYS = 180  # P18-2
CRASH = "CRASH_NO_ARTIFACT"  # P18-1: ended without writing any result artifact
# P18-7: reasons that are infrastructure or governance (U_ops); every other
# unavailability is a procedure no-result (U_proc) [DESIGN: list for review]
U_OPS_REASONS = frozenset({"MISSING_DAY", "DUPLICATED_DAY", "IRREGULAR_DAY",
                           "MISALIGNED_SERIES", "SIGMA_UNBOUND"})  # fmt: skip


class CycleError(ValueError):
    """The cycle cannot proceed (invalid declaration, record or look)."""


def check_declaration(
    declared: dict[str, list[dict[str, Any]]], eligible: bool
) -> None:
    """P18-1: before the first evaluation. With an eligible window both families
    are declared; each declared family has 1..MAX_DECLARED trials with unique ids, every
    trial a valid interface (`screen.check_trial`) belonging to its family."""
    if set(declared) - set(FAMILIES):
        raise CycleError(f"unknown family {sorted(set(declared) - set(FAMILIES))}")
    if eligible and set(declared) != set(FAMILIES):
        raise CycleError("an eligible window needs both families declared")
    if not any(declared.values()):
        raise CycleError("at least one family must be declared")
    for family, trials in declared.items():
        if eligible and not trials:
            raise CycleError(
                f"{family}: 'not researched' needs a cycle without an eligible window"
            )
        if len(trials) > MAX_DECLARED:
            raise CycleError(f"{family}: {len(trials)} trials > {MAX_DECLARED}")
        ids = [t["trial_id"] for t in trials]
        if len(set(ids)) != len(ids):
            raise CycleError(f"{family}: duplicate trial ids")
        for t in trials:
            screen.check_trial(t)
            if t["family"] != family:
                raise CycleError(f"{t['trial_id']} is not a {family} trial")


def check_eligibility(*, partition_start: datetime, window_end: datetime, t_min: int,
                      last_seen: datetime, embargo_days: int,
                      g_days: int) -> tuple[datetime, int]:  # fmt: skip
    """P18-0 (iii) and A-B7 (v), recomputed (R14C-S-3). The window start is
    derived, never taken from the caller: w0 = partition start + g (DRAFT R-3:
    the partition's first g days are dropped). `window_end` (exclusive) is the
    end of the validated C2 manifest's complete days (loader slice); T is the
    whole days in [w0, window_end). The recorded embargo is the bound g, w0 is
    at least g after the last observation mounted or evaluated before
    declaration, and T >= T_min. Returns (w0, T). (i), (ii) and (iv) are
    recorded governance checks the module cannot prove."""
    if embargo_days != g_days:
        raise CycleError(f"recorded embargo {embargo_days} != bound g {g_days}")
    for name, t in (("partition start", partition_start), ("window end", window_end)):
        if t.utcoffset() != timedelta(0) or t != t.replace(hour=0, minute=0, second=0,
                                                           microsecond=0):  # fmt: skip
            raise CycleError(f"{name} {t} is not a UTC day boundary")
    w0 = partition_start + timedelta(days=g_days)
    if w0 < last_seen + timedelta(days=embargo_days):
        raise CycleError(
            "window starts inside the embargo after the last seen observation"
        )
    t_days = (window_end - w0) // DAY
    if t_days < t_min:
        raise CycleError(f"T = {t_days} < T_min = {t_min}")
    return w0, t_days


def check_screen_record(record: bytes, record_sha256: str, trials: list[dict[str, Any]],
                        object_sha256: str) -> None:  # fmt: skip
    """A-U1: the declaration's fail-closed screen record is the declared one,
    for this trial set and this qualification object, and its outcome is
    SCREEN_AVAILABLE. The module does not re-run the screen."""
    if hashlib.sha256(record).hexdigest() != record_sha256:
        raise CycleError("screen record bytes do not match the declared hash")
    r = json.loads(record)
    if r.get("trial_set_sha256") != screen.trial_set_sha256(trials):
        raise CycleError("screen record is for another trial set")
    if r.get("qualification_object_sha256") != object_sha256:
        raise CycleError("screen record is for another qualification object")
    if r.get("outcome") != "SCREEN_AVAILABLE":
        raise CycleError(f"screen outcome {r.get('outcome')!r}")


def family_attempts(
    entries: Sequence[Any],
    *,
    family: str,
    cycle: str,
    trial_of: dict[tuple[str, int], str],
) -> list[dict[str, Any]]:
    """The family's confirmation attempts in this cycle, in ledger order, from
    the durable `core.attempts` records (R14C-S-2). Every start record is
    validated first (`attempt_counts` fails closed); `trial_of` maps a start's
    (hypothesis_hash, trial_index) to its declared trial id [DESIGN: until the
    S4 record layout binds it]. `start` and `end` are the ledger positions of
    the start and outcome records (R14C2-S-1); `outcome` and `end` are None
    while no outcome is recorded."""
    attempts.attempt_counts(entries, family=family, cycle=cycle)
    outcomes: dict[str, tuple[int, dict[str, Any]]] = {}
    for i, e in enumerate(entries):
        if e.record_type == attempts.ATTEMPT_OUTCOME_RECORD_TYPE:
            aid = e.payload["attempt_id"]
            if aid in outcomes:
                raise CycleError(f"attempt {aid} has two outcome records")
            outcomes[aid] = (i, e.payload)
    out = []
    for i, e in enumerate(entries):
        if e.record_type != attempts.ATTEMPT_STARTED_RECORD_TYPE:
            continue
        p = e.payload
        if (p["family"], p["cycle"], p["partition"]) != (
            family, cycle, attempts.PARTITION_CONFIRMATION
        ):  # fmt: skip
            continue
        key = (p["hypothesis_hash"], p["trial_index"])
        if key not in trial_of:
            raise CycleError(f"attempt {p['attempt_id']} is for an undeclared trial")
        end, o = outcomes.get(p["attempt_id"], (None, {}))
        out.append({"trial_id": trial_of[key], "outcome": o.get("outcome"),
                    "reason_code": o.get("reason_code"), "start": i,
                    "end": end})  # fmt: skip
    return out


def trial_states(family_attempts_: list[dict[str, Any]],
                 trial_ids: list[str]) -> dict[str, str]:  # fmt: skip
    """P18-1 over the whole family (R14C-S-2, R14C2-S-1/2). Attempts carry
    their ledger positions (`start`, `end`). A crash is a trial's first attempt
    recorded `failed` with the crash code; the family's one re-run slot goes
    to the crash whose outcome was recorded first. Only that trial may have a
    second attempt, started after the crash was recorded, and nothing may
    follow it. States:
    `unstarted`, `running` (last attempt has no outcome yet), `completed`,
    `rerun` (its slot crash awaits the re-run) or `final` (ended without a
    completed evaluation). Any other sequence is refused."""
    by: dict[str, list[dict[str, Any]]] = {tid: [] for tid in trial_ids}
    for a in sorted(family_attempts_, key=lambda a: a["start"]):
        if a["trial_id"] not in by:
            raise CycleError(f"attempt for undeclared trial {a['trial_id']}")
        by[a["trial_id"]].append(a)
    crashes = [
        seq[0] for seq in by.values()
        if seq and seq[0]["outcome"] == attempts.OUTCOME_FAILED
        and seq[0]["reason_code"] == CRASH and seq[0]["end"] is not None
    ]  # fmt: skip
    slot = min(crashes, key=lambda a: a["end"])["trial_id"] if crashes else None
    for tid, seq in by.items():
        if len(seq) > 2 or (
            len(seq) == 2 and (tid != slot or seq[1]["start"] < seq[0]["end"])
        ):
            raise CycleError(f"{tid}: attempt {len(seq)} is not permitted")
    states = {}
    for tid, seq in by.items():
        if not seq:
            states[tid] = "unstarted"
        elif seq[-1]["outcome"] is None:
            states[tid] = "running"
        elif seq[-1]["outcome"] == attempts.OUTCOME_COMPLETED:
            states[tid] = "completed"
        elif tid == slot and len(seq) == 1:
            states[tid] = "rerun"
        else:
            states[tid] = "final"
    return states


def look_allowed(states: dict[str, str], cycle_start: datetime, now: datetime,
                 terminated: bool, looked: bool) -> bool:  # fmt: skip
    """P18-2: one shared look, at the earlier of every declared trial finished
    (completed, or final) or day 180; never after a protocol-revision or
    invalidation record (no pick), never twice."""
    if terminated:
        raise CycleError("cycle ended before the pick: no pick, no promotion")
    if looked:
        raise CycleError("the cycle's one look has already run")
    done = all(s in ("completed", "final") for s in states.values())
    return done or now >= cycle_start + timedelta(days=LOOK_DAYS)


@dataclass(frozen=True)
class Nomination:
    """P18-3, P18-4 and A-V1 for one family."""

    available: bool  # A_f
    reason: str | None
    nominee: str | None  # trial id
    z: float | None
    task12: dsr.FamilyResult  # reported; V governs (A-V1)
    v: dsr.FamilyResult
    x: np.ndarray | None = None  # T x K, columns in ascending trial-id order
    cause: str | None = None  # P18-7 when A_f fails: U_ops or U_proc


def nominate(
    family: str,
    states: dict[str, str],
    window: tuple[datetime, int],
    completed: dict[str, tuple[str, list[Any], list[float]]],
    declared_hashes: dict[str, str],
    family_seed: str,
    rule: str,
    classifier: Callable[[np.ndarray, list[float]], bool] | None,
) -> Nomination:
    """`states` is `trial_states` over the durable attempt records, one entry
    per declared trial; `completed[id] = (configuration hash, days, daily BTC
    E-DIFF values)` for each trial whose state is `completed` (R14C-S-4).
    `window` is check_eligibility's (w0, T): every day index must be exactly
    the T complete UTC days from w0 (Annex B §2.1; R14C2-S-3).
    A_f fails on any trial not completed, a hash mismatch or a day index
    other than the window's (all U_ops, P18-7), or on
    any dsr.evaluate unavailability (U_proc). Columns are in ascending
    trial-id order, so dsr.evaluate's lowest-column tie rule is P18-4's
    lowest-declared-id rule; its column maps back to that id. Method V
    refuses unless `dsr.v_runtime_check` passed at startup (A-V1)."""
    if classifier is None:  # D-18 O18-2: never evaluated without it
        raise CycleError("the supported-law classifier is required")
    if set(states) != set(declared_hashes):
        raise CycleError(f"{family}: trial ids do not match the declaration")
    if any(states[tid] != "completed" for tid in completed if tid in states) or (
        set(completed) - set(states)
    ):
        raise CycleError(f"{family}: evaluation output without a completed attempt")
    trial_ids = sorted(states)
    expected = [window[0] + i * DAY for i in range(window[1])]
    empty = dsr.FamilyResult("NOT_EVALUATED")

    def ops(reason: str) -> Nomination:
        return Nomination(False, reason, None, None, empty, empty, cause="U_ops")

    for tid in trial_ids:
        if states[tid] != "completed" or tid not in completed:
            return ops(f"{tid}: no completed evaluation ({states[tid]})")
        if completed[tid][0] != declared_hashes[tid]:
            return ops(f"{tid}: configuration hash mismatch")
        days, values = completed[tid][1], completed[tid][2]
        if list(days) != expected or len(values) != len(expected):
            return ops(f"{tid}: MISALIGNED_SERIES")
    x = np.array([completed[tid][2] for tid in trial_ids], dtype=float).T
    v = dsr.evaluate(x, family_seed, rule, numerics="v", classifier=classifier)
    t12 = dsr.evaluate(x, family_seed, rule, numerics="task12", classifier=classifier)
    if v.reason is not None or v.nominee is None:
        return Nomination(False, v.reason, None, None, t12, v, x, cause="U_proc")
    return Nomination(True, None, trial_ids[v.nominee], v.z, t12, v, x)


def family_gates(nomination: Nomination, z_crit: str, benchmark_sha256: str,
                 canonical_sha256: str) -> dict[str, Gate]:  # fmt: skip
    """G-9 (A P18-6 on V's z), G-10 (C-9 on the same family matrix the
    nomination used) and G-13 (R-10). Every gate is computed (P18-7)."""
    x = nomination.x
    return {
        "G-9": g9(nomination.z, z_crit),
        "G-10": pbo(x) if x is not None else _unavailable("NO_FAMILY_MATRIX"),
        "G-13": g13(benchmark_sha256, canonical_sha256),
    }


def cause_code(gate: Gate) -> str | None:
    """P18-7: U_ops (infrastructure or governance) first, else U_proc."""
    if gate.result != UNAVAILABLE:
        return None
    reason = (gate.reason or "").split(":")[-1]
    return "U_ops" if reason in U_OPS_REASONS else "U_proc"


def nominee_outcome(gates_: dict[str, Gate]) -> str:
    """P18-5: the nominee proceeds only if every pre-lockbox gate is PASS or a
    frozen N/A; any FAIL or UNAVAILABLE leaves the family with no promotable
    trial (no fallback, no replacement). All 14 gates are read: a gate not
    computed counts as UNAVAILABLE (P18-7), and N/A is accepted only where
    Annex C fixes it (C-0 Outcomes; R14C-S-1)."""
    if set(gates_) - set(GATES):
        raise CycleError(f"unknown gates {sorted(set(gates_) - set(GATES))}")
    outcomes = (PASS, FAIL, NA, UNAVAILABLE)
    odd = sorted(k for k, g in gates_.items() if g.result not in outcomes)
    if odd:  # C-0: only four outcomes (R14C2-S-4)
        raise CycleError(f"result outside PASS/FAIL/N/A/UNAVAILABLE for {odd}")
    bad = sorted(k for k, g in gates_.items() if g.result == NA and k not in NA_GATES)
    if bad:
        raise CycleError(f"N/A is not fixed by Annex C for {bad}")
    results = [gates_[k].result if k in gates_ else UNAVAILABLE for k in GATES]
    if UNAVAILABLE in results:
        return "NO_RESULT"
    if FAIL in results:
        return "FAILED"
    return "PROCEEDS_TO_LOCKBOX"


def seeds_record(family_seed: str, trial_ids: list[str]) -> dict[str, str]:
    """R-13: every trial_seed_j = SHA256(cj({"family_seed", "trial_id"})),
    recorded for the evaluation (Constitution §27)."""
    return {
        tid: sha({"family_seed": family_seed, "trial_id": tid}) for tid in trial_ids
    }
