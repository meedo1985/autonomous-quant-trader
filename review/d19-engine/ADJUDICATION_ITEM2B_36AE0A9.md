# Adjudication of the GPT-6 Sol review of D-19 engine item 2b at 36ae0a9

Review: `review/d19-engine/SOL6_ITEM2B_REVIEW_36AE0A9.md` (part A FIX for
pilot use, part B SOUND WITH FIXES; I2B-1..I2B-8; from a packet).
Adjudicated and repaired by Claude Opus 5.5 (`claude-opus-5-5`) on
2026-10-10. Not yet re-reviewed.

## Part A, code

| ID | Decision | Repair and evidence |
|---|---|---|
| I2B-1 High | AGREE, repaired | The caller-supplied loader is gone. `semi.exploration_returns(raw_root)` reads bars only through the existing `aqt.data.klines.build_exploration_manifest`, which refuses any other partition before a file is read, opens only the exploration months' archives (each checked against its sidecar) and keeps only bars inside `[WINDOW_START, WINDOW_END_EXCLUSIVE)`. It returns both manifest hashes for the qualification object (§3.4 item 1). The pure part is `joint_returns(series, start, end_exclusive)`, which refuses a wrong symbol order, a naive or non-whole-day window, and a window without a return day. Tests: `test_exploration_returns_read_only_through_the_exploration_builder` (the builder is the only reader, called with `"exploration"` for both symbols; the window is the protocol's); `test_joint_returns_refuse_a_bad_window_or_order`. The builder's own refusal and window filtering stay covered by `tests/unit/test_klines.py`. |
| I2B-2 Medium | AGREE, repaired | Left-out days are now a list of dates over every return day of the window (d and d − 1 both inside it), leading and trailing included; kept + left out = all return days. Test `test_joint_returns_list_every_left_out_return_day` (interior, leading, trailing). Joining the two sides of a gap in the source array is disclosed in proposal R-1, with an alternative, for the owner. |
| I2B-8 Medium | AGREE, repaired in part | Added: pinned fixed-seed vectors for the bootstrap and the signs; a scripted generator showing the sign-then-length order and a block boundary that keeps its sign (`test_block_signs_draw_sign_then_length_per_block`); the pre-refactor loop copied verbatim from 5664f0c and compared exactly with `benchmark_exposure`. The replication test is now described as an algebra check. **Carried:** stream independence of `"market"` and `"sign"` (§8), causality of exposures and QJ sharing cannot be tested before the libraries and the Q5/QJ assembly exist; they are tests of that step. |

## Part B, the proposal: for the owner

I2B-3 to I2B-7 concern the proposal, not built code. Each is a decision for the owner, together with R-1..R-6.

| ID | Drafter's view (advice, not a decision) |
|---|---|
| I2B-3 High, R-4 | Agree that a random K-subset certifies a mixture over designs, not each fixed design. Options: (a) keep the mixture and narrow the Q5/QJ claim and the §3.6 wording to it; (b) a fixed, frozen design per K. (b) keeps §3.6 as written. Changing §3.6 is a change to the accepted preregistration. |
| I2B-4 High, R-5 | Agree that the paths are less representative without the frozen 0.10 rebalance band and the 24-hour minimum hold for risk increases. On daily bars the band is cheap to apply, and the minimum hold equals the 1-day horizon. Recommend applying both, so that no simplification remains. |
| I2B-5 Medium, R-3 | Agree. The HAR weights, the GARCH ω and starting variance, and how an H-day forecast becomes σ̂ must be written as equations before the owner accepts R-3. The drafter will add them to the proposal. |
| I2B-6 Medium, R-2/R-3 | Agree. The proposal will state the timing: the price index is the cumulative product of the path's BTC returns, exposure on day t uses rows through t − 1, and refreshes fall on days 0, H, 2H, … counted from the start of the warm-up. Prefix invariance will be tested when the libraries are built. |
| I2B-7 Medium, R-3/R-4 | Agree that duplicates must be identified. Prefer alternative (b): replace the two duplicate EWMA horizons with `EWMA_72h` and `EWMA_336h`, which are allowed estimators. That removes the correlation-1 columns. |

No calibration was run.

## Checks after repair (2026-10-10, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_semi.py tests/unit/test_klines.py -q -p no:cacheprovider` | 0 | 45 passed |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 142 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_choose.py tests/unit/test_calibration_semi.py` | 0 | No issues in 69 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |

The rest of the suite was not rerun. The only change is to `calibration/semi.py` and its tests. No module other than `tests/unit/test_calibration_semi.py` imports `calibration.semi`, and `calibration/generator.py` is unchanged since the full run at 36ae0a9 (143 + 1801 passed).
