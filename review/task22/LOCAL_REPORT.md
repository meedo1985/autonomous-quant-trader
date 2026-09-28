# Task 22 local report: executor state machine and ambiguous orders

Date: 2026-09-27. Coding AI: Claude Opus 5.5 (`claude-opus-5-5`).
Branch: `task22-executor`, from `main` at `1cbb50d`.

Section 16 lists the executor state machine, so merging needs a
different-model review (GPT-6 Astra, per owner answer Q2) and the owner's
behavioural review. Neither has happened yet.

## What changed

| File | Change |
| --- | --- |
| `src/aqt/execution/orders.py` (new) | `ExecutorConfig` (the two open section 21 values, no defaults), `client_order_id_for` (one id per authorization, from its nonce), `order_quantity` (rounded down to the step, capped at `max_qty`, 0 below `min_qty`) |
| `src/aqt/execution/machine.py` (new) | `State`, `Event`, the explicit `TRANSITIONS` table, `Executor.execute` |
| `src/aqt/execution/simulator.py` | Two additive `Fault` fields, both off by default: `lost_placements` (the request never arrives, the order does not exist) and `unknown_queries` (a query times out). The Task 18 simulator could not script confirmed absence or an unknown query without them. |
| `tests/unit/test_executor.py` (new) | 27 tests against a scripted venue and the real governor |
| `tests/integration/test_executor_simulator.py` (new) | 8 tests: governor, executor, and the simulator |
| `tests/unit/test_simulator.py` | 4 tests for the new faults |

## How section 21 is read

Frozen text: "Timeout → query clientOrderId. NOT_FOUND → wait protocol delay
→ query again. Confirmed absence may resend only with same clientOrderId and
unexpired authorization; otherwise get new authorization. UNKNOWN →
reconcile/FREEZE."

- **One order per authorization.** The `clientOrderId` is a digest of the
  authorization's nonce, so a resend is the same order to the venue. The
  quantity, side and decision time are fixed for the run.
- **Timeout** (or any placement error that is not a definite rejection) →
  `QUERYING`. `NOT_FOUND` and `DUPLICATE_CLIENT_ORDER_ID` from a placement are
  not taken as rejections, because the id may already name an order.
- **NOT_FOUND** → `AWAITING_RECHECK`: sleep `not_found_delay`, query again.
  `absence_queries` NOT_FOUND answers in a row are confirmed absence. Fewer than
  two is refused, because the frozen text itself names two.
- **Confirmed absence** → resend only if `now < expires_at`; otherwise
  `NEW_AUTHORIZATION_REQUIRED`.
- **UNKNOWN** → `FREEZE`. Three things count as unknown: a query with no
  definite answer, a found order that differs from what was sent, and a
  `sleep` that did not advance the clock. After FREEZE the executor never
  places anything and does **not** release the governor's reservation, so the
  governor refuses every new decision for that symbol until reconciliation
  (Task 23) clears it. The "reconcile" half of "reconcile/FREEZE" is Task 23.
- **Release** (`Governor.release`, the Task 21 contract) happens only after the
  venue's own answer confirms the end of the order: filled, expired after a
  partial fill, rejected, or confirmed absent with no resend allowed. An
  unredeemed authorization is also released when the state it was bound to
  has moved or when its quantity rounds below `min_qty`, so it cannot block
  the next decision.

## Acceptance tests (roadmap Task 22)

| # | Criterion | Evidence |
| --- | --- | --- |
| 1 | Timeout, NOT_FOUND-then-found, NOT_FOUND-then-absent, UNKNOWN each drive the named transition | `test_timeout_queries_the_client_order_id`, `test_not_found_waits_the_protocol_delay_then_finds_the_order`, `test_confirmed_absence_resends_with_the_identical_client_order_id`, `test_unknown_ends_in_freeze_and_never_in_a_new_order` (3 cases); simulator versions in the integration file |
| 2 | Resend after confirmed absence reuses the identical `clientOrderId` | `test_confirmed_absence_resends_with_the_identical_client_order_id`, `test_a_lost_order_confirmed_absent_is_resent_under_the_same_id` |
| 3 | Resend with an expired authorization is refused; a new one is demanded | `test_a_resend_after_expiry_is_refused_and_asks_for_a_new_authorization`, `test_a_lost_order_after_expiry_needs_a_new_authorization` |
| 4 | UNKNOWN ends in reconcile-or-FREEZE, never a new order | `test_unknown_ends_in_freeze_and_never_in_a_new_order`, `test_an_unknown_query_freezes_and_keeps_the_reservation`, `test_freeze_is_reachable_only_from_ambiguity_and_never_leads_to_placing` |
| 5 | No path places two distinct orders under one authorization | `test_one_authorization_never_places_two_orders`, `test_random_venue_behaviour_never_exceeds_one_order_or_the_bound` (400 random venue scripts) |
| 6 | Every (state, event) pair is defined or explicitly rejected | `test_every_state_event_pair_is_defined_or_explicitly_rejected`, `test_terminal_states_have_no_way_out_and_others_have_one` |

