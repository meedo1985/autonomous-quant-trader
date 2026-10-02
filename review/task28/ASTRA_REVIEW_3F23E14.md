# Task 28 Astra review of `3f23e14` (FIX; A28-1..A28-6 blockers)

Date: 2026-10-02. Requested by the owner ("yes start Task 28", after being
asked whether to run Astra on PR #38).

- Invocation: `codex exec -s read-only -m gpt-6-astra -o <last> - < ASTRA_PROMPT_3F23E14.md`
  (codex-cli 0.157.1; log header: model `gpt-6-astra`, sandbox read-only,
  reasoning effort high, session `01a0fc60-0793-7821-9c2e-efdc974c6096`).
- Prompt: `ASTRA_PROMPT_3F23E14.md` in this folder, SHA-256
  `b29a0dd3098d1bd8d09038e879486864d7a4ab34046a1936aa193673e4702a2f`.
- Run on a PC inside the repository with read-only commands; no network, no
  credential store. The reviewer's final message follows verbatim.

---

**Verdict: FIX.**

Reviewer: **GPT-6 Astra**, independent first review of Claude Opus 5.5’s implementation. Reviewed `3f23e14fcf4477124e3dba7225e4d59d47726ecb`, against `995126da09f7c8c90f1a03a2696376123b53762f`, branch `task28-telegram-alerts`, identified as draft PR #38. PR metadata was not checked online.

No network requests, credential-store access, restricted-data access, or repository changes were made. All credentials below were synthetic. The working tree remained clean.

**Findings**

1. **A28-1 — BLOCKER — Truncating an error description before redaction leaks token material.**  
   `src/aqt/monitoring/telegram.py:200–201`, `scripts/alert_channel.py:51`.

   A failed response with `description = "x"*180 + token` cuts the token at character 200 before attempting exact replacement. Its first 20 characters survive. `TelegramSink.write()` sends this directly to local sinks; `send_test()` puts it into the exception printed by the CLI. This violates §28.

   **Reproduced: yes.** `python -B -`, in-memory R2 harness using a fake HTTP 400 response and the actual CLI `main()` with `owner_channel` replaced:
   ```text
   R2 partial_token_in_local= True full_token= False
   R2 cli_exit= 2 partial_token_in_stderr= True
   ```
   Minimum correction: keep remote descriptions out of diagnostics, as the design originally promises. Locally constructed status/error codes suffice.

2. **A28-2 — BLOCKER — The Telegram redaction pattern misses the actual token-bearing URL.**  
   `src/aqt/monitoring/alerts.py:57`.

   The leading `\b` cannot match between `bot` and the token’s first digit: both are word characters. An event field containing `https://api.telegram.org/bot<token>/sendMessage` passes through the router unchanged.

   **Reproduced: yes.** `python -B -`, R1/R15 harnesses emitting that URL through `AlertRouter`, `StreamSink`, and the real `LedgerSink` with only its disk append replaced:
   ```text
   R1 url_token_in_stdout= True
   R15 url_token_in_operations_payload= True
   ```
   Minimum correction: recognize the token in its URL context; cover both field names and values with regression checks.

3. **A28-3 — BLOCKER — A failed manual channel test has no durable failure event.**  
   `src/aqt/monitoring/telegram.py:253–259`, `scripts/alert_channel.py:40–51`.

   `send_test()` calls `send()` directly, bypassing the failure-event handling in `write()`. The CLI then prints a refusal to stderr. It configures no operations-log sink and records nothing in the test ledger for that failed attempt. Thus the owner’s normal `alert_channel.py test` failure is not both logged and alerted locally.

   **Reproduced: yes.** `python -B -`, R4 fake-HTTP-500 harness:
   ```text
   R4 failed_test_local_events= 0
   ```
   Minimum correction: route failed test sends through shared, sanitized local failure reporting and provide a durable CLI audit sink.

4. **A28-4 — BLOCKER — Response parsing can escape the “never raises” sink and terminate the loop.**  
   `src/aqt/monitoring/telegram.py:191–195`, `src/aqt/app/paper_loop.py:944`, `1196–1201`.

   A deeply nested JSON response raises `RecursionError`; the parsing handler catches only `ValueError`. No local failure event is emitted. This also escapes `check_channel()`’s exception tuple. The surrounding loop writes its refusal marker and re-raises, contradicting the promised failure containment and Q28-2 behavior.

   **Reproduced: yes.** `python -B -`, R10 fake-response harness with `b"["*100000 + b"]"*100000`:
   ```text
   R10 escaped= RecursionError fallback_events= 0
   ```
   Minimum correction: contain response-processing failures within the send boundary, with locally constructed diagnostics. Bound response size as well.

5. **A28-5 — BLOCKER — An acknowledgment remains valid after changing the bot or recipient.**  
   `src/aqt/monitoring/telegram.py:260–280`, `286–312`.

   The ledger records only the code digest and send time. If the owner replaces the credential-store entry with another bot/chat, the unchanged global ledger authorizes the new channel without testing its delivery. A typo in the replacement chat can therefore pass the start gate.

   **Reproduced: yes.** `python -B -`, R6 harness sharing acknowledged records between two different synthetic bot/chat credentials:
   ```text
   R6 replaced_channel_problem= None due= False
   ```
   Minimum correction: bind acknowledgments to a non-secret channel identity/version and invalidate them when the configured channel changes. Do not store raw credentials.

6. **A28-6 — BLOCKER — Clock rollback extends freshness and suppresses reminders.**  
   `src/aqt/monitoring/telegram.py:294–302`, `src/aqt/app/paper_loop.py:936–939`.

   After a clock correction backwards, future-dated sends are treated as fresh. Separately, a previously recorded `reminded` timestamp suppresses every check until wall time catches up. A 30-day correction can therefore postpone testing/reminders for approximately 30 days.

   **Reproduced: yes.** `python -B -`, R5 ledger harness and R11 harness compiling the exact nested `check_channel()` AST:
   ```text
   R5 rollback_30_days_problem= None due= False
   R11 reminders_after_rollback_and_hour= 1 channel_checks= 1
   ```
   Minimum correction: reject future-dated freshness evidence and handle backward clock movement explicitly when scheduling checks.

7. **A28-7 — NON-BLOCKING — Random code reuse breaks the advertised one-time acknowledgment.**  
   `src/aqt/monitoring/telegram.py:252`, `271–276`.

   Codes are sampled from one million possibilities without checking prior use. When a new test repeats an acknowledged code, its acknowledgment is rejected forever as “already acknowledged.” Reuse of an old unacknowledged code can instead let an old message acknowledge the newer send.

   **Reproduced: yes**, for the first case. `python -B -`, R7 harness forcing the same random code on two sends eight days apart:
   ```text
   R7 repeated_random_code= that test is already acknowledged
   ```
   Minimum correction: avoid previously issued codes or distinguish test instances unambiguously.

8. **A28-8 — NON-BLOCKING — Hash integrity does not validate channel-record semantics; malformed timestamps escape refusal handling.**  
   `src/aqt/monitoring/telegram.py:242–247`, `288–302`, `src/aqt/app/paper_loop.py:582`, `944`.

   A correctly hash-chained acknowledgment containing a naive `sent_at` passes generic ledger verification, then raises `TypeError` outside `problem()`’s handler. A malformed SENT timestamp raises `ValueError` from `due()`, outside the loop’s handled exception types. This requires semantically invalid records; ordinary byte corruption is correctly detected.

   **Reproduced: yes.** `python -B -`, R12/R21 harnesses, including a canonical, correctly hashed ledger envelope:
   ```text
   R21 naive_payload_hash_chain_intact= True
   R21 naive_payload_escaped= TypeError
   R12 malformed_timestamp_loop_escaped= ValueError
   R21 changed_bytes_detected= True
   ```
   Minimum correction: validate channel-record fields, UTC timestamps, and acknowledgment references within the contained ledger-reading boundary.

9. **A28-9 — NON-BLOCKING — Malformed credential blobs escape the controlled refusal path.**  
   `src/aqt/monitoring/telegram.py:151`, `scripts/alert_channel.py:50`, `scripts/run_paper_trading.py:60`.

   An invalid stored blob raises `UnicodeDecodeError`; both CLI handlers expect `ChannelError` instead. The result is an uncaught traceback rather than a controlled refusal. Memory is nevertheless freed correctly.

   **Reproduced: yes.** `python -B -`, R16 harness replacing `ctypes.WinDLL` with a fake returning a one-byte UTF-16 blob:
   ```text
   R16 malformed_blob_escaped= UnicodeDecodeError freed= 1
   ```
   Minimum correction: convert decoding failures into a fixed, secret-free `ChannelError`, suppressing the original exception context.

**Assessment of T28-01 through T28-06**

| Local finding | Assessment |
|---|---|
| T28-01 | Non-blocking success-path coverage gap, but testing it does **not** require writing real credentials. The fake native API reproduced the Windows x64 layout: size 80, blob offset 40, username offset 72; UTF-16LE decoding and `CredFree` passed. See A28-9 for failure handling. |
| T28-02 | Agree with the intended overdue window. Precisely, the implementation remains current at exactly seven days and becomes due **after** seven days. That matches “older than seven days.” |
| T28-03 | Agree that hashing six digits does not provide meaningful secrecy against ledger readers. That does not resolve the distinct reuse problem in A28-7. |
| T28-04 | Partially agree. Sends are synchronous. However, the 10-second urllib timeout is not a guaranteed total-call deadline: DNS and a response trickling data can exceed it. The report should not promise an absolute ten-second maximum. |
| T28-05 | Agree: direct fallback events bypass the loop counter but normally reach local logs. Counting is informational. |
| T28-06 | Agree with deferral to Task 30. Windows-only support is explicit and does not authorize a server deployment. |

**Other reviewed behavior**

- The request guard rejects non-HTTPS and different hosts. The fake-opener test observed `POST`, `api.telegram.org`, and timeout `10.0`; redirects are refused. No host was contacted.
- Ordinary urllib exceptions do not leak their messages. A fake `HTTPError` containing the synthetic URL/token was safely reported when its complete token appeared within the untruncated description.
- Credential and request representations hide the token/URL in their designated secret fields. The native success-path test used no Windows credential-store calls.
- Wrong and repeated acknowledgments are rejected. Acknowledging an eight-day-old code does not refresh its send time or permit startup.
- Missing and overdue acknowledgments produced logged `REFUSE_START`, with zero orders.
- An ordinary in-run test-send failure produced a reminder and left the mode `RUNNING`.
- Failed deliveries of REDACTION and ALERT_CHANNEL events did not recurse with the production-style local-sink configuration: two transport attempts completed with local failure events and no synthetic-token leakage.
- With `channel=None`, a two-day synthetic base/head comparison produced identical reports and event bytes. **The full Task 25 golden drills were not independently rerun.**
- D-1’s bot route and D-8’s credential-store mechanism are present. D-2 is incomplete because of A28-5/A28-6; §28 fails because of A28-1/A28-2. This task does not establish server-offline monitoring or authorize shadow under §19.

**Commands and validation**

Read-only inspection used `Get-Content`, `Select-String`, directory listings, and numbered Python reads of the requested documents, changed code, ledger/router dependencies, and validation configuration.

Git commands included:

```text
git status --short --untracked-files=all
git rev-parse HEAD main
git branch --show-current
git diff --stat main 3f23e14
git diff main 3f23e14 -- <reviewed implementation paths>
git diff
git diff --cached
git diff --check main 3f23e14
git diff --name-only main 3f23e14 -- docs protocols schemas specs FROZEN_HASHES.json '*.sha256'
git show 995126d:src/aqt/app/paper_loop.py
git diff --exit-code
git diff --cached --exit-code
```

All completed; Git warned that the user-level ignore file was inaccessible. No tracked/staged/untracked changes were reported.

Validation commands:

```text
.venv/Scripts/python.exe -B -m ruff check --no-cache .
.venv/Scripts/python.exe -B -m ruff format --check --no-cache .
.venv/Scripts/python.exe -B -m mypy --no-incremental --cache-dir nul src scripts
.venv/Scripts/python.exe -B -c "from importlinter.cli import lint_imports_command; lint_imports_command(['--no-cache'])"
.venv/Scripts/python.exe -B -m pytest -q --capture=sys -p no:cacheprovider tests/unit/test_telegram.py -k 'critical_event_is_sent or only_critical_events or sink_without_a_local or only_the_telegram_host or credential_never_prints or token_in_an_event'
```

Results: lint passed; **111 files formatted**; types passed for **58 source files**; **6 import contracts kept**; **6 tests passed, 12 deselected**.

Initial system-Python attempts lacked pytest/ruff/mypy. The venv pytest attempt with default capture failed with `FileNotFoundError: No usable temporary directory`; in-memory capture resolved this for the six filesystem-free tests. Full-suite validation remains unverified independently.

The reported reproductions ran through PowerShell here-strings piped to `python -B -`; the actual-loop comparisons used `.venv/Scripts/python.exe -B -` with a filesystem-write audit guard. An initial loop harness omitted required `operations_log`; the corrected harness passed.

A read-only Python port of the frozen verifier passed: **28 trusted files, exact inventory, 14 sidecars, Constitution self-hash, seven manifest/protocol bindings, and nested bindings**. No protected paths differ from the base.

This response is the review record requested; it is **not committed**. The fixes, retained findings, and subsequent review must be preserved by the authorized maintainer. Human review under §16 remains outstanding.