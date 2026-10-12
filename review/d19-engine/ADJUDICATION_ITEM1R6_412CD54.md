# Adjudication of the GPT-6 Sol focused re-review at 412cd54

Review: `review/d19-engine/SOL6_ITEM1R5_REREVIEW_412CD54.md` (FIX for pilot
use; I1R6-1, I1R6-2; I1R5-1..3 closed; stated scope accepted again; no
driver-written record refused; from a packet). Adjudicated and repaired by
Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-10. Not yet re-reviewed.

| ID | Decision | Repair and evidence |
|---|---|---|
| I1R6-1 Medium | AGREE, repaired | After rules 1-2 fail (`INVALID_SERIES`, `ZERO_VARIANCE_COLUMN`), a column has no finite Sharpe ratio, so `dev_replication`'s `nominee()` returns null and writes `u_g = "NO_NOMINEE"`; `consistent` now refuses a recorded nominee in that case (the shape check already ties a null nominee to `NO_NOMINEE`). The test helper writes such records as the driver does. Test `test_no_u_g_nominee_after_rules_1_2`. Only this direction is enforced: requiring a nominee whenever rules 1-2 pass could refuse a writable record if a finite column ever overflowed its Sharpe ratio. |
| I1R6-2 Low | AGREE, repaired | New T cases are coherent apart from T, so only the T check can refuse them: a fractional T with `UNSUPPORTED_LAW` entries and a max L/T of 3/9.5 under refusing thresholds, and T = 0 with `BLOCK_LENGTH_CAPPED` entries whose stored lengths make the old code reach `max(L_j)/T`. Verified: with the T check reverted (`v in (k,)` only) the test fails; restored, it passes. The added `ArithmeticError` catch is defence in depth: after the T check no reachable input raises it (Python float overflow gives inf, not an exception), so it has no separate test. |

No calibration was run.

## Checks after repair (2026-10-10, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_choices.py -q -p no:cacheprovider` | 0 | 20 passed |
| same `-k equal_blocks` with the T check temporarily reverted, then restored | 1 | 1 failed (the test detects I1R5-2/3); file restored, `git diff` shows only the intended changes |
| `.venv/Scripts/python -m pytest` the five calibration files (`rundef`, `chunks`, `reduce`, `binomial`, `choices`) `-q -p no:cacheprovider` | 0 | 111 passed in 353.12 s (includes the real-record driver tests) |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those five files | 0 | 1801 passed, 9 skipped in 361.44 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 139 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_choose.py` | 0 | No issues in 67 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |
