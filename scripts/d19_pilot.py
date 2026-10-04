"""D-19 measured pilot (prereg rev 6 §10): time one outer replication per
pilot cell, accelerated (bit-identical) and pure-Python reference paths, and
extrapolate the full run.

Synthetic data only; produces timings, never a calibration result.

Usage: python scripts/d19_pilot.py [--reps N] [--reference-sample N]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")  # method V pinned runtime
os.environ.setdefault("OPENBLAS_CORETYPE", "Haswell")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # the top-level `calibration` package

from calibration import dsr, fast, gates  # noqa: E402
from calibration.classifier import diagnostics  # noqa: E402
from calibration.generator import Cell, generate  # noqa: E402
from calibration.seeds import family_seed, outer_seed, stream  # noqa: E402

PREREG = "e1e4e7e8c01954912d0dad7f30a8a90308d96d6f"  # accepted rev 6 commit
CELLS = [
    Cell("pilot-largest", 80, 1247, "gaussian", "factor"),
    Cell("pilot-median", 20, 730, "garch", "equi0.9"),
    Cell("pilot-small", 2, 365, "ar0.5", "near_duplicates"),
    Cell("pilot-k1", 1, 1247, "t5", "independent"),
]
REPS_PER_CELL = 42_000  # 22,000 development + 20,000 held-out (prereg §5-§6)


def one(cell: Cell, rep: int, numerics: str) -> dict[str, float | str]:
    seed = outer_seed(PREREG, cell.cell_id, "d19-pilot-v1", rep)
    t0 = time.perf_counter()
    legs = generate(cell, stream(seed, "market"), stream(seed, "columns"))
    t1 = time.perf_counter()
    fam = family_seed(seed, cell.cell_id, "agnostic", cell.k, PREREG, rep)
    lengths: list[float] = []

    def classify(x, ls):  # time the diagnostics; accept (thresholds not fitted)
        lengths.extend(ls)
        diagnostics(x, ls)
        return True

    result = dsr.evaluate(
        legs.x, fam, "largest", numerics=numerics, classifier=classify
    )
    t2 = time.perf_counter()
    if result.nominee is not None:
        gates.u_g(
            legs.x,
            legs.candidates,
            legs.benchmark,
            result.nominee,
            seed,
            reference=numerics == "reference",
        )
    t3 = time.perf_counter()
    return {"generate": t1 - t0, "dsr": t2 - t1, "gates": t3 - t2, "total": t3 - t0,
            "reason": result.reason or "available"}  # fmt: skip


def main() -> int:
    fast.self_check()
    dsr.v_runtime_check()
    parser = argparse.ArgumentParser()
    parser.add_argument("--reps", type=int, default=3)
    parser.add_argument("--reference-sample", type=int, default=1)
    args = parser.parse_args()
    report = []
    for cell in CELLS:
        runs = [one(cell, r, "v") for r in range(args.reps)]
        row = {
            "cell": cell.cell_id, "K": cell.k, "T": cell.t,
            "v_s_per_rep": sum(f["total"] for f in runs) / len(runs),
            "v_parts": {p: sum(f[p] for f in runs) / len(runs)
                           for p in ("generate", "dsr", "gates")},
            "reasons": [f["reason"] for f in runs],
        }  # fmt: skip
        if args.reference_sample and cell.k <= 20:
            ex = [one(cell, r, "task12") for r in range(args.reference_sample)]
            row["task12_exact_s_per_rep"] = sum(e["total"] for e in ex) / len(ex)
        row["core_hours_full_run"] = row["v_s_per_rep"] * REPS_PER_CELL / 3600
        report.append(row)
        print(json.dumps(row), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
