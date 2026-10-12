# ruff: noqa
"""GAP-1..4 sensitivity: g under alternative readings (run from the repository root: python review/d19-engine/gap_sensitivity.py). Exploration data only, through build_exploration_manifest."""

import math, sys, itertools
from datetime import timedelta
from math import fsum

sys.path[:0] = [".", "src"]
from pathlib import Path
from aqt.data.klines import EXPLORATION, build_exploration_manifest
from aqt.backtest import costs
from calibration import gap

b = build_exploration_manifest(EXPLORATION, "BTCUSDT", Path("data/raw"))
print(
    "missing archives:", b.missing_archives if hasattr(b, "missing_archives") else "n/a"
)
series = b.series
H = timedelta(hours=1)
closes = {x.open_time: x.close for x in series.bars}
decay = 0.5 ** (1 / 168)


def vol_time_aware():
    times = [t for t in sorted(closes) if t - H in closes]
    rets = [math.log(closes[t] / closes[t - H]) for t in times]
    out, var, prev = {}, None, None
    for k, (t, r) in enumerate(zip(times, rets)):
        if k + 1 <= 168:
            if k >= 1:
                m = fsum(rets[: k + 1]) / (k + 1)
                var = fsum((x - m) ** 2 for x in rets[: k + 1]) / k
        else:
            dt = round((t - prev) / H)
            var = decay**dt * var + (1 - decay) * r * r
        prev = t
        if var is not None:
            out[t] = math.sqrt(var)
    return out


def targets(sigma, h, hour):
    o = {}
    for t, p in closes.items():
        later = closes.get(t + h * H)
        s = sigma.get(t, 0.0)
        if t.hour == hour and later is not None and s > 0:
            o[t.date()] = math.log(later / p) / (s * math.sqrt(h))
    return o


def acf_pairs(values, max_lag):
    present = [v for v in values if v is not None]
    n = len(present)
    mean = fsum(present) / n
    den = fsum((v - mean) ** 2 for v in present)
    r, npairs = [], []
    for k in range(1, max_lag + 1):
        pr = [
            (a, c)
            for a, c in zip(values, values[k:])
            if a is not None and c is not None
        ]
        r.append(fsum((a - mean) * (c - mean) for a, c in pr) / den)
        npairs.append(len(pr))
    return r, npairs, n


def cut(r, ns, tail):
    sig = [
        k
        for k in range(1, len(r) + 1)
        if abs(r[k - 1])
        > gap.Z * math.sqrt((1 + 2 * fsum(x * x for x in r[: k - 1])) / ns[k - 1])
    ]
    L = max(sig, default=0)
    return L + 1 if (tail and L) else L


sig_base = gap.hourly_volatility(series)
sig_ta = vol_time_aware()
rows = {}
for vol, bandn, tail, hour in itertools.product(
    ("obs", "time"), ("all", "pairs"), (False, True), range(24)
):
    sigma = sig_base if vol == "obs" else sig_ta
    gaps = []
    for h in gap.HORIZONS_HOURS:
        tg = targets(sigma, h, hour)
        first, last = min(tg), max(tg)
        days = [first + timedelta(d) for d in range((last - first).days + 1)]
        r, npairs, n = acf_pairs([tg.get(d) for d in days], 4 * (h // 24))
        ns = [n] * len(r) if bandn == "all" else npairs
        gaps.append(max(h // 24, cut(r, ns, tail)))
    rows[(vol, bandn, tail, hour)] = (max(gaps), gaps)
print("base (obs, all, last, 23):", rows[("obs", "all", False, 23)])
for key in [
    (v, bn, t)
    for v in ("obs", "time")
    for bn in ("all", "pairs")
    for t in (False, True)
]:
    gs = [rows[key + (hr,)][0] for hr in range(24)]
    print(
        key,
        "g at 23:",
        rows[key + (23,)],
        " g over hours 0-23: min",
        min(gs),
        "max",
        max(gs),
        "counts",
        {x: gs.count(x) for x in sorted(set(gs))},
    )
