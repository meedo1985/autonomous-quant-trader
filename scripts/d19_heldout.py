"""D-19 held-out certification (prereg §6, §8; §13 rev 7g items 3 and 6),
started by the owner's launcher after the attempt's O-6a freeze read and the
publication of its drand round (§4 step 6), inside the pinned image.

  run --object DIR --posted SHA --attempt N --round R --randomness HEX
      --store DIR [--raw-root DIR]
      One hash-chained chain per final qualifying cell, bound to the posted
      `qualification_object_sha256`, `N_i` replications each (the object's
      allocation, 20k or 40k), in two worker processes. Prints chain heads
      only: no held-out event content is shown before `certify` (P18-6).
      Restarting resumes, as the driver does.
  certify --object DIR --posted SHA --attempt N --store DIR --out REPORT.json
      The final reduction: every chain must verify first; then each
      enumerated test's events, its one-sided Clopper-Pearson upper bound at
      alpha = 0.025/M and the acceptance (§6). Exit 0 accepted, 2 not.

Seeds (§8): namespace d19-heldout-v{N}; anchor = SHA256(cj({beacon_randomness,
qobj, round})); everything else as in development. A replication is the
development record (`d19_run._family_record`, both block rules) with the
window classifier at the frozen final thresholds of its `T` level (§3.5
item 3); `certify` reads the frozen `family_block_rule` and `z_crit`.

Readings (proposed, for review):
- HO-1 Code: the object's run definition names the engine commit; every
  loaded `calibration`/`aqt` module and `scripts/d19_run.py` must be that
  commit's, `calibration/mapping.py` the object's, and this file the
  object's `heldout.py` (as the mapping, MP-4); the runtime, canaries, image
  digest and reference vectors must equal the run definition's.
- HO-2 `M` is the object's test manifest (`choices.json` "m", every
  candidate cell, §5 `M_max`): the targets were computed at it. The gate
  refuses unless that manifest is `choices.test_manifest` of the whole cell
  manifest (HO-R2), and `choices.json` holds exactly one known status for
  every manifest unit (HO2-R1). Tests of demoted cells are not run and not certified;
  Bonferroni over the rest at 0.025/M stays valid. A test of a qualifying
  unit without replications is a refusal, never "not run".
- HO-3 Every chunk's binding is SHA256(cj({anchor,
  qualification_object_sha256})), so it binds the posted object and the
  attempt's anchor (HO-R1). The anchor inputs are created once, atomically,
  in `<store>/heldout-v{N}/attempt.json` and made durable (file and
  directory entries) before any worker starts (HO2-R2); `certify` rebuilds
  the binding from that record and refuses without it.
- HO-4 Not checked here, for the attempt's procedure: the drand signature,
  that the round is the first at or after T_Qn + 24h, the O-6a freeze read
  and the two DF5-2 pre-run records.

Stop a run as the driver says: the whole service, never the parent alone.
Synthetic data, and for Q5 cells exploration data only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import FIRST_EXCEPTION, ProcessPoolExecutor, wait
from pathlib import Path
from typing import Any

os.environ["OPENBLAS_NUM_THREADS"] = "1"  # method V pinned runtime (VS1-4)
os.environ["OPENBLAS_CORETYPE"] = "Haswell"
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src"), str(ROOT / "scripts")]
sys.dont_write_bytecode = True  # R6-1
sys.pycache_prefix = tempfile.mkdtemp(prefix="d19-no-bytecode-")

# d19_run first: it sets its own bytecode prefix before importing the
# engine, so every engine module is cached (never written) under one prefix.
import d19_run  # noqa: E402

from calibration import (  # noqa: E402
    binomial,
    choices,
    chunks,
    mapping,
    reduce,
    rules,
    semi,
)
from calibration.generator import SEMI_LAWS, Cell, cells_from_manifest  # noqa: E402
from calibration.rundef import canonical_sha256, host_provenance  # noqa: E402
from calibration.seeds import cj, outer_seed, sha  # noqa: E402

ATTEMPTS = (1, 2)  # §8: d19-heldout-v1, d19-heldout-v2
STATUSES = ("qualifying", "demoted_availability", "demoted_cap")  # choices
NAMES = ("choices.json", "definition.json", "freeze.json", "mapping.py", "heldout.py")


def namespace(attempt: int) -> str:
    """The seed namespace of attempt `attempt` (§8)."""
    if attempt not in ATTEMPTS:
        raise ValueError(f"attempt must be one of {ATTEMPTS}")
    return f"d19-heldout-v{attempt}"


def anchor(qobj: str, round_: int, randomness: str) -> str:
    """§8 held-out anchor."""
    if not re.fullmatch(r"[0-9a-f]{64}", randomness):
        raise ValueError("beacon randomness must be 64 lowercase hex digits")
    if type(round_) is not int or round_ < 1:
        raise ValueError("the drand round must be a positive integer")
    return sha({"beacon_randomness": randomness, "qobj": qobj, "round": round_})


def load(obj: Path, posted: str) -> dict[str, bytes]:
    """The object's files this runner reads, each checked against its
    manifest, whose hash must be the posted one. ValueError otherwise."""
    manifest = json.loads((obj / "manifest.json").read_bytes())
    if sha(manifest) != posted:
        raise ValueError("the qualification object is not the posted one")
    files = {}
    for name in NAMES:
        data = (obj / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != manifest.get(name):
            raise ValueError(f"{name} does not match the object's manifest")
        files[name] = data
    return files


def gate(
    obj: Path, posted: str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """HO-1, on every start, in every process that computes or reduces:
    returns the object's (choices, definition, freeze)."""
    files = load(obj, posted)
    report, defn, freeze = (json.loads(files[n]) for n in NAMES[:3])
    mapping.check_engine(defn, ROOT, files["mapping.py"])
    commit = defn["engine_commit"]
    try:
        driver = subprocess.run(
            ["git", "-C", str(ROOT), "show", f"{commit}:scripts/d19_run.py"],
            capture_output=True, check=True,
        ).stdout  # fmt: skip
    except subprocess.CalledProcessError as error:
        raise ValueError(f"engine commit {commit} not readable") from error
    if canonical_sha256(Path(d19_run.__file__).read_bytes()) != canonical_sha256(
        driver
    ):
        raise ValueError("the loaded scripts/d19_run.py is not the run's")
    if canonical_sha256(Path(__file__).read_bytes()) != canonical_sha256(
        files["heldout.py"]
    ):
        raise ValueError("this runner is not the object's heldout.py")
    mapping.check_runtime(defn)
    cells = cells_from_manifest(defn["cell_manifest"])
    tests = choices.test_manifest([(c.cell_id, c.law) for c in cells])
    if report["tests"] != tests or report["m"] != len(tests):
        raise ValueError("the test manifest is not the cell manifest's (HO-R2)")
    if not (report.get("qualifies") is True and report.get("margin_ok") is True):
        raise ValueError("the object's method does not qualify")
    units = {u for c in cells for u in _units(c)}
    if set(report["cells"]) != units or any(
        r.get("status") not in STATUSES for r in report["cells"].values()
    ):
        raise ValueError("choices.json needs one known status per manifest unit")
    final = {
        u: r["held_out"]
        for u, r in report["cells"].items()
        if r["status"] == "qualifying"
    }
    if freeze["allocation"] != final or set(final.values()) - set(choices.HELD_OUT):
        raise ValueError("the allocation is not the final cells' 20k/40k")
    return report, defn, freeze


