# Focused re-review: D-19 driver repairs of FR-1..FR-5 at `3028626`

Recorded verbatim from the reviewer's final report (2026-10-10), below the
line. Prompt: `review/d19-engine/FR_REREVIEW_PROMPT.md`, with a covering
instruction allowing focused tests and forbidding `git stash`.

Failed attempts before this review (no review content, nothing to record
beyond this note): two `codex exec -s read-only -m gpt-6-sol -c
model_reasoning_effort=high` runs (CLI banner model `gpt-6-sol`, effort
high; sessions `01a12597-5152-7503-b4c2-b7e9bdf63474` and
`01a12599-07b5-7942-8765-7e7f3e680e24`) both reported that the local command
runner rejected `git rev-parse HEAD`, the review files and the diff, and
gave no verdict. Per the owner's fallback rule the review went to Fable.

## Adjudication (Claude Opus 5.5, 2026-10-10)

| ID | Decision |
|---|---|
| FR2-1 INFO | AGREE, not repaired: Windows-only aliasing fails closed and the calibration host is Linux (§13 rev 7g item 6). Revisit only if a run is ever made on Windows. |
| FR2-2 INFO | AGREE, carried: the pilot procedure on the Linux host will include one deliberately failing chain, confirming that no worker outlives the parent and that the run exits promptly, with the result recorded in the pilot evidence (next to FE-7). |

---

**Reviewer metadata:** Claude Fable 5.1, an independent reviewer standing in for GPT-6 Sol, whose two attempts failed because its sandbox could not run commands. The session's system context gives the model ID as `claude-fable-5-1`. No other runtime metadata (reasoning effort, session ID) was available to check. Run as a Claude Code subagent on 2026-10-10.
**Commit reviewed:** `30286262c650725790ad7f4881925a5b06ce4e19` on `d19-calibration-engine`, compared with `1ac6f0b`.
**Scope:** The checks set by `review/d19-engine/FR_REREVIEW_PROMPT.md`, covering the FR-1..FR-5 repairs in `calibration/chunks.py`, `scripts/d19_run.py`, `tests/unit/test_calibration_chunks.py` and `tests/unit/test_calibration_rundef.py`. Inputs were `SOL6_FA_REREVIEW_EEF38B3.md` and `ADJUDICATION_FR_EEF38B3.md`. The review was read-only: no edits, commits, git state changes, network access or calibration runs. Unlike the prompt's sandbox assumption, the focused tests could be run here, and they were.

## Verdict: ACCEPT for pilot runs

All five FR findings are closed as adjudicated. The repairs introduce no new blocking or non-blocking defect. The two findings below are informational. Items still open from earlier adjudication are unchanged: the FA-1 governance part (owner), the FA-2 `runtime_identity` proposal, and FE-4 and FE-7.

## Check results

1. **FR-1 closed.** The lock is now at `<namespace>/.locks/<cell_id>` (`calibration/chunks.py:122-124`). `_CELL_ID = [A-Za-z0-9][A-Za-z0-9._-]{0,63}` (`calibration/generator.py:42`) means a cell id cannot start with `.`, so no chain directory can be `.locks`. A lock file is never a chain directory, and each lock name is the cell id, so two different cells never share a lock on POSIX. Nothing enumerates the namespace directory. The only `iterdir` is `_strays` on `chain.root` (`chunks.py:144`), and `verify` and `reduce` address chunks by path, so `.locks` cannot be read as a stray or a cell. Windows-only aliasing of cell ids is a separate, pre-existing issue that fails closed (FR2-1).
2. **FR-2 closed.** `others` is captured before the pool exists (`scripts/d19_run.py:125`), so only children that appeared later are terminated (`:135`).
   - **Lazy spawn:** on Python 3.14 with the `spawn` context, workers are started on demand by `submit` in the main thread. The `except` block runs after any `submit` has returned or raised, so every started worker is already in `multiprocessing.process._children` and appears in `active_children()`.
   - **Replacement after a crash:** there is none. A dead worker breaks the executor, and no `max_tasks_per_child` is set, so no replacement worker can appear after the snapshot.
   - **Unrelated children:** one would be terminated only if another thread in the same process started a child during the run. The standalone script has no such thread.
3. **FR-3 closed.** `BaseException` is caught (`:134`). The run's workers are terminated, then `KeyboardInterrupt` or `SystemExit` is re-raised (`:137-138`), so the interruption is not swallowed. Heads are printed only after the `try` completes normally (`:143-144`), never for an interrupted or failed run.
   - **Shutdown after terminate:** `shutdown(cancel_futures=True)` (`:142`) runs after the workers are terminated. The executor's manager thread sees the workers' sentinels, marks the pool broken and joins dead processes, so I found no hang path.
   - **Unmitigated case:** a SIGTERM to the parent alone skips the `except` block entirely (default handler). FR-5's instruction to stop the whole control group covers this.
