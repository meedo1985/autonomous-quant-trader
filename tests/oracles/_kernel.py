"""Exact-arithmetic backtest oracle kernel for the Task 6 acceptance suite.

This module is **test-private on purpose**. It lives under ``tests/``, is never
imported by ``aqt``, and must not become production code. It is a direct
transcription of the frozen semantics of ``specs/BACKTESTER_SPEC_v1.md``,
``specs/COST_MODEL_v1.md``, ``specs/CANONICAL_BENCHMARKS_v1.md`` and
``protocols/protocol_v1.yaml`` into exact rational arithmetic
(:class:`fractions.Fraction` and :class:`int`), so that every ledger identity
asserted by the Task 6 suite is:

* independent of the production backtester, which does not exist yet, and
* independent of floating-point ambiguity, so no tolerance has to be invented.

Deferred on purpose. Comparing these identities against the NumPy reference
implementation, and against the production backtester through an adapter, is
**DEFERRED TO THE NEXT ORDERED TASK**: neither artefact exists, and
``docs/RESEARCH_CONSTITUTION.md`` section 16 fixes the order
``human spec review -> oracle tests -> leakage canaries -> NumPy reference ->
production implementation``. No placeholder, stub or skipped test stands in
for them here.

Transcribed frozen semantics
----------------------------

* A decision taken at ``close(t)`` is executed at ``open(t+1)``
  (``BACKTESTER_SPEC_v1.md`` item 2). Segment ``i`` of a ledger is therefore
  the interval ``[open(i), open(i+1))``; its exposure is the exposure actually
  held over that interval after execution at ``open(i)``
  (``BACKTESTER_SPEC_v1.md`` item 8).
* Exposure targets are clipped to ``[0, 1]`` (item 3;
  ``scope.max_exposure_per_asset``).
* Cost is charged on the absolute change in exposure (item 4) at a per-side
  rate expressed as a fraction of traded notional (``COST_MODEL_v1.md``).
* Risk increases happen only at the scheduled 00:00 UTC decision and respect
  the 24h minimum hold (item 5; ``scope.risk_increase_rule``); exposure
  reductions may happen at any hourly bar (item 6).

Human-accepted oracle conventions
---------------------------------

These were explicitly accepted by the owner and are recorded in
``review/task6/HUMAN_ACCEPTANCE.md``.

1. **Production accounting compounds equity.** The additive fixed-notional
   aggregator remains an independent diagnostic oracle. Cost is charged at an
   execution before the exposure earns the following open-to-open return.
2. **The path starts flat.** Exposure before segment 0 is ``0``, so entering
   the market is a trade and is charged. Nothing is charged for holding a
   non-zero terminal exposure: the frozen documents describe no forced
   liquidation at the end of a sample.
3. **The 10pp band is inclusive.** The sequential target ledger holds actual
   drifted exposure without cost below the band. The separate
   :func:`require_admissible` checker rejects a purported executed-state path
   containing such a change. Float production code must reuse Task 5's bounded
   ULP-aware comparator; this exact oracle needs no tolerance.
4. **Targets and actual held weights are distinct.** Between trades, a
   fractional risky-asset weight drifts with its return. The accepted exact
   no-trade drift and next-turnover identities are provided here before the
   ordered NumPy reference. :func:`build_target_ledger` is the test-private
   sequential oracle; it is not the future NumPy or production engine.
"""

import hashlib
import json
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from fractions import Fraction
from itertools import product
from typing import Final

ZERO: Final = Fraction(0)
ONE: Final = Fraction(1)

MIN_EXPOSURE: Final = ZERO
MAX_EXPOSURE: Final = ONE

BAR_INTERVAL: Final = timedelta(hours=1)
HOURS_PER_DAY: Final = 24
SCHEDULED_DECISION_ANCHOR_HOUR_UTC: Final = 0
MINIMUM_HOLDING_FOR_RISK_INCREASE: Final = timedelta(hours=24)
REBALANCE_BAND_ABSOLUTE: Final = Fraction(1, 10)

BPS_PER_UNIT: Final = 10_000
FALLBACK_TAKER_FEE_BPS: Final = Fraction(10)
SPREAD_ALLOWANCE_BPS: Final = Fraction(2)
SLIPPAGE_FLOOR_BPS: Final = Fraction(1)
SLIPPAGE_CAP_BPS: Final = Fraction(15)
SLIPPAGE_VOL_COEFFICIENT: Final = Fraction(1, 20)
STRESS_MULTIPLIERS: Final = (Fraction(1), Fraction(3, 2), Fraction(2), Fraction(3))


