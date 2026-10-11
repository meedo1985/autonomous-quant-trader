"""The qualifying grid (prereg §3.2, §13 rev 7g items 1-2) and canonical
cell ids (owner decision 2026-10-11 on FA-1, I2A-4)."""

from __future__ import annotations

import dataclasses
from collections import Counter

import pytest

from calibration import grid, rundef
from calibration.generator import Cell, cells_from_manifest

T = 1200


def test_the_grid_is_the_preregistered_104_cells() -> None:
    """§13 item 7: about 104 cells, 102 ordinary and 2 QJ."""
    assert len(grid.GRID) == len(set(grid.GRID)) == 104
    group = Counter(
        "Q1" if law == "gaussian"
        else "Q3" if (law, dep) == ("garch", "factor")
        else "Q2" if law in grid.Q2_LAWS
        else law
        for law, dep, _ in grid.GRID
    )  # fmt: skip
    assert group == {"Q1": 26, "Q2": 60, "Q3": 2, "unequal": 3, "mixed_ar": 3,
                     "semi-trend": 4, "semi-vol": 4, "semi-joint": 2}  # fmt: skip
    assert {k for _, _, k in grid.GRID} == {1, 2, 5, 20}


def test_every_grid_cell_is_a_valid_generator_cell_with_a_canonical_id() -> None:
    cells = grid.cells(T)
    manifest = {"cells": [dataclasses.asdict(c) for c in cells]}
    assert cells_from_manifest(manifest) == cells  # path-safe, unique, valid
    assert cells[0].cell_id == "gaussian.independent.k1.t1200"
    assert "skewtp.opposites.k5.t1200" in {c.cell_id for c in cells}
    assert grid.problem(cells) is None


@pytest.mark.parametrize(
    ("change", "message"),
    [
        # I2A-4: Q2 allows independent, rho = 0.9 or opposites only
        (lambda cs: [*cs, Cell(grid.canonical_id("skewt+", "equi0.5", 2, T), 2, T,
                               "skewt+", "equi0.5")], "extra"),
        (lambda cs: cs[1:], "missing"),
        (lambda cs: [dataclasses.replace(cs[0], cell_id="mine"), *cs[1:]], "FA-1"),
        (lambda cs: [dataclasses.replace(cs[0], t=T + 1, cell_id=grid.canonical_id(
            cs[0].law, cs[0].dependence, cs[0].k, T + 1)), *cs[1:]], "one T"),
    ],
)  # fmt: skip
def test_anything_but_the_exact_grid_is_refused(change, message: str) -> None:  # type: ignore[no-untyped-def]
    cells = change(grid.cells(T))
    assert message in str(grid.problem(cells))
    manifest = {
        "purpose": "qualification",
        "replications": dict(rundef.PRESCRIBED),
        "cells": [dataclasses.asdict(c) for c in cells],
    }
    with pytest.raises(ValueError, match=message):
        rundef.run_plan(manifest)


def test_the_full_grid_can_meet_the_coverage_rule() -> None:
    """Every O18-4 category (with the owner's readings) has grid cells, so
    coverage fails only through demotion, never by construction."""
    from calibration import choices

    cells = {c.cell_id: (c.law, c.dependence, c.k) for c in grid.cells(T)}
    covered = choices.coverage(cells, set(cells))
    assert all(covered.values()), [n for n, ids in covered.items() if not ids]
    assert covered["joint_generator"] == sorted(
        c for c in cells if c.startswith("semi-joint.")
    )
