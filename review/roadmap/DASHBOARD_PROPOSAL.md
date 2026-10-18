# Proposal: a read-only dashboard for the forward paper app (Task 33)

**Status:** PROPOSAL. Nothing here is authorized until the owner approves it.
**Author:** Claude Opus 5.5 (`claude-opus-5-5`), coding AI, advisory only (Constitution sections 15 and 16).
**Date:** 2026-10-18. Revised the same day after Sol's review (`DASHBOARD_SOL_REVIEW_807022F.md`, DB-1..DB-9).
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
| Health | last complete line of `forward/account-1/forward_reports.jsonl`; last bar of `live/BTCUSDT-1h.jsonl` | Labelled **"last reported step"**: its time, `final_mode`, refusals, health-breach hours. Separately, the age of the last report and the age of the last bar. **Red** when the last report is older than 2 hours, when the bar is older than 2 hours, or when the last step reported a refusal. A recent bar alone never shows the service as running (DB-5). |
| Balances | `final_balances` per report | BTC and USDT balances with their units, on **separate** scales. No equity line in this task: the reports hold no time-matched price, and the page does not invent one (DB-6). |
| `L-02` status | the `l02` field | `raw_decisions`, `effective_decisions`, `method` and, when unavailable, `reason`, against the target 240. When the method is the fallback, the panel says so: the fallback count is not the same quantity as the primary one (`LOSS_BOUND_DEFAULTS.md`), so the page doesn't present it as interchangeable (DBR-1). **No completion date** (DB-7). Labelled a waiting condition, not evidence of an edge. |
| Activity | `scheduled_decisions`, `orders_sent`, `governor_refusals`, `authorizations` | Labelled **"per reported step"**: one step can cover hours across days, so no per-day counts (DB-8). |
| Incidents | `forward/account-1/incidents.jsonl` | The last 20, newest first, only after the whole hash chain verifies with `aqt.core.ledger.verify_ledger`; otherwise "invalid", with the reason (DBR-4). |
| Code identity | `/etc/aqt/deployments.jsonl` | Labelled **"latest approved commit"**, shown only when the whole ledger verifies (`aqt.core.ledger.verify_ledger`) and its final record is an approval; otherwise "unknown" (DBR-4). Not "running commit": the record does not prove what the process runs (DB-8). |

Each panel shows the time of the data it shows. For each input file it distinguishes four states: absent, pending (an incomplete last line, being written), invalid or unreadable (with the reason), and valid. Only complete, newline-terminated records are read (DB-4).

Every page states, in a banner: **"Paper trading, simulated money. This shows the app's recorded activity, not that the strategy has an edge."**

The top of the page shows **"as of <generation time>"**, and every age and health colour is computed at that time. The page is static, so if the generator stops, the page stops updating. The owner checks the "as of" time; a page more than 30 minutes old means the dashboard itself is not updating, whatever its colours say (DBR-2).

## 2. How it works (the simplest design that is safe)

1. **A small module, `src/aqt/dashboard.py`, with a thin `scripts/dashboard.py` entry point.** Python standard library only, with no new dependency. It reads the files above and writes one self-contained HTML page with the charts drawn inline (SVG). The code sits inside the `aqt` package because import-linter contracts only cover `aqt.*` modules, and a new `forbidden` contract stops `aqt.dashboard` from importing `aqt.execution`, `aqt.governor`, `aqt.app`, `aqt.research`, `aqt.models` or `aqt.lockbox_eval`. The script holds no logic.
   Every text that comes from a file is HTML-escaped, in text and in attributes. Plotted numbers are checked to be finite before drawing. The page carries a strict content-security policy (no scripts) (DB-2).
2. **Two accounts, least privilege (DB-1).** `/var/lib/aqt` is mode `700` (`deploy/install.sh`), so read access is granted explicitly, not assumed:
   - **`aqt-dash`, the generator**, run by a systemd timer every 15 minutes. It has read access only to the input files above, and traverse access to their directories (POSIX ACLs, with default ACLs so new files stay readable). It has no write access to app data, code, `/etc/aqt` or service controls. It writes the new page in `/var/lib/aqt-dashboard/staging/`, outside the served directory but on the same filesystem, then renames it to `/var/lib/aqt-dashboard/www/index.html` atomically. It writes nowhere else. The served directory never holds anything but the finished page, so no partial file and no directory listing can be served (DBR-3).
   - **`aqt-web`, the web server**: `python3 -m http.server --bind 127.0.0.1 8080 --directory /var/lib/aqt-dashboard/www`, as its own unit. The unit has `ConditionPathExists=/var/lib/aqt-dashboard/www/index.html`, and the install publishes a first page before enabling it, so the server never starts on an empty directory and never lists it (DBR2-1). The unit also has `ProtectSystem=strict`, `ProtectHome=yes` and `InaccessiblePaths=/var/lib/aqt /etc/aqt /opt/aqt /opt/aqt-d19`. The claim is narrow: `aqt-web` cannot read the AQT data, the deployment record or the code. It is not "it can read only one directory" (DBR2-2).
   - The served directory holds one regular file, `index.html`, written by the generator. It never holds a symbolic link, because `http.server` would follow one out of the directory (DBR2-2).
   - The runbook steps check these permissions on the installed server (for example, that `aqt-dash` cannot write a test file under `/var/lib/aqt`). A unit test alone cannot establish them.
