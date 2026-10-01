# Task 27 Astra re-review of `9363171` — text-only (FIX; A27-16..A27-18 blockers)

Date: 2026-10-01. Requested by the owner ("Make next").

- Invocation: `codex exec -s read-only -m gpt-6-astra -` (codex-cli 0.154.0).
- **Text-only**, as for the earlier Task 27 records. Attached verbatim from
  `9363171`: `ASTRA_REREVIEW_C6C8F06.md`, `LOCAL_REPORT.md`, `DESIGN.md`,
  `state.py`, `paper_loop.py`, `live_bars.py`, `safety.py`,
  `test_paper_recovery.py`, and `git diff c6c8f06 9363171 -- src scripts tests`.
  Prompt bundle SHA-256: `b72fb686eae15e151c1c7a626c8be0fefe21eab4710132b3536050ca1e135aff`.
- The reviewer ran no command. The reviewer's final message follows verbatim.

---

**Verdict: FIX.**

Reviewer: **GPT-6 Astra**, independent different-model reviewer of implementation by Claude Opus 5.5. Reviewed supplied commit **`9363171`**, branch `task27-persistent-state`, draft PR **#37**.

This review was **text-only**, solely from the attachments. I ran no commands and accessed no filesystem, network, credentials, exchange APIs, or confirmation/lockbox data. Commit identity was not independently verified. Local skills were not attached or read. The orchestrator reports **1696 passed, 4 skipped**, clean ruff, formatting, mypy `src scripts`, six import contracts, and frozen verification PASS; I did not verify these results. This final message is the review record; I have not committed it.

**Repair assessments**

| Finding | Assessment | Evidence |
|---|---|---|
| **A27-13** | **INCOMPLETE** | The original post-buy hour-end scenario is repaired: `valued_through=H` excludes H from replay, preserving peak 100. Ordinary executor and FLATTEN pre-send snapshots also exclude their already-valued decision hour. However, the watermark is inconsistent with a reset after a waited override, startup waiting, and valuations made with unresolved FREEZE balances: A27-16–18. |
| **A27-14** | **CORRECT** | Startup no longer overwrites the replayed latch. With `valued=START - HOUR`, replay processes the fall at H and recovery at H+1, returns an armed latch, and the live H+2 fall opens the second incident. |
| **A27-15** | **INCOMPLETE** | The reported `1,3,3` and `1,3,2` cases now refuse without appending; `1,3,4` retains the intended prefix behavior. However, the strict-order test examines the reply only after filtering out older bars. A reordered reply containing such a bar can still be accepted: A27-19. |

**The author’s A27-14 explanation is correct.** The modified helper’s default declares H already valued. The original command therefore no longer represents an unprocessed fall at H. Explicitly seeding `valued=START - HOUR` restores the original scenario; it is a necessary fixture adjustment, not a weakening of that scenario.

**Snapshot and replay trace**

| Save path | What the attached code records |
|---|---|
| Startup `save(ready)` | Replay’s returned watermark, but replay stops before `config.start`, not `ready`. Waiting hours remain unprocessed: A27-17. |
| Executor pre-send | Current decision hour, whose pre-order valuation and loss check have run. Confirmed post-order holdings are consequently used only for later replayed hours. This repairs the ordinary pending-buy and pending-sell cases. |
| FLATTEN `before_send` | The same current-hour boundary, with the sell pending in `sent`. Startup reconciliation resolves it before later-hour replay. |
| Owner command before valuation | Previous watermark. Replay can subsequently process the command hour; the command itself does not falsely advance valuation. |
| Hour-end and final | Whatever watermark the loop last assigned; saving does not itself advance it. |
| FREEZE exit, successful or failed | The hour has already been marked valued using the old local baseline. Successful recovery changes balances without correcting that valuation. Unresolved orders make this material: A27-18. |
| Successful HALT override | Peak resets to completion-time equity and the latch arms, but the watermark remains the initiating decision hour. A wait spanning hours permits pre-reset prices to be replayed into the new peak: A27-16. |
| Failed/refused HALT override | No reset. The initiating hour has already updated peak and watermark; its loss firing is bypassed by the override branch. The wait is not included in that watermark. |
| Skipped hours | Startup waits, recovery waits, health breaches and missing bars do not advance the watermark. A later successful valuation advances it directly to that later hour, making intervening hours inaccessible to future replay. A27-17 demonstrates the restart-dependent consequence. |

