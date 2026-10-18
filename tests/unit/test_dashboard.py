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


def test_future_report_is_red(tmp_path: Path) -> None:
    # T33-2: a clock or file from the future is not healthy
    data, record = _server(tmp_path, report_at=NOW + timedelta(hours=1))
    assert "<section class=red><h2>Health" in dashboard.render(data, record, NOW)


def test_governor_refusals_are_shown_not_red(tmp_path: Path) -> None:
    # T33-2 (partly agreed): the governor refusing is the governor working
    data, record = _server(tmp_path)
    page = dashboard.render(data, record, NOW)
    assert "Governor refusals in the last step: 2" in page
    assert "class=red" not in page


@pytest.mark.parametrize(
    "bad",
    [
        {"at": NOW.isoformat(), "l02": {}, "report": None},
        {
            "at": NOW.isoformat(),
            "l02": {},
            "report": {"governor_refusals": {"cap": "2"}},
        },
        {"at": "yesterday", "l02": {}, "report": {}},
        [1, 2],
    ],
)
def test_a_malformed_complete_report_is_invalid_not_a_crash(
    tmp_path: Path, bad: object
) -> None:
    # T33-1
    data, record = _server(tmp_path)
    with (data / dashboard.REPORTS).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(bad) + "\n")
    page = dashboard.render(data, record, NOW)
    assert "reports: invalid line 3" in page
    assert "<section class=red><h2>Health" in page
    assert "Raw decisions" not in page


def test_each_input_shows_its_own_state(tmp_path: Path) -> None:
    # T33-4: pending reports, a torn incident ledger, unreadable bars
    data, record = _server(tmp_path)
    with (data / dashboard.REPORTS).open("a", encoding="utf-8") as handle:
        handle.write('{"at": "2026')
    with (data / dashboard.INCIDENTS).open("ab") as handle:
        handle.write(b'{"entry_hash"')
    (data / dashboard.BARS).unlink()
    (data / dashboard.BARS).mkdir()  # reading a directory fails: unreadable
    page = dashboard.render(data, record, NOW)
    assert "reports: pending last line is still being written" in page
    assert "incidents: pending" in page
    assert "bars: invalid unreadable" in page
    assert "Raw decisions 5" in page  # complete rows before the pending line


def test_attribute_text_is_escaped(tmp_path: Path) -> None:
    # T33-4: an asset name lands in an SVG attribute
    data, record = _server(tmp_path)
    row = _report(NOW)
    row["report"]["final_balances"] = {'X" onload="alert(1)': "1"}
    _lines(data / dashboard.REPORTS, [row])
    page = dashboard.render(data, record, NOW)
    assert 'onload="alert' not in page
    assert "X&quot; onload=&quot;alert(1) balance" in page


def test_panels_show_their_data_time(tmp_path: Path) -> None:
    # T33-3
    data, record = _server(tmp_path)
    page = dashboard.render(data, record, NOW)
    assert f"Latest values from the report at {NOW.isoformat()}" in page  # L-02
    assert f"BTC: last 0.01 (report at {NOW.isoformat()})" in page


def test_an_unrepresentable_bar_is_invalid_not_a_crash(tmp_path: Path) -> None:
    # T33R-1
    data, record = _server(tmp_path)
    _lines(data / dashboard.BARS, [{"open_time": "9999-12-31T23:30:00+00:00"}])
    page = dashboard.render(data, record, NOW)
    assert "bars: invalid line 1" in page
    assert "<section class=red><h2>Health" in page


def test_a_non_numeric_balance_is_invalid(tmp_path: Path) -> None:
    # T33R-2: never an older value under a newer time
    data, record = _server(tmp_path)
    late = _report(NOW)
    late["report"]["final_balances"] = {"BTC": "n/a"}
    _lines(data / dashboard.REPORTS, [_report(NOW - timedelta(hours=1)), late])
    page = dashboard.render(data, record, NOW)
    assert "reports: invalid line 2" in page
    assert "BTC: last" not in page


def test_an_asset_missing_from_the_latest_report_keeps_its_own_time(
    tmp_path: Path,
) -> None:
    # T33R2-1: BTC at 11:00, then only ETH at 12:00
    data, record = _server(tmp_path)
    early, late = _report(NOW - timedelta(hours=1)), _report(NOW)
    late["report"]["final_balances"] = {"ETH": "2"}
    _lines(data / dashboard.REPORTS, [early, late])
    page = dashboard.render(data, record, NOW)
    assert (
        f"BTC: last 0.01 (report at {(NOW - timedelta(hours=1)).isoformat()})" in page
    )
    assert f"ETH: last 2 (report at {NOW.isoformat()})" in page


def test_sandbox_check_accepts_an_input_not_written_yet(tmp_path: Path) -> None:
    # server 2026-10-18: incidents.jsonl does not exist until a first incident
    missing = tmp_path / "incidents.jsonl"
    results = dict(dashboard.sandbox_check([missing], [], tmp_path / "secret"))
    assert results[f"{missing} is absent; can list {tmp_path}"] is True


def test_a_listed_input_that_cannot_be_found_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # T33F-1: e.g. a dangling link: the name is listed, the read finds nothing
    present = tmp_path / "incidents.jsonl"
    present.write_text("", encoding="utf-8")

    def gone(self: Path) -> bytes:
        raise FileNotFoundError(self)

    monkeypatch.setattr(Path, "read_bytes", gone)
    results = dict(dashboard.sandbox_check([present], [], tmp_path / "secret"))
    assert results[f"{present} is absent; can list {tmp_path}"] is False
