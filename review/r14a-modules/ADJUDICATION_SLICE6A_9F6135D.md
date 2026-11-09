# Adjudication: Sol review of confirmation slice 6a at 9f6135d

- Review record: `SOL_CONFIRMATION_SLICE6A_9F6135D.md` (gpt-6-sol, high, verdict FIX).
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-09. The adjudication is the
  author's and approves nothing. The repairs are in the commit that adds this file.

| ID | Sol | Decision | Repair |
|---|---|---|---|
| R14S6A-S-1 | BLOCKER | **Accepted.** In a fresh process, `aqt.core.preregistration` was imported after R-14's loaded-module inventory had run, so a changed line-266 module would not have been checked. | `start` now runs the chain, reads the signed rows, calls `load_line266()`, and only then runs `verify_code` and the engine and image checks. Any failure after the load resets `_TRIAL_SEED` to None. ST-1 is reworded. Tests: in-process, `verify_code` sees `_TRIAL_SEED` set and preregistration loaded. In a fresh process, preregistration is absent before `start` and present when `verify_code` runs, and the jsonschema placeholders are gone afterwards. Image, engine and code failures after the load leave `_TRIAL_SEED` None. Chain failures still refuse before the load. |
| R14S6A-S-2 | BLOCKER (tests) | **Accepted.** | New tests. (1) For **both** loader copies, the file is replaced on disk between the hash check and execution (`compile` is patched to swap the file first); the module runs the hashed bytes (A, not B). A loader that re-read the file, for example through `exec_module`, fails this. (2) In a fresh process, a non-empty bytecode cache is refused by the frozen `bytecode_problem`, and so is a calibration module executed from a planted `.pyc` ("was not loaded from its source"). (3) The real `check_screen_code`, called through `cf.verify_code` with a synthetic engine inventory, passes with exactly the two modules and refuses a third loaded calibration module. |
| R14S6A-S-3 | QUESTION | **Left open, no code change: already an owner item.** This is the lockbox's inherited limitation, R14L2-S-2: the module checks that the acceptance record is consistent with the post but cannot establish that the post was accepted on chain. Who vouches for the record, and how its provenance is verified before `start`, is the open owner decision recorded in `check_acceptance`'s docstring. Binding it is a pre-signing item for both modules. | Recorded as LG6A-4. |

LG6A-1 (the confirmation signed rows deferred to 6b) and LG6A-3 (the 6b split) were
accepted by Sol as a sound build split. LG6A-2 (launch route) remains a pre-signing
blocker.

Validation: 366 passed (`pytest tests/unit/test_c2_confirmation*.py
tests/unit/test_c2_lockbox*.py tests/unit/test_d19_deploy.py`); ruff format and check
clean; `mypy src` clean; strict mypy on the module and the start test clean; lint-imports
7 kept. Sol re-check: one round.
