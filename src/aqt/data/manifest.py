"""Deterministic data manifests for the frozen Cycle-1 protocol.

This module implements the identity layer required by
`docs/RESEARCH_CONSTITUTION.md` section 6 ("full hash lineage;
point-in-time fees/filters/status where available") and section 27
(reproducibility and hash canonicalization) before any trial may bind a
`data_manifest_hash` under `protocols/protocol_v1.yaml`
`cycle_start_bindings`.

It records identities only. Nothing here accepts a hash, binds a cycle, or
enforces protocol state; that belongs to the protected pre-trial workflow.

Trust boundary
--------------
Constitution section 7 says only `lockbox_eval` reads lockbox data. The
builder and the verifier in this module therefore refuse the lockbox
partition before they look at any data. A lockbox partition may enter a
composite manifest only as a `SealedPartitionReference`, which carries a
partition name, a symbol, a declared window, and an opaque manifest hash --
never raw artifact hashes, parsed hashes, bar counts, or gaps.

Canonicalization
----------------
Manifest JSON follows `schemas/HASH_CANONICALIZATION_v1.md`: UTF-8, keys
sorted recursively, list order preserved, compact separators, the
self-referential hash field removed before hashing. Floating-point values are
rejected outright, including NaN and infinity, so no manifest identity can
depend on a repr or a rounding mode.

Parsed bars are identified by a versioned little-endian binary encoding with
an explicit type tag, shape, interval, timestamps, and binary64 OHLCV values,
so parsed identity never passes through JSON floats either.
"""

from __future__ import annotations

import hashlib
import json
import struct
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Final

from aqt.data.bars import BAR_INTERVAL, BAR_INTERVAL_LABEL, BarSeries, require_utc

__all__ = [
    "AVAILABLE",
    "BARS_ENCODING_MAGIC",
    "BARS_ENCODING_VERSION",
    "LOCKBOX_PARTITION",
    "PROTOCOL_PARTITIONS",
    "UNAVAILABLE",
    "AvailabilityRecord",
    "CompositeManifest",
    "Gap",
    "ManifestError",
    "PartitionEntry",
    "PartitionManifest",
    "RawArtifact",
    "SealedPartitionReference",
    "available",
    "build_composite_manifest",
    "build_partition_manifest",
    "canonical_hash",
    "canonical_json_bytes",
    "encode_bar_series",
    "sealed_partition_reference",
    "unavailable",
    "verify_composite_manifest",
    "verify_partition_manifest",
]

PROTOCOL_PARTITIONS: Final[tuple[str, str, str]] = (
    "exploration",
    "confirmation",
    "lockbox",
)
"""The three partitions declared by `protocols/protocol_v1.yaml`."""

LOCKBOX_PARTITION: Final[str] = "lockbox"

AVAILABLE: Final[str] = "AVAILABLE"
UNAVAILABLE: Final[str] = "UNAVAILABLE"

BARS_ENCODING_MAGIC: Final[bytes] = b"AQT-BARS"
BARS_ENCODING_VERSION: Final[int] = 1
_BARS_DTYPE_TAG: Final[bytes] = b"binary64"
_BARS_COLUMNS: Final[int] = 5

_SELF_HASH_FIELD: Final[str] = "manifest_sha256"
_HEX64: Final[str] = "0123456789abcdef"


class ManifestError(ValueError):
    """Raised when input violates the manifest identity rules."""


# ---------------------------------------------------------------------------
# Canonical JSON
# ---------------------------------------------------------------------------


def _canonicalize(value: object, path: str) -> Any:
    """Return a JSON-ready value, rejecting floats and unsupported types."""
    if value is None or isinstance(value, bool | int | str):
        return value
    if isinstance(value, float):
        raise ManifestError(
            f"{path} is a float ({value!r}); manifest JSON rejects all "
            "floating-point values, including NaN and infinity"
        )
    if isinstance(value, Mapping):
        canonical: dict[str, Any] = {}
        for key in value:
            if not isinstance(key, str):
                raise ManifestError(f"{path} has a non-string key {key!r}")
            canonical[key] = _canonicalize(value[key], f"{path}.{key}")
        return {key: canonical[key] for key in sorted(canonical)}
    if isinstance(value, list | tuple):
        return [
            _canonicalize(item, f"{path}[{index}]") for index, item in enumerate(value)
        ]
    raise ManifestError(f"{path} has unsupported type {type(value).__name__}")


