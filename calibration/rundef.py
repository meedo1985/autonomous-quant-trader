"""Run definition and start gate of prereg §13 rev 7g item 6 (D19CR-4).

The run definition is committed before the threshold run; its SHA-256 binds
threshold and development chunks. It carries the gating identity: the A-V1
runtime identity, the image digest, and the canary and reference-vector
values measured on the run's own machine, and the code hash of everything
the engine runs (`calibration/` and the whole `src/aqt` package: the run
must use its own pinned checkout, never the forward-paper one). `start_gate`
re-checks all of it on every start and resume, before any chunk runs. Host
provenance, including the libc and libm files the process has loaded, is
recorded in each chunk and never compared (FE-4: libc is gated only through
the image digest, which the owner's launcher must take from `docker inspect`
on the host, never typed by hand)."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import platform
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from calibration import classifier, dsr, gates
from calibration.generator import Cell, generate
from calibration.seeds import cj, family_seed, outer_seed, sha, stream

RECORD_TYPE = "aqt.d19.run_definition.v1"
IMAGE_DIGEST_ENV = "AQT_IMAGE_DIGEST"
_ANCHOR = "d19-reference-vectors-v1"
_PREREG = "reference-vectors"  # stands in for the protocol hash in family seeds
REFERENCE_CASES = (
    Cell("refvec-k1-t5", 1, 365, "t5", "independent"),
    Cell("refvec-k2-ar", 2, 365, "ar0.5", "near_duplicates"),
    Cell("refvec-k5-garch", 5, 365, "garch", "equi0.5"),
    Cell("refvec-k20-factor", 20, 365, "gaussian", "factor"),
)


def _exact(value: object) -> object:
    """Floats as their exact hex form (no rounding, NaN representable)."""
    if isinstance(value, float):
        return value.hex()
    if isinstance(value, dict):
        return {k: _exact(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_exact(v) for v in value]
    return value


def _reference_outputs(cell: Cell) -> dict[str, object]:
    """Every output of one reference case, before hashing."""
    seed = outer_seed(_ANCHOR, cell.cell_id, "refvec", 0)
    legs = generate(cell, stream(seed, "market"), stream(seed, "columns"))
    fam = family_seed(seed, cell.cell_id, "agnostic", cell.k, _PREREG, 0)
    result = dsr.evaluate(legs.x, fam, "largest", numerics="v")
    nominee = 0 if result.nominee is None else result.nominee
    trace: list[object] = []
    gate = gates.u_g(
        legs.x, legs.candidates, legs.benchmark, nominee, seed, trace=trace
    )
    return {
        "x": hashlib.sha256(legs.x.tobytes()).hexdigest(),
        "benchmark": hashlib.sha256(legs.benchmark.tobytes()).hexdigest(),
        "candidates": hashlib.sha256(legs.candidates.tobytes()).hexdigest(),
        "diagnostics": classifier.diagnostics(legs.x),  # FA-2: threshold numerics
        "result": dataclasses.asdict(result),
        "u_g": gate,
        "u_g_trace": trace,
    }


def _unavailable_outputs() -> dict[str, object]:
    """FE-3: a case built to be UNAVAILABLE (G-2: a -150% day ruins equity)."""
    cell = REFERENCE_CASES[1]
    seed = outer_seed(_ANCHOR, cell.cell_id, "refvec", 0)
    legs = generate(cell, stream(seed, "market"), stream(seed, "columns"))
    ruined = legs.candidates.copy()
    ruined[5, 0] = -1.5
    trace: list[object] = []
    gate = gates.u_g(legs.x, ruined, legs.benchmark, 0, seed, trace=trace)
    return {"u_g": gate, "u_g_trace": trace}


def reference_vectors() -> dict[str, str]:
    """The reference-vector suite: generator, classifier diagnostics, method
    V and the gates (with their intermediate numbers) on fixed synthetic
    cases; each value is the SHA-256 of every output, bit-exact."""
    out = {c.cell_id: sha(_exact(_reference_outputs(c))) for c in REFERENCE_CASES}
    out["refvec-k2-g2-unavailable"] = sha(_exact(_unavailable_outputs()))
    return out


def host_provenance() -> dict[str, object]:
    """CPU model, microcode and host kernel release: recorded, never compared."""
    first: dict[str, str] = {}
    try:  # Linux: the first CPU's block of /proc/cpuinfo
        block = Path("/proc/cpuinfo").read_text("utf-8").split("\n\n")[0]
        for line in block.splitlines():
            key, _, value = line.partition(":")
            first[key.strip()] = value.strip()
    except OSError:
        pass
    return {
        "cpu_model": first.get("model name", platform.processor()),
        "microcode": first.get("microcode", ""),
        "kernel": platform.release(),
        "libraries": loaded_libraries(),
    }


def loaded_libraries() -> dict[str, str]:
    """SHA-256 of the libc and libm files this process has mapped (Linux;
    empty elsewhere): disclosed provenance next to the image digest (FE-4)."""
    paths: set[str] = set()
    try:
        for line in Path("/proc/self/maps").read_text("utf-8").splitlines():
            path = line.split()[-1]
            name = Path(path).name
            if path.startswith("/") and name.startswith(("libc.so", "libc-", "libm")):
                paths.add(path)
    except OSError:
        return {}
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sorted(paths)}


def gating(image_digest: str) -> dict[str, Any]:
    """The gating identity of this machine, measured when the run definition
    is recorded: method V's pinned environment is checked first (V refuses
    to run before it), then the reference vectors are computed."""
    identity, measured = dsr.runtime_identity(), dsr.canaries()
    dsr.v_runtime_check(identity, measured)
    return {
        "identity": identity,
        "image_digest": image_digest,
        "canaries": measured,
        "reference_vectors": reference_vectors(),
    }


CODE_DIRS = ("calibration", "src/aqt", "scripts")


def is_code(rel: str) -> bool:
    """Whether a relative POSIX path is engine code: `calibration/*.py`,
    `src/aqt/**/*.py` and the `scripts/d19_*.py` entry points (RR-2)."""
    path = PurePosixPath(rel)
    return path.suffix == ".py" and (
        str(path.parent) == "calibration"
        or rel.startswith("src/aqt/")
        or (str(path.parent) == "scripts" and path.name.startswith("d19_"))
    )


def canonical_sha256(data: bytes) -> str:
    """CRLF read as LF, so a commit has one identity on every OS (RR-4)."""
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def code_inventory(root: Path) -> dict[str, str]:
    """Every engine code file under `root`: relative POSIX path to the
    canonical SHA-256 of its bytes."""
    files = {
        p.relative_to(root).as_posix(): p
        for d in CODE_DIRS
        for p in (root / d).rglob("*.py")
    }
    return {
        rel: canonical_sha256(path.read_bytes())
        for rel, path in sorted(files.items())
        if is_code(rel)
    }


def generator_sha256(root: Path) -> str:
    """The code hash recorded in the run definition (FE-2, RR-2, RR-4)."""
    return sha(code_inventory(root))


def loaded_outside(root: Path) -> list[str]:
    """Modules this process runs that the code hash does not cover: an
    `aqt`/`calibration` module loaded from anywhere but `root` (RR-2), or any
    module loaded from inside `root` that is not hashed code, such as a
    nested `calibration/extra/x.py` or a script helper (R4-1)."""
    base = root.resolve()
    # Third-party modules of the interpreter's own installation (a virtual
    # environment may sit in the checkout) are gated by the runtime identity;
    # an engine module never is, wherever it lies (R5-1).
    runtime = {Path(sys.prefix).resolve(), Path(sys.base_prefix).resolve()}
    outside = []
    for name, module in sorted(sys.modules.items()):
        file = getattr(module, "__file__", None)
        path = None if file is None else Path(file).resolve()
        inside = path is not None and path.is_relative_to(base)
        hashed = inside and is_code(path.relative_to(base).as_posix())  # type: ignore[union-attr]
        if name.split(".")[0] in ("aqt", "calibration"):
            if not hashed:
                outside.append(name)
        elif path is not None and any(path.is_relative_to(r) for r in runtime):
            continue
        elif inside and not hashed:
            outside.append(name)
    return outside


PRESCRIBED = {"threshold": 300_000, "dev": 12_000}  # §13 rev 7g items 3, 4
SEED_NAMESPACES = {"threshold": "d19-threshold-v1", "dev": "d19-dev-v1"}  # §8
PILOT_PREFIX = "pilot-"  # FA-1


def seed_spec(prereg_sha256: str) -> dict[str, object]:
    """The seed specification a run definition records, derived, never
    supplied (DR2-2): prereg §8's anchor for threshold and development
    runs is the preregistration hash, and its namespaces."""
    return {"anchor": prereg_sha256, "namespaces": dict(SEED_NAMESPACES)}


def run_plan(manifest: object) -> dict[str, int]:
    """Replications per namespace, from the cell manifest, or ValueError
    (DR-3). A `qualification` run uses exactly the prescribed counts; a
    `pilot` run (the measured re-pilot) any positive count below them, on
    `pilot-` cell ids only (FA-1). Both are in the
    run definition, so its hash binds them and a resume cannot change them."""
    if not isinstance(manifest, dict):
        raise ValueError("cell manifest is not an object")
    purpose, counts = manifest.get("purpose"), manifest.get("replications")
    if purpose not in ("qualification", "pilot") or not isinstance(counts, dict):
        raise ValueError("cell manifest needs purpose and replications")
    if set(counts) != set(PRESCRIBED) or not all(
        type(n) is int and n >= 1 for n in counts.values()
    ):
        raise ValueError(f"replications must be positive integers for {PRESCRIBED}")
    # FA-1: pilot draws share the threshold namespace and anchor, so a pilot
    # cell id must carry PILOT_PREFIX (never valid elsewhere) and a pilot
    # stays below the prescribed counts: no pilot draw is a qualification draw.
    cells = manifest.get("cells")
    entries = cells if isinstance(cells, list) else []
    ids = [c.get("cell_id") for c in entries if isinstance(c, dict)]
    piloted = [isinstance(i, str) and i.startswith(PILOT_PREFIX) for i in ids]
    if purpose == "pilot":
        if not all(piloted):
            raise ValueError(f"every pilot cell id must start with {PILOT_PREFIX!r}")
        if any(n >= PRESCRIBED[ns] for ns, n in counts.items()):
            raise ValueError(f"a pilot must stay below the prescribed {PRESCRIBED}")
    elif any(piloted):
        raise ValueError(f"{PILOT_PREFIX!r} cell ids are for pilot runs only")
    if purpose == "qualification":
        # DR2-1: a qualification run needs the complete frozen cell
        # manifest (every candidate cell at T = T_C2) and every generator
        # (skew-t, Q2m, Q5, QJ); neither exists yet, so none is accepted.
        raise ValueError(
            "qualification runs are refused until the frozen cell manifest "
            "and all generators are built and verified"
        )
    return dict(counts)


def bytecode_problem() -> str | None:
    """Why engine code may not be running from its hashed source, or None
    (R6-1): a stale, unchecked or planted `.pyc` can run different code while
    `__file__` names the source. The entry script must set
    `sys.dont_write_bytecode` and point `sys.pycache_prefix` at a new empty
    directory before importing any engine module."""
    prefix = sys.pycache_prefix
    if not sys.dont_write_bytecode or prefix is None:
        return "bytecode caching is not disabled"
    if any(Path(prefix).rglob("*.pyc")):
        return "the bytecode cache directory is not empty"
    for name, module in sorted(sys.modules.items()):
        if name.split(".")[0] not in ("aqt", "calibration"):
            continue
        cached = getattr(module, "__cached__", None)
        origin = getattr(getattr(module, "__spec__", None), "origin", None)
        if not str(origin).endswith(".py") or (
            cached is not None and not Path(cached).is_relative_to(Path(prefix))
        ):
            return f"{name} was not loaded from its source"
    return None


def build(
    *,
    prereg_commit: str,
    prereg_sha256: str,
    engine_commit: str,
    generator_code_sha256: str,
    cell_manifest: object,
    image_digest: str,
    exploration_manifest_sha256: str,
) -> dict[str, Any]:
    """The run definition (§13 item 6), measured on this machine."""
    return {
        "record_type": RECORD_TYPE,
        "prereg_commit": prereg_commit,
        "prereg_sha256": prereg_sha256,
        "engine_commit": engine_commit,
        "generator_sha256": generator_code_sha256,
        "cell_manifest": cell_manifest,
        "seed_spec": seed_spec(prereg_sha256),
        "exploration_manifest_sha256": exploration_manifest_sha256,
        "gating": gating(image_digest),
    }


def definition_sha256(defn: dict[str, Any]) -> str:
    return sha(defn)


def write(path: Path, defn: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("wb") as handle:
        handle.write(cj(defn))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def load(path: Path) -> dict[str, Any]:
    defn = json.loads(path.read_bytes())
    if not isinstance(defn, dict) or defn.get("record_type") != RECORD_TYPE:
        raise ValueError(f"{path}: not a D-19 run definition")
    return defn


def start_gate(defn: dict[str, Any], root: Path) -> dict[str, Any]:
    """Run on every start and resume, before any chunk, in every process
    that computes chunks (R3-3: each worker runs it itself and builds its
    `Chain` from `definition_sha256(defn)` and the gating returned here). The
    entry script and every loaded engine module must be hashed code under
    `root`; that code, the pinned runtime, both canaries, the image digest
    and the full reference-vector suite must equal the run definition's.
    Returns the gating identity every chunk of the run must carry."""
    main = getattr(sys.modules.get("__main__"), "__file__", None)
    entry = None if main is None else Path(main).resolve()
    if (
        entry is None
        or not entry.is_relative_to(root.resolve())
        or not is_code(entry.relative_to(root.resolve()).as_posix())
    ):
        raise RuntimeError(f"U_ops: start gate: entry point is not hashed code: {main}")
    if outside := loaded_outside(root):
        raise RuntimeError(f"U_ops: start gate: loaded outside the checkout: {outside}")
    if problem := bytecode_problem():
        raise RuntimeError(f"U_ops: start gate: {problem}")
    if generator_sha256(root) != defn["generator_sha256"]:
        raise RuntimeError("U_ops: start gate: engine code differs")
    recorded = defn["gating"]
    try:
        dsr.v_runtime_check(recorded["identity"], recorded["canaries"])
    except RuntimeError as error:
        raise RuntimeError(f"U_ops: start gate: {error}") from error
    if os.environ.get(IMAGE_DIGEST_ENV) != recorded["image_digest"]:
        raise RuntimeError("U_ops: start gate: image digest differs")
    if reference_vectors() != recorded["reference_vectors"]:
        raise RuntimeError("U_ops: start gate: reference vectors differ")
    return dict(recorded)
