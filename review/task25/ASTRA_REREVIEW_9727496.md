# Task 25 Astra re-review, attempt 3 — complete (ACCEPT)

Date: 2026-09-29. Requested by the owner ("make astra review for all we need").

- Invocation: `codex exec -s read-only -m gpt-6-astra -` (CLI header
  `model: gpt-6-astra`); the model reports only the GPT-6 family.
- The prompt was the attempt-2 prompt; a planned update naming head
  `9727496` and the A25R repairs failed to apply (the implementer's shell
  quoting error). The reviewer found the actual head itself and reviewed the
  A25R repairs, as stated below.
- The reviewer's final message follows verbatim.

---

**Verdict: ACCEPT**, with one non-blocking audit limitation.

Reviewer: OpenAI Codex, GPT-6 family. GPT-6 Astra was requested; exact serving-model metadata is not exposed in this interface.

Reviewed commit: **`9727496ff20c6691b9d6166045ab88a8d1fb35ff`**, current `task25-drills-evidence`, against `01f10ad`. The branch had advanced beyond the stated `1f7f07d`, including the additional repairs in `818010b`.

All execution was offline and read-only, using synthetic or exploration data. Generated artifacts and mutations stayed in memory. Worktree and index remained clean.

| Finding | Assessment | Evidence |
|---|---|---|
| **A25-1** | **CORRECT** | `scripts/run_drills.py:140` requires a control order after HALT. The clean run supplies one; the unmutated HALT run suppresses it. Bypassing `may_trade` produces one post-HALT order and fails the drill. |
| **A25-2** | **CORRECT** | `scripts/run_drills.py:176` checks bounded, ordered, chained steps and final balance; line 189 restores the remainder bound. Both the 100% sell and premature-stop mutations fail. The committed run has ten steps, maximum share 0.5000, remainder 0.00108 BTC. |
| **A25-3** | **CORRECT** | `scripts/run_drills.py:96`, `:270`, and `:367` refuse reused output. Existing runner and FREEZE directories raised `FileExistsError`; prior files stayed unchanged. A standalone `summary.json` caused exit 2 and remained untouched. Reading the ambiguous drill’s incident caused REFUSED without modifying that ledger. |
| **T25-03** | **CORRECT** | `.gitattributes:11` preserves evidence bytes. All 31 tracked drill files matched committed blobs through Git checkout filters with `core.autocrlf=true`. All 11 ledgers verified intact. Deliberate CRLF conversion failed canonical-byte verification. |

The mutations ran through `rtk proxy .venv/Scripts/python.exe -B -` with an inline memory-I/O harness. They replaced `may_trade` to permit HALT, forced `max_step_fraction=Decimal(1)`, or triggered `FLATTEN_DONE` after two steps:

```text
HALT_GATE_BYPASSED False
  clean-run orders after that time 1; orders after HALT 1; final HALT

FLATTEN_100_PERCENT False
  1 steps; largest share 1.0000; BTC left 0.00000

FLATTEN_PREMATURE_DONE False
  2 steps; largest share 0.5000; BTC left 0.27477
```

The previously recorded **A25R-1 and A25R-2 are also corrected**. At `paper_loop.py:594`, `held_before` comes from the simulator immediately before sizing. Its balance accessor returns a copy without changing state. A probe with local BTC 0.9, venue BTC 1, and tolerance 0.2 logged `held_before=1`, `orig_qty=0.50000`. Injected reconciliation failure produced FREEZE after exactly one FLATTEN event. Three zero fills still emitted the critical streak alert. Deterministic reruns passed.

A25R-3 from the interrupted review remains unspecified; I have not invented a replacement finding for it.

**A25R-4 — NON-BLOCKING: lost-reply FLATTEN sells remain absent from the ORDER audit and order count.**

Location: [paper_loop.py:604](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/app/paper_loop.py:604), [PAPER_TRADING_EVIDENCE.md:181](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/task25/PAPER_TRADING_EVIDENCE.md:181).

Concrete scenario: start with 1 BTC, command FLATTEN immediately, and configure `Fault(timeout=True)` for its first deterministic FLATTEN client-order ID. The simulator fills the sell before losing the reply. `tick` returns `None` after recording FREEZE, so the new logging/counting block is skipped.

**Reproduced: yes.** Command: `rtk proxy .venv/Scripts/python.exe -B -`, inline memory-I/O harness using the synthetic paper-loop fixture and the scenario above. Exit 0:

```text
FLATTEN_LOST_REPLY mode FREEZE orders_sent 0 BTC 0.50000 ORDER_events 0
```

The incident and transition retain the client-order ID, and further trading stops. This does not invalidate the committed drills, but “logs every FLATTEN sell” overstates coverage. Narrow that claim or propose explicit attempted/unknown-order logging. No repair was applied during this read-only review.

| Drill | Acceptance |
|---|---|
| Clean multi-month run | **Met** — 3,504 hours, 146 scheduled decisions, two orders, RUNNING |
| HALT | **Met** — zero orders after HALT against one control opportunity |
| FLATTEN | **Met** — ten bounded hourly steps, chained balances, small remainder, HALT |
| FREEZE-and-reconcile | **Met** — lost reply, blind reconciliation refused, full reconciliation reaches HALT; disclosed controller-level scope |
| Ambiguous order | **Met** — one order, one open incident, FREEZE |
| REFUSE_START | **Met** — both starts refused, zero orders, dummy credential value absent |

The replay reproduced **all 20 non-lock evidence files byte-for-byte**, including the summary. Packet numbers and shortened excerpts match the committed logs.

Validation on Windows, Python 3.14.7:

| Command/check | Result |
|---|---|
| `rtk proxy .venv/Scripts/ruff.exe check --no-cache .` | Exit 0 |
| `rtk proxy .venv/Scripts/ruff.exe format --check --no-cache .` | Exit 0; 101 files |
| `rtk proxy .venv/Scripts/python.exe -B -m mypy --no-incremental --cache-dir=nul src scripts` | Exit 0; 53 files |
| `rtk proxy .venv/Scripts/lint-imports.exe --no-cache --no-logo` | Exit 0; six contracts kept |
| `rtk proxy git diff --check 01f10ad task25-drills-evidence` | Exit 0 |
| Affected integration modules, direct memory-backed invocation | 29 cases passed |
| Frozen verification | 29 baseline blobs unchanged; 14 sidecars, self-hash, manifest and protocol bindings passed |

The combined test harness subsequently exited 1 because my auxiliary probe supplied invalid `fill_fraction=0`. The corrected probe used a positive fraction that rounds to zero and passed with exit 0. This was a harness error.

The full suite was not independently rerun; the committed author result is 1,576 passed, four skipped. Memory-backed checks exclude OS locking/fsync validation.

This final message is the review record. Its commit and the required human §16 review remain outstanding.
