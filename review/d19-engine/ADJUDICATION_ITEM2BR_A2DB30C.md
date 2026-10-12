# Adjudication of the GPT-6 Sol re-review of D-19 engine item 2b at a2db30c

Review: `review/d19-engine/SOL6_ITEM2B_REREVIEW_A2DB30C.md`. Part A was
ACCEPT for pilot use of the library-independent code, part B SOUND WITH
FIXES, findings I2BR-1..I2BR-5, from a packet. Adjudicated by Claude Opus 5.5
(`claude-opus-5-5`) on 2026-10-11.

| ID | Decision | Repair and evidence |
|---|---|---|
| I2BR-1 High | AGREE, repaired | The `Exposures` contract in `calibration/semi.py` now says that row t is the exposure held on day t, which earns r_t, and that it may use only rows < t. The algebra test's fixture uses the level through t − 1. Prefix invariance will be tested on each library when it is built, before any Q5/QJ pilot. |
| I2BR-2 Medium | AGREE, defined in proposal revision 3 | A decision is made at the start of every path day, including day 0. The held state before it is 0, and every rule has a defined day-0 target. |
| I2BR-3 Medium | AGREE, defined | For s < 0, `r_s² = v̄` (this affects only HAR's first 22 warm-up days); a trend rule's target is 0 until L prices exist. |
| I2BR-4 Medium | AGREE, defined | A table gives the trial identity of every rule. The EWMA half-life is part of the parameter point, with a 24 h horizon. The balance claim of R-4 is restated as balance in the indexed choices. The library design is unchanged, so no owner choice was overridden. |
| I2BR-5 Low | AGREE, defined | `v̄` uses divisor n (`ddof = 0`). The source is refused if any BTC row has `1 + r ≤ 0` or is non-finite, and a non-finite price index raises an error. |

The definitions for I2BR-2..I2BR-5 are drafter defaults, which the owner
accepts or amends with the whole proposal. They will be bound in the library
code and its tests.

No calibration was run.

## Checks after repair (2026-10-11, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_semi.py -q -p no:cacheprovider` | 0 | 16 passed |
| `.venv/Scripts/python -m ruff check calibration tests/unit/test_calibration_semi.py` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check calibration tests/unit/test_calibration_semi.py` | 0 | 14 files already formatted |
| `.venv/Scripts/python -m mypy calibration tests/unit/test_calibration_semi.py` | 0 | No issues in 14 source files |

The only code changes are one comment in `calibration/semi.py` and one test fixture, so the rest of the suite and the import and frozen-file checks were not rerun. Those last passed at dac7075.
