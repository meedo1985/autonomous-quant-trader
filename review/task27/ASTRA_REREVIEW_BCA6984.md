# Task 27 Astra re-review of the A27 repairs at `bca6984` — text-only (FIX; A27-8..A27-10 blockers)

Date: 2026-10-01. Requested by the owner ("Make next").

- Invocation: `codex exec -s read-only -m gpt-6-astra -` (codex-cli 0.154.0).
- **Text-only**, as for `ASTRA_REVIEW_2B94313.md`. Attached verbatim from
  `bca6984`: that record, `LOCAL_REPORT.md`, `OWNER_ANSWERS.md`, `state.py`,
  `paper_loop.py`, `live_bars.py`, `fetch_live_bars.py`, `reconcile.py`, and
  `git diff 2b94313 bca6984 -- src scripts tests`. Prompt bundle SHA-256:
  `f326350da0a23be02be33ebbebb5e253d1241dfc709867ccb95d79f6314cadd0`.
- The reviewer ran no command. The reviewer's final message follows verbatim.

---

**Verdict: FIX.**

Reviewer: **GPT-6 Astra**, independent different-model reviewer of implementation by Claude Opus 5.5. Reviewed supplied commit **`bca6984`**, branch `task27-persistent-state`, draft PR **#37**, against the attached `2b94313` review and repair diff.

This review was **text-only**. I ran no commands and accessed no filesystem, network, credentials, exchange APIs, or confirmation/lockbox data. Commit identity and validation results were not independently verified. The orchestrator reports **1686 passed, 4 skipped**, clean ruff, formatting, mypy and six import contracts, and frozen verification PASS. Skills, the ledger implementation, and the current safety-controller implementation were not attached; I do not claim to have independently reviewed them. This final message is the review record; I have not committed it.

All reproduction commands below are **not reproduced (sandbox unavailable)**. They use synthetic data and temporary directories.

| Finding | Assessment | Evidence |
|---|---|---|
| **A27-1** | **INCOMPLETE** | Hourly and final saves now use `max(done, busy_until)`; SHUTDOWN uses `max(config.end, busy_until)`. Successful delayed recovery therefore fixes the original backdated-save case. However, an unsuccessful override returns to the original hour after waiting and can emit a loss-stop event at that earlier time: **A27-8**. |
| **A27-2** | **CORRECT** | Startup and successful recoveries apply `_last_increase()` before discarding resolved orders. It takes the latest filled-buy decision time, preserves a later existing value, ignores sells, zero fills and confirmed absence, and is idempotent for an order whose bookkeeping already ran. |
| **A27-3** | **INCOMPLETE** | Inclusive replay repairs the supplied constant-holdings, armed-stop example. It does not reconstruct holdings after an unresolved fill, and it replays only the maximum equity—not the latch transitions: **A27-9**, **A27-10**. |
| **A27-4** | **CORRECT** | For a forward gap, the fetch stores the contiguous prefix, refuses the remaining batch, and explicit `first_missing` must match the resulting store position. Normal page advancement starts after the last accepted bar. A nearby duplicate-response regression remains: **A27-11**. |
| **A27-5** | **CORRECT** | Exact, mutually exclusive row-key sets reject hybrid rows. Reading constructs `GapRecord`, enforcing nonblank string actor/statement, aligned UTC endpoints, UTC record time and increasing endpoints. Placement and symbol checks remain. The owner’s “Name + statement” answer resolves the provenance question; cryptographic provenance is not required by that answer. |
| **A27-6** | **INCOMPLETE** | Round-trip comparison rejects the disclosed string/truncated pairs, unknown fields and identifier coercions in the loaded snapshot. Every entry’s record type is checked. Earlier snapshot payloads still escape schema validation: **A27-12**. |
| **A27-7** | **CORRECT** | `STATE_RESUMED` now preserves HALT or FREEZE during replay, including repeated crashes before the subsequent snapshot. It remains invalid in RUNNING or FLATTEN. |