class OracleError(ValueError):
    """Raised when an oracle input violates a transcribed frozen rule."""


@dataclass(frozen=True, slots=True)
class Segment:
    """One executed holding interval ``[open(i), open(i+1))``."""

    index: int
    execution_time: datetime
    exposure: Fraction
    gross_return: Fraction
    traded: Fraction
    cost: Fraction


@dataclass(frozen=True, slots=True)
class Ledger:
    """A complete exact per-segment record of one simulated exposure path."""

    start: datetime
    cost_rate: Fraction
    stress_multiplier: Fraction
    segments: tuple[Segment, ...]


def require_utc_hour(moment: datetime) -> None:
    """Reject anything that is not an exact UTC hour boundary."""
    if moment.tzinfo is None or moment.utcoffset() != timedelta(0):
        raise OracleError(f"timestamp {moment!r} is not UTC")
    if moment.minute or moment.second or moment.microsecond:
        raise OracleError(f"timestamp {moment!r} is not aligned to a 1h bar")


def slippage_bps(sigma_hourly_bps: Fraction) -> Fraction:
    """``min(15, max(1, 0.05 * sigma_hourly_bps))`` in exact arithmetic."""
    if sigma_hourly_bps < 0:
        raise OracleError("hourly volatility in bps cannot be negative")
    scaled = SLIPPAGE_VOL_COEFFICIENT * sigma_hourly_bps
    return min(SLIPPAGE_CAP_BPS, max(SLIPPAGE_FLOOR_BPS, scaled))


def per_side_cost_bps(sigma_hourly_bps: Fraction) -> Fraction:
    """``fee_bps + spread_bps + slippage_bps`` at the fallback fee."""
    return (
        FALLBACK_TAKER_FEE_BPS + SPREAD_ALLOWANCE_BPS + slippage_bps(sigma_hourly_bps)
    )


def cost_rate_from_bps(total_bps: Fraction) -> Fraction:
    """Convert a per-side cost in basis points to a fraction of notional."""
    if total_bps < 0:
        raise OracleError("cost in bps cannot be negative")
    return total_bps / BPS_PER_UNIT


def clip_exposure(target: Fraction) -> Fraction:
    """Clip a target exposure to the frozen long-only ``[0, 1]`` range."""
    return min(MAX_EXPOSURE, max(MIN_EXPOSURE, target))


def drifted_exposure(exposure: Fraction, gross_return: Fraction) -> Fraction:
    """Actual risky-asset weight after a no-trade segment with zero cash return."""
    if not MIN_EXPOSURE <= exposure <= MAX_EXPOSURE:
        raise OracleError(f"actual exposure {exposure} outside [0, 1]")
    if gross_return <= -ONE:
        raise OracleError("a positive-price segment return must be greater than -1")
    return exposure * (ONE + gross_return) / (ONE + exposure * gross_return)


def exposure_change_to_target(target: Fraction, current: Fraction) -> Fraction:
    """Signed trade from actual held weight to a clipped decision target."""
    if not MIN_EXPOSURE <= current <= MAX_EXPOSURE:
        raise OracleError(f"actual exposure {current} outside [0, 1]")
    return clip_exposure(target) - current


def reaches_rebalance_band(change: Fraction) -> bool:
    """Whether an exact exposure change reaches the inclusive frozen 10pp band."""
    return abs(change) >= REBALANCE_BAND_ABSOLUTE


