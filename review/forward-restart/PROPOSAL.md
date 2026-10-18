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

## 2. Proposed change (revised after Sol's review FR-1..FR-4)

In `scripts/run_forward_paper.py` `main`, after the deployment check and the Telegram channel set-up, and before the first step:
- the service always waits until the next scheduled slot, the next hour plus `STEP_OFFSET` (:01);
- it logs one INFO line: "waiting until HH:01 UTC for the first step";
- it then enters the loop exactly as today.

There is no cut-off minute to justify. A start at 14:00:30 waits 30 s; a start at 14:01:10 waits until 15:01 (FR-1, FR-2). Every first step then runs at the same moment as every normal hourly step. So its freshness margin is the one every step already has, not a new one.

About 5 lines, plus a test. `--once` (a manual one-step run) is unchanged and still runs at once.

**A residual, not introduced by this change (FR-2).** `step()` takes `now` before fetching bars, and the lag check uses that time. A slow fetch is therefore measured as of before the fetch. This holds for every hourly step today; the change does not touch it. Reported here for completeness; not proposed now.

## 3. What changes and what does not, for the owner

**Rules that do not change:**
- the 5-minute lag rule;
- the alert-test, deployment, saved-state and health checks;
- the `LOOP_LAG` missed-hour report;
- the replay of missed hours.

**Outcomes that do change (FR-4):**
- The first step runs up to about an hour later.
- It can therefore fetch one more bar, cover one more hour, and report one more missed hour, later.
- The missed hours are still reported and replayed, never skipped.

**When the owner sees a refusal (FR-3):**
- **At once, before the wait:** the deployment approval check and the Telegram channel set-up (they run before it today).
- **Only after the wait (up to about an hour):** everything reached through `run_step`. That is the alert-test check, the saved-state and refuse-marker checks, the health checks and the startup reconciliation.
- **During the wait,** `systemctl status aqt-paper` shows **active (running)** and the log shows the "waiting until" line, although no step has run yet. So after a restart the owner checks the log after HH:03, not just the status.

**Against:** a late refusal (for example an overdue alert test) is seen up to an hour later than today. Mitigation, not proposed now: run the alert-test check before the wait, which is a larger change to protected start-up code.

**Not considered:** raising `max_loop_lag_s`. That weakens a safety limit, which is an owner value in the deployment settings.

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

- **Q-R1.** Approve building this change (at start, the service always waits for the next :01 step)?
