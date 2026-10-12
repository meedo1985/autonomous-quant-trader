# D-19 re-pilot (FE-7): findings

**Status:** FINAL for the pilot, 2026-10-12, from the owner's step G and H outputs. Nothing here is a qualification result, and no decision is taken here: the decisions listed at the end are the owner's.

**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-11; completed 2026-10-12, from the verbatim outputs in `PILOT_FE7_EVIDENCE.md` and `pilot_fe7_choices.json`.

## 1. The server can run the calibration

| Check (preregistration §13 rev 7g item 6; FE items) | Result |
|---|---|
| CPU runs the pinned runtime (`probe`) | **Yes.** AMD EPYC-Rome (Zen 2). The pinned `OPENBLAS_CORETYPE=Haswell` crash seen on AMD EPYC Zen 4/5 CI runners does not apply to this server. |
| Image pinned by digest; the digest is never typed (FE-4) | **Yes.** The image id was read by the launcher (`sha256:6e410191…`). |
| Memory cap in place (systemd slice, FE4-2) | **Yes.** It is checked before every start. |
| A killed worker stops the whole run, and none survives (FR2-2) | **Yes** (PASS). Exit 1, with the cause `BrokenProcessPool`. |
| An interrupted and resumed run equals a clean run (item 6) | **Yes** (PASS). All 13 cells are byte-identical, including the cell cut by the kill. |
| Forward paper unaffected | **Yes.** `aqt-paper.service` active, up since 2026-10-05, during the development run; the engine runs at `nice -n 19`. |
| Memory with 2 workers | **467 MB** slice peak over the whole night (19% of the 2.5 GB cap); the run container's peak was 413 MB. |
| The development run completes | **Yes.** 15:40:41Z to 00:42:14Z (9 h 02 min), exit 0, 2 chunks in every development chain. |
| Non-finite threshold diagnostics (FE-7) | **None:** 0 of 296,000 values, in every cell. |

## 2. Measured cost

**Threshold run (measured).** These are seconds per 500 draws for one worker, from the chunk times:

| Cells | Seconds per 500 draws |
|---|---|
| synthetic cells, K ≤ 5 | 2 |
| synthetic cells, K = 20 | 3–5 |
| Q5 trend (K = 20) | 24 |
| Q5 vol (K = 20) | 19 |
| QJ at K = 2 | 7 |
| QJ at K = 20 | 40 |

The full threshold run is 300,000 draws in each of the 104 grid cells. The Q5 cost at K = 20 is used for every K, which is an upper bound. That comes to about **80 worker-hours, so about 40 hours, under 2 days, with 2 workers.** The preregistration assumed about 100 laptop-core-hours.

**Development replication (measured).** From `times dev`: one worker's seconds for the second chunk of 500 replications, both block rules and `U_G`, at T = 1247.

| Cells | Seconds per 500 | Seconds per replication |
|---|---|---|
| K = 1 (Q1 independent) | 1,486 | 3.0 |
| K = 2 (Q2m) | 1,964 | 3.9 |
| K = 5 (Q1 clusters, Q2m, Q4) | 1,882–2,035 | 3.9 |
| K = 20 (Q1, Q2 t5, Q2m, Q3, Q5 trend, Q5 vol) | 2,163–2,231 | 4.4 |
| QJ at K = 2 (two families) | 3,664 | 7.3 |
| QJ at K = 20 (two families) | 4,363 | 8.7 |

At K = 20, Q5 costs the same as the synthetic cells: the DSR and `U_G` work dominates, not the generator. The run's wall time (32,493 s) was 6.7% above the ideal split of its worker time over 2 workers (30,462 s), from the tail where one worker had nothing left.

**Full run, from the measured figures.** The grid has 9 cells at K = 1, 29 at K = 2, 32 at K = 5, 32 at K = 20, and the 2 QJ cells. Assumptions: the per-K cost above for every law; a held-out replication costs a development one less one block rule (about 1.05 s, twice for QJ; the timer measured this at K = 2 and 5 only); no 40k escapes.

| Part | Worker-hours |
|---|---|
| Development, 12,000 per cell | about 1,400 |
| Held-out, 20,000 per cell | about 1,720 |
| **Total** | **about 3,130, so about 65 days with 2 workers, about 70 with the tail overhead** |

The threshold run (under 2 days), any 40k escapes and the reported-only runs come on top. **Estimate: about 2½ months** of server time, against the preregistration's 4–5 months on a shared server. The provisional figure in the draft is confirmed.

## 3. I1-8: the second block rule

The second block rule costs about 1.05 s of about 3.95 s per development replication, so about 27% of development time. Over the full development phase that is about **370 worker-hours, about 8 days of wall time with 2 workers**.

This is material but not large: about 12% of the total. The I1-8 proposal would choose the rule on the first 2,000 development replications per cell and then compute only that rule. It would save about 6–7 of those days. It is a change to the accepted preregistration (§5 step 1), **so it is the owner's decision only**. The current code follows the accepted text.

## 4. Development event counts (smoke measurement only)

With 1,000 replications per cell these counts measure cost and show that the chain works. They cannot resolve rates near the targets (`OWNER_DECISION_FE7_PILOT_SIZE.md`). Every cell is `demoted_cap` by design: below about 7,700 development replications the cap rule demotes every cell, so the statuses, `z_crit = None` and the empty `final_thresholds` are not decisions.

- `U_G` events: **0 in every cell.**
- DSR events: 0 everywhere except **`pilot-q3-factor-k20` (1)** and **`pilot-qj-k20/vol` (4)**. Joint `U_proc` events: 0 at QJ K = 2, 4 at QJ K = 20.
- Coverage lists: all empty.

**One early warning, not a result.** The pilot's development target for the DSR rate is τ = 0.00132 (at M = 49; the full run's larger M makes it stricter). If `pilot-qj-k20/vol` had exactly that true rate, 4 or more events in 1,000 would happen about 4.5% of the time. So the QJ K = 20 vol family may have a DSR rate above target, and the full run may demote that cell. One event in `pilot-q3-factor-k20` is unremarkable (73% likely at τ). The full run decides this, not the pilot. Nothing here changes the plan.

## 5. Decisions for the owner (after the results)

1. **Go-ahead for the full run**, from the confirmed cost estimate (§4 freeze order, step 2).
2. **I1-8:** keep both block rules for every development replication, as accepted, or adopt the prefix proposal. The second option is a preregistration change.
3. ~~If `nonfinite` > 0~~: not needed, there were none (0 of 296,000).
4. **Automatic reboots:** keep them off for the full run, or switch them back on now.
