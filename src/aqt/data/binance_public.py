"""Credential-free download of Binance Spot public 1h kline archives.

Roadmap Task 13 (`review/roadmap/ROADMAP_PROPOSAL.md`). This module downloads
bytes and verifies them; it parses nothing and interprets nothing. Parsing into
`BarSeries` is Task 14 and goes through `aqt.data.bars`.

Constitution obligations
------------------------
- Section 6: raw is immutable. Every artifact is written once and never
  overwritten; a re-run over an existing artifact re-verifies it and changes
  nothing. A missing archive is returned as `UNAVAILABLE` with a reason, never
  skipped or filled.
- Section 28 and Milestone 0.1: no credentials. The client refuses to start
  while any Binance key or secret variable is set, and a request that carries
  an authentication header, a signature, or an `apiKey` parameter cannot be
  constructed.
- Section 2: Binance Spot, BTCUSDT and ETHUSDT, 1h bars only.
- Section 15: Cycle-1 research network access is denied. The AI writes this
  code; the owner runs `scripts/download_market_data.py`. Tests use a fake
  transport with sockets blocked.

Sources are `data.binance.vision` (published archives with `.CHECKSUM` files)
and `data-api.binance.vision`, Binance's public market-data-only host.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final
from urllib.parse import parse_qsl, quote, urlsplit

from aqt.data.manifest import (
    AvailabilityRecord,
    available,
    canonical_json_bytes,
    unavailable,
)

__all__ = [
    "ALLOWED_HOSTS",
    "ALLOWED_SYMBOLS",
    "EXPLORATION_MONTHS",
    "BinancePublicClient",
    "DownloadError",
    "DownloadRecord",
    "FetchResponse",
    "PublicRequest",
    "Transport",
    "archive_url",
    "exchange_info_url",
    "months_between",
    "refuse_credentials",
    "urllib_transport",
]

ALLOWED_SYMBOLS: Final[tuple[str, str]] = ("BTCUSDT", "ETHUSDT")
INTERVAL: Final[str] = "1h"
ALLOWED_HOSTS: Final[frozenset[str]] = frozenset(
    {"data.binance.vision", "data-api.binance.vision"}
)
_ARCHIVE_BASE: Final[str] = "https://data.binance.vision/data/spot/monthly/klines"
_EXCHANGE_INFO: Final[str] = "https://data-api.binance.vision/api/v3/exchangeInfo"

EXPLORATION_MONTHS: Final[tuple[tuple[int, int], tuple[int, int]]] = (
    (2017, 8),
    (2021, 12),
)
"""Inclusive month span covering `protocols/protocol_v1.yaml`
`partitions.exploration` (2017-08-17 to 2021-12-31). Whole months are fetched;
trimming to the window is Task 14's job."""

_FORBIDDEN_HEADERS: Final[frozenset[str]] = frozenset(
    {"authorization", "x-mbx-apikey", "cookie"}
)
_FORBIDDEN_PARAMS: Final[frozenset[str]] = frozenset(
    {"apikey", "signature", "timestamp", "recvwindow"}
)
_HEX64: Final[str] = "0123456789abcdef"


class DownloadError(RuntimeError):
    """Raised when a download cannot be completed safely."""


def refuse_credentials(environ: Mapping[str, str]) -> None:
    """Fail closed if any Binance key or secret variable is present."""
    found = sorted(
        name
        for name in environ
        if name.upper().startswith("BINANCE")
        and ("KEY" in name.upper() or "SECRET" in name.upper())
    )
    if found:
        raise DownloadError(
            f"refusing to start: credential variables are set ({', '.join(found)});"
            " this client uses public endpoints only and must never see a key"
        )


@dataclass(frozen=True, slots=True)
class PublicRequest:
    """An unauthenticated HTTPS GET to an allow-listed public host."""

    url: str
    headers: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        parts = urlsplit(self.url)
        if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS:
            raise DownloadError(f"not an allow-listed public HTTPS URL: {self.url}")
        if parts.username or parts.password:
            raise DownloadError("a public request must not carry URL credentials")
        for key, _ in parse_qsl(parts.query, keep_blank_values=True):
            if key.lower() in _FORBIDDEN_PARAMS:
                raise DownloadError(f"a public request must not carry {key!r}")
        for name, _ in self.headers:
            if name.lower() in _FORBIDDEN_HEADERS:
                raise DownloadError(f"a public request must not carry header {name!r}")


