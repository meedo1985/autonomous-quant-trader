"""Market and leg generators of prereg rev 6 §3.1–§3.2 (agnostic groups).

Laws built so far: Gaussian, t5, AR(1), GARCH(1,1)-t5 (common sigma_t).
Skew-t and the semi-empirical market (Q5/QJ) are added when the full run is
authorised; the measured pilot only needs cost-representative cells."""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np

SIGMA = 0.035  # daily, unconditional
SCALE_X = 0.3
BURN = 500


@dataclass(frozen=True, slots=True)
class Cell:
    cell_id: str
    k: int
    t: int
    law: str = "gaussian"  # gaussian | t5 | ar0.2 | ar0.5 | garch
    dependence: str = "independent"  # independent | equi0.5 | equi0.9 | equi0.99 |
    # near_duplicates | exact_duplicate | opposites | clusters | factor


LAWS = ("gaussian", "t5", "ar0.2", "ar0.5", "garch")
DEPENDENCES = (
    "independent",
    "equi0.5",
    "equi0.9",
    "equi0.99",
    "near_duplicates",
    "exact_duplicate",
    "opposites",
    "clusters",
    "factor",
)
K_VALUES = (1, 2, 5, 20)  # §13 rev 7g item 1
_CELL_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")


def cells_from_manifest(manifest: object) -> list[Cell]:
    """The manifest's cells, or ValueError (DR-2): exactly the five fields,
    unique path-safe ids, K in {1, 2, 5, 20}, T >= 16, a law and dependence
    this generator implements and that fit K. Nothing falls through to a
    generator default."""
    if not isinstance(manifest, dict) or not isinstance(manifest.get("cells"), list):
        raise ValueError("cell manifest has no list of cells")
    cells, seen = [], set()
    for entry in manifest["cells"]:
        if not isinstance(entry, dict) or set(entry) != set(Cell.__slots__):
            raise ValueError(f"cell entry does not have exactly {Cell.__slots__}")
        cell = Cell(**entry)
        if not isinstance(cell.cell_id, str) or not _CELL_ID.fullmatch(cell.cell_id):
            raise ValueError(f"cell id is not path-safe: {cell.cell_id!r}")
        if cell.cell_id in seen:
            raise ValueError(f"duplicate cell id: {cell.cell_id}")
        seen.add(cell.cell_id)
        if type(cell.k) is not int or cell.k not in K_VALUES:
            raise ValueError(f"{cell.cell_id}: K must be one of {K_VALUES}")
        if type(cell.t) is not int or cell.t < 16:
            raise ValueError(f"{cell.cell_id}: T must be an integer >= 16")
        if cell.law not in LAWS or cell.dependence not in DEPENDENCES:
            raise ValueError(f"{cell.cell_id}: unknown law or dependence")
        if cell.k == 1 and cell.dependence != "independent":
            raise ValueError(f"{cell.cell_id}: K = 1 has no dependence")
        if cell.dependence == "clusters" and cell.k not in (5, 20):
            raise ValueError(f"{cell.cell_id}: clusters need K = 5 or 20")
        cells.append(cell)
    if not cells:
        raise ValueError("cell manifest has no cells")
    return cells


@dataclass(frozen=True, slots=True)
class Legs:
    x: np.ndarray  # T x K E-DIFF columns, population mean 0
    benchmark: np.ndarray  # T
    candidates: np.ndarray  # T x K = benchmark + X


def _innovations(
    rng: np.random.Generator, law: str, shape: tuple[int, ...]
) -> np.ndarray:
    if law in ("t5", "garch"):
        return np.asarray(rng.standard_t(5, shape) / np.sqrt(5 / 3))
    return rng.standard_normal(shape)


def sigma_matrix(cell: Cell, rng: np.random.Generator) -> np.ndarray:
    k, dep = cell.k, cell.dependence
    s = np.eye(k)
    if dep.startswith("equi"):
        rho = float(dep[4:])
        s = (1 - rho) * np.eye(k) + rho * np.ones((k, k))
    elif dep == "near_duplicates":
        for i in range(0, k - 1, 2):
            s[i, i + 1] = s[i + 1, i] = 0.999
    elif dep == "opposites":
        g1 = np.arange(k) < k // 2
        same = g1[:, None] == g1[None, :]
        s = np.where(same, 0.9, -0.9)
        np.fill_diagonal(s, 1.0)
    elif dep == "clusters":
        first = {5: 1, 20: 5, 80: 20}[k]
        a = np.arange(k) < first
        s = np.where(a[:, None] == a[None, :], 0.9, 0.2)
        np.fill_diagonal(s, 1.0)
    elif dep == "factor":
        lam = rng.uniform(0.3, 0.99, k)
        s = np.outer(lam, lam) + np.diag(1 - lam**2)
    return s


def _root(s: np.ndarray) -> np.ndarray:
    w, v = np.linalg.eigh(s)
    return (v * np.sqrt(np.clip(w, 0, None))) @ v.T


def _sigma_path(rng: np.random.Generator, law: str, n: int) -> np.ndarray:
    if law != "garch":
        return np.full(n, SIGMA)
    a, b = 0.10, 0.85
    omega = SIGMA**2 * (1 - a - b)
    e = _innovations(rng, "t5", (n + BURN,))
    var, out = SIGMA**2, np.empty(n + BURN)
    for i in range(n + BURN):
        out[i] = np.sqrt(var)
        var = omega + a * (out[i] * e[i]) ** 2 + b * var
    return out[BURN:]


def generate(
    cell: Cell, market: np.random.Generator, columns: np.random.Generator
) -> Legs:
    t, k = cell.t, cell.k
    sigma = _sigma_path(market, cell.law, t)
    eps = _innovations(market, cell.law, (t,))
    r = sigma * eps
    # benchmark: e_t = min(1, 0.40/(sigma_hat*sqrt(365))), EWMA half-life 7 days
    decay = 0.5 ** (1 / 7)
    var_hat, e = SIGMA**2, np.empty(t)
    for i in range(t):
        e[i] = min(1.0, 0.40 / (np.sqrt(var_hat) * np.sqrt(365)))
        var_hat = decay * var_hat + (1 - decay) * r[i] ** 2
    benchmark = e * r
    root = _root(sigma_matrix(cell, columns))
    law = cell.law if cell.law != "garch" else "t5"
    z = _innovations(columns, law, (t + BURN, k))
    if cell.law.startswith("ar"):
        phi = float(cell.law[2:])
        for i in range(1, t + BURN):
            z[i] = phi * z[i - 1] + np.sqrt(1 - phi**2) * z[i]
    xs = z[BURN:] @ root.T
    if cell.dependence == "exact_duplicate" and k >= 2:
        xs[:, 1] = xs[:, 0]
    x = SCALE_X * sigma[:, None] * xs
    return Legs(x, benchmark, benchmark[:, None] + x)
