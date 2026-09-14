"""Tamper-evident ledger tests. Synthetic payloads only, no real data.

The concurrency test starts real operating-system processes with the `spawn`
start method, which is the only start method Windows has, so the cross-process
lock is exercised as it will be used.
"""

from __future__ import annotations

import dataclasses
import json
import multiprocessing
import os
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from aqt.core.ledger import (
    ENTRY_FIELDS,
    GENESIS_HASH,
    LOCK_SUFFIX,
    LedgerEntry,
    LedgerError,
    append_entry,
    read_entries,
    verify_ledger,
)
from aqt.data.manifest import canonical_json_bytes

_RECORD_TYPE = "aqt.test.record.v1"
_MOMENT = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)

_WORKERS = 4
_APPENDS_PER_WORKER = 8


def _ledger(tmp_path: Path) -> Path:
    return tmp_path / "registry.jsonl"


def _append(path: Path, index: int) -> LedgerEntry:
    return append_entry(
        path,
        record_type=_RECORD_TYPE,
        payload={"index": index, "note": "synthetic"},
        recorded_at_utc=_MOMENT,
    )


def _seed(path: Path, count: int) -> tuple[LedgerEntry, ...]:
    return tuple(_append(path, index) for index in range(count))


# ---------------------------------------------------------------------------
# Format and chain
# ---------------------------------------------------------------------------


def test_empty_and_missing_ledgers_are_intact(tmp_path: Path) -> None:
    report = verify_ledger(_ledger(tmp_path))
    assert (report.intact, report.entry_count, report.head_hash) == (
        True,
        0,
        GENESIS_HASH,
    )
    assert read_entries(_ledger(tmp_path)) == ()


def test_entries_are_canonical_lf_terminated_json_lines(tmp_path: Path) -> None:
    path = _ledger(tmp_path)
    _seed(path, 3)
    data = path.read_bytes()

    assert b"\r" not in data
    lines = data.split(b"\n")
    assert lines[-1] == b""
    for number, line in enumerate(lines[:-1]):
        parsed = json.loads(line.decode("utf-8"))
        assert set(parsed) == ENTRY_FIELDS
        assert parsed["sequence"] == number
        assert canonical_json_bytes(parsed) == line


def test_sequence_numbers_are_monotonic_and_hashes_chain(tmp_path: Path) -> None:
    path = _ledger(tmp_path)
    entries = _seed(path, 5)

    assert [entry.sequence for entry in entries] == [0, 1, 2, 3, 4]
    assert entries[0].previous_hash == GENESIS_HASH
    for previous, current in zip(entries, entries[1:], strict=False):
        assert current.previous_hash == previous.entry_hash
    assert len({entry.entry_hash for entry in entries}) == len(entries)

    report = verify_ledger(path)
    assert (report.intact, report.entry_count) == (True, 5)
    assert report.head_hash == entries[-1].entry_hash
    assert read_entries(path) == entries


