# D-19 measured pilot, finding 3: an exact speed-up is not enough; rev 7 is withdrawn (2026-10-04)

**By:** Claude Opus 5.5 (`claude-opus-5-5`)
**Engine:** branch `d19-calibration-engine`, commit `1c2ad55`
**Data:** synthetic only; timings only

## 1. Rev 7 is withdrawn

Sol DS7 (`77f9593`) rated rev 7 §13 UNSOUND. Its point holds: a 1% audit cannot prove that the fast arithmetic made the same decisions as the exact code.

Rev 7 is therefore **withdrawn**. The accepted text stays rev 6 (`e1e4e7e`), unchanged.

Fable did not review rev 7: that run was stopped by a usage limit before it produced any output.

## 2. Bit-identical acceleration (built and proven)

The engine now has a second exact path that reproduces the pure-Python reference **bit for bit**. It works by:
- gathering samples with NumPy;
- summing with `math.fsum`, which is correctly rounded and therefore independent of order;
- squaring with NumPy `power` using an *array* exponent, which calls the same C `pow` as Python's `** 2`. On this platform, `x * x` differs from `** 2` in about 5 cases in 10,000. A self-check refuses to run if this identity stops holding.

**Tests prove it.** The whole `FamilyResult` is equal float for float across 4 laws and both block rules. The PW block length matches production exactly, including random-walk and sparse inputs. G-1 availability matches production.

**Measured cost per replication:**

| Cell | Bit-identical accelerated | Pure-Python reference | Non-identical fast arithmetic (finding 2) |
|---|---|---|---|
| `K = 80`, `T = 1247` | **65.2 s** | (about 114 s for the Sharpe part alone) | 5.1 s |
| `K = 20`, `T = 730` | 11.0 s | 27.7 s | 2.4 s |
| `K = 2`, `T = 365` | 1.4 s | 1.9 s | 1.1 s |
| `K = 1`, `T = 1247` | 4.2 s | 5.5 s | 4.4 s |

**What this means.** Staying bit-exact with the Task 12 Sharpe code costs about 760 core-hours for the largest cell. The full grid would need **tens of thousands of core-hours**, so it is not a workable route.

## 3. A cleaner route: one definition, no equivalence question

The per-replicate Sharpe inside the DSR bootstrap is bound by draft clause R-8 to "the Task 12 Sharpe code at a hash fixed under `<<OPEN D-20>>`". R-8 is **AI draft wording**, not an owner decision, and D-20 is open. Annex B's own `fsum` sentence covers the statistics *across* replicates (`S0`, `var_b`, in replicate index order), and those stay exact.

**Proposal.** D-20 binds the DSR replicate Sharpes, and the G-1 replicate Sharpes, to **one vectorised, deterministic implementation `V`**:
- the counts-times-matrix sums on mean-centred columns;
- run single-threaded on the pinned runtime (Python, NumPy and BLAS versions, recorded in the qualification object).

Draft R-8 is reworded to match. `V` is then **the** method in both calibration and every real evaluation, so no fast-versus-exact question arises.

**Costs and limits:**
- **Index-generation floor.** Indices remain the production loop, about 0.85 s per replication at `T = 1247`, paid for both DSR and G-1.
- **Estimated total.** About **8,000–12,000 core-hours** for the full grid (estimate). On this 6-core laptop that is about 2–3 months. A rented 64-vCPU machine would take about one week, probably at a cost of a few hundred US dollars; no quote has been taken.
- **Reproducibility.** Results reproduce on the pinned runtime and CPU class. Bit-reproduction on other hardware is not claimed, because BLAS kernels differ by CPU. Constitution §27 is met by pinning the runtime.

**Approvals needed.**
- **R-8 and D-20:** the rewording is a draft change, and D-20 is an owner decision row. Both go to the final two-model review of the wording.
- **Rev 6:** the preregistration needs no change, because it binds "the method build … with the `<<OPEN D-20>>` bindings".

## 4. What the owner can choose

1. **Bind `V` and continue.** D-20 for the replicate Sharpe, then a re-pilot, then the compute choice (laptop for months, or rented for about a week, which is real money).
2. **Shrink the grid.** This needs a preregistration amendment, for example certifying only `T_C2` and a smaller set of `K`. It could cut the cost several-fold, but the claim covers less.
3. **Pause D-19.** Promotion stays blocked, and forward paper trading continues.
