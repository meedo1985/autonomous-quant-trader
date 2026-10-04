# D-19 calibration: compute plan and price estimate (for the owner's decision)

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`)
**Asked for by:** owner decision `d20-proposal/OWNER_DECISION_D20_V.md` (`b58d1c3`), "Get a rental quote first". **Nothing is rented and nothing is spent without the owner's explicit approval.**

**Status:** an estimate built from public price listings, not a vendor quote. Prices change; they are re-checked on the day of renting.

## 1. How much work

| Quantity | Value |
|---|---|
| Replications | about 379 cells × 42,000 replications (22,000 development + 20,000 held-out) |
| Time per replication, with method V | 0.9–6.7 s, measured on this laptop's cores on mains power (`PILOT_FINDINGS_3`, engine `ea5b615`) |
| Total | about **12,000 laptop-core-hours** |
| Server adjustment | server cores run about 1.2× slower than this laptop's turbo, so about **14,000 server-core-hours** (assumed) |

The replications are independent, so they spread over any number of cores without coordination.

## 2. Options

| Option | Machine (public list price, 2026) | Time to finish | Estimated cost |
|---|---|---|---|
| **A. AWS spot, recommended** | `c7a.48xlarge`: 192 physical AMD cores, 384 GB RAM. Spot about **$3.51/h**, on-demand $9.85/h | about **3–4 days** | about **$250–350** at spot. Interruptions add some restarts. The on-demand ceiling is about $700–900. |
| B. Hetzner dedicated cloud | `CCX63`: 48 dedicated vCPU (24 cores), €1.37/h after the June 2026 price rise | about 3–4 weeks | about **€700–800** |
| C. This laptop | 6 cores, 8 GB RAM, mains power | about **3 months**, continuous | no money. The machine is busy throughout, and low memory has already stopped background jobs. |

**Sources:**
- [AWS c7a.48xlarge (Vantage)](https://instances.vantage.sh/aws/ec2/c7a.48xlarge)
- [c7a.48xlarge (cloudprice.net)](https://cloudprice.net/aws/ec2/instances/c7a.48xlarge)
- [Hetzner CCX63 (Spare Cores)](https://sparecores.com/server/hcloud/ccx63)
- [Hetzner price adjustment, 15 June 2026](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/)

## 3. The pinned runtime (method V) on rented machines

V's results must be reproducible later on the same runtime for the real evaluation (A-V1). The plan:
- **One container image** holds Python, NumPy and BLAS. The image hash is recorded in the qualification object. The calibration runs in it, and every later real evaluation runs in the same image, including on this laptop under Docker.
- **Pinned processor settings:**
  - `OPENBLAS_NUM_THREADS=1` and `OPENBLAS_CORETYPE=Haswell`.
  - `NPY_DISABLE_CPU_FEATURES` turns off AVX-512 on the AMD Zen 4 servers. NumPy then uses the same instruction set (AVX2) as this laptop's i7-10710U, and the runtime identity's CPU features match on both machines.
- **Proof of the pin.** The known-answer canary and the full identity check (`v_runtime_check`) must pass on both machines before anything counts. A short test run on one cheap rented core proves this before the large machine is rented.

## 4. What must still happen before any money is spent

**Before renting:**
1. **Finish the engine.** These parts are not built yet:
   - the skew-t law, the unequal-moments (Q2m) cells, the exploration-data (Q5) cells and the joint (QJ) cells;
   - the classifier threshold run;
   - the exact-binomial target script and the `z_crit`/`T_min` selection;
   - the full-run driver, which checkpoints each cell so a spot interruption only loses a little work;
   - the frozen reference vectors;
   - the qualification-object assembly.
2. **Review the engine.** It needs the §16 different-model review and the owner's PR review, then a merge on the owner's word.
3. **Bitcoin keys and coins.** The owner commits the record of the keys and coins `A_Q1`, `F_Q1`, `D_Q1`, `A_Q2` and `F_Q2`. This completes the D-19 acceptance, as `OWNER_DECISION_D19_ACCEPT.md` requires.
4. **Owner's rental account.** The owner creates the account himself and sets a hard budget alarm, for example $400. No access key ever enters the repository, a log or a prompt.
5. **Re-check prices,** then ask the owner to approve the spend.

**Then two runs:**
- **Development run.** About half the cost. It is followed by the freeze and the Bitcoin post (`AQTQ1`).
- **Held-out run.** The other half.

## 5. What leaves this computer

- **Sent to the rented machine:** the code; the exploration-partition BTC/ETH price data (pre-2022, used by the Q5 cells); the container image.
- **Never sent:** confirmation data, lockbox data, or `data/forward`.

The rented machine belongs to the owner's own account, so nothing is shared with any other person.
