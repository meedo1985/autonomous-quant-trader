# Task 28 local report: Telegram alert sink

Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-02. Branch
`task28-telegram-alerts` from `main` `995126d`. Design `DESIGN.md`; owner
answers Q28-1 (type the code), Q28-2 (remind hourly, keep running) in
`OWNER_ANSWERS.md`.

## Changes

| File | What |
| --- | --- |
| `src/aqt/monitoring/telegram.py` (new) | `TelegramSink` (CRITICAL only; a failed send becomes a local CRITICAL `ALERT_CHANNEL` event, never raised); `TelegramRequest` guard (HTTPS to `api.telegram.org` only); `urllib_transport` (POST, redirects refused, 10 s timeout); `read_windows_credential` (Credential Manager entry `aqt-telegram`, standard library `ctypes`); `ChannelTests` (hash-chained ledger of sent and acknowledged tests, the code kept as its SHA-256; `problem()`, `due()`); `owner_channel` factory for the owner-run scripts. |
| `src/aqt/monitoring/events.py` | New event kind `ALERT_CHANNEL`. |
| `src/aqt/monitoring/alerts.py` | Redaction also matches the Telegram token shape. |
| `src/aqt/app/paper_loop.py` | Optional `channel`: start refused if the test is unacknowledged, overdue or its ledger damaged; each hour, at most once per wall-clock hour, a due test is sent and an overdue one raises a CRITICAL alert; the mode is never changed (Q28-2). Without `channel` nothing changes. |
| `scripts/alert_channel.py` (new) | Owner commands `test`, `ack <code>`, `status`. |
| `scripts/run_paper_trading.py` | `--telegram` adds the sink and the channel check. |
| `tests/unit/test_telegram.py` (new) | 18 tests, fake transport and fake clock; nothing is sent. |

## Acceptance (roadmap 2, Task 28)

| Criterion | Evidence |
| --- | --- |
| A failed send is itself logged and alerted locally | `test_a_failed_send_is_alerted_locally_without_the_token` (network error, HTTP 500, non-JSON, `ok:false`): one local CRITICAL `ALERT_CHANNEL` on stdout and in the hash-chained log, nothing raised |
| An overdue test refuses start | `test_an_overdue_test_refuses_the_start`, `test_an_untested_channel_refuses_the_start`, `test_a_damaged_test_ledger_refuses`; 7-day boundary in `test_an_acknowledged_test_lasts_seven_days` |
| The token never appears in any log, report or test | Error texts are built from the exception type and status only; Telegram's own description has the token replaced; same test checks stdout and log bytes for a token-bearing exception and reply; `test_the_credential_never_prints_its_token`; `test_a_token_in_an_event_field_is_redacted`. The test token is synthetic. The real token is read only from the credential store at run time. |
| Q28-1 code acknowledgment | `test_a_test_must_be_acknowledged_with_its_code` (wrong code, repeat refused; code not stored in clear) |
| Q28-2 in-run behaviour | `test_an_overdue_test_during_a_run_is_sent_and_reminded_hourly` (test sent by the run, reminders limited by the wall clock, mode RUNNING) |

The real credential reader was run once on this PC with no entry stored:
`python scripts/alert_channel.py --ledger <scratch> status` printed
"Refused: no credential 'aqt-telegram' in the credential store", exit 2. No
message was sent to Telegram by this AI or by any test.

## Findings

