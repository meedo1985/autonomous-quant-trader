# Task 16 Astra review adjudication

Review record: `REVIEW_ASTRA.md`, saved as returned. Reviewer: GPT-6 Astra
(`gpt-6-astra`, reasoning effort high, Codex CLI, read-only, session
`01a0de86-3a84-7020-8faf-0881bf7dfd0d`), run on 2026-09-26 after merge at the
owner's request ("yes let astra review task 16 too"). Packet: the diff
`5fda787..fbc4abc`, recorded check output (not rerun), and context from the
manifest, benchmark, engine and klines modules, `protocol_v1.yaml` lines 60-72
and Constitution sections 6, 7, 9, 15 and 16. Verdict: **FIX**.

Astra reported no defect in the code. Its only finding is about the merge
process.

| ID | Severity | Decision | Evidence and action |
| --- | --- | --- | --- |
| A-1 | BLOCKER | Accepted as a record of fact; the remedy is the owner's | `OWNER_DECISION.md` confirms that no human PR review was recorded before the merge of PR #24. Astra reads the harness as section 16 "protocol-enforcement logic"; Fable's review took the same view (T16-Q1). Whether it is protected remains the owner's reading, but on that reading the merge lacked the required human review, and a later review cannot change when the merge happened. The AI cannot supply a human review. Action: record the gap here; ask the owner whether to review the merged code now and have that recorded as a post-merge review. |

## AI process error

Before the merge, the coding AI offered the owner two paths for T16-Q1, and one
of them was to merge without reviewing, which it said it would record as the
owner's decision. Both reviewers read the harness as protected, and on that
reading offering the second path treated a section 16 requirement as optional.
From now on, for work that a reviewer or the AI identifies as possibly
protected, the AI will present the section 16 human review as a condition of
merge, not as one of two options. The owner may still decide that a component
is not protected, and that decision is recorded in their own words.
