"""Binance 1h kline archives to `BarSeries`, and the exploration manifest.

Roadmap Task 14 (`review/roadmap/ROADMAP_PROPOSAL.md`). Reads the raw archives
Task 13 stored, verifies each against its sidecar, parses them strictly into
`aqt.data.bars.Bar` objects, and builds a `PartitionManifest` for the
**exploration** partition only. It binds nothing: the manifest hash is not
entered into any cycle record (that is a `cycle_start_bindings` act).

Constitution obligations
------------------------
- Section 6: one bar-semantics module. Bars are built by `aqt.data.bars`;
  nothing here re-implements alignment, ordering, or price checks. Nothing is
  filled, interpolated, or corrected: a malformed row raises and no partial
  series is returned; absent hours become declared `Gap` records.
- Section 6, "outages untradeable": Binance archives contain irregular rows
  around exchange outages (bars cut short by a maintenance stop, bars running
  on a mid-hour offset after a restart). A row is **regular** only if it opens
  exactly on the hour and closes exactly 1 ms before the next hour. Every
  other well-formed row (its prices and volume pass the same checks as a
  regular bar) is an **outage row**: it becomes no bar, it is listed
  in the build report with its file, line, times, and reason, and the hours it
  would have covered are left to the declared gaps. Nothing is shifted onto
  the hour grid or stretched to a full hour.
- Sections 7 and 7a: only the exploration partition can be built. Any other
  partition, including lockbox, is refused before any file is read.
- Section 27: identity uses `aqt.data.manifest` canonical hashing unchanged.

Binance Spot kline CSV rows have 12 fields and no header; `open_time` and
`close_time` are Unix milliseconds for archives before 2025. Any other shape,
including microsecond timestamps, is rejected rather than guessed.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from aqt.data.bars import BAR_INTERVAL, Bar, BarSemanticsError, BarSeries
from aqt.data.binance_public import EXPLORATION_MONTHS, INTERVAL, months_between
from aqt.data.manifest import (
    Gap,
    PartitionManifest,
    RawArtifact,
    build_partition_manifest,
    unavailable,
)

__all__ = [
    "EXPLORATION",
    "OutageRow",
    "ParsedArchive",
    "WINDOW_END_EXCLUSIVE",
    "WINDOW_START",
    "ExplorationBuild",
    "KlineError",
    "build_exploration_manifest",
    "parse_archive",
    "parser_code_sha256",
]

EXPLORATION: Final[str] = "exploration"
WINDOW_START: Final[datetime] = datetime(2017, 8, 17, tzinfo=UTC)
WINDOW_END_EXCLUSIVE: Final[datetime] = datetime(2022, 1, 1, tzinfo=UTC)
"""`protocols/protocol_v1.yaml` `partitions.exploration`: 2017-08-17T00:00:00Z
to 2021-12-31T23:59:59Z inclusive, i.e. `[2017-08-17, 2022-01-01)`."""

_FIELDS: Final[int] = 12
_HOUR_MS: Final[int] = 3_600_000
_MS_DIGITS: Final[int] = 13


class KlineError(ValueError):
    """Raised when a raw archive cannot be turned into bars exactly."""


def parser_code_sha256() -> str:
    """SHA-256 of this module's source with line endings normalized to LF, so
    the identity does not depend on the checkout's `core.autocrlf` setting."""
    source = Path(__file__).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(source).hexdigest()