| ID | Severity | Finding | Disposition |
| --- | --- | --- | --- |
| T28-01 | NON-BLOCKING | The credential reader's success path (a stored entry) is not exercised by any test: testing it would write to the owner's credential store. | Disclosed. The owner's first `alert_channel.py test` exercises it; a wrong decoding shows as a refused send (HTTP 401/404), reported locally. |
| T28-02 | NON-BLOCKING | A new weekly test becomes due once more than 7 days have passed since the last one (corrected after Astra's re-review), so every week there is an overdue window (hourly reminders) until the owner types the code. | As answered in Q28-2. Sending earlier (say at 6 days) would avoid it; an owner choice if the reminders are a nuisance. |
| T28-03 | NON-BLOCKING | The code is 6 digits stored as its SHA-256: anyone who can read the ledger can recover it by trying a million values. | Whoever can read the ledger is on the app's machine and could acknowledge anyway; the hash only keeps the code out of plain view. |
| T28-04 | NON-BLOCKING | A send blocks the loop while it runs; the 10 s timeout bounds each socket operation, not the whole call (corrected after Astra). | Acceptable for an hourly loop; CRITICAL events are rare. |
| T28-05 | NON-BLOCKING | The local failure event is written to the local sinks directly, so the loop's event count in the run report does not include it. | It is in the operations log; the count is informational. |
| T28-06 | QUESTION (Task 30) | The credential reader is Windows-only; on another system the channel refuses to start. | The server's system is the owner's choice (D-7); its equivalent is added with Task 30. |

## Validation (2026-10-02, Python 3.14.7, Windows 11, exit 0 each)

- `python -m pytest -q -p no:cacheprovider`: 1724 passed, 4 skipped.
- `ruff check .`: all checks passed. `ruff format --check .`: clean (after
  formatting the new test file).
- `mypy src scripts`: no issues, 58 source files.
- `lint-imports`: 6 kept, 0 broken.
- `git diff --check`: clean.
- Frozen verification (Python port of `review/task6/verify_frozen.ps1`;
  PowerShell 7 not installed): 28/28 trusted bytes and exact inventory,
  14/14 sidecars, Constitution self-hash PASS; no file under `docs/`,
  `protocols/`, `schemas/`, `specs/` or the manifest differs from `main`.
- Task 25 drills: `python scripts/run_drills.py --config
  configs/paper_trading.example.toml --out <scratch>`, exit 0;
  `diff -r <scratch> review/task25/drills`: no difference.

LOCAL GATE: PASS. Required before merge (section 16, start check is
protocol-enforcement logic): independent different-model review (Astra),
then the owner's walkthrough. Adversarial review status: NOT SENT.

## Astra review of `3f23e14` and repairs

Record: `ASTRA_REVIEW_3F23E14.md` (prompt `ASTRA_PROMPT_3F23E14.md`), run on
this PC with read-only commands, no network, no credential store; every
finding reproduced with synthetic tokens. Verdict FIX.

| ID | Astra severity | Decision | Repair | Validation |
| --- | --- | --- | --- | --- |
| A28-1 | BLOCKER | AGREE — repaired | Telegram's reply description is no longer passed on at all; the reason is the HTTP status and "not accepted" only. | `test_a_failed_send_is_alerted_locally_without_the_token` (180 characters then the token) |
| A28-2 | BLOCKER | AGREE — repaired | The token pattern starts at `(?<!\d)` instead of `\b`, so it matches after `bot` in the URL. | `test_a_token_inside_its_url_is_redacted` (field value and field name) |
| A28-3 | BLOCKER | AGREE — repaired | A failed `send_test` writes a CRITICAL `ALERT_CHANNEL` event (`failed_kind` CHANNEL_TEST) to the local sinks; the owner's script adds a hash-chained `alert_channel_log.jsonl` beside the ledger. | `test_a_failed_test_send_is_alerted_locally` |
| A28-4 | BLOCKER | AGREE — repaired | `send` contains every failure in building, sending and reading; the reply is parsed up to 64 KiB and the transport reads at most that. The loop's hourly check catches every exception (type name only). | Deep-JSON case in the failed-send test; `test_a_check_that_fails_does_not_stop_the_run` |
| A28-5 | BLOCKER | AGREE — repaired | Every record carries the SHA-256 fingerprint of chat id and token; problem, due and acknowledge count only this channel's records; a code sent to another channel is refused. | `test_a_new_bot_or_chat_needs_its_own_test` |
| A28-6 | BLOCKER | AGREE — repaired | A record dated after the clock is a problem ("the clock is behind ..."), nothing is due and no test is sent; the hourly check runs again whenever the clock reads before its last check. | `test_a_clock_set_back_is_reported_not_trusted`, `test_a_clock_going_back_does_not_silence_the_hourly_check` |
| A28-7 | NON-BLOCKING | AGREE — repaired | A code whose hash is already in the ledger is drawn again. | `test_a_code_is_never_issued_twice` |
| A28-8 | NON-BLOCKING | AGREE — repaired | Every record is checked (type, exact keys, 64-hex digests, UTC timestamp, an acknowledgment of a recorded send); any problem, of any type, is a `ChannelError` with no secret. | `test_a_well_chained_but_malformed_record_refuses` |
| A28-9 | NON-BLOCKING | AGREE — repaired | A blob that is not text is a `ChannelError` raised outside the decoding handler, so no exception context carries it. | `test_the_credential_reader_with_a_fake_store` (not-text case) |

On the local findings: T28-01 is now covered with a fake `advapi32` as the
reviewer showed (UTF-16LE as `cmdkey` stores it, plain UTF-8, not text;
the memory is freed once each), without touching the real store. T28-04's
wording is corrected above. T28-02, T28-03, T28-05, T28-06 as before, the
reviewer agreeing.

Each new test fails at `3f23e14` (14 failures with the changed refusal
text) and passes after.

Validation after these repairs (2026-10-02, Python 3.14.7, Windows 11, exit 0
each): `pytest -q` 1738 passed, 4 skipped; `ruff check .`, `ruff format
--check .`, `mypy src scripts` (58 files), `lint-imports` (6 kept),
`git diff --check` clean; no file under `docs/`, `protocols/`,
`schemas/`, `specs/` or the manifest differs from `main`; Task 25 drills
rerun, identical to `review/task25/drills`. Re-reviewed below.

## Astra re-review of `816cd26` and repairs

Record: `ASTRA_REREVIEW_816CD26.md` (prompt `ASTRA_PROMPT_816CD26.md`;
attempt 1, cut off by the usage limit with no verdict, is
`ASTRA_REREVIEW_816CD26_ATTEMPT_1.md`). Verdict ACCEPT: A28-1..A28-7 and
A28-9 CORRECT, A28-8 INCOMPLETE (its remainder is A28-10), four new
NON-BLOCKING findings. The owner asked for all four to be repaired.

| ID | Astra severity | Decision | Repair | Validation |
| --- | --- | --- | --- | --- |
| A28-10 | NON-BLOCKING | AGREE — repaired | A ledger that records a send with a code hash already sent is refused ("issues a code twice"), so an old code cannot acknowledge a newer test. This also closes the rest of A28-8. | `test_a_code_sent_twice_in_the_ledger_refuses` |
| A28-11 | NON-BLOCKING | AGREE — repaired | `problem()` reads the clock inside its handler and returns a refusal for any error ("channel test unreadable: <type>"); the loop's hourly check reads the clock inside its handler, so a bad clock is reported every decision hour and the loop runs on. | `test_a_bad_clock_is_reported_not_raised` |
| A28-12 | NON-BLOCKING | AGREE — repaired | The transport reads one byte past the 64 KiB bound; a reply longer than the bound is never parsed and counts as not accepted. | `test_a_reply_past_the_bound_is_not_a_success` (through `urllib_transport` with a fake opener, and through the sink) |
| A28-13 | NON-BLOCKING | AGREE — repaired | `alert_channel.py` refuses a `--ledger` named `alert_channel_log.jsonl` (any letter case), before anything is sent or written. The log keeps its name, so the owner's existing log stays where it is. | `test_the_test_ledger_cannot_share_the_failure_log` (two runs, no request, no file) |

The T28-02 wording is corrected above (due after 7 days, not at 7 days).
The other T28 dispositions stand, the reviewer agreeing.

Each of the four new tests fails at `816cd26` (4 failed, 32 passed) and
passes after.

Validation after these repairs (2026-10-02, Python 3.14.7, Windows 11, exit 0
each): `pytest -q -p no:cacheprovider` 1742 passed, 4 skipped; `ruff check .`
all passed; `ruff format --check .` 111 files formatted; `mypy src scripts`
no issues in 58 files; `lint-imports` 6 kept, 0 broken; `git diff --check`
clean; frozen verification (Python port of `review/task6/verify_frozen.ps1`)
28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash,
7/7 manifest and protocol bindings, nested bindings; no file under `docs/`,
`protocols/`, `schemas/`, `specs/` or the manifest differs from `main`; Task
25 drills rerun, identical to `review/task25/drills`.

LOCAL GATE: PASS. Astra's ACCEPT covers `816cd26`; these four non-blocking
repairs follow its own suggested corrections and were not sent back for a
third review. Remaining before merge: the owner's walkthrough (section 16).

## Owner's real-channel test (2026-10-02)

The owner stored the bot credential in Windows Credential Manager entry
`aqt-telegram`; the token was never shown to this AI, in the chat,
the repository or a log. The first two `alert_channel.py test` runs were
refused by Telegram with HTTP 404, because the stored password was not the
token as given (once repeated, once only the part after the colon). Both
were reported as local CRITICAL `ALERT_CHANNEL` events reading only
"HTTP 404, not accepted", with no token; they were diagnosed from the
stored value's length and shape only, never its content. After the owner
stored it again, two tests were sent and acknowledged by typing their codes,
at 12:45Z and 12:51Z. `status` then reported the channel tested; the
channel is current until 2026-10-09 12:51Z.
