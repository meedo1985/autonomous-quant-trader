"""Roadmap 2 Task 28: the Telegram sink and its weekly test. Every request
goes to a fake transport; nothing is sent anywhere. The token below is
synthetic."""

from __future__ import annotations

import ctypes
import importlib.util
import io
import json
import re
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from aqt.core.ledger import append_entry, read_entries
from aqt.monitoring.alerts import AlertRouter, LedgerSink, Sink, StreamSink
from aqt.monitoring.events import Event, EventKind, Severity
from aqt.monitoring.telegram import (
    TEST_INTERVAL,
    ChannelError,
    ChannelTests,
    TelegramCredential,
    TelegramRequest,
    TelegramResponse,
    TelegramSink,
    read_windows_credential,
    urllib_transport,
)
from tests.integration.test_paper_loop import _config, _run, _series

TOKEN = "123456789:" + "A" * 35
CREDENTIAL = TelegramCredential(chat_id="42", token=TOKEN)
NOW = datetime(2026, 10, 2, 12, tzinfo=UTC)
OK = TelegramResponse(200, b'{"ok":true}')


class Fake:
    """A transport that records requests and answers from a script."""

    def __init__(self, *answers: TelegramResponse | Exception) -> None:
        self.answers = list(answers)
        self.requests: list[TelegramRequest] = []

    def __call__(self, request: TelegramRequest) -> TelegramResponse:
        self.requests.append(request)
        answer = self.answers.pop(0) if self.answers else OK
        if isinstance(answer, Exception):
            raise answer
        return answer

    def texts(self) -> list[str]:
        return [json.loads(r.body)["text"] for r in self.requests]


class Clock:
    def __init__(self, now: datetime = NOW) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now


def _event(**fields: str) -> Event:
    return Event(EventKind.STARTUP, Severity.CRITICAL, NOW, fields)


def _sink(fake: Fake, stream: io.StringIO) -> TelegramSink:
    return TelegramSink(CREDENTIAL, fake, [StreamSink(stream, Severity.INFO)])


def test_a_critical_event_is_sent_to_the_owners_chat() -> None:
    fake, stream = Fake(), io.StringIO()
    _sink(fake, stream).write(_event(decision="REFUSE_START", reason="x"))
    (request,) = fake.requests
    assert request.url == f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    body = json.loads(request.body)
    assert body["chat_id"] == "42"
    assert body["text"].startswith("CRITICAL STARTUP at 2026-10-02 12:00:00Z")
    assert "reason: x" in body["text"]
    assert stream.getvalue() == ""


def test_only_critical_events_reach_the_sink() -> None:
    fake = Fake()
    router = AlertRouter([_sink(fake, io.StringIO())])
    router.emit(Event(EventKind.STARTUP, Severity.WARNING, NOW, {}))
    router.emit(_event())
    assert len(fake.requests) == 1


@pytest.mark.parametrize(
    "answer",
    [
        OSError(f"cannot reach https://api.telegram.org/bot{TOKEN}/sendMessage"),
        TelegramResponse(500, b""),
        TelegramResponse(200, b"not json"),
        TelegramResponse(
            400, b'{"ok":false,"description":"bad ' + TOKEN.encode() + b'"}'
        ),
        # A28-1: a long description used to be cut inside the token.
        TelegramResponse(
            400,
            b'{"ok":false,"description":"' + b"x" * 180 + TOKEN.encode() + b'"}',
        ),
        # A28-4: a reply too deep to parse.
        TelegramResponse(200, b"[" * 100_000 + b"]" * 100_000),
    ],
)
def test_a_failed_send_is_alerted_locally_without_the_token(
    tmp_path: Path, answer: TelegramResponse | Exception
) -> None:
    """Roadmap acceptance: a failed send is logged and alerted locally, never
    raised into the loop, and the token reaches no log."""
    stream, log = io.StringIO(), tmp_path / "operations.jsonl"
    local = [StreamSink(stream, Severity.INFO), LedgerSink(log, Severity.INFO)]
    router = AlertRouter([*local, TelegramSink(CREDENTIAL, Fake(answer), local)])
    router.emit(_event(reason="loss stop"))
    lines = [json.loads(line) for line in stream.getvalue().splitlines()]
    assert [line["kind"] for line in lines] == ["STARTUP", "ALERT_CHANNEL"]
    failure = lines[1]
    assert failure["severity"] == "CRITICAL"
    assert failure["fields"]["failed_kind"] == "STARTUP"
    assert TOKEN not in stream.getvalue()
    assert TOKEN.encode() not in log.read_bytes()
    assert TOKEN[:12] not in stream.getvalue() and "AAAA" not in stream.getvalue()