3. **The page is not on the internet (DB-3).** The firewall stays SSH only. The web server binds `127.0.0.1` explicitly, and the bind is checked, because `http.server` listens on all interfaces by default. The owner opens a tunnel that is also bound to loopback on the laptop (`ssh -L 127.0.0.1:8080:127.0.0.1:8080 ...`), then opens `http://localhost:8080`. The line comes as a one-click Desktop file.

**What the tunnel does and does not add.** It adds no port reachable from the internet. While the tunnel is open, programs on the owner's laptop and local users on the server can read the page. That is acceptable for a read-only page about paper money. It is not "no attack surface".

**Why not a public web page with a password.** It would open a new port to the internet, need TLS certificates and a login, and become something to defend. The trade-off: the owner can't open it from a phone without SSH.

**Phone alternative (option B, can be added later):** a daily Telegram message with the same summary (balances, `L-02` status, health). It reuses the existing bot, with no new port. Recommended as a follow-up if the owner wants it on the phone.

## 3. Relation to the roadmap

- It does not change the timeline of anything. It can be built while the D-19 calibration runs (about 2½ months), which needs no coding.
- It reads some of the files **Task 32** (monthly evidence report) will read. Whether Task 32 can reuse any of its code is decided when Task 32's requirements are set, not promised here (DB-9).
- **Not §16 protected** in the drafter's reading, and Sol agrees (DB-9): a presentation-only page is outside the components §16 lists. This holds only while the implementation stays outside them: it must not import or change execution, governor, protocol or statistics code. The build gets its own Sol review. The owner decides whether it needs the §16 PR review; the drafter recommends yes, because it runs on the trading server.

## 4. Size and acceptance

Its own branch and PR. A rough size of one session is an estimate, not a condition (DB-9).

**Accept:**
- run on a copy of synthetic account files, it renders every panel;
- for each input file, the four states (absent, pending partial line, invalid or unreadable, valid) are shown distinctly, never a crash and never invented numbers; tests cover a concurrent append and a corrupt record;
- the health panel is red for a stale report, a stale bar and a reported refusal, each tested;
- a synthetic malicious string (`<script>`, a quote inside an attribute) in incidents and refusals appears escaped and inert;
- the page is staged outside the served directory and renamed into it; on the server, `find /var/lib/aqt-dashboard/www -mindepth 1 ! -name index.html` prints nothing and `index.html` is a regular file (no other file, no symbolic link), so no other file is served; the web unit does not start before the first page exists (startup order tested);
- the "as of" time is shown, and a test with a stopped generator (an old page) shows the "as of" time unchanged;
- the `L-02` panel shows raw and effective counts, the method and the reason, and labels a fallback count;
- a tampered `deployments.jsonl` or `incidents.jsonl` (one byte changed) shows "unknown" or "invalid", never a commit or incidents;
- the labels "last reported step", "per reported step" and "latest approved commit" appear, with no equity line and no `L-02` date;
- the new import contract (section 2, item 1) is kept, and `lint-imports` fails if `aqt.dashboard` imports a forbidden package;
- on the server: the web server is not reachable on the external interface, `aqt-dash` cannot write under `/var/lib/aqt`, and `aqt-web` cannot read `/var/lib/aqt`, `/etc/aqt` or the code. These checks are runbook steps, and their outputs are recorded;
- the runbook gains the install steps and the one-line tunnel;
- full validation is recorded, and Sol reviews the build.

**Server steps for the owner (after merge):** install the two accounts, the timer and the localhost server, and run the permission checks (about 10 commands, from a Notepad file). Then open the page through the tunnel.

## 5. Questions for the owner

- **Q-D1. Approve Task 33 as described?** Read-only page, via the SSH tunnel, built now while the calibration runs.
- **Q-D2. Also the daily Telegram summary (option B)?** Recommended: later, as its own small task.
- **Q-D3. §16 PR review for this task?** Recommended: yes.
