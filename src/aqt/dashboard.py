"""Read-only dashboard page for forward paper trading (Task 33).

`review/roadmap/DASHBOARD_PROPOSAL.md`, as accepted by Sol and approved by
the owner (`DASHBOARD_OWNER_ANSWERS.md`). `build` reads the forward paper
files and writes one static HTML page; it never writes anywhere else, and it
has no control. Every file-derived text is HTML-escaped (DB-2). Each input is
absent, pending (an unterminated last line), invalid or valid, and is shown
as such: nothing is invented (DB-4). Nothing here is evidence of an edge.
"""

from __future__ import annotations

import html
import json
import math
import os
import socket
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path
from typing import Any, Final

from aqt.core.deployment import APPROVED
from aqt.core.ledger import LedgerError, read_entries

ABSENT: Final[str] = "absent"
PENDING: Final[str] = "pending"
INVALID: Final[str] = "invalid"
VALID: Final[str] = "valid"

STALE: Final[timedelta] = timedelta(hours=2)  # DB-5
FALLBACK: Final[str] = "HORIZON_FALLBACK"  # aqt.metrics.statistics (DBR-1)
SHOWN: Final[int] = 20
REPORTS: Final[str] = "forward/account-1/forward_reports.jsonl"
INCIDENTS: Final[str] = "forward/account-1/incidents.jsonl"
BARS: Final[str] = "live/BTCUSDT-1h.jsonl"
BANNER: Final[str] = (
    "Paper trading, simulated money. This shows the app's recorded activity, "
    "not that the strategy has an edge."
)


@dataclass(frozen=True, slots=True)
class Source:
    """One input file as found: its state, its complete rows, and why."""

    state: str
    rows: tuple[Any, ...] = ()
    note: str = ""


def report_problem(row: object) -> str | None:
    """Why a forward report row cannot be shown, or None (T33-1)."""
    if not isinstance(row, dict):
        return "not a JSON object"
    if _when(row.get("at")) is None:
        return "'at' is not a time with a zone"
    step, count = row.get("report"), row.get("l02")
    if not isinstance(step, dict) or not isinstance(count, dict):
        return "'report' or 'l02' is not an object"
    for key, kind in (
        ("final_balances", dict),
        ("governor_refusals", dict),
        ("refused", list),
    ):
        if not isinstance(step.get(key, kind()), kind):
            return f"'{key}' is not a {kind.__name__}"
    refusals = step.get("governor_refusals", {})
    if not all(type(n) is int for n in refusals.values()):
        return "'governor_refusals' holds a non-integer"
    # T33R-2: a skipped amount would show an older value under a newer time
    if any(_number(v) is None for v in step.get("final_balances", {}).values()):
        return "'final_balances' holds a non-number"
    return None


def bar_problem(row: object) -> str | None:
    """Why a bar store row cannot be shown, or None; a row without
    `open_time` (a gap record) is kept and not shown."""
    if not isinstance(row, dict):
        return "not a JSON object"
    if "open_time" not in row:
        return None
    opened = _when(row["open_time"])
    if opened is None:
        return "'open_time' is not a time with a zone"
    try:
        opened + timedelta(hours=1)
    except OverflowError:  # T33R-1: its close is not a representable time
        return "'open_time' has no representable close"
    return None


def read_jsonl(
    path: Path, problem: Callable[[object], str | None] = lambda row: None
) -> Source:
    """Complete, newline-terminated JSON rows of `path` (DB-4). An
    unterminated last line is a write in progress: the rows before it are
    kept and the source is pending. Any unparsable complete line, or a row
    `problem` refuses, makes the whole source invalid (T33-1)."""
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return Source(ABSENT)
    except OSError as error:
        return Source(INVALID, note=f"unreadable: {error}")
    lines = data.split(b"\n")
    tail = lines.pop()
    try:
        rows = tuple(json.loads(line) for line in lines)
    except ValueError as error:  # JSON and UTF-8 errors alike
        return Source(INVALID, note=f"not valid JSON lines: {error}")
    for number, row in enumerate(rows, 1):
        why = problem(row)
        if why is not None:
            return Source(INVALID, note=f"line {number}: {why}")
    if tail:
        return Source(PENDING, rows, "last line is still being written")
    return Source(VALID, rows) if rows else Source(ABSENT, note="empty")


