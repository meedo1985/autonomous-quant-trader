# Adjudication of the GPT-6 Sol focused re-review of the item 2b libraries at ee9354a

**Review:** `review/d19-engine/SOL6_ITEM2B_LIBRARIES_REREVIEW_EE9354A.md`, from a packet.
- **Verdict:** FIX.
- **Earlier findings:** I2BL-2 and I2BL-3 resolved; I2BL-1 partly resolved.
- **New finding:** I2BLR-1.

Adjudicated and repaired by Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-11.

| ID | Decision | Repair and evidence |
|---|---|---|
| I2BLR-1 High (and I2BL-1) | AGREE, repaired | **The test now covers every day.** `test_every_target_ignores_its_own_day[trend/vol]` checks every rule (54) on **every** day t of a 240-day path. Targets 0..t must be identical whether r_t is +60%, −60% or 0.<br><br>**The test cannot pass vacuously.** The path drifts up and has high volatility (mean 0.4%, sd 6% per day), so trend signals are mostly on and sizes mostly below 1. On at least 95% of days, the same change must also show in a later target, so changes are not masked. The measured rate was at least 99.2% for every rule.<br><br>**Mutation check (not committed).** The reviewer's own example was planted: rule 6 (L = 200, H = 7) reading `price[t]` at refreshes from day 217. The test fails with "rule 6, day 217". With the code restored, all tests pass. `calibration/rules.py` is unchanged by this repair. |

No calibration was run.

## Checks after repair (2026-10-11, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rules.py tests/unit/test_calibration_semi.py -q -p no:cacheprovider` | 0 | 36 passed in 11.17 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 144 files already formatted |
| `.venv/Scripts/python -m mypy calibration tests/unit/test_calibration_rules.py` | 0 | No issues in 15 source files |

Only the test file changed, so the rest of the suite and the import and frozen-file checks were not rerun.
