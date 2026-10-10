# Focused re-review prompt: D-19 driver repairs of Fable FA-1..FA-5 at eef38b3

You are an independent reviewer (not an authority) of repository
`D:\PMP-programs-for-sharawi\autonomous-quant-trader`, branch
`d19-calibration-engine`, commit `eef38b3`. READ-ONLY: do not edit, create or
delete files, commit, or touch git state; no network; no server; no
calibration runs. The laptop has ~8 GB RAM: run only focused tests if needed,
e.g. `.venv\Scripts\python -m pytest tests/unit/test_calibration_chunks.py -q -p no:cacheprovider`
(`tests/unit/test_calibration_rundef.py` takes ~4 minutes).

Read `review/d19-engine/FABLE_ADVERSARIAL_REVIEW_8936859.md` (findings) and
`review/d19-engine/ADJUDICATION_FABLE_8936859.md` (decisions), then the diff
`git diff 8882cc9 eef38b3` (calibration/chunks.py, calibration/rundef.py,
scripts/d19_run.py and tests).

Check:
1. Each of FA-1..FA-5 is closed as adjudicated (FA-1 governance part and the
   FA-2 runtime_identity part are deliberately open; judge only whether
   leaving them open is safe given qualification runs are refused).
2. FA-1: can a pilot still produce a draw that a qualification run would use
   (prefix check bypass, ids from malformed entries, counts)? Is
   `d19_run_definition.py record` consistent with the new rule?
3. FA-3: the lock on POSIX (`fcntl.flock`) and Windows (`msvcrt.locking` on a
   file opened `a+b`): correct exclusion, released on crash, lock file
   location vs `_strays`, any deadlock/regression for resume.
4. FA-4: `run` returning `verify(chain)` under the lock; directory fsync
   placement; does anything now refuse a valid resume?
5. FA-5: `wait(FIRST_EXCEPTION)` + terminating `multiprocessing.active_children()`
   + `shutdown(cancel_futures=True)`: can it hang, kill unrelated processes,
   lose an exception, or print heads for an incomplete run? Python >= 3.12.
6. Whether the new tests actually fail without the repairs.
7. Anything else these repairs introduce.

Output a complete review record in markdown, ready to commit verbatim:
title, reviewer model metadata (as you observe it), commit reviewed, scope,
commands run with results, verdict (ACCEPT / FIX / UNSOUND, for pilot runs),
findings with stable IDs FR-1, FR-2, ... (severity, file:line, concrete
failure scenario, proposed repair), or "no findings".
