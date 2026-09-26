"""Offline tests for the public Binance downloader. Sockets are blocked."""

from __future__ import annotations

import hashlib
import json
import re
import socket
from datetime import UTC, datetime
from pathlib import Path

import pytest

from aqt.data.binance_public import (
    EXPLORATION_MONTHS,
    BinancePublicClient,
    DownloadError,
    FetchResponse,
    PublicRequest,
    archive_url,
    exchange_info_url,
    months_between,
    refuse_credentials,
)
from aqt.data.manifest import AVAILABLE, UNAVAILABLE

ARCHIVE = b"PK\x03\x04 synthetic archive bytes, not market data"
NAME = "BTCUSDT-1h-2020-01.zip"
URL = archive_url("BTCUSDT", 2020, 1)
NOW = datetime(2026, 9, 26, 12, 0, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def _no_sockets(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_: object, **__: object) -> None:
        raise AssertionError("network access attempted in an offline test")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)


class FakeTransport:
    def __init__(self, responses: dict[str, list[FetchResponse]]) -> None:
        self.responses = responses
        self.requests: list[PublicRequest] = []

    def __call__(self, request: PublicRequest) -> FetchResponse:
        self.requests.append(request)
        queue = self.responses.get(request.url)
        if not queue:
            return FetchResponse(404, b"")
        return queue.pop(0) if len(queue) > 1 else queue[0]


def _checksum(data: bytes, name: str = NAME) -> bytes:
    return f"{hashlib.sha256(data).hexdigest()}  {name}\n".encode()


def _serving(archive: bytes = ARCHIVE, checksum: bytes | None = None) -> FakeTransport:
    return FakeTransport(
        {
            URL: [FetchResponse(200, archive)],
            URL + ".CHECKSUM": [FetchResponse(200, checksum or _checksum(archive))],
        }
    )


def _client(
    transport: FakeTransport, root: Path, **kwargs: object
) -> BinancePublicClient:
    return BinancePublicClient(
        transport, root, environ={}, clock=lambda: NOW, sleep=lambda _: None, **kwargs
    )


def test_fetch_stores_exact_bytes_with_independent_hash(tmp_path: Path) -> None:
    record = _client(_serving(), tmp_path).fetch_monthly_klines("BTCUSDT", 2020, 1)

    assert record.path is not None and record.path.read_bytes() == ARCHIVE
    assert record.availability.status == AVAILABLE
    assert record.availability.source_sha256 == hashlib.sha256(ARCHIVE).hexdigest()
    assert record.availability.as_of_utc == NOW
    sidecar = json.loads(record.path.with_name(NAME + ".source.json").read_bytes())
    assert sidecar["sha256"] == hashlib.sha256(ARCHIVE).hexdigest()
    assert sidecar["source_url"] == URL
    assert sidecar["byte_count"] == len(ARCHIVE)


def test_checksum_mismatch_raises_and_writes_nothing(tmp_path: Path) -> None:
    transport = _serving(checksum=_checksum(b"other bytes"))
    with pytest.raises(DownloadError, match="checksum mismatch"):
        _client(transport, tmp_path).fetch_monthly_klines("BTCUSDT", 2020, 1)
    assert [p for p in tmp_path.rglob("*") if p.is_file()] == []


def test_checksum_naming_another_file_is_rejected(tmp_path: Path) -> None:
    transport = _serving(checksum=_checksum(ARCHIVE, "ETHUSDT-1h-2020-01.zip"))
    with pytest.raises(DownloadError, match="does not describe"):
        _client(transport, tmp_path).fetch_monthly_klines("BTCUSDT", 2020, 1)


@pytest.mark.parametrize(
    ("url", "headers"),
    [
        (URL, (("X-MBX-APIKEY", "k"),)),
        (URL, (("Authorization", "Bearer k"),)),
        (URL + "?apiKey=k", ()),
        (URL + "?signature=abc&timestamp=1", ()),
        ("https://user:pw@data.binance.vision/x", ()),
        ("https://api.binance.com/api/v3/account", ()),
        ("http://data.binance.vision/x", ()),
    ],
)
def test_authenticated_or_unlisted_request_cannot_be_built(
    url: str, headers: tuple[tuple[str, str], ...]
) -> None:
    with pytest.raises(DownloadError):
        PublicRequest(url, headers)


def test_every_request_sent_is_unauthenticated(tmp_path: Path) -> None:
    transport = _serving()
    client = _client(transport, tmp_path)
    client.fetch_monthly_klines("BTCUSDT", 2020, 1)
    client.fetch_exchange_info()
    assert transport.requests and all(r.headers == () for r in transport.requests)


