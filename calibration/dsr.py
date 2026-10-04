"""Annex B method `aqt.dsr.bootstrap_max.candidate.v2`, family level.

Annex B numerics throughout (fsum, two-pass, replicate order). Two
implementations of the *same* bits: the pure-Python `reference` and the
accelerated default in `calibration.fast`, which is bit-identical (see its
docstring), so no computational-equivalence rule is needed.

Indices come from the production stationary-bootstrap construction
(`aqt.metrics.statistics`), keyed by a family seed with purpose
`dsr_family_max_null` (Annex B §2.4)."""

from __future__ import annotations

import hashlib
import json
import math
import random
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from aqt.metrics.statistics import (
    BOOTSTRAP_ATTEMPTS,
    CONVENTION_DOCUMENT_SHA256,
    SEED_DOMAIN,
    block_length,
)
from calibration import fast

PURPOSE = "dsr_family_max_null"
WINDOW = '["2022-01-01T00:00:00Z","2025-06-01T00:00:00Z"]'


@dataclass(frozen=True, slots=True)
class FamilyResult:
    reason: str | None  # None = available (A_f holds for the method)
    block: float | None = None
    capped: bool = False
    nominee: int | None = None
    z: float | None = None  # z_f* of the nominee
    s0: float | None = None
    length_ratio: float | None = None  # max_j L_j / T


