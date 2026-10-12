# Owner decision: the cutoff reading of the gap rule (GAP-1)

**Decision by:** the owner, in the Claude Code session on 2026-10-12, answering one question.
**Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`). This file records the owner's choice; the AI made no decision.

**Context.** `SOL6_GAP_REVIEW_7333F1C.md` GAP-1 and its adjudication. Of every reading measured (`gap_sensitivity.py`), only the cutoff reading changes `g`.

**Question as asked:**
> "The frozen protocol says the gap ends at the 'first lag after which no remaining lag is significant'. For weekly (168 h) targets, lags 1 to 7 days show dependence and lag 8 onward doesn't. Which reading fixes g? (Every other reading I checked gives the same g.)"

**Options shown:**
- "Lag 7, g = 7 (Recommended)": After lag 7, no lag is significant, so the cutoff is 7. Excluding 7 days puts the first test-window decision 8 days after the last research one, a distance the data shows no dependence at. T_C2 = 1,240 days.
- "Lag 8, g = 8": Read as the first lag of the quiet tail, so the cutoff is 8. One day more caution, and the test window is one day shorter: T_C2 = 1,239 days.

**Owner's choice, verbatim:** "Lag 7, g = 7 (Recommended)".

**Recorded meaning.** G-5 stands: the cutoff is the largest significant lag. With readings G-1..G-5 on the BTCUSDT exploration manifest `5f92ec5041c9560d5f31bdb99b9686d7522697e65a8e61d514a0b0dda6d0b65b`, `g = 7` and `T_C2 = 1240`. The value is fixed for the full run when it is written into the run definition, before the threshold run (preregistration §3.1).
