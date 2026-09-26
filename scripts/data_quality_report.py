"""Write the exploration data quality and outage report (Task 15).

Usage:
    python scripts/data_quality_report.py --raw data/raw \
        --manifests data/processed/manifests \
        --out review/task15/DATA_QUALITY_REPORT.md

The report is derived from the raw archives and refused unless each rebuilt
manifest is byte-identical to the manifest Task 14 wrote, so it always
describes the recorded manifest. The report file is write-once:
an identical rerun is a no-op, a different one is refused.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from aqt.data.binance_public import ALLOWED_SYMBOLS
from aqt.data.klines import EXPLORATION
from aqt.data.quality import QualityReportError, render_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--manifests", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    recorded = {
        symbol: (args.manifests / f"{EXPLORATION}-{symbol}-1h.json").read_bytes()
        for symbol in ALLOWED_SYMBOLS
    }
    content = render_report(args.raw, recorded).encode("utf-8")
    if args.out.exists():
        # A committed copy may have been checked out with CRLF line endings.
        if args.out.read_bytes().replace(b"\r\n", b"\n") != content:
            raise QualityReportError(f"refusing to replace a different {args.out}")
        print(f"unchanged: {args.out}")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("xb") as handle:
        handle.write(content)
    print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
