# Adjudication of the Sol review of screen S6a at 664b2ec

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. Review record: `SOL6_SCREEN_S6A_REVIEW_664B2EC.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S6A-R1 | High | **Accept.** WF-2 asks for refusal at declaration, and `check_trial` does not know `w0`. | `MODEL_WARMUP_HOURS = 731 * 24 + REQUIRED_HISTORY_BARS` (the most hours 24 calendar months can span, plus the feature history); `check_trial` refuses a model trial below it. `screen_gates` keeps the exact `w0`-specific check (`model_warmup_hours`). Test `test_a_model_trial_needs_its_training_window_as_warm_up`. |
| S6A-R2 | High | **Accept.** The compact candidate list lost calendar spacing, so ACF lags were not calendar lags. | `training_rows` passes `embargo_days` a calendar-day sequence from the first to the last candidate day with `None` for days without a candidate, exactly as `gap.py` does; `n` is the count of present labels. The embargo test now checks an every-other-day sequence against `gap.py` directly. (Model trials build one row per 00:00 instant of a contiguous path, slice S6b `model_column`.) |
| S6A-R3 | High | **Accept.** `sigma_bps[j - 3]` wrapped to the series end for `j < 3`. | `labels` refuses `j < 3` and an instant whose `P[t+H]` is beyond the series (`INSUFFICIENT_HISTORY`). Two test cases. |
| S6A-R4 | Medium | **Accept.** | `check_model_features` requires every entry to be a string before deduplicating. Test case `[[]]`. |

The reviewer's remark that the reproducibility test cannot detect a deterministic but wrong class or setting is noted: the class mapping is checked by reading `build_model` against WF-5 in review; a fixed-setting test would only restate the code.

Not repaired: none.

Validation: `pytest tests/unit/test_calibration_screen.py tests/unit/test_d19_deploy.py` 138 passed with `-W error::FutureWarning`; ruff check and format clean; mypy clean; lint-imports 6 kept, 0 broken.
