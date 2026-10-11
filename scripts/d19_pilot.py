"""D-19 re-pilot timing (FE-7, I1-8): per replication, the time of each
stage of a development replication, with the two Annex B block rules timed
separately, on representative grid cells at T = 1247 (the T_C2 upper bound,
so the cost is not understated).

Synthetic data only, own seed namespace (never a run's); produces timings,
never a calibration result. Run inside the calibration image:

    sudo sh d19.sh timing        (or: python scripts/d19_pilot.py --reps N)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"  # method V pinned runtime (VS1-4)
os.environ["OPENBLAS_CORETYPE"] = "Haswell"
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from calibration import dsr, gates  # noqa: E402
from calibration.classifier import diagnostics  # noqa: E402
from calibration.generator import Cell, generate  # noqa: E402
from calibration.seeds import family_seed, outer_seed, stream  # noqa: E402

ANCHOR = "d19-pilot-timing"  # never a run's anchor or namespace (FA-1)
CELLS = [
    Cell("pilot-timing-k20", 20, 1247, "garch", "equi0.9"),
    Cell("pilot-timing-k5", 5, 1247, "gaussian", "clusters"),
    Cell("pilot-timing-k2", 2, 1247, "t5", "opposites"),
]


def one(cell: Cell, rep: int) -> dict[str, float]:
    seed = outer_seed(ANCHOR, cell.cell_id, "d19-pilot-v1", rep)
    fam = family_seed(seed, cell.cell_id, "agnostic", cell.k, ANCHOR, rep)
    t = [time.perf_counter()]
    legs = generate(cell, stream(seed, "market"), stream(seed, "columns"))
    t.append(time.perf_counter())
    diagnostics(legs.x)
    t.append(time.perf_counter())
    nominee = None
    for rule in ("largest", "median"):
        result = dsr.evaluate(legs.x, fam, rule, classifier=lambda *_: True)
        nominee = nominee if nominee is not None else result.nominee
        t.append(time.perf_counter())
    gates.u_g(legs.x, legs.candidates, legs.benchmark, nominee or 0, seed)
    t.append(time.perf_counter())
    names = ("generate", "diagnostics", "dsr_largest", "dsr_median", "u_g")
    return {n: t[i + 1] - t[i] for i, n in enumerate(names)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reps", type=int, default=20)
    args = parser.parse_args()
    dsr.v_runtime_check(dsr.runtime_identity(), dsr.canaries())  # this runtime
    for cell in CELLS:
        runs = [one(cell, r) for r in range(args.reps)]
        mean = {n: sum(r[n] for r in runs) / len(runs) for n in runs[0]}
        print(json.dumps({"cell": cell.cell_id, "K": cell.k, "T": cell.t,
                          "reps": args.reps, "seconds_per_rep": mean,
                          "total": sum(mean.values())}), flush=True)  # fmt: skip
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
