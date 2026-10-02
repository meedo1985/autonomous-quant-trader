"""Which code may run on the server (roadmap 2 Task 30; owner answer Q30-2).

The owner approves one commit at a time in a hash-chained ledger kept outside
the checkout, where the app's account can read but not write it. A run on the
server starts only if the checkout is exactly the newest approved commit: the
commit is on `main` (as last fetched), nothing is modified, untracked or
masked anywhere in the checkout, no ignored file (such as bytecode) sits
among the code that runs (S30-2), and `src/aqt` matches its committed bytes
(`aqt.core.code_identity`). On the server the checkout, its history and its
interpreter belong to root, so the app's account can change none of them
(S30-1, S30-3; deploy/RUNBOOK.md). Approving records the owner's name and
statement; like the gap record (Q27-3) it is checked every time but is not
a cryptographic signature: the file's permissions protect it.
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Final

from aqt.core.code_identity import CodeIdentityError, SourceBundle, git_source_bundle
from aqt.core.ledger import LedgerError, append_entry, read_entries, verify_ledger

__all__ = ["APPROVED", "MAIN", "DeploymentError", "approve", "approved_code"]

APPROVED: Final[str] = "aqt.deployment.approved.v1"
MAIN: Final[str] = "origin/main"
_COMMIT: Final = re.compile(r"[0-9a-f]{40}")


class DeploymentError(RuntimeError):
    """The checkout may not run, or an approval is malformed."""


def approve(
    record: Path, *, commit: str, approved_by: str, statement: str, at: datetime
) -> None:
    """Append the owner's approval of `commit` (a full 40-character id)."""
    if not _COMMIT.fullmatch(commit):
        raise DeploymentError("give the full 40-character commit id")
    if not (approved_by.strip() and statement.strip()):
        raise DeploymentError("an approval needs the owner's name and statement")
    append_entry(
        record,
        record_type=APPROVED,
        payload={"approved_by": approved_by, "commit": commit, "statement": statement},
        recorded_at_utc=at,
    )


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        ("git", "-C", str(root), *arguments),
        capture_output=True,
        text=True,
        check=False,
    )


def approved_code(record: Path, root: Path) -> SourceBundle:
    """The checkout's source identity, if it may run; else `DeploymentError`."""
    try:
        verify_ledger(record).require_intact()
        entries = read_entries(record)
    except (LedgerError, OSError) as error:
        raise DeploymentError(f"deployment record unreadable: {error}") from None
    if not entries or entries[-1].record_type != APPROVED:
        raise DeploymentError("no approved commit in the deployment record")
    approved = str(entries[-1].payload.get("commit", ""))
    try:
        source = git_source_bundle(root)  # HEAD; src/aqt exactly as committed
    except CodeIdentityError as error:
        raise DeploymentError(str(error)) from None
    if source.commit != approved:
        raise DeploymentError(
            f"checkout is {source.commit}, the approved commit is {approved}"
        )
    if _git(root, "merge-base", "--is-ancestor", approved, MAIN).returncode:
        raise DeploymentError(f"{approved} is not on {MAIN}")
    status = _git(root, "status", "--porcelain", "--untracked-files=all")
    masked = [
        line
        for line in _git(root, "ls-files", "-v").stdout.splitlines()
        if line[:1] in {"h", "s", "S"}
    ]
    ignored = _git(
        root, "ls-files", "--others", "--ignored", "--exclude-standard",
        "--", "src", "scripts", "configs",
    ).stdout.splitlines()  # fmt: skip
    if status.returncode or status.stdout.strip() or masked or ignored:
        changed = (status.stdout.strip().splitlines() + masked + ignored)[:5]
        raise DeploymentError(f"checkout differs from its commit: {changed}")
    return source
