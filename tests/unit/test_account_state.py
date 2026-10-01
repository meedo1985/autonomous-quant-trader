"""Roadmap 2 Task 27 part a: account state that survives restarts."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

import aqt.app.paper_loop as loop
from aqt.app.state import (
    RECORD_TYPE,
    AccountDir,
    AccountState,
    StateError,
    StateJournal,
)
from aqt.backtest.costs import Side
from aqt.core.ledger import LedgerError, append_entry
from aqt.execution.reconcile import LocalRecord
from aqt.execution.safety import Mode
from aqt.execution.simulator import Order, OrderStatus

T0 = datetime(2026, 9, 29, tzinfo=UTC)


def _order(cid: str, qty: str = "0.12345678") -> Order:
    return Order(
        client_order_id=cid,
        symbol="BTCUSDT",
        side=Side.SELL,
        orig_qty=Decimal(qty),
        executed_qty=Decimal(qty),
        status=OrderStatus.FILLED,
        decision_time=T0,
        fill_time=T0 + timedelta(hours=1),
        fill_price=Decimal("65000.01"),
        quote_amount=Decimal("8024.6912345"),
        cost_quote=Decimal("0.0000000001"),
        cost_bps=Decimal("27"),
        limit_price=Decimal("64350.00"),
    )


def _state(**changes: object) -> AccountState:
    base = AccountState(
        mode=Mode.FREEZE,
        entered_at=T0 + timedelta(hours=2),
        record=LocalRecord(
            {"USDT": Decimal("1234.567890123456789"), "BTC": Decimal("0.5")},
            {"aqt-exec-1": _order("aqt-exec-1"), "aqt-exec-2": None},
        ),
        sent={"aqt-flat-1": None, "aqt-flat-2": _order("aqt-flat-2", "0.25")},
        attempts={"aqt-flat-1": (Decimal("0.5"), Decimal("64000.00"))},
        peak=Decimal("10000.000000000000001"),
        stop_armed=False,
        last_increase=T0,
        zero_fills=2,
    )
    return replace(base, **changes)


def test_a_snapshot_round_trips_exactly(tmp_path: Path) -> None:
    journal = StateJournal(tmp_path / "state.jsonl")
    state = _state()
    journal.save(state, T0 + timedelta(hours=2))
    loaded = journal.load()
    assert loaded == state
    assert loaded is not None and loaded.as_mapping() == state.as_mapping()


def test_an_account_never_run_has_no_state(tmp_path: Path) -> None:
    assert StateJournal(tmp_path / "state.jsonl").load() is None


def test_the_last_snapshot_is_the_state(tmp_path: Path) -> None:
    journal = StateJournal(tmp_path / "state.jsonl")
    journal.save(_state(mode=Mode.RUNNING), T0)
    journal.save(_state(mode=Mode.HALT, sent={}), T0 + timedelta(hours=1))
    loaded = journal.load()
    assert loaded is not None
    assert loaded.mode is Mode.HALT and dict(loaded.sent) == {}


def test_an_edited_snapshot_breaks_the_chain_and_refuses(tmp_path: Path) -> None:
    """A hand edit (HALT back to RUNNING) is detected, not trusted."""
    journal = StateJournal(tmp_path / "state.jsonl")
    journal.save(_state(mode=Mode.HALT), T0)
    text = journal.path.read_text("utf-8").replace('"HALT"', '"RUNNING"')
    journal.path.write_text(text, "utf-8", newline="\n")
    with pytest.raises(LedgerError):
        journal.load()


def test_a_torn_last_line_refuses(tmp_path: Path) -> None:
    journal = StateJournal(tmp_path / "state.jsonl")
    journal.save(_state(), T0)
    with journal.path.open("ab") as handle:
        handle.write(b'{"sequence": 1, "payl')
    with pytest.raises(LedgerError):
        journal.load()


def test_another_record_type_last_refuses(tmp_path: Path) -> None:
    path = tmp_path / "state.jsonl"
    StateJournal(path).save(_state(), T0)
    append_entry(path, record_type="something.else.v1", payload={}, recorded_at_utc=T0)
    with pytest.raises(StateError, match="record type"):
        StateJournal(path).load()


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("mode", "SLEEPING"),
        ("peak", "NaN"),
        ("peak", 10000),  # a float or int, not a decimal string
        ("entered_at", "2026-09-29T02:00:00"),  # naive
        ("stop_armed", "yes"),
        ("zero_fills", True),
        ("incidents_seen", -1),
        ("incidents_seen", "3"),
        ("sent", {"aqt-flat-1": {"client_order_id": "x"}}),  # incomplete order
    ],
)
def test_a_snapshot_that_does_not_parse_exactly_refuses(
    tmp_path: Path, key: str, value: object
) -> None:
    path = tmp_path / "state.jsonl"
    payload = _state().as_mapping()
    payload[key] = value
    append_entry(path, record_type=RECORD_TYPE, payload=payload, recorded_at_utc=T0)
    with pytest.raises(StateError):
        StateJournal(path).load()


def test_the_account_directory_is_per_account_not_per_run(tmp_path: Path) -> None:
    """F24-3: every run of one account shares its incident log, and so its
    refuse-start marker and journal."""
    first, second = AccountDir(tmp_path / "acct"), AccountDir(tmp_path / "acct")
    first.incident_log().open("OWNER_HALT", "left open", T0)
    assert second.incident_log().open_incidents()
    assert loop.refuse_marker_path(second.incident_log()).parent == first.root
    assert first.journal.path == second.journal.path


def test_snapshots_are_canonical_json(tmp_path: Path) -> None:
    """Decimals are strings, so nothing is rounded through a float."""
    journal = StateJournal(tmp_path / "state.jsonl")
    journal.save(_state(), T0)
    line = json.loads(journal.path.read_text("utf-8").splitlines()[0])
    assert line["payload"]["peak"] == "10000.000000000000001"
    assert line["payload"]["record"]["balances"]["USDT"] == "1234.567890123456789"


@pytest.mark.parametrize(
    "change",
    [
        {"attempts": {"x": "12"}},  # a string read as a pair
        {"attempts": {"x": ["1", "2", "3"]}},  # truncated to two
        {"unknown": 1},  # an unknown field
        {"peak": "1.0e3"},  # parses, but not as written
    ],
)
def test_a_snapshot_must_parse_exactly(change: dict[str, object]) -> None:
    """A27-6: a snapshot is accepted only if it is exactly what the state
    writes."""
    payload = {**_state().as_mapping(), **change}
    with pytest.raises(StateError, match="exactly|parse"):
        AccountState.from_mapping(payload)


def test_a_foreign_entry_anywhere_in_the_journal_refuses(tmp_path: Path) -> None:
    """A27-6: every entry is a snapshot, not only the last."""
    journal = StateJournal(tmp_path / "state.jsonl")
    append_entry(journal.path, record_type="other.v1", payload={}, recorded_at_utc=T0)
    journal.save(_state(), T0 + timedelta(hours=1))
    with pytest.raises(StateError, match="unexpected record type"):
        journal.load_saved()
