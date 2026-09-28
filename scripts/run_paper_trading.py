"""Run the paper-trading loop on exploration data (roadmap Task 24).

Usage:
    python scripts/run_paper_trading.py --config configs/paper_trading.example.toml
        --raw data/raw --out data/processed/paper

Reads only the exploration archives through the Task 14 manifest builder,
trades only against the simulator, and writes the run report, the operations
log and the incident log under `--out/<run_id>/`. Exit code 0 on a completed
run, 2 on REFUSE_START.
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
from aqt.monitoring.alerts import LedgerSink, StreamSink
from aqt.monitoring.events import Severity

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--raw", type=Path, default=Path("data/raw"))
    parser.add_argument("--out", type=Path, default=Path("data/processed/paper"))
    args = parser.parse_args(argv)

    config = load_config(args.config)
    build = build_exploration_manifest(EXPLORATION, config.symbol, args.raw)
    out = args.out / config.run_id
    out.mkdir(parents=True, exist_ok=True)
    operations = out / "operations.jsonl"
    report = run_paper(
        config,
        build.series,
        data_manifest_hash=build.manifest.manifest_sha256,
        sinks=[
            StreamSink(sys.stdout, Severity.WARNING),
            LedgerSink(operations, Severity.INFO),
        ],
        incidents=IncidentLog(out / "incidents.jsonl"),
        operations_log=operations,
        environ=os.environ,
        repository_root=REPOSITORY_ROOT,
    )
    text = json.dumps(report.as_mapping(), indent=2, sort_keys=True)
    (out / "report.json").write_text(text + "\n", encoding="utf-8")
    print(text)
    return 2 if report.refused else 0


if __name__ == "__main__":
    raise SystemExit(main())