def test_a_sink_without_a_local_fallback_is_refused() -> None:
    with pytest.raises(ChannelError):
        TelegramSink(CREDENTIAL, Fake(), [])


def test_only_the_telegram_host_is_reachable() -> None:
    with pytest.raises(ChannelError):
        TelegramRequest("https://example.com/bot1/sendMessage", b"")
    with pytest.raises(ChannelError):
        TelegramRequest("http://api.telegram.org/bot1/sendMessage", b"")


def test_the_credential_never_prints_its_token() -> None:
    assert TOKEN not in repr(CREDENTIAL)
    assert TOKEN not in repr(
        TelegramRequest(f"https://api.telegram.org/bot{TOKEN}/x", b"")
    )


def test_a_token_in_an_event_field_is_redacted() -> None:
    stream = io.StringIO()
    AlertRouter([StreamSink(stream, Severity.INFO)]).emit(
        _event(note=f"key was {TOKEN}")
    )
    assert TOKEN not in stream.getvalue() and "REDACTED" in stream.getvalue()


def _tests(tmp_path: Path, fake: Fake, clock: Clock) -> ChannelTests:
    return ChannelTests(tmp_path / "tests.jsonl", _sink(fake, io.StringIO()), clock)


def _code(fake: Fake) -> str:
    match = re.search(r"ack (\d{6})", fake.texts()[-1])
    assert match is not None
    return match.group(1)


def test_a_test_must_be_acknowledged_with_its_code(tmp_path: Path) -> None:
    fake, clock = Fake(), Clock()
    tests = _tests(tmp_path, fake, clock)
    assert (
        tests.problem()
        == "no acknowledged alert channel test for this bot and chat (D-2)"
    )
    assert tests.due()
    tests.send_test()
    code = _code(fake)
    assert code not in (tmp_path / "tests.jsonl").read_text()  # only its hash
    assert not tests.due()
    assert tests.problem() is not None  # sent, not yet acknowledged
    with pytest.raises(ChannelError, match="no test"):
        tests.acknowledge("000000" if code != "000000" else "111111")
    assert tests.acknowledge(code) == NOW
    assert tests.problem() is None
    with pytest.raises(ChannelError, match="already"):
        tests.acknowledge(code)


def test_an_acknowledged_test_lasts_seven_days(tmp_path: Path) -> None:
    fake, clock = Fake(), Clock()
    tests = _tests(tmp_path, fake, clock)
    tests.send_test()
    clock.now = NOW + timedelta(days=3)  # acknowledged late: counts from sending
    tests.acknowledge(_code(fake))
    clock.now = NOW + TEST_INTERVAL
    assert tests.problem() is None and not tests.due()
    clock.now += timedelta(seconds=1)
    assert "overdue" in str(tests.problem()) and tests.due()


def test_an_unsent_test_is_not_recorded(tmp_path: Path) -> None:
    tests = _tests(tmp_path, Fake(TelegramResponse(500, b"")), Clock())
    with pytest.raises(ChannelError, match="not sent"):
        tests.send_test()
    assert not (tmp_path / "tests.jsonl").exists()


def test_a_damaged_test_ledger_refuses(tmp_path: Path) -> None:
    fake = Fake()
    tests = _tests(tmp_path, fake, Clock())
    tests.send_test()
    tests.acknowledge(_code(fake))
    path = tmp_path / "tests.jsonl"
    path.write_text(path.read_text().replace("sent_at", "sent_At"))
    assert "unreadable" in str(tests.problem())


def _acknowledged(tmp_path: Path, clock: Clock) -> tuple[Fake, ChannelTests]:
    fake = Fake()
    tests = _tests(tmp_path, fake, clock)
    tests.send_test()
    tests.acknowledge(_code(fake))
    return fake, tests


def test_an_untested_channel_refuses_the_start(tmp_path: Path) -> None:
    tests = _tests(tmp_path, Fake(), Clock())
    report = _run(tmp_path / "run", _config(2), _series(24 * 12), channel=tests)
    assert report.refused == (
        "no acknowledged alert channel test for this bot and chat (D-2)",
    )


def test_an_overdue_test_refuses_the_start(tmp_path: Path) -> None:
    clock = Clock()
    _, tests = _acknowledged(tmp_path, clock)
    clock.now += TEST_INTERVAL + timedelta(seconds=1)
    report = _run(tmp_path / "run", _config(2), _series(24 * 12), channel=tests)
    assert len(report.refused) == 1 and "overdue" in report.refused[0]


