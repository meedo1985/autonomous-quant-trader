# Task 21 owner answer: T21-Q1

Date: 2026-09-26

The owner answered, verbatim: "confirm 5 minutes for T21-Q1".

The question, as the coding AI (Claude Opus 5.5) put it after GPT-6 Astra's
finding R2-4: what is the upper limit on how long after a decision an order
may still be authorized and redeemed (`MAX_DECISION_WINDOW`)? The AI proposed 5
minutes, and said the owner could confirm it or choose less.

Effect: `MAX_DECISION_WINDOW` stays at 5 minutes, and is now recorded as the
owner's confirmed limit rather than an AI proposal. `GovernorConfig.decision_window`
may be set at or below it; the actual configured value is still chosen when
the paper loop is configured.

This records the owner's answer to T21-Q1 only. It is not the owner's section 16
PR review of Task 21, which is still required before merge.
