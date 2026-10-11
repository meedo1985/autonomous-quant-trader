# D-19 re-pilot (FE-7): findings

**Status:** DRAFT, written while the development run is still going. The sections marked *pending* are filled in from the owner's step G and H outputs. Nothing here is a qualification result, and no decision is taken here: the decisions listed at the end are the owner's.

**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-11, from the verbatim outputs in `PILOT_FE7_EVIDENCE.md`.

## 1. The server can run the calibration

| Check (preregistration §13 rev 7g item 6; FE items) | Result |
|---|---|
| CPU runs the pinned runtime (`probe`) | **Yes.** AMD EPYC-Rome (Zen 2). The pinned `OPENBLAS_CORETYPE=Haswell` crash seen on AMD EPYC Zen 4/5 CI runners does not apply to this server. |
| Image pinned by digest; the digest is never typed (FE-4) | **Yes.** The image id was read by the launcher (`sha256:6e410191…`). |
| Memory cap in place (systemd slice, FE4-2) | **Yes.** It is checked before every start. |
| A killed worker stops the whole run, and none survives (FR2-2) | **Yes** (PASS). Exit 1, with the cause `BrokenProcessPool`. |
| An interrupted and resumed run equals a clean run (item 6) | **Yes** (PASS). All 13 cells are byte-identical, including the cell cut by the kill. |
| Forward paper unaffected | *pending (step G)* |
| Memory with 2 workers | *pending (step G)*. The slice peak during the threshold run was 273 MB. |

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

**Development replication (timer, I1-8; provisional).** On this server, at T = 1247:

| Cell | Total per replication | Largest-block rule | Median-block rule | `U_G` |
|---|---|---|---|---|
| K = 5 | 3.89 s | 1.00 s | 1.05 s | 1.84 s |
| K = 2 | 3.99 s | 1.04 s | 1.08 s | 1.86 s |

The K = 20 line was cut off in the paste. The real per-cell figures come from the development run's own chunk times (`times dev`, *pending*).

**Full run, provisional** (assumes 3.95 s per development replication with both rules, 2.9 s per held-out replication with one rule, QJ at double cost, and no escapes):

| Part | Worker-hours |
|---|---|
| Development, 12,000 per cell | about 1,400 |
| Held-out, 20,000 per cell | about 1,700 |
| **Total** | **about 3,100, so about 65 days with 2 workers** |

The threshold run (about 2 days), the 40k escapes and the reported-only runs come on top. The preregistration's scenarios assumed 4–5 months on a shared server. The measured speed suggests nearer **2½–3 months**. This is to be confirmed from `times dev`.

## 3. I1-8: the second block rule

The second block rule costs about 1.05 s of about 3.95 s per development replication, so about 27% of development time. Over the full development phase that is about **370 worker-hours, about 8 days of wall time with 2 workers**.

This is material but not large: about 12% of the provisional total. The I1-8 proposal would choose the rule on the first 2,000 development replications per cell and then compute only that rule. It would save about 6–7 of those days. It is a change to the accepted preregistration (§5 step 1), **so it is the owner's decision only**. The current code follows the accepted text.

## 4. Pending from the development run

- `memwatch`: the peak memory with both workers running, against the 2.5 GB cap. Forward paper must still be running.
- `times dev`: development cost per cell, including Q5 and QJ. This replaces the provisional figures in section 2.
- `nonfinite`: non-finite threshold diagnostics (FE-7). If any are found, how to treat them is the **owner's decision**.
- `choices.json`: per cell, the development DSR and `U_G` event counts. With 1,000 replications per cell these are a cost and smoke measurement. They cannot resolve rates near 5·10⁻⁵ (`OWNER_DECISION_FE7_PILOT_SIZE.md`).

## 5. Decisions for the owner (after the results)

1. **Go-ahead for the full run**, from the confirmed cost estimate (§4 freeze order, step 2).
2. **I1-8:** keep both block rules for every development replication, as accepted, or adopt the prefix proposal. The second option is a preregistration change.
3. **If `nonfinite` > 0:** how to treat non-finite threshold draws (FE-7).
4. **Automatic reboots:** keep them off for the full run, or switch them back on now.
