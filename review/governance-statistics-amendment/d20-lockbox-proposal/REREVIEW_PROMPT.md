# Re-check: D-20 lockbox proposal, revision 2

You are an independent adversarial reviewer, read-only, not an authority. This is the R19-2 re-check of `review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV2.md` (Claude Opus 5.5), which answers the first-round reviews. Follow `.agents/skills/statistical-binding-review/SKILL.md`. Write nothing.

**Your own first-round record:** Codex Sol: `SOL_REVIEW_D87AB70.md` (your findings D20LR-S-1..9). Codex Astra: `ASTRA_REVIEW_D87AB70.md` (your findings D20LR-A-1..9; the report's labels D20LR-Codex-n are A-n). Re-check YOUR OWN findings against revision 2's §1a disposition table; you may read the other reviewer's record for context.

**Verify against** the same sources as the first round (`REVIEW_PROMPT.md` in this folder), plus `qualification-definition.json`, `FULL_RUN_START_EVIDENCE.md`, `deploy/calibration/FREEZE_HELDOUT.md` and `calibration/qobj.py` l.56-63, which revision 2 uses for the engine-commit and object-file facts.

**Check:**
1. Is each of your findings resolved, partly resolved or not resolved? Give evidence.
2. Are the repairs correct? In particular: the model-seed mapping `int(seed_l266, 16) % 2**31` against protocol l.266 and D20_D13; the provenance recomputation; the cap anchor and comparison table; the EventResult -> daily returns / `_max_drawdown` adapter; the exact schemas, numeric ordering and step-2 atomicity; the key-custody rules.
3. Did revision 2 introduce any new defect or contradiction with D-11, D-12, D20_D13, the frozen texts or day 255? Check new findings D20L-15..21.
4. Are the row labels (ALREADY DECIDED / NECESSARY DETAIL / RECOMMENDED NEW DEFAULT) honest, and are owner questions Q1-Q5 fair, complete and answerable by a non-statistician?
5. Name any machinery that could be dropped.

**Findings:** IDs `D20LR2-<reviewer>-n` (Sol: `D20LR2-S-n`; Astra: `D20LR2-A-n`), each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair. If you cannot see your exact model variant, still use your letter as given here; the caller verifies the model from the CLI header.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
