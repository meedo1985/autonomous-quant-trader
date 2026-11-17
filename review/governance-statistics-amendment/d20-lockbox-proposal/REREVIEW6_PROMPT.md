# Re-check: D-20 lockbox proposal, revision 7

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. This is the R19-2 re-check of `review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV7.md` (Claude Opus 5.5), a delta on `PROPOSAL_REV6.md` whose §1.2 (store) and §1.3 (residual R5) replace rev 6's whole and whose §1.4 (proposed scoped Constitution §7 exception wording) is new. It answers `SOL_REREVIEW5_2CDBF88.md` (D20LR6-S-1..5) and `ASTRA_REREVIEW5_2CDBF88.md` (D20LR6-A-1..5). Direction: simplify rather than patch; claim only what is true and testable.

**IDs.** Codex Sol: findings `D20LR7-S-n`. Codex Astra: findings `D20LR7-A-n` — Astra MUST use the letter **A**, not S, even if it cannot see its model variant; the caller verifies the model from the CLI header.

**Check:**
1. For EVERY rev-7 disposition of your own D20LR6 findings, say ACCEPT, ACCEPT WITH NOTES or FIX, with evidence. You may check the other reviewer's rows.
2. D20L-62 (fixed result): a finished record counts only if `finished_at < D*` with the clock read after the result is durable; the result is fixed once by a durable fixed-result entry `aqt.lockbox.fixed.v1` written at the first `state` / `guard_state` / `insert_release` at or after `R_0 − 21,600`; every later answer reads that entry. Can any interleaving or restart still make `state`, `guard_state` and the release disagree, or change a result after it is fixed? Is D-12 step 5 preserved?
3. D20L-63 (commit point): an index append counts at the clock re-read taken while holding `L_store`, sound only because every index reader also takes `L_store` and fsyncs first; a release whose fsync completes after `R_j` is logged as a P-5 outage extending the 72 h, routed to the owner as Q7. Is the argument that "durable before the deadline" cannot be enforced after a crash correct? Is the reader-fsync condition actually guaranteed for every reader? Do T-S1/T-S2 inject inside `append_entry` (`src/aqt/core/ledger.py` l.340-416), during sealing, and between bar clock read and send?
4. D20L-64 (durability): fsync of index file, its directory and the sealed directory before any read under `L_store`; torn line = §26 stop; 12-row crash table (process and machine crash, restart after C); T-S4 needs a test file layer that drops un-fsynced data, otherwise those rows are "not available" and block completion. Complete? Note the agent's `UNVERIFIED_EXTERNAL_ASSUMPTION` that fsync is effective for data written by another process on the target OS/filesystem.
5. D20L-65 (availability) and §1.3 R5: is the claim now limited to lock independence, and is the disclosure (shared disk/CPU stalls, missed releases incl. expiry near day 255, sealed activity after `D*`) accurate and complete? Is T-S3 now testable as written?
6. D20L-66 and §1.4: is the proposed scoped §7 l.79 exception (and optional protocol l.76 wording) narrow, correct and sufficient for R5? Does it leak scope to later cycles beyond what Q6 says?
7. D20L-67: wording (cap scoped to C/`D*`-limited operations, post-C release inserts allowed, `append_entry` described accurately, no implied latency bound).
8. Owner questions: Q1 replaced, Q6 rewritten, Q7 new ("When does a save count as made in time?"). Fair, plain, answerable by a non-statistician? Q2(i), Q2(ii), Q3-Q5 unchanged: still consistent?
9. New index record types (fixed-result entry, P-5 outage entry) must be listed in the S4 consolidated text; P-5 availability-log measurement (D-12 T-7) is still unbound — blocker or carry-forward?
10. Errata noted by the author and not applied: E7-1 (rev 6 l.160 cites rev 3 l.253-258; should be l.253-257), E7-2 (Sol rev-6 record l.24 cites D-12 P-7 at l.87; the clause is at l.92), E7-3 (rev 6 l.107, l.183 superseded by D20L-67/65). Caller erratum applied before commit: E7-4 (rev 7 l.69 now cites rev 3 l.186). Confirm.

**Findings:** each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
