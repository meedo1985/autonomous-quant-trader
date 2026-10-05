"""D-19 run driver (prereg §13 rev 7g item 6), started by the owner's
launcher on the calibration machine inside the pinned image.

  run --definition PATH --store DIR --namespace threshold --replications N
      [--workers 2]
      One hash-chained chain per cell of the run definition's manifest, in
      worker processes. Every worker runs the start gate itself before any
      chunk (R3-3) and builds its chain only from the run-definition hash and
      the gating the gate returns (FE-5); host provenance is recorded, never
      compared. Restarting resumes: finished chunks are verified and kept.

Only the threshold namespace is built: each replication is the classifier
diagnostics of one generator draw. Development and held-out need the
tau/z_crit selection and the qualification object and are refused here.

The launcher must take AQT_IMAGE_DIGEST from `docker inspect` on the host
(FE-4) and run this under `nice 19` with a systemd `MemoryMax` of 2.5 GB.
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
from typing import Any  # noqa: E402

from calibration import chunks, classifier, rundef  # noqa: E402
from calibration.generator import Cell, generate  # noqa: E402
from calibration.seeds import outer_seed, stream  # noqa: E402

NAMESPACES = ("threshold",)


def _exact(values: dict[str, float]) -> dict[str, str]:
    return {name: value.hex() for name, value in sorted(values.items())}


def threshold_replication(cell: Cell, anchor: str, rep: int) -> dict[str, str]:
    """One threshold-run draw: the classifier diagnostics, bit-exact."""
    seed = outer_seed(anchor, cell.cell_id, "threshold", rep)
    legs = generate(cell, stream(seed, "market"), stream(seed, "columns"))
    return _exact(classifier.diagnostics(legs.x))


def worker(
    definition: Path, store: Path, namespace: str, cell_id: str, replications: int
) -> str:
    """One chain, in its own process: the start gate first, then the chunks
    (R3-3, FE-5). Returns the chain head."""
    defn = rundef.load(definition)
    gating = rundef.start_gate(defn, ROOT)
    cells = {c["cell_id"]: Cell(**c) for c in defn["cell_manifest"]["cells"]}
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
    run.add_argument("--replications", type=int, required=True)
    run.add_argument("--workers", type=int, default=2)
    args = parser.parse_args(argv)
    if args.namespace not in NAMESPACES:
        print(f"namespace {args.namespace!r} is not built", file=sys.stderr)
        return 1
    defn = rundef.load(args.definition)
    try:
        rundef.start_gate(defn, ROOT)  # fail fast; every worker checks again
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1
    jobs: list[tuple[Any, ...]] = [
        (args.definition, args.store, args.namespace, c["cell_id"], args.replications)
        for c in defn["cell_manifest"]["cells"]
    ]
    context = multiprocessing.get_context("spawn")
    with context.Pool(args.workers) as pool:
        heads = pool.starmap(worker, jobs)
    for job, head in zip(jobs, heads, strict=True):
        print(f"{job[2]}/{job[3]}: {head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
