# Adjudication of the Sol review of screen S2 at ac8ca71

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-16. Review record: `SOL6_SCREEN_S2_REVIEW_AC8CA71.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S2-R1 | Medium | **Accept.** No test changed the target at the instant a pending order fills. | `test_a_due_fill_comes_before_the_same_instants_decision`: 0.5 decided at 00:00 fills at 01:00, and the 0.3 decided at 01:00 is a reduction due at 02:00. Deciding before the fill would see 0 and refuse an intraday increase. |
| S2-R2 | Medium | **Accept.** The cost test had a constant fee and no delay. | `test_delayed_costs_use_decision_volatility_and_fill_time_fees`: the fee schedule changes at the fill instant (0 to 50 bps) and bar 24 closes at a spike (sigma 93 to 1,480 bps in the decision-to-fill hour). The delayed fill's cost equals the cost model at the decision's sigma and the fill's fee, and differs from both wrong combinations. |

Test-only change; `event_contract.py` is unchanged.

Not repaired: none.

Validation: `pytest tests/unit/test_event_contract.py` 15 passed; ruff check and format clean; mypy clean.