@dataclass(frozen=True, slots=True)
class FetchResponse:
    status: int
    body: bytes


Transport = Callable[[PublicRequest], FetchResponse]


def urllib_transport(request: PublicRequest, *, timeout: float = 60.0) -> FetchResponse:
    """The real network transport. Only the owner-run CLI uses it."""
    req = urllib.request.Request(request.url, headers=dict(request.headers))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return FetchResponse(status=response.status, body=response.read())
    except urllib.error.HTTPError as error:
        return FetchResponse(status=error.code, body=b"")


def archive_url(symbol: str, year: int, month: int) -> str:
    _require_symbol(symbol)
    name = f"{symbol}-{INTERVAL}-{year:04d}-{month:02d}.zip"
    return f"{_ARCHIVE_BASE}/{symbol}/{INTERVAL}/{name}"


def exchange_info_url(symbols: tuple[str, ...]) -> str:
    for symbol in symbols:
        _require_symbol(symbol)
    listed = ",".join(f'"{symbol}"' for symbol in symbols)
    return f"{_EXCHANGE_INFO}?symbols={quote(f'[{listed}]', safe=',')}"


def months_between(
    first: tuple[int, int], last: tuple[int, int]
) -> list[tuple[int, int]]:
    """Inclusive list of `(year, month)` from `first` to `last`."""
    year, month = first
    months: list[tuple[int, int]] = []
    while (year, month) <= last:
        months.append((year, month))
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return months


def _require_symbol(symbol: str) -> None:
    if symbol not in ALLOWED_SYMBOLS:
        raise DownloadError(f"symbol must be one of {ALLOWED_SYMBOLS}, got {symbol!r}")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _iso(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True, slots=True)
class DownloadRecord:
    """The outcome for one requested artifact: stored bytes or a reason."""

    name: str
    source_url: str
    availability: AvailabilityRecord
    path: Path | None = None

    def as_mapping(self) -> dict[str, object]:
        return {
            "availability": self.availability.as_mapping(),
            "name": self.name,
            "path": None if self.path is None else self.path.as_posix(),
            "source_url": self.source_url,
        }


