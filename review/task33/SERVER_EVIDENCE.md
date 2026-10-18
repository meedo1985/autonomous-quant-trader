# Task 33 on the owner's server, and the forward-paper stop of 2026-10-18

The owner ran the commands on the server and pasted the outputs into the Claude Code session. Claude Opus 5.5 (`claude-opus-5-5`) records them here; trimming is stated.

## 1. Dashboard install (RUNBOOK §9, commit `9bc84e3`)

```
root@aqt-server:~# ss -ltnH | sort > /tmp/ports.before
root@aqt-server:~# cd /tmp
root@aqt-server:/tmp# curl -fsSLO https://raw.githubusercontent.com/meedo1985/autonomous-quant-trader/9bc84e3ff2e67efa54db8d70a106e0f56ba08267/deploy/dashboard/install.sh
root@aqt-server:/tmp# sudo sh install.sh https://github.com/meedo1985/autonomous-quant-trader.git 9bc84e3ff2e67efa54db8d70a106e0f56ba08267
Created symlink '/etc/systemd/system/timers.target.wants/aqt-dashboard.timer' → '/etc/systemd/system/aqt-dashboard.timer'.
Installed the dashboard at 9bc84e3ff2e67efa54db8d70a106e0f56ba08267. Next: RUNBOOK.md section 9 checks.
root@aqt-server:/tmp# ss -ltnH | sort > /tmp/ports.after; diff /tmp/ports.before /tmp/ports.after && echo "ok: no port added"
ok: no port added
```

The sandbox check, full output (`journalctl -u aqt-dashboard@check.service -o cat | tail -16`):

```
Starting aqt-dashboard@check.service - aqt read-only dashboard (check)...
PASS can read /var/lib/aqt/data/forward/account-1/forward_reports.jsonl
PASS can read /var/lib/aqt/data/live/BTCUSDT-1h.jsonl
FAIL can read /var/lib/aqt/data/forward/account-1/incidents.jsonl
PASS can read /etc/aqt/deployments.jsonl
PASS cannot write in /var/lib/aqt
PASS cannot write in /etc/aqt
PASS cannot write in /opt
PASS cannot read /etc/aqt/telegram
PASS cannot open a socket (inet)
PASS cannot open a socket (Unix)
PASS io_uring_setup is refused
aqt-dashboard@check.service: Main process exited, code=exited, status=2/INVALIDARGUMENT
aqt-dashboard@check.service: Failed with result 'exit-code'.
Failed to start aqt-dashboard@check.service - aqt read-only dashboard (check).
```

**The one FAIL is explained by a missing file.** `ls -l /var/lib/aqt/data/forward/account-1/` (below) shows no `incidents.jsonl`: the app has never recorded an incident. The check treated an input not written yet as unreadable; the page itself shows it as "absent". This does **not** show that the dashboard can read the file once it exists. That stays unverified until the file exists and the check passes it (T33F-2). Repair on branch `task33-followup`: an absent input passes only if reading it finds no file **and** its directory lists without that name; any other read failure still fails (T33F-1). The other ten checks passed on the server, including "cannot read /etc/aqt/telegram". The check is to be run again after the repair is installed.

```
/var/lib/aqt/data/forward/account-1/:
total 1260
-rw-r--r-- 1 aqt aqt 214361 Oct 18 11:01 forward_cursor.jsonl
-rw-r--r-- 1 aqt aqt      0 Oct  5 01:01 forward_cursor.jsonl.lock
-rw-r--r-- 1 aqt aqt 298567 Oct 18 11:01 forward_reports.jsonl
-rw-r--r-- 1 aqt aqt 321525 Oct 18 11:01 operations.jsonl
-rw-r--r-- 1 aqt aqt      0 Oct  5 01:01 operations.jsonl.lock
-rw-r--r-- 1 aqt aqt 431866 Oct 18 10:01 state.jsonl
-rw-r--r-- 1 aqt aqt      0 Oct  5 01:01 state.jsonl.lock
```

## 2. Forward paper stopped at 11:01 UTC: weekly alert test overdue

