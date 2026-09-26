"""Synthetic tests for events, alert routing, redaction, and health checks."""

from __future__ import annotations

import io
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from aqt.core.ledger import read_entries, verify_ledger
from aqt.data.manifest import canonical_json_bytes
from aqt.monitoring.alerts import (
    LEDGER_RECORD_TYPE,
    REDACTED,
    ROTATION_RECORD_TYPE,
    AlertConfigError,
    AlertRouter,
    LedgerSink,
    RotatingLedgerSink,
    StreamSink,
    verify_rotated_log,
)
from aqt.monitoring.events import Event, EventError, EventKind, Severity
from aqt.monitoring.health import check_clock_skew, check_loop_lag, check_stale_data

AT = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=UTC)
SHA256 = "5f92ec5041c9560d5f31bdb99b9686d7522697e65a8e61d514a0b0dda6d0b65b"
API_KEY = "vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A"


@pytest.mark.parametrize("kind", list(EventKind))
def test_every_event_kind_round_trips_through_canonical_json(kind: EventKind) -> None:
    event = Event(kind, Severity.WARNING, AT, {"s": "x", "i": -3, "b": True, "n": None})
    data = canonical_json_bytes(event.as_mapping())
    assert Event.from_mapping(json.loads(data)) == event


@pytest.mark.parametrize(
    "bad",
    [
        {"at": AT.replace(tzinfo=None)},  # naive time
        {"fields": {"x": 1.5}},  # floats cannot be canonical
        {"fields": {"": "x"}},
        {"kind": "STARTUP"},  # a bare string is not an EventKind
    ],
)
def test_events_refuse_values_they_cannot_represent(bad: dict[str, object]) -> None:
    args: dict[str, object] = {
        "kind": EventKind.STARTUP,
        "severity": Severity.INFO,
        "at": AT,
        "fields": {},
    }
    args.update(bad)
    with pytest.raises((EventError, ValueError)):
        Event(**args)  # type: ignore[arg-type]


def test_ledger_log_is_hash_chained_and_a_mutated_line_fails(tmp_path: Path) -> None:
    path = tmp_path / "ops.jsonl"
    router = AlertRouter([LedgerSink(path, Severity.INFO)])
    for n in range(3):
        router.emit(Event(EventKind.ORDER, Severity.INFO, AT, {"n": n}))
    verify_ledger(path).require_intact()
    entries = read_entries(path)
    assert [e.record_type for e in entries] == [LEDGER_RECORD_TYPE] * 3
    assert [Event.from_mapping(e.payload).fields["n"] for e in entries] == [0, 1, 2]

    lines = path.read_bytes().splitlines(keepends=True)
    tampered = lines[1].replace(b'"n":1', b'"n":7')
    assert tampered != lines[1]
    lines[1] = tampered
    path.write_bytes(b"".join(lines))
    assert not verify_ledger(path).intact
    with pytest.raises(ValueError):
        router.emit(Event(EventKind.ORDER, Severity.INFO, AT, {"n": 3}))


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("api_key", "anything"),
        ("binance_secret", "anything"),
        ("note", API_KEY),  # a Binance-shaped key under an innocent name
        ("header", "Bearer abc.def.ghi"),
        ("pem", "-----BEGIN RSA PRIVATE KEY-----\nMIIE"),
    ],
)
def test_credential_shaped_values_are_redacted_and_the_redaction_logged(
    name: str, value: str
) -> None:
    stream = io.StringIO()
    router = AlertRouter([StreamSink(stream, Severity.INFO)])
    emitted = router.emit(Event(EventKind.ORDER, Severity.INFO, AT, {name: value}))
    assert emitted.fields[name] == REDACTED
    output = stream.getvalue()
    assert value not in output
    first, second = (json.loads(line) for line in output.splitlines())
    assert first["kind"] == "REDACTION" and first["fields"]["fields"] == name
    assert second["fields"][name] == REDACTED


