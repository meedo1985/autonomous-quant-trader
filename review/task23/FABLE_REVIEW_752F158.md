# Task 23 adversarial review of `752f158` (Claude Fable 5.1)

Date: 2026-09-28

- Reviewer model: Claude Fable 5.1 (`claude-fable-5-1`), a Claude Code
  subagent, read-only. Requested by the owner ("use Fable now") as a
  substitute for the exact GPT-6 Astra review while Codex was at its usage
  limit. It is not an exact-Astra review; the owner accepted the substitution.
- Implementation of Task 23: Claude Opus 5.5 and OpenAI Codex (GPT-6 family).
- Reviewed commit: `752f158b88654684964971d7f8e1b9723b22fb47`, base `edc3b39`.
- Reviewer's tests: `pytest -q tests/unit/test_safety.py
  tests/integration/test_reconciliation.py` -> 52 passed.

Findings are recorded verbatim in substance below; dispositions are in
`ADJUDICATION.md`.

## F23-1 — BLOCKER — protective trigger refused on a backwards timestamp

`safety.py:258-269`: `_time` raises `SafetyError("time went backwards")` for
every trigger, including OWNER_HALT, INCIDENT, LOSS_STOP, AMBIGUOUS_ORDER and
RECONCILIATION_FAILED. After an override at 02:00:00, `trigger(LOSS_STOP,
01:59:59)` is refused and the controller stays RUNNING with `may_trade()`
True. In FLATTEN, a LOSS_STOP stamped before the last step is refused and
FLATTEN keeps selling, defeating T23-QB in that timing. Reproduced (probe
P1): LOSS_STOP, OWNER_HALT and AMBIGUOUS_ORDER all REFUSED, mode RUNNING.
Suggested fix: clamp protective triggers to `max(at, latest)` and record the
original time; keep strict check for FREEZE_EXIT, HALT_OVERRIDE,
OWNER_FLATTEN.

## F23-2 — NON-BLOCKING — recovery accepts a report that never queried the ambiguous order

`exit_freeze` and `override_halt` check only `report.passed` and its time,
not that `report.resolved` covers the controller's unresolved `self.sent`
ids. A `LocalRecord(venue.balances())` with no orders passes by construction.
`self.sent` is never cleared, so feeding it again after `next_record()` would
double-apply orders. Reproduced (probe P3): FREEZE with an unresolved
FLATTEN id, tautological report passed, exit_freeze -> HALT, override ->
RUNNING, zero venue queries for the id. Suggested fix: require every id in
`sent` since the last passed reconciliation to be in `report.resolved`, and
define when `sent` is cleared.

## F23-3 — NON-BLOCKING / QUESTION — repeated FLATTEN ticks sell 87.5% in one bar

`tick` accepts a repeated `decision_time`; each call sells 50% of the
remainder. Four ticks for one bar sold 0.5, 0.25, 0.125 BTC at the same fill
time (probe P2). Suggested fix: require `decision_time` to advance strictly,
or have the owner define "per step" and make cadence a Task 24 obligation.

## F23-4 — NON-BLOCKING — mark price validated only when max_notional applies

`safety.py:405-415`: a NaN mark with no maximum notional raises
`decimal.InvalidOperation` out of `tick` (mode stays FLATTEN, no incident);
a mark <= 0 is logged as FLATTEN_DONE instead of FLATTEN_FAULT. Reproduced
(probe P4). No order is placed. Suggested fix: validate the mark
unconditionally before sizing.

## Verification of prior repairs

- T23-I01 cutoff advance on failed override: correct. Side note: a partial
  `close()` failure leaves the cutoff unadvanced; acceptable, no new alarm.
- T23-I02 max_notional sizing: correct. Caveat: the simulator checks notional
  against the decision bar's close, so Task 24 must pass that close as
  `mark_price`.
- T23-QB alarm during FLATTEN -> HALT: correct except the F23-1 timing.
- Strict-after reconciliation: correct by timestamp; coverage gap is F23-2.
- Acceptance criteria 1-6 hold under monotonic well-formed inputs; criterion
  1 can fail to engage under F23-1, criterion 4 holds only by timestamp.

## Verdict

FIX.
