# Adjudication of the Sol re-review 2 of screen S3 at 0bda53c

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-16. Review record: `SOL6_SCREEN_S3_REREVIEW2_0BDA53C.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S3R2-R1 | High | **Accept.** numpy's own file input (`np.load`, `from numpy import load`) and `import *` let hashed code read an unhashed file. | `check_code` refuses `import *`, and the forbidden list (checked against names, attributes and `from` aliases) adds numpy file input and output: `load`, `save`, `savez`, `savez_compressed`, `loadtxt`, `savetxt`, `genfromtxt`, `fromfile`, `tofile`, `fromregex`, `memmap`, `DataSource`, `lib`, `ctypeslib`. Six new test cases. |
| S3R2-R2 | Medium | **Accept.** | `_code_ref` requires both parts to be identifiers, so `check_trial` refuses a dotted module for `signal` and `overlay` before hashing. The test fixture now uses a top-level name; two refusal cases. |
| S3R2-R3 | Medium | **Accept.** | `model.<name>` is compared with its JSON type (`_typed`): `True` is not `1`. Refusal test added. |

S3R-R3 is closed by the owner's decision (`OWNER_DECISION_S3R_R3_G14_SIGN_MODELS.md`, verbatim "Yes, apply it (Recommended)"): G-14 is mandatory for every model trial, logistic included. TI-5 now cites it; the code already had this default.

Not repaired: none.

Validation: `pytest tests/unit/test_calibration_screen.py` 62 passed; ruff check and format clean; mypy clean; lint-imports 6 kept, 0 broken.
