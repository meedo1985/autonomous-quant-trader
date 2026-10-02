# Task 28 Astra re-review of `816cd26` (attempt 2) — ACCEPT

Date: 2026-10-02, run started 17:42 local (+03:00). Requested by the owner
("yes run Astra again"); attempt 1 was cut off by the usage limit, see
`ASTRA_REREVIEW_816CD26_ATTEMPT_1.md`.

- Invocation: `codex exec -s read-only -m gpt-6-astra -o <last> - < review/task28/ASTRA_PROMPT_816CD26.md`
- Log header: OpenAI Codex v0.157.1; model `gpt-6-astra`; provider openai;
  approval never; sandbox read-only; reasoning effort high; session id
  `01a0fd10-d65d-76b0-811c-ee760268c700`; tokens used 103,832; exit 0.
- Checkout HEAD at run time: `6fa4933`. Prompt SHA-256:
  `739edf8571b406745f7c2df97cfeb89019d015cf18c0621b02ae406ded6ffefa`.
- Findings: A28-1..A28-7, A28-9 CORRECT; A28-8 INCOMPLETE (non-blocking, see
  A28-10); new A28-10..A28-13 all NON-BLOCKING. The author's dispositions
  follow in `LOCAL_REPORT.md`.

Below is the reviewer's final message, verbatim.

---

**Verdict: ACCEPT — independent code re-review, with four NON-BLOCKING findings below.** The six original blockers are repaired. This is not a declaration that the full task gate or human review is complete.

Reviewer: **GPT-6 Astra**. Implementation author: Claude Opus 5.5, as identified in the supplied record.

Reviewed commit: **`816cd26e09d9ba682ee393e92cf3c42320853dc8`**, against `3f23e14`, branch `task28-telegram-alerts`, identified by the user as draft PR #38. Checkout HEAD was `6fa49332d20aad88bd27429ccff7ed350732dd0a`; its two additional files are review documents. Reviewed implementation bytes match `816cd26`. PR metadata was not checked online.

No network, credential-store, exchange, confirmation, or lockbox access occurred. No repository files were changed. Credentials and responses used in reproductions were synthetic.

**Disposition of A28-1 through A28-9**

| ID | Assessment | Evidence |
|---|---|---|
| A28-1 | **CORRECT** | R2: the long token-bearing response description produced no token prefix in local output. Actual CLI returned 2 without leaking it. Remote descriptions are discarded. |
| A28-2 | **CORRECT** | R1/R15: token-bearing URLs in both field names and values were redacted from stream output and operations-ledger payloads. |
| A28-3 | **CORRECT** | R4: actual CLI wiring, with memory-backed ledger writes, produced one durable `ALERT_CHANNEL` event with `failed_kind=CHANNEL_TEST`, plus stderr notification. |
| A28-4 | **CORRECT** | R10: deeply nested JSON produced one local failure event without escaping. R12: malformed-record exceptions were contained by the actual compiled `check_channel`. The broader unconditional containment claim has an edge case in A28-11. |
| A28-5 | **CORRECT** | R6: changing either chat or token changed the fingerprint, required a new test, and refused acknowledgment using the previous channel’s code. |
| A28-6 | **CORRECT** | R5: 30-day rollback reported “clock is behind,” returned `due=False`, and refused sending. R11: forward and backward scheduling produced four checks/four reminders at the expected boundaries. |
| A28-7 | **CORRECT** | R7: forced draws `[5,5,7]` issued `000005`, then `000007`; both could be acknowledged. This establishes sequential issuance behavior, not concurrent issuance guarantees. |
| A28-8 | **INCOMPLETE — NON-BLOCKING** | The original timestamp escapes are fixed. R12/R21 rejected naive, malformed and non-UTC timestamps, malformed digests, unknown keys, and acknowledgment without a preceding send. Semantic validation still accepts duplicate issuance; see A28-10. |
| A28-9 | **CORRECT** | R16: invalid blobs produced fixed-text `ChannelError`, no retained exception context, and exactly one `CredFree`. UTF-8 and UTF-16LE success paths passed against a fake native API. |

**New findings**

All reproductions below ran as PowerShell here-strings piped to:

```text
rtk proxy .venv/Scripts/python.exe -B -
```

Ledger reproductions used memory-backed canonical ledger bytes and the real ledger parser/hash verification. No ledger files were written.

**A28-10 — NON-BLOCKING — Duplicate issuance passes record validation.**  
`src/aqt/monitoring/telegram.py:304`, `:365`

Concrete scenario: a correctly hash-chained ledger contains a SENT record, followed eight days later by another SENT with the same code digest and channel but a newer `sent_at`. `_records()` accepts both. Typing the original code acknowledges the newer record because `acknowledge()` selects `sent[-1]`, and `problem()` returns `None`.

