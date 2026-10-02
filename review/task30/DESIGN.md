# Task 30 design: server runbook and code identity

**Status:** design note, before code. Author: Claude Opus 5.5
(`claude-opus-5-5`), 2026-10-02. Authorized by roadmap 2 answer Q-D (Tasks
26, 27, 28, 30, in that order); code waits until PR #38 (Task 28) merges.
Owner settings: D-7 (rented server, fixed IP), D-8 (OS credential store),
`review/deployment/OWNER_SETTINGS_2026-09-29.md`. Closes T24-03 (the
deployed commit is not checked).

## 1. What it delivers

- **A runbook** at `deploy/RUNBOOK.md` (not under the frozen
  `docs/`): rent and harden the server (owner), install Python and the app
  from a reviewed commit, create the app's own user account, store the
  credentials (D-8), start the service on boot, where the logs go, how to
  update, how to stop. Every command is copyable; the owner runs them. The
  AI never logs into the server and never sees its address or credentials.
- **Code identity check at start** (`REFUSE_START`, section 19 "config/hash
  mismatch"): the run refuses unless (a) every file under `src/aqt` (and the
  scripts and configs the run uses) matches the commit exactly — no
  modified, untracked or masked file, reusing `aqt.core.code_identity`
  `_require_clean`; and (b) that commit is on `main` (see Q30-2). The
  started event records the commit id and the code hash, so every log says
  which code produced it.
- **Service files** for the chosen system (Q30-1), e.g. a `systemd` unit:
  restart on crash only after the Task 27 refuse marker check, never as
  root, logs to the account directory.
- **The server's credential store** (T28-06, D-8) for the Telegram channel
  on the chosen system.

## 2. Acceptance (roadmap 2)

A dry run of the runbook on a clean machine (see Q30-4); a modified file
refuses start.

## 3. Decisions needed from the owner

- **Q30-1. The server's operating system.** (a) Ubuntu Linux LTS: the
  usual choice for small servers, about $5-6/month, `systemd` starts the
  app on boot; the credential store is a file only the app's account can
  read, or `systemd`'s encrypted credentials; or (b) Windows Server: the
  same credential store as your PC, but about twice the price (licence)
  and heavier to run.
- **Q30-2. Which commit may run.** (a) any commit on `main` (every commit
  there passed review and your "merge"); the update step fetches `main`
  from GitHub, the start check needs no network; or (b) only the one commit
  you named in a signed deployment record, so even a later merge does not
  run until you approve it for the server.
- **Q30-3. How updates happen.** (a) you run the update steps by hand when
  you decide (stop, fetch, check out the commit, start); or (b) the server
  updates itself to the newest `main` on a timer.
- **Q30-4. Where the dry run happens.** (a) on a fresh Ubuntu machine that
  GitHub starts for the project's checks (free, no server needed, repeated
  on every change of the runbook); or (b) on the rented server, once you
  have it.

## 4. Size and review

About 200 lines of code and tests plus the runbook. The start check is
protocol-enforcement logic (section 16): Astra review and the owner's
walkthrough before merge.
