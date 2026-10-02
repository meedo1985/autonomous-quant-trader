"""CRITICAL alerts to the owner's private Telegram bot, and its weekly test
(roadmap 2 Task 28; owner settings D-1, D-2, D-8; answers Q-B, Q28-1, Q28-2).

- `TelegramSink` sends each CRITICAL event as one message. A failed send is
  never raised into the loop: it is written, as a CRITICAL `ALERT_CHANNEL`
  event, to the local sinks.
- The bot token and chat id come from the OS credential store (D-8), one
  entry `aqt-telegram`: user name the chat id, password the token. They are
  never in the repository, a configuration file, a log, a report or a test
  (section 28). Every error text here is built from the exception type and
  the HTTP status, never from the exception's message, so the URL, which
  holds the token, cannot reach a log.
- `ChannelTests` keeps the weekly test in a hash-chained ledger: a sent test
  is recorded by the SHA-256 of its one-time code, the owner acknowledges by
  typing the code (Q28-1), and the start is refused when the newest
  acknowledged test was sent more than 7 days ago (D-2). The app never reads
  messages from Telegram.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Final
from urllib.parse import urlsplit

from aqt.core.ledger import append_entry, read_entries, verify_ledger
from aqt.data.bars import require_utc
from aqt.monitoring.alerts import REDACTED, Sink
from aqt.monitoring.events import Event, EventKind, Severity

__all__ = [
    "CREDENTIAL_TARGET",
    "TEST_INTERVAL",
    "ChannelError",
    "ChannelTests",
    "DEFAULT_LEDGER",
    "TelegramCredential",
    "TelegramRequest",
    "TelegramResponse",
    "TelegramSink",
    "owner_channel",
    "read_windows_credential",
    "urllib_transport",
]

TELEGRAM_HOST: Final[str] = "api.telegram.org"
CREDENTIAL_TARGET: Final[str] = "aqt-telegram"
DEFAULT_LEDGER: Final[Path] = Path("data/processed/alerts/channel_tests.jsonl")
TEST_INTERVAL: Final[timedelta] = timedelta(days=7)  # OWNER-SET D-2
SENT: Final[str] = "aqt.channel_test.sent.v1"
ACKNOWLEDGED: Final[str] = "aqt.channel_test.acknowledged.v1"
_MAX_TEXT: Final[int] = 4000  # Telegram's limit is 4096 characters


class ChannelError(RuntimeError):
    """The alert channel cannot do what was asked; the text holds no secret."""


@dataclass(frozen=True, slots=True)
class TelegramCredential:
    chat_id: str
    token: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class TelegramRequest:
    """A POST to the Telegram Bot API, and nowhere else."""

    url: str = field(repr=False)
    body: bytes

    def __post_init__(self) -> None:
        parts = urlsplit(self.url)
        if parts.scheme != "https" or parts.hostname != TELEGRAM_HOST:
            raise ChannelError("not a Telegram Bot API HTTPS URL")


@dataclass(frozen=True, slots=True)
class TelegramResponse:
    status: int
    body: bytes


Transport = Callable[[TelegramRequest], TelegramResponse]


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_: object, **__: object) -> None:
        return None


_OPENER: Final = urllib.request.build_opener(_RefuseRedirects)


def urllib_transport(
    request: TelegramRequest, *, timeout: float = 10.0
) -> TelegramResponse:
    """The real network transport. Only the owner-run app uses it."""
    req = urllib.request.Request(
        request.url,
        data=request.body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with _OPENER.open(req, timeout=timeout) as response:
            return TelegramResponse(status=response.status, body=response.read())
    except urllib.error.HTTPError as error:
        return TelegramResponse(status=error.code, body=error.read())


def read_windows_credential(target: str = CREDENTIAL_TARGET) -> TelegramCredential:
    """Read the generic credential `target` from Windows Credential Manager."""
    if sys.platform != "win32":
        raise ChannelError("the credential store is read on Windows only (D-8)")
    import ctypes
    from ctypes import wintypes

    class _Credential(ctypes.Structure):
        _fields_ = [  # noqa: RUF012 - the ctypes layout of CREDENTIALW
            ("Flags", wintypes.DWORD),
            ("Type", wintypes.DWORD),
            ("TargetName", wintypes.LPWSTR),
            ("Comment", wintypes.LPWSTR),
            ("LastWritten", wintypes.FILETIME),
            ("CredentialBlobSize", wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
            ("Persist", wintypes.DWORD),
            ("AttributeCount", wintypes.DWORD),
            ("Attributes", ctypes.c_void_p),
            ("TargetAlias", wintypes.LPWSTR),
            ("UserName", wintypes.LPWSTR),
        ]

    advapi = ctypes.WinDLL("advapi32", use_last_error=True)
    found = ctypes.POINTER(_Credential)()
    if not advapi.CredReadW(target, 1, 0, ctypes.byref(found)):  # 1: generic
        raise ChannelError(f"no credential {target!r} in the credential store")
    try:
        entry = found.contents
        blob = ctypes.string_at(entry.CredentialBlob, entry.CredentialBlobSize)
        token = blob.decode("utf-16-le") if b"\x00" in blob else blob.decode()
        chat_id = entry.UserName or ""
    finally:
        advapi.CredFree(found)
    if not chat_id or not token:
        raise ChannelError(f"credential {target!r} lacks a chat id or a token")
    return TelegramCredential(chat_id=chat_id, token=token)


def _text(event: Event) -> str:
    lines = [f"{event.severity} {event.kind} at {event.at:%Y-%m-%d %H:%M:%S}Z"]
    lines += [f"{name}: {value}" for name, value in event.fields.items()]
    return "\n".join(lines)[:_MAX_TEXT]


class TelegramSink:
    """Send each CRITICAL event to the owner's chat; report failures locally."""

    min_severity = Severity.CRITICAL

    def __init__(
        self,
        credential: TelegramCredential,
        transport: Transport,
        local: Sequence[Sink],
    ) -> None:
        if not local:
            raise ChannelError("a failed send needs a local sink to be reported on")
        self._credential = credential
        self._transport = transport
        self._local = tuple(local)

    def send(self, text: str) -> str | None:
        """Send `text`; return why it failed, or None. Never raises."""
        url = f"https://{TELEGRAM_HOST}/bot{self._credential.token}/sendMessage"
        body = json.dumps({"chat_id": self._credential.chat_id, "text": text})
        try:
            response = self._transport(TelegramRequest(url, body.encode()))
        except Exception as error:  # noqa: BLE001 - reported, never raised
            return f"send failed: {type(error).__name__}"
        try:
            reply = json.loads(response.body)
            ok = isinstance(reply, dict) and reply.get("ok") is True
        except ValueError:
            reply, ok = None, False
        if response.status == 200 and ok:
            return None
        why = f"HTTP {response.status}"
        if isinstance(reply, dict) and isinstance(reply.get("description"), str):
            description = reply["description"][:200]
            why += ": " + description.replace(self._credential.token, REDACTED)
        return why

    def write(self, event: Event) -> None:
        why = self.send(_text(event))
        if why is None:
            return
        failure = Event(
            EventKind.ALERT_CHANNEL,
            Severity.CRITICAL,
            event.at,
            {"channel": "telegram", "failed_kind": str(event.kind), "error": why},
        )
        for sink in self._local:
            sink.write(failure)


