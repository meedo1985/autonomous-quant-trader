"""D-19 development choices (prereg §5 with §13 rev 7g item 3), started by
the owner's launcher after the development run, inside the pinned image.

  choose --definition PATH --store DIR --out REPORT.json

Runs the start gate, verifies every threshold and development chain of the
run definition's manifest (pass or fail only), then writes the report of
`calibration.choices.choose`: `family_block_rule`, each cell's availability
status and held-out N, `z_crit`, and the classifier thresholds of the final
qualifying cells (§3.5 item 3, for the freeze), and the coverage rule (§5
step 4, §3.2): `qualifies` needs every O18-4 category to keep a qualifying cell.
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
    chain: chunks.Chain, bounds: reduce.Bounds, joint: bool = False
) -> list[dict[str, list[choices.Rep]]]:
    """A verified development chain as replications per block rule: one
    entry, or one per family (`reduce.FAMILIES` order) of a QJ cell. Every
    record must follow from the development thresholds (I1-3)."""
    families: tuple[str | None, ...] = reduce.FAMILIES if joint else (None,)
    out: list[dict[str, list[choices.Rep]]] = [
        {rule: [] for rule in choices.RULES} for _ in families
    ]
    for rep, stored in enumerate(chunks.reduce(chain)):
        if not isinstance(stored, dict) or (
            joint and set(stored) != set(reduce.FAMILIES)
        ):
            raise ValueError(f"{chain.cell_id} rep {rep}: malformed record")
        for per, family in zip(out, families, strict=True):
            record = stored if family is None else stored[family]
            if not isinstance(record, dict):
                raise ValueError(f"{chain.cell_id} rep {rep}: malformed record")
            problem = choices.consistent(record, bounds)
            if problem is not None:
                raise ValueError(f"{chain.cell_id} rep {rep} {family}: {problem}")
            for rule in choices.RULES:
                r = record[rule]
                per[rule].append(
                    choices.Rep(r["reason"], _float(r["z"]), record["u_g"])
                )
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
        gating = rundef.start_gate(defn, ROOT)
        chains = {
            (ns, c.cell_id): _chain(defn, args.store, ns, c, gating)
            for ns in ("threshold", "dev")
            for c in cells
        }
        heads = {f"{ns}/{c}": chunks.verify(chain) for (ns, c), chain in chains.items()}
        # Per unit: a cell, or one family of a QJ cell ("<cell>/<family>";
        # cell ids never hold "/").
        bounds: dict[str, reduce.Bounds] = {}
        units: dict[str, Cell] = {}
        joint: dict[str, tuple[str, str]] = {}
        for c in cells:
            sets = reduce.cell_thresholds(
                chains["threshold", c.cell_id], c.law == "semi-joint"
            )
            names = [c.cell_id]
            if c.law == "semi-joint":
                names = [f"{c.cell_id}/{f}" for f in reduce.FAMILIES]
                joint[c.cell_id] = (names[0], names[1])
            bounds.update(zip(names, sets, strict=True))
            units.update(dict.fromkeys(names, c))
        pooled = reduce.pooled(list(bounds.values()))
        dev: dict[str, dict[str, list[choices.Rep]]] = {}
        for c in cells:
            per = development(
                chains["dev", c.cell_id],
                reduce.for_k(pooled[c.t], c.k),
                c.law == "semi-joint",
            )
            names = list(joint.get(c.cell_id, (c.cell_id,)))
            dev.update(zip(names, per, strict=True))
    except (ValueError, RuntimeError) as error:  # ChainError is a RuntimeError
        print(error, file=sys.stderr)
        return 1
    report = choices.choose(
        dev, choices.enumerated_tests([c.law for c in cells]), joint
    )
    final = [
        bounds[c]
        for c, r in report["cells"].items()  # type: ignore[attr-defined]
        if r["status"] == "qualifying"
    ]
    report["final_thresholds"] = {
        f"T={t}": {"upper": up, "lower": lo}
        for t, (up, lo) in sorted(reduce.pooled(final).items())
    }
    covered = choices.coverage(
        {u: (c.law, c.dependence, c.k) for u, c in units.items()},
        {c for c, r in report["cells"].items() if r["status"] == "qualifying"},  # type: ignore[attr-defined]
    )
    report["coverage"] = covered
    report["qualifies"] = bool(report["qualifies_before_coverage"]) and all(
        covered.values()
    )
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
