"""Run the Task 25 paper-trading drills on exploration data (roadmap Task 25).

Usage:
    python scripts/run_drills.py --config configs/paper_trading.example.toml
        --raw data/raw --out review/task25/drills

Each drill writes its run report, operations log and incident log under
`--out/<drill>/`, checks its expected outcome, and records the result in
`--out/summary.json`. Simulator only; no credentials; nothing is traded.
Exit code 0 when every drill met its expected outcome, 1 otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

from aqt.app.paper_loop import (
    PaperConfig,
    RunReport,
    contiguous_window,
    load_config,
    nonce_for,
    run_paper,
)
from aqt.data.bars import BarSeries
from aqt.data.klines import EXPLORATION, build_exploration_manifest
from aqt.execution.orders import client_order_id_for
from aqt.execution.reconcile import LocalRecord, reconcile
from aqt.execution.safety import (
    IncidentLog,
    Mode,
    SafetyController,
    SafetyError,
    Trigger,
)
from aqt.execution.simulator import Fault, Scenario, SimulatedExchange
from aqt.governor.authorization import Authorization
from aqt.monitoring.alerts import AlertRouter, LedgerSink
from aqt.monitoring.events import Severity

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HOUR = timedelta(hours=1)
DAY = 24 * HOUR
DRILL_DAYS = 30
"""Every drill but the clean run uses the first 30 days of the window."""


@dataclass(frozen=True, slots=True)
class DrillResult:
    name: str
    expected: str
    observed: str
    passed: bool


def _events(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text("utf-8").splitlines() if path.exists() else []
    return [json.loads(line)["payload"] for line in lines]


def _transitions(out: Path) -> list[tuple[object, object, object]]:
    return [
        (e["fields"].get("from"), e["fields"].get("to"), e["fields"].get("trigger"))
        for e in _events(out / "operations.jsonl")
        if e["kind"] == "STATE_TRANSITION"
    ]


class _Runner:
    def __init__(self, series: BarSeries, manifest_hash: str, root: Path) -> None:
        self.series = series
        self.manifest_hash = manifest_hash
        self.root = root

    def run(
        self,
        name: str,
        config: PaperConfig,
        *,
        incidents: Path | None = None,
        environ: Mapping[str, str] | None = None,
        **kwargs: object,
    ) -> tuple[RunReport, Path]:
        out = self.root / name
        # Never reuse or clear an earlier attempt's logs (section 26, A25-3).
        out.mkdir(parents=True, exist_ok=False)
        operations = out / "operations.jsonl"
        report = run_paper(
            replace(config, run_id=f"drill-{name}"),
            self.series,
            data_manifest_hash=self.manifest_hash,
            sinks=[LedgerSink(operations, Severity.INFO)],
            incidents=IncidentLog(incidents or out / "incidents.jsonl"),
            operations_log=operations,
            environ=environ or {},
            repository_root=REPOSITORY_ROOT,
            **kwargs,  # type: ignore[arg-type]
        )
        text = json.dumps(report.as_mapping(), indent=2, sort_keys=True)
        (out / "report.json").write_text(text + "\n", encoding="utf-8", newline="\n")
        return report, out


def drill_clean(runner: _Runner, config: PaperConfig) -> DrillResult:
    report, _ = runner.run("clean", config)
    passed = report.refused == () and report.final_mode in ("RUNNING", "HALT")
    return DrillResult(
        "clean",
        "full window runs to the end without refusal; no FREEZE",
        f"hours {report.hours}, scheduled {report.scheduled_decisions}, "
        f"authorizations {report.authorizations}, orders {report.orders_sent}, "
        f"final {report.final_mode}",
        passed,
    )


def _orders_from(out: Path, at: datetime) -> list[dict[str, Any]]:
    return [
        e
        for e in _events(out / "operations.jsonl")
        if e["kind"] == "ORDER" and str(e["at"]) >= at.isoformat()
    ]


def drill_halt(runner: _Runner, config: PaperConfig, control: Path) -> DrillResult:
    """Over the clean run's window, so the clean run is the control: it shows
    an order the HALT must suppress (A25-1)."""
    at = config.start + 10 * DAY
    expected_orders = _orders_from(control, at)
    report, out = runner.run("halt", config, commands={at: Trigger.OWNER_HALT})
    after = _orders_from(out, at)
    passed = report.final_mode == "HALT" and after == [] and len(expected_orders) > 0
    return DrillResult(
        "halt",
        f"owner HALT at {at.isoformat()}: the clean run places an order after "
        "that time; with the HALT there is none; ends in HALT",
        f"clean-run orders after that time {len(expected_orders)} "
        f"({', '.join(str(e['at'])[:16] for e in expected_orders)}); "
        f"orders after HALT {len(after)}, final {report.final_mode}",
        passed,
    )


def drill_flatten(runner: _Runner, config: PaperConfig) -> DrillResult:
    at = config.start + 10 * DAY
    report, out = runner.run("flatten", config, commands={at: Trigger.OWNER_FLATTEN})
    moves = _transitions(out)
    held = Decimal(report.final_balances.get("BTC", "0"))
    steps = [
        (
            str(e["at"])[:16],
            Decimal(e["fields"]["held_before"]),
            Decimal(e["fields"]["orig_qty"]),
            Decimal(e["fields"]["executed_qty"]),
        )
        for e in _orders_from(out, at)
        if e["fields"].get("state") == "FLATTEN"
    ]
    fraction = config.flatten.max_step_fraction
    # Each step from the audit log (A25-2): at most `fraction` of the holding
    # it was sized from, one per hour, and each starts from what the last
    # left. The remainder is never negative.
    bounded = all(qty <= held_before * fraction for _, held_before, qty, _ in steps)
    hourly = all(a[0] < b[0] for a, b in zip(steps, steps[1:], strict=False))
    chained = all(b[1] == a[1] - a[3] for a, b in zip(steps, steps[1:], strict=False))
    last = steps[-1][1] - steps[-1][3] if steps else None
    passed = (
        len(steps) >= 2
        and bounded
        and hourly
        and chained
        and last == held
        and held >= 0
        and report.final_mode == "HALT"
        and ("FLATTEN", "HALT", "FLATTEN_DONE") in moves
    )
    trace = [[t, str(h), str(q), str(x)] for t, h, q, x in steps]
    (out / "steps.json").write_text(
        json.dumps(trace, indent=2) + "\n", "utf-8", newline="\n"
    )
    return DrillResult(
        "flatten",
        f"owner FLATTEN at {at.isoformat()}: each logged sell is at most "
        f"{fraction} of the holding before it, one per hour, chained, then HALT "
        "with a non-negative remainder",
        f"{len(steps)} steps, largest share "
        f"{max((q / h for _, h, q, _ in steps), default=0):.4f}, "
        f"transitions {moves}, final {report.final_mode}, BTC left {held}",
        passed,
    )


def _first_order_id(run_id: str) -> str:
    nonce = nonce_for(run_id, 0)
    return client_order_id_for(cast(Authorization, SimpleNamespace(nonce=nonce)))


def drill_ambiguous(runner: _Runner, config: PaperConfig) -> DrillResult:
    faulty = _first_order_id("drill-ambiguous")
    scenario = Scenario({faulty: Fault(timeout=True, unknown_queries=5)})
    report, out = runner.run("ambiguous", config, scenario=scenario)
    moves = _transitions(out)
    open_incidents = IncidentLog(out / "incidents.jsonl").open_incidents()
    passed = (
        report.final_mode == "FREEZE"
        and report.orders_sent == 1
        and [m[2] for m in moves] == ["AMBIGUOUS_ORDER"]
        and len(open_incidents) == 1
    )
    return DrillResult(
        "ambiguous",
        "first order times out and its status cannot be read: section 21 ends "
        "in FREEZE with one incident; no further order for the rest of the run",
        f"orders {report.orders_sent}, transitions {moves}, "
        f"open incidents {len(open_incidents)}, final {report.final_mode}",
        passed,
    )


def drill_refuse_start(runner: _Runner, config: PaperConfig) -> DrillResult:
    incidents = runner.root / "ambiguous" / "incidents.jsonl"
    left_open, _ = runner.run("refuse_start_open_incident", config, incidents=incidents)
    dummy = {"BINANCE_API_KEY": "drill-dummy-not-a-key"}
    credential, out = runner.run("refuse_start_credential", config, environ=dummy)
    logged = (out / "operations.jsonl").read_text("utf-8")
    passed = (
        left_open.final_mode == "REFUSED"
        and any("open incidents" in r for r in left_open.refused)
        and credential.final_mode == "REFUSED"
        and any("credential" in r for r in credential.refused)
        and "drill-dummy-not-a-key" not in logged
        and left_open.orders_sent == credential.orders_sent == 0
    )
    return DrillResult(
        "refuse_start",
        "a start with the ambiguous drill's incident still open, and a start "
        "with a Binance key variable set, are both refused with no order; the "
        "variable's value is never logged",
        f"open incident: {left_open.refused}; credential: {credential.refused}",
        passed,
    )


def drill_freeze_reconcile(
    series: BarSeries, config: PaperConfig, out: Path
) -> DrillResult:
    """Controller level: the paper loop never leaves FREEZE within a run, so
    the recovery half is exercised on the same components directly."""
    out.mkdir(parents=True, exist_ok=False)
    at = config.start + 10 * DAY
    step_id = (
        "aqt-flat-"
        + hashlib.sha256(f"{config.symbol}|{at.isoformat()}|1".encode()).hexdigest()[
            :27
        ]
    )
    window = contiguous_window(series, config.start, config.end)
    if isinstance(window, str):
        return DrillResult("freeze_reconcile", "", window, False)
    held = {"USDT": Decimal(0), "BTC": Decimal(1)}
    exchange = SimulatedExchange(
        {config.symbol: window},
        {config.symbol: config.filters},
        dict(held),
        scenario=Scenario({step_id: Fault(timeout=True)}),
    )
    incidents = IncidentLog(out / "incidents.jsonl")
    controller = SafetyController(
        AlertRouter([LedgerSink(out / "operations.jsonl", Severity.INFO)]),
        incidents,
        at,
        mode=Mode.RUNNING,
    )
    controller.trigger(Trigger.OWNER_FLATTEN, at, "drill: FLATTEN pressed")
    mark = Decimal(repr(series.bar_at(at - HOUR).close))
    controller.tick(
        exchange, config.symbol, config.filters, config.flatten, mark, at, at
    )
    faults = [
        e["fields"]["detail"]
        for e in _events(out / "operations.jsonl")
        if e["fields"].get("trigger") == "FLATTEN_FAULT"
    ]
    steps = [f"after the timed-out sell: {controller.mode} ({'; '.join(faults)})"]
    later = at + HOUR
    blind = reconcile(exchange, LocalRecord(held), config.tolerance, later)
    try:
        controller.exit_freeze(blind, later)
        steps.append("blind check ACCEPTED")
    except SafetyError as error:
        steps.append(f"blind check refused: {error}")
    full = reconcile(
        exchange, LocalRecord(held, controller.sent), config.tolerance, later
    )
    steps.append(f"full check passed={full.passed}, resolved={list(full.resolved)}")
    mode = controller.exit_freeze(full, later)
    steps.append(f"after the full check: {mode}; BTC {exchange.balances()['BTC']}")
    passed = (
        controller_froze_on_timeout(faults)
        and steps[1].startswith("blind check refused")
        and full.passed
        and mode is Mode.HALT
        and exchange.balances()["BTC"] < held["BTC"]  # the lost-reply sell filled
    )
    (out / "steps.json").write_text(
        json.dumps(steps, indent=2) + "\n", "utf-8", newline="\n"
    )
    return DrillResult(
        "freeze_reconcile",
        "a FLATTEN sell whose reply is lost enters FREEZE; a check that did not "
        "look the order up is refused; a check that did passes and leaves "
        "FREEZE for HALT (never straight to trading)",
        "; ".join(steps),
        passed,
    )


def controller_froze_on_timeout(faults: list[str]) -> bool:
    """The FREEZE must come from the lost reply, not from a rejection."""
    return len(faults) == 1 and faults[0].startswith("SimulatedTimeout")


def run_drills(
    config: PaperConfig, series: BarSeries, manifest_hash: str, out: Path
) -> list[DrillResult]:
    runner = _Runner(series, manifest_hash, out)
    short = replace(config, end=config.start + DRILL_DAYS * DAY)
    drills: list[Callable[[], DrillResult]] = [
        lambda: drill_clean(runner, config),
        lambda: drill_halt(runner, config, out / "clean"),
        lambda: drill_flatten(runner, short),
        lambda: drill_ambiguous(runner, short),
        lambda: drill_refuse_start(runner, short),
        lambda: drill_freeze_reconcile(series, short, out / "freeze_reconcile"),
    ]
    return [drill() for drill in drills]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--raw", type=Path, default=Path("data/raw"))
    parser.add_argument("--out", type=Path, default=Path("review/task25/drills"))
    args = parser.parse_args(argv)

    if args.out.exists() and any(args.out.iterdir()):
        print(
            f"refusing: {args.out} is not empty; use a fresh directory", file=sys.stderr
        )
        return 2
    config = load_config(args.config)
    build = build_exploration_manifest(EXPLORATION, config.symbol, args.raw)
    results = run_drills(config, build.series, build.manifest.manifest_sha256, args.out)
    summary = {
        "data_manifest_sha256": build.manifest.manifest_sha256,
        "drills": [asdict(r) for r in results],
    }
    text = json.dumps(summary, indent=2)
    (args.out / "summary.json").write_text(text + "\n", encoding="utf-8", newline="\n")
    print(text)
    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
