# Task 22 owner review (Constitution section 16)

Date: 2026-09-27

## What the owner was asked

The coding AI (Claude Opus 5.5) gave a plain-language description of the
executor in `src/aqt/execution/machine.py` and `orders.py`:

- Each approved trade becomes exactly one order with one fixed id. If the
  exchange does not answer, the executor asks about that id, waits, and asks
  again. It resends only that same order, and only while the approval is
  valid.
- If the answer cannot be known, the clock misbehaves, or the exchange shows
  something other than what was sent, it freezes. Nothing new trades until
  the account is checked (Task 23).
- Every order carries the owner's price cap (`OWNER_ANSWER_Q3.md`). Beyond
  it, nothing trades.
- After any order is sent, even a clean fill, the next trade waits for the
  account check.

It then asked three questions, with the answers the owner selected:

1. "Each approved trade may become only ONE order. [...] It resends the same
   order only while the approval is still valid; after that it needs a fresh
   approval. Is that what you want?" — **Yes**
2. "When the system can't tell what happened to an order [...] it FREEZES: no
   new trades until the account is checked. Is that what you want?" —
   **Yes**
3. "After ANY order is sent, even one that filled cleanly, the next trade on
   that coin waits until the account is checked against the exchange (built
   in Task 23). [...] Is that what you want?" — **Yes**

## What this review is, and is not

- It is the owner's **behavioural review**: a confirmation that the
  executor's behaviour, as described, is what the owner wants. It is not a
  line-by-line code review (see `review/task17/OWNER_REVIEW.md`).
- The code was checked by GPT-6 Astra, the different-model reviewer named in
  Q2. Three reviews are recorded (`REVIEW.md`, `REVIEW_2.md`, `REVIEW_3.md`),
  all with verdict FIX, and every finding was repaired
  (`ADJUDICATION*.md`).
- **A fourth Astra review of the R3 repairs (commit `8d69238`) has not
  happened.** The attempt at 09:21 on 2026-09-27 failed on the Codex usage
  limit (reset 13:51). Task 22 must not merge until that review returns
  ACCEPT, or its findings are repaired and accepted.
- Still unset owner values: the protocol delay and absence count (T22-Q1,
  proposal 10 s / 2), and `max_slippage_bps`.