def _digest(code: str) -> str:
    return hashlib.sha256(code.strip().encode()).hexdigest()


class ChannelTests:
    """The weekly test of the Telegram channel (D-2), kept in a ledger."""

    def __init__(
        self, path: Path, sink: TelegramSink, clock: Callable[[], datetime]
    ) -> None:
        self.path = path
        self._sink = sink
        self._clock = clock

    def now(self) -> datetime:
        """The wall clock, checked to be UTC."""
        return require_utc(self._clock(), field_name="clock")

    def _entries(self) -> list[tuple[str, dict[str, object]]]:
        if not self.path.exists():
            return []
        verify_ledger(self.path).require_intact()
        return [(e.record_type, e.payload) for e in read_entries(self.path)]

    def _sent_times(self, record_type: str) -> list[datetime]:
        return [
            datetime.fromisoformat(str(payload["sent_at"]))
            for kind, payload in self._entries()
            if kind == record_type
        ]

    def send_test(self) -> None:
        """Send a test carrying a fresh code; record it once it was sent."""
        now = self.now()
        code = f"{secrets.randbelow(10**6):06d}"
        why = self._sink.send(
            f"aqt alert channel test, sent {now:%Y-%m-%d %H:%M}Z.\n"
            f"Confirm on the app's computer:\n"
            f"python scripts/alert_channel.py ack {code}"
        )
        if why is not None:
            raise ChannelError(f"test not sent: {why}")
        append_entry(
            self.path,
            record_type=SENT,
            payload={"code_sha256": _digest(code), "sent_at": now.isoformat()},
            recorded_at_utc=now,
        )

    def acknowledge(self, code: str) -> datetime:
        """Record the owner's code; return when its test was sent."""
        now = self.now()
        entries = self._entries()
        done = {p["code_sha256"] for k, p in entries if k == ACKNOWLEDGED}
        digest = _digest(code)
        for kind, payload in reversed(entries):
            if kind == SENT and payload["code_sha256"] == digest:
                if digest in done:
                    raise ChannelError("that test is already acknowledged")
                append_entry(
                    self.path,
                    record_type=ACKNOWLEDGED,
                    payload={"code_sha256": digest, "sent_at": payload["sent_at"]},
                    recorded_at_utc=now,
                )
                return datetime.fromisoformat(str(payload["sent_at"]))
        raise ChannelError("no test was sent with that code")

    def problem(self) -> str | None:
        """Why the start must be refused, or None."""
        try:
            acknowledged = self._sent_times(ACKNOWLEDGED)
        except Exception as error:  # noqa: BLE001 - a damaged ledger refuses
            return f"channel test ledger unreadable: {type(error).__name__}"
        if not acknowledged:
            return "no acknowledged alert channel test (D-2)"
        newest = max(acknowledged)
        if self.now() - newest > TEST_INTERVAL:
            return f"alert channel test overdue: last acknowledged test sent {newest}"
        return None

    def due(self) -> bool:
        """A new test is due: none was sent in the last 7 days."""
        sent = self._sent_times(SENT)
        return not sent or self.now() - max(sent) > TEST_INTERVAL


def owner_channel(
    ledger: Path, local: Sequence[Sink]
) -> tuple[TelegramSink, ChannelTests]:
    """The owner's real channel: the stored credential, the network and the
    wall clock. Used by the owner-run scripts only, never by tests."""
    sink = TelegramSink(read_windows_credential(), urllib_transport, local)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    return sink, ChannelTests(ledger, sink, lambda: datetime.now(UTC))
