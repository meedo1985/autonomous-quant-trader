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

**The one FAIL is explained by a missing file.** `ls -l /var/lib/aqt/data/forward/account-1/` (below) shows no `incidents.jsonl` at that time (T33FR3-2: absent now; the listing does not show the history). The check treated an absent input as unreadable; the page itself shows it as "absent". This does **not** show that the dashboard can read the file once it exists. That stays unverified until the file exists and the check passes it (T33F-2). Repair on branch `task33-followup`: an absent input passes only if reading it finds no file **and** its directory lists without that name; any other read failure still fails (T33F-1). The other ten checks passed on the server, including "cannot read /etc/aqt/telegram". The check is to be run again after the repair is installed.

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

The failure is stamped 11:01:03 UTC. The install output carries no timestamp, so no order between the two is claimed (T33FR5-1). `systemctl status aqt-paper` showed `Active: failed (Result: exit-code) since Sun 2026-10-18 11:01:03 UTC`.

From `journalctl -u aqt-paper -n 40`, trimmed: the 37 report lines before it are left out; they are in the owner's paste in the session and are not described here (T33FR3-2). The last lines, verbatim:

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

Cause, from the code: `scripts/run_forward_paper.py` runs a step immediately at start. `aqt.app.forward.observation` sets `scheduled` to the close of the newest bar, and `paper_loop`'s start check refuses a lag above `max_loop_lag_s = 300`. So a start is refused when its first step fetches bars, finds a pending window, and the check sees more than 300 s of lag (T33FR6-1). A retry at 13:05:20 missed by 20 seconds (`journalctl -u aqt-paper --since 13:00 | grep -v '"l02"'`):

```
Oct 18 13:05:22 aqt-server python[326490]: {"at":"2026-10-18T13:05:20.420605Z","fields":{"first_missed":"2026-10-18T10:00:00+00:00","last_missed":"2026-10-18T11:00:00+00:00","missed_hours":2,"note":"run late, as a replay would run them"},"kind":"LOOP_LAG","severity":"CRITICAL"}
Oct 18 13:05:23 aqt-server python[326490]: {"at":"2026-10-18T10:00:00.000000Z","fields":{"decision":"REFUSE_START","reason":"health check at start: LOOP_LAG {'lag_ms': 320420, 'max_lag_ms': 300000}"},"kind":"STARTUP","severity":"CRITICAL"}
```

The owner then scheduled the start for 14:01:30 UTC:

```
root@aqt-server:/tmp# sudo systemd-run --on-calendar="2026-10-18 14:01:30 UTC" /usr/bin/systemctl start aqt-paper
Running timer as unit: run-p326906-i328322.timer
Will run service as unit: run-p326906-i328322.service
root@aqt-server:/tmp# systemctl status aqt-paper --no-pager | head -3
● aqt-paper.service - aqt forward paper trading
     Loaded: loaded (/etc/systemd/system/aqt-paper.service; enabled; preset: enabled)
     Active: active (running) since Sun 2026-10-18 14:01:43 UTC; 1min 44s ago
```

**Missed hours: the four-hour window completed without refusal (T33F-3, T33FR-1, T33FR2-1, T33FR4-1).** The owner ran three read-only checks. Each one locates its records by time, not by position.

**The step cursor**, verbatim:

