"""Committed-source identity for the `aqt` package.

Constitution section 18 requires that any backtester change produce a new
hash, and `protocols/protocol_v1.yaml` `cycle_start_bindings` refuses to run a
trial until an accepted code hash is bound. This module computes that identity
from committed Git blob bytes rather than from the working checkout, so the
hash does not move when `core.autocrlf` rewrites line endings on checkout.

The bundle covers every committed blob under `src/aqt`, so a new module cannot
be silently excluded, and the builder refuses a dirty or untracked covered path
rather than hashing a tree that nobody can reproduce from the commit.

The environment fingerprint is recorded beside the source hash and is
deliberately not folded into it: the same source must keep the same identity on
a different interpreter build, while the interpreter and library versions stay
on the record for reproduction.

Like `aqt.data.manifest`, this module records identities only. It does not
accept a hash and does not bind a cycle.
"""

from __future__ import annotations

import hashlib
import platform
import subprocess
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Final

from aqt.core.paths import REPOSITORY_ROOT
from aqt.data.manifest import canonical_hash

__all__ = [
    "COVERED_PREFIX",
    "PROJECT_DISTRIBUTION",
    "PYPROJECT_PATH",
    "CodeIdentity",
    "CodeIdentityError",
    "EnvironmentFingerprint",
    "SourceBundle",
    "SourceFile",
    "code_identity",
    "environment_fingerprint",
    "git_source_bundle",
]

COVERED_PREFIX: Final[str] = "src/aqt/"
"""Every committed blob under this prefix is part of the source bundle."""

PYPROJECT_PATH: Final[str] = "pyproject.toml"
PROJECT_DISTRIBUTION: Final[str] = "autonomous-quant-trader"

_REGULAR_FILE_MODES: Final[frozenset[str]] = frozenset({"100644", "100755"})
_UNKNOWN: Final[str] = "UNAVAILABLE"


class CodeIdentityError(RuntimeError):
    """Raised when committed source identity cannot be established."""