Mutation checks, each applied alone to the source and run against the two
executor test files:

| Mutation | Result |
| --- | --- |
| Resend even after expiry | caught |
| UNKNOWN query leads to resend | **hung** (see T22-05) |
| Release the reservation on FREEZE | caught |
| Skip the protocol delay | caught |
| One NOT_FOUND counts as absence | caught |
| Remove the order-mismatch check | caught (after adding the wrong-side test; the first run survived) |
| `DUPLICATE_CLIENT_ORDER_ID` treated as a rejection | caught |
| New `clientOrderId` per attempt | caught |
| Quantity rounded up one step | caught |

## Validation

Environment: Windows 11, `.venv` Python 3.14.

| Command | Result |
| --- | --- |
| `pytest -q` | 1461 passed, 4 skipped in 81.70s |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 90 files already formatted |
| `mypy src scripts` | Success: no issues found in 46 source files |
| `lint-imports` | Contracts: 5 kept, 0 broken |

Frozen verification: SHA-256 of every file in `docs/`, `protocols/`,
`schemas/`, `specs/` and `FROZEN_HASHES.json` was recorded before any edit
and is byte-identical after. `git diff main` touches none of those paths.

## Disclosed deviations and limits

- **T22-01. Task 18 simulator changed.** The two new fault fields are additive
  and default to off, and every existing simulator test still passes. The
  simulator had been reviewed and accepted without them.
- **T22-02. Error meanings are the simulator's, not Binance's.** Every
  placement error except `NOT_FOUND` and `DUPLICATE_CLIENT_ORDER_ID` is taken
  as a definite rejection. On Binance some errors leave the outcome unknown
  (for example a backend timeout). Before any real venue adapter exists, its
  error codes must be mapped to "rejected" versus "unknown" from official
  Binance documentation. Until then, anything uncertain must map to unknown.
- **T22-03. `MARKET_LOT_SIZE` (T18-06) is still open.** The executor rounds to
  the filters the caller passes in. Every test passes explicit synthetic
  filters. No exchange-derived filters reach the executor.
- **T22-04. Release follows order-level confirmation, not account
  reconciliation.** Balance reconciliation is Task 23. The next decision must
  be made from a freshly read `ActualState`, and the governor re-evaluates from
  it (section 20).
- **T22-05. Termination depends on the clock.** Each resend comes after at
  least one full protocol delay, the executor checks that each sleep advanced
  the clock (otherwise FREEZE), and no resend is allowed after expiry. That
  bounds placements at `ttl / delay + 1`, and the fuzz test asserts this. A
  mutation that sends UNKNOWN to resend bypasses the sleep and loops forever
  instead of failing a test. The test suite has no per-test timeout.
- **T22-06. Slippage is reported, not enforced.** A market order cannot be
  capped. `adverse_move_bps` compares the fill price with the state's mark
  price, and `slippage_breach` flags a move beyond `max_slippage_bps`. The
  simulator fills at the next bar's open, so any gap of more than 15 bps shows
  as a breach. What a breach should trigger is question T22-Q2.

## Owner questions

- **T22-Q1. The protocol delay and the absence count** (deployment draft
  section 7, `[OPEN]`). The executor refuses to run without them. Proposal: 10
  seconds, and 2 NOT_FOUND answers, the minimum the frozen text allows. Neither
  value is adopted.
- **T22-Q2. What a slippage breach does.** Options: report only (current), or
  FREEZE after a breach until reviewed. FREEZE is the safer choice, but with
  hourly bars it would stop paper trading often.

## Outstanding before merge

- GPT-6 Astra review (section 16, Q2).
- Owner behavioural review (section 16), in plain language with yes/no
  questions, as for Tasks 17 and 21.

