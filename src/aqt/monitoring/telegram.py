"""CRITICAL alerts to the owner's private Telegram bot, and its weekly test
(roadmap 2 Task 28; owner settings D-1, D-2, D-8; answers Q-B, Q28-1, Q28-2).

- `TelegramSink` sends each CRITICAL event as one message. A failed send is
  never raised into the loop: it is written, as a CRITICAL `ALERT_CHANNEL`
  event, to the local sinks.
- The bot token and chat id come from the OS credential store (D-8): on
  Windows one entry `aqt-telegram`, user name the chat id, password the
  token; on the Ubuntu server (Task 30) the file `/etc/aqt/telegram`, chat id
  then token on two lines, readable only by the app's account. They are
  never in the repository, a configuration file, a log, a report or a test
  (section 28). Every error text here is built from the exception type and
  the HTTP status only, never from an exception's message or Telegram's
  reply, so the URL, which holds the token, cannot reach a log (A28-1).
- `ChannelTests` keeps the weekly test in a hash-chained ledger: a sent test
  is recorded by the SHA-256 of its one-time code and the fingerprint of the
  bot and chat it went to, the owner acknowledges by typing the code
  (Q28-1), and the start is refused when the newest acknowledged test on
  this bot and chat was sent more than 7 days ago (D-2). The app never reads
  messages from Telegram.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Final
from urllib.parse import urlsplit

from aqt.core.ledger import append_entry, read_entries, verify_ledger
from aqt.data.bars import require_utc
from aqt.monitoring.alerts import Sink
from aqt.monitoring.events import Event, EventKind, Severity

__all__ = [
    "CREDENTIAL_FILE",
    "CREDENTIAL_TARGET",
    "DEFAULT_LEDGER",
    "TEST_INTERVAL",
    "ChannelError",
    "ChannelTests",
    "TelegramCredential",
    "TelegramRequest",
    "TelegramResponse",
    "TelegramSink",
    "owner_channel",
    "read_credential",
    "read_file_credential",
    "read_windows_credential",
    "urllib_transport",
]

TELEGRAM_HOST: Final[str] = "api.telegram.org"
CREDENTIAL_TARGET: Final[str] = "aqt-telegram"
CREDENTIAL_FILE: Final[Path] = Path("/etc/aqt/telegram")
DEFAULT_LEDGER: Final[Path] = Path("data/processed/alerts/channel_tests.jsonl")
TEST_INTERVAL: Final[timedelta] = timedelta(days=7)  # OWNER-SET D-2
SENT: Final[str] = "aqt.channel_test.sent.v1"
ACKNOWLEDGED: Final[str] = "aqt.channel_test.acknowledged.v1"
_MAX_TEXT: Final[int] = 4000  # Telegram's limit is 4096 characters
_MAX_REPLY: Final[int] = 65536  # a longer reply is refused, never parsed


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
    """The real network transport. Only the owner-run app uses it. `timeout`
    bounds each blocking socket operation, not the whole call (T28-04). One
    byte past the bound is read, so a cut reply is told from a whole one
    (A28-12)."""
    req = urllib.request.Request(
        request.url,
        data=request.body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with _OPENER.open(req, timeout=timeout) as response:
            return TelegramResponse(response.status, response.read(_MAX_REPLY + 1))
    except urllib.error.HTTPError as error:
        return TelegramResponse(error.code, error.read(_MAX_REPLY + 1))


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
    token: str | None = None
    try:
        entry = found.contents
        blob = ctypes.string_at(entry.CredentialBlob, entry.CredentialBlobSize)
        try:
            token = blob.decode("utf-16-le") if b"\x00" in blob else blob.decode()
        except UnicodeDecodeError:
            pass  # refused below, outside this handler: no context kept (A28-9)
        chat_id = entry.UserName or ""
    finally:
        advapi.CredFree(found)
    if token is None:
        raise ChannelError(f"credential {target!r} is not readable text")
    if not chat_id or not token:
        raise ChannelError(f"credential {target!r} lacks a chat id or a token")
    return TelegramCredential(chat_id=chat_id, token=token)


def read_file_credential(path: Path = CREDENTIAL_FILE) -> TelegramCredential:
    """Read the chat id and token from `path`, a file that only its owner, the
    account reading it, may read (the server's store, D-8, T28-06)."""
    if sys.platform == "win32":
        raise ChannelError("the credential file is read on Linux only")
    try:
        info = path.stat()
        if info.st_mode & 0o077 or info.st_uid != os.getuid():
            raise ChannelError(f"{path} must be readable by this account only")
        lines = path.read_text("utf-8").split()
    except ChannelError:
        raise
    except (OSError, UnicodeDecodeError) as error:
        raise ChannelError(f"{path} unreadable: {type(error).__name__}") from None
    if len(lines) != 2:
        raise ChannelError(f"{path} must hold the chat id and the token")
    return TelegramCredential(chat_id=lines[0], token=lines[1])


def read_credential() -> TelegramCredential:
    """The owner's credential from this system's store."""
    if sys.platform == "win32":
        return read_windows_credential()
    return read_file_credential()


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

    @property
    def fingerprint(self) -> str:
        """Names this bot and chat without revealing them: a test proves only
        the channel it was sent on (A28-5)."""
        identity = f"telegram|{self._credential.chat_id}|{self._credential.token}"
        return hashlib.sha256(identity.encode()).hexdigest()

    def send(self, text: str) -> str | None:
        """Send `text`; return why it failed, or None. Never raises. The
        reason is built here from the exception type and the HTTP status:
        nothing the network or Telegram says is passed on (A28-1, A28-4)."""
        try:
            url = f"https://{TELEGRAM_HOST}/bot{self._credential.token}/sendMessage"
            body = json.dumps({"chat_id": self._credential.chat_id, "text": text})
            response = self._transport(TelegramRequest(url, body.encode()))
        except Exception as error:  # noqa: BLE001 - reported, never raised
            return f"send failed: {type(error).__name__}"
        try:
            status = int(response.status)
        except Exception:  # noqa: BLE001 - any unreadable reply
            return "send failed: unreadable reply"
        try:
            # A reply past the bound may be the head of a longer one (A28-12).
            ok = len(response.body) <= _MAX_REPLY
            reply = json.loads(response.body) if ok else None
            ok = isinstance(reply, dict) and reply.get("ok") is True
        except Exception:  # noqa: BLE001 - an unreadable body is no success
            ok = False
        if status == 200 and ok:
            return None
        return f"HTTP {status}" + ("" if ok else ", not accepted")

    def report(self, at: datetime, failed: str, why: str) -> None:
        """Write a failed send to the local sinks, as a CRITICAL event."""
        failure = Event(
            EventKind.ALERT_CHANNEL,
            Severity.CRITICAL,
            at,
            {"channel": "telegram", "failed_kind": failed, "error": why},
        )
        for sink in self._local:
            sink.write(failure)

    def write(self, event: Event) -> None:
        why = self.send(_text(event))
        if why is not None:
            self.report(event.at, str(event.kind), why)


def _digest(code: str) -> str:
    return hashlib.sha256(code.strip().encode()).hexdigest()


def _hex64(value: object) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or value.strip("0123456789abcdef")
    ):
        raise ChannelError("channel test ledger has a malformed digest")
    return value


