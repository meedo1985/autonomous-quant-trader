You are an independent, adversarial code reviewer (section 16 different-model review, GPT-6 Astra). Read-only: do not edit files, do not use the network.

Repository: autonomous-quant-trader. Branch fix/forward-l02-unknown-order, HEAD 5ac8f17. Background: the forward-paper service on the owner's server crashed after every hourly step that sent an order (`l02_count -> snapshots -> expected_balances: ValueError: an order with an unknown outcome has no expected balance`). First repair 30a8bed skipped unknown-outcome snapshots. A Fable 5.1 review (review/forward-l02-fix/FABLE_REVIEW.md) returned FIX with FF44-1..3; adjudication review/forward-l02-fix/ADJUDICATION_FABLE.md; repairs in 5ac8f17.

Review the whole fix (diff below, main..5ac8f17) for correctness:
1. Are FF44-1..3 actually repaired? Is the `until` cutoff right (midnights <= first snapshot of a trailing unknown run)? Off-by-one at exactly a midnight?
2. Can `unknown_since` be reset wrongly (a known snapshot after an unknown that is not actually the resolution, e.g. a different order resolved while another stays unknown — note the check is on any None in the merged record.orders + sent)?
3. Any caller of `snapshots()` or `daily_equity_returns()` broken by the signature change (grep src, scripts, tests)?
4. Does the test fail on main and on 30a8bed for the right reasons?
Read src/aqt/app/forward.py, src/aqt/app/paper_loop.py, src/aqt/execution/safety.py, src/aqt/execution/reconcile.py, src/aqt/app/state.py as needed.

Output: first line "Reviewer model: <model id>", then verdict ACCEPT or FIX, then findings AF44-1, AF44-2, ... with severity, location, failure scenario, suggested repair. Concise, evidence-based.