def test_a_tested_channel_runs_and_stays_quiet(tmp_path: Path) -> None:
    clock = Clock()
    fake, tests = _acknowledged(tmp_path, clock)
    report = _run(tmp_path / "run", _config(2), _series(24 * 12), channel=tests)
    assert report.refused == () and report.final_mode == "RUNNING"
    assert len(fake.requests) == 1  # the test itself; nothing else was due


class Ticking(Clock):
    """A wall clock that moves 1 minute on every reading once ticking."""

    def __init__(self, now: datetime) -> None:
        super().__init__(now)
        self.ticking = False

    def __call__(self) -> datetime:
        if self.ticking:
            self.now += timedelta(minutes=1)
        return self.now


def test_an_overdue_test_during_a_run_is_sent_and_reminded_hourly(
    tmp_path: Path,
) -> None:
    """Q28-2: the run sends the due test itself and, while it is overdue,
    raises a CRITICAL alert at most once per wall-clock hour. The mode does
    not change."""
    clock = Ticking(NOW)
    fake, tests = _acknowledged(tmp_path, clock)
    # The start check reads exactly 7 days (still current); every later
    # reading is past it, so the run's first hour finds the test due.
    clock.now = NOW + TEST_INTERVAL - timedelta(minutes=1)
    clock.ticking = True
    sink = TelegramSink(
        CREDENTIAL, fake, [LedgerSink(tmp_path / "ops.jsonl", Severity.INFO)]
    )
    channel = ChannelTests(tmp_path / "tests.jsonl", sink, clock)
    report = _run(
        tmp_path / "run",
        _config(1),
        _series(24 * 12),
        channel=channel,
        sinks=[LedgerSink(tmp_path / "run" / "operations.jsonl", Severity.INFO), sink],
    )
    assert report.refused == () and report.final_mode == "RUNNING"
    texts = fake.texts()
    assert sum(t.startswith("aqt alert channel test") for t in texts) == 2
    reminders = [t for t in texts if t.startswith("CRITICAL ALERT_CHANNEL")]
    assert reminders and all("overdue" in t for t in reminders)
    # 24 decision hours take about 1.5 wall-clock hours here (a few readings
    # per check): the overdue test is reminded once per wall hour, not hourly
    # by the bar clock.
    assert 1 <= len(reminders) <= 2


@pytest.mark.parametrize(
    "fields",
    [
        {"url": f"https://api.telegram.org/bot{TOKEN}/sendMessage"},
        {f"https://api.telegram.org/bot{TOKEN}/sendMessage": "x"},
    ],
)
def test_a_token_inside_its_url_is_redacted(fields: dict[str, str]) -> None:
    """A28-2: no word boundary precedes the token after `bot`."""
    stream = io.StringIO()
    AlertRouter([StreamSink(stream, Severity.INFO)]).emit(_event(**fields))
    assert TOKEN[:12] not in stream.getvalue()


def test_a_failed_test_send_is_alerted_locally(tmp_path: Path) -> None:
    """A28-3: the owner's `test` command records its failure locally too."""
    log = tmp_path / "log.jsonl"
    failing = Fake(TelegramResponse(500, b""))
    sink = TelegramSink(CREDENTIAL, failing, [LedgerSink(log, Severity.INFO)])
    tests = ChannelTests(tmp_path / "tests.jsonl", sink, Clock())
    with pytest.raises(ChannelError, match="not sent"):
        tests.send_test()
    (entry,) = read_entries(log)
    fields = entry.payload["fields"]
    assert entry.payload["kind"] == "ALERT_CHANNEL"
    assert fields["failed_kind"] == "CHANNEL_TEST"
    assert fields["error"] == "HTTP 500, not accepted"


