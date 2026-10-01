"""Append Binance's latest closed 1h bars to the live bar store (roadmap 2,
Task 26).

Usage:
    python scripts/fetch_live_bars.py --store data/live/BTCUSDT-1h.jsonl
        [--start 2026-09-29T00:00:00Z]   # only for an empty store

After a real Binance gap (the fetch stores the bars before it and is refused
with "gap ... where FIRST_MISSING is next"), the owner may sign a gap record
instead of fetching (owner answer Q27-3): from FIRST_MISSING, which must be
the hour the store expects, until RESUMES_AT, the first hour Binance has
again. No request is made, and the missing hours are never filled:
    python scripts/fetch_live_bars.py --store data/live/BTCUSDT-1h.jsonl
        --acknowledge-gap 2026-10-02T02:00:00Z 2026-10-02T05:00:00Z
        --actor NAME --statement "Binance has no bars for these hours (link)"

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
    parser.add_argument(
        "--acknowledge-gap",
        type=datetime.fromisoformat,
        nargs=2,
        default=None,
        metavar=("FIRST_MISSING", "RESUMES_AT"),
        help="sign a gap record for these hours; nothing is fetched",
    )
    parser.add_argument("--actor", default="")
    parser.add_argument("--statement", default="")
    args = parser.parse_args(argv)
    try:
        refuse_credentials(os.environ)
        if args.acknowledge_gap is not None:
            first_missing, resumes_at = args.acknowledge_gap
            gap = LiveBarStore(args.store, args.symbol).acknowledge_gap(
                first_missing,
                resumes_at,
                args.actor,
                args.statement,
                datetime.now(UTC),
            )
            print(
                f"gap recorded: {gap.first_missing.isoformat()} until "
                f"{gap.resumes_at.isoformat()}, signed by {gap.actor}"
            )
            return 0
        result = fetch_new_bars(
            urllib_transport,
            LiveBarStore(args.store, args.symbol),
            args.symbol,
            datetime.now(UTC),
            MAX_SKEW,
            args.start,
        )
    except (DownloadError, LiveBarError, OSError) as error:
        # OSError covers network failures and timeouts (F26-4).
        print(f"refused: {error}", file=sys.stderr)
        return 2
    last = result.last_open_time.isoformat() if result.last_open_time else "none"
    print(f"appended {result.appended} bars; last {last}; skew {result.skew}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