The replay correctly retains its final latch after emitting a missed firing. FREEZE replay suppresses firing without spending the latch. Those repairs do not resolve the distinction between a valuation using confirmed holdings and one using a baseline that still has unresolved orders.

**A27-16 — BLOCKER — A waited override allows pre-reset prices to rebuild the discarded peak**

**Location:** `src/aqt/app/paper_loop.py:889` (`valued = decision_time`), `end_halt`’s completion-time peak reset, and `:710` (replay window).

Concrete scenario:

1. HALT holds one BTC, peak 100.
2. Override begins at H. Its preliminary valuation sets `valued=H`.
3. Reconciliation completes at H+2. Decision-hour marks are H:100, H+1:120, H+2:90.
4. The successful override correctly resets peak to **90**, using the last close before completion.
5. Its snapshot is saved at H+2 but still says **valued through H**.
6. Restart at H+3 replays H+1 and H+2: peak becomes 120, then 90 breaches its 96 line.

An accepted Q27-1/Q27-2 reset is undone by replaying prices from before its effective time. Startup opens an unwarranted LOSS_STOP and enters FLATTEN from RUNNING.

The reset needs a replay boundary consistent with its effective valuation time; changing peak and latch alone is insufficient.

**A27-17 — BLOCKER — Startup waiting produces different retained peaks depending on another restart**

**Location:** `src/aqt/app/paper_loop.py:710` (`config.start` as replay endpoint), startup’s `while moment < ready`, and `:889`.

Concrete scenario, HALT throughout:

- Snapshot: valued through H−1, one BTC, peak 100.
- Startup requested at H; reconciliation finishes at H+2.
- Decision-hour marks: H:120, H+1:90, H+2:90, H+3:90.

Two paths through the supplied code:

| Path | Result |
|---|---|
| Continue after startup | Replay stops before H. Startup skips H and H+1. Live H+2 sets `valued=H+2` at equity 90. Peak stays **100**, and H’s 120 can never be replayed. |
| Restart after the ready snapshot, before a live valuation | The ready snapshot still has `valued=H−1`. Restart at H+3 replays H’s 120 and the subsequent fall. Peak becomes **120**, with a LOSS_STOP incident. |

The same holdings, prices and completed startup reconciliation produce different retained safety state solely because of another restart. The ready snapshot and subsequent live processing disagree about whether those hours need replay.

**A27-18 — BLOCKER — FREEZE snapshots mark unresolved-balance valuations complete, preventing recovery of the actual peak**

**Location:** `src/aqt/app/paper_loop.py:886–889` (valuation from `local.balances` and watermark advancement), `:708–710` (confirmed holdings replayed only beyond that watermark).

Concrete scenario:

1. At H, an account with 100 USDT sends a buy for one BTC. It fills at 100, but the result remains unreadable and the controller enters FREEZE.
2. The local reconciliation baseline remains **100 USDT**, with the buy unresolved.
3. At H+1, BTC’s mark is 120. FREEZE still values the local cash baseline as 100, then saves `valued_through=H+1`.
4. Restart at H+2 confirms the filled buy and one BTC. The current mark is 90.
5. Replay starts after H+1, so the actual equity of 120 is never considered. Saved peak remains **100**.

If restart instead occurs before the H+1 FREEZE snapshot, confirmed holdings value H+1 at 120 and preserve peak **120**. Thus postponing restart by one FREEZE hour loses the recoverable peak.

This also affects FLATTEN leftovers held in `controller.sent`: both order sources are reconciled at startup, but advancing the watermark using their unreconciled baseline prevents confirmed holdings from correcting earlier affected hours. FREEZE’s intentional suppression of LOSS_STOP firing does not justify discarding peak information.

