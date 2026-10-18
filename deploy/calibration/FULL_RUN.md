# D-19 full calibration run (threshold and development): your command sheet

**Status: DRAFT.** Do not run any of it yet. Prepared on 2026-10-18 and revised after Sol's review (FS-1..FS-5), so the run can start soon after its preconditions hold. The blanks are marked `<<...>>`; each is filled only when its input exists.

**What it is.** Freeze-order steps 3 and 4 of the preregistration (§4): the threshold run over every qualifying cell, then development (§5). You gave the go-ahead at the measured cost: about 3,130 worker-hours, about 2½ months with 2 workers (`review/d19-engine/OWNER_DECISION_FE7_GO_AHEAD.md`). It qualifies nothing by itself. The freeze, the `AQTQ1` post and held-out certification come later, each with its own sheet. Forward paper keeps running, and nothing here touches it.

**Size.** 104 cells: the qualifying grid at `T = T_C2 = 1240` (`calibration/grid.py`). Chunks are 500 replications each (`calibration/chunks.py`). So each cell needs **600 threshold chunks** (300,000 replications) and **24 development chunks** (12,000), the prescribed counts (`rundef.PRESCRIBED`).

## 0. Preconditions: all are checked and recorded before step S (FS-1)

| # | Precondition | Source |
|---|---|---|
| P1 | The complete key record: `A_Q1`, `A_Q2` (recorded 2026-10-12) and the funded coins `F_Q1`, `F_Q2` with outpoint, amount and height, each address checked as never spent from and holding only its coin (OF1-3), and `D_Q1` | prereg §4 channel; `review/d19-engine/KEY_RECORD_DRAFT.md` |
| P2 | Your acceptance record, with those values substituted and the accepted preregistration hash pinned | prereg §12 item 1 |
| P3 | A merged engine change that admits a qualification run only with that accepted hash (today `rundef.run_plan` refuses, DR2-1). It also adds `deploy/calibration/qualification-cells.json`, tested equal to `grid.manifest(T_C2, PRESCRIBED)`. It gets Sol's review and **your §16 PR review**, and it implements the reviewed "by the freeze" build order | `calibration/rundef.py`; `OWNER_DECISION_BUILD_ORDER.md` |
| P4 | The build-order reading relied on by P3 has its independent review recorded | **holds**: `review/d19-engine/SOL6_BUILD_ORDER_REVIEW_D321147.md` |
| P5 | `T_C2 = 1240` fixed | **holds**: `calibration/grid.py`, owner decision on GAP-1 |
| P6 | Automatic reboots off for the whole run | §13 item 6; your decision "3 off"; step B |

Until P1–P3 hold, the engine refuses step C's `record` and step D's `run` for qualification. That is the intended guard, not a fault.

In the commands:
- `<<ENGINE_COMMIT>>` is the full 40-character merged commit of P3;
- `<<PREREG_COMMIT>>` is the commit of your acceptance record (P2);
- `<<PREREG_SHA256>>` is the accepted preregistration hash.

I give you all three in a Notepad file.

**Run every line on its own, one at a time; never paste a block. If any line fails, or prints an error, `refused`, `STOP` or `FAIL`, stop there and send me the output.** Each line that depends on a check stops by itself when the check fails (FSR-1).

## S. Set the earlier runs' files aside (nothing is deleted) (FS-2)

Run these one at a time. First check that no D-19 process is running at all:

```sh
cd /opt/aqt-d19/app/deploy/calibration
sudo sh d19.sh status
sudo sh d19.sh screen-status
if ! cg=$(systemctl show aqt-d19.slice -p ControlGroup --value); then echo "STOP: cannot read aqt-d19.slice"; elif [ -z "$cg" ]; then echo "ok: no D-19 process is running"; elif [ -n "$(sudo find "/sys/fs/cgroup$cg" -name cgroup.procs -exec cat {} +)" ]; then echo "STOP: D-19 processes are running"; else echo "ok: no D-19 process is running"; fi
```

Check: neither status says `Up`, and the last line starts `ok:`. Then move each file, refusing to overwrite and stopping at the first failure:

```sh
(cd /var/lib/aqt-d19 && for f in definition.json cells.json store choices.json; do if [ -e "$f" ]; then [ ! -e "$f.repilot-e39b23d" ] || { echo "STOP: $f.repilot-e39b23d exists"; exit 1; }; mv "$f" "$f.repilot-e39b23d" || { echo "STOP: mv $f failed"; exit 1; }; fi; done; ls)
```

Check: no `STOP` line. The listing shows the `*.repilot-e39b23d` names, plus `raw`, `manifests` and the screen-pilot records, which stay. A development run reads only the chains bound to its own definition, so the moved chains could not enter it in any case.

## A. Set the current engine aside; install, build, probe

```sh
old=$(git -C /opt/aqt-d19/app rev-parse --short HEAD) && echo "$old" && if [ -e "/opt/aqt-d19/app-$old" ]; then echo "STOP: app-$old exists"; else sudo mv /opt/aqt-d19/app "/opt/aqt-d19/app-$old" && echo "ok: moved to app-$old"; fi
rm -rf /tmp/aqt-d19-src
git clone https://github.com/meedo1985/autonomous-quant-trader.git /tmp/aqt-d19-src
git -C /tmp/aqt-d19-src checkout <<ENGINE_COMMIT>> && echo "ok: checked out"
sudo sh /tmp/aqt-d19-src/deploy/calibration/d19.sh install https://github.com/meedo1985/autonomous-quant-trader.git <<ENGINE_COMMIT>>
git -C /opt/aqt-d19/app rev-parse HEAD
cd /opt/aqt-d19/app/deploy/calibration
sudo sh d19.sh build
sudo sh d19.sh probe
```

