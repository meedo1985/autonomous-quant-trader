# Task 28 design: Telegram alert sink

**Status:** design note, before code. Author: Claude Opus 5.5
(`claude-opus-5-5`), 2026-10-02. Authorized by roadmap 2 answer Q-D; the
token's existence by Q-B (`review/roadmap/ROADMAP_2_OWNER_ANSWERS.md`).
Owner settings: D-1 (private Telegram bot), D-2 (test every 7 days), D-8 (OS
credential store), `review/deployment/OWNER_SETTINGS_2026-09-29.md`.

## 1. What it does

- **`TelegramSink`** (`aqt.monitoring.telegram`): a `Sink` with minimum
  severity CRITICAL. Each event becomes one short text message to the
  owner's private chat through `https://api.telegram.org/bot<token>/sendMessage`.
  The event has already passed the router's redaction.
- **A failed send** (network error, timeout, non-200, Telegram `ok: false`)
  is not raised into the loop. The sink writes a CRITICAL `ALERT_CHANNEL`
  event to the local sinks (stdout and the hash-chained operations log),
  naming the failure without the URL or token. Roadmap acceptance: "a failed
  send is itself logged and alerted locally".
- **Credential:** one Windows Credential Manager entry, target
  `aqt-telegram`, username = chat id, password = bot token, read with the
  standard library (`ctypes`, `CredReadW`). Neither value is in the
  repository, a config file, a log, a report, a test, or this AI's context.
  A missing entry, or a non-Windows machine, is a `REFUSE_START` when the
  channel is required; the server equivalent is added with Task 30 once the
  owner has chosen the server's system (D-7).
- **Request guard:** like the Task 13 guard, but for one host: HTTPS to
  `api.telegram.org` only, POST, redirects refused, a timeout. Every error
  text is built by the sink (exception type and HTTP status), never from the
  exception's message, so no URL (which holds the token) can reach a log.
- **Redaction:** the router's credential patterns gain the Telegram token
  shape (`<digits>:<35 characters>`), as a second line of defence.

## 2. The weekly test (D-2)

- `scripts/alert_channel.py test` sends a test message carrying a fresh
  one-time code and records the send (time and the code's SHA-256, not the
  code) in a hash-chained `channel_tests.jsonl` in the account directory.
- The owner acknowledges by typing the code he received (see Q28-1).
  The acknowledgment is appended to the same ledger. A wrong code is refused.
- **Start check:** when the run requires the channel, the start is refused
  if the newest acknowledged test was sent more than 7 days ago by the wall
  clock, or the ledger is damaged.

## 3. Which runs need it

Simulated replays (drills, historical paper runs) keep local alerting only:
they run on past bars and must stay reproducible offline. The channel and
its test check apply when the config has a `[telegram]` section; forward
paper (Task 29) and shadow will require that section. Section 19, "alerting
before shadow", is met before shadow, as the deployment draft section 5
says.

## 4. Decisions needed from the owner

- **Q28-1. How you acknowledge the weekly test.** (a) the test message
  shows a short code; you type `python scripts/alert_channel.py ack <code>`
  on the app's machine (no extra network use; proves the message arrived);
  or (b) you reply to the bot in Telegram and the app reads the reply (the
  app must then also read messages from Telegram).
- **Q28-2. A run that passes 7 days without an acknowledged test.** The
  start check only runs at start, and a forward-paper run lasts months.
  (a) the app sends the weekly test itself and, while overdue, raises a
  CRITICAL alert every hour but keeps running; or (b) the app HALTs until
  the test is acknowledged (then your section 14 override restarts trading).

## 5. Acceptance (roadmap 2)

A failed send is itself logged and alerted locally; an overdue test refuses
start; the token never appears in any log, report or test. Tests use a fake
transport and a fake credential reader; nothing is sent anywhere by the
test suite or by this AI.

## 6. Size and review

About 300 lines with tests. The start check is protocol-enforcement logic
(section 16): Astra review and the owner's walkthrough before merge.
