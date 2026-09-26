"""Severity routing, secret redaction, and local sinks (roadmap Task 19).

Constitution section 19 requires alerting before shadow; section 26 requires
append-only, tamper-evident logs; section 28 forbids secrets in logs.

- A router must have at least one sink that receives CRITICAL events, or it
  refuses to start: a critical event can never be dropped silently.
- Every event passes a redaction step before any sink sees it. A field whose
  name or value looks like a credential is replaced, and a separate REDACTION
  event records which field was replaced (never the value).
- Sinks are local only: a text stream (stdout in practice) and the
  hash-chained ledger of `aqt.core.ledger`, which verifies the whole chain
  before every append. External channels need credentials and network access,
  both out of scope until the deployment protocol names them.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path
from typing import Final, Protocol, TextIO

from aqt.core.ledger import append_entry
from aqt.data.manifest import canonical_json_bytes
from aqt.monitoring.events import Event, EventKind, Severity

__all__ = [
    "LEDGER_RECORD_TYPE",
    "REDACTED",
    "AlertConfigError",
    "AlertRouter",
    "LedgerSink",
    "Sink",
    "StreamSink",
    "redact",
]

LEDGER_RECORD_TYPE: Final[str] = "aqt.monitoring.event.v1"
REDACTED: Final[str] = "[REDACTED]"

_SECRET_NAME: Final = re.compile(
    r"(api[_-]?key|secret|token|password|passphrase|signature|private[_-]?key)",
    re.IGNORECASE,
)
_SECRET_VALUE: Final = (
    # A Binance-style key: 64 letters and digits that are not a lowercase hex
    # SHA-256 digest, which this project logs legitimately and often.
    re.compile(r"(?=[A-Za-z0-9]{64}\b)(?![0-9a-f]{64}\b)[A-Za-z0-9]{64}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bBearer\s+\S+", re.IGNORECASE),
)


class AlertConfigError(RuntimeError):
    """Raised when the alerting configuration could drop a critical event."""


class Sink(Protocol):
    min_severity: Severity

    def write(self, event: Event) -> None: ...


class StreamSink:
    """One canonical JSON line per event on a text stream."""

    def __init__(self, stream: TextIO, min_severity: Severity) -> None:
        self.stream = stream
        self.min_severity = min_severity

    def write(self, event: Event) -> None:
        self.stream.write(canonical_json_bytes(event.as_mapping()).decode() + "\n")
        self.stream.flush()


class LedgerSink:
    """Append each event to a hash-chained ledger file."""

    def __init__(self, path: Path, min_severity: Severity) -> None:
        self.path = path
        self.min_severity = min_severity

    def write(self, event: Event) -> None:
        append_entry(
            self.path,
            record_type=LEDGER_RECORD_TYPE,
            payload=event.as_mapping(),
            recorded_at_utc=event.at,
        )


def redact(event: Event) -> tuple[Event, tuple[str, ...]]:
    """Return the event with credential-shaped fields replaced, and their names."""
    fields = dict(event.fields)
    replaced: list[str] = []
    for name, value in fields.items():
        suspicious = bool(_SECRET_NAME.search(name)) or (
            isinstance(value, str) and any(p.search(value) for p in _SECRET_VALUE)
        )
        if suspicious and value is not None:
            fields[name] = REDACTED
            replaced.append(name)
    if not replaced:
        return event, ()
    return Event(event.kind, event.severity, event.at, fields), tuple(replaced)


class AlertRouter:
    """Route each event to every sink whose minimum severity it meets."""

    def __init__(self, sinks: Sequence[Sink]) -> None:
        # CRITICAL is the top severity, so every sink receives it: the only way
        # to drop a critical event is to have no sink at all.
        if not sinks:
            raise AlertConfigError(
                "no sink receives CRITICAL events; alerting must exist before "
                "the loop can run (Constitution section 19)"
            )
        self._sinks = tuple(sinks)

    def emit(self, event: Event) -> Event:
        """Redact, then deliver. A sink failure propagates; nothing is swallowed."""
        clean, replaced = redact(event)
        if replaced:
            self._deliver(
                Event(
                    EventKind.REDACTION,
                    Severity.WARNING,
                    event.at,
                    {"event_kind": str(event.kind), "fields": ",".join(replaced)},
                )
            )
        self._deliver(clean)
        return clean

    def _deliver(self, event: Event) -> None:
        for sink in self._sinks:
            if event.severity.rank >= sink.min_severity.rank:
                sink.write(event)
