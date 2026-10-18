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
2. **One sandboxed generator, enforced by systemd (DB-1, DBR3-2).** A systemd timer runs it every 15 minutes as its own account, `aqt-dash`. `/var/lib/aqt` is mode `700` (`deploy/install.sh`), so read access is given by the unit, not by file modes or ACLs:
   - `AmbientCapabilities=CAP_DAC_READ_SEARCH` and `CapabilityBoundingSet=CAP_DAC_READ_SEARCH`: on paths visible to it, it can read files and search directories whatever their modes. It has no other privilege.
   - `ProtectSystem=strict`, `ProtectHome=yes` and `ReadWritePaths=/var/lib/aqt-dashboard`: the regular filesystem is read-only to it, except its own directory. `ProtectSystem=strict` does not cover `/dev`, `/proc` and `/sys`, so `PrivateDevices=yes`, `ProtectKernelTunables=yes`, `ProtectControlGroups=yes` and `ProtectProc=invisible` are added for those (DBR4-2).
   - `InaccessiblePaths=/etc/aqt/telegram`: the bot credential is hidden from it.
   - Sockets: `PrivateNetwork=yes`, `RestrictAddressFamilies=none`, `SystemCallArchitectures=native` (so no secondary syscall ABI bypasses the family restriction) and `SystemCallFilter=~io_uring_setup` (DBR4-1, DBR5-1, DBR6-2). One socket is inherited: by systemd default, stdout and stderr go to the journal over a Unix socket, which carries the generator's own log lines (DBR6-1). No other socket is passed in. The claim is limited to what the server checks test.
   - `NoNewPrivileges=yes`.

   The claims are narrow, and each one is tested on the server inside the same sandbox (section 4):
   - it can read the input files;
   - it cannot read the credential;
   - it cannot write under `/var/lib/aqt`, `/etc/aqt` or `/opt`;
   - `socket(2)` fails for inet and Unix sockets, and `io_uring_setup` is refused.

   Nothing beyond the tested boundaries is claimed. In particular, it is **not** "it can read only the input files". It writes the new page in `/var/lib/aqt-dashboard/staging/`, then renames it to `/var/lib/aqt-dashboard/page/index.html` (same filesystem, atomic). `/var/lib/aqt-dashboard` and `page/` are mode `755` and the page `644`, so the owner's login can traverse to it and copy it (DBR4-3). The page holds only what the panels show: it contains no credential and no file other than itself. The runbook steps check this on the installed server; a unit test alone cannot establish it.
3. **No web server, nothing on the internet (DB-3, DBR3-1).** The firewall stays SSH only, and the server runs no web server at all. The owner copies the finished page to the laptop with the SSH access they already have (`scp <server>:/var/lib/aqt-dashboard/page/index.html "%USERPROFILE%\Desktop\aqt-dashboard.html"`, an absolute local destination; DBR4-3), then double-clicks it. The command comes as a one-click Desktop file. This removes every serving question (bind address, directory listing, symbolic links, a tunnel) instead of guarding against each.

**Why not a web page.** A localhost web server plus an SSH tunnel works, but its review found edge cases in every round (DB-3, DBR-3, DBR2-1, DBR2-2, DBR3-1). A public page with a password would open a new port to the internet, need TLS certificates and a login, and become something to defend. Copying a file needs none of this. The trade-off: the page is a snapshot as of its "as of" time, refreshed by copying again, and the owner can't open it from a phone without SSH.

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
- the page is written in `staging/` and renamed into `page/`, so a copy never gets a partial page (tested);
- the "as of" time is shown, and a test with a stopped generator (an old page) shows the "as of" time unchanged;
- the `L-02` panel shows raw and effective counts, the method and the reason, and labels a fallback count;
- a tampered `deployments.jsonl` or `incidents.jsonl` (one byte changed) shows "unknown" or "invalid", never a commit or incidents;
- the labels "last reported step", "per reported step" and "latest approved commit" appear, with no equity line and no `L-02` date;
- the new import contract (section 2, item 1) is kept, and `lint-imports` fails if `aqt.dashboard` imports a forbidden package;
- on the server, run inside the generator's own sandbox (`systemd-run` with the unit's settings): it can read the input files, cannot write a test file under `/var/lib/aqt`, `/etc/aqt` or `/opt`, cannot read `/etc/aqt/telegram`, `socket(2)` fails for inet and Unix sockets, and `io_uring_setup` is refused. These checks are runbook steps, and their outputs are recorded;
- no listening port is added (`ss -ltn` before and after the install is the same);
- after the first generation, the owner's own Desktop file copies the page end to end, and the copy opens (recorded);
- the runbook gains the install steps and the one-line copy command;
- full validation is recorded, and Sol reviews the build.

**Server steps for the owner (after merge):** install the account and the timer, and run the sandbox checks (about 8 commands, from a Notepad file). Then copy the page with the Desktop file and double-click it.

## 5. Questions for the owner

- **Q-D1. Approve Task 33 as described?** Read-only page, copied to the laptop over SSH, built now while the calibration runs.
- **Q-D2. Also the daily Telegram summary (option B)?** Recommended: later, as its own small task.
- **Q-D3. §16 PR review for this task?** Recommended: yes.
