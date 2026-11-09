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
from datetime import UTC, datetime, timedelta
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
V1_CONFIRMATION_START = datetime(2022, 1, 1, tzinfo=UTC)  # protocol_v1.yaml:66
# inclusive end, the same in v1 and in the C2 binding (DRAFT_WORDING partitions)
V1_CONFIRMATION_END = datetime(2025, 5, 31, 23, 59, 59, tzinfo=UTC)
CRASH = "CRASH_NO_ARTIFACT"  # P18-1: ended without writing any result artifact
NOT_COMPLETED = (attempts.OUTCOME_FAILED, attempts.OUTCOME_ABORTED)
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


def check_eligibility(*, c2_start: datetime, c2_end: datetime, t_min: int,
                      last_seen: datetime, embargo_days: int,
                      g_days: int) -> tuple[datetime, int]:  # fmt: skip
    """P18-0 (iii) and A-B7 (v), recomputed (R14C-S-3, R14C5-S-1). `c2_start`
    is the signed C2's `partitions.confirmation.start`, which DRAFT R-3 makes
    the eligible window's start and the C2 binding fixes at the v1 partition
    start plus g (DRAFT_WORDING `partitions`): it must equal exactly
    V1_CONFIRMATION_START + g, and w0 = c2_start. `c2_end` is the signed C2's
    inclusive `partitions.confirmation.end`, which must equal
    V1_CONFIRMATION_END; T is the whole days in [w0, c2_end + 1 s)
    (R14C6-S-1). That every one of those days is present is the loader's
    manifest check (slice 6). The recorded embargo is the bound g,
    w0 is at least g after the last observation mounted or evaluated before
    declaration, and T >= T_min. Returns (w0, T). (i), (ii) and (iv) are
    recorded governance checks the module cannot prove."""
    if embargo_days != g_days:
        raise CycleError(f"recorded embargo {embargo_days} != bound g {g_days}")
    if c2_end != V1_CONFIRMATION_END:
        raise CycleError(f"C2 end {c2_end} is not {V1_CONFIRMATION_END}")
    window_end = c2_end + timedelta(seconds=1)
    for name, t in (("C2 start", c2_start), ("window end", window_end)):
        if t.utcoffset() != timedelta(0) or t != t.replace(hour=0, minute=0, second=0,
                                                           microsecond=0):  # fmt: skip
            raise CycleError(f"{name} {t} is not a UTC day boundary")
    if c2_start != V1_CONFIRMATION_START + timedelta(days=g_days):
        raise CycleError(
            f"C2 start {c2_start} is not the v1 partition start plus g = {g_days} days"
        )
    w0 = c2_start
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
    recorded not completed (`failed` or `aborted`) with the crash code
    (R14C3-S-1); the family's one re-run slot goes to the crash whose outcome
    was recorded first. Only that trial may have a second attempt, started
    after the crash was recorded, and nothing may follow it. While a first
    attempt that started before that crash record has no outcome, the slot is
    undetermined (it may be an earlier unrecorded crash): no re-run is
    permitted until recovery records its outcome (R14C3-S-2), and the crashed
    trials are `undetermined`, not finished, so the look waits for them or
    day 180 (R14C4-S-1). States:
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
        if seq and seq[0]["outcome"] in NOT_COMPLETED
        and seq[0]["reason_code"] == CRASH and seq[0]["end"] is not None
    ]  # fmt: skip
    first = min(crashes, key=lambda a: a["end"]) if crashes else None
    # R14C4-S-1: an undetermined slot grants no re-run, but states are still
    # returned so the day-180 look can record the family (P18-2, P18-7)
    undetermined = first is not None and any(
        seq and seq[0]["end"] is None and seq[0]["start"] < first["end"]
        for seq in by.values()
    )
    slot = first["trial_id"] if first and not undetermined else None
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
        elif undetermined and len(seq) == 1 and seq[0] in crashes:
            states[tid] = "undetermined"  # may still get the slot
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


# --- slice 4: seeds (DESIGN §5.1; DRAFT R-7, R-13, seed_disclosure; line 266) --

POLICY = "L266_MOD_2_31"  # D-20 A1b, as the lockbox module's POLICY
_HEX = frozenset("0123456789abcdef")


class SeedError(CycleError):
    """seed_disclosure / DESIGN §5.1: a seed cannot be verified; the evaluation
    is invalid and no gate runs."""


@dataclass(frozen=True)
class Chain:
    """The drand chain the signed C2 fixes (`seed_disclosure.beacon`), never a
    caller's choice: the loader reads it from the signed bytes (slice 6)."""

    public_key: str
    genesis_time: int  # unix seconds of round 1
    period: int  # seconds between rounds
    scheme: str  # must be SCHEME, the only one this module verifies (FP3)


@dataclass(frozen=True)
class Beacon:
    """One drand output as published: round, randomness, signature (hex)."""

    round: int
    randomness: str
    signature: str


# Protocol line 266, the frozen `aqt.core.preregistration.trial_seed` (R-8), set
# only by load_line266 (DESIGN_SEED_VERIFIER rev 3 §2).
_TRIAL_SEED: Callable[..., str] | None = None


