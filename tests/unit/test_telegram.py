"""Roadmap 2 Task 28: the Telegram sink and its weekly test. Every request
goes to a fake transport; nothing is sent anywhere. The token below is
synthetic."""

from __future__ import annotations

import io
import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from aqt.monitoring.alerts import AlertRouter, LedgerSink, StreamSink
from aqt.monitoring.events import Event, EventKind, Severity
from aqt.monitoring.telegram import (
    TEST_INTERVAL,
    ChannelError,
    ChannelTests,
    TelegramCredential,
    TelegramRequest,
    TelegramResponse,
    TelegramSink,
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
    assert "AAAA" not in stream.getvalue()


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
    assert tests.problem() == "no acknowledged alert channel test (D-2)"
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
    assert report.refused == ("no acknowledged alert channel test (D-2)",)


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
