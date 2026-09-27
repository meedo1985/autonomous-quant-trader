# Task 23 local report: HALT, FLATTEN, FREEZE and reconciliation

Date: 2026-09-27. Coding AI: Claude Opus 5.5 (`claude-opus-5-5`).
Branch: `task23-safety`, from `task22-executor` at `ee3f4ca`. Task 22 is not
merged yet (its fourth Astra review is pending), so this branch contains it.

Section 16 covers protocol-enforcement logic, which includes this code.
Merging needs a GPT-6 Astra review and the owner's behavioural review.
Neither has happened yet.

## What changed

| File | Change |
| --- | --- |
| `src/aqt/execution/reconcile.py` (new) | `LocalRecord`, `reconcile`, `ReconciliationReport`, `settle` |
| `src/aqt/execution/safety.py` (new) | `Mode`, `Trigger`, `MODE_TRANSITIONS`, `IncidentLog`, `HaltOverride`, `OwnerAction`, `FlattenBounds`, `SafetyController`, `startup_check` |
| `src/aqt/execution/orders.py` | The exact cap arithmetic moved into `capped_price`, so FLATTEN sells share it. `limit_price_for` calls it; behaviour unchanged. |
| `src/aqt/execution/simulator.py` | `open_orders()`, always empty: market and immediate-or-cancel orders never rest |
| `tests/unit/test_safety.py` (new) | 27 tests (with parametrized cases) |
| `tests/integration/test_reconciliation.py` (new) | 11 tests against the simulator, including the Task 22 hand-over |

## How sections 14, 19, 22 and 26 are read

- **Only RUNNING trades** (`may_trade`). The governor and executor act only
  there.
