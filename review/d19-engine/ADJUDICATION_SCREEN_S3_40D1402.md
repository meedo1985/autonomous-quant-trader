# Adjudication of the Sol review of screen S3 at 40d1402

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-16. Review record: `SOL6_SCREEN_S3_REVIEW_40D1402.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S3-R1 | High | **Accept.** Hashing the file and then importing could return a cached older module, and a dotted name runs package `__init__` files. | TI-2: `load` compiles exactly the hashed bytes into a fresh `types.ModuleType` that is never put in `sys.modules`, and accepts only a `.py` source. What that module imports is bound elsewhere (image digest; the S7 driver's engine-commit check of loaded `aqt` / `calibration` modules, as `mapping.py` MP-4). Test `test_code_runs_from_exactly_the_hashed_bytes` (module imported, then edited: the edited bytes run, the cached module is untouched and stays registered). |
| S3-R2 | High | **Accept.** The grid was not tied to what runs. | TI-2 / TI-6: the signal is called as `signal(inputs, params)`, `params` = `parameter_point` without `tau` and `sigma`. `tau` and `sigma` can be grid dimensions only under those names; their point must equal the top-level field and their grid values must be allowed (TAUS; the family's sigmas). G-8 neighbour runs substitute grid values through the same path. Tests: two new refusal cases plus `test_sizing_dimensions_are_bound_and_kept_from_the_signal`. |
| S3-R3 | High | **Accept.** Applicability of G-14 must be fixed from declared fields, and `logistic` needs a preregistered sign objective (protocol `logistic_use`). | TI-5: `model` gains `target` ∈ {`vol_scaled_target`, `sign_of_vol_scaled_target`}; `logistic` requires the sign target and only `logistic` may use it. Both model the vol-scaled target at the trial's horizon, so `g14_applies` is true for every model trial (reading for review; the alternative, G-14 N/A for sign models, is listed in TI-5's wording by omission and would need a decision). Tests: three refusal cases, `test_g14_applies_to_model_trials_only`. |
| S3-R4 | Medium | **Accept.** | TI-4: `family` ∈ {`trend`, `vol`}, the families the D-19 calibration covers (`calibration/rules.py` FAMILIES). `fixed_size` and other names are refused. |
| S3-R5 | Medium | **Accept.** | TI-1: every mapping key (model params, parameter_point, grid) must be a non-empty string. Two refusal cases. |
| S3-R6 | Medium | **Accept** (helper now, enforcement in the runner). | TI-8: `overlay_violation(target, out)` is true for any hour where the output is neither the target nor 0, or a shape mismatch; the C-6 runner (S2/S4) must call it on every run. Test `test_the_overlay_may_only_keep_the_target_or_exit`. |

Not repaired: none. Carried to later slices: S3-R1's import binding (S7 driver check), S3-R6's per-run enforcement (runner).

Validation: `pytest tests/unit/test_calibration_screen.py` 46 passed; ruff check and format clean; mypy clean; lint-imports 6 kept, 0 broken.
