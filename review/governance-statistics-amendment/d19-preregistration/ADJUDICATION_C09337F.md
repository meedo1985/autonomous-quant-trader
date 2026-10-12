# Adjudication of BF1 (Fable) and BS1 (Sol) on the D-19 §13 budget version at `c09337f`

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter
**Records:**
- `FABLE_REVIEW_C09337F.md` (`7c7cf49`): UNSOUND, blocker BF1-1
- `SOL_REVIEW_C09337F.md` (`769f966`): UNSOUND, blocker BS1-1

**Result:** `PREREGISTRATION.md` §13 rev 7c. The drafter recomputed the τ values, the 12k development bounds and the order-statistic ranks independently; they agree with both reviewers.

**Context change since rev 7b.** The owner must switch the laptop off and chose a small rented server (Hetzner CX23, about €6 a month) to run forward paper. The calibration moves to the same server, with no extra cost. This changes the machine, the worker count and the estimate in §13 item 6.

Every finding is accepted.

| Findings | Disposition |
|---|---|
| BF1-1, BS1-1 (BLOCKER) | Fable option (a), which Sol also proposed: 12,000 development and 20,000 held-out replications in every cell, with the 10k branch deleted and §5 step 2 restated. **Drafter's addition:** with a single `T` level, one cell failing availability would otherwise fail the whole method, so a failing cell is demoted to a challenge cell, as the cap rule already does, and the coverage rule decides. This is new text for the next reviewers to check. |
| BF1-2, BS1-3 | Certified for `T = T_C2` exactly; a window with `T ≠ T_C2` is ineligible, not `U_proc^R`. A new owner question `<<OWNER A-B7-EQ>>` is added beside `<<OWNER O18-4-T>>`. |
| BF1-3, BS1-2 | The 99.999% order statistic (ranks 299,997 and 4). The tails are enumerated: exactly eight, as Sol counted, not "about 10". Ties are accepted (inclusive). The rate is stated as expected, not "at most". Non-finite refusals are measured with DSR availability. |
| BF1-4, BS1-4 | Re-estimated: about 104 × 32,000 × 4.5 s plus about 300 for QJ, the threshold run and the reported-only runs, then ×1.2 for a shared server core: about 5,400 server-core-hours, about 3½–4 months on 2 vCPU. It is labelled as not measured; the re-pilot on the server measures it. |
| BF1-5, BS1-5 | Preregistered run rules in §13 item 6: 500-replication chunks, atomic rename, hash-chained records bound to the object, namespace, cell, range and runtime; a runtime check and canary on every start; held-out progress-only visibility, with resume not an access; an interrupted-versus-clean byte-identity test; memory measured with 2 workers. BF1-5(d) (detached from Claude Code) is met by running on the owner's server. BF1-5(e) is met by a recreatable pinned runtime with a hash lock file; the host-migration risk is disclosed. |
| BF1-6 | §9 and §11 are now listed as overridden. The new §11 sentence is in §13 item 8. The §3.3, §3.4 and §9 reported-only runs are cut to 2,000 replications and costed. |
| BF1-7 | The L/T cost is corrected to about 1,000–1,500 core-hours; §3.6 also drops L/T; the threshold-run cost is to be measured, not assumed. |
| BF1-8 | The disclosed-effect note is reworded: τ uses `N_i = 20,000` as run, and the power cost comes from the 12k development UCB. |