The successful override’s reset now uses reconciled balances and the close corresponding to reconciliation completion when that bar exists. Replaying its saved hour uses that same close, so inclusion alone does not resurrect the pre-reset peak. However, the broad exception handler still falls back to the pre-wait mark when the completion bar is unavailable; the supplied delayed-recovery test does not exercise that boundary or assert the reset value.

**A27-8 — BLOCKER — A refused delayed override continues processing with the old timestamp.**

Locations: `src/aqt/app/paper_loop.py:795` (`end_halt` rejection handler), `:895` (override call and subsequent loss-stop branch).

Concrete scenario:

1. HALT holds one BTC, peak 120, current equity 90, stop armed.
2. Override reconciliation starts at `START` and finishes two hours later.
3. The override lacks its written record, so it is refused at the completion time.
4. `end_halt()` returns `False`.
5. The loop processes the already-computed breach and calls `controller.trigger(LOSS_STOP, decision_time, ...)` at `START`.

The operations log moves backwards after the override refusal. Updating the final snapshot timestamp does not repair the intervening events. A failed reconciliation at the override also returns through this same fallthrough.

The rest of the hour must respect completion of the attempted recovery even when HALT does not end.

**A27-9 — BLOCKER — Replaying saved holdings misses peaks earned by a buy resolved at startup.**

Locations: `src/aqt/app/paper_loop.py:702` (replay inputs), `:1138` (`_equities`).

Concrete scenario:

1. The pre-send snapshot contains 100 USDT, zero BTC, peak 100 and an unknown pending buy.
2. The buy fills for one BTC at 100; the process dies before bookkeeping.
3. While down, BTC closes at 120 and then 90.
4. Startup correctly reconciles the buy and restores `last_increase`.
5. Equity replay nevertheless values every missed hour using **100 USDT**, because it receives `resumed.record.balances`.
6. Current equity is 90 against a reconstructed peak of 100, so the required breach below 96 is missed.

The inverse problem exists for sells: replay continues valuing assets that the account already sold, potentially inventing a later peak. Correct recovery requires the holdings applicable to each valuation, or a refusal when those valuations cannot be established.

**A27-10 — BLOCKER — Replay does not restore re-arming of the loss-stop latch.**

Locations: `src/aqt/app/paper_loop.py:698–705`, `:1138` (`_equities` returns values used only for `max`).

Concrete scenario:

1. Saved HALT state has peak 100 and `stop_armed=False` after a previous breach.
2. A missed decision hour values equity at 100. The ordinary loop would re-arm the stop.
3. The next hour values equity at 70.
4. Restart reconstructs peak 100 but retains `stop_armed=False`.
5. The new fall generates no LOSS_STOP incident.

This violates the existing HALT behavior: the owner’s HALT must remain effective, while a newly armed breach must still be recorded. Replaying only the peak cannot reproduce the latch’s path-dependent state.

The following exact command exercises **A27-8, A27-9 and A27-10** independently and collects the failed assertions:

