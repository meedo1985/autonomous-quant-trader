# Forward paper: L-02 count crash on the server (2026-10-05)

## What the owner saw

On the owner's server (main `6342c9a`, service `aqt-paper`), `journalctl` at
2026-10-05 05:01Z showed the process exiting with status 1 after every hourly
step since the first order, and `systemd` restarting it (restart counter 5):

```
File "/opt/aqt/app/scripts/run_forward_paper.py", line 108, in step
  "l02": l02_count(account.journal, series).as_mapping(),
File "/opt/aqt/app/src/aqt/app/forward.py", line 224, in snapshots
  out.append((at, expected_balances(_local(state))))
File "/opt/aqt/app/src/aqt/execution/reconcile.py", line 139, in expected_balances
  raise ValueError("an order with an unknown outcome has no expected balance")
```

## Effect

- Each hourly step finished before the crash: the cursor shows `START`/`END`
  pairs with `refused: false` for every hour 00:00Z-05:00Z, and the state
  journal was saved. Trading decisions were not lost.
- The hourly report line (`L-02` count + run report) was never appended or
  printed, and each hour ended with an unplanned exit and restart.
- Paper only; no money is involved.

## Cause

A step saves the account state after an order is sent and before its outcome is
known (T23-09: the sent order is recorded with outcome `None`). `snapshots()`
read every journal entry and called `expected_balances()` on each, which
refuses an unknown outcome. The Task 29 tests never called `l02_count` after a
step that traded, so this was not caught.

## Repair

`snapshots()` skips a snapshot with an order of unknown outcome. The snapshot
recording the outcome follows within the same step, so the daily valuation
(last snapshot at or before each 00:00Z) loses at most the minutes inside one
step, and only uses balances whose orders are all known. A journal whose last
entry is in flight (a crash mid-step) is already refused by `resumed_venue`.

Test: `test_l02_count_skips_snapshots_with_an_order_in_flight`
(`tests/integration/test_forward_paper.py`) runs ordinary hourly steps, asserts
an in-flight snapshot exists, and calls `l02_count`. It failed with the server's
`ValueError` before the repair and passes after.

## Checks

- `.venv/Scripts/python.exe -m pytest tests/integration/test_forward_paper.py -q`: 21 passed.
- `ruff check src tests scripts`: all checks passed; `ruff format`: applied to the two changed files.
- `mypy src`: no issues in 53 source files.
- `lint-imports`: 6 kept, 0 broken.
- Full suite `.venv/Scripts/python.exe -m pytest -q`: 1787 passed, 9 skipped (6 min 10 s).
- Frozen artifacts: `git diff --stat main` touches none of `docs/ protocols/ schemas/ specs/ FROZEN_HASHES.json`.

## Still required

`src/aqt/app/forward.py` is forward-paper runtime code (Task 29 had a section 16
review), so: a different-model review, the owner's yes/no walkthrough, a PR
merged on the owner's word, then the owner approves the new commit and
re-installs it on the server (`deploy/RUNBOOK.md`, update section).
