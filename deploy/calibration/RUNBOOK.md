# D-19 calibration runbook (FE-4)

For the owner. You run every step. The AI never logs into the server.
These steps run the calibration engine beside forward paper. They never
touch `/opt/aqt` or the `aqt-paper` service.

This runbook authorizes nothing by itself:
- The re-pilot needs your word first (FE-7).
- Any qualification run needs your go-ahead after the re-pilot (preregistration §4, step 2).
- The engine refuses qualification runs in code until they are allowed.

## What it sets up

- **`/opt/aqt-d19/app`:** the engine's own checkout at the commit you choose. It belongs to root, and the engine only reads it.
- **`/var/lib/aqt-d19`:** the run's files (definition, chunks, choices). It belongs to the engine's account, uid 990.
- **The image `aqt-d19:<commit>`:** Python 3.14 and NumPy 2.5.3, the only package, pinned by hash.
- **The slice `aqt-d19.slice`:** caps the calibration at 2.5 GB of memory, so forward paper keeps the rest.

Every engine process has these limits:
- it runs at the lowest CPU priority (`nice 19`);
- it has no network;
- it runs as uid 990, never root.

The run is tied to the image's id. The launcher reads that id itself with `docker image inspect`, so you never type it.

## 1. Install (once per engine commit)

Clone the repository and check out the commit you chose. The commit id is a hash of every file in it, so the script you then run as root is exactly that commit's script (FE4-6):

```sh
git clone https://github.com/meedo1985/autonomous-quant-trader.git /tmp/aqt-d19-src
git -C /tmp/aqt-d19-src checkout <commit>
git -C /tmp/aqt-d19-src rev-parse HEAD    # must print <commit>
sudo sh /tmp/aqt-d19-src/deploy/calibration/d19.sh install https://github.com/meedo1985/autonomous-quant-trader.git <commit>
sudo sh /opt/aqt-d19/app/deploy/calibration/d19.sh build
```

`build` prints the image id. From here on, run the installed copy from its folder:

```sh
cd /opt/aqt-d19/app/deploy/calibration
```

Check that this server's CPU can run the pinned runtime:

```sh
sudo sh d19.sh probe
```

It prints `This CPU runs the pinned runtime.`, or it stops with one of two results:

- **Exit 3, "refused: the measurement crashed (segmentation fault)".** The engine's measurement crashed on this server. On newer AMD EPYC (Zen 4/5) that has been the pinned math kernel, but the cause here is not proven until it is diagnosed. Stop and send me the whole output. Only once the cause is confirmed is changing the pin a decision for you (D-20 binding).
- **Any other error.** Stop and send me the whole output and the exit status. Nothing is decided from it until it is diagnosed.

Switch automatic reboots off for the run (§13 item 6). Security updates still install:

```sh
echo 'Unattended-Upgrade::Automatic-Reboot "false";' | sudo tee /etc/apt/apt.conf.d/99aqt-d19-no-reboot
apt-config dump | grep Automatic-Reboot    # the last line must say "false"
```

When the calibration is over, switch them back:

```sh
sudo rm /etc/apt/apt.conf.d/99aqt-d19-no-reboot
```

## 2. Exploration data (once)

Copy the archives that forward paper already downloaded, then build the BTC manifest inside the image:

```sh
sudo cp -r /var/lib/aqt/data/raw /var/lib/aqt-d19/raw
sudo chown -R 990:990 /var/lib/aqt-d19/raw
sudo sh d19.sh manifests
```

## 3. Record the run definition

The cell manifest file (`cells.json`) and the commits come with the step that uses them (the re-pilot, FE-7). Put `cells.json` in `/var/lib/aqt-d19` (owner uid 990). Then:

```sh
sudo sh d19.sh record --out definition.json --prereg-commit <prereg commit> \
    --engine-commit <commit> --cell-manifest cells.json \
    --exploration-manifest manifests/exploration-BTCUSDT-1h.json --raw-root raw
```

It prints the run-definition hash. Nothing has run yet.

**Commit it before step 4 (§13 item 6, S16-2).** Send the hash and the file (`sudo cat /var/lib/aqt-d19/definition.json`). It is committed to the repository and pushed, and you get the commit id back. Start `run threshold` only after that. The commit's time, before the first threshold chunk, is the record that this definition came first; the qualification object checks it at the freeze.

## 4. Run, watch, stop, resume

```sh
sudo sh d19.sh run threshold     # starts in the background
sudo sh d19.sh status            # running or not, and chunks per cell
sudo sh d19.sh stop              # stops; finished chunks are kept
sudo sh d19.sh run threshold     # resumes from the last finished chunk
```

When `threshold` has finished, run `dev` the same way, then:

```sh
sudo sh d19.sh choose            # writes /var/lib/aqt-d19/choices.json
```

`status` shows only the container state and counts. It never opens a chunk's content.

Every start first checks that the memory cap really applies. Docker must use systemd's cgroup driver, `aqt-d19.slice` must have `MemoryMax` 2560M, and a test container must land in that slice. If any check fails, nothing starts and the reason is printed.

If `status` shows `Exited (1)`, the run stopped on an error. To see why:

```sh
sudo docker logs --tail 20 aqt-d19
```

This applies to threshold and development runs only. The held-out run, which is not built yet, will have its own rule.
