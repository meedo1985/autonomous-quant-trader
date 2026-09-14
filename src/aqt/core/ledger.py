"""Tamper-evident append-only JSON Lines ledger.

`docs/RESEARCH_CONSTITUTION.md` section 26 requires the registry, trials,
lockbox logs, attestations, incidents, and cycle outcomes to be append-only and
tamper-evident. This module provides that storage primitive and nothing else:
it records entries, it verifies chains, and it refuses to write to a ledger it
cannot verify.

Storage format
--------------
One entry per line, UTF-8, LF-terminated, canonical JSON under
`schemas/HASH_CANONICALIZATION_v1.md` (keys sorted recursively, compact
separators, no floating-point values). Each entry carries its zero-based
`sequence`, the `previous_hash` of the entry before it (`GENESIS_HASH` for the
first), and its own `entry_hash` computed with the `entry_hash` field removed.
Verification re-serializes every line and compares bytes, so a re-ordered key,
a duplicate key, or a changed payload is detected even when the JSON still
parses.

Ordering authority
------------------
The sequence number, not `recorded_at_utc`, defines order. Concurrent writers
on different clocks may record non-monotonic timestamps; verification therefore
never infers corruption from a timestamp.

Failure behaviour
-----------------
`verify_ledger` reports damage and returns; it never truncates, rewrites, or
repairs a file. `append_entry` verifies the whole existing chain while holding
an exclusive cross-process lock and raises before opening the file for writing,
so a torn trailing write or an altered historical entry is preserved exactly as
found.

This module stores facts. It holds no opinion about what may be recorded, and
it makes no eligibility, budget, or permission decision.
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from aqt.data.manifest import ManifestError, canonical_hash, canonical_json_bytes

__all__ = [
    "ENTRY_FIELDS",
    "ENTRY_HASH_FIELD",
    "GENESIS_HASH",
    "LOCK_SUFFIX",
    "LOCK_TIMEOUT_SECONDS",
    "LedgerEntry",
    "LedgerError",
    "LedgerVerification",
    "append_entry",
    "read_entries",
    "verify_ledger",
]

GENESIS_HASH: Final[str] = "0" * 64
"""`previous_hash` of the first entry; no entry can ever hash to it."""

ENTRY_HASH_FIELD: Final[str] = "entry_hash"

ENTRY_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "entry_hash",
        "payload",
        "previous_hash",
        "record_type",
        "recorded_at_utc",
        "sequence",
    }
)

LOCK_SUFFIX: Final[str] = ".lock"
LOCK_TIMEOUT_SECONDS: Final[float] = 120.0

_HEX64: Final[str] = "0123456789abcdef"
_TIMESTAMP_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%SZ"
_LOCK_POLL_SECONDS: Final[float] = 0.005


class LedgerError(ValueError):
    """Raised when a ledger is damaged or an entry violates the format."""


def _require_sha256(value: object, name: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(char not in _HEX64 for char in value)
    ):
        raise LedgerError(f"{name} must be a lowercase 64-hex SHA-256, got {value!r}")
    return value


def _require_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise LedgerError(f"{name} must be a non-empty unpadded string, got {value!r}")
    return value


def _format_timestamp(moment: datetime | None) -> str:
    """Render a whole-second UTC timestamp for the ledger envelope.

    The timestamp lives in the envelope on purpose: a registration time is
    storage metadata and must not move the content identity of the payload.
    """
    if moment is None:
        moment = datetime.now(UTC)
    if not isinstance(moment, datetime):
        raise LedgerError(f"recorded_at_utc must be a datetime, got {moment!r}")
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise LedgerError("recorded_at_utc must be timezone-aware UTC")
    return moment.astimezone(UTC).replace(microsecond=0).strftime(_TIMESTAMP_FORMAT)


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    """One immutable ledger line.

    The payload is held as canonical JSON text rather than as a parsed object,
    so an entry handed to a caller cannot be mutated through a shared
    reference.
    """

    record_type: str
    sequence: int
    recorded_at_utc: str
    payload_json: str
    previous_hash: str
    entry_hash: str

    @property
    def payload(self) -> dict[str, Any]:
        """A freshly parsed copy of the payload; mutating it changes nothing."""
        parsed: dict[str, Any] = json.loads(self.payload_json)
        return parsed

    def as_mapping(self) -> dict[str, object]:
        """Return the canonical mapping, `entry_hash` included."""
        return {
            "entry_hash": self.entry_hash,
            "payload": self.payload,
            "previous_hash": self.previous_hash,
            "record_type": self.record_type,
            "recorded_at_utc": self.recorded_at_utc,
            "sequence": self.sequence,
        }

    def line_bytes(self) -> bytes:
        """Return the exact stored line, terminating LF included."""
        return canonical_json_bytes(self.as_mapping()) + b"\n"


@dataclass(frozen=True, slots=True)
class LedgerVerification:
    """The result of reading a ledger without modifying it."""

    path: str
    byte_count: int
    entry_count: int
    head_hash: str
    intact: bool
    problem: str | None

    def require_intact(self) -> None:
        """Raise `LedgerError` when the ledger is damaged."""
        if not self.intact:
            raise LedgerError(f"{self.path} is damaged: {self.problem}")


def _parse_line(line: bytes, *, number: int, expected_previous: str) -> LedgerEntry:
    """Parse and fully verify one stored line."""
    try:
        text = line.decode("utf-8")
    except UnicodeDecodeError as error:
        raise LedgerError(f"line {number} is not valid UTF-8: {error}") from error
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as error:
        raise LedgerError(f"line {number} is not valid JSON: {error}") from error
    if not isinstance(parsed, dict):
        raise LedgerError(
            f"line {number} is a {type(parsed).__name__}, not a JSON object"
        )
    if set(parsed) != ENTRY_FIELDS:
        missing = sorted(ENTRY_FIELDS - set(parsed))
        extra = sorted(set(parsed) - ENTRY_FIELDS)
        raise LedgerError(
            f"line {number} has the wrong envelope fields; missing={missing}, "
            f"extra={extra}"
        )

    payload = parsed["payload"]
    if not isinstance(payload, dict):
        raise LedgerError(f"line {number} payload is not a JSON object")
    sequence = parsed["sequence"]
    if isinstance(sequence, bool) or not isinstance(sequence, int):
        raise LedgerError(f"line {number} sequence is not an integer")
    if sequence != number - 1:
        raise LedgerError(
            f"line {number} records sequence {sequence}; sequence numbers must be "
            f"dense and start at zero, so {number - 1} was expected"
        )
    entry = LedgerEntry(
        record_type=_require_text(parsed["record_type"], f"line {number} record_type"),
        sequence=sequence,
        recorded_at_utc=_require_text(
            parsed["recorded_at_utc"], f"line {number} recorded_at_utc"
        ),
        payload_json=canonical_json_bytes(payload).decode("utf-8"),
        previous_hash=_require_sha256(
            parsed["previous_hash"], f"line {number} previous_hash"
        ),
        entry_hash=_require_sha256(parsed["entry_hash"], f"line {number} entry_hash"),
    )

    try:
        datetime.strptime(entry.recorded_at_utc, _TIMESTAMP_FORMAT)
    except ValueError as error:
        raise LedgerError(
            f"line {number} recorded_at_utc {entry.recorded_at_utc!r} is not a "
            f"whole-second UTC timestamp: {error}"
        ) from error
    if entry.line_bytes() != line + b"\n":
        raise LedgerError(
            f"line {number} is not canonical JSON; its bytes do not reproduce from "
            "the parsed entry"
        )
    if entry.previous_hash != expected_previous:
        raise LedgerError(
            f"line {number} chains to {entry.previous_hash}, but the preceding "
            f"entry hashes to {expected_previous}"
        )
    expected_hash = canonical_hash(entry.as_mapping(), self_field=ENTRY_HASH_FIELD)
    if entry.entry_hash != expected_hash:
        raise LedgerError(
            f"line {number} records entry_hash {entry.entry_hash}, recomputed "
            f"{expected_hash}"
        )
    if entry.entry_hash == GENESIS_HASH:
        raise LedgerError(f"line {number} collides with the genesis hash")
    return entry


def _scan(data: bytes) -> tuple[tuple[LedgerEntry, ...], str | None]:
    """Verify `data` and return the intact prefix plus the first problem."""
    if not data:
        return (), None
    lines = data.split(b"\n")
    trailing = lines.pop()

    entries: list[LedgerEntry] = []
    previous = GENESIS_HASH
    problem: str | None = None
    for index, line in enumerate(lines):
        try:
            entry = _parse_line(line, number=index + 1, expected_previous=previous)
        except (LedgerError, ManifestError) as error:
            problem = str(error)
            break
        entries.append(entry)
        previous = entry.entry_hash

    if problem is None and trailing:
        problem = (
            f"line {len(lines) + 1} is a torn trailing write of {len(trailing)} "
            "bytes with no terminating newline"
        )
    return tuple(entries), problem


def verify_ledger(path: Path | str) -> LedgerVerification:
    """Verify the chain at `path` and report what was found.

    A missing file is an empty, intact ledger. Damage is reported, never
    repaired: the file is opened read-only and its bytes are left untouched.
    """
    target = Path(path)
    data = target.read_bytes() if target.is_file() else b""
    entries, problem = _scan(data)
    return LedgerVerification(
        path=str(target),
        byte_count=len(data),
        entry_count=len(entries),
        head_hash=entries[-1].entry_hash if entries else GENESIS_HASH,
        intact=problem is None,
        problem=problem,
    )


def read_entries(path: Path | str) -> tuple[LedgerEntry, ...]:
    """Return every verified entry, raising `LedgerError` on any damage."""
    target = Path(path)
    data = target.read_bytes() if target.is_file() else b""
    entries, problem = _scan(data)
    if problem is not None:
        raise LedgerError(f"{target} is damaged: {problem}")
    return entries


if sys.platform == "win32":  # pragma: no cover - exercised on Windows only
    import msvcrt

    def _try_lock(fd: int) -> bool:
        try:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        except OSError:
            return False
        return True

    def _unlock(fd: int) -> None:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)

else:  # pragma: no cover - exercised on POSIX only
    import fcntl

    def _try_lock(fd: int) -> bool:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return False
        return True

    def _unlock(fd: int) -> None:
        fcntl.flock(fd, fcntl.LOCK_UN)


@contextmanager
def _exclusive_lock(path: Path) -> Iterator[None]:
    """Serialize appenders across processes using a sidecar lock file.

    A separate lock file is used so the lock never depends on the ledger file
    existing, and so a crashed writer releases it when the operating system
    closes the handle.
    """
    lock_path = path.with_name(path.name + LOCK_SUFFIX)
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
        while True:
            os.lseek(descriptor, 0, os.SEEK_SET)
            if _try_lock(descriptor):
                break
            if time.monotonic() >= deadline:
                raise LedgerError(
                    f"could not acquire {lock_path} within "
                    f"{LOCK_TIMEOUT_SECONDS} seconds"
                )
            time.sleep(_LOCK_POLL_SECONDS)
        try:
            yield
        finally:
            _unlock(descriptor)
    finally:
        os.close(descriptor)


def append_entry(
    path: Path | str,
    *,
    record_type: str,
    payload: Mapping[str, object],
    recorded_at_utc: datetime | None = None,
) -> LedgerEntry:
    """Append one entry and return it.

    The whole existing chain is verified under an exclusive cross-process lock
    before anything is written. A damaged ledger raises `LedgerError` and is
    left byte-for-byte as it was found. The appended bytes are flushed and
    fsynced before the lock is released, so a following reader in another
    process sees a complete line or no line at all.
    """
    target = Path(path)
    _require_text(record_type, "record_type")
    if not isinstance(payload, Mapping):
        raise LedgerError(f"payload must be a mapping, got {type(payload).__name__}")
    recorded = _format_timestamp(recorded_at_utc)
    payload_json = canonical_json_bytes(payload).decode("utf-8")

    with _exclusive_lock(target):
        data = target.read_bytes() if target.is_file() else b""
        entries, problem = _scan(data)
        if problem is not None:
            raise LedgerError(
                f"{target} is damaged and will not be appended to: {problem}"
            )

        draft = LedgerEntry(
            record_type=record_type,
            sequence=len(entries),
            recorded_at_utc=recorded,
            payload_json=payload_json,
            previous_hash=entries[-1].entry_hash if entries else GENESIS_HASH,
            entry_hash="",
        )
        entry = replace(
            draft,
            entry_hash=canonical_hash(draft.as_mapping(), self_field=ENTRY_HASH_FIELD),
        )
        with open(target, "ab") as handle:
            handle.write(entry.line_bytes())
            handle.flush()
            os.fsync(handle.fileno())
    return entry
