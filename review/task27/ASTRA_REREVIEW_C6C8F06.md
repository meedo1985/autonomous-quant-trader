# Task 27 Astra re-review of `c6c8f06` — text-only (FIX; A27-13, A27-14 blockers)

Date: 2026-10-01. Requested by the owner ("Make next").

- Invocation: `codex exec -s read-only -m gpt-6-astra -` (codex-cli 0.154.0).
- **Text-only**, as for the earlier Task 27 records. Attached verbatim from
  `c6c8f06`: `ASTRA_REREVIEW_BCA6984.md`, `LOCAL_REPORT.md`, `DESIGN.md`,
  `OWNER_ANSWERS.md`, `state.py`, `paper_loop.py`, `live_bars.py`, `safety.py`,
  and `git diff bca6984 c6c8f06 -- src scripts tests`. Prompt bundle SHA-256:
  `7f3f785cf3b2f7e220be27fe31b28df97755f3ab4140af574f037d162d57a9a7`.
- The reviewer ran no command. The reviewer's final message follows verbatim.

---

**Verdict: FIX.**

Reviewer: **GPT-6 Astra**, independent different-model reviewer of implementation by Claude Opus 5.5. Reviewed supplied commit **`c6c8f06`**, branch `task27-persistent-state`, draft PR **#37**.

This review was **text-only**. I ran no commands and accessed no filesystem, network, credentials, exchange APIs, or confirmation/lockbox data. Commit identity was not independently verified. The orchestrator reports **1692 passed, 4 skipped**, clean ruff, formatting, mypy `src scripts`, six import contracts, and frozen verification PASS; I did not verify those results. Local skills were not attached or read. This final message is the review record; I have not committed it.

### Repair assessments

| Finding | Assessment | Evidence |
|---|---|---|
| **A27-8** | **CORRECT** | `end_halt` now returns `True` on every path that performs reconciliation: success, failed reconciliation, and rejected override artifacts. The caller ends that hour in all three cases. `False` means immediate rejection outside HALT, where no reconciliation ran and continued processing is appropriate. Subsequent saves and skipped hours respect `busy_until`. |
| **A27-9** | **INCOMPLETE** | The pre-send pending-buy scenario is repaired: the saved hour uses pre-order balances and later hours use reconciled balances. Pending sells receive the corresponding improvement. However, the assumption that **every** saved snapshot contains pre-order balances is false: ordinary hour-end snapshots contain post-order balances. Inclusive replay can invent a peak using those holdings: **A27-13**. |
| **A27-10** | **INCOMPLETE** | `_replay` now reconstructs re-arming and detects a missed firing. Raising that firing at `ready` correctly avoids backdating and enters FLATTEN from RUNNING under S-4. However, the caller unconditionally disarms the stop even when a subsequent replayed recovery re-armed it. A new fall in the first live hour then goes unrecorded: **A27-14**. |
| **A27-11** | **INCOMPLETE** | The exact `1,1,2` scenario now refuses without writing. But the code checks only the first continuity break. A forward gap followed by a duplicate or reordered bar still commits a prefix from a malformed reply: **A27-15**. |
| **A27-12** | **CORRECT** | Every journal entry now passes both the record-type check and `AccountState.from_mapping`. A malformed earlier snapshot cannot be hidden by a valid final snapshot. The supplied malformed `attempts` case is rejected by the round-trip comparison. |
| **T27-13** | **CORRECT** | Both live processing and replay suppress LOSS_STOP firing in FREEZE without spending an armed latch. Peak updates and re-arming on recovery above the line remain consistent between the two paths. FREEZE_EXIT still reconciles, leads only to HALT, and ends its hour. |

The successful HALT override still resets peak to reconciled equity and arms the stop, implementing Q27-1/Q27-2 when the completion-time valuation is available. Its hour ends before the loss check, so the old breach does not immediately undo a successful reset. A missed incident raised at startup must be included in the override’s incident set; refusal of an override naming only older incidents is appropriate. Reconciliation at exactly the new HALT entry time also fails the controller’s existing strict “after entry” requirement.

From RUNNING, a replayed missed firing enters FLATTEN at `ready`; the first eligible live hour reaches `tick`, unless an owner HALT, health failure, or other existing protective condition intervenes. The supplied pending-buy regression uses an owner HALT and therefore does not test that selling path.

### A27-13 — BLOCKER — Inclusive replay can invent a peak from post-order holdings

**Location:** `src/aqt/app/paper_loop.py:708` (`_replay` inputs), `:1195` (`held = saved if hour == first else confirmed`).

The journal does not distinguish a pre-send snapshot from an hour-end snapshot. `_replay` nevertheless treats the saved balances as the holdings applicable before that hour’s orders.

Concrete scenario:

1. Before decision hour H, the account holds 100 USDT and peak is 100.
2. The preceding bar closes at 120.
3. During H, a buy fills for one BTC at 100.
4. Reconciliation succeeds; the hour-end snapshot records one BTC, no cash, peak 100, and no outstanding orders.
5. The process restarts at H+1; the H bar closes at 90.
6. Replay values the saved hour as **one BTC × 120**, inventing peak 120.
7. The first live valuation of 90 breaches the invented 96 line. The actual retained peak of 100 gives an 80 line and no breach.

No unknown fill is necessary. A favorable buy fill below the preceding mark is sufficient. The saved peak is no longer preserved faithfully, and RUNNING can enter an unwarranted FLATTEN.

The fix must account for snapshot phase or equivalent evidence; using saved holdings unconditionally for the saved hour cannot establish its historical equity.

### A27-14 — BLOCKER — Startup discards the replay’s final re-armed latch

