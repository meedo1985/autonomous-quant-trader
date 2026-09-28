# Owner answer: what the L-03 loss stop does (S-4 reconfirmed)

Date: 2026-09-28. Asked by Claude Opus 5.5.

## Why it was asked

On 2026-09-27 the owner chose S-4 (`review/deployment/OWNER_SETTINGS_2026-09-27.md`):
at the L-03 breach the system sells everything in FLATTEN steps, then HALTs.
That record was on the Task 24 branch only. The Task 23 review on its own
branch could not see it, and T23-C1 restored L-03 to HALT, which was merged
to `main` in PR #29.

The AI's Task 23 behavioural question 1 (`review/task23/OWNER_REVIEW.md`)
then described the loss stop as entering HALT, without checking S-4. The
owner's "Yes" there was given without the conflict before him, so it was
not treated as overriding S-4. The AI told the owner this was its mistake.

## The question as asked

"When the 20% loss stop fires, what should the system do?"

- "Sell, then HALT (your S-4)": sells in steps (at most half per hour, never
  below 1% under the market price), then stops. Limits further losses if the
  price keeps falling, but locks in the loss. This is what you chose on
  2026-09-27.
- "HALT and keep coins": stops all trading and keeps the coins until you
  decide. Nothing is sold automatically; if the price keeps falling, the loss
  grows. This is what main does now.

## The owner's answer

**"Sell, then HALT (your S-4)"**.

## Effect

`safety.py` on `task24-paper-loop-v2`: LOSS_STOP from RUNNING or HALT enters
FLATTEN, and from FLATTEN keeps FLATTEN (it no longer stops the selling).
Every other alarm during FLATTEN still enters HALT (T23-QB). This amends the
Task 23 behaviour the owner approved in question 1 of `OWNER_REVIEW.md`, and
is part of Task 24's reviews.
