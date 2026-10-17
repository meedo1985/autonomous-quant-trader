# Adjudication of the Sol re-review of screen S4a at d73d72b

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. Review record: `SOL6_SCREEN_S4A_REREVIEW_D73D72B.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S4AR-R1 | Medium | **Accept.** A gapped series raised `BarSemanticsError` (from `BarSeries.require_contiguous`) where the factory raises `FeatureFactoryError`. | `feature_columns` now checks the length first and then calls the factory's own `_require_contiguous_hourly`, in the factory's order. The gap test asserts `FeatureFactoryError` from both `feature_columns` and `compute_features`. |

Not repaired: none.

Validation: `pytest tests/unit/test_feature_columns.py tests/unit/test_calibration_screen.py` 101 passed; ruff check and format clean; mypy clean; lint-imports 6 kept, 0 broken.
