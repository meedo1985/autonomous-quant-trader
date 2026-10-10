"""D-19 run driver (prereg §13 rev 7g item 6), started by the owner's
launcher on the calibration machine inside the pinned image.

  run --definition PATH --store DIR --namespace threshold
      One hash-chained chain per cell of the run definition's manifest, in
      worker processes. Every worker runs the start gate itself before any
      chunk (R3-3) and builds its chain only from the run-definition hash and
      the gating the gate returns (FE-5); host provenance is recorded, never
      compared. Restarting resumes: finished chunks are verified and kept.
      The replication count comes from the run definition's plan (DR-3),
      seeds from prereg §8: namespace d19-threshold-v1, anchor = the
      preregistration hash recorded in the definition (DR-1).

Only the threshold namespace is built: each replication is the classifier
diagnostics of one generator draw. Development and held-out need the
tau/z_crit selection and the qualification object and are refused here.

The launcher must take AQT_IMAGE_DIGEST from `docker inspect` on the host
(FE-4) and run this under `nice 19` with a systemd `MemoryMax` of 2.5 GB.
To stop a run, stop the whole service (its control group), never the parent
process alone: an orphaned worker keeps its chain's lock and computes on, and
a relaunch is refused for that chain until it ends (FA-3, FR-5).
Synthetic data only.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"  # method V pinned runtime (VS1-4)
os.environ["OPENBLAS_CORETYPE"] = "Haswell"
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]  # this checkout's code only (RR-2)
# No cached bytecode is read or written, in this process and in every worker,
# which re-runs these lines when it imports this script (R6-1).
sys.dont_write_bytecode = True
sys.pycache_prefix = tempfile.mkdtemp(prefix="d19-no-bytecode-")

import argparse  # noqa: E402
import multiprocessing  # noqa: E402
import struct  # noqa: E402
from concurrent.futures import FIRST_EXCEPTION, ProcessPoolExecutor, wait  # noqa: E402
from typing import Any  # noqa: E402

from calibration import chunks, classifier, rundef  # noqa: E402
from calibration.generator import Cell, cells_from_manifest, generate  # noqa: E402
from calibration.seeds import outer_seed, stream  # noqa: E402

NAMESPACES = rundef.SEED_NAMESPACES  # prereg §8
WORKERS = 2  # §13 rev 7g item 6: two workers, not a run-time choice (DR5-1)


def _exact(values: dict[str, float]) -> dict[str, str]:
    """Each value as its IEEE-754 binary64 bit pattern (big-endian hex):
    every NaN payload and signed zero kept (DR-4)."""
    return {n: struct.pack(">d", v).hex() for n, v in sorted(values.items())}


def threshold_replication(cell: Cell, anchor: str, rep: int) -> dict[str, str]:
    """One threshold-run draw: the classifier diagnostics, bit-exact."""
    seed = outer_seed(anchor, cell.cell_id, NAMESPACES["threshold"], rep)
    legs = generate(cell, stream(seed, "market"), stream(seed, "columns"))
    return _exact(classifier.diagnostics(legs.x))


def worker(
    definition: Path, store: Path, namespace: str, cell_id: str, expected: str
) -> str:
    """One chain, in its own process: the start gate first, then the chunks
    (R3-3, FE-5). Returns the chain head."""
    defn = rundef.load(definition)
    if rundef.definition_sha256(defn) != expected:  # DR4-1
        raise ValueError("the run definition changed after the run started")
    gating = rundef.start_gate(defn, ROOT)
    manifest = defn["cell_manifest"]
    cells = {c.cell_id: c for c in cells_from_manifest(manifest)}
    replications = rundef.run_plan(manifest)[namespace]
    if defn["seed_spec"] != rundef.seed_spec(defn["prereg_sha256"]):
        raise ValueError("seed specification is not the §8 one (DR2-2)")
    cell, anchor = cells[cell_id], defn["seed_spec"]["anchor"]
    chain = chunks.Chain(
        store / namespace / cell_id,
        binding=rundef.definition_sha256(defn),
        namespace=namespace,
        cell_id=cell_id,
        replications=replications,
        gating=gating,
        host=rundef.host_provenance(),
    )
    return chunks.run(chain, lambda rep: threshold_replication(cell, anchor, rep))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="D-19 run driver")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--definition", type=Path, required=True)
    run.add_argument("--store", type=Path, required=True)
    run.add_argument("--namespace", required=True)
    args = parser.parse_args(argv)
    if args.namespace not in NAMESPACES:
        print(f"namespace {args.namespace!r} is not built", file=sys.stderr)
        return 1
    defn = rundef.load(args.definition)
    try:
        cells = cells_from_manifest(defn["cell_manifest"])  # DR-2
        rundef.run_plan(defn["cell_manifest"])  # DR-3
        rundef.start_gate(defn, ROOT)  # fail fast; every worker checks again
    except (ValueError, RuntimeError) as error:
        print(error, file=sys.stderr)
        return 1
    expected = rundef.definition_sha256(defn)  # every worker must load this
    jobs: list[tuple[Any, ...]] = [
        (args.definition, args.store, args.namespace, c.cell_id, expected)
        for c in cells
    ]
    # A worker that dies (killed, out of memory) breaks the executor, which
    # then fails every pending job instead of waiting for it (DR3-1). The
    # first failure in any chain stops the run at once: running workers are
    # terminated, never left computing to the end of their chain (FA-5).
    context = multiprocessing.get_context("spawn")
    others = set(multiprocessing.active_children())  # never terminated (FR-2)
    pool = ProcessPoolExecutor(WORKERS, mp_context=context)
    try:
        futures = [pool.submit(worker, *job) for job in jobs]
        done, _ = wait(futures, return_when=FIRST_EXCEPTION)
        for future in futures:
            if future in done and (failure := future.exception()) is not None:
                raise failure
        heads = [future.result() for future in futures]
    except BaseException as error:  # noqa: BLE001 - any failure stops the run
        for child in set(multiprocessing.active_children()) - others:
            child.terminate()  # the pool's workers, also on Ctrl-C (FR-3)
        if not isinstance(error, Exception):
            raise
        print(f"run stopped: {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    finally:
        pool.shutdown(cancel_futures=True)
    for job, head in zip(jobs, heads, strict=True):
        print(f"{job[2]}/{job[3]}: {head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
