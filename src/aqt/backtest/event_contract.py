"""The C2 event contract of Annex C C-6 (screen slice S2, D-19).

Status: implements `review/governance-statistics-amendment/s4-amendment-draft/
ANNEX_C_GATE_DEFINITIONS.md` revision 4, C-6, an AI wording proposal that is
NOT ACTIVE. Nothing in the paper app or the Cycle-1 backtester
(`aqt.backtest.engine`) calls this module; the D-19 screen does
(`calibration/screen.py`). It is bound by the engine commit of the D-19 run
definition only if merged before that definition is recorded
(`review/d19-engine/SCREEN_PLAN.md` section 3).

Time is a sequence of hourly instants `j`, the open of bar `j`, equal to the
close of bar `j - 1` (C-6 (1)). The decision at instant `j` sees closes
through bar `j - 1` and stores an absolute target exposure. The exposure held
after instant `j`'s fills earns bar `j`'s open-to-next-open return. At each
instant, in order (C-6 (4)):

1. A due order (decided at `j - 1` under execution delay) fills at `open_j`.
2. The decision is evaluated against held exposure `held` (C-6 (4.2)):
   - its direction is fixed now: increase if target > held, reduction if
     target < held;
   - an increase needs a 00:00 UTC instant, a clock that is unset or at least
     24 h old, and `reaches_rebalance_band(target - held)`;
   - a reduction needs `reaches_rebalance_band(target - held)` at any hour,
     except that a reduction to target 0 is never blocked by the band.
3. A passing decision is an order. At baseline it fills now at `open_j`;
   under execution delay (G-7) it is due at `j + 1`.
4. An order still unfilled at the window end is dropped.

Fills (C-6 (2), (5)): a reduction fills at `min(target, held at fill)`; an
increase fills as ordered. A fill updates exposure and equity together, and
costs `|new - held|` at the frozen cost model: sigma from the returns
observable at the decision (as `costs.trade_cost`), the fee at the fill time,
the stress multiplier. The clock is set only by a fill that actually raised
held exposure, to that order's 00:00 decision instant (Q10 (b)). Held
exposure drifts with price between fills (C-6 (3)), as in
`engine._drifted_exposure`.

Readings EC-n (proposed, for review):
- EC-1 Targets are clipped to [0, 1] (BACKTESTER_SPEC l.3); a non-finite
  target is refused, never repaired.
- EC-2 At delay 0, with no reduction to 0 that the band would have blocked,
  this gives exactly `engine.run_backtest`'s exposures, costs and equity;
  the unit tests check that identity.
- EC-3 The run starts flat, with no pending order and an unset clock (C-10
  (4) states it for G-11 draws; it holds for every run here).
- EC-4 A caller may pass `sigma_bps`, the series' cost-model volatility
  (`ewma_hourly_volatility_bps_series(hourly_log_returns_bps(series))`),
  to avoid recomputing it for the many runs of one screen path (G-11's 500
  draws); a series of the wrong length is refused. Results are identical.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from aqt.backtest.costs import (
    FeeSchedule,
    ewma_hourly_volatility_bps_series,
    hourly_log_returns_bps,
    per_side_cost_bps,
    resolve_taker_fee_bps,
)
from aqt.benchmarks.canonical import (
    MAX_EXPOSURE,
    MIN_EXPOSURE,
    MINIMUM_HOLD_FOR_RISK_INCREASE,
    is_scheduled_decision,
    reaches_rebalance_band,
)
from aqt.data.bars import BarSeries

__all__ = ["EventContractError", "EventResult", "Fill", "run_event_contract"]

DELAYS = (0, 1)


class EventContractError(ValueError):
    """Input the event contract refuses."""


@dataclass(frozen=True, slots=True)
class Fill:
    decision_instant: int
    fill_instant: int
    held_before: float
    exposure: float
    cost: float


@dataclass(frozen=True, slots=True)
class EventResult:
    """Per instant `start + i`: exposure held over bar `start + i` and equity
    at its end (initial equity 1); every fill; orders dropped at the end."""

    start: int
    exposure: tuple[float, ...]
    equity: tuple[float, ...]
    fills: tuple[Fill, ...]
    dropped: int

    @property
    def final_equity(self) -> float:
        return self.equity[-1] if self.equity else 1.0

    @property
    def turnover(self) -> float:
        return math.fsum(abs(f.exposure - f.held_before) for f in self.fills)


def _drift(exposure: float, gross_return: float) -> float:
    if exposure in (MIN_EXPOSURE, MAX_EXPOSURE):
        return exposure
    return exposure * (1.0 + gross_return) / (1.0 + exposure * gross_return)


def run_event_contract(
    series: BarSeries,
    targets: Sequence[float],
    start: int,
    *,
    fees: FeeSchedule | None = None,
    stress_multiplier: float = 1.0,
    delay: int = 0,
    sigma_bps: Sequence[float] | None = None,
) -> EventResult:
    """Run `targets[i]`, decided at instant `start + i`, under C-6.
    `sigma_bps`, if given, must be the series' own cost-model volatility
    (EC-4); it saves recomputing it for many runs on one series."""
    if not isinstance(series, BarSeries):
        raise EventContractError("series must be a BarSeries")
    if delay not in DELAYS or isinstance(delay, bool):
        raise EventContractError(f"delay must be one of {DELAYS}")
    series.require_contiguous()
    bars = series.bars
    n = len(targets)
    if start < 3 or start + n >= len(bars):
        raise EventContractError(
            "need two observable returns before the first decision and a "
            "following open after the last"
        )
    clipped = []
    for i, t in enumerate(targets):
        value = float(t)
        if not math.isfinite(value):
            raise EventContractError(f"target {i} is not finite: {t!r}")
        clipped.append(min(MAX_EXPOSURE, max(MIN_EXPOSURE, value)))
    per_side_cost_bps(sigma_hourly_bps=0.0, stress_multiplier=stress_multiplier)
    sigma = (
        ewma_hourly_volatility_bps_series(hourly_log_returns_bps(series))
        if sigma_bps is None
        else sigma_bps
    )
    if len(sigma) != len(bars) - 2:
        raise EventContractError("sigma_bps does not match the series")

    held = MIN_EXPOSURE
    equity = 1.0
    clock: datetime | None = None
    pending: tuple[int, float, bool] | None = None  # decided at, target, increase
    exposure: list[float] = []
    path: list[float] = []
    fills: list[Fill] = []

    def fill(decided: int, j: int, target: float, increase: bool) -> None:
        nonlocal held, equity, clock
        new = target if increase else min(target, held)
        traded = abs(new - held)
        cost = per_side_cost_bps(
            sigma_hourly_bps=sigma[decided - 3],
            fee=resolve_taker_fee_bps(fees, bars[j].open_time),
            stress_multiplier=stress_multiplier,
        ).cost_quote(traded)
        if cost >= 1.0:
            raise EventContractError(f"fill at {j} would consume all equity")
        equity *= 1.0 - cost
        fills.append(Fill(decided, j, held, new, cost))
        if new > held:
            clock = bars[decided].open_time
        held = new

    for i, target in enumerate(clipped):
        j = start + i
        if pending is not None:  # step 1
            fill(pending[0], j, pending[1], pending[2])
            pending = None
        moment = bars[j].open_time  # step 2
        delta = target - held
        if delta > 0.0:
            passes = (
                is_scheduled_decision(moment)
                and (clock is None or moment - clock >= MINIMUM_HOLD_FOR_RISK_INCREASE)
                and reaches_rebalance_band(delta)
            )
        elif delta < 0.0:
            passes = target == MIN_EXPOSURE or reaches_rebalance_band(delta)
        else:
            passes = False
        if passes:  # step 3
            if delay == 0:
                fill(j, j, target, delta > 0.0)
            else:
                pending = (j, target, delta > 0.0)
        gross = (bars[j + 1].open - bars[j].open) / bars[j].open
        if not math.isfinite(gross) or gross <= -1.0:
            raise EventContractError(f"bar {j} return {gross!r} is not valid")
        exposure.append(held)
        equity *= 1.0 + held * gross
        if not math.isfinite(equity) or equity <= 0.0:
            raise EventContractError(f"equity after bar {j} is {equity!r}")
        path.append(equity)
        held = _drift(held, gross)
    return EventResult(
        start=start,
        exposure=tuple(exposure),
        equity=tuple(path),
        fills=tuple(fills),
        dropped=int(pending is not None),  # step 4
    )
