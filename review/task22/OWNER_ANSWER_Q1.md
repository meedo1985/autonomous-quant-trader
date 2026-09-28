# Owner answer to T22-Q1 (protocol delay and confirmed-absence count)

Date: 2026-09-27.

## The question as asked (by Claude Opus 5.5)

"Order check timing: after a 'not found' answer, how long to wait before
asking the exchange again, and how many 'not found' answers mean the order
really doesn't exist. I suggest 10 seconds and 2 answers."

## The owner's answer, verbatim

> use 10 seconds and 2 answers

## Effect

- `ExecutorConfig(not_found_delay=10 seconds, absence_queries=2)`. Two is
  the minimum the frozen section 21 wording allows.
- Deployment protocol draft section 7: the `[OPEN]` value becomes
  `[OWNER-SET T22-Q1]`. The draft as a whole is still not adopted.
- The code sets no defaults. The value is passed as configuration by the
  process that runs the executor (Task 24).
- Confirmed absence never releases a reservation (Astra R-2), so a venue
  that lags longer than two answers cannot cause an unseen double position.
  The worst case is a resend under the same id, which the simulator
  deduplicates (R-6 covers the real venue).
