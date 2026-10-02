"""Approve the commit the server may run, and check a checkout (roadmap 2 Task 30).

Usage, on the server, by the owner (see deploy/RUNBOOK.md):
    sudo python scripts/deployment.py approve <commit> --by "Name" --statement "..."
    python scripts/deployment.py check     may this checkout run?

`--record` is the deployment record (default /etc/aqt/deployments.jsonl),
writable by root only. Exit code 0 on success, 2 otherwise.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from aqt.core.deployment import DeploymentError, approve, approved_code
from aqt.core.ledger import LedgerError

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--record", type=Path, default=Path("/etc/aqt/deployments.jsonl")
    )
    commands = parser.add_subparsers(dest="command", required=True)
    approving = commands.add_parser("approve")
    approving.add_argument("commit")
    approving.add_argument("--by", required=True)
    approving.add_argument("--statement", required=True)
    commands.add_parser("check")
    args = parser.parse_args(argv)
    try:
        if args.command == "approve":
            approve(
                args.record,
                commit=args.commit,
                approved_by=args.by,
                statement=args.statement,
                at=datetime.now(UTC),
            )
            print(f"Approved {args.commit}.")
        else:
            source = approved_code(args.record, REPOSITORY_ROOT)
            print(f"May run: {source.commit}, source {source.source_sha256}.")
    except (DeploymentError, LedgerError, OSError) as error:
        print(f"Refused: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
