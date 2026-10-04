"""Annex B method `aqt.dsr.bootstrap_max.candidate.v2`, family level.

Replicate Sharpes (`numerics`):
- `"v"` (default): the one vectorised deterministic method `V` proposed for
  binding under D-20 (PILOT_FINDINGS_3), used identically in calibration and
  in every real evaluation: counts x matrix sums on mean-centred columns,
  single-threaded BLAS on the pinned runtime;
- `"task12"`: the Task 12 Sharpe numerics (fsum, two-pass), accelerated and
  bit-identical to `"reference"`, its pure-Python form (`calibration.fast`).
Statistics across replicates (`S0`, `var_b`) always use fsum in replicate
index order (Annex B §2.3).

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
from typing import TYPE_CHECKING

import numpy as np

from aqt.metrics.statistics import (
    BOOTSTRAP_ATTEMPTS,
    CONVENTION_DOCUMENT_SHA256,
    SEED_DOMAIN,
    block_length,
)
from calibration import fast
from calibration.seeds import sha

if TYPE_CHECKING:
    from pathlib import Path

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
    numerics: str = "v",
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
        if numerics == "reference"
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
    replicate = {
        "v": _replicates_v,
        "task12": _replicates_accelerated,
        "reference": _replicates_reference,
    }[numerics]
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


V_ENVIRONMENT = {"OPENBLAS_NUM_THREADS": "1", "OPENBLAS_CORETYPE": "Haswell"}
V_CANARY = "d26180459e2c6639334610fd4b31d953a7d08b5987330795cc233202bfbf7dfc"


def _interpreter_files(base: object) -> list[Path]:
    """The base interpreter executable and its shared library (VF2-3)."""
    import sys  # noqa: PLC0415
    import sysconfig  # noqa: PLC0415
    from pathlib import Path  # noqa: PLC0415

    exe = Path(str(base))
    names = {
        f"python{sys.version_info.major}{sys.version_info.minor}.dll",
        str(sysconfig.get_config_var("LDLIBRARY") or ""),
    }
    libdir = Path(str(sysconfig.get_config_var("LIBDIR") or exe.parent))
    found = [
        p
        for d in (exe.parent, libdir)
        for n in names
        if n
        for p in [d / n]
        if p.is_file()
    ]
    return sorted({exe, *found})


def runtime_identity() -> dict[str, str]:
    """What method V's bits depend on (VS1-4): interpreter and NumPy/BLAS
    binaries by hash, platform, CPU dispatch features, and the pinned env."""
    import os  # noqa: PLC0415
    import platform  # noqa: PLC0415
    import sys  # noqa: PLC0415
    from pathlib import Path  # noqa: PLC0415

    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    core = Path(np.__file__).parent
    binaries = sorted(
        p
        for p in [*core.rglob("_multiarray_umath*"), *core.parent.rglob("*openblas*")]
        if p.suffix in (".pyd", ".so", ".dll", ".dylib")
    )
    import importlib  # noqa: PLC0415

    umath = importlib.import_module("numpy._core._multiarray_umath")
    features = getattr(umath, "__cpu_features__", {})
    return {
        "python": sys.version,
        "python_binaries": sha(
            {
                p.name: digest(p)
                for p in _interpreter_files(
                    Path(getattr(sys, "_base_executable", sys.executable))
                )
            }
        ),
        "numpy": np.__version__,
        "binaries": sha({p.name: digest(p) for p in binaries}),
        "platform": f"{platform.system()} {platform.machine()}",
        "cpu_features": sha(sorted(k for k, v in features.items() if v)),
        **{name: os.environ.get(name, "") for name in V_ENVIRONMENT},
    }


_V_VERIFIED = False


def v_runtime_check(expected: dict[str, str]) -> None:
    """Fail closed (a U_ops cause) unless method V runs on its pinned runtime
    (VF1-2): the environment above, set before NumPy is imported, and a fixed
    known-answer matrix product hashing to `V_CANARY`."""
    import os  # noqa: PLC0415

    for name, value in V_ENVIRONMENT.items():
        if os.environ.get(name) != value:
            raise RuntimeError(f"U_ops: method V needs {name}={value}")
    rng = np.random.Generator(np.random.Philox(key=[2026, 1004]))
    c = rng.integers(0, 4, (200, 300)).astype(np.float64)
    y = rng.standard_normal((300, 40)) * 0.01
    if hashlib.sha256((c @ y).tobytes()).hexdigest() != V_CANARY:
        raise RuntimeError("U_ops: method V known-answer check failed on this runtime")
    if runtime_identity() != expected:
        raise RuntimeError("U_ops: runtime differs from the qualified runtime")
    global _V_VERIFIED  # noqa: PLW0603
    _V_VERIFIED = True


def _replicates_v(
    x: np.ndarray, draws: list[list[int]]
) -> tuple[list[list[float]] | None, list[list[float]] | None]:
    """Method V (D-20 proposal rev 2), a counts-weighted **two-pass** variance:
    1. mu_j = fsum(x[:, j]) / T; Y = X - mu.
    2. C[b, t] = occurrences of day t in replicate b; s1 = C @ Y; m = s1 / T.
    3. ss[b, j] = sum_t C[b, t] * (Y[t, j] - m[b, j]) ** 2 (chunked einsum);
       var = ss / (T - 1).
    4. S* = (m + mu) / sqrt(var); S-null = m / sqrt(var).
    INVALID_REPLICATE (None) if any intermediate is non-finite, any var <= 0,
    or any replicate column's drawn values are all equal (rule 5 exactly)."""
    if not _V_VERIFIED:
        raise RuntimeError("U_ops: method V needs v_runtime_check(identity) first")
    t, k = x.shape
    b = len(draws)
    try:  # VS2-2: fsum overflow on extreme finite inputs is a refusal
        mu = np.array([math.fsum(x[:, j].tolist()) / t for j in range(k)])
    except OverflowError:
        return None, None
    y = x - mu
    if not (np.isfinite(mu).all() and np.isfinite(y).all()):
        return None, None
    counts = (
        np.bincount(
            (np.arange(b)[:, None] * t + np.asarray(draws)).ravel(), minlength=b * t
        )
        .reshape(b, t)
        .astype(np.float64)
    )
    s1 = counts @ y
    m = s1 / t
    ss = np.empty_like(m)
    for lo in range(0, b, 64):
        d = y[None, :, :] - m[lo : lo + 64, None, :]
        ss[lo : lo + 64] = np.einsum("bt,btk->bk", counts[lo : lo + 64], d * d)
    var = ss / (t - 1)
    if not (np.isfinite(s1).all() and np.isfinite(var).all()):
        return None, None
    # Rule 5 exactly (VF1-1): a constant replicate column's two-pass var is
    # rounding noise of order eps**2 times its squared (centred or raw) level;
    # only such
    # near-zero variances need the exact "all drawn values equal" check.
    scale = m * m + (m + mu) ** 2 + np.finfo(float).tiny  # centred and raw level
    for b_, j in zip(*np.nonzero(var <= 1e-20 * scale), strict=True):
        drawn = x[np.asarray(draws[b_]), j]
        if (drawn == drawn[0]).all():
            return None, None
        # VF2-2: distinct values within rounding of each other: the Task 12
        # two-pass decides validity and supplies var, so rule 5 is exact.
        var[b_, j] = fast.mean_var(drawn)[1]
    if (var <= 0).any():
        return None, None
    sd = np.sqrt(var)
    star, null = (m + mu) / sd, m / sd
    if not (np.isfinite(star).all() and np.isfinite(null).all()):
        return None, None
    return star.tolist(), null.tolist()
