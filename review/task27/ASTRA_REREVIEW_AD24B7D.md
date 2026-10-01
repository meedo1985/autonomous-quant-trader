# Task 27 Astra re-review of `ad24b7d` — text-only (FIX; A27-20, A27-21 blockers)

Date: 2026-10-01. Requested by the owner ("Make next").

- Invocation: `codex exec -s read-only -m gpt-6-astra -` (codex-cli 0.154.0).
- **Text-only**, as for the earlier Task 27 records. Attached verbatim from
  `ad24b7d`: `ASTRA_REREVIEW_9363171.md`, `LOCAL_REPORT.md`, `DESIGN.md`,
  `OWNER_ANSWERS.md`, `state.py`, `paper_loop.py`, `live_bars.py`, `safety.py`,
  `test_paper_recovery.py`, and `git diff 9363171 ad24b7d -- src scripts tests`.
  Prompt bundle SHA-256: `41c2a802e8013344add5bc2192da893936052178e7c426869fc60dc44afea35f`.
- The reviewer ran no command. The reviewer's final message follows verbatim.

---

**Verdict: FIX.**

Reviewer: **GPT-6 Astra**, independent different-model reviewer of implementation by Claude Opus 5.5. Reviewed supplied commit **`ad24b7d`**, branch `task27-persistent-state`, draft PR **#37**.

This review was **text-only**, using only the attachments. I ran no commands and accessed no filesystem, network, credentials, exchange APIs, or confirmation/lockbox data. Commit identity was not independently verified. Local skills and the full Constitution/S-4 source documents were not attached or read. The orchestrator reports **1700 passed, 4 skipped**, clean ruff, formatting, mypy `src scripts`, six import contracts, and frozen verification PASS; I did not verify those results. This final message is the review record; I have not committed it.

**Repair assessments**

| Finding | Assessment | Evidence |
|---|---|---|
| **A27-16** | **CORRECT** | A successful waited override now resets peak, arms the latch, and sets `valued = max(hour, closed + HOUR)` together before saving. Its old pre-reset prices are excluded both from subsequent busy-hour valuation and restart replay. The original 120→90 scenario retains peak 90 after restart. |
| **A27-17** | **INCOMPLETE** | Startup-wait and ordinary busy/health hours now invoke `fire(value(...))`, repairing the original startup comparison. However, the claimed uniform rule still fails on refused overrides, and replay can discard available historical bars: A27-20 and A27-21. Repeated historical firings also differ: A27-22. |
| **A27-18** | **CORRECT** | `value()` refuses valuation whenever either `local.orders` or `controller.sent` is nonempty. Successful FREEZE_EXIT settles holdings and replays deferred hours with firing suppressed; startup resolves both order sources before replay. This repairs the original unresolved-baseline peak loss, including unsettled FLATTEN sells. |
| **A27-19** | **CORRECT** | Strict ordering is checked on the parsed reply before filtering older rows. Reply `1,0,2` now raises before any append. The same guard rejects `1,3,3` and `1,3,2`, while an increasing forward gap can retain its valid prefix. |

**The A27-18 “late” fixture disposition is justified.** Its manually advanced watermark represents precisely the unresolved-balance valuation that the new guard prevents. It is no longer a reachable snapshot from that loop path. This establishes the repair for newly produced snapshots; it does not establish automatic repair of snapshots already produced by the old implementation.

The replacement regression demonstrates watermark retention and subsequent advancement. It does not itself compare the original 120/90 peak scenario across different recovery timings, so its evidence is narrower than the report’s general equivalence claim.

**Valuation and save-path assessment**

| Site | Assessment |
|---|---|
| `value()` / `fire()` | Correctly separates valuation from firing, but callers must complete both before treating the hour as processed. Refused override branches violate this requirement. |
| Startup skip loop | Values available bars with confirmed holdings and applies the FREEZE exclusion through `fire()`. Repairs the original waited-startup case. |
| Busy hours | Uses reconciled holdings or leaves the watermark unchanged if orders remain unresolved. A successful override’s reset boundary excludes earlier busy hours. |
| Health-breach hours | Values and may open LOSS_STOP; places no order that hour. This is a material disclosed behavior change, discussed below. |
| No-bar hours | Leaves the watermark unchanged. However, startup’s earlier `contiguous_window` slicing can make existing replay bars appear absent. |
| FREEZE_EXIT | A failed exit preserves deferred valuation. A successful exit replays through the initiating hour with `fires=False`; subsequent waiting hours use the HALT path. |
| Successful HALT override | The saved reset and watermark are consistent. A kill before its snapshot conservatively restores the earlier protective state; successful override completion is not independently journaled for replay. |
| Refused/failed override | The initiating hour can already be marked valued, yet its firing is bypassed. A refusal can therefore permanently consume an unreported breach. |
| Startup `_replay` | Restores peak/latch over the bars it receives, but receives truncated history and returns only the first missed firing. |
| Saves | Saves preserve the current watermark rather than inventing one. Executor and FLATTEN pre-send saves retain their already-valued decision hour. Hour-end/final saves nevertheless persist the incomplete override bookkeeping described below. |

