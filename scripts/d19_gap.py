"""Compute the C2 gap `g` and `T_C2 = 1247 - g` from the BTCUSDT
exploration partition (`calibration/gap.py`). Prints one JSON record with
the exploration manifest hash it was computed from.

  python scripts/d19_gap.py --raw-root data/raw"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "src")]  # this checkout's code only

import argparse  # noqa: E402
import json  # noqa: E402

from aqt.data.klines import EXPLORATION, build_exploration_manifest  # noqa: E402
from calibration import gap  # noqa: E402

C2_DAYS = 1247  # preregistration §3.1: T_C2 = 1247 - g


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, required=True)
    args = parser.parse_args()
    build = build_exploration_manifest(EXPLORATION, "BTCUSDT", args.raw_root)
    record = gap.gap(build.series)
    record["T_C2"] = C2_DAYS - record["g"]  # type: ignore[operator]
    record["exploration_manifest_sha256"] = build.manifest.manifest_sha256
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
