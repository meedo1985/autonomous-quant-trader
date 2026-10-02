"""Roadmap 2 Task 30: only the owner's approved commit runs on the server.
Every repository here is a throwaway one; the real tree is never judged."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from aqt.core.deployment import DeploymentError, approve, approved_code
from aqt.monitoring.telegram import ChannelError, read_file_credential
from tests.integration.test_paper_loop import _config, _run, _series

NOW = datetime(2026, 10, 2, 12, tzinfo=UTC)


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ("git", "-C", str(root), "-c", "user.email=t@example.invalid",
         "-c", "user.name=t", "-c", "commit.gpgsign=false", *arguments),
        check=True, capture_output=True, text=True,
    ).stdout.strip()  # fmt: skip


def _commit(root: Path, path: str, text: str) -> str:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8", newline="\n")
    _git(root, "add", "--all")
    _git(root, "commit", "--quiet", "-m", path)
    return _git(root, "rev-parse", "HEAD")


@pytest.fixture
def server(tmp_path: Path) -> tuple[Path, Path, str]:
    """A checkout on `main` as fetched, and a record approving its commit."""
    root = tmp_path / "app"
    root.mkdir()
    _git(root, "init", "--quiet")
    _commit(root, "pyproject.toml", '[project]\nname = "x"\n')
    _commit(root, "scripts/run.py", "RUN = 1\n")
    head = _commit(root, "src/aqt/__init__.py", "")
    _git(root, "update-ref", "refs/remotes/origin/main", head)
    record = tmp_path / "deployments.jsonl"
    approve(record, commit=head, approved_by="Owner", statement="ok", at=NOW)
    return root, record, head


def test_the_approved_commit_may_run(server: tuple[Path, Path, str]) -> None:
    root, record, head = server
    assert approved_code(record, root).commit == head


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        (lambda r: (r / "scripts/run.py").write_text("RUN = 2\n"), "differs"),
        (lambda r: (r / "scripts/new.py").write_text(""), "differs"),
        (lambda r: (r / "src/aqt/__init__.py").write_text("X = 1\n"), "src/aqt"),
        (
            lambda r: (
                _git(r, "update-index", "--skip-worktree", "scripts/run.py"),
                (r / "scripts/run.py").write_text("RUN = 3\n"),
            ),
            "differs",
        ),
    ],
)
def test_a_modified_checkout_refuses(
    server: tuple[Path, Path, str], change: object, reason: str
) -> None:
    """Acceptance: a modified, added or masked file refuses the start."""
    root, record, _ = server
    change(root)  # type: ignore[operator]
    with pytest.raises(DeploymentError, match=reason):
        approved_code(record, root)


def test_only_the_newest_approval_counts(server: tuple[Path, Path, str]) -> None:
    root, record, head = server
    newer = _commit(root, "scripts/run.py", "RUN = 4\n")
    _git(root, "update-ref", "refs/remotes/origin/main", newer)
    _git(root, "checkout", "--quiet", head)
    approve(record, commit=newer, approved_by="Owner", statement="ok", at=NOW)
    with pytest.raises(DeploymentError, match="approved commit is " + newer):
        approved_code(record, root)


def test_a_commit_not_on_main_refuses(server: tuple[Path, Path, str]) -> None:
    root, record, _ = server
    local = _commit(root, "scripts/run.py", "RUN = 5\n")
    approve(record, commit=local, approved_by="Owner", statement="ok", at=NOW)
    with pytest.raises(DeploymentError, match="not on origin/main"):
        approved_code(record, root)


def test_a_missing_or_damaged_record_refuses(
    server: tuple[Path, Path, str], tmp_path: Path
) -> None:
    root, record, _ = server
    with pytest.raises(DeploymentError, match="no approved commit"):
        approved_code(tmp_path / "none.jsonl", root)
    record.write_text(record.read_text().replace("Owner", "Other"))
    with pytest.raises(DeploymentError, match="unreadable"):
        approved_code(record, root)


@pytest.mark.parametrize(
    ("commit", "by"), [("abc123", "Owner"), ("a" * 40, " "), ("A" * 40, "Owner")]
)
def test_an_approval_needs_a_full_commit_and_a_name(
    tmp_path: Path, commit: str, by: str
) -> None:
    with pytest.raises(DeploymentError):
        approve(
            tmp_path / "r.jsonl", commit=commit, approved_by=by, statement="ok", at=NOW
        )
    assert not (tmp_path / "r.jsonl").exists()


def test_the_loop_refuses_an_unapproved_checkout(tmp_path: Path) -> None:
    record = tmp_path / "deployments.jsonl"
    approve(record, commit="0" * 40, approved_by="Owner", statement="ok", at=NOW)
    report = _run(tmp_path / "run", _config(1), _series(24 * 12), deployment=record)
    assert report.final_mode == "REFUSED" and report.orders_sent == 0
    assert any(r.startswith("deployment: ") for r in report.refused)


def test_the_start_event_names_the_approved_code(
    server: tuple[Path, Path, str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The loop's own tree is not a clean approved checkout while tests run,
    so the check is given the throwaway server's answer."""
    root, record, head = server
    source = approved_code(record, root)
    monkeypatch.setattr("aqt.app.paper_loop.approved_code", lambda *_: source)
    report = _run(tmp_path / "run", _config(1), _series(24 * 12), deployment=record)
    assert report.refused == ()
    log = (tmp_path / "run" / "operations.jsonl").read_text()
    assert head in log and source.source_sha256 in log


@pytest.mark.skipif(sys.platform == "win32", reason="the server's credential file")
@pytest.mark.parametrize(
    ("mode", "text", "error"),
    [
        (0o600, "42\n123:abc\n", None),
        (0o640, "42\n123:abc\n", "this account only"),
        (0o600, "42\n", "chat id and the token"),
    ],
)
def test_the_server_credential_file(
    tmp_path: Path, mode: int, text: str, error: str | None
) -> None:
    """T28-06: on Linux the credential is a file only the app's account reads."""
    path = tmp_path / "telegram"
    path.write_text(text)
    os.chmod(path, mode)
    if error is None:
        credential = read_file_credential(path)
        assert (credential.chat_id, credential.token) == ("42", "123:abc")
    else:
        with pytest.raises(ChannelError, match=error) as caught:
            read_file_credential(path)
        assert "123:abc" not in str(caught.value)
