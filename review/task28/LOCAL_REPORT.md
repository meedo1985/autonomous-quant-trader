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
| T28-02 | NON-BLOCKING | The weekly test is due exactly 7 days after the last one, so every week there is an overdue window (hourly reminders) until the owner types the code. | As answered in Q28-2. Sending earlier (say at 6 days) would avoid it; an owner choice if the reminders are a nuisance. |
| T28-03 | NON-BLOCKING | The code is 6 digits stored as its SHA-256: anyone who can read the ledger can recover it by trying a million values. | Whoever can read the ledger is on the app's machine and could acknowledge anyway; the hash only keeps the code out of plain view. |
| T28-04 | NON-BLOCKING | A send can block the loop for up to its 10 s timeout per CRITICAL event. | Acceptable for an hourly loop; CRITICAL events are rare. |
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
