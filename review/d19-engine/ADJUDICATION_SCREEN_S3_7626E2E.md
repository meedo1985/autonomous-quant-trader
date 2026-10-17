# Adjudication of the Sol re-review of screen S3 at 7626e2e

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-16. Review record: `SOL6_SCREEN_S3_REREVIEW_7626E2E.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S3R-R1 | High | **Accept.** `find_spec` of a dotted name imports its package, and the hashed module could import unhashed local code. | TI-2: `module` must be top-level (`isidentifier`). `check_code` parses the hashed bytes: imports only `math` and `numpy` (image-bound), no relative import, no `__import__`, `importlib`, `exec`, `eval`, `compile`, `open`, `__builtins__`. Everything a trial's code can run is its hashed file or the image. A deliberate evasion of the name check is disclosed as a false declaration the check cannot rule out. Tests: `test_trial_code_is_self_contained` (7 cases), `test_a_package_module_is_refused`. |
| S3R-R2 | High | **Accept.** | TI-6: a model hyperparameter is a grid dimension only as `model.<name>`, with `<name>` in `model.params` at the point's value; a plain point name may not equal a `model.params` key. `model_params` gives the fit's parameters (neighbours override); `signal_params` excludes `model.` names. Test `test_model_hyperparameters_enter_the_grid_only_as_model_dimensions`. |
| S3R-R3 | High | **Accept as a decision item, not repaired.** Whether C-12 (1) covers a logistic model of the sign of the vol-scaled target is a clause-specific binding; AI cannot settle it. | TI-5 marked PENDING. The code keeps the stricter default (G-14 mandatory for every model trial) until the owner decides. Asked of the owner on 2026-10-16. |
| S3R-R4 | Medium | **Accept.** | Tests now cover a package module, the import restrictions, `g14_applies` for the logistic declaration, and a vol-family sigma point that differs from the top-level sigma. |

Not repaired: S3R-R3, pending the owner's decision (reason above).

Validation: `pytest tests/unit/test_calibration_screen.py` 55 passed; ruff check and format clean; mypy clean; lint-imports 6 kept, 0 broken.
