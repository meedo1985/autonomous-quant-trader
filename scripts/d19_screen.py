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
      frozen reference vectors first (DR-6). Exit 0 VALID, 2 INVALID.

`--trials` is a JSON list of trial declarations; `--trial-code` the
directory of their signal and overlay modules (searched last, DR-8). A record
is never overwritten. All logic is `calibration/screen.py` (bound by its
bytes); this script only parses arguments.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from calibration import screen  # noqa: E402
from calibration.seeds import cj, sha  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="D-19 declared-strategy screen")
    sub = parser.add_subparsers(dest="command", required=True)
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
    trials = json.loads(args.trials.read_bytes())
    if args.command == "pilot" and len(trials) != screen.MAX_TRIALS:
        parser.error(f"the pilot screens a {screen.MAX_TRIALS}-trial set (prereg §10)")
    code = args.trial_code.resolve()
    out = args.out.open("xb")  # S7-R8, S7R-R4: reserved before any work
    reserved = os.fstat(out.fileno())
    try:
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
                trials,
                args.raw_root,
                args.object,
                args.posted,
                ROOT,
                args.workers,
                code,
            )
        out.write(cj(record))
        out.close()
    except BaseException:
        out.close()
        try:  # S7R2-R1: remove the path only if it is still this run's file
            now = os.stat(args.out)
            if (now.st_dev, now.st_ino) == (reserved.st_dev, reserved.st_ino):
                args.out.unlink()
        except FileNotFoundError:
            pass
        raise
    if args.command == "pilot":
        print("MEASUREMENT", sha(record))
        return 0
    print(record["outcome"], sha(record))
    return 0 if record["outcome"] == "VALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
