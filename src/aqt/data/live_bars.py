"""Live closed 1h bars from Binance's public market-data API (roadmap 2,
Task 26; owner answer Q-A, `review/roadmap/ROADMAP_2_OWNER_ANSWERS.md`).

The app, not the AI, calls `data-api.binance.vision` with no credential,
through the Task 13 request guard (`PublicRequest`): an allow-listed HTTPS
host, no key, signature or auth header, redirects refused.

Every row passes the `aqt.data.bars` checks and must span exactly its hour.
The bar still forming is left out; a malformed or irregular closed bar is
refused, never skipped. Bars are appended to a local store that accepts only
the next hour: a gap, a duplicate or an out-of-order bar refuses the whole
batch, and nothing is filled or corrected (Constitution section 6). A clock
more than `max_skew` away from Binance's refuses the fetch (owner setting
S-5: 5 s).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Final
from urllib.parse import urlencode

from aqt.data.bars import BAR_INTERVAL, Bar, BarSemanticsError, BarSeries, require_utc
from aqt.data.binance_public import (
    ALLOWED_SYMBOLS,
    INTERVAL,
    PublicRequest,
    Transport,
)

__all__ = [
    "KLINES_URL",
    "TIME_URL",
    "FetchResult",
    "LiveBarError",
    "LiveBarStore",
    "fetch_new_bars",
    "parse_klines",
]

KLINES_URL: Final[str] = "https://data-api.binance.vision/api/v3/klines"
TIME_URL: Final[str] = "https://data-api.binance.vision/api/v3/time"
MAX_LIMIT: Final[int] = 1000
_HOUR_MS: Final[int] = 3_600_000


class LiveBarError(RuntimeError):
    """A live fetch or append that cannot be completed safely."""


def _ms(moment: datetime) -> int:
    return int(require_utc(moment).timestamp() * 1000)


def _time(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=UTC)


def parse_klines(body: bytes, now: datetime) -> tuple[Bar, ...]:
    """Closed bars from a `/api/v3/klines` reply, in order. The bar whose
    hour has not ended by `now` is dropped; any other bad row is an error."""
    now_ms = _ms(now)
    try:
        rows = json.loads(body)
    except ValueError as error:
        raise LiveBarError(f"klines reply is not JSON: {error}") from None
    if not isinstance(rows, list):
        raise LiveBarError("klines reply is not a list")
    bars: list[Bar] = []
    for index, row in enumerate(rows):
        where = f"klines row {index}"
        if not isinstance(row, list) or len(row) < 7:
            raise LiveBarError(f"{where}: malformed")
        open_ms, close_ms = row[0], row[6]
        if not isinstance(open_ms, int) or not isinstance(close_ms, int):
            raise LiveBarError(f"{where}: times are not integers")
        if close_ms >= now_ms:
            if index != len(rows) - 1:
                raise LiveBarError(f"{where}: an unclosed bar before the last row")
            continue  # the hour still forming
        if open_ms % _HOUR_MS or close_ms != open_ms + _HOUR_MS - 1:
            raise LiveBarError(f"{where}: does not span exactly one hour")
        try:
            bars.append(
                Bar(
                    _time(open_ms),
                    float(row[1]),
                    float(row[2]),
                    float(row[3]),
                    float(row[4]),
                    float(row[5]),
                )
            )
        except (TypeError, ValueError, BarSemanticsError) as error:
            raise LiveBarError(f"{where}: {error}") from None
    return tuple(bars)


class LiveBarStore:
    """Append-only JSON-lines file of closed bars, one hour after another."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def bars(self) -> tuple[Bar, ...]:
        if not self.path.exists():
            return ()
        bars = []
        for line in self.path.read_text("utf-8").splitlines():
            row = json.loads(line)
            bars.append(
                Bar(
                    datetime.fromisoformat(row["open_time"]),
                    row["open"],
                    row["high"],
                    row["low"],
                    row["close"],
                    row["volume"],
                )
            )
        return tuple(bars)

    def series(self, symbol: str) -> BarSeries:
        return BarSeries(symbol, self.bars())

    def last_open_time(self) -> datetime | None:
        bars = self.bars()
        return bars[-1].open_time if bars else None

    def append(self, new: tuple[Bar, ...], first: datetime | None = None) -> None:
        """Append `new`; each bar must be exactly one hour after the last,
        and on an empty store the first must be at `first` when given."""
        if not new:
            return
        last = self.last_open_time()
        if last is not None:
            expected = last + BAR_INTERVAL
        else:
            expected = new[0].open_time if first is None else first
        for bar in new:
            if bar.open_time != expected:
                kind = (
                    "gap" if bar.open_time > expected else "duplicate or out of order"
                )
                raise LiveBarError(
                    f"{kind}: bar {bar.open_time.isoformat()} where "
                    f"{expected.isoformat()} is next; nothing appended"
                )
            expected += BAR_INTERVAL
        lines = "".join(
            json.dumps(
                {
                    "close": b.close,
                    "high": b.high,
                    "low": b.low,
                    "open": b.open,
                    "open_time": b.open_time.isoformat(),
                    "volume": b.volume,
                },
                sort_keys=True,
            )
            + "\n"
            for b in new
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(lines)
            handle.flush()
            os.fsync(handle.fileno())


@dataclass(frozen=True, slots=True)
class FetchResult:
    appended: int
    last_open_time: datetime | None
    skew: timedelta


def _get(transport: Transport, url: str) -> bytes:
    response = transport(PublicRequest(url))
    if response.status != 200:
        raise LiveBarError(f"HTTP {response.status} from {url}")
    return response.body


def fetch_new_bars(
    transport: Transport,
    store: LiveBarStore,
    symbol: str,
    now: datetime,
    max_skew: timedelta,
    start: datetime | None = None,
) -> FetchResult:
    """Fetch every closed bar after the store's last one (or from `start`
    when the store is empty) and append them. Refuses a skewed clock."""
    now = require_utc(now, field_name="now")
    if symbol not in ALLOWED_SYMBOLS:
        raise LiveBarError(f"symbol {symbol!r} is not allowed")
    try:
        server = json.loads(_get(transport, TIME_URL))["serverTime"]
    except (ValueError, KeyError, TypeError) as error:
        raise LiveBarError(f"server time unreadable: {error}") from None
    skew = now - _time(int(server))
    if abs(skew) > max_skew:
        raise LiveBarError(f"clock skew {skew} exceeds {max_skew}; nothing fetched")
    last = store.last_open_time()
    if last is not None:
        begin = last + BAR_INTERVAL
    elif start is not None:
        begin = require_utc(start, field_name="start")
    else:
        raise LiveBarError("an empty store needs an explicit start")
    appended = 0
    while True:
        query = urlencode(
            {
                "symbol": symbol,
                "interval": INTERVAL,
                "startTime": _ms(begin),
                "limit": MAX_LIMIT,
            }
        )
        bars = parse_klines(_get(transport, f"{KLINES_URL}?{query}"), now)
        bars = tuple(b for b in bars if b.open_time >= begin)
        store.append(bars, first=begin)
        appended += len(bars)
        if len(bars) < MAX_LIMIT - 1:
            break
        begin = bars[-1].open_time + BAR_INTERVAL
    return FetchResult(appended, store.last_open_time(), skew)
