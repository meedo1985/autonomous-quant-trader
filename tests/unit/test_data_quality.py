"""Synthetic tests for the exploration data quality report. No market data."""

from __future__ import annotations

import decimal
import hashlib
import importlib.util
import io
import json
import re
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from aqt.data.klines import build_exploration_manifest
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
        # A fixed member timestamp keeps the archive bytes, and therefore the
        # manifest hashes, identical across fixture builds (R-3).
        member = zipfile.ZipInfo(f"{name}.csv", date_time=(2020, 1, 1, 0, 0, 0))
        handle.writestr(member, "\n".join(lines) + "\n")
    content = buffer.getvalue()
    directory = root / "klines" / symbol / "1h"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{name}.zip").write_bytes(content)
    sidecar = {"name": f"{name}.zip", "sha256": hashlib.sha256(content).hexdigest()}
    (directory / f"{name}.zip.source.json").write_bytes(json.dumps(sidecar).encode())


def _line(open_ms: int, close_ms: int) -> str:
    return f"{open_ms},100.0,110.0,90.0,105.0,2.5,{close_ms},1,1,1,1,0"


def _raw(root: Path, symbols: tuple[str, ...] = ("BTCUSDT",)) -> Path:
    """March 2020 only: 5 bars, a 3-hour hole holding one cut-short row, 4 bars."""
    hours = [MAR + i * HOUR for i in [*range(5), *range(8, 12)]]
    lines = [_line(_ms(h), _ms(h) + 3_599_999) for h in hours]
    lines.append(_line(_ms(MAR + 5 * HOUR), _ms(MAR + 5 * HOUR) + 1_306_694))
    for symbol in symbols:
        _store(root, symbol, lines)
    return root


def _recorded(raw: Path, symbols: tuple[str, ...] = ("BTCUSDT",)) -> dict[str, bytes]:
    return {
        symbol: canonical_json_bytes(
            build_exploration_manifest("exploration", symbol, raw).manifest.as_mapping()
        )
        for symbol in symbols
    }


def _report(root: Path, symbols: tuple[str, ...] = ("BTCUSDT",)) -> str:
    raw = _raw(root, symbols)
    return render_report(raw, _recorded(raw, symbols))


def test_report_is_deterministic(tmp_path: Path) -> None:
    first = _report(tmp_path / "a")
    second = _report(tmp_path / "b")
    assert first == second
    assert first.endswith("\n") and not first.endswith("\n\n")


def test_coverage_ignores_the_ambient_decimal_context(tmp_path: Path) -> None:
    """R-1: 9/744 must print 1.210 % whatever the caller's decimal settings."""
    raw = _raw(tmp_path)
    recorded = _recorded(raw)
    expected = render_report(raw, recorded)
    assert "| 2020-03 | 744 | 9 | 735 | 1.210 % |" in expected
    with decimal.localcontext() as context:
        context.rounding = decimal.ROUND_DOWN
        context.prec = 2
        assert render_report(raw, recorded) == expected


def test_every_gap_and_outage_row_appears(tmp_path: Path) -> None:
    raw = _raw(tmp_path)
    build = build_exploration_manifest("exploration", "BTCUSDT", raw)
    report = render_report(raw, _recorded(raw))
    assert len(build.manifest.gaps) == 3
    for number, gap in enumerate(build.manifest.gaps, start=1):
        start = gap.start.strftime("%Y-%m-%d %H:%M")
        end = gap.end.strftime("%Y-%m-%d %H:%M")
        hours = (gap.end - gap.start) // HOUR
        assert f"| {number} | {start} | {end} | {hours} |" in report
    assert "| 2020-03-02 03:00" not in report  # a present hour is not a gap
    assert "BTCUSDT-1h-2020-03.csv | 10 | 2020-03-02 05:00:00.000 |" in report
    assert "| Outage rows excluded | 1 |" in report


def test_monthly_coverage_accounts_for_every_hour(tmp_path: Path) -> None:
    report = _report(tmp_path)
    assert "| 2020-03 | 744 | 9 | 735 | 1.210 % |" in report
    assert "| 2017-08 | 360 | 0 | 360 | 0.000 % |" in report  # from the 17th


