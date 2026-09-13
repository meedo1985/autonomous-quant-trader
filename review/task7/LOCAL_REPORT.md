# Task 7 local report

Date: 2026-09-13  
Base commit: `a1838742f1ed6e204278881efab3dcbd9f875acf` (accepted Task 6)  
Implementation model: Claude Opus 5 (`claude-opus-5`, high effort)

## Scope

Task 7 adds only a research/test-side NumPy `float64` reference and synthetic
comparisons against the accepted exact Task 6 oracle. It covers clipped target
exposure, fractional drift of actual held weight, next-open execution, absolute
turnover, cost-before-return, the inclusive 10 percentage point band, UTC
midnight scheduling, the 24-hour minimum hold, intraday reductions, and the
accepted additive/compounded diagnostics. No production backtester or strategy
code was added. No frozen governance file or accepted Task 6 file changed.

NumPy is a development-only dependency because the repository specification
requires a NumPy reference while runtime packages remain unchanged.

## Validation evidence

| Check | Result |
|---|---|
| Focused reference tests | `36 passed` |
| Full suite | `819 passed, 4 skipped` |
| Ruff (`tests/reference`) | passed |
| Mypy (`src`, no incremental cache) | passed, 20 source files |
| Import contracts | passed, 4 kept, 0 broken |
| `git diff --check` | passed |
| Frozen v1 audit and Task 6 accepted hashes | unchanged and verified |

The reference comparison bounds are derived from binary64 unit roundoff
(`2**-53`) and the operation graph in `_error_bounds.py`; they are not trading
or performance thresholds. Discrete trade/HOLD decisions are asserted exactly.

## Changed files

- `pyproject.toml` (NumPy in the development extra only)
- `tests/reference/__init__.py`
- `tests/reference/_numpy_reference.py`
- `tests/reference/_error_bounds.py`
- `tests/reference/_fixtures.py`
- `tests/reference/test_numpy_reference_comparison.py`
- `tests/reference/test_reference_band_tolerance.py`
- `review/task7/AUTHORIZED_SPEC.md`
- `review/task7/OPUS_PROMPT.md`

No commit or push was performed by the implementation run. Task 8 was not
started. The remaining gate is independent adversarial review and owner
acceptance of this Task 7 snapshot.
