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

## Repair

As planned above:

- `Governor.release(authorization, now)` ends a reservation. A redeemed
  authorization stays reserved until released; an unredeemed one lapses at
  expiry, or on release, and is then dead for good.
- `now` may never move backwards (`CLOCK_WENT_BACKWARDS`), in `decide`,
  `redeem` and `release`.
- `MAX_DECISION_WINDOW` is 5 minutes (AI proposal, question T21-Q1 to the
  owner). `GovernorConfig` refuses a longer window.
- `ActualState` refuses values with a decimal exponent outside +/-20 or more
  than 34 significant digits. A computed quantity of zero is refused.

Tests: `test_a_redeemed_transition_is_reserved_until_released` (R2-1, R2-2),
`test_time_never_moves_backwards` (R2-3),
`test_an_abandoned_authorization_can_never_be_redeemed`,
`test_the_decision_window_cannot_exceed_its_limit` (R2-4) and
`test_extreme_magnitudes_are_refused_at_once` (R2-5, 4 cases). Three earlier
tests reused one governor across out-of-order times; the new clock rule
refused them, so each scenario now gets its own governor. `ZERO_QUANTITY` is a
guard with no test: with bounded values, a change that reaches the 0.10 band
always needs a nonzero quantity.

Mutation checks, each failing at least one test: a redeemed reservation lapsing
at expiry; the clock allowed to go back; dead authorizations not remembered
(first survived, and caught after adding the abandon test); a one-hour window
limit; unbounded exponents.

Validation after repair, `.venv` Python 3.14.7: `pytest -q` 1399 passed, 4
skipped in 187.23s; `ruff check .` and `ruff format --check .` pass; `mypy src
scripts` no issues in 43 files; `lint-imports` 5 kept, 0 broken; no frozen
path changed.

These repairs have not been re-reviewed.