def load_line266() -> None:
    """Import line 266's frozen `trial_seed` on the qualified image (R-8). The
    caller runs this before any protected read, so R-14's byte check covers
    `preregistration.py` and its imports (SV2-S-3). That module imports
    `jsonschema` at top level for `_validate_against_schema` only, and the image
    lacks it: for this one import, inert placeholders stand in for its three
    names and refuse if ever used; they are removed afterwards. No other
    jsonschema is ever loaded through here."""
    global _TRIAL_SEED
    _TRIAL_SEED = None  # a failed reload must not leave an earlier one (R14SM-S-1)
    import importlib
    import sys
    import types

    def refuse(*_: object, **__: object) -> None:
        raise SeedError("jsonschema is not available to the evaluation")

    root = types.ModuleType("jsonschema")
    exc = types.ModuleType("jsonschema.exceptions")
    root.Draft202012Validator = type(  # type: ignore[attr-defined]
        "Draft202012Validator",
        (),
        {"__init__": refuse, "check_schema": staticmethod(refuse)},
    )
    for name in ("SchemaError", "ValidationError"):
        setattr(exc, name, type(name, (Exception,), {"__init__": refuse}))
    root.exceptions = exc  # type: ignore[attr-defined]
    names = ("jsonschema", "jsonschema.exceptions")
    saved = {n: sys.modules[n] for n in names if n in sys.modules}
    try:
        if "aqt.core.preregistration" not in sys.modules:
            sys.modules.update({"jsonschema": root, "jsonschema.exceptions": exc})
        module = importlib.import_module("aqt.core.preregistration")
    finally:
        for n in names:
            sys.modules.pop(n, None)
        sys.modules.update(saved)
    _TRIAL_SEED = module.trial_seed


def _hex(value: object, length: int | None = None) -> bool:
    return (
        isinstance(value, str)
        and len(value) > 0
        and len(value) % 2 == 0
        and set(value) <= _HEX
        and (length is None or len(value) == length)
    )


# --- slice 4a, route M: drand quicknet BLS verification, standard library only ---
# seed_disclosure `verification` and R-14a item 7: the module verifies the beacon
# signature itself. Scheme `bls-unchained-g1-rfc9380` (FP3): signature on G1, key on
# G2, message SHA-256(round as 8-byte big-endian), hash-to-G1 by RFC 9380
# BLS12381G1_XMD:SHA-256_SSWU_RO_ with drand's DST. Constants from RFC 9380 (§8.8.1,
# Appendix E.2) and the BLS12-381 definition; pinned by the RFC's vectors and real
# drand rounds in the tests. Public data only, so constant time is not needed.

