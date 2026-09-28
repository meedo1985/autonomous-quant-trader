# Task 23 Claude Opus 5.5 adversarial review

Date: 2026-09-28

Verdict: **CHANGES REQUIRED**

## Reviewer metadata

- Model: Claude Opus 5.5, `claude-opus-5-5`, as the runtime reported it.
- Session ID: the session did not expose one; none is invented here.
- Base: `edc3b39` (`origin/main` and merge-base).
- Head: `7aafb6d` (`origin/task23-safety` at the review fetch).
- The code was unchanged since `900bdc4`; later commits changed review records only.
- Review was read-only. No credentials, exchange calls, or file edits were used.

## BLOCKER

### T23-C1 — L-03 to FLATTEN lacks committed authority in this PR

**Where:** `src/aqt/execution/safety.py:16-17,114-115,119` and
`tests/unit/test_safety.py:426-439`.

**Evidence:**

- The code cites `review/deployment/OWNER_SETTINGS_2026-09-27.md`, which is not
  on this branch or `main`. It exists only on `task24-paper-loop`.
- `review/pre-deployment/LOSS_BOUNDS_ADOPTION_RECORD.md:14,29` records the owner
  adopting automatic HALT for L-03.
- The Task 23 deployment draft still says L-03 enters HALT, automatic FLATTEN
  triggers are open, and FLATTEN is entered by owner command or open triggers.
- The S-4 record does not authorize `(HALT, LOSS_STOP) -> FLATTEN`; that mapping
  can make an owner-commanded HALT sell after a false drawdown signal.

**Impact:** protected section 16 behavior differs from its committed authority,
and an autonomous sell from HALT has no committed owner choice behind it.

**Smallest safe correction:** bring the S-4 authority into this PR and align
the records, then obtain an explicit owner answer for `(HALT, LOSS_STOP)`; until
then map it to HALT.

### T23-C2 — HALT or FREEZE can use reconciliation older than a later incident

**Where:** `src/aqt/execution/safety.py:303-306,319,340,349`.

**Scenario A:** HALT at t0, passed reconciliation at t1, a new incident at t2,
then a HALT override accepts the t1 report and returns RUNNING.

**Scenario B:** FREEZE at t0, passed reconciliation at t1, reconciliation failure
at t2, then FREEZE exit accepts the t1 report and returns HALT.

**Evidence:** successful self-transitions restore the old `entered_at`; both
freshness checks compare only with that old timestamp.

**Impact:** trading may resume on evidence older than the latest incident,
contrary to the natural reading of sections 14 and 22.

**Smallest safe correction:** track the latest successfully recorded incident
time and require both recovery reports to be at least as new; add both scenarios
as regressions.

## NON-BLOCKING

### T23-C3 — FLATTEN can sell more than 50% in one step

**Where:** `src/aqt/execution/safety.py:405-412`.

With 0.155 BTC at 100 USDT and a 10 USDT minimum, half is below the minimum, so
the fallback sells the entire 0.155 BTC. The owner approved "at most 50% per
step"; the exception appeared only in the local report, not in the question.

**Correction:** obtain owner acceptance for a final-remainder exception or stop
at HALT and leave the remainder. Also replace "zero exposure" with "no sellable
exposure" wherever that is the actual behavior.

### T23-C4 — Incident-write failure is protected only in memory

**Where:** `src/aqt/execution/safety.py:282-287,353,487-495`.

If the incident ledger write fails, the controller stays in FREEZE but no
incident is durable. A restart can pass `startup_check`, and without a restart
the recovery path is undocumented.

**Correction:** document and test recording an `OWNER_HALT` incident after the
ledger recovers, and bind Task 24 to refuse restart after an audit-write failure
until the failure is durably recorded.

### T23-C5 — The HALT-override recovery incident can also fail

**Where:** `src/aqt/execution/safety.py:368-378`.

If incident closure succeeds, the transition alert fails, and the recovery
incident write also fails, HALT has no open incident and normal override remains
impossible. The recovery write error also replaces the alert error at the top
level.

**Correction:** test and document the `OWNER_HALT` recovery path after the
ledger returns; optionally preserve the original alert failure explicitly.

### T23-C6 — FLATTEN can retry zero fills indefinitely

**Where:** `src/aqt/execution/safety.py:440-453` and
`tests/unit/test_safety.py:201-208`.

A market beyond the 100 bps cap can expire every IOC unfilled while mode stays
FLATTEN. Only entry into FLATTEN is alerted.

**Correction:** Task 24 should alert after a bounded number of consecutive
zero-fill steps. No Task 23 code change is required.

## QUESTION

### T23-QA — Must reconciliation be strictly after the state entry or incident?

The code accepts equal timestamps because it checks `<`. The frozen text says
"after" for FREEZE recovery.

### T23-QB — Did the owner accept continuing FLATTEN through later alarms?

Task 23 proposal T23-01 keeps flattening on INCIDENT and LOSS_STOP alarms. The
reviewer found no committed owner acceptance.

## Examined with no finding

- No path was found that leaves `may_trade()` true after a protective trigger.
- Reconciliation rejects or raises for non-finite values, server errors,
  untracked open orders, and failed reports passed to `settle`.
- FLATTEN does not oversell or cross zero when the venue balance is valid.
- No frozen file, secret, strategy code, or restricted data was found.

## Missing evidence reported by Claude

- Claude could not run runtime probes for C2, C4, or C5 because its read-only
  environment denied temporary-file writes.
- Claude could not read PR CI through `gh` and did not run the full local gate.
- Claude did not independently verify the blob IDs in `REVIEW.md`.
- Claude read the S-4 record from `task24-paper-loop`, not this branch.

This report is an independent review, not authorization to trade, deploy, or
merge. Every item requires local adjudication and evidence.
