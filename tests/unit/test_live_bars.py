"""Roadmap 2 Task 26: live closed bars from Binance's public API (fake
transport, sockets blocked)."""

from __future__ import annotations

import json
import socket
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from aqt.data.binance_public import FetchResponse, PublicRequest
from aqt.data.live_bars import (
    KLINES_URL,
    TIME_URL,
    LiveBarError,
    LiveBarStore,
    fetch_new_bars,
    parse_klines,
)

T0 = datetime(2026, 9, 29, tzinfo=UTC)
HOUR = timedelta(hours=1)
H_MS = 3_600_000
SKEW = timedelta(seconds=5)


@pytest.fixture(autouse=True)
def _no_sockets(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_: object, **__: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)


def _ms(moment: datetime) -> int:
    return int(moment.timestamp() * 1000)


def _row(open_time: datetime, price: float = 100.0) -> list[object]:
    o = _ms(open_time)
    p = str(price)
    return [o, p, p, p, p, "5.0", o + H_MS - 1, "500", 10, "2", "200", "0"]


class Exchange:
    """Answers /time and /klines from a list of bar rows, like Binance."""

    def __init__(self, rows: list[list[object]], server: datetime) -> None:
        self.rows = rows
        self.server = server
        self.requests: list[PublicRequest] = []

    def __call__(self, request: PublicRequest) -> FetchResponse:
        self.requests.append(request)
        parts = urlsplit(request.url)
        if request.url == TIME_URL:
            body = {"serverTime": _ms(self.server)}
            return FetchResponse(200, json.dumps(body).encode())
        assert f"https://{parts.hostname}{parts.path}" == KLINES_URL
        query = parse_qs(parts.query)
        start = int(query["startTime"][0])
        limit = int(query["limit"][0])
        chosen = [r for r in self.rows if int(r[0]) >= start][:limit]  # type: ignore[call-overload]
        return FetchResponse(200, json.dumps(chosen).encode())


def _hours(n: int, forming: bool = True) -> list[list[object]]:
    rows = [_row(T0 + i * HOUR, 100.0 + i) for i in range(n)]
    if forming:
        rows.append(_row(T0 + n * HOUR, 999.0))  # the hour still open
    return rows


def test_a_fresh_store_gets_every_closed_bar_and_not_the_forming_one(
    tmp_path: Path,
) -> None:
    now = T0 + 5 * HOUR + timedelta(minutes=3)
    exchange = Exchange(_hours(5), now)
    store = LiveBarStore(tmp_path / "bars.jsonl")
    result = fetch_new_bars(exchange, store, "BTCUSDT", now, SKEW, start=T0)
    assert result.appended == 5
    assert [b.close for b in store.bars()] == [100.0, 101.0, 102.0, 103.0, 104.0]
    assert result.last_open_time == T0 + 4 * HOUR
    for request in exchange.requests:
        assert "apiKey" not in request.url and request.headers == ()


def test_a_second_fetch_resumes_after_the_last_bar(tmp_path: Path) -> None:
    store = LiveBarStore(tmp_path / "bars.jsonl")
    fetch_new_bars(
        Exchange(_hours(3), T0 + 3 * HOUR),
        store,
        "BTCUSDT",
        T0 + 3 * HOUR,
        SKEW,
        start=T0,
    )
    later = T0 + 6 * HOUR + timedelta(seconds=1)
    exchange = Exchange(_hours(6), later)
    result = fetch_new_bars(exchange, store, "BTCUSDT", later, SKEW)
    assert result.appended == 3
    assert len(store.bars()) == 6
    start = parse_qs(urlsplit(exchange.requests[-1].url).query)["startTime"][0]
    assert int(start) == _ms(T0 + 3 * HOUR)


def test_a_gap_in_the_reply_appends_nothing(tmp_path: Path) -> None:
    rows = _hours(5)
    del rows[2]  # Binance skipped an hour
    store = LiveBarStore(tmp_path / "bars.jsonl")
    now = T0 + 5 * HOUR
    with pytest.raises(LiveBarError, match="gap"):
        fetch_new_bars(Exchange(rows, now), store, "BTCUSDT", now, SKEW, start=T0)
    assert store.bars() == ()


def test_a_gap_at_the_start_is_refused(tmp_path: Path) -> None:
    store = LiveBarStore(tmp_path / "bars.jsonl")
    now = T0 + 5 * HOUR
    with pytest.raises(LiveBarError, match="gap"):
        fetch_new_bars(
            Exchange(_hours(5)[2:], now), store, "BTCUSDT", now, SKEW, start=T0
        )


