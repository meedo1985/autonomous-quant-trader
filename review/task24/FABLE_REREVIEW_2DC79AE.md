# Task 24 re-review of `646d514..2dc79ae` (Claude Fable 5.1)

Date: 2026-09-28

- Reviewer model: Claude Fable 5.1 (`claude-fable-5-1`), a read-only Claude
  Code subagent, requested by the owner ("yes run the Fable re-review");
  owner-chosen substitute for the exact GPT-6 Astra review.
- Reviewed commit: `2dc79ae`, diff `646d514..2dc79ae`.
- Tests: `test_safety.py` + `test_paper_loop.py`, 81 passed in 456.30s. The
  three new tests were run against exported `646d514` source and all fail
  there. Probe files deleted; working tree clean.

## Per finding

- **F24-1: CORRECT**, but introduces F24R-1. Probe: owner HALT 2020-01-10T05:00
  then crash: only `RUNNING -> HALT OWNER_HALT`, one order in the run, final
  BTC 1.07636 (old code: `HALT -> FLATTEN LOSS_STOP`, 11 orders, 0.00106).
  In `run_paper` HALT is reached only by OWNER_HALT or FLATTEN_DONE
  (INCIDENT never fired; FREEZE terminal); the owner's option text covers
  every HALT, no separate question needed. Tests correct.
- **F24-2: CORRECT.** Pinned value equals the working-tree file, the
  committed blob and the sidecar; `.gitattributes` has
  `/FROZEN_HASHES.json -text`, so LF/CRLF checkouts (incl. CI) keep bytes;
  script and tests unaffected; Constitution check now anchored by the pin.
- **F24-3: CORRECT as disclosure** (T24-08); small gap in F24R-3.
- **F24-4: owner-decided, consistent.** The breach `continue` precedes the
  peak update and stop check, so the next good hour re-checks.

## New findings

### F24R-1 — BLOCKER — after an owner HALT a loss-stop breach is silent

`paper_loop.py:580-590` fires LOSS_STOP only in RUNNING, so the
`(HALT, LOSS_STOP) -> HALT` entry is unreachable. `OWNER_ANSWERS_2026-09-28.md`
Effect says "an incident is still opened"; deployment draft section 5 says
"Must alert CRITICAL: … any `L-03` breach [ADOPTED L-03]"; the owner's answer
ends "You decide what to do with the coins" but nothing tells him. Reproduced:
owner HALT on 01-10 then crash — one CRITICAL event (the OWNER_HALT), no
"below" event, one incident; final equity ~6,665 vs peak ~10,000 (33% loss)
unalerted. Regression vs `646d514`. Related, pre-existing: a breach first
seen during FLATTEN was unalerted. Suggested: fire whenever the latch is
armed in any mode but FREEZE; add a test; or correct the Effect record.

### F24R-2 — NON-BLOCKING — stale docstring

`paper_loop.py:706-708`: `ZERO_FILL_ALERT_AFTER` still says "A proposal, not
an owner-set value." The owner set it (T24-Q1).

### F24R-3 — NON-BLOCKING — adjudication describes unreachable behaviour

`ADJUDICATION.md` F24-1 row says "if the owner later resumes RUNNING while
still below the line, the stop fires then" — impossible in `run_paper`
(commands allow only OWNER_HALT/OWNER_FLATTEN; `peak`/`stop_armed` not
persisted). For a future continuing account: if an owner HALT pre-empted the
stop, an override would sell everything at once; if the stop already fired,
the latch stays disarmed until equity regains 80% of the old peak, which an
all-USDT account may never do, leaving no L-03 stop. Not reproduced
(unreachable). Suggested: correct the sentence; add override and latch rules
to T24-08 as an open decision.

## Checked, no issue

`safety.py` module docstring consistent; deployment draft section 6 does not
say from which mode (optional clarification); F24-4 matches the owner's
option; frozen artifacts unchanged.

## Verdict

FIX.
