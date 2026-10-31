# Codex Luna review of PR #80 (d18badf), unbuffered stdout for the paper service

Prompt: reproduced in section "Prompt" below. Reviewer metadata from the Codex CLI header (2026-10-31): model `gpt-5.6-luna`, provider openai, sandbox read-only, approval never, reasoning effort medium, Codex CLI v0.164.0, session id `01a1918a-af66-7eb3-aab1-9bdb2a92ea47`, 66,257 tokens. Reviewed the branch at `d18badf`. This is the different-model review. The owner's PR review is still required before merge.

Verdict: **ACCEPT WITH NOTES**: 0 BLOCKER, 0 NON-BLOCKING, 1 QUESTION (PR80-L-1). No gaps in numbering.

Disposition: **PR80-L-1 repaired** in the commit that adds this record. The unit-file comment now reads "Report lines then reach the journal when printed, without waiting for a later stdout flush." No finding is left unrepaired.

Noted for deploying (not a finding): `approved_code()` refuses any changed file under `/opt/aqt/app`, so this commit needs a new approval through the RUNBOOK route. The PR description already says to deploy through the usual approved-commit route.

## Report (verbatim)

What this change does: `PYTHONUNBUFFERED=1` is applied directly to the service’s Python process. It fixes delayed stdout delivery for the hourly `print()` report lines; no wrapper, `-u`, or additional unit is needed.

- `StreamSink` already calls `flush()`, so alerts and Telegram failure reporting remain immediate.
- Ledger/state/deployment-record writes are file operations and are unaffected.
- `approved_code()` rejects any changed file in `/opt/aqt/app`, so this commit must be newly approved. The RUNBOOK’s update path correctly installs the unit, runs `daemon-reload`, then performs approval/check.
- Restart behavior and log volume are unchanged. Only buffering and syscall timing change.
- The initial installer also copies the updated unit and reloads systemd.

**PR80-L-1 — QUESTION**  
**Place:** `deploy/aqt-paper.service:16`, commit description.

**Failure scenario:** “Journal timestamps are then the hour each report was written” is slightly too strong. Journal timestamps reflect when systemd receives the line, which should be near the `print()` call, not necessarily the report’s embedded `at` timestamp if computation or I/O is delayed.

**Minimal repair:** Say “journaled when the report line is emitted” or “without waiting for a later stdout flush.”

**Verdict: ACCEPT WITH NOTES**
## Prompt

# Review: PR #80, unbuffered stdout for the paper service

You are an independent different-model reviewer, read-only, not an authority. Write nothing. The repository is checked out on branch `deploy-unbuffered-stdout` (commit d18badf). Run `git diff main...HEAD` to see the change: one line, `Environment=PYTHONUNBUFFERED=1`, plus a comment, added to `deploy/aqt-paper.service`. The purpose is that hourly report lines reach the systemd journal when they are written, not at a later buffer flush.

Check, with evidence from the repo (`deploy/aqt-paper.service`, `deploy/RUNBOOK.md`, `scripts/run_forward_paper.py` and what it imports):
1. Does the change do what it claims for this ExecStart? Is anything else (another unit, a wrapper, a `-u` flag, explicit flush) needed or already present?
2. Can it break anything: alerts, Telegram, the state journal, the deployment-record / approved-code check (does the approved code identity cover the unit file, so the deploy route in the RUNBOOK needs a new approval?), restart behaviour, log volume?
3. Is the PR description accurate, including the deploy steps?

IDs: findings `PR80-L-n`, each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario, minimal repair. Verdict: ACCEPT, ACCEPT WITH NOTES, or FIX.
