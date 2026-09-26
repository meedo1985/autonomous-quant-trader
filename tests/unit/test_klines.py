"""Synthetic tests for the strict kline archive parser. No market data."""

from __future__ import annotations

import hashlib
import io
import re
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from aqt.data import klines
from aqt.data.bars import Bar
from aqt.data.binance_public import EXPLORATION_MONTHS
from aqt.data.klines import (
    WINDOW_END_EXCLUSIVE,
    WINDOW_START,
    KlineError,
    OutageRow,
    parse_archive,
    parser_code_sha256,
)

HOUR_MS = 3_600_000
JAN_2020 = int(datetime(2020, 1, 1, tzinfo=UTC).timestamp()) * 1000


def row(
    open_ms: int,
    o: str = "100.0",
    h: str = "110.0",
    low: str = "90.0",
    c: str = "105.0",
    v: str = "2.5",
    close_ms: int | None = None,
) -> str:
    close = open_ms + HOUR_MS - 1 if close_ms is None else close_ms
    return f"{open_ms},{o},{h},{low},{c},{v},{close},250.0,7,1.0,100.0,0"


def archive(rows: list[str], member: str = "BTCUSDT-1h-2020-01.csv") -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as handle:
        handle.writestr(member, "\n".join(rows) + "\n")
    return buffer.getvalue()


def parse(content: bytes) -> tuple[Bar, ...]:
    parsed = parse_archive(content, symbol="BTCUSDT", year=2020, month=1)
    assert parsed.outage_rows == ()
    return parsed.bars


def test_archive_round_trips_to_exact_bars() -> None:
    bars = parse(
        archive([row(JAN_2020), row(JAN_2020 + HOUR_MS, c="99.5", low="95.0")])
    )
    assert bars == (
        Bar(datetime(2020, 1, 1, tzinfo=UTC), 100.0, 110.0, 90.0, 105.0, 2.5),
        Bar(datetime(2020, 1, 1, 1, tzinfo=UTC), 100.0, 110.0, 95.0, 99.5, 2.5),
    )


@pytest.mark.parametrize(
    ("rows", "message"),
    [
        ([row(JAN_2020) + ",extra"], "expected 12 fields"),
        ([row(JAN_2020 * 1000)], "13-digit millisecond"),  # microsecond era
        ([row(JAN_2020 - HOUR_MS)], "outside 2020-01"),
        ([row(JAN_2020, close_ms=12)], "13-digit millisecond"),
        ([row(JAN_2020, h="80.0")], "line 1"),  # high below low
        ([row(JAN_2020, o="nan")], "line 1"),
        ([row(JAN_2020, v="abc")], "line 1"),
        ([row(JAN_2020), row(JAN_2020 + HOUR_MS, v="-1")], "line 2"),
    ],
)
def test_malformed_row_raises_and_returns_nothing(
    rows: list[str], message: str
) -> None:
    with pytest.raises(KlineError, match=re.escape(message)):
        parse(archive(rows))


def test_empty_wrongly_named_or_corrupt_archives_raise() -> None:
    empty = io.BytesIO()
    with zipfile.ZipFile(empty, "w") as handle:
        handle.writestr("BTCUSDT-1h-2020-01.csv", "")
    with pytest.raises(KlineError, match="no rows"):
        parse(empty.getvalue())
    with pytest.raises(KlineError, match="unreadable"):
        parse(archive([row(JAN_2020)])[:-30])  # truncated archive
    with pytest.raises(KlineError, match="exactly"):
        parse(archive([row(JAN_2020)], member="ETHUSDT-1h-2020-01.csv"))
    with pytest.raises(KlineError, match="unreadable"):
        parse(b"not a zip archive")


def test_parser_identity_ignores_checkout_line_endings() -> None:
    source = Path(klines.__file__).read_bytes().replace(b"\r\n", b"\n")
    assert parser_code_sha256() == hashlib.sha256(source).hexdigest()


def test_window_matches_protocol_and_download_months() -> None:
    text = (Path(__file__).parents[2] / "protocols" / "protocol_v1.yaml").read_text(
        encoding="utf-8"
    )
    match = re.search(r'exploration: \{start: "([^"]+)", end: "([^"]+)"\}', text)
    assert match is not None
    start = datetime.fromisoformat(match.group(1))
    end = datetime.fromisoformat(match.group(2))
    assert WINDOW_START == start
    assert WINDOW_END_EXCLUSIVE == end + timedelta(seconds=1)
    last_hour = WINDOW_END_EXCLUSIVE - timedelta(hours=1)
    assert (WINDOW_START.year, WINDOW_START.month) == EXPLORATION_MONTHS[0]
    assert (last_hour.year, last_hour.month) == EXPLORATION_MONTHS[1]


@pytest.mark.parametrize(
    ("open_ms", "close_ms", "reason"),
    [
        (JAN_2020 + 1_694_789, JAN_2020 + 1_694_789 + HOUR_MS - 1, "not on the hour"),
        (JAN_2020, JAN_2020 + 1_753_419, "ends before the hour"),
        (JAN_2020, JAN_2020 + HOUR_MS, "runs past the hour"),
        (JAN_2020 + HOUR_MS, JAN_2020 + 1_000, "before open_time"),
    ],
)
def test_outage_rows_become_no_bar_and_are_reported(
    open_ms: int, close_ms: int, reason: str
) -> None:
    """Shapes seen in real Binance archives around exchange maintenance."""
    regular = row(JAN_2020 + 5 * HOUR_MS)
    parsed = parse_archive(
        archive([row(open_ms, close_ms=close_ms), regular]),
        symbol="BTCUSDT",
        year=2020,
        month=1,
    )
    assert [bar.open_time for bar in parsed.bars] == [
        datetime(2020, 1, 1, 5, tzinfo=UTC)
    ]
    [outage] = parsed.outage_rows
    assert outage == OutageRow(
        "BTCUSDT-1h-2020-01.csv", 1, open_ms, close_ms, outage.reason
    )
    assert reason in outage.reason


def test_outage_rows_are_still_checked_for_shape() -> None:
    with pytest.raises(KlineError, match="expected 12 fields"):
        parse_archive(
            archive([row(JAN_2020 + 1) + ",x"]), symbol="BTCUSDT", year=2020, month=1
        )


_SHORT = JAN_2020 + 1_000  # a bar that closes one second after it opens


@pytest.mark.parametrize(
    ("open_ms", "close_ms"),
    [(JAN_2020, _SHORT), (JAN_2020 + 1_694_789, JAN_2020 + 1_694_789 + HOUR_MS - 1)],
)
@pytest.mark.parametrize(
    "values",
    [
        {"o": "nan"},
        {"v": "abc"},
        {"v": "-1"},
        {"h": "80.0"},  # high below low
        {"low": "0"},
        {"c": "inf"},
    ],
)
def test_malformed_values_fail_even_on_an_outage_row(
    open_ms: int, close_ms: int, values: dict[str, str]
) -> None:
    """R-1: an irregular time must not let a malformed row pass as an outage."""
    rows = [row(open_ms, close_ms=close_ms, **values), row(JAN_2020 + 5 * HOUR_MS)]
    with pytest.raises(KlineError, match="line 1"):
        parse_archive(archive(rows), symbol="BTCUSDT", year=2020, month=1)