## Update after Astra review 1 (see `REVIEW.md`, `ADJUDICATION.md`)

This supersedes the "Release" bullet, T22-04, T22-05 and T22-06 above:

- **Release:** the executor releases the governor's reservation only when it
  sent nothing to the venue. Any run that placed an order, even one that ends
  filled, rejected or confirmed absent, ends with `reconciliation_required`,
  and only reconciliation (Task 23) releases it.
- **Clock:** every clock reading must move forward, or the run FREEZEs.
  Placements are also capped at the authorization's lifetime divided by the
  protocol delay, plus one.
- **Expiry** is checked immediately before every placement.
- **Slippage:** a fill beyond `max_slippage_bps` ends in FREEZE. It cannot be
  prevented with a market order.
- **New question T22-Q3:** enforcing the slippage bound before the fill needs
  a price-capped order type in a live adapter. That is an execution-contract
  decision for the owner, not an AI edit.
- **T22-Q2 now reads:** breaches FREEZE by default. Should that be relaxed?

Validation after repair: `pytest -q` 1467 passed, 4 skipped; ruff, format,
mypy and lint-imports clean; frozen files unchanged.

## Update after Astra review 2 and owner answer T22-Q3

- R2-1, R2-2 repaired (`ADJUDICATION_2.md`).
- T22-Q3 answered by the owner, "Cap the price" (`OWNER_ANSWER_Q3.md`). Every
  order is immediate-or-cancel at the slippage cap, and a gap beyond it
  trades nothing (`NOT_FILLED`). This supersedes T22-06 and T22-Q2. Paper
  results can now differ from the always-fill backtest; disclosed.
- Still open for the owner: T22-Q1 (protocol delay and absence count) and the
  `max_slippage_bps` value itself.

## Update: defect found by the Task 24 loop (T22-07)

- **T22-07. Full-exposure buys were always rejected.** The quantity was the
  governor's bound: all the cash at the mark. At a 100% target the frozen
  costs made every such buy `INSUFFICIENT_BALANCE`. It surfaced when the
  Task 24 loop ran on synthetic data at a 100% baseline target. A buy is now
  also capped by `affordable_quantity`: the largest step multiple whose cost
  at the price cap, plus the cost model's worst-case 27 bps per side (fee 10
  + spread 2 + slippage cap 15), fits in the quote balance. This places less
  than authorized, which section 20 allows. A fee schedule above the
  fallback could still be rejected, which ends the run safely as REJECTED.
- Tests: `test_a_full_exposure_buy_is_sized_to_what_the_cash_can_pay` (fails
  without the fix), `test_affordable_quantity_never_exceeds_the_cash_at_the_worst_cost`.
- This change is not covered by Astra reviews 1 to 3. It goes into the fourth
  review.

## Update after independent review 4 and the exact-head local gate

Review 4 is recorded in `REVIEW_4.md` against clean commit `5d08c6f`. Its code
verdict is ACCEPT, with no blocker and two simulator-scope non-blocking
findings: future live sizing must distinguish free from locked quote balance,
and must use the verified account fee rather than assuming the frozen 10 bps
fallback. No code repair was warranted inside Task 22's simulator-only scope.

Exact-head validation:

| Command | Result |
| --- | --- |
| `.venv\Scripts\python.exe -m pytest -q` | 1480 passed, 4 skipped in 80.29s |
| `.venv\Scripts\python.exe -m ruff check .` | All checks passed |
| `.venv\Scripts\python.exe -m ruff format --check .` | 90 files already formatted |
| `.venv\Scripts\python.exe -m mypy src scripts` | Success: 46 source files |
| `.venv\Scripts\lint-imports.exe` | Contracts: 5 kept, 0 broken |
| `git diff --check origin/main...HEAD` | clean at reviewed commit |
| `review/task6/verify_frozen.ps1` (PowerShell 7) | 28/28 trusted bytes and 14/14 sidecars; all bindings pass |

The first `pytest.exe -q` attempt exposed a stale launcher that selected an
obsolete Python 3.12 path against the Python 3.14 environment. The required
documented `python -m pytest` command ran with Python 3.14.7 and passed; no
dependency or source file was changed to obtain the result.

Still required before merge: the owner's section 16 review of T22-07 and the
reviewer-metadata choice stated in `REVIEW_4.md`.
