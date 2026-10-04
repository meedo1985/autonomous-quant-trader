"""Seeds of the D-19 preregistration rev 6 §8 (`e1e4e7e`)."""

from __future__ import annotations

import hashlib
import json

import numpy as np


def cj(value: object) -> bytes:
    """Canonical JSON: UTF-8, sorted keys, no insignificant whitespace."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha(value: object) -> str:
    return hashlib.sha256(cj(value)).hexdigest()


def outer_seed(anchor: str, cell_id: str, ns: str, rep: int) -> str:
    return sha({"anchor": anchor, "cell_id": cell_id, "ns": ns, "rep": rep})


def stream(seed: str, name: str) -> np.random.Generator:
    """numpy Philox (4x64, 10 rounds), key = first 16 digest bytes as two
    big-endian uint64, counter 0."""
    digest = bytes.fromhex(sha({"seed": seed, "stream": name}))
    key = [int.from_bytes(digest[i : i + 8], "big") for i in (0, 8)]
    return np.random.Generator(np.random.Philox(key=key, counter=0))


def family_seed(
    seed: str, cell_id: str, family: str, k: int, prereg: str, rep: int
) -> str:
    """Annex B §2.4 family seed with the §8 synthetic fields, extended by R-7
    with round = rep (byte encoding of R-7 is <<OPEN D-20>>; canonical JSON
    used here provisionally)."""
    trials = [
        {
            "configuration_hash": sha({"j": j, "seed": seed, "tag": "c"}),
            "hypothesis_hash": sha({"j": j, "seed": seed, "tag": "h"}),
            "trial_id": f"t{j:03d}",
        }
        for j in range(k)
    ]
    annex_b = sha(
        {
            "cycle_id": "D19",
            "data_manifest_hash": seed,
            "family_id": family,
            "protocol_hash": prereg,
            "trials": trials,
            "window_id": cell_id,
        }
    )
    beacon = sha({"seed": seed, "tag": "beacon"})
    return sha({"annex_b_seed": annex_b, "beacon_randomness": beacon, "round": rep})
