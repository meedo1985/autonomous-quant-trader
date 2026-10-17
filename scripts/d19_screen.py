"""D-19 declared-strategy screen (prereg §7.2), inside the pinned image.

  pilot   --trials FILE --trial-code DIR --raw-root DIR --out RECORD.json
          [--workers N]
      prereg §10's measurement: one screen of a 20-trial set at the C2
      window, without a qualification object. The record is
      `measurement_only` and has no outcome (DR-7). Prints MEASUREMENT.
  declare --trials FILE --trial-code DIR --raw-root DIR --out RECORD.json
          --object DIR --posted SHA [--workers N]
      the screen a declaration lists: checks the posted qualification
      object, its code, runtime, the exploration bars and the screen's
      frozen reference vectors first (DR-6). Exit 0 SCREEN_AVAILABLE, 2 INVALID.
  summary --record RECORD.json
      a measurement record's seconds per trial (total and slowest path), its
      gate results per trial, and the screen's reference vectors (S8).

`--trials` is a JSON list of trial declarations; `--trial-code` the
directory of their signal and overlay modules (searched last, DR-8). A record
is never overwritten. All logic is `calibration/screen.py` (bound by its
bytes); this script only parses arguments.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# S16S-1: the pinned runtime and no bytecode, as d19_run.py, before NumPy or
# any engine module is imported (workers re-run these lines on import)
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OPENBLAS_CORETYPE"] = "Haswell"
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
sys.dont_write_bytecode = True
sys.pycache_prefix = tempfile.mkdtemp(prefix="d19-no-bytecode-")

import argparse  # noqa: E402
import json  # noqa: E402
from typing import BinaryIO  # noqa: E402

from calibration import screen  # noqa: E402
from calibration.seeds import cj, sha  # noqa: E402


def reserve(out: Path) -> BinaryIO:
    """S7-R8, S7R-R4, S7R4-R1..R3: claim `out` exclusively before any work
    (O_CREAT | O_EXCL: fails if anything exists there, a dangling link
    included; two runs cannot both claim it). The record is written through
    this handle, never reopened by name, and nothing is ever deleted: a
    failed run leaves the empty claimed file, to be removed by hand."""
    try:
        return out.open("xb")
    except FileExistsError as e:
        raise SystemExit(f"refused: {out} exists; a record is never overwritten") from e


def summary(record: dict[str, object]) -> list[str]:
    """S8: what the cost pilot reports, one line per trial plus totals."""
    runs = record["runs"]
    assert isinstance(runs, list)
    lines = [  # S8-R3: availability, not passes; never a declaration
        "MEASUREMENT ONLY (prereg §10 pilot): gate results are availability, "
        "not passes; nothing here is a declaration outcome"
    ]
    total = 0.0
    for tid in sorted({r["trial_id"] for r in runs}):
        own = [r for r in runs if r["trial_id"] == tid]
        secs = [float(r.get("seconds", 0.0)) for r in own]
        total += sum(secs)
        results: dict[str, int] = {}
        for r in own:
            for gate, value in r["gates"].items():
                key = f"{gate}:{'available' if value is None else value}"
                results[key] = results.get(key, 0) + 1
        lines.append(
            f"{tid}: {len(own)} paths, {sum(secs):.0f} s total, "
            f"slowest {max(secs):.0f} s; "
            + ", ".join(f"{k} x{n}" for k, n in sorted(results.items()))
        )
    lines.append(
        f"all trials: {total:.0f} worker-seconds ({total / 3600:.1f} worker-hours)"
    )
    lines.append(f"availability: {record.get('availability')}")
    runtimes = {json.dumps(r.get("runtime"), sort_keys=True) for r in runs}
    lines.append(f"job runtimes (S16SR-1): {sorted(runtimes)}")
    lines.append(
        f"reference vectors: {json.dumps(record['reference_vectors'], sort_keys=True)}"
    )
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="D-19 declared-strategy screen")
    sub = parser.add_subparsers(dest="command", required=True)
    show = sub.add_parser("summary")
    show.add_argument("--record", type=Path, required=True)
    for name in ("pilot", "declare"):
        p = sub.add_parser(name)
        p.add_argument("--trials", type=Path, required=True)
        p.add_argument("--trial-code", type=Path, required=True)
        p.add_argument("--raw-root", type=Path, required=True)
        p.add_argument("--out", type=Path, required=True)
        p.add_argument("--workers", type=int, default=2)
        if name == "declare":
            p.add_argument("--object", type=Path, required=True)
            p.add_argument("--posted", required=True)
    args = parser.parse_args(argv)
    if args.command == "summary":
        print("\n".join(summary(json.loads(args.record.read_bytes()))))
        return 0
    trials = json.loads(args.trials.read_bytes())
    if args.command == "pilot" and len(trials) != screen.MAX_TRIALS:
        parser.error(f"the pilot screens a {screen.MAX_TRIALS}-trial set (prereg §10)")
    code = args.trial_code.resolve()
    out = reserve(args.out)
    if args.command == "pilot":
        record = screen.run_screen(
            trials,
            screen.load_hourly_source(args.raw_root),
            screen.C2_W0,
            screen.C2_WINDOW_DAYS * 24,
            screen.C2_WINDOW_ID,
            screen.C2_G_DAYS,
            workers=args.workers,
            code_dir=code,
        )
    else:
        record = screen.declare(
            trials, args.raw_root, args.object, args.posted, ROOT, args.workers, code
        )
    with out:
        out.write(cj(record))
    if args.command == "pilot":
        print("MEASUREMENT", sha(record))
        return 0
    print(record["outcome"], sha(record))
    return 0 if record["outcome"] == "SCREEN_AVAILABLE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
