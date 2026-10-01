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

# Part b2: the ways back from FREEZE and HALT, and the live-store gap record

Date: 2026-10-01. Coding AI: Claude Opus 5.5 (`claude-opus-5-5`). Same branch,
on `main` with PRs #35 and #36 merged in (`33b39a4`). Owner answers used:
Q27-1, Q27-2, Q27-3 (`OWNER_ANSWERS.md`), T27-01 "Allow it" (same file).

## What changed

| File | Change |
| --- | --- |
| `src/aqt/app/paper_loop.py` (section 16 protected) | `OwnerOverride` and `run_paper(overrides=...)`: the owner's section 14 override at an hour; the loop reconciles and calls `override_halt`. On success the loss-stop peak is reset to the equity then and the stop armed (Q27-1, Q27-2); nothing trades that hour. Owner command `FREEZE_EXIT`: reconcile, and on a pass `exit_freeze` to HALT. Reservations of unreconciled executor orders are released by the passed recovery reconciliation. No decision before a reconciliation that waited has ended (A2324R-4); REFUSE_START stamped when the startup check ended (A2324R-5) |
| `src/aqt/data/live_bars.py` | `GapRecord`, `LiveBarStore.acknowledge_gap`, `gaps()`, `next_open_time()`: an owner-signed record lets the store continue after a real Binance gap; the hours stay missing (Q27-3, T26-04) |
| `scripts/fetch_live_bars.py` | `--acknowledge-gap RESUMES_AT --actor --statement`: signs a gap record; no request is made |
| `tests/integration/test_paper_recovery.py` (new), `tests/unit/test_live_bars.py` | 9 and 8 new tests |
| `review/task27/OWNER_ANSWERS.md` | T27-01 answer recorded |

Behaviour:
- **Nothing leaves FREEZE by itself.** Only the owner's `FREEZE_EXIT`
  command starts a reconciliation; a failed one is logged with its reason and
  FREEZE stays (its incident is already open). A pass leads to HALT, never
  RUNNING (section 22); the incident stays open for the section 14 override.
  Default behaviour, and so the Task 25 drills, are unchanged.
- **HALT ends only on the override**, with all five section 14 artifacts:
  the owner supplies the incident ids (every open one), the written record,
  the cause, the owner action and the timestamp; the loop supplies the
  reconciliation. Any missing or wrong artifact is a logged refusal and HALT
  stays. A failed reconciliation at the override is a new safety event: the
  account FREEZEs with a new incident.
- A command for an hour that is skipped (startup or a reconciliation still
  waiting, a health breach, no bar) is logged as refused, never lost silently.
  A FREEZE_EXIT outside FREEZE is refused and the hour goes on.

## Review skills applied (AGENTS.md)

`task-gate-review`, `quant-code-review`, `scientific-reproducibility-review`
and `binance-quant-review` were read from `.agents/skills/` and applied by
the implementer. This is self-review, not independent review.