class BinancePublicClient:
    """Write-once downloader over an injected transport."""

    def __init__(
        self,
        transport: Transport,
        root: Path,
        *,
        environ: Mapping[str, str] | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        attempts: int = 3,
        backoff_seconds: float = 5.0,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        refuse_credentials(os.environ if environ is None else environ)
        if attempts < 1:
            raise ValueError("attempts must be at least 1")
        self._transport = transport
        self._root = root
        self._clock = clock
        self._attempts = attempts
        self._backoff = backoff_seconds
        self._sleep = sleep

    def fetch_monthly_klines(
        self, symbol: str, year: int, month: int
    ) -> DownloadRecord:
        url = archive_url(symbol, year, month)
        name = url.rsplit("/", 1)[1]
        path = self._root / "klines" / symbol / INTERVAL / name
        existing = self._existing(name, url, path)
        if existing is not None:
            return existing

        archive = self._get(url)
        if archive is None:
            return DownloadRecord(name, url, unavailable(f"HTTP 404 for {url}"))
        checksum = self._get(url + ".CHECKSUM")
        if checksum is None:
            raise DownloadError(f"archive exists but its CHECKSUM is missing: {url}")
        published = _parse_checksum(checksum, name)
        if _sha256(archive) != published:
            raise DownloadError(
                f"checksum mismatch for {name}: published {published}, "
                f"computed {_sha256(archive)}; nothing written"
            )
        extra = {
            "checksum_sha256": _sha256(checksum),
            "checksum_url": url + ".CHECKSUM",
        }
        return self._store(name, url, path, archive, extra)

    def fetch_exchange_info(
        self, symbols: tuple[str, ...] = ALLOWED_SYMBOLS
    ) -> DownloadRecord:
        """One point-in-time filter and status snapshot; no checksum is published."""
        url = exchange_info_url(symbols)
        as_of = self._clock()
        name = f"exchangeInfo-{as_of.astimezone(UTC):%Y%m%dT%H%M%SZ}.json"
        path = self._root / "exchange_info" / name
        existing = self._existing(name, url, path)
        if existing is not None:
            return existing
        body = self._get(url)
        if body is None:
            return DownloadRecord(name, url, unavailable(f"HTTP 404 for {url}"))
        return self._store(name, url, path, body, {}, as_of=as_of)

    def _get(self, url: str) -> bytes | None:
        """Bounded retries on transport faults and 5xx; 404 means absent."""
        request = PublicRequest(url)
        failure = ""
        for attempt in range(self._attempts):
            if attempt:
                self._sleep(self._backoff)
            try:
                response = self._transport(request)
            except OSError as error:
                failure = f"transport error: {error}"
                continue
            if response.status == 200:
                return response.body
            if response.status == 404:
                return None
            if response.status >= 500:
                failure = f"HTTP {response.status}"
                continue
            # 418/429 are rate-limit signals: stop rather than evade them.
            raise DownloadError(f"HTTP {response.status} for {url}; stopping")
        raise DownloadError(
            f"gave up on {url} after {self._attempts} attempts: {failure}"
        )

    def _store(
        self,
        name: str,
        url: str,
        path: Path,
        content: bytes,
        extra: Mapping[str, object],
        *,
        as_of: datetime | None = None,
    ) -> DownloadRecord:
        moment = (as_of or self._clock()).replace(microsecond=0)
        digest = _sha256(content)
        sidecar = {
            "as_of_utc": _iso(moment),
            "byte_count": len(content),
            "name": name,
            "sha256": digest,
            "source_url": url,
            **extra,
        }
        _write_once(path, content)
        _write_once(_sidecar(path), canonical_json_bytes(sidecar))
        return DownloadRecord(name, url, available(digest, moment), path)

    def _existing(self, name: str, url: str, path: Path) -> DownloadRecord | None:
        """Re-verify an artifact already on disk; never rewrite it."""
        if not path.exists():
            if _sidecar(path).exists():
                raise DownloadError(f"sidecar without artifact: {_sidecar(path)}")
            return None
        try:
            sidecar = json.loads(_sidecar(path).read_bytes())
        except FileNotFoundError:
            raise DownloadError(f"artifact without sidecar: {path}") from None
        if sidecar.get("source_url") != url or sidecar.get("name") != name:
            raise DownloadError(f"sidecar does not describe {url}: {_sidecar(path)}")
        if _sha256(path.read_bytes()) != sidecar.get("sha256"):
            raise DownloadError(f"stored bytes no longer match their sidecar: {path}")
        as_of = datetime.strptime(sidecar["as_of_utc"], "%Y-%m-%dT%H:%M:%SZ")
        return DownloadRecord(
            name, url, available(sidecar["sha256"], as_of.replace(tzinfo=UTC)), path
        )


def _sidecar(path: Path) -> Path:
    return path.with_name(path.name + ".source.json")


def _parse_checksum(checksum: bytes, name: str) -> str:
    """Parse a `sha256sum`-format line naming exactly `name`."""
    try:
        digest, listed = checksum.decode("ascii").split()
    except ValueError:
        raise DownloadError(f"malformed CHECKSUM for {name}: {checksum!r}") from None
    if listed.lstrip("*") != name or len(digest) != 64 or set(digest) - set(_HEX64):
        raise DownloadError(f"CHECKSUM does not describe {name}: {checksum!r}")
    return digest


def _write_once(path: Path, content: bytes) -> None:
    """Create `path` with `content`; fail if it already exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".part")
    partial.write_bytes(content)
    try:
        os.link(partial, path)  # fails if `path` exists, on every platform
    except FileExistsError:
        raise DownloadError(
            f"refusing to overwrite existing artifact: {path}"
        ) from None
    finally:
        partial.unlink()
