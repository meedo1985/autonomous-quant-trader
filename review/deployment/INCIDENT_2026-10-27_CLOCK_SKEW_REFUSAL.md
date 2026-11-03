# Incident: one refused hour in forward paper, 2026-10-27 14:01Z

Status: closed, no repair. Recorded 2026-10-30 from the owner's Telegram
alerts and server output (owner-run, read-only commands). The server address
and login source are deliberately not recorded.

## Alerts

```
CRITICAL STALE_DATA at 2026-10-27 14:01:00Z
refused: clock skew -1 day, 23:59:51.674139 exceeds 0:00:05; nothing fetched

CRITICAL LOOP_LAG at 2026-10-27 15:01:00Z
missed_hours: 1
first_missed: 2026-10-27T13:00:00+00:00
last_missed: 2026-10-27T13:00:00+00:00
note: run late, as a replay would run them
```

`-1 day, 23:59:51.674139` is Python's form of a timedelta of -8.33 s: local
time minus Binance server time.

## Server evidence (2026-10-30 ~10:07Z)

- `timedatectl`: `System clock synchronized: yes`, `NTP service: active`, UTC.
- `journalctl -u systemd-timesyncd -u chrony` 2026-10-27 12:00-16:00: no entries
  (no clock step or resync logged).
- `journalctl -u aqt-paper` around the alert:
  - `Oct 27 14:01:08 ... {"at":"2026-10-27T14:01:00.000139Z", ... "kind":"STALE_DATA" ...}`
  - `Oct 27 15:01:02 ... {"at":"2026-10-27T15:01:00.000131Z", ... "kind":"LOOP_LAG" ...}`
- `grep -c "clock skew"` over the aqt-paper journal since 2026-10-27: `1`.

## Cause

`scripts/run_forward_paper.py` reads `now` before calling `fetch_new_bars`,
and `src/aqt/data/live_bars.py` computes `skew = now - server_now` after the
`/api/v3/time` request returns. Request latency therefore counts as skew.
The step began at 14:01:00.000 and its alert was journaled at 14:01:08, an
~8 s delay matching the -8.33 s "skew"; the next step journaled 2 s after its
start. With the clock synchronized and no resync logged, the evidence points
to a slow Binance time response (or network stall), not a clock error. This
is an inference from timestamps; the request duration itself is not logged.

## Effect

Designed behaviour, no data loss: the 14:01 step fetched and ran nothing; the
15:01 step reported the 13:00 decision hour as missed and ran it late exactly
as a replay would. Balances in the surrounding reports are unchanged
(BTC 0.11519, USDT 18.924...); no order was involved.

## Decision

No code change now (one occurrence in about three days). If it recurs, the
proposed repair is to measure the request round trip and exclude it from the
skew (for example compare against the midpoint of local times before and after
the request). That is a live-path change and needs review and the owner's
section 16 PR review before merge.

## Side observation

The hourly report lines (stdout) for 2026-10-26 00:01Z through 2026-10-27
13:01Z were all journaled at 14:01:08: stdout is block-buffered under
systemd, so journal timestamps of report lines are flush times, not event
times. Alerts and the state journal are unaffected. Possible later fix:
`PYTHONUNBUFFERED=1` in `deploy/aqt-paper.service` (a deployment change; same
review route).