Not caused by the dashboard; it happened about 1.5 h before the install. `systemctl status aqt-paper` showed `Active: failed (Result: exit-code) since Sun 2026-10-18 11:01:03 UTC`.

From `journalctl -u aqt-paper -n 40`, trimmed: the 37 report lines before it (steps from 2026-10-17 00:01 to 2026-10-18 10:01, all `final_mode` `RUNNING`, `refused` empty) are left out. The last lines, verbatim:

```
Oct 18 11:01:02 aqt-server python[1038]: {"at":"2026-10-18T10:00:00.000000Z","fields":{"decision":"REFUSE_START","reason":"alert channel test overdue: last acknowledged test sent 2026-10-11 10:46:15.513515+00:00"},"kind":"STARTUP","severity":"CRITICAL"}
Oct 18 11:01:03 aqt-server systemd[1]: aqt-paper.service: Main process exited, code=exited, status=2/INVALIDARGUMENT
Oct 18 11:01:03 aqt-server systemd[1]: aqt-paper.service: Failed with result 'exit-code'.
```

This is the designed refusal (D-2: a weekly acknowledged test). The owner reports that he sent the test and acknowledged it (RUNBOOK §4); no command output of that step was pasted, so it is recorded as the owner's report (T33F-4). The Telegram alerts quoted below show that messages are delivered. The next start passed the test check, since it refused only on lag.

## 3. Two refused restarts: the start check's 5-minute lag

At 12:38 UTC, after the test, the owner's restart refused. Telegram message, as pasted by the owner:

```
CRITICAL LOOP_LAG at 2026-10-18 12:38:41Z
missed_hours: 1
first_missed: 2026-10-18T10:00:00+00:00
last_missed: 2026-10-18T10:00:00+00:00
note: run late, as a replay would run them
CRITICAL STARTUP at 2026-10-18 10:00:00Z
decision: REFUSE_START
reason: health check at start: LOOP_LAG {'lag_ms': 2321110, 'max_lag_ms': 300000}
```

Cause, from the code: `scripts/run_forward_paper.py` runs a step immediately at start. `aqt.app.forward.observation` sets `scheduled` to the close of the newest bar, and `paper_loop`'s start check refuses a lag above `max_loop_lag_s = 300`. A start more than 5 minutes after the hour is therefore always refused. A retry at 13:05:20 missed by 20 seconds (`journalctl -u aqt-paper --since 13:00 | grep -v '"l02"'`):

```
Oct 18 13:05:22 aqt-server python[326490]: {"at":"2026-10-18T13:05:20.420605Z","fields":{"first_missed":"2026-10-18T10:00:00+00:00","last_missed":"2026-10-18T11:00:00+00:00","missed_hours":2,"note":"run late, as a replay would run them"},"kind":"LOOP_LAG","severity":"CRITICAL"}
Oct 18 13:05:23 aqt-server python[326490]: {"at":"2026-10-18T10:00:00.000000Z","fields":{"decision":"REFUSE_START","reason":"health check at start: LOOP_LAG {'lag_ms': 320420, 'max_lag_ms': 300000}"},"kind":"STARTUP","severity":"CRITICAL"}
```

The owner then scheduled the start for 14:01:30 UTC (`systemd-run --on-calendar="2026-10-18 14:01:30 UTC" /usr/bin/systemctl start aqt-paper`). The owner reported, in his words: "all is done and woeks as you tell". No status output was pasted for this start, so it is recorded as the owner's report and not verified here.

**Missed hours:** the quoted alerts name 10:00 and 11:00 as missed. By design (Task 29) every missed hour is reported as CRITICAL `LOOP_LAG` and run late, as a replay would run it, never skipped. That 10:00–13:00 were in fact all run is **not verified** here: no output of the 14:01:30 step was pasted (T33F-3). It can be checked with `grep -c '"2026-10-18T1[0-3]' /var/lib/aqt/data/forward/account-1/forward_reports.jsonl` or on the dashboard.

**Finding F-RESTART (open, for an owner decision):** a manual start in the middle of an hour always refuses. A proposal (the start waits until the next hour's step) would change protected forward-paper code, so it needs the owner's approval, review and §16.
