# Task 24 local report: the paper-trading loop

Date: 2026-09-27. Coding AI: Claude Opus 5.5 (`claude-opus-5-5`).
Branch: `task24-paper-loop`, on top of `task23-safety` (which contains
`task22-executor`). Neither is merged yet.

Section 16 covers protocol-enforcement logic, which includes this code.
Merging needs a GPT-6 Astra review and the owner's behavioural review.
Neither has happened yet. Q1 (section 25) was answered by the signature on
2026-09-26, Q2 names Astra, and Q5 is answered in `OWNER_ANSWER_Q5.md`
(baseline only).

## What changed

| File | Change |
| --- | --- |
| `src/aqt/allocation/predictor.py` (new) | `baseline_proposal`: the frozen `VOL_TARGET_BUY_AND_HOLD` target only, on the unbroken run of bars ending at the decision |
| `src/aqt/app/paper_loop.py` (new) | `PaperConfig`, `load_config`, `run_paper`, `RunReport`, `frozen_hash_problems`, `contiguous_window`, `nonce_for` |
| `scripts/run_paper_trading.py` (new) | Loads the exploration series through the Task 14 manifest builder, runs, and writes the report and logs |
| `configs/paper_trading.example.toml` (new) | Every value, each marked OWNER-SET or `[OPEN]` |
| `pyproject.toml` | New contract: `aqt.app` cannot import research, model or lockbox code |
| `tests/integration/test_paper_loop.py` (new) | 17 tests |
| Task 22 `orders.py`, `machine.py` (on the Task 22 branch) | T22-07: buys sized to what the cash can pay. Found here; see below. |

## How the loop reads section 19

Each hour, in order:
1. the safety controller (FLATTEN step; HALT or FREEZE stops trading);
2. the predictor;
3. the governor, deciding from the reconciled state;
4. the executor, placing one capped order at most;
5. reconciliation of anything sent. Only a passed reconciliation settles
   (releases) the reservation.

A FREEZE from the executor, or a failed reconciliation, freezes the run. The
run then does nothing more until the end of the window.

REFUSE_START, each tested alone:
- a frozen hash mismatch (protocol, cost model, benchmark spec, Constitution
  content hash);
- no alert sink;
- a damaged operations log;
- a Binance credential variable set (the value is never echoed);
- a run window crossing a data gap;
- a failed startup reconciliation;
- an open incident.

A non-simulator adapter is refused when the configuration is read.

## Acceptance tests (roadmap Task 24)

| # | Criterion | Evidence |
| --- | --- | --- |
| 1 | A multi-month run is deterministic across two runs | `test_a_multi_month_run_is_deterministic`: 60 days, identical report digest and identical operations-log bytes, and orders actually filled |
| 2 | Every REFUSE_START condition tested individually | `test_refuse_start_on_a_hash_mismatch` (3 files), `..._without_an_alert_sink`, `..._on_a_damaged_operations_log`, `..._when_a_credential_is_set`, `..._when_the_window_crosses_a_data_gap`, `..._on_a_reconciliation_mismatch`, `..._with_an_open_incident` |
| 3 | No order without a live, unexpired authorization | `test_no_order_is_placed_without_a_live_unexpired_authorization`: every placement is matched to a successful redemption, and the executor clock at placement lies in `[issued_at, expires_at)` |
| 4 | A non-simulator adapter raises at configuration | `test_a_non_simulator_adapter_is_refused_at_configuration`, `test_the_example_configuration_loads` |
| 5 | A mid-run fault drives section 21, then section 22, and ends in FREEZE, not in an order | `test_a_mid_run_fault_ends_in_freeze_not_in_an_order`: order state `FREEZE`, trigger `AMBIGUOUS_ORDER`, one open incident, no further order through the rest of the window |
| 6 | The report names the protocol hash, data manifest hash, decision count and cost model hash | `test_the_report_names_the_hashes_and_the_decision_count` |

Also tested: an owner FLATTEN sells everything and ends in HALT; an owner
HALT stops all orders.

Mutation checks, each applied alone and run against the relevant tests. All
7 were caught: no hash check, no credential check, no adapter check, no
FREEZE on an unknown order, no gap check, no startup reconciliation, owner
commands ignored. The FREEZE mutation survived the first test version. That
revealed the fault test was passing through the backup reconciliation freeze
on a *rejected* order (see T22-07). The test now asserts the executor's own
`FREEZE` and the `AMBIGUOUS_ORDER` trigger.

## Defects found while building the loop