**Reproduced: yes**, harness A: generate a normal send, append the duplicate through the memory-backed canonical ledger writer, advance eight days, acknowledge the original code.

```text
duplicate_issue_old_code_accepts_new_send= True
```

This requires semantically invalid input; normal sequential `send_test()` now prevents it. Reject repeated SENT code digests during record validation. I am not treating a locally fabricated hash chain as a demonstrated remote attack.

**A28-11 — NON-BLOCKING — Clock errors remain outside containment.**  
`src/aqt/monitoring/telegram.py:391`; `src/aqt/app/paper_loop.py:938`

Concrete scenario: an injected clock returns a naive datetime. Both `problem()` and the loop’s initial `channel.now()` call raise `BarSemanticsError`; the loop emits no channel reminder. Thus “Never raises” and “nothing it meets stops the loop” remain broader than the implementation.

**Reproduced: yes**, harness A, using an acknowledged channel and the unchanged nested `check_channel` compiled from its AST:

```text
clock_invalid problem= BarSemanticsError: clock must be UTC-aware, got naive value
check= BarSemanticsError: clock must be UTC-aware, got naive value reminders= 0
```

The production factory supplies `datetime.now(UTC)`, so this reproduction does not establish an ordinary production-clock failure. Include clock acquisition in containment or narrow the documented contract.

**A28-12 — NON-BLOCKING — The response bound can accept a malformed response prefix.**  
`src/aqt/monitoring/telegram.py:119`, `:214`

Concrete scenario: HTTP 200 body is `{"ok":true}`, padded with spaces through byte 65,536, followed by `INVALID`. The complete response is invalid JSON, but truncation leaves valid JSON and `send()` reports success.

**Reproduced: yes**, harness A:

```text
response 200 size= 65543 result= None
```

The allocation/read bound works; oversized-response detection does not. Reading one additional byte and rejecting oversized replies would distinguish complete responses from prefixes. Ordinary oversized JSON truncated inside its object is already refused.

**A28-13 — NON-BLOCKING — A supported ledger filename can collide with the new CLI log.**  
`scripts/alert_channel.py:43`

Concrete scenario:

```text
alert_channel.py --ledger alert_channel_log.jsonl test
```

The first send fails. Its failure event is appended to the same file used for channel tests. After transport recovery, retrying refuses the now semantically mixed ledger before attempting another send.

**Reproduced: yes**, dedicated CLI collision harness calling actual `main()` twice, first with fake HTTP 500 and then fake success:

```text
CLI collision first_exit= 2 retry_exit= 2 requests= 1
retry_refusal= Refused: channel test ledger has an unknown record
CLI collision hash_chain_intact= True
```

Reject colliding paths or derive a distinct log filename from the selected ledger.

**Fingerprint, records, clocks and transport**

The fingerprint is deterministic for identical credential strings. With a valid high-entropy bot token, the SHA-256 digest does not expose the token or chat directly. It does expose equality between channel identities and permits checking a guessed complete credential pair; it is a fingerprint, not encryption. No credential recovery was demonstrated.

Separate token-rotation and chat-change reproductions required fresh tests. An acknowledgment for the previous fingerprint did not satisfy the replacement channel. Delimiter ambiguity requires credential strings outside the expected token/chat formats; no valid-channel collision was demonstrated.

A valid send at `12:00:00.900000Z`, acknowledged at `12:00:00.950000Z`, remained valid:

```text
same_second_valid= None envelope= 2026-10-02T12:00:00Z
```

The envelope’s whole-second precision does not truncate payload `sent_at`. UTC normalization preserves microseconds. Nonzero-offset timestamps are explicitly refused by `require_utc`; the production factory writes UTC. I found no timezone or same-second false refusal for normally generated records.

Hourly gating skips checks before the forward one-hour boundary and immediately checks when time moves behind the previous check. A continually falling clock can consequently trigger every decision-hour check, consistent with the repair’s documented behavior.

Transport reproductions observed POST, the permitted host, timeout `10.0`, refused redirects, and `read(65536)` on both success and HTTP-error paths. Non-200 responses, `ok:false`, unreadable status and deep JSON failed safely. The timeout remains a per-operation timeout, not a total deadline.

**R1–R21 reproduction coverage**