def plan(
    report: dict[str, Any], defn: dict[str, Any], freeze: dict[str, Any]
) -> list[tuple[Cell, int, reduce.Bounds]]:
    """Per final qualifying cell: its `N_i` and its window classifier, the
    frozen final thresholds of its `T` level for its `K` (§3.5 item 3)."""
    allocation = freeze["allocation"]
    cells = cells_from_manifest(defn["cell_manifest"])
    if set(allocation) - {u for c in cells for u in _units(c)}:
        raise ValueError("the allocation names a unit outside the cell manifest")
    out = []
    for cell in cells:
        units = _units(cell)
        if not any(u in allocation for u in units):
            continue
        sizes = {allocation.get(u) for u in units}
        if len(sizes) != 1:
            raise ValueError(f"{cell.cell_id}: its families differ in N")
        frozen = report["final_thresholds"][f"T={cell.t}"]
        pool = tuple(
            {n: float(v) for n, v in frozen[s].items()} for s in ("upper", "lower")
        )
        out.append((cell, sizes.pop(), reduce.for_k(pool, cell.k)))  # type: ignore[arg-type]
    return out


def _units(cell: Cell) -> list[str]:
    """The cell's units as choices.json names them."""
    if cell.law == "semi-joint":
        return [f"{cell.cell_id}/{f}" for f in reduce.FAMILIES]
    return [cell.cell_id]


