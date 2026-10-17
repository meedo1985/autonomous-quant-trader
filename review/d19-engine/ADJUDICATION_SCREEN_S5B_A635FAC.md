# Adjudication of the Sol review of screen S5b at a635fac

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. Review record: `SOL6_SCREEN_S5B_REVIEW_A635FAC.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S5B-R1 | High | **Accept.** The 559-day test counted draw targets, not draw statistics. | `test_every_g11_draw_is_scored_and_one_bad_draw_makes_it_unavailable`: spies count 500 draw statistics on a clean run; a second run injects an unavailable statistic at draw 250, and G-11 reports it after exactly 250 scored draws. |
| S5B-R2 | Medium | **Accept.** | `test_a_g11_draw_overlay_sees_the_real_hour_and_starts_fresh`: for two shifts, the overlay receives the real-hour close of every window hour, unshifted, and its state starts empty in each draw. |

The reviewer's note that EC-4's length check cannot detect a wrong series of the right length is accepted as stated in EC-4: the caller (`screen_gates`' `prepare`) computes it from the same series, and the identity test covers that path.

Test-only change; `calibration/screen.py` and `event_contract.py` are unchanged.

Not repaired: none.

Validation: `pytest tests/unit/test_calibration_screen.py -k g11` 10 passed; ruff, mypy clean.
