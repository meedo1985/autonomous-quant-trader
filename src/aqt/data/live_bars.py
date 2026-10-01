"""Live closed 1h bars from Binance's public market-data API (roadmap 2,
Task 26; owner answer Q-A, `review/roadmap/ROADMAP_2_OWNER_ANSWERS.md`).

The app, not the AI, calls `data-api.binance.vision` with no credential,
through the Task 13 request guard (`PublicRequest`): an allow-listed HTTPS
host, no key, signature or auth header, redirects refused.

Every row passes the `aqt.data.bars` checks and must span exactly its hour.
The bar still forming is left out; a malformed or irregular closed bar is
refused, never skipped. Bars are appended to a local store that accepts only
the next hour: a duplicate or an out-of-order bar refuses the whole batch; at
a gap the bars before it are stored and the rest refused. Nothing is filled
or corrected (Constitution section 6); the store continues after a gap only
on the owner's signed gap record (Q27-3). A clock
more than `max_skew` away from Binance's refuses the fetch (owner setting
S-5: 5 s).
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from itertools import pairwise
from pathlib import Path
from typing import Final
from urllib.parse import urlencode

from aqt.core.ledger import LedgerError, _exclusive_lock
from aqt.data.bars import (
    BAR_INTERVAL,
    Bar,
    BarSemanticsError,
    BarSeries,
    require_aligned_utc,
    require_utc,
)
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
    "GapRecord",
    "LiveBarError",
    "LiveBarStore",
    "fetch_new_bars",
    "parse_klines",
]

LIVE_START_FLOOR: Final[datetime] = datetime(2026, 9, 1, tzinfo=UTC)
"""The first hour after the protocol's lockbox partition
(`protocols/protocol_v1.yaml:67`, ends 2026-08-31T23:59:59Z). A live store
never starts inside confirmation or lockbox data (F26-3)."""

KLINES_URL: Final[str] = "https://data-api.binance.vision/api/v3/klines"
TIME_URL: Final[str] = "https://data-api.binance.vision/api/v3/time"
MAX_LIMIT: Final[int] = 1000
_HOUR_MS: Final[int] = 3_600_000
_BAR_KEYS: Final = frozenset(
    {"close", "high", "low", "open", "open_time", "symbol", "volume"}
)
_GAP_KEYS: Final = frozenset(
    {
        "gap_actor",
        "gap_first_missing",
        "gap_recorded_at",
        "gap_resumes_at",
        "gap_statement",
        "symbol",
    }
)


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


@dataclass(frozen=True, slots=True)
class GapRecord:
    """The owner's signed statement that Binance has no bars from
    `first_missing` until `resumes_at` (owner answer Q27-3, T26-04). The
    hours stay missing; nothing is filled."""

    first_missing: datetime
    resumes_at: datetime
    actor: str
    statement: str
    recorded_at: datetime

    def __post_init__(self) -> None:
        """The whole contract, on writing and on reading (A27-5)."""
        if not all(
            isinstance(t, str) and t.strip() for t in (self.actor, self.statement)
        ):
            raise LiveBarError("a gap record needs the owner's name and statement")
        try:
            for name in ("first_missing", "resumes_at"):
                require_aligned_utc(getattr(self, name), BAR_INTERVAL, field_name=name)
            require_utc(self.recorded_at, field_name="recorded_at")
        except BarSemanticsError as error:
            raise LiveBarError(str(error)) from None
        if self.resumes_at <= self.first_missing:
            raise LiveBarError(f"gap record ends at {self.resumes_at.isoformat()}")

    def as_row(self, symbol: str) -> dict[str, str]:
        return {
            "gap_actor": self.actor,
            "gap_first_missing": self.first_missing.isoformat(),
            "gap_recorded_at": self.recorded_at.isoformat(),
            "gap_resumes_at": self.resumes_at.isoformat(),
            "gap_statement": self.statement,
            "symbol": symbol,
        }


class LiveBarStore:
    """Append-only JSON-lines file of one symbol's closed bars, one hour
    after another, never before `LIVE_START_FLOOR`; the only jump allowed is
    over an owner-signed `GapRecord` (Q27-3).

    Every row names its symbol, so a store cannot mix symbols (A26-2).
    Reading checks the whole file, not only its last row (A26-3): the
    symbol, the floor, and that each bar is exactly one hour after the one
    before. Appenders are serialized across processes by the ledger's lock
    file, and each re-reads the store under it (A26-1)."""

    def __init__(self, path: Path, symbol: str) -> None:
        if symbol not in ALLOWED_SYMBOLS:
            raise LiveBarError(f"symbol {symbol!r} is not allowed")
        self.path = path
        self.symbol = symbol

    def _read(self) -> tuple[tuple[Bar, ...], tuple[GapRecord, ...], datetime | None]:
        """Every bar, every gap record, and the hour the next bar must open
        at (`None` for an empty store); refuses anything else."""
        if not self.path.exists():
            return (), (), None
        text = self.path.read_text("utf-8")
        lines = text.splitlines()
        if text and not text.endswith("\n"):
            # A write cut off before its newline: refuse before any append
            # joins the next row onto it (A26-4).
            raise LiveBarError(f"{self.path} line {len(lines)}: no final newline")
        bars: list[Bar] = []
        gaps: list[GapRecord] = []
        expected: datetime | None = None
        for number, line in enumerate(lines, start=1):
            where = f"{self.path} line {number}"
            try:
                row = json.loads(line)
                if not isinstance(row, dict) or set(row) not in (_BAR_KEYS, _GAP_KEYS):
                    # Exactly a bar or exactly a gap record, nothing mixed (A27-5).
                    raise ValueError("not a bar row or a gap record row")
                symbol = row["symbol"]
                if "gap_first_missing" in row:
                    gap = GapRecord(
                        datetime.fromisoformat(row["gap_first_missing"]),
                        datetime.fromisoformat(row["gap_resumes_at"]),
                        row["gap_actor"],
                        row["gap_statement"],
                        datetime.fromisoformat(row["gap_recorded_at"]),
                    )
                else:
                    bar = Bar(
                        datetime.fromisoformat(row["open_time"]),
                        row["open"],
                        row["high"],
                        row["low"],
                        row["close"],
                        row["volume"],
                    )
            except (
                ValueError,
                KeyError,
                TypeError,
                BarSemanticsError,
                LiveBarError,
            ) as error:
                # A torn or edited line: refuse, naming it (F26-2).
                raise LiveBarError(f"{where}: {error}") from None
            if symbol != self.symbol:
                raise LiveBarError(f"{where}: {symbol!r} in the {self.symbol} store")
            try:
                if "gap_first_missing" in row:
                    _require_gap(gap, expected)
                    gaps.append(gap)
                    expected = gap.resumes_at
                else:
                    _require_next(bar, expected)
                    bars.append(bar)
                    expected = bar.open_time + BAR_INTERVAL
            except LiveBarError as error:
                raise LiveBarError(f"{where}: {error}") from None
        return tuple(bars), tuple(gaps), expected

    def bars(self) -> tuple[Bar, ...]:
        return self._read()[0]

    def gaps(self) -> tuple[GapRecord, ...]:
        """The owner-signed gaps, in order; their hours have no bar."""
        return self._read()[1]

    def series(self) -> BarSeries:
        """The bars; a recorded gap is a missing interval, never filled."""
        return BarSeries(self.symbol, self.bars())

    def last_open_time(self) -> datetime | None:
        bars = self.bars()
        return bars[-1].open_time if bars else None

    def next_open_time(self) -> datetime | None:
        """The hour the next bar must open at, after any recorded gap."""
        return self._read()[2]

    def acknowledge_gap(
        self,
        first_missing: datetime,
        resumes_at: datetime,
        actor: str,
        statement: str,
        at: datetime,
    ) -> GapRecord:
        """Record the owner's signed statement that Binance has no bars from
        `first_missing` until `resumes_at` (Q27-3). `first_missing` must be
        the hour the store's next bar is due, so every bar before the gap is
        stored first and no valid hour is called missing (A27-4)."""
        gap = GapRecord(first_missing, resumes_at, actor, statement, at)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with _exclusive_lock(self.path):
                expected = self._read()[2]
                if expected is None:
                    raise LiveBarError("an empty store has no gap to record")
                _require_gap(gap, expected)
                self._write([gap.as_row(self.symbol)])
        except LedgerError as error:  # the lock was not acquired
            raise LiveBarError(f"{error}; nothing recorded") from None
        return gap

    def append(self, new: tuple[Bar, ...], first: datetime | None = None) -> None:
        """Append `new`; each bar must be exactly one hour after the last,
        and on an empty store the first must be at `first` when given."""
        if not new:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with _exclusive_lock(self.path):
                self._append_locked(new, first)
        except LedgerError as error:  # the lock was not acquired
            raise LiveBarError(f"{error}; nothing appended") from None

    def _append_locked(self, new: tuple[Bar, ...], first: datetime | None) -> None:
        expected = self.next_open_time()
        try:
            if expected is None:
                _require_next(new[0], None)  # the floor
                expected = new[0].open_time if first is None else first
            for bar in new:
                _require_next(bar, expected)
                expected = bar.open_time + BAR_INTERVAL
        except LiveBarError as error:
            raise LiveBarError(f"{error}; nothing appended") from None
        self._write(
            [
                {
                    "close": b.close,
                    "high": b.high,
                    "low": b.low,
                    "open": b.open,
                    "open_time": b.open_time.isoformat(),
                    "symbol": self.symbol,
                    "volume": b.volume,
                }
                for b in new
            ]
        )

    def _write(self, rows: Sequence[Mapping[str, object]]) -> None:
        """Append `rows`, fsynced; the caller holds the lock."""
        lines = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(lines)
            handle.flush()
            os.fsync(handle.fileno())


def _require_gap(gap: GapRecord, expected: datetime | None) -> None:
    """A gap record starts at the hour the next bar was due and ends at a
    later hour; it never opens a store."""
    if expected is None or gap.first_missing != expected:
        due = "nothing" if expected is None else expected.isoformat()
        raise LiveBarError(
            f"gap record from {gap.first_missing.isoformat()} where {due} is next"
        )


def _require_next(bar: Bar, expected: datetime | None) -> None:
    """`bar` must open at `expected`; a store's first bar (`expected` None)
    must not be before `LIVE_START_FLOOR` (A26-3)."""
    if expected is None:
        if bar.open_time < LIVE_START_FLOOR:
            raise LiveBarError(
                f"bar {bar.open_time.isoformat()} is before "
                f"{LIVE_START_FLOOR.isoformat()}: confirmation and lockbox data "
                "never enter the live store"
            )
        return
    if bar.open_time != expected:
        kind = "gap" if bar.open_time > expected else "duplicate or out of order"
        raise LiveBarError(
            f"{kind}: bar {bar.open_time.isoformat()} where "
            f"{expected.isoformat()} is next"
        )


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
    when the store is empty) and append them. Refuses a skewed clock.
    Every input is checked before any request (F26-4)."""
    now = require_utc(now, field_name="now")
    if symbol != store.symbol:
        raise LiveBarError(f"symbol {symbol} into the {store.symbol} store (A26-2)")
    after = store.next_open_time()  # past any owner-signed gap (Q27-3)
    if after is not None:
        begin = after
    elif start is None:
        raise LiveBarError("an empty store needs an explicit start")
    else:
        try:
            begin = require_aligned_utc(start, BAR_INTERVAL, field_name="start")
        except BarSemanticsError as error:
            raise LiveBarError(str(error)) from None
    if begin < LIVE_START_FLOOR:
        raise LiveBarError(
            f"start {begin.isoformat()} is before {LIVE_START_FLOOR.isoformat()}: "
            "confirmation and lockbox data never enter the live store"
        )
    try:
        server = json.loads(_get(transport, TIME_URL))["serverTime"]
    except (ValueError, KeyError, TypeError) as error:
        raise LiveBarError(f"server time unreadable: {error}") from None
    server_now = _time(int(server))
    skew = now - server_now
    if abs(skew) > max_skew:
        raise LiveBarError(f"clock skew {skew} exceeds {max_skew}; nothing fetched")
    # A bar is closed only when it has ended on both clocks, so a local clock
    # ahead of Binance's cannot store a forming bar (F26-1).
    cutoff = min(now, server_now)
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
        bars = parse_klines(_get(transport, f"{KLINES_URL}?{query}"), cutoff)
        bars = tuple(b for b in bars if b.open_time >= begin)
        # At a gap the bars before it are stored, then the gap refuses: the
        # owner can then record exactly the missing hours (A27-4, Q27-3). A
        # duplicate or reordered bar refuses the whole reply (A27-11).
        whole = 0
        while (
            whole < len(bars) and bars[whole].open_time == begin + whole * BAR_INTERVAL
        ):
            whole += 1
        ordered = all(a.open_time < b.open_time for a, b in pairwise(bars))
        if whole < len(bars) and not ordered:
            store.append(bars, first=begin)  # refuses, nothing stored
        store.append(bars[:whole], first=begin)
        appended += whole
        if whole < len(bars):
            store.append(bars[whole:], first=begin)  # refuses, naming the gap
        if len(bars) < MAX_LIMIT - 1:
            break
        begin = bars[-1].open_time + BAR_INTERVAL
    return FetchResult(appended, store.last_open_time(), skew)
