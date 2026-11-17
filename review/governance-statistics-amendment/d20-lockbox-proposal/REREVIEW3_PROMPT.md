# Re-check: D-20 lockbox proposal, revision 4

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. This is the R19-2 re-check of `review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV4.md` (Claude Opus 5.5), a delta on `PROPOSAL_REV3.md` answering `SOL_REREVIEW2_C86EA8D.md` (D20LR3-S-1..6) and `ASTRA_REREVIEW2_C86EA8D.md` (D20LR3-A-1..6).

**IDs.** Codex Sol: findings `D20LR4-S-n`. Codex Astra: findings `D20LR4-A-n` — Astra MUST use the letter **A**, not S, even if it cannot see its model variant; the caller verifies the model from the CLI header.

**Check:**
1. For EVERY rev-4 §1a disposition of your own D20LR3 findings, and of the FIX rows you marked (Sol: A-4; Astra: S-4, A-1, A-2), say ACCEPT, ACCEPT WITH NOTES or FIX, with evidence. You may check the other reviewer's rows.
2. New findings D20L-37..50 and the D20L-36 reclassification: real, correctly classified, correctly repaired or routed? Especially D20L-46 (store lock vs `ledger.py` l.340-416), D20L-48 (R-14, DRAFT l.152, applied to the confirmation end-price rule) and D20L-50 (cap guard).
3. B4.1 as replaced: entitlement, order/cooldown deferral (DRAFT l.241, l.243), cap, crash points, the read gate under `L_store`. Sweep every surface a non-sealed party sees (pre-read entry, release entry, no-read entry, publisher `state`, `DEFERRED`/`CAP_REACHED` answers) for anything that separates FAIL kinds or reveals finish timing.
4. B4.2: L4 composition and both new rows; reproduce the PASS fixture bytes and SHA-256 under `calibration/seeds.py` `cj`.
5. A1b/Q5: policy branch, evidence rule, Annex C l.412-413 wording; Q5 and Q2(ii) timing against `deploy/calibration/FREEZE_HELDOUT.md` steps G0/G and `calibration/qobj.py` l.198-210. Note: this branch predates main's `review/d19-engine/FREEZE_REVIEWS.json` (commit 3d6d8ef, on main); do not report its absence here as a finding.
6. Author errata not applied in the file: E4-1 (the §4 self-check says "five notes"; there are eight note rows), E4-2 (§0 should cite `event_contract.py` l.151-156; the default path refuses a 2 h series with `CostModelError`), E4-3 (revision 3's B4.3 rule "attestation non-null iff PASS and R_j < C" stands and the store enforces it at insert). Confirm or add.
7. Are Q1-Q5 fair and answerable by a non-statistician? Is anything still droppable?

**Findings:** each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