```bash
PYTHONPATH=. python - <<'PY'
from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import aqt.app.paper_loop as loop
from aqt.app.state import AccountDir, AccountState
from aqt.backtest.costs import Side
from aqt.core.ledger import read_entries
from aqt.data.bars import BarSeries
from aqt.execution.reconcile import LocalRecord
from aqt.execution.safety import IncidentLog, Mode, Trigger
from aqt.execution.simulator import Order, OrderStatus
from tests.integration.test_paper_loop import _config, _run, _series, HOUR
from tests.integration.test_paper_restart import START
from tests.integration.test_paper_recovery import _override

class Venue:
    def __init__(self, balances, orders=None):
        self._balances = balances
        self._orders = orders or {}

    def balances(self):
        return dict(self._balances)

    def open_orders(self):
        return ()

    def query_order(self, cid):
        return self._orders[cid]

def series_with(prices, default=100.0):
    return BarSeries(
        symbol="BTCUSDT",
        bars=tuple(
            replace(
                b,
                open=prices.get(b.open_time, default),
                high=prices.get(b.open_time, default),
                low=prices.get(b.open_time, default),
                close=prices.get(b.open_time, default),
            )
            for b in _series(24 * 14).bars
        ),
    )

def seed(account, at, mode, balances, peak, armed=True, orders=None):
    incidents = account.incident_log()
    if mode is Mode.HALT:
        incidents.open(str(Trigger.OWNER_HALT), "owner halt", at)
    if not armed:
        incidents.open(str(Trigger.LOSS_STOP), "earlier fall", at)
    seen = (
        len(read_entries(incidents.path))
        if incidents.path.exists() else 0
    )
    account.journal.save(
        AccountState(
            mode=mode,
            entered_at=at,
            record=LocalRecord(balances, orders or {}),
            sent={},
            attempts={},
            peak=D(peak),
            stop_armed=armed,
            last_increase=None,
            incidents_seen=seen,
        ),
        at,
    )

def run(account, venue, series, start, **kwargs):
    result = _run(
        account.root,
        _config(1, start=start, end=start + HOUR),
        series,
        incidents=account.incident_log(),
        journal=account.journal,
        venue=venue,
        **kwargs,
    )
    assert not result.refused, result.refused
    return result

def losses(account):
    return sum(
        e.record_type == IncidentLog.OPEN
        and e.payload.get("kind") == str(Trigger.LOSS_STOP)
        for e in read_entries(account.incidents_path)
    )

failures = []

with TemporaryDirectory() as directory:
    root = Path(directory)

    # A27-8: refusal at completion, then LOSS_STOP at the old hour.
    account = AccountDir(root / "timing")
    balances = {"BTC": D(1), "USDT": D(0)}
    seed(account, START - HOUR, Mode.HALT, balances, "120")
    invalid = replace(
        _override(account.incident_log().open_incidents(), START),
        written_record="",
    )
    real_reconcile = loop.reconcile

    def delayed(*args, **kwargs):
        report = real_reconcile(*args, **kwargs)
        return replace(report, at=report.at + 2 * HOUR)

    with patch.object(loop, "reconcile", delayed):
        run(
            account, Venue(balances), series_with({}, default=90.0), START,
            overrides={START: invalid},
        )
    stamps = [
        e.recorded_at_utc for e in read_entries(account.operations_path)
    ]
    if stamps != sorted(stamps):
        failures.append(("A27-8", stamps))

    # A27-9: pending buy changes holdings before the missed peak.
    account = AccountDir(root / "holdings")
    buy = Order(
        client_order_id="recovered-buy",
        symbol="BTCUSDT",
        side=Side.BUY,
        orig_qty=D(1),
        executed_qty=D(1),
        status=OrderStatus.FILLED,
        decision_time=START,
        fill_time=START,
        fill_price=D(100),
        quote_amount=D(100),
        cost_quote=D(0),
        cost_bps=D(0),
        limit_price=None,
    )
    seed(
        account, START, Mode.RUNNING,
        {"BTC": D(0), "USDT": D(100)}, "100",
        orders={buy.client_order_id: None},
    )
    restart = START + 3 * HOUR
    run(
        account,
        Venue(
            {"BTC": D(1), "USDT": D(0)},
            {buy.client_order_id: buy},
        ),
        series_with({
            START + HOUR: 120.0,
            START + 2 * HOUR: 90.0,
        }),
        restart,
        commands={restart: Trigger.OWNER_HALT},
    )
    saved = account.journal.load()
    assert saved.last_increase == START
    if saved.peak != D(120) or losses(account) != 1:
        failures.append(("A27-9", str(saved.peak), losses(account)))

    # A27-10: missed recovery above the line should re-arm the latch.
    account = AccountDir(root / "latch")
    balances = {"BTC": D(1), "USDT": D(0)}
    seed(account, START, Mode.HALT, balances, "100", armed=False)
    previous_losses = losses(account)
    run(
        account,
        Venue(balances),
        series_with({
            START - HOUR: 70.0,
            START: 100.0,
            START + HOUR: 70.0,
        }),
        START + 2 * HOUR,
    )
    if losses(account) != previous_losses + 1:
        failures.append(
            ("A27-10", previous_losses, losses(account))
        )

assert not failures, failures
PY
```

