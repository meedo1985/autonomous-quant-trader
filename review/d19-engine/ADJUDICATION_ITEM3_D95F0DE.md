# Adjudication of the GPT-6 Sol review of D-19 engine item 3 at d95f0de

**Review:** `review/d19-engine/SOL6_ITEM3_REVIEW_D95F0DE.md` (ACCEPT; no I3
findings). The packet defect is disclosed in that record: the diff was empty,
and the reviewed `grid.py` and `run_plan` text is byte-identical to `d95f0de`.

**Adjudicated by:** Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-11. No
repairs were needed.

The reviewer made four points. None is a finding. Each is answered here:

| Point | Answer |
|---|---|
| The counts are checked by `run_plan`, not by `grid.problem`, and `PRESCRIBED` was not supplied. | Correct and intended: `run_plan` owns the counts. `PRESCRIBED = {"threshold": 300_000, "dev": 12_000}` (`calibration/rundef.py`, §13 rev 7g items 3–4). `test_a_bad_run_plan_is_refused` refuses a qualification manifest with other counts. |
| A qualification run might bypass `run_plan` through an unshown entry point. | Every entry point that records or runs a definition calls `run_plan`: `d19_run_definition.py record`, the driver's `main`, its `worker` and `d19_choose`. The packet listed those callers. No other script writes chunks. |
| The prereg-hash and T_C2 checks must exist before DR2-1 is lifted. | Agreed. This is a standing condition on lifting DR2-1, recorded in `ITEM3_QUALIFYING_GRID.md` ("Why qualification is still refused"). |
| The packet had no usable diff, and the tests were not attached. | The tests ran in the gate below. The review covered the code under review byte for byte, but not the tests. |

No calibration was run.

## Checks on `bfe1c23` (= `d95f0de` code plus the corrected review record)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest` the ten `tests/unit/test_calibration_*.py` files `-q -p no:cacheprovider` | 0 | 224 passed in 793.28 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those ten files | 0 | 1786 passed, 9 skipped in 365.49 s |
| `ruff check .` / `ruff format --check .` | 0 | All checks passed / 146 files already formatted |
| `mypy calibration src scripts/d19_run.py scripts/d19_run_definition.py scripts/d19_choose.py` | 0 | No issues in 71 source files |
| `lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28, 14/14, Constitution self-hash, 7/7, nested bindings pass |

An earlier gate was stopped and is not used. It had started before the item 3 commit existed (`index.lock`), so its results would have mixed two commits.

**Outcome:** item 3 is accepted for engine use. Qualification stays refused (DR2-1) until T_C2 (`g`), the accepted preregistration hash, the container image and the re-pilot exist.
