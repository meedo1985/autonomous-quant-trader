# Owner decision: development threshold pooling (I2BW-1)

**Decision by:** the owner, in the Claude Code session on 2026-10-11, answering a question.
**Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`). This file records the owner's choice; the AI made no decision.

**Question:**
> How should the window classifier's thresholds be pooled? The preregistration (§3.5) says "per T level, over all candidate cells". The engine currently also separates by family size K.

**Owner's choice, verbatim:** "Pool over all K (Recommended)".

**The option as presented:**
> Follows the accepted text literally, so no amendment is needed. Each threshold becomes the extreme over every cell at that T, whatever K. Correlation thresholds come from K ≥ 2 cells only, and K is still checked exactly. The thresholds come out wider, so fewer windows are refused, and the refusal-rate guarantee still holds.

**Effect:**
- This replaces item 1's per-K default (`ITEM1_DEVELOPMENT_AND_CHOICES.md`, "Interpretations made here", item 1).
- It implements §3.5 item 2 as written.

**Review trail:**
- `SOL6_ITEM2B_Q5_WIRING_REREVIEW_B6EDC5C.md`, finding I2BW-1.