@pytest.mark.parametrize(
    "name", ["BINANCE_API_KEY", "BINANCE_API_SECRET", "BINANCE_SECRET_KEY"]
)
def test_client_refuses_to_start_with_credentials_in_environment(
    name: str, tmp_path: Path
) -> None:
    with pytest.raises(DownloadError, match=name):
        BinancePublicClient(_serving(), tmp_path, environ={name: "x"})
    refuse_credentials({"BINANCE_REGION": "global"})  # not a credential


def test_missing_archive_is_unavailable_not_filled(tmp_path: Path) -> None:
    record = _client(FakeTransport({}), tmp_path).fetch_monthly_klines(
        "ETHUSDT", 2017, 8
    )
    assert record.availability.status == UNAVAILABLE
    assert "404" in (record.availability.reason or "")
    assert record.path is None
    assert list(tmp_path.rglob("*")) == []


def test_rerun_is_a_no_op_and_never_rewrites(tmp_path: Path) -> None:
    first = _client(_serving(), tmp_path).fetch_monthly_klines("BTCUSDT", 2020, 1)
    assert first.path is not None
    stamp = first.path.stat().st_mtime_ns

    transport = _serving(archive=b"changed upstream")
    again = _client(transport, tmp_path).fetch_monthly_klines("BTCUSDT", 2020, 1)

    assert transport.requests == []
    assert again == first
    assert first.path.read_bytes() == ARCHIVE
    assert first.path.stat().st_mtime_ns == stamp


def test_tampered_artifact_is_refused(tmp_path: Path) -> None:
    first = _client(_serving(), tmp_path).fetch_monthly_klines("BTCUSDT", 2020, 1)
    assert first.path is not None
    first.path.write_bytes(b"edited")
    with pytest.raises(DownloadError, match="no longer match"):
        _client(_serving(), tmp_path).fetch_monthly_klines("BTCUSDT", 2020, 1)


def test_retries_are_bounded_on_server_errors(tmp_path: Path) -> None:
    transport = FakeTransport({URL: [FetchResponse(503, b"")]})
    with pytest.raises(DownloadError, match="after 3 attempts"):
        _client(transport, tmp_path).fetch_monthly_klines("BTCUSDT", 2020, 1)
    assert len(transport.requests) == 3


def test_transient_error_then_success(tmp_path: Path) -> None:
    transport = _serving()
    transport.responses[URL].insert(0, FetchResponse(502, b""))
    record = _client(transport, tmp_path).fetch_monthly_klines("BTCUSDT", 2020, 1)
    assert record.availability.status == AVAILABLE


@pytest.mark.parametrize("status", [418, 429, 403])
def test_rate_limit_stops_without_retry(status: int, tmp_path: Path) -> None:
    transport = FakeTransport({URL: [FetchResponse(status, b"")]})
    with pytest.raises(DownloadError, match="stopping"):
        _client(transport, tmp_path).fetch_monthly_klines("BTCUSDT", 2020, 1)
    assert len(transport.requests) == 1


def test_only_allowed_symbols() -> None:
    with pytest.raises(DownloadError):
        archive_url("SOLUSDT", 2020, 1)


def test_exchange_info_snapshot_is_recorded(tmp_path: Path) -> None:
    body = b'{"symbols":[]}'
    url = exchange_info_url(("BTCUSDT", "ETHUSDT"))
    transport = FakeTransport({url: [FetchResponse(200, body)]})
    record = _client(transport, tmp_path).fetch_exchange_info()
    assert record.path is not None and record.path.read_bytes() == body
    assert record.availability.as_of_utc == NOW
    assert record.name == "exchangeInfo-20260926T120000Z.json"


def test_exploration_months_cover_the_protocol_window() -> None:
    text = (Path(__file__).parents[2] / "protocols" / "protocol_v1.yaml").read_text(
        encoding="utf-8"
    )
    match = re.search(
        r'exploration: \{start: "(\d{4})-(\d{2})-\d{2}T[^"]*", '
        r'end: "(\d{4})-(\d{2})-\d{2}T',
        text,
    )
    assert match is not None
    y0, m0, y1, m1 = (int(g) for g in match.groups())
    assert EXPLORATION_MONTHS == ((y0, m0), (y1, m1))
    months = months_between(*EXPLORATION_MONTHS)
    assert months[0] == (2017, 8) and months[-1] == (2021, 12)
    assert len(months) == 53
