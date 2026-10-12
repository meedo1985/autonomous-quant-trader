# Owner decision: re-pilot size (FE7-1)

**Decision by:** the owner, in the Claude Code session on 2026-10-11, answering one question.
**Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`). This file records the owner's choice; the AI made no decision.

**Question as asked:**
> "Re-pilot size: how many development replications per cell (13 cells)? Rare events can't be measured precisely at any pilot size; each cell's real decision comes from the full run's 12,000."

**Options shown:**
- "1,000 per cell (Recommended)": about 10 hours, one overnight run. It gives speed, memory, cost and a rough event rate, but only resolves rates of about 1 in 1,000 or higher. That is enough for the go-ahead estimate.
- "3,000 per cell": about 1.5 days. Rates resolve to about 1 in 3,000, which is still far from the rare events, but the cost estimate is tighter.

**Owner's choice, verbatim:** "1,000 per cell (Recommended)".

**Disclosed with the choice (Sol FE7-1):**
- At 1,000 development replications, a cell with zero `U_G` events has a 95% upper bound of about 0.003. Pooled over 13 cells, the bound is about 0.0002.
- The re-pilot therefore cannot resolve `U_G` rates near 5·10⁻⁵, the rates the escape estimate turns on. It serves as a cost and smoke measurement.
- Each cell's escape is decided by the full run's own 12,000 development replications (§13 item 3).
