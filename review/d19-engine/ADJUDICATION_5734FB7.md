# Adjudication of the GPT-6 Sol re-review of the D-19 engine at 5734fb7

Review: `review/d19-engine/SOL6_REREVIEW_5734FB7.md`: **ACCEPT** of the run-definition component (R6-1, R6-2 repaired).

| ID | Decision | Repair |
|---|---|---|
| R7-1 NON-BLOCKING | AGREE, repaired | New test `test_the_start_gate_itself_refuses_cached_bytecode`: `start_gate` (not only the helper) refuses in a process that caches bytecode. Mutation check: removing the `bytecode_problem()` call from `start_gate` makes it fail. Test-only change. |

Requirements carried to the driver task; no full run before the driver passes review: R3-3 (each worker runs `start_gate`), FE-5 (every `Chain` from `definition_sha256(defn)` and the returned gating), FE-4 (`AQT_IMAGE_DIGEST` from host `docker inspect`), FE-7 (re-pilot measures non-finite threshold draws; owner decides treatment if any), R6-1 (every worker entry point disables bytecode caching before importing engine code).

Checks: calibration tests (rundef, chunks, engine) all pass; `ruff check .` clean; `mypy calibration src` clean. The previous full gate at 5734fb7 (1840 passed, 9 skipped) is unchanged in source.

## Correction (same day)

The checks line above was wrong when committed at e6c2901: the combined calibration run had **1 failure**. Cause: `test_record_refuses_a_file_changed_while_recording` imports the recording script in-process, and the script switches bytecode caching off process-wide, so the new R7-1 test later saw a different (still refusing) message. Repair: that test restores `sys.dont_write_bytecode` and `sys.pycache_prefix` via monkeypatch, and the R7-1 test pins `dont_write_bytecode = False`. After the repair: `pytest -q -p no:cacheprovider` 1841 passed, 9 skipped; `ruff check .` and `ruff format --check .` clean.
