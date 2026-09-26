"""Task 17: the exploration job log and the 250-job review trigger."""

from __future__ import annotations

import ast
import multiprocessing
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from aqt.benchmarks.canonical import BenchmarkId
from aqt.core.ledger import LedgerError, read_entries, verify_ledger
from aqt.data.bars import Bar, BarSeries
from aqt.data.manifest import (
    PartitionManifest,
    RawArtifact,
    build_partition_manifest,
    unavailable,
)
from aqt.research import joblog
from aqt.research.harness import HarnessConfig
from aqt.research.joblog import (
    JOB_RECORD_TYPE,
    REVIEW_TRIGGER_JOBS,
    JobLogError,
    clearance_path,
    record_job,
    review_status,
    run_logged,
)

HOUR = timedelta(hours=1)
START = datetime(2018, 1, 1, tzinfo=UTC)
CONFIG = HarnessConfig(BenchmarkId.BUY_AND_HOLD)
SERIES = BarSeries(
    symbol="BTCUSDT",
    bars=tuple(
        Bar(
            open_time=START + index * HOUR,
            open=100.0 + index,
            high=102.0 + index,
            low=99.0 + index,
            close=101.0 + index,
            volume=1.0,
        )
        for index in range(10)
    ),
)
MANIFEST = build_partition_manifest(
    partition="exploration",
    series=SERIES,
    raw_artifacts=[RawArtifact("synthetic.zip", b"synthetic")],
    parser_code_sha256="0" * 64,
    window_start_utc=START,
    window_end_exclusive_utc=START + 10 * HOUR,
    fees=unavailable("synthetic"),
    exchange_filters=unavailable("synthetic"),
    symbol_status=unavailable("synthetic"),
)


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True,
        capture_output=True,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    (root / "README").write_text("x\n")
    _git(root, "add", "README")
    _git(root, "commit", "-q", "-m", "init")
    return root


def _log_jobs(log: Path, count: int, cycle: str = "cycle-1") -> None:
    for _ in range(count):
        record_job(log, cycle, MANIFEST, CONFIG)


@pytest.fixture(scope="module")
def full_log(tmp_path_factory: pytest.TempPathFactory) -> bytes:
    """The bytes of a log holding exactly 250 jobs of `cycle-1`, built once."""
    log = tmp_path_factory.mktemp("full") / "jobs.jsonl"
    _log_jobs(log, REVIEW_TRIGGER_JOBS)
    return log.read_bytes()


def test_job_250_raises_the_flag_and_jobs_1_to_249_do_not(
    tmp_path: Path, repo: Path, full_log: bytes
) -> None:
    lines = full_log.splitlines(keepends=True)
    assert len(lines) == REVIEW_TRIGGER_JOBS
    log = tmp_path / "jobs.jsonl"
    # Every prefix of a hash-chained log is the log as it stood after that job.
    # Each status call re-verifies the chain, so a sample of counts is checked
    # rather than all 250.
    flags = {}
    for count in (1, 2, 125, 248, 249, 250):
        log.write_bytes(b"".join(lines[:count]))
        status = review_status(log, "cycle-1", repo)
        assert status.job_count == count
        flags[count] = status.review_required
    assert flags == {1: False, 2: False, 125: False, 248: False, 249: False, 250: True}
    # Jobs of another cycle are counted separately.
    assert review_status(log, "cycle-2", repo).job_count == 0


def _commit_clearance(repo: Path, text: str) -> None:
    record = repo / clearance_path("cycle-1")
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(text)
    _git(repo, "add", clearance_path("cycle-1"))
    _git(repo, "commit", "-q", "-m", "clearance")


def test_only_a_committed_clearance_clears_the_flag(
    tmp_path: Path, repo: Path, full_log: bytes
) -> None:
    log = tmp_path / "jobs.jsonl"
    log.write_bytes(full_log)
    record = repo / clearance_path("cycle-1")
    record.parent.mkdir(parents=True)
    record.write_text("Reviewed by the owner.\nCleared through job: 250\n")
    assert review_status(log, "cycle-1", repo).review_required  # not committed
    _git(repo, "add", clearance_path("cycle-1"))
    assert review_status(log, "cycle-1", repo).review_required  # staged only
    _git(repo, "commit", "-q", "-m", "clearance")
    status = review_status(log, "cycle-1", repo)
    assert (status.cleared_through, status.review_required) == (250, False)
    # Review is due again 250 jobs after the last clearance: with job 1
    # cleared, 249 uncleared jobs do not raise it; with none cleared, 250 do.
    _commit_clearance(repo, "Cleared through job: 1\n")
    assert not review_status(log, "cycle-1", repo).review_required
    _commit_clearance(repo, "Nothing cleared.\n")
    assert review_status(log, "cycle-1", repo).review_required


