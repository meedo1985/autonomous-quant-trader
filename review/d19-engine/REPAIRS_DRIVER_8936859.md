# D-19 driver repairs after the Claude reviews of 8936859

Author: Claude Opus 5.5 (`claude-opus-5-5`), the driver's implementer.
Session https://claude.ai/code/session_01JyNxBd7qn8zGQu2HzD5QXm,
2026-10-07. Owner instruction: "Make what need fix them" (after the code
repairs were proposed). Base: `4f15402` (code equal to `8936859`).

Reviews adjudicated:
- `CLAUDE_REVIEW_DRIVER_8936859.md` (Opus 5.5, findings CRD-1 to CRD-4);
- `FABLE_REVIEW_DRIVER_8936859.md` (Fable 5.1, findings FD-1 to FD-6).

Both reviews are by Claude models. Neither is the different-model review
required by Constitution section 16; a Codex re-review is still needed (see
the end of this record).

## Adjudication

| ID | Severity | Verdict | Evidence | Disposition | Validation |
| --- | --- | --- | --- | --- | --- |
| FD-1 / CRD-1 | BLOCKER for dev/held-out / NON-BLOCKING for threshold pilots | AGREE | Reproduced here: 546 of 20,000 values differ; 0 with `NPY_DISABLE_CPU_FEATURES=X86_V4`; `test_block_length_is_bit_identical_to_production` failed | **Repaired.** `fast._squares` uses Python `**`, the reference's own operation, instead of NumPy `power`. The cost is the same (25 µs against 26 µs per T=365 column). `self_check` now compares `mean_var` with the pure-Python reference, and runs in `rundef.gating()` (recording) and `rundef.start_gate()` (every start), as a `U_ops` refusal | New tests: `test_mean_var_is_bit_identical_to_the_reference_on_every_runtime`, `test_a_runtime_where_fast_differs_is_never_recorded`, `test_a_runtime_where_fast_differs_stops_the_start`; the old failing test now passes on AVX-512 Linux |
| FD-2 / CRD-2 | NON-BLOCKING | AGREE | Probes by both reviewers; the first repair attempt (`wait(FIRST_EXCEPTION)` plus `cancel_futures`) still let 5 queued jobs run, because jobs already in the pool's call queue cannot be cancelled | **Repaired** in `run_all`: at most one job per worker is handed to the pool. The first exception is raised when the other running job ends, and no later job starts | `test_a_failed_chain_stops_the_run_without_waiting_for_earlier_ones`, 5 of 5 runs passed; it fails with the old `pool.map` |
| FD-4 / CRD-3 | QUESTION / NON-BLOCKING | AGREE | Analysis by both reviewers (deterministic content, so a crash or wasted work, not wrong bytes) | **Repaired:** exclusive lock on `<store>/<namespace>/.lock`, taken after the parent's start gate and held for the run; `fcntl.flock` on Linux, `msvcrt.locking` on Windows; released when the process ends | `test_a_second_run_on_the_same_store_is_refused` (Linux); the Windows branch is not exercised here (see limitations) |
| FD-6 | NON-BLOCKING | AGREE | Code reading | **Repaired:** the definition is loaded inside the `try`, so a bad file gives a message and exit 1; each process removes its empty bytecode directory at exit | `test_a_missing_definition_is_a_message_not_a_traceback` |
| FD-3 | NON-BLOCKING | AGREE | The reference-vector suite has no `classifier.diagnostics` case; the identity hashes only two NumPy binaries | **Not repaired.** Adding a classifier case and hashing every NumPy `.so` changes the run-definition content: proposal for the owner. Within one pinned image the digest covers it, so threshold pilots are sound | — |
| FD-5 | QUESTION | AGREE (information) | Adding development changes the code hash and `SEED_NAMESPACES` | **Not repaired; no code change proposed.** Owner information: pilot threshold chunks are disposable and cannot become qualification chunks | — |
| CRD-4 | QUESTION | open | Pilots reuse the §8 threshold seeds | **Not repaired.** Question for the owner and the statistician before development is built; it would need a preregistration amendment if a pilot namespace is wanted | — |

