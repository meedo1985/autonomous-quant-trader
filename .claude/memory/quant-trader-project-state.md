---
name: quant-trader-project-state
description: "Where autonomous-quant-trader stands as of 2026-09-21 — what is blocked, what is open, and what to resume."
metadata: 
  node_type: memory
  type: project
  originSessionId: 018ca6fb-df6b-4e1a-aac6-f0040be4035c
  modified: 2026-09-21T16:36:50.908Z
---

As of 2026-09-21 the project is deliberately halted and that is the correct
state. Cycle `C1` never started, verdict is `KEEP_BLOCKED`, no `D-nn` row of
`review/governance-statistics-amendment/v1.1-method-candidate/HUMAN_DECISION_MATRIX.md`
has moved, and no frozen artifact has been touched.

**PRs #9 and #10 were merged on or before 2026-09-22** (loss-bounds survey; the
Lesson 2 magnitude self-correction). As of 2026-09-22 there are no open PRs and
the working tree is clean. The loss-bounds survey lives at
`review/pre-deployment/LOSS_BOUNDS_AND_OPEN_DECISIONS.md` and records four
decision requests `L-01`–`L-04` to the owner, all still unanswered.

On 2026-09-22 the owner said he has no background in the subject and asked the
AI to choose the loss bounds. PR #11 (merged 2026-09-22, commit `f648029`) proposes `L-02` >= 240 effective
decisions forward, `L-03` a 20% absolute stop from peak live equity, `L-04`
written record plus no increase while below peak. `L-01` (the money amount) is
**declined by the AI and defaulted to zero** — the missing input there is the
owner's finances, not expertise. All four remain **proposals until he adopts
them** in section 6 of `review/pre-deployment/LOSS_BOUND_DEFAULTS.md`.

Also in PR #11: the §25 owner
acknowledgment is now **written out for signature** at
`review/pre-deployment/OWNER_ACKNOWLEDGMENT_S25.md`, nine clauses `C-1`-`C-9`
mapped to the frozen text, signature block blank. The owner reported **Codex
unavailable on 2026-09-22**, so the different-model review of the statistics
curriculum still cannot run.

**Unresolved and worth resuming:**
- The statistics curriculum `.agents/skills/sharpe-selection-statistics/SKILL.md`
  has had **no independent review**. Three Fable attempts died on HTTP 429 out of
  credits. Codex is installed at `~/AppData/Roaming/npm/codex` and is the live
  alternative; the owner was asked which reviewer to use and had not answered.
- `D-16` and `D-17` (effective trial count, and which count enters `A(N)`) are the
  rows where a wrong answer promotes noise, because `A(N)` is monotone in `N` and
  an undercount lowers the hurdle.
- `F-5`/`F-6`/`F-8` on `src/aqt/core/attempts.py`: the partition is a
  caller-supplied label while §9's criterion is a fact about the data mounted; two
  record types both claim to be the §9 count; and nothing forces a caller to call
  `start_attempt`, so counting at evaluation start is a convention not a guarantee.
- Constitution §25 owner acknowledgment is **unsigned**, and §19's required
  deployment protocol **does not exist** — two hard blockers on live trading that
  are independent of every statistical question.

**Why:** the halt is a designed outcome, not a stall; `KEEP_BLOCKED` and
`NO_EDGE_FOUND` are recorded as valid results. Treat a request to "move forward"
as a request to work below the gates, not to open them.

**How to apply:** resume by asking which of the above the owner wants, and note
that §25 is the cheapest safety step available. See [[owner-constraints]] and
[[ai-review-record-discipline]].
