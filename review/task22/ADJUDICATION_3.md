# Task 22 adjudication of Astra review 3

Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the implementer. Date:
2026-09-27. Review: `REVIEW_3.md` (GPT-6 Astra, verdict FIX, commit `ce75fd9`).
Reviewer confirmed R2-1 and R2-2 as REPAIRED.

| ID | Verdict | Repair |
| --- | --- | --- |
| R3-1 BLOCKER (R-5 not yet repaired) | **Accepted, repaired.** The trace was confirmed: 34-digit round-half-even arithmetic lifted the exact bound `100.15 - 1.0015e-32` to `100.15`. | `limit_price_for` computes the bound exactly with `Fraction`, floors (buy) or ceils (sell) to the tick exactly, and converts to `Decimal` with rounding directed toward the mark. Test `test_the_price_cap_is_never_looser_than_the_exact_bound` covers the reviewer's two boundary cases plus 500 random marks and bounds on both sides, with and without a tick, and checks the cap against the exact bound. It fails on the previous code. |
| R3-2 BLOCKER | **Accepted, repaired.** | `limit_price_for` returns `None` when no positive price lies within the bound. The executor fires `NO_VALID_PRICE` (READY → REFUSED). Nothing is sent and the redeemed reservation is released through the existing ownership rule. Test `test_no_valid_price_refuses_and_releases_instead_of_raising` (tick 200) also checks that a fresh decision is then authorized. It fails on the previous code. |
| R3-3 NON-BLOCKING | **Accepted, repaired.** | A capped buy is checked for funds at its cap, as the venue locks quote at the limit price. It is never checked at a fill price the cap forbids. Test `test_a_capped_buy_is_checked_for_funds_at_its_cap` fails on the previous code. |

Validation after repair: `pytest -q` 1478 passed, 4 skipped in 96.07s; ruff
check and format clean; `mypy src scripts` clean (46 files); lint-imports 5
kept, 0 broken. Frozen files are identical to the pre-task snapshot.