def canonical_json_bytes(value: Mapping[str, object]) -> bytes:
    """Serialize `value` under the frozen JSON canonicalization rules."""
    canonical = _canonicalize(value, "manifest")
    return json.dumps(
        canonical, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def canonical_hash(
    value: Mapping[str, object], *, self_field: str | None = _SELF_HASH_FIELD
) -> str:
    """Return the SHA-256 of `value` with its self-referential hash removed."""
    payload = dict(value)
    if self_field is not None:
        payload.pop(self_field, None)
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


# ---------------------------------------------------------------------------
# Shared validation helpers
# ---------------------------------------------------------------------------


def _require_sha256(value: str, name: str) -> str:
    if len(value) != 64 or any(char not in _HEX64 for char in value):
        raise ManifestError(f"{name} must be a lowercase 64-hex SHA-256, got {value!r}")
    return value


def _require_text(value: str, name: str) -> str:
    if not value or value.strip() != value:
        raise ManifestError(f"{name} must be non-empty and unpadded, got {value!r}")
    return value


def _require_partition(value: str) -> str:
    if value not in PROTOCOL_PARTITIONS:
        raise ManifestError(
            f"partition must be one of {PROTOCOL_PARTITIONS}, got {value!r}"
        )
    return value


def _refuse_lockbox(partition: str, operation: str) -> None:
    """Fail closed before any lockbox data is inspected."""
    if partition == LOCKBOX_PARTITION:
        raise ManifestError(
            f"{operation} refuses the lockbox partition; only aqt.lockbox_eval "
            "may read lockbox data, and it supplies a sealed reference"
        )


def _iso(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _require_whole_second_utc(value: datetime, name: str) -> datetime:
    moment = require_utc(value, field_name=name)
    if moment.microsecond:
        raise ManifestError(f"{name} must be a whole second, got {moment.isoformat()}")
    return moment


# ---------------------------------------------------------------------------
# Canonical parsed-bar encoding
# ---------------------------------------------------------------------------


def encode_bar_series(series: BarSeries) -> bytes:
    """Return the versioned binary encoding of `series`.

    Layout, all integers little-endian:

    * 8-byte magic `AQT-BARS`, then uint32 format version.
    * 8-byte dtype tag `binary64`, uint32 column count, uint32 row count.
    * uint64 bar interval in seconds.
    * uint32 symbol byte length, then the UTF-8 symbol.
    * per bar: int64 `open_time` in milliseconds since the Unix epoch, then
      open, high, low, close, and volume as binary64.
    """
    interval_seconds = int(series.interval.total_seconds())
    if series.interval != timedelta(seconds=interval_seconds):
        raise ManifestError(
            f"interval {series.interval} is not a whole number of seconds"
        )
    symbol = series.symbol.encode("utf-8")
    parts: list[bytes] = [
        BARS_ENCODING_MAGIC,
        struct.pack("<I", BARS_ENCODING_VERSION),
        _BARS_DTYPE_TAG,
        struct.pack("<II", _BARS_COLUMNS, len(series.bars)),
        struct.pack("<Q", interval_seconds),
        struct.pack("<I", len(symbol)),
        symbol,
    ]
    for bar in series.bars:
        epoch_us = int(round(bar.open_time.timestamp() * 1_000_000))
        epoch_ms, remainder = divmod(epoch_us, 1_000)
        if remainder:
            raise ManifestError(
                f"open_time {bar.open_time.isoformat()} is not a whole millisecond"
            )
        parts.append(
            struct.pack(
                "<q5d",
                epoch_ms,
                bar.open,
                bar.high,
                bar.low,
                bar.close,
                bar.volume,
            )
        )
    return b"".join(parts)


# ---------------------------------------------------------------------------
# Manifest components
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, init=False)
class RawArtifact:
    """One immutable source file identified by SHA-256 of its exact bytes."""

    name: str
    sha256: str
    byte_count: int

    def __init__(self, name: str, content: bytes) -> None:
        """Compute identity from one immutable byte snapshot."""
        _require_text(name, "raw artifact name")
        if not isinstance(content, bytes):
            raise ManifestError("raw artifact content must be exact bytes")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "sha256", hashlib.sha256(content).hexdigest())
        object.__setattr__(self, "byte_count", len(content))

    def as_mapping(self) -> dict[str, object]:
        return {
            "byte_count": self.byte_count,
            "name": self.name,
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class Gap:
    """A declared half-open UTC outage interval `[start, end)`.

    Constitution section 6 makes outages untradeable rather than silently
    filled, so a gap is declared data, not an inference.
    """

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        start = _require_whole_second_utc(self.start, "gap start")
        end = _require_whole_second_utc(self.end, "gap end")
        if end <= start:
            raise ManifestError(
                f"gap must be a non-empty half-open interval, got "
                f"[{start.isoformat()}, {end.isoformat()})"
            )
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)

    def contains(self, moment: datetime) -> bool:
        """True when `moment` lies in the half-open interval."""
        return self.start <= moment < self.end

    def as_mapping(self) -> dict[str, object]:
        return {"end_exclusive_utc": _iso(self.end), "start_utc": _iso(self.start)}


