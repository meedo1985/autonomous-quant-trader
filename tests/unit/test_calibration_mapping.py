import hashlib
import json

import numpy as np
import pytest

from calibration import classifier, grid, mapping
from calibration.seeds import cj, sha


def _x(k: int, t: int = grid.T_C2 + 30) -> np.ndarray:
    return np.random.default_rng(7).standard_normal((t, k))


def _entry(values: dict[str, float], widen: float) -> dict[str, dict[str, str]]:
    """Bounds around `values`: upper tails + widen, lower tails - widen."""
    up = {n: v + (widen if n in classifier.UPPER else 0.0) for n, v in values.items()
          if n not in classifier.LOWER}  # fmt: skip
    lo = {n: v - (widen if n in classifier.LOWER else 0.0) for n, v in values.items()
          if n not in classifier.UPPER}  # fmt: skip
    return {"upper": {n: v.hex() for n, v in up.items()},
            "lower": {n: v.hex() for n, v in lo.items()}}  # fmt: skip


def _report(x: np.ndarray) -> dict[str, object]:
    values = classifier.diagnostics(x[-grid.T_C2 :])
    tight = dict(values, max_excess_kurtosis=values["max_excess_kurtosis"] - 0.01)
    other_k = classifier.diagnostics(_x(1)[-grid.T_C2 :])
    return {
        "cells": {
            "q1-k2": {"status": "qualifying"},
            "q1-k2-tight": {"status": "qualifying"},
            "qj-k2/trend": {"status": "qualifying"},
            "demoted-k2": {"status": "challenge"},
            "q1-k1": {"status": "qualifying"},
        },
        "cell_bounds": {
            "q1-k2": _entry(values, 0.5),
            "q1-k2-tight": _entry(tight, 0.0),  # kurtosis just outside
            "qj-k2/trend": _entry(values, 0.0),  # ties accepted
            "demoted-k2": _entry(values, 1.0),  # matches, but not final
            "q1-k1": _entry(other_k, 10.0),  # another K
        },
    }


def test_accepts_only_final_qualifying_cells_of_its_k_holding_every_tail():
    x = _x(2)
    record = mapping.map_design(x, _report(x))
    assert record["accepted"] and record["reason"] is None
    assert record["cells"] == ["q1-k2", "qj-k2/trend"]
    assert record["days"] == grid.T_C2
    assert float.fromhex(record["diagnostics"]["T"]) == grid.T_C2


def test_uses_the_last_t_c2_days():
    x = _x(2)
    report = _report(x)
    shifted = np.vstack([x[:30] * 50, x[30:]])  # warm-up rows never read
    assert mapping.map_design(shifted, report)["cells"] == ["q1-k2", "qj-k2/trend"]


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        (lambda x: x[: grid.T_C2 - 1], "fewer than T_C2 days after warm-up"),
        (
            lambda x: np.where(np.arange(len(x))[:, None] == len(x) - 1, np.nan, x),
            "non-finite diagnostic",
        ),  # fmt: skip
        (lambda x: x**3, "outside every final qualifying cell"),
    ],
)
def test_refusals(change, reason):
    x = _x(2)
    record = mapping.map_design(change(x), _report(x))
    assert (
        not record["accepted"] and record["cells"] == [] and record["reason"] == reason
    )


def test_load_checks_the_posted_hash_and_the_choices_file(tmp_path):
    chosen = json.dumps({"cells": {}, "cell_bounds": {}}).encode()
    manifest = {"choices.json": hashlib.sha256(chosen).hexdigest()}
    (tmp_path / "choices.json").write_bytes(chosen)
    (tmp_path / "manifest.json").write_bytes(cj(manifest))
    assert mapping.load(tmp_path, sha(manifest)) == {"cells": {}, "cell_bounds": {}}
    with pytest.raises(ValueError, match="not the posted one"):
        mapping.load(tmp_path, "0" * 64)
    (tmp_path / "choices.json").write_bytes(chosen + b" ")
    with pytest.raises(ValueError, match="does not match"):
        mapping.load(tmp_path, sha(manifest))


def test_record_hash_is_canonical():
    x = _x(2)
    record = mapping.map_design(x, _report(x))
    assert mapping.record_sha256(record) == sha(json.loads(json.dumps(record)))