@dataclass(frozen=True, slots=True)
class _Record:
    kind: str
    code_sha256: str
    channel: str
    sent_at: datetime


class ChannelTests:
    """The weekly test of the Telegram channel (D-2), kept in a ledger.

    Every record names the channel it was sent on (`TelegramSink.fingerprint`):
    a test proves only that bot and chat, so a changed credential needs a new
    test (A28-5). A record dated after the wall clock means the clock went
    back: that is reported, never taken as fresh (A28-6)."""

    def __init__(
        self, path: Path, sink: TelegramSink, clock: Callable[[], datetime]
    ) -> None:
        self.path = path
        self._sink = sink
        self._clock = clock

    def now(self) -> datetime:
        """The wall clock, checked to be UTC."""
        return require_utc(self._clock(), field_name="clock")

    def _records(self) -> list[_Record]:
        """Every record, checked; any problem is a `ChannelError` (A28-8)."""
        try:
            if not self.path.exists():
                return []
            verify_ledger(self.path).require_intact()
            records: list[_Record] = []
            for entry in read_entries(self.path):
                payload = entry.payload
                keys = {"channel", "code_sha256", "sent_at"}
                if (
                    entry.record_type not in (SENT, ACKNOWLEDGED)
                    or set(payload) != keys
                ):
                    raise ChannelError("channel test ledger has an unknown record")
                record = _Record(
                    entry.record_type,
                    _hex64(payload["code_sha256"]),
                    _hex64(payload["channel"]),
                    require_utc(
                        datetime.fromisoformat(str(payload["sent_at"])),
                        field_name="sent_at",
                    ),
                )
                if record.kind == ACKNOWLEDGED and (
                    replace(record, kind=SENT) not in records
                ):
                    raise ChannelError(
                        "channel test ledger acknowledges an unsent test"
                    )
                if record.kind == SENT and any(
                    r.code_sha256 == record.code_sha256 for r in records
                ):  # each code is issued once (A28-10)
                    raise ChannelError("channel test ledger issues a code twice")
                records.append(record)
            return records
        except ChannelError:
            raise
        except Exception as error:  # noqa: BLE001 - a damaged ledger refuses
            raise ChannelError(
                f"channel test ledger unreadable: {type(error).__name__}"
            ) from None

    @staticmethod
    def _behind(records: list[_Record], now: datetime) -> str | None:
        latest = max((r.sent_at for r in records), default=None)
        if latest is not None and latest > now:
            return f"the clock is behind the newest channel test ({latest})"
        return None

    def _mine(self, records: list[_Record], kind: str) -> list[datetime]:
        own = self._sink.fingerprint
        return [r.sent_at for r in records if r.kind == kind and r.channel == own]

    def send_test(self) -> None:
        """Send a test carrying a fresh code; record it once it was sent. A
        failed send is also written to the local sinks (A28-3)."""
        now = self.now()
        records = self._records()
        if (behind := self._behind(records, now)) is not None:
            raise ChannelError(behind)
        used = {r.code_sha256 for r in records}
        code = f"{secrets.randbelow(10**6):06d}"
        while _digest(code) in used:  # each code is issued once (A28-7)
            code = f"{secrets.randbelow(10**6):06d}"
        why = self._sink.send(
            f"aqt alert channel test, sent {now:%Y-%m-%d %H:%M}Z.\n"
            f"Confirm on the app's computer:\n"
            f"python scripts/alert_channel.py ack {code}"
        )
        if why is not None:
            self._sink.report(now, "CHANNEL_TEST", why)
            raise ChannelError(f"test not sent: {why}")
        append_entry(
            self.path,
            record_type=SENT,
            payload={
                "channel": self._sink.fingerprint,
                "code_sha256": _digest(code),
                "sent_at": now.isoformat(),
            },
            recorded_at_utc=now,
        )

    def acknowledge(self, code: str) -> datetime:
        """Record the owner's code; return when its test was sent."""
        now = self.now()
        records = self._records()
        digest = _digest(code)
        sent = [r for r in records if r.kind == SENT and r.code_sha256 == digest]
        if not sent:
            raise ChannelError("no test was sent with that code")
        test = sent[-1]
        if test.channel != self._sink.fingerprint:
            raise ChannelError("that test was sent to a different bot or chat")
        if replace(test, kind=ACKNOWLEDGED) in records:
            raise ChannelError("that test is already acknowledged")
        append_entry(
            self.path,
            record_type=ACKNOWLEDGED,
            payload={
                "channel": test.channel,
                "code_sha256": digest,
                "sent_at": test.sent_at.isoformat(),
            },
            recorded_at_utc=now,
        )
        return test.sent_at

    def problem(self) -> str | None:
        """Why the start must be refused, or None. Never raises: a bad clock
        is a refusal too (A28-11)."""
        try:
            records = self._records()
            now = self.now()
        except ChannelError as error:
            return str(error)
        except Exception as error:  # noqa: BLE001 - e.g. a clock not in UTC
            return f"channel test unreadable: {type(error).__name__}"
        if (behind := self._behind(records, now)) is not None:
            return behind
        acknowledged = self._mine(records, ACKNOWLEDGED)
        if not acknowledged:
            return "no acknowledged alert channel test for this bot and chat (D-2)"
        newest = max(acknowledged)
        if now - newest > TEST_INTERVAL:
            return f"alert channel test overdue: last acknowledged test sent {newest}"
        return None

    def due(self) -> bool:
        """A new test is due: none was sent on this channel in the last 7
        days. Not while the clock is behind a record (`problem` says so)."""
        records = self._records()
        now = self.now()
        if self._behind(records, now) is not None:
            return False
        sent = self._mine(records, SENT)
        return not sent or now - max(sent) > TEST_INTERVAL


def owner_channel(
    ledger: Path, local: Sequence[Sink]
) -> tuple[TelegramSink, ChannelTests]:
    """The owner's real channel: the stored credential, the network and the
    wall clock. Used by the owner-run scripts only, never by tests."""
    sink = TelegramSink(read_credential(), urllib_transport, local)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    return sink, ChannelTests(ledger, sink, lambda: datetime.now(UTC))