@dataclass(frozen=True, slots=True)
class AvailabilityRecord:
    """A point-in-time fee, filter, or symbol-status record.

    Either `AVAILABLE` with the source hash and the `as_of_utc` snapshot
    time, or `UNAVAILABLE` with a reason. There is no third, implicit state.
    """

    status: str
    source_sha256: str | None = None
    as_of_utc: datetime | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.status == AVAILABLE:
            if self.source_sha256 is None or self.as_of_utc is None:
                raise ManifestError(
                    "an AVAILABLE record requires both source_sha256 and as_of_utc"
                )
            if self.reason is not None:
                raise ManifestError("an AVAILABLE record must not carry a reason")
            _require_sha256(self.source_sha256, "availability source_sha256")
            object.__setattr__(
                self,
                "as_of_utc",
                _require_whole_second_utc(self.as_of_utc, "as_of_utc"),
            )
        elif self.status == UNAVAILABLE:
            if self.source_sha256 is not None or self.as_of_utc is not None:
                raise ManifestError(
                    "an UNAVAILABLE record must not carry a source hash or as_of_utc"
                )
            _require_text(self.reason or "", "availability reason")
        else:
            raise ManifestError(
                f"status must be {AVAILABLE!r} or {UNAVAILABLE!r}, got {self.status!r}"
            )

    def as_mapping(self) -> dict[str, object]:
        if self.status == AVAILABLE:
            assert self.as_of_utc is not None
            return {
                "as_of_utc": _iso(self.as_of_utc),
                "source_sha256": self.source_sha256,
                "status": AVAILABLE,
            }
        return {"reason": self.reason, "status": UNAVAILABLE}


def available(source_sha256: str, as_of_utc: datetime) -> AvailabilityRecord:
    """Build an `AVAILABLE` point-in-time record."""
    return AvailabilityRecord(
        status=AVAILABLE, source_sha256=source_sha256, as_of_utc=as_of_utc
    )


def unavailable(reason: str) -> AvailabilityRecord:
    """Build an `UNAVAILABLE` record with an explicit reason."""
    return AvailabilityRecord(status=UNAVAILABLE, reason=reason)


# ---------------------------------------------------------------------------
# Partition manifest
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PartitionManifest:
    """Identity and lineage for one symbol inside one protocol partition."""

    partition: str
    symbol: str
    interval_label: str
    window_start_utc: datetime
    window_end_exclusive_utc: datetime
    raw_artifacts: tuple[RawArtifact, ...]
    parser_code_sha256: str
    parsed_sha256: str
    bar_count: int
    first_open_time_utc: datetime
    last_open_time_utc: datetime
    gaps: tuple[Gap, ...]
    fees: AvailabilityRecord
    exchange_filters: AvailabilityRecord
    symbol_status: AvailabilityRecord
    manifest_sha256: str

    def as_mapping(self) -> dict[str, object]:
        """Return the canonical mapping, self-hash field included."""
        return {
            "bar_count": self.bar_count,
            "exchange_filters": self.exchange_filters.as_mapping(),
            "fees": self.fees.as_mapping(),
            "first_open_time_utc": _iso(self.first_open_time_utc),
            "gaps": [gap.as_mapping() for gap in self.gaps],
            "interval_label": self.interval_label,
            "last_open_time_utc": _iso(self.last_open_time_utc),
            "manifest_sha256": self.manifest_sha256,
            "manifest_type": "aqt.partition_manifest.v1",
            "parsed_sha256": self.parsed_sha256,
            "parser_code_sha256": self.parser_code_sha256,
            "partition": self.partition,
            "raw_artifacts": [artifact.as_mapping() for artifact in self.raw_artifacts],
            "symbol": self.symbol,
            "symbol_status": self.symbol_status.as_mapping(),
            "window_end_exclusive_utc": _iso(self.window_end_exclusive_utc),
            "window_start_utc": _iso(self.window_start_utc),
        }

    def sealed_reference(self) -> SealedPartitionReference:
        """Return the sealed form of this manifest, dropping all raw lineage."""
        return sealed_partition_reference(
            partition=self.partition,
            symbol=self.symbol,
            interval_label=self.interval_label,
            window_start_utc=self.window_start_utc,
            window_end_exclusive_utc=self.window_end_exclusive_utc,
            manifest_sha256=self.manifest_sha256,
        )


