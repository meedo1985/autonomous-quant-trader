"""Semi-empirical market of prereg §3.4 (Q5, QJ): the parts that do not
depend on the trend and vol rule libraries (engine item 2b).

1. Source: demeaned daily BTC and ETH returns of the **exploration
   partition only** (`exploration_returns`). Bars are read only by
   `aqt.data.klines.build_exploration_manifest`, which refuses every other
   partition before a file is read, opens only the exploration months'
   archives (each checked against its sidecar) and keeps only bars inside
   the exploration window; the two manifest hashes are returned for the
   qualification object (§3.4 item 1).
2. Path: a joint stationary bootstrap (mean block 20; 60 for the §3.4
   sensitivity rerun) of those rows, from the `"market"` stream.
3. Exposures: computed causally on the resampled BTC path by the rule
   library, which is passed in (`exposures`), with a warm-up before day 0.
4. Columns: raw X~_j = (e_j - e^b) r with e^b the §3.1 benchmark stand-in;
   every geometric block of mean 20 gets one iid fair sign from the
   `"sign"` stream, the first block starting at day 0, shared by all
   columns (and both families in QJ); X = s X~, C = b + X, so E[X] = 0.

PENDING: the daily-return rule (`daily_closes`, `joint_returns`) and
the rule libraries are part of the rule-library proposal
(`review/d19-engine/ITEM2B_RULE_LIBRARY_PROPOSAL.md`), which needs reviews
and the owner's decision before any Q5/QJ cell is run."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

from aqt.data.bars import BarSeries
from aqt.data.klines import (
    EXPLORATION,
    WINDOW_END_EXCLUSIVE,
    WINDOW_START,
    build_exploration_manifest,
)
from calibration.generator import Legs, benchmark_exposure

SYMBOLS = ("BTCUSDT", "ETHUSDT")
HOURS_PER_DAY = 24
MEAN_BLOCK = 20  # §3.4; the sensitivity rerun uses 60

# exposures(path) -> (rows of path) x K exposures. Row t is the exposure
# held on day t, which earns r_t; it is decided at the close of day t - 1
# and may use only rows < t of the path (columns: BTC, ETH daily simple
# returns). Each library must be tested for this prefix invariance.
Exposures = Callable[[np.ndarray], np.ndarray]


def daily_closes(series: BarSeries) -> dict[date, float]:
    """The 23:00 UTC close of every complete UTC day (all 24 hourly bars
    present). Incomplete days are left out, never filled (Constitution §6)."""
    hours: dict[date, int] = {}
    closes: dict[date, float] = {}
    for bar in series.bars:
        day = bar.open_time.date()
        hours[day] = hours.get(day, 0) + 1
        if bar.open_time.hour == HOURS_PER_DAY - 1:
            closes[day] = bar.close
    return {d: c for d, c in closes.items() if hours[d] == HOURS_PER_DAY}


def exploration_returns(
    raw_root: Path,
) -> tuple[np.ndarray, tuple[str, ...], tuple[date, ...]]:
    """The demeaned (BTC, ETH) daily returns of the exploration partition,
    the two manifest hashes, and the left-out return days (`joint_returns`)."""
    builds = [build_exploration_manifest(EXPLORATION, s, raw_root) for s in SYMBOLS]
    returns, left_out = joint_returns(
        [b.series for b in builds], WINDOW_START, WINDOW_END_EXCLUSIVE
    )
    return returns, tuple(b.manifest.manifest_sha256 for b in builds), left_out


@dataclass(frozen=True)
class Source:
    """The demeaned (BTC, ETH) daily returns and their identity, which the
    run definition records and every worker re-checks (§3.4 item 1)."""

    returns: np.ndarray
    identity: dict[str, object]


def load_source(raw_root: Path) -> Source:
    returns, hashes, left_out = exploration_returns(raw_root)
    data = np.ascontiguousarray(returns, dtype="<f8").tobytes()
    identity: dict[str, object] = {
        "manifest_sha256": dict(zip(SYMBOLS, hashes, strict=True)),
        "returns_sha256": hashlib.sha256(data).hexdigest(),
        "rows": len(returns),
        "left_out_days": len(left_out),
    }
    return Source(returns, identity)


def joint_returns(
    series: list[BarSeries], start: datetime, end_exclusive: datetime
) -> tuple[np.ndarray, tuple[date, ...]]:
    """Demeaned daily simple returns, one column per series in `SYMBOLS`
    order, for every return day d of the window: d - 1 and d both lie in
    [start, end_exclusive) as whole UTC days. Day d is kept only when d and
    d - 1 are complete for every series; every other return day of the
    window is left out, never filled, and listed (the first window day has
    no predecessor and is not a return day). Kept rows are adjacent in the
    array even across a left-out day, as across the bootstrap's wrap."""
    if [s.symbol for s in series] != list(SYMBOLS):
        raise ValueError(f"need the series of {SYMBOLS} in that order")
    first, last = start.date(), (end_exclusive - timedelta(days=1)).date()
    whole = all(
        m.utcoffset() == timedelta(0) and not m.timestamp() % 86_400
        for m in (start, end_exclusive)
    )
    if not whole or first >= last:
        raise ValueError("the window must be at least two whole UTC days")
    closes = [daily_closes(s) for s in series]
    rows, left_out = [], []
    for n in range(1, (last - first).days + 1):
        d = first + timedelta(days=n)
        if all(d in c and d - timedelta(days=1) in c for c in closes):
            rows.append([c[d] / c[d - timedelta(days=1)] - 1 for c in closes])
        else:
            left_out.append(d)
    if len(rows) < 2:
        raise ValueError("too few complete consecutive days")
    returns = np.asarray(rows, dtype=float)
    return returns - returns.mean(axis=0), tuple(left_out)


