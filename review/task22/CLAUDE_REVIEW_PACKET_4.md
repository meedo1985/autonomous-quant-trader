# Task 22 Claude adversarial review packet 4

**Status:** READY FOR HUMAN RELAY — NOT SENT.
**Prepared:** 2026-09-28.

Review Task 22's final executor state, focusing on T22-07. This is a read-only
adversarial review. Do not edit files, invent live-adapter behavior, access
credentials, or propose changes to frozen governance.

## Identity and scope

- Base: `1cbb50d41177d119fa95b891d7f48c9ef15304d6` (`origin/main`).
- Code-review snapshot: `5d08c6f01f690e589e0eabbc252d73e12eb364fd`.
- T22-07 commit: `2041d35939d29bf6c4eeb77ea2684f8871ec522b`.
- Branch: `task22-executor`; worktree clean at the reviewed snapshot.
- Diff: 17 files, 2523 insertions, 14 deletions. Production code is
  `src/aqt/execution/machine.py`, `orders.py`, and the additive Task 18
  simulator changes. Tests are synthetic and offline.
- Excluded: real/testnet adapters, credentials, network order calls, live
  error mapping, Task 23 reconciliation implementation, and frozen changes.

Inspect the complete Git objects with:

```text
git diff 1cbb50d41177d119fa95b891d7f48c9ef15304d6..5d08c6f01f690e589e0eabbc252d73e12eb364fd
git show 2041d35939d29bf6c4eeb77ea2684f8871ec522b
```

The complete T22-07 production change is:

```diff
--- a/src/aqt/execution/machine.py
+++ b/src/aqt/execution/machine.py
@@
-        self.quantity = order_quantity(self.auth, self.x._filters)
+        quantity = order_quantity(self.auth, self.x._filters)
+        if self.auth.side is Side.BUY:
+            affordable = affordable_quantity(
+                self.actual.quote_balance, limit_price, self.x._filters
+            )
+            quantity = min(quantity, affordable)
+        if quantity < self.x._filters.min_qty:
+            quantity = Decimal(0)
+        self.quantity = quantity

--- a/src/aqt/execution/orders.py
+++ b/src/aqt/execution/orders.py
@@
+WORST_CASE_COST_BPS = Decimal(
+    repr(FALLBACK_TAKER_FEE_BPS + SPREAD_ALLOWANCE_BPS + SLIPPAGE_CAP_BPS)
+)
+
+def affordable_quantity(
+    quote_balance: Decimal, limit_price: Decimal, filters: SymbolFilters
+) -> Decimal:
+    unit = Fraction(limit_price) * (1 + Fraction(WORST_CASE_COST_BPS) / 10_000)
+    steps = math.floor(Fraction(quote_balance) / unit / Fraction(filters.step_size))
+    return _DEC.multiply(Decimal(max(steps, 0)), filters.step_size)
```

The commit also adds an end-to-end full-exposure regression and a 500-case
exact-arithmetic property test. See the complete commit for those test hunks.

## Governing acceptance criteria

1. Timeout, NOT_FOUND/found, NOT_FOUND/absent, and UNKNOWN follow section 21.
2. Confirmed-absence resend reuses the same client order ID.
3. Expired authorization cannot resend.
4. UNKNOWN ends in reconciliation/FREEZE and never a new order.
5. One authorization cannot place two distinct orders.
6. Every state/event pair is defined or explicitly rejected.

Section 20 also requires every order to stay within quantity and slippage
bounds. Owner answers bind a 10-second delay, two NOT_FOUND answers, and an
immediate-or-cancel price cap.

## Validation and frozen evidence

- `python -m pytest -q`: 1480 passed, 4 skipped in 80.29s.
- `ruff check .`: pass.
- `ruff format --check .`: 90 files formatted.
- `mypy src scripts`: 46 source files, no issues.
- `lint-imports`: 5 contracts kept, 0 broken.
- `git diff --check origin/main...HEAD`: pass at the reviewed snapshot.
- Frozen verifier: 28/28 trusted bytes, 14/14 sidecars, all self-hashes and
  protocol bindings pass.

The first direct `pytest.exe` attempt used a stale Python 3.12 launcher and
failed collection. The documented `python -m pytest` command used the actual
Python 3.14.7 environment and passed. No dependency was changed.

## Known limits already disclosed

- A future live adapter cannot rely on permanent Binance client-ID
  deduplication after a fill.
- T22-07 uses total quote balance; a future adapter must distinguish free from
  locked funds. In current simulator scope, an unavailable balance rejects
  safely.
- The affordability reserve uses the frozen fallback fee of 10 bps; an actual
  higher fee rejects safely and must be supplied by a future adapter.
- Exchange error-code classification and additional live filters remain
  explicitly deferred until a real adapter task.

## Questions for the reviewer

1. Can any T22-07 arithmetic or Decimal-context path return a quantity above
   the governor bound, above the affordable exact step count, or off step?
2. Can reducing a buy quantity change client-order identity across a resend or
   create two accepted orders under one authorization in the simulator?
3. Does any failure after redemption but before placement strand or release a
   reservation unsafely?
4. Does the cap-plus-27-bps check remain conservative for every fill the
   simulator can execute under the frozen fallback cost model?
5. Did review 4 misclassify either free/locked balance or higher-fee behavior
   as non-blocking within the simulator-only Task 22 boundary?

Return stable IDs under `BLOCKER`, `NON-BLOCKING`, or `QUESTION`. For each,
give file/line, trigger, evidence, impact, and the smallest safe correction.
State missing evidence explicitly. End with ACCEPT or FIX and record the exact
Claude model metadata shown by the reviewing interface.