def _ordered_gaps(gaps: Iterable[Gap]) -> tuple[Gap, ...]:
    ordered = tuple(sorted(gaps, key=lambda gap: (gap.start, gap.end)))
    for previous, current in zip(ordered, ordered[1:], strict=False):
        if current.start < previous.end:
            raise ManifestError(
                f"declared gaps overlap: [{previous.start.isoformat()}, "
                f"{previous.end.isoformat()}) and [{current.start.isoformat()}, "
                f"{current.end.isoformat()})"
            )
    return ordered


def _replace_manifest_hash(draft: PartitionManifest, digest: str) -> PartitionManifest:
    return PartitionManifest(
        partition=draft.partition,
        symbol=draft.symbol,
        interval_label=draft.interval_label,
        window_start_utc=draft.window_start_utc,
        window_end_exclusive_utc=draft.window_end_exclusive_utc,
        raw_artifacts=draft.raw_artifacts,
        parser_code_sha256=draft.parser_code_sha256,
        parsed_sha256=draft.parsed_sha256,
        bar_count=draft.bar_count,
        first_open_time_utc=draft.first_open_time_utc,
        last_open_time_utc=draft.last_open_time_utc,
        gaps=draft.gaps,
        fees=draft.fees,
        exchange_filters=draft.exchange_filters,
        symbol_status=draft.symbol_status,
        manifest_sha256=digest,
    )


def build_partition_manifest(
    *,
    partition: str,
    series: BarSeries,
    raw_artifacts: Sequence[RawArtifact],
    parser_code_sha256: str,
    window_start_utc: datetime,
    window_end_exclusive_utc: datetime,
    fees: AvailabilityRecord,
    exchange_filters: AvailabilityRecord,
    symbol_status: AvailabilityRecord,
    gaps: Sequence[Gap] = (),
    interval_label: str = BAR_INTERVAL_LABEL,
) -> PartitionManifest:
    """Build a partition manifest; refuses the lockbox partition.

    The refusal happens before `series` is read, so a general caller cannot
    obtain raw lockbox identity through this API.
    """
    _require_partition(partition)
    _refuse_lockbox(partition, "build_partition_manifest")

    _require_sha256(parser_code_sha256, "parser_code_sha256")
    if series.interval != BAR_INTERVAL or interval_label != BAR_INTERVAL_LABEL:
        raise ManifestError(
            f"Cycle-1 manifests require {BAR_INTERVAL_LABEL} bars; got series "
            f"interval {series.interval} and label {interval_label!r}"
        )
    if not raw_artifacts:
        raise ManifestError("a partition manifest requires at least one raw artifact")
    ordered_artifacts = tuple(sorted(raw_artifacts, key=lambda item: item.name))
    names = [artifact.name for artifact in ordered_artifacts]
    if len(set(names)) != len(names):
        raise ManifestError("raw artifact names must be unique")

    start = _require_whole_second_utc(window_start_utc, "window_start_utc")
    end = _require_whole_second_utc(
        window_end_exclusive_utc, "window_end_exclusive_utc"
    )
    if end <= start:
        raise ManifestError(
            f"window must be a non-empty half-open interval, got "
            f"[{start.isoformat()}, {end.isoformat()})"
        )
    if series.start < start or series.end > end:
        raise ManifestError(
            f"{series.symbol} bars span [{series.start.isoformat()}, "
            f"{series.end.isoformat()}) which leaves the declared window "
            f"[{start.isoformat()}, {end.isoformat()})"
        )

    ordered_gaps = _ordered_gaps(gaps)
    for gap in ordered_gaps:
        if gap.start < start or gap.end > end:
            raise ManifestError(
                f"declared gap [{gap.start.isoformat()}, {gap.end.isoformat()}) "
                f"leaves the partition window"
            )
    for bar in series.bars:
        for gap in ordered_gaps:
            if gap.contains(bar.open_time):
                raise ManifestError(
                    f"bar at {bar.open_time.isoformat()} falls inside declared gap "
                    f"[{gap.start.isoformat()}, {gap.end.isoformat()})"
                )

    for name, record in (
        ("fees", fees),
        ("exchange_filters", exchange_filters),
        ("symbol_status", symbol_status),
    ):
        if record.status == AVAILABLE:
            assert record.as_of_utc is not None
            if record.as_of_utc > start:
                raise ManifestError(
                    f"{name} as_of_utc {record.as_of_utc.isoformat()} is after the "
                    f"partition start {start.isoformat()}; a point-in-time record "
                    "may not be taken from the future of the window it governs"
                )

    draft = PartitionManifest(
        partition=partition,
        symbol=series.symbol,
        interval_label=interval_label,
        window_start_utc=start,
        window_end_exclusive_utc=end,
        raw_artifacts=ordered_artifacts,
        parser_code_sha256=parser_code_sha256,
        parsed_sha256=hashlib.sha256(encode_bar_series(series)).hexdigest(),
        bar_count=len(series.bars),
        first_open_time_utc=series.bars[0].open_time,
        last_open_time_utc=series.bars[-1].open_time,
        gaps=ordered_gaps,
        fees=fees,
        exchange_filters=exchange_filters,
        symbol_status=symbol_status,
        manifest_sha256="",
    )
    result = _replace_manifest_hash(draft, canonical_hash(draft.as_mapping()))
    _validate_partition_manifest(result, series=series)
    return result


