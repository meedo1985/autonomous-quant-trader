# F-RESTART on the owner's server (commit `0a2957d`), 2026-10-18

The owner ran `paper_update.txt` (RUNBOOK §7, §3, §5) on the server and pasted the output into the Claude Code session. Claude Opus 5.5 (`claude-opus-5-5`) records it here verbatim. The only change is the owner's name in the approval line, replaced by `[owner's name]` because this repository is public.

```
root@aqt-server:/tmp# sudo systemctl stop aqt-paper
root@aqt-server:/tmp# sudo git -C /opt/aqt/app fetch --quiet origin
root@aqt-server:/tmp# sudo git -C /opt/aqt/app checkout --quiet 0a2957d51fee63ee57b52826c07fc1b0f45aa254
root@aqt-server:/tmp# sudo /opt/aqt/app/.venv/bin/pip install --quiet --no-compile -e /opt/aqt/app
root@aqt-server:/tmp# sudo chmod -R go-w /opt/aqt
root@aqt-server:/tmp# sudo install -m 644 /opt/aqt/app/deploy/aqt-paper.service /etc/systemd/system/ && sudo systemctl daemon-reload
root@aqt-server:/tmp# sudo /opt/aqt/app/.venv/bin/python -B /opt/aqt/app/scripts/deployment.py approve 0a2957d51fee63ee57b52826c07fc1b0f45aa254 --by "[owner's name]" --statement "Reviewed and merged PR 65; approved for this server"
Approved 0a2957d51fee63ee57b52826c07fc1b0f45aa254.
root@aqt-server:/tmp# sudo -u aqt /opt/aqt/app/.venv/bin/python /opt/aqt/app/scripts/deployment.py check
May run: 0a2957d51fee63ee57b52826c07fc1b0f45aa254, source 0c1005f1dd401310a9d578fee4cc0d43e525bb09feec2c81782b050427459665.
root@aqt-server:/tmp# sudo systemctl start aqt-paper
root@aqt-server:/tmp# sleep 5; journalctl -u aqt-paper --since -2min --no-pager | grep -v '"l02"' | tail -5
Oct 18 17:22:21 aqt-server systemd[1]: Started aqt-paper.service - aqt forward paper trading.
Oct 18 17:22:22 aqt-server python[329043]: waiting until 2026-10-18 18:01 UTC for the first step
```

The approved commit is the one the server runs. A start at 17:22:21 waits for 18:01, as `first_slot` specifies.

**Pending:** the first step after 18:01, to be checked with `journalctl` and `systemctl status`.
