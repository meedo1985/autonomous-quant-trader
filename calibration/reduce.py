"""Reduction of verified chains (prereg §3.5, §13 rev 7g item 4).

The driver stores every diagnostic as its IEEE-754 binary64 bit pattern
(big-endian hex). `cell_thresholds` reads a complete, verified threshold
chain and fits that cell's per-tail thresholds; `pooled` takes, per `K`, the
extreme over cells: the development thresholds of §3.5 item 2 ("per `T`
level, the extreme over all candidate cells"; every cell has `T = T_C2`,
§13 item 2, and `K` is an exact check of the classifier, so cells of
different `K` are never pooled)."""

from __future__ import annotations

import struct

from calibration import chunks, classifier

Bounds = tuple[dict[str, float], dict[str, float]]  # (upper, lower)


def decode(values: object) -> dict[str, float]:
    """One stored draw back to floats, bit-exact."""
    if not isinstance(values, dict):
        raise ValueError("stored draw is not an object")
    return {n: struct.unpack(">d", bytes.fromhex(v))[0] for n, v in values.items()}


def cell_thresholds(chain: chunks.Chain) -> Bounds:
    """The cell's (upper, lower) thresholds from its whole threshold chain;
    `ChainError` if the chain is incomplete or broken."""
    return classifier.fit_thresholds([decode(v) for v in chunks.reduce(chain)])


def pooled(cells: list[Bounds]) -> dict[int, Bounds]:
    """Per `K`: the largest upper and the smallest lower threshold over the
    cells of that `K`."""
    out: dict[int, Bounds] = {}
    for upper, lower in cells:
        k = int(upper["K"])
        if k not in out:
            out[k] = (dict(upper), dict(lower))
            continue
        up, lo = out[k]
        if up["T"] != upper["T"]:
            raise ValueError(f"K = {k}: cells differ in T")
        for name, value in upper.items():
            up[name] = max(up[name], value)
        for name, value in lower.items():
            lo[name] = min(lo[name], value)
    return out