**A27-11 — NON-BLOCKING — A duplicate response now commits a prefix before refusing.**

Location: `src/aqt/data/live_bars.py:440` (prefix scan and two separate `append` calls).

Concrete scenario: the store contains hour 0; a reply contains hours **1, 1, 2**. The new fetch writes hour 1, then refuses the duplicate in the second append.

Previously, the single append rejected the entire response. The module still promises whole-batch refusal for duplicates and out-of-order bars. The repair distinguishes a contiguous prefix from everything else, but does not distinguish a forward gap from a duplicate before committing that prefix.

This does not create duplicate stored bars or bypass continuity; it is a partial-write regression and a contract mismatch.

Exact reproduction command:

```bash
PYTHONPATH=. python - <<'PY'
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from aqt.data.bars import Bar
from aqt.data.live_bars import LiveBarError, LiveBarStore, fetch_new_bars

t = datetime(2026, 9, 29, tzinfo=UTC)
h = timedelta(hours=1)
now = t + 4 * h

def ms(at):
    return int(at.timestamp() * 1000)

def row(n):
    opened = ms(t + n * h)
    return [opened, "100", "100", "100", "100", "1",
            opened + 3_600_000 - 1]

with TemporaryDirectory() as directory:
    store = LiveBarStore(Path(directory) / "bars.jsonl", "BTCUSDT")
    store.append((Bar(t, 100.0, 100.0, 100.0, 100.0, 1.0),))
    before = store.path.read_bytes()
    replies = iter([
        {"serverTime": ms(now)},
        [row(1), row(1), row(2)],
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
        raise AssertionError("duplicate response was accepted")

    assert store.path.read_bytes() == before, (
        "duplicate response committed a prefix before refusing"
    )
PY
```

**A27-12 — NON-BLOCKING — An earlier malformed snapshot remains accepted.**

Location: `src/aqt/app/state.py:240` (entry loop checks only record type; parsing applies only to `last.payload`).

Concrete scenario: a correctly hash-chained account-state entry contains `attempts={"x": "12"}`, followed by a valid snapshot. `load_saved()` accepts the journal. Loading that malformed entry alone would refuse it.

This leaves the whole-history schema portion of A27-6 unresolved. It is not a demonstrated trading bypass, but contradicts the documented refusal of snapshots that do not parse exactly.

Exact reproduction command:

```bash
PYTHONPATH=. python - <<'PY'
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from aqt.app.state import RECORD_TYPE, StateError, StateJournal
from aqt.core.ledger import append_entry
from tests.unit.test_account_state import _state, T0

with TemporaryDirectory() as directory:
    journal = StateJournal(Path(directory) / "state.jsonl")
    malformed = _state().as_mapping()
    malformed["attempts"] = {"x": "12"}
    append_entry(
        journal.path,
        record_type=RECORD_TYPE,
        payload=malformed,
        recorded_at_utc=T0,
    )
    journal.save(_state(), T0 + timedelta(hours=1))

    try:
        journal.load_saved()
    except StateError:
        pass
    else:
        raise AssertionError("earlier malformed snapshot was accepted")
PY
```

The supplied repair tests can be rerun with the following exact command, also **not reproduced (sandbox unavailable)**:

```bash
PYTHONPATH=. python -m pytest -q tests/integration/test_paper_recovery.py tests/unit/test_account_state.py tests/unit/test_live_bars.py
```

**FIX remains required for A27-8, A27-9 and A27-10.** A27-11 and A27-12 need explicit dispositions. T27-12’s outstanding drill comparison remains unverified; this text-only review does not complete that validation or replace the owner’s section 16 review.