# Local gate: confirmation slice 6a (start chain, loader, start)

- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-09, applying `task-gate-review`,
  `scientific-reproducibility-review`, `quant-code-review`. Self-review by the author; the
  independent review is Sol (`SLICE6A_PROMPT_SOL.md`).
- Scope: DESIGN §4 (loading and the start check; "each module carries its own copy of
  this sequence ... a test checks that the two copies are identical"), §5.2 step 1, §5.1
  (line 266 before any protected read). Slice 6 is split: **6b** is the evaluation run
  (steps 2-8) and the C2 evaluation record. It depends on owner items: the
  confirmation-specific signed rows (OD-4), the confirmation partition access path, and
  the store interface (DESIGN §10).
- Finding IDs: LG6A-n. **LOCAL GATE: PASS** (no open blocker), items in §5.

## 1. Changed files

- `calibration/c2_confirmation.py` (appended; new stdlib imports `importlib.util`, `sys`,
  `types`, `Path`, `Mapping`):
  - the lockbox's section "the start chain and the loader", copied verbatim by script from
    `c2_lockbox.py` (comments included): `POST_SCRIPT_PREFIX`, `MODULE_ROWS`,
    `MODULE_PATHS`, `SIGNED_ROWS`, `ChainError`, `parse_tx`, `txid`,
    `post_declaration_sha256`, `ACCEPTANCE_*`, `MIN_CONFIRMATIONS`, `check_acceptance`,
    `protocol_row`, `verify_chain`, `load_verified`, `verify_code`;
  - then the module's own `Started` and `start`.
- `tests/unit/test_c2_confirmation_start.py` (new, 30 tests).

## 2. Validation (Windows 11, repo `.venv`, Python 3.14)

| Command | Result |
|---|---|
| `pytest tests/unit/test_c2_confirmation_start.py` | 30 passed |
| `pytest tests/unit/test_c2_confirmation*.py tests/unit/test_c2_lockbox*.py tests/unit/test_d19_deploy.py` | 358 passed (engine import test still `['numpy']`) |
| `ruff format --check .`, `ruff check .` | clean |
| `mypy src` | no issues (56 files) |
| `mypy --strict` module + new test | no issues |
| `lint-imports` | 7 kept, 0 broken |

## 3. Frozen artifacts

None touched; `c2_lockbox.py` is read (copied from), not changed.

## 4. Self-review

- Identity: the whole copied section equals the lockbox's text, comments included. Each
  copied function's `inspect.getsource` and each constant (including `_HEX`) also equal
  the lockbox's. Neither module imports the other.
- `start` (ST-1): the chain runs over both module files as on disk. The signed values are
  read from the verified protocol bytes. Then the code check, the engine-commit check and
  the image check run, and only then `load_line266`. Six broken links each refuse with
  `ChainError` before line 266 loads: a swapped module file, the declaration, the protocol,
  the acceptance record, the image, the engine commit. A failed line-266 load raises
  `SeedError`. A real start leaves `_TRIAL_SEED` set. `Started` is frozen and its chain
  log read-only.
- Frozen `rundef.bytecode_problem()` passes in a fresh process. In it, the real
  confirmation file is loaded by the lockbox's `load_verified`, then the real lockbox file
  by the confirmation's copy (DESIGN §4 test, R14D3-S-1).

## 5. Items left open

- **LG6A-1 [DESIGN] ST-2:** the confirmation-specific signed values (the drand chain key,
  genesis and period, z_crit, T_min, g, the classifier) are not read in 6a. Their row
  names are an owner item (OD-4), and 6b reads them from `Started.protocol`.
- **LG6A-2 (pre-signing, R14D3-S-2):** the launch route is still open, as for the lockbox.
  `start` cannot establish that the running bytes are these files.
- **LG6A-3 (slice 6b):** steps 2-8 (declaration validity, seeds, per-trial runs and
  `d_sha256`, the look, nominee gates, C-14, sealing, the evaluation record). The open
  inputs are the confirmation partition read path and the store interface (DESIGN §10).
  Earlier slices left wiring items for 6b: R14S4-S-3 (lockbox lookup by family and trial
  id), SV1-S-6 (sealing handoff), LG5-2/LG5-3 (evaluation-record hash, `d_sha256`
  encoding), LG5-7, LG5B-6.

Claude/Sol status: prompt `SLICE6A_PROMPT_SOL.md`, sent with this commit.
- **LG6A-4 [OWNER] acceptance-record provenance (R14S6A-S-3):** inherited from the lockbox (R14L2-S-2). The chain checks that the record is consistent with the post, not that the post was accepted on chain. Binding who vouches for it is pre-signing, for both modules.
