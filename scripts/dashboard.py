"""Build the read-only dashboard page, or check its sandbox (Task 33).

Run on the server by the systemd unit `aqt-dashboard@.service`
(deploy/dashboard/), never by hand as root:
    dashboard.py build   write /var/lib/aqt-dashboard/page/index.html
    dashboard.py check   the sandbox checks of DASHBOARD_PROPOSAL.md section 4
Exit code 0 on success, 2 otherwise.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

from aqt.dashboard import BARS, INCIDENTS, REPORTS, build, sandbox_check

DATA = Path("/var/lib/aqt/data")
DEPLOYMENTS = Path("/etc/aqt/deployments.jsonl")
OUT = Path("/var/lib/aqt-dashboard")


def main(argv: list[str]) -> int:
    if argv == ["build"]:
        print(f"wrote {build(DATA, DEPLOYMENTS, OUT, datetime.now(UTC))}")
        return 0
    if argv == ["check"]:
        results = sandbox_check(
            [DATA / REPORTS, DATA / BARS, DATA / INCIDENTS, DEPLOYMENTS],
            [Path("/var/lib/aqt"), Path("/etc/aqt"), Path("/opt")],
            Path("/etc/aqt/telegram"),
        )
        for name, held in results:
            print(f"{'PASS' if held else 'FAIL'} {name}")
        return 0 if all(held for _, held in results) else 2
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
