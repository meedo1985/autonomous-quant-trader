# Task 27 local report, part a: storing and loading account state

Date: 2026-09-29. Coding AI: Claude Opus 5.5 (`claude-opus-5-5`). Branch
`task27-persistent-state`, stacked on `review/task23-24-astra-postmerge`
(PR #35, not yet merged) because Task 27 builds on its loop changes.
Design and owner answers: `DESIGN.md`, `OWNER_ANSWERS.md`.

## What changed (part a)

| File | Change |
| --- | --- |
| `src/aqt/app/state.py` (new) | `AccountState` (the design's section 2 table), `StateJournal` (hash-chained snapshots on `aqt.core.ledger`: locked, fsynced, verified on read), `AccountDir` (one directory per account: incident log, operations log, journal; the refuse-start marker sits beside the incident log, so it is per account too) |
| `tests/unit/test_account_state.py` (new) | 15 tests |

Behaviour:
- A snapshot round-trips exactly, Decimals as strings (no float rounding),
  orders field by field.
- The last snapshot is the state. An account never run has none.
- A damaged chain (a hand edit, e.g. HALT turned into RUNNING; a torn last
  line) raises `LedgerError`; an entry of another type, or a snapshot that
  does not parse exactly (unknown mode, NaN or non-string decimal, naive
  time, wrong types, incomplete order), raises `StateError`. The caller must
  refuse the start on either (part b).

Mutation checks: loading the first snapshot instead of the last fails 2
tests; dropping the record-type check fails 1; accepting non-string decimals
fails 1.

## Not in part a (part b)

The loop does not yet save or load state; `run_paper` is unchanged.
Part b: save a snapshot after every change, load on start (a FREEZE or HALT
resumes as FREEZE or HALT), refuse on a damaged or inconsistent journal,
apply Q27-1/Q27-2 (on the owner's HALT override, the loss-stop peak resets to
current equity), and the Q27-3 signed gap record for the live store.
Acceptance for the whole task (kill at every step and restart) is part b's.

## Validation

Windows 11, `.venv` Python 3.14: `pytest -q` 1606 passed, 4 skipped;
`ruff check .` and `ruff format --check .` clean (103 files); `mypy src
scripts` no issues (54 files); `lint-imports` 6 kept; `git diff --check`
clean; no frozen file differs from `main`.
