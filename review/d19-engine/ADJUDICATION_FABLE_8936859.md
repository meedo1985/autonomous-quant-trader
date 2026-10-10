# Adjudication of the Claude Fable 5.1 adversarial review of the D-19 run driver at 8936859

Review: `review/d19-engine/FABLE_ADVERSARIAL_REVIEW_8936859.md` (verdict
ACCEPT for threshold pilot runs; FA-1..FA-5). Adjudicated and repaired by
Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-10. The repairs are not yet
re-reviewed.

| ID | Decision | Repair and evidence |
|---|---|---|
| FA-1 QUESTION | AGREE on the code part, repaired; governance part OPEN for the owner | `rundef.run_plan`: every pilot cell id must start with `PILOT_PREFIX = "pilot-"`, a pilot's counts must stay below `PRESCRIBED`, and a non-pilot manifest with a `pilot-` id is refused. Pilot seeds therefore never coincide with qualification seeds, although they keep the §8 namespace and anchor (no §8 change). Tests: three new `test_a_bad_run_plan_is_refused` cases; fixture cells renamed `pilot-k1`/`pilot-k2`. **Open, for the owner before any qualification threshold run:** fix qualification cell ids canonically (from K, T, law, dependence) or freeze the manifest before any threshold-namespace draw, and have the qualification path check that `prereg_commit`/`prereg_sha256` are the accepted rev 7g ones. Qualification runs remain refused in code until then (DR2-1). |
| FA-2 NON-BLOCKING | AGREE on the reference-vector part, repaired; binary-hash part NOT REPAIRED (proposal) | `_reference_outputs` now includes `classifier.diagnostics(legs.x)` for every reference case, so the pocketfft/log/corrcoef numerics of the threshold run are gated through the reference vectors. Test `test_reference_vectors_see_the_classifier_diagnostics` (a one-ulp change to one diagnostic changes every case). Not repaired: adding `_pocketfft_umath*`/`_umath_linalg*` to `runtime_identity` would change the decided A-V1 identity; that is an owner/governance proposal, and the reference vector now covers the behaviour. |
| FA-3 NON-BLOCKING | AGREE, repaired | `chunks.run` holds an exclusive non-blocking lock on `<cell_id>.lock` beside the chain directory (`fcntl.flock` on POSIX, `msvcrt.locking` on Windows) and refuses a second writer with `ChainError`; the OS releases it when the process ends. Test `test_a_second_writer_on_a_chain_is_refused`. Run-procedure note for the launcher: stop the whole service cgroup, never the parent alone. |
| FA-4 NON-BLOCKING | AGREE, repaired | `chunks.run` returns `verify(chain)` (bytes re-read from disk) under the lock; `_write` fsyncs the directory after `os.replace`, and `run` fsyncs the namespace directory after `mkdir` (POSIX; Windows cannot fsync a directory). Test `test_the_head_is_read_back_from_disk` (on-disk bytes truncated after the write → `ChainError`, no head). |
| FA-5 NON-BLOCKING | AGREE, repaired | `main` submits every chain and waits with `FIRST_EXCEPTION`; the first failure terminates the pool's worker processes (`multiprocessing.active_children()`, portable to Python 3.12) and exits 1. Test `test_a_failing_chain_stops_the_run_without_waiting_for_earlier_ones` (first chain sleeps 600 s, second fails; the run must stop within the 180 s timeout). |

Still carried: FE-4 (launcher takes the image digest from `docker inspect`)
and FE-7 (re-pilot measurement of non-finite threshold draws). No
calibration was run.

## Checks after repair (2026-10-10, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_chunks.py tests/unit/test_calibration_rundef.py -q -p no:cacheprovider` | 1 | 72 passed, 1 failed in 242.87 s: the new FA-2 test's own nudge (`+1e-15`) was below one ulp of the chosen value; changed to `math.nextafter` on a finite value |
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py -q -p no:cacheprovider -k classifier_diagnostics` | 0 | 1 passed |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider --ignore=tests/unit/test_calibration_rundef.py --ignore=tests/unit/test_calibration_chunks.py` | 0 | 1801 passed, 9 skipped in 418.24 s (includes `test_calibration_engine.py`) |
| `.venv/Scripts/python.exe -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python.exe -m ruff format --check .` | 0 | 132 files already formatted |
| `.venv/Scripts/python.exe -m mypy calibration src` | 0 | No issues in 62 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| `C:\Users\PMP Cordination\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and exact inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |
