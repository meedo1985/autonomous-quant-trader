# Task 24 re-review of `e206675..20dcd42` (Claude Fable 5.1)

Date: 2026-09-28

- Reviewer model: Claude Fable 5.1 (`claude-fable-5-1`), read-only Claude
  Code subagent; owner-chosen substitute for the exact GPT-6 Astra review
  (owner "ok" to the recommended third review).
- Reviewed commit: `20dcd42`, diff `e206675..20dcd42`.
- Tests: `-k "loss_stop or halt or flatten"` on `test_safety.py` and
  `test_paper_loop.py`, 37 passed; the new test fails on `2dc79ae` source at
  `assert len(stops) == 1`. Probes in temp, deleted; tree clean.

## Per finding

- **F24R-1: CORRECT.** LOSS_STOP fires when breached, latch armed, held >=
  min_qty, mode not FREEZE; RUNNING -> FLATTEN is the only selling path;
  HALT -> HALT and FLATTEN -> FLATTEN with incident and CRITICAL; all
  entries exist, so the trigger cannot raise. Probe (owner FLATTEN at each
  hour 01-13 17:00-22:00 of `_crash_series`): breach first seen during owner
  FLATTEN gives one `FLATTEN->FLATTEN LOSS_STOP CRITICAL`, FLATTEN_DONE ends
  in HALT, latch disarmed, no duplicate; no breach above the line; same-hour
  and stop-first cases give exactly one LOSS_STOP; no two orders share a
  timestamp. The self-transition does not reset `_last_flatten_decision`, so
  one step per bar holds. The new test proves its claim.
- **F24R-2: CORRECT.** Docstring now owner-set.
- **F24R-3: CORRECT.** Adjudication sentence corrected; open decisions in
  T24-08.

## New findings

### F24S-1 — NON-BLOCKING — breach during FREEZE never alerted; draft silent

`paper_loop.py:586` vs `DEPLOYMENT_PROTOCOL_v1_DRAFT.md:172` ("Must alert
CRITICAL: … any `L-03` breach"). In a paper run FREEZE lasts to the end, so
a later crash is never reported. Mitigated: FREEZE already raised CRITICAL
and an incident; exclusion disclosed in ADJUDICATION and LOCAL_REPORT. Fix:
note it in draft section 5 or the section 6 FREEZE row. Not reproduced
(follows from the condition).

### F24S-2 — NON-BLOCKING — no test asserts the FLATTEN -> FLATTEN alert

Only the HALT case is tested; `test_the_loss_stop_never_overrides_an_owner_halt`
exercises the FLATTEN breach but does not assert it. Fix: one assertion.
Reproduced via the probe above.

Docstring note (not a finding): `safety.py` module docstring's "keeps
FLATTEN going if it fires again there" does not describe a first firing
during an owner FLATTEN; one-line touch-up.

## Checked, no issue

Dust holding: `held >= min_qty` can hide a breach only in a band of about
1% (FLATTEN cap) or 15 bps plus fees in an almost all-USDT account; in
RUNNING the latch stays armed; guard predates the diff; not reproduced.
Health-breach hours match F24-4. No path sells except from RUNNING; the
owner's HALT is never left by the stop. Draft section 6 and T24-08
consistent. Frozen artifacts unchanged.

## Verdict

ACCEPT.