def additive_price_grid(
    first_open: Fraction, hourly_steps: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    """Build open prices by adding exact steps, keeping magnitudes small."""
    opens = [first_open]
    for step in hourly_steps:
        nxt = opens[-1] + step
        if nxt <= 0:
            raise OracleError("synthetic price path reached a non-positive price")
        opens.append(nxt)
    return tuple(opens)


def repeat_daily(values: Sequence[Fraction]) -> tuple[Fraction, ...]:
    """Expand one value per decision day into one value per 1h bar."""
    expanded: list[Fraction] = []
    for value in values:
        expanded.extend([value] * HOURS_PER_DAY)
    return tuple(expanded)


def segment_returns(opens: Sequence[Fraction]) -> tuple[Fraction, ...]:
    """Exact simple returns from ``open(i)`` to ``open(i+1)``."""
    if len(opens) < 2:
        raise OracleError("a price grid needs at least two opens")
    for price in opens:
        if price <= 0:
            raise OracleError("open prices must be strictly positive")
    return tuple((opens[i + 1] - opens[i]) / opens[i] for i in range(len(opens) - 1))


def require_admissible(start: datetime, exposures: Sequence[Fraction]) -> None:
    """Reject an exposure path the frozen scheduling rules forbid.

    Risk increases only at the 00:00 UTC decision and only at least 24h after
    the previous increase; reductions may occur at any hourly bar; a change
    smaller than the 10pp band is not an action at all.
    """
    require_utc_hour(start)
    previous = MIN_EXPOSURE
    last_increase: datetime | None = None
    for index, target in enumerate(exposures):
        exposure = clip_exposure(target)
        execution_time = start + index * BAR_INTERVAL
        change = exposure - previous
        if change != ZERO and not reaches_rebalance_band(change):
            raise OracleError(
                f"change {change} at index {index} is inside the 10pp band"
            )
        if change > ZERO:
            if execution_time.hour != SCHEDULED_DECISION_ANCHOR_HOUR_UTC:
                raise OracleError(
                    f"risk increase at index {index} is not at the 00:00 UTC decision"
                )
            if (
                last_increase is not None
                and execution_time - last_increase < MINIMUM_HOLDING_FOR_RISK_INCREASE
            ):
                raise OracleError(
                    f"risk increase at index {index} breaks the 24h minimum hold"
                )
            last_increase = execution_time
        previous = exposure


def build_ledger(
    start: datetime,
    opens: Sequence[Fraction],
    exposures: Sequence[Fraction],
    cost_rate: Fraction,
    stress_multiplier: Fraction = ONE,
) -> Ledger:
    """Build the exact ledger from an already executed actual-exposure path."""
    require_utc_hour(start)
    if len(exposures) != len(opens) - 1:
        raise OracleError(
            f"{len(exposures)} exposures cannot fill {len(opens) - 1} segments"
        )
    if cost_rate < 0 or stress_multiplier < 0:
        raise OracleError("cost rate and stress multiplier must be non-negative")
    if cost_rate * stress_multiplier >= ONE:
        raise OracleError("a full-size trade would cost at least its own notional")
    returns = segment_returns(opens)
    segments: list[Segment] = []
    previous = MIN_EXPOSURE
    for index, target in enumerate(exposures):
        exposure = clip_exposure(target)
        traded = abs(exposure - previous)
        segments.append(
            Segment(
                index=index,
                execution_time=start + index * BAR_INTERVAL,
                exposure=exposure,
                gross_return=returns[index],
                traded=traded,
                cost=cost_rate * stress_multiplier * traded,
            )
        )
        previous = exposure
    return Ledger(
        start=start,
        cost_rate=cost_rate,
        stress_multiplier=stress_multiplier,
        segments=tuple(segments),
    )


def build_target_ledger(
    start: datetime,
    opens: Sequence[Fraction],
    targets: Sequence[Fraction],
    cost_rate: Fraction,
    stress_multiplier: Fraction = ONE,
) -> Ledger:
    """Build a sequential ledger from targets and drifted actual weights."""
    require_utc_hour(start)
    if len(targets) != len(opens) - 1:
        raise OracleError(
            f"{len(targets)} targets cannot fill {len(opens) - 1} segments"
        )
    if cost_rate < 0 or stress_multiplier < 0:
        raise OracleError("cost rate and stress multiplier must be non-negative")
    if cost_rate * stress_multiplier >= ONE:
        raise OracleError("a full-size trade would cost at least its own notional")

    returns = segment_returns(opens)
    segments: list[Segment] = []
    current = MIN_EXPOSURE
    last_increase: datetime | None = None
    for index, (target, gross_return) in enumerate(zip(targets, returns, strict=True)):
        execution_time = start + index * BAR_INTERVAL
        change = exposure_change_to_target(target, current)
        traded = ZERO
        executed = current
        if change != ZERO and reaches_rebalance_band(change):
            increase_is_allowed = change > ZERO and (
                execution_time.hour == SCHEDULED_DECISION_ANCHOR_HOUR_UTC
                and (
                    last_increase is None
                    or execution_time - last_increase
                    >= MINIMUM_HOLDING_FOR_RISK_INCREASE
                )
            )
            if change < ZERO or increase_is_allowed:
                if increase_is_allowed:
                    last_increase = execution_time
                traded = abs(change)
                executed = clip_exposure(target)

        segments.append(
            Segment(
                index=index,
                execution_time=execution_time,
                exposure=executed,
                gross_return=gross_return,
                traded=traded,
                cost=cost_rate * stress_multiplier * traded,
            )
        )
        current = drifted_exposure(executed, gross_return)

    return Ledger(
        start=start,
        cost_rate=cost_rate,
        stress_multiplier=stress_multiplier,
        segments=tuple(segments),
    )


def turnover(ledger: Ledger) -> Fraction:
    """Total absolute change in exposure, entry included."""
    return sum((segment.traded for segment in ledger.segments), ZERO)


def total_cost(ledger: Ledger) -> Fraction:
    """Total cost as a fraction of a fixed unit notional."""
    return sum((segment.cost for segment in ledger.segments), ZERO)


def additive_gross_pnl(ledger: Ledger) -> Fraction:
    """Fixed-notional gross PnL: ``sum(exposure_i * return_i)``."""
    return sum(
        (segment.exposure * segment.gross_return for segment in ledger.segments),
        ZERO,
    )


def additive_net_pnl(ledger: Ledger) -> Fraction:
    """Fixed-notional PnL net of the charged cost."""
    return additive_gross_pnl(ledger) - total_cost(ledger)


def compounded_gross_equity(ledger: Ledger) -> Fraction:
    """Terminal equity from a unit start, ignoring cost."""
    equity = ONE
    for segment in ledger.segments:
        equity *= ONE + segment.exposure * segment.gross_return
    return equity


def compounded_net_equity(ledger: Ledger) -> Fraction:
    """Terminal equity from a unit start, cost charged at each execution."""
    equity = ONE
    for segment in ledger.segments:
        equity *= ONE - segment.cost
        equity *= ONE + segment.exposure * segment.gross_return
    return equity


def losing_segments(ledger: Ledger) -> tuple[Segment, ...]:
    """Segments whose held exposure lost money before cost."""
    return tuple(
        segment
        for segment in ledger.segments
        if segment.exposure * segment.gross_return < ZERO
    )


def binary_exposure_paths(count: int) -> Iterator[tuple[Fraction, ...]]:
    """Every flat-or-fully-invested path over ``count`` decisions."""
    if count < 0:
        raise OracleError("cannot enumerate a negative number of decisions")
    yield from product((MIN_EXPOSURE, MAX_EXPOSURE), repeat=count)


def spearman_rho(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    """Exact Spearman rank correlation for tie-free samples.

    Uses ``1 - 6 * sum(d^2) / (n * (n^2 - 1))``, which is exact in rational
    arithmetic because both rank vectors are permutations of ``1..n``. Ties
    are rejected rather than silently corrected.
    """
    size = len(left)
    if size != len(right):
        raise OracleError("Spearman inputs must have equal length")
    if size < 2:
        raise OracleError("Spearman needs at least two observations")
    squared = sum(
        (a - b) ** 2 for a, b in zip(_ranks(left), _ranks(right), strict=True)
    )
    return ONE - Fraction(6 * squared, size * (size * size - 1))


def _ranks(values: Sequence[Fraction]) -> tuple[int, ...]:
    if len(set(values)) != len(values):
        raise OracleError("tied values have no exact tie-free rank")
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0] * len(values)
    for rank, index in enumerate(order, start=1):
        ranks[index] = rank
    return tuple(ranks)


def exact(value: Fraction) -> str:
    """Canonical loss-free text form of an exact rational."""
    if not isinstance(value, Fraction):
        raise OracleError(f"{value!r} is not an exact rational")
    return f"{value.numerator}/{value.denominator}"


def canonical_record_bytes(record: Mapping[str, str]) -> bytes:
    """Apply the frozen compact-JSON canonicalization to an oracle record."""
    payload = json.dumps(
        dict(record),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return payload.encode("utf-8")


def record_digest(payload: bytes) -> str:
    """SHA-256 of a canonical oracle record."""
    return hashlib.sha256(payload).hexdigest()


def utc(year: int, month: int, day: int, hour: int = 0) -> datetime:
    """Build a UTC hour-aligned synthetic timestamp."""
    return datetime(year, month, day, hour, tzinfo=UTC)
