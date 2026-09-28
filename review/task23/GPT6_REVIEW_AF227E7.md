# Task 23 GPT-6 review of `af227e7`

Date: 2026-09-28

Verdict: **REVISION REQUIRED**

## Reviewer metadata and identity limitation

- CLI request: exact `gpt-6-astra`, selected with `codex exec -m gpt-6-astra`.
- Runtime-reported identity: OpenAI Codex, GPT-6 family. The runtime did not
  expose an exact deployment identifier or reasoning setting, and the reviewer
  explicitly said it could not certify that the run was `gpt-6-astra`.
- Thread/session ID: `01a0e7e7-5bdb-7b71-a0cb-dab8e2a0d06e`.
- Codex CLI: `0.157.1`.
- Sandbox: read-only; session: ephemeral.
- Base: `edc3b39dd890f5c92c1c7542b7853ae62055b4d2`.
- Head: `af227e73fce69658eb49a0ae9bb11f27b60af344`.
- Runtime: Windows 11 `10.0.26200`; Python 3.14.7; pytest 8.4.2;
  Ruff 0.11.13; mypy 2.3.1; import-linter 2.15.
- Worktree was clean before and after the review. No file edit, commit,
  credential, exchange call, confirmation data, or lockbox data was used.

Because exact model metadata was not exposed, this review does not close the
owner's exact-Astra gate even though the CLI selection was exact.

## BLOCKER

### T23-QB — continuing FLATTEN through alarms remains unauthorized

**Where:** `src/aqt/execution/safety.py`, FLATTEN mappings for `INCIDENT` and
`LOSS_STOP`; `review/task23/ADJUDICATION.md` T23-QB.

**Evidence:** after entering FLATTEN, either alarm leaves FLATTEN active. The
reviewer reproduced a later 0.500 BTC sale from a 1 BTC holding. The committed
L-03 adoption calls for automatic HALT, and no committed owner decision
authorizes continued selling through either alarm.

**Impact:** an unresolved protected behavior is executable.

**Smallest correction:** obtain and record an owner decision. Without one,
map both transitions to HALT, preserve incident logging, and prove later ticks
place no orders.

### T23-I01 — override recovery incident does not invalidate old reconciliation

**Where:** `src/aqt/execution/safety.py`, `override_halt` freshness check and
the `HALT_OVERRIDE_FAILED` recovery path.

**Evidence:** HALT at 00:00; passed reconciliation at 01:00; override at 02:00
closes the old incident but its transition alert fails. The exception handler
opens `HALT_OVERRIDE_FAILED` at 02:00 while `entered_at` remains 00:00. At
03:00, an override naming that new incident can reuse the 01:00 report and
return RUNNING. The reviewer reproduced this on the actual controller with
in-memory sinks.

**Impact:** the reconciliation predates the latest safety incident, leaving
the earlier C2 freshness repair incomplete.

**Smallest correction:** advance the recovery cutoff and monotonic timestamp
when the override transition fails, including when the recovery incident write
also fails. Reject reports before or equal to that time; accept a later report.

### T23-I02 — FLATTEN ignores the supplied maximum-notional filter

**Where:** `src/aqt/execution/safety.py`, FLATTEN quantity calculation;
`src/aqt/execution/simulator.py`, `FILTER_MAX_NOTIONAL` enforcement.

**Evidence:** with 1 BTC, a 100 USDT mark, 50% step fraction, 10 USDT minimum,
and 20 USDT maximum notional, FLATTEN requests 0.5 BTC. The simulator rejects
it and the controller enters FREEZE with the full holding. A 0.2 BTC order at
the same price and filters succeeds.

**Impact:** a known supported filter prevents de-risking although a valid
bounded step exists. The rejection is caused by local sizing, not necessarily
venue-state divergence.

**Smallest correction:** include maximum notional in the quantity bound, round
down to the lot step, then check minimums. Keep FREEZE for an unexpected reject
and add the valid-smaller-step regression.

### T23-I03 — the review sandbox could not certify the complete mandatory gate

**Evidence:** the guarded full suite reached 33 passing tests, then a fixture
requiring temporary storage failed because the review sandbox prohibited
writes. The installed mypy 2.3.1 is outside the project's declared
`mypy>=1.15,<2`, although the no-cache type check passed. Fresh PR CI was not
verified. The locally recorded 1,528 passed / 4 skipped result was prior
evidence, not reproduced by this reviewer.

