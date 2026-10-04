"""Account state that survives restarts (roadmap 2, Task 27 part a;
`review/task27/DESIGN.md`).

Everything the safety system knows lives, per account rather than per run,
in one directory (`AccountDir`): the incident log, the operations log, the
refuse-start marker, and a state journal. The journal is a hash-chained,
append-only ledger (`aqt.core.ledger`) of `AccountState` snapshots; the last
snapshot is the state to resume from. A damaged journal, or a snapshot that
does not parse exactly, raises: a start that cannot know its state must not
start (Constitution section 26; T23-04, T24-08, F24-3).

Part a stores and loads the state. Wiring it into the loop, and the owner's
loss-stop answers Q27-1 and Q27-2, are part b.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final

from aqt.backtest.costs import Side
from aqt.core.ledger import append_entry, read_entries
from aqt.data.bars import require_utc
from aqt.execution.reconcile import LocalRecord
from aqt.execution.safety import IncidentLog, Mode
from aqt.execution.simulator import Order, OrderStatus

__all__ = ["RECORD_TYPE", "AccountDir", "AccountState", "StateError", "StateJournal"]

RECORD_TYPE: Final[str] = "aqt.app.account_state.v1"
_SAVED_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%SZ"  # `aqt.core.ledger` stamps


class StateError(ValueError):
    """A snapshot that cannot be trusted as the account's state."""


def _time(value: object, name: str) -> datetime:
    if not isinstance(value, str):
        raise StateError(f"{name} must be a timestamp string, got {value!r}")
    try:
        return require_utc(datetime.fromisoformat(value), field_name=name)
    except ValueError as error:
        raise StateError(f"{name}: {error}") from None


def _decimal(value: object, name: str) -> Decimal:
    if not isinstance(value, str):
        raise StateError(f"{name} must be a decimal string, got {value!r}")
    try:
        number = Decimal(value)
    except InvalidOperation:
        raise StateError(f"{name} is not a decimal: {value!r}") from None
    if not number.is_finite():
        raise StateError(f"{name} is not finite: {value!r}")
    return number


def _order_out(order: Order | None) -> dict[str, str] | None:
    return None if order is None else order.as_mapping()


def _order_in(data: object, name: str) -> Order | None:
    if data is None:
        return None
    if not isinstance(data, Mapping):
        raise StateError(f"{name} must be an order mapping")
    try:
        limit = data["limit_price"]
        return Order(
            client_order_id=str(data["client_order_id"]),
            symbol=str(data["symbol"]),
            side=Side(data["side"]),
            orig_qty=_decimal(data["orig_qty"], f"{name}.orig_qty"),
            executed_qty=_decimal(data["executed_qty"], f"{name}.executed_qty"),
            status=OrderStatus(data["status"]),
            decision_time=_time(data["decision_time"], f"{name}.decision_time"),
            fill_time=_time(data["fill_time"], f"{name}.fill_time"),
            fill_price=_decimal(data["fill_price"], f"{name}.fill_price"),
            quote_amount=_decimal(data["quote_amount"], f"{name}.quote_amount"),
            cost_quote=_decimal(data["cost_quote"], f"{name}.cost_quote"),
            cost_bps=_decimal(data["cost_bps"], f"{name}.cost_bps"),
            limit_price=None if limit == "" else _decimal(limit, f"{name}.limit_price"),
        )
    except (KeyError, ValueError) as error:
        raise StateError(f"{name}: {error}") from None


def _orders_in(data: object, name: str) -> dict[str, Order | None]:
    if not isinstance(data, Mapping):
        raise StateError(f"{name} must be a mapping")
    return {str(k): _order_in(v, f"{name}[{k}]") for k, v in data.items()}


