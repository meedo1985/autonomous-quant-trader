# Task 22 fourth independent review

Date: 2026-09-28.

Reviewer: OpenAI Codex, GPT-6 family (system-exposed model metadata). The
runtime did not expose a more specific service SKU, so this record does not
claim an independently observed `gpt-6-astra` label. The implementation and
T22-07 repair were written by Claude Opus 5.5 (`claude-opus-5-5`), so this is
a different-model review for Constitution section 16. The owner still supplies
the required human review before merge.

Reviewed commit: `5d08c6f01f690e589e0eabbc252d73e12eb364fd`.
Base commit: `1cbb50d41177d119fa95b891d7f48c9ef15304d6` (`origin/main`).
The worktree was clean. The complete base-to-head diff was reviewed, with
specific attention to T22-07 in commit `2041d35939d29bf6c4eeb77ea2684f8871ec522b`.
No files were edited during the code review.

## Scope and method

The review traced authorization redemption, price-cap construction, buy and
sell sizing, submission, timeout/query/retry handling, terminal states,
reservation release, simulator balance accounting, and the Task 23 hand-off.
It checked the frozen Constitution sections 2, 16, and 19-22, the frozen
protocol, threat model, cost model, backtester specification, the roadmap Task
22 acceptance criteria, the three earlier reviews and adjudications, and the
owner's recorded T22-Q1 and T22-Q3 answers.

The Binance-facing check used official documentation as observed on
2026-09-28:

- General Spot REST information confirms that timeout and 5xx outcomes can be
  unknown and directs clients to query status:
  <https://developers.binance.com/en/docs/products/spot/rest-api>.
- The Spot glossary confirms that IOC may partially fill and expires the
  remainder, a LIMIT fill is no worse than its price, balances distinguish
  `free` from `locked`, and an order may be queried by client order ID:
  <https://developers.binance.com/en/docs/products/spot/faqs/spot_glossary>.

Task 22 remains simulator-only. No credentials, account endpoint, live order,
testnet order, confirmation data, or lockbox data was accessed.

## Findings

**R4-1 — NON-BLOCKING — Affordability uses the state's total quote balance,
not a venue free-balance field.**

`ActualState.quote_balance` includes locked amounts. If an eventual live
adapter reports a positive locked quote balance, T22-07 can request more than
the free balance can pay. That fails closed as a venue rejection and cannot
overspend or exceed the authorization. The Task 18 simulator has no locked
balance and the repository has no live adapter. The smallest safe correction
belongs at the future adapter/account-state boundary: supply reconciled free
funds for order sizing and retain total funds for exposure accounting. Do not
change Task 22's simulator contract speculatively.

**R4-2 — NON-BLOCKING — The 27 bps affordability reserve uses the frozen
fallback fee, not an arbitrary higher account fee.**

A point-in-time taker fee above 10 bps can make the conservative quantity
insufficiently conservative. The simulator then rejects the order without a
fill or negative balance, and `LOCAL_REPORT.md` already discloses this limit.
An eventual live adapter must size from the verified account fee or reserve a
documented upper bound. No Task 22 repair is required for the accepted
fallback-fee simulator scope.

No BLOCKER was found. In particular, T22-07 computes the affordable step count
with exact rational arithmetic, rounds quantity downward, takes the minimum of
that quantity and the governor/venue bound, and converts a sub-minimum result to
the existing no-order refusal. It cannot increase exposure beyond section 20's
authorization. At the simulator boundary the whole requested buy is checked at
the limit price with costs before any fill, so the new path cannot make the
quote balance negative.

## Acceptance and validation

All six roadmap acceptance criteria remain covered. The T22-07 regressions
exercise a full-exposure buy through governor, executor, and simulator and a
500-case exact-arithmetic property check.

Commands run against the reviewed code snapshot:

| Command | Result |
| --- | --- |
| `.venv\Scripts\python.exe -m pytest -q` | PASS: 1480 passed, 4 skipped in 80.29s |
| `.venv\Scripts\python.exe -m ruff check .` | PASS |
| `.venv\Scripts\python.exe -m ruff format --check .` | PASS: 90 files already formatted |
| `.venv\Scripts\python.exe -m mypy src scripts` | PASS: 46 source files |
| `.venv\Scripts\lint-imports.exe` | PASS: 5 kept, 0 broken |
| `git diff --check origin/main...HEAD` | PASS after commit `5d08c6f` removed six trailing spaces from the first review record |
| `review/task6/verify_frozen.ps1` under PowerShell 7 | PASS: 28/28 trusted bytes, 14/14 sidecars, all self-hashes and bindings |

The first attempted test command used the stale `.venv\Scripts\pytest.exe`
launcher and failed collection because that launcher selected an obsolete
Python 3.12 path against Python 3.14 packages. The documented
`python -m pytest` invocation used the environment's actual Python 3.14.7
interpreter and passed. The failed command was an environment-launcher failure,
not a discarded test result.

## Verdict

**CODE VERDICT: ACCEPT.**

**MERGE GATE: PENDING HUMAN REVIEW.** The owner must review T22-07's behavior:
a buy may be reduced to the largest affordable step at the authorized price
cap; if no valid minimum quantity is affordable, nothing is sent and the
authorization is released. The owner must also accept the recorded GPT-6
family metadata as satisfying the chosen different-model reviewer, or request
a rerun in an interface that exposes the exact `gpt-6-astra` label.
