# Task 21 owner review (Constitution section 16)

Date: 2026-09-26

## What the owner was asked

The coding AI (Claude Opus 5.5) gave a plain-language walkthrough of
`Governor.decide`, `redeem` and `release` in `src/aqt/governor/machine.py`, with
line references, and asked three questions:

1. Do you want risk increases only at 00:00 UTC, at most once a day, and
   daytime changes only as cuts of at least 10 points?
2. Do you want every trade to need a single-use approval that expires within
   5 minutes and is refused if the holdings changed?
3. Is it fine that emergency exits are handled separately, by FLATTEN in
   Task 23, rather than by this governor?

## What the owner answered, verbatim

> 1 dont want to increase
> 2 yes
> 3yes if its ok

Answer 1 was ambiguous. The AI explained that every position starts at 0%, so
without increases the system could never buy, and that real money is already
kept at zero by the adopted loss bound L-01 = 0. It then asked the owner to
choose. The owner selected, verbatim:

> "Keep the rule as is (Recommended)"

That option read: "Buying/increasing is allowed, but ONLY at 00:00 UTC and at
most once a day; daytime changes are cuts only. Real money stays at zero anyway
because L-01 = 0. PR #26 can be merged as it is."

On answer 3, the AI told the owner that the choice was theirs and that GPT-6
Astra had reviewed and accepted the split (`REVIEW_4.md`).

## What this review is, and is not

- It is the owner's **behavioural review**: a confirmation that the governor's
  behaviour, as described in the walkthrough, is what the owner wants.
- It is **not** a line-by-line code review. The owner has said they cannot
  review code (see `review/task17/OWNER_REVIEW.md`).
- The owner's understanding rests on the AI's description. The code was checked
  by GPT-6 Astra, the different-model reviewer named in Q2, across four
  reviews: `REVIEW.md`, `REVIEW_2.md`, `REVIEW_3.md`, and `REVIEW_4.md`, whose
  verdict was ACCEPT.
- The owner also confirmed the 5-minute decision window (`OWNER_ANSWER_Q1.md`).
  `max_slippage_bps` and `authorization_ttl` are still unset owner values, and
  the governor cannot run without them.

## Effect

With the different-model reviews and this owner review recorded, the section 16
conditions for merging Task 21 are treated as met. The owner's instruction to
proceed was "next 1", in reply to the AI's offer to do the walkthrough and then
merge.
