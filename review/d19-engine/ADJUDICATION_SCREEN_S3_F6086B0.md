# Adjudication of the Sol re-review 5 of screen S3 at f6086b0

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-16. Review record: `SOL6_SCREEN_S3_REREVIEW5_F6086B0.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S3R5-R1 | High | **Accept.** `from numpy import f2py` passed: the hook checked the module name, not the fromlist. | Trial code may not use `from ... import` at all (except `from __future__`): `check_code` refuses it, and `_code_import` raises on any non-empty fromlist. The forbidden attribute names add numpy's tool submodules and helpers `f2py`, `testing`, `rec`, `ma`, `dump`, `dumps`, `loads`, `show_config`, `show_runtime`, `info`, so `np.f2py` is refused too. Tests: five static cases (including `from math import sqrt`, `np.f2py`, `np.testing`, and an allowed `from __future__`), one run-time case. |

Residual, disclosed in TI-2: numpy is large, and a deliberate evasion through objects it returns is a false declaration these checks cannot rule out.

Not repaired: none.

Validation: `pytest tests/unit/test_calibration_screen.py` 79 passed; ruff check and format clean; mypy clean; lint-imports 6 kept, 0 broken.
