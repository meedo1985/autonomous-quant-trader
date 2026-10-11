"""The qualifying grid (prereg §3.2 with §13 rev 7g items 1-2) and its
canonical cell ids (owner decision 2026-10-11 on FA-1).

Every qualification cell is one of the grid's (law, dependence, K) at the
one length `T = T_C2`, and its id is computed from those settings, so no
id is a free seed input. `generator.cells_from_manifest` accepts more
combinations, for pilots and exploration; this module is the stricter
check at the qualification boundary (I2A-4)."""

from __future__ import annotations

from calibration.generator import Cell

K_ALL = (1, 2, 5, 20)  # §13 rev 7g item 1
# §3.2 dependence levels and the K they apply at
Q1_LEVELS = (
    ("independent", K_ALL),
    ("equi0.5", (2, 5, 20)),
    ("equi0.9", (2, 5, 20)),
    ("equi0.99", (2, 5, 20)),
    ("near_duplicates", (2, 5, 20)),
    ("exact_duplicate", (2, 5, 20)),
    ("opposites", (2, 5, 20)),
    ("clusters", (5, 20)),
    ("factor", (5, 20)),
)
Q2_LAWS = ("t5", "skewt+", "skewt-", "garch", "ar0.2", "ar0.5")
Q2_LEVELS = (("independent", K_ALL), ("equi0.9", (2, 5, 20)), ("opposites", (2, 5, 20)))


def _grid() -> list[tuple[str, str, int]]:
    """(law, dependence, K) of every qualifying cell, in group order."""
    out = [("gaussian", dep, k) for dep, ks in Q1_LEVELS for k in ks]  # Q1
    out += [(law, dep, k) for law in Q2_LAWS for dep, ks in Q2_LEVELS for k in ks]
    out += [("garch", "factor", k) for k in (5, 20)]  # Q3
    out += [("unequal", "independent", k) for k in (2, 5, 20)]  # Q2m
    out += [("mixed_ar", "independent", k) for k in (2, 5, 20)]  # Q4
    out += [(f"semi-{f}", "independent", k) for f in ("trend", "vol") for k in K_ALL]
    out += [("semi-joint", "independent", k) for k in (2, 20)]  # QJ
    return out


GRID = tuple(_grid())


def canonical_id(law: str, dependence: str, k: int, t: int) -> str:
    """The cell id computed from its settings ("+" is not path-safe)."""
    return f"{law.replace('+', 'p')}.{dependence}.k{k}.t{t}"


def cells(t: int) -> list[Cell]:
    """The full qualifying grid at `T = t` (= T_C2), with canonical ids."""
    return [Cell(canonical_id(law, dep, k, t), k, t, law, dep) for law, dep, k in GRID]


def problem(cells_: list[Cell]) -> str | None:
    """Why these cells are not exactly the qualifying grid at one `T` with
    canonical ids, or None."""
    lengths = {c.t for c in cells_}
    if len(lengths) != 1:
        return f"qualification cells need one T (T_C2), got {sorted(lengths)}"
    (t,) = lengths
    wrong = sorted(
        c.cell_id
        for c in cells_
        if c.cell_id != canonical_id(c.law, c.dependence, c.k, c.t)
    )
    if wrong:
        return f"cell ids are not the canonical ones (FA-1): {wrong[:3]}"
    have = sorted((c.law, c.dependence, c.k) for c in cells_)
    if have != sorted(GRID):
        parts = [
            f"{name} {sorted(cells)[:3]}"
            for name, cells in (
                ("extra", set(have) - set(GRID)),
                ("missing", set(GRID) - set(have)),
            )
            if cells
        ] or ["a cell appears twice"]
        return f"not the qualifying grid at T = {t}: {'; '.join(parts)}"
    return None


def manifest(t: int, replications: dict[str, int]) -> dict[str, object]:
    """The qualification cell manifest at `T = t` (= T_C2): the whole grid
    with canonical ids. It is a pure function of `t` and the prescribed
    counts, so it is "frozen" by recording those."""
    return {
        "purpose": "qualification",
        "replications": dict(replications),
        "cells": [
            {"cell_id": c.cell_id, "k": c.k, "t": c.t, "law": c.law,
             "dependence": c.dependence}
            for c in cells(t)
        ],
    }  # fmt: skip
