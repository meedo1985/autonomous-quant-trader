"""Run definition and start gate of prereg §13 rev 7g item 6 (D19CR-4).

The run definition is committed before the threshold run; its SHA-256 binds
threshold and development chunks. It carries the gating identity: the A-V1
runtime identity, the image digest, and the canary and reference-vector
values measured on the run's own machine. `start_gate` re-measures all of it
on every start and resume, before any chunk runs. Host provenance is
recorded in each chunk and never compared."""

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
        gate = None
        if result.nominee is not None:
            gate = gates.u_g(
                legs.x, legs.candidates, legs.benchmark, result.nominee, seed
            )
        outputs = {
            "x": hashlib.sha256(legs.x.tobytes()).hexdigest(),
            "candidates": hashlib.sha256(legs.candidates.tobytes()).hexdigest(),
            "result": dataclasses.asdict(result),
            "u_g": gate,
        }
        out[cell.cell_id] = sha(_exact(outputs))
    return out


def host_provenance() -> dict[str, str]:
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
    }


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
    """SHA-256 over every `calibration/*.py` file (sorted relative path and
    bytes): the generator-code hash."""
    files = sorted((root / "calibration").glob("*.py"))
    return sha({p.relative_to(root).as_posix(): p.read_bytes().hex() for p in files})


def build(
    *,
    prereg_commit: str,
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


def start_gate(defn: dict[str, Any]) -> dict[str, Any]:
    """Run on every start and resume, before any chunk: the pinned runtime,
    both canaries, the image digest and the full reference-vector suite must
    equal the run definition's. Returns the gating identity every chunk of
    the run must carry."""
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