SCHEME = "bls-unchained-g1-rfc9380"
_DST = b"BLS_SIG_BLS12381G1_XMD:SHA-256_SSWU_RO_NUL_"
_P = 0x1A0111EA397FE69A4B1BA7B6434BACD764774B84F38512BF6730D2A0F6B0F6241EABFFFEB153FFFFB9FEFFFFFFFFAAAB  # noqa: E501
_R = 0x73EDA753299D7D483339D80809A1D80553BDA402FFFE5BFEFFFFFFFF00000001
_X_ABS = 0xD201000000010000  # |x|, the BLS12-381 parameter x is negative
_H_EFF = 0xD201000000010001  # RFC 9380 §8.8.1 h_eff = 1 - x
_A_ISO = 0x144698A3B8E9433D693A02C96D4982B0EA985383EE66A8D8E8981AEFD881AC98936F8DA0E0F97F5CF428082D584C1D  # noqa: E501
_B_ISO = 0x12E2908D11688030018B12E8753EEE3B2016C1F0F24F4070A0B9C14FCEF35EF55A23215A316CEAA5D1CC48E98E172BE0  # noqa: E501
_Z_ISO = 11
_G2_X = (
    0x024AA2B2F08F0A91260805272DC51051C6E47AD4FA403B02B4510B647AE3D1770BAC0326A805BBEFD48056C8C121BDB8,
    0x13E02B6052719F607DACD3A088274F65596BD0D09920B61AB5DA61BBDC7F5049334CF11213945D57E5AC7D055D042B7E,
)
_G2_Y = (
    0x0CE5D527727D6E118CC9CDC6DA2E351AADFD9BAA8CBDD3A76D429A695160D12C923AC9CC3BACA289E193548608B82801,
    0x0606C4A02EA734CC32ACD2B02BC28B99CB3E287E85A763AF267492AB572E99AB3F370D275CEC1DA1AAA9075FF05F79BE,
)
# RFC 9380 Appendix E.2, k_(i,j) for j = 0.. (x_den and y_den are monic)
_ISO1 = (
    0x11A05F2B1E833340B809101DD99815856B303E88A2D7005FF2627B56CDB4E2C85610C2D5F2E62D6EAEAC1662734649B7,
    0x17294ED3E943AB2F0588BAB22147A81C7C17E75B2F6A8417F565E33C70D1E86B4838F2A6F318C356E834EEF1B3CB83BB,
    0xD54005DB97678EC1D1048C5D10A9A1BCE032473295983E56878E501EC68E25C958C3E3D2A09729FE0179F9DAC9EDCB0,
    0x1778E7166FCC6DB74E0609D307E55412D7F5E4656A8DBF25F1B33289F1B330835336E25CE3107193C5B388641D9B6861,
    0xE99726A3199F4436642B4B3E4118E5499DB995A1257FB3F086EEB65982FAC18985A286F301E77C451154CE9AC8895D9,
    0x1630C3250D7313FF01D1201BF7A74AB5DB3CB17DD952799B9ED3AB9097E68F90A0870D2DCAE73D19CD13C1C66F652983,
    0xD6ED6553FE44D296A3726C38AE652BFB11586264F0F8CE19008E218F9C86B2A8DA25128C1052ECADDD7F225A139ED84,
    0x17B81E7701ABDBE2E8743884D1117E53356DE5AB275B4DB1A682C62EF0F2753339B7C8F8C8F475AF9CCB5618E3F0C88E,
    0x80D3CF1F9A78FC47B90B33563BE990DC43B756CE79F5574A2C596C928C5D1DE4FA295F296B74E956D71986A8497E317,
    0x169B1F8E1BCFA7C42E0C37515D138F22DD2ECB803A0C5C99676314BAF4BB1B7FA3190B2EDC0327797F241067BE390C9E,
    0x10321DA079CE07E272D8EC09D2565B0DFA7DCCDDE6787F96D50AF36003B14866F69B771F8C285DECCA67DF3F1605FB7B,
    0x6E08C248E260E70BD1E962381EDEE3D31D79D7E22C837BC23C0BF1BC24C6B68C24B1B80B64D391FA9C8BA2E8BA2D229,
)
_ISO2 = (
    0x8CA8D548CFF19AE18B2E62F4BD3FA6F01D5EF4BA35B48BA9C9588617FC8AC62B558D681BE343DF8993CF9FA40D21B1C,
    0x12561A5DEB559C4348B4711298E536367041E8CA0CF0800C0126C2588C48BF5713DAA8846CB026E9E5C8276EC82B3BFF,
    0xB2962FE57A3225E8137E629BFF2991F6F89416F5A718CD1FCA64E00B11ACEACD6A3D0967C94FEDCFCC239BA5CB83E19,
    0x3425581A58AE2FEC83AAFEF7C40EB545B08243F16B1655154CCA8ABC28D6FD04976D5243EECF5C4130DE8938DC62CD8,
    0x13A8E162022914A80A6F1D5F43E7A07DFFDFC759A12062BB8D6B44E833B306DA9BD29BA81F35781D539D395B3532A21E,
    0xE7355F8E4E667B955390F7F0506C6E9395735E9CE9CAD4D0A43BCEF24B8982F7400D24BC4228F11C02DF9A29F6304A5,
    0x772CAACF16936190F3E0C63E0596721570F5799AF53A1894E2E073062AEDE9CEA73B3538F0DE06CEC2574496EE84A3A,
    0x14A7AC2A9D64A8B230B3F5B074CF01996E7F63C21BCA68A81996E1CDF9822C580FA5B9489D11E2D311F7D99BBDCC5A5E,
    0xA10ECF6ADA54F825E920B3DAFC7A3CCE07F8D1D7161366B74100DA67F39883503826692ABBA43704776EC3A79A1D641,
    0x95FC13AB9E92AD4476D6E3EB3A56680F682B4EE96F7D03776DF533978F31C1593174E4B4B7865002D6384D168ECDD0A,
)
_ISO3 = (
    0x90D97C81BA24EE0259D1F094980DCFA11AD138E48A869522B52AF6C956543D3CD0C7AEE9B3BA3C2BE9845719707BB33,
    0x134996A104EE5811D51036D776FB46831223E96C254F383D0F906343EB67AD34D6C56711962FA8BFE097E75A2E41C696,
    0xCC786BAA966E66F4A384C86A3B49942552E2D658A31CE2C344BE4B91400DA7D26D521628B00523B8DFE240C72DE1F6,
    0x1F86376E8981C217898751AD8746757D42AA7B90EEB791C09E4A3EC03251CF9DE405ABA9EC61DECA6355C77B0E5F4CB,
    0x8CC03FDEFE0FF135CAF4FE2A21529C4195536FBE3CE50B879833FD221351ADC2EE7F8DC099040A841B6DAECF2E8FEDB,
    0x16603FCA40634B6A2211E11DB8F0A6A074A7D0D4AFADB7BD76505C3D3AD5544E203F6326C95A807299B23AB13633A5F0,
    0x4AB0B9BCFAC1BBCB2C977D027796B3CE75BB8CA2BE184CB5231413C4D634F3747A87AC2460F415EC961F8855FE9D6F2,
    0x987C8D5333AB86FDE9926BD2CA6C674170A05BFE3BDD81FFD038DA6C26C842642F64550FEDFE935A15E4CA31870FB29,
    0x9FC4018BD96684BE88C9E221E4DA1BB8F3ABD16679DC26C1E8B6E6A1F20CABE69D65201C78607A360370E577BDBA587,
    0xE1BBA7A1186BDB5223ABDE7ADA14A23C42A0CA7915AF6FE06985E7ED1E4D43B9B3F7055DD4EBA6F2BAFAAEBCA731C30,
    0x19713E47937CD1BE0DFD0B8F1D43FB93CD2FCBCB6CAF493FD1183E416389E61031BF3A5CCE3FBAFCE813711AD011C132,
    0x18B46A908F36F6DEB918C143FED2EDCC523559B8AAF0C2462E6BFE7F911F643249D9CDF41B44D606CE07C8A4D0074D8E,
    0xB182CAC101B9399D155096004F53F447AA7B12A3426B08EC02710E807B4633F06C851C1919211F20D4C04F00B971EF8,
    0x245A394AD1ECA9B72FC00AE7BE315DC757B3B080D4C158013E6632D3C40659CC6CF90AD1C232A6442D9D3F5DB980133,
    0x5C129645E44CF1102A159F748C4A3FC5E673D81D7E86568D9AB0F5D396A7CE46BA1049B6579AFB7866B1E715475224B,
    0x15E6BE4E990F03CE4EA50B3B42DF2EB5CB181D8F84965A3957ADD4FA95AF01B2B665027EFEC01C7704B456BE69C8B604,
)
_ISO4 = (
    0x16112C4C3A9C98B252181140FAD0EAE9601A6DE578980BE6EEC3232B5BE72E7A07F3688EF60C206D01479253B03663C1,
    0x1962D75C2381201E1A0CBD6C43C348B885C84FF731C4D59CA4A10356F453E01F78A4260763529E3532F6102C2E49A03D,
    0x58DF3306640DA276FAAAE7D6E8EB15778C4855551AE7F310C35A5DD279CD2ECA6757CD636F96F891E2538B53DBF67F2,
    0x16B7D288798E5395F20D23BF89EDB4D1D115C5DBDDBCD30E123DA489E726AF41727364F2C28297ADA8D26D98445F5416,
    0xBE0E079545F43E4B00CC912F8228DDCC6D19C9F0F69BBB0542EDA0FC9DEC916A20B15DC0FD2EDEDDA39142311A5001D,
    0x8D9E5297186DB2D9FB266EAAC783182B70152C65550D881C5ECD87B6F0F5A6449F38DB9DFA9CCE202C6477FAAF9B7AC,
    0x166007C08A99DB2FC3BA8734ACE9824B5EECFDFA8D0CF8EF5DD365BC400A0051D5FA9C01A58B1FB93D1A1399126A775C,
    0x16A3EF08BE3EA7EA03BCDDFABBA6FF6EE5A4375EFA1F4FD7FEB34FD206357132B920F5B00801DEE460EE415A15812ED9,
    0x1866C8ED336C61231A1BE54FD1D74CC4F9FB0CE4C6AF5920ABC5750C4BF39B4852CFE2F7BB9248836B233D9D55535D4A,
    0x167A55CDA70A6E1CEA820597D94A84903216F763E13D87BB5308592E7EA7D4FBC7385EA3D529B35E346EF48BB8913F55,
    0x4D2F259EEA405BD48F010A01AD2911D9C6DD039BB61A6290E591B36E636A5C871A5C29F4F83060400F8B49CBA8F6AA8,
    0xACCBB67481D033FF5852C1E48C50C477F94FF8AEFCE42D28C0F9A88CEA7913516F968986F7EBBEA9684B529E2561092,
    0xAD6B9514C767FE3C3613144B45F1496543346D98ADF02267D5CEEF9A00D9B8693000763E3B90AC11E99B138573345CC,
    0x2660400EB2E4F3B628BDD0D53CD76F2BF565B94E72927C1CB748DF27942480E420517BD8714CC80D1FADC1326ED06F7,
    0xE0FA1D816DDC03E6B24255E0D7819C171C40F65E273B853324EFCD6356CAA205CA2F570F13497804415473A1D634B8F,
)


