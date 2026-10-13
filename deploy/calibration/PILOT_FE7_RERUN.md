# D-19 re-pilot, second run, on the rebuilt image: your command sheet

**Why.** Owner decision D-20 §3a (a) (`review/governance-statistics-amendment/d20-d13-proposal/OWNER_DECISION_D20_D13.md`) added scikit-learn and LightGBM to the calibration image (PR #58). CI showed the engine's canary and reference-vector outputs are byte-identical on the new image. That does not prove the re-pilot's rates, cost and speed are unchanged. So the re-pilot runs again on the rebuilt image before the go-ahead. The first run's measurements are now planning estimates only.

**Engine commit:** `e39b23dc23f0acd4b113479f3a05d66511d9f0ad` (main after PR #58).

**What stays the same.** You run these on the server, as root, as before. Forward paper keeps running, and nothing here touches it. This is a measurement only: it qualifies nothing and decides nothing. **If any command fails, or prints an error, `refused` or `FAIL`, stop there and send me the output.**

**Time:** about 45 minutes of your attention, then the development run overnight.

## 0. Set the first re-pilot's files aside (nothing is deleted)

The installer needs an empty `/opt/aqt-d19/app`, and the new run needs empty run folders. The first run's files are renamed, and the downloaded data (`raw`, `manifests`) is kept for reuse.

```sh
sudo docker ps -a --filter name=^aqt-d19$ --format '{{.Status}}'
old=$(git -C /opt/aqt-d19/app rev-parse --short HEAD); echo "$old"
sudo mv /opt/aqt-d19/app "/opt/aqt-d19/app-$old"
sudo install -d -o 990 -g 990 -m 700 /var/lib/aqt-d19/repilot1
cd /var/lib/aqt-d19 && for f in store store-clean definition.json choices.json cells.json; do [ -e "$f" ] && sudo mv "$f" repilot1/; done; ls /var/lib/aqt-d19
```

The first line must not say `Up`: no run may be going. If it does, stop and send me the output. The last line must list `raw`, `manifests` and `repilot1`.

## A. Install, build, probe (about 15 minutes)

```sh
rm -rf /tmp/aqt-d19-src
git clone https://github.com/meedo1985/autonomous-quant-trader.git /tmp/aqt-d19-src
git -C /tmp/aqt-d19-src checkout e39b23dc23f0acd4b113479f3a05d66511d9f0ad
git -C /tmp/aqt-d19-src rev-parse HEAD
sudo sh /tmp/aqt-d19-src/deploy/calibration/d19.sh install https://github.com/meedo1985/autonomous-quant-trader.git e39b23dc23f0acd4b113479f3a05d66511d9f0ad
cd /opt/aqt-d19/app/deploy/calibration
sudo sh d19.sh build
sudo sh d19.sh probe
```

The fourth line must print `e39b23dc23f0acd4b113479f3a05d66511d9f0ad`. **Send me** the line `build` prints (the image id) and the last line of `probe`. If `probe` does not print `This CPU runs the pinned runtime.`, stop here.

## B. Automatic reboots

```sh
apt-config dump | grep Automatic-Reboot
```

The last line must say `"false"`. If it does not, run step B of `PILOT_FE7.md`, then check again.

## C. Cell list and run definition (data reused)

```sh
sudo install -o 990 -g 990 -m 644 /opt/aqt-d19/app/deploy/calibration/pilot-cells.json /var/lib/aqt-d19/cells.json
sudo sh d19.sh record --out definition.json \
    --prereg-commit fff4e5fc3668887db60468740f3b5818ca7a3337 \
    --engine-commit e39b23dc23f0acd4b113479f3a05d66511d9f0ad --cell-manifest cells.json \
    --exploration-manifest manifests/exploration-BTCUSDT-1h.json --raw-root raw
```

**Send me** the hash that `record` prints.

## D–H. As in the first run

Steps D (timing), E (threshold run with the failing-chain check), F (resume check), G (development run overnight, with `memwatch`) and H (results) are exactly those of `PILOT_FE7.md`, unchanged. Run them in order, from `/opt/aqt-d19/app/deploy/calibration`, and send me what each one asks for.

When we are done, I compare both runs. I then tell you whether the go-ahead stands, or what needs your decision.
