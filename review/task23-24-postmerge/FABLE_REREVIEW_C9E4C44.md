# PR #35 re-review of `c9e4c44` (Claude Fable 5.1)

Date: 2026-09-29. Requested by the owner ("let fable make a review").

- Reviewer model: Claude Fable 5.1 (`claude-fable-5-1`), read-only subagent.
  **Same provider family as the implementer**: a stand-in while Codex is at
  its limit. The different-family (Astra) re-review is still outstanding.
- Reviewed: `git diff 162e5ea c9e4c44` (commits `6450768`, `0e1e86e`,
  `4b0d72f`, `c9e4c44`), in a temporary worktree since removed.
- Reviewer's validation: `pytest -q` 1585 passed, 4 skipped, 1 failed
  (`test_statistical_metrics.py::test_convention_hash_matches_approved_document`,
  a hash mismatch the reviewer attributes to its worktree checkout with
  `core.autocrlf=true`; the file is not in the diff and no frozen file
  differs); ruff, format (101 files), mypy (53 files) clean.

## Prior findings

- **A2324-1: CORRECT.** Consecutive NOT_FOUND count per order, `delay`
  apart; unresolved without a check; known orders differ at once; matches
  `machine.py:361-363, 449-456` and T22-Q1; the loop passes the executor
  config at all three sites; a hidden fill still fails the balance check.
  Remaining difference: an exception from `sleep`/`clock` propagates out of
  `reconcile` (the loop's `_Clock` cannot raise; no finding).
- **A2324-2: CORRECT.** Latch intact; HALT stays HALT; FLATTEN stays
  FLATTEN; dust from RUNNING enters FLATTEN and ends at once in HALT. No
  committed test covers dust-from-RUNNING.
- **A2324-3: CORRECT.**
- **A2324-4: INCOMPLETE** — see F35-2.
- **A25R-4: CORRECT**, documentation gap F35-3. A filter rejection is also
  logged as FLATTEN_UNKNOWN and counted (observed, conservative).
- **A2324R-1: CORRECT.**
- **A2324R-2: INCOMPLETE** — see F35-1 and F35-4.

## New findings

### F35-1 — BLOCKER — an owner command at a skipped start hour is lost

`paper_loop.py:555-559`: `while moment < decision.report.at: moment += HOUR`
skips the start hour; owner commands apply only at `if decision_time in
owner`, so a HALT (or FLATTEN) keyed to `config.start` is never applied,
logged or refused, and the loop trades in RUNNING. Reproduced with the test
helpers, a restart with an unknown order and an owner HALT at start:

```
no-unknown final_mode HALT orders_sent 0 OWNER_HALT events 1
unknown-at-start final_mode RUNNING orders_sent 1 OWNER_HALT events 0
```

A regression introduced by the A2324R-2 repair; the owner's HALT must win
(§22, F24-1). Repair: apply (or log and refuse) owner commands whose hour is
skipped; add a test.

### F35-2 — NON-BLOCKING — a manifest that is valid JSON but not an object crashes before any logged refusal

`frozen_hash_problems` (`paper_loop.py:305/316/323`) and `:443-455`:
`frozen[key]` on a list or `None` raises `TypeError`, not caught; a
non-string `constitution_content_hash` would raise `AttributeError` (not
run); `report()` would fail on `.get` for a non-dict; no refuse marker.
Reproduced:

```
'{' -> REFUSED unreadable logged refusals: 2
'[]' -> RAISED TypeError list indices must be integers or slices, not str | log exists: False
'null' -> RAISED TypeError 'NoneType' object is not subscriptable | log exists: False
```

### F35-3 — NON-BLOCKING — FLATTEN_UNKNOWN omits the quantity and cap sent

The event records id, `held_before`, side, state, but not how much may have
been sold (unlike FLATTEN's `orig_qty`). Reproduced (fields printed).

### F35-4 — NON-BLOCKING — STARTUP START and a startup incident are stamped before the waiting check finished

`paper_loop.py:533` (`config.start`) and `startup_check`'s
`incidents.open(..., at)`. Reproduced: `STARTUP 2020-01-09T00:00:00Z START`
while the report is stamped 00:00:10. Consequence noted (not a defect): a
start at 00:00 that waits loses that day's scheduled decision.

## Tests versus claims

The new tests prove their claims. Uncovered: owner command at a skipped
start hour (F35-1), non-object manifest (F35-2), dust from RUNNING.

## Verdict

FIX.