def read_ledger(path: Path) -> Source:
    """Entries of a hash-chained ledger, shown only when the whole chain
    verifies (DBR-4); a torn last line alone is a write in progress."""
    try:
        if not path.exists():
            return Source(ABSENT)
        entries = read_entries(path)
    except OSError as error:
        return Source(INVALID, note=f"unreadable: {error}")
    except LedgerError as error:
        problem = str(error)
        state = PENDING if "torn trailing write" in problem else INVALID
        return Source(state, note=problem)
    return Source(VALID, entries) if entries else Source(ABSENT, note="empty")


def _when(text: object) -> datetime | None:
    try:
        moment = datetime.fromisoformat(str(text))
    except ValueError:
        return None
    return moment if moment.tzinfo else None


def _number(value: object) -> float | None:
    try:
        number = float(str(value))
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def _e(value: object) -> str:
    return html.escape(str(value), quote=True)


def _age(now: datetime, then: datetime | None) -> str:
    if then is None:
        return "unknown"
    minutes = int((now - then).total_seconds() // 60)
    return f"{minutes // 60} h {minutes % 60:02d} min"


def _state(source: Source, label: str) -> str:
    if source.state == VALID:
        return ""
    return f'<p class="warn">{_e(label)}: {_e(source.state)} {_e(source.note)}</p>'


def health(reports: Source, bars: Source, now: datetime) -> tuple[bool, str]:
    """DB-5: the last reported step, its age and the last bar's age. Red on a
    stale or future report or bar (T33-2), a reported refusal, or unknown
    data. Rows are already checked by `report_problem` and `bar_problem`.
    Governor refusals are shown, not red: they are the governor working."""
    last = reports.rows[-1] if reports.rows else {"report": {}}
    step = last["report"]
    at = _when(last.get("at"))
    bar_rows = [r for r in bars.rows if "open_time" in r]
    opened = _when(bar_rows[-1]["open_time"]) if bar_rows else None
    closed = opened + timedelta(hours=1) if opened else None
    refused = step.get("refused") or []
    governor = sum(step.get("governor_refusals", {}).values())
    red = (
        at is None
        or closed is None
        or not timedelta(0) <= now - at <= STALE
        or not timedelta(0) <= now - closed <= STALE
        or bool(refused)
    )
    body = (
        f"<p>Last reported step: {_e(at.isoformat() if at else 'unknown')}, "
        f"mode {_e(step.get('final_mode', 'unknown'))}, health-breach hours "
        f"{_e(step.get('health_breach_hours', 'unknown'))}.</p>"
        f"<p>Age of the last report: {_e(_age(now, at))}. "
        f"Age of the last bar (since its close): {_e(_age(now, closed))}.</p>"
        f"<p>Refusals in the last step: {_e(', '.join(map(str, refused)) or 'none')}"
        f". Governor refusals in the last step: {_e(governor)}.</p>"
    )
    return red, body


def _spark(values: Sequence[float], unit: str, at: str) -> str:
    """One inline SVG line; numbers only, already checked finite. `at` is
    the time of the report the last value comes from (T33R2-1)."""
    low, high = min(values), max(values)
    span = (high - low) or 1.0
    step = 600 / max(len(values) - 1, 1)
    points = " ".join(
        f"{i * step:.1f},{110 - (v - low) / span * 100:.1f}"
        for i, v in enumerate(values)
    )
    return (
        f'<svg viewBox="0 0 600 120" width="100%" height="120" role="img" '
        f'aria-label="{_e(unit)} balance"><polyline fill="none" '
        f'stroke="currentColor" stroke-width="2" points="{points}"/></svg>'
        f"<p>{_e(unit)}: last {values[-1]:g} (report at {_e(at)}), "
        f"low {low:g}, high {high:g}</p>"
    )


def balances(reports: Source) -> str:
    """DB-6: each asset on its own scale, with its unit; no equity line."""
    series: dict[str, list[float]] = {}
    last_at: dict[str, str] = {}
    for row in reports.rows:  # amounts are checked numbers (T33R-2)
        for asset, amount in row["report"].get("final_balances", {}).items():
            series.setdefault(str(asset), []).append(float(amount))
            last_at[str(asset)] = str(row["at"])
    if not series:
        return "<p>no data</p>"
    return "".join(
        _spark(values, asset, last_at[asset])
        for asset, values in sorted(series.items())
    )


def _data_time(reports: Source) -> str:
    """T33-3: the time of the report a panel's latest values come from."""
    return f"<p>Latest values from the report at {_e(reports.rows[-1]['at'])}.</p>"


def l02(reports: Source) -> str:
    """DB-7, DBR-1: counts, method and reason; no completion date."""
    if not reports.rows:
        return "<p>no data</p>"
    count = reports.rows[-1]["l02"]
    method = count.get("method")
    note = (
        "<p>This count uses the fallback method. It is not the same quantity "
        "as the primary (Newey-West) count.</p>"
        if method == FALLBACK
        else ""
    )
    return _data_time(reports) + (
        f"<p>Raw decisions {_e(count.get('raw_decisions'))}; effective decisions "
        f"{_e(count.get('effective_decisions'))} of the {_e(count.get('target'))} "
        f"needed; method {_e(method)}; reason {_e(count.get('reason') or 'none')}."
        f"</p>{note}<p>A waiting condition, not evidence of an edge.</p>"
    )


def activity(reports: Source) -> str:
    """DB-8: totals per reported step, newest first."""
    rows = []
    for row in reversed(reports.rows[-SHOWN:]):
        step = row["report"]
        total = sum(step.get("governor_refusals", {}).values())
        cells = (
            row["at"],
            step.get("hours"),
            step.get("scheduled_decisions"),
            step.get("authorizations"),
            step.get("orders_sent"),
            total,
        )
        rows.append("<tr>" + "".join(f"<td>{_e(c)}</td>" for c in cells) + "</tr>")
    head = "".join(
        f"<th>{h}</th>"
        for h in (
            "step at",
            "hours",
            "decisions",
            "authorizations",
            "orders",
            "governor refusals",
        )
    )
    return f"<table><tr>{head}</tr>{''.join(rows)}</table>" if rows else "<p>none</p>"


def incidents(source: Source) -> str:
    rows = [
        f"<tr><td>{_e(e.recorded_at_utc)}</td><td>{_e(e.record_type)}</td>"
        f"<td>{_e(e.payload_json)}</td></tr>"
        for e in reversed(source.rows[-SHOWN:])
    ]
    return f"<table>{''.join(rows)}</table>" if rows else "<p>none</p>"


def code_identity(source: Source) -> str:
    """DB-8, DBR-4: the latest approved commit, only from an intact record."""
    if source.state != VALID or source.rows[-1].record_type != APPROVED:
        return "<p>Latest approved commit: unknown.</p>"
    last = source.rows[-1]
    payload = last.payload
    return (
        f"<p>Latest approved commit: <code>{_e(payload.get('commit'))}</code>, "
        f"approved by {_e(payload.get('approved_by'))} at "
        f"{_e(last.recorded_at_utc)}.</p>"
    )


def render(data: Path, deployments: Path, now: datetime) -> str:
    """The whole page, computed as of `now` (DBR-2)."""
    reports = read_jsonl(data / REPORTS, report_problem)
    bars = read_jsonl(data / BARS, bar_problem)
    incident_log = read_ledger(data / INCIDENTS)
    record = read_ledger(deployments)
    red, health_body = health(reports, bars, now)
    panels = (
        ("Health", _state(reports, "reports") + _state(bars, "bars") + health_body),
        ("Balances", balances(reports)),
        ("L-02 status", l02(reports)),
        ("Activity per reported step", activity(reports)),
        (
            "Incidents (last 20)",
            _state(incident_log, "incidents") + incidents(incident_log),
        ),
        ("Code identity", _state(record, "deployment record") + code_identity(record)),
    )
    sections = "".join(
        f"<section{' class=red' if title == 'Health' and red else ''}>"
        f"<h2>{title}</h2>{body}</section>"
        for title, body in panels
    )
    return (
        "<!doctype html><html lang=en><head><meta charset=utf-8>"
        '<meta http-equiv="Content-Security-Policy" '
        "content=\"default-src 'none'; style-src 'unsafe-inline'\">"
        '<meta name=viewport content="width=device-width,initial-scale=1">'
        "<title>AQT paper dashboard</title><style>"
        "body{font:15px system-ui,sans-serif;margin:16px;max-width:900px}"
        "section{border:1px solid #888;border-radius:6px;padding:8px 12px;"
        "margin:12px 0}.red{border:3px solid #c00;background:#fee}"
        ".warn{color:#a40}.banner{font-weight:bold}table{border-collapse:"
        "collapse;font-size:13px}td,th{border:1px solid #ccc;padding:2px 6px}"
        "</style></head><body>"
        f'<p class="banner">{_e(BANNER)}</p>'
        f"<h1>As of {_e(now.isoformat(timespec='seconds'))}</h1>"
        "<p>The page is a snapshot: if this time is more than 30 minutes old, "
        "the dashboard itself is not updating, whatever the colours say.</p>"
        f"{sections}</body></html>"
    )


def build(data: Path, deployments: Path, out: Path, now: datetime) -> Path:
    """Write the page to `out/staging`, then rename it to
    `out/page/index.html`, so a copy never sees a partial page (DBR-3)."""
    staging, page = out / "staging", out / "page"
    staging.mkdir(exist_ok=True)
    page.mkdir(exist_ok=True)
    temporary = staging / "index.html"
    temporary.write_text(render(data, deployments, now), encoding="utf-8")
    temporary.chmod(0o644)
    target = page / "index.html"
    os.replace(temporary, target)
    return target


def sandbox_check(
    readable: Sequence[Path], unwritable: Sequence[Path], secret: Path
) -> list[tuple[str, bool]]:
    """The proposal's server checks, run inside the generator's own unit
    (section 4): each line is a check and whether it held."""
    results: list[tuple[str, bool]] = []
    for path in readable:
        if path.exists():
            results.append((f"can read {path}", _try(path.read_bytes)))
        else:  # not written yet, e.g. no incident ever: the page shows "absent"
            listed = _try(partial(os.listdir, path.parent))
            results.append((f"{path} is absent; can list {path.parent}", listed))
    for directory in unwritable:
        probe = directory / ".aqt-dashboard-check"
        wrote = _try(partial(probe.touch, exist_ok=False))
        if wrote:
            probe.unlink()  # leave nothing behind
        results.append((f"cannot write in {directory}", not wrote))
    results.append((f"cannot read {secret}", not _try(secret.read_bytes)))
    unix = getattr(socket, "AF_UNIX", socket.AF_INET)  # absent on some Windows
    for family, name in ((socket.AF_INET, "inet"), (unix, "Unix")):
        opened = _try(partial(_open_socket, family))
        results.append((f"cannot open a socket ({name})", not opened))
    results.append(("io_uring_setup is refused", _io_uring_refused()))
    return results


def _open_socket(family: int) -> None:
    socket.socket(family).close()


def _try(action: Callable[[], object]) -> bool:
    try:
        action()
    except OSError:
        return False
    return True


def _io_uring_refused() -> bool:
    if sys.platform != "linux":
        return False  # not checkable here; never reported as held
    import ctypes

    libc = ctypes.CDLL(None, use_errno=True)
    params = ctypes.create_string_buffer(120)
    fd = libc.syscall(425, 1, params)  # x86-64 io_uring_setup
    if fd >= 0:
        os.close(fd)
        return False
    return True