def _inv(a: int) -> int:
    if a % _P == 0:
        raise SeedError("BLS arithmetic: division by zero")
    return pow(a, -1, _P)


def _sqrt(a: int) -> int | None:
    """A square root mod p (p = 3 mod 4), or None."""
    y = pow(a, (_P + 1) // 4, _P)
    return y if y * y % _P == a % _P else None


class _Fq:
    """F_p[w]/(w^D + sum MOD), coefficients low to high; D = 1 is F_p."""

    __slots__ = ("c",)
    D = 1
    MOD: tuple[tuple[int, int], ...] = ()

    def __init__(self, c: Sequence[int]) -> None:
        self.c = tuple(v % _P for v in c)

    @classmethod
    def of(cls, v: int) -> Any:
        return cls((v,) + (0,) * (cls.D - 1))

    def _co(self, o: Any) -> Any:
        return o if isinstance(o, _Fq) else self.of(o)

    def __add__(self, o: Any) -> Any:
        return type(self)([a + b for a, b in zip(self.c, self._co(o).c, strict=True)])

    __radd__ = __add__

    def __sub__(self, o: Any) -> Any:
        return type(self)([a - b for a, b in zip(self.c, self._co(o).c, strict=True)])

    def __rsub__(self, o: Any) -> Any:
        return self._co(o) - self

    def __neg__(self) -> Any:
        return type(self)([-a for a in self.c])

    def __mul__(self, o: Any) -> Any:
        if isinstance(o, int):
            return type(self)([a * o for a in self.c])
        d, t = self.D, [0] * (2 * self.D - 1)
        for i, a in enumerate(self.c):
            if a:
                for j, b in enumerate(o.c):
                    t[i + j] += a * b
        for k in range(2 * d - 2, d - 1, -1):  # w^D = -sum(m_i w^i)
            if t[k]:
                for i, m in self.MOD:
                    t[k - d + i] -= t[k] * m
        return type(self)(t[:d])

    __rmul__ = __mul__

    def __eq__(self, o: object) -> bool:
        return isinstance(o, _Fq | int) and self.c == self._co(o).c

    def __hash__(self) -> int:
        return hash(self.c)

    def zero(self) -> bool:
        return not any(self.c)


class _F1(_Fq):
    pass


class _F2(_Fq):  # u^2 = -1
    D, MOD = 2, ((0, 1),)


class _F12(_Fq):  # w^12 = 2 w^6 - 2; u = w^6 - 1
    D, MOD = 12, ((0, 2), (6, -2))


_Pt = tuple[Any, Any, Any]  # homogeneous projective (X, Y, Z); Z = 0 is infinity


def _double(pt: _Pt) -> _Pt:
    x, y, z = pt
    w = 3 * x * x
    s = y * z
    b = x * y * s
    h = w * w - 8 * b
    s2 = s * s
    return 2 * h * s, w * (4 * b - h) - 8 * y * y * s2, 8 * s * s2


def _add(p1: _Pt, p2: _Pt) -> _Pt:
    if p1[2].zero():
        return p2
    if p2[2].zero():
        return p1
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    u1, u2, v1, v2 = y2 * z1, y1 * z2, x2 * z1, x1 * z2
    if v1 == v2:
        return _double(p1) if u1 == u2 else (x1 * 0 + 1, x1 * 0 + 1, x1 * 0)
    u, v = u1 - u2, v1 - v2
    v2_, w = v * v, z1 * z2
    v3, v2x = v * v2_, v2_ * v2
    a = u * u * w - v3 - 2 * v2x
    return v * a, u * (v2x - a) - v3 * u2, v3 * w


def _mul(pt: _Pt, n: int) -> _Pt:
    out = (pt[0] * 0 + 1, pt[0] * 0 + 1, pt[0] * 0)
    for bit in bin(n)[2:]:
        out = _double(out)
        if bit == "1":
            out = _add(out, pt)
    return out


def _affine1(pt: _Pt) -> tuple[int, int]:
    z = _inv(pt[2].c[0])
    return pt[0].c[0] * z % _P, pt[1].c[0] * z % _P


def _g1(x: int, y: int) -> _Pt:
    return _F1.of(x), _F1.of(y), _F1.of(1)


def _g1_from_bytes(b: bytes) -> _Pt:
    """ZCash compressed G1: curve, range and subgroup checks; infinity refused."""
    if len(b) != 48 or b[0] & 0xE0 not in (0x80, 0xA0):
        raise SeedError("BLS signature is not a compressed G1 point")
    x = int.from_bytes(bytes([b[0] & 0x1F]) + b[1:], "big")
    y = _sqrt(x**3 + 4) if x < _P else None
    if y is None:
        raise SeedError("BLS signature is not on the curve")
    if (y > (_P - 1) // 2) != bool(b[0] & 0x20):
        y = _P - y
    pt = _g1(x, y)
    if not _mul(pt, _R)[2].zero():
        raise SeedError("BLS signature is not in the G1 subgroup")
    return pt


def _f2_sqrt(a0: int, a1: int) -> tuple[int, int] | None:
    if a1 % _P == 0:
        r = _sqrt(a0)
        if r is not None:
            return r, 0
        r = _sqrt(-a0)
        return (0, r) if r is not None else None
    n = _sqrt(a0 * a0 + a1 * a1)
    if n is None:
        return None
    for d in (a0 + n, a0 - n):
        x0 = _sqrt(d * _inv(2))
        if x0:
            x1 = a1 * _inv(2 * x0) % _P
            if ((x0 * x0 - x1 * x1) % _P, 2 * x0 * x1 % _P) == (a0 % _P, a1 % _P):
                return x0, x1
    return None


def _g2_from_bytes(b: bytes) -> _Pt:
    """ZCash compressed G2 (c1 then c0): curve, range and subgroup checks."""
    if len(b) != 96 or b[0] & 0xE0 not in (0x80, 0xA0):
        raise SeedError("BLS public key is not a compressed G2 point")
    x1 = int.from_bytes(bytes([b[0] & 0x1F]) + b[1:48], "big")
    x0 = int.from_bytes(b[48:], "big")
    if x0 >= _P or x1 >= _P:
        raise SeedError("BLS public key is out of range")
    x = _F2((x0, x1))
    rhs = x * x * x + _F2((4, 4))
    y = _f2_sqrt(*rhs.c)
    if y is None:
        raise SeedError("BLS public key is not on the curve")
    big = (y[1] if y[1] else y[0]) > (_P - 1) // 2
    if big != bool(b[0] & 0x20):
        y = ((_P - y[0]) % _P, (_P - y[1]) % _P)
    pt = (x, _F2(y), _F2.of(1))
    if not _mul(pt, _R)[2].zero():
        raise SeedError("BLS public key is not in the G2 subgroup")
    return pt


def _expand_xmd(msg: bytes, dst: bytes, n: int) -> bytes:
    """RFC 9380 §5.3.1 expand_message_xmd with SHA-256."""
    ell = -(-n // 32)
    if len(dst) > 255 or ell > 255:
        raise SeedError("expand_message_xmd: bad lengths")
    dst_p = dst + bytes([len(dst)])
    b0 = hashlib.sha256(bytes(64) + msg + n.to_bytes(2, "big") + b"\0" + dst_p).digest()
    out = [hashlib.sha256(b0 + b"\x01" + dst_p).digest()]
    for i in range(2, ell + 1):
        mixed = bytes(a ^ c for a, c in zip(b0, out[-1], strict=True))
        out.append(hashlib.sha256(mixed + bytes([i]) + dst_p).digest())
    return b"".join(out)[:n]


def _sswu(u: int) -> tuple[int, int]:
    """RFC 9380 §6.6.2 simplified SWU onto E' (A', B', Z = 11)."""
    a, b, z = _A_ISO, _B_ISO, _Z_ISO
    tv1 = (z * z * pow(u, 4, _P) + z * u * u) % _P
    if tv1 == 0:
        x1 = b * _inv(z * a) % _P
    else:
        x1 = -b * _inv(a) * (1 + _inv(tv1)) % _P
    y = _sqrt(x1**3 + a * x1 + b)
    x = x1
    if y is None:
        x = z * u * u * x1 % _P
        y = _sqrt(x**3 + a * x + b)
        if y is None:  # impossible for a correct map; refuse rather than guess
            raise SeedError("simplified SWU found no square")
    if u % 2 != y % 2:
        y = _P - y
    return x, y


def _poly(coeffs: Sequence[int], x: int) -> int:
    acc = 0
    for c in reversed(coeffs):
        acc = (acc * x + c) % _P
    return acc


def _iso_map(x: int, y: int) -> _Pt:
    """RFC 9380 Appendix E.2, the 11-isogeny E' -> E."""
    xd = _poly((*_ISO2, 1), x)
    yd = _poly((*_ISO4, 1), x)
    if xd == 0 or yd == 0:
        return _F1.of(1), _F1.of(1), _F1.of(0)
    return _g1(_poly(_ISO1, x) * _inv(xd) % _P, y * _poly(_ISO3, x) * _inv(yd) % _P)


def _hash_to_g1(msg: bytes, dst: bytes = _DST) -> _Pt:
    """RFC 9380 §3 hash_to_curve, suite BLS12381G1_XMD:SHA-256_SSWU_RO_."""
    uniform = _expand_xmd(msg, dst, 128)
    q0 = _iso_map(*_sswu(int.from_bytes(uniform[:64], "big") % _P))
    q1 = _iso_map(*_sswu(int.from_bytes(uniform[64:], "big") % _P))
    return _mul(_add(q0, q1), _H_EFF)


def _twist(pt: _Pt) -> _Pt:
    """G2 (y^2 = x^3 + 4(1 + u)) into E(F_p12) (y^2 = x^3 + 4): u -> w^6 - 1, so
    1 + u = w^6, and (x, y) -> (x / w^2, y / w^3)."""

    def lift(e: _F2) -> _F12:
        return _F12((e.c[0] - e.c[1], 0, 0, 0, 0, 0, e.c[1], 0, 0, 0, 0, 0))

    w_inv = _F12((0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, -_inv(2)))  # w^11 = 2w^5 - 2/w
    w_inv2 = w_inv * w_inv
    x, y, z = pt
    return lift(x) * w_inv2, lift(y) * w_inv2 * w_inv, lift(z)


def _line(p1: _Pt, p2: _Pt, t: _Pt) -> tuple[_F12, _F12]:
    """The line through p1 and p2 (tangent if equal) at t, as numerator, denominator."""
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    xt, yt, zt = t
    num, den = y2 * z1 - y1 * z2, x2 * z1 - x1 * z2
    if den.zero():
        if not num.zero():  # vertical
            return xt * z1 - x1 * zt, z1 * zt
        num, den = 3 * x1 * x1, 2 * y1 * z1
    return num * (xt * z1 - x1 * zt) - den * (yt * z1 - y1 * zt), den * zt * z1


def _miller(q: _Pt, p: _Pt) -> tuple[_F12, _F12]:
    """Miller loop f_{|x|,Q}(P) as numerator, denominator (Q twisted, P lifted)."""
    r, fn, fd = q, _F12.of(1), _F12.of(1)
    for bit in bin(_X_ABS)[3:]:
        n, d = _line(r, r, p)
        fn, fd, r = fn * fn * n, fd * fd * d, _double(r)
        if bit == "1":
            n, d = _line(r, q, p)
            fn, fd, r = fn * n, fd * d, _add(r, q)
    return fn, fd


def _pow12(a: _F12, e: int) -> _F12:
    out: _F12 = _F12.of(1)
    for bit in bin(e)[2:]:
        out = out * out
        if bit == "1":
            out = out * a
    return out


def _lift1(pt: _Pt) -> _Pt:
    x, y = _affine1(pt)
    return _F12.of(x), _F12.of(y), _F12.of(1)


def bls_verify(public_key: str, round_: int, signature: str) -> bool:
    """True iff `signature` verifies for drand round `round_` under `public_key`
    (scheme SCHEME). Malformed points raise SeedError."""
    sig = _g1_from_bytes(bytes.fromhex(signature))
    key = _g2_from_bytes(bytes.fromhex(public_key))
    h = _hash_to_g1(hashlib.sha256(round_.to_bytes(8, "big")).digest())
    if h[2].zero():
        raise SeedError("hash to G1 gave the point at infinity")
    neg_g2 = (_F2(_G2_X), -_F2(_G2_Y), _F2.of(1))
    # e(sig, -g2) * e(H(m), key) == 1; numerator and denominator kept apart so no
    # F_p12 inverse is needed: (n1 n2)^E == (d1 d2)^E, E = (p^12 - 1) / r.
    n1, d1 = _miller(_twist(neg_g2), _lift1(sig))
    n2, d2 = _miller(_twist(key), _lift1(h))
    num, den = n1 * n2, d1 * d2
    if num.zero() or den.zero():
        raise SeedError("BLS pairing degenerated")
    e = (_P**12 - 1) // _R
    return _pow12(num, e) == _pow12(den, e)


def beacon_round(capture_cdx: str, chain: Chain) -> int:
    """seed_disclosure `round`: the first round whose scheduled time is at least
    T + 24h, T the 14-digit UTC CDX timestamp; drand schedules round r at
    genesis_time + (r - 1) * period."""
    if not (
        isinstance(capture_cdx, str)
        and len(capture_cdx) == 14
        and capture_cdx.isdigit()
    ):
        raise SeedError(f"capture timestamp {capture_cdx!r} is not 14 CDX digits")
    if (
        type(chain.genesis_time) is not int
        or type(chain.period) is not int
        or chain.period <= 0
    ):
        raise SeedError("chain genesis time and period must be integers, period > 0")
    try:
        t = datetime.strptime(capture_cdx, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
    except ValueError:
        raise SeedError(
            f"capture timestamp {capture_cdx!r} is not a UTC time"
        ) from None
    target = int(t.timestamp()) + 86_400
    if target <= chain.genesis_time:
        return 1
    return 1 + -(-(target - chain.genesis_time) // chain.period)  # ceiling division


def check_beacon(beacon: Beacon, round_: int, chain: Chain) -> None:
    """seed_disclosure `verification`: the beacon is the fixed round, its
    randomness is SHA-256 of its signature (drand's definition), and its
    signature verifies against the chain key, checked here by bls_verify
    (R-14a item 7). Anything else is a seed failure."""
    if chain.scheme != SCHEME:
        raise SeedError(f"chain scheme {chain.scheme!r} is not {SCHEME}")
    if type(beacon.round) is not int or beacon.round != round_:
        raise SeedError(
            f"beacon round {beacon.round!r} is not the fixed round {round_}"
        )
    if not (
        _hex(beacon.randomness, 64)
        and _hex(beacon.signature)
        and _hex(chain.public_key)
    ):
        raise SeedError(
            "beacon randomness, signature or chain key is not lowercase hex"
        )
    if hashlib.sha256(bytes.fromhex(beacon.signature)).hexdigest() != beacon.randomness:
        raise SeedError("beacon randomness is not SHA-256 of its signature")
    if not bls_verify(chain.public_key, beacon.round, beacon.signature):
        raise SeedError("beacon signature does not verify against the chain key")


def annex_b_seed(
    *,
    protocol_hash: str,
    family: str,
    cycle_id: str,
    window_id: str,
    data_manifest_hash: str,
    trials: list[dict[str, Any]],
) -> str:
    """Annex B §2.4: SHA-256 of the canonical JSON of these fields, `trials` in
    declared trial-id order, each {trial_id, hypothesis_hash, configuration_hash}."""
    keys = ("trial_id", "hypothesis_hash", "configuration_hash")
    return sha(
        {
            "cycle_id": cycle_id,
            "data_manifest_hash": data_manifest_hash,
            "family_id": family,
            "protocol_hash": protocol_hash,
            "trials": [{k: t[k] for k in keys} for t in trials],
            "window_id": window_id,
        }
    )


def beacon_family_seed(annex_b: str, beacon: Beacon) -> str:
    """R-7 (owner decision D20/D13, B2): family_seed_f =
    SHA256(cj({annex_b_seed, beacon_randomness, round})); all three validated
    before hashing."""
    if not (_hex(annex_b, 64) and _hex(beacon.randomness, 64)):
        raise SeedError("annex_b_seed and beacon_randomness must be 64 lowercase hex")
    if type(beacon.round) is not int or beacon.round < 1:
        raise SeedError("round must be a positive integer")
    return sha(
        {
            "annex_b_seed": annex_b,
            "beacon_randomness": beacon.randomness,
            "round": beacon.round,
        }
    )


_RECORD_FIELDS = frozenset(
    {"trial_id", "hypothesis_hash", "configuration_hash", "trial_index"}
)


def _check_records(
    family: str, trials: list[dict[str, Any]], records: list[dict[str, Any]]
) -> None:
    """Each declared trial has exactly one immutable C2 trial record, in the
    declared order, whose configuration hash is the trial object's."""
    if not all(isinstance(r, dict) and set(r) == _RECORD_FIELDS for r in records):
        raise SeedError(f"{family}: trial record fields")
    if [r["trial_id"] for r in records] != [t["trial_id"] for t in trials]:
        raise SeedError(
            f"{family}: trial records do not match the declared trials in order"
        )
    ids = [r["trial_id"] for r in records]
    # a duplicate would silently drop a seed (P18-1, Constitution §27; R14S4-S-2)
    if len(set(ids)) != len(ids):
        raise SeedError(f"{family}: trial_id must be distinct")
    indices = [r["trial_index"] for r in records]
    if any(type(i) is not int or i < 0 for i in indices) or len(set(indices)) != len(
        indices
    ):
        raise SeedError(f"{family}: trial_index must be distinct non-negative integers")
    for t, r in zip(trials, records, strict=True):
        if not _hex(r["hypothesis_hash"], 64):
            raise SeedError(f"{t['trial_id']}: hypothesis_hash is not 64 lowercase hex")
        if r["configuration_hash"] != screen.trial_sha256(t):
            raise SeedError(
                f"{t['trial_id']}: configuration_hash is not the trial object's"
            )


def derive_seeds(
    *,
    declared: dict[str, list[dict[str, Any]]],
    records: dict[str, list[dict[str, Any]]],
    protocol_hash: str,
    cycle_id: str,
    window_id: str,
    data_manifest_hash: str,
    beacon: Beacon,
    capture_cdx: str,
    chain: Chain,
) -> dict[str, Any]:
    """DESIGN §5.1, step 3: every seed of the evaluation, verified from the
    governing records, with its provenance (Constitution §27). Raises
    SeedError on any failure: the evaluation is invalid and no gate runs."""
    if not (_hex(protocol_hash, 64) and _hex(data_manifest_hash, 64)):
        raise SeedError("protocol_hash and data_manifest_hash must be 64 lowercase hex")
    if set(records) != set(declared):
        raise SeedError("trial records are not for exactly the declared families")
    round_ = beacon_round(capture_cdx, chain)
    check_beacon(beacon, round_, chain)
    line266 = _TRIAL_SEED
    if line266 is None:
        raise SeedError("line 266 is not loaded: call load_line266 before any read")
    families: dict[str, Any] = {}
    for family, trials in declared.items():
        recs = records[family]
        _check_records(family, trials, recs)
        annex_b = annex_b_seed(
            protocol_hash=protocol_hash,
            family=family,
            cycle_id=cycle_id,
            window_id=window_id,
            data_manifest_hash=data_manifest_hash,
            trials=recs,
        )
        f_seed = beacon_family_seed(annex_b, beacon)
        trial_seeds = seeds_record(f_seed, [r["trial_id"] for r in recs])
        per_trial: dict[str, Any] = {}
        for r in recs:
            try:  # protocol line 266, unchanged for the nominee's fit (R-13)
                seed_l266 = line266(
                    protocol_hash=protocol_hash,
                    hypothesis_hash=r["hypothesis_hash"],
                    trial_index=r["trial_index"],
                )
            except Exception as e:
                raise SeedError(f"line-266 seed failed: {type(e).__name__}") from None
            if not _hex(seed_l266, 64):
                raise SeedError(
                    f"{r['trial_id']}: line-266 seed is not 64 lowercase hex"
                )
            per_trial[r["trial_id"]] = {
                "trial_index": r["trial_index"],
                "trial_seed": trial_seeds[
                    r["trial_id"]
                ],  # R-13: G-1, G-11, G-14 streams
                "seed_l266": seed_l266,
                "estimator_seed_policy": POLICY,
                "estimator_seed": screen.estimator_seed(seed_l266),  # 0 valid (D20L-44)
            }
        families[family] = {
            "annex_b_seed": annex_b,
            "family_seed": f_seed,
            "trials": per_trial,
        }
    return {
        "beacon": {
            "chain_public_key": chain.public_key,
            "capture_cdx": capture_cdx,
            "round": beacon.round,
            "randomness": beacon.randomness,
            "signature": beacon.signature,
        },
        "inputs": {
            "protocol_hash": protocol_hash,
            "cycle_id": cycle_id,
            "window_id": window_id,
            "data_manifest_hash": data_manifest_hash,
        },
        "families": families,
    }
