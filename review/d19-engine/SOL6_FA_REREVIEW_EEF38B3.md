<!-- Recorded verbatim from codex exec (OpenAI Codex v0.160.0) on 2026-10-10. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12588-9536-72c2-96db-235531209e28. Prompt: review/d19-engine/FA_REREVIEW_PROMPT_EEF38B3.md. Tokens used: 68,876. -->

# Focused re-review: D-19 driver repairs at `eef38b3`

**Reviewer metadata:** Codex, independent reviewer. The session identifies the reviewer as based on GPT-6; an exact runtime model ID and reasoning-effort value were not exposed for verification.  
**Commit reviewed:** `eef38b383adf5d934062851055c848eab25734c2` on `d19-calibration-engine`, against `8882cc9`.  
**Scope:** FA-1 through FA-5 in the repair diff, the recorder and driver call paths, relevant tests, and the cited preregistration. Read-only review; no network or calibration run.

## Verdict: FIX for pilot runs

FA-1’s seed separation works on the recorder and driver paths: both validate every cell before `run_plan`, pilots require `pilot-` IDs and fewer than 300,000 replications, and qualification remains unconditionally refused. Malformed entries cannot bypass those entry points. FA-2’s diagnostic outputs now enter the reference vectors; its proposed binary-hash change remains open. FA-4’s returned head is read back under the lock. FA-5 does not print heads after an ordinary worker failure.

The new lock path conflicts with a valid cell ID, so an otherwise valid pilot manifest can fail. Worker termination also has operational defects described below. The open FA-1 governance decision and FA-2 runtime-identity proposal do not make the currently refused qualification path executable.

## Findings

### FR-1 — BLOCKER — lock file conflicts with a valid cell directory

**Location:** `calibration/chunks.py:121`; `calibration/generator.py:42,57–60`  
**Scenario:** A pilot manifest may validly contain both `pilot-a` and `pilot-a.lock`. Running `pilot-a` creates the sibling file `pilot-a.lock`; running the second cell then tries to create a directory at that path and fails. Reversing their order makes the first cell’s lock open target a directory. The conflict can also occur with a lock file left by an earlier run.  
**Repair:** Put locks in a dedicated location whose path cannot be a valid cell directory, and account for existing lock files when changing the layout. Add a two-cell regression test.

### FR-2 — NON-BLOCKING — failure cleanup can terminate unrelated children

**Location:** `scripts/d19_run.py:130–132`  
**Scenario:** If `main()` runs in a process that already owns another `multiprocessing.Process`, any chain failure terminates that process too: `active_children()` is process-wide, not executor-specific. The standalone script normally has only pool workers, but the function itself does not enforce that condition.  
**Repair:** Terminate only processes owned by this executor, or explicitly constrain and enforce standalone execution.

### FR-3 — NON-BLOCKING — interruption can wait for a long worker

**Location:** `scripts/d19_run.py:125,130–136`  
**Scenario:** `KeyboardInterrupt` and `SystemExit` bypass `except Exception`. The `finally` block then calls `shutdown()` with its default `wait=True`, without terminating workers. Ctrl-C during a long chain can therefore wait for that chain to finish. `cancel_futures=True` does not stop running work.  
**Repair:** Handle interruption separately, terminate the executor’s workers, then shut down and propagate the interruption.

### FR-4 — NON-BLOCKING — first-run directory durability is incomplete

**Location:** `calibration/chunks.py:153–154`  
**Scenario:** `mkdir(parents=True)` can create both `store/threshold` and the cell directory. Fsyncing only `store/threshold` makes the cell entry durable but does not ensure the new `threshold` entry is durable in `store`. After power loss, that namespace and its fsynced chunks may be lost.  
**Repair:** Fsync each parent after creating its child directory, or require a durably prepared store and namespace before `run`.

### FR-5 — NON-BLOCKING — the stated stop procedure is absent from operational instructions

**Location:** `scripts/d19_run.py:20–23`  
**Scenario:** The adjudication says the launcher procedure must stop the whole service cgroup. That direction appears in the adjudication, but a repository search found no corresponding instruction in the driver’s operational text. Killing only the parent can leave a worker computing while a relaunch is refused by its lock.  
**Repair:** Add the cgroup stop instruction to the run procedure used by the launcher.

## Closure and test assessment

- **FA-1:** Code repair holds on actual entry points; qualification governance remains open. `d19_run_definition.py record` validates cells before applying the new rule.
- **FA-2:** Reference-vector repair holds. The proposed `runtime_identity` binary hashes remain open as adjudicated.
- **FA-3:** OS locks are released when their process exits and sit outside `_strays`; FR-1 prevents full acceptance of the lock layout.
- **FA-4:** `run` verifies disk bytes under the lock. FR-4 limits the new durability claim on a first run.
- **FA-5:** `FIRST_EXCEPTION` surfaces an ordinary failed future without waiting for earlier chains; success requires every result before heads print. FR-2 and FR-3 limit cleanup behavior.

By inspection, the new tests would fail against the pre-repair code: the FA-1 cases would be accepted or raise the wrong error; changing classifier diagnostics would not change reference vectors; `_sole_writer` would be absent; a torn final chunk would still return the in-memory head; and the slow-first-chain test would time out under ordered `pool.map`. The lock test does not cover the FR-1 name collision or cross-process exclusion.

## Commands and results

| Command | Result |
|---|---|
| `git rev-parse HEAD`; `git status --short --untracked-files=all` | HEAD matched `eef38b3`; one pre-existing untracked review prompt, left untouched. |
| `git diff 8882cc9 eef38b3 -- calibration/chunks.py calibration/rundef.py scripts/d19_run.py tests/unit/test_calibration_chunks.py tests/unit/test_calibration_rundef.py` | Inspected repair diff. |
| `git diff --check 8882cc9 eef38b3` | Exit 0; no whitespace errors. |
| `git diff --`; `git diff --cached --` | No tracked working-tree changes shown; cached check emitted a global-ignore permission warning. |
| `Get-Content` on the two Fable records, affected source and tests, review skills, Constitution, protocol, and hash specification; `git show docs/d19-recommendation:review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md` | Read successfully. |
| `git grep -n -i -e 'whole service cgroup' -e 'parent alone' -e 'orphaned worker' -e 'stop the whole' -- review scripts calibration` | Found the stop instruction in review records, not operational driver instructions. |
| `.venv\Scripts\python -m pytest tests/unit/test_calibration_chunks.py -q -p no:cacheprovider` | Exit 1 before collection: pytest could not obtain a writable temporary directory in this read-only sandbox. No test result is claimed. |

No files or git state were changed. Full task-gate validation and frozen-artifact byte verification were outside this focused read-only review; the reviewed commit diff lists no frozen artifact changes.
