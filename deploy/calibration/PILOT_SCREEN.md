# D-19 screen cost pilot (prereg §10, slice S8): your command sheet

**Why.** Before the go-ahead, prereg §10 requires "one screen of a 20-trial set", measured. It tells us how long a real screen takes on your server, and §12 item 2 says a set size whose measured screen cost is infeasible cannot be declared in C2. It also produces the screen's float reference vector on the pinned image, which must be frozen into `calibration/screen.py` before any real screen (DR-6).

**What runs.** The 20 example trials in `deploy/calibration/screen-pilot/` (8 trend rules, 6 vol rules, 6 models: linear, ridge, lasso, elastic net, logistic, LightGBM at its largest allowed size), each on all 30 null paths, every screened gate. It is a measurement only: nothing is declared, nothing is decided, and forward paper keeps running untouched.

**Engine commit:** `e01e745a…`: use the full hash printed by step A's `rev-parse`.

**Time:** about 15 minutes of your attention, then about 15 hours of running (an estimate from the laptop: 14 rules ≈ 50 s per path, 5 linear-family models ≈ 4-6 min per path, LightGBM ≈ 20 min per path, on 2 workers).

**If any command fails, or prints an error, `refused` or `FAIL`, stop there and send me the output.**

## 0. Set the re-pilot's code aside (nothing is deleted)

```sh
cd /opt/aqt-d19/app/deploy/calibration
sudo sh d19.sh status
old=$(git -C /opt/aqt-d19/app rev-parse --short HEAD); echo "$old"
sudo mv /opt/aqt-d19/app "/opt/aqt-d19/app-$old"
```

The first line must not say `Up`. The second must print `e39b23d`.

## A. Install, build, probe

```sh
rm -rf /tmp/aqt-d19-src
git clone https://github.com/meedo1985/autonomous-quant-trader.git /tmp/aqt-d19-src
git -C /tmp/aqt-d19-src checkout e01e745
git -C /tmp/aqt-d19-src rev-parse HEAD
sudo sh /tmp/aqt-d19-src/deploy/calibration/d19.sh install https://github.com/meedo1985/autonomous-quant-trader.git "$(git -C /tmp/aqt-d19-src rev-parse HEAD)"
cd /opt/aqt-d19/app/deploy/calibration
sudo sh d19.sh build
sudo sh d19.sh probe
```

**Send me** the full hash (line 4), the line `build` prints (the image id) and the last line of `probe` (it must be `This CPU runs the pinned runtime.`).

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

**Send me** both outputs. `screen-summary` prints one line per trial (seconds, slowest path, gate results), the total worker-hours, and the reference vectors. If it exits with an error instead, send me `sudo docker logs --tail 40 aqt-d19-screen`.

When we are done I tell you what a 20-trial screen costs, which set sizes are feasible, and the next step (freezing the reference vector, then the screen's §16 PR).
