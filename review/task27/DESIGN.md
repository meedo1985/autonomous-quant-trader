# Task 27 design: state that survives restarts

**Status:** design note, before code. Author: Claude Opus 5.5
(`claude-opus-5-5`), 2026-09-29. Authorized by roadmap 2 answer Q-D. Code
waits until PRs #35 and #36 merge, because it builds on both.

## 1. The problem

Today a paper run is one process: everything the safety system knows lives
in memory and dies with it (T24-08, F24-3, F24R-3, T23-04). That was fine for
replays, where every run is a fresh simulated account. A live forward-paper
or shadow app runs for months and **will** restart: updates, reboots, power
cuts. After a restart it must know everything it knew before, or it can
trade when it should not.

## 2. What must be kept, per account (not per run)

| State | Lives today in | Why it matters after a restart |
| --- | --- | --- |
| Incident log | `incidents.jsonl` per run | An open incident must refuse the start (§14) whatever the run id |
| Refuse-start marker | next to the incident log | A crash marker must block every later start until the owner clears it (T23-04) |
| Mode (RUNNING, HALT, FLATTEN, FREEZE) and its entry time | controller memory | A HALT must still be a HALT after a reboot; a FREEZE must still need reconciliation |
| Unsettled FLATTEN orders (`sent`) and their quantity and cap (`attempts`) | controller memory | Recovery must look them up (F23-2, A2324-1); forgetting them allows a blind recovery |
| Last reconciled record (balances plus orders sent since) | loop memory | The baseline reconciliation compares against (T23-09) |
| Loss-stop peak and latch | loop memory | Without the peak, a restart resets the 20% line to the current (lower) equity: the stop silently moves |
| Last risk increase time; zero-fill streak | loop memory | Governor pacing; alert continuity |
| Live bar store gap record | none | T26-04: a real Binance gap needs an owner-acknowledged record to continue |

## 3. Proposed mechanism

- One **state directory per account** (for example `state/<account>/`), not
  per run id. Every paper, forward-paper or shadow run for that account uses
  it. A new run id no longer means fresh state (F24-3).
- The incident log and the operations log stay as they are (hash-chained,
  append-only).
- A new **state journal**, also a hash-chained append-only ledger: the loop
  appends a snapshot of the table's state after every change (mode change,
  order sent, reconciliation, new peak). On start, the last intact snapshot is
  loaded; a damaged journal, or a snapshot that disagrees with the incident
  log, is a `REFUSE_START`.
- Startup order: marker check, journal load, reconciliation against the
  loaded record (with the section 21 absence check), incident check. A loaded
  FREEZE or HALT is resumed as FREEZE or HALT, never as RUNNING.
- Writes are fsynced before the action they describe is considered done. A
  crash between an order and its journal entry is covered because the order
  id is journaled **before** sending, as FLATTEN already does in memory.

## 4. Decisions needed from the owner before coding

These were recorded as open in Task 24 (F24R-3) and belong to the owner:

- **Q27-1. Restarting from HALT while still below the loss line.** If the
  owner ends a HALT while equity is still more than 20% under its peak,
  should the loss stop fire again at once (selling in steps), or wait for a
  new fall?
- **Q27-2. Re-arming the loss stop after it sold everything.** After a
  loss-stop sell-off the account is almost all cash, so equity may never get
  back above 80% of the old peak, and the stop would never re-arm. Options:
  reset the peak to current equity when the owner restarts trading; or keep
  the old peak (the stop stays spent until the owner decides).
- **Q27-3. A real gap in Binance's prices** (T26-04). Options: the owner
  acknowledges the gap in a signed record and the store continues after it;
  or the store stops for good and a new one is started.

## 5. Acceptance (from roadmap 2)

Killing the process at every step and restarting never loses an open
incident, never double-counts an order, never starts past a marker, and
never resumes RUNNING from a HALT or FREEZE. Plus: a restart keeps the
loss-stop peak, and a damaged journal refuses the start.

## 6. Size and review

Likely over the 400-line budget; split point: (a) state directory, journal
and startup load; (b) loop wiring and the loss-stop decisions. Protected
under section 16: Astra review and the owner's walkthrough before merge.