def test_refuses_unless_the_recorded_manifest_matches(tmp_path: Path) -> None:
    """R-2: every fact comes from the raw archives and must match the record."""
    raw = _raw(tmp_path)
    recorded = _recorded(raw)
    tampered = {
        "BTCUSDT": recorded["BTCUSDT"].replace(b'"bar_count":9', b'"bar_count":8')
    }
    assert tampered != recorded
    with pytest.raises(QualityReportError, match="differs from the recorded"):
        render_report(raw, tampered)
    with pytest.raises(QualityReportError, match="no recorded manifests"):
        render_report(raw, {})


def test_report_takes_no_caller_supplied_evidence() -> None:
    """R-2: the only inputs are the raw archives and the recorded manifests, so
    outage rows cannot be passed in (or left out) by a caller."""
    import inspect

    assert list(inspect.signature(render_report).parameters) == [
        "raw_root",
        "recorded_manifests",
    ]


_FORBIDDEN = re.compile(
    r"\b(sample size|sharpe|returns?|volatility|mean|median|average|std|"
    r"variance|deviation|p-value|significan\w*|confidence|t-stat\w*|"
    r"correlat\w*|drawdown|edge|ess|effective)\b",
    re.IGNORECASE,
)
_TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}(:\d{2}\.\d{3})?")
_DECIMAL = re.compile(r"\d\.\d")


def _misplaced_decimals(report: str) -> list[str]:
    """Lines holding a decimal number that is not a timestamp or a coverage
    percentage in a Coverage column (or the Coverage row of a field table)."""
    bad: list[str] = []
    header: list[str] | None = None
    for line in report.splitlines():
        if not line.startswith("|"):
            header = None
            if _DECIMAL.search(_TIMESTAMP.sub("", line)):
                bad.append(line)
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if header is None:
            header = cells
            continue
        if set(line) <= set("|-"):
            continue
        for name, cell in zip(header, cells, strict=True):
            text = _TIMESTAMP.sub("", cell)
            if not _DECIMAL.search(text):
                continue
            coverage = name == "Coverage" or (
                header[:2] == ["Field", "Value"] and cells[0] == "Coverage"
            )
            if not (coverage and re.fullmatch(r"\d+\.\d{3} %", text)):
                bad.append(line)
    return bad


def test_report_states_no_statistic_and_no_prices(tmp_path: Path) -> None:
    """R-4: decimals are checked by where they sit, not only by their width."""
    report = _report(tmp_path)
    assert _FORBIDDEN.findall(report) == []
    assert _misplaced_decimals(report) == []
    assert "100.0" not in report and "105.0" not in report  # no prices
    assert "not\na measure of how much statistical evidence" in report


@pytest.mark.parametrize(
    "injected",
    [
        ("| Hourly bars | 9 |", "| Hourly bars | 9 |\n| Skewness | 1.234 % |"),
        ("| Hourly bars | 9 |", "| Hourly bars | 9.500 |"),
        ("## BTCUSDT\n", "## BTCUSDT\n\nSkewness: 1.234\n"),
    ],
)
def test_content_check_catches_a_planted_statistic(
    tmp_path: Path, injected: tuple[str, str]
) -> None:
    """The R-4 check is not vacuous: planted numbers are flagged."""
    report = _report(tmp_path)
    old, new = injected
    assert old in report
    assert _misplaced_decimals(report.replace(old, new, 1)) != []


def test_symbols_are_ordered_and_gap_agreement_is_stated(tmp_path: Path) -> None:
    raw = _raw(tmp_path, ("ETHUSDT", "BTCUSDT"))
    report = render_report(raw, _recorded(raw, ("ETHUSDT", "BTCUSDT")))
    assert report.index("## BTCUSDT") < report.index("## ETHUSDT")
    assert "Declared gaps are **identical** across the symbols." in report


def _cli() -> object:
    path = Path(__file__).parents[2] / "scripts" / "data_quality_report.py"
    spec = importlib.util.spec_from_file_location("data_quality_report", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_checks_recorded_manifests_and_is_write_once(tmp_path: Path) -> None:
    symbols = ("BTCUSDT", "ETHUSDT")
    raw = _raw(tmp_path / "raw", symbols)
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    for symbol, content in _recorded(raw, symbols).items():
        (manifests / f"exploration-{symbol}-1h.json").write_bytes(content)
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