def _replicate_seed(family_seed: str, n: int, b: int) -> int:
    """The production `replicate_seed_material` layout with the DSR purpose,
    BTC at cost 1 (Annex B §2.4)."""
    material = json.dumps(
        [SEED_DOMAIN, family_seed, CONVENTION_DOCUMENT_SHA256, PURPOSE,
         "BTCUSDT", "1.0", WINDOW, n, b],
        ensure_ascii=False, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")  # fmt: skip
    return int.from_bytes(hashlib.sha256(material).digest(), "big")


def indices(family_seed: str, n: int, b: int, block: float) -> list[int]:
    """Production `bootstrap_indices` algorithm, same generator and draws."""
    generator = random.Random(_replicate_seed(family_seed, n, b))

    def uniform() -> int:
        drawn = generator.getrandbits(n.bit_length())
        while drawn >= n:
            drawn = generator.getrandbits(n.bit_length())
        return drawn

    out = [uniform()]
    for _ in range(1, n):
        out.append(uniform() if generator.random() < 1 / block else (out[-1] + 1) % n)
    return out


def _column_lengths(column: list[float]) -> tuple[float | None, bool]:
    """L_j = max(L(u_j), L(psi_j)); (None, _) if either fails; capped flag."""
    n = len(column)
    mean = math.fsum(column) / n
    sd = math.sqrt(math.fsum((x - mean) ** 2 for x in column) / (n - 1))
    s = mean / sd
    u = [(x - mean) / sd for x in column]
    psi = [v - (s / 2) * (v * v - 1) for v in u]
    lengths = [block_length(u), block_length(psi)]
    if any(r.value is None for r in lengths):
        return None, False
    return max(r.value for r in lengths if r.value is not None), any(
        r.clipping == "UPPER" for r in lengths
    )


def family_block(lengths: list[float], rule: str) -> float:
    if rule == "largest":
        return max(lengths)
    ordered = sorted(lengths)
    k = len(ordered)
    return ordered[k // 2] if k % 2 else (ordered[k // 2 - 1] + ordered[k // 2]) / 2


def _sharpe_exact(values: list[float]) -> float:
    n = len(values)
    mean = math.fsum(values) / n
    return mean / math.sqrt(math.fsum((x - mean) ** 2 for x in values) / (n - 1))


def _mean_var(values: list[float]) -> tuple[float, float]:
    n = len(values)
    mean = math.fsum(values) / n
    return mean, math.fsum((x - mean) ** 2 for x in values) / (n - 1)


def evaluate(
    x: np.ndarray,
    family_seed: str,
    rule: str,
    *,
    reference: bool = False,
    classifier: Callable[[np.ndarray, list[float]], bool] | None = None,
) -> FamilyResult:
    """Annex B §2.5 rules 1-6 in order, then S0, D_j, z_j and the nominee.
    `classifier(x, lengths)` returning False refuses (UNSUPPORTED_LAW),
    between rules 4 and 5 (prereg §3.5)."""
    t, k = x.shape
    if not np.isfinite(x).all():
        return FamilyResult("INVALID_SERIES")
    if (x.std(axis=0, ddof=1) == 0).any():
        return FamilyResult("ZERO_VARIANCE_COLUMN")
    pairs = (
        [_column_lengths(x[:, j].tolist()) for j in range(k)]
        if reference
        else fast.column_lengths(x)
    )
    lengths: list[float] = []
    capped = False
    for length, cap in pairs:
        if length is None:
            return FamilyResult("BLOCK_LENGTH_UNAVAILABLE")
        lengths.append(length)
        capped = capped or cap
    ratio = max(lengths) / t
    if capped:
        return FamilyResult("BLOCK_LENGTH_CAPPED", capped=True, length_ratio=ratio)
    if classifier is not None and not classifier(x, lengths):
        return FamilyResult("UNSUPPORTED_LAW", length_ratio=ratio)
    block = family_block(lengths, rule)
    draws = [indices(family_seed, t, b, block) for b in range(BOOTSTRAP_ATTEMPTS)]
    replicate = _replicates_reference if reference else _replicates_accelerated
    s_star, s_null = replicate(x, draws)
    if s_star is None or s_null is None:
        return FamilyResult("INVALID_REPLICATE", block=block, length_ratio=ratio)
    observed = [_sharpe_exact(x[:, j].tolist()) for j in range(k)]
    s0 = math.fsum(max(row) for row in s_null) / BOOTSTRAP_ATTEMPTS
    dispersion = [_mean_var([row[j] for row in s_star])[1] for j in range(k)]
    if not math.isfinite(s0) or any(
        not (d > 0 and math.isfinite(d)) for d in dispersion
    ):
        return FamilyResult("INVALID_ARITHMETIC", block=block, length_ratio=ratio)
    # z_j = (S_j - S0)/sd_b(S*_j): sqrt(T-1) cancels (Annex B §2.3)
    z = [(observed[j] - s0) / math.sqrt(dispersion[j]) for j in range(k)]
    if any(not math.isfinite(v) for v in z):
        return FamilyResult("INVALID_ARITHMETIC", block=block, length_ratio=ratio)
    nominee = max(range(k), key=lambda j: (observed[j], -j))  # ties: lowest id
    return FamilyResult(None, block, False, nominee, z[nominee], s0, ratio)


def _replicates_reference(
    x: np.ndarray, draws: list[list[int]]
) -> tuple[list[list[float]] | None, list[list[float]] | None]:
    t, k = x.shape
    columns = [x[:, j].tolist() for j in range(k)]
    centred = [[v - math.fsum(c) / t for v in c] for c in columns]
    star, null = [], []
    for idx in draws:
        row_s, row_n = [], []
        for j in range(k):
            sample = [columns[j][i] for i in idx]
            mean, var = _mean_var(sample)
            if var == 0 or not math.isfinite(var):
                return None, None
            row_s.append(mean / math.sqrt(var))
            row_n.append(_sharpe_exact([centred[j][i] for i in idx]))
        star.append(row_s)
        null.append(row_n)
    return star, null


def _replicates_accelerated(
    x: np.ndarray, draws: list[list[int]]
) -> tuple[list[list[float]] | None, list[list[float]] | None]:
    """Bit-identical to `_replicates_reference` (NumPy gather, fsum sums)."""
    t, k = x.shape
    centred = np.column_stack(
        [x[:, j] - math.fsum(x[:, j].tolist()) / t for j in range(k)]
    )
    star, null = [], []
    for idx in draws:
        s = fast.sharpes(x[idx])
        if s is None:
            return None, None
        star.append(s.tolist())
        n_ = fast.sharpes(centred[idx])
        if n_ is None:
            return None, None
        null.append(n_.tolist())
    return star, null
