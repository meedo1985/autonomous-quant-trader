"""A synthetic experiment record built from Task 9 identities.

This proves that the manifest and code-identity hashes fit the frozen
`schemas/experiment.schema.json` shape. It records identities only: nothing
here accepts a hash, binds a real cycle, or writes a trial. The bars are
synthetic and the repository under test is a throwaway created by pytest.
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from aqt.core.code_identity import code_identity
from aqt.core.paths import REPOSITORY_ROOT
from aqt.data.bars import Bar, BarSeries
from aqt.data.manifest import (
    RawArtifact,
    available,
    build_composite_manifest,
    build_partition_manifest,
    sealed_partition_reference,
    unavailable,
    verify_composite_manifest,
)

_PARTITION_WINDOWS = {
    "exploration": (
        datetime(2017, 8, 17, tzinfo=UTC),
        datetime(2022, 1, 1, tzinfo=UTC),
    ),
    "confirmation": (
        datetime(2022, 1, 1, tzinfo=UTC),
        datetime(2025, 6, 1, tzinfo=UTC),
    ),
    "lockbox": (
        datetime(2025, 6, 1, tzinfo=UTC),
        datetime(2026, 9, 1, tzinfo=UTC),
    ),
}
_PARSER_HASH = "1" * 64
_FEE_HASH = "2" * 64


def _series(symbol: str, start: datetime) -> BarSeries:
    return BarSeries(
        symbol=symbol,
        bars=tuple(
            Bar(
                open_time=start + timedelta(hours=hour),
                open=100.0,
                high=110.0,
                low=90.0,
                close=105.0,
                volume=10.0,
            )
            for hour in range(24)
        ),
    )


def _partition(name: str) -> object:
    start, end = _PARTITION_WINDOWS[name]
    return build_partition_manifest(
        partition=name,
        series=_series("BTCUSDT", start),
        raw_artifacts=(
            RawArtifact(name=f"BTCUSDT-1h-{name}.csv", content=b"3" * 4096),
        ),
        parser_code_sha256=_PARSER_HASH,
        window_start_utc=start,
        window_end_exclusive_utc=end,
        fees=available(_FEE_HASH, start),
        exchange_filters=available(_FEE_HASH, start),
        symbol_status=unavailable("no point-in-time status snapshot archived"),
    )


@pytest.fixture
def synthetic_repo(tmp_path: Path) -> Path:
    """A throwaway repository so code identity never reads the real tree."""
    for relative, text in (
        ("pyproject.toml", '[project]\nname = "x"\n'),
        ("src/aqt/__init__.py", ""),
        ("src/aqt/data/bars.py", "BAR = 1\n"),
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
    for arguments in (
        ("init", "--quiet"),
        ("add", "--all"),
        ("commit", "--quiet", "-m", "initial"),
    ):
        subprocess.run(
            (
                "git",
                "-C",
                str(tmp_path),
                "-c",
                "user.email=tests@example.invalid",
                "-c",
                "user.name=tests",
                "-c",
                "commit.gpgsign=false",
                *arguments,
            ),
            check=True,
            capture_output=True,
        )
    return tmp_path


def _validate_against_frozen_schema(record: dict[str, object]) -> None:
    """Check `record` against the frozen experiment schema, unmodified."""
    schema = json.loads(
        (REPOSITORY_ROOT / "schemas" / "experiment.schema.json").read_text("utf-8")
    )
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(record)


def test_synthetic_experiment_record_accepts_task9_hashes(synthetic_repo: Path) -> None:
    lockbox_start, lockbox_end = _PARTITION_WINDOWS["lockbox"]
    composite = build_composite_manifest(
        cycle_id="C1",
        protocol_sha256=json.loads(
            (REPOSITORY_ROOT / "FROZEN_HASHES.json").read_text("utf-8")
        )["protocol_file_sha256"],
        partitions=(
            _partition("exploration"),
            _partition("confirmation"),
            sealed_partition_reference(
                partition="lockbox",
                symbol="BTCUSDT",
                interval_label="1h",
                window_start_utc=lockbox_start,
                window_end_exclusive_utc=lockbox_end,
                manifest_sha256="4" * 64,
            ),
        ),  # type: ignore[arg-type]
    )
    verify_composite_manifest(composite)
    identity = code_identity(synthetic_repo)

    frozen = json.loads((REPOSITORY_ROOT / "FROZEN_HASHES.json").read_text("utf-8"))
    record = {
        "experiment_id": "SYNTHETIC-TASK9-NOT-A-TRIAL",
        "hypothesis_hash": "5" * 64,
        "protocol_hash": frozen["protocol_file_sha256"],
        "protocol_status": "FROZEN",
        "trial_index": 0,
        "seed": 0,
        "backtester_hash": identity.source_sha256,
        "data_manifest_hash": composite.manifest_sha256,
    }
    _validate_against_frozen_schema(record)
    assert record["data_manifest_hash"] == composite.manifest_sha256
    assert record["backtester_hash"] == identity.source.source_sha256