Check: the first line ends with `ok: moved to app-…`, and the checkout line with `ok: checked out`. The **installed** checkout's `rev-parse HEAD` prints `<<ENGINE_COMMIT>>` in full (FS-3). **Send me** the image id that `build` prints and the last line of `probe` (`This CPU runs the pinned runtime.`).

## B. Automatic reboots off (P6)

```sh
echo 'Unattended-Upgrade::Automatic-Reboot "false";' | sudo tee /etc/apt/apt.conf.d/99aqt-d19-no-reboot
apt-config dump | grep Automatic-Reboot
```

The last line must say `"false"`. Security updates still install. When the whole calibration is over, remove the file again (RUNBOOK §1).

## C. Cell list and run definition, checked before anything runs (FS-3)

The exploration archives (`raw`) and the BTC manifest (`manifests`) are already in `/var/lib/aqt-d19` from the re-pilot. Running `manifests` again with this engine is a check: it writes nothing if its result is byte-identical to the existing manifest, and refuses (`refusing to replace a different existing file`) if not. In that case, stop and send me the output. Go on only after the line `ok: manifest unchanged` (FSR-1).

```sh
sudo sh d19.sh manifests && echo "ok: manifest unchanged"
sudo install -o 990 -g 990 -m 644 /opt/aqt-d19/app/deploy/calibration/qualification-cells.json /var/lib/aqt-d19/cells.json
sha256sum /opt/aqt-d19/app/deploy/calibration/qualification-cells.json /var/lib/aqt-d19/cells.json
sudo sh d19.sh record --out definition.json \
    --prereg-commit <<PREREG_COMMIT>> \
    --engine-commit <<ENGINE_COMMIT>> --cell-manifest cells.json \
    --exploration-manifest manifests/exploration-BTCUSDT-1h.json --raw-root raw
sudo cat /var/lib/aqt-d19/definition.json
sha256sum /var/lib/aqt-d19/definition.json
```

Check: the two cell-list hashes are equal. **Send me** everything from `record` on. Before you go on, I check against the file that:
- the preregistration hash is `<<PREREG_SHA256>>`;
- the engine commit is `<<ENGINE_COMMIT>>`;
- the cell manifest is the 104-cell qualification list with the prescribed counts;
- the image id is the one `build` printed.

**Commit before running (§13 item 6, S16-2):**
- I commit the definition to the repository and push it, and you get the commit id and the blob's SHA-256.
- Then, on the server:

```sh
curl -fsSL https://raw.githubusercontent.com/meedo1985/autonomous-quant-trader/<<DEFINITION_COMMIT>>/<<DEFINITION_PATH>> | sha256sum
sha256sum /var/lib/aqt-d19/definition.json
```

The two hashes must be equal. That proves the committed file is the one that will run. **Do not start step D before both match.**

The commit time alone is weak evidence of the order. The freeze's own checks (qualification object, QO-2) decide what more is needed. Nothing in this sheet replaces them.

## D. Threshold run (several weeks)

```sh
sudo sh d19.sh run threshold
sudo sh d19.sh memwatch
sudo sh d19.sh status
systemctl status aqt-paper --no-pager | head -3
```

`memwatch` takes 10 minutes; it records the run's own memory peak with 2 workers running. **Send me** all three outputs: the run `Up`, a memory peak, and forward paper `active (running)`.

**Weekly check (FS-5).** Run these, and send me the **whole** output:

```sh
sudo sh d19.sh status
systemctl status aqt-paper --no-pager | head -3
```

`status` lists one line per started cell (`<chunks> threshold/<cell id>`). It lists a cell only once it has a chunk. I compare every listed id with the 104 ids of `qualification-cells.json`, the file whose hash you checked in step C. I report any expected id that is missing, any unexpected id, and the chunk counts.

**Finished** when `status` shows `Exited (0)` and my comparison shows all 104 expected ids at `600 threshold/`, and no other `threshold/` line. A count of 104 lines alone is not enough: an unexpected id could stand in for a missing one.

**If `status` shows `Exited` with a code other than 0 (FS-4):** collect, then stop. Do not restart yet:

```sh
sudo sh d19.sh status
sudo docker logs --tail 40 aqt-d19
```

Send me both. A restart (`run threshold`) removes the old container and its log, so collect first. I assess the failure and check that the definition, engine and image are unchanged. Then I tell you whether to resume with `sudo sh d19.sh run threshold`, which continues from the last finished chunk.

## E. Development run (several weeks)

Start it only after D has finished:

```sh
sudo sh d19.sh run dev
sudo sh d19.sh memwatch
sudo sh d19.sh status
systemctl status aqt-paper --no-pager | head -3
```

The weekly check (the whole `status` output), the failure rule and the resume rule are the same as in D, with `dev` in place of `threshold`. **Finished** when `status` shows `Exited (0)` and my comparison shows all 104 expected ids at `24 dev/` and no other `dev/` line.

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
