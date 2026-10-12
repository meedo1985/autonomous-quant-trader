# Adjudication of the GPT-6 Sol review of the D-19 run driver at 1789d0b

Review: `review/d19-engine/SOL6_DRIVER_REVIEW_1789D0B.md` (DR-1..DR-5). The
review confirmed R3-3, FE-5 and R6-1 are met by the spawn design. Adjudicated
and repaired by Claude (Opus 5.5) on 2026-10-05.

| ID | Decision | Repair |
|---|---|---|
| DR-1 BLOCKER | AGREE, repaired | Verified against prereg §8: namespace `"d19-threshold-v1"`, anchor "the preregistration hash" in threshold and development runs. The driver now uses that namespace and the run definition's `prereg_sha256` (SHA-256 of `PREREGISTRATION.md` read from the recorded preregistration commit); `seed_spec` no longer supplies an anchor. Reading "the preregistration hash" as the content SHA-256 of the file at the recorded commit is the AI's interpretation, disclosed here. Test: every stored draw equals `outer_seed(prereg_sha256, cell, "d19-threshold-v1", rep)` → generator → diagnostics. |
| DR-2 BLOCKER | AGREE, repaired | `generator.cells_from_manifest` refuses: not a list, no cells, entries without exactly the five fields, non-path-safe or duplicate ids, K outside {1, 2, 5, 20}, T < 16 or non-integer, unknown law or dependence, K = 1 with a dependence, clusters at K ≠ 5/20. `record` refuses such a manifest; the driver checks it before starting the pool and again in each worker. Tests: ten malformed manifests. |
| DR-3 BLOCKER | AGREE, repaired | The replication count is no longer a command-line argument: the manifest carries `purpose` (`qualification` or `pilot`) and `replications`, checked by `rundef.run_plan` (positive integers; a qualification run must use exactly 300,000 threshold draws per §13 item 4). Both are inside the run definition, so its hash binds them: a resume cannot change the count, and a different plan is a different binding. Tests: bad plans refused; with a 501-draw plan, a deleted second chunk plus a torn `.tmp` resume byte-identically; the 3-draw definition on the same store is refused (ChainError). |
| DR-4 NON-BLOCKING | AGREE, repaired | Each diagnostic is stored as its IEEE-754 binary64 bit pattern (`struct.pack(">d")` hex), keeping NaN payloads and signed zeros. |
| DR-5 BLOCKER | AGREE, repaired | Added: seeds test (DR-1); a chain carries exactly the gating the worker's own `start_gate` returned (a sentinel), not the definition's copy; real interruption resume (DR-3); malformed manifests and plans; changed plan on the same store. |

Requirements still carried (no full run before they pass review): FE-4
(launcher takes the digest from host `docker inspect`, applies `nice 19` and
`MemoryMax`), FE-7 (re-pilot measures non-finite threshold draws). Development
and held-out namespaces are not built.

## Checks after repair (2026-10-05)

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider` | 1862 passed, 9 skipped |
| `.venv/Scripts/python.exe -m ruff check .` / `ruff format --check .` | clean / 132 files formatted |
| `.venv/Scripts/python.exe -m mypy calibration src` | 62 files, no issues |
| `.venv/Scripts/lint-imports.exe` | 6 kept, 0 broken |
| `pwsh -NoProfile -File review/task6/verify_frozen.ps1` | PASS |
