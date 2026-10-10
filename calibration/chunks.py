"""Chunked, hash-chained replication store of prereg §13 rev 7g item 6.

One chain per (namespace, cell). Replications are cut into fixed chunks of
`CHUNK`; each finished chunk is one file, written to a temporary name and
renamed. A chunk records its binding hash (run definition, or qualification
object for held-out), namespace, cell, replication range, gating identity,
host provenance, results, the hash of the previous chunk and its own hash.

The content hash covers every field except `host` and itself: host
provenance is recorded and disclosed, never compared (§13 item 6), so a
chunk recomputed on another host with the same gating identity keeps the
chain intact.

Verification reads bytes and reports only pass or fail (P18-6: not access).
`results` is read only by `reduce`, which the caller invokes at the final
reduction."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from calibration.seeds import cj

CHUNK = 500
GENESIS = "0" * 64


class ChainError(RuntimeError):
    """The chain stops: missing, duplicated, out-of-range, broken-chain or
    foreign chunk, or a gating identity that differs from the run's."""


@dataclass(frozen=True, slots=True)
class Chain:
    root: Path  # <store>/<namespace>/<cell_id>
    binding: str
    namespace: str
    cell_id: str
    replications: int
    gating: Mapping[str, object]
    host: Mapping[str, object]
    size: int = CHUNK

    def path(self, start: int) -> Path:
        return self.root / f"chunk-{start:07d}.json"

    def starts(self) -> range:
        return range(0, self.replications, self.size)


def _digest(record: Mapping[str, object]) -> str:
    core = {k: v for k, v in record.items() if k not in ("host", "content_sha256")}
    return hashlib.sha256(cj(core)).hexdigest()


def _load(path: Path) -> dict[str, object] | None:
    """The chunk at `path`, or `None` when it is incomplete or corrupt."""
    try:
        record = json.loads(path.read_bytes())
    except (OSError, ValueError):
        return None
    if not isinstance(record, dict) or record.get("content_sha256") != _digest(record):
        return None
    return record


def _check(chain: Chain, record: dict[str, object], start: int, previous: str) -> str:
    stop = min(start + chain.size, chain.replications)
    expected = {
        "binding": chain.binding,
        "namespace": chain.namespace,
        "cell_id": chain.cell_id,
        "start": start,
        "stop": stop,
        "previous_sha256": previous,
    }
    for key, value in expected.items():
        if record.get(key) != value:
            raise ChainError(f"{chain.path(start).name}: {key} does not match")
    if record.get("gating") != json.loads(cj(chain.gating)):
        raise ChainError(f"{chain.path(start).name}: gating identity differs")
    results = record.get("results")
    if not isinstance(results, list) or len(results) != stop - start:
        raise ChainError(f"{chain.path(start).name}: wrong number of results")
    return str(record["content_sha256"])


def _write(path: Path, record: dict[str, object]) -> None:
    tmp = path.with_suffix(".tmp")
    with tmp.open("wb") as handle:
        handle.write(cj(record))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)
    _sync_dir(path.parent)


def _sync_dir(directory: Path) -> None:
    """Make a rename or a new entry in `directory` durable (FA-4). POSIX
    only: Windows cannot open a directory for fsync."""
    if sys.platform != "win32":
        fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


@contextmanager
def _sole_writer(chain: Chain) -> Iterator[None]:
    """An exclusive lock on `<namespace>/.locks/<cell_id>`, or ChainError
    (FA-3): a second writer (relaunch, orphaned worker) is refused. A cell id
    cannot start with a dot, so the lock never collides with a chain (FR-1).
    The lock goes with the process, so a crash leaves none."""
    locks = chain.root.parent / ".locks"
    locks.mkdir(exist_ok=True)
    with (locks / chain.cell_id).open("a+b") as handle:
        try:
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise ChainError(f"{chain.cell_id}: another writer holds it") from error
        yield


def _strays(chain: Chain, *, restart: bool) -> None:
    """Refuse files the chain does not name (duplicated or out of range).
    An unfinished temporary is deleted unread on a restart and refused by
    read-only verification (D19CR-2)."""
    names = {chain.path(s).name for s in chain.starts()}
    for entry in chain.root.iterdir():
        if entry.suffix == ".tmp" and restart:
            entry.unlink()
        elif entry.name not in names:
            raise ChainError(f"{entry.name}: not a chunk of this chain")


def run(chain: Chain, compute: Callable[[int], object]) -> str:
    """Verify the chain, compute every missing chunk with `compute(rep)` and
    return the final chain head as `verify` reads it back from disk (FA-4).
    A corrupt chunk is deleted unread and recomputed; a gap before an
    existing chunk stops the chain; one writer at a time (FA-3)."""
    created = [d for d in (chain.root, *chain.root.parents) if not d.exists()]
    chain.root.mkdir(parents=True, exist_ok=True)
    for directory in created:  # every new directory's entry is durable (FR-4)
        _sync_dir(directory.parent)
    with _sole_writer(chain):
        _compute(chain, compute)
        return verify(chain)


def _compute(chain: Chain, compute: Callable[[int], object]) -> None:
    _strays(chain, restart=True)
    existing = [s for s in chain.starts() if chain.path(s).exists()]
    last = existing[-1] if existing else -1
    previous = GENESIS
    for start in chain.starts():
        path = chain.path(start)
        record = _load(path) if path.exists() else None
        if record is None:
            if path.exists():
                path.unlink()  # corrupt or incomplete: deleted unread
            elif start < last:
                raise ChainError(f"{path.name}: missing before a later chunk")
            stop = min(start + chain.size, chain.replications)
            record = {
                "binding": chain.binding,
                "namespace": chain.namespace,
                "cell_id": chain.cell_id,
                "start": start,
                "stop": stop,
                "gating": json.loads(cj(chain.gating)),
                "host": json.loads(cj(chain.host)),
                "previous_sha256": previous,
                "results": [compute(rep) for rep in range(start, stop)],
            }
            record["content_sha256"] = _digest(record)
            _write(path, record)
        previous = _check(chain, record, start, previous)


def verify(chain: Chain) -> str:
    """The final chain head of a complete chain; pass or `ChainError`.
    Read-only."""
    _strays(chain, restart=False)
    previous = GENESIS
    for start in chain.starts():
        record = _load(chain.path(start))
        if record is None:
            raise ChainError(f"{chain.path(start).name}: missing or corrupt")
        previous = _check(chain, record, start, previous)
    return previous


def reduce(chain: Chain) -> Iterator[object]:
    """Every replication's result in replication order, after `verify`."""
    verify(chain)
    for start in chain.starts():
        record = _load(chain.path(start))
        assert record is not None and isinstance(record["results"], list)
        yield from record["results"]
