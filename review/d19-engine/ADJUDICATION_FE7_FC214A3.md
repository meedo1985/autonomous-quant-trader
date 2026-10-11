# Adjudication of the GPT-6 Sol review of the D-19 FE-7 re-pilot kit at fc214a3

**Review:** `review/d19-engine/SOL6_FE7_REVIEW_FC214A3.md` (FIX before the kit goes to the owner; FE7-1..FE7-8).

**Adjudicated and repaired by:** Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-11. Not yet re-reviewed.

| ID | Decision | Repair and evidence |
|---|---|---|
| FE7-1 High (owner) | AGREE, repaired; size decided by the owner | `pilot-cells.json` now has 13 cells. It holds every cell of the thin categories (§13 item 3): Q1 clusters at K = 5 and 20, Q2m at K = 2, 5 and 20, and QJ at K = 2 and 20. It also keeps at least one cell of each of Q1, Q2, Q3, Q4 and Q5. A test checks the thin cells against `grid.GRID`. The owner chose 1,000 development replications per cell (`OWNER_DECISION_FE7_PILOT_SIZE.md`). The reviewer's resolution figures are disclosed there: the pilot is a cost and smoke measurement, and each escape is decided by the full run's own 12,000. `choices.json` already reports per cell (and per QJ family) the DSR and `U_G` event counts and their denominators. Intervals follow from those counts. |
| FE7-2 High | AGREE, repaired | `d19.sh clean-check` runs the threshold namespace again, from scratch, into `store-clean`. `d19_pilot_checks.py compare` then requires every cell's chunks to have equal content hashes and results in both stores, and fails otherwise. The sheet runs it after the interrupted and resumed threshold run. CI runs it as well. |
| FE7-3 High | AGREE, repaired | `status` prints the run's own `StartedAt`, `FinishedAt` and exit code (`docker inspect`). The sheet asks for `status` after the killed attempt, after the threshold run and after the development run. That gives wall time per namespace and attempt. The worker time per replication follows from the wall time, the two workers and the counts in `status`. The synthetic timer separates only the per-stage costs (I1-8). |
| FE7-4 Medium | AGREE, repaired | `status` prints `aqt-d19.slice`'s `MemoryPeak`, the exact cgroup peak since the slice started. It is taken during the development run, after both workers have run for 15 minutes. |
| FE7-5 High (owner, if any are found) | AGREE, repaired | `nonfinite` is now `d19_pilot_checks.py nonfinite`. It parses each threshold chunk's `results`, takes the diagnostic values (per family for QJ), and decodes each one as binary64. It counts only those that are not finite, prints the count per cell and in total, and refuses a missing or empty store. It runs after `choose`, which has verified every chain. If the count is positive, the treatment is the owner's decision (FE-7). There is a test with a NaN, an infinity and a QJ record. |
| FE7-6 Medium | AGREE IN PART, repaired | `U_G` is now timed only when a nominee exists, as in the run. **Kept:** the classifier accepts every window, so Annex B always runs to the end. That makes the timed DSR cost an upper bound, which is the conservative direction, and the docstring now says so. The largest grid K is 20, so the timer's shapes span the grid. Q5 and QJ costs come from the development run's own times. Whether the second rule's cost warrants a preregistration change stays an owner proposal (I1-8). |
| FE7-7 High | AGREE, repaired | `d19.sh failcheck` does the check itself. It refuses unless the run is going and exactly two `spawn_main` workers exist. It kills one with `kill -9`, waits up to 120 s for the run to stop, requires a non-zero exit, and requires the other worker's host PID to be gone. Only then does it print `PASS`. The sheet resumes only after that `PASS`. |
| FE7-8 Medium | AGREE, repaired | The copy runs only if `/var/lib/aqt-d19/raw` does not exist (`test ! -e ... &&`). A run counts as finished only when `status` shows `Exited (0)` and **all 13** cell lines of the namespace show their full chunk count. |

No calibration was run.

## Re-review (`SOL6_FE7_REREVIEW_A939AD0.md`: FIX)

FE7-1 and FE7-5 are resolved. FE7-7 is resolved in code but not exercised end to end in CI: the CI pilot finishes in about 13 s. The owner's sheet runs `failcheck` against a real run, and the engine's unit tests cover the killed-worker path.