def _validate_partition_manifest(
    manifest: PartitionManifest, *, series: BarSeries | None
) -> None:
    """Validate semantic invariants independently of the self-hash."""
    _require_partition(manifest.partition)
    _refuse_lockbox(manifest.partition, "verify_partition_manifest")
    _require_text(manifest.symbol, "symbol")
    if manifest.interval_label != BAR_INTERVAL_LABEL:
        raise ManifestError(
            f"Cycle-1 manifests require interval_label {BAR_INTERVAL_LABEL!r}"
        )
    start = _require_whole_second_utc(manifest.window_start_utc, "window_start_utc")
    end = _require_whole_second_utc(
        manifest.window_end_exclusive_utc, "window_end_exclusive_utc"
    )
    if end <= start:
        raise ManifestError("partition window must be a non-empty half-open interval")
    _require_sha256(manifest.parser_code_sha256, "parser_code_sha256")
    _require_sha256(manifest.parsed_sha256, "parsed_sha256")
    if manifest.bar_count <= 0:
        raise ManifestError("bar_count must be positive")
    first = _require_whole_second_utc(
        manifest.first_open_time_utc, "first_open_time_utc"
    )
    last = _require_whole_second_utc(manifest.last_open_time_utc, "last_open_time_utc")
    if first > last or first < start or last + BAR_INTERVAL > end:
        raise ManifestError("recorded bar coverage leaves the partition window")

    if not manifest.raw_artifacts:
        raise ManifestError("a partition manifest requires at least one raw artifact")
    if any(not isinstance(item, RawArtifact) for item in manifest.raw_artifacts):
        raise ManifestError("raw_artifacts must contain RawArtifact values")
    ordered_artifacts = tuple(
        sorted(manifest.raw_artifacts, key=lambda item: item.name)
    )
    if manifest.raw_artifacts != ordered_artifacts:
        raise ManifestError("raw_artifacts are not in canonical name order")
    if len({item.name for item in ordered_artifacts}) != len(ordered_artifacts):
        raise ManifestError("raw artifact names must be unique")

    if any(not isinstance(gap, Gap) for gap in manifest.gaps):
        raise ManifestError("gaps must contain Gap values")
    ordered_gaps = _ordered_gaps(manifest.gaps)
    if manifest.gaps != ordered_gaps:
        raise ManifestError("gaps are not in canonical order")
    for gap in ordered_gaps:
        if gap.start < start or gap.end > end:
            raise ManifestError("a declared gap leaves the partition window")

    for name, record in (
        ("fees", manifest.fees),
        ("exchange_filters", manifest.exchange_filters),
        ("symbol_status", manifest.symbol_status),
    ):
        if not isinstance(record, AvailabilityRecord):
            raise ManifestError(f"{name} must be an AvailabilityRecord")
        if record.status == AVAILABLE:
            assert record.as_of_utc is not None
            if record.as_of_utc > start:
                raise ManifestError(f"{name} snapshot is from the partition future")

    if series is None:
        return
    if series.interval != BAR_INTERVAL:
        raise ManifestError("Cycle-1 manifests require a 1h BarSeries")
    if series.symbol != manifest.symbol:
        raise ManifestError("series symbol does not match manifest symbol")
    if len(series.bars) != manifest.bar_count:
        raise ManifestError("series bar count does not match manifest bar_count")
    if series.bars[0].open_time != first or series.bars[-1].open_time != last:
        raise ManifestError("series coverage does not match manifest coverage")
    if series.start < start or series.end > end:
        raise ManifestError("series bars leave the partition window")
    for bar in series.bars:
        if any(gap.contains(bar.open_time) for gap in ordered_gaps):
            raise ManifestError("an observed bar falls inside a declared gap")
    parsed = hashlib.sha256(encode_bar_series(series)).hexdigest()
    if parsed != manifest.parsed_sha256:
        raise ManifestError("parsed hash mismatch against the supplied series")


