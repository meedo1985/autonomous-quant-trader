"""D-19 development choices (prereg §5 with §13 rev 7g item 3), started by
the owner's launcher after the development run, inside the pinned image.

  choose --definition PATH --store DIR --out REPORT.json

Runs the start gate, verifies every threshold and development chain of the
run definition's manifest (pass or fail only), then writes the report of
`calibration.choices.choose`: `family_block_rule`, each cell's availability
status and held-out N, `z_crit`, and the classifier thresholds of the final
qualifying cells (§3.5 item 3, for the freeze). The coverage rule (§5
step 4) needs the frozen cell manifest's categories and is not applied here.
Development records only; no held-out data exists or is read.
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
sys.dont_write_bytecode = True  # R6-1
sys.pycache_prefix = tempfile.mkdtemp(prefix="d19-no-bytecode-")

import argparse  # noqa: E402
import json  # noqa: E402
from typing import Any  # noqa: E402

from calibration import choices, chunks, reduce, rundef  # noqa: E402
from calibration.generator import Cell, cells_from_manifest  # noqa: E402
from calibration.seeds import sha  # noqa: E402

TESTS_PER_AGNOSTIC_CELL = 3  # error, DSR availability, U_G (prereg §6)
# I1-4: M = 3 per cell holds only for family-agnostic cells (Q1-Q4). Any other
# law refuses here until per-family and joint tests are counted (Q5, QJ).
AGNOSTIC_LAWS = (
    "gaussian", "t5", "ar0.2", "ar0.5", "garch", "skewt+", "skewt-", "unequal",
    "mixed_ar",
)  # fmt: skip


def _chain(
    defn: dict[str, Any], store: Path, ns: str, cell: Cell, gating: object
) -> chunks.Chain:
    return chunks.Chain(
        store / ns / cell.cell_id,
        binding=rundef.definition_sha256(defn),
        namespace=ns,
        cell_id=cell.cell_id,
        replications=rundef.run_plan(defn["cell_manifest"])[ns],
        gating=gating,  # type: ignore[arg-type]
        host={},
    )


def _float(value: object) -> float | None:
    return None if value is None else reduce.decode({"v": value})["v"]


def development(
    chain: chunks.Chain, bounds: reduce.Bounds
) -> dict[str, list[choices.Rep]]:
    """A verified development chain as replications per block rule; every
    record must follow from the development thresholds (I1-3)."""
    out: dict[str, list[choices.Rep]] = {rule: [] for rule in choices.RULES}
    for rep, record in enumerate(chunks.reduce(chain)):
        if not isinstance(record, dict):
            raise ValueError(f"{chain.cell_id} rep {rep}: malformed record")
        problem = choices.consistent(record, bounds)
        if problem is not None:
            raise ValueError(f"{chain.cell_id} rep {rep}: {problem}")
        for rule in choices.RULES:
            r = record[rule]
            out[rule].append(choices.Rep(r["reason"], _float(r["z"]), record["u_g"]))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="D-19 development choices")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("choose")
    run.add_argument("--definition", type=Path, required=True)
    run.add_argument("--store", type=Path, required=True)
    run.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    defn = rundef.load(args.definition)
    try:
        cells = cells_from_manifest(defn["cell_manifest"])
        other = sorted({c.law for c in cells} - set(AGNOSTIC_LAWS))
        if other:
            raise ValueError(f"tests are not counted for laws {other} (I1-4)")
        gating = rundef.start_gate(defn, ROOT)
        chains = {
            (ns, c.cell_id): _chain(defn, args.store, ns, c, gating)
            for ns in ("threshold", "dev")
            for c in cells
        }
        heads = {f"{ns}/{c}": chunks.verify(chain) for (ns, c), chain in chains.items()}
        bounds = {
            c.cell_id: reduce.cell_thresholds(chains["threshold", c.cell_id])
            for c in cells
        }
        pooled = reduce.pooled(list(bounds.values()))
        dev = {
            c.cell_id: development(chains["dev", c.cell_id], pooled[c.k]) for c in cells
        }
    except (ValueError, RuntimeError) as error:  # ChainError is a RuntimeError
        print(error, file=sys.stderr)
        return 1
    report = choices.choose(dev, TESTS_PER_AGNOSTIC_CELL * len(cells))
    final = [
        bounds[c]
        for c, r in report["cells"].items()  # type: ignore[attr-defined]
        if r["status"] == "qualifying"
    ]
    report["final_thresholds"] = {
        str(k): {"upper": up, "lower": lo}
        for k, (up, lo) in sorted(reduce.pooled(final).items())
    }
    report["definition_sha256"] = rundef.definition_sha256(defn)
    if defn["cell_manifest"]["purpose"] == "pilot":  # I1R-5
        report["measurement_only"] = (
            "pilot run: development counts below about 7,700 per cell demote "
            "every cell by the cap rule, so these statuses, z_crit and final "
            "thresholds are not qualification decisions; read the event counts"
        )
    report["chain_heads"] = heads  # I1-3: the chains this report was made from
    report["dev_thresholds_sha256"] = sha(
        {str(k): [{n: v.hex() for n, v in side.items()} for side in b]
         for k, b in sorted(pooled.items())}
    )  # fmt: skip
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", "utf-8")
    if not report["margin_ok"]:  # I1-6, I1R-4: fail closed, the owner decides
        print(
            f"margin_failed: a target comparison is within {choices.MARGIN_MIN:g}",
            file=sys.stderr,
        )
        return 3
    print(f"z_crit {report['z_crit']}, family_block_rule {report['family_block_rule']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
