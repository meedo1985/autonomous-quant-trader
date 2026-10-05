You are an independent, adversarial code reviewer (section 16 different-model review). Read-only: do not edit files, do not use the network, do not run anything that writes outside a temp dir.

Repository: autonomous-quant-trader (Python). Context: forward paper trading (Task 29) runs hourly on the owner's server. On 2026-10-05 the service crashed after every step that had sent an order:
`scripts/run_forward_paper.py:108 l02_count -> src/aqt/app/forward.py snapshots -> reconcile.expected_balances: ValueError: an order with an unknown outcome has no expected balance`.
The step's decisions and state journal were saved before the crash; only the hourly report line was lost and systemd restarted the process.

The repair (diff below) makes `snapshots()` skip any journal snapshot whose LocalRecord (record.orders + sent) contains an order with outcome None.

Review for correctness:
1. Is skipping the right semantics for `daily_equity_returns` (last snapshot at or before each 00:00Z)? Can a skipped in-flight snapshot be the only one covering a midnight, so a day's valuation becomes wrong rather than merely delayed? Can it bridge a gap the docstring says must never be bridged?
2. Can an unknown-outcome order persist across steps (e.g. lost reply, reconcile NOT_FOUND re-query, FLATTEN `sent`), making L-02 silently stall or misvalue for many hours? If so, should that be reported rather than skipped?
3. Any other caller of expected_balances / snapshots with the same failure?
4. Is the test adequate (does it fail on the old code for the server's reason)?

Read src/aqt/app/forward.py, src/aqt/execution/reconcile.py, src/aqt/app/state.py, src/aqt/app/paper_loop.py as needed.

Output: verdict ACCEPT or FIX, then findings with stable IDs SF44-1, SF44-2, ... each with severity, location, failure scenario, and suggested repair. Be concise.

Diff (main..fix/forward-l02-unknown-order, excluding the review record):
```diff
diff --git a/src/aqt/app/forward.py b/src/aqt/app/forward.py
index c12dc74..abc3672 100644
--- a/src/aqt/app/forward.py
+++ b/src/aqt/app/forward.py
@@ -216,12 +216,17 @@ def resumed_venue(
 
 
 def snapshots(journal: StateJournal) -> list[tuple[datetime, Mapping[str, Decimal]]]:
-    """Every saved snapshot's time and the balances it implies."""
+    """Every saved snapshot's time and the balances it implies. A snapshot
+    saved while an order's outcome is still unknown (sent, not yet answered)
+    implies no balances and is skipped: the snapshot that records the outcome
+    follows it within the same step."""
     out: list[tuple[datetime, Mapping[str, Decimal]]] = []
     for entry in read_entries(journal.path):
-        state = AccountState.from_mapping(entry.payload)
+        local = _local(AccountState.from_mapping(entry.payload))
+        if any(order is None for order in local.orders.values()):
+            continue
         at = datetime.fromisoformat(entry.recorded_at_utc.replace("Z", "+00:00"))
-        out.append((at, expected_balances(_local(state))))
+        out.append((at, expected_balances(local)))
     return out
 
 
diff --git a/tests/integration/test_forward_paper.py b/tests/integration/test_forward_paper.py
index 68e022b..30ee4a1 100644
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
@@ -107,6 +108,24 @@ def test_hourly_forward_steps_end_where_one_replay_ends(tmp_path: Path) -> None:
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
+    assert count.as_mapping()
+
+
 def _lags(account: AccountDir) -> list[dict[str, object]]:
     return [
         e.payload["fields"]
@@ -417,3 +436,7 @@ def test_the_script_checks_the_deployment_before_anything_else(
     log = (tmp_path / script.REFUSALS).read_text()
     assert "REFUSE_START" in log and "deployment: " in log
     assert not (tmp_path / "a").exists() and not (tmp_path / "s").exists()
+
+
+def _local_orders(state: AccountState) -> list[object]:
+    return [*state.record.orders.values(), *state.sent.values()]
```