```diff
diff --git a/src/aqt/app/forward.py b/src/aqt/app/forward.py
index c12dc74..84819f3 100644
--- a/src/aqt/app/forward.py
+++ b/src/aqt/app/forward.py
@@ -215,14 +215,30 @@ def resumed_venue(
     )
 
 
-def snapshots(journal: StateJournal) -> list[tuple[datetime, Mapping[str, Decimal]]]:
-    """Every saved snapshot's time and the balances it implies."""
+def snapshots(
+    journal: StateJournal,
+) -> tuple[list[tuple[datetime, Mapping[str, Decimal]]], datetime | None]:
+    """Every saved snapshot's time and the balances it implies, and the time
+    valuation must stop (`None`: never).
+
+    A snapshot saved while an order's outcome is unknown implies no balances
+    and is skipped. Usually a later snapshot of the same step records the
+    outcome; until then the last known balances stand, so a midnight inside
+    that window is valued before the order (a known approximation, at most one
+    step long, FF44-2). When no known snapshot follows (an executor FREEZE or a
+    FLATTEN fault left the outcome unknown), the holdings since are unknown:
+    valuation stops at the first of those snapshots (FF44-1)."""
     out: list[tuple[datetime, Mapping[str, Decimal]]] = []
+    unknown_since: datetime | None = None
     for entry in read_entries(journal.path):
-        state = AccountState.from_mapping(entry.payload)
+        local = _local(AccountState.from_mapping(entry.payload))
         at = datetime.fromisoformat(entry.recorded_at_utc.replace("Z", "+00:00"))
-        out.append((at, expected_balances(_local(state))))
-    return out
+        if any(order is None for order in local.orders.values()):
+            unknown_since = unknown_since or at
+            continue
+        unknown_since = None
+        out.append((at, expected_balances(local)))
+    return out, unknown_since
 
 
 def daily_equity_returns(
@@ -230,13 +246,14 @@ def daily_equity_returns(
     closes: Mapping[datetime, Decimal],
     base: str,
     quote: str = "USDT",
+    until: datetime | None = None,
 ) -> list[float]:
     """Simple returns of equity between consecutive 00:00 UTC valuations.
 
     At each midnight at or after the first snapshot, the balances are those of the
     last snapshot saved at or before it, valued at the close of the bar that
     closes then (`closes` is keyed by close time). Valuation stops at the
-    first midnight with no close: a gap is never bridged."""
+    first midnight with no close, and after `until`: a gap is never bridged."""
     if not saved:
         return []
     ordered = sorted(saved, key=lambda pair: pair[0])
@@ -246,7 +263,7 @@ def daily_equity_returns(
         midnight += DAY  # the first midnight at or after the first snapshot
     values: list[Decimal] = []
     i = 0
-    while midnight in closes:
+    while midnight in closes and (until is None or midnight <= until):
         while i + 1 < len(ordered) and ordered[i + 1][0] <= midnight:
             i += 1
         balances = ordered[i][1]
@@ -421,4 +438,5 @@ def l02_count(journal: StateJournal, series: BarSeries) -> EffectiveDecisions:
         bar.open_time + bar.interval: Decimal(str(bar.close)) for bar in series.bars
     }
     base = series.symbol.removesuffix("USDT")
-    return effective_decisions(daily_equity_returns(snapshots(journal), closes, base))
+    saved, until = snapshots(journal)
+    return effective_decisions(daily_equity_returns(saved, closes, base, until=until))
diff --git a/tests/integration/test_forward_paper.py b/tests/integration/test_forward_paper.py
index 68e022b..82da89b 100644
--- a/tests/integration/test_forward_paper.py
+++ b/tests/integration/test_forward_paper.py
@@ -18,6 +18,7 @@ from aqt.app.forward import (
     ForwardError,
     daily_equity_returns,
     effective_decisions,
+    l02_count,
     run_step,
     skipped_while_busy_event,
     unfinished_hours,
@@ -28,6 +29,7 @@ from aqt.core.deployment import approve
 from aqt.core.ledger import append_entry, read_entries
 from aqt.data.bars import BarSeries
 from aqt.execution.orders import ExecutorConfig, client_order_id_for
+from aqt.execution.reconcile import LocalRecord
 from aqt.execution.safety import Mode
 from aqt.execution.simulator import Fault, Scenario, SimulatedExchange
 from aqt.monitoring.alerts import LedgerSink
@@ -107,6 +109,36 @@ def test_hourly_forward_steps_end_where_one_replay_ends(tmp_path: Path) -> None:
     assert _lags(account) == []  # on time and never interrupted: no breach
 
 
+def test_l02_count_skips_snapshots_with_an_order_in_flight(tmp_path: Path) -> None:
+    """A step saves the sent order before its outcome is known; that snapshot
+    has no expected balance and must not stop the `L-02` count (server crash
+    2026-10-05, every hour after the first order)."""
+    series = _series(24 * 14)
+    account = AccountDir(tmp_path)
+    for k in range(HOURS + 1):
+        _step(account, series, START + k * HOUR)
+    in_flight = [
+        e
+        for e in read_entries(account.journal.path)
+        if None in _local_orders(AccountState.from_mapping(e.payload))
+    ]
+    assert in_flight  # the case occurs in an ordinary run
+    count = l02_count(account.journal, _upto(series, START + HOURS * HOUR))
+    assert count.raw_decisions == 1  # START and START + 24h valued (FF44-3)
+    # FF44-1: an outcome still unknown when the step ended (executor FREEZE,
+    # FLATTEN fault) leaves the holdings unknown, so no later midnight is
+    # valued, although its close exists.
+    state = account.journal.load()
+    assert state is not None
+    orders = {**state.record.orders, "unknown": None}
+    unknown = replace(state, record=LocalRecord(state.record.balances, orders))
+    account.journal.save(unknown, START + (HOURS + 1) * HOUR)
+    later = _upto(series, START + 50 * HOUR)  # the START + 48h close exists
+    assert l02_count(account.journal, later).raw_decisions == 1
+    account.journal.save(state, START + (HOURS + 2) * HOUR)  # outcome learned
+    assert l02_count(account.journal, later).raw_decisions == 2
+
+
 def _lags(account: AccountDir) -> list[dict[str, object]]:
     return [
         e.payload["fields"]
@@ -417,3 +449,7 @@ def test_the_script_checks_the_deployment_before_anything_else(
     log = (tmp_path / script.REFUSALS).read_text()
     assert "REFUSE_START" in log and "deployment: " in log
     assert not (tmp_path / "a").exists() and not (tmp_path / "s").exists()
+
+
+def _local_orders(state: AccountState) -> list[object]:
+    return [*state.record.orders.values(), *state.sent.values()]
```
