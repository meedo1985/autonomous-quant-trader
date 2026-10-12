# D-19 measured pilot, finding 1: kernel timings (2026-10-04)

**By:** Claude Opus 5.5 (`claude-opus-5-5`), under the owner's build and pilot go-ahead (`OWNER_DECISION_D19_ACCEPT.md`, `ec35a29`).

**What this is.** These are timings of the computational kernels the accepted preregistration (rev 6, `e1e4e7e`) binds, measured on synthetic Gaussian data. This is not the full pilot: the engine, the gates, the screen and the mapping are not built yet. No calibration result exists, and no confirmation, lockbox or `data/` content was used.

**Machine.** Intel Core i7-10710U: 6 cores, 12 threads, 8 GB RAM, Windows. NumPy uses OpenBLAS.

## Measured, per outer replication (`B = 2000` inner replicates)

| Kernel | Binding source | `T = 365` | `T = 1247` |
|---|---|---|---|
| Production `bootstrap_indices`, pure Python | Annex B §2.4 (the "existing replicate-seed construction") | 0.22 s | 0.85 s |
| Production `block_length` (Politis–White), per column, ×2 influences | Annex B §2.2 | `K = 80`: 0.29 s | `K = 80`: 1.58 s |
| Sharpe of both laws, **exact Annex B numerics** (`math.fsum`, two-pass, per replicate and column) | Annex B §2.3 | — | `K = 80`: about **114 s** |
| Sharpe of both laws, fancy-indexed NumPy copy | none (benchmark only) | `K = 1`: 0.02 s | `K = 20`: 1.44 s; `K = 80`: 12.3 s |
| Sharpe of both laws, **counts × matrix product** (vectorised) | none (proposal) | — | `K = 80`: **0.12 s** |

On one checked replicate and column, the vectorised Sharpe matched the exact `fsum` two-pass value with a relative difference of 0.0. That is one sample, not a proof of exact agreement in general.

## What follows (estimates from the table)

- **Exact numerics are infeasible here.** With the exact Annex B numerics, the largest cell (`K = 80`, `T = 1247`) costs about 114 s per replication. At 22,000 development plus 20,000 held-out replications, that is about **1,300 core-hours for that one cell**. The full grid would take tens of thousands of core-hours.
- **The vectorised path is feasible in principle.** The largest cell drops to about 2.6 s per replication: indices 0.85 + block length 1.6 + Sharpe 0.12. That is about **30 core-hours per large cell** before the gates. A rough full-grid estimate is 2,000–5,000 core-hours, since most cells are smaller. On this 6-core laptop that is weeks of continuous running, and the 8 GB of RAM already causes Claude Code to stop background jobs.
- **The bottleneck then moves** to the two production pure-Python routines: index generation and block length.

## Proposals (AI defaults; for review, then the owner)

1. **Computational-equivalence rule (needs a preregistration amendment, rev 7).**
   - Calibration computes the Annex B quantities with a vectorised implementation: counts × matrix sums, plus a vectorised index generator that reproduces the production index law.
   - **Exactness audit.** A frozen random 1% of replications in every cell is also recomputed with the exact production code. If any event decision differs (`A_f`, `E_f`, nominee, `U_G`), the calibration attempt is void.
   - **Production is unchanged.** The real evaluation keeps the exact `fsum` reference, as P18-6 requires.
   - **Why an amendment is needed.** Rev 6 says "the inner algorithm is the frozen build code, rerun exactly", so this change needs the two reviews and the owner.
2. **Compute location** (owner, after the full pilot). Run locally for weeks, or rent cloud CPUs. At typical spot prices the rental might cost on the order of a few hundred US dollars, though no quote has been taken. Renting is real money and the owner's decision.
3. **Scope.** If cost must fall, the cheapest cut keeps the certified `T` levels to `T_min` and `T_C2` in Q1. Fewer `T_min` candidates are allowed, and this needs the same amendment.

## Next

1. Build the engine on a branch from `main`, with the exact path and the vectorised path side by side, so the audit is real.
2. Measure the full pilot items of §10, including the `U_G` gates, a QJ cell, the screen and the mapping.
3. Then put proposals 1–3 to the reviewers and the owner, together with the measured numbers.
