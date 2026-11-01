# Paper server deployment of main f715dfe (PR #80, #81), 2026-11-01

The owner ran `Desktop\AQT deploy PR80.txt` Parts 1-3 on the paper server and
pasted the output; recorded here verbatim where quoted.

## Part 1 (read only)

- `/opt/aqt/app` HEAD: `7290f29845e8c4b2c9db5dcf0c76fba21ca6c016`
- last approval: sequence 3, commit `7290f29...`, approved_by `Mahmoud`,
  recorded 2026-10-24T12:14:26Z, entry_hash `60c5bebf...1565`.

Check before Part 2 (Claude): `7290f29` is an ancestor of `f715dfe`. Between
them the only change reaching the paper service is `deploy/aqt-paper.service`
(+`Environment=PYTHONUNBUFFERED=1`); `src/` and the config are unchanged; the
rest is calibration/freeze code (separate `/opt/aqt-d19`), docs and tests.

## Part 2

```
Approved f715dfe16e0da21e910296b52b999f0f13f942cb.
May run: f715dfe16e0da21e910296b52b999f0f13f942cb, source 673b2108bd10b534160f9f5621420f6c5a329ea4f23fb23c422dbf7344d02aa0.
grep -c PYTHONUNBUFFERED -> 1
Active: active (running) since Sun 2026-11-01 10:13:58 UTC
```

One stray line was pasted as a command (`deployment.py check must print ...`,
`command not found`); it ran nothing.

## Part 3 (journal after the first step)

```
Nov 01 10:13:58 aqt-server systemd[1]: Started aqt-paper.service - aqt forward paper trading.
Nov 01 10:13:59 aqt-server python[734123]: waiting until 2026-11-01 11:01 UTC for the first step
Nov 01 11:01:04 aqt-server python[734123]: {"at": "2026-11-01T11:01:00.000121+00:00", "l02": {"effective_decisions": 27.0, ... "target": 240}, "report": {... "final_mode": "RUNNING", "health_breach_hours": 0, ... "refused": [], "run_id": "forward-1-20261101T1000Z", ...}}
```

The last line of `forward_reports.jsonl` carries the same `at`
(`2026-11-01T11:01:00.000121+00:00`).

## Result

PASS: the report line reached the journal at 11:01:04, when printed (PR #80's
purpose); the step for the 10:00 hour ran; mode RUNNING, 0 health breaches,
nothing refused; L-02 27/240.
