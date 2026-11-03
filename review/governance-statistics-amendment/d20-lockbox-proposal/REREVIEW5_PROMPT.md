# Re-check: D-20 lockbox proposal, revision 6

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. This is the R19-2 re-check of `review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV6.md` (Claude Opus 5.5), a delta on `PROPOSAL_REV5.md` whose store section §1.2 replaces B4.1 whole. It answers `SOL_REREVIEW4_06C6989.md` (D20LR5-S-1..4) and `ASTRA_REREVIEW4_06C6989.md` (D20LR5-A-1..3). Direction for this revision: simplify rather than patch; mechanism was deleted (fixed delay Δ, `L_seal`, public snapshot P, scheduled fix step at `D*`, contention test) and the remaining timing residual is disclosed (R5) and routed to the owner (Q6) instead of claimed away.

**IDs.** Codex Sol: findings `D20LR6-S-n`. Codex Astra: findings `D20LR6-A-n` — Astra MUST use the letter **A**, not S, even if it cannot see its model variant; the caller verifies the model from the CLI header.

**Check:**
1. For EVERY rev-6 disposition of your own D20LR5 findings, say ACCEPT, ACCEPT WITH NOTES or FIX, with evidence. You may check the other reviewer's rows.
2. D20L-56 (re-read the store clock immediately before every time-limited write; scope includes release insert against `R_j` and each bar response; "durable before C" = moment the write is decided). Is a decided-before-C, durable-after-C write sound? Do tests T-S1/T-S2 cover every crossing?
3. D20L-57 (snapshot deleted; index + write-once sealed files are the only records). Check the crash table: does every crash point, including restart after C and the inherited partial-last-line case (E6-2, store stops for a human under §26), leave exactly one durable truth with nothing to rebuild or replay? Is T-S4 sufficient?
4. D20L-58 and §1.3 residual R5: is the disclosure accurate and complete (what leaks, which windows, unmeasured size)? Is availability really independent of sealed work (T-S3)? Is anything still claimed that cannot be tested? Compare with D-12's accepted residuals R1-R4 (`d12-proposal/PROPOSAL_REV7.md`, `OWNER_DECISION_D12.md`).
5. D20L-60 (QUESTION): can R5 be disclosed like D-12's residuals, or does Constitution §7 l.79 ("research receives PASS/FAIL only") require a C2 row?
6. D20L-61: with the fix step gone, a finished PASS whose disk write stalls past a FAIL release is published as FAIL, treated as a storage fault extending D-12's R3. Check this against D-12's rule that no release-time step may turn a PASS into a FAIL. Is this acceptable, or a blocker?
7. D20L-59: Q1 replaced (six-hour boundary listed with its effect, Δ dropped, no overclaim, "may fail if too little time remains"). New Q6 ("Accept, disclosed (Recommended)" / "Keep blocked"): fair and answerable by a non-statistician? Q2(i), Q2(ii), Q3-Q5 unchanged: still consistent with the new store?
8. Consolidated signing text deferred to the S4 draft as a recorded obligation: acceptable?
9. Caller erratum applied before commit: E6-1 (§1a row citation corrected to Sol l.27, l.30, l.41). Confirm.

**Findings:** each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
