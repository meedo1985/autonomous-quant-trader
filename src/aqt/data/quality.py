"""Exploration data quality and outage report (roadmap Task 15).

A deterministic Markdown report over Task 14's exploration builds: coverage by
month, every declared gap (outage window), every outage row, and the
availability of fees, exchange filters, and symbol status. It is evidence that
the data is fit to explore on, not an analysis of it.

- Section 6: outage windows are untradeable; this report makes each one
  explicit. Every declared `Gap` appears in the outage table.
- Section 23: bar counts are stated as bar counts. The report contains counts,
  coverage fractions, and timestamps only: no prices and no statistic.

The report is derived entirely from the raw archives: it builds each
exploration manifest itself (Task 14), refuses unless that manifest is
byte-identical to the recorded one and verifies against its own parsed bars,
and takes every other fact (outage rows, missing archives) from the same build.
No caller can supply evidence the manifest check does not cover.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from decimal import ROUND_HALF_EVEN, Context, Decimal
from pathlib import Path
from typing import Final

from aqt.data.bars import BAR_INTERVAL
from aqt.data.binance_public import EXPLORATION_MONTHS, months_between
from aqt.data.klines import (
    EXPLORATION,
    WINDOW_END_EXCLUSIVE,
    WINDOW_START,
    ExplorationBuild,
    build_exploration_manifest,
)
from aqt.data.manifest import (
    AvailabilityRecord,
    Gap,
    canonical_json_bytes,
    verify_partition_manifest,
)

__all__ = ["QualityReportError", "render_report"]


class QualityReportError(ValueError):
    """Raised when the inputs cannot support a truthful report."""


def _iso(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%d %H:%M")


def _iso_ms(ms: int) -> str:
    moment = datetime.fromtimestamp(ms / 1000, tz=UTC)
    return moment.strftime("%Y-%m-%d %H:%M:%S.") + f"{ms % 1000:03d}"


def _hours(start: datetime, end: datetime) -> int:
    return (end - start) // BAR_INTERVAL


_DECIMAL: Final = Context(prec=28, rounding=ROUND_HALF_EVEN)
"""Fixed arithmetic for coverage figures, independent of the ambient context."""


def _percent(part: int, whole: int) -> str:
    """A coverage fraction as a percentage, exact decimal arithmetic."""
    ratio = _DECIMAL.divide(_DECIMAL.multiply(Decimal(part), Decimal(100)), whole)
    return f"{ratio.quantize(Decimal('0.001'), context=_DECIMAL)} %"


def _month_span(year: int, month: int) -> tuple[datetime, datetime]:
    start = max(datetime(year, month, 1, tzinfo=UTC), WINDOW_START)
    nxt = datetime(year + month // 12, month % 12 + 1, 1, tzinfo=UTC)
    return start, min(nxt, WINDOW_END_EXCLUSIVE)


def _overlap(gap: Gap, start: datetime, end: datetime) -> int:
    return max(0, _hours(max(gap.start, start), min(gap.end, end)))


def _availability(name: str, record: AvailabilityRecord) -> str:
    if record.status == "AVAILABLE":
        assert record.as_of_utc is not None
        return f"| {name} | AVAILABLE | as of {_iso(record.as_of_utc)} UTC |"
    return f"| {name} | UNAVAILABLE | {record.reason} |"


def _section(build: ExplorationBuild) -> list[str]:
    manifest = build.manifest
    try:
        verify_partition_manifest(manifest, series=build.series)
    except ValueError as error:
        raise QualityReportError(
            f"{manifest.symbol}: manifest does not verify; no report: {error}"
        ) from None

    window_hours = _hours(WINDOW_START, WINDOW_END_EXCLUSIVE)
    gap_hours = sum(_hours(gap.start, gap.end) for gap in manifest.gaps)
    if manifest.bar_count + gap_hours != window_hours:
        raise QualityReportError(
            f"{manifest.symbol}: {manifest.bar_count} bars + {gap_hours} gap hours "
            f"do not account for the {window_hours} hours of the window"
        )
    present = {bar.open_time for bar in build.series.bars}

    lines = [
        f"## {manifest.symbol}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Manifest SHA-256 | `{manifest.manifest_sha256}` |",
        f"| Parsed bars SHA-256 | `{manifest.parsed_sha256}` |",
        f"| Parser code SHA-256 | `{manifest.parser_code_sha256}` |",
        f"| Raw archives | {len(manifest.raw_artifacts)} |",
        f"| Missing archives | {len(build.missing_archives)} |",
        f"| Hours in window | {window_hours} |",
        f"| Hourly bars | {manifest.bar_count} |",
        f"| Hours in declared gaps | {gap_hours} |",
        f"| Coverage | {_percent(manifest.bar_count, window_hours)} |",
        f"| First bar opens | {_iso(manifest.first_open_time_utc)} UTC |",
        f"| Last bar opens | {_iso(manifest.last_open_time_utc)} UTC |",
        f"| Outage rows excluded | {len(build.outage_rows)} |",
        f"| Rows outside the window | {build.bars_outside_window} |",
        "",
        "### Point-in-time records",
        "",
        "| Record | Status | Detail |",
        "|---|---|---|",
        _availability("Fees", manifest.fees),
        _availability("Exchange filters", manifest.exchange_filters),
        _availability("Symbol status", manifest.symbol_status),
        "",
        f"### Outage windows ({len(manifest.gaps)} declared gaps, untradeable)",
        "",
        "| # | Start (UTC) | End, exclusive (UTC) | Hours |",
        "|---|---|---|---|",
    ]
    lines += [
        f"| {n} | {_iso(g.start)} | {_iso(g.end)} | {_hours(g.start, g.end)} |"
        for n, g in enumerate(manifest.gaps, start=1)
    ]
    lines += [
        "",
        f"### Outage rows ({len(build.outage_rows)}, excluded from the bars)",
        "",
        "| Archive | Line | Open (UTC) | Close (UTC) | Reason |",
        "|---|---|---|---|---|",
    ]
    lines += [
        f"| {r.source} | {r.line} | {_iso_ms(r.open_time_ms)} | "
        f"{_iso_ms(r.close_time_ms)} | {r.reason} |"
        for r in build.outage_rows
    ]
    lines += [
        "",
        "### Coverage by month",
        "",
        "| Month | Hours in window | Bars | Gap hours | Coverage |",
        "|---|---|---|---|---|",
    ]
    for year, month in months_between(*EXPLORATION_MONTHS):
        start, end = _month_span(year, month)
        hours = _hours(start, end)
        bars = sum(1 for moment in present if start <= moment < end)
        gaps = sum(_overlap(gap, start, end) for gap in manifest.gaps)
        if bars + gaps != hours:
            raise QualityReportError(
                f"{manifest.symbol} {year:04d}-{month:02d}: bars and gaps "
                "do not account for every hour"
            )
        lines.append(
            f"| {year:04d}-{month:02d} | {hours} | {bars} | {gaps} | "
            f"{_percent(bars, hours)} |"
        )
    return lines + [""]


def render_report(raw_root: Path, recorded_manifests: Mapping[str, bytes]) -> str:
    """Render the report for every symbol in `recorded_manifests`.

    A pure function of the raw archives under `raw_root` and the recorded
    manifest bytes: each symbol is rebuilt from the archives, and the report is
    refused unless the rebuilt manifest equals the recorded one exactly.
    """
    if not recorded_manifests:
        raise QualityReportError("no recorded manifests to report on")
    ordered: list[ExplorationBuild] = []
    for symbol in sorted(recorded_manifests):
        build = build_exploration_manifest(EXPLORATION, symbol, raw_root)
        rebuilt = canonical_json_bytes(build.manifest.as_mapping())
        if rebuilt != recorded_manifests[symbol]:
            raise QualityReportError(
                f"{symbol}: the manifest rebuilt from the raw archives differs "
                "from the recorded manifest; no report"
            )
        ordered.append(build)
    gap_sets = {tuple(build.manifest.gaps) for build in ordered}

    lines = [
        "# Exploration data quality and outage report",
        "",
        "Generated by `scripts/data_quality_report.py` (roadmap Task 15) from the",
        "Task 14 exploration manifests. Partition: exploration, "
        f"{_iso(WINDOW_START)} UTC to {_iso(WINDOW_END_EXCLUSIVE)} UTC (exclusive).",
        "",
        "Every manifest below was verified against its own parsed bars before",
        "this report was written. The report states counts, coverage fractions,",
        "and timestamps only. Bar counts are counts of hourly bars; they are not",
        "a measure of how much statistical evidence the data holds.",
        "",
        "Hours in a declared gap are outage windows: untradeable (Constitution",
        "section 6). Nothing in them was filled or corrected.",
        "",
        "| Symbol | Hourly bars | Declared gaps | Gap hours | Coverage |",
        "|---|---|---|---|---|",
    ]
    window_hours = _hours(WINDOW_START, WINDOW_END_EXCLUSIVE)
    for build in ordered:
        gaps = build.manifest.gaps
        lines.append(
            f"| {build.manifest.symbol} | {build.manifest.bar_count} | {len(gaps)} | "
            f"{sum(_hours(g.start, g.end) for g in gaps)} | "
            f"{_percent(build.manifest.bar_count, window_hours)} |"
        )
    if len(ordered) > 1:
        same = "identical" if len(gap_sets) == 1 else "NOT identical"
        lines += ["", f"Declared gaps are **{same}** across the symbols."]
    lines.append("")
    for build in ordered:
        lines += _section(build)
    return "\n".join(lines)
