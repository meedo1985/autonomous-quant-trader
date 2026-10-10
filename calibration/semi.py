"""Semi-empirical market of prereg §3.4 (Q5, QJ): the parts that do not
depend on the trend and vol rule libraries (engine item 2b).

1. Source: demeaned daily BTC and ETH returns of the **exploration
   partition only** (`exploration_returns`), refused before any bar is read
   unless both manifests are exploration manifests inside the protocol's
   exploration window, and checked against their parsed hashes after.
2. Path: a joint stationary bootstrap (mean block 20; 60 for the §3.4
   sensitivity rerun) of those rows, from the `"market"` stream.
3. Exposures: computed causally on the resampled BTC path by the rule
   library, which is passed in (`exposures`), with a warm-up before day 0.
4. Columns: raw X~_j = (e_j - e^b) r with e^b the §3.1 benchmark stand-in;
   every geometric block of mean 20 gets one iid fair sign from the
   `"sign"` stream, the first block starting at day 0, shared by all
   columns (and both families in QJ); X = s X~, C = b + X, so E[X] = 0.

PENDING: the daily-return rule (`daily_closes`, `exploration_returns`) and
the rule libraries are part of the rule-library proposal
(`review/d19-engine/ITEM2B_RULE_LIBRARY_PROPOSAL.md`), which needs reviews
and the owner's decision before any Q5/QJ cell is run."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, timedelta

import numpy as np

from aqt.data.bars import BarSeries
from aqt.data.klines import WINDOW_END_EXCLUSIVE, WINDOW_START
from aqt.data.manifest import PartitionManifest, verify_partition_manifest
from calibration.generator import Legs, benchmark_exposure

SYMBOLS = ("BTCUSDT", "ETHUSDT")
HOURS_PER_DAY = 24
MEAN_BLOCK = 20  # §3.4; the sensitivity rerun uses 60

# exposures(path) -> (rows of path) x K exposures, causal: row t uses only
# rows <= t of the path (columns: BTC, ETH daily simple returns).
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
    manifests: dict[str, PartitionManifest],
    load: Callable[[PartitionManifest], BarSeries],
) -> tuple[np.ndarray, int]:
    """Demeaned daily (BTC, ETH) simple returns for every day d whose close
    and the previous day's close are complete for both symbols, and the
    number of calendar days left out. Refuses any manifest that is not an
    exploration manifest inside the exploration window, before reading."""
    if set(manifests) != set(SYMBOLS):
        raise ValueError(f"need exactly the manifests of {SYMBOLS}")
    for symbol, manifest in manifests.items():
        if manifest.partition != "exploration" or manifest.symbol != symbol:
            raise ValueError(f"{symbol}: not an exploration manifest of {symbol}")
        if (
            manifest.window_start_utc < WINDOW_START
            or manifest.window_end_exclusive_utc > WINDOW_END_EXCLUSIVE
        ):
            raise ValueError(f"{symbol}: manifest window leaves the exploration window")
    closes = []
    for symbol in SYMBOLS:
        series = load(manifests[symbol])
        verify_partition_manifest(manifests[symbol], series=series)
        closes.append(daily_closes(series))
    days = sorted(set(closes[0]) & set(closes[1]))
    rows = [
        [c[d] / c[d - timedelta(days=1)] - 1 for c in closes]
        for d in days
        if all(d - timedelta(days=1) in c for c in closes)
    ]
    if len(rows) < 2:
        raise ValueError("too few complete consecutive days")
    span = (days[-1] - days[0]).days if days else 0
    returns = np.asarray(rows, dtype=float)
    return returns - returns.mean(axis=0), span - len(rows)


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
