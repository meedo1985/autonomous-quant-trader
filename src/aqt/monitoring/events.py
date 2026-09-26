"""Typed operational events (roadmap Task 19).

Every event is one kind, one severity, one UTC timestamp, and a flat mapping
of string, integer, boolean, or null fields. Floats are not allowed, so every
event serializes to canonical JSON (`schemas/HASH_CANONICALIZATION_v1.md`)
and round-trips exactly.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from aqt.data.bars import require_utc

__all__ = ["Event", "EventError", "EventKind", "FieldValue", "Severity"]

FieldValue = str | int | bool | None

_TIME_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%S.%fZ"


class EventError(ValueError):
    """Raised for an event that cannot be represented exactly."""


class Severity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

    @property
    def rank(self) -> int:
        return list(Severity).index(self)


class EventKind(StrEnum):
    STARTUP = "STARTUP"
    SHUTDOWN = "SHUTDOWN"
    STATE_TRANSITION = "STATE_TRANSITION"  # section 22: every transition is logged
    ORDER = "ORDER"
    RECONCILIATION = "RECONCILIATION"
    STALE_DATA = "STALE_DATA"
    CLOCK_SKEW = "CLOCK_SKEW"
    LOOP_LAG = "LOOP_LAG"
    REDACTION = "REDACTION"


@dataclass(frozen=True, slots=True)
class Event:
    kind: EventKind
    severity: Severity
    at: datetime
    fields: Mapping[str, FieldValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.kind, EventKind):
            raise EventError(f"kind must be an EventKind, got {self.kind!r}")
        if not isinstance(self.severity, Severity):
            raise EventError(f"severity must be a Severity, got {self.severity!r}")
        object.__setattr__(self, "at", require_utc(self.at, field_name="at"))
        checked: dict[str, FieldValue] = {}
        for key, value in self.fields.items():
            if not isinstance(key, str) or not key:
                raise EventError(f"field names must be non-empty strings: {key!r}")
            if value is not None and not isinstance(value, str | int | bool):
                raise EventError(f"field {key!r} has unsupported type {type(value)}")
            checked[key] = value
        object.__setattr__(self, "fields", MappingProxyType(checked))

    def as_mapping(self) -> dict[str, object]:
        return {
            "at": self.at.strftime(_TIME_FORMAT),
            "fields": dict(self.fields),
            "kind": str(self.kind),
            "severity": str(self.severity),
        }

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, object]) -> Event:
        if set(mapping) != {"at", "fields", "kind", "severity"}:
            raise EventError(f"unexpected event keys: {sorted(mapping)}")
        fields, at = mapping["fields"], mapping["at"]
        kind, severity = mapping["kind"], mapping["severity"]
        if not (
            isinstance(fields, Mapping)
            and isinstance(at, str)
            and isinstance(kind, str)
            and isinstance(severity, str)
        ):
            raise EventError("malformed event mapping")
        return cls(
            kind=EventKind(kind),
            severity=Severity(severity),
            at=datetime.strptime(at, _TIME_FORMAT).replace(tzinfo=UTC),
            fields=fields,
        )
