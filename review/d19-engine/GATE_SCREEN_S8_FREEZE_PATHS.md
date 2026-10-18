# Task gate: S8 freezes the screen's `paths` reference vector

Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-18, applying `task-gate-review`, `scientific-reproducibility-review` and `quant-code-review`. This is a local gate. It is not an independent review and not the owner's §16 review.

**Base:** `c9a5ad3` (screen-plan). **Task:** SCREEN_PLAN.md S8 / DR-6 (S7-R4): freeze `FROZEN_REFERENCE_VECTORS["paths"]` in `calibration/screen.py` from the pinned image, before any real screen.

## Change

- `calibration/screen.py`: `"paths": None` becomes `"99e244543c3bc0e906d85fd5b607e4a45a595183e9eee4a646f3d2b86d5d2152"`. The comment names the evidence.
- `tests/unit/test_calibration_screen.py`: asserts the frozen value. The `not frozen yet` refusal is still tested, with `paths` patched back to `None`.

No other logic changes. `screen_reference_vectors()` and the `declare` guards are unchanged.

## Provenance (scientific reproducibility)

- The value is the `reference vectors` line of `screen-summary` from the third pilot (`PILOT_SCREEN_EVIDENCE.md`, step C, commit `c9a5ad3`). That pilot ran on engine `4fed8f5` in image `54bfcf5394cb`, with the probe reporting the pinned runtime.
- The record computes it with `run_screen` → `screen_reference_vectors()` in the `d19_screen.py` process. That process sets `OPENBLAS_NUM_THREADS=1` and `OPENBLAS_CORETYPE=Haswell` at import (`scripts/d19_screen.py:32-33`). The summary shows one job runtime, the pinned one.
- The same pilot reproduced `g11` and `g14` exactly as already frozen: the input and code path are the ones expected.
- The laptop gives `paths` = `9d247856…6f4b`: not the pinned image, so a different value is expected for the float path (S7-R4). This is why the test asserts the constant and does not recompute it.
- **Limitation:** the value comes from one computation on the server. It is not reproduced independently. This fails closed: `declare` recomputes the vectors and refuses on any difference (`calibration/screen.py`, `declare`). A wrong frozen value blocks a declaration; it cannot pass a wrong screen.

## Quant review

The change touches no data flow, timing, costs, partitions or selection. The applicable areas are N/A for this change, because it only moves a guard from "refuse, not frozen" to "refuse unless equal". Gate semantics: G-8 `N/A` rows in the pilot are PL-3 frozen N/A (`g8_na`), so `ALL_AVAILABLE` is consistent.

## Validation (Windows laptop, `.venv`, Python of the repository venv)

| Command | Result |
|---|---|
| `ruff format --check .` | exit 0, 173 files already formatted (after `ruff format` of the test file) |
| `ruff check .` | exit 0, all checks passed |
| `mypy src` | exit 0, no issues in 55 files |
| `lint-imports` | exit 0, 6 contracts kept, 0 broken |
| `pytest tests/unit/test_calibration_screen.py` | exit 0, 163 passed |
| `pytest --ignore-glob="tests/unit/test_calibration_*"` | exit 0, 1814 passed, 9 skipped |
| `pytest tests/unit/test_calibration_*.py tests/unit/test_d19_deploy.py --deselect tests/unit/test_calibration_screen.py` | exit 0, 297 passed, 163 deselected (the screen file, run above) |

The CI calibration job pins `numpy==2.5.3`, `scikit-learn==1.9.1` and `lightgbm==4.7.0` on Linux; this run used the laptop venv. CI runs on the PR.

## Frozen artifacts

`git diff --name-only c9a5ad3 -- docs protocols schemas specs FROZEN_HASHES.json` is empty. No sidecar or hash was touched.

## Findings

| ID | Class | Finding |
|---|---|---|
| G-FP-1 | NON-BLOCKING | Single server computation (see Limitation). It fails closed. A second computation comes free with the first real `declare`. |

**LOCAL GATE: PASS.** The independent review and the owner's §16 PR review are outstanding. `calibration/screen.py` is in qobj's `REVIEWED` set.
