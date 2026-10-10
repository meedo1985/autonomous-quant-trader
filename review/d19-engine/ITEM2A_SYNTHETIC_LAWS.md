# D-19 engine item 2a: skew-t, unequal moments, mixed AR column

Implemented by Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-10 on branch
`d19-calibration-engine`, under the owner's build go-ahead and the accepted
§13 rev 7g. Not yet reviewed. No calibration was run.

Item 2 is split: **2a** (this note) adds the family-agnostic synthetic laws
still missing from the generator; **2b** adds the semi-empirical market of
§3.4 (Q5, QJ), which bootstraps exploration-partition BTC/ETH data and needs
the real trend and vol rule libraries, so it gets its own step and review.
Q4 was also missing and is built here.

## What was built (`calibration/generator.py`)

| Law | Prereg | Construction |
|---|---|---|
| `skewt+`, `skewt-` | §3.1, Q2 | Azzalini skew-t, ν = 5, shape ±α_s. Draws in the order U0, U1 (standard normal), W (χ²₅): `X = (δ|U0| + √(1−δ²) U1)·√(5/W)`, standardised to mean 0 and variance 1 with the exact moments. Applies to ε and to the column innovations, as t5 does. |
| α_s | §3.1 "frozen numerically ... and recorded" | `ALPHA_S = 0.9224371221852867` (δ = 0.678026142255548): the shape whose standardised skewness is exactly 1, from the exact product moments `E[X^k] = E[Z^k]·E[(ν/W)^(k/2)]` (`skew_t_moments`). −α_s gives −1 by symmetry. |
| `unequal` | §3.2 Q2m | Columns j < ceil(K/2) are t5, the rest Gaussian; `c_j = 0.5` for even j and 2 for odd j; independent; K ≥ 2. |
| `mixed_ar` | §3.2 Q4 | Column 0 is AR(1) with φ = 0.5, the other columns iid Gaussian; independent; K ≥ 2. |

`cells_from_manifest` refuses `unequal` and `mixed_ar` unless K ≥ 2 and the
dependence is `independent`. `scripts/d19_choose.py`'s `AGNOSTIC_LAWS` now
lists the four new laws (all family-agnostic). The reference-vector suite
gains `refvec-k2-skewt` and `refvec-k5-unequal`, so the start gate also
covers the χ² draws and the skew-t standardisation.

## Interpretations (AI defaults; for review and the owner)

1. **Market ε in Q2m and Q4 is Gaussian with constant σ.** §3.2 specifies only the columns for these groups; the Q1 core market is used.
2. **Q4's AR column is column 0.** §3.2 says "one AR(1) column ... among iid columns" without an index; column order carries no meaning in an exchangeable family.
3. **α_s is fixed by exact moments, not by simulation.** Sample skewness is not a reliable estimator at ν = 5 (the sixth moment is infinite), so the formula is validated by simulation at ν = 30 and α_s is re-derived by bisection in a test.

## Noted, not changed

The existing AR(1) laws (`ar0.2`, `ar0.5`) apply AR(1) to the column
innovations only; ε stays Gaussian. §3.1 lists AR(1) among "laws of ε and of
the column innovations". This is reviewed code from before item 2a; whether
ε should also be AR(1) is raised here for the reviewer and not changed.

## Tests

`tests/unit/test_calibration_generator.py`: α_s gives skewness ±1 and is
re-derived; the moment formula matches simulation at ν = 30; the skew-t
draws have mean 0 and variance 1 at ν = 5 with the right sign of skew; Q2m
column laws and the 4:1 scale ratio; Q4's lag-1 autocorrelation 0.5 in
column 0 only; manifest refusals and acceptance.

## Checks (2026-10-10, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_generator.py -q -p no:cacheprovider` | 0 | 10 passed |
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py -q -p no:cacheprovider -k "reference_vectors or start_gate_passes"` | 0 | 6 passed |
| `.venv/Scripts/python -m pytest` the six calibration files (`rundef`, `chunks`, `reduce`, `binomial`, `choices`, `generator`) `-q -p no:cacheprovider` | 0 | 121 passed in 465.14 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those six files | 0 | 1801 passed, 9 skipped in 558.25 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 140 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_choose.py` | 0 | No issues in 67 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |
