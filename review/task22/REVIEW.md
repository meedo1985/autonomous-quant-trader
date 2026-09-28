# Task 22 review 1 (Constitution section 16 different-model review)

Reviewer: GPT-6 Astra (`codex exec -s read-only -m gpt-6-astra`, reported model
`gpt-6-astra`, 83,964 tokens). Date: 2026-09-27. Reviewed commit `34043c7`.
Recorded verbatim below. Adjudication is in `ADJUDICATION.md`.

---

Model: GPT-6 Astra

**R-1 — BLOCKER — A zero-quantity replay releases a frozen reservation.**
[src/aqt/execution/machine.py:291](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/machine.py:291), lines 412–415.

Scenario: execute an authorization with `Fault(timeout=True, unknown_queries=1)`. The order fills, but the executor returns `FREEZE` and retains its reservation. Construct another executor using the same governor and authorization, with `min_qty=10` against the authorized quantity of 5. The zero-quantity branch skips `redeem()`, sets `release_unredeemed=True`, and successfully releases the **already-redeemed** authorization. New decisions become possible without reconciliation.

Suggested repair: establish single-use ownership before permitting abandonment. A zero-quantity invocation must never release an authorization previously redeemed by another invocation. Add the two-execution regression above.

**R-2 — BLOCKER — Automatic release bypasses the Task 21 reconciliation contract.**
[src/aqt/execution/machine.py:410](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/machine.py:410).

`_finish()` releases redeemed authorizations without reconciliation or a refreshed account state. The existing unit test at `tests/unit/test_executor.py:167` even requests another authorization using the original, pre-fill state.

A stronger simulator-only scenario is `Fault(timeout=True, not_found_queries=2)` with sleep extending beyond authorization expiry. The exchange fills the first order, hides it from both queries, and the executor returns `NEW_AUTHORIZATION_REQUIRED`, `order=None`, `released=True`. A new authorization against the unchanged input state can then execute another order despite the undiscovered fill.

Suggested repair: retain redeemed reservations until the required reconciliation confirms the outcome and establishes the actual state for subsequent decisions. Task 22 can return a pending-reconciliation result without implementing all of Task 23.

**R-3 — BLOCKER — Authorization can expire between validation and placement.**
[src/aqt/execution/machine.py:322](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/machine.py:322), lines 331–339.

Scenario: the confirmed-absence check reads `expires_at − 1 microsecond`. `fire(AUTHORIZATION_VALID)` then reads a time at or after expiry. The next loop iteration calls `_place()` unconditionally. The resend occurs after expiry, even though the transition log itself can show that expiry has passed. Initial placement has the corresponding gap after `redeem()`.

Suggested repair: check validity immediately at the submission boundary for every attempt, with explicit expired transitions. Test clock advancement between redemption/authorization validation and submission; the current expiry tests advance time only during sleep.

**R-4 — BLOCKER — Backward clock jumps bypass the termination argument.**
[src/aqt/execution/machine.py:248](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/machine.py:248), lines 315–325.

Only the interval surrounding `sleep()` is checked. A backward jump during placement or querying is accepted.

Concrete scripted scenario: each placement resets the injected clock to the issuance time and times out; every query returns `NOT_FOUND`; each sleep advances the clock by the required ten seconds. Every sleep check passes, every resend check sees an unexpired authorization, and execution loops indefinitely. The governor’s monotonic-time protection is never consulted during those retries.

Suggested repair: reject backward observations throughout the run, transition to `FREEZE`, and retain the reservation. Add a regression with rollback outside sleep and a bounded test timeout.

**R-5 — BLOCKER — Maximum slippage is observational rather than an authorization bound.**
[src/aqt/execution/machine.py:331](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/machine.py:331), lines 410–424.

The venue receives neither the reference price nor the authorized slippage limit. The integration test already demonstrates the failure: a 15-bps authorization fills at a 100-bps adverse move, ends `FILLED`, and releases its reservation. The breach is calculated only after release.

Suggested repair: establish an execution contract that can honor the authorized bound, or refuse execution when it cannot. Preserve the frozen backtest semantics; any incompatible governance interpretation requires the applicable approval process. Freezing after an excessive fill can contain subsequent activity, but cannot retroactively enforce the original bound.

**R-6 — NON-BLOCKING — One client ID does not prove one exchange order.**
[tests/unit/test_executor.py:308](D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_executor.py:308); `src/aqt/execution/orders.py:3`.

The fuzz assertion proves identical request tuples and per-request quantity bounds. It does not count distinct accepted orders or cumulative fills. The simulator supplies permanent deduplication independently of the executor.

For a venue that accepts reuse after a fill, the sequence “fill, lost response, two lagging `NOT_FOUND` responses, resend” can execute the full quantity twice while every current tuple assertion passes. Binance explicitly permits client-ID reuse after the previous order fills. [Official order documentation, checked 2026-09-27](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade).

Suggested repair: qualify the guarantee as simulator-specific, document the required venue semantics, and test accepted-order identities and cumulative executed quantity. This is non-blocking for the explicitly simulator-only scope, but blocks carrying the present guarantee into a real adapter.

Comments on the disclosed deviations and questions:

- **T22-01 / T22-03:** No objection within the stated simulator-only scope.
- **T22-02:** The current simulator documents `ExchangeError` as a rejected request, so I do not classify its existing placement errors as a separate blocker. However, wrapping backend timeouts or server errors in that type would immediately produce `REJECTED` and release. Before another adapter, require explicit rejection classification with unknown outcomes handled conservatively. Binance documents backend timeout and HTTP 5xx outcomes as potentially successful. [Official API documentation](https://developers.binance.com/en/docs/products/spot/rest-api).
- **T22-04:** Disagree; R-1 and R-2 show why the disclosed release shortcut is unsafe.
- **T22-05:** Disagree with the claimed unconditional placement bound; R-4 supplies a counterexample. The hanging mutation also needs a bounded test failure.
- **T22-06 / T22-Q2:** Disagree that report-only is sufficient to honor §20. Post-breach handling and prevention of an unauthorized fill are separate obligations.
- **T22-Q1:** Explicit configuration without defaults is appropriate. Two negative responses do not establish reliable absence under the simulator’s own arbitrary query-lag faults; R-2 demonstrates the consequence. The proposed values remain unapproved.

Reviewed commit: `34043c717e4176695d5a0583f55f3033c5871710`. Findings are static traces, not executed reproductions. I did not rerun validation; the supplied results remain implementer evidence. The working tree is clean and the diff against `main` contains only the seven listed files. No files were edited. This review record still needs to be committed by the implementer, and human review remains outstanding.

Verdict: FIX
