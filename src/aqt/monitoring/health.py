"""Health checks for the live loop (roadmap Task 19).

Each check is a pure function of explicit timestamps and a threshold and
returns an `Event` when the condition is breached, else `None`. Thresholds and
severities are parameters with no defaults: choosing them is a policy decision
for the deployment protocol (Task 20), not for this module.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from aqt.data.bars import require_utc
from aqt.monitoring.events import Event, EventKind, Severity

__all__ = ["check_clock_skew", "check_loop_lag", "check_stale_data"]


def _positive(limit: timedelta, name: str) -> timedelta:
    if limit <= timedelta(0):
        raise ValueError(f"{name} must be positive, got {limit}")
    return limit


def _ms(delta: timedelta) -> int:
    return delta // timedelta(milliseconds=1)


def check_stale_data(
    *, latest_bar_close: datetime, now: datetime, max_age: timedelta, severity: Severity
) -> Event | None:
    """Breach when the newest bar closed more than `max_age` before `now`."""
    age = require_utc(now, field_name="now") - require_utc(
        latest_bar_close, field_name="latest_bar_close"
    )
    if age <= _positive(max_age, "max_age"):
        return None
    return Event(
        EventKind.STALE_DATA,
        severity,
        now,
        {"age_ms": _ms(age), "max_age_ms": _ms(max_age)},
    )


def check_clock_skew(
    *,
    local_now: datetime,
    reference_now: datetime,
    max_skew: timedelta,
    severity: Severity,
) -> Event | None:
    """Breach when the local clock differs from a reference clock (for
    example the exchange's server time) by more than `max_skew` either way."""
    skew = require_utc(local_now, field_name="local_now") - require_utc(
        reference_now, field_name="reference_now"
    )
    if abs(skew) <= _positive(max_skew, "max_skew"):
        return None
    return Event(
        EventKind.CLOCK_SKEW,
        severity,
        local_now,
        {"skew_ms": _ms(skew), "max_skew_ms": _ms(max_skew)},
    )


def check_loop_lag(
    *, scheduled: datetime, started: datetime, max_lag: timedelta, severity: Severity
) -> Event | None:
    """Breach when a loop iteration started more than `max_lag` after its
    scheduled time. Starting early is not lag."""
    lag = require_utc(started, field_name="started") - require_utc(
        scheduled, field_name="scheduled"
    )
    if lag <= _positive(max_lag, "max_lag"):
        return None
    return Event(
        EventKind.LOOP_LAG,
        severity,
        started,
        {"lag_ms": _ms(lag), "max_lag_ms": _ms(max_lag)},
    )