| Reproductions | Result |
|---|---|
| R1/R15 | No token in stream or operations payload. |
| R2/R4 | No token prefix; CLI exit 2; one logged test-send failure. |
| R3 | Missing/wrong/repeated acknowledgment refused; exactly seven days remains current; one microsecond later is overdue. |
| R5/R6 | Rollback refused; both channel changes require fresh acknowledgment. |
| R7/R8 | Repeated random draw avoided; acknowledging an eight-day-old send remains overdue. |
| R9/R10 | HTTPError text suppressed; representations hide token; deep JSON contained. |
| R11 | Four expected forward/backward checks and reminders. |
| R12/R21 | Invalid records refused without loop escape; unsent acknowledgment refused; changed bytes detected. |
| R13/R14 | Request guard and bounded reads passed; fallback did not recurse: two attempts, four local events, no token leak. |
| R16 | Fake Windows layout `(size=80, blob offset=40, username offset=72)`; decoding/freeing passed. |
| R17/R18 | Actual loop refused missing/overdue acknowledgment, with zero orders. |
| R19 | Actual loop continued `RUNNING` after due-test failure; no startup refusal; reminder emitted. |
| R20 | Two-day synthetic run with `channel=None`: reports and event bytes identical between `3f23e14` and repaired code. |

These were reconstructed reproductions from the recorded scenarios; the prior standalone harness source was not present in that review record.

**T28-01 through T28-06**

- **T28-01:** Coverage gap addressed by fake-native tests; no real credential-store access needed.
- **T28-02:** Owner-approved overdue behavior holds. The report still incorrectly says “due exactly 7 days”; implementation becomes due **after** seven days.
- **T28-03:** Disposition holds: hashing six digits provides little secrecy against ledger readers. Sequential code reuse is repaired.
- **T28-04:** Corrected per-socket-operation timeout wording holds.
- **T28-05:** Disposition holds: direct local failure events bypass the report counter but reach configured local sinks.
- **T28-06:** Windows-only deployment limitation and Task 30 deferral remain explicit.

**Commands and validation**

Read-only inspection used `git`, numbered Python file reads, and PowerShell `Get-Content`/`Select-String` for the requested records, implementation, tests, ledger dependencies, Constitution §16, and validation configuration. `rg` was unavailable; a direct `rtk proxy Get-Content` invocation also failed because it is a PowerShell builtin.

Principal Git commands:

```text
git status --untracked-files=all
git rev-parse HEAD
git rev-parse 816cd26
git diff --stat 3f23e14 816cd26
git diff 3f23e14 816cd26 -- <five requested implementation/test paths>
git diff 816cd26 HEAD
git show 3f23e14:src/aqt/app/paper_loop.py
git diff --check 3f23e14 816cd26
git diff --check 3f23e14 816cd26 -- <five requested paths>
git diff --name-only 995126d 816cd26 -- docs protocols schemas specs FROZEN_HASHES.json '*.sha256'
git diff --exit-code
git diff --cached --exit-code
```

Commands used `rtk`/`rtk proxy`. The implementation-only whitespace check passed. The whole repair diff’s check exited 1 for nine Markdown trailing-space line breaks in the verbatim prior review record; no implementation whitespace errors were reported.

Independent validation, Python **3.14.7**:

```text
.venv/Scripts/python.exe -B -m ruff check --no-cache .
.venv/Scripts/python.exe -B -m ruff format --check --no-cache .
.venv/Scripts/python.exe -B -m mypy --no-incremental --cache-dir nul src scripts
.venv/Scripts/python.exe -B -c "from importlinter.cli import lint_imports_command; lint_imports_command(['--no-cache'])"
```

All exited 0: lint passed, **111 files formatted**, **58 source files type-checked**, **6 import contracts kept**.

```text
.venv/Scripts/python.exe -B -m pytest -q --capture=sys -p no:cacheprovider tests/unit/test_telegram.py -k 'critical_event_is_sent or only_critical_events or sink_without_a_local or only_the_telegram_host or credential_never_prints or token_in_an_event or token_inside_its_url or credential_reader_with_a_fake_store'
```

**11 passed, 21 deselected**, exit 0.

```text
.venv/Scripts/python.exe -B -m pytest -q --capture=sys -p no:cacheprovider --maxfail=1 tests/unit/test_telegram.py
```

**Blocked by the sandbox:** two passed, then fixture setup failed with `FileNotFoundError: No usable temporary directory`, exit 1. Full-suite and full Task 25 golden-drill validation were not independently rerun. The author’s reported results remain author evidence.

In-memory reproduction harnesses exited 0. Frozen verification passed **28 trusted files and exact inventory, 14 sidecars, Constitution self-hash, manifest/protocol bindings**. An initial verification-harness assertion used newline-normalized text; rerunning with raw Constitution bytes passed without changing files.

The working tree remained clean; Git warned that its user-level ignore file was inaccessible.

**ACCEPT applies to this independent code review.** All original BLOCKER findings are closed; A28-10–A28-13 remain deliberately unrepaired under the read-only scope. The complete local gate is not independently certified because filesystem-dependent validation was unavailable. Human review and committing this review record remain outstanding; I did not commit or merge anything.