```
root@aqt-server:/tmp# sudo grep '2026-10-18T1[0-4]' /var/lib/aqt/data/forward/account-1/forward_cursor.jsonl | cut -c1-400
{"entry_hash":"4b909f7f2460e4932ef48fd2ed65feaa19cc17d08abaca385725a34024f082ef","payload":{"end":"2026-10-18T10:00:00+00:00","start":"2026-10-18T09:00:00+00:00","step":"START"},"previous_hash":"84b3155ec7cf71f1fbc781557eb6afe260c6ae881d712fa614783725e55582c9","record_type":"aqt.app.forward_cursor.v1","recorded_at_utc":"2026-10-18T10:01:00Z","sequence":642}
{"entry_hash":"d96a8a450595669e70ddfb87a8f7e973f217b837bb72ae531ee5824fe055b5af","payload":{"refused":false,"step":"END"},"previous_hash":"4b909f7f2460e4932ef48fd2ed65feaa19cc17d08abaca385725a34024f082ef","record_type":"aqt.app.forward_cursor.v1","recorded_at_utc":"2026-10-18T10:01:00Z","sequence":643}
{"entry_hash":"c49b1948f9d128eb5173002ec84c8d17b2488368af4a642bb5e2c2d9c6dcd40c","payload":{"end":"2026-10-18T11:00:00+00:00","start":"2026-10-18T10:00:00+00:00","step":"START"},"previous_hash":"d96a8a450595669e70ddfb87a8f7e973f217b837bb72ae531ee5824fe055b5af","record_type":"aqt.app.forward_cursor.v1","recorded_at_utc":"2026-10-18T11:01:00Z","sequence":644}
{"entry_hash":"df619dd7672833ce34502e714d276970d72f8865070c3814f2ce2030ea615483","payload":{"refused":true,"step":"END"},"previous_hash":"c49b1948f9d128eb5173002ec84c8d17b2488368af4a642bb5e2c2d9c6dcd40c","record_type":"aqt.app.forward_cursor.v1","recorded_at_utc":"2026-10-18T11:01:00Z","sequence":645}
{"entry_hash":"c83d4a59a6a51555afe0e821cd7168b02c527e3687faaadc73801a51cc685385","payload":{"end":"2026-10-18T12:00:00+00:00","start":"2026-10-18T10:00:00+00:00","step":"START"},"previous_hash":"df619dd7672833ce34502e714d276970d72f8865070c3814f2ce2030ea615483","record_type":"aqt.app.forward_cursor.v1","recorded_at_utc":"2026-10-18T12:38:41Z","sequence":646}
{"entry_hash":"95db1d129ed0a90a877497f1c7e26c745c39bc58c40fba73ca730cbcf21a84b4","payload":{"refused":true,"step":"END"},"previous_hash":"c83d4a59a6a51555afe0e821cd7168b02c527e3687faaadc73801a51cc685385","record_type":"aqt.app.forward_cursor.v1","recorded_at_utc":"2026-10-18T12:38:41Z","sequence":647}
{"entry_hash":"e316c1cce688784bac6aaf9cc78f2e4261490c34736f4626a0adbfb300c5f2ee","payload":{"end":"2026-10-18T13:00:00+00:00","start":"2026-10-18T10:00:00+00:00","step":"START"},"previous_hash":"95db1d129ed0a90a877497f1c7e26c745c39bc58c40fba73ca730cbcf21a84b4","record_type":"aqt.app.forward_cursor.v1","recorded_at_utc":"2026-10-18T13:05:20Z","sequence":648}
{"entry_hash":"7cca760e2cfcda06d98a1df335e84540fad6a48599623d2a8e3f0987b7d7fb4a","payload":{"refused":true,"step":"END"},"previous_hash":"e316c1cce688784bac6aaf9cc78f2e4261490c34736f4626a0adbfb300c5f2ee","record_type":"aqt.app.forward_cursor.v1","recorded_at_utc":"2026-10-18T13:05:20Z","sequence":649}
{"entry_hash":"3cf979a20e3c5e46623c430ef52dd53a11ec64e4d3d315e10d3a7c6f3a0b70fb","payload":{"end":"2026-10-18T14:00:00+00:00","start":"2026-10-18T10:00:00+00:00","step":"START"},"previous_hash":"7cca760e2cfcda06d98a1df335e84540fad6a48599623d2a8e3f0987b7d7fb4a","record_type":"aqt.app.forward_cursor.v1","recorded_at_utc":"2026-10-18T14:01:44Z","sequence":650}
{"entry_hash":"9bd9e5d378c8f9f728a8e2bd5632882ce163e0e42e1aa4d39eb2893781cd4583","payload":{"refused":false,"step":"END"},"previous_hash":"3cf979a20e3c5e46623c430ef52dd53a11ec64e4d3d315e10d3a7c6f3a0b70fb","record_type":"aqt.app.forward_cursor.v1","recorded_at_utc":"2026-10-18T14:01:44Z","sequence":651}
```

**The reports**, verbatim:

```
root@aqt-server:/tmp# sudo grep '"at": "2026-10-18T1[3-5]' /var/lib/aqt/data/forward/account-1/forward_reports.jsonl | grep -o '"at": "[^"]*"\|"hours": [0-9]*\|"refused": \[[^]]*\]\|"final_mode": "[A-Z]*"\|"scheduled_decisions": [0-9]*'
"at": "2026-10-18T13:05:20.420605+00:00"
"final_mode": "REFUSED"
"hours": 3
"refused": ["health check at start: LOOP_LAG {'lag_ms': 320420, 'max_lag_ms': 300000}"]
"scheduled_decisions": 0
"at": "2026-10-18T14:01:44.190723+00:00"
"final_mode": "RUNNING"
"hours": 4
"refused": []
"scheduled_decisions": 0
```

**The operation events**, verbatim:

```
root@aqt-server:/tmp# sudo grep '2026-10-18T1[0-4]' /var/lib/aqt/data/forward/account-1/operations.jsonl | grep -o '"kind":"[A-Z_]*"\|"record_type":"[^"]*"' | sort | uniq -c
      3 "kind":"LOOP_LAG"
      2 "kind":"SHUTDOWN"
      4 "kind":"STARTUP"
      9 "record_type":"aqt.monitoring.event.v1"
```

So the 14:01:44 step's window of 10:00 to 14:00 (four hours) completed without refusal, and the report written after its cursor `END` shows `RUNNING` with `hours: 4`. There are 3 `LOOP_LAG` events, which fits the three late starts (12:38, 13:05, 14:01); the count alone does not tie each event to a start. The report shows `scheduled_decisions: 0` for that step. Each refused step was followed by a step whose window starts again at 10:00, as the cursor shows. What this establishes: the step covering 10:00 to 14:00 completed without refusal, and no event kind other than `LOOP_LAG`, `SHUTDOWN` and `STARTUP` appears in these hours. It does not by itself prove that every hour inside the window was processed. That is the loop's tested replay behaviour (Task 29), not observed hour by hour here (T33FR3-2).

**Finding F-RESTART (open, for an owner decision):** by the code's rule above, a start is refused when its first step fetches bars successfully, finds a pending window, and the start health check sees more than 300 s of lag against the newest bar close. A failed fetch returns 1 without that check, and no pending window returns without a report (T33FR5-2). It was observed twice here (12:38:41, 13:05:20); the rule, not the two observations, is what makes it general (T33FR4-2). A proposal (the start waits until the next hour's step) would change protected forward-paper code, so it needs the owner's approval, review and §16.

## 4. The fixed check on the server (PR #64, commit `4d7f11f`)

```
root@aqt-server:/tmp# sudo git -C /opt/aqt-dashboard/app fetch --quiet origin
root@aqt-server:/tmp# sudo git -C /opt/aqt-dashboard/app checkout --quiet 4d7f11f19f88de9b9016bb6c3f674cdccf2eea12
root@aqt-server:/tmp# sudo chmod -R go-w /opt/aqt-dashboard; git -C /opt/aqt-dashboard/app rev-parse HEAD
4d7f11f19f88de9b9016bb6c3f674cdccf2eea12
root@aqt-server:/tmp# sudo systemctl start aqt-dashboard@check.service; sudo journalctl -u aqt-dashboard@check.service -o cat --no-pager | tail -13
PASS can read /var/lib/aqt/data/forward/account-1/forward_reports.jsonl
PASS can read /var/lib/aqt/data/live/BTCUSDT-1h.jsonl
PASS /var/lib/aqt/data/forward/account-1/incidents.jsonl is absent; can list /var/lib/aqt/data/forward/account-1
PASS can read /etc/aqt/deployments.jsonl
PASS cannot write in /var/lib/aqt
PASS cannot write in /etc/aqt
PASS cannot write in /opt
PASS cannot read /etc/aqt/telegram
PASS cannot open a socket (inet)
PASS cannot open a socket (Unix)
PASS io_uring_setup is refused
aqt-dashboard@check.service: Deactivated successfully.
Finished aqt-dashboard@check.service - aqt read-only dashboard (check).
```

All 11 checks pass on the server. Reading `incidents.jsonl` once it exists stays unverified until that file exists (T33F-2).
