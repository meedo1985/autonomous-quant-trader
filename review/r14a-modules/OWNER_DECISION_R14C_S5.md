# Owner decision R14C-S-5 (confirmation module trial-count bound)

- Date: 2026-11-07.
- Question (Sol review `SOL_CONFIRMATION_REVIEW_E843198.md`, R14C-S-5): Annex A P18-1 allows `1 <= |J_f| <= 80`, but A-U1 requires a SCREEN_AVAILABLE screen record for the declared set and the frozen `calibration/screen.py` (`MAX_TRIALS = 20`, `trial_set_sha256`) refuses more than 20 trials, the sizes qualified by the owner's prereg §12 item 2 decision (`d19-preregistration/OWNER_DECISION_S12_SCREEN_FEASIBILITY.md`). How should the confirmation module handle a 21-80 trial declaration?
- Options offered: refuse more than 20 early (recommended); leave 80 and fail later at the screen-record check; raise it as a governance item.
- Owner's answer, given in the Claude Code session by selecting the option: **Refuse >20 early**.
- Recorded by Claude Opus 5.5 (`claude-opus-5-5`); this file records the owner's choice, it is not the owner's review of anything.
- Consequence: `check_declaration` refuses more than `screen.MAX_TRIALS` (20) trials per family. No governing text is amended: P18-1's 80 stays the outer bound in Annex A; the module only refuses at declaration a set that A-U1 with the frozen screen could never admit. If the S4/C2 text is later reconciled, the module follows it.
