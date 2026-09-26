# Owner approval of the roadmap proposal

**Document approved:** `review/roadmap/ROADMAP_PROPOSAL.md` (PR #13, head
`e25b651`).
**Date:** 2026-09-26.
**Given by:** the repository owner, as an instruction to the coding AI (Claude
Opus 5.5) in a Claude Code session. The owner's words, verbatim:

> approve the roadmap and merge PR 13

The coding AI wrote this record and performed the merge on that instruction. It
did not approve anything itself. This record states what the owner said and
nothing more: it does not state that the owner audited the roadmap line by
line, and it adds no assessment on his behalf.

## What the approval authorizes

Per the roadmap's own approval clause:

- **Tasks 13–20 are authorized, in order, subject to the answers to Q1–Q5.**
- **Tasks 21–25 may be written but may not merge** until Q2 is answered and the
  Constitution section 16 different-model plus human review is on record.

The approval authorizes no trading, no credentials, no confirmation or lockbox
access, no cycle start, no trial registration, no statistical binding, and no
change to any frozen artifact. Those remain out of scope exactly as roadmap
section 0 and section 3 state.

## Questions still unanswered at approval

| Question | Status | Effect |
|---|---|---|
| Q1: does a simulated equity curve trigger section 25? | **Unanswered** | Task 16 must not start until answered, because the roadmap's safest reading makes the section 25 signature a prerequisite. |
| Q2: who is the section 16 reviewer? | **Unanswered** | Tasks 21–25 cannot merge. |
| Q3: which partitions does Task 13 download? | **Unanswered** | Task 13 (PR #14) implements the conservative reading: exploration only, enforced in code. |
| Q4: who executes the network calls? | **Unanswered** | Task 13 implements the conservative reading: the owner runs the CLI; the AI makes no network call. |
| Q5: the paper loop's predictor | **Unanswered** | Needed only by Task 24. |

Answering Q3 or Q4 differently from Task 13's reading would require a change to
Task 13 before or after it merges.
