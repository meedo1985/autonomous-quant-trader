# Task 16 owner review, after merge (Constitution section 16)

Date: 2026-09-26

**This review happened after the merge.** PR #24 was merged on 2026-09-26 as
`fbc4abc` without a human PR review (`OWNER_DECISION.md`). GPT-6 Astra recorded
that gap as A-1 (`REVIEW_ASTRA.md`, `ADJUDICATION_ASTRA.md`). A review after the
fact cannot change when the merge happened; it closes the gap only in the
sense that the owner has now looked at the behaviour and confirmed it.

## What the owner was asked

The coding AI (Claude Opus 5.5) gave a plain-language walkthrough of
`run_exploration` in `src/aqt/research/harness.py` as it stands on `main`:
partition and date checks before any data is read (lines 191-208), the job log
call (line 190), gaps never filled (lines 214-217), and results stamped
`NOT_A_REGISTERED_TRIAL` (line 63). The owner first asked for an agent to
answer; the AI declined, because these are questions about what the owner
wants. It then offered the questions as choices.

## What the owner answered, verbatim (selected options)

1. Research locked to the 2017-2021 exploration data, with later periods
   refused: **"Yes"**
2. Gaps never filled in, with short stretches listed instead: **"Yes"**
3. Exploration results never counted as official tests: **"No"**

The AI explained that section 9 (frozen) makes exploration not a registered
trial, and that promising ideas go on to registered trials tested on the
confirmation data. It asked what "No" meant. The owner selected:

> **"Ideas should move on to testing"**: "Good ideas found in exploration
> should be able to go on to official testing on the confirmation data. That is
> already how the project works; the harness stays as it is."

So the owner's answer to question 3 is consistent with the harness and with
section 9. No change to the code follows.

## What this review is, and is not

- It is the owner's **behavioural review**, made after the merge, of the
  behaviour described in the walkthrough.
- It is **not** a line-by-line code review; the owner has said they cannot
  review code.
- The owner's understanding rests on the AI's description. The code was
  checked by Claude Fable (`REVIEW.md`, FIX, repaired) and GPT-6 Astra
  (`REVIEW_ASTRA.md`, no code defect).