def test_duplicates_and_out_of_order_bars_are_refused(tmp_path: Path) -> None:
    store = LiveBarStore(tmp_path / "bars.jsonl")
    bars = parse_klines(json.dumps(_hours(3, forming=False)).encode(), T0 + 3 * HOUR)
    store.append(bars)
    with pytest.raises(LiveBarError, match="duplicate or out of order"):
        store.append(bars[-1:])
    with pytest.raises(LiveBarError, match="duplicate or out of order"):
        store.append(bars[:1])
    assert len(store.bars()) == 3


@pytest.mark.parametrize(
    "bad",
    [
        lambda r: r.__setitem__(6, int(r[0]) + H_MS),  # runs past the hour
        lambda r: r.__setitem__(0, int(r[0]) + 60_000),  # not on the hour
        lambda r: r.__setitem__(2, "1.0"),  # high below the close
        lambda r: r.__setitem__(4, "nan"),  # not a price
    ],
)
def test_an_irregular_closed_bar_is_refused_not_skipped(bad: object) -> None:
    rows = _hours(3, forming=False)
    bad(rows[1])  # type: ignore[operator]
    with pytest.raises(LiveBarError):
        parse_klines(json.dumps(rows).encode(), T0 + 5 * HOUR)


def test_an_unclosed_bar_before_the_last_row_is_refused() -> None:
    rows = _hours(3, forming=False)
    with pytest.raises(LiveBarError, match="unclosed"):
        parse_klines(json.dumps(rows).encode(), T0 + HOUR + timedelta(minutes=1))


@pytest.mark.parametrize("offset", [timedelta(seconds=6), timedelta(seconds=-6)])
def test_a_skewed_clock_fetches_nothing(tmp_path: Path, offset: timedelta) -> None:
    now = T0 + 5 * HOUR
    exchange = Exchange(_hours(5), now + offset)
    store = LiveBarStore(tmp_path / "bars.jsonl")
    with pytest.raises(LiveBarError, match="skew"):
        fetch_new_bars(exchange, store, "BTCUSDT", now, SKEW, start=T0)
    assert [r.url for r in exchange.requests] == [TIME_URL]
    assert store.bars() == ()


def test_an_empty_store_needs_a_start_and_symbols_are_allow_listed(
    tmp_path: Path,
) -> None:
    store = LiveBarStore(tmp_path / "bars.jsonl")
    exchange = Exchange(_hours(2), T0 + 2 * HOUR)
    with pytest.raises(LiveBarError, match="explicit start"):
        fetch_new_bars(exchange, store, "BTCUSDT", T0 + 2 * HOUR, SKEW)
    with pytest.raises(LiveBarError, match="not allowed"):
        fetch_new_bars(exchange, store, "DOGEUSDT", T0 + 2 * HOUR, SKEW, start=T0)


def test_more_than_one_page_is_fetched_in_order(tmp_path: Path) -> None:
    now = T0 + 2100 * HOUR + timedelta(seconds=1)
    exchange = Exchange(_hours(2100), now)
    store = LiveBarStore(tmp_path / "bars.jsonl")
    result = fetch_new_bars(exchange, store, "BTCUSDT", now, SKEW, start=T0)
    assert result.appended == 2100
    series = store.series("BTCUSDT")
    assert len(series) == 2100


