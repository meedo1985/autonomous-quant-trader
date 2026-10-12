# Adjudication of the GPT-6 Sol focused re-review of the item 2b libraries at 5624d3e

**Review:** `review/d19-engine/SOL6_ITEM2B_LIBRARIES_REREVIEW2_5624D3E.md`, made
from a packet. Verdict FIX. I2BLR-1 is partly resolved, and there is a new
finding, I2BLR2-1.

Adjudicated and repaired by Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-11.

| ID | Decision | Repair and evidence |
|---|---|---|
| I2BLR2-1 High (and I2BLR-1) | AGREE, repaired by both routes the reviewer allowed | See the four points below. |

**I2BLR2-1: what was changed.**

1. **The claim is narrowed.** `test_every_target_ignores_its_own_day` now states
   what it proves: for every rule and every day t of the 240-day path,
   targets 0..t are identical under four values of r_t. These are the path's
   own value (as the reviewer asked), +60%, −60% and 0. The test states that
   this does not prove detection of every conceivable partial look-ahead.
2. **Committed per-rule witnesses replace the 95% later-target counter.**
   `test_the_check_catches_each_rules_one_day_look_ahead` runs each of the 54
   rules on the path shifted one day earlier, so target t reads r_1 .. r_t: a
   whole-rule one-day look-ahead. It requires the same check to fail for
   every rule, and it does.
3. **The earlier mutation checks** (a planted look-ahead in rule 6 from day 217;
   look-ahead in all L = 200, H = 7 rules) remain recorded in the previous
   adjudications as uncommitted evidence.
4. **The production code is unchanged.** The reviewer notes that it shows lagged
   reads in the relevant calculations.

No calibration was run.

## Checks after repair (2026-10-11, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rules.py tests/unit/test_calibration_semi.py -q -p no:cacheprovider` | 0 | 38 passed in 19.86 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m mypy calibration tests/unit/test_calibration_rules.py` | 0 | No issues in 15 source files |

Only the test file changed.
