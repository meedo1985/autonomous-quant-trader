# Owner decision: item 2b step 2 readings (QJ and coverage)

**Decision by:** the owner, in the Claude Code session on 2026-10-11, answering four questions.
**Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`). The AI made no decision. These are readings of the accepted preregistration, not amendments. Context: `ITEM2B_STEP2_PLAN.md`.

| Q | Question as asked (shortened) | Owner's choice, verbatim |
|---|---|---|
| Q2 | How should the window classifier check a QJ window? | "Per family (Recommended)": the trend half and the vol half are checked separately, each on its own K columns. |
| Q3 | Should the two families' `U_G` bootstrap draws in a QJ cell use the same outer seed? | "Shared seed (Recommended)": as written; the budget already assumes the two tests are not independent. |
| Q4 | What happens if a QJ cell's joint `U_proc` (bound 0.01) fails in development? | "Check and demote (Recommended)": if the 90% UCB exceeds the limit, the cell is demoted to a challenge cell. |
| Q5 | Coverage readings: "ρ > 0" covers equicorrelated, near-duplicate, duplicate, cluster and factor cells, but not opposites. QJ at K = 2 counts as two-trial. Q5 counts for one-trial and two-trial. GARCH (Q3) and skew-t do not count as heavy tails. | "Yes, these readings (Recommended)" |

Q1 was not asked. P:52 and P:310-319 make `M` one count over every enumerated test, "taken from the manifest".
