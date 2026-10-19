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

## The first step after the wait (checked at about 18:06 UTC)

`journalctl --since "2026-10-18 17:55" --until "2026-10-18 18:10" | grep -v '"l02"'` printed `-- No entries --`. That check could not show a normal step: a step's only screen line is its report, which contains `"l02"` and is filtered out, and the service's stdout reaches the journal in blocks (on 2026-10-18 the report lines of earlier steps appeared together at 11:01:02). `systemctl status` showed `Active: active (running) since Sun 2026-10-18 17:22:21 UTC; 44min ago`; a refused step would have stopped the service.

The step record on disk, verbatim (each line cut at 300 characters by the command):

```
root@aqt-server:/tmp# sudo tail -n 2 /var/lib/aqt/data/forward/account-1/forward_cursor.jsonl | cut -c1-300
{"entry_hash":"8a1dbe2337fa211b8aa7910c8213174767f24ede91be52d98f7b353037ddba93","payload":{"end":"2026-10-18T18:00:00+00:00","start":"2026-10-18T17:00:00+00:00","step":"START"},"previous_hash":"9904b553f54df0f9b2ecbfeba20caa18b688e22311d8c51fbbaa51504be4180b","record_type":"aqt.app.forward_cursor.v
{"entry_hash":"121dbc0e5610960189a7a6e3fe23820af9a7f36dedca43845b6f0de487a2bd1b","payload":{"refused":false,"step":"END"},"previous_hash":"8a1dbe2337fa211b8aa7910c8213174767f24ede91be52d98f7b353037ddba93","record_type":"aqt.app.forward_cursor.v1","recorded_at_utc":"2026-10-18T18:01:00Z","sequence":6
root@aqt-server:/tmp# sudo tail -c 700 /var/lib/aqt/data/forward/account-1/forward_reports.jsonl
95a1e52b25dc3d2c8f2683878b49327ae", "data_manifest_hash": "12dce0bb6174a6dfda4540ba93e70f9ae3ae02f149d297ff97ace89a59ee468e", "events": 2, "final_balances": {"BTC": "0.11519", "USDT": "18.92443642790740705860511"}, "final_mode": "RUNNING", "governor_refusals": {"INSIDE_REBALANCE_BAND": 1}, "health_breach_hours": 0, "hours": 1, "note": "Bar count is not sample size. Paper run on the exploration partition against the simulator; no edge, Sharpe, or promotion claim is made.", "orders_sent": 0, "predictor": "VOL_TARGET_BUY_AND_HOLD", "protocol_hash": "d22efb8989cb31a1d673000bba1e69baf5e0965bb400a8798aa966a3035d8b26", "refused": [], "run_id": "forward-1-20261018T1700Z", "scheduled_decisions": 0}}
```

So the first step after the start ran at the 18:01 slot. Its window was 17:00 to 18:00 (one hour), its `END` is `refused: false`, and its report (run `forward-1-20261018T1700Z`) shows `RUNNING` with `refused` empty. The START line's own time is cut off by `cut -c1-300`; the END is recorded at `2026-10-18T18:01:00Z`.

**Note for later checks:** use the step cursor and the report file, not `journalctl` with the `"l02"` filter.
