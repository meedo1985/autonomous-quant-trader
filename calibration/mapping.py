"""Declaration-time design-to-cell mapping of preregistration §3.6, with
§13 rev 7g items 3 and 4 (O18-4; DS3-1, DS4-1, DF4-1).

A declared family, run as its declared trial set on the exploration
partition only, gives a daily E-DIFF matrix (days x trials). The §3.5
diagnostics (`classifier.diagnostics`, without `L_j/T`) are computed on its
last `T_C2` rows. The design is accepted if, and only if, at least one
**final qualifying** unit (a cell, or one family of a QJ cell) of the
frozen qualification object has `K = K` and `T = T_C2` and holds every
diagnostic within its **own** stored per-tail order statistics (ties
accepted). A non-finite diagnostic is a refusal. Fewer than `T_C2` rows
after the trials' warm-up is a refusal: the design cannot be mapped. The
pooled thresholds are the window classifier's, never used here.

Readings (proposed, for review):
- MP-1 The caller supplies the E-DIFF rows of the complete exploration
  days after the trials' warm-up, in day order; the mapping takes the
  last `T_C2` of them. Building E-DIFF from a declared family, and
  checking and binding that input, is the declaration's own code (MP-R3,
  left to that later task).
- MP-2 Every final qualifying unit counts, of any group or family label:
  §3.6 names only `K_c = K` and `T_c = T_C2`.
- MP-3 The statuses and bounds are read only from a qualification object
  whose `manifest.json` hashes to the posted `qualification_object_sha256`
  and whose `choices.json` and `definition.json` match its manifest
  (MP-R1); the record carries that hash.
- MP-4 The diagnostics come from the run's own code on the run's pinned
  runtime (MP-R2, MP-R4): the engine commit of the object's run definition
  must hold exactly the engine code the run recorded (`generator_sha256`);
  every loaded `calibration` and `aqt` module must be loaded from its
  source in this checkout, with bytecode caching off as at a run start
  (`rundef.bytecode_problem`), and equal that commit's file, except this
  file, which must equal the object's reviewed `mapping.py`; and the
  runtime identity, both canaries, the image digest and the reference
  vectors must equal the run definition's, as at a chunk start. The entry
  script is the declaration's own (MP-R3).

The record (outcome, matched unit ids, diagnostics as float hex, object
hash) and its SHA-256 go into the declaration (§3.6 "Outcome")."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

from calibration import classifier, dsr, grid, rundef
from calibration.seeds import sha

SELF = "calibration/mapping.py"


def load(obj: Path, posted_sha256: str) -> tuple[dict[str, Any], dict[str, Any], bytes]:
    """`choices.json`, `definition.json` and the reviewed `mapping.py` of
    the qualification object at `obj`, after checking that its manifest is
    the posted one (MP-3). ValueError otherwise."""
    manifest = json.loads((obj / "manifest.json").read_bytes())
    if sha(manifest) != posted_sha256:
        raise ValueError("the qualification object is not the posted one")
    out = []
    for name in ("choices.json", "definition.json", "mapping.py"):
        data = (obj / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != manifest.get(name):
            raise ValueError(f"{name} does not match the object's manifest")
        out.append(data)
    return json.loads(out[0]), json.loads(out[1]), out[2]


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=True
    ).stdout


def loaded() -> dict[str, Path]:
    """Every loaded `calibration` and `aqt` module's source, by path
    relative to this checkout; ValueError if one has none or lies outside."""
    base = Path(__file__).resolve().parents[1]
    out = {}
    for name, module in sorted(sys.modules.items()):
        if name.split(".")[0] not in ("aqt", "calibration"):
            continue
        file = getattr(module, "__file__", None)
        path = None if file is None else Path(file).resolve()
        if path is None or not path.is_relative_to(base):
            raise ValueError(f"{name} is not loaded from this checkout")
        out[path.relative_to(base).as_posix()] = path
    return out


def check_engine(defn: dict[str, Any], root: Path, reviewed: bytes) -> None:
    """MP-4, code: the run definition's engine commit in the repository at
    `root` holds the code the run recorded, and every loaded engine module
    is that commit's, or for this file the object's `reviewed` mapping.
    ValueError otherwise."""
    commit = defn["engine_commit"]
    try:
        names = _git(root, "ls-tree", "-r", "--name-only", commit).decode()
        inventory = {
            rel: rundef.canonical_sha256(_git(root, "show", f"{commit}:{rel}"))
            for rel in sorted(names.splitlines())
            if rundef.is_code(rel)
        }
    except subprocess.CalledProcessError as error:
        raise ValueError(f"engine commit {commit} not readable") from error
    if sha(inventory) != defn["generator_sha256"]:
        raise ValueError("the engine commit is not the run's recorded code")
    if problem := rundef.bytecode_problem():
        raise ValueError(problem)
    inventory[SELF] = rundef.canonical_sha256(reviewed)
    for rel, path in loaded().items():
        if rundef.canonical_sha256(path.read_bytes()) != inventory.get(rel):
            raise ValueError(f"the loaded {rel} is not the run's")


def check_runtime(defn: dict[str, Any]) -> None:
    """MP-4, runtime: the run definition's pinned runtime, canaries, image
    digest and reference vectors, as the start gate checks them."""
    recorded = defn["gating"]
    dsr.v_runtime_check(recorded["identity"], recorded["canaries"])
    if os.environ.get(rundef.IMAGE_DIGEST_ENV) != recorded["image_digest"]:
        raise RuntimeError("image digest differs")
    if rundef.reference_vectors() != recorded["reference_vectors"]:
        raise RuntimeError("reference vectors differ")


def map_design(
    obj: Path, posted_sha256: str, e_diff: np.ndarray, root: Path
) -> dict[str, Any]:
    """The §3.6 record of one declared design against the posted
    qualification object (MP-3), after the engine and runtime checks
    (MP-4). `e_diff`: the complete exploration days after warm-up, days by
    trials (MP-1); `root`: a repository holding the engine commit."""
    report, defn, reviewed = load(obj, posted_sha256)
    check_engine(defn, root, reviewed)
    check_runtime(defn)
    return _compare(e_diff, report) | {"qualification_object_sha256": posted_sha256}


def _bounds(
    entry: dict[str, dict[str, str]],
) -> tuple[dict[str, float], dict[str, float]]:
    up, lo = (
        {n: float.fromhex(v) for n, v in entry[s].items()} for s in ("upper", "lower")
    )
    return up, lo


def _compare(e_diff: np.ndarray, report: dict[str, Any]) -> dict[str, Any]:
    """The comparison of §3.6 against a report's final qualifying units."""
    x = np.asarray(e_diff, dtype=float)
    if x.ndim != 2 or x.shape[1] < 1:
        raise ValueError("E-DIFF must be a days x trials matrix")
    if x.shape[0] < grid.T_C2:
        return {"accepted": False, "reason": "fewer than T_C2 days after warm-up",
                "days": x.shape[0], "cells": [], "diagnostics": None}  # fmt: skip
    values = classifier.diagnostics(x[-grid.T_C2 :])
    matched = sorted(
        unit
        for unit, row in report["cells"].items()
        if row["status"] == "qualifying"
        and classifier.within(values, *_bounds(report["cell_bounds"][unit]))
    )
    finite = all(np.isfinite(v) for v in values.values())
    return {
        "accepted": bool(matched),
        "reason": None
        if matched
        else (
            "outside every final qualifying cell" if finite else "non-finite diagnostic"
        ),
        "days": grid.T_C2,
        "cells": matched,
        "diagnostics": {n: v.hex() for n, v in sorted(values.items())},
    }


def record_sha256(record: dict[str, Any]) -> str:
    """The hash of a mapping record, for the declaration."""
    return sha(record)