def test_the_cli_refuses_while_a_key_variable_is_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import importlib.util

    path = Path(__file__).resolve().parents[2] / "scripts" / "fetch_live_bars.py"
    spec = importlib.util.spec_from_file_location("fetch_live_bars", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["fetch_live_bars"] = module
    spec.loader.exec_module(module)
    monkeypatch.setenv("BINANCE_API_KEY", "dummy-not-a-key")
    assert (
        module.main(
            [
                "--store",
                str(tmp_path / "b.jsonl"),
                "--start",
                "2026-09-29T00:00:00+00:00",
            ]
        )
        == 2
    )
    assert not (tmp_path / "b.jsonl").exists()


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "live"


class FixtureExchange:
    """Replays the committed klines fixture (synthetic, in Binance's
    documented row format; no real reply is recorded: the AI makes no call)."""

    def __init__(self, server: datetime) -> None:
        self.body = (FIXTURE / "klines_btcusdt_1h.json").read_bytes()
        self.server = server

    def __call__(self, request: PublicRequest) -> FetchResponse:
        if request.url == TIME_URL:
            body = {"serverTime": _ms(self.server)}
            return FetchResponse(200, json.dumps(body).encode())
        return FetchResponse(200, self.body)


def test_the_committed_fixture_replays_byte_identically(tmp_path: Path) -> None:
    """F26-5: the roadmap's acceptance, as worded."""
    now = T0 + 5 * HOUR + timedelta(minutes=2)
    stores = []
    for name in ("a", "b"):
        store = LiveBarStore(tmp_path / f"{name}.jsonl")
        fetch_new_bars(FixtureExchange(now), store, "BTCUSDT", now, SKEW, start=T0)
        stores.append(store.path.read_bytes())
    expected = (FIXTURE / "expected_store.jsonl").read_bytes()
    assert stores[0] == stores[1] == expected


def test_a_local_clock_ahead_never_stores_the_forming_bar(tmp_path: Path) -> None:
    """F26-1 (the reviewer's scenario): Binance is at 04:59:57 and the local
    clock 4 s ahead, within S-5. The 04:00 hour is still forming on Binance,
    so it is not stored."""
    server = T0 + 5 * HOUR - timedelta(seconds=3)
    now = server + timedelta(seconds=4)
    exchange = Exchange(_hours(4, forming=False) + [_row(T0 + 4 * HOUR, 123.0)], server)
    store = LiveBarStore(tmp_path / "bars.jsonl")
    result = fetch_new_bars(exchange, store, "BTCUSDT", now, SKEW, start=T0)
    assert result.appended == 4
    assert result.last_open_time == T0 + 3 * HOUR
    assert 123.0 not in [b.close for b in store.bars()]


def test_a_torn_store_line_is_a_named_refusal(tmp_path: Path) -> None:
    """F26-2: a crash mid-append leaves a torn line; the store refuses,
    naming the file and line, instead of raising a raw parse error."""
    store = LiveBarStore(tmp_path / "bars.jsonl")
    store.append(parse_klines(json.dumps(_hours(1, forming=False)).encode(), T0 + HOUR))
    with store.path.open("a", encoding="utf-8") as handle:
        handle.write('{"close": 100.0, "hi')
    with pytest.raises(LiveBarError, match="bars.jsonl line 2"):
        store.bars()


@pytest.mark.parametrize(
    "start",
    [
        datetime(2025, 6, 1, tzinfo=UTC),  # lockbox
        datetime(2024, 1, 1, tzinfo=UTC),  # confirmation
        datetime(2026, 8, 31, 23, tzinfo=UTC),  # last lockbox hour
    ],
)
def test_the_store_never_starts_in_restricted_data(
    tmp_path: Path, start: datetime
) -> None:
    """F26-3: no start before 2026-09-01; refused before any request."""
    exchange = Exchange(_hours(3), T0)
    store = LiveBarStore(tmp_path / "bars.jsonl")
    with pytest.raises(LiveBarError, match="lockbox"):
        fetch_new_bars(exchange, store, "BTCUSDT", T0, SKEW, start=start)
    assert exchange.requests == [] and store.bars() == ()


def test_a_bad_start_is_refused_before_any_request(tmp_path: Path) -> None:
    """F26-4: input checks come first, so a bad start never reaches the
    network."""
    exchange = Exchange(_hours(3), T0)
    store = LiveBarStore(tmp_path / "bars.jsonl")
    with pytest.raises(LiveBarError, match="UTC"):
        fetch_new_bars(
            exchange, store, "BTCUSDT", T0, SKEW, start=datetime(2026, 9, 29)
        )
    assert exchange.requests == []


def test_the_cli_turns_network_errors_into_a_refusal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F26-4: a failed request is exit 2, not a traceback."""
    import importlib.util
    import urllib.error

    path = Path(__file__).resolve().parents[2] / "scripts" / "fetch_live_bars.py"
    spec = importlib.util.spec_from_file_location("fetch_live_bars_net", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["fetch_live_bars_net"] = module
    spec.loader.exec_module(module)

    def down(_: PublicRequest) -> FetchResponse:
        raise urllib.error.URLError("no route")

    monkeypatch.setattr(module, "urllib_transport", down)
    monkeypatch.delenv("BINANCE_API_KEY", raising=False)
    args = [
        "--store",
        str(tmp_path / "b.jsonl"),
        "--start",
        "2026-09-29T00:00:00+00:00",
    ]
    assert module.main(args) == 2
