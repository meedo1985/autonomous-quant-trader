# Adjudication of the Sol review of screen S6c at 01a5075

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. Review record: `SOL6_SCREEN_S6C_REVIEW_01A5075.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S6C-R1 | High | **Accept.** A NaN prediction returned without an exception could be ranked into a finite IC. | `spearman_ic` refuses any non-finite prediction or target first (`NONFINITE_IC_INPUT`, G14-4). Test case added to `test_spearman_ic_uses_midranks`. |
| S6C-R2 | Medium | **Accept.** The shift spy saw one refit window, and pipeline tests ran three draws. | `test_g14_runs_the_nominee_and_every_draw_in_every_window`: a 61-day window (three refits), spies on `g14_draw` and `walk_forward`: every draw `d` draws its own offset in every window `w = 0, 1, 2`, and G-14 runs the nominee plus one pipeline per draw. The frozen reference test, which runs unpatched, asserts `G14_DRAWS == 500`. |

Not repaired: none.

Validation: `pytest tests/unit/test_calibration_screen.py tests/unit/test_d19_deploy.py tests/unit/test_event_contract.py tests/unit/test_feature_columns.py` all passed with `-W error::FutureWarning`; ruff check and format clean; mypy clean; lint-imports 6 kept, 0 broken.