4. **FR-4 closed.** `created` is computed before `mkdir` (`chunks.py:156-159`), and the parent of each new directory is fsynced.
   - **Relative paths:** `Path('s/threshold/c').parents` ends at `.`, which always exists, so the last fsync, of the parent of `s`, opens `.`, which is valid.
   - **Already-existing parents:** these are skipped correctly, since their entries were made durable earlier or predate the run.
   - **Race between the two workers:** if worker B sees a namespace that worker A has created but not yet fsynced, A fsyncs it immediately afterwards. A power loss in that window can only lose chunks that are not yet reported. No head is printed before every chain finishes, and restart recomputes missing chunks.
   - **`.locks` is not fsynced.** This is correct, because lock files carry no data.
5. **FR-5 closed.** The module docstring (`scripts/d19_run.py:20-22`) now tells the launcher to stop the whole control group, never the parent alone, and gives the reason.
6. **Do the new tests fail without the repairs?**
   - `test_a_lock_never_collides_with_another_cells_chain`: under the eef38b3 layout, cell `pilot-a` leaves the file `dev/pilot-a.lock`, and creating cell `pilot-a.lock`'s directory at that path then fails. The adjudication records the stashed-code failure.
   - `test_a_failure_terminates_only_the_runs_own_workers`: the old code made one `active_children()` call, which the mock answers with `[unrelated]`. In the `chain failed` case, `unrelated` would be terminated and `own` would not. In the `KeyboardInterrupt` case, `except Exception` would not catch the interrupt, so `own` would not be terminated. Both parameters fail on the old code by inspection.
   - FR-4 has no test, as the adjudication states (FR2-2).
7. **Other effects of the repairs:** none found.

## Findings

### FR2-1: INFO: Windows aliasing of distinct cell ids (pre-existing, fails closed)
**Location:** `calibration/generator.py:42`; `calibration/chunks.py:122-124`
**Scenario:** On Windows (NTFS, case-insensitive and stripping trailing dots), `pilot-a`, `pilot-A` and `pilot-a.` are valid and distinct cell ids, but they name the same chain directory and the same lock file. A reserved device name such as `nul` is also accepted. Every order fails closed:
- **Concurrent:** the second worker's lock is refused with `ChainError`, which stops the run.
- **Sequential:** `_check` rejects the other cell's chunks on `cell_id` (`chunks.py:84-86`).
- **Device name:** `mkdir` fails.

This behaviour predates FR-1 and does not occur on the Linux calibration host.
**Proposed repair (optional):** restrict cell ids to lower-case letters, without a trailing dot, if Windows runs ever matter. No action is needed for pilot runs on the Linux host.

### FR2-2: INFO: the FR-2/FR-3/FR-4 repairs are verified by inspection and mocks only
**Location:** `tests/unit/test_calibration_rundef.py` (new `test_a_failure_terminates_only_the_runs_own_workers`); `calibration/chunks.py:156-159`
**Scenario:** The FR-2 and FR-3 test replaces both `ProcessPoolExecutor` (with a thread pool) and `active_children`, so it does not exercise real lazy worker spawn or real `terminate`/`shutdown` timing. The FR-4 fsync loop has no test because it is POSIX-only. A future change to executor internals would therefore not be caught.
**Proposed repair (optional):** on the Linux host, run a pilot cell with a deliberately failing chain once, and confirm that no worker outlives the parent and the process exits promptly. Record the result with the pilot evidence.

## Commands and results

| Command | Exit | Result |
|---|---:|---|
| `git rev-parse HEAD` | 0 | `30286262c650725790ad7f4881925a5b06ce4e19` |
| `cat review/d19-engine/SOL6_FA_REREVIEW_EEF38B3.md review/d19-engine/ADJUDICATION_FR_EEF38B3.md` | 0 | Read |
| `git diff --stat 1ac6f0b HEAD -- calibration scripts tests`; `git diff 1ac6f0b HEAD -- calibration scripts tests` | 0 | 4 files, +74 −8; inspected |
| Read `scripts/d19_run.py` (whole), `calibration/chunks.py:74-215`, `calibration/generator.py:35-65`; grep for `iterdir`, `glob(`, `listdir`, `scandir`, `.locks` in `calibration`, `scripts`, `src` | 0 | Only `_strays` enumerates, and only `chain.root` |
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_chunks.py -q -p no:cacheprovider` | 0 | 14 passed in 1.05 s |
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py -q -p no:cacheprovider -k "terminates_only or failing_chain or collides"` | 0 | 3 passed, 59 deselected in 11.64 s |
| `.venv/Scripts/python --version` | 0 | Python 3.14.7 |
| `git status --short` | 0 | Clean; no files or git state changed |

Not run, by instruction: the full test suite, ruff, mypy, lint-imports and frozen-artifact verification. The adjudication records them as passing at this commit, and that claim was not re-checked here. The reviewed diff touches no frozen artifact.
