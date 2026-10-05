# Adjudication of the GPT-6 Sol re-review of the D-19 engine at adaa192

Review: `review/d19-engine/SOL6_REREVIEW_ADAA192.md` (R4-1, R4-2; R3-1, R3-2,
R3-4 confirmed; R3-3/FE-4/FE-5/FE-7 accepted as driver requirements provided
no full run starts before they pass review). Adjudicated and repaired by
Claude (Opus 5.5) on 2026-10-05.

| ID | Decision | Repair |
|---|---|---|
| R4-1 MAJOR | AGREE, repaired | `loaded_outside` now reports any loaded module whose file is inside the checkout but is not hashed code (e.g. `calibration/extra/worker.py`, a script helper), plus `aqt`/`calibration` modules loaded from elsewhere. The interpreter's own installation (`sys.prefix`, `sys.base_prefix`; a virtual environment may sit inside the checkout) is excluded: it is gated by the runtime identity. Test: a nested helper added after recording is reported and absent from the inventory. |
| R4-2 MAJOR | AGREE, repaired | Every git call uses `--no-replace-objects`; HEAD is captured once (`rev-parse --verify HEAD^{commit}`) and that ID is used for `ls-tree` and every `show`; `record` re-reads HEAD before writing and refuses if it moved. Test: with `git replace A B` and a working tree matching B, recording A is refused. Mutation check: removing `--no-replace-objects` makes that test fail. |

Carried to the driver task unchanged (no full run before they pass review):
R3-3, FE-4, FE-5, FE-7.

## Checks after repair (2026-10-05)

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider` | 1835 passed, 9 skipped |
| `.venv/Scripts/python.exe -m ruff check .` / `ruff format --check .` | clean / 131 files formatted |
| `.venv/Scripts/python.exe -m mypy calibration src` | 62 files, no issues |
| `.venv/Scripts/lint-imports.exe` | 6 kept, 0 broken |
| `pwsh -NoProfile -File review/task6/verify_frozen.ps1` | PASS |
