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

# Part b1: the loop saves and resumes the account

Date: 2026-09-29. Coding AI: Claude Opus 5.5 (`claude-opus-5-5`). Same branch.

## What changed

| File | Change |
| --- | --- |
| `src/aqt/app/paper_loop.py` | `run_paper(journal=..., venue=...)`: load on start, resume, save; `_resume` replays alarms the journal missed |
| `src/aqt/app/state.py` | `incidents_seen` (incident-log length at save); `StateJournal.load_saved` (snapshot plus save time) |
| `src/aqt/execution/safety.py` (section 16 protected) | `SafetyController.before_send` hook, called after a FLATTEN sell is recorded and before it is placed; `startup_check(resuming=...)`: open incidents refuse only a start that would be RUNNING |
| `tests/integration/test_paper_restart.py` (new) | 12 tests, including kill-at-every-write |

Behaviour, with a journal (without one, nothing changes; drills below):
- **Saves**: after startup, after every hour, after an owner command, and
  before any order is placed (executor order: its client id as sent with
  unknown outcome; FLATTEN sell: through `before_send`). A save that fails
  stops the run with the refuse-start marker, before the order is placed.
- **Resume**: the saved mode, moved on by every incident opened after the
  snapshot (through the frozen-by-code `MODE_TRANSITIONS` table), so a crash
  between an alarm and its save cannot resume RUNNING. HALT, FLATTEN and
  FREEZE resume as themselves; a resumed FLATTEN keeps selling. Peak, latch,
  last risk increase and zero-fill streak are restored.
- **Startup reconciliation** includes the saved unsettled orders and FLATTEN
  sells, so an order sent just before a crash is found (or confirmed absent
  under section 21) rather than lost or counted twice.
- **REFUSE_START** added: damaged journal chain or unparseable snapshot; an
  incident log shorter than the snapshot recorded; an incident that cannot
  follow the saved mode; a start not after the last save.
- Nonces of a resumed run are seeded with its start time, so no client order
  id is reused across runs.

## Findings and limits (T27-nn)

- **T27-01 (owner-visible).** An open incident no longer refuses a start that
  resumes HALT, FLATTEN or FREEZE; those modes cannot trade, and section 14
  ("Trading resumes only after incident closure plus successful
  reconciliation") is still enforced by `override_halt`. A start that would be
  RUNNING with an incident open is still refused. This needs the owner's yes in
  the walkthrough.
- **T27-02.** A resumed HALT or FREEZE with no incident open (a crash between
  closing the incidents and saving RUNNING) opens `STATE_RESUMED`, so the
  owner's section 14 override has an incident to close.
- **T27-03 (limit).** An owner FLATTEN command from RUNNING opens no incident;
  a crash after it but before its save loses it, and the owner must repeat it.
- **T27-04 (limit).** The loop still has no path out of FREEZE, and no owner
  HALT override; both are part b2 (the override, with Q27-1/Q27-2: the
  loss-stop peak resets to equity at the override).
- **T27-05 (deferred).** Q27-3 (signed gap record) belongs to the Task 26
  live store, which is on PR #36 and not in this branch's base.
- **T27-06.** `scripts/run_paper_trading.py` does not use a journal: its venue
  is a fresh simulator per run, which a resumed record could never reconcile
  with. The journal is for the forward-paper and shadow apps (Tasks 28, 30).

## Tests

Kill test: a 16-hour run that buys, is FLATTENed by the owner in steps and
HALTs, killed before each of its durable writes in turn (every incident,
event and journal append; the marker removed, as after a power cut), then
restarted at the hour after the last save against the same venue. Every
restart passes its startup reconciliation, never resumes RUNNING with an
incident open, ends with the saved record equal to the venue balances and
nothing unsettled, and ends HALTed.

Mutation checks (each reverted): no pre-send save for executor orders, 1
test fails; no `before_send`, 1 fails; no alarm replay, 1 fails; no hourly
save, 1 fails; peak not restored, 1 fails.

## Validation (part b1)

Windows 11, `.venv` Python 3.14: `pytest -q` 1620 passed, 4 skipped;
`ruff check .` clean, `ruff format --check .` 104 files formatted; `mypy src
scripts` no issues (54 files); `lint-imports` 6 kept; `git diff --check`
clean; no frozen file differs from `main`. `scripts/run_drills.py` rerun
into a scratch directory is byte-identical to `review/task25/drills`
(`diff -r`). `verify_frozen.ps1` not run (PowerShell 7 absent); git shows no
frozen diff.