def test_hashes_and_ordinary_values_are_not_redacted() -> None:
    stream = io.StringIO()
    router = AlertRouter([StreamSink(stream, Severity.INFO)])
    fields = {"manifest_sha256": SHA256, "symbol": "BTCUSDT", "qty": "0.5"}
    router.emit(Event(EventKind.ORDER, Severity.INFO, AT, fields))
    [line] = stream.getvalue().splitlines()
    assert json.loads(line)["fields"] == fields


def test_a_router_with_no_sink_refuses_to_start() -> None:
    with pytest.raises(AlertConfigError, match="section 19"):
        AlertRouter([])


def test_events_reach_only_sinks_whose_minimum_they_meet() -> None:
    quiet, loud = io.StringIO(), io.StringIO()
    router = AlertRouter(
        [StreamSink(quiet, Severity.CRITICAL), StreamSink(loud, Severity.INFO)]
    )
    router.emit(Event(EventKind.ORDER, Severity.INFO, AT))
    router.emit(Event(EventKind.STALE_DATA, Severity.CRITICAL, AT))
    assert len(loud.getvalue().splitlines()) == 2
    assert [json.loads(x)["kind"] for x in quiet.getvalue().splitlines()] == [
        "STALE_DATA"
    ]


def test_a_failing_sink_is_not_swallowed() -> None:
    class Broken:
        min_severity = Severity.INFO

        def write(self, event: Event) -> None:
            raise OSError("disk full")

    with pytest.raises(OSError, match="disk full"):
        AlertRouter([Broken()]).emit(Event(EventKind.ORDER, Severity.CRITICAL, AT))


MINUTE = timedelta(minutes=1)


def test_stale_data_is_reported_only_beyond_the_limit() -> None:
    close = AT - 5 * MINUTE
    assert (
        check_stale_data(
            latest_bar_close=close,
            now=AT,
            max_age=5 * MINUTE,
            severity=Severity.CRITICAL,
        )
        is None
    )  # exactly at the limit is not stale
    event = check_stale_data(
        latest_bar_close=close, now=AT, max_age=4 * MINUTE, severity=Severity.CRITICAL
    )
    assert event is not None and event.kind is EventKind.STALE_DATA
    assert dict(event.fields) == {"age_ms": 300_000, "max_age_ms": 240_000}


@pytest.mark.parametrize("offset", [2 * MINUTE, -2 * MINUTE])
def test_clock_skew_is_reported_in_either_direction(offset: timedelta) -> None:
    event = check_clock_skew(
        local_now=AT,
        reference_now=AT + offset,
        max_skew=MINUTE,
        severity=Severity.WARNING,
    )
    assert event is not None and event.fields["skew_ms"] == -offset // timedelta(
        milliseconds=1
    )
    assert (
        check_clock_skew(
            local_now=AT,
            reference_now=AT + offset,
            max_skew=3 * MINUTE,
            severity=Severity.WARNING,
        )
        is None
    )


def test_loop_lag_counts_late_starts_only() -> None:
    assert (
        check_loop_lag(
            scheduled=AT,
            started=AT - 10 * MINUTE,
            max_lag=MINUTE,
            severity=Severity.WARNING,
        )
        is None
    )  # early is not lag
    event = check_loop_lag(
        scheduled=AT, started=AT + 2 * MINUTE, max_lag=MINUTE, severity=Severity.WARNING
    )
    assert event is not None and event.fields == {
        "lag_ms": 120_000,
        "max_lag_ms": 60_000,
    }


@pytest.mark.parametrize("limit", [timedelta(0), -MINUTE])
def test_thresholds_must_be_positive(limit: timedelta) -> None:
    with pytest.raises(ValueError, match="positive"):
        check_loop_lag(scheduled=AT, started=AT, max_lag=limit, severity=Severity.INFO)