def stationary_indices(
    rng: np.random.Generator, n_source: int, n: int, mean_block: int
) -> np.ndarray:
    """Politis-Romano stationary bootstrap: a uniform start, then each day
    restarts uniformly with probability 1/mean_block or moves to the next
    source row (wrapping). Draw order: one uniform start, then per day one
    uniform test and, on a restart, one uniform index."""
    out = np.empty(n, dtype=np.int64)
    out[0] = rng.integers(n_source)
    for i in range(1, n):
        if rng.random() < 1 / mean_block:
            out[i] = rng.integers(n_source)
        else:
            out[i] = (out[i - 1] + 1) % n_source
    return out


def block_signs(rng: np.random.Generator, n: int, mean_block: int) -> np.ndarray:
    """One iid fair +-1 per geometric block (mean length mean_block, at
    least 1), the first block starting at day 0. Draw order per block: the
    sign, then the length."""
    out = np.empty(n)
    day = 0
    while day < n:
        sign = 1.0 if rng.random() < 0.5 else -1.0
        length = int(rng.geometric(1 / mean_block))
        out[day : day + length] = sign
        day += length
    return out


def semi_empirical(
    source: np.ndarray,
    exposures: Exposures,
    market: np.random.Generator,
    sign: np.random.Generator,
    t: int,
    warmup: int,
    mean_block: int = MEAN_BLOCK,
) -> Legs:
    """One §3.4 replication: T days after `warmup` days of rule history."""
    path = source[stationary_indices(market, len(source), warmup + t, mean_block)]
    e = np.asarray(exposures(path), dtype=float)
    if e.ndim != 2 or e.shape[0] != warmup + t:
        raise ValueError("exposures must have one row per path day")
    r_all = path[:, 0]
    e_b = benchmark_exposure(r_all)[warmup:]
    r = r_all[warmup:]
    raw = (e[warmup:] - e_b[:, None]) * r[:, None]
    x = block_signs(sign, t, mean_block)[:, None] * raw
    benchmark = e_b * r
    return Legs(x, benchmark, benchmark[:, None] + x)
