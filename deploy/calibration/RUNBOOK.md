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

```sh
curl -fsSLO https://raw.githubusercontent.com/meedo1985/autonomous-quant-trader/<commit>/deploy/calibration/d19.sh
sudo sh d19.sh install https://github.com/meedo1985/autonomous-quant-trader.git <commit>
sudo sh d19.sh build
```

`build` prints the image id. Check that automatic reboots are off for the run:

```sh
grep -r Automatic-Reboot /etc/apt/apt.conf.d/ || echo "not set (default: off)"
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

## 4. Run, watch, stop, resume

```sh
sudo sh d19.sh run threshold     # starts in the background
sudo sh d19.sh status            # running or not, last log lines, chunks per cell
sudo sh d19.sh stop              # stops; finished chunks are kept
sudo sh d19.sh run threshold     # resumes from the last finished chunk
```

When `threshold` has finished, run `dev` the same way, then:

```sh
sudo sh d19.sh choose            # writes /var/lib/aqt-d19/choices.json
```

`status` shows only counts. It never opens a chunk's content.
