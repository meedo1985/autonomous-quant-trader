# Proposal: a read-only dashboard for the forward paper app (Task 33)

**Status:** PROPOSAL. Nothing here is authorized until the owner approves it.
**Author:** Claude Opus 5.5 (`claude-opus-5-5`), coding AI, advisory only (Constitution sections 15 and 16).
**Date:** 2026-10-18.
**Asked by the owner:** "draft the dashboard proposal" (2026-10-18). Today the owner sees the app only through Telegram alerts and server commands.

## 0. What it is, and what it is not

A page the owner opens in a browser to see how forward paper trading is doing. **It only reads.** It cannot start, stop, change or trade anything.

Out of scope, and not reachable by this task:
- any button or control;
- any write to the app's files;
- any order or trading key;
- any change to the strategy, the governor, the protocol or a frozen file;
- any research or D-19 decision;
- a public web address.

## 1. What the page shows

From the files the service already writes under `/var/lib/aqt/data/` (read-only):

| Panel | Source | Shows |
|---|---|---|
| Health | last line of `forward/account-1/forward_reports.jsonl`; last bar of `live/BTCUSDT-1h.jsonl` | Last step time, last bar time, mode (`final_mode`), refusals, health-breach hours. Red when the last bar is older than 2 hours. |
| Account | `final_balances` over time | Paper equity and position over time, as one line chart. |
| `L-02` progress | the `l02` field | Effective decisions so far out of 240, with the method (primary or fallback), and a rough date at today's pace. |
| Activity | `scheduled_decisions`, `orders_sent`, `governor_refusals`, `authorizations` | Counts per day. |
| Incidents | `forward/account-1/incidents.jsonl` | The last 20, newest first. |
| Code identity | `/etc/aqt/deployments.jsonl` | The approved commit the service runs. |

Every page states, in a banner: **"Paper trading, simulated money. This shows that the machinery runs, not that the strategy has an edge."**

## 2. How it works (the simplest design that is safe)

1. **A small script, `scripts/dashboard.py`.** Python standard library only, with no new dependency. It reads the files above and writes one self-contained HTML page with the charts drawn inline (SVG). It imports nothing from `execution`, `governor` or the paper loop, and an import-boundary contract enforces that.
2. **A systemd timer runs it every 15 minutes** as a separate account with read-only access to `/var/lib/aqt/data`. It writes only its own page (`/var/lib/aqt-dashboard/index.html`).
3. **The page is not on the internet.** The server's firewall stays as it is (SSH only). The owner sees the page through the SSH connection they already use: one line opens a private tunnel, then the owner opens `http://localhost:8080` in the browser. A tiny standard-library web server serves the page **on the server's localhost only**. I give the line as a one-click file on the Desktop, like the other commands.

**Why not a public web page with a password.** It would open a new port to the internet, need TLS certificates and a login, and become something to defend. The tunnel gives the same page with no new attack surface. The trade-off: the owner can't open it from a phone without SSH.

**Phone alternative (option B, can be added later):** a daily Telegram message with the same summary (equity, `L-02` progress, health). It reuses the existing bot, with no new port. Recommended as a follow-up if the owner wants it on the phone.

## 3. Relation to the roadmap

- It does not change the timeline of anything. It can be built while the D-19 calibration runs (about 2½ months), which needs no coding.
- It overlaps **Task 32** (monthly evidence report): both read the same files. The summary code is written once, and Task 32 can reuse it later.
- **Not §16 protected** in the drafter's reading: it reads only, and touches no execution, governor, protocol or statistics code. A different-model review (Sol) is still planned. The owner decides whether it needs the §16 PR review; the drafter recommends yes, because it runs on the trading server.

## 4. Size and acceptance

About 300–400 changed lines, one session, on its own branch and PR.

**Accept:**
- run on a copy of synthetic account files, it renders every panel;
- with a missing or empty file, it shows "no data" for that panel, never a crash and never invented numbers;
- with a bar older than 2 hours, the health panel is red;
- a test proves the script opens every file read-only and writes only its own page;
- the import contract forbids importing `execution` and `governor`;
- the runbook gains the install steps and the one-line tunnel;
- full validation is recorded, and Sol reviews it.

**Server steps for the owner (after merge):** install the timer and the localhost server (about 6 commands, from a Notepad file), then open the page through the tunnel.

## 5. Questions for the owner

- **Q-D1. Approve Task 33 as described?** Read-only page, via the SSH tunnel, built now while the calibration runs.
- **Q-D2. Also the daily Telegram summary (option B)?** Recommended: later, as its own small task.
- **Q-D3. §16 PR review for this task?** Recommended: yes.