def test_a_check_that_fails_does_not_stop_the_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A28-4: whatever the hourly check meets is reported, never raised."""
    _, tests = _acknowledged(tmp_path, Clock())

    def broken(self: ChannelTests) -> bool:
        raise RecursionError

    monkeypatch.setattr(ChannelTests, "due", broken)
    report = _run(tmp_path / "run", _config(1), _series(24 * 12), channel=tests)
    assert report.refused == () and report.final_mode == "RUNNING"
    log = (tmp_path / "run" / "operations.jsonl").read_text()
    assert "channel test failed: RecursionError" in log


def test_a_new_bot_or_chat_needs_its_own_test(tmp_path: Path) -> None:
    """A28-5: an acknowledgment proves only the channel it was sent on."""
    clock = Clock()
    fake, _ = _acknowledged(tmp_path, clock)
    old_code = _code(fake)
    other = TelegramCredential(chat_id="43", token=TOKEN)
    sink = TelegramSink(other, fake, [StreamSink(io.StringIO(), Severity.INFO)])
    tests = ChannelTests(tmp_path / "tests.jsonl", sink, clock)
    assert "no acknowledged" in str(tests.problem()) and tests.due()
    with pytest.raises(ChannelError, match="different bot"):
        tests.acknowledge(old_code)


def test_a_clock_set_back_is_reported_not_trusted(tmp_path: Path) -> None:
    """A28-6: records dated after the clock refuse, and nothing is due."""
    clock = Clock()
    _, tests = _acknowledged(tmp_path, clock)
    clock.now = NOW - timedelta(days=30)
    assert "clock is behind" in str(tests.problem()) and not tests.due()
    with pytest.raises(ChannelError, match="clock is behind"):
        tests.send_test()


class Falling(Clock):
    """A wall clock that goes back 2 hours on every reading once falling."""

    def __init__(self, now: datetime) -> None:
        super().__init__(now)
        self.falling = False

    def __call__(self) -> datetime:
        if self.falling:
            self.now -= timedelta(hours=2)
        return self.now


def test_a_clock_going_back_does_not_silence_the_hourly_check(
    tmp_path: Path,
) -> None:
    """A28-6: a reading before the last check starts a new hour at once."""
    clock = Falling(NOW)
    _, tests = _acknowledged(tmp_path, clock)
    clock.now = NOW + timedelta(hours=4)  # the start check still passes
    clock.falling = True
    report = _run(tmp_path / "run", _config(1), _series(24 * 12), channel=tests)
    assert report.refused == () and report.final_mode == "RUNNING"
    log = (tmp_path / "run" / "operations.jsonl").read_text()
    assert log.count("clock is behind") >= 20  # about once per decision hour


def test_a_code_is_never_issued_twice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A28-7: a random repeat is drawn again, so both tests can be confirmed."""
    draws = iter([5, 5, 7])
    monkeypatch.setattr(
        "aqt.monitoring.telegram.secrets.randbelow", lambda _: next(draws)
    )
    clock, fake = Clock(), Fake()
    tests = _tests(tmp_path, fake, clock)
    tests.send_test()
    first = _code(fake)
    clock.now += timedelta(days=8)
    tests.send_test()
    second = _code(fake)
    assert (first, second) == ("000005", "000007")
    tests.acknowledge(first)
    tests.acknowledge(second)
    assert tests.problem() is None


def test_a_well_chained_but_malformed_record_refuses(tmp_path: Path) -> None:
    """A28-8: a naive timestamp in an intact chain is a refusal, not a crash."""
    path = tmp_path / "tests.jsonl"
    append_entry(
        path,
        record_type="aqt.channel_test.sent.v1",
        payload={
            "channel": "0" * 64,
            "code_sha256": "0" * 64,
            "sent_at": "2026-10-02T12:00:00",
        },
        recorded_at_utc=NOW,
    )
    tests = ChannelTests(path, _sink(Fake(), io.StringIO()), Clock())
    assert "unreadable" in str(tests.problem())
    with pytest.raises(ChannelError):
        tests.due()


@pytest.mark.skipif(sys.platform != "win32", reason="Windows credential store")
@pytest.mark.parametrize(
    ("blob", "expected"),
    [
        (TOKEN.encode("utf-16-le"), TOKEN),  # as `cmdkey` stores it
        (TOKEN.encode(), TOKEN),
        (b"\x00\xd8", None),  # not text: refused, not a traceback (A28-9)
    ],
)
def test_the_credential_reader_with_a_fake_store(
    monkeypatch: pytest.MonkeyPatch, blob: bytes, expected: str | None
) -> None:
    """T28-01: the success path, against a fake `advapi32`; the real store
    is never touched."""
    freed: list[object] = []
    keep: list[object] = []

    class FakeAdvapi:
        def CredReadW(self, target: str, kind: int, flags: int, out: object) -> int:  # noqa: N802
            assert (target, kind, flags) == ("aqt-telegram", 1, 0)
            pointer = out._obj  # type: ignore[attr-defined]
            entry = type(pointer)._type_()
            data = (ctypes.c_ubyte * len(blob)).from_buffer_copy(blob)
            keep.extend([entry, data])
            entry.CredentialBlobSize = len(blob)
            entry.CredentialBlob = ctypes.cast(data, ctypes.POINTER(ctypes.c_ubyte))
            entry.UserName = "42"
            pointer.contents = entry
            return 1

        def CredFree(self, pointer: object) -> None:  # noqa: N802
            freed.append(pointer)

    monkeypatch.setattr(ctypes, "WinDLL", lambda *_, **__: FakeAdvapi(), raising=False)
    if expected is None:
        with pytest.raises(ChannelError, match="not readable") as caught:
            read_windows_credential()
        assert caught.value.__context__ is None
    else:
        assert read_windows_credential() == TelegramCredential("42", expected)
    assert len(freed) == 1