| ID | Source | Severity | Finding | Disposition |
| --- | --- | --- | --- | --- |
| T27-07 | quant-code-review (self) | BLOCKER, repaired | A FREEZE_EXIT in a non-FREEZE hour skipped that hour, including a FLATTEN step | Refused and the hour goes on; `test_freeze_exit_outside_freeze_is_refused_and_the_hour_goes_on` (fails without the repair) |
| T27-08 | binance-quant-review (self) | BLOCKER, repaired | A reconciliation mismatch at the override was only a refusal, not an incident (section 0) | FREEZE with `RECONCILIATION_FAILED`; `test_a_failed_reconciliation_at_the_override_freezes` (fails without the repair) |
| T27-09 | quant-code-review (self) | NON-BLOCKING, repaired | A recovery left the governor reservation of a frozen executor order held, so no later decision could be authorized (`OUTSTANDING_AUTHORIZATION`) | Released by the passed recovery reconciliation (`settle`); the override test fails with 88 such refusals without it |
| T27-10 | binance-quant-review (self) | NON-BLOCKING, open | The live store is a plain JSON-lines file, not hash-chained: an edit that keeps continuity (a bar value, a gap record's text) is not detected. The gap record's "signature" is the owner's name and statement, not a cryptographic signature | Disclosed; a chained or signed store is a later decision |
| T27-11 | binance-quant-review (self) | QUESTION | Whether Binance can have a real kline gap, and how it is announced, was not checked against official Binance documentation (no network check by the AI) | For the owner's walkthrough; the record trusts the owner's statement |
| T27-12 | scientific-reproducibility-review (self) | NON-BLOCKING, open | Task 25 drills not rerun on this machine: `data/raw` exploration archives are absent and the AI does not download Binance data | Owner to rerun on the PC: `python scripts/run_drills.py --config configs/paper_trading.example.toml --out <scratch>` then `diff -r <scratch> review/task25/drills` |

Mutation checks (each reverted): settle removed, 1 fails; REFUSE_START
stamp at start, 1 fails; no waiting-reconciliation skip, 1 fails; T27-07 and
T27-08 repairs removed, 2 fail. Every `T0..` test uses synthetic bars.

The T27-04 limit is closed; T27-05 is closed by the gap record.

## Validation (part b2)

Python 3.14.4, Linux aarch64 (Android proot), `.venv`, exit 0 each:
`pytest -q` 1672 passed, 4 skipped; `ruff check .` clean; `ruff format
--check .` clean; `mypy src scripts` no issues; `lint-imports` 6 kept;
`git diff --check` clean. Frozen files: a Python port of
`review/task6/verify_frozen.ps1` (PowerShell absent; same checks in the same
order, run from scratch space, not committed) printed PASS for 28/28 trusted
bytes and exact inventory, 14/14 sidecars, the Constitution self-hash, 7/7
manifest and protocol bindings, and the nested bindings. Task 25 drills: not
rerun (T27-12). Windows was not exercised (the lock's `msvcrt` branch).

Local gate: PASS for part b2 with T27-10, T27-11, T27-12 open. Required
before merge: different-model (Astra) review and the owner's section 16
walkthrough.

## Astra review of `2b94313` and repairs

Record: `ASTRA_REVIEW_2B94313.md` (committed `bf21419`), text-only (the
Codex sandbox cannot start here). Verdict FIX. Every reproduction in the
record was then run locally (`.venv`, `PYTHONPATH=.`) at `2b94313`: all
seven failed as the reviewer predicted. After the repairs all seven pass.

| ID | Astra severity | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- | --- |
| A27-1 | BLOCKER | AGREE — repaired | The hourly and final saves and SHUTDOWN used the hour's start, not the end of a reconciliation that waited; journal and log stamps went back (reproduced: `...03:00Z`, then `...01:00Z`). They now use the later of the two. The override's peak reset values equity at the last close before its reconciliation ended. | `test_saves_follow_a_recovery_that_waited` |
| A27-2 | BLOCKER | AGREE — repaired | A buy filled before a crash and found by the startup check left `last_increase` unset (reproduced: `None`). Any filled buy a passed reconciliation resolves, at startup or in a recovery, now moves `last_increase` to its decision time. | `test_a_buy_filled_before_a_crash_keeps_its_risk_increase` |
| A27-3 | BLOCKER | AGREE — repaired | A peak valued but not saved was lost (reproduced: 100, not 120). On resume every decision hour from the saved hour to the start is valued again from the bars and the saved holdings; the saved hour is included because a save can precede its valuation. Holdings are the saved ones: an order sent after the last save is resolved by the startup check, not replayed into the peak. | `test_a_peak_valued_but_not_saved_is_valued_again` (also asserts the LOSS_STOP incident in HALT) |
| A27-4 | BLOCKER | AGREE — repaired | A gap record began at the store's next hour even when valid bars before the gap had been refused with the batch (reproduced). A fetch now stores the bars before a gap and then refuses; `append` itself stays all-or-nothing. `acknowledge_gap` takes the first missing hour from the owner and refuses unless it is the hour the store expects. CLI: `--acknowledge-gap FIRST_MISSING RESUMES_AT`. | `test_a_gap_record_names_exactly_the_missing_hours`, `test_a_gap_in_the_reply_stores_only_the_bars_before_it` |
| A27-5 | BLOCKER | AGREE — repaired; provenance decided by the owner | Reading checked only a gap's place (reproduced: an unsigned hybrid row hid a bar). A row must now be exactly a bar or exactly a gap record; `GapRecord` enforces the whole contract (owner name and statement, hour-aligned UTC hours, UTC record time, a later end) on reading and writing. Provenance: owner answer "Name + statement" (`OWNER_ANSWERS.md`). | `test_a_bar_row_cannot_be_turned_into_a_gap`, `test_a_gap_record_is_checked_in_full_when_read` (unsigned, non-UTC, unaligned) |
| A27-6 | NON-BLOCKING | AGREE — repaired | `from_mapping` coerced and truncated (reproduced: `"12"` accepted). A snapshot is now accepted only if the state writes it back identically; `load_saved` checks every entry's record type. | `test_a_snapshot_must_parse_exactly` (4 cases), `test_a_foreign_entry_anywhere_in_the_journal_refuses` |
| A27-7 | NON-BLOCKING | AGREE — repaired | A replayed `STATE_RESUMED` refused the start (reproduced). It is opened in HALT or FREEZE and leaves the mode as it is, like `HALT_OVERRIDE_FAILED`. | `test_a_resumed_state_incident_is_replayed` |

Each new test fails at `2b94313` (14 failures; the gap-record tests also
because `acknowledge_gap` now takes the first missing hour) and passes after.
Self-review findings: Astra supported T27-07, T27-08, T27-09; T27-10 is now
the owner-accepted limit above; T27-11 and T27-12 stay open.

Validation after the A27 repairs (Python 3.14.4, Linux aarch64 proot, exit 0
each): `pytest -q` 1686 passed, 4 skipped; `ruff check .`, `ruff format
--check .`, `mypy src scripts`, `lint-imports` (6 kept), `git diff --check`
clean; frozen verification (Python port) PASS. Not yet re-reviewed.

## Astra re-review of `bca6984` and repairs

Record: `ASTRA_REREVIEW_BCA6984.md`, text-only. A27-2, A27-4, A27-5, A27-7
correct; A27-1, A27-3, A27-6 incomplete (via A27-8..A27-10, A27-12). Verdict
FIX. The reviewer's three reproductions were run locally at `bca6984`: all
failed as predicted (A27-8 stamps `00:00`, `02:00`, `00:00`; A27-9 peak 100,
no LOSS_STOP; A27-10 no new LOSS_STOP; A27-11 prefix written; A27-12
accepted). After the repairs all pass.

| ID | Astra severity | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- | --- |
| A27-8 | BLOCKER | AGREE — repaired | A refused override (or a failed reconciliation at it) fell through to the rest of the hour at the hour's start, after its reconciliation had ended. Any override attempt that reconciles now ends the hour; only HALT or FREEZE can follow, so nothing is traded either way, and the hour's loss check runs the next hour. | `test_a_refused_override_after_a_wait_ends_its_hour` |
| A27-9 | BLOCKER | AGREE — repaired | The replay valued missed hours with the saved holdings, missing a buy that filled before the crash. The saved hour is valued with the saved holdings (its valuation precedes its orders); every later missed hour with the holdings the startup reconciliation confirmed. Orders pending at a save are decided in the saved hour, so this is the loop's own sequencing. | `test_missed_hours_are_valued_with_the_confirmed_holdings` (peak 120, LOSS_STOP recorded, `last_increase` restored) |
| A27-10 | BLOCKER | AGREE — repaired | The replay restored the peak only. `_replay` now runs the loop's loss-stop bookkeeping for each missed hour: peak, re-arming, and the first hour the stop would have fired. A missed firing is raised at startup (alert, incident and, from RUNNING, FLATTEN under S-4). In FREEZE the stop neither fires nor disarms, as in the loop. | `test_missed_hours_rearm_the_loss_stop` |
| A27-11 | NON-BLOCKING | AGREE — repaired | The bars before a break were stored for a duplicate too. Only a forward gap keeps them; a duplicate or reordered bar refuses the whole reply, as the module states. | `test_a_duplicate_in_the_reply_stores_nothing` |
| A27-12 | NON-BLOCKING | AGREE — repaired | `load_saved` parsed only the last snapshot. Every snapshot must now parse exactly. | `test_an_earlier_malformed_snapshot_refuses` |
| T27-13 | self (found while repairing A27-10) | BLOCKER, repaired | Making FREEZE_EXIT a command (part b2) dropped the loss check's FREEZE exclusion: a fall in FREEZE opened a LOSS_STOP incident every armed hour, unlike before. The exclusion is restored. | `test_a_freeze_records_no_loss_stop` |

Each new test fails at `bca6984` (6 failures) and passes after.
`test_ending_a_halt_rearms_the_loss_stop_from_equity_now` now saves its
inflated peak with the stop spent: with it armed, the replay correctly
records the fall, which the override (naming only earlier incidents) then
refuses. The test's subject, the reset at the override, is unchanged.

Validation after these repairs (Python 3.14.4, Linux aarch64 proot, exit 0
each): `pytest -q` 1692 passed, 4 skipped; `ruff check .`, `ruff format
--check .`, `mypy src scripts`, `lint-imports` (6 kept), `git diff --check`
clean; frozen verification (Python port) PASS. Not yet re-reviewed.