def binding(posted: str, anchor_: str) -> str:
    """HO-3: what every held-out chunk is bound to."""
    return sha({"anchor": anchor_, "qualification_object_sha256": posted})


def _attempt_path(store: Path, ns: str) -> Path:
    return store / ns.removeprefix("d19-") / "attempt.json"


def attempt_record(store: Path, ns: str, record: dict[str, Any]) -> None:
    """HO-3: created once, complete, by an atomic link (a concurrent start
    loses with FileExistsError); any later start must bring the same inputs."""
    path = _attempt_path(store, ns)
    created = [d for d in (path.parent, *path.parent.parents) if not d.exists()]
    path.parent.mkdir(parents=True, exist_ok=True)
    for directory in created:  # every new directory entry is durable (HO2-R2)
        chunks._sync_dir(directory.parent)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".attempt-")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(cj(record))
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(tmp, path)
        except FileExistsError:
            if path.read_bytes() != cj(record):
                raise ValueError(
                    f"{path}: another attempt's inputs are recorded"
                ) from None
    finally:
        os.unlink(tmp)
    chunks._sync_dir(path.parent)  # the record's link, before any chunk (HO2-R2)


def recorded_anchor(store: Path, ns: str, posted: str) -> str:
    """The attempt's anchor from its record, recomputed from the recorded
    beacon inputs and the posted object (HO-3). ValueError otherwise."""
    path = _attempt_path(store, ns)
    if not path.is_file():
        raise ValueError(f"{path}: no attempt record")
    record = json.loads(path.read_bytes())
    key = anchor(posted, record.get("round"), record.get("beacon_randomness", ""))
    expected = {"anchor": key, "beacon_randomness": record["beacon_randomness"],
                "qobj": posted, "round": record["round"]}  # fmt: skip
    if path.read_bytes() != cj(expected):
        raise ValueError(f"{path}: not this object's attempt record")
    return key


def replication(
    cell: Cell,
    anchor_: str,
    ns: str,
    prereg: str,
    rep: int,
    bounds: reduce.Bounds,
    source: semi.Source | None = None,
) -> dict[str, Any]:
    """One held-out replication: `d19_run.dev_replication` with the
    held-out namespace, anchor and frozen thresholds."""
    seed = outer_seed(anchor_, cell.cell_id, ns, rep)
    parts = rules.families(cell, rules.draw(cell, seed, source))
    records = {
        label: d19_run._family_record(cell, label, legs, seed, prereg, rep, bounds)
        for label, legs in parts.items()
    }
    return records if cell.law == "semi-joint" else records[rules.family_label(cell)]


def _chain(store: Path, bound: str, ns: str, cell: Cell, n: int, gating: Any,
           host: Any) -> chunks.Chain:  # fmt: skip
    return chunks.Chain(store / ns.removeprefix("d19-") / cell.cell_id, binding=bound,
                        namespace=ns, cell_id=cell.cell_id, replications=n,
                        gating=gating, host=host)  # fmt: skip


