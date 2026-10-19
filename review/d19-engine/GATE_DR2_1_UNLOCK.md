# Gate: DR2-1 unlock mechanism and qualification cell list (full-run precondition P3)

Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-18, applying `task-gate-review`, `scientific-reproducibility-review` and `quant-code-review`. A local gate; not Sol's review, not the owner's §16 PR review.

**Authorization:**
- the owner's answer "Yes, build it now (Recommended)" (2026-10-18), to build P3 now with the value left empty;
- the build-order decision `OWNER_DECISION_BUILD_ORDER.md`, with its review `SOL6_BUILD_ORDER_REVIEW_D321147.md`.

## Change

| File | What |
|---|---|
| `calibration/rundef.py` | `ACCEPTED_PREREG_SHA256: str \| None = None`. `run_plan(manifest, prereg_sha256)` admits a qualification manifest only when that constant is set and equals `prereg_sha256`; otherwise it refuses as before. Pilot plans are unchanged. |
| `scripts/d19_run.py` | Every `run_plan` call passes the run definition's `prereg_sha256`: the job set-up, each worker, and `dev_bounds`. |
| `scripts/d19_run_definition.py` | `record` passes the hash of the preregistration bytes it reads at `--prereg-commit`, the same bytes it records. |
| `deploy/calibration/qualification-cells.json` | `grid.manifest(T_C2, PRESCRIBED)`: 104 cells, threshold 300,000, dev 12,000. |
| `tests/unit/test_calibration_rundef.py` | The file equals the grid manifest. A refusal while nothing is pinned, and for any other or missing hash; admitted only for the pinned hash. |

**Effect today: none.** The constant is `None`, so every qualification run is still refused, as before. The refusal message changes; its prefix `qualification runs are refused` is kept. Pinning the value is a later one-line change, after the owner's acceptance record. It goes through its own review and PR.

## Reproducibility and quant notes

- The hash the run compares is the run definition's `prereg_sha256`. `record` computes it from the preregistration file at the full commit ID it resolves. The workers' seed check (DR2-2) already requires the seed anchor to equal it, so one value binds the seeds and the admission.
- No statistic, threshold, seed, generator or chain format changes. Chunks already written are unaffected; no qualification chunk exists.
- The cell list is a pure function of `T_C2` and `PRESCRIBED`, and the test pins it.

## Validation (Windows laptop, `.venv`)

| Command | Result |
|---|---|
| `ruff format --check .`, `ruff check .` | exit 0 |
| `mypy src` | exit 0 |
| `lint-imports` | exit 0, 7 kept |
| `pytest tests/unit/test_calibration_*.py tests/unit/test_d19_deploy.py` | 462 passed (16 min 24 s), exit 0 |

No frozen file changed.

**LOCAL GATE:** PASS.

## Repair of Sol's review (DR21-R1, DR21-R2), 2026-10-19

Review `SOL6_DR2_1_UNLOCK_REVIEW_C536943.md` (FIX); adjudication `ADJUDICATION_DR2_1_UNLOCK_C536943.md`; repair commit `2057ad3`.

| Command | Result |
|---|---|
| `ruff format --check .`, `ruff check .` | exit 0 |
| `mypy src` | exit 0 |
| `lint-imports` | exit 0, 7 kept |
| `pytest tests/unit/test_calibration_*.py tests/unit/test_d19_deploy.py` (repair uncommitted) | 454 passed, 9 failed: every failure is `test_calibration_heldout.py`'s check that the loaded `scripts/d19_run.py` equals the committed one, which an uncommitted edit fails by design |
| `pytest tests/unit/test_calibration_heldout.py` at `2057ad3` (clean tree) | 20 passed |
| new DR21-R1 test against the old `scripts/d19_run.py` | fails (reproduced) |

No frozen file changed.

**LOCAL GATE (repair):** PASS.
