# Adjudication of the GPT-6 Sol re-review of the D-19 engine at 90c64df

Review: `review/d19-engine/SOL6_REREVIEW_90C64DF.md` (R3-1..R3-4; RR-1 and
RR-4 confirmed repaired). Adjudicated and repaired by Claude (Opus 5.5) on
2026-10-05.

| ID | Decision | Repair |
|---|---|---|
| R3-1 MAJOR | AGREE, repaired | `record` resolves `--prereg-commit` with `git rev-parse --verify <c>^{commit}` and stores and reads the full commit ID. Test: `--prereg-commit HEAD` is stored as the full HEAD ID. |
| R3-2 MAJOR | AGREE, repaired | `start_gate` refuses unless the entry script (`__main__`) is hashed code under the checkout (`scripts/d19_*.py`, `calibration/*.py`, `src/aqt/**`), so a dirty or unhashed driver/launcher cannot pass; the driver must be a `scripts/d19_*.py` file. Tests: a launcher copy outside the hashed code is refused ("entry point is not hashed code"); the inventory holds `scripts/d19_run_definition.py` and `scripts/d19_pilot.py` and no other script. |
| R3-3 BLOCKER before a full run | AGREE, driver requirement | Not implementable before the driver exists. `start_gate`'s docstring now states it must run in every process that computes chunks, and each worker builds its `Chain` from `definition_sha256(defn)` and the returned gating. The driver's review must check this; no full run before it. FE-4 (digest from host `docker inspect`) remains a launcher requirement. |
| R3-4 MINOR | AGREE, repaired | `start_gate` itself is tested to refuse modules loaded outside the checkout (not only the helper); the G-10/G-12 trace test also asserts the final `reference_vectors()` hash changes; the inventory test covers the `d19_` entry points. |

Open requirements carried to the driver task (all must be met and reviewed
before any full run): R3-3 per-worker gate and Chain construction; FE-5 Chain
from the definition hash and gating only; FE-4 digest from host inspection;
FE-7 re-pilot measures non-finite threshold draws.

## Checks after repair (2026-10-05)

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider` | 1833 passed, 9 skipped |
| `.venv/Scripts/python.exe -m ruff check .` / `ruff format --check .` | clean / 131 files formatted |
| `.venv/Scripts/python.exe -m mypy calibration src` | 62 files, no issues |
| `.venv/Scripts/lint-imports.exe` | 6 kept, 0 broken |
| `pwsh -NoProfile -File review/task6/verify_frozen.ps1` | PASS |
