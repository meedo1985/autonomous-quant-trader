# Task 20 independent adversarial review

Model: GPT-6 Astra.
Checks were not rerun by me. The supplied check output was produced by the implementer, Claude Opus 5.5, at `cca2750`. This review uses only the supplied text.

## R-1 — BLOCKER — Deployment draft §3, steps 1–4
Reconciliation reads exchange open orders but never requires each exchange order to have a matching local record. An exchange-side sell order absent from the local registry can leave total asset balances unchanged while locking existing BTC. All local-order checks can pass, yet that outstanding order can subsequently fill outside the restarted executor's tracked state.
Require reconciliation of exchange orders against local orders in both directions, including reserved balances; unmatched exchange orders must prevent startup.

## R-2 — BLOCKER — Deployment draft §2 and §2.2(2)
Paper explicitly permits historical data, and shadow entry requires only completion of the `L-02` paper period. Historical replay can therefore satisfy the gate described in §1 as a **forward** paper period.
Distinguish historical simulation from forward paper operation and require the `L-02` evidence to come from the latter. This finding does not concern the expected stale PENDING status.

## R-3 — BLOCKER — Deployment draft §10(1)
An immediate return from canary to shadow or paper has no prerequisite for resolving live orders or managing retained live exposure. Switching to the shadow configuration removes the order-sending adapter, but an already accepted canary order can still fill at Binance.
Define a transition procedure that resolves outstanding orders and explicitly assigns management of remaining live exposure before disabling live execution. Changing the stage alone is not necessarily a risk reduction under frozen §14.

## R-4 — NON-BLOCKING — Deployment draft §4(7)
The refusal condition covers **any secret** outside the executor identity, while its frozen citation restricts **production keys** to that identity. A separate external alert service holding its own messaging credential would trigger this refusal despite satisfying the cited identity restriction.
Narrow the condition to production trading keys, or mark the broader identity restriction as proposed and reconcile it with the external alert design.

## R-5 — NON-BLOCKING — `tests/unit/test_deployment_protocol_draft.py`, `QUOTES` and protocol-reference tests
The count assertion prevents a wholly empty test run, but individual citations can still escape validation. `QUOTES` skips the syntax already used in §3: `[FROZEN §19 "Startup reconciliation required"]`. Replacing that quotation with an invented requirement leaves the section valid and does not reduce the existing matched-quotation count.
Also, replacing `protocol:303-304` with `protocol:304-303` produces an empty validation loop; the separate hard-coded key checks still pass.
Recognize every supported quotation syntax and reject reversed ranges before iteration.

T20-01 is justified by the reported exact-inventory constraint: placing this proposal under `review/deployment/` avoids adding to the frozen inventory. The referenced verifier itself was not supplied for independent inspection.

**Verdict: FIX.**