| ID | Decision | Repair and evidence |
|---|---|---|
| FE7R-1 High (and FE7-2) | AGREE, repaired | `compare` now requires, for every cell, the same chunk file names in both stores, byte-identical file contents, and the same set of cells. Equal bytes mean equal content hashes, so the chain heads are the same. |
| FE7R-2 Medium | AGREE, repaired | `clean-check` refuses if `store-clean` exists, so it always starts from an empty store. CI checks that a second `clean-check` is refused. |
| FE7-3 | AGREE, repaired | `d19.sh times` prints, for each chain, the seconds between consecutive finished chunks. A chain runs on one worker at a time, so each interval is one worker's measured time for 500 replications. That gives 3 intervals per threshold cell and 1 per development cell. The sheet asks for it after each namespace. CI runs it. |
| FE7-4 | AGREE, repaired | `d19.sh memwatch` samples the slice's `MemoryCurrent` every 10 s for 10 minutes during the development run. It counts only samples where `docker top` shows exactly two `spawn_main` workers, and reports their maximum and the number of samples counted. |
| FE7-6 | DISAGREE, with evidence | In the development run, the classifier passed to Annex B is a precomputed decision: `scripts/d19_run.py:183`, `dsr.evaluate(..., classifier=lambda *_: accept)`. `accept` comes from `classifier.within(diagnostics(x), ...)`, which runs once before Annex B and is timed by the timer's `diagnostics` stage. With `accept = True` the production path is the timer's path, and with a refusal Annex B stops earlier. The timer's DSR time is therefore the production path's worst case. The reviewer did not have `dev_replication`. |
| FE7-8 | AGREE, repaired | The sheet uses `d19.sh copy-raw`. It refuses loudly if `/var/lib/aqt-d19/raw` exists, and otherwise copies the archives, sets the owner and prints the archive count. The silent skip of `test ... &&` is gone. |

## Re-review 2 (`SOL6_FE7_REREVIEW2_3401757.md`: FIX; FE7-2/FE7R-1, FE7R-2 and FE7-8 resolved; FE7-6 disagreement justified)

| ID | Decision | Repair |
|---|---|---|
| FE7R2-1 High (and FE7-3) | AGREE IN PART, repaired | A chain's chunks run back to back on one worker (`chunks.run`). An interval between two of its chunks is therefore that worker's time for 500 replications, unless it crosses a stop and resume. `times` now reads the current run's `StartedAt` and marks any interval that crosses it as "(spans a restart)". The sheet says such intervals are not used. The development run is never interrupted, so all its intervals are worker times. **Not done:** timing inside the worker. That would change the engine driver for a pilot measurement. The marked intervals give the same figure for every uninterrupted interval. |
| FE7R2-2 Medium (and FE7-4) | AGREE, repaired | `memwatch` now reports the run container's exact kernel high-water mark, `memory.peak` of its cgroup scope under `aqt-d19.slice`, which no spike can escape. Its samples are only evidence that both workers ran. It refuses with `FAIL` if no sample saw 2 workers. CI starts a container in the slice and requires `memory.peak` at exactly the path `memwatch` reads. |
| FE7R2-3 Medium | AGREE, repaired | `copy-raw` copies into `raw.partial`, removes it if the copy fails, and renames it to `raw` only after success. The sheet now tells the owner to stop on any failed command or error output, not only on `refused` or `FAIL`. |

## Re-review 3 (`SOL6_FE7_REREVIEW3_AF7805A.md`: FIX; FE7R2-2 and FE7R2-3 resolved; the "AGREE IN PART" on FE7R2-1 judged justified in principle)

| ID | Decision | Repair |
|---|---|---|
| FE7R3-1 Medium | AGREE, repaired | `times` now takes the namespace: `times threshold` or `times dev`. It is read while that namespace's last run is the current container, so the restart it compares against is that run's own. The sheet asks for `times threshold` in step E, right after the resumed threshold run, and `times dev` in step H. CI runs `times threshold`. |
| FE7R3-2 Low | AGREE, repaired | The start time keeps its fraction (`date ... +%s.%N`), so a chunk finished in the same second as the restart is still compared correctly. |
