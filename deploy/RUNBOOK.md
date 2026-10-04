# Server runbook (roadmap 2 Task 30)

For the owner. You run every step; the AI never logs into the server and
never sees its address or any credential. Owner answers: Ubuntu (Q30-1),
only the commit you approve runs (Q30-2), you update by hand (Q30-3). A
GitHub test machine repeats steps 2, 3 and a refused step 5 on every change
(`.github/workflows/ci.yml`, job `runbook-dry-run`).

Who owns what: the code in `/opt/aqt/app`, its history and its Python belong
to root, and only you (with `sudo`) change them. The app runs as its own
account `aqt`, which can read and run the code but not change it, and writes
only to `/var/lib/aqt`. So the app can never approve or swap its own code.

This runbook authorizes nothing by itself: no real money and no Binance keys.
Forward paper trading (Task 29) was authorized on 2026-10-04 with the baseline
only (`review/roadmap/OWNER_ANSWER_QC_2026-10-04.md`): the service fetches
Binance's public hourly bars and trades paper money on the simulator.

## 1. Rent and secure the server

- Ubuntu 24.04 LTS, the smallest plan (about $5-6/month). Record its fixed IP
  in your own notes (D-7), not in the repository.
- Log in with an SSH key, not a password. Then:

```sh
sudo apt-get update && sudo apt-get upgrade -y
sudo ufw allow OpenSSH && sudo ufw enable
```

## 2. Install a reviewed commit

Choose a commit on `main` that you merged (GitHub shows its full
40-character id). Then:

```sh
curl -fsSLO https://raw.githubusercontent.com/meedo1985/autonomous-quant-trader/<commit>/deploy/install.sh
sudo sh install.sh https://github.com/meedo1985/autonomous-quant-trader.git <commit>
```

This creates the app's own account `aqt` (no login, not root), puts the code
in `/opt/aqt/app` (owned by root), and installs the service. It does not
start anything.

## 3. Approve the commit

Only root can write the record; the app can only read it:

```sh
sudo /opt/aqt/app/.venv/bin/python -B /opt/aqt/app/scripts/deployment.py approve <commit> --by "Your Name" --statement "Reviewed and merged; approved for this server"
sudo -u aqt /opt/aqt/app/.venv/bin/python /opt/aqt/app/scripts/deployment.py check
```

The check prints `May run: <commit>`. Any changed, added or hidden file in
`/opt/aqt/app` makes it print `Refused: ...` instead, and the app refuses to
start for the same reason.

## 4. Telegram and data

Store the bot credential in a file only `aqt` can read (D-8). The second
command opens an editor: type the chat id on the first line and the token
on the second, save, close. Nothing appears on screen or in the shell
history.

```sh
sudo install -o aqt -g aqt -m 600 /dev/null /etc/aqt/telegram
sudo -u aqt nano /etc/aqt/telegram
sudo -u aqt sh -c 'cd /var/lib/aqt && /opt/aqt/app/.venv/bin/python /opt/aqt/app/scripts/alert_channel.py test'
sudo -u aqt sh -c 'cd /var/lib/aqt && /opt/aqt/app/.venv/bin/python /opt/aqt/app/scripts/alert_channel.py ack <code>'
sudo -u aqt sh -c 'cd /var/lib/aqt && /opt/aqt/app/.venv/bin/python /opt/aqt/app/scripts/download_market_data.py --root data/raw'
```

Repeat `test` and `ack` at least every 7 days (D-2).

## 5. Start, and start on boot

```sh
sudo systemctl start aqt-paper
sudo systemctl enable aqt-paper
systemctl status aqt-paper
```

A refused start (exit code 2) is not retried; a crash is, and the app then
refuses by itself while an earlier error is unresolved (Task 27).

## 6. Logs

- Screen output: `journalctl -u aqt-paper`.
- Hourly reports with the `L-02` count, operations log, incidents and the
  account's saved state: `/var/lib/aqt/data/forward/account-1/`.
- The live bar store: `/var/lib/aqt/data/live/BTCUSDT-1h.jsonl`.
- A start refused because the code is not the approved commit:
  `/var/lib/aqt/data/forward/deployment_refusals.jsonl`.
- Telegram tests: `/var/lib/aqt/data/processed/alerts/`.
- Approvals: `/etc/aqt/deployments.jsonl`.

## 7. Update to a newer commit

Only when you decide, and only to a commit you merged:

```sh
sudo systemctl stop aqt-paper
sudo git -C /opt/aqt/app fetch --quiet origin
sudo git -C /opt/aqt/app checkout --quiet <commit>
sudo /opt/aqt/app/.venv/bin/pip install --quiet --no-compile -e /opt/aqt/app
sudo chmod -R go-w /opt/aqt
sudo install -m 644 /opt/aqt/app/deploy/aqt-paper.service /etc/systemd/system/ && sudo systemctl daemon-reload
```

Then step 3 (approve, check) and `sudo systemctl start aqt-paper`. To go
back, do the same with the previous commit; every approval stays in the
record.

## 8. Stop

```sh
sudo systemctl stop aqt-paper
sudo systemctl disable aqt-paper
```
