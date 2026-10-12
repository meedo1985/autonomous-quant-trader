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
- MP-4 The diagnostics come from the run's own classifier on the run's
  pinned runtime (MP-R2): the engine commit of the object's run definition
  must hold exactly the engine code the run recorded (`generator_sha256`),
  the classifier loaded here must be that commit's, and the runtime
  identity, both canaries, the image digest and the reference vectors must
  equal the run definition's, as at a chunk start.

The record (outcome, matched unit ids, diagnostics as float hex, object
hash) and its SHA-256 go into the declaration (§3.6 "Outcome")."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import numpy as np

from calibration import classifier, dsr, grid, rundef
from calibration.seeds import sha

CLASSIFIER = "calibration/classifier.py"


def load(obj: Path, posted_sha256: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """`choices.json` and `definition.json` of the qualification object at
    `obj`, after checking that its manifest is the posted one (MP-3).
    ValueError otherwise."""
    manifest = json.loads((obj / "manifest.json").read_bytes())
    if sha(manifest) != posted_sha256:
        raise ValueError("the qualification object is not the posted one")
    out = []
    for name in ("choices.json", "definition.json"):
        data = (obj / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != manifest.get(name):
            raise ValueError(f"{name} does not match the object's manifest")
        out.append(json.loads(data))
    return out[0], out[1]


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=True
    ).stdout


def check_engine(defn: dict[str, Any], root: Path) -> None:
    """MP-4, code: the run definition's engine commit in the repository at
    `root` holds the code the run recorded, and the classifier loaded here
    is that commit's. ValueError otherwise."""
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
    loaded = Path(classifier.__file__).read_bytes()
    if rundef.canonical_sha256(loaded) != inventory.get(CLASSIFIER):
        raise ValueError("the loaded classifier is not the run's")


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
    report, defn = load(obj, posted_sha256)
    check_engine(defn, root)
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
