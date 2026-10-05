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
from pathlib import Path
from typing import Any

from calibration import dsr, gates
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


def reference_vectors() -> dict[str, str]:
    """The reference-vector suite: generator, method V and the gates on fixed
    synthetic cases; each value is the SHA-256 of every output, bit-exact."""
    out: dict[str, str] = {}
    for cell in REFERENCE_CASES:
        seed = outer_seed(_ANCHOR, cell.cell_id, "refvec", 0)
        legs = generate(cell, stream(seed, "market"), stream(seed, "columns"))
        fam = family_seed(seed, cell.cell_id, "agnostic", cell.k, _PREREG, 0)
        result = dsr.evaluate(legs.x, fam, "largest", numerics="v")
        nominee = 0 if result.nominee is None else result.nominee
        trace: list[object] = []
        gate = gates.u_g(
            legs.x, legs.candidates, legs.benchmark, nominee, seed, trace=trace
        )
        outputs = {
            "x": hashlib.sha256(legs.x.tobytes()).hexdigest(),
            "benchmark": hashlib.sha256(legs.benchmark.tobytes()).hexdigest(),
            "candidates": hashlib.sha256(legs.candidates.tobytes()).hexdigest(),
            "result": dataclasses.asdict(result),
            "u_g": gate,
            "u_g_trace": trace,
        }
        out[cell.cell_id] = sha(_exact(outputs))
    # FE-3: one case built to be UNAVAILABLE (G-2: a -150% day ruins equity)
    cell = REFERENCE_CASES[1]
    seed = outer_seed(_ANCHOR, cell.cell_id, "refvec", 0)
    legs = generate(cell, stream(seed, "market"), stream(seed, "columns"))
    ruined = legs.candidates.copy()
    ruined[5, 0] = -1.5
    trace = []
    gate = gates.u_g(legs.x, ruined, legs.benchmark, 0, seed, trace=trace)
    out["refvec-k2-g2-unavailable"] = sha(_exact({"u_g": gate, "u_g_trace": trace}))
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


def generator_sha256(root: Path) -> str:
    """SHA-256 over every file the engine can run: `calibration/*.py` and
    `src/aqt/**/*.py` (sorted relative path and bytes; FE-2)."""
    files = sorted(
        [*(root / "calibration").glob("*.py"), *(root / "src" / "aqt").rglob("*.py")]
    )
    return sha({p.relative_to(root).as_posix(): p.read_bytes().hex() for p in files})


def build(
    *,
    prereg_commit: str,
    prereg_sha256: str,
    engine_commit: str,
    generator_code_sha256: str,
    cell_manifest: object,
    seed_spec: object,
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
        "seed_spec": seed_spec,
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
    """Run on every start and resume, before any chunk: the code under
    `root`, the pinned runtime, both canaries, the image digest and the full
    reference-vector suite must equal the run definition's. Returns the
    gating identity every chunk of the run must carry."""
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
