"""D-19 declared-strategy screen (prereg §7.2), inside the pinned image.

  run --trials FILE --trial-code DIR --raw-root DIR --w0 ISO --window-days N
      --window-id STR --g-days N --out RECORD.json
      [--object DIR --posted SHA | --pilot] [--workers N]

`--trials` is a JSON list of trial declarations; `--trial-code` the
directory holding their signal and overlay modules (put on `sys.path`). A
real screen needs the posted qualification object (DR-6); `--pilot` runs the
prereg §10 measurement without it and marks the record `measurement_only`
(DR-7). Exit 0 for a VALID record, 2 for INVALID. Everything else is
`calibration/screen.py` (bound by its bytes); this script only parses
arguments.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[1]),
    str(Path(__file__).resolve().parents[1] / "src"),
]

from calibration import screen  # noqa: E402
from calibration.seeds import cj, sha  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="D-19 declared-strategy screen")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--trials", type=Path, required=True)
    run.add_argument("--trial-code", type=Path, required=True)
    run.add_argument("--raw-root", type=Path, required=True)
    run.add_argument("--w0", required=True)
    run.add_argument("--window-days", type=int, required=True)
    run.add_argument("--window-id", required=True)
    run.add_argument("--g-days", type=int, required=True)
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--workers", type=int, default=2)
    mode = run.add_mutually_exclusive_group(required=True)
    mode.add_argument("--pilot", action="store_true")
    mode.add_argument("--object", type=Path)
    run.add_argument("--posted")
    args = parser.parse_args(argv)
    if args.out.exists():
        parser.error(f"{args.out} exists; a record is never overwritten")
    if args.object is not None:
        if not args.posted:
            parser.error("--object needs --posted")
        screen.check_object(
            args.object, args.posted, Path(__file__).resolve().parents[1]
        )
    sys.path.insert(0, str(args.trial_code.resolve()))
    trials = json.loads(args.trials.read_bytes())
    record = screen.run_screen(
        trials,
        screen.load_hourly_source(args.raw_root),
        datetime.fromisoformat(args.w0),
        args.window_days * 24,
        args.window_id,
        args.g_days,
        workers=args.workers,
        pilot=args.pilot,
        code_dir=args.trial_code,
    )
    args.out.write_bytes(cj(record))
    print(record["outcome"], sha(record))
    return 0 if record["outcome"] == "VALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
