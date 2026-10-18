# Adjudication of the Sol re-review of S6a and review of S6b at b00d59b

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. Review records: `SOL6_SCREEN_S6A_REREVIEW_B00D59B.md`, `SOL6_SCREEN_S6B_REVIEW_B00D59B.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S6AR-R1 | Medium | **Accept.** The model warm-up comparison ran before the warm-up's type check. | `check_trial` compares only an `int` warm-up; any other type reaches the existing `TrialError`. |
| S6B-R1 | High | **Accept.** Inference was limited to decisions with realised labels, so the window's last `H` days had no emission. | `walk_forward` (new, shared by the nominee and G-14 null pipelines) trains on decisions whose label is realised by each refit but predicts at **every** 00:00 window decision; `model_column` builds the hourly input from it. Test `test_emissions_cover_every_window_decision_at_long_horizons` (H = 168 h, every gate available). |
| S6B-R2 | Medium | **Owner decided** (2026-10-17, `OWNER_DECISION_MR1_ETH_OWN_FIT.md`): "Train on Ethereum's own data (Recommended)". | MR-1 now cites the decision; behaviour unchanged. |
| S6B-R3 | Low | **Accept, correcting the design instead of the code.** The first training decision `j` reads row `j - 1`, which needs `j - 1 >= REQUIRED_HISTORY_BARS - 1`, so the warm-up need is exactly the 24-month span plus `REQUIRED_HISTORY_BARS`; the design's "+ 1" was one hour too many. | `SCREEN_S6_DESIGN.md` WF-2 and MR-4 state the exact bound and its derivation. |

The reviewer's note that the G-6 test checked only that predictions differ: `test_g6_reinfers_from_exactly_the_previous_hour_row` now records the rows passed to `predict` and asserts they are exactly the feature rows of bar `j - 2`.

Not repaired: none.

Validation: `pytest tests/unit/test_calibration_screen.py tests/unit/test_d19_deploy.py` 146 passed with `-W error::FutureWarning` (G-14 at 3 draws in tests; 500 in production); ruff check and format clean; mypy clean; lint-imports 6 kept, 0 broken.
