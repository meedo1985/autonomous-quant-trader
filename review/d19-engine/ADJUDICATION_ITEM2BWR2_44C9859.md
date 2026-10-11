# Adjudication of the GPT-6 Sol re-review 2 of item 2b step 1 at 44c9859

**Review:** `review/d19-engine/SOL6_ITEM2B_Q5_WIRING_REREVIEW2_44C9859.md`
(FIX for pilot use; I2BW-1 and I2BW-5 resolved; I2BW-2 unresolved through the
new finding I2BWR2-1; I2BWR2-2 Low).

**Adjudicated and repaired by:** Claude Opus 5.5 (`claude-opus-5-5`) on
2026-10-11, in commit `3e622d2`. Not yet re-reviewed.

| ID | Decision | Repair and evidence |
|---|---|---|
| I2BWR2-1 High (and I2BW-2) | AGREE, repaired | `record` now reads `--exploration-manifest` once. The bytes it compares with the canonical rebuild are the bytes it hashes into the run definition. In a Q5 run, the rebuilt BTC manifest's own `manifest_sha256` must also equal the BTC hash in the loaded source's identity (`source["manifest_sha256"]["BTCUSDT"]`). That restores the comparison the earlier repair removed. Archives that change between the source load and the rebuild are therefore refused. **Test:** inside `test_a_q5_pilot_runs_on_recorded_exploration_data_only`, the script is loaded in-process from the clean checkout. The rebuild is patched to see the other archives, and the matching `other.json` is supplied. `main` returns 1 with "not the BTC exploration", and nothing is written. **Mutation check:** with the hash comparison removed (temporary commit, then reset), the same test fails (`assert 0 == 1`). With the repair, the test passes. The single-read part is plain from the code: one `read_bytes()` call, and its result is used for both the check and the hash. The test does not cover it on its own. |
| I2BWR2-2 Low | AGREE, repaired | The `scripts/d19_run.py` module docstring now says development thresholds are "per T level, each tail's extreme over every cell's complete threshold chain, of any K". |

No calibration was run.

## Checks on `3e622d2` (2026-10-11, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest` the nine `tests/unit/test_calibration_*.py` files `-q -p no:cacheprovider` | 0 | 194 passed in 584.76 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those nine files | 0 | 1786 passed, 9 skipped in 368.39 s |
| `.venv/Scripts/python -m ruff check .` / `ruff format --check .` | 0 | All checks passed / 144 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_run_definition.py scripts/d19_choose.py` | 0 | No issues in 70 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |

**Outcome.** The focused re-review 3 (`SOL6_ITEM2B_Q5_WIRING_REREVIEW3_3E622D2.md`) is ACCEPT for pilot use, with no new findings. That closes the review loop for item 2b step 1 (Q5 wiring) for pilot use.
