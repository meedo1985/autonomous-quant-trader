"""Sandbox exploration job log and the 250-job review trigger (roadmap Task 17).

`protocols/protocol_v1.yaml` `partitions.sandbox_exploration_policy`: "all jobs
logged; human review triggered after 250 jobs". Every exploration job run
through `run_logged` is appended to a hash-chained `aqt.core.ledger` file
before it runs, so a job that later fails is still counted.

Job numbers are not stored. A job's number is its position among the cycle's
job entries in the ledger's sequence order, which the ledger's cross-process
lock makes unique, so two concurrent writers cannot both claim job 250.

The review flag
---------------
The flag is raised once a cycle has `REVIEW_TRIGGER_JOBS` jobs beyond the last
human clearance. Nothing in this module can clear it: a clearance exists only
as a human-written file committed to the repository at
`review/exploration-review/<cycle_id>.md`, read from the `HEAD` commit (an
uncommitted or unstaged file does not count). Each line of the form
`Cleared through job: <n>` clears the jobs up to `n`; the highest one counts.
The coding AI must never write that file (Constitution section 4).
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from aqt.core.ledger import append_entry, read_entries, verify_ledger
from aqt.data.bars import BarSeries
from aqt.data.manifest import PartitionManifest
from aqt.research.harness import HarnessConfig, HarnessResult, run_exploration

__all__ = [
    "JOB_RECORD_TYPE",
    "RESULT_RECORD_TYPE",
    "REVIEW_TRIGGER_JOBS",
    "JobLogError",
    "ReviewStatus",
    "clearance_path",
    "record_job",
    "review_status",
    "run_logged",
]

REVIEW_TRIGGER_JOBS: Final[int] = 250
JOB_RECORD_TYPE: Final[str] = "exploration_job"
RESULT_RECORD_TYPE: Final[str] = "exploration_job_result"
_CLEARED: Final[re.Pattern[str]] = re.compile(
    r"^Cleared through job: (\d+)\s*$", re.MULTILINE
)
_CYCLE_ID: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class JobLogError(ValueError):
    """Raised on an invalid cycle id or an unreadable clearance."""


@dataclass(frozen=True, slots=True)
class ReviewStatus:
    """How many jobs a cycle has, and whether human review is due."""

    cycle_id: str
    job_count: int
    cleared_through: int
    review_required: bool


def _require_cycle_id(cycle_id: str) -> str:
    if not isinstance(cycle_id, str) or not _CYCLE_ID.fullmatch(cycle_id):
        raise JobLogError(f"invalid cycle id {cycle_id!r}")
    return cycle_id


def clearance_path(cycle_id: str) -> str:
    """Repository-relative path of the human clearance record for a cycle."""
    return f"review/exploration-review/{_require_cycle_id(cycle_id)}.md"


def _cleared_through(repo_root: Path, cycle_id: str) -> int:
    """The highest job number cleared in the committed clearance record."""
    try:
        shown = subprocess.run(
            ["git", "-C", str(repo_root), "show", f"HEAD:{clearance_path(cycle_id)}"],
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise JobLogError(f"cannot run git to read the clearance: {error}") from None
    if shown.returncode != 0:
        return 0
    try:
        text = shown.stdout.decode("utf-8")
    except UnicodeDecodeError as error:
        raise JobLogError(
            f"clearance {clearance_path(cycle_id)} is not UTF-8 text: {error}"
        ) from None
    return max((int(n) for n in _CLEARED.findall(text)), default=0)


def _job_count(log_path: Path, cycle_id: str) -> int:
    if not log_path.exists():
        return 0
    verify_ledger(log_path).require_intact()
    return sum(
        1
        for entry in read_entries(log_path)
        if entry.record_type == JOB_RECORD_TYPE
        and entry.payload["cycle_id"] == cycle_id
    )


def review_status(log_path: Path, cycle_id: str, repo_root: Path) -> ReviewStatus:
    """Count the cycle's jobs and compare them with the committed clearance.

    Raises `LedgerError` if the log fails verification, and `JobLogError` if
    the clearance cannot be read or clears jobs that do not exist yet (a typo,
    or the cycle continuing in a different log file).
    """
    _require_cycle_id(cycle_id)
    # The clearance is read before the count: jobs only grow, so a clearance
    # read first can exceed a count taken after it only if it is really
    # beyond the log, never because a job was appended in between.
    cleared = _cleared_through(repo_root, cycle_id)
    count = _job_count(log_path, cycle_id)
    if cleared > count:
        raise JobLogError(
            f"clearance for {cycle_id!r} covers job {cleared}, beyond the "
            f"{count} jobs in {log_path}"
        )
    return ReviewStatus(
        cycle_id=cycle_id,
        job_count=count,
        cleared_through=cleared,
        review_required=count - cleared >= REVIEW_TRIGGER_JOBS,
    )


def record_job(
    log_path: Path, cycle_id: str, manifest: PartitionManifest, config: HarnessConfig
) -> int:
    """Append one job entry and return the ledger sequence it was given."""
    entry = append_entry(
        log_path,
        record_type=JOB_RECORD_TYPE,
        payload={
            "benchmark": config.benchmark.value,
            "cycle_id": _require_cycle_id(cycle_id),
            "manifest_sha256": manifest.manifest_sha256,
            "partition": manifest.partition,
            "stress_multiplier": float(config.stress_multiplier).hex(),
            "symbol": manifest.symbol,
        },
    )
    return entry.sequence


def run_logged(
    log_path: Path,
    cycle_id: str,
    repo_root: Path,
    manifest: PartitionManifest,
    load: Callable[[PartitionManifest], BarSeries],
    config: HarnessConfig,
) -> tuple[HarnessResult, ReviewStatus]:
    """Log the job, run it, log its result digest, and report review status.

    On failure the original exception is re-raised with the review status
    added as a note, so a failed job that makes review due still reports it.

    The status is checked first, so an unreadable or invalid clearance stops
    the job before anything is logged or run. The job is then logged before it
    runs. A due review is reported, not enforced: the policy says review is
    triggered, not that exploration stops.
    """
    review_status(log_path, cycle_id, repo_root)
    sequences: list[int] = []

    def log_job(logged: PartitionManifest, logged_config: HarnessConfig) -> None:
        sequences.append(record_job(log_path, cycle_id, logged, logged_config))

    try:
        result = run_exploration(manifest, load, config, log_job=log_job)
    except BaseException as error:
        # The job was logged, and may be the one that makes review due; say
        # so on the original failure rather than losing it.
        try:
            note = (
                f"exploration job log: {review_status(log_path, cycle_id, repo_root)!r}"
            )
        except Exception as status_error:  # noqa: BLE001 - keep the original error
            note = f"exploration job log: review status unavailable: {status_error}"
        error.add_note(note)
        raise
    append_entry(
        log_path,
        record_type=RESULT_RECORD_TYPE,
        payload={
            "cycle_id": cycle_id,
            "job_sequence": sequences[0],
            "result_digest": result.digest(),
        },
    )
    return result, review_status(log_path, cycle_id, repo_root)
