# Adjudication of the Sol review of screen S4a at ebf0c8a

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. Review record: `SOL6_SCREEN_S4A_REVIEW_EBF0C8A.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S4A-R1 | Major | **Accept.** A blanket finite check refused rows the factory returns (`atr_24 = inf` from a finite mean true range over a subnormal close). | The blanket check is removed; `feature_columns` applies exactly the factory's own checks (`_require_finite` on the EMA, SMA, each `rv_*`, `ewma_vol_168h` and the mean true range before division; `log_return` and `true_range` check themselves). Unchecked derived ratios are returned as computed. Test `test_a_value_the_factory_returns_unchecked_is_returned` (the reviewer's case: exact equality with the factory row, `atr_24 = inf`). |
| S4A-R2 | Medium | **Accept.** | The factory's interval check is added before anything else, and a `CostModelError` from the EWMA series is re-raised as `FeatureFactoryError`, as `ewma_volatility` does. Test `test_a_non_hourly_series_is_refused`. |

The reviewer's remark that the private helpers need reassessing if the runtime changes is recorded here; the pinned image binds them (R-8).

Not repaired: none.

Validation: `pytest tests/unit/test_feature_columns.py` 5 passed; ruff check and format clean; mypy clean; lint-imports 6 kept, 0 broken.