def test_a_code_sent_twice_in_the_ledger_refuses(tmp_path: Path) -> None:
    """A28-10: a ledger that issues one code twice is refused, so the old
    code cannot acknowledge the newer test."""
    clock, fake = Clock(), Fake()
    tests = _tests(tmp_path, fake, clock)
    tests.send_test()
    (sent,) = read_entries(tests.path)
    clock.now += timedelta(days=8)
    append_entry(
        tests.path,
        record_type=sent.record_type,
        payload={**sent.payload, "sent_at": clock.now.isoformat()},
        recorded_at_utc=clock.now,
    )
    assert tests.problem() == "channel test ledger issues a code twice"
    with pytest.raises(ChannelError, match="twice"):
        tests.acknowledge(_code(fake))


class Naive(Clock):
    """A wall clock that loses its time zone once `broken` is set, after one
    more good reading (the start check)."""

    def __init__(self) -> None:
        super().__init__()
        self.broken = False
        self.good = 1

    def __call__(self) -> datetime:
        if self.broken and not self.good:
            return self.now.replace(tzinfo=None)
        if self.broken:
            self.good -= 1
        return self.now


def test_a_bad_clock_is_reported_not_raised(tmp_path: Path) -> None:
    """A28-11: `problem` and the hourly check contain a clock error too."""
    clock = Naive()
    _, tests = _acknowledged(tmp_path, clock)
    clock.broken = True
    report = _run(tmp_path / "run", _config(1), _series(24 * 12), channel=tests)
    assert report.refused == () and report.final_mode == "RUNNING"
    log = (tmp_path / "run" / "operations.jsonl").read_text()
    assert log.count("BarSemanticsError") >= 20  # once per decision hour
    assert tests.problem() == "channel test unreadable: BarSemanticsError"


def test_a_reply_past_the_bound_is_not_a_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A28-12: the transport reads one byte past the bound, and a reply that
    long is refused even when its head is a valid answer."""
    body = b'{"ok":true}'.ljust(65536) + b"INVALID"
    asked: list[int] = []

    class Response:
        status = 200

        def __enter__(self) -> Response:
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def read(self, size: int) -> bytes:
            asked.append(size)
            return body[:size]

    class Opener:
        def open(self, *_: object, **__: object) -> Response:
            return Response()

    monkeypatch.setattr("aqt.monitoring.telegram._OPENER", Opener())
    sink = TelegramSink(
        CREDENTIAL, urllib_transport, [StreamSink(io.StringIO(), Severity.INFO)]
    )
    assert sink.send("hello") == "HTTP 200, not accepted"
    assert asked == [65537]
    assert _sink(Fake(TelegramResponse(200, body)), io.StringIO()).send("x") == (
        "HTTP 200, not accepted"
    )


def test_the_test_ledger_cannot_share_the_failure_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A28-13: `--ledger` named like the CLI's failure log is refused before
    anything is sent or written."""
    path = Path(__file__).parents[2] / "scripts" / "alert_channel.py"
    spec = importlib.util.spec_from_file_location("alert_channel", path)
    assert spec is not None and spec.loader is not None
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    fake = Fake(TelegramResponse(500, b""), OK)

    def fake_channel(
        ledger: Path, local: list[Sink]
    ) -> tuple[TelegramSink, ChannelTests]:
        sink = TelegramSink(CREDENTIAL, fake, local)
        return sink, ChannelTests(ledger, sink, Clock())

    monkeypatch.setattr(cli, "owner_channel", fake_channel)
    ledger = tmp_path / "Alert_Channel_Log.jsonl"
    for _ in range(2):
        assert cli.main(["--ledger", str(ledger), "test"]) == 2
    assert fake.requests == [] and not ledger.exists()
    assert "may not be named" in capsys.readouterr().err
