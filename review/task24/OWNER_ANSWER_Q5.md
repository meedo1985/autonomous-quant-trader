# Owner answer to roadmap Q5 (the paper loop's predictor)

Date: 2026-09-27.

## The question (roadmap `ROADMAP_PROPOSAL.md` section 5, Q5, as offered in session)

Should the paper loop's target source be the frozen deployable baseline
`VOL_TARGET_BUY_AND_HOLD` only, or should a placeholder predictor interface
also be reserved for a future model task? The AI recommended the baseline
only.

## The owner's answer, verbatim

> yes baseline only, go Task 24

## Effect

`src/aqt/allocation/predictor.py` returns only the frozen
`VOL_TARGET_BUY_AND_HOLD` target from `aqt.benchmarks.canonical`. No model,
no placeholder model interface, and no other benchmark is selectable. The
owner's stated trading rule (`review/owner-input/TRADING_RULE_2026-09-27.md`)
is not part of the loop.
