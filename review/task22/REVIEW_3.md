# Task 22 review 3 (Constitution section 16 different-model review)

Reviewer: GPT-6 Astra (`codex exec -s read-only -m gpt-6-astra`, 76,417
tokens). Date: 2026-09-27. Reviewed commit `ce75fd9`. Recorded verbatim.
Adjudication in `ADJUDICATION_3.md`.

---

Model: GPT-6 Astra

Reviewed `ce75fd9` and the complete Task 22 diff against `main`. Findings are static traces; no files edited or validation rerun.

- **R-5 — NOT REPAIRED.** The cap is now transmitted and enforced before filling, but intermediate decimal rounding can loosen it beyond the authorization: R3-1.
- **R2-1 — REPAIRED.** Successful redemption establishes reservation ownership; expiry before the first placement releases it. Sent and replayed authorizations remain protected.
- **R2-2 — REPAIRED.** Cleanup uses the last accepted timestamp and no longer reads and silently suppresses a faulty clock.

**R3-1 — BLOCKER — Intermediate rounding can permit a fill beyond the authorized slippage.**

Location: [orders.py:97](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/orders.py:97), also line 105.

Scenario: BUY with the exact mark `100 − 10^-32`, slippage `15` bps, and tick `0.01`. This mark has 34 significant digits and passes `ActualState` validation.

The exact upper bound is:

```text
100.15 − 1.0015 × 10^-32
```

However, `_DEC.multiply` uses 34-digit round-half-even arithmetic and rounds this **up to 100.15**. Subsequent tick flooring preserves `100.15`; flooring the exact bound would produce `100.14`. A simulator open of `100.15` therefore fills beyond the authorization. Post-fill FREEZE cannot undo that fill.

Repair: calculate the bound and tick count exactly, then round conservatively—BUY downward, SELL upward. Without a tick, use a conservatively directed conversion. Add exact-arithmetic boundary regressions for both sides; the final integral rounding alone does not establish the invariant.

**R3-2 — BLOCKER — Cap-construction failure strands a redeemed reservation without a terminal result.**

Location: [machine.py:384](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/machine.py:384), [orders.py:108](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/orders.py:108).

Scenario: a valid synthetic BUY authorization with mark `100`, slippage `15` bps, and `tick_size=200`. These inputs pass the existing constructors. Redemption succeeds, but tick flooring produces zero and `limit_price_for()` raises `ValueError`. `go()` catches only `_ClockFault`, so execution escapes without reaching `_finish()`.

Nothing was sent, yet the authorization remains spent and reserved. Replay returns `ALREADY_USED`; new decisions encounter `OUTSTANDING_AUTHORIZATION`. A SELL with the currently permitted `max_slippage_bps=10000` also reaches this exception.

Repair: represent an unusable cap as an explicit no-send refusal, log the terminal transition, and release only this invocation’s reservation through the existing ownership guard. Test the result, zero placements, release, and subsequent authorization.

**R3-3 — NON-BLOCKING — An unaffordable out-of-cap price changes expiration into rejection.**

Location: [simulator.py:335](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/simulator.py:335).

Scenario: BUY quantity `5`, quote balance `1000`, cap `100.15`, and next open `1000`. The order is affordable within its cap. The simulator correctly sets executed quantity to zero, but then checks affordability of the entire quantity at the prohibited price `1000`. It raises `INSUFFICIENT_BALANCE`, producing `REJECTED` rather than the specified `NOT_FILLED` outcome.

Repair: ensure affordability validation for capped orders does not price a hypothetical execution beyond their cap. Preserve full-order affordability checks for executable fills and add this larger-gap regression. No unauthorized trade occurs, and the reservation remains held, so this is non-blocking for immediate safety.

The remaining requested checks pass by inspection: BUY/SELL comparison directions are correct; the executor derives the cap solely from the bound state’s mark; the simulator evaluates it against the fill-bar open; frozen fill-price and cost calculations remain unchanged; duplicate identity includes the cap; and `NOT_FILLED` retains the reservation with reconciliation required.

Supplied validation remains implementer evidence: **1475 passed, 4 skipped**, lint/format/type/import checks clean, and reported mutation checks caught. The reviewed diff changes no frozen files or sidecars; hashes were not reverified. This review record still requires committing, and human §16 review remains outstanding.

Verdict: FIX