def test_health_checks_reject_naive_times() -> None:
    with pytest.raises(ValueError):
        check_stale_data(
            latest_bar_close=AT.replace(tzinfo=None),
            now=AT,
            max_age=MINUTE,
            severity=Severity.INFO,
        )


# --- Review repairs (review/task19/REVIEW.md) ---------------------------------


def test_the_redaction_record_reaches_a_critical_only_log(tmp_path: Path) -> None:
    """R-1: a sink that takes only CRITICAL events still gets the audit record."""
    path = tmp_path / "ops.jsonl"
    router = AlertRouter([LedgerSink(path, Severity.CRITICAL)])
    router.emit(
        Event(EventKind.ORDER, Severity.CRITICAL, AT, {"api_key": "credential"})
    )
    kinds = [Event.from_mapping(e.payload).kind for e in read_entries(path)]
    assert kinds == [EventKind.REDACTION, EventKind.ORDER]


def test_a_credential_shaped_field_name_never_reaches_a_sink() -> None:
    """R-2: the name is replaced too, in the event and in the audit record."""
    stream = io.StringIO()
    router = AlertRouter([StreamSink(stream, Severity.INFO)])
    name = "api_key=" + API_KEY
    emitted = router.emit(
        Event(EventKind.ORDER, Severity.INFO, AT, {"ok": 1, name: "x"})
    )
    assert API_KEY not in stream.getvalue()
    assert dict(emitted.fields) == {"ok": 1, "redacted_field_1": REDACTED}
    audit = json.loads(stream.getvalue().splitlines()[0])
    assert audit["fields"]["fields"] == "redacted_field_1"


def _day(n: int) -> datetime:
    return datetime(2026, 9, 26 + n, 12, tzinfo=UTC)


def test_the_log_rotates_daily_and_the_chain_continues(tmp_path: Path) -> None:
    """R-3: one file per UTC day, each linked to the previous file's head."""
    router = AlertRouter([RotatingLedgerSink(tmp_path, Severity.INFO)])
    for n in range(3):
        for k in range(2):
            router.emit(Event(EventKind.ORDER, Severity.INFO, _day(n), {"k": k}))
    names = sorted(p.name for p in tmp_path.iterdir() if p.suffix == ".jsonl")
    assert names == [f"operations-2026-09-{d}.jsonl" for d in (26, 27, 28)]
    assert verify_rotated_log(tmp_path) == 3
    second = read_entries(tmp_path / names[1])
    assert second[0].record_type == ROTATION_RECORD_TYPE
    assert (
        second[0].payload["previous_head_hash"]
        == verify_ledger(tmp_path / names[0]).head_hash
    )


def test_a_late_timestamp_never_reopens_an_older_file(tmp_path: Path) -> None:
    router = AlertRouter([RotatingLedgerSink(tmp_path, Severity.INFO)])
    router.emit(Event(EventKind.ORDER, Severity.INFO, _day(1)))
    router.emit(Event(EventKind.ORDER, Severity.INFO, _day(0)))  # late event
    assert [p.name for p in tmp_path.glob("*.jsonl")] == ["operations-2026-09-27.jsonl"]
    assert len(read_entries(tmp_path / "operations-2026-09-27.jsonl")) == 2


@pytest.mark.parametrize("damage", ["edit_first_file", "delete_middle_file"])
def test_damage_to_a_rotated_log_is_detected(tmp_path: Path, damage: str) -> None:
    router = AlertRouter([RotatingLedgerSink(tmp_path, Severity.INFO)])
    for n in range(3):
        router.emit(Event(EventKind.ORDER, Severity.INFO, _day(n), {"n": n}))
    files = sorted(tmp_path.glob("*.jsonl"))
    if damage == "edit_first_file":
        data = files[0].read_bytes()
        assert b'"n":0' in data
        files[0].write_bytes(data.replace(b'"n":0', b'"n":9'))
    else:
        files[1].unlink()
    with pytest.raises(ValueError):
        verify_rotated_log(tmp_path)
