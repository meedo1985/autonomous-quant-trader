# D-19 measured pilot, finding 2: full replication timings (2026-10-04)

**By:** Claude Opus 5.5 (`claude-opus-5-5`), under the owner's build and pilot go-ahead (`ec35a29`).

**Engine:** branch `d19-calibration-engine`, commit `6dfd9b5`. It is a top-level `calibration/` package, outside `aqt` because it uses NumPy. It contains:
- Annex B v2, in an exact path and a fast path;
- the generator;
- the `U_G` gates;
- the classifier diagnostics;
- the seeds.

**Command:** `python scripts/d19_pilot.py --reps 2 --exact-sample 1`.

**Data:** synthetic only. The run produced timings only; no calibration result exists.

**Machine:** i7-10710U, 6 cores and 12 threads, 8 GB RAM.

## Per outer replication (`B = 2000`; DSR method plus every `U_G` gate on the nominee)

| Pilot cell | Fast path total | Generator | DSR | Gates | Exact path |
|---|---|---|---|---|---|
| `K = 80`, `T = 1247`, factor | 5.09 s | 0.02 | 2.34 | 2.73 | not run (about 114 s for the Sharpe part alone, per finding 1) |
| `K = 20`, `T = 730`, GARCH, `ρ = 0.9` | 2.38 s | 0.01 | 0.76 | 1.62 | 19.97 s |
| `K = 2`, `T = 365`, AR 0.5, near-duplicates | 1.09 s | 0.00 | 0.30 | 0.79 | 1.94 s |
| `K = 1`, `T = 1247`, t₅ | 4.39 s | 0.00 | 1.32 | 3.07 | 5.79 s |

**Gate costs.** The gates are dominated by the production G-1 paired-CI routine, a pure-Python loop of 2,000 replicates per nominee. G-10's 12,870 splits and G-12's three horizons are small next to it.

**Projection per cell.** At 42,000 replications per cell (22,000 development and 20,000 held-out), the fast path costs 13–59 core-hours per cell.

## Extrapolation (estimate)

- **As built.** The grid has about 380 cells, and the QJ cells cost about double. At an average of about 3 s per replication, the total is about **13,000 core-hours**. On this laptop that is about 3 months of continuous running, and the 8 GB of RAM is already tight.
- **With the obvious optimisations.**
  - A vectorised G-1 (the same counts-times-matrix trick as the DSR Sharpe).
  - A vectorised index generator that reproduces the production Mersenne-Twister draws exactly.
  - A vectorised block length.

  These should give about 3–5 times less, roughly **3,000–4,500 core-hours**. That is about a month locally, or a few days on a rented 64-vCPU machine. No price has been quoted; at typical cloud spot prices it is probably a few hundred US dollars.
- **Not yet measured.** The declared-strategy screen and the declaration mapping need the strategy-rule libraries and hourly backtests, which are not built yet. They are per-declaration costs, not part of the calibration total.

## What needs a decision

1. **Computational-equivalence amendment (rev 7).** All of these optimisations, including the fast DSR numerics already used here, compute the Annex B quantities in a way other than the frozen exact code. Rev 6 does not allow that. **Proposed rule:**
   - Calibration uses the fast implementation.
   - A frozen random 1% of replications in every cell is recomputed exactly.
   - If any event decision differs, the attempt is void.
   - Production evaluation stays exact.

   The amendment needs two reviews and the owner's acceptance.
2. **Compute.** After the optimisation and a re-pilot, the owner chooses between about a month on this laptop and a few days of rented compute, which is real money.
3. **Or pause D-19.** Promotion stays blocked either way until certification. Forward paper trading of the baseline is unaffected.