def test_the_library_has_no_way_to_write_a_clearance() -> None:
    tree = ast.parse(Path(joblog.__file__).read_text(encoding="utf-8"))
    called = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute | ast.Name)
    }
    assert not called & {"open", "write_text", "write_bytes", "mkdir", "unlink"}
    # The only subprocess call is a read-only `git show`.
    git_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.List)
        and node.elts
        and isinstance(node.elts[0], ast.Constant)
        and node.elts[0].value == "git"
    ]
    assert len(git_calls) == 1
    assert "show" in [e.value for e in git_calls[0].elts if isinstance(e, ast.Constant)]


def test_the_log_is_hash_chained_and_a_mutation_fails(
    tmp_path: Path, repo: Path
) -> None:
    log = tmp_path / "jobs.jsonl"
    _log_jobs(log, 3)
    assert verify_ledger(log).intact
    lines = log.read_bytes().splitlines(keepends=True)
    lines[1] = lines[1].replace(b"BUY_AND_HOLD", b"CASH_AND_HOLD")
    log.write_bytes(b"".join(lines))
    assert not verify_ledger(log).intact
    with pytest.raises(LedgerError):
        review_status(log, "cycle-1", repo)


def test_run_logged_logs_the_job_before_the_run_and_its_result_after(
    tmp_path: Path, repo: Path
) -> None:
    log = tmp_path / "jobs.jsonl"
    result, status = run_logged(
        log, "cycle-1", repo, MANIFEST, lambda _: SERIES, CONFIG
    )
    entries = read_entries(log)
    assert [e.record_type for e in entries] == [
        JOB_RECORD_TYPE,
        "exploration_job_result",
    ]
    assert entries[1].payload["result_digest"] == result.digest()
    assert status.job_count == 1

    def fail(_: PartitionManifest) -> BarSeries:
        raise RuntimeError("load failed")

    with pytest.raises(RuntimeError):
        run_logged(log, "cycle-1", repo, MANIFEST, fail, CONFIG)
    assert review_status(log, "cycle-1", repo).job_count == 2


@pytest.mark.parametrize("cycle", ["", "../x", "a/b", "cycle 1"])
def test_unsafe_cycle_ids_are_refused(cycle: str) -> None:
    with pytest.raises(JobLogError):
        clearance_path(cycle)


def _worker(arguments: tuple[str, int]) -> None:
    path, count = arguments
    _log_jobs(Path(path), count)


def test_concurrent_writers_produce_one_valid_chain(tmp_path: Path, repo: Path) -> None:
    log = tmp_path / "jobs.jsonl"
    context = multiprocessing.get_context("spawn")
    with context.Pool(2) as pool:
        pool.map(_worker, [(str(log), 15), (str(log), 15)])
    report = verify_ledger(log)
    assert (report.intact, report.entry_count) == (True, 30)
    assert review_status(log, "cycle-1", repo).job_count == 30


def test_a_clearance_beyond_the_job_count_is_refused(
    tmp_path: Path, repo: Path
) -> None:
    """R-1: a clearance cannot cover jobs that do not exist yet."""
    log = tmp_path / "jobs.jsonl"
    _log_jobs(log, 3)
    _commit_clearance(repo, "Cleared through job: 100000\n")
    with pytest.raises(JobLogError, match="beyond"):
        review_status(log, "cycle-1", repo)


def test_an_unreadable_clearance_is_refused_before_the_job_runs(
    tmp_path: Path, repo: Path
) -> None:
    """R-3: a non-UTF-8 clearance raises JobLogError and nothing is logged."""
    record = repo / clearance_path("cycle-1")
    record.parent.mkdir(parents=True)
    record.write_bytes(b"Cleared through job: 1\n\xff\n")
    _git(repo, "add", clearance_path("cycle-1"))
    _git(repo, "commit", "-q", "-m", "clearance")
    log = tmp_path / "jobs.jsonl"
    ran: list[PartitionManifest] = []

    def load(manifest: PartitionManifest) -> BarSeries:
        ran.append(manifest)
        return SERIES

    with pytest.raises(JobLogError, match="UTF-8"):
        run_logged(log, "cycle-1", repo, MANIFEST, load, CONFIG)
    assert ran == []
    assert not log.exists()
