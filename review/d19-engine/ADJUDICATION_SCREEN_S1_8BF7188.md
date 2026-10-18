# Adjudication of the Sol review of screen S1 at 8bf7188

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-16. Review record: `SOL6_SCREEN_S1_REVIEW_8BF7188.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S1-R1 | Medium | **Accept.** Joining common hours into adjacent rows let a 168-row block step across a missing hour, so "mean block 168 h" was 168 rows, not hours. §7.2 says hours. | SP-2: `hourly_indices` restarts a block (one uniform index) wherever the next row is not the next clock hour, and at the end of the source instead of wrapping. Blocks are always consecutive clock hours. The bootstrap now lives in `screen.py` (bound by its bytes); `semi.stationary_indices` is unchanged. Test `test_a_block_never_continues_across_a_missing_hour_or_the_end`. |
| S1-R2 | High | **Accept.** Real BTC/ETH bars make it practically impossible (exp needs a cumulative log move above ~709), but the code must not return a non-finite or zero price silently. | SP-7: `reconstruct` raises `PathUnavailable` for any non-finite or non-positive price; the S7 driver records it as a procedure failure, never repairs it. Test `test_a_path_that_overflows_or_underflows_is_unavailable`. |
| S1-R3 | Medium | **Accept.** numpy gives `Generator` methods no cross-version stability. | SP-6 now says the draws are reproducible on the pinned numpy 2.5.3, and the frozen hash detects a change. |

Reference draws hash changed (end-of-source restart and the gap rule): new value in `tests/unit/test_calibration_screen.py`. The first-bar float vector is unchanged.

Not repaired: none.

Validation: `pytest tests/unit/test_calibration_screen.py tests/unit/test_calibration_qobj.py` 31 passed; ruff check and format clean; mypy clean; lint-imports 6 kept, 0 broken.
