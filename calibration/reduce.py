"""Reduction of verified chains (prereg §3.5, §13 rev 7g item 4).

The driver stores every diagnostic as its IEEE-754 binary64 bit pattern
(big-endian hex). `cell_thresholds` reads a complete, verified threshold
chain and fits that cell's per-tail thresholds. `pooled` takes, per `T`
level, every tail's extreme over all candidate cells at that level, whatever
their `K`: the development thresholds of §3.5 item 2 ("per `T` level, the
extreme over all candidate cells"; owner decision 2026-10-11 on I2BW-1).
`for_k` makes one cell's threshold set from its level's pool: `K` and `T`
stay exact checks, and the correlation tails exist only for `K >= 2`."""

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


EXACT = ("K", "T")


def pooled(cells: list[Bounds]) -> dict[int, Bounds]:
    """Per `T` level: the largest upper and the smallest lower value of each
    tail over every cell at that level, of any `K`. A pool carries `T` and
    the tails, not `K`."""
    out: dict[int, Bounds] = {}
    for upper, lower in cells:
        t = upper["T"]
        up, lo = out.setdefault(int(t), ({"T": t}, {"T": t}))
        for name, value in upper.items():
            if name not in EXACT:
                up[name] = max(up.get(name, value), value)
        for name, value in lower.items():
            if name not in EXACT:
                lo[name] = min(lo.get(name, value), value)
    return out


def for_k(pool: Bounds, k: int) -> Bounds:
    """The threshold set for `K = k` from its `T` level's pool: `K` and `T`
    exact, and exactly the tails `classifier.required(k)` names. ValueError
    if the pool lacks one (no cell with `K >= 2` at that level)."""
    up, lo = pool
    need = classifier.required(k)
    exact = {"K": float(k), "T": up["T"]}
    try:
        upper = exact | {n: up[n] for n in sorted(need & set(classifier.UPPER))}
        lower = exact | {n: lo[n] for n in sorted(need & set(classifier.LOWER))}
    except KeyError as missing:
        raise ValueError(f"T = {up['T']}: no candidate cell has {missing}") from None
    return upper, lower
