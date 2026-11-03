# Step G0 evidence: build checkout installed (FP2 (d))

- Run by the owner on the server (`root@aqt-server`), 2026-10-25, before 09:57 local
  (screenshot `Screenshot 2026-10-25 095716.png`, read by Claude Opus 5.5).
  Transcribed below from the screenshot; the login banner (addresses, last-login
  source) is left out on purpose.
- Sheet: `deploy/calibration/FREEZE_HELDOUT.md` step G0, build commit
  `ed0bfbfa7a544f6e925d72d77734007a51d2c77e` (PR #77 merge).

```text
root@aqt-server:~# sudo git clone --quiet https://github.com/meedo1985/autonomous-quant-trader.git /opt/aqt-d19/build
root@aqt-server:~# sudo git -C /opt/aqt-d19/build checkout --quiet ed0bfbfa7a544f6e925d72d77734007a51d2c77e
root@aqt-server:~# sudo chmod -R go-w /opt/aqt-d19/build
root@aqt-server:~# sudo git -C /opt/aqt-d19/build rev-parse HEAD
ed0bfbfa7a544f6e925d72d77734007a51d2c77e
root@aqt-server:~# sudo git -C /opt/aqt-d19/app rev-parse HEAD
eeaa7282e3b7c87790c162d679016c290d5f4ea5
root@aqt-server:~# sudo git -C /opt/aqt-d19/build remote get-url origin
https://github.com/meedo1985/autonomous-quant-trader.git
root@aqt-server:~# sudo git -C /opt/aqt-d19/build --no-optional-locks status --porcelain --untracked-files=all
root@aqt-server:~# sudo find /opt/aqt-d19/build \( ! -user 0 -o -perm /022 \) -print -quit
root@aqt-server:~#
```

Checks against the sheet: first `rev-parse` is the build commit; second is
`eeaa728...`; origin is the repository's GitHub address; `status` and `find`
print nothing. **All pass. FP2 (d) holds from this record.** `/opt/aqt-d19/app`
was not touched.
