# D-19 full calibration run (threshold and development): your command sheet

**Status: DRAFT.** Do not run any of it yet. Prepared on 2026-10-18 so that the run can start soon after its preconditions hold. The blanks are marked `<<...>>`, and they are filled only when their inputs exist.

**What it is.** Freeze-order steps 3 and 4 of the preregistration (§4): the threshold run over every qualifying cell, then development (§5). You gave the go-ahead at the measured cost: about 3,130 worker-hours, about 2½ months with 2 workers (`review/d19-engine/OWNER_DECISION_FE7_GO_AHEAD.md`). It qualifies nothing by itself. The freeze, the `AQTQ1` post and held-out certification come later, each with its own sheet. Forward paper keeps running, and nothing here touches it.

## 0. Preconditions (all must hold before step A)

| # | Precondition | Source | State on 2026-10-18 |
|---|---|---|---|
| P1 | Both attempt wallets funded; `F_Q1`, `F_Q2` and `D_Q1` fixed | prereg §4 channel, key record | **open**: funding planned 2026-10-19 |
| P2 | Your acceptance record, which pins the accepted preregistration hash | prereg §12 item 1, `<<ACCEPTANCE: …>>` | **open**, after P1 |
| P3 | The engine admits a qualification run. Today `rundef.run_plan` refuses one in code (DR2-1) until the accepted hash is pinned. That needs a reviewed change, merged after your §16 PR review, which also adds the qualifying cell list `deploy/calibration/qualification-cells.json` | `calibration/rundef.py` | **open**, after P2 |
| P4 | Automatic reboots off for the whole run | §13 item 6; your decision "3 off" | do in step B |
| P5 | No other D-19 run up (the launcher refuses anyway) | launcher `alone` guard | holds: the screen pilot exited |

Until P1–P3 hold, the engine refuses step C's `record` and step D's `run` for qualification. That is the intended guard, not a fault.

In the commands:
- `<<ENGINE_COMMIT>>` is the merged commit of P3;
- `<<PREREG_COMMIT>>` is the commit of your acceptance record (P2).

I give you both in the chat, and you copy them from the Notepad file.

**If any command fails, or prints an error, `refused` or `FAIL`, stop there and send me the output.**

## S. Set the re-pilot's and the screen pilot's files aside (nothing is deleted)

The re-pilot left its definition, cell list and chains in `/var/lib/aqt-d19`. The full run never reads them: a development run reads only the chains of its own definition, each bound to that definition's hash. They are moved aside anyway, so that `status` counts only the full run.

```sh
cd /opt/aqt-d19/app/deploy/calibration
sudo sh d19.sh status
sudo sh -c 'cd /var/lib/aqt-d19 && for f in definition.json cells.json store choices.json; do [ -e "$f" ] && mv "$f" "$f.repilot-e39b23d"; done; ls'
```

Check: `status`'s first line does not say `Up`. The listing shows the `*.repilot-e39b23d` names, plus `raw`, `manifests` and the screen-pilot records, which stay.

## A. Set the current engine aside; install, build, probe

```sh
old=$(git -C /opt/aqt-d19/app rev-parse --short HEAD); echo "$old"
sudo mv /opt/aqt-d19/app "/opt/aqt-d19/app-$old"
rm -rf /tmp/aqt-d19-src
git clone https://github.com/meedo1985/autonomous-quant-trader.git /tmp/aqt-d19-src
git -C /tmp/aqt-d19-src checkout <<ENGINE_COMMIT>>
git -C /tmp/aqt-d19-src rev-parse HEAD
sudo sh /tmp/aqt-d19-src/deploy/calibration/d19.sh install https://github.com/meedo1985/autonomous-quant-trader.git <<ENGINE_COMMIT>>
cd /opt/aqt-d19/app/deploy/calibration
sudo sh d19.sh build
sudo sh d19.sh probe
```

`rev-parse HEAD` must print `<<ENGINE_COMMIT>>`. **Send me** the image id that `build` prints and the last line of `probe` (`This CPU runs the pinned runtime.`).

## B. Automatic reboots off (P4)

```sh
echo 'Unattended-Upgrade::Automatic-Reboot "false";' | sudo tee /etc/apt/apt.conf.d/99aqt-d19-no-reboot
apt-config dump | grep Automatic-Reboot
```

The last line must say `"false"`. Security updates still install. When the whole calibration is over, remove the file again (RUNBOOK §1).

## C. Cell list and run definition

The exploration archives (`raw`) and the BTC manifest (`manifests`) are already in `/var/lib/aqt-d19` from the re-pilot. Running `manifests` again with this engine is a check: it writes nothing if its result is byte-identical to the existing manifest, and refuses (`refusing to replace a different existing file`) if not. In that case, stop and send me the output.

```sh
sudo sh d19.sh manifests
sudo install -o 990 -g 990 -m 644 /opt/aqt-d19/app/deploy/calibration/qualification-cells.json /var/lib/aqt-d19/cells.json
sudo sh d19.sh record --out definition.json \
    --prereg-commit <<PREREG_COMMIT>> \
    --engine-commit <<ENGINE_COMMIT>> --cell-manifest cells.json \
    --exploration-manifest manifests/exploration-BTCUSDT-1h.json --raw-root raw
sudo cat /var/lib/aqt-d19/definition.json
```

**Send me** the hash that `record` prints and the whole file. **Commit before running (§13 item 6, S16-2):**
- I commit the definition to the repository and push it, and you get the commit id back.
- Its commit time, before the first threshold chunk, is the record that this definition came first. The freeze checks it.
- **Do not start step D before I send you that commit id.**

## D. Threshold run (several weeks)

```sh
sudo sh d19.sh run threshold
sleep 600; sudo sh d19.sh status; systemctl status aqt-paper --no-pager | head -3
```

**Send me** both outputs: the run `Up`, and forward paper `active (running)`.

Then check about once a week with `sudo sh d19.sh status`, and **send me** its output.

If `status` shows `Exited` with a code other than 0:

```sh
sudo docker logs --tail 20 aqt-d19
sudo sh d19.sh run threshold    # resumes from the last finished chunk; only after I have read the log
```

The threshold run is finished when `status` shows `Exited (0)` and every `threshold/...` line shows the full chunk count for its cell. I tell you the expected count from the merged cell list.

## E. Development run (several weeks)

Start it only after D has finished:

```sh
sudo sh d19.sh run dev
sleep 600; sudo sh d19.sh status; systemctl status aqt-paper --no-pager | head -3
```

Same weekly `status` and the same rule on an error. It is finished when every `dev/...` line is complete.

## F. Choices

```sh
sudo sh d19.sh choose
sudo cat /var/lib/aqt-d19/choices.json
```

**Send me** the file. It goes into the qualification object at the freeze (freeze order step 5, its own sheet).

## What this sheet does not do

- No freeze, no `AQTQ1` post, no held-out run. Each comes later with its own sheet and reviews.
- No change to forward paper.
- No look at any chunk's content: `status` shows counts only (P18-6).