def verify_partition_manifest(
    manifest: PartitionManifest, *, series: BarSeries | None = None
) -> None:
    """Recompute the manifest hash; refuses the lockbox partition.

    When `series` is supplied, the parsed hash is recomputed from the bars, so
    the declared lineage is checked against real data rather than asserted.
    """
    _validate_partition_manifest(manifest, series=series)
    _require_sha256(manifest.manifest_sha256, "manifest_sha256")
    expected = canonical_hash(manifest.as_mapping())
    if expected != manifest.manifest_sha256:
        raise ManifestError(
            f"partition manifest hash mismatch: recorded "
            f"{manifest.manifest_sha256}, recomputed {expected}"
        )


# ---------------------------------------------------------------------------
# Sealed reference and composite manifest
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SealedPartitionReference:
    """An opaque partition identity carrying no raw lineage.

    This is the only form in which the lockbox partition may enter a
    composite manifest. It deliberately omits raw artifact hashes, the parsed
    hash, the bar count, and gap declarations.
    """

    partition: str
    symbol: str
    interval_label: str
    window_start_utc: datetime
    window_end_exclusive_utc: datetime
    manifest_sha256: str

    def __post_init__(self) -> None:
        if self.partition != LOCKBOX_PARTITION:
            raise ManifestError("only the lockbox partition may use a sealed reference")
        _require_text(self.symbol, "symbol")
        if self.interval_label != BAR_INTERVAL_LABEL:
            raise ManifestError("Cycle-1 sealed references require interval_label '1h'")
        _require_sha256(self.manifest_sha256, "manifest_sha256")
        start = _require_whole_second_utc(self.window_start_utc, "window_start_utc")
        end = _require_whole_second_utc(
            self.window_end_exclusive_utc, "window_end_exclusive_utc"
        )
        if end <= start:
            raise ManifestError("sealed window must be a non-empty half-open interval")
        object.__setattr__(self, "window_start_utc", start)
        object.__setattr__(self, "window_end_exclusive_utc", end)

    def as_mapping(self) -> dict[str, object]:
        return {
            "interval_label": self.interval_label,
            "manifest_sha256": self.manifest_sha256,
            "manifest_type": "aqt.sealed_partition_reference.v1",
            "partition": self.partition,
            "symbol": self.symbol,
            "window_end_exclusive_utc": _iso(self.window_end_exclusive_utc),
            "window_start_utc": _iso(self.window_start_utc),
        }


def sealed_partition_reference(
    *,
    partition: str,
    symbol: str,
    interval_label: str,
    window_start_utc: datetime,
    window_end_exclusive_utc: datetime,
    manifest_sha256: str,
) -> SealedPartitionReference:
    """Build a sealed reference from an already-computed manifest hash.

    This is the only lockbox-admitting entry point: it accepts a hash, never
    raw bytes, bars, or a parser.
    """
    return SealedPartitionReference(
        partition=partition,
        symbol=symbol,
        interval_label=interval_label,
        window_start_utc=window_start_utc,
        window_end_exclusive_utc=window_end_exclusive_utc,
        manifest_sha256=manifest_sha256,
    )


