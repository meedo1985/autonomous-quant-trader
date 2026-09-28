# Task 23 re-review of `3b9237e` (Claude Fable 5.1)

Date: 2026-09-28

- Reviewer model: Claude Fable 5.1 (`claude-fable-5-1`), a read-only Claude
  Code subagent, requested by the owner ("yes run the Fable re-review").
  Substitute for the exact GPT-6 Astra review, chosen by the owner.
- Reviewed commit: `3b9237e` (repairs to F23-1..F23-4), read against
  `git diff 752f158 3b9237e` and the full `safety.py` and `reconcile.py`.
- Reviewer's tests: 64 passed (`test_safety.py`, `test_reconciliation.py`).

## Earlier findings

- **F23-1: CORRECT.** Clamping only moves `entered_at` forward, so it can
  never make an older reconciliation eligible; a report later than the latest
  time stays eligible. OWNER_FLATTEN and both procedures remain strict.
- **F23-2: CORRECT for FLATTEN orders**, limits in F23R-1 and F23R-2. The
  coverage check runs before any state change; clearing `sent` cannot lose an
  order because no FLATTEN order is sent outside FLATTEN; HALT_OVERRIDE_FAILED
  keeps `sent`. The override test sets `mode = HALT` directly: this reaches an
  unreachable state (HALT with an unknown `None` entry) and hides no bug, but
  does not cover the reachable case (HALT holding a known FILLED order).
- **F23-3: CORRECT.** Cannot block FLATTEN permanently while bars advance;
  a raising `place_order` delays the next step by one bar. See F23R-3.
- **F23-4: CORRECT.** Mark validated before any read or sizing.

No path found that trades outside RUNNING, sells more than 50% within one
`decision_time`, or crosses zero.

## New findings

### F23R-1 — NON-BLOCKING — recovery must rebuild from the pre-FLATTEN baseline; undocumented

`safety.py` `sent` docstring says "since the last passed reconciliation", but
`sent` is cleared only on recovery. Scenario: OWNER_FLATTEN, one FILLED step,
LOSS_STOP -> HALT; a routine reconciliation passes and the loop advances to
`next_record()`; a second INCIDENT moves `entered_at` past it. A report from
`next_record()` alone is refused ("did not resolve"); `next_record()` plus
`sent` fails (fill counted twice); only the pre-FLATTEN baseline plus `sent`
passes. Reproduced. Fix: state that the baseline must not advance while
`sent` is non-empty, or clear `sent` on any passed report that resolved it.

### F23R-2 — NON-BLOCKING — coverage checks only FLATTEN orders

The controller does not record executor order ids; `trigger(AMBIGUOUS_ORDER,
...)` carries only a detail string. A blind `LocalRecord(balances)` report
then passes `exit_freeze` and `override_halt`. Also `sent` is in memory only,
so a restarted controller accepts a blind recovery. Reproduced. Fix: Task 24
obligation (the loop's `LocalRecord` must carry ambiguous executor ids and
persisted FLATTEN ids), or let AMBIGUOUS_ORDER carry the id into `sent`.

### F23R-3 — NON-BLOCKING — a future `decision_time` stalls FLATTEN silently

`decision_time` is never checked against `at`. `tick(decision_time=T0+10h,
at=T0+4h)` sells 0.5; correct ticks for bars 5-9 then return None with no
incident or alert. Reproduced. Fix: refuse `decision_time > at` as
FLATTEN_FAULT before recording the decision.

## Verdict

ACCEPT.
