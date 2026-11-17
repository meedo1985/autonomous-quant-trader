# Re-check: D-20 lockbox proposal, revision 5

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. This is the R19-2 re-check of `review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV5.md` (Claude Opus 5.5), a delta on `PROPOSAL_REV4.md` answering `SOL_REREVIEW3_DF28EE6.md` (D20LR4-S-1..3) and `ASTRA_REREVIEW3_DF28EE6.md` (D20LR4-A-1..2).

**IDs.** Codex Sol: findings `D20LR5-S-n`. Codex Astra: findings `D20LR5-A-n` — Astra MUST use the letter **A**, not S, even if it cannot see its model variant; the caller verifies the model from the CLI header.

**Check:**
1. For EVERY rev-5 disposition of your own D20LR4 findings, say ACCEPT, ACCEPT WITH NOTES or FIX, with evidence. You may check the other reviewer's rows.
2. New findings D20L-51..55: real, correctly classified, correctly repaired? Especially:
   - D20L-51: `insert_release` attestation required iff PASS and R_j < C; validation of signature, evaluation ID, `cooling_off_start = R_j`; does a PASS without valid attestation become a missed release with no other trace?
   - D20L-52: new `begin_read` order (read-only reconciliation, cap, entitlement, budget, order/cooldown); worker deadline `D* = min(d_w, C)` derived from P-6 (`d12-proposal/PROPOSAL_REV7.md`); refusal of bars, `write_bundle`, `mark_finished` at or after `D*` and of `record_pre_read_check` at or after C. Is the accepted consequence (a read started near C usually ends FAIL/DEADLINE and spends the family's try) correctly stated and fair to put to the owner?
   - D20L-53: two never-nested locks `L_store` / `L_seal`; atomic public snapshot `P`; scheduled write of the result into `P` at `D*`; fixed response delay Δ with slower answers logged as §26 incidents; the moved `state` boundary `R_0 − 21,600` (author's own change, not requested). Does the contention test (answers in [Δ, Δ+ε], bytes equal to idle run under `L_seal` held and worker fsync load, finished vs crashed worker indistinguishable, instrumented `L_seal` fails on any public use) actually close the side-channel? Any remaining surface that separates FAIL kinds or reveals finish timing?
3. D20L-54 (E4-1, E4-2) and D20L-55 (Q5 wording, Q1/Q4 summaries, deletion of `DEFERRED {earliest}`, Q2(ii) R-14 alternative, uniform `CAP_REACHED`): applied correctly?
4. Is the declined consolidation (all bindings into one document deferred to the S4 draft) acceptable?
5. New defaults: Δ (value set at build qualification) and the `state` boundary move. Correctly routed to the owner under Q1?
6. Are Q1-Q5 fair and answerable by a non-statistician? Is anything still droppable?

**Findings:** each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
