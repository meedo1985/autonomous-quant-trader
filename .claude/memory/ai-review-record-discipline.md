---
name: ai-review-record-discipline
description: "This repo requires a review's record to be committed before it is cited, and never treats an AI review as authority."
metadata: 
  node_type: memory
  type: project
  originSessionId: 018ca6fb-df6b-4e1a-aac6-f0040be4035c
  modified: 2026-09-21T16:36:59.676Z
---

`AGENTS.md` line 40 requires that a review or adversarial check is not complete
until its record is committed — reviewer model metadata, every finding with its
stable ID, and every finding deliberately left unrepaired with its reason —
committed in or before the commit that applies its repairs. Citing an
uncommitted review record is forbidden.

**Why:** a third adversarial check's report was never written to disk. Six of its
findings survive only because a later document tabulated them; the four
identifiable now solely by the numbering gaps `S1-1`, `S2-1`, `S2-2`, `S3-1` are
unrecoverable. The loss is recorded in
`review/governance-statistics-amendment/v1.1-method-candidate/README.md` §6.5
rather than hidden.

**How to apply:** when a subagent review returns, commit its verbatim record
first and alone, then apply repairs in a separate commit that cites it. Never
write the owner's review, assessment, or signature on his behalf — `review/
attempt-counting/OWNER_REVIEW.md` records his determinations as given and states
plainly that he trusted the process rather than auditing the code, because a
record that overstates itself is worth less than one that admits what it is.
See [[owner-constraints]] and [[quant-trader-project-state]].