**Impact:** this is an evidence/environment blocker, not a product test
failure.

**Smallest correction:** rerun the complete gate on the repaired head in an
authorized writable environment with declared dependencies and retain fresh CI
evidence.

### T23-I04 — exact-model and recorded human-review gates remain open

**Evidence:** Q2 selects exact GPT-6 Astra. This run's runtime did not expose
an exact deployment identifier; the earlier Astra attempt issued no verdict.
At the reviewed head this response was uncommitted, and human approval remained
outstanding.

**Impact:** Section 16 review cannot be declared closed.

**Smallest correction:** preserve this complete record before repairs, obtain
verifiable exact-model evidence, and obtain the separate recorded human PR
review.

## NON-BLOCKING

### T23-N01 — deployment draft still promises zero exposure

The repaired bounded sequence can stop with a 0.155 BTC remainder when no next
step fits both the 50% maximum and minimum notional. Change the draft's “Zero
exposure, then HALT” to “zero exposure or no valid bounded step, then HALT,”
with the remainder recorded.

### T23-C4 / T23-A0-04 — restart durability remains a Task 24 dependency

The in-process `OWNER_HALT` recovery path works. A failed incident write is
still only a memory-state FREEZE; a clean restart can pass without a durable
incident. The deferral is acceptable for the unwired Task 23 controller, but
Task 24 must implement durable startup refusal and restart recovery before use.

### T23-C6 — zero-fill escalation remains a Task 24 dependency

Three consecutive zero-fill steps left FLATTEN active with only its entry
alert. This does not add risk, but de-risking can stall. Task 24 must implement
the already recorded bounded zero-fill alert.

### T23-R3 — live-adapter accounting remains deferred

Simulator reconciliation does not establish contracts for live free/locked
balances, commission assets, venue rounding, or malformed account responses.
These must be validated before a live adapter. Current exchange documentation
verification was N/A to this offline review.

## Prior finding dispositions verified by the reviewer

| Prior IDs | Review result |
| --- | --- |
| C1 / A0-05 | LOSS_STOP now HALTs from RUNNING/HALT and preserves FREEZE; the FLATTEN exception remains T23-QB. |
| C2 / A0-03 | Original HALT/FREEZE self-transition cases are fixed; T23-I01 is a distinct uncovered path. |
| C3 / A0-01 | Whole-remainder exception is removed and observed reductions respect 50%; T23-N01 remains. |
| A0-02 | The 300 BTC case respects 100 BTC `max_qty`; unexpected filter rejection enters FREEZE; `max_notional` omission is T23-I02. |
| C4 / A0-04 | In-process recovery works; restart durability remains disclosed and deferred. |
| C5 | Double-write-failure recovery through fresh OWNER_HALT works; the successful recovery-incident path exposes T23-I01. |
| C6 | Zero-fill behavior was reproduced; loop escalation remains deferred. |
| QA | Equal timestamps are refused for both recovery procedures. |
| R1 | Audit failure cannot leave a protective transition RUNNING. |
| R2 | Recovery incident makes a failed override retryable; freshness remains T23-I01. |
| R3 | Simulator-only limitation remains explicit. |

## Checks actually run

- `git diff --check edc3b39 af227e7`: passed.
- Ruff check and format check with caches disabled: passed; 94 files formatted.
- mypy without incremental/SQLite caches: passed for 48 source files.
- import-linter: 5 contracts kept, 0 broken.
- Guarded selected Task 23 tests: 10 passed, 38 deselected.
- Guarded full suite: 33 passed, then stopped when a fixture required forbidden
  temporary-file writes.
- Independent frozen verification: trusted 28-file inventory and exact bytes
  matched the baseline, base, and head; 14 sidecars; Constitution canonical
  hash; seven manifest bindings; seven protocol bindings; nested bindings.
- Synthetic in-memory probes passed all six nominal acceptance scenarios and
  reproduced T23-QB, T23-I01, and T23-I02.

No additional question was reported. The exact-Astra identity gap, the three
code/authority blockers, the complete-gate evidence issue, fresh CI, and human
review all remained open at this snapshot.
