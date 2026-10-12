# Owner decisions after the FE-7 re-pilot: go-ahead, I1-8, reboots

**Decision by:** the owner, in the Claude Code session on 2026-10-12, answering three questions.
**Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`). This file records the owner's choices; the AI made no decision.

**Basis:** `PILOT_FE7_FINDINGS.md` (final, commit 32406dc) and its evidence.

**Questions as asked** (each with the AI's recommendation shown):
1. "Approve the full run (about 2½ months)?" Recommended: yes. Disclosed: approving does not start it; it still waits for the key record A_Q1…F_Q2 (accepted preregistration hash) and `T_C2` (the `g` of `gap_embargo.rule`).
2. "The second block rule (I1-8): keep computing both block rules in every development replication as agreed, or use the shortcut that drops one rule after the first 2,000?" Recommended: keep both. Disclosed: the shortcut saves about 6 days and changes the accepted preregistration (§5 step 1).
3. "Automatic reboots: keep them off for the full run?" Recommended: off. Disclosed: security updates still install; the owner can restart by hand, and a stopped run resumes byte-identically (step F).

**Owner's answer, verbatim:** "1 yes, 2 keep both, 3 off"

**Recorded meaning:**
1. **Go-ahead given** for the full calibration run at the measured cost (about 3,130 worker-hours, about 2½ months with 2 workers; §4 freeze order, step 2). It starts only once its other preconditions are met.
2. **I1-8 closed: no change.** Both block rules are computed for every development replication, as the accepted text says. The prefix proposal is not adopted.
3. **Automatic reboots stay off** (`Unattended-Upgrade::Automatic-Reboot "false"`) for the full run.

The non-finite question did not arise: 0 of 296,000 diagnostic values were non-finite.
