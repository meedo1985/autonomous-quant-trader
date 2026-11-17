# Re-check: D-20 lockbox proposal, revision 8

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. This is the R19-2 re-check of `review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV8.md` (Claude Opus 5.5), a delta on `PROPOSAL_REV7.md` whose store, timing-residual and §7 sections replace rev 7's whole. It answers `SOL_REREVIEW6_F50838F.md` (D20LR7-S-1..5) and `ASTRA_REREVIEW6_F50838F.md` (D20LR7-A-1..6). Direction: simplify rather than patch; claim only what is true and testable. The owner chose a revision over a redesign.

**IDs.** Codex Sol: findings `D20LR8-S-n`. Codex Astra: findings `D20LR8-A-n` — Astra MUST use the letter **A**, not S, even if it cannot see its model variant; the caller verifies the model from the CLI header.

**Check:**
1. For EVERY rev-8 disposition of your own D20LR7 findings, say ACCEPT, ACCEPT WITH NOTES or FIX, with evidence. You may check the other reviewer's rows.
2. **D20L-69 (focus):** the finish's clock check and finished-record link now run under `L_store`, clock read after the result is durable; the fixed-result entry and first-fixing rule are deleted. Is the §1.2 lock-ordering proof correct — can any interleaving, crash or restart still let two answers at or after `R_0 − 21,600` see different finished records, or let a finish change an outcome already observed? Is the reintroduced lock-wait timing channel (and a stalled finish delaying a release) fully disclosed in R5/Q6? Is the recorded alternative (rev 7 lock-free finish + step-5 change to owner) better? Is the remaining meaning of step 5/P-7 ("a save counts at its clock check under the lock") correctly routed to Q7/C2?
3. D20L-68: sealed-directory fsync after lookup and before use; selection point = lookup under `L_store`; T-S4 interleaving test (and its check that rev 7's order fails). Complete for every consumer of sealed names, including the read gate's startup prerequisites?
4. D20L-70: outage entry deleted; availability measurement (P-5, T-7) a mandatory S4/build carry-forward with minimum T-7 schedule; no 72-hour make-up claimed; no promotion may rely on an unbound/unreconciled log. Sufficient, or must anything be bound now?
5. D20L-71 (Q7 tradeoff wording, stricter policy offered as an option) and D20L-72 (§7 row: delayed or missed releases and cap expiry they cause; forbids only added research-visible disclosure; rev 8 adds no index record type).
6. D20L-73 (13-row crash table: survival, loss and partial persistence, before/after completed fsync; mock validates the algorithm under its model only; `UNVERIFIED_EXTERNAL_ASSUMPTION` kept) and D20L-74 (Q1 wording, "briefly" deleted, T-S1 accepts `R_j − 21,600`, refuses `R_j`).
7. New D20L-75: a §26 stop needs "a human" to reconcile records; if that is the owner he could see a release row or sealed result early; left unbound as an owner/S4 decision. Correct classification? Should it be an owner question now?
8. Owner questions: Q1, Q6 changed; Q7 rewritten (one draft rule plus "Ask for the stricter rule"). Fair, plain, answerable by a non-statistician? Q2(i), Q2(ii), Q3-Q5 unchanged: still consistent?
9. Errata E7-1, E7-3 applied; E7-2 recorded as note. Confirm. Is anything still droppable?

**Findings:** each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
