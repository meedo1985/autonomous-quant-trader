"""Synthetic tests for the exploration data quality report. No market data."""

from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import io
import json
import re
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from aqt.data.klines import ExplorationBuild, build_exploration_manifest
from aqt.data.manifest import canonical_json_bytes
from aqt.data.quality import QualityReportError, render_report

HOUR = timedelta(hours=1)
MAR = datetime(2020, 3, 2, tzinfo=UTC)


def _ms(moment: datetime) -> int:
    return int(moment.timestamp()) * 1000


def _store(root: Path, symbol: str, lines: list[str]) -> None:
    name = f"{symbol}-1h-2020-03"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as handle:
        handle.writestr(f"{name}.csv", "\n".join(lines) + "\n")
    content = buffer.getvalue()
    directory = root / "klines" / symbol / "1h"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{name}.zip").write_bytes(content)
    sidecar = {"name": f"{name}.zip", "sha256": hashlib.sha256(content).hexdigest()}
    (directory / f"{name}.zip.source.json").write_bytes(json.dumps(sidecar).encode())


def _line(open_ms: int, close_ms: int) -> str:
    return f"{open_ms},100.0,110.0,90.0,105.0,2.5,{close_ms},1,1,1,1,0"


def _raw(root: Path, symbol: str = "BTCUSDT") -> Path:
    """March 2020 only: 5 bars, a 3-hour hole holding one cut-short row, 4 bars."""
    hours = [MAR + i * HOUR for i in [*range(5), *range(8, 12)]]
    lines = [_line(_ms(h), _ms(h) + 3_599_999) for h in hours]
    lines.append(_line(_ms(MAR + 5 * HOUR), _ms(MAR + 5 * HOUR) + 1_306_694))
    _store(root, symbol, lines)
    return root


def _build(root: Path, symbol: str = "BTCUSDT") -> ExplorationBuild:
    return build_exploration_manifest("exploration", symbol, _raw(root, symbol))


def test_report_is_deterministic(tmp_path: Path) -> None:
    first = render_report([_build(tmp_path / "a")])
    second = render_report([_build(tmp_path / "b")])
    assert first == second
    assert first.endswith("\n") and not first.endswith("\n\n")


def test_every_gap_appears_in_the_outage_table(tmp_path: Path) -> None:
    build = _build(tmp_path)
    report = render_report([build])
    assert len(build.manifest.gaps) == 3
    for number, gap in enumerate(build.manifest.gaps, start=1):
        start = gap.start.strftime("%Y-%m-%d %H:%M")
        end = gap.end.strftime("%Y-%m-%d %H:%M")
        hours = (gap.end - gap.start) // HOUR
        assert f"| {number} | {start} | {end} | {hours} |" in report
    assert "| 2020-03-02 03:00" not in report  # a present hour is not a gap
    assert "BTCUSDT-1h-2020-03.csv | 10 | 2020-03-02 05:00:00.000 |" in report


def test_monthly_coverage_accounts_for_every_hour(tmp_path: Path) -> None:
    report = render_report([_build(tmp_path)])
    assert "| 2020-03 | 744 | 9 | 735 | 1.210 % |" in report
    assert "| 2017-08 | 360 | 0 | 360 | 0.000 % |" in report  # from the 17th


def test_refuses_when_the_manifest_does_not_verify(tmp_path: Path) -> None:
    build = _build(tmp_path)
    digest = build.manifest.manifest_sha256
    wrong = dataclasses.replace(
        build.manifest, manifest_sha256=("0" if digest[0] != "0" else "1") + digest[1:]
    )
    with pytest.raises(QualityReportError, match="does not verify"):
        render_report([dataclasses.replace(build, manifest=wrong)])
    other_bars = dataclasses.replace(build.series, bars=build.series.bars[:-1])
    with pytest.raises(QualityReportError, match="does not verify"):
        render_report([dataclasses.replace(build, series=other_bars)])


_FORBIDDEN = re.compile(
    r"\b(sample size|sharpe|returns?|volatility|mean|median|average|std|"
    r"variance|deviation|p-value|significan\w*|confidence|t-stat\w*|"
    r"correlat\w*|drawdown|edge|ess|effective)\b",
    re.IGNORECASE,
)


def test_report_states_no_statistic_and_no_prices(tmp_path: Path) -> None:
    report = render_report([_build(tmp_path)])
    assert _FORBIDDEN.findall(report) == []
    assert "100.0" not in report and "105.0" not in report  # no prices
    numbers = re.findall(r"\d+\.\d+", report)
    assert all(re.fullmatch(r"\d+\.\d{3}", n) for n in numbers)  # coverage only
    assert "not\na measure of how much statistical evidence" in report


def test_symbols_are_ordered_and_gap_agreement_is_stated(tmp_path: Path) -> None:
    btc = _build(tmp_path, "BTCUSDT")
    eth = _build(tmp_path, "ETHUSDT")
    report = render_report([eth, btc])
    assert report.index("## BTCUSDT") < report.index("## ETHUSDT")
    assert "Declared gaps are **identical** across the symbols." in report
    with pytest.raises(QualityReportError, match="duplicate"):
        render_report([btc, btc])
    with pytest.raises(QualityReportError, match="no builds"):
        render_report([])


def _cli() -> object:
    path = Path(__file__).parents[2] / "scripts" / "data_quality_report.py"
    spec = importlib.util.spec_from_file_location("data_quality_report", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_checks_recorded_manifests_and_is_write_once(tmp_path: Path) -> None:
    raw = _raw(_raw(tmp_path / "raw", "BTCUSDT"), "ETHUSDT")
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    for symbol in ("BTCUSDT", "ETHUSDT"):
        build = build_exploration_manifest("exploration", symbol, raw)
        (manifests / f"exploration-{symbol}-1h.json").write_bytes(
            canonical_json_bytes(build.manifest.as_mapping())
        )
    out = tmp_path / "report.md"
    args = ["--raw", str(raw), "--manifests", str(manifests), "--out", str(out)]
    cli = _cli()

    assert cli.main(args) == 0  # type: ignore[attr-defined]
    written = out.read_bytes()
    out.write_bytes(written.replace(b"\n", b"\r\n"))  # a CRLF checkout
    assert cli.main(args) == 0  # type: ignore[attr-defined]

    out.write_bytes(written + b"edited\n")
    with pytest.raises(QualityReportError, match="refusing to replace"):
        cli.main(args)  # type: ignore[attr-defined]

    recorded = manifests / "exploration-ETHUSDT-1h.json"
    recorded.write_bytes(recorded.read_bytes() + b" ")
    out.unlink()
    with pytest.raises(QualityReportError, match="differs"):
        cli.main(args)  # type: ignore[attr-defined]
    assert not out.exists()
