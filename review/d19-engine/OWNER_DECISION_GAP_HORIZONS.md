# Owner decision: horizons the gap g covers

**Decision by:** the owner, in the Claude Code session on 2026-10-12, answering one question.
**Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`). This file records the owner's choice; the AI made no decision.

**Context.** `T_C2 = 1247 − g` (preregistration §3.1). `g` comes from the §4 draft's `gap_embargo.rule`: "ceiling, in whole days, of the maximum over declared horizons of max(label_horizon, target_autocorr_cutoff)". It is fixed from exploration data before the threshold run, and a C2 declaration with a different `g` is invalid (§1). So the set of horizons must be fixed now.

**Question as asked:**
> "The gap g (days cut between research data and the C2 test window) is computed from the strategy horizons that C2 may later declare. Once fixed, a C2 declaration whose g differs is invalid. Which horizons should g cover?"

**Options shown:**
- "All three (Recommended)": 24 h, 72 h and 168 h, all the horizons the frozen protocol allows (`protocols/protocol_v1.yaml` `target.horizons_hours`). C2 can then declare any of them. g is at most 28 days, so T_C2 is at least 1,219 days.
- "Only 24 h": a smaller g and a slightly longer test window, but C2 could then never declare 72 h or 168 h strategies.

**Owner's choice, verbatim:** "All three (Recommended)".

**Recorded meaning.** `g` is computed over the horizons {24, 72, 168} hours, whatever subset a C2 declaration later uses.
