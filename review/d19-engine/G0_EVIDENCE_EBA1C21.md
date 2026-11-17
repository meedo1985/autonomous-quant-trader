# Step G0 redo at eba1c21 (FREEZE_HELDOUT.md FP2 (d)), 2026-11-01

The owner ran `Desktop\AQT G0 redo eba1c21.txt` on the server and pasted the
output (verbatim):

```
root@aqt-server:~# sudo git -C /opt/aqt-d19/build fetch --quiet origin
root@aqt-server:~# sudo git -C /opt/aqt-d19/build checkout --quiet eba1c213a183233460231cf12853d7207fee6f53
root@aqt-server:~# sudo chmod -R go-w /opt/aqt-d19/build
root@aqt-server:~# sudo git -C /opt/aqt-d19/build rev-parse HEAD
eba1c213a183233460231cf12853d7207fee6f53
root@aqt-server:~# sudo git -C /opt/aqt-d19/app rev-parse HEAD
eeaa7282e3b7c87790c162d679016c290d5f4ea5
root@aqt-server:~# sudo git -C /opt/aqt-d19/build remote get-url origin
https://github.com/meedo1985/autonomous-quant-trader.git
root@aqt-server:~# sudo git -C /opt/aqt-d19/build --no-optional-locks status --porcelain --untracked-files=all
root@aqt-server:~# sudo find /opt/aqt-d19/build \( ! -user 0 -o -perm /022 \) -print -quit
```

Result: **PASS**. The build checkout is the full commit `eba1c21` (main after
PR #81 and PR #82), unmodified, root-owned and not group/other-writable, with the
GitHub origin; the development run's checkout `/opt/aqt-d19/app` is unchanged at
`eeaa728`. Replaces the 2026-10-25 installation at `ed0bfbf` (`G0_EVIDENCE.md`) as
FP2 (d)'s evidence. At `eba1c21`, `screen.py` is `e6ba5ac5...` as listed in
`FREEZE_REVIEWS.json`, and `d19.sh freeze` runs T1b first (PR #82; T1b passed in the
pinned image on CI run 41304582247).
