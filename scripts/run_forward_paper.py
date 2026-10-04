"""Run forward paper trading on live public bars (roadmap 2, Task 29).

Usage:
    python scripts/run_forward_paper.py --config configs/forward_paper.example.toml
        --store data/live/BTCUSDT-1h.jsonl --account data/forward/account-1
        [--once] [--telegram] [--deployment-record PATH]

Each step appends Binance's newly closed public 1h bars to the store, then runs
the paper loop (baseline only, simulator only) over every decision hour whose
fill bar has closed, resuming the account from its journal
(`aqt.app.forward`). Without `--once` it steps a minute after every hour until
stopped. The configuration's `start` is the account's first decision hour; its
`end` is not used. Reads no exchange credential and refuses to run while any
Binance key variable is set; with `--telegram` it reads only the owner's
Telegram token (D-8). No real money is involved (owner answer Q-C, 2026-10-04).

Each step that runs appends one line to `<account>/forward_reports.jsonl`: the
loop's report and the `L-02` effective-decision count with its method.

A failed fetch (network, Binance, clock skew) is alerted and retried at the
next hour; its hours stay pending. A refused step stops the program with exit
code 2, which is never retried (`deploy/aqt-paper.service`): the refusal is
already logged and alerted, and the owner resolves it. With `--once`, exit code
0 is a step that ran or had nothing to do, 1 a failed fetch, 2 a refusal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from aqt.app.forward import ForwardError, l02_count, run_step
from aqt.app.paper_loop import PaperConfig, load_config
from aqt.app.state import AccountDir
from aqt.benchmarks.canonical import VOL_TARGET_HALF_LIFE_HOURS
from aqt.core.deployment import DeploymentError, approved_code
from aqt.data.binance_public import DownloadError, refuse_credentials, urllib_transport
from aqt.data.live_bars import LiveBarError, LiveBarStore, fetch_new_bars
from aqt.monitoring.alerts import AlertRouter, LedgerSink, Sink, StreamSink
from aqt.monitoring.events import Event, EventKind, Severity
from aqt.monitoring.telegram import (
    DEFAULT_LEDGER,
    ChannelError,
    ChannelTests,
    owner_channel,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MAX_SKEW = timedelta(seconds=5)  # owner setting S-5
STEP_OFFSET = timedelta(minutes=1)  # after the hour, so the bar has closed
REPORTS = "forward_reports.jsonl"
REFUSALS = Path("data/forward/deployment_refusals.jsonl")  # under the working dir
WARM_UP = (VOL_TARGET_HALF_LIFE_HOURS + 2) * timedelta(hours=1)
"""Bars the baseline needs before its first decision, plus its decision bar."""


def step(
    config: PaperConfig,
    store: LiveBarStore,
    account: AccountDir,
    sinks: list[Sink],
    channel: ChannelTests | None,
    deployment: Path | None,
) -> int:
    now = datetime.now(UTC)
    try:
        refuse_credentials(os.environ)
        # An empty store starts early enough for the baseline's warm-up.
        first = None if store.next_open_time() is not None else config.start - WARM_UP
        fetched = fetch_new_bars(
            urllib_transport, store, config.symbol, now, MAX_SKEW, first
        )
    except (DownloadError, LiveBarError, OSError) as error:
        # No new bars: nothing runs; the hours stay pending and are reported
        # as missed by the step that runs them.
        event = Event(
            EventKind.STALE_DATA, Severity.CRITICAL, now, {"refused": str(error)}
        )
        AlertRouter(sinks).emit(event)
        return 1
    series = store.series()
    try:
        report = run_step(
            config,
            series,
            account,
            now=now,
            reference_now=now - fetched.skew,
            sinks=sinks,
            data_manifest_hash=hashlib.sha256(store.path.read_bytes()).hexdigest(),
            environ=os.environ,
            repository_root=REPOSITORY_ROOT,
            channel=channel,
            deployment=deployment,
        )
    except ForwardError:
        return 2  # already alerted
    if report is None:
        return 0
    line = {
        "at": now.isoformat(),
        "l02": l02_count(account.journal, series).as_mapping(),
        "report": report.as_mapping(),
    }
    with (account.root / REPORTS).open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(line, sort_keys=True) + "\n")
    print(json.dumps(line, sort_keys=True))
    return 2 if report.refused else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Forward paper trading (Task 29)")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--store", type=Path, required=True)
    parser.add_argument("--account", type=Path, required=True)
    parser.add_argument("--once", action="store_true", help="run one step and exit")
    parser.add_argument("--telegram", action="store_true")
    parser.add_argument("--deployment-record", type=Path)
    args = parser.parse_args(argv)
    if args.deployment_record is not None:
        # Before the configuration, any data, network or channel, as the
        # replay runner does (S30-4): unapproved code stops here, logged to a
        # fixed file, and is never retried.
        try:
            approved_code(args.deployment_record, REPOSITORY_ROOT)
        except DeploymentError as error:
            refusal = {"decision": "REFUSE_START", "reason": f"deployment: {error}"}
            REFUSALS.parent.mkdir(parents=True, exist_ok=True)
            AlertRouter(
                [
                    StreamSink(sys.stdout, Severity.WARNING),
                    LedgerSink(REFUSALS, Severity.INFO),
                ]
            ).emit(
                Event(EventKind.STARTUP, Severity.CRITICAL, datetime.now(UTC), refusal)
            )
            return 2
    config = load_config(args.config)
    store = LiveBarStore(args.store, config.symbol)
    account = AccountDir(args.account)
    sinks: list[Sink] = [
        StreamSink(sys.stdout, Severity.WARNING),
        LedgerSink(account.operations_path, Severity.INFO),
    ]
    channel: ChannelTests | None = None
    if args.telegram:
        try:
            telegram, channel = owner_channel(DEFAULT_LEDGER, list(sinks))
        except ChannelError as error:
            refusal = {"decision": "REFUSE_START", "reason": f"telegram: {error}"}
            event = Event(
                EventKind.STARTUP, Severity.CRITICAL, datetime.now(UTC), refusal
            )
            AlertRouter(sinks).emit(event)
            return 2
        sinks.append(telegram)
    while True:
        code = step(config, store, account, sinks, channel, args.deployment_record)
        if args.once or code == 2:
            return code
        now = datetime.now(UTC)
        hour = now.replace(minute=0, second=0, microsecond=0)
        time.sleep((hour + timedelta(hours=1) + STEP_OFFSET - now).total_seconds())


if __name__ == "__main__":
    raise SystemExit(main())
