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
  last `T_C2` of them. Building E-DIFF from a declared family is the
  declaration's own code, not this file's.
- MP-2 Every final qualifying unit counts, of any group or family label:
  §3.6 names only `K_c = K` and `T_c = T_C2`.
- MP-3 The bounds and statuses are read only from a qualification object
  whose `manifest.json` hashes to the posted `qualification_object_sha256`
  and whose `choices.json` matches its manifest entry.
- MP-4 The diagnostics are computed by the frozen `classifier`, so the
  mapping runs in the pinned image, like the threshold run whose order
  statistics it compares against.

The record (outcome, matched unit ids, diagnostics as float hex) and its
SHA-256 go into the declaration (§3.6 "Outcome")."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from calibration import classifier, grid
from calibration.seeds import sha


def load(obj: Path, expected_sha256: str) -> dict[str, Any]:
    """`choices.json` of the qualification object at `obj`, after checking
    that its manifest is the posted one (MP-3). ValueError otherwise."""
    manifest = json.loads((obj / "manifest.json").read_bytes())
    if sha(manifest) != expected_sha256:
        raise ValueError("the qualification object is not the posted one")
    chosen = (obj / "choices.json").read_bytes()
    if hashlib.sha256(chosen).hexdigest() != manifest.get("choices.json"):
        raise ValueError("choices.json does not match the object's manifest")
    report: dict[str, Any] = json.loads(chosen)
    return report


def _bounds(
    entry: dict[str, dict[str, str]],
) -> tuple[dict[str, float], dict[str, float]]:
    up, lo = (
        {n: float.fromhex(v) for n, v in entry[s].items()} for s in ("upper", "lower")
    )
    return up, lo


def map_design(e_diff: np.ndarray, report: dict[str, Any]) -> dict[str, Any]:
    """The §3.6 record of one declared design: `accepted`, the matching
    final qualifying units, the diagnostics (float hex) and the reason of
    a refusal. `e_diff` holds the complete exploration days after warm-up,
    days by trials (MP-1)."""
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
    return {
        "accepted": bool(matched),
        "reason": None
        if matched
        else (
            "outside every final qualifying cell"
            if all(np.isfinite(v) for v in values.values())
            else "non-finite diagnostic"
        ),
        "days": grid.T_C2,
        "cells": matched,
        "diagnostics": {n: v.hex() for n, v in sorted(values.items())},
    }


def record_sha256(record: dict[str, Any]) -> str:
    """The hash of a mapping record, for the declaration."""
    return sha(record)