**Location:** `src/aqt/app/paper_loop.py:720–728`, especially `stop_armed = False` after emitting the missed firing.

Concrete scenario, in HALT throughout:

| Decision hour | Equity | Required bookkeeping |
|---|---:|---|
| H, replayed | 70 | Peak 100, armed stop fires and disarms |
| H+1, replayed | 100 | Stop re-arms |
| H+2, first live hour | 70 | New fall fires again |

`_replay` correctly returns peak 100, **armed=True**, and the first missed firing at H. Startup records that missed firing at `ready`, then overwrites the returned latch with `False`. The live H+2 breach consequently opens no incident.

HALT remains effective, but one of two distinct armed breaches is lost. This is the nearby first-live-hour case missing from the added latch test.

Recording a historical firing must preserve subsequent replayed latch transitions.

### A27-15 — NON-BLOCKING — A duplicate after a forward gap still commits a prefix

**Location:** `src/aqt/data/live_bars.py:446–454`, first-break classification and prefix append.

Concrete scenario: the store contains hour 0; the reply contains **1,3,3**.

The first break is classified as a forward gap. Hour 1 is committed before the remainder is refused. The duplicate later in the reply is never considered when deciding whether to write the prefix.

Similarly, **1,3,2** commits hour 1 despite the reordered suffix. This contradicts the documented whole-reply refusal for duplicates and reordered bars. It does not introduce duplicate stored bars or bridge the gap, so its severity remains non-blocking.

A pure forward-gap reply such as **1,3,4** should retain the intended prefix behavior.

### Exact reproduction command

**Not reproduced (sandbox unavailable).** The following command independently exercises A27-13, A27-14, and A27-15 using synthetic inputs and temporary directories. It collects failures so the first one does not prevent the others from running.

```bash
PYTHONPATH=. python - <<'PY'
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal as D
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from aqt.app.state import AccountDir
from aqt.data.bars import Bar
from aqt.data.live_bars import LiveBarError, LiveBarStore, fetch_new_bars
from aqt.execution.safety import Mode, Trigger
from tests.integration.test_paper_recovery import (
    START, HOUR, ONE_BTC, _Venue, _seed, _priced, _one_hour, _losses,
)

failures = []

with TemporaryDirectory() as directory:
    root = Path(directory)

    # A27-13: valid post-buy hour-end state; no unsettled order remains.
    account = AccountDir(root / "post_buy")
    _seed(account, START, Mode.RUNNING, ONE_BTC, "100")
    restart = START + HOUR
    _one_hour(
        account,
        _Venue(ONE_BTC),
        _priced({START - HOUR: 120.0, START: 90.0}),
        restart,
        commands={restart: Trigger.OWNER_HALT},
    )
    saved = account.journal.load()
    assert saved is not None
    if saved.peak != D(100) or _losses(account) != 0:
        failures.append((
            "A27-13",
            {"peak": str(saved.peak), "losses": _losses(account)},
        ))

    # A27-14: missed firing, missed re-arm, then a fresh live breach.
    account = AccountDir(root / "rearmed")
    _seed(account, START, Mode.HALT, ONE_BTC, "100")
    _one_hour(
        account,
        _Venue(ONE_BTC),
        _priced({
            START - HOUR: 70.0,
            START: 100.0,
            START + HOUR: 70.0,
        }),
        START + 2 * HOUR,
    )
    if _losses(account) != 2:
        failures.append(("A27-14", {"losses": _losses(account)}))

    # A27-15: the duplicate/reordering occurs after the first forward gap.
    t = datetime(2026, 9, 29, tzinfo=UTC)
    h = timedelta(hours=1)
    now = t + 5 * h

    def ms(at):
        return int(at.timestamp() * 1000)

    def row(n):
        opened = ms(t + n * h)
        return [
            opened, "100", "100", "100", "100", "1",
            opened + 3_600_000 - 1,
        ]

    for label, hours in (
        ("duplicate", (1, 3, 3)),
        ("reordered", (1, 3, 2)),
    ):
        store = LiveBarStore(root / f"{label}.jsonl", "BTCUSDT")
        store.append((Bar(t, 100.0, 100.0, 100.0, 100.0, 1.0),))
        before = store.path.read_bytes()
        replies = iter([
            {"serverTime": ms(now)},
            [row(n) for n in hours],
        ])

        def transport(request):
            return SimpleNamespace(
                status=200,
                body=json.dumps(next(replies)).encode(),
            )

        try:
            fetch_new_bars(
                transport, store, "BTCUSDT", now, timedelta(seconds=5)
            )
        except LiveBarError:
            pass
        else:
            failures.append(("A27-15", label, "reply accepted"))

        if store.path.read_bytes() != before:
            failures.append(("A27-15", label, "prefix committed"))

assert not failures, failures
PY
```

The existing repair tests should also be rerun with this exact command, **not reproduced (sandbox unavailable)**:

```bash
PYTHONPATH=. python -m pytest -q tests/integration/test_paper_recovery.py tests/unit/test_account_state.py tests/unit/test_live_bars.py
```

**Task 27 does not yet meet DESIGN.md section 5 as a whole.** A27-13 demonstrates that restarting can change the loss-stop peak incorrectly; A27-14 leaves the path-dependent latch recovery incomplete. The attached code supports the intended marker refusal, incident retention, and protective-mode resume mechanisms, but this text-only review does not independently establish the universal kill-at-every-step acceptance claim. T27-12’s drill comparison also remains outstanding in the supplied report.

**FIX required for A27-13 and A27-14; A27-15 needs repair or an explicit disposition.**