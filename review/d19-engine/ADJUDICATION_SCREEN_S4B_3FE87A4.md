# Adjudication of the Sol review of screen S4b at 3fe87a4

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. Review record: `SOL6_SCREEN_S4B_REVIEW_3FE87A4.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S4B-R1 | High | **Accept.** Trial code was loaded once per path, so a module global could carry rows from one run into the next (for example into the lagged G-6 run). | RN-3: `signal` and `overlay` are loaded afresh (fresh module globals) inside every run, with fresh state dicts. Test `test_trial_code_state_never_crosses_runs` (a global call counter that would exceed one window if shared). |
| S4B-R2 | High | **Accept.** C-10 (1) requires `s_h >= 0`; clipping hid negative values. | RN-3: a negative `s` makes the run unavailable, `NEGATIVE_SIGNAL`, before clipping. Test `test_a_negative_signal_is_refused`. |
| S4B-R3 | Medium | **Accept.** | RN-3a: each run keeps its `s` series; `class_mismatch` is applied to every run of a `constant_signal` trial, and a mismatch in any run makes G-11 `CLASS_MISMATCH`. Test `test_a_constant_signal_trial_is_checked_every_hour` (alternating and constant cases). |
| S4B-R4 | Medium | **Accept.** | RN-3: every value passed to trial code (the `s_inputs` row; the overlay's market row) and `sigma_hat` is checked before the call; non-finite is `INVALID_SERIES`. Disclosed in RN-3: the overlay receives every feature, so a non-finite feature it does not read still counts. Test `test_a_non_finite_input_is_unavailable_even_if_the_signal_ignores_it`. |

Also added at the reviewer's note: `test_an_unavailable_eth_check_carries_into_the_btc_gates` (a flat ETH path: G-3 `INVALID_SERIES`, G-5..G-7 `G-3:INVALID_SERIES`). RN-6 now states that `screen_gates` reports availability only; PASS or FAIL is not part of the screen's outcome (§7.2).

Not repaired: none.

Validation: `pytest tests/unit/test_calibration_screen.py tests/unit/test_feature_columns.py tests/unit/test_event_contract.py` 121 passed; ruff check and format clean; mypy clean; lint-imports 6 kept, 0 broken.