@dataclass(frozen=True, slots=True)
class AccountState:
    """What a restart must know (`review/task27/DESIGN.md` section 2)."""

    mode: Mode
    entered_at: datetime
    record: LocalRecord
    """Balances of the last passed reconciliation, plus every order sent
    since (T23-09)."""
    sent: Mapping[str, Order | None]
    """FLATTEN orders not yet settled by a passed reconciliation."""
    attempts: Mapping[str, tuple[Decimal, Decimal]]
    """Quantity and price cap of each FLATTEN order sent (F35-3)."""
    peak: Decimal
    stop_armed: bool
    last_increase: datetime | None
    valued_through: datetime | None
    """The last decision hour whose valuation `peak` and `stop_armed`
    include (`None` before any): a restart replays only later hours
    (A27-13)."""
    zero_fills: int = 0
    incidents_seen: int = 0
    """Entries in the incident log when saved: an incident opened after it
    is an alarm this snapshot has not applied (part b)."""
    unfinished_from: datetime | None = None
    """The first decision hour the run had not finished when this was saved:
    the hour in progress at a save within an hour, the next one at an hour's
    end (S29R2-1). `None` in a snapshot written before it was recorded."""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "entered_at", require_utc(self.entered_at, field_name="entered_at")
        )
        for name in ("last_increase", "valued_through", "unfinished_from"):
            if getattr(self, name) is not None:
                require_utc(getattr(self, name), field_name=name)
        if not self.peak.is_finite() or self.peak < 0:
            raise StateError(f"invalid peak {self.peak}")
        if self.zero_fills < 0 or self.incidents_seen < 0:
            raise StateError("zero_fills and incidents_seen must not be negative")
        for name in ("sent", "attempts"):
            object.__setattr__(self, name, MappingProxyType(dict(getattr(self, name))))

    def as_mapping(self) -> dict[str, object]:
        # Omitted when `None`, so earlier snapshots still parse exactly.
        unfinished = (
            {}
            if self.unfinished_from is None
            else {"unfinished_from": self.unfinished_from.isoformat()}
        )
        return {
            **unfinished,
            "attempts": {
                k: [str(q), str(c)] for k, (q, c) in sorted(self.attempts.items())
            },
            "entered_at": self.entered_at.isoformat(),
            "incidents_seen": self.incidents_seen,
            "last_increase": (
                None if self.last_increase is None else self.last_increase.isoformat()
            ),
            "mode": str(self.mode),
            "peak": str(self.peak),
            "record": {
                "balances": {
                    k: str(v) for k, v in sorted(self.record.balances.items())
                },
                "orders": {
                    k: _order_out(v) for k, v in sorted(self.record.orders.items())
                },
            },
            "sent": {k: _order_out(v) for k, v in sorted(self.sent.items())},
            "stop_armed": self.stop_armed,
            "valued_through": (
                None if self.valued_through is None else self.valued_through.isoformat()
            ),
            "zero_fills": self.zero_fills,
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> AccountState:
        try:
            record = data["record"]
            attempts = data["attempts"]
            if not isinstance(attempts, Mapping) or not isinstance(record, Mapping):
                raise StateError("attempts and record must be mappings")
            balances = record["balances"]
            if not isinstance(balances, Mapping):
                raise StateError("record.balances must be a mapping")
            stop_armed = data["stop_armed"]
            zero_fills = data["zero_fills"]
            seen = data["incidents_seen"]
            if not isinstance(stop_armed, bool) or {type(zero_fills), type(seen)} != {
                int
            }:
                raise StateError(
                    "stop_armed must be a bool, zero_fills and incidents_seen ints"
                )
            last = data["last_increase"]
            valued = data["valued_through"]
            unfinished = data.get("unfinished_from")
            state = cls(
                mode=Mode(data["mode"]),
                entered_at=_time(data["entered_at"], "entered_at"),
                record=LocalRecord(
                    {str(k): _decimal(v, f"balance {k}") for k, v in balances.items()},
                    _orders_in(record["orders"], "record.orders"),
                ),
                sent=_orders_in(data["sent"], "sent"),
                attempts={
                    str(k): (
                        _decimal(v[0], f"attempts[{k}] quantity"),
                        _decimal(v[1], f"attempts[{k}] cap"),
                    )
                    for k, v in attempts.items()
                },
                peak=_decimal(data["peak"], "peak"),
                stop_armed=stop_armed,
                last_increase=None if last is None else _time(last, "last_increase"),
                valued_through=(
                    None if valued is None else _time(valued, "valued_through")
                ),
                zero_fills=zero_fills,
                incidents_seen=seen,
                unfinished_from=None
                if unfinished is None
                else _time(unfinished, "unfinished_from"),
            )
        except (KeyError, IndexError, TypeError, ValueError) as error:
            if isinstance(error, StateError):
                raise
            raise StateError(f"snapshot does not parse: {error!r}") from None
        # Exact: the snapshot must be what this state writes, so no unknown
        # field, coerced value or truncated pair is accepted (A27-6).
        if state.as_mapping() != data:
            raise StateError("snapshot does not parse exactly")
        return state


class StateJournal:
    """Hash-chained, append-only snapshots of one account's state."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def save(self, state: AccountState, at: datetime) -> None:
        """Append a snapshot; fsynced before this returns."""
        append_entry(
            self.path,
            record_type=RECORD_TYPE,
            payload=state.as_mapping(),
            recorded_at_utc=require_utc(at, field_name="at"),
        )

    def load(self) -> AccountState | None:
        """The last snapshot, or `None` for an account never run. A damaged
        chain raises `LedgerError`; a snapshot that does not parse exactly,
        or an entry of another type, raises `StateError`."""
        last = self.load_saved()
        return None if last is None else last[0]

    def load_saved(self) -> tuple[AccountState, datetime] | None:
        """`load`, with the time the snapshot was saved at."""
        if not self.path.exists():
            return None
        entries = read_entries(self.path)
        if not entries:
            return None
        for entry in entries:  # every entry, not only the last (A27-6, A27-12)
            if entry.record_type != RECORD_TYPE:
                raise StateError(f"unexpected record type {entry.record_type!r}")
            AccountState.from_mapping(entry.payload)
        last = entries[-1]
        saved_at = datetime.strptime(last.recorded_at_utc, _SAVED_FORMAT)
        return AccountState.from_mapping(last.payload), saved_at.replace(tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class AccountDir:
    """One account's directory: every run of that account uses it (F24-3)."""

    root: Path

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    @property
    def incidents_path(self) -> Path:
        return self.root / "incidents.jsonl"

    @property
    def operations_path(self) -> Path:
        return self.root / "operations.jsonl"

    @property
    def journal(self) -> StateJournal:
        return StateJournal(self.root / "state.jsonl")

    def incident_log(self) -> IncidentLog:
        return IncidentLog(self.incidents_path)