def worker(
    obj: Path, posted: str, attempt: int, anchor_: str, store: Path, cell_id: str,
    raw_root: Path | None,
) -> str:  # fmt: skip
    """One chain, in its own process, after its own gate (R3-3)."""
    report, defn, freeze = gate(obj, posted)
    ns = namespace(attempt)
    cell, n, bounds = next(
        p for p in plan(report, defn, freeze) if p[0].cell_id == cell_id
    )
    source = None
    if cell.law in SEMI_LAWS:
        if raw_root is None:
            raise ValueError(f"{cell_id}: a Q5 cell needs --raw-root")
        source = semi.load_source(raw_root)
        if source.identity != defn.get("exploration_source"):
            raise ValueError("exploration data differs from the run definition")
    bound = binding(posted, anchor_)
    chain = _chain(store, bound, ns, cell, n, defn["gating"], host_provenance())
    prereg = defn["prereg_sha256"]
    return chunks.run(
        chain, lambda rep: replication(cell, anchor_, ns, prereg, rep, bounds, source)
    )


def _float(value: object) -> float | None:
    return None if value is None else reduce.decode({"v": value})["v"]


def frozen_reps(
    chain: chunks.Chain, cell: Cell, bounds: reduce.Bounds, rule: str
) -> dict[str, list[choices.Rep]]:
    """A verified held-out chain as replications under the frozen block
    rule, per unit; every record must follow from the frozen thresholds."""
    units = _units(cell)
    out: dict[str, list[choices.Rep]] = {u: [] for u in units}
    joint = cell.law == "semi-joint"
    for rep, stored in enumerate(chunks.reduce(chain)):
        if not isinstance(stored, dict) or (
            joint and set(stored) != set(reduce.FAMILIES)
        ):
            raise ValueError(f"{cell.cell_id} rep {rep}: malformed record")
        for unit, family in zip(
            units, reduce.FAMILIES if joint else (None,), strict=True
        ):
            record = stored if family is None else stored[family]
            problem = (
                choices.consistent(record, bounds)
                if isinstance(record, dict)
                else "malformed record"
            )
            if problem is not None:
                raise ValueError(f"{unit} rep {rep}: {problem}")
            r = record[rule]
            out[unit].append(choices.Rep(r["reason"], _float(r["z"]), record["u_g"]))
    return out


def _events(kind: str, reps: list[list[choices.Rep]], z: float) -> int:
    """§6 test events (choices' own predicates)."""
    if kind == "error":
        return sum(choices._passes(r, z) for r in reps[0])
    if kind == "dsr":
        return sum(r.reason is not None for r in reps[0])
    if kind == "u_g":
        return sum(r.u_g is not None for r in reps[0])
    pairs = list(zip(*reps, strict=True))
    if kind == "error_joint":
        return sum(choices._either(a, b, z) for a, b in pairs)
    if kind == "u_proc_joint":
        return sum(choices._unavailable(a) or choices._unavailable(b) for a, b in pairs)
    raise ValueError(f"unknown test kind {kind!r}")


