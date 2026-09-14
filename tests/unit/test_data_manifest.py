"""Synthetic data-manifest tests. No real market data, no network access."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import UTC, datetime, timedelta

import pytest

from aqt.data.bars import BAR_INTERVAL, Bar, BarSeries
from aqt.data.manifest import (
    AVAILABLE,
    BARS_ENCODING_MAGIC,
    PROTOCOL_PARTITIONS,
    UNAVAILABLE,
    AvailabilityRecord,
    Gap,
    ManifestError,
    PartitionManifest,
    RawArtifact,
    available,
    build_composite_manifest,
    build_partition_manifest,
    canonical_hash,
    canonical_json_bytes,
    encode_bar_series,
    sealed_partition_reference,
    unavailable,
    verify_composite_manifest,
    verify_partition_manifest,
)

_WINDOW_START = datetime(2024, 1, 1, tzinfo=UTC)
_WINDOW_END = datetime(2024, 1, 2, tzinfo=UTC)
_PARSER_HASH = "a" * 64
_RAW_BYTES = b"raw-bars-v1"
_RAW_HASH = hashlib.sha256(_RAW_BYTES).hexdigest()
_FEE_HASH = "c" * 64


def _ts(hour: int) -> datetime:
    return _WINDOW_START + timedelta(hours=hour)


def _bar(hour: int, *, close: float = 105.0, interval: timedelta = BAR_INTERVAL) -> Bar:
    return Bar(
        open_time=_ts(hour),
        open=100.0,
        high=110.0,
        low=90.0,
        close=close,
        volume=10.0,
        interval=interval,
    )


def _series(bars: tuple[Bar, ...] | None = None, symbol: str = "BTCUSDT") -> BarSeries:
    return BarSeries(symbol=symbol, bars=bars or tuple(_bar(hour) for hour in range(4)))


def _availability() -> dict[str, AvailabilityRecord]:
    return {
        "fees": available(_FEE_HASH, _WINDOW_START),
        "exchange_filters": available(_FEE_HASH, _WINDOW_START),
        "symbol_status": unavailable("no point-in-time status snapshot archived"),
    }


def _manifest(
    *,
    partition: str = "exploration",
    series: BarSeries | None = None,
    raw_artifacts: tuple[RawArtifact, ...] | None = None,
    parser_code_sha256: str = _PARSER_HASH,
    gaps: tuple[Gap, ...] = (),
) -> PartitionManifest:
    return build_partition_manifest(
        partition=partition,
        series=series or _series(),
        raw_artifacts=raw_artifacts
        or (RawArtifact(name="BTCUSDT-1h-2024-01.csv", content=_RAW_BYTES),),
        parser_code_sha256=parser_code_sha256,
        window_start_utc=_WINDOW_START,
        window_end_exclusive_utc=_WINDOW_END,
        gaps=gaps,
        **_availability(),
    )


# ---------------------------------------------------------------------------
# Acceptance 1: canonical bytes are repeatable and reject floats
# ---------------------------------------------------------------------------


def test_canonical_bytes_sort_keys_recursively_and_stay_compact() -> None:
    payload = {"b": 1, "a": {"d": [3, 2], "c": True}}
    encoded = canonical_json_bytes(payload)
    assert encoded == b'{"a":{"c":true,"d":[3,2]},"b":1}'
    assert canonical_json_bytes(json.loads(encoded.decode("utf-8"))) == encoded


@pytest.mark.parametrize("value", [1.5, math.nan, math.inf, -math.inf])
def test_canonical_bytes_reject_every_float(value: float) -> None:
    with pytest.raises(ManifestError, match="rejects all"):
        canonical_json_bytes({"x": value})


def test_canonical_hash_excludes_the_self_hash_field() -> None:
    body = {"manifest_type": "t", "value": 1}
    digest = canonical_hash(body)
    assert canonical_hash({**body, "manifest_sha256": digest}) == digest


def test_manifest_construction_is_repeatable() -> None:
    assert _manifest().manifest_sha256 == _manifest().manifest_sha256


def test_manifest_json_is_float_free() -> None:
    assert canonical_json_bytes(_manifest().as_mapping())


# ---------------------------------------------------------------------------
# Acceptance 2: hash sensitivity
# ---------------------------------------------------------------------------


def test_encoding_is_versioned_and_declares_type_and_shape() -> None:
    encoded = encode_bar_series(_series())
    assert encoded.startswith(BARS_ENCODING_MAGIC)
    assert b"binary64" in encoded[:24]
    assert len(encoded) == 8 + 4 + 8 + 8 + 8 + 4 + len(b"BTCUSDT") + 4 * 48


def test_parsed_hash_changes_when_a_value_changes() -> None:
    changed = _series(
        tuple(_bar(hour, close=105.5 if hour == 2 else 105.0) for hour in range(4))
    )
    assert encode_bar_series(_series()) != encode_bar_series(changed)


def test_parsed_hash_changes_when_a_timestamp_changes() -> None:
    shifted = _series(tuple(_bar(hour) for hour in range(1, 5)))
    assert encode_bar_series(_series()) != encode_bar_series(shifted)


def test_parsed_hash_changes_when_the_interval_changes() -> None:
    daily = timedelta(days=1)
    series = BarSeries(
        symbol="BTCUSDT",
        bars=(_bar(0, interval=daily),),
        interval=daily,
    )
    hourly = BarSeries(symbol="BTCUSDT", bars=(_bar(0),))
    assert encode_bar_series(series) != encode_bar_series(hourly)


def test_manifest_hash_changes_when_the_parser_hash_changes() -> None:
    assert (
        _manifest().manifest_sha256
        != _manifest(parser_code_sha256="d" * 64).manifest_sha256
    )


def test_manifest_hash_changes_when_a_raw_hash_changes() -> None:
    other = (RawArtifact(name="BTCUSDT-1h-2024-01.csv", content=b"other raw bytes"),)
    assert _manifest().manifest_sha256 != _manifest(raw_artifacts=other).manifest_sha256


def test_manifest_hash_changes_when_a_gap_is_declared() -> None:
    gapped = _manifest(
        series=_series(tuple(_bar(hour) for hour in (0, 1, 3))),
        gaps=(Gap(start=_ts(2), end=_ts(3)),),
    )
    ungapped = _manifest(series=_series(tuple(_bar(hour) for hour in (0, 1, 3))))
    assert gapped.manifest_sha256 != ungapped.manifest_sha256


# ---------------------------------------------------------------------------
# Acceptance 3: lineage
# ---------------------------------------------------------------------------


def test_partition_lineage_links_raw_parser_and_parsed_identity() -> None:
    series = _series()
    manifest = _manifest(series=series)
    assert [artifact.sha256 for artifact in manifest.raw_artifacts] == [_RAW_HASH]
    assert manifest.parser_code_sha256 == _PARSER_HASH
    assert (
        manifest.parsed_sha256 == hashlib.sha256(encode_bar_series(series)).hexdigest()
    )
    assert manifest.bar_count == len(series.bars)
    verify_partition_manifest(manifest, series=series)


def test_raw_artifact_identity_is_computed_from_exact_bytes() -> None:
    artifact = RawArtifact(name="bars.csv", content=_RAW_BYTES)
    changed = RawArtifact(name="bars.csv", content=_RAW_BYTES + b"\n")
    assert artifact.sha256 == hashlib.sha256(_RAW_BYTES).hexdigest()
    assert artifact.byte_count == len(_RAW_BYTES)
    assert changed.sha256 != artifact.sha256


def test_raw_artifact_rejects_caller_asserted_metadata() -> None:
    with pytest.raises(TypeError):
        RawArtifact(name="bars.csv", sha256=_RAW_HASH, byte_count=1)  # type: ignore[call-arg]


def test_verification_detects_a_tampered_field() -> None:
    manifest = _manifest()
    tampered = PartitionManifest(**{**vars_of(manifest), "bar_count": 99})
    with pytest.raises(ManifestError, match="hash mismatch"):
        verify_partition_manifest(tampered)


def test_verification_rejects_rehashed_semantically_invalid_fields() -> None:
    manifest = _manifest()
    invalid = PartitionManifest(
        **{**vars_of(manifest), "bar_count": 99, "manifest_sha256": ""}
    )
    rehashed = PartitionManifest(
        **{**vars_of(invalid), "manifest_sha256": canonical_hash(invalid.as_mapping())}
    )
    with pytest.raises(ManifestError, match="bar count"):
        verify_partition_manifest(rehashed, series=_series())


def test_partition_builder_rejects_non_hourly_series() -> None:
    two_hours = timedelta(hours=2)
    series = BarSeries(
        symbol="BTCUSDT",
        bars=(_bar(0, interval=two_hours),),
        interval=two_hours,
    )
    with pytest.raises(ManifestError, match="require 1h bars"):
        build_partition_manifest(
            partition="exploration",
            series=series,
            raw_artifacts=(RawArtifact("r.csv", b"raw"),),
            parser_code_sha256=_PARSER_HASH,
            window_start_utc=_WINDOW_START,
            window_end_exclusive_utc=_WINDOW_END,
            interval_label="2h",
            **_availability(),
        )


def test_verification_detects_bars_that_do_not_match_the_parsed_hash() -> None:
    manifest = _manifest()
    other = _series(tuple(_bar(hour, close=106.0) for hour in range(4)))
    with pytest.raises(ManifestError, match="parsed hash mismatch"):
        verify_partition_manifest(manifest, series=other)


def vars_of(manifest: PartitionManifest) -> dict[str, object]:
    return {field: getattr(manifest, field) for field in PartitionManifest.__slots__}


# ---------------------------------------------------------------------------
# Acceptance 4: lockbox refusal
# ---------------------------------------------------------------------------


def test_builder_refuses_the_lockbox_partition() -> None:
    with pytest.raises(ManifestError, match="refuses the lockbox partition"):
        _manifest(partition="lockbox")


def test_verifier_refuses_the_lockbox_partition() -> None:
    manifest = _manifest()
    lockbox = PartitionManifest(**{**vars_of(manifest), "partition": "lockbox"})
    with pytest.raises(ManifestError, match="refuses the lockbox partition"):
        verify_partition_manifest(lockbox)


def test_sealed_reference_exposes_no_raw_lockbox_identity() -> None:
    sealed = sealed_partition_reference(
        partition="lockbox",
        symbol="BTCUSDT",
        interval_label="1h",
        window_start_utc=datetime(2025, 6, 1, tzinfo=UTC),
        window_end_exclusive_utc=datetime(2026, 9, 1, tzinfo=UTC),
        manifest_sha256="f" * 64,
    )
    keys = set(sealed.as_mapping())
    assert keys.isdisjoint({"raw_artifacts", "parsed_sha256", "bar_count", "gaps"})


# ---------------------------------------------------------------------------
# Acceptance 5: gap and point-in-time constraints
# ---------------------------------------------------------------------------


def test_gap_must_be_a_non_empty_half_open_interval() -> None:
    with pytest.raises(ManifestError, match="half-open"):
        Gap(start=_ts(2), end=_ts(2))


def test_gaps_are_sorted_and_may_not_overlap() -> None:
    series = _series(tuple(_bar(hour) for hour in (0, 3)))
    manifest = _manifest(
        series=series,
        gaps=(Gap(start=_ts(2), end=_ts(3)), Gap(start=_ts(1), end=_ts(2))),
    )
    assert [gap.start for gap in manifest.gaps] == [_ts(1), _ts(2)]
    with pytest.raises(ManifestError, match="overlap"):
        _manifest(
            series=series,
            gaps=(Gap(start=_ts(1), end=_ts(3)), Gap(start=_ts(2), end=_ts(3))),
        )


def test_an_observed_bar_may_not_fall_inside_a_declared_gap() -> None:
    with pytest.raises(ManifestError, match="falls inside declared gap"):
        _manifest(gaps=(Gap(start=_ts(2), end=_ts(3)),))


def test_a_declared_gap_may_not_leave_the_window() -> None:
    with pytest.raises(ManifestError, match="leaves the partition window"):
        _manifest(gaps=(Gap(start=_ts(-2), end=_ts(-1)),))


def test_bars_may_not_leave_the_declared_window() -> None:
    with pytest.raises(ManifestError, match="leaves the declared window"):
        build_partition_manifest(
            partition="exploration",
            series=_series(),
            raw_artifacts=(RawArtifact(name="r.csv", content=b"r"),),
            parser_code_sha256=_PARSER_HASH,
            window_start_utc=_ts(1),
            window_end_exclusive_utc=_WINDOW_END,
            **_availability(),
        )


def test_an_available_record_requires_a_source_hash_and_as_of_time() -> None:
    with pytest.raises(ManifestError, match="requires both"):
        AvailabilityRecord(status=AVAILABLE, source_sha256=_FEE_HASH)


def test_an_unavailable_record_requires_a_reason() -> None:
    with pytest.raises(ManifestError, match="availability reason"):
        AvailabilityRecord(status=UNAVAILABLE, reason="")


def test_point_in_time_records_may_not_come_from_the_window_future() -> None:
    with pytest.raises(ManifestError, match="may not be taken from the future"):
        build_partition_manifest(
            partition="exploration",
            series=_series(),
            raw_artifacts=(RawArtifact(name="r.csv", content=b"r"),),
            parser_code_sha256=_PARSER_HASH,
            window_start_utc=_WINDOW_START,
            window_end_exclusive_utc=_WINDOW_END,
            fees=available(_FEE_HASH, _ts(1)),
            exchange_filters=available(_FEE_HASH, _WINDOW_START),
            symbol_status=unavailable("not archived"),
        )


# ---------------------------------------------------------------------------
# Acceptance 6: composite coverage
# ---------------------------------------------------------------------------


def _composite_entries() -> tuple[object, ...]:
    return (
        _manifest(partition="exploration"),
        _manifest(partition="confirmation"),
        sealed_partition_reference(
            partition="lockbox",
            symbol="BTCUSDT",
            interval_label="1h",
            window_start_utc=datetime(2025, 6, 1, tzinfo=UTC),
            window_end_exclusive_utc=datetime(2026, 9, 1, tzinfo=UTC),
            manifest_sha256="f" * 64,
        ),
    )


def test_composite_requires_exactly_the_three_protocol_partitions() -> None:
    entries = _composite_entries()
    composite = build_composite_manifest(
        cycle_id="C1",
        protocol_sha256="d" * 64,
        partitions=entries,  # type: ignore[arg-type]
    )
    assert {entry.partition for entry in composite.partitions} == set(
        PROTOCOL_PARTITIONS
    )
    verify_composite_manifest(composite)
    with pytest.raises(ManifestError, match="missing="):
        build_composite_manifest(
            cycle_id="C1",
            protocol_sha256="d" * 64,
            partitions=entries[:2],  # type: ignore[arg-type]
        )


def test_composite_refuses_an_unsealed_lockbox_partition() -> None:
    manifest = _manifest()
    lockbox = PartitionManifest(**{**vars_of(manifest), "partition": "lockbox"})
    with pytest.raises(ManifestError, match="only as a"):
        build_composite_manifest(
            cycle_id="C1",
            protocol_sha256="d" * 64,
            partitions=(
                _manifest(partition="exploration"),
                _manifest(partition="confirmation"),
                lockbox,
            ),  # type: ignore[arg-type]
        )


def test_only_lockbox_may_use_a_sealed_reference() -> None:
    with pytest.raises(ManifestError, match="only the lockbox"):
        sealed_partition_reference(
            partition="exploration",
            symbol="BTCUSDT",
            interval_label="1h",
            window_start_utc=_WINDOW_START,
            window_end_exclusive_utc=_WINDOW_END,
            manifest_sha256="f" * 64,
        )


def test_composite_verifier_rejects_a_rehashed_invalid_header() -> None:
    composite = build_composite_manifest(
        cycle_id="C1",
        protocol_sha256="d" * 64,
        partitions=_composite_entries(),  # type: ignore[arg-type]
    )
    draft = type(composite)(
        cycle_id="",
        protocol_sha256="bad",
        partitions=composite.partitions,
        manifest_sha256="",
    )
    tampered = type(composite)(
        cycle_id=draft.cycle_id,
        protocol_sha256=draft.protocol_sha256,
        partitions=draft.partitions,
        manifest_sha256=canonical_hash(draft.as_mapping()),
    )
    with pytest.raises(ManifestError, match="cycle_id"):
        verify_composite_manifest(tampered)


def test_composite_requires_all_partitions_for_each_symbol() -> None:
    entries = list(_composite_entries())
    entries[1] = _manifest(partition="confirmation", series=_series(symbol="ETHUSDT"))
    with pytest.raises(ManifestError, match="requires exactly"):
        build_composite_manifest(
            cycle_id="C1", protocol_sha256="d" * 64, partitions=entries
        )  # type: ignore[arg-type]


def test_composite_verification_recomputes_embedded_hashes() -> None:
    composite = build_composite_manifest(
        cycle_id="C1",
        protocol_sha256="d" * 64,
        partitions=_composite_entries(),  # type: ignore[arg-type]
    )
    broken = tuple(
        PartitionManifest(**{**vars_of(entry), "bar_count": 99})
        if isinstance(entry, PartitionManifest)
        else entry
        for entry in composite.partitions
    )
    tampered = type(composite)(
        cycle_id=composite.cycle_id,
        protocol_sha256=composite.protocol_sha256,
        partitions=broken,
        manifest_sha256=composite.manifest_sha256,
    )
    with pytest.raises(ManifestError, match="hash mismatch"):
        verify_composite_manifest(tampered)


def test_composite_never_carries_raw_lockbox_identity() -> None:
    composite = build_composite_manifest(
        cycle_id="C1",
        protocol_sha256="d" * 64,
        partitions=_composite_entries(),  # type: ignore[arg-type]
    )
    mapping = composite.as_mapping()
    lockbox_entry = next(
        entry
        for entry in mapping["partitions"]  # type: ignore[index]
        if entry["partition"] == "lockbox"
    )
    assert set(lockbox_entry).isdisjoint({"raw_artifacts", "parsed_sha256", "gaps"})
