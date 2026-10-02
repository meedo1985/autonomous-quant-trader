"""Run the paper-trading loop on exploration data (roadmap Task 24).

Usage:
    python scripts/run_paper_trading.py --config configs/paper_trading.example.toml
        --raw data/raw --out data/processed/paper

Reads only the exploration archives through the Task 14 manifest builder,
trades only against the simulator, and writes the run report, the operations
log and the incident log under `--out/<run_id>/`. With `--telegram`, CRITICAL
events also go to the owner's Telegram bot and the run needs a weekly test
acknowledged within 7 days (Task 28; `scripts/alert_channel.py`). With
`--deployment-record`, the run starts only from the owner's approved commit
(Task 30; `scripts/deployment.py`, `deploy/RUNBOOK.md`). Exit code
0 on a completed run, 2 on REFUSE_START.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from aqt.app.paper_loop import load_config, run_paper
from aqt.data.klines import EXPLORATION, build_exploration_manifest
from aqt.execution.safety import IncidentLog
from aqt.monitoring.alerts import LedgerSink, Sink, StreamSink
from aqt.monitoring.events import Severity
from aqt.monitoring.telegram import DEFAULT_LEDGER, ChannelError, owner_channel

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--raw", type=Path, default=Path("data/raw"))
    parser.add_argument("--out", type=Path, default=Path("data/processed/paper"))
    parser.add_argument(
        "--telegram",
        action="store_true",
        help="also alert the owner's Telegram bot (needs a tested channel)",
    )
    parser.add_argument(
        "--deployment-record",
        type=Path,
        help="the server's deployment record; refuse unless this is its commit",
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)
    build = build_exploration_manifest(EXPLORATION, config.symbol, args.raw)
    out = args.out / config.run_id
    out.mkdir(parents=True, exist_ok=True)
    operations = out / "operations.jsonl"
    sinks: list[Sink] = [
        StreamSink(sys.stdout, Severity.WARNING),
        LedgerSink(operations, Severity.INFO),
    ]
    channel = None
    if args.telegram:
        try:
            telegram, channel = owner_channel(DEFAULT_LEDGER, list(sinks))
        except ChannelError as error:
            print(f"Refused: {error}", file=sys.stderr)
            return 2
        sinks.append(telegram)
    report = run_paper(
        config,
        build.series,
        data_manifest_hash=build.manifest.manifest_sha256,
        sinks=sinks,
        incidents=IncidentLog(out / "incidents.jsonl"),
        operations_log=operations,
        environ=os.environ,
        repository_root=REPOSITORY_ROOT,
        channel=channel,
        deployment=args.deployment_record,
    )
    text = json.dumps(report.as_mapping(), indent=2, sort_keys=True)
    (out / "report.json").write_text(text + "\n", encoding="utf-8")
    print(text)
    return 2 if report.refused else 0


if __name__ == "__main__":
    raise SystemExit(main())
