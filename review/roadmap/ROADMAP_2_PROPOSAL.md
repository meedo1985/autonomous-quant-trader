# Roadmap 2 proposal: forward paper and shadow (Tasks 26-32)

**Status:** PROPOSAL. Nothing here is authorized until the owner approves it.
**Author:** Claude Opus 5.5 (`claude-opus-5-5`), coding AI, advisory only
(Constitution sections 15 and 16).
**Date:** 2026-09-29.
**Baseline:** roadmap 1 (Tasks 13-25) ends with a simulator paper-trading app
on historical data (Task 25, PR #31, pending review). Cycle `C1` has not
started; verdict `KEEP_BLOCKED`; `L-01` is 0.

## 0. What this roadmap is, and what it is not

It takes the app from replaying 2020 prices to running **live, around the
clock, on a rented server**. It covers the two stages the deployment draft
puts before any real money:

| Stage | Prices | Orders | Money |
| --- | --- | --- | --- |
| **Forward paper** | live, as they arrive | to the simulator only | none |
| **Shadow** | live | computed, approved and logged, **never sent** | none |

Out of scope, and not reachable by finishing every task below: canary or any
real order; a trading API key; raising `L-01`; starting `C1`; any statistical
binding (`D-16`, `D-17`, ...); any strategy other than the frozen baseline
`VOL_TARGET_BUY_AND_HOLD`; changing any frozen file.

## 1. The honest timeline

The rules, not the code, set the pace:

- **Forward paper must reach `L-02`: at least 240 *effective* decisions**
  (adopted 2026-09-26). The protocol's unit discounts correlated decisions
  (`protocol_v1.yaml:242-244`). The baseline decides once a day, so this is
  **at least 8 months** of live running, more if the primary method (Newey-West
  ESS) is used rather than the fallback. Historical replay cannot count
  (deployment draft §2.1, review finding R-2).
- **Shadow then runs 90 days** (owner setting D-3).
- So the earliest a canary could even be proposed is **about 11 months after
  forward paper starts**, and only if every gate passes. Building the software
  (the tasks below) is weeks; the waiting is the rules working as intended.
- **What this proves:** that the machinery works live for months. **What it
  does not prove:** an edge. The strategy is still buy-and-hold with a risk
  target. An edge can only come from research cycle `C1`, which is blocked on
  `D-16`/`D-17`. A strategy chosen later starts its own `L-02` clock.

## 2. Conventions

Those of roadmap 1 section 1 apply unchanged: one session and about 400
changed lines per task; full validation recorded under `review/task<NN>/`;
`task-gate-review` at every task end; the section 16 different-model review
(GPT-6 Astra) and the owner's behavioural review before any protected merge;
merge only on the owner's instruction.

## 3. Tasks

### Task 26 — Live public market data (no keys)

Read closed hourly BTCUSDT bars from Binance's public market-data API
(`data-api.binance.vision`, no credential), validate them with the Task 14
bar rules, and append them to a local store. Refuse gaps, duplicates,
unclosed bars and clock skew (S-5). Blocked on **Q-A**.
**Accept:** a recorded fixture replays byte-identically; a gap, a duplicate
and an out-of-order bar are each refused; no credential variable is read.

### Task 27 — State that survives restarts (T24-08, F24-3, F24R-3)

Persist, per account rather than per run: the incident log, the refuse-start
marker, the loss-stop peak and latch, unsettled FLATTEN orders, and the last
reconciled record. Decide with the owner the two recorded loss-stop questions
(sell at once on a HALT override below the line; how the stop re-arms).
**Accept:** killing the process at every step and restarting never loses an
open incident, never double-counts an order, and never starts past a marker.

### Task 28 — Telegram alert sink (D-1, D-2)

A sink that sends CRITICAL events to a private Telegram bot; a weekly test
alert the owner acknowledges; `REFUSE_START` if the last acknowledged test is
older than 7 days. The bot token is read from the OS credential store (D-8)
and never logged. Blocked on **Q-B**.
**Accept:** a failed send is itself logged and alerted locally; an overdue
test refuses start; the token never appears in any log, report or test.

### Task 29 — Forward paper mode

The Task 24 loop on the live bar store and a wall clock, fills simulated.
Counts effective decisions toward `L-02` and states which method it used
(primary or fallback), as `LOSS_BOUND_DEFAULTS.md` requires.
**Accept:** the same bars give the same decisions as replay; a missed hour is
a health breach, never a silent skip; the `L-02` counter matches a
hand-computed example.

### Task 30 — Server runbook and code identity (D-7, T24-03)

A written runbook for the rented server: install, service start on boot,
where logs go, how to update from a reviewed commit only. `REFUSE_START` if
the running code is not a reviewed commit on `main`. The owner rents the
server and records its IP; the AI never logs into it.
**Accept:** a dry run of the runbook on a clean machine; a modified file
refuses start.

### Task 31 — Shadow mode

A shadow adapter that takes each authorized order, checks it against
Binance's live filters (re-read daily), and logs exactly what would have been
sent, **without an order endpoint in the code at all**. A test proves no
code path can reach an order URL.
**Accept:** shadow and forward paper on the same bars make the same
decisions; the no-order-path test fails if any order URL is added.

### Task 32 — Forward-paper and shadow evidence report

A monthly report in the section 23 form (decisions, effective decisions and
method, costs, incidents, alerts tested), committed, with the statement that
it proves operation, not edge.

## 4. Questions for the owner before approval

- **Q-A. Live price data over the network.** Constitution §15 denies the
  research AI network access in Cycle 1; the live path (§19) must read live
  prices. The proposal is: the *app*, running on the server, may read
  Binance's public market-data API (no key, read-only); the AI never makes
  these calls itself. Approve, or keep it blocked?
- **Q-B. The Telegram bot token.** It is a credential. Milestone 0.1 forbade
  credentials, and §28 allows production secrets only under the executor's
  identity. Approve a Telegram token stored only on the server (D-8), never
  in the repository or shown to an AI?
- **Q-C. Which strategy runs forward paper.** Only the frozen baseline exists.
  Running it starts the machinery's months of live evidence now; a strategy
  from `C1` later would restart its own `L-02` clock. Run the baseline, or
  wait for `C1`?
- **Q-D. Order of work.** Tasks 26-28 and 30 need no strategy and no money.
  Approve them first and decide Tasks 29, 31, 32 later?

## 5. What stays true after Task 32

No real order has been sent; no trading key exists; `L-01` is 0; `C1` has not
started; no edge is shown. Canary needs, at minimum: `L-02` and 90 days of
shadow met with no open incident; the §8 key rehearsals; `L-01` raised by the
owner; the deployment protocol activated by the owner under Constitution §4;
and, for any strategy other than the baseline, a promotion under the frozen
rules.