**A27-19 — NON-BLOCKING — Filtering precedes whole-reply order validation**

**Location:** `src/aqt/data/live_bars.py:446` (`ordered`), and the preceding `open_time >= begin` filter.

Concrete scenario:

- Store contains hour 0; next expected hour is 1.
- Closed-bar reply is **1,0,2**.
- Filtering removes hour 0, leaving **1,2**.
- The strict-order check passes and both bars are appended.

The original reply was reordered and included an already-stored hour, yet it is accepted. This contradicts the documented whole-reply refusal. It does not corrupt stored continuity, so it is non-blocking. If older overlap is intentionally allowed, that exception must be explicit; ordering of the original reply still needs a defined rule.

**Reproductions**

All commands below are **not reproduced (sandbox unavailable)**.

The following exact command exercises A27-16–19 using synthetic fixtures, temporary directories and simulated completion delays. Each assertion describes the required property; the attached code predicts failures.

```bash
PYTHONPATH=. python - <<'PY'
import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal as D
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

import aqt.app.paper_loop as loop
from aqt.app.state import AccountDir
from aqt.backtest.costs import Side
from aqt.data.bars import Bar
from aqt.data.live_bars import LiveBarError, LiveBarStore, fetch_new_bars
from aqt.execution.safety import Mode, Trigger
from aqt.execution.simulator import Order, OrderStatus
import tests.integration.test_paper_recovery as r

H = r.START
hour = r.HOUR
failures = []

def check(label, condition, observed):
    if not condition:
        failures.append((label, observed))

with TemporaryDirectory() as directory:
    root = Path(directory)

    # A27-16: completion-time reset must exclude pre-reset prices.
    account = AccountDir(root / "override")
    r._seed(account, H - hour, Mode.HALT, r.ONE_BTC, "100")
    series = r._priced({
        H - hour: 100.0,
        H: 120.0,
        H + hour: 90.0,
        H + 2 * hour: 90.0,
    })
    wanted = r._override(account.incident_log().open_incidents(), H)
    real_reconcile = loop.reconcile

    def delayed_recovery(*args, **kwargs):
        report = real_reconcile(*args, **kwargs)
        return replace(report, at=report.at + 2 * hour)

    with patch.object(loop, "reconcile", delayed_recovery):
        r._one_hour(
            account, r._Venue(r.ONE_BTC), series, H,
            overrides={H: wanted},
        )

    before = account.journal.load()
    assert before is not None
    assert before.mode is Mode.RUNNING and before.peak == D(90)

    restart = H + 3 * hour
    r._one_hour(
        account, r._Venue(r.ONE_BTC), series, restart,
        commands={restart: Trigger.OWNER_HALT},
    )
    saved = account.journal.load()
    assert saved is not None
    check(
        "A27-16",
        saved.peak == D(90) and r._losses(account) == 0,
        {"peak": str(saved.peak), "losses": r._losses(account)},
    )

    # A27-17: same startup wait, with and without a restart after ready.
    series = r._priced({
        H - hour: 120.0,
        H: 90.0,
        H + hour: 90.0,
        H + 2 * hour: 90.0,
    }, default=90.0)
    real_startup = loop.startup_check

    def delayed_startup(*args, **kwargs):
        decision = real_startup(*args, **kwargs)
        return replace(
            decision,
            report=replace(
                decision.report, at=decision.report.at + 2 * hour
            ),
        )

    continuous = AccountDir(root / "continuous")
    restarted = AccountDir(root / "restarted")
    for account in (continuous, restarted):
        r._seed(account, H - hour, Mode.HALT, r.ONE_BTC, "100")

    with patch.object(loop, "startup_check", delayed_startup):
        report = r._run(
            continuous.root,
            r._config(1, start=H, end=H + 4 * hour),
            series,
            incidents=continuous.incident_log(),
            journal=continuous.journal,
            venue=r._Venue(r.ONE_BTC),
        )
        assert report.refused == ()
        # Ends after saving ready, with no eligible live decision.
        r._one_hour(restarted, r._Venue(r.ONE_BTC), series, H)

    r._one_hour(
        restarted, r._Venue(r.ONE_BTC), series, H + 3 * hour
    )
    a = continuous.journal.load()
    b = restarted.journal.load()
    assert a is not None and b is not None
    check(
        "A27-17",
        (a.peak, r._losses(continuous)) ==
        (b.peak, r._losses(restarted)),
        {
            "continuous": [str(a.peak), r._losses(continuous)],
            "restarted": [str(b.peak), r._losses(restarted)],
        },
    )

    # A27-18: one more FREEZE snapshot must not hide the confirmed peak.
    buy = Order(
        client_order_id="recovered-buy",
        symbol="BTCUSDT",
        side=Side.BUY,
        orig_qty=D(1),
        executed_qty=D(1),
        status=OrderStatus.FILLED,
        decision_time=H,
        fill_time=H,
        fill_price=D(100),
        quote_amount=D(100),
        cost_quote=D(0),
        cost_bps=D(0),
        limit_price=None,
    )
    cash = {"BTC": D(0), "USDT": D(100)}
    series = r._priced({H: 120.0, H + hour: 90.0})
    peaks = []
    for label, later_snapshot in (("early", False), ("late", True)):
        account = AccountDir(root / label)
        r._seed(
            account, H, Mode.FREEZE, cash, "100",
            orders={buy.client_order_id: None},
        )
        if later_snapshot:
            state = account.journal.load()
            assert state is not None
            # Exactly the H+1 FREEZE bookkeeping: unresolved cash
            # baseline still values 100, but the watermark advances.
            account.journal.save(
                replace(state, valued_through=H + hour), H + hour
            )
        r._one_hour(
            account,
            r._Venue(r.ONE_BTC, {buy.client_order_id: buy}),
            series,
            H + 2 * hour,
        )
        saved = account.journal.load()
        assert saved is not None and saved.mode is Mode.FREEZE
        peaks.append(saved.peak)

    check(
        "A27-18",
        peaks == [D(120), D(120)],
        {"early_and_late_peaks": [str(p) for p in peaks]},
    )

    # A27-19: older rows must not conceal original-reply reordering.
    t = datetime(2026, 9, 29, tzinfo=UTC)
    h = timedelta(hours=1)
    now = t + 4 * h

    def ms(at):
        return int(at.timestamp() * 1000)

    def row(n):
        opened = ms(t + n * h)
        return [
            opened, "100", "100", "100", "100", "1",
            opened + 3_600_000 - 1,
        ]

    store = LiveBarStore(root / "bars.jsonl", "BTCUSDT")
    store.append((Bar(t, 100.0, 100.0, 100.0, 100.0, 1.0),))
    before = store.path.read_bytes()
    replies = iter([
        {"serverTime": ms(now)},
        [row(n) for n in (1, 0, 2)],
    ])

    def transport(request):
        return SimpleNamespace(
            status=200,
            body=json.dumps(next(replies)).encode(),
        )

    refused = False
    try:
        fetch_new_bars(
            transport, store, "BTCUSDT", now, timedelta(seconds=5)
        )
    except LiveBarError:
        refused = True
    check(
        "A27-19",
        refused and store.path.read_bytes() == before,
        {
            "refused": refused,
            "store_changed": store.path.read_bytes() != before,
        },
    )

assert not failures, failures
PY
```

Existing repair regressions, **not reproduced (sandbox unavailable)**:

```bash
PYTHONPATH=. python -m pytest -q tests/integration/test_paper_recovery.py tests/unit/test_account_state.py tests/unit/test_live_bars.py
```

**Task 27 does not yet meet DESIGN.md section 5 as a whole.** The original post-order replay and latch defects are substantially repaired, but A27-16–18 demonstrate that restart timing can still change or lose the required loss-stop peak, including undoing an owner-authorized reset. The supplied evidence supports the marker, incident retention and protective-mode mechanisms; it does not establish the universal kill-at-every-step acceptance claim. T27-12’s outstanding drill comparison also remains disclosed in the report.

**FIX required for A27-16–18. A27-19 requires repair or an explicit disposition.**