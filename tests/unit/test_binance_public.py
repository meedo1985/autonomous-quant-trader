"""Offline tests for the public Binance downloader. Sockets are blocked."""

from __future__ import annotations

import email.message
import functools
import hashlib
import http.client
import importlib.util
import io
import json
import re
import socket
import urllib.request
import urllib.response
from datetime import UTC, datetime
from pathlib import Path

import pytest

from aqt.data import binance_public
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
    urllib_transport,
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
    def __init__(self, responses: dict[str, list[FetchResponse | Exception]]) -> None:
        self.responses = responses
        self.requests: list[PublicRequest] = []

    def __call__(self, request: PublicRequest) -> FetchResponse:
        self.requests.append(request)
        queue = self.responses.get(request.url)
        if not queue:
            return FetchResponse(404, b"")
        item = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(item, Exception):
            raise item
        return item


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


@pytest.mark.parametrize("status", [301, 302, 403, 418, 429])
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


# --- Review repairs (review/task13/REVIEW.md) --------------------------------


@pytest.mark.parametrize(
    ("year", "month"), [(2017, 7), (2022, 1), (2025, 6), (2020, 0), (2020, 13)]
)
def test_months_outside_exploration_are_refused_before_disk_or_network(
    year: int, month: int, tmp_path: Path
) -> None:
    """R-2: the client, not only the CLI, confines downloads to exploration."""
    cached = (
        tmp_path / "klines" / "BTCUSDT" / "1h" / f"BTCUSDT-1h-{year}-{month:02d}.zip"
    )
    cached.parent.mkdir(parents=True)
    cached.write_bytes(b"planted")
    transport = _serving()
    with pytest.raises(DownloadError, match="outside the exploration months"):
        _client(transport, tmp_path).fetch_monthly_klines("BTCUSDT", year, month)
    assert transport.requests == []
    assert [p for p in tmp_path.rglob("*") if p.is_file()] == [cached]


def test_concurrent_writer_cannot_change_published_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R-1: a second writer arriving between link and cleanup is refused."""
    target = tmp_path / "artifact.zip"
    real_link = binance_public.os.link
    raced: list[BaseException] = []

    def link_then_race(src: str, dst: str) -> None:
        real_link(src, dst)
        if not raced:
            with pytest.raises(DownloadError) as caught:
                binance_public._write_once(target, b"second writer")
            raced.append(caught.value)

    monkeypatch.setattr(binance_public.os, "link", link_then_race)
    binance_public._write_once(target, ARCHIVE)

    assert raced and "refusing to overwrite" in str(raced[0])
    assert target.read_bytes() == ARCHIVE
    assert [p.name for p in tmp_path.iterdir()] == ["artifact.zip"]


class _RedirectingHTTPS(urllib.request.BaseHandler):
    handler_order = 100  # ahead of the default HTTPS handler

    def __init__(self, location: str) -> None:
        self.location = location
        self.opened: list[str] = []

    def https_open(self, req: urllib.request.Request) -> urllib.response.addinfourl:
        self.opened.append(req.full_url)
        headers = email.message.Message()
        headers["Location"] = self.location
        response = urllib.response.addinfourl(
            io.BytesIO(b""), headers, req.full_url, 302
        )
        response.msg = "Found"
        return response


@pytest.mark.parametrize(
    "location",
    [
        "http://data.binance.vision/x.zip",
        "https://evil.example/x.zip",
        "https://data.binance.vision/x.zip?apiKey=k",
    ],
)
def test_real_transport_refuses_redirects(
    location: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R-3: a redirect target is never requested; the 3xx surfaces as-is."""
    server = _RedirectingHTTPS(location)
    opener = urllib.request.build_opener(binance_public._RefuseRedirects, server)
    monkeypatch.setattr(binance_public, "_OPENER", opener)

    response = urllib_transport(PublicRequest(URL))

    assert response.status == 302
    assert server.opened == [URL]


def test_module_opener_uses_the_redirect_refusing_handler() -> None:
    handlers = binance_public._OPENER.handlers
    redirect = [
        h for h in handlers if isinstance(h, urllib.request.HTTPRedirectHandler)
    ]
    assert [type(h) for h in redirect] == [binance_public._RefuseRedirects]


