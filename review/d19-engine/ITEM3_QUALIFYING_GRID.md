# D-19 engine item 3: qualifying grid and canonical cell ids

**Built by:** Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-11. No calibration was run.

## What is built

- **`calibration/grid.py`.**
  - **`GRID`** is the 104 qualifying (law, dependence, K) combinations of prereg §3.2, with the §13 rev 7g items 1–2 applied: K ∈ {1, 2, 5, 20} and one length. The count matches §13 item 7, "about 104": 102 ordinary cells and 2 QJ.

    | Group | Cells |
    |---|---:|
    | Q1 Gaussian, every dependence level at the K it applies at | 26 |
    | Q2: 6 laws × {independent, ρ = 0.9, opposites} | 60 |
    | Q3 common GARCH, one factor, K ∈ {5, 20} | 2 |
    | Q2m, K ∈ {2, 5, 20} | 3 |
    | Q4, K ∈ {2, 5, 20} | 3 |
    | Q5, per family | 8 |
    | QJ, K ∈ {2, 20} | 2 |

  - **`canonical_id`** is `law.dependence.kK.tT`, with "+" written "p" because it is not path-safe. The owner decided this on FA-1 (`OWNER_DECISION_FA1_CANONICAL_CELL_IDS.md`).
  - **`cells(t)` and `manifest(t, replications)`** produce the full qualification manifest at `T = t`. The manifest is a pure function of T_C2 and the prescribed counts, so recording those two values freezes it.
  - **`problem(cells)`** refuses anything but exactly the grid at one T with canonical ids: extra cells, missing cells, a duplicate, a non-canonical id, or two T levels.
- **`rundef.run_plan`, qualification branch.**
  - It first requires exactly the prescribed counts (300,000 threshold and 12,000 development).
  - It then requires `grid.problem` to find nothing. This enforces I2A-4 at the qualification boundary.
  - **It then still refuses.**

## Why qualification is still refused (DR2-1 kept)

1. **T_C2 = 1247 − g.** `g` is `gap_embargo.value_days`, computed by `gap_embargo.rule` from exploration data. That rule is part of the §4 amendment draft, and no code computes it yet.
2. **The accepted preregistration hash.** `PREREGISTRATION.md` still reads "NOT YET COMPLETE (keys record pending)", so its accepted hash is not final. The FA-1 point that the qualification path must check `prereg_sha256` waits for the owner's key record.
3. **The container image and launcher (FE-4), and the re-pilot (FE-7).** The owner's go-ahead follows the re-pilot (§4 freeze order, step 2).

## Tests

- **`tests/unit/test_calibration_grid.py`:**
  - the 104-cell group counts;
  - every grid cell is a valid generator cell with a canonical, unique, path-safe id;
  - the four refusals, each also through `rundef.run_plan`. One of them is an out-of-grid Q2 cell (`skewt+`, `equi0.5`, K = 2), the I2A-4 example;
  - with every grid cell qualifying, every coverage category is non-empty.
- **`test_a_bad_run_plan_is_refused`:**
  - a qualification manifest with other counts is refused for its counts;
  - the exact grid manifest at prescribed counts reaches the final DR2-1 refusal.

## Interpretations made here (for review)

- **Q2 "GARCH-t₅" and Q3 "common GARCH" are both the generator law `garch`.** They differ by dependence: Q2 uses independent, ρ = 0.9 or opposites; Q3 uses one factor.
- **The two skew-t laws ("skew-t ±1") are two Q2 laws.** Q2 therefore has 6 laws.
- **Q5 runs at every K in {1, 2, 5, 20}, per family.** QJ runs only at {2, 20} (§13 item 1).
