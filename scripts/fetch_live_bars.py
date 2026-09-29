"""Append Binance's latest closed 1h bars to the live bar store (roadmap 2,
Task 26).

Usage:
    python scripts/fetch_live_bars.py --store data/live/BTCUSDT-1h.jsonl
        [--start 2026-09-29T00:00:00Z]   # only for an empty store

Reads only Binance's public market-data API, with no credential; refuses to
run while any Binance key variable is set. Run by the owner or by the app on
its own machine, never by the AI (owner answer Q-A). Exit 0 on success, 2 on
a refusal.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from aqt.data.binance_public import DownloadError, refuse_credentials, urllib_transport
from aqt.data.live_bars import LiveBarError, LiveBarStore, fetch_new_bars

MAX_SKEW = timedelta(seconds=5)
"""Owner setting S-5: clock skew above 5 s is a breach."""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--store", type=Path, required=True)
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--start", type=datetime.fromisoformat, default=None)
    args = parser.parse_args(argv)
    try:
        refuse_credentials(os.environ)
        result = fetch_new_bars(
            urllib_transport,
            LiveBarStore(args.store),
            args.symbol,
            datetime.now(UTC),
            MAX_SKEW,
            args.start,
        )
    except (DownloadError, LiveBarError) as error:
        print(f"refused: {error}", file=sys.stderr)
        return 2
    last = result.last_open_time.isoformat() if result.last_open_time else "none"
    print(f"appended {result.appended} bars; last {last}; skew {result.skew}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
