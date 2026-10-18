"""Task 33: the read-only dashboard page (DASHBOARD_PROPOSAL.md section 4)."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from aqt import dashboard
from aqt.core.deployment import APPROVED
from aqt.core.ledger import append_entry

NOW = datetime(2026, 10, 18, 12, 0, tzinfo=UTC)
COMMIT = "a" * 40


def _report(
    at: datetime, *, refused: list[str] | None = None, method: str = "NEWEY_WEST"
) -> dict:
    return {
        "at": at.isoformat(),
        "l02": {
            "effective_decisions": 3.5,
            "method": method,
            "raw_decisions": 5,
            "reason": None,
            "target": 240,
        },
        "report": {
            "authorizations": 1,
            "final_balances": {"BTC": "0.01", "USDT": "900.5"},
            "final_mode": "NORMAL",
            "governor_refusals": {"cap": 2},
            "health_breach_hours": 0,
            "hours": 1,
            "orders_sent": 1,
            "refused": refused or [],
            "scheduled_decisions": 1,
        },
    }


def _bar(opened: datetime) -> dict:
    return {
        "close": "1",
        "high": "1",
        "low": "1",
        "open": "1",
        "open_time": opened.isoformat(),
        "symbol": "BTCUSDT",
        "volume": "1",
    }


def _lines(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def _server(
    tmp_path: Path,
    *,
    report_at: datetime = NOW,
    bar_open: datetime = NOW - timedelta(hours=1),
    refused: list[str] | None = None,
    method: str = "NEWEY_WEST",
    detail: str = "venue timeout",
) -> tuple[Path, Path]:
    data = tmp_path / "data"
    _lines(
        data / dashboard.REPORTS,
        [
            _report(report_at - timedelta(hours=1)),
            _report(report_at, refused=refused, method=method),
        ],
    )
    _lines(data / dashboard.BARS, [_bar(bar_open)])
    append_entry(
        data / dashboard.INCIDENTS,
        record_type="aqt.execution.incident.open.v1",
        payload={"detail": detail, "kind": "venue"},
        recorded_at_utc=NOW,
    )
    record = tmp_path / "deployments.jsonl"
    append_entry(
        record,
        record_type=APPROVED,
        payload={"approved_by": "Owner", "commit": COMMIT, "statement": "ok"},
        recorded_at_utc=NOW,
    )
    return data, record


def test_every_panel_renders_with_its_labels(tmp_path: Path) -> None:
    data, record = _server(tmp_path)
    page = dashboard.render(data, record, NOW)
    for text in (
        "Paper trading, simulated money",
        "As of 2026-10-18T12:00:00+00:00",
        "Last reported step",
        "Activity per reported step",
        "Raw decisions 5",
        "of the 240 needed",
        f"Latest approved commit: <code>{COMMIT}</code>",
        "venue timeout",
        "BTC: last 0.01",
        "USDT: last 900.5",
    ):
        assert text in page
    assert "equity" not in page.lower()  # DB-6
    assert "class=red" not in page  # fresh report and bar, no refusal


@pytest.mark.parametrize(
    ("change", "why"),
    [
        ({"report_at": NOW - timedelta(hours=3)}, "stale report"),
        ({"bar_open": NOW - timedelta(hours=4)}, "stale bar"),
        ({"refused": ["governor: cap"]}, "refusal"),
    ],
)
def test_health_is_red(tmp_path: Path, change: dict, why: str) -> None:
    data, record = _server(tmp_path, **change)
    assert "<section class=red><h2>Health" in dashboard.render(data, record, NOW), why


def test_fallback_count_is_labelled(tmp_path: Path) -> None:
    data, record = _server(tmp_path, method=dashboard.FALLBACK)
    assert "not the same quantity" in dashboard.render(data, record, NOW)


def test_the_four_states(tmp_path: Path) -> None:
    path = tmp_path / "x.jsonl"
    assert dashboard.read_jsonl(path).state == dashboard.ABSENT
    path.write_text('{"a": 1}\n{"a": 2', encoding="utf-8")  # an append in progress
    found = dashboard.read_jsonl(path)
    assert (found.state, found.rows) == (dashboard.PENDING, ({"a": 1},))
    path.write_text('{"a": 1}\nnot json\n', encoding="utf-8")  # a corrupt record
    assert dashboard.read_jsonl(path).state == dashboard.INVALID
    path.write_text('{"a": 1}\n', encoding="utf-8")
    assert dashboard.read_jsonl(path).state == dashboard.VALID


def test_missing_inputs_show_no_data_never_numbers(tmp_path: Path) -> None:
    page = dashboard.render(tmp_path / "none", tmp_path / "none.jsonl", NOW)
    assert "Latest approved commit: unknown" in page
    assert "<section class=red><h2>Health" in page
    assert "no data" in page


def test_file_text_is_escaped(tmp_path: Path) -> None:
    evil = '<script>alert(1)</script>" onload="x'
    data, record = _server(tmp_path, refused=[evil], detail=evil)
    page = dashboard.render(data, record, NOW)
    assert "<script" not in page
    assert "&lt;script&gt;" in page
    assert '" onload="' not in page


def test_tampered_ledgers_show_unknown_or_invalid(tmp_path: Path) -> None:
    data, record = _server(tmp_path)
    for path in (record, data / dashboard.INCIDENTS):
        raw = bytearray(path.read_bytes())
        raw[raw.index(b"Owner" if path == record else b"venue")] ^= 1
        path.write_bytes(bytes(raw))
    page = dashboard.render(data, record, NOW)
    assert "Latest approved commit: unknown" in page
    assert COMMIT not in page
    assert "incidents: invalid" in page
    assert "venue timeout" not in page


def test_build_renames_a_finished_page_into_place(tmp_path: Path) -> None:
    data, record = _server(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    page = dashboard.build(data, record, out, NOW)
    assert page == out / "page" / "index.html"
    assert list((out / "staging").iterdir()) == []
    assert [p.name for p in (out / "page").iterdir()] == ["index.html"]
    if sys.platform != "win32":
        assert page.stat().st_mode & 0o777 == 0o644
    # a stopped generator: the page keeps its own time
    assert "As of 2026-10-18T12:00:00" in page.read_text(encoding="utf-8")


def test_sandbox_check_reports_each_boundary(tmp_path: Path) -> None:
    readable = tmp_path / "in.jsonl"
    readable.write_text("{}\n", encoding="utf-8")
    results = dict(dashboard.sandbox_check([readable], [tmp_path], tmp_path / "secret"))
    assert results[f"can read {readable}"] is True
    # outside the sandbox these do not hold, and are reported so
    assert results[f"cannot write in {tmp_path}"] is False
    assert not (tmp_path / ".aqt-dashboard-check").exists()
    assert results["cannot open a socket (inet)"] is False
    assert "io_uring_setup is refused" in results
