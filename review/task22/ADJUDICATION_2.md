# Task 22 adjudication of Astra review 2

Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the implementer. Date:
2026-09-27. Review: `REVIEW_2.md` (GPT-6 Astra, verdict FIX, commit `a3bb5af`).

| ID | Verdict | Action |
| --- | --- | --- |
| R-1 to R-4 | Reviewer: REPAIRED | none |
| R-6 | Reviewer: ACCEPTED-DEFERRAL (simulator only) | The hidden-fill, two NOT_FOUND, unexpired-resend integration regression the reviewer suggested is not added. The existing hidden-fill test covers the expired branch, and the simulator deduplicates ids. Left as follow-up coverage. |
| R-5 | Reviewer: REJECTED-DEFERRAL. Containment is accepted, but section 20's slippage bound is still not enforced before the fill. | **Open, owner decision T22-Q3.** Enforcing the bound needs a price-capped order, which changes the execution contract. The reviewer says not to change fill semantics silently. The AI does not decide this. Task 22 stays open until the owner answers. |
| R2-1 BLOCKER | **Accepted, repaired.** Confirmed: expiry before the first placement left a redeemed reservation that was neither released nor flagged. | A successful redemption makes the run the owner of the reservation. A run that sent nothing now releases it at `REFUSED` or `NEW_AUTHORIZATION_REQUIRED`. FREEZE still keeps it. The boundary test now asserts `released=True`, `reconciliation_required=False`, `ALREADY_USED` on replay, and that a fresh decision is authorized. |
| R2-2 NON-BLOCKING | **Accepted, repaired.** | `_finish` no longer reads the clock. It releases at the last accepted reading, so no fault can be found and swallowed after the terminal state. Test: `test_a_clock_fault_at_the_end_is_not_hidden`. |

Validation after repair: `pytest -q` 1468 passed, 4 skipped in 93.28s;
ruff check and format clean; `mypy src scripts` clean (46 files); lint-imports
5 kept, 0 broken. Frozen files are identical to the pre-task snapshot.

These repairs have not been re-reviewed. The third Astra review waits for the
owner's T22-Q3 answer, so that one review covers both.

## R-5 after the owner's answer (`OWNER_ANSWER_Q3.md`, "Cap the price")

**Repaired.** Every order is now immediate-or-cancel, capped at
`max_slippage_bps` from the mark price (`orders.limit_price_for`, rounded to
the tick toward the mark). The simulator fills a capped order at the next open
only if that open is within the cap. Otherwise the order expires with nothing
filled (`NOT_FILLED`, reconciliation required). The fill price and the frozen
cost model are unchanged. No future price is consulted: the cap comes from
the mark, and the venue alone decides at the fill. The slippage FREEZE stays
as a backstop in case a venue breaks the cap.

Simulator additions: an optional `limit_price` on `place_order` (part of the
duplicate-id identity), `Order.limit_price`, and `SymbolFilters.tick_size`,
read from `PRICE_FILTER` (a tick of 0 means no tick rule). `PERCENT_PRICE` is
not modelled (disclosed).

Tests: `test_a_gap_beyond_the_price_cap_trades_nothing` (integration: open 100
bps up, cap 15 bps, balances unchanged),
`test_every_order_carries_the_price_cap_of_its_authorization`,
`test_the_price_cap_rounds_toward_the_mark_on_the_tick`,
`test_an_unfilled_capped_order_ends_not_filled`, and four simulator tests.
Mutations caught: executor sends no cap, venue ignores the cap, cap rounded
away from the mark, no-fill treated as partial, R2-1 release removed.

Validation: `pytest -q` 1475 passed, 4 skipped in 81.31s; ruff, format, mypy
(46 files) and lint-imports clean; frozen files unchanged.

Disclosed divergence: the backtest assumes every order fills. With the cap,
paper trading skips a trade when the next open gaps beyond the bound, so
paper and backtest results can differ.
