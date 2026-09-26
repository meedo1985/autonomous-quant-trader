"""Owner-run download of Binance Spot public 1h klines (roadmap Task 13).

The coding AI never runs this: Constitution section 15 denies Cycle-1 research
network access. Only the exploration partition is fetched until the owner
answers roadmap question Q3 about confirmation and lockbox archives.

Usage:
    python scripts/download_market_data.py --root data/raw

Every run writes a new summary under `<root>/runs/` listing each artifact as
AVAILABLE with its hash or UNAVAILABLE with a reason. The exit code is 1 if
anything was unavailable, so a gap is never mistaken for success.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from aqt.data.binance_public import (
    ALLOWED_SYMBOLS,
    EXPLORATION_MONTHS,
    BinancePublicClient,
    months_between,
    urllib_transport,
)
from aqt.data.manifest import UNAVAILABLE, canonical_json_bytes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--symbol", choices=ALLOWED_SYMBOLS, action="append")
    args = parser.parse_args(argv)

    client = BinancePublicClient(urllib_transport, args.root)
    started = datetime.now(UTC)
    records = [client.fetch_exchange_info()]
    for symbol in args.symbol or ALLOWED_SYMBOLS:
        for year, month in months_between(*EXPLORATION_MONTHS):
            record = client.fetch_monthly_klines(symbol, year, month)
            print(record.availability.status, record.name, flush=True)
            records.append(record)

    summary = {
        "partition": "exploration",
        "records": [record.as_mapping() for record in records],
        "started_utc": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    runs = args.root / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    out = runs / f"download-{started:%Y%m%dT%H%M%S%fZ}.json"
    with out.open("xb") as handle:
        handle.write(canonical_json_bytes(summary))
    missing = [r.name for r in records if r.availability.status == UNAVAILABLE]
    print(f"summary: {out}; unavailable: {len(missing)}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
