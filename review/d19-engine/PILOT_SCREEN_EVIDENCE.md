# D-19 screen cost pilot (prereg §10, slice S8): evidence from the owner's server

The owner ran the commands on his server and pasted the outputs into the Claude Code session. Claude Opus 5.5 (`claude-opus-5-5`) records them here verbatim, with any trimming stated. The SSH login banner is left out: it shows a client IP address.

**Kit:** `deploy/calibration/PILOT_SCREEN.md`, 20 trials in `deploy/calibration/screen-pilot/`. First attempt on engine `ebdf20806a0e59bde9305bc052a18c98fd3a7b33`; second attempt on engine `3573e222faed4c4e032d04282c1550569f68c107`.

## 2026-10-17, first attempt: step 0 (re-pilot code set aside)

The 26 per-namespace lines that `status` prints after `slice memory peak` are trimmed: 13 `dev/pilot-*` lines with count 2 and 13 `threshold/pilot-*` lines with count 4, the re-pilot's stores.

```
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh status
Exited (0) 7 hours ago
started 2026-10-16T20:27:30.33631332Z finished 2026-10-17T05:23:56.587136212Z exit 0
slice memory peak: 506847232 bytes
[26 namespace lines trimmed]
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# old=$(git -C /opt/aqt-d19/app rev-parse --short HEAD); echo "$old"
[the slice check from the sheet]
e39b23d
ok: app-e39b23d is free
ok: no D-19 process is running
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# cd /
root@aqt-server:/# sudo mv /opt/aqt-d19/app /opt/aqt-d19/app-e39b23d
root@aqt-server:/# ls /opt/aqt-d19
app-cbde711  app-e39b23d
```

## First attempt: step A (install, build, probe)

The clone and apt output are trimmed. The build's 8 steps all used the cache.

```
root@aqt-server:/# git -C /tmp/aqt-d19-src rev-parse HEAD
ebdf20806a0e59bde9305bc052a18c98fd3a7b33
Installed engine ebdf20806a0e59bde9305bc052a18c98fd3a7b33. Next: sudo sh d19.sh build
Successfully tagged aqt-d19:ebdf20806a0e59bde9305bc052a18c98fd3a7b33
Image aqt-d19:ebdf20806a0e59bde9305bc052a18c98fd3a7b33 id sha256:54bfcf5394cbd7a40fd3351d2fda6ed61fd7564435fe2f14bcb182f996f9790c
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh probe
This CPU runs the pinned runtime.
```

The image id equals the re-pilot's image (`PILOT_FE7_RERUN_EVIDENCE.md`, step A).

## First attempt: step B (the screen stopped after 36 s)

```
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh screen-status
Exited (1) 14 minutes ago
started 2026-10-17T12:52:24.677014308Z finished 2026-10-17T12:53:00.386311144Z exit 1
  File "/usr/local/lib/python3.14/concurrent/futures/_base.py", line 396, in __get_result
    raise self._exception
aqt.data.bars.BarSemanticsError: high 158.36103274821556 is below open/low/close (156.35606198642708, 155.04359757328257, 158.3610327482157) at 2021-06-27T11:00:00+00:00
● aqt-paper.service - aqt forward paper trading
     Loaded: loaded (/etc/systemd/system/aqt-paper.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-10-05 06:30:33 UTC; 1 week 5 days ago
```

**Cause and fix.** `reconstruct` chained closes as `log(o0) + cumsum(c)`, a different addition order from `log_open + hi`. A source bar closing at its high or low could therefore give a path high below its close, or a path low above it. On the laptop, with the old code, all 30 pilot paths from the real exploration data fail `Bar` validation; with the fix, all 30 pass. The fix is `37680a8` (each close is `fl(log_open + c)`). Sol ACCEPTED it, with S1F-R1 a disclosed residual: record `SOL6_SCREEN_S1_FIX_REVIEW_37680A8.md`, adjudication `ADJUDICATION_SCREEN_S1_FIX_37680A8.md`. The failed run measured nothing, and nothing was declared. As `reserve()` is designed to, it left an empty claimed record.

## Second attempt: step 0 (empty record and first-attempt code set aside)

```
root@aqt-server:/# ls -l /var/lib/aqt-d19/screen-pilot.json
-rw-r--r-- 1 systemd-resolve systemd-resolve 0 Oct 17 12:52 /var/lib/aqt-d19/screen-pilot.json
root@aqt-server:/# sudo mv /var/lib/aqt-d19/screen-pilot.json /var/lib/aqt-d19/screen-pilot.failed-ebdf208.json
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh screen-status
Exited (1) 58 minutes ago
started 2026-10-17T12:52:24.677014308Z finished 2026-10-17T12:53:00.386311144Z exit 1
[the same three traceback lines as above]
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# old=$(git -C /opt/aqt-d19/app rev-parse --short HEAD); echo "$old"
[the slice check from the sheet]
ebdf208
ok: app-ebdf208 is free
ok: no D-19 process is running
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# cd /
root@aqt-server:/# sudo mv /opt/aqt-d19/app /opt/aqt-d19/app-ebdf208
root@aqt-server:/# ls /opt/aqt-d19
app-cbde711  app-e39b23d  app-ebdf208
```

(The file's owner shows as `systemd-resolve`. This is presumably the host's name for uid 990, which is the container's `d19` user. It was not checked on the server.)

## Second attempt: step A

The clone and apt output are trimmed. The build's 8 steps all used the cache.

```
root@aqt-server:/# git -C /tmp/aqt-d19-src rev-parse HEAD
3573e222faed4c4e032d04282c1550569f68c107
Installed engine 3573e222faed4c4e032d04282c1550569f68c107. Next: sudo sh d19.sh build
Successfully tagged aqt-d19:3573e222faed4c4e032d04282c1550569f68c107
Image aqt-d19:3573e222faed4c4e032d04282c1550569f68c107 id sha256:54bfcf5394cbd7a40fd3351d2fda6ed61fd7564435fe2f14bcb182f996f9790c
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh probe
This CPU runs the pinned runtime.
```

## Second attempt: step B (started 14:27Z)

The paste of the `screen-pilot` command itself was not sent. Seven minutes later:

```
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh screen-status
Up 7 minutes
started 2026-10-17T14:27:06.036248406Z finished 0001-01-01T00:00:00Z exit 0
memory peak so far: 563146752 bytes
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# systemctl status aqt-paper --no-pager | head -3
● aqt-paper.service - aqt forward paper trading
     Loaded: loaded (/etc/systemd/system/aqt-paper.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-10-05 06:30:33 UTC; 1 week 5 days ago
```

The second attempt was later stopped: its linear-family fits ran on an unpinned OpenBLAS (S16S-1), so its timings cannot support the cost decision.

## Third attempt: step S (second attempt stopped)

The owner reported the `stop` itself without its output. The checks afterwards, with the step 0 checks run as single lines (output trimmed: the calibration `status` job list):

```
root@aqt-server:~# ls -l /var/lib/aqt-d19/; cd /opt/aqt-d19/app/deploy/calibration; sudo sh d19.sh status; git -C /opt/aqt-d19/app rev-parse --short HEAD; ls /opt/aqt-d19; systemctl show aqt-d19.slice -p ControlGroup --value
-rw-r--r-- 1 systemd-resolve systemd-resolve     0 Oct 17 12:52 screen-pilot.failed-ebdf208.json
-rw-r--r-- 1 systemd-resolve systemd-resolve     0 Oct 17 14:27 screen-pilot.json
Exited (0) 13 hours ago
started 2026-10-16T20:27:30.33631332Z finished 2026-10-17T05:23:56.587136212Z exit 0
3573e22
app  app-cbde711  app-e39b23d  app-ebdf208
/aqt.slice/aqt-d19.slice
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh screen-status; sudo find /sys/fs/cgroup/aqt.slice/aqt-d19.slice -name cgroup.procs -exec cat {} +; echo END
Exited (143) About an hour ago
started 2026-10-17T14:27:06.036248406Z finished 2026-10-17T17:04:40.058228383Z exit 143
END
```

The second attempt ended at 17:04:40Z with exit 143 (SIGTERM, the `stop`). The slice was still listed but held no process (nothing between the command and `END`). The `status` line is the calibration re-pilot, not the screen.

## Third attempt: step 0 (empty record and second-attempt code set aside)

```
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo mv /var/lib/aqt-d19/screen-pilot.json /var/lib/aqt-d19/screen-pilot.unpinned-3573e22.json; sudo mv /opt/aqt-d19/app /opt/aqt-d19/app-3573e22; ls -l /var/lib/aqt-d19/ | grep screen; ls /opt/aqt-d19
-rw-r--r-- 1 systemd-resolve systemd-resolve     0 Oct 17 12:52 screen-pilot.failed-ebdf208.json
-rw-r--r-- 1 systemd-resolve systemd-resolve     0 Oct 17 14:27 screen-pilot.unpinned-3573e22.json
app-3573e22  app-cbde711  app-e39b23d  app-ebdf208
```

## Third attempt: step A

The clone and apt output are trimmed. The build's 8 steps all used the cache.

```
4fed8f5cb078e25ce4b63d681236d63984e6cd77
Installed engine 4fed8f5cb078e25ce4b63d681236d63984e6cd77. Next: sudo sh d19.sh build
Successfully tagged aqt-d19:4fed8f5cb078e25ce4b63d681236d63984e6cd77
Image aqt-d19:4fed8f5cb078e25ce4b63d681236d63984e6cd77 id sha256:54bfcf5394cbd7a40fd3351d2fda6ed61fd7564435fe2f14bcb182f996f9790c
Next: sudo sh d19.sh probe
This CPU runs the pinned runtime.
```

The image id is the same as in the first two attempts.

## Third attempt: step B (started 18:15Z)

Status was read immediately after the start (the 10-minute check is below once received):

```
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh screen-pilot
6b85aa2230883c8e4b9726fe566bd24466efe410cef9e4612c644fc8cc4e0c54
Started. Progress: sudo sh d19.sh screen-status
Up Less than a second
started 2026-10-17T18:15:10.493389752Z finished 0001-01-01T00:00:00Z exit 0
memory peak so far: 18309120 bytes
● aqt-paper.service - aqt forward paper trading
     Loaded: loaded (/etc/systemd/system/aqt-paper.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-10-05 06:30:33 UTC; 1 week 5 days ago
```

## Step C (results)

Pending: the third attempt is expected to finish about 2026-10-18 09:15Z. `screen-summary` must show a single job runtime, the pinned one.
