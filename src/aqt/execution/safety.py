"""HALT, FLATTEN, FREEZE, incidents, and startup (roadmap Task 23).

Constitution section 22: "HALT adds no risk. FLATTEN is bounded de-risking.
FREEZE makes no autonomous risk change. State transitions logged; exit FREEZE
only after reconciliation." Section 14: "Risk reductions are immediate [...]
HALT override requires: written incident record, identified or bounded
cause, successful reconciliation, explicit owner action, and timestamp.
Trading resumes only after incident closure plus successful reconciliation."
Section 0: an incident is "HALT, reconciliation mismatch, unexplained
exposure, ambiguous order, credential anomaly, or comparable safety event".

How that reads here:

* Only RUNNING lets the governor and executor trade (`may_trade`).
* HALT places no order at all, not even a reduction: stopping is the whole
  of HALT. FLATTEN is the reducing path, and the owner may start it from
  RUNNING or HALT at any time, whatever reservation the governor holds.
* The `L-03` loss stop enters FLATTEN from RUNNING; during any FLATTEN
  (its own or the owner's) it alerts and FLATTEN goes on; FLATTEN then ends
  in HALT (owner setting S-4,
  `review/deployment/OWNER_SETTINGS_2026-09-27.md`, reconfirmed 2026-09-28 in
  `review/task24/OWNER_ANSWER_S4.md`). In HALT it stays HALT: the owner's
  HALT always wins (`review/task24/OWNER_ANSWERS_2026-09-28.md`). Any other
  alarm during FLATTEN stops the selling in HALT.
* FLATTEN sells only, at most the free base balance the venue reports, in
  steps of at most `max_step_fraction` of it, each an immediate-or-cancel
  order capped at `max_slippage_bps` below the mark. It can never cross
  zero, because spot cannot sell what it does not hold. When what is left
  cannot be sold (below the lot or notional minimum), FLATTEN ends in HALT.
  Any unclear outcome of a FLATTEN order is FREEZE.
* FREEZE does nothing. It is left only through a passed reconciliation taken
  after it began, and it leads to HALT, because the ambiguous order that
  caused it is an incident that still needs closing. An owner FLATTEN
  request during FREEZE is refused: the frozen text allows no exit before
  reconciliation.
* Every entry into HALT or FREEZE opens an incident in an append-only,
  hash-chained ledger (section 26). HALT is left only through
  `override_halt`, which needs all five section 14 artifacts, closes every
  open incident, and fabricates none of them.
* Every transition is logged through the alert router; entries into HALT,
  FLATTEN and FREEZE are CRITICAL (deployment draft section 5).
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Context, Decimal
from enum import StrEnum
from pathlib import Path
from typing import Final, Protocol

from aqt.backtest.costs import Side as TradeSide
from aqt.core.ledger import append_entry, read_entries
from aqt.data.bars import require_utc
from aqt.execution.orders import capped_price
from aqt.execution.reconcile import (
    LocalRecord,
    ReconciliationReport,
    ReconcilingVenue,
    reconcile,
)
from aqt.execution.simulator import ExchangeError, Order, SymbolFilters
from aqt.governor.authorization import Side
from aqt.monitoring.alerts import AlertRouter
from aqt.monitoring.events import Event, EventKind, Severity

__all__ = [
    "MODE_TRANSITIONS",
    "FlattenBounds",
    "HaltOverride",
    "IncidentLog",
    "Mode",
    "OwnerAction",
    "SafetyController",
    "SafetyError",
    "StartupDecision",
    "Trigger",
    "startup_check",
]

_DEC: Final = Context(prec=34)
_QUOTE: Final[str] = "USDT"


class SafetyError(RuntimeError):
    """A refused safety action; protective failures may leave FREEZE or HALT."""


class Mode(StrEnum):
    RUNNING = "RUNNING"
    HALT = "HALT"
    FLATTEN = "FLATTEN"
    FREEZE = "FREEZE"


class Trigger(StrEnum):
    OWNER_HALT = "OWNER_HALT"
    INCIDENT = "INCIDENT"
    LOSS_STOP = "LOSS_STOP"  # L-03, detected by the loop (Task 24)
    OWNER_FLATTEN = "OWNER_FLATTEN"
    FLATTEN_DONE = "FLATTEN_DONE"
    FLATTEN_FAULT = "FLATTEN_FAULT"
    AMBIGUOUS_ORDER = "AMBIGUOUS_ORDER"
    RECONCILIATION_FAILED = "RECONCILIATION_FAILED"
    FREEZE_EXIT = "FREEZE_EXIT"
    HALT_OVERRIDE = "HALT_OVERRIDE"


_M, _T = Mode, Trigger
_TO_HALT: Final = (_T.OWNER_HALT, _T.INCIDENT)
_TO_FREEZE: Final = (_T.AMBIGUOUS_ORDER, _T.RECONCILIATION_FAILED)

MODE_TRANSITIONS: Final[dict[tuple[Mode, Trigger], Mode]] = {
    **{(_M.RUNNING, t): _M.HALT for t in _TO_HALT},
    # The L-03 stop sells everything in FLATTEN steps, then HALTs (S-4).
    (_M.RUNNING, _T.LOSS_STOP): _M.FLATTEN,
    (_M.RUNNING, _T.OWNER_FLATTEN): _M.FLATTEN,
    **{(_M.RUNNING, t): _M.FREEZE for t in _TO_FREEZE},
    **{(_M.HALT, t): _M.HALT for t in _TO_HALT},
    (_M.HALT, _T.LOSS_STOP): _M.HALT,  # the owner's HALT wins (F24-1)
    (_M.HALT, _T.OWNER_FLATTEN): _M.FLATTEN,
    **{(_M.HALT, t): _M.FREEZE for t in _TO_FREEZE},
    (_M.HALT, _T.HALT_OVERRIDE): _M.RUNNING,
    # Only S-4 authorizes an alarm to keep selling: the L-03 stop. Any other
    # alarm stops in HALT; the owner can start FLATTEN again after assessing.
    (_M.FLATTEN, _T.OWNER_HALT): _M.HALT,
    (_M.FLATTEN, _T.INCIDENT): _M.HALT,
    (_M.FLATTEN, _T.LOSS_STOP): _M.FLATTEN,
    (_M.FLATTEN, _T.OWNER_FLATTEN): _M.FLATTEN,
    (_M.FLATTEN, _T.FLATTEN_DONE): _M.HALT,
    (_M.FLATTEN, _T.FLATTEN_FAULT): _M.FREEZE,
    **{(_M.FLATTEN, t): _M.FREEZE for t in _TO_FREEZE},
    # FREEZE absorbs every alarm and leaves only through reconciliation.
    **{(_M.FREEZE, t): _M.FREEZE for t in (*_TO_HALT, _T.LOSS_STOP, *_TO_FREEZE)},
    (_M.FREEZE, _T.FREEZE_EXIT): _M.HALT,
}
"""Every allowed mode change. Anything else is refused."""

_INCIDENT_TRIGGERS: Final = frozenset(
    {*_TO_HALT, _T.LOSS_STOP, *_TO_FREEZE, _T.FLATTEN_DONE, _T.FLATTEN_FAULT}
)
"""Triggers that open an incident: every entry into HALT or FREEZE, and
every alarm raised while in a protective mode."""

_ALARMS: Final = frozenset({*_TO_HALT, _T.LOSS_STOP, *_TO_FREEZE})
"""Alarms are never refused for a late timestamp: a risk reduction is
immediate (section 14), so a stale stamp is moved up to the latest time."""


class IncidentLog:
    """Incidents in an append-only, hash-chained ledger (section 26).

    An incident's id is the hash of the entry that opened it. Reading
    verifies the whole chain first, so a damaged log raises instead of
    reporting nothing open.
    """

    OPEN: Final[str] = "aqt.execution.incident.open.v1"
    CLOSE: Final[str] = "aqt.execution.incident.close.v1"

    def __init__(self, path: Path) -> None:
        self.path = path

    def open(self, kind: str, detail: str, at: datetime) -> str:
        entry = append_entry(
            self.path,
            record_type=self.OPEN,
            payload={"detail": detail, "kind": kind},
            recorded_at_utc=at,
        )
        return entry.entry_hash

    def close(
        self, incident_id: str, resolution: Mapping[str, str], at: datetime
    ) -> None:
        append_entry(
            self.path,
            record_type=self.CLOSE,
            payload={"incident_id": incident_id, **resolution},
            recorded_at_utc=at,
        )

    def open_incidents(self) -> tuple[str, ...]:
        opened: list[str] = []
        closed: set[str] = set()
        for entry in read_entries(self.path):
            if entry.record_type == self.OPEN:
                opened.append(entry.entry_hash)
            elif entry.record_type == self.CLOSE:
                closed.add(str(entry.payload["incident_id"]))
        return tuple(i for i in opened if i not in closed)


@dataclass(frozen=True, slots=True)
class OwnerAction:
    """Who acted, and what they said. Supplied by the owner, never by code."""

    actor: str
    statement: str


@dataclass(frozen=True, slots=True)
class HaltOverride:
    """The five section 14 artifacts. `None` means missing; nothing defaults.

    `incident_ids` must name every open incident, since trading resumes only
    after incident closure.
    """

    incident_ids: tuple[str, ...] | None
    written_record: str | None
    cause: str | None
    reconciliation: ReconciliationReport | None
    owner_action: OwnerAction | None
    timestamp: datetime | None


@dataclass(frozen=True, slots=True)
class FlattenBounds:
    """`[OPEN]` in the deployment draft section 6; both required.

    `max_step_fraction` is the largest share of the free base balance sold
    in one step; `max_slippage_bps` caps each sell below the mark.
    """

    max_step_fraction: Decimal
    max_slippage_bps: Decimal

    def __post_init__(self) -> None:
        if not 0 < self.max_step_fraction <= 1:
            raise ValueError(f"invalid max_step_fraction {self.max_step_fraction}")
        if not self.max_slippage_bps.is_finite() or self.max_slippage_bps < 0:
            raise ValueError(f"invalid max_slippage_bps {self.max_slippage_bps}")


def _floor_to_step(quantity: Decimal, step: Decimal) -> Decimal:
    return _DEC.multiply(_DEC.divide_int(quantity, step), step)


class SafetyController:
    """The protective mode of one trading process."""

    def __init__(
        self,
        router: AlertRouter,
        incidents: IncidentLog,
        at: datetime,
        *,
        mode: Mode,
    ) -> None:
        """`mode` has no default: the caller chooses RUNNING only after
        `startup_check` passes."""
        self._router = router
        self._incidents = incidents
        self.mode = mode
        self.entered_at = require_utc(at, field_name="at")
        self._latest = self.entered_at
        self.sent: dict[str, Order | None] = {}
        """FLATTEN orders not yet settled by a passed reconciliation. Recovery
        requires a report that resolved every one of them. Only
        `settle_flatten` or a successful recovery removes them, so a caller
        advances its baseline balances past an order exactly when it settles
        it."""
        self._flatten_steps = 0
        self._last_flatten_decision: datetime | None = None

    def may_trade(self) -> bool:
        """Whether the governor and executor may act at all."""
        return self.mode is Mode.RUNNING

    def _time(self, at: datetime) -> datetime:
        at = require_utc(at, field_name="at")
        if at < self._latest:
            raise SafetyError(f"time went backwards: {at} < {self._latest}")
        return at

    def trigger(self, trigger: Trigger, at: datetime, detail: str = "") -> Mode:
        """Apply `trigger`; refused (and nothing changes) when not allowed."""
        at = require_utc(at, field_name="at")
        if trigger in _ALARMS and at < self._latest:
            detail = f"{detail} (stamped {at.isoformat()})".lstrip()
            at = self._latest
        at = self._time(at)
        if trigger in (Trigger.FREEZE_EXIT, Trigger.HALT_OVERRIDE):
            raise SafetyError(f"{trigger} needs its own procedure")
        return self._move(trigger, at, detail)

    def _move(self, trigger: Trigger, at: datetime, detail: str) -> Mode:
        target = MODE_TRANSITIONS.get((self.mode, trigger))
        if target is None:
            raise SafetyError(f"{trigger} is not allowed in {self.mode}")
        source = self.mode
        if target is not Mode.RUNNING:
            # Fail closed before either required audit write. If the incident
            # ledger or alert sink fails, no caller can keep trading.
            self.mode = Mode.FREEZE
            self.entered_at = at
            self._latest = at
        incident = ""
        if trigger in _INCIDENT_TRIGGERS:
            incident = self._incidents.open(str(trigger), detail, at)
        severity = Severity.CRITICAL if target is not Mode.RUNNING else Severity.WARNING
        self._router.emit(
            Event(
                EventKind.STATE_TRANSITION,
                severity,
                at,
                {
                    "detail": detail,
                    "from": str(source),
                    "incident_id": incident or None,
                    "to": str(target),
                    "trigger": str(trigger),
                },
            )
        )
        # A later alarm makes any earlier reconciliation stale, including on
        # protective self-transitions.
        self.entered_at = at
        self.mode = target
        self._latest = at
        return target

    def exit_freeze(self, report: ReconciliationReport, at: datetime) -> Mode:
        """FREEZE to HALT, only on a passed reconciliation taken after the
        FREEZE began."""
        at = self._time(at)
        if self.mode is not Mode.FREEZE:
            raise SafetyError(f"not in FREEZE ({self.mode})")
        if not report.passed:
            raise SafetyError("reconciliation failed: " + "; ".join(report.differences))
        if report.at <= self.entered_at or report.at > at:
            raise SafetyError("the reconciliation does not follow the FREEZE")
        self._require_covers(report)
        mode = self._move(Trigger.FREEZE_EXIT, at, f"reconciliation {report.digest()}")
        self.sent.clear()
        return mode

    def settle_flatten(self, report: ReconciliationReport) -> None:
        """Forget the FLATTEN orders a passed reconciliation resolved; the
        caller carries `report.next_record()` forward. A failed report
        settles nothing."""
        if not report.passed:
            raise SafetyError("a failed reconciliation settles nothing")
        for client_order_id in report.resolved:
            self.sent.pop(client_order_id, None)

    def _require_covers(self, report: ReconciliationReport) -> None:
        missing = sorted(set(self.sent) - set(report.resolved))
        if missing:
            raise SafetyError(f"the reconciliation did not resolve {missing}")

    def override_halt(self, override: HaltOverride, at: datetime) -> Mode:
        """HALT to RUNNING with all five section 14 artifacts, closing every
        open incident. Any missing or invalid artifact refuses it."""
        at = self._time(at)
        if self.mode is not Mode.HALT:
            raise SafetyError(f"not in HALT ({self.mode})")
        if not override.written_record or not override.written_record.strip():
            raise SafetyError("HALT override refused: missing written incident record")
        if not override.cause or not override.cause.strip():
            raise SafetyError(
                "HALT override refused: missing identified or bounded cause"
            )
        report = override.reconciliation
        if report is None or not report.passed:
            raise SafetyError(
                "HALT override refused: missing successful reconciliation"
            )
        if report.at <= self.entered_at or report.at > at:
            raise SafetyError("HALT override refused: reconciliation predates the HALT")
        try:
            self._require_covers(report)
        except SafetyError as error:
            raise SafetyError(f"HALT override refused: {error}") from None
        action = override.owner_action
        if action is None or not action.actor.strip() or not action.statement.strip():
            raise SafetyError("HALT override refused: missing explicit owner action")
        stamp = override.timestamp
        if stamp is None:
            raise SafetyError("HALT override refused: missing timestamp")
        stamp = require_utc(stamp, field_name="timestamp")
        if not self.entered_at <= stamp <= at:
            raise SafetyError("HALT override refused: timestamp outside the HALT")
        still_open = set(self._incidents.open_incidents())
        named = set(override.incident_ids or ())
        if not named or named != still_open:
            raise SafetyError(
                "HALT override refused: it must name every open incident "
                f"(open: {sorted(still_open)}, named: {sorted(named)})"
            )
        resolution = {
            "actor": action.actor,
            "cause": override.cause,
            "owner_statement": action.statement,
            "reconciliation": report.digest(),
            "timestamp": stamp.isoformat(),
            "written_record": override.written_record,
        }
        for incident_id in sorted(named):
            self._incidents.close(incident_id, resolution, at)
        try:
            mode = self._move(Trigger.HALT_OVERRIDE, at, f"owner {action.actor}")
            self.sent.clear()
            return mode
        except Exception:
            # The closed incidents cannot be reopened. Keep HALT recoverable by
            # recording the failed transition as a new incident for the retry.
            # Advance the cutoff first, so even a failed recovery write cannot
            # leave earlier reconciliation eligible.
            self.mode = Mode.HALT
            self.entered_at = at
            self._latest = at
            self._incidents.open(
                "HALT_OVERRIDE_FAILED",
                f"owner {action.actor}: transition audit failed",
                at,
            )
            raise

    def tick(
        self,
        venue: _FlattenVenue,
        symbol: str,
        filters: SymbolFilters,
        bounds: FlattenBounds,
        mark_price: Decimal,
        decision_time: datetime,
        at: datetime,
    ) -> Order | None:
        """The controller's only autonomous action: one FLATTEN step. In any
        other mode it touches nothing and returns `None`."""
        at = self._time(at)
        if self.mode is not Mode.FLATTEN:
            return None
        decision_time = require_utc(decision_time, field_name="decision_time")
        if decision_time > at:
            self._move(
                Trigger.FLATTEN_FAULT, at, f"decision time {decision_time} > {at}"
            )
            return None
        last = self._last_flatten_decision
        if last is not None and decision_time <= last:
            # At most one step per decision bar, so "50% per step" cannot
            # compound within one bar on a repeated or duplicated tick.
            return None
        if not mark_price.is_finite() or mark_price <= 0:
            self._move(Trigger.FLATTEN_FAULT, at, f"invalid mark price: {mark_price}")
            return None
        base = symbol.removesuffix(_QUOTE)
        try:
            free = venue.balances().get(base, Decimal(0))
        except Exception as error:  # noqa: BLE001 - the holding is unknown
            self._move(Trigger.FLATTEN_FAULT, at, f"balance unreadable: {error}")
            return None
        quantity_bound = min(
            _DEC.multiply(free, bounds.max_step_fraction), filters.max_qty
        )
        if filters.max_notional is not None:
            quantity_bound = min(
                quantity_bound, _DEC.divide(filters.max_notional, mark_price)
            )
        quantity = _floor_to_step(quantity_bound, filters.step_size)
        small = _DEC.multiply(quantity, mark_price) < filters.min_notional
        if quantity <= 0 or quantity < filters.min_qty or small:
            self._move(
                Trigger.FLATTEN_DONE,
                at,
                f"no sellable step within the bound; {base} left: {free}",
            )
            return None
        cap = capped_price(Side.SELL, mark_price, bounds.max_slippage_bps, filters)
        if cap is None:
            self._move(Trigger.FLATTEN_FAULT, at, "no valid sell price")
            return None
        self._flatten_steps += 1
        seed = f"{symbol}|{at.isoformat()}|{self._flatten_steps}"
        client_order_id = "aqt-flat-" + hashlib.sha256(seed.encode()).hexdigest()[:27]
        self.sent[client_order_id] = None
        self._last_flatten_decision = decision_time
        try:
            order = venue.place_order(
                client_order_id,
                symbol,
                TradeSide.SELL,
                quantity,
                decision_time,
                limit_price=cap,
            )
        except ExchangeError as error:
            # Local filter checks already passed. A venue rejection means the
            # account or filters differ from what this controller used.
            self._move(Trigger.FLATTEN_FAULT, at, str(error))
            return None
        except Exception as error:  # noqa: BLE001 - the outcome is unknown
            self._move(Trigger.FLATTEN_FAULT, at, f"{type(error).__name__}: {error}")
            return None
        expected = (client_order_id, symbol, TradeSide.SELL, quantity, cap)
        actual = (
            order.client_order_id,
            order.symbol,
            order.side,
            order.orig_qty,
            order.limit_price,
        )
        if actual != expected or order.executed_qty > quantity:
            self._move(Trigger.FLATTEN_FAULT, at, f"venue order {actual} != {expected}")
            return None
        self.sent[client_order_id] = order
        self._latest = at
        return order


class _FlattenVenue(ReconcilingVenue, Protocol):
    def place_order(
        self,
        client_order_id: str,
        symbol: str,
        side: TradeSide,
        quantity: Decimal,
        decision_time: datetime,
        *,
        limit_price: Decimal | None = None,
    ) -> Order: ...


@dataclass(frozen=True, slots=True)
class StartupDecision:
    start: bool
    reasons: tuple[str, ...]
    report: ReconciliationReport


def startup_check(
    venue: ReconcilingVenue,
    local: LocalRecord,
    tolerance: Mapping[str, Decimal],
    incidents: IncidentLog,
    at: datetime,
) -> StartupDecision:
    """Section 19, "Startup reconciliation required": REFUSE_START on any
    reconciliation difference or open incident. A failed reconciliation
    opens an incident. The other REFUSE_START conditions of the deployment
    draft section 4 (hashes, alert channel, health) belong to the loop."""
    report = reconcile(venue, local, tolerance, at)
    reasons: list[str] = []
    if not report.passed:
        reasons.append("reconciliation failed: " + "; ".join(report.differences))
        incidents.open(str(Trigger.RECONCILIATION_FAILED), reasons[-1], at)
    still_open = incidents.open_incidents()
    if still_open:
        reasons.append(f"open incidents: {', '.join(still_open)}")
    return StartupDecision(start=not reasons, reasons=tuple(reasons), report=report)
