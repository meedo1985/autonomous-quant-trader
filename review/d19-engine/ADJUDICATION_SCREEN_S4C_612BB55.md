# Adjudication of the Sol review of screen S4c at 612bb55

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. Review record: `SOL6_SCREEN_S4C_REVIEW_612BB55.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S4C-R1 | Medium | **Accept.** C-8 step 1 (`N/A` without a dimension) comes before anything else. | PL-3: `screen_gates` classifies G-8's dimensions first; a `MODEL_PENDING` or `SIGMA_UNBOUND` trial without one gets G-8 `N/A`, and with one gets the same pending reason as the other gates. Test cases added to `test_model_and_unbound_sizing_trials_wait_for_their_slices`. |
| S4C-R2 | Medium | **Accept** (defence in depth). The R-8 `paired_sharpe_statistics` already returns `None` rather than a non-finite improvement, but C-8 step 2 says "not finite", so the screen checks it itself. | `leg_stats` treats a `None` or non-finite E-IMPROV as unavailable. Test `test_a_non_finite_e_improv_is_unavailable` (the statistic patched to return NaN). |
| S4C-R3 | Low | **Accept, with a reading.** A single-value grid entry has no neighbour and was not chosen among alternatives. Reading it as a boundary would make every fixed numeric constant an automatic G-8 FAIL, which C-8 cannot intend. | PL-1: an ordered numeric tunable dimension needs at least two values; a single value is a fixed constant. This is a drafting reading for review, not an owner binding (the owner's G-8 decision is about which settings count, and is unchanged). Test added. |

Also added: a test where the selected point itself fails (every gate unavailable, G-8 included).

Not repaired: none.

Validation: `pytest tests/unit/test_calibration_screen.py` 106 passed; ruff check and format clean; mypy clean; lint-imports 6 kept, 0 broken.
