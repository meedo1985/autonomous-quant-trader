# Task gate: freeze runs T1b in the pinned image

**LOCAL GATE: PASS** (2026-11-01, branch `freeze-runs-t1b`, base main `f715dfe`).

## Task

PR #81's gate (`review/pre-freeze-screen/TASK_GATE.md`, item 2) left one obligation:
T1b (the screen's `paths` reference vector, computed, equals the frozen one) must
run in the pinned image before step G. The image has no pytest and `d19.sh` had no
command for it. Owner chose this fix on 2026-11-01 ("ok go ahead with 1").

## Change

| File | What |
|---|---|
| `scripts/d19_screen.py` | `vectors` subcommand: exit 0 if `screen_reference_vectors() == FROZEN_REFERENCE_VECTORS`, else refusal, exit 1 |
| `deploy/calibration/d19.sh` | `engine()` mounts `${CODE:-$APP}`; `CODE=""` at top level (T1BF-S-1); `freeze` runs `d19_screen.py vectors` on the build commit's clone, no network, before the build, then clears `CODE` |
| `.github/workflows/ci.yml` | launcher job requires the T1b pass line before the expected pilot refusal |
| `tests/unit/test_d19_deploy.py`, `tests/unit/test_calibration_screen.py` | order/clear checks, inherited-`CODE` run (T1BFR-S-1), CLI exit codes |
| `review/deployment/SERVER_EVIDENCE_2026-11-01_F715DFE.md` | paper server deployment record (separate, docs only) |

`calibration/screen.py` is unchanged; its sha in `FREEZE_REVIEWS.json` stays valid.

## Validation (Windows laptop, `.venv` Python 3.14)

| Command | Result |
|---|---|
| `python -m ruff check .` | pass |
| `python -m ruff format --check .` | pass (177 files) |
| `python -m mypy src` | pass (56 files) |
| `lint-imports` | 7 kept, 0 broken |
| `sh -n deploy/calibration/d19.sh` | pass |
| `pytest tests/unit/test_calibration_*.py tests/unit/test_d19_deploy.py` (at 3ba1bef) | 482 passed, 1 skipped (T1b, off-image) |
| `pytest --ignore-glob="tests/unit/test_calibration_*"` (at 3ba1bef) | 1856 passed, 9 skipped |
| `pytest tests/unit/test_d19_deploy.py` (at bd0276f, after both repairs) | 11 passed |
| `python scripts/d19_screen.py vectors` (off-image) | refusal, exit 1 (expected) |

The repairs after 3ba1bef touch only `d19.sh`'s top-level `CODE=""` and
`test_d19_deploy.py`; the full suites were not rerun after them (laptop memory;
the deploy file covers the change). **The in-image T1b run is CI's launcher job**;
it must be green on the PR head before merge.

## Frozen files

`git rev-parse` of `docs`, `protocols`, `schemas`, `specs`, `FROZEN_HASHES.json`
are identical at `f715dfe` and the branch head. Sidecar hashes not re-verified
independently (`verify_frozen.ps1` needs PowerShell 7, absent); no frozen path is
in the diff.

## Reviews

- Sol (gpt-6-sol) FIX T1BF-S-1 -> repaired: `SOL_REVIEW_3BA1BEF.md`.
- Sol re-check ACCEPT WITH NOTES T1BFR-S-1 -> repaired (test only, not re-reviewed): `SOL_RECHECK_4477A82.md`.
- Quant/reproducibility: launcher plumbing; no statistic, data or model changed. The check compares the build commit's screen (the one `qobj.build` copies and `declare()` later checks) in the image the run uses.

## Outstanding before merge

1. CI green on the PR head, including the launcher job's T1b pass line (first in-image run).
2. Owner §16 PR review (launcher is protocol-enforcement code).

After merge: G0 redo at the merge commit (not `f715dfe`), and the freeze sheet's
FP2 (d) / step G commits updated; the sheet's "T1b must run before G" becomes "freeze runs T1b".
