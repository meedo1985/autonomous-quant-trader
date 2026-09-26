"""Exploration manifest built end to end from a synthetic raw directory."""

from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import io
import json
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType

import pytest

from aqt.data.klines import (
    WINDOW_END_EXCLUSIVE,
    WINDOW_START,
    KlineError,
    build_exploration_manifest,
)
from aqt.data.manifest import (
    UNAVAILABLE,
    Gap,
    ManifestError,
    canonical_json_bytes,
    verify_partition_manifest,
)

HOUR = timedelta(hours=1)


def _ms(moment: datetime) -> int:
    return int(moment.timestamp()) * 1000


def _line(open_ms: int, close_ms: int) -> str:
    return f"{open_ms},100.0,110.0,90.0,105.0,2.5,{close_ms},1,1,1,1,0"


def _store(
    root: Path,
    year: int,
    month: int,
    hours: list[datetime],
    extra: tuple[str, ...] = (),
) -> None:
    """Write a synthetic archive and a Task-13-style sidecar."""
    name = f"BTCUSDT-1h-{year:04d}-{month:02d}"
    lines = [_line(_ms(h), _ms(h) + 3_599_999) for h in hours] + list(extra)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as handle:
        handle.writestr(f"{name}.csv", "\n".join(lines) + "\n")
    content = buffer.getvalue()
    directory = root / "klines" / "BTCUSDT" / "1h"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{name}.zip").write_bytes(content)
    sidecar = {"name": f"{name}.zip", "sha256": hashlib.sha256(content).hexdigest()}
    (directory / f"{name}.zip.source.json").write_bytes(json.dumps(sidecar).encode())


def _hours(start: datetime, count: int) -> list[datetime]:
    return [start + i * HOUR for i in range(count)]


# August 2017: two hours before the window, then 10 hours from 04:00 on the 17th.
# March 2020: 5 hours, a 3-hour hole, then 4 hours, plus one outage row (a
# bar cut short at 05:21, as Binance archives show around maintenance) inside
# the hole. Every other month is absent.
AUG = datetime(2017, 8, 17, 4, tzinfo=UTC)
MAR = datetime(2020, 3, 2, tzinfo=UTC)


@pytest.fixture
def raw(tmp_path: Path) -> Path:
    before = [
        datetime(2017, 8, 16, 22, tzinfo=UTC),
        datetime(2017, 8, 16, 23, tzinfo=UTC),
    ]
    _store(tmp_path, 2017, 8, before + _hours(AUG, 10))
    cut_short = _line(_ms(MAR + 5 * HOUR), _ms(MAR + 5 * HOUR) + 1_306_694)
    _store(tmp_path, 2020, 3, _hours(MAR, 5) + _hours(MAR + 8 * HOUR, 4), (cut_short,))
    return tmp_path


def test_build_is_deterministic_and_verifies(raw: Path) -> None:
    first = build_exploration_manifest("exploration", "BTCUSDT", raw)
    second = build_exploration_manifest("exploration", "BTCUSDT", raw)
    assert canonical_json_bytes(first.manifest.as_mapping()) == canonical_json_bytes(
        second.manifest.as_mapping()
    )
    assert first.manifest.manifest_sha256 == second.manifest.manifest_sha256
    verify_partition_manifest(first.manifest, series=first.series)


def test_a_flipped_hash_byte_is_rejected(raw: Path) -> None:
    build = build_exploration_manifest("exploration", "BTCUSDT", raw)
    digest = build.manifest.parsed_sha256
    flipped = ("0" if digest[0] != "0" else "1") + digest[1:]
    tampered = dataclasses.replace(build.manifest, parsed_sha256=flipped)
    with pytest.raises(ManifestError):
        verify_partition_manifest(tampered)
    with pytest.raises(ManifestError):
        verify_partition_manifest(
            build.manifest,
            series=dataclasses.replace(build.series, bars=build.series.bars[:-1]),
        )


def test_gaps_cover_exactly_the_absent_hours(raw: Path) -> None:
    build = build_exploration_manifest("exploration", "BTCUSDT", raw)
    assert build.manifest.gaps == (
        Gap(WINDOW_START, AUG),
        Gap(AUG + 10 * HOUR, MAR),
        Gap(MAR + 5 * HOUR, MAR + 8 * HOUR),
        Gap(MAR + 12 * HOUR, WINDOW_END_EXCLUSIVE),
    )
    present = {bar.open_time for bar in build.series.bars}
    window_hours = (WINDOW_END_EXCLUSIVE - WINDOW_START) // HOUR
    gap_hours = sum((g.end - g.start) // HOUR for g in build.manifest.gaps)
    assert len(present) + gap_hours == window_hours


def test_report_names_trimmed_bars_and_missing_archives(raw: Path) -> None:
    build = build_exploration_manifest("exploration", "BTCUSDT", raw)
    assert build.bars_outside_window == 2
    [outage] = build.outage_rows
    assert (outage.source, outage.line) == ("BTCUSDT-1h-2020-03.csv", 10)
    assert "ends before the hour" in outage.reason
    assert build.report()["outage_rows"] == [outage.as_mapping()]
    assert build.manifest.bar_count == 19
    assert len(build.missing_archives) == 53 - 2
    assert "BTCUSDT-1h-2020-03.zip" not in build.missing_archives
    manifest = build.manifest
    for record in (manifest.fees, manifest.exchange_filters, manifest.symbol_status):
        assert record.status == UNAVAILABLE


@pytest.mark.parametrize("partition", ["lockbox", "confirmation", "EXPLORATION"])
def test_other_partitions_are_refused_before_any_file_is_read(
    partition: str, raw: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_io(*_: object, **__: object) -> None:
        raise AssertionError("a file was touched")

    monkeypatch.setattr(Path, "read_bytes", no_io)
    monkeypatch.setattr(Path, "exists", no_io)
    with pytest.raises(KlineError, match="refused before any file is read"):
        build_exploration_manifest(partition, "BTCUSDT", raw)


def test_tampered_archive_is_refused(raw: Path) -> None:
    path = raw / "klines" / "BTCUSDT" / "1h" / "BTCUSDT-1h-2020-03.zip"
    path.write_bytes(path.read_bytes() + b"x")
    with pytest.raises(KlineError, match="no longer match"):
        build_exploration_manifest("exploration", "BTCUSDT", raw)


def _cli() -> ModuleType:
    path = Path(__file__).parents[2] / "scripts" / "build_manifests.py"
    spec = importlib.util.spec_from_file_location("build_manifests", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_refuses_confirmation_and_writes_nothing(raw: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    args = ["--raw", str(raw), "--out", str(out), "--partition", "confirmation"]
    assert _cli().main(args) == 2
    assert not out.exists()


def test_cli_output_is_write_once(raw: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    args = ["--raw", str(raw), "--out", str(out), "--symbol", "BTCUSDT"]
    cli = _cli()
    assert cli.main(args) == 0
    manifest_path = out / "exploration-BTCUSDT-1h.json"
    written = manifest_path.read_bytes()
    assert json.loads(written)["partition"] == "exploration"
    assert cli.main(args) == 0  # identical rebuild: no-op
    assert manifest_path.read_bytes() == written
    manifest_path.write_bytes(written + b" ")
    with pytest.raises(KlineError, match="refusing to replace"):
        cli.main(args)
