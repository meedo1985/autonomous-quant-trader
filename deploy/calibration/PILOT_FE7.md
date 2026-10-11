# D-19 re-pilot (FE-7): your command sheet

You run these on the server, logged in as root as usual. Copy each block exactly. Forward paper keeps running and is never touched.

The re-pilot is a measurement only. It qualifies nothing and decides nothing. The engine refuses qualification runs in code.

Where a step says **send me**, paste the output into the chat. In the commands:
- `<commit>` is the engine commit id I give you in the chat;
- the preregistration commit is already filled in.

**Time:** about 30 minutes of your attention, then an overnight run of about 5–8 hours.

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

The third line must print `<commit>`. **Send me** the last line of `probe`.

**If `probe` refuses, stop here.** Nothing else is run until we have diagnosed it.

## B. Switch automatic reboots off for the run

```sh
echo 'Unattended-Upgrade::Automatic-Reboot "false";' | sudo tee /etc/apt/apt.conf.d/99aqt-d19-no-reboot
apt-config dump | grep Automatic-Reboot
```

The last line must say `"false"`.

## C. Data, cell list, run definition

```sh
sudo cp -r /var/lib/aqt/data/raw /var/lib/aqt-d19/raw
sudo chown -R 990:990 /var/lib/aqt-d19/raw
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

## E. Threshold run and the failing-chain check (FR2-2)

```sh
sudo sh d19.sh run threshold
sleep 60
sudo docker top aqt-d19 -eo pid,args
```

The list shows the run's processes. Two of them contain `spawn_main`: those are the two workers. Kill **one** of them, putting its number in place of `<PID>`:

```sh
sudo kill -9 <PID>
sleep 30
sudo sh d19.sh status
sudo docker top aqt-d19
sudo docker logs --tail 5 aqt-d19
```

`status` should now say `Exited`. `docker top` should say the container is not running, which shows that no worker outlived the run. **Send me** all three outputs. Then resume:

```sh
sudo sh d19.sh run threshold
```

Check now and then with `sudo sh d19.sh status`. The threshold run is finished when the status says `Exited (0)` and every `threshold/...` line shows `4`.

## F. Development run (overnight)

```sh
sudo sh d19.sh run dev
sleep 600
sudo docker stats --no-stream aqt-d19
free -m
systemctl status aqt-paper --no-pager | head -3
```

**Send me** these three outputs. They show the memory with 2 workers and that forward paper is still running.

The development run is finished when the status says `Exited (0)` and every `dev/...` line shows `2`.

## G. Results (the next day)

```sh
sudo sh d19.sh status
sudo sh d19.sh nonfinite
sudo ls -l --time-style=+%s /var/lib/aqt-d19/store/threshold/* /var/lib/aqt-d19/store/dev/*
sudo sh d19.sh choose
sudo cat /var/lib/aqt-d19/choices.json
```

**Send me** all of it. Here is what each output tells me:
- `nonfinite`: the number of non-finite threshold draws (FE-7);
- the file times: the speed per replication;
- `choices.json`: the development event counts.

Every number here is development or threshold data. Nothing held-out exists.

When we are done, I will tell you whether to switch automatic reboots back on, or to keep them off for the full run.