PartitionEntry = PartitionManifest | SealedPartitionReference


@dataclass(frozen=True, slots=True)
class CompositeManifest:
    """The cycle-level manifest over all three protocol partitions."""

    cycle_id: str
    protocol_sha256: str
    partitions: tuple[PartitionEntry, ...]
    manifest_sha256: str

    def as_mapping(self) -> dict[str, object]:
        return {
            "cycle_id": self.cycle_id,
            "manifest_sha256": self.manifest_sha256,
            "manifest_type": "aqt.composite_manifest.v1",
            "partitions": [entry.as_mapping() for entry in self.partitions],
            "protocol_sha256": self.protocol_sha256,
        }


def _entry_key(entry: PartitionEntry) -> tuple[str, str]:
    return (entry.partition, entry.symbol)


def _ordered_entries(entries: Sequence[PartitionEntry]) -> tuple[PartitionEntry, ...]:
    if any(
        not isinstance(entry, PartitionManifest | SealedPartitionReference)
        for entry in entries
    ):
        raise ManifestError("composite entries have an unsupported type")
    ordered = tuple(sorted(entries, key=_entry_key))
    keys = [_entry_key(entry) for entry in ordered]
    if len(set(keys)) != len(keys):
        raise ManifestError("composite entries must be unique per partition and symbol")
    symbols = {entry.symbol for entry in ordered}
    for symbol in symbols:
        present = {entry.partition for entry in ordered if entry.symbol == symbol}
        if present != set(PROTOCOL_PARTITIONS):
            missing = sorted(set(PROTOCOL_PARTITIONS) - present)
            extra = sorted(present - set(PROTOCOL_PARTITIONS))
            raise ManifestError(
                f"symbol {symbol!r} requires exactly the three protocol partitions; "
                f"missing={missing}, extra={extra}"
            )
    for entry in ordered:
        if entry.partition == LOCKBOX_PARTITION and not isinstance(
            entry, SealedPartitionReference
        ):
            raise ManifestError(
                "the lockbox partition may enter a composite only as a "
                "SealedPartitionReference"
            )
        if entry.partition != LOCKBOX_PARTITION and not isinstance(
            entry, PartitionManifest
        ):
            raise ManifestError("exploration and confirmation require full manifests")
    return ordered


def build_composite_manifest(
    *,
    cycle_id: str,
    protocol_sha256: str,
    partitions: Sequence[PartitionEntry],
) -> CompositeManifest:
    """Build the composite manifest over the three protocol partitions."""
    _require_text(cycle_id, "cycle_id")
    _require_sha256(protocol_sha256, "protocol_sha256")
    ordered = _ordered_entries(partitions)
    for entry in ordered:
        if isinstance(entry, PartitionManifest):
            verify_partition_manifest(entry)
        else:
            _require_sha256(entry.manifest_sha256, "manifest_sha256")
    draft = CompositeManifest(
        cycle_id=cycle_id,
        protocol_sha256=protocol_sha256,
        partitions=ordered,
        manifest_sha256="",
    )
    return CompositeManifest(
        cycle_id=cycle_id,
        protocol_sha256=protocol_sha256,
        partitions=ordered,
        manifest_sha256=canonical_hash(draft.as_mapping()),
    )


def verify_composite_manifest(manifest: CompositeManifest) -> None:
    """Recompute every embedded hash and the composite hash itself."""
    _require_text(manifest.cycle_id, "cycle_id")
    _require_sha256(manifest.protocol_sha256, "protocol_sha256")
    _require_sha256(manifest.manifest_sha256, "manifest_sha256")
    ordered = _ordered_entries(manifest.partitions)
    if ordered != manifest.partitions:
        raise ManifestError("composite partitions are not in canonical order")
    for entry in ordered:
        if isinstance(entry, PartitionManifest):
            verify_partition_manifest(entry)
    expected = canonical_hash(manifest.as_mapping())
    if expected != manifest.manifest_sha256:
        raise ManifestError(
            f"composite manifest hash mismatch: recorded "
            f"{manifest.manifest_sha256}, recomputed {expected}"
        )