def tally(report: dict[str, Any], reps: dict[str, list[choices.Rep]]) -> dict[str, Any]:
    """§6: per enumerated test, the events and the one-sided Clopper-Pearson
    upper bound at alpha = 0.025/M (HO-2); accepted iff every run test is
    within its bound. `reps`: the final units' frozen-rule replications. A
    test is run iff its units are qualifying; one without replications is
    a ValueError (HO-R2)."""
    m, z = report["m"], float(report["z_crit"])
    if len(report["tests"]) != m:
        raise ValueError("the test manifest does not hold M tests")
    alpha = binomial.FAMILY_ALPHA / m
    status = {u: r["status"] for u, r in report["cells"].items()}
    out = []
    for unit, label, kind in report["tests"]:
        names = [f"{unit}/{f}" for f in reduce.FAMILIES] if label == "joint" else [unit]
        qualifying = [status.get(n) == "qualifying" for n in names]
        if not any(qualifying):
            out.append({"test": [unit, label, kind], "run": False})
            continue
        if not all(qualifying) or not all(n in reps for n in names):
            raise ValueError(f"{unit} {kind}: a qualifying unit has no replications")
        group = [reps[n] for n in names]
        n, x = len(group[0]), _events(kind, group, z)
        ucb = binomial.upper(x, n, 1 - alpha)
        bound = choices.BOUNDS[kind]
        out.append({"test": [unit, label, kind], "run": True, "n": n, "events": x,
                    "ucb": ucb, "bound": bound, "within": ucb <= bound})  # fmt: skip
    run = [t for t in out if t["run"]]
    return {"m": m, "alpha": alpha, "tests": out,
            "accepted": bool(run) and all(t["within"] for t in run)}  # fmt: skip


def _pool(jobs: list[tuple[Any, ...]]) -> list[str]:
    """The driver's two-worker pool: the first failure stops every worker
    (DR3-1, FA-5, FR-2, FR-3)."""
    context = multiprocessing.get_context("spawn")
    others = set(multiprocessing.active_children())
    pool = ProcessPoolExecutor(d19_run.WORKERS, mp_context=context)
    try:
        futures = [pool.submit(worker, *job) for job in jobs]
        done, _ = wait(futures, return_when=FIRST_EXCEPTION)
        for future in futures:
            if future in done and (failure := future.exception()) is not None:
                raise failure
        return [future.result() for future in futures]
    except BaseException:
        for child in set(multiprocessing.active_children()) - others:
            child.terminate()
        raise
    finally:
        pool.shutdown(cancel_futures=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="D-19 held-out certification")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "certify"):
        p = sub.add_parser(name)
        p.add_argument("--object", type=Path, required=True)
        p.add_argument("--posted", required=True)
        p.add_argument("--attempt", type=int, required=True)
        p.add_argument("--store", type=Path, required=True)
        if name == "run":
            p.add_argument("--round", type=int, required=True)
            p.add_argument("--randomness", required=True)
            p.add_argument("--raw-root", type=Path)
        else:
            p.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        ns = namespace(args.attempt)
        report, defn, freeze = gate(args.object, args.posted)
        planned = plan(report, defn, freeze)
        if args.command == "run":
            if args.raw_root is None and any(c.law in SEMI_LAWS for c, _, _ in planned):
                raise ValueError("Q5 cells need --raw-root")
            key = anchor(args.posted, args.round, args.randomness)
            record = {"anchor": key, "beacon_randomness": args.randomness,
                      "qobj": args.posted, "round": args.round}  # fmt: skip
            attempt_record(args.store, ns, record)
            jobs = [(args.object, args.posted, args.attempt, key, args.store,
                     c.cell_id, args.raw_root) for c, _, _ in planned]  # fmt: skip
            for (cell, _, _), head in zip(planned, _pool(jobs), strict=True):
                print(f"{ns}/{cell.cell_id}: {head}")
            return 0
        gating = defn["gating"]
        bound = binding(args.posted, recorded_anchor(args.store, ns, args.posted))
        chains = [(c, b, _chain(args.store, bound, ns, c, n, gating, {}))
                  for c, n, b in planned]  # fmt: skip
        heads = {
            c.cell_id: chunks.verify(ch) for c, _, ch in chains
        }  # all, before any read
        reps: dict[str, list[choices.Rep]] = {}
        for cell, bounds, chain in chains:
            reps |= frozen_reps(chain, cell, bounds, report["family_block_rule"])
        result = tally(report, reps)
    except Exception as error:  # noqa: BLE001 - any failure stops: refuse, publish nothing
        print(f"refused: {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    result |= {
        "qualification_object_sha256": args.posted,
        "binding": bound,
        "namespace": ns,
        "chain_heads": heads,
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", "utf-8")
    print("accepted" if result["accepted"] else "not accepted")
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
