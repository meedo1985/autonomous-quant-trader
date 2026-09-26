# Task 17 local implementation and gate report

Date: 2026-09-26
Base commit: `fbc4abc` (`main`)
Branch: `task17-exploration-joblog`
Author and reviewer: Claude Opus 5.5 (`claude-opus-5-5`), coding AI. This is a
**self-review**, not an independent one.

## Authority

Roadmap Task 17, approved in `review/roadmap/OWNER_APPROVAL.md`, unblocked by
the section 25 signature. The owner said "start task 17" on 2026-09-26.

## Scope

- `src/aqt/research/joblog.py` (new, 167 lines): `record_job`, `run_logged`,
  `review_status`, `ReviewStatus`, `clearance_path`, `JobLogError`.
- `tests/unit/test_joblog.py` (new, 10 tests, synthetic data).

No existing module, frozen artifact or import contract changed.

## Design

Source: `protocols/protocol_v1.yaml` `partitions.sandbox_exploration_policy`,
"all jobs logged; human review triggered after 250 jobs".

- **Log:** each job is one `exploration_job` entry in an `aqt.core.ledger` file
  (hash-chained, cross-process locked), holding the cycle id, manifest hash,
  partition, symbol, benchmark and stress (`float.hex`). `run_logged` appends it
  **before** running, so a job that fails is still counted. After a successful
  run it appends an `exploration_job_result` entry with the result digest.
- **Job numbers are not stored.** A job's number is its position among the
  cycle's job entries in ledger order, which the ledger's lock makes unique, so
  two concurrent writers cannot both be job 250.
- **Flag:** `review_status` reports `review_required` when the cycle has at
  least 250 jobs beyond the last clearance. The log is verified first, so a
  damaged log raises instead of being counted.
- **Clearance:** only a file committed at
  `review/exploration-review/<cycle_id>.md`, read from `HEAD` with
  `git show`. Its highest `Cleared through job: <n>` line counts. The module has
  no code path that writes a file (checked by a test).

### Deliberate choices the owner should know about

- **T17-01. The flag recurs every 250 jobs after the last clearance.** The
  protocol says "after 250 jobs" and does not say what happens after a review.
  Recurring is the AI's reading; the alternative is a single review per cycle.
- **T17-02. The flag is reported, not enforced.** `run_logged` keeps running
  jobs when review is due; the protocol says review is "triggered", not that
  exploration stops. Blocking further jobs until clearance is a one-line
  change if the owner wants it.
- **T17-03. "Human" is procedural, not mechanical.** The library cannot tell who
  wrote the clearance file. That it is committed in `HEAD` is checked; that a
  human wrote it rests on Constitution section 4 and `AGENTS.md` (the AI may
  not write it) and on review of the commit.
- **T17-04. `run_exploration` can still be called without logging.** The Task 16
  harness does not import the ledger (its tests forbid `aqt.core` imports), so
  logging happens only through `run_logged`. A caller that uses the harness
  directly is not logged. Scripts should use `run_logged`.
- **T17-05. The cycle id is caller-supplied text** (letters, digits, `.`, `_`,
  `-`), because no cycle registry exists yet.
- **T17-06. The 250-job test samples counts** 1, 2, 125, 248, 249 and 250 of
  one real 250-job log, rather than all 250: each status call re-verifies the
  chain, and checking every count took about 35 s.

## Acceptance criteria (roadmap Task 17)

| # | Criterion | Evidence |
| --- | --- | --- |
| 1 | Job 250 sets the flag; jobs 1-249 do not | `test_job_250_raises_the_flag_and_jobs_1_to_249_do_not` |
| 2 | Library code cannot clear it; only a committed human record does | `test_only_a_committed_clearance_clears_the_flag` (uncommitted and staged-only files do not count), `test_the_library_has_no_way_to_write_a_clearance` |
| 3 | Hash-chained; a mutated entry fails verification | `test_the_log_is_hash_chained_and_a_mutation_fails` (and `review_status` refuses the damaged log) |
| 4 | Two processes produce one valid chain | `test_concurrent_writers_produce_one_valid_chain` (`spawn` processes, 30 entries, intact) |

Also: `test_run_logged_logs_the_job_before_the_run_and_its_result_after`, and
`test_unsafe_cycle_ids_are_refused` (4 cases).

Mutation checks: flag at 251 instead of 250 fails 2 tests; reading the git
index instead of `HEAD` fails 1; logging after the run instead of before fails 1.

## Validation

Environment: Windows 11, `.venv` Python 3.14.7.

| Command | Result |
| --- | --- |
| `pytest -q` | 1380 passed, 4 skipped in 212.60s |
| `ruff check .` | All checks passed (after one `isinstance` fix) |
| `ruff format --check .` | 83 files already formatted (after formatting) |
| `mypy src scripts` | Success: no issues found in 42 source files |
| `lint-imports` | Contracts: 5 kept, 0 broken |
| `git diff --check main...HEAD` | clean |

Frozen verification: `git diff --name-only main` lists only the two new files.

## Outstanding

- An independent review by a different model has not been done.
- **QUESTION T17-Q1 (owner):** like T16-Q1, this implements a protocol rule
  (`sandbox_exploration_policy`), so it may be section 16 "protocol-enforcement
  logic", which needs a human PR review as well as a different-model review.
  The AI does not decide this.
