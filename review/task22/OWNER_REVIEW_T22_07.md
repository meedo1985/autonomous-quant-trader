# Task 22 owner review addendum: T22-07 and reviewer metadata

Date: 2026-09-28.
Pull request: #28, `task22-executor` into `main`.

## What the owner was asked

After the fourth independent review accepted the code, the owner was asked to
approve both remaining section 16 items:

1. A buy may be reduced to the largest affordable step at its authorized price
   cap. If the minimum valid quantity is unaffordable, nothing is sent and the
   authorization is released.
2. The recorded OpenAI GPT-6 family review satisfies the owner's
   different-model requirement even though this interface did not expose the
   exact `gpt-6-astra` service suffix.

The owner was told that approval would be recorded, PR #28 marked ready, and
merged after CI passed.

## Owner response, verbatim

> i confirmed that and aproved

## Effect

The owner approved both stated items. This closes the human behavioral review
for T22-07 and accepts `review/task22/REVIEW_4.md` as the different-model review
chosen for this merge. Together with the earlier owner review in
`OWNER_REVIEW.md`, Constitution section 16's human-review requirement for Task
22 is satisfied.

This approval applies only to Task 22's deterministic simulated-exchange
scope. It does not authorize credentials, testnet or live orders, a live
adapter, shadow mode, promotion, or any change to frozen governance.