def _load_cli() -> object:
    path = Path(__file__).parents[2] / "scripts" / "download_market_data.py"
    spec = importlib.util.spec_from_file_location("download_market_data", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_writes_a_summary_when_a_run_stops(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R-5: a failure after a successful archive still leaves a run record."""
    first = archive_url("BTCUSDT", 2017, 8)
    second = archive_url("BTCUSDT", 2017, 9)
    info = exchange_info_url(("BTCUSDT", "ETHUSDT"))
    first_name = first.rsplit("/", 1)[1]
    transport = FakeTransport(
        {
            info: [FetchResponse(200, b"{}")],
            first: [FetchResponse(200, ARCHIVE)],
            first + ".CHECKSUM": [FetchResponse(200, _checksum(ARCHIVE, first_name))],
            second: [FetchResponse(200, ARCHIVE)],
            second + ".CHECKSUM": [FetchResponse(200, _checksum(b"x", "wrong.zip"))],
        }
    )
    for name in [
        n for n in __import__("os").environ if n.upper().startswith("BINANCE")
    ]:
        monkeypatch.delenv(name)
    cli = _load_cli()
    monkeypatch.setattr(cli, "urllib_transport", transport)

    code = cli.main(["--root", str(tmp_path), "--symbol", "BTCUSDT"])  # type: ignore[attr-defined]

    assert code == 2
    [summary_path] = (tmp_path / "runs").iterdir()
    summary = json.loads(summary_path.read_bytes())
    assert summary["failure"]["operation"] == "BTCUSDT 2017-09"
    assert [r["name"] for r in summary["records"]][1:] == [first_name]
    assert len(transport.requests) == 5


# --- Second-review repairs (review/task13/REVIEW_2.md, R2-1) ------------------


def test_interrupted_response_is_retried(tmp_path: Path) -> None:
    transport = _serving()
    transport.responses[URL].insert(0, http.client.IncompleteRead(b"PK"))
    record = _client(transport, tmp_path).fetch_monthly_klines("BTCUSDT", 2020, 1)
    assert record.path is not None and record.path.read_bytes() == ARCHIVE


def test_persistent_interrupted_response_is_a_download_error(tmp_path: Path) -> None:
    transport = FakeTransport({URL: [http.client.IncompleteRead(b"PK")]})
    with pytest.raises(DownloadError, match="IncompleteRead"):
        _client(transport, tmp_path).fetch_monthly_klines("BTCUSDT", 2020, 1)
    assert len(transport.requests) == 3
    assert [p for p in tmp_path.rglob("*") if p.is_file()] == []


def _valid_sidecar() -> dict[str, object]:
    return {
        "name": NAME,
        "source_url": URL,
        "sha256": hashlib.sha256(ARCHIVE).hexdigest(),
        "as_of_utc": "2026-09-26T12:00:00Z",
    }


@pytest.mark.parametrize(
    "content",
    [
        b"not json",
        bytes([0xFF, 0xFE]),
        b"[]",
        json.dumps({**_valid_sidecar(), "as_of_utc": None}).encode(),
        json.dumps({**_valid_sidecar(), "as_of_utc": "yesterday"}).encode(),
        json.dumps(
            {k: v for k, v in _valid_sidecar().items() if k != "as_of_utc"}
        ).encode(),
    ],
)
def test_malformed_sidecar_is_a_download_error(content: bytes, tmp_path: Path) -> None:
    first = _client(_serving(), tmp_path).fetch_monthly_klines("BTCUSDT", 2020, 1)
    assert first.path is not None
    first.path.with_name(NAME + ".source.json").write_bytes(content)
    transport = _serving()
    with pytest.raises(DownloadError, match="unreadable sidecar"):
        _client(transport, tmp_path).fetch_monthly_klines("BTCUSDT", 2020, 1)
    assert transport.requests == []
    assert first.path.read_bytes() == ARCHIVE


def _quiet_cli(monkeypatch: pytest.MonkeyPatch, transport: FakeTransport) -> object:
    import os

    for name in [n for n in os.environ if n.upper().startswith("BINANCE")]:
        monkeypatch.delenv(name)
    cli = _load_cli()
    monkeypatch.setattr(cli, "urllib_transport", transport)
    quiet = functools.partial(BinancePublicClient, sleep=lambda _: None)
    monkeypatch.setattr(cli, "BinancePublicClient", quiet)
    return cli


def _only_summary(root: Path) -> dict[str, object]:
    [path] = (root / "runs").iterdir()
    summary = json.loads(path.read_bytes())
    assert isinstance(summary, dict)
    return summary


def test_cli_records_a_refusal_to_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transport = FakeTransport({})
    cli = _quiet_cli(monkeypatch, transport)
    monkeypatch.setenv("BINANCE_API_KEY", "x")

    code = cli.main(["--root", str(tmp_path)])  # type: ignore[attr-defined]

    assert code == 2
    summary = _only_summary(tmp_path)
    assert summary["failure"] == {
        "error": summary["failure"]["error"],  # type: ignore[index]
        "operation": "start",
    }
    assert "BINANCE_API_KEY" in summary["failure"]["error"]  # type: ignore[index]
    assert summary["records"] == []
    assert transport.requests == []


def test_cli_records_an_interrupted_response_after_a_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = archive_url("BTCUSDT", 2017, 8)
    second = archive_url("BTCUSDT", 2017, 9)
    first_name = first.rsplit("/", 1)[1]
    transport = FakeTransport(
        {
            exchange_info_url(("BTCUSDT", "ETHUSDT")): [FetchResponse(200, b"{}")],
            first: [FetchResponse(200, ARCHIVE)],
            first + ".CHECKSUM": [FetchResponse(200, _checksum(ARCHIVE, first_name))],
            second: [http.client.IncompleteRead(b"PK")],
        }
    )
    cli = _quiet_cli(monkeypatch, transport)

    code = cli.main(["--root", str(tmp_path), "--symbol", "BTCUSDT"])  # type: ignore[attr-defined]

    assert code == 2
    summary = _only_summary(tmp_path)
    assert summary["failure"]["operation"] == "BTCUSDT 2017-09"  # type: ignore[index]
    assert "IncompleteRead" in summary["failure"]["error"]  # type: ignore[index]
    names = [r["name"] for r in summary["records"]]  # type: ignore[attr-defined]
    assert names[1:] == [first_name]
    # exchangeInfo, archive, CHECKSUM, then three bounded attempts; no more.
    assert [r.url for r in transport.requests] == [
        exchange_info_url(("BTCUSDT", "ETHUSDT")),
        first,
        first + ".CHECKSUM",
        second,
        second,
        second,
    ]


# --- Third-review repairs (review/task13/REVIEW_3.md, R3-1) -------------------


class _BrokenStream(io.StringIO):
    def write(self, _: str) -> int:
        raise BrokenPipeError("console closed")


def _one_month_transport(second: FetchResponse | Exception) -> FakeTransport:
    first = archive_url("BTCUSDT", 2017, 8)
    first_name = first.rsplit("/", 1)[1]
    return FakeTransport(
        {
            exchange_info_url(("BTCUSDT", "ETHUSDT")): [FetchResponse(200, b"{}")],
            first: [FetchResponse(200, ARCHIVE)],
            first + ".CHECKSUM": [FetchResponse(200, _checksum(ARCHIVE, first_name))],
            archive_url("BTCUSDT", 2017, 9): [second],
        }
    )


def test_cli_broken_console_does_not_change_the_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failing stdout neither drops stored records nor stops the run."""
    transport = _one_month_transport(FetchResponse(404, b""))
    cli = _quiet_cli(monkeypatch, transport)
    monkeypatch.setattr("sys.stdout", _BrokenStream())

    code = cli.main(["--root", str(tmp_path), "--symbol", "BTCUSDT"])  # type: ignore[attr-defined]

    summary = _only_summary(tmp_path)
    assert summary["failure"] is None
    records = summary["records"]
    assert isinstance(records, list)
    assert len(records) == 1 + 53  # exchangeInfo plus every exploration month
    assert records[1]["availability"]["status"] == AVAILABLE
    assert code == 1  # months after the first are unavailable in this fake


def test_cli_broken_console_during_failure_still_writes_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transport = _one_month_transport(http.client.IncompleteRead(b"PK"))
    cli = _quiet_cli(monkeypatch, transport)
    monkeypatch.setattr("sys.stdout", _BrokenStream())
    monkeypatch.setattr("sys.stderr", _BrokenStream())

    code = cli.main(["--root", str(tmp_path), "--symbol", "BTCUSDT"])  # type: ignore[attr-defined]

    assert code == 2
    summary = _only_summary(tmp_path)
    assert summary["failure"]["operation"] == "BTCUSDT 2017-09"  # type: ignore[index]
    assert len(summary["records"]) == 2  # type: ignore[arg-type]


def test_cli_records_a_filesystem_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transport = _one_month_transport(FetchResponse(404, b""))
    cli = _quiet_cli(monkeypatch, transport)

    def denied(path: Path, content: bytes) -> None:
        raise PermissionError(f"denied: {path}")

    monkeypatch.setattr(binance_public, "_write_once", denied)

    code = cli.main(["--root", str(tmp_path), "--symbol", "BTCUSDT"])  # type: ignore[attr-defined]

    assert code == 2
    summary = _only_summary(tmp_path)
    assert summary["failure"]["operation"] == "exchangeInfo"  # type: ignore[index]
    assert "PermissionError" in summary["failure"]["error"]  # type: ignore[index]
    assert summary["records"] == []
    assert len(transport.requests) == 1


def test_cli_summary_write_failure_propagates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transport = _one_month_transport(FetchResponse(404, b""))
    cli = _quiet_cli(monkeypatch, transport)
    (tmp_path / "runs").write_bytes(b"a file where the runs directory belongs")

    with pytest.raises(OSError):
        cli.main(["--root", str(tmp_path), "--symbol", "BTCUSDT"])  # type: ignore[attr-defined]