The attachments therefore do **not** establish live-versus-restart equivalence at every kill point.

**A27-20 — BLOCKER — A refused override marks a breached hour complete without recording its loss stop**

Location: `src/aqt/app/paper_loop.py:967–974`, the `end_halt(...)`/`continue` branch following `valuation = value(...)`.

Concrete scenario:

1. HALT holds one BTC, peak 100, latch armed, valued through H−1.
2. H’s decision mark is 70.
3. The owner supplies an invalid override, such as an empty written record.
4. `value(H, ...)` advances `valued` to H and returns a breach.
5. Reconciliation passes, but `override_halt` refuses the artifact.
6. `end_halt` returns `True`; the caller continues without `fire(valuation, ...)`.
7. The hour-end snapshot records H as valued, with no LOSS_STOP incident.
8. H+1 recovers to 100. The transient breach is permanently lost.

If killed before step 7, restart replays H and opens the LOSS_STOP incident. Thus the same refused override and prices produce **zero incidents uninterrupted versus one after a kill**.

A successful owner reset intentionally supersedes the earlier loss line. A refused override supplies no such authorization. Timestamp ordering does not require discarding the alert: it can be recorded at reconciliation completion.

**A27-21 — BLOCKER — Startup discards available pre-gap replay bars, losing an unsaved peak**

Location: `src/aqt/app/paper_loop.py:714`, startup `_replay`, together with the preceding `series = window` assignment and `contiguous_window()`.

Concrete scenario:

- Saved state: HALT, one BTC, peak 100, valued through H−1.
- H’s decision mark is 120.
- The loop values H, then dies before saving that peak.
- The supplied series contains the required historical 120 bar, followed by a real missing bar at open time H+1.
- Restart begins at H+3, in the contiguous segment beginning at H+2, with mark 90.

`contiguous_window()` returns the restart’s contiguous segment. Assigning it back to `series` discards the available bars before the gap. `_replay()` then treats H’s 120 bar as unavailable and skips it.

Result: saved peak **100**, no LOSS_STOP, instead of peak **120** and a breach at 90.

The restart window itself is valid and contiguous. This finding does not ask the simulator to trade across a gap or invent a missing bar. It requires retaining available historical evidence for recovery separately from the contiguous decision window.

**A27-22 — NON-BLOCKING — Multiple missed loss-stop firings are collapsed into one incident**

Location: `src/aqt/app/paper_loop.py:714`, startup `_replay` and its single `missed` trigger; `_replay()` statement `missed = missed or hour`.

Concrete scenario, HALT throughout, peak 100 and armed:

| Decision hour | Mark |
|---|---:|
| H | 70 |
| H+1 | 100 |
| H+2 | 70 |
| H+3 | 100 |

Uninterrupted processing records **two** LOSS_STOP incidents. Restart after these four hours records **one**, because `_replay()` retains only the first firing despite rearming and firing internally again.

Peak, final latch and protective mode agree, so this is non-blocking by itself. However, it contradicts strict incident equivalence and the stated “loss stop firing as usual” rule. Either preserve each firing or explicitly document and accept historical alert coalescing.

**A27-23 — QUESTION — Confirm the owner’s acceptance of persistent FLATTEN triggered during a health breach**

Location: `src/aqt/app/paper_loop.py:945`, health-breach `fire(value(...))`.

Concrete scenario: RUNNING holds one BTC with peak 100; a stale-data health breach coincides with a supplied decision mark of 70. The new code opens LOSS_STOP and enters FLATTEN without placing an order that hour. A later healthy hour continues FLATTEN even if the mark has recovered to 100.

That follows the attached description of S-4’s LOSS_STOP transition and preserves the immediate health-hour order prohibition. It is nevertheless more than an additional alert: it commits the controller to later liquidation based on a valuation made during the health breach.

The attached owner answers authorize the override reset and protective-mode restart; they do not expressly address this change. The full S-4/health policy is absent, so I cannot establish a policy violation or certify owner acceptance. The walkthrough should explicitly cover this scenario. This question is not an additional code blocker.

**Reproductions**

The following exact command is **not reproduced (sandbox unavailable)**. It uses synthetic fixtures and collects the predicted A27-20–22 failures; its final assertion expresses the required properties. It also prints the A27-23 health-hour behavior for owner review.

