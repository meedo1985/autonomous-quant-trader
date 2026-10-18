# D-19 screen cost pilot (prereg §10, slice S8): your command sheet

**Why.** Before the go-ahead, prereg §10 requires "one screen of a 20-trial set", measured. It tells us how long a real screen takes on your server, and §12 item 2 says a set size whose measured screen cost is infeasible cannot be declared in C2. It also produces the screen's float reference vector on the pinned image, which must be frozen into `calibration/screen.py` before any real screen (DR-6).

**What runs.** The 20 example trials in `deploy/calibration/screen-pilot/` (8 trend rules, 6 vol rules, 6 models: linear, ridge, lasso, elastic net, logistic, LightGBM at its largest allowed size), each on all 30 null paths, every screened gate. It is a measurement only: nothing is declared, nothing is decided, and forward paper keeps running untouched.

**Engine commit:** `4fed8f5cb078e25ce4b63d681236d63984e6cd77`.

**Second attempt (2026-10-17).** The first attempt, on engine `ebdf208`, stopped after 36 s. It hit a rounding fault in the path builder, fixed in `37680a8` (record `review/d19-engine/ADJUDICATION_SCREEN_S1_FIX_37680A8.md`). It left an empty `/var/lib/aqt-d19/screen-pilot.json`, which must be moved aside (`screen-pilot.failed-ebdf208.json`) before step B. 

**Third attempt (2026-10-17).** The second attempt, on engine `3573e22`, ran with the linear-family model fits on an unpinned OpenBLAS: `d19_screen.py` did not set the pinned runtime (S16S-1, §16 review of PR #61). Its timings cannot support the cost decision, so it is stopped. Its empty claimed record is moved aside as `screen-pilot.unpinned-3573e22.json`. Engine `4fed8f5` repairs S16S-1 and records each job's runtime, which `screen-summary` prints. Do step S first; the steps after it are for the third attempt.

## S. Stop the second attempt and set its empty record aside (nothing is deleted)

```sh
cd /opt/aqt-d19/app/deploy/calibration
sudo sh d19.sh stop
sudo sh d19.sh screen-status
ls -l /var/lib/aqt-d19/screen-pilot.json
```

Check: `stop` prints `stopped <id>`, `screen-status` then says `Exited`, and `ls -l` shows the file with size `0`. Only then:

```sh
sudo mv /var/lib/aqt-d19/screen-pilot.json /var/lib/aqt-d19/screen-pilot.unpinned-3573e22.json
```

If the size is not `0`, do not move it: send me the output.

**Time:** about 15 minutes of your attention, then about 15 hours of running (an estimate from the laptop: 14 rules ≈ 50 s per path, 5 linear-family models ≈ 4-6 min per path, LightGBM ≈ 20 min per path, on 2 workers). This holds for this mix only: a set of 20 LightGBM trials would take about 100 hours, so the result is reported per kind of trial, not per set size (S8 review).

**No other D-19 run may be going:** the launcher refuses to start the screen while a calibration run is up, and the reverse.

**If any command fails, or prints an error, `refused` or `FAIL`, stop there and send me the output.**

## 0. Set the re-pilot's code aside (nothing is deleted)

```sh
cd /opt/aqt-d19/app/deploy/calibration
sudo sh d19.sh status
old=$(git -C /opt/aqt-d19/app rev-parse --short HEAD); echo "$old"
if [ -e "/opt/aqt-d19/app-$old" ]; then echo "STOP: app-$old already exists"; else echo "ok: app-$old is free"; fi
if ! cg=$(systemctl show aqt-d19.slice -p ControlGroup --value); then echo "STOP: cannot read aqt-d19.slice"
elif [ -z "$cg" ]; then echo "ok: no D-19 process is running (the slice is inactive)"
elif ! procs=$(sudo find "/sys/fs/cgroup$cg" -name cgroup.procs -exec cat {} +); then echo "STOP: cannot read the processes of aqt-d19.slice"
elif [ -n "$procs" ]; then echo "STOP: D-19 processes are running"
else echo "ok: no D-19 process is running"; fi
```

Check before going on (S8-R4, S8R-R3, S8R2-R2, S8R3-R1):
- the first line `status` prints must not say `Up`;
- the line printed by `echo "$old"` (after `status`'s own lines) must be `3573e22` (the second attempt's engine);
- the last two lines must be `ok: app-3573e22 is free` and a line starting `ok: no D-19 process is running` (the second fails closed: any query it cannot make prints `STOP`; it also catches a `clean-check`, which the old launcher starts without a name). If either says `STOP: …`, stop and send me the output.

Then:

```sh
sudo mv /opt/aqt-d19/app "/opt/aqt-d19/app-$old"
ls /opt/aqt-d19
```

The last line must list `app-cbde711`, `app-e39b23d`, `app-ebdf208` and `app-3573e22` (and nothing called `app`).

## A. Install, build, probe

```sh
rm -rf /tmp/aqt-d19-src
git clone https://github.com/meedo1985/autonomous-quant-trader.git /tmp/aqt-d19-src
git -C /tmp/aqt-d19-src checkout 4fed8f5cb078e25ce4b63d681236d63984e6cd77
git -C /tmp/aqt-d19-src rev-parse HEAD
sudo sh /tmp/aqt-d19-src/deploy/calibration/d19.sh install https://github.com/meedo1985/autonomous-quant-trader.git 4fed8f5cb078e25ce4b63d681236d63984e6cd77
cd /opt/aqt-d19/app/deploy/calibration
sudo sh d19.sh build
sudo sh d19.sh probe
```

The fourth line must print `4fed8f5cb078e25ce4b63d681236d63984e6cd77`. **Send me** the line `build` prints (the image id) and the last line of `probe` (it must be `This CPU runs the pinned runtime.`).

## B. Start the pilot screen

```sh
sudo sh d19.sh screen-pilot
```

It prints a long id and `Started. Progress: sudo sh d19.sh screen-status`. Ten minutes later:

```sh
sudo sh d19.sh screen-status
systemctl status aqt-paper --no-pager | head -3
```

**Send me** both outputs: the screen must say `Up …` with a memory figure, and forward paper `active (running)`.

## C. Results (the next day)

When `screen-status` shows `Exited (0)`:

```sh
sudo sh d19.sh screen-status
sudo sh d19.sh screen-summary
```

**Send me** both outputs. `screen-summary` starts with `MEASUREMENT ONLY`, then prints one line per trial (seconds, slowest path, and which gates were **available**: this pilot checks availability, not passes), the total worker-hours, the job runtimes (it must be one entry, `{"OPENBLAS_CORETYPE": "Haswell", "OPENBLAS_NUM_THREADS": "1"}`), and the reference vectors. If it exits with an error instead, send me `sudo docker logs --tail 40 aqt-d19-screen`.

When we are done I tell you what a 20-trial screen costs, which set sizes are feasible, and the next step (freezing the reference vector, then the screen's §16 PR).
