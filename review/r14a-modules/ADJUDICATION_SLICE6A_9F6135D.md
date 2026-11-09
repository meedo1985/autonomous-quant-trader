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

## Re-check (SOL_CONFIRMATION_SLICE6A_RECHECK_4FA758F.md, verdict FIX)

Sol closed R14S6A-S-2; it found S-1 and S-3 only partly closed. S-3 remains the owner and
pre-signing item LG6A-4.

| ID | Sol | Decision | Repair |
|---|---|---|---|
| R14S6AR-S-1 | BLOCKER | **Accepted.** Line 266's modules were imported, and so executed, before any byte check. | `line266_sources(root, engine_commit)` takes the SHA-256 of each line-266 module's blob at the **signed** engine commit: `aqt.core.paths`, then `aqt.core.preregistration`, which are the only modules the import newly loads; the others are already loaded with this module. `load_line266(sources)` runs each not-yet-loaded one from exactly those bytes, through `load_verified`, and refuses if the import adds any other `aqt`/`calibration` module. The post-load inventory check is kept. Tests, in fresh processes: authenticated bytes load; with a wrong preregistration digest it **never enters `sys.modules`**, so it never executes; leaving `aqt.core.paths` out of the sources is refused as unauthenticated. `line266_sources` matches the git blobs at HEAD and refuses an unknown commit. |
| R14S6AR-S-2 | BLOCKER | **Accepted, with Sol's first correction.** | Any refusal in `start` sets `_START_FAILED`; every later `start` in that process refuses with "retry in a fresh process". Test: refuse, then a valid start is still refused. |
| R14S6AR-S-3 | NON-BLOCKING | **Accepted.** | `start` clears `_TRIAL_SEED` on entry. Test: one success, then a refused second attempt, leaves it None. |

Residual, recorded: modules already loaded before `start` (`aqt.core.ledger`,
`aqt.data.manifest`, and everything this module imports) are the launch route's concern
(LG6A-2, R14D3-S-2), as for the lockbox. Whether import-time code could reach confirmation
data depends on the open access mechanism (DESIGN §10). 6b obtains the read only after
`start` returns.

Validation: 371 passed (same suites); ruff format and check clean; `mypy src` clean;
strict mypy on the module and the start test clean; lint-imports 7 kept.

## Second re-check (SOL_CONFIRMATION_SLICE6A_RECHECK2_EB00731.md, verdict FIX)

Sol closed R14S6AR-S-2 and S-3, accepted the launch-route boundary (LG6A-2), and found
R14S6AR-S-1 partly closed.

| ID | Sol | Decision | Repair |
|---|---|---|---|
| R14S6AR2-S-1 | BLOCKER | **Accepted.** An `aqt`/`calibration` module imported *by* an authenticated line-266 module could execute from disk before the after-the-fact check refused it. | While line 266 loads, `load_line266(sources)` inserts an import gate at the front of `sys.meta_path`. Its `find_spec` raises `SeedError` for any `aqt`/`calibration` module that is not yet loaded and not in the authenticated sources, **before** the import system can execute it. The gate is removed in `finally`. The after-load check stays as a second line. Fresh-process test: an authenticated module imports a probe module whose top-level code writes a marker file; the import is refused, the marker file never exists, and the gate is gone afterwards. The earlier unauthenticated-`aqt.core.paths` test now shows refusal by the gate, with preregistration never left loaded. |
| R14S6AR2-S-2 | NON-BLOCKING | **Accepted.** | Test: `start` asks `line266_sources` for `(root, the signed engine_commit row)`, and the very mapping returned reaches `load_line266` unchanged (identity checked). |

Validation: 373 passed (same suites); ruff format and check clean; `mypy src` clean;
strict mypy on the module and the start test clean; lint-imports 7 kept.

## Third re-check (SOL_CONFIRMATION_SLICE6A_RECHECK3_9C5D5DF.md, verdict FIX)

Sol closed R14S6AR2-S-2 and found R14S6AR2-S-1 (and so R14S6AR-S-1) still partly closed.

| ID | Sol | Decision | Repair |
|---|---|---|---|
| R14S6AR2-S-1 (rest) | BLOCKER | **Accepted, with Sol's correction.** The gate allowed listed names: a listed module imported before its verified turn, a reload, or a repository file loaded under another name could still run from disk. | The gate now refuses **every** finder lookup in the load window, whatever the name. Two facts make this safe. The verified modules never pass through the import system (`load_verified` executes their hashed bytes directly). And a real line-266 load on this engine adds only `aqt.core.paths` and `aqt.core.preregistration` (checked in a fresh process), so no legitimate lookup is refused. Fresh-process tests: a listed module imported early, a reload of `calibration.seeds`, and an import of a module outside aqt/calibration (`zipapp`) are each refused before any code runs, the marker is never written, and the gate is removed. The authenticated full load still succeeds. |
| R14S6AR3-S-1 | NON-BLOCKING | **Accepted.** | The gate is installed inside the `try`. Test: a `sys.meta_path` whose `insert` raises after inserting leaves no gate behind. |

Validation: 377 passed (same suites); ruff format and check clean; `mypy src` clean;
strict mypy on the module and the start test clean; lint-imports 7 kept. This repair
applies Sol's stated minimal correction and was not re-sent to Sol, after four rounds on
6a. Another round is available on request.
