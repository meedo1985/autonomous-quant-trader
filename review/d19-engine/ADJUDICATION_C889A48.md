# Adjudication of the GPT-6 Sol re-review of the D-19 engine at c889a48

Review: `review/d19-engine/SOL6_REREVIEW_C889A48.md` (R5-1, R5-2). Adjudicated
and repaired by Claude (Opus 5.5) on 2026-10-05.

| ID | Decision | Repair |
|---|---|---|
| R5-1 MAJOR | AGREE, repaired | `loaded_outside` checks every `aqt`/`calibration` module against the hashed inventory wherever it lies, including under `sys.prefix`; only non-engine modules of the interpreter's installation are skipped. Test: a fake `aqt.d19_fake` module under `sys.prefix` is reported. |
| R5-2 MAJOR | AGREE, repaired | `record` computes the code hash once, passes it to `build`, and immediately before writing re-runs the full HEAD-blob comparison and recomputes the hash; any difference writes nothing. Test: an engine file edited during `build` leaves no definition written (exit 1). |

Carried to the driver task unchanged (no full run before they pass review):
R3-3, FE-4, FE-5, FE-7.

## Checks after repair (2026-10-05)

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider` | 1837 passed, 9 skipped |
| `.venv/Scripts/python.exe -m ruff check .` / `ruff format --check .` | clean / 131 files formatted |
| `.venv/Scripts/python.exe -m mypy calibration src` | 62 files, no issues |
| `.venv/Scripts/lint-imports.exe` | 6 kept, 0 broken |
| `pwsh -NoProfile -File review/task6/verify_frozen.ps1` | PASS |