- **HALT places no order at all**, not even a reduction (roadmap acceptance
  test 1, and Astra's Task 21 review 4). Reducing is FLATTEN's job, and the
  owner can start FLATTEN from RUNNING or HALT at any time, whatever
  reservation the governor holds (the Task 21 requirement).
- **FLATTEN** sells only. Each step sells at most `max_step_fraction` of the
  free base balance the venue reports, as an immediate-or-cancel sell capped
  `max_slippage_bps` below the mark. It can never go below zero, because it
  never sells more than the venue says is held. A step too small for the lot
  or notional minimum sells the whole remainder instead. When nothing
  sellable is left, it ends in HALT. Any unclear FLATTEN outcome is FREEZE.
- **FREEZE does nothing.** It does not even read the venue. It is left only
  through a passed reconciliation taken after it began, and it goes to HALT,
  not RUNNING, because the ambiguous order that caused it is an incident that
  must still be closed. An owner FLATTEN during FREEZE is refused, because the
  frozen text allows no exit from FREEZE before reconciliation.
- **Incidents** (section 0: "HALT, reconciliation mismatch, ... ambiguous
  order") go into an append-only, hash-chained ledger (`aqt.core.ledger`,
  section 26). Every entry into HALT or FREEZE opens one. A damaged ledger
  raises; it never reports "nothing open".
- **HALT override** needs all five section 14 artifacts, all supplied by the
  caller: a written record, a cause, a passed reconciliation taken after the
  HALT, an owner action (who acted and what they said), and a timestamp
  within the HALT. It must name every open incident, closes them all, and
  records the artifacts in the close entries. The code fills in none of them.
- **Reconciliation** queries every order sent since the last reconciliation.
  It fails on any unresolved query, any difference from the local copy, any
  order still open, any open order with no local record, or any balance that
  differs from the last reconciled balance plus the exact effect of the
  resolved orders. Only a passed report can `settle` (release governor
  reservations) or produce the next `LocalRecord`.
- **Startup** (`startup_check`) refuses on a failed reconciliation (and opens
  an incident) or on any open incident.
- Every mode change is logged through the alert router. Entries into HALT,
  FLATTEN and FREEZE are CRITICAL.

## Acceptance tests (roadmap Task 23)

| # | Criterion | Evidence |
| --- | --- | --- |
| 1 | HALT while holding exposure places no order | `test_halt_while_holding_exposure_places_no_order` (a spy venue records no call of any kind) |
| 2 | FLATTEN reduces monotonically, never below zero | `test_flatten_reduces_monotonically_and_never_crosses_zero`, `test_flatten_never_sells_more_than_is_held`, `test_flatten_with_the_price_beyond_its_cap_sells_nothing` |
| 3 | FREEZE takes no autonomous action as prices move | `test_freeze_takes_no_action_while_prices_move` |
| 4 | Exiting FREEZE without a successful reconciliation is refused | `test_exiting_freeze_needs_a_passed_reconciliation_after_it`, `test_no_trigger_leaves_freeze_except_reconciliation` |
| 5 | A HALT override missing any one of the five artifacts is refused, once per artifact | `test_a_halt_override_missing_any_artifact_is_refused` (5 cases), plus `test_empty_or_wrong_artifacts_are_refused_too` (7) and `test_a_failed_or_stale_reconciliation_refuses_the_override` |
| 6 | Startup detects an injected mismatch and refuses to start | `test_an_injected_balance_mismatch_refuses_to_start`, `test_an_untracked_open_order_refuses_to_start` |

Also tested: every (mode, trigger) pair is defined or refused; the tampered
incident log; time going backwards; the Task 22 hidden-fill hand-over
(`test_a_hidden_fill_is_found_and_only_then_released`).

Mutation checks, each applied alone. All 17 were caught after one test
addition: HALT reducing, FREEZE acting, FLATTEN doubling its step, FREEZE
exit without a passed reconciliation, each of the five override checks,
override without closing every incident, FREEZE exiting to RUNNING, HALT
without an incident, ignoring untracked open orders, ignoring balances,
ignoring the local copy, settling on a failed report, and treating a server
error as absence. The last one survived at first;
`test_a_server_error_on_the_query_is_unresolved_not_absent` was added.

The tests also found an implementation error: FLATTEN stopped with 0.155 BTC
(about 15 USDT) still sellable, because half of it was under the 10 USDT
notional minimum. A step below the minimum now sells the whole remainder.

## Validation

Environment: Windows 11, `.venv` Python 3.14.

| Command | Result |
| --- | --- |
| `pytest -q` | 1516 passed, 4 skipped in 107.81s |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 94 files already formatted |
| `mypy src scripts` | Success: no issues found in 48 source files |
| `lint-imports` | Contracts: 5 kept, 0 broken |
| `git diff --check` | clean |

Frozen files: SHA-256 identical to the Task 22 pre-task snapshot.

## Disclosed choices and limits

- **T23-01. Alarms during FLATTEN keep flattening.** An incident or loss-stop
  alarm during FLATTEN is recorded as an incident but does not stop the
  reduction. Only the owner's HALT stops it. This is a proposal: the frozen
  text does not say.
- **T23-02. Every HALT is an incident** (section 0). That includes the HALT
  at the end of a completed FLATTEN, so resuming after any FLATTEN needs the
  five-artifact override.
- **T23-03. Startup covers only reconciliation and incidents.** The other
  `REFUSE_START` conditions in deployment draft section 4 (hashes, alert
  channel, health checks, adapter) belong to the loop (Task 24).
- **T23-04. Mode survives a restart only through the incident log.** An open
  incident refuses the start. There is no separate stored mode.
- **T23-05. The simulator never has open orders**, so the untracked-open-order
  case is tested with a subclass that reports one.
- **T23-06. Loss-stop detection (`L-03`) is not here.** The trigger exists;
  computing drawdown from peak equity is the loop's job (Task 24).

## Owner questions

- **T23-Q1. FLATTEN bounds** (deployment draft section 6, `[OPEN]`).
  Proposal: sell at most **50%** of the holding per step, capped **1%** (100
  bps) below the mark. The exit cap is wider than the trading cap, because an
  exit that never fills in a falling market protects nothing.
- **T23-Q2. Reconciliation tolerance** (deployment draft section 3, `[OPEN]`).
  Proposal: **0**, exact, on the simulator. A real venue's rounding may need
  more, to be decided before shadow.

## Outstanding before merge

- Task 22 must merge first (its fourth Astra review is pending).
- GPT-6 Astra review of Task 23 (section 16).
- The owner's behavioural review.
