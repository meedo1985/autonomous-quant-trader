# Adjudication of the Fable 5.1 review of the D-19 engine at aa3457b

Review: `review/d19-engine/FABLE_REVIEW_AA3457B.md` (FE-1..FE-8). Adjudicated
and repaired by Claude (Opus 5.5) on 2026-10-05.

| ID | Decision | Repair / reason |
|---|---|---|
| FE-1 MAJOR | AGREE, repaired | `start_gate(defn, root)` recomputes the code hash first and stops with "U_ops: start gate: engine code differs". `record` refuses unless `--engine-commit` is the checkout's HEAD and `git status --porcelain` is empty (git missing is a refusal). Tests: wrong commit and dirty checkout refused; an edit after recording stops the start. |
| FE-2 MAJOR | AGREE, repaired | `generator_sha256` covers `calibration/*.py` and all of `src/aqt/**/*.py` (the engine imports 13 `aqt` modules; a fixed whole-package hash avoids a stale list and import-order dependence). Consequence, recorded in the module docstring: the calibration runs from its own pinned checkout, never the forward-paper one, or every app update would stop it. Test: an edit of `src/aqt/metrics/statistics.py` stops the start. |
| FE-3 MAJOR | AGREE, repaired | `gates.g1/g10/g12/u_g` take an optional `trace` (G-1 block length and every replicate's two scaled Sharpes, G-10 split variances as bytes, G-12 ESS per horizon); availability logic unchanged (`u_g` now returns the first unavailable reason by short-circuit, same result). Reference vectors hash the benchmark leg and the trace, and add `refvec-k2-g2-unavailable` (a -150% day, G-2 INVALID_SERIES). Test: nudging `fast.mean_var` by 1e-15 changes the K = 5 vector without flipping availability. |
| FE-4 MAJOR | PARTIAL, repaired as provenance + procedure | Gating libc separately would be an amendment (BF5-1), so not done. `host_provenance()` now records SHA-256 of the libc/libm files mapped in `/proc/self/maps` (Linux), in every chunk, disclosed, never compared. The run procedure (module and script docstrings) requires the launcher to take `AQT_IMAGE_DIGEST` from `docker inspect` on the host, never typed. The launcher itself is part of the server runbook still to write. |
| FE-5 MINOR | AGREE, deferred to the driver | The run driver (not yet built) must build each `Chain` only from `binding=definition_sha256(defn)` and `gating=start_gate(defn, root)`, with a test of that order. Recorded here as a driver requirement. |
| FE-6 MINOR | AGREE, repaired | `within` checks K/T presence and the exact field set (for the window's own K) before finiteness; a missing field is an error even with a NaN; a real K/T mismatch is still a refusal. Test added. |
| FE-7 MINOR | AGREE, open owner/re-pilot item | A non-finite threshold draw stops the threshold run (fail closed). Before the threshold run, the re-pilot measures the non-finite-diagnostic rate per cell (Q5/QJ especially); if non-zero, its treatment goes to the owner as a decision. Not a code change now. |
| FE-8 MINOR | AGREE, repaired | Tests for identity change ("runtime differs"), code change, U_G numerics, lower-bound tie and below-bound refusal; run definition records `prereg_sha256` of the preregistration file (`--prereg-file`). |

Left unrepaired, with reasons: FE-5 (no driver yet; requirement recorded),
FE-7 (needs measured rate, then possibly an owner decision), FE-4's libc
gating (would be an amendment; provenance and procedure done instead).

## Checks after repair (2026-10-05)

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider` | 1821 passed, 9 skipped |
| `.venv/Scripts/python.exe -m ruff check .` / `ruff format --check .` | clean / 131 files formatted |
| `.venv/Scripts/python.exe -m mypy calibration src` | 62 files, no issues |
| `.venv/Scripts/lint-imports.exe` | 6 kept, 0 broken |
| `pwsh -NoProfile -File review/task6/verify_frozen.ps1` | PASS (28/28, 14/14, self-hash, 7/7, nested) |

Not yet re-reviewed by a different model.
