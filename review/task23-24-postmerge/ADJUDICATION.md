# Tasks 23-24 post-merge review: adjudication

Record: `ASTRA_REVIEW_1E02472.md` (committed `6450768` before these repairs).
Also repairs Task 25's A25R-4 (`review/task25/ASTRA_REREVIEW_9727496.md`),
which touches the same loop. Repairs by Claude Opus 5.5 on branch
`review/task23-24-astra-postmerge`.

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| A2324-1 | AGREE — BLOCKER, repaired | `reconcile` resolved an order whose outcome was unknown to "absent" on its first NOT_FOUND, with no delayed re-query (§21). New `AbsenceCheck(delay, queries, sleep)`: such an order is confirmed absent only after `queries` NOT_FOUND answers, `delay` apart. Without an `AbsenceCheck` the order stays unresolved (fail closed). `startup_check` accepts it; the paper loop passes the owner-set executor values (T22-Q1: 10 s, 2 answers) on its simulated clock at startup, after executor orders, and after FLATTEN steps. A known order (local copy) that returns NOT_FOUND is still a difference at once. | `test_one_not_found_never_resolves_an_unknown_order` (no check: unresolved, FREEZE kept); `test_a_lagging_not_found_is_queried_again_after_the_delay` (the reviewer's scenario with one lagging NOT_FOUND: the delayed query finds the expired order, one 10 s wait). Three existing tests now pass the check explicitly. |
| A2324-2 | AGREE — BLOCKER, repaired | The loop still required `held >= min_qty` before firing LOSS_STOP, so a dust account breached silently (incomplete F24R-1). The condition is removed; the latch still limits the stop to once per fall. From RUNNING a dust holding enters FLATTEN, which ends at once in HALT (no sellable step). | `test_a_breach_on_a_holding_too_small_to_sell_still_alerts` (reviewer's scenario: 0.000009 BTC, owner HALT, 30%+ fall: one CRITICAL LOSS_STOP, no order). |
| A2324-3 | AGREE — repaired | `load_config` ignored `max_notional`. It now reads it when present; absent means none. | `test_the_configuration_reads_the_maximum_notional`. |
| A2324-4 | AGREE — repaired | A malformed `FROZEN_HASHES.json` raised before the alert router existed. The parse is guarded; `frozen_hash_problems` then refuses the start through the logged REFUSE_START path and the report names the hashes "unreadable". | `test_a_malformed_frozen_manifest_is_a_logged_refusal`. |
| A25R-4 | AGREE — repaired | A FLATTEN sell whose reply was lost was not logged as an ORDER nor counted. The loop now logs every new FLATTEN id without a returned order as `ORDER` `state FLATTEN_UNKNOWN` (CRITICAL) with the holding it was sized from, and counts it. | `test_a_flatten_sell_with_a_lost_reply_is_logged_and_counted`. |

Each new test fails on `main` before these repairs (the two `test_safety.py`
tests cannot import there, since `AbsenceCheck` did not exist) and passes
after.

Validation (Windows 11, `.venv` Python 3.14): `pytest -q` 1582 passed, 4
skipped; `ruff check .` and `ruff format --check .` clean (101 files);
`mypy src scripts` no issues (53 files); `lint-imports` 6 kept; `git diff
--check` clean; no frozen file differs from `main`. The Task 25 drills rerun
into a fresh directory are byte-identical to the committed evidence, so the
repairs change no drill outcome.

These repairs touch section 16 protected code (reconciliation, safety,
loop) and need an Astra review and the owner's behavioural review before
merge.

## Astra re-review attempt 1 (cut off): A2324R-1, A2324R-2

Record: `ASTRA_REREVIEW_ATTEMPT_1.md` (committed `4b0d72f` before these
repairs). No verdict; the reviewer confirmed the A2324-2..4 reproductions and
the one-query FREEZE case now pass.

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| A2324R-1 | AGREE — repaired | `AbsenceCheck` trusted `sleep`. It now takes a `clock`; after each wait the clock must have advanced by at least the delay, or the order is unresolved ("the clock did not advance by the protocol delay"), as the executor already requires. | `test_absence_needs_the_clock_to_advance_by_the_delay` (no advance; 5 s backwards). |
| A2324R-2 | AGREE — repaired | The waits left reports stamped at the pre-wait time. `reconcile` now stamps a report that used an `AbsenceCheck` at the later of `at` and the clock after the waits. Callers must then act at or after that time: `exit_freeze` and `override_halt` already refuse a report later than their `at`. The loop skips any decision hour before the startup check's report time, so nothing is traded backdated. | `test_the_report_is_stamped_after_the_waits` (report at `at + 10 s`); `test_no_decision_is_stamped_before_a_waiting_startup_check` (the reviewer's scenario; fails when the skip is removed: a FILLED order at 00:00). Two recovery tests now act at the report's time. |

Validation after the A2324R repairs: `pytest -q` 1586 passed, 4 skipped;
ruff, format (101 files), mypy (53 files), 6 import contracts and `git diff
--check` clean; no frozen file differs from `main`; the Task 25 drills rerun
byte-identical. Not yet re-reviewed.

## Fable 5.1 re-review of `c9e4c44` (same-family stand-in)

Record: `FABLE_REREVIEW_C9E4C44.md` (committed `d30e9c8` before these
repairs). A2324-1, A2324-2, A2324-3, A25R-4 and A2324R-1 judged correct;
A2324-4 and A2324R-2 incomplete. Verdict FIX.

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| F35-1 | AGREE — BLOCKER, repaired | My A2324R-2 skip dropped owner commands keyed to skipped hours. The skip now applies any owner command for a skipped hour when the startup check ends (`apply_owner`), so an owner HALT wins before any trading. | `test_an_owner_halt_at_a_skipped_start_hour_still_applies` (reviewer's scenario: HALT, 0 orders, one OWNER_HALT) |
| F35-2 | AGREE — repaired | A manifest that is valid JSON but not an object is treated as unreadable; `frozen_hash_problems` also catches `TypeError` and `AttributeError`. Refused through the logged path. | `test_a_manifest_that_is_not_an_object_is_a_logged_refusal` (`[]`, `null`, a string) |
| F35-3 | AGREE — repaired | The controller records each FLATTEN order's quantity and cap (`attempts`) before sending; FLATTEN_UNKNOWN logs `orig_qty` and `limit_price`. | Lost-reply test asserts both fields |
| F35-4 | AGREE — repaired | STARTUP START and the controller's entry time use the startup report's time (after the waits); `startup_check` opens its incident at the report's time. | Waiting-startup test asserts START at 00:00:10 (one 10 s wait) |
| Dust from RUNNING | AGREE — test added | — | `test_a_dust_breach_while_running_ends_in_halt_without_an_order` |

Each F35 test fails on `c9e4c44` (6 failures) and passes after.

Validation after the F35 repairs: `pytest -q` 1591 passed, 4 skipped; ruff,
format (101 files), mypy (53 files), 6 import contracts, `git diff --check`
clean; no frozen file differs from `main`; Task 25 drills rerun
byte-identical. The different-family (Astra) re-review is still required.

## Astra re-review of `ca4f1bd` (text-only)

Record: `ASTRA_REREVIEW_CA4F1BD.md` (committed `a9c7959`). The Codex
sandbox cannot start on the owner's Android/proot machine, so the reviewer
read attached texts and ran nothing. A2324-1..4, A25R-4 and F35-1..4 judged
correct; A2324R-1 and A2324R-2 incomplete (via A2324R-3, A2324R-4). Verdict
FIX.

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| A2324R-3 | AGREE — BLOCKER, repaired | `reconcile` only compared the readings around each wait, and stamped the report with `max(at, clock())`, so a final reading back at the start passed and backdated the report. The latest accepted reading now starts at `at` and is threaded through every query; a reading before it leaves the order unresolved ("the clock moved backwards"), and a final reading before it fails the report. The report is stamped at the later of the latest accepted reading and the final one, never earlier. | `test_a_clock_that_moves_back_fails_instead_of_backdating` (reviewer's scenario: fails, stamped `at + 10 s`); `test_a_clock_behind_the_start_confirms_nothing`. Both fail on `ca4f1bd` and pass after. |
| A2324R-4 | AGREE — NON-BLOCKING, open | Startup does not carry `decision.report.next_record()` forward, so orders confirmed absent are queried again, and FLATTEN reconciliation waits do not advance the loop. Bounded, sell-only simulator behaviour; no extra exposure shown. Left for the owner to schedule (with Task 27 part b2, which rewires startup resume). | Not yet. |
| A2324R-5 | AGREE — NON-BLOCKING, open | REFUSE_START after a waiting startup check is stamped `config.start`, before its incident. Same scheduling as A2324R-4. | Not yet. |

Validation after the A2324R-3 repair (Python 3.14.4, Linux aarch64 proot):
`pytest -q` 1593 passed, 4 skipped; ruff, format, mypy, 6 import contracts
and `git diff --check` clean. Different-family re-review of the repair is
still required.