def test_entries_are_immutable_and_payloads_are_copies(tmp_path: Path) -> None:
    entry = _append(_ledger(tmp_path), 0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.record_type = "other"  # type: ignore[misc]

    payload = entry.payload
    payload["index"] = 99
    assert entry.payload["index"] == 0


def test_payload_keys_are_sorted_and_line_endings_survive_escaping(
    tmp_path: Path,
) -> None:
    path = _ledger(tmp_path)
    entry = append_entry(
        path,
        record_type=_RECORD_TYPE,
        payload={"z": "tail", "a": "first\nsecond", "m": {"y": 1, "x": 2}},
        recorded_at_utc=_MOMENT,
    )
    assert entry.payload_json == '{"a":"first\\nsecond","m":{"x":2,"y":1},"z":"tail"}'
    assert len(path.read_bytes().splitlines()) == 1
    assert read_entries(path)[0].payload["a"] == "first\nsecond"


def test_timestamp_is_envelope_metadata_and_must_be_utc(tmp_path: Path) -> None:
    path = _ledger(tmp_path)
    entry = _append(path, 0)
    assert entry.recorded_at_utc == "2026-01-02T03:04:05Z"

    offset = _MOMENT.astimezone(timezone(timedelta(hours=3)))
    other = append_entry(
        tmp_path / "other.jsonl",
        record_type=_RECORD_TYPE,
        payload={"index": 0, "note": "synthetic"},
        recorded_at_utc=offset,
    )
    assert other.recorded_at_utc == entry.recorded_at_utc
    assert other.entry_hash == entry.entry_hash

    with pytest.raises(LedgerError, match="timezone-aware UTC"):
        append_entry(
            path,
            record_type=_RECORD_TYPE,
            payload={},
            recorded_at_utc=_MOMENT.replace(tzinfo=None),
        )


def test_appends_reject_unusable_record_types_and_payloads(tmp_path: Path) -> None:
    path = _ledger(tmp_path)
    with pytest.raises(LedgerError, match="record_type"):
        append_entry(path, record_type=" ", payload={}, recorded_at_utc=_MOMENT)
    with pytest.raises(LedgerError, match="payload must be a mapping"):
        append_entry(
            path,
            record_type=_RECORD_TYPE,
            payload=[1, 2],  # type: ignore[arg-type]
            recorded_at_utc=_MOMENT,
        )
    with pytest.raises(ValueError, match="float"):
        append_entry(
            path,
            record_type=_RECORD_TYPE,
            payload={"value": 1.5},
            recorded_at_utc=_MOMENT,
        )
    assert not path.exists()


# ---------------------------------------------------------------------------
# Damage detection and preservation
# ---------------------------------------------------------------------------


def _assert_preserved_and_refused(path: Path, before: bytes, pattern: str) -> None:
    """Verification and a rejected append must both leave the bytes alone."""
    report = verify_ledger(path)
    assert not report.intact
    assert report.problem is not None
    assert pattern in report.problem
    assert path.read_bytes() == before

    with pytest.raises(LedgerError, match="damaged"):
        read_entries(path)
    assert path.read_bytes() == before

    with pytest.raises(LedgerError, match="will not be appended to"):
        _append(path, 99)
    assert path.read_bytes() == before


def test_torn_trailing_write_is_detected_and_preserved(tmp_path: Path) -> None:
    path = _ledger(tmp_path)
    entries = _seed(path, 3)
    torn = _append(tmp_path / "scratch.jsonl", 3).line_bytes()[:37]
    with open(path, "ab") as handle:
        handle.write(torn)
    before = path.read_bytes()

    report = verify_ledger(path)
    assert report.entry_count == 3
    assert report.head_hash == entries[-1].entry_hash
    _assert_preserved_and_refused(path, before, "torn trailing write")


def test_altered_historical_entry_is_detected_and_preserved(tmp_path: Path) -> None:
    path = _ledger(tmp_path)
    _seed(path, 3)
    lines = path.read_bytes().splitlines()
    tampered = json.loads(lines[1].decode("utf-8"))
    tampered["payload"]["index"] = 42
    lines[1] = canonical_json_bytes(tampered)
    path.write_bytes(b"\n".join(lines) + b"\n")
    before = path.read_bytes()

    report = verify_ledger(path)
    assert report.entry_count == 1
    _assert_preserved_and_refused(path, before, "recomputed")


def test_reordered_keys_are_detected_even_though_the_json_parses(
    tmp_path: Path,
) -> None:
    path = _ledger(tmp_path)
    _seed(path, 2)
    lines = path.read_bytes().splitlines()
    parsed = json.loads(lines[0].decode("utf-8"))
    reordered = json.dumps(
        dict(reversed(list(parsed.items()))), separators=(",", ":")
    ).encode("utf-8")
    assert reordered != lines[0]
    lines[0] = reordered
    path.write_bytes(b"\n".join(lines) + b"\n")

    _assert_preserved_and_refused(path, path.read_bytes(), "not canonical JSON")


def test_duplicate_json_keys_are_detected(tmp_path: Path) -> None:
    path = _ledger(tmp_path)
    entry = _append(path, 0)
    line = entry.line_bytes().decode("utf-8")
    smuggled = line.replace('"index":0', '"index":0,"index":42', 1)
    assert smuggled != line
    path.write_bytes(smuggled.encode("utf-8"))

    _assert_preserved_and_refused(path, path.read_bytes(), "not canonical JSON")


def test_removed_entry_breaks_the_chain(tmp_path: Path) -> None:
    path = _ledger(tmp_path)
    _seed(path, 3)
    lines = path.read_bytes().splitlines()
    path.write_bytes(lines[0] + b"\n" + lines[2] + b"\n")

    _assert_preserved_and_refused(path, path.read_bytes(), "sequence")


def test_reversed_entries_break_the_chain(tmp_path: Path) -> None:
    path = _ledger(tmp_path)
    _seed(path, 2)
    lines = path.read_bytes().splitlines()
    path.write_bytes(lines[1] + b"\n" + lines[0] + b"\n")

    _assert_preserved_and_refused(path, path.read_bytes(), "sequence")


def test_blank_and_invalid_lines_are_detected(tmp_path: Path) -> None:
    path = _ledger(tmp_path)
    _seed(path, 1)
    with open(path, "ab") as handle:
        handle.write(b"\n")
    _assert_preserved_and_refused(path, path.read_bytes(), "not valid JSON")

    other = tmp_path / "other.jsonl"
    other.write_bytes(b'{"not":"an entry"}\n')
    _assert_preserved_and_refused(other, other.read_bytes(), "envelope fields")

    binary = tmp_path / "binary.jsonl"
    binary.write_bytes(b"\xff\xfe\n")
    _assert_preserved_and_refused(binary, binary.read_bytes(), "not valid UTF-8")


def test_lock_file_is_a_sidecar_and_is_not_part_of_the_chain(tmp_path: Path) -> None:
    path = _ledger(tmp_path)
    _seed(path, 1)
    lock = path.with_name(path.name + LOCK_SUFFIX)
    assert lock.is_file()
    assert lock.read_bytes() == b""
    assert verify_ledger(path).intact


# ---------------------------------------------------------------------------
# Real cross-process concurrency
# ---------------------------------------------------------------------------


def _concurrent_worker(arguments: tuple[str, int, int]) -> list[tuple[int, str]]:
    """Append `count` entries from a separate operating-system process."""
    path, worker, count = arguments
    observed: list[tuple[int, str]] = []
    for index in range(count):
        entry = append_entry(
            path,
            record_type=_RECORD_TYPE,
            payload={"index": index, "pid": os.getpid(), "worker": worker},
            recorded_at_utc=_MOMENT,
        )
        observed.append((entry.sequence, entry.entry_hash))
    return observed


def test_concurrent_processes_cannot_fork_the_append_sequence(tmp_path: Path) -> None:
    path = _ledger(tmp_path)
    context = multiprocessing.get_context("spawn")
    arguments = [(str(path), worker, _APPENDS_PER_WORKER) for worker in range(_WORKERS)]
    with context.Pool(_WORKERS) as pool:
        results = pool.map(_concurrent_worker, arguments)

    total = _WORKERS * _APPENDS_PER_WORKER
    claimed = [item for worker_result in results for item in worker_result]
    assert len(claimed) == total
    assert sorted(sequence for sequence, _ in claimed) == list(range(total))

    report = verify_ledger(path)
    assert (report.intact, report.entry_count) == (True, total)

    entries = read_entries(path)
    assert [entry.sequence for entry in entries] == list(range(total))
    assert {(entry.sequence, entry.entry_hash) for entry in entries} == set(claimed)

    witnessed = {
        (payload["worker"], payload["index"])
        for payload in (entry.payload for entry in entries)
    }
    assert len(witnessed) == total
    assert len({payload["pid"] for payload in (e.payload for e in entries)}) > 1
