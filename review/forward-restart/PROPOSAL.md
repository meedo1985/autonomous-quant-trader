# Proposal: forward paper waits for the next hour instead of refusing a late start (F-RESTART)

**Status:** PROPOSAL. Nothing here is authorized until the owner approves it.
**Author:** Claude Opus 5.5 (`claude-opus-5-5`), coding AI, advisory only (Constitution sections 15 and 16).
**Date:** 2026-10-18. **Asked by the owner:** "Restart-fix proposal (Recommended)", chosen from the options for today.
**Evidence:** `review/task33/SERVER_EVIDENCE.md` section 3, finding F-RESTART.

## 1. The problem, as it happened

On 2026-10-18, forward paper had stopped (weekly alert test overdue). After the test, two manual restarts were refused:
- at 12:38:41, with a lag of 2,321 s;
- at 13:05:20, with a lag of 320 s, against a limit of 300 s.

A start scheduled for 14:01:30 worked.

**Cause, in the code:**
- `scripts/run_forward_paper.py` runs a step **immediately** at start, then every hour at :01 (`STEP_OFFSET`).
- That step's start health check measures lag from the close of the newest bar (`aqt.app.forward.observation`, `scheduled = end`), and refuses above `max_loop_lag_s = 300` (`configs/forward_paper.example.toml`).
- A refusal exits with code 2, which systemd does not retry (`RestartPreventExitStatus=2`).

So a start that fetches bars, finds a pending window and comes more than 5 minutes after the hour is refused. The owner must then start again inside the first 5 minutes of an hour.

## 2. Proposed change (the smallest one)

In `scripts/run_forward_paper.py` `main`, before the first step:
- if the time now is later than **:04** past the hour (`STEP_OFFSET` plus a 3-minute margin, which stays below the 5-minute limit);
- then log one INFO line, "waiting until HH:01 so the start check sees a fresh bar", and sleep until the next hour plus `STEP_OFFSET`;
- then enter the loop exactly as today.

About 5 lines, plus a test.

**What does not change:**
- the 5-minute lag rule and every other start check (alert test, deployment approval, saved state, health);
- the missed-hour `LOOP_LAG` report;
- the replay of missed hours;
- `--once` (a manual one-step run).

The wait happens **before** any check, so a start that should be refused for another reason is still refused, only up to an hour later.

## 3. Trade-offs, for the owner

- **For:** a restart works at any minute; nobody has to time it. An outage costs at most one more waiting hour, and those hours are reported and replayed as today.
- **Against:**
  - A refusal for another reason (for example an overdue alert test) shows up only after the wait, up to an hour later, instead of at once.
  - Mitigation, not proposed now: run the alert-test and deployment checks before waiting. That is a larger change to protected start-up code.
- **Not considered:** raising `max_loop_lag_s`. That weakens a safety limit, which is an owner value in the deployment settings.

## 4. Governance

- `scripts/run_forward_paper.py` is forward-paper start-up code that the owner reviewed under §16 (Task 29). The change therefore follows the full path:
  - this proposal;
  - Sol's review of the proposal;
  - the owner's approval;
  - the build, with tests and Sol's review;
  - the owner's §16 PR review;
  - a server update by the owner (RUNBOOK §7).
- It changes no frozen file, protocol, threshold or statistic.

## 5. Question for the owner

- **Q-R1.** Approve building this change (the start waits until :01 of the next hour when it is later than :04)?
