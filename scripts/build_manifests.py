"""Build exploration partition manifests from downloaded archives (Task 14).

Usage:
    python scripts/build_manifests.py --raw data/raw --out data/processed/manifests

For each symbol, writes `<out>/exploration-<SYMBOL>-1h.json` (the canonical
manifest) and `<out>/exploration-<SYMBOL>-1h.build.json` (how it was built:
missing archives, gap count, bars trimmed to the window). Output is write-once:
an identical rebuild is a no-op, a different one is refused. Only the
exploration partition can be built; the manifest hash is not bound anywhere.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from aqt.data.binance_public import ALLOWED_SYMBOLS
from aqt.data.klines import EXPLORATION, KlineError, build_exploration_manifest
from aqt.data.manifest import PROTOCOL_PARTITIONS, canonical_json_bytes


def _write_once(path: Path, content: bytes) -> None:
    if path.exists():
        if path.read_bytes() != content:
            raise KlineError(f"refusing to replace a different existing file: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(content)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--partition", choices=PROTOCOL_PARTITIONS, default=EXPLORATION)
    parser.add_argument("--symbol", choices=ALLOWED_SYMBOLS, action="append")
    args = parser.parse_args(argv)
    if args.partition != EXPLORATION:
        print(
            f"refused: only the {EXPLORATION!r} partition can be built "
            f"(requested {args.partition!r})",
            file=sys.stderr,
        )
        return 2

    for symbol in args.symbol or ALLOWED_SYMBOLS:
        build = build_exploration_manifest(EXPLORATION, symbol, args.raw)
        stem = f"{EXPLORATION}-{symbol}-1h"
        _write_once(
            args.out / f"{stem}.json", canonical_json_bytes(build.manifest.as_mapping())
        )
        _write_once(
            args.out / f"{stem}.build.json", canonical_json_bytes(build.report())
        )
        report = build.report()
        print(
            f"{symbol}: {report['bar_count']} bars, {report['gap_count']} gaps "
            f"({report['gap_hours']} h), {len(build.missing_archives)} missing "
            f"archives, manifest {build.manifest.manifest_sha256}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
