"""Test the Telegram alert channel, and acknowledge a test (roadmap 2 Task 28).

Usage, on the app's computer, by the owner:
    python scripts/alert_channel.py test        send a test with a fresh code
    python scripts/alert_channel.py ack 123456  confirm the code you received
    python scripts/alert_channel.py status      is the channel tested?

The bot token and chat id are read from the Windows Credential Manager entry
`aqt-telegram` (user name: chat id; password: token; owner setting D-8).
This script never prints them. To store them once, in a Windows terminal:
    cmdkey /generic:aqt-telegram /user:<chat id> /pass
(`/pass` with no value asks for the token, so it stays out of the shell
history.) Tests are recorded in `--ledger`. A test
must be acknowledged at least every 7 days (D-2), or a run that uses the
channel refuses to start. Exit code 0 on success, 2 otherwise.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from aqt.core.ledger import LedgerError
from aqt.monitoring.alerts import StreamSink
from aqt.monitoring.events import Severity
from aqt.monitoring.telegram import DEFAULT_LEDGER, ChannelError, owner_channel


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("test")
    ack = commands.add_parser("ack")
    ack.add_argument("code")
    commands.add_parser("status")
    args = parser.parse_args(argv)
    try:
        _, tests = owner_channel(
            args.ledger, [StreamSink(sys.stderr, Severity.CRITICAL)]
        )
        if args.command == "test":
            tests.send_test()
            print("Test sent. Type the code from Telegram: alert_channel.py ack <code>")
        elif args.command == "ack":
            sent = tests.acknowledge(args.code)
            print(f"Acknowledged the test sent at {sent:%Y-%m-%d %H:%M}Z.")
        problem = tests.problem()
    except (ChannelError, LedgerError) as error:
        print(f"Refused: {error}", file=sys.stderr)
        return 2
    print(problem or "Channel tested within the last 7 days.")
    return 2 if problem and args.command == "status" else 0


if __name__ == "__main__":
    raise SystemExit(main())
