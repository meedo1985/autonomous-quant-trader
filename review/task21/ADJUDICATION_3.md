# Task 21 third review adjudication

Review record: `REVIEW_3.md`, saved as returned. Reviewer: GPT-6 Astra
(`gpt-6-astra`, reasoning effort high, Codex CLI, read-only, session
`01a0ded9-d48a-7230-b246-a77eac57ced7`), run on 2026-09-26 at the owner's
request ("let astra review the task 21 fixes again"). Packet: `REVIEW_2.md`,
`ADJUDICATION_2.md`, the repair diff `94f0b9b..fb84c36` for code and tests, the
current governor modules and tests line-numbered, recorded checks and mutation
results (not rerun), `canonical.py` lines 607-785, and Constitution sections
14, 20 and 21. Verdict: **FIX**. The reviewer marked R-1, R-2 and R2-2 to R2-5
REPAIRED, and R2-1 NOT REPAIRED (see R3-1).

Reproduced on `fb84c36`:

| ID | Severity | Decision | Reproduction and action |
| --- | --- | --- | --- |
| R3-1 | BLOCKER | Observation accepted; not repaired in the governor, **deferred to Task 23** with reasons below | A buy redeemed at 00:01 and released at 00:06: a reduction with decision time 00:00 was refused `STALE_DECISION`, and with 00:06 it was refused `INVALID_DECISION_TIME`. The next possible reduction is at the 01:00 decision. |
| R3-2 | BLOCKER | Accepted | On a fresh governor, `decide` with naive `now=datetime(2026, 1, 5)` returned `UNKNOWN_SYMBOL`, and the next call with a UTC `now` raised `TypeError: can't compare offset-naive and offset-aware datetimes`. Repair: every call validates `now` as timezone-aware UTC before the clock stores or compares it; an invalid `now` raises `ValueError` and leaves the governor usable. |

## Why R3-1 is deferred rather than repaired here

- **Decisions happen only at hourly bar closes.** `protocol_v1.yaml`
  `scope.hourly_signal_evaluation` is `true`, and
  `scope.scheduled_decision_anchor_utc` is 00:00. The governor applies the frozen
  `rebalance` rule, which accepts only bar-aligned decision times, just as the
  backtester does. A strategy produces no new target between bars, so after the
  00:00 decision the next routine reduction is due at 01:00. That is the
  protocol's schedule, not a delay the governor adds.
- **Section 14's immediate reductions are safety actions:** "reduce capital,
  tighten limits, kill, HALT, FREEZE". Those are roadmap Task 23 (HALT,
  FLATTEN, FREEZE). Allowing off-schedule rebalances through the governor
  would weaken the section 20 binding to scheduled decisions.
- **Requirement carried to Task 23:** HALT and FLATTEN must be able to reduce
  exposure at once, at any time, including while a governor reservation is
  outstanding. They must do so without issuing an overlapping authorization
  that could conflict with an order in flight. This is recorded in
  `LOCAL_REPORT.md`, and the owner is told it is an open disagreement with the
  reviewer.

Also addressed from the review's notes: a test that a reservation on one
symbol does not block the other.

## Repair

- R3-2: `Governor._clock` validates `now` with `require_utc` before storing or
  comparing it, in `decide`, `redeem` and `release`. Test:
  `test_an_invalid_timestamp_leaves_the_governor_usable`. Removing the check
  fails it.
- Also added: `test_a_reservation_on_one_symbol_does_not_block_the_other`, and
  `test_after_a_late_release_the_next_reduction_is_at_the_next_bar`, which
  documents the R3-1 behaviour kept here.

Validation after repair, `.venv` Python 3.14.7: `pytest -q` 1402 passed, 4
skipped in 187.76s; `ruff check .` and `ruff format --check .` pass; `mypy src
scripts` no issues in 43 files; `lint-imports` 5 kept, 0 broken.

This repair has not been re-reviewed.
