# Task 22 review 2 (Constitution section 16 different-model review)

Reviewer: GPT-6 Astra (`codex exec -s read-only -m gpt-6-astra`, 92,393
tokens). Date: 2026-09-27. Reviewed commit `a3bb5af`. Recorded verbatim.
Adjudication in `ADJUDICATION_2.md`.

---

Model: GPT-6 Astra

Reviewed commit `a3bb5af`, including the first review, adjudication, report update, implementation, and both executor test files. Findings below are static traces; I did not rerun validation or edit files.

- **R-1 — REPAIRED.** [`machine.py:353`](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/machine.py:353) redeems before quantity calculation. `ALREADY_USED` never sets `releasable`; the governor checks prior use before `STATE_CHANGED`. The replay regression at `tests/unit/test_executor.py:499` exercises the original frozen-reservation bypass.

- **R-2 — REPAIRED.** [`machine.py:466`](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/machine.py:466) permits release only with zero placement attempts. The counter increments before calling the venue, including calls that subsequently raise. Every sent path retains the reservation and returns `reconciliation_required=True`. The hidden-fill regression at `tests/integration/test_executor_simulator.py:162` verifies that lagging absence responses cannot reopen authorization.

- **R-3 — REPAIRED.** [`machine.py:372`](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/machine.py:372) checks `now >= expires_at` immediately before every submission. Its expired transition exists from `SUBMITTING`; both initial placement and resend pass through this guard. The boundary regression at `tests/unit/test_executor.py:540` covers expiry after redemption. Its reservation aftermath exposes **R2-1** below.

- **R-4 — REPAIRED**, for the original rollback/retry defect. [`machine.py:306`](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/machine.py:306) rejects decreasing observations. `fire()` reads time before changing state, so a rollback during transition logging leaves a live source state with a defined `CLOCK_FAULT → FREEZE` transition. The exception handler supplies the last accepted timestamp without rereading the faulty clock. The placement cap uses exact integer timedelta division; its extra allowance at an exactly divisible lifetime is conservative because the expiry guard remains authoritative. The regression at `tests/unit/test_executor.py:555` covers rollback during placement. Terminal cleanup has a separate reporting defect, **R2-2**.

- **R-5 — REJECTED-DEFERRAL.** Containment is repaired: [`machine.py:450`](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/machine.py:450) detects an excessive adverse move before accepting the fill outcome, freezes, and retains the reservation. However, `tests/integration/test_executor_simulator.py:154` still demonstrates an actual simulated fill at **100 bps against a 15-bps authorization**. The venue receives no price bound.

  Simulator-only scope does not resolve this requirement: Constitution §20 binds maximum slippage, and [`ROADMAP_PROPOSAL.md:441`](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/roadmap/ROADMAP_PROPOSAL.md:441) explicitly promises that authorization is never exceeded. FREEZE is appropriate containment, but T22-Q3 remains an unresolved acceptance blocker. Deferring the execution-contract choice to the owner is appropriate; treating that deferral as satisfying §20 is not. Obtain a documented governance-compatible resolution before closing R-5. Do not silently alter frozen fill semantics or inspect future prices to avoid breaches.

- **R-6 — ACCEPTED-DEFERRAL**, restricted to Task 22’s simulator. [`orders.py:6`](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/orders.py:6) now states the required deduplication assumption. `simulator.py:249` returns the existing order before creating another fill; integration tests inspect fill events and balances. Binance’s current documentation still permits client-ID reuse after a previous fill, so a real-adapter guarantee remains deferred. [Official documentation, checked 2026-09-27](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade). The specific hidden-fill → two negative queries → unexpired resend integration regression remains useful follow-up coverage.

**R2-1 — BLOCKER — Expiry before first submission strands a redeemed reservation without requesting reconciliation.**

Location: [`machine.py:376`](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/machine.py:376), `machine.py:469`, `machine.py:483`.

Concrete scenario: use the existing boundary-expiry test. Redemption succeeds just before expiry; the submission guard then detects expiry and sends nothing. The result is:

```text
state = NEW_AUTHORIZATION_REQUIRED
released = False
reconciliation_required = False
```

`releasable` was never set, and `_finish()` only releases `REFUSED` runs. The governor retains redeemed reservations beyond expiry (`governor/machine.py:142–149`). A fresh proposal within the decision window therefore receives `OUTSTANDING_AUTHORIZATION`; replay receives `ALREADY_USED`. Waiting does not clear it.

Suggested repair: explicitly resolve reservations owned by this invocation when expiry prevents its first submission—either release through the established no-send abandonment path, or retain and truthfully signal required reconciliation. Extend the boundary test to assert reservation disposition and the resulting governor behavior. Preserve the prohibition on releasing previously sent or replayed authorizations.

**R2-2 — NON-BLOCKING — Cleanup silently suppresses a clock fault.**

Location: [`machine.py:472`](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/machine.py:472).

Concrete scenario: use zero-quantity filters and clock readings `[t, t, t − 1 second]`, with `t` valid for redemption. `_begin()` redeems and records `NO_QUANTITY → REFUSED`; `_finish()` detects rollback on its release-time reading and silently passes. The result reports `REFUSED`, no clock-fault transition, `released=False`, and `reconciliation_required=False`, despite the comment saying reconciliation must clear the reservation.

Suggested repair: make the final clock check part of the state-machine outcome before committing the terminal refusal, or explicitly represent and log failed cleanup with a recovery requirement. Simply firing `CLOCK_FAULT` from the current terminal `REFUSED` state would raise `IllegalTransition`. Add the three-reading regression. This is non-blocking for immediate order safety because nothing was sent and the reservation remains held.

I found no reachable repaired-code path that releases after sending, submits after an observed expiry, or submits after entering FREEZE. No additional live-state transition gap was found.

Implementer evidence remains: `pytest -q` **1467 passed, 4 skipped**; Ruff check/format, mypy, and import contracts passed. The working tree is clean; the reviewed commit range changes no frozen files or sidecars. Hash verification and mutation outcomes remain implementer-reported. This response must be committed as the second review record; human §16 review remains outstanding.

Verdict: FIX
