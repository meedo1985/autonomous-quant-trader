"""D-19 chunk store (prereg §13 rev 7g item 6): an interrupted and resumed
chain is byte-identical to a clean one; integrity failures stop the chain.
Synthetic data only."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from calibration import chunks
from calibration.chunks import Chain, ChainError
from calibration.generator import Cell, generate
from calibration.seeds import outer_seed, stream

CELL = Cell("test-cell", 2, 60, "garch", "equi0.5")


def _compute(rep: int) -> list[float]:
    seed = outer_seed("0" * 64, CELL.cell_id, "dev", rep)
    legs = generate(CELL, stream(seed, "market"), stream(seed, "columns"))
    return [float(v) for v in legs.x.mean(axis=0)]


def _chain(root: Path, **changes: object) -> Chain:
    chain = Chain(
        root / "dev" / CELL.cell_id,
        binding="b" * 64,
        namespace="dev",
        cell_id=CELL.cell_id,
        replications=23,
        gating={"image": "sha256:x", "numpy": "2"},
        host={"cpu": "A"},
        size=5,
    )
    return replace(chain, **changes)  # type: ignore[arg-type]


def _bytes(chain: Chain) -> dict[str, bytes]:
    return {p.name: p.read_bytes() for p in sorted(chain.root.iterdir())}


def test_an_interrupted_and_resumed_chain_is_byte_identical(tmp_path: Path) -> None:
    clean = _chain(tmp_path / "clean")
    head = chunks.run(clean, _compute)
    resumed = _chain(tmp_path / "resumed")
    calls = 0

    def dies_at_rep_12(rep: int) -> list[float]:
        nonlocal calls
        calls += 1
        if rep == 12:
            raise KeyboardInterrupt
        return _compute(rep)

    with pytest.raises(KeyboardInterrupt):
        chunks.run(resumed, dies_at_rep_12)
    assert len(_bytes(resumed)) == 2  # chunks 0 and 5 finished, 10 never written
    assert chunks.run(resumed, _compute) == head
    assert _bytes(resumed) == _bytes(clean)
    assert list(chunks.reduce(resumed)) == [_compute(r) for r in range(23)]


def test_a_corrupt_or_unfinished_chunk_is_recomputed(tmp_path: Path) -> None:
    chain = _chain(tmp_path)
    head = chunks.run(chain, _compute)
    clean = _bytes(chain)
    chain.path(5).write_bytes(clean["chunk-0000005.json"][:-9])  # torn
    (chain.root / "chunk-0000010.tmp").write_bytes(b"partial")
    with pytest.raises(ChainError):
        chunks.verify(chain)
    assert chunks.run(chain, lambda rep: _compute(rep)) == head
    assert _bytes(chain) == clean


def test_a_host_change_alone_keeps_the_chain(tmp_path: Path) -> None:
    chain = _chain(tmp_path)
    head = chunks.run(chain, _compute)
    chain.path(5).unlink()
    chain.path(10).unlink()
    chain.path(15).unlink()
    chain.path(20).unlink()
    moved = replace(chain, host={"cpu": "B"})
    assert chunks.run(moved, _compute) == head
    assert b'"cpu":"B"' in moved.path(20).read_bytes()  # recorded, not compared


def test_a_gap_before_a_later_chunk_stops_the_chain(tmp_path: Path) -> None:
    chain = _chain(tmp_path)
    chunks.run(chain, _compute)
    chain.path(5).unlink()
    with pytest.raises(ChainError, match="missing before a later chunk"):
        chunks.run(chain, _compute)


@pytest.mark.parametrize(
    "changes",
    [
        {"gating": {"image": "sha256:y", "numpy": "2"}},
        {"binding": "c" * 64},
    ],
)
def test_a_chunk_from_another_run_or_runtime_stops_the_chain(
    tmp_path: Path, changes: dict[str, object]
) -> None:
    chunks.run(_chain(tmp_path), _compute)
    with pytest.raises(ChainError):
        chunks.run(_chain(tmp_path, **changes), _compute)


def test_a_foreign_or_out_of_range_file_stops_the_chain(tmp_path: Path) -> None:
    chain = _chain(tmp_path)
    chunks.run(chain, _compute)
    chain.path(5).rename(chain.root / "chunk-0000006.json")
    with pytest.raises(ChainError, match="not a chunk of this chain"):
        chunks.run(chain, _compute)


def test_a_relinked_chunk_breaks_the_chain(tmp_path: Path) -> None:
    """A self-consistent chunk spliced in from another chain position."""
    chain = _chain(tmp_path)
    chunks.run(chain, _compute)
    other = _chain(tmp_path / "other", replications=30)
    chunks.run(other, lambda rep: _compute(rep + 1))
    chain.path(10).write_bytes(other.path(10).read_bytes())
    with pytest.raises(ChainError):
        chunks.verify(chain)


@pytest.mark.parametrize("name", ["chunk-0000009.json", "chunk-0000030.json"])
def test_verify_and_reduce_refuse_a_duplicated_or_out_of_range_chunk(
    tmp_path: Path, name: str
) -> None:
    """D19CR-2: final verification checks the directory too, read-only."""
    chain = _chain(tmp_path)
    chunks.run(chain, _compute)
    (chain.root / name).write_bytes(chain.path(0).read_bytes())
    with pytest.raises(ChainError, match="not a chunk of this chain"):
        chunks.verify(chain)
    with pytest.raises(ChainError, match="not a chunk of this chain"):
        list(chunks.reduce(chain))
    assert (chain.root / name).exists()  # verification deletes nothing


def test_verify_refuses_an_unfinished_temporary_without_deleting_it(
    tmp_path: Path,
) -> None:
    chain = _chain(tmp_path)
    chunks.run(chain, _compute)
    tmp = chain.root / "chunk-0000010.tmp"
    tmp.write_bytes(b"partial")
    with pytest.raises(ChainError):
        chunks.verify(chain)
    assert tmp.exists()


def test_a_second_writer_on_a_chain_is_refused(tmp_path: Path) -> None:
    """FA-3: while one writer holds a chain, another is refused; the lock
    is released when the first is done."""
    chain = _chain(tmp_path)
    chain.root.mkdir(parents=True)
    with chunks._sole_writer(chain):
        with pytest.raises(ChainError, match="another writer"):
            chunks.run(chain, _compute)
    chunks.run(chain, _compute)


def test_a_lock_never_collides_with_another_cells_chain(tmp_path: Path) -> None:
    """FR-1: `x` and `x.lock` are both valid cell ids."""
    for cell_id in ("pilot-a", "pilot-a.lock"):
        chain = replace(
            _chain(tmp_path), root=tmp_path / "dev" / cell_id, cell_id=cell_id
        )
        chunks.run(chain, _compute)
        chunks.verify(chain)


def test_the_head_is_read_back_from_disk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """FA-4: bytes that differ on disk from what was computed stop the run
    instead of returning a head nothing on disk supports."""
    write = chunks._write

    def torn(path: Path, record: dict[str, object]) -> None:
        write(path, record)
        if path.name == "chunk-0000010.json":
            path.write_bytes(path.read_bytes()[:-9])

    monkeypatch.setattr(chunks, "_write", torn)
    with pytest.raises(ChainError, match="missing or corrupt"):
        chunks.run(_chain(tmp_path), _compute)
