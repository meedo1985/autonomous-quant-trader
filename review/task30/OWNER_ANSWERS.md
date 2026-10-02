# Owner answers to the Task 30 design questions

Date: 2026-10-02. Asked by Claude Opus 5.5 from `DESIGN.md` section 3 in a
Claude Code session; question and option texts as asked (the order and
recommendation of Q30-2's options differ from the design note's first
draft), answers the owner's selections.

- **Q30-1.** "Which operating system should the rented server run?" —
  **"Ubuntu Linux (Recommended)"**: "The usual choice for small servers,
  about $5-6/month. The app starts on boot by itself, and your keys sit in a
  file only the app's own account can read."
- **Q30-2.** "Which version of the code may run on the server?" — **"Only
  what you approve (Recommended)"**: "Only the one commit you name in a
  signed deployment record. A later merge doesn't run on the server until
  you approve it there too. Safer when real money is involved."
- **Q30-3.** "How should the server be updated to new code?" — **"You run
  the steps (Recommended)"**: "When you decide, you run the update steps
  from the guide: stop, fetch, switch to the approved commit, start. Nothing
  changes on the server unless you choose to."
- **Q30-4.** "Where should the guide's test run on a clean machine
  happen?" — **"GitHub test machine (Recommended)"**: "A fresh Ubuntu
  machine that GitHub starts for the project's checks. Free, no server
  needed, and repeated every time the guide changes."

## Effect on Task 30

The server runs Ubuntu LTS under `systemd`, as its own non-root account.
The start check refuses unless the checkout is unmodified and its commit is
the one named in the owner's signed deployment record (and on `main`).
Updates are manual runbook steps. The runbook's dry run is a CI job on a
fresh GitHub Ubuntu runner. The Telegram credential on Ubuntu is a file
readable only by the app's account (D-8's "server's equivalent"; T28-06).
None of this rents a server, sets an IP, or authorizes keys or trading.
