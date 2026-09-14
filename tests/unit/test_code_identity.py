"""Committed-source identity tests against synthetic throwaway Git repos.

No real market data and no network access. Every repository used here is
created inside pytest's temporary directory, so the checks never depend on,
or disturb, the state of the working repository.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from aqt.core.code_identity import (
    COVERED_PREFIX,
    CodeIdentityError,
    code_identity,
    environment_fingerprint,
    git_source_bundle,
)

_PYPROJECT = '[project]\nname = "autonomous-quant-trader"\nversion = "0.1.0"\n'


def _git(root: Path, *arguments: str) -> None:
    subprocess.run(
        (
            "git",
            "-C",
            str(root),
            "-c",
            "user.email=tests@example.invalid",
            "-c",
            "user.name=tests",
            "-c",
            "commit.gpgsign=false",
            *arguments,
        ),
        check=True,
        capture_output=True,
    )


def _write(root: Path, relative: str, text: str) -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A committed repository with a small `src/aqt` tree."""
    _git(tmp_path, "init", "--quiet")
    _write(tmp_path, "pyproject.toml", _PYPROJECT)
    _write(tmp_path, "src/aqt/__init__.py", "")
    _write(tmp_path, "src/aqt/core/__init__.py", "")
    _write(tmp_path, "src/aqt/core/version.py", '__version__ = "0.1.0"\n')
    _write(tmp_path, "src/aqt/data/bars.py", "BAR = 1\n")
    _write(tmp_path, "README.md", "outside the covered prefix\n")
    _git(tmp_path, "add", "--all")
    _git(tmp_path, "commit", "--quiet", "-m", "initial")
    return tmp_path


def test_bundle_covers_every_tracked_file_under_the_prefix(repo: Path) -> None:
    bundle = git_source_bundle(repo)
    assert [item.path for item in bundle.files] == [
        "src/aqt/__init__.py",
        "src/aqt/core/__init__.py",
        "src/aqt/core/version.py",
        "src/aqt/data/bars.py",
    ]
    assert bundle.covered_prefix == COVERED_PREFIX
    assert len(bundle.commit) == 40


def test_bundle_hashes_committed_blob_bytes(repo: Path) -> None:
    bundle = git_source_bundle(repo)
    entry = next(item for item in bundle.files if item.path == "src/aqt/data/bars.py")
    assert entry.sha256 == hashlib.sha256(b"BAR = 1\n").hexdigest()
    assert entry.byte_count == len(b"BAR = 1\n")


def test_bundle_hash_is_stable_across_checkout_line_endings(repo: Path) -> None:
    expected = git_source_bundle(repo).source_sha256
    # Simulate a CRLF checkout of a covered file, then restore the LF bytes
    # Git actually stored. Only the committed blob may drive the identity.
    (repo / "src/aqt/data/bars.py").write_bytes(b"BAR = 1\r\n")
    with pytest.raises(CodeIdentityError, match="not clean"):
        git_source_bundle(repo)
    _git(repo, "checkout", "--", "src/aqt/data/bars.py")
    assert git_source_bundle(repo).source_sha256 == expected


def test_bundle_hash_changes_when_a_covered_file_changes(repo: Path) -> None:
    before = git_source_bundle(repo).source_sha256
    _write(repo, "src/aqt/data/bars.py", "BAR = 2\n")
    _git(repo, "add", "--all")
    _git(repo, "commit", "--quiet", "-m", "change")
    assert git_source_bundle(repo).source_sha256 != before


def test_bundle_hash_changes_when_a_new_module_is_added(repo: Path) -> None:
    before = git_source_bundle(repo).source_sha256
    _write(repo, "src/aqt/data/manifest.py", "MANIFEST = 1\n")
    _git(repo, "add", "--all")
    _git(repo, "commit", "--quiet", "-m", "add module")
    assert git_source_bundle(repo).source_sha256 != before


def test_bundle_ignores_changes_outside_the_covered_prefix(repo: Path) -> None:
    before = git_source_bundle(repo)
    _write(repo, "README.md", "still outside\n")
    _git(repo, "add", "--all")
    _git(repo, "commit", "--quiet", "-m", "docs")
    after = git_source_bundle(repo)
    assert after.source_sha256 == before.source_sha256
    assert after.commit != before.commit
    assert "commit" not in before.content_mapping()


def test_builder_refuses_a_dirty_covered_file(repo: Path) -> None:
    _write(repo, "src/aqt/core/version.py", '__version__ = "9.9.9"\n')
    with pytest.raises(CodeIdentityError, match="not clean"):
        git_source_bundle(repo)


def test_builder_refuses_a_staged_but_uncommitted_covered_file(repo: Path) -> None:
    _write(repo, "src/aqt/core/version.py", '__version__ = "9.9.9"\n')
    _git(repo, "add", "--all")
    with pytest.raises(CodeIdentityError, match="not clean"):
        git_source_bundle(repo)


def test_builder_refuses_an_untracked_covered_file(repo: Path) -> None:
    _write(repo, "src/aqt/models/linear.py", "MODEL = 1\n")
    with pytest.raises(CodeIdentityError, match="not clean"):
        git_source_bundle(repo)


@pytest.mark.parametrize("flag", ["--assume-unchanged", "--skip-worktree"])
def test_builder_refuses_index_flags_that_mask_worktree_changes(
    repo: Path, flag: str
) -> None:
    path = "src/aqt/core/version.py"
    _git(repo, "update-index", flag, path)
    _write(repo, path, '__version__ = "9.9.9"\n')
    with pytest.raises(CodeIdentityError, match="assume-unchanged|skip-worktree"):
        git_source_bundle(repo)


def test_builder_refuses_an_ignored_source_file(repo: Path) -> None:
    exclude = repo / ".git" / "info" / "exclude"
    exclude.write_text("src/aqt/ignored.py\n", encoding="utf-8", newline="\n")
    _write(repo, "src/aqt/ignored.py", "IGNORED = True\n")
    with pytest.raises(CodeIdentityError, match="ignored untracked"):
        git_source_bundle(repo)


def test_builder_accepts_an_untracked_file_outside_the_prefix(repo: Path) -> None:
    _write(repo, "notes.md", "scratch\n")
    assert git_source_bundle(repo).source_sha256


def test_environment_fingerprint_records_details_outside_the_source_hash(
    repo: Path,
) -> None:
    fingerprint = environment_fingerprint(repo)
    assert (
        fingerprint.pyproject_sha256
        == hashlib.sha256(_PYPROJECT.encode("utf-8")).hexdigest()
    )
    assert fingerprint.python_version
    assert fingerprint.numpy_version
    assert fingerprint.project_version
    assert len(fingerprint.environment_sha256) == 64

    identity = code_identity(repo)
    assert identity.source_sha256 == git_source_bundle(repo).source_sha256
    assert fingerprint.environment_sha256 not in identity.source_sha256
    assert set(identity.source.as_mapping()).isdisjoint(
        {"python_version", "numpy_version", "environment_sha256"}
    )