```bash
PYTHONPATH=. python - <<'PY'
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal as D
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import aqt.app.paper_loop as loop
from aqt.app.state import AccountDir, StateJournal
from aqt.data.bars import BarSeries
from aqt.execution.safety import Mode
import tests.integration.test_paper_recovery as r

H, hour = r.START, r.HOUR
failures = []

def check(label, condition, observed):
    print(label, observed)
    if not condition:
        failures.append((label, observed))

def run(account, series, start, end, **kwargs):
    result = r._run(
        account.root,
        r._config(1, start=start, end=end),
        series,
        incidents=account.incident_log(),
        journal=account.journal,
        venue=r._Venue(r.ONE_BTC),
        **kwargs,
    )
    assert result.refused == (), result.refused
    return result

with TemporaryDirectory() as directory:
    root = Path(directory)

    # A27-20: invalid override, transient breach, kill before hourly save.
    series = r._priced({H - hour: 70.0, H: 100.0})
    continuous = AccountDir(root / "override-continuous")
    restarted = AccountDir(root / "override-restarted")
    for account in (continuous, restarted):
        r._seed(account, H - hour, Mode.HALT, r.ONE_BTC, "100")

    def invalid(account):
        return replace(
            r._override(account.incident_log().open_incidents(), H),
            written_record="",
        )

    run(
        continuous, series, H, H + 2 * hour,
        overrides={H: invalid(continuous)},
    )
    real_save = StateJournal.save

    def kill_valued_hour(self, state, at):
        if state.valued_through == H:
            raise r._Killed
        real_save(self, state, at)

    try:
        with patch.object(StateJournal, "save", kill_valued_hour):
            run(
                restarted, series, H, H + hour,
                overrides={H: invalid(restarted)},
            )
    except r._Killed:
        pass
    else:
        raise AssertionError("A27-20 kill point not reached")

    loop.refuse_marker_path(restarted.incident_log()).unlink(missing_ok=True)
    run(restarted, series, H + hour, H + 2 * hour)
    observed = (r._losses(continuous), r._losses(restarted))
    check("A27-20", observed == (1, 1), observed)

    # A27-21: available historical peak discarded by restart-window slicing.
    account = AccountDir(root / "gap")
    r._seed(account, H - hour, Mode.HALT, r.ONE_BTC, "100")
    priced = r._priced(
        {H - hour: 120.0, H: 90.0, H + 2 * hour: 90.0},
        default=90.0,
    )
    series = BarSeries(
        symbol=priced.symbol,
        bars=tuple(
            bar for bar in priced.bars
            if bar.open_time != H + hour
        ),
    )

    def kill_peak(self, state, at):
        if state.peak == D(120):
            raise r._Killed
        real_save(self, state, at)

    try:
        with patch.object(StateJournal, "save", kill_peak):
            run(account, series, H, H + hour)
    except r._Killed:
        pass
    else:
        raise AssertionError("A27-21 kill point not reached")

    loop.refuse_marker_path(account.incident_log()).unlink(missing_ok=True)
    run(account, series, H + 3 * hour, H + 4 * hour)
    saved = account.journal.load()
    assert saved is not None
    observed = (str(saved.peak), r._losses(account))
    check(
        "A27-21",
        saved.peak == D(120) and r._losses(account) == 1,
        observed,
    )

    # A27-22: two separate missed falls should match live incident history.
    series = r._priced({
        H - hour: 70.0,
        H: 100.0,
        H + hour: 70.0,
        H + 2 * hour: 100.0,
    })
    continuous = AccountDir(root / "cycles-continuous")
    restarted = AccountDir(root / "cycles-restarted")
    for account in (continuous, restarted):
        r._seed(account, H - hour, Mode.HALT, r.ONE_BTC, "100")
    run(continuous, series, H, H + 4 * hour)
    run(restarted, series, H + 4 * hour, H + 5 * hour)
    observed = (r._losses(continuous), r._losses(restarted))
    check("A27-22", observed == (2, 2), observed)

    # A27-23: health breach still commits RUNNING to FLATTEN.
    account = AccountDir(root / "health")
    r._seed(account, H - 2 * hour, Mode.RUNNING, r.ONE_BTC, "100")
    series = r._priced({H - hour: 70.0})
    config = r._config(1, start=H - hour, end=H + hour)

    def observe(at):
        observation = loop.bar_clock_observation(at)
        if at == H:
            return replace(
                observation,
                latest_bar_close=(
                    at - config.health.max_data_age - timedelta(seconds=1)
                ),
            )
        return observation

    with patch.object(loop, "baseline_proposal", return_value="synthetic hold"):
        result = run(
            account, series, H - hour, H + hour, observe=observe
        )
    print("A27-23", {
        "mode": result.final_mode,
        "losses": r._losses(account),
        "orders_sent": result.orders_sent,
    })

assert not failures, failures
PY
```

Existing repair regressions, **not reproduced (sandbox unavailable)**:

```bash
PYTHONPATH=. python -m pytest -q tests/integration/test_paper_recovery.py tests/unit/test_account_state.py tests/unit/test_live_bars.py
```

**Task 27 does not yet meet DESIGN.md section 5 as a whole.** The original reset and unresolved-order watermark repairs are sound, but A27-21 directly loses a required peak after a kill, and A27-20 makes safety-incident history depend on whether an incomplete valuation was saved. A27-22 needs an explicit disposition; A27-23 belongs in the owner walkthrough. T27-12’s outstanding drill comparison also remains disclosed.

**FIX required for A27-20 and A27-21.**