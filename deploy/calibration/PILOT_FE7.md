# D-19 re-pilot (FE-7): your command sheet

You run these on the server, logged in as root as usual. Copy each block exactly. Forward paper keeps running, and nothing here touches it.

The re-pilot is a measurement only. It qualifies nothing and decides nothing. The engine refuses qualification runs in code.

In the commands:
- `<commit>` is the engine commit id I give you in the chat;
- the preregistration commit is already filled in.

Where a step says **send me**, paste the output into the chat. **If any command fails or prints an error, `refused` or `FAIL`, stop there and send me the output.** Do not go on to the next command.

**Time:** about 45 minutes of your attention. The development run then takes one night, about 10 hours.

**What you run:** 13 cells. There is one cell from each group. Every cell of the thin categories is included: 2 Q1 clusters, 3 Q2m and 2 QJ. Each cell runs 2,000 threshold and 1,000 development replications at T = 1247. This is your choice of 2026-10-11 (`OWNER_DECISION_FE7_PILOT_SIZE.md`).

## A. Install, build, probe (about 15 minutes)

```sh
git clone https://github.com/meedo1985/autonomous-quant-trader.git /tmp/aqt-d19-src
git -C /tmp/aqt-d19-src checkout <commit>
git -C /tmp/aqt-d19-src rev-parse HEAD
sudo sh /tmp/aqt-d19-src/deploy/calibration/d19.sh install https://github.com/meedo1985/autonomous-quant-trader.git <commit>
cd /opt/aqt-d19/app/deploy/calibration
sudo sh d19.sh build
sudo sh d19.sh probe
```

The third line must print `<commit>`. **Send me** the last line of `probe`. If `probe` does not print `This CPU runs the pinned runtime.`, stop here.

## B. Switch automatic reboots off for the run

```sh
echo 'Unattended-Upgrade::Automatic-Reboot "false";' | sudo tee /etc/apt/apt.conf.d/99aqt-d19-no-reboot
apt-config dump | grep Automatic-Reboot
```

The last line must say `"false"`.

## C. Data, cell list, run definition

`copy-raw` copies forward paper's downloaded archives once. It refuses if a copy already exists, so stop there and send me the output.

```sh
sudo sh d19.sh copy-raw
sudo sh d19.sh manifests
sudo install -o 990 -g 990 -m 644 /opt/aqt-d19/app/deploy/calibration/pilot-cells.json /var/lib/aqt-d19/cells.json
sudo sh d19.sh record --out definition.json \
    --prereg-commit fff4e5fc3668887db60468740f3b5818ca7a3337 \
    --engine-commit <commit> --cell-manifest cells.json \
    --exploration-manifest manifests/exploration-BTCUSDT-1h.json --raw-root raw
```

**Send me** the output of `manifests` and the hash that `record` prints.

## D. Timing of the two block rules (I1-8, about 5 minutes)

```sh
sudo sh d19.sh timing
```

**Send me** the three lines it prints.

## E. Threshold run, with the failing-chain check (FR2-2)

Start the run and let it work for two minutes. Then `failcheck` kills one of its two workers and checks that the whole run stops and that no worker survives:

```sh
sudo sh d19.sh run threshold
sleep 120
sudo sh d19.sh failcheck
sudo sh d19.sh status
```

`failcheck` must print `PASS: ...`. **Send me** both outputs. Then resume, which continues from the last finished chunk:

```sh
sudo sh d19.sh run threshold
```

Check now and then with `sudo sh d19.sh status`. The threshold run is finished when `status` shows `Exited (0)`, and **all 13** `threshold/...` lines show `4`. Then:

```sh
sudo sh d19.sh status
sudo sh d19.sh times threshold
```

**Send me** both outputs. `times` gives each cell's seconds between finished chunks, one worker's time for 500 replications. An interval marked `(spans a restart)` crosses the failcheck stop, so it is not used.

## F. Resume check (about as long as the threshold run, under an hour)

This runs the threshold namespace again from scratch, in a separate folder, and compares it with the interrupted-and-resumed one:

```sh
sudo sh d19.sh clean-check
```

It must end with `PASS: the resumed threshold run equals the clean run`. **Send me** the output.

## G. Development run (overnight)

```sh
sudo sh d19.sh run dev
sudo sh d19.sh memwatch
systemctl status aqt-paper --no-pager | head -3
```

`memwatch` takes 10 minutes. It checks every 10 seconds that both workers are running, then reads the run's exact memory high-water mark from the kernel. **Send me** both outputs: they show the peak memory with 2 workers, and that forward paper is still running.

The development run is finished when `status` shows `Exited (0)` and **all 13** `dev/...` lines show `2`.

## H. Results (the next day)

```sh
sudo sh d19.sh status
sudo sh d19.sh times dev
sudo sh d19.sh choose
sudo sh d19.sh nonfinite
sudo cat /var/lib/aqt-d19/choices.json
```

**Send me** all of it. Here is what each output tells me:
- `status` and `times dev`: the run times and each cell's measured development time per 500 replications (the threshold ones came in step E);
- `nonfinite`: the non-finite threshold draws, per cell (FE-7). If any exist, how to treat them is your decision;
- `choices.json`: the development event counts.

Every number here comes from development or threshold data. Nothing held-out exists.

When we are done, I will tell you whether to switch automatic reboots back on, or to keep them off for the full run.
