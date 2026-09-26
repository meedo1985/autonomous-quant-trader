# Task 21 second review adjudication

Review record: `REVIEW_2.md`, saved as returned. Reviewer: GPT-6 Astra
(`gpt-6-astra`, reasoning effort high, Codex CLI, read-only, session
`01a0decc-6056-7623-9115-d5cb5556bff6`), run on 2026-09-26 at the owner's
request ("let astra review the task 21 fixes"). Packet: the repair diff
`84de545..94f0b9b`, the current governor modules and tests line-numbered,
recorded checks and mutation results (not rerun), `canonical.py` excerpts,
`protocol_v1.yaml` lines 49-62 and 111-113, and Constitution sections 12, 14
and 20. Verdict: **FIX**. R-3 REPAIRED; R-1 and R-2 NOT REPAIRED.

Reproduced on `94f0b9b` before any change:

| ID | Severity | Decision | Reproduction |
| --- | --- | --- | --- |
| R2-1 | BLOCKER | Accepted | After a 0.2 -> 0.5 buy was redeemed and filled, a reduction to 0.2 at 00:02 returned `OUTSTANDING_AUTHORIZATION`. |
| R2-2 | BLOCKER | Accepted | A redeemed buy of 3 left unfilled; at 00:05 (expired) a second request on the same balances returned another `Authorization` for 3. |
| R2-3 | BLOCKER | Accepted | A issued at 00:00, B at 00:05; redeeming A at 00:04 and then B at 00:05 both returned `None` (allowed). |
| R2-4 | BLOCKER | Accepted | With `decision_window` of one hour, a 00:00 proposal was authorized at 00:59:59. |
| R2-5 | NON-BLOCKING, raised | Accepted, treated as a blocker | With price `1e-1000001` the call did not return within 30 s (it did not reach the `Overflow` Astra predicted; the exact-integer arithmetic on million-digit numbers hangs instead). An unbounded hang in the authorization issuer is a safety defect, so it is repaired, not deferred. The zero-quantity case was not run separately because it uses the same magnitudes. |

## Repair plan

- **R2-1 and R2-2: a reservation lasts until the transition is released.** An
  unredeemed authorization reserves the symbol until it expires, and then can
  never be redeemed. A redeemed one reserves it until `Governor.release` is
  called; the executor calls that only after reconciliation shows the order
  finished or cancelled (a contract for Task 22). After a release, a reduction
  (or any decision) is computed from the reconciled actual state straight away.
  While an order is still unresolved, new authorizations stay refused;
  emergency de-risking while an order is in flight belongs to HALT and FLATTEN
  (Task 23), not to a second overlapping authorization.
- **R2-3: time only moves forward.** The governor refuses any call whose `now`
  is earlier than the latest `now` it has seen (`CLOCK_WENT_BACKWARDS`), and an
  expired authorization is marked dead the first time expiry is observed.
- **R2-4: a hard upper limit on `decision_window`,** proposed by the AI at 5
  minutes. The frozen rule says increases happen "only at 00:00 UTC", so a
  short limit is the conservative reading. This value is a proposal: the owner
  must confirm it or choose a lower one (question T21-Q1). It can only tighten
  the rule, never loosen it.
- **R2-5: bounded magnitudes.** `ActualState` refuses quantities, balances and
  prices whose decimal exponent is outside [-20, 20], so arithmetic stays
  small. A computed quantity of zero is refused (`ZERO_QUANTITY`) rather than
  authorized.