def _git(repository_root: Path, *arguments: str) -> bytes:
    completed = subprocess.run(  # noqa: S603 - fixed argv, no shell
        ("git", "-C", str(repository_root), *arguments),
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise CodeIdentityError(
            f"git {' '.join(arguments)} failed with exit {completed.returncode}: "
            f"{detail}"
        )
    return completed.stdout


@dataclass(frozen=True, slots=True)
class SourceFile:
    """One committed blob, identified by Git object id and content SHA-256."""

    path: str
    blob_id: str
    sha256: str
    byte_count: int

    def as_mapping(self) -> dict[str, object]:
        return {
            "blob_id": self.blob_id,
            "byte_count": self.byte_count,
            "path": self.path,
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class SourceBundle:
    """The committed `src/aqt` tree at one commit."""

    commit: str
    covered_prefix: str
    files: tuple[SourceFile, ...]
    source_sha256: str

    def content_mapping(self) -> dict[str, object]:
        """The mapping the source hash covers: committed content only.

        The commit id is deliberately excluded. Constitution section 18 ties a
        new hash to a code change, so an unrelated commit that touches nothing
        under `src/aqt` must not move the identity of the same source tree.
        """
        return {
            "bundle_type": "aqt.source_bundle.v1",
            "covered_prefix": self.covered_prefix,
            "file_count": len(self.files),
            "files": [item.as_mapping() for item in self.files],
        }

    def as_mapping(self) -> dict[str, object]:
        return {
            **self.content_mapping(),
            "commit": self.commit,
            "source_sha256": self.source_sha256,
        }


@dataclass(frozen=True, slots=True)
class EnvironmentFingerprint:
    """Interpreter and dependency versions recorded beside the source hash."""

    pyproject_sha256: str
    python_version: str
    python_implementation: str
    numpy_version: str
    project_version: str
    environment_sha256: str

    def as_mapping(self) -> dict[str, object]:
        return {
            "environment_sha256": self.environment_sha256,
            "fingerprint_type": "aqt.environment_fingerprint.v1",
            "numpy_version": self.numpy_version,
            "project_version": self.project_version,
            "pyproject_sha256": self.pyproject_sha256,
            "python_implementation": self.python_implementation,
            "python_version": self.python_version,
        }


@dataclass(frozen=True, slots=True)
class CodeIdentity:
    """A source bundle plus the environment it was observed in."""

    source: SourceBundle
    environment: EnvironmentFingerprint

    @property
    def source_sha256(self) -> str:
        """The committed-source hash, free of any environment detail."""
        return self.source.source_sha256

    def as_mapping(self) -> dict[str, object]:
        return {
            "environment": self.environment.as_mapping(),
            "identity_type": "aqt.code_identity.v1",
            "source": self.source.as_mapping(),
        }


def _require_clean(repository_root: Path) -> None:
    """Refuse dirty or untracked paths under the covered prefix."""
    status = _git(
        repository_root,
        "status",
        "--porcelain",
        "--untracked-files=all",
        "--",
        COVERED_PREFIX.rstrip("/"),
    ).decode("utf-8", "replace")
    entries = [line for line in status.splitlines() if line.strip()]
    if entries:
        raise CodeIdentityError(
            f"working tree is not clean under {COVERED_PREFIX}; refusing to record "
            "a code identity that cannot be reproduced from the commit: "
            + "; ".join(sorted(entries))
        )

    masked = []
    for line in (
        _git(repository_root, "ls-files", "-v", "--", COVERED_PREFIX.rstrip("/"))
        .decode("utf-8", "replace")
        .splitlines()
    ):
        if line and line[0] in {"h", "s", "S"}:
            masked.append(line)
    if masked:
        raise CodeIdentityError(
            "covered paths use assume-unchanged or skip-worktree: " + "; ".join(masked)
        )

    ignored = (
        _git(
            repository_root,
            "ls-files",
            "--others",
            "--ignored",
            "--exclude-standard",
            "-z",
            "--",
            COVERED_PREFIX.rstrip("/"),
        )
        .decode("utf-8", "replace")
        .split("\0")
    )
    unsafe_ignored = [
        path
        for path in ignored
        if path and not ("/__pycache__/" in path and path.endswith(".pyc"))
    ]
    if unsafe_ignored:
        raise CodeIdentityError(
            "ignored untracked files exist under the covered prefix: "
            + "; ".join(sorted(unsafe_ignored))
        )


def _blob_sha256(repository_root: Path, blob_id: str) -> tuple[str, int]:
    content = _git(repository_root, "cat-file", "blob", blob_id)
    return hashlib.sha256(content).hexdigest(), len(content)


def _tree_entries(
    repository_root: Path, commit: str, path: str
) -> list[tuple[str, str, str]]:
    """Return `(mode, blob_id, path)` for every blob under `path`."""
    raw = _git(repository_root, "ls-tree", "-r", "-z", commit, "--", path)
    entries: list[tuple[str, str, str]] = []
    for record in raw.decode("utf-8").split("\0"):
        if not record:
            continue
        meta, _, entry_path = record.partition("\t")
        mode, object_type, blob_id = meta.split(" ")
        if object_type != "blob":
            raise CodeIdentityError(
                f"{entry_path} is a {object_type}, which the source bundle does "
                "not cover"
            )
        if mode not in _REGULAR_FILE_MODES:
            raise CodeIdentityError(
                f"{entry_path} has unsupported mode {mode}; the source bundle "
                "covers regular files only"
            )
        entries.append((mode, blob_id, entry_path))
    return entries


def git_source_bundle(repository_root: Path = REPOSITORY_ROOT) -> SourceBundle:
    """Hash every committed blob under `src/aqt` at `HEAD`.

    Raises `CodeIdentityError` when any covered path is modified, staged, or
    untracked, because the resulting hash would not be reproducible from the
    recorded commit.
    """
    root = Path(repository_root)
    commit = _git(root, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
    _require_clean(root)

    files: list[SourceFile] = []
    for _mode, blob_id, path in _tree_entries(root, commit, COVERED_PREFIX.rstrip("/")):
        working_blob = _git(root, "hash-object", "--path", path, path).decode().strip()
        if working_blob != blob_id:
            raise CodeIdentityError(
                f"working content for {path} differs from committed blob {blob_id}"
            )
        digest, byte_count = _blob_sha256(root, blob_id)
        files.append(
            SourceFile(path=path, blob_id=blob_id, sha256=digest, byte_count=byte_count)
        )
    if not files:
        raise CodeIdentityError(
            f"commit {commit} has no committed files under {COVERED_PREFIX}"
        )
    ordered = tuple(sorted(files, key=lambda item: item.path))

    draft = SourceBundle(
        commit=commit,
        covered_prefix=COVERED_PREFIX,
        files=ordered,
        source_sha256="",
    )
    digest = canonical_hash(draft.content_mapping(), self_field=None)
    return SourceBundle(
        commit=commit,
        covered_prefix=COVERED_PREFIX,
        files=ordered,
        source_sha256=digest,
    )


def _distribution_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return _UNKNOWN


def environment_fingerprint(
    repository_root: Path = REPOSITORY_ROOT, *, commit: str = "HEAD"
) -> EnvironmentFingerprint:
    """Record the committed `pyproject.toml` hash and runtime versions."""
    root = Path(repository_root)
    entries = _tree_entries(root, commit, PYPROJECT_PATH)
    if len(entries) != 1:
        raise CodeIdentityError(
            f"expected exactly one committed {PYPROJECT_PATH}, found {len(entries)}"
        )
    pyproject_sha256, _ = _blob_sha256(root, entries[0][1])

    draft = EnvironmentFingerprint(
        pyproject_sha256=pyproject_sha256,
        python_version=platform.python_version(),
        python_implementation=platform.python_implementation(),
        numpy_version=_distribution_version("numpy"),
        project_version=_distribution_version(PROJECT_DISTRIBUTION),
        environment_sha256="",
    )
    digest = canonical_hash(draft.as_mapping(), self_field="environment_sha256")
    return EnvironmentFingerprint(
        pyproject_sha256=draft.pyproject_sha256,
        python_version=draft.python_version,
        python_implementation=draft.python_implementation,
        numpy_version=draft.numpy_version,
        project_version=draft.project_version,
        environment_sha256=digest,
    )


def code_identity(repository_root: Path = REPOSITORY_ROOT) -> CodeIdentity:
    """Return the committed-source bundle and its environment fingerprint."""
    source = git_source_bundle(repository_root)
    return CodeIdentity(
        source=source,
        environment=environment_fingerprint(repository_root, commit=source.commit),
    )