- **T22-07 (in Task 22's executor): full-exposure buys were always
  rejected.** At a 100% target the order cost all the cash plus fees, so the
  simulator rejected it (`INSUFFICIENT_BALANCE`). Fixed on the Task 22 branch
  and merged up: buys are also capped by what the cash pays for at the price
  cap plus the cost model's worst-case 27 bps. Recorded in
  `review/task22/LOCAL_REPORT.md`, and part of Task 22's pending fourth
  review.
- **Data gaps.** The frozen baseline and the frozen cost model both refuse
  gapped history. The exploration data has 31 unbroken runs per symbol, the
  longest being 2020-06-28 to 2020-11-30. The predictor uses the unbroken
  run ending at each decision, as the research harness does, and a run
  window crossing a gap is refused at start.

## Validation

Environment: Windows 11, `.venv` Python 3.14.

| Command | Result |
| --- | --- |
| `pytest -q` | 1535 passed, 4 skipped in 254.39s |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 99 files already formatted |
| `mypy src scripts` | Success: no issues found in 52 source files |
| `lint-imports` | Contracts: 6 kept, 0 broken |

Frozen files: SHA-256 identical to the pre-Task-22 snapshot.

Real-data smoke run: see the addendum below.

## Disclosed choices and limits

- **T24-01. Speed.** The frozen volatility estimator uses exact fraction
  arithmetic over the whole history at every decision, so a 5-month run takes
  about 3 minutes and the 60-day test about 100 seconds. The frozen code was
  not changed for speed.
- **T24-02. Health checks** (stale data, clock skew, loop lag; deployment
  draft section 4 item 9) are not wired in. Their thresholds are `[OPEN]`,
  and on the bar clock of a simulated run they cannot fire.
- **T24-03. Code identity** (the deployed commit, in section 4 item 1's list)
  is not checked. The loop checks the frozen specification hashes only.
- **T24-04. The loss stop (L-03) is not computed yet.** The trigger exists
  (Task 23). Drawdown from peak equity is for Task 25's drills, or an owner
  question if it should be automatic now.
- **T24-05. Owner commands in a simulated run are scheduled** (`commands`), so
  drills are reproducible. There is no interactive command channel.
- **T24-06. Reconciliation right after each order.** An order is reconciled
  in the same hour it is sent, so the governor is never blocked into the
  next hour by a completed order.
- **T24-07. The example configuration** carries `[OPEN]` example values for
  `max_slippage_bps` (15), `authorization_ttl` (120 s) and the exchange
  filters. They are not the owner's choices.

## Outstanding before merge

- Tasks 22 and 23 merge first; each needs its Astra review and owner review.
- GPT-6 Astra review of Task 24.
- The owner's behavioural review.

## Addendum: real-data smoke run

`python scripts/run_paper_trading.py --config configs/paper_trading.example.toml`
on BTCUSDT exploration data, 2020-07-06 to 2020-11-29, which is inside the
longest unbroken run. Data manifest `5f92ec5041c9560d5f31bdb99b9686d7522697e65a8e61d514a0b0dda6d0b65b`. Result: 3504 hours,
146 scheduled decisions, 2 authorizations, 2 orders sent, 3502 governor
refusals (`INSIDE_REBALANCE_BAND`), final mode RUNNING, final balances
0.95551 BTC and 2429.72 USDT (from 10000 USDT). The baseline bought close to
its target early and then held. The previous run, before T22-07, reported
30 "orders" because its full-exposure buys were being rejected and retried
daily.

This is one paper run of a benchmark on exploration data. It is not
evidence of anything about returns.

## Update: L-03 stop and health checks wired in (owner settings S-4, S-5)

Built on the owner's instruction ("Yes, build both"), after the senior
advisor check (`review/deployment/SENIOR_ADVISOR_CHECK_2026-09-27.md`) found
both missing. This supersedes T24-02 and T24-04.

- **L-03 loss stop.** Each hour the loop marks equity from the reconciled
  balances at the decision bar's close and tracks its peak. At 20% below the
  peak (`loss_stop_fraction`, ADOPTED L-03), while still holding a sellable
  amount in RUNNING or HALT, it fires `LOSS_STOP`. On the Task 23 branch
  that now enters FLATTEN (`safety.py`, S-4), which sells and ends in HALT.
  An incident is opened.
- **Health checks** (`aqt.monitoring.health`, S-5 thresholds: 2 h / 5 s /
  5 min, each CRITICAL). A breach at start is a REFUSE_START. A breach during
  the run blocks every order that hour, FLATTEN steps included, and is
  counted in `health_breach_hours`. On a simulated run the readings come from
  the bar clock and never breach. Tests inject readings through `observe`.
- New tests: `test_the_loss_stop_sells_everything_then_halts`,
  `test_no_loss_stop_without_a_drawdown`,
  `test_refuse_start_when_a_health_check_fails`,
  `test_a_health_breach_blocks_orders_for_that_hour`, and
  `test_the_loss_stop_sells_then_halts_and_opens_an_incident` (Task 23).
  Mutations caught: no L-03 trigger, health breaches ignored, peak not kept.
- The 60-day determinism path falls more than 20% from its peak, so it now
  ends in HALT through the L-03 stop. Both runs still agree byte for byte.
- Validation: `pytest -q` 1539 passed plus the corrected determinism test
  (see the commit); ruff, format, mypy (52 files), lint-imports (6 kept)
  clean; frozen files unchanged.

## Update 2026-09-28: rebuilt on merged Tasks 22 and 23

By Claude Opus 5.5 (`claude-opus-5-5`), on the owner's instruction ("go Task
24"). Tasks 22 and 23 were merged to `main` (PR #28, PR #29 `c84a5e2`) after
their reviews changed them. The old branch `task24-paper-loop` carried the
pre-review copies, so Task 24 was re-created as `task24-paper-loop-v2` from
`main`, taking only Task 24's own files (loop, predictor, script, example
config, tests, import contract, owner settings, advisor check, deployment
draft edits). The old branch is kept, unmerged, for its history.

### Changes to meet the merged Task 23 contract (`review/task23/LOCAL_REPORT.md`)

- **S-4 restored** (`OWNER_ANSWER_S4.md`): LOSS_STOP enters FLATTEN from
  RUNNING or HALT and keeps FLATTEN going; other alarms during FLATTEN HALT.
- **T23-09 / F23R-1.** The loop used to clear `controller.sent` after every
  FLATTEN reconciliation, even a failed one, which would let a later recovery
  accept a report that never looked up those orders. New
  `SafetyController.settle_flatten(report)` removes only the ids a *passed*
  report resolved; on failure the loop keeps the pre-step baseline plus the
  orders.
- **T23-09 / F23R-2.** An executor order is added to the loop's `LocalRecord`
  before an AMBIGUOUS_ORDER FREEZE, so it stays on record until a passed
  reconciliation settles it. Across restarts, an open incident (every FREEZE
  opens one) refuses the start.
- **T23-09 mark price.** Already the decision bar's close, as the simulator
  checks notional.
- **T23-04 durable refusal.** Any exception out of the hourly loop (for
  example a failed incident or alert write) writes
  `<incident log>.refuse_start` with the error, and re-raises. A start with
  that file present is a REFUSE_START. Only the owner removes it.
- **T23-08 zero fills.** Every `ZERO_FILL_ALERT_AFTER` (= 3, a proposal, not
  owner-set) consecutive IOC orders with nothing filled emit a CRITICAL alert.
  Alert only; it does not stop trading.
- **New defect found and fixed: the loss stop re-fired every hour.** After a
  loss-stop FLATTEN ends in HALT with an unsellable remainder, equity stays
  below the line, so the loop fired LOSS_STOP every hour (FLATTEN, then
  FLATTEN_DONE, two incidents an hour). It now fires once per fall below the
  line and re-arms only when equity is back above it.
- The two FLATTEN loop tests asserted the old whole-remainder behaviour; they
  now assert the reviewed rule (the remainder is under twice the notional
  minimum at the lowest price in the run).

New tests: `test_the_loss_stop_flattens_and_opens_an_incident`,
`test_the_loss_stop_sells_everything_then_halts` (unit),
`test_only_a_passed_reconciliation_settles_flatten_orders`,
`test_a_failed_audit_write_refuses_every_later_start`,
`test_consecutive_zero_fills_raise_a_critical_alert`, and the fires-once
assertion in the loop's loss-stop test. Mutation check: removing the latch
makes the loss-stop test fail (LOSS_STOP counted more than once).

Validation of this state (Windows 11, `.venv` Python 3.14):

| Command | Result |
| --- | --- |
| `pytest -q` | 1570 passed, 4 skipped in 380.98s |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 99 files already formatted |
| `mypy src scripts` | no issues in 52 source files |
| `lint-imports` | 6 kept, 0 broken |
| `git diff --check` | clean |

The frozen verifier needs PowerShell 7, not installed on this machine; git
shows no file under `docs/`, `protocols/`, `schemas/`, `specs/` or
`FROZEN_HASHES.json` differs from `main`.

### Outstanding before merge

- An independent review of Task 24 (GPT-6 Astra, or a substitute the owner
  chooses).
- The owner's behavioural review (section 16).
- Owner question T24-Q1: `ZERO_FILL_ALERT_AFTER = 3`, alert only.

## Update 2026-09-28: Fable review repairs

See `FABLE_REVIEW_646D514.md`, `ADJUDICATION.md`, `OWNER_ANSWERS_2026-09-28.md`.

- F24-1: the owner's HALT wins; S-4 applies from RUNNING only.
- F24-2: `FROZEN_HASHES.json` pinned in code (`FROZEN_MANIFEST_SHA256`).
- T24-Q1 answered: alert only after 3 consecutive zero fills.
- Health-breach hours: pause only (owner, F24-4).
- **T24-08. Paper-only scope of run state** (F24-3). Incident log, refuse
  marker, loss-stop peak and unsettled FLATTEN orders live per run. Any stage
  that continues an account must scope and persist them per account, and the
  owner must decide (F24R-3): whether a HALT override while still below the
  L-03 line sells at once (the latch is still armed if an owner HALT
  pre-empted the stop), and how the stop re-arms after it has fired, since an
  all-USDT account may never regain 80% of the old peak and would then run
  with no L-03 stop.
- F24R-1 (re-review): every L-03 breach outside FREEZE now opens an incident
  and a CRITICAL alert; it sells only from RUNNING.
