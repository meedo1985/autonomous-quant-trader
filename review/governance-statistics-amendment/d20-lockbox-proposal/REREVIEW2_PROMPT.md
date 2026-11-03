# Re-check: D-20 lockbox proposal, revision 3

You are an independent adversarial reviewer, read-only, not an authority. This is the R19-2 re-check of `review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md` (Claude Opus 5.5), which answers `SOL_REREVIEW_3DCA780.md` (D20LR2-S-1..6) and `ASTRA_REREVIEW_3DCA780.md` (D20LR2-A-1..6). Follow `.agents/skills/statistical-binding-review/SKILL.md`. Write nothing.

**Your own record:** Codex Sol: D20LR2-S-n. Codex Astra: D20LR2-A-n. For EVERY row of revision 3's §1a table that answers one of your findings, say ACCEPT, ACCEPT WITH NOTES or FIX, with evidence. You may also check the other reviewer's rows.

**Verify against** the sources listed in revision 3 §0, especially: `src/aqt/backtest/event_contract.py` l.93-221; `src/aqt/data/bars.py` l.181-200, l.273-282; `src/aqt/core/ledger.py` l.282-308, l.369-415; `calibration/screen.py` l.302-306, l.720-721, l.1473-1477, l.1499-1556; `d12-proposal/PROPOSAL_REV7.md` l.62-147 and `OWNER_DECISION_D12.md`; `d11-proposal/PROPOSAL_REV3.md` l.50-60; Constitution l.70-90, l.145-153, l.189-200; DRAFT_WORDING l.145-153; Annex C l.139-160, l.403-414.

**Check:**
1. Every disposition of your findings (ACCEPT / ACCEPT WITH NOTES / FIX).
2. New findings D20L-22..36. In particular, the ones neither re-check raised: D20L-23 (default-commitment disclosure), D20L-24 (circular `finished`), D20L-26 (cause precedence), D20L-31 (R-14 puts the seed change before the freeze), D20L-34 (final-hour bar outside the authorised data), D20L-35, D20L-36. Are they real, correctly classified, and correctly repaired or routed?
3. B4.1: crash points, concurrency, the read gate. Sweep every record or answer a non-sealed party can see (pre-read entry, release entry, no-read entry, publisher `state`) for anything that separates FAIL kinds.
4. B4.2: do the canonical PASS bytes reproduce under `cj`? Is the three-valued AND and the precedence correct?
5. B3a's table against P-5..P-7, and its equality cases.
6. B4.4: does a faithful replay change anything outside `operational`?
7. Are the row labels honest? Are Q1-Q5 fair and answerable by a non-statistician? Is Q5's timing claim true?
8. Author's known errata, not applied: E-1 (B4.4 should cite "D-12 Q4 route R-a", not "P-6 R-a"); E-2 (D20L-34 should cite `screen.py` l.720-721, not l.719-720); E-3 (the publisher's `state` must return only the effective `{result, commitment}` and only after `d_w`, never whether a finished record exists). Confirm them or add to them.
9. Name any machinery that could still be dropped.

**Findings:** IDs `D20LR3-<reviewer>-n` (Sol: `D20LR3-S-n`; Astra: `D20LR3-A-n`), each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair. If you cannot see your exact model variant, still use your letter; the caller verifies the model from the CLI header.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
