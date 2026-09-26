Model: GPT-6 Astra

Checks were not rerun by me. The reported check results were produced by implementer Claude Opus 5.5 at `84de545`. This review uses the supplied code and evidence.

**R-1 — BLOCKER — `src/aqt/governor/machine.py:93`, `:113`, `:162`**

Scheduling checks the proposal timestamp, while issuance accepts any `now` within the following hour. A midnight proposal requesting `0.2 → 0.8` is therefore authorized at `00:59:59`; the final test explicitly expects this. With the fixture's five-minute TTL, redemption against the unchanged actual state also succeeds at `01:03`. Independently, an allowed four-hour TTL permits a midnight authorization to be redeemed at `03:00`.

T21-02 therefore leaves a reachable scheduling bypass. Enforce the governed timing restriction at issuance and redemption; a caller-supplied decision timestamp and configurable TTL cannot extend it. The randomized test misses this because `_decide` always makes `now == decision_time` and never exercises redemption sequences.

**R-2 — BLOCKER — `src/aqt/governor/machine.py:129`, `:145`, `:157–166`**

Distinct nonces permit overlapping authorizations against the same actual state. At midnight, use base quantity `2`, quote balance `800`, mark price `100`, and no previous increase. Request target `0.5` twice: both authorizations allow buying `3` base units. Redeem both before submitting either order. Both redemptions succeed against the still-current actual snapshot.

The resulting permissions allow buying `6` units, reaching exposure `0.8` despite each authorized target being `0.5`. Unique, single-use nonces prevent replay of one token but do not prevent duplicate permissions for one transition. Prevent overlapping executable transitions and require reconciliation or release of the outstanding transition before issuing another conflicting permission. Add this sequential regression test; no concurrency is needed.

**R-3 — BLOCKER — `src/aqt/governor/machine.py:122–127`; `src/aqt/governor/authorization.py:41`**

The quantity bound uses finite-precision, round-to-nearest arithmetic, so it can exceed the quantity implied by the target. At midnight, use base quantity `0`, quote balance `1000`, mark price `30000`, and target `0.5`. The exact maximum buy is `1/60` BTC. The 34-digit division rounds this repeating decimal upward, issuing a maximum strictly greater than `1/60`.

This violates the requested quantity ceiling even at the reference price with no fees or slippage. Decimal arithmetic alone does not make the calculation exact. Derive a conservative bound accounting for intermediate rounding and trade direction, and test repeating divisions against an exact rational oracle.

Verdict: **FIX**