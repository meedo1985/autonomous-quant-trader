Model: GPT-6 Astra

Checks were not rerun by me. All reported checks and mutation results were produced by implementer Claude Opus 5.5 at `94f0b9b`; this review uses only the supplied code and evidence.

**R2-1 — BLOCKER — `src/aqt/governor/machine.py:109–117`, `:186`**

A completed transition still blocks immediate risk reduction. Issue the fixture’s `0.2 → 0.5` BUY at midnight, redeem and fully fill it at 00:01, then request `0.5 → 0.2` using the reconciled holdings and midnight decision timestamp. The governor returns `OUTSTANDING_AUTHORIZATION` until 00:05, although the original token is consumed and its order completed. This contradicts section 14’s immediate reductions. Provide a reconciled completion/supersession path that permits reductions while preventing conflicting execution; simply clearing the reservation on redemption would be unsafe. The new overlap test waits until expiry and never exercises redemption or early completion.

**R2-2 — BLOCKER — `src/aqt/governor/machine.py:110`, `:165`**

Expiry does not establish that a redeemed transition has finished. From base `2`, quote `800`, price `100`, authorize and redeem BUY `3` at midnight; its submitted order remains unfilled at 00:05. A second request for target `0.5` then receives another BUY `3`. The actual balances still include locked amounts, so the second calculation remains unchanged, and sufficient unlocked quote remains to submit it. Both orders can subsequently fill, reaching `0.8`. Keep redeemed transitions reserved until reconciliation establishes completion or cancellation. The test at lines 260–264 assumes the first fill has completed instead of testing this reachable case.

**R2-3 — BLOCKER — `src/aqt/governor/machine.py:110`, `:177–186`**

Clock rollback resurrects an authorization after its reservation has been replaced. With unchanged state and the fixture config, issue A for BUY `3` at 00:00, then B for BUY `3` at 00:05, when A is considered expired. Move `now` back to 00:04 and redeem A; then redeem B at 00:05 before either fills. Both succeed, restoring the original overshoot. Redemption checks neither reservation ownership nor irreversible expiration; it also accepts times before issuance. Reject backward-time use and prevent replaced/expired tokens from becoming executable again. The existing expiry test explicitly permits later redemption after an earlier call already observed expiry.

**R2-4 — BLOCKER — `src/aqt/governor/authorization.py:105`, `src/aqt/governor/machine.py:100–107`**

The accepted configuration `decision_window=timedelta(hours=1)` reproduces R-1’s late issuance: a midnight `0.2 → 0.8` proposal is authorized at 00:59:59 and can immediately be redeemed. Capping expiry at 01:00 fixes the TTL extension but leaves the original within-hour bypass available through valid configuration. Establish and enforce the governed maximum window; the supplied evidence leaves its value open. Tests exercise only ten minutes, so the reported full-bar mutation failure does not establish safety across accepted configurations.

**R2-5 — NON-BLOCKING — `src/aqt/governor/machine.py:53–58`**

The conversion has a narrower exponent range than the accepted finite Decimal inputs. With base `0`, quote `1`, price `Decimal("1e-1000001")`, and target `0.5`, equity/exposure evaluation succeeds, but converting the exact quantity `5e1000000` raises `decimal.Overflow` instead of returning an authorization or refusal. Conversely, base `1e-1000033`, quote `0`, price `1e1000033`, target `0` produces a SELL authorization with quantity zero through underflow, preventing the requested liquidation. Handle these values explicitly or reject unsupported magnitudes at validation. The six rational-oracle cases cover neither exponent boundary.

R-1: **NOT REPAIRED** — TTL is capped, but an accepted full-bar window preserves late issuance.
R-2: **NOT REPAIRED** — simultaneous initial issuance is blocked; unresolved execution and clock rollback still permit overlapping transitions.
R-3: **REPAIRED** — exact rational arithmetic with downward conversion closes the above-exact quantity defect; R2-5 concerns conversion failure and zero quantities.

Verdict: **FIX**