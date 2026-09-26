# Task 21 review adjudication

Review record: `REVIEW.md`, saved as returned. Reviewer: GPT-6 Astra
(`gpt-6-astra`, reasoning effort high, Codex CLI, read-only, session
`01a0dec1-6906-7731-8615-b348c868ff85`), run on 2026-09-26 as the section 16
different-model reviewer named by the owner (roadmap Q2). Packet: the diff
`main...84de545`, both new modules line-numbered, recorded check output (not
rerun), excerpts of `canonical.py` and `bars.py`, `protocol_v1.yaml` lines
49-62 and 111-113, Constitution sections 12, 14, 16, 17 and 20. Verdict:
**FIX**, three blockers.

All three were reproduced on `84de545` before any repair:

| ID | Severity | Decision | Reproduction | Repair |
| --- | --- | --- | --- | --- |
| R-1 | BLOCKER | Accepted | A 00:00 proposal for 0.2 -> 0.8 was authorized at 00:59:59 and redeemed at 01:03 (`redeem` returned `None`). T21-02 narrowed the gap to one bar but did not close it; the TTL could extend it further. | A new required `GovernorConfig.decision_window`: an authorization is issued only within that window after `decision_time`, and it expires no later than `decision_time + decision_window`, whatever the TTL. Its value is `[OPEN]`, so the owner sets it; there is no default. |
| R-2 | BLOCKER | Accepted | Two authorizations for 0.5 from base 2, quote 800 at 100 each allowed 3.0 units, and both redeemed against the same state: 6 units in total, reaching 0.8. | At most one outstanding authorization per symbol: until the last one expires, a new one is refused (`OUTSTANDING_AUTHORIZATION`). After expiry, a new decision starts from the actual state, which then includes any fills. |
| R-3 | BLOCKER | Accepted | Base 0, quote 1000, price 30000, target 0.5 gave `0.01666666666666666666666666666666667` BTC, more than the exact 1/60. | The bound is computed exactly with `fractions.Fraction` and converted to `Decimal` rounding toward zero, so it never exceeds the exact quantity. Tested against an exact rational oracle, including repeating divisions. |

Owner decision created by R-1: the value of `decision_window` (how long after
the 00:00 or hourly decision an order may still be authorized and sent). It
joins `max_slippage_bps` and `authorization_ttl` as open values in the
deployment protocol draft.

## Repair

- R-1: `GovernorConfig.decision_window` (required, at most one bar). A
  proposal is refused as `STALE_DECISION` once `now >= decision_time +
  decision_window`, and `expires_at` is capped at that moment whatever the TTL.
  Test: `test_a_decision_cannot_be_issued_or_redeemed_after_its_window` (a 00:00
  proposal at 00:59 is refused; with a 4h TTL, redemption at 03:00 is refused).
- R-2: one outstanding authorization per symbol until it expires; a new one is
  refused as `OUTSTANDING_AUTHORIZATION`. Test:
  `test_only_one_authorization_is_outstanding_per_symbol` (Astra's scenario).
- R-3: the quantity bound is computed with `fractions.Fraction` and converted
  to `Decimal` with `ROUND_FLOOR`. Test:
  `test_the_quantity_bound_never_exceeds_the_exact_quantity` (6 cases against an
  exact rational oracle, including 1/60 and 1/3).

Mutation checks, each failing at least one test: TTL not capped; window set to
a full bar; overlapping authorizations allowed; rounding to nearest.

Implementer errors in the new tests, fixed before use: the property test
shared one governor across out-of-order times, which the new
one-at-a-time rule then blocked; one test stamped the proposal with the late
time; one case targeted a change inside the band.

Validation after repair, `.venv` Python 3.14.7: `pytest -q` 1391 passed, 4
skipped in 171.57s; `ruff check .` and `ruff format --check .` pass; `mypy src
scripts` no issues in 43 files; `lint-imports` 5 kept, 0 broken; no frozen
path changed.

These repairs have not been re-reviewed.

