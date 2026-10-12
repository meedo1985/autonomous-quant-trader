"""The C2 gap `g` of the §4 draft's `gap_embargo.rule`, from exploration
data only (preregistration §3.1: `T_C2 = 1247 - g`, fixed before the
threshold run).

`gap_embargo.rule`: "ceiling, in whole days, of the maximum over declared
horizons of max(label_horizon, target_autocorr_cutoff)". The horizons are
all three of `protocol_v1.yaml` `target.horizons_hours` (owner decision,
`review/d19-engine/OWNER_DECISION_GAP_HORIZONS.md`). The cutoff is the
frozen protocol's `validation.embargo`: the ACF of the target sampled at
the daily decision frequency, Bartlett bands at alpha 0.05, lags up to
4 * horizon in daily steps, "first lag after which no remaining lag is
significant".

Readings (proposed, for review; recorded in `ITEM_GAP_RULE.md`):
- G-1 Data: BTCUSDT bars of the exploration partition, read only through
  `build_exploration_manifest` (it refuses every other partition).
- G-2 Target (`target.formula`): log(P[t+H]/P[t]) / (sigma_t * sqrt(H)),
  `P` the hourly close and sigma_t the trailing EWMA hourly volatility
  (168 h half-life, `specs/COST_MODEL_v1.md`, reused from
  `aqt.backtest.costs`) of the 1-hour log returns up to `t`. A return
  exists only between consecutive hourly bars; nothing is filled.
- G-3 Daily decision time: the close of the 23:00 UTC bar, as
  `semi.daily_closes`. A day has a target only if its bar, the bar H hours
  later and sigma_t exist; other days are missing, never filled.
- G-4 ACF: over the calendar days from the first to the last target, with
  the mean and variance of the present targets; r_k sums only pairs where
  both days are present. Bartlett: se_k = sqrt((1 + 2 sum_{j<k} r_j^2) / n),
  n the number of present targets; lag k is significant if
  |r_k| > z_{0.975} se_k.
- G-5 Cutoff: the largest significant lag in 1..max_lag, or 0 if none.
  The gap of a horizon is max(H / 24, cutoff) days; `g` is the largest."""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from math import fsum
from statistics import NormalDist

from aqt.backtest.costs import ewma_hourly_volatility_bps_series
from aqt.data.bars import BarSeries

HORIZONS_HOURS = (24, 72, 168)  # owner decision on the gap horizons
ALPHA = 0.05  # validation.embargo.alpha
LAG_FACTOR = 4  # validation.embargo.max_lag: 4 * horizon in daily steps
DECISION_HOUR = 23  # G-3
Z = NormalDist().inv_cdf(1 - ALPHA / 2)
_HOUR = timedelta(hours=1)
_BPS = 1e4


def hourly_volatility(series: BarSeries) -> dict[datetime, float]:
    """sigma_t (log-return units) at each bar open time `t` whose estimate
    uses the 1-hour log returns up to that bar's close (G-2)."""
    closes = {b.open_time: b.close for b in series.bars}
    times = [t for t in sorted(closes) if t - _HOUR in closes]
    returns = [math.log(closes[t] / closes[t - _HOUR]) * _BPS for t in times]
    if len(returns) < 2:
        return {}
    estimates = ewma_hourly_volatility_bps_series(returns)
    return {t: s / _BPS for t, s in zip(times[1:], estimates, strict=True)}


def daily_targets(series: BarSeries, horizon: int) -> dict[date, float]:
    """The target of each day with a decision bar, the bar `horizon` hours
    later and a positive sigma_t (G-2, G-3)."""
    closes = {b.open_time: b.close for b in series.bars}
    sigma = hourly_volatility(series)
    out = {}
    for t, price in closes.items():
        later = closes.get(t + horizon * _HOUR)
        s = sigma.get(t, 0.0)
        if t.hour == DECISION_HOUR and later is not None and s > 0:
            out[t.date()] = math.log(later / price) / (s * math.sqrt(horizon))
    return out


def acf(values: list[float | None], max_lag: int) -> list[float]:
    """r_1..r_max_lag over a daily sequence with missing days (G-4)."""
    present = [v for v in values if v is not None]
    mean = fsum(present) / len(present)
    denominator = fsum((v - mean) ** 2 for v in present)
    return [
        fsum(
            (a - mean) * (b - mean)
            for a, b in zip(values, values[k:], strict=False)
            if a is not None and b is not None
        )
        / denominator
        for k in range(1, max_lag + 1)
    ]


def cutoff(r: list[float], n: int) -> int:
    """The largest lag significant under Bartlett bands, or 0 (G-4, G-5)."""
    significant = [
        k
        for k in range(1, len(r) + 1)
        if abs(r[k - 1]) > Z * math.sqrt((1 + 2 * fsum(x * x for x in r[: k - 1])) / n)
    ]
    return max(significant, default=0)


def gap(series: BarSeries) -> dict[str, object]:
    """Per horizon: present targets, max lag, cutoff and gap in days; and
    `g`, the largest gap."""
    horizons: dict[str, dict[str, object]] = {}
    gaps: list[int] = []
    for h in HORIZONS_HOURS:
        targets = daily_targets(series, h)
        first, last = min(targets), max(targets)
        days = [first + timedelta(d) for d in range((last - first).days + 1)]
        days_h = h // 24
        max_lag = LAG_FACTOR * days_h
        lag = cutoff(acf([targets.get(d) for d in days], max_lag), len(targets))
        gaps.append(max(days_h, lag))
        horizons[f"{h}h"] = {
            "targets": len(targets),
            "first": first.isoformat(),
            "last": last.isoformat(),
            "max_lag": max_lag,
            "cutoff": lag,
            "gap_days": gaps[-1],
        }
    return {"horizons": horizons, "g": math.ceil(max(gaps))}