Also proposed for the owner, unchanged by this repair: whether the pinned image
should also disable AVX-512 dispatch or the server should lack it. With FD-1
repaired this no longer affects `fast`, but the canaries and method V's
`einsum`/BLAS paths still depend on the CPU features recorded in the runtime
identity.

## Changed files

- `calibration/fast.py`: `_squares` and the new `self_check`.
- `calibration/rundef.py`: `fast.self_check()` in `gating()` and
  `start_gate()`.
- `scripts/d19_run.py`: `lock`, `run_all`, loading inside the `try`, bytecode
  directory cleanup.
- `tests/unit/test_calibration_engine.py`, `tests/unit/test_calibration_rundef.py`:
  six new tests. One assertion changed:
  `test_the_parent_hands_its_definition_hash_to_every_worker` now checks
  that no chunk is written, instead of that the store directory does not
  exist. The lock file is created before the workers start, and the
  property the test protects is that no chunk is written.

The engine code hash changes. Any run definition recorded before this commit
no longer passes the start gate. None has been recorded on the server.

## Mutation checks (each change undone in turn, then restored)

| Mutation | Result |
| --- | --- |
| `run_all` back to `pool.map` | the failed-chain test fails |
| no `fcntl.flock` | the second-run test fails |
| `_squares` back to NumPy `power` | 2 tests fail (the bit-identity test and the block-length test) |
| no `self_check` in `gating`/`start_gate` | 2 tests fail |

## Validation (Linux x86-64, AVX-512, Python 3.13.16, NumPy 2.5.3, scratchpad venv with `pip install -e ".[dev]"`)

| Command | Exit | Result |
| --- | --- | --- |
| `python -m pytest -q -p no:cacheprovider` | 0 | 1875 passed, 7 skipped in 362 s |
| `ruff check .` | 0 | All checks passed |
| `ruff format --check .` | 0 | 132 files already formatted |
| `mypy src` | 0 | no issues, 53 files |
| `mypy calibration scripts/d19_run.py scripts/d19_run_definition.py` | 0 | no issues, 11 files |
| `lint-imports` | 0 | 6 kept, 0 broken |
| `git diff --check` | 0 | clean |

**Frozen artifacts.** `git diff --quiet origin/main -- docs protocols schemas specs FROZEN_HASHES.json FROZEN_HASHES.json.sha256`
exits 0, so these paths are byte-identical to merged `main`, and there are no
untracked files in them. An independent Python check found:
- 14 of 14 sidecar SHA-256 values match their files;
- the 7 raw-file hashes in `FROZEN_HASHES.json` each match the named frozen
  file.

`review/task6/verify_frozen.ps1` was not run, because PowerShell is not
installed here. The Constitution's canonical self-hash was not recomputed;
it rests on byte identity with `main`, where it was last verified.

## Limitations

- Not run on Windows. The `msvcrt.locking` branch and the Windows test run
  remain to be checked on the owner's laptop.
- Not run in the pinned image or on the server (FE-4, FE-7 still open).

## Local gate

`task-gate-review` with `quant-code-review` and
`scientific-reproducibility-review`, applied to this repair:
- **Determinism:** heads are returned in job order. Chunk bytes do not
  depend on scheduling (seeds are per replication).
- **No silent fallback:** every new path refuses with exit 1.
- **Scope:** no strategy, threshold, or governance change. Qualification is
  still refused. The repaired `fast` is bit-identical to the reference by
  construction.
- No secrets. No restricted data.

**LOCAL GATE: PASS** for threshold pilot scope.
Outstanding before merge:
- the Codex different-model re-review
  (`DRIVER_REREVIEW_PROMPT_5.md`, status **NOT SENT**: no Codex in this
  container, human relay needed);
- the owner's behavioural review;
- the Windows test run.