def _month_bounds_ms(year: int, month: int) -> tuple[int, int]:
    start = datetime(year, month, 1, tzinfo=UTC)
    end = datetime(year + month // 12, month % 12 + 1, 1, tzinfo=UTC)
    return int(start.timestamp()) * 1000, int(end.timestamp()) * 1000


def _millis(text: str, where: str) -> int:
    if len(text) != _MS_DIGITS or not text.isdigit():
        raise KlineError(f"{where}: expected a 13-digit millisecond time, got {text!r}")
    return int(text)


@dataclass(frozen=True, slots=True)
class OutageRow:
    """A well-formed row that is not a regular hourly bar; see module doc."""

    source: str
    line: int
    open_time_ms: int
    close_time_ms: int
    reason: str

    def as_mapping(self) -> dict[str, object]:
        return {
            "close_time_ms": self.close_time_ms,
            "line": self.line,
            "open_time_ms": self.open_time_ms,
            "reason": self.reason,
            "source": self.source,
        }


@dataclass(frozen=True, slots=True)
class ParsedArchive:
    bars: tuple[Bar, ...]
    outage_rows: tuple[OutageRow, ...]


def _irregularity(open_ms: int, close_ms: int) -> str | None:
    if open_ms % _HOUR_MS:
        return "open_time is not on the hour"
    if close_ms < open_ms:
        return "close_time is before open_time"
    if close_ms < open_ms + _HOUR_MS - 1:
        return "bar ends before the hour does"
    if close_ms > open_ms + _HOUR_MS - 1:
        return "bar runs past the hour"
    return None


def parse_archive(
    content: bytes, *, symbol: str, year: int, month: int
) -> ParsedArchive:
    """Parse one monthly archive; raise on any malformed row."""
    name = f"{symbol}-{INTERVAL}-{year:04d}-{month:02d}"
    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
        members = archive.namelist()
    except (zipfile.BadZipFile, ValueError) as error:
        raise KlineError(f"{name}.zip is unreadable: {error}") from None
    if members != [f"{name}.csv"]:
        raise KlineError(f"{name}.zip must hold exactly {name}.csv, has {members}")
    try:
        text = archive.read(members[0]).decode("ascii")
    except (zipfile.BadZipFile, ValueError) as error:  # incl. UnicodeDecodeError
        raise KlineError(f"{name}.zip is unreadable: {error}") from None

    first_ms, end_ms = _month_bounds_ms(year, month)
    bars: list[Bar] = []
    outages: list[OutageRow] = []
    rows = csv.reader(io.StringIO(text), strict=True)
    for line_no, row in enumerate(rows, start=1):
        where = f"{name}.csv line {line_no}"
        if len(row) != _FIELDS:
            raise KlineError(f"{where}: expected {_FIELDS} fields, got {len(row)}")
        open_ms = _millis(row[0], where)
        close_ms = _millis(row[6], where)
        if not first_ms <= open_ms < end_ms:
            raise KlineError(f"{where}: open_time lies outside {year:04d}-{month:02d}")
        # Every row's values pass the `aqt.data.bars` checks before it is
        # classified, so a malformed row cannot pass as an outage. For an
        # outage row the Bar is labelled with its hour only to run those checks
        # and is then discarded; the raw times go to the report unchanged.
        try:
            bar = Bar(
                open_time=datetime.fromtimestamp(
                    (open_ms - open_ms % _HOUR_MS) / 1000, tz=UTC
                ),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
            )
        except (ValueError, BarSemanticsError) as error:
            raise KlineError(f"{where}: {error}") from None
        reason = _irregularity(open_ms, close_ms)
        if reason is not None:
            outages.append(OutageRow(f"{name}.csv", line_no, open_ms, close_ms, reason))
            continue
        bars.append(bar)
    if not bars and not outages:
        raise KlineError(f"{name}.csv has no rows")
    return ParsedArchive(tuple(bars), tuple(outages))


def _verified_bytes(path: Path) -> bytes:
    """Archive bytes, checked against the sidecar Task 13 wrote beside them."""
    sidecar_path = path.with_name(path.name + ".source.json")
    try:
        sidecar = json.loads(sidecar_path.read_bytes())
    except (FileNotFoundError, ValueError):
        raise KlineError(f"missing or unreadable sidecar: {sidecar_path}") from None
    content = path.read_bytes()
    if not isinstance(sidecar, dict) or sidecar.get("name") != path.name:
        raise KlineError(f"sidecar does not describe {path.name}: {sidecar_path}")
    if hashlib.sha256(content).hexdigest() != sidecar.get("sha256"):
        raise KlineError(f"stored bytes no longer match their sidecar: {path}")
    return content


def _absent_runs(series: BarSeries) -> tuple[Gap, ...]:
    """Every absent hour of the window, as maximal half-open runs."""
    present = {bar.open_time for bar in series.bars}
    gaps: list[Gap] = []
    run_start: datetime | None = None
    moment = WINDOW_START
    while moment < WINDOW_END_EXCLUSIVE:
        if moment in present:
            if run_start is not None:
                gaps.append(Gap(run_start, moment))
                run_start = None
        elif run_start is None:
            run_start = moment
        moment += BAR_INTERVAL
    if run_start is not None:
        gaps.append(Gap(run_start, WINDOW_END_EXCLUSIVE))
    return tuple(gaps)


@dataclass(frozen=True, slots=True)
class ExplorationBuild:
    """The manifest plus the facts a person needs to audit how it was built."""

    manifest: PartitionManifest
    series: BarSeries
    missing_archives: tuple[str, ...]
    bars_outside_window: int
    outage_rows: tuple[OutageRow, ...]

    def report(self) -> dict[str, object]:
        return {
            "bar_count": self.manifest.bar_count,
            "bars_outside_window": self.bars_outside_window,
            "gap_count": len(self.manifest.gaps),
            "gap_hours": sum(
                (gap.end - gap.start) // BAR_INTERVAL for gap in self.manifest.gaps
            ),
            "manifest_sha256": self.manifest.manifest_sha256,
            "missing_archives": list(self.missing_archives),
            "outage_rows": [row.as_mapping() for row in self.outage_rows],
            "symbol": self.manifest.symbol,
        }


def build_exploration_manifest(
    partition: str, symbol: str, raw_root: Path
) -> ExplorationBuild:
    """Build the exploration manifest for `symbol` from Task 13's raw archives.

    Any partition other than exploration is refused before a file is read.
    """
    if partition != EXPLORATION:
        raise KlineError(
            f"only the {EXPLORATION!r} partition can be built here; {partition!r} "
            "is refused before any file is read"
        )
    directory = raw_root / "klines" / symbol / INTERVAL
    artifacts: list[RawArtifact] = []
    bars: list[Bar] = []
    outages: list[OutageRow] = []
    missing: list[str] = []
    for year, month in months_between(*EXPLORATION_MONTHS):
        name = f"{symbol}-{INTERVAL}-{year:04d}-{month:02d}.zip"
        path = directory / name
        if not path.exists():
            missing.append(name)
            continue
        content = _verified_bytes(path)
        artifacts.append(RawArtifact(name, content))
        parsed = parse_archive(content, symbol=symbol, year=year, month=month)
        bars.extend(parsed.bars)
        outages.extend(parsed.outage_rows)

    inside = [b for b in bars if WINDOW_START <= b.open_time < WINDOW_END_EXCLUSIVE]
    if not inside:
        raise KlineError(f"no {symbol} bars inside the exploration window")
    try:
        series = BarSeries(symbol=symbol, bars=tuple(inside))
    except BarSemanticsError as error:
        raise KlineError(f"{symbol}: {error}") from None
    reason = (
        "no point-in-time record for the exploration window; the only "
        "exchangeInfo snapshot postdates the window start (T13-01)"
    )
    manifest = build_partition_manifest(
        partition=EXPLORATION,
        series=series,
        raw_artifacts=artifacts,
        parser_code_sha256=parser_code_sha256(),
        window_start_utc=WINDOW_START,
        window_end_exclusive_utc=WINDOW_END_EXCLUSIVE,
        fees=unavailable("no point-in-time fee schedule is recorded for the window"),
        exchange_filters=unavailable(reason),
        symbol_status=unavailable(reason),
        gaps=_absent_runs(series),
    )
    return ExplorationBuild(
        manifest=manifest,
        series=series,
        missing_archives=tuple(missing),
        bars_outside_window=len(bars) - len(inside),
        outage_rows=tuple(outages),
    )
