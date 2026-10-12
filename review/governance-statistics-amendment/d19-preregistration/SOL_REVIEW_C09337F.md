# Sol review BS1 of the D-19 preregistration §13 budget version at `c09337f`: UNSOUND

Date: 2026-10-04. R19-2 independent statistical review, run with Codex CLI (`codex exec`, model requested `gpt-5.6-sol`, reasoning effort high), read-only. The drafter is Claude Opus 5.5. The reviewer's final report is reproduced below unchanged.

---

Model: Codex, GPT-5 family; exact serving-model identifier is not exposed  
Commit reviewed: `c09337fef6d8d25e39e4d9e00b0cc0403b81076e`  
Verdict: **UNSOUND**

The τ table is correct. At `M≈330`, independent exact-binomial calculations reproduce `0.0153202`, `0.000579635`, `0.0000190551`, and `0.000202157`. The blocking defect is how those values interact with development.

- **BS1-1 — BLOCKER — §13.3 versus §5 step 2.** With 10,000 development replications and zero `U_G` events, the one-sided 90% upper bound is `0.000230232`. This exceeds both `τ_G(10k)=0.0000190551` and `τ_G(20k)=0.000202157`. Thus every cell triggers 20,000 held-out replications and, under the intended substitution into §5, no cell can pass the development availability condition. Minimum development `N` for even zero events to meet `τ_G(20k)` is 11,389. Fix: completely restate revised §5 step 2; a simple coherent option is at least 12,000 development replications, fixed 20,000 held-out replications, and recomputed budget. [§13.3](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md:470>)

- **BS1-2 — MAJOR — §13.4 classifier.** Substituting `99.998%` into the existing order-statistic formulas gives ranks 299,994 and 7. Each independent future-tail probability is `7/300001 = 2.3333×10⁻⁵`, not at most `2×10⁻⁵`. After dropping `L/T`, the listed classifier has eight stochastic tails, whose union bound is `1.8667×10⁻⁴` and therefore does fit the budget; “about 10 tails” would give `2.3333×10⁻⁴` and fail it. Fix: enumerate exactly eight tails, bind exact ranks and inclusive comparisons, and account explicitly for non-finite refusals. Alternatively use upper rank 299,995 and lower rank 6 to make the claimed per-tail bound true. [§13.4](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md:482>)

- **BS1-3 — MAJOR — §13.2 / A-B7.** A-B7 makes `T_min` a lower bound (`T ≥ T_min`), while rev 7b certifies only exactly `T=T_C2`. Saying a later window merely needs “at least `T_C2`” implies unsupported coverage for `T>T_C2`. Fix: require recalibration for every `T≠T_C2`, or obtain an explicit binding that evaluation uses an exactly `T_C2`-day preregistered window. Add this to the owner question; the current `O18-4-T` question covers only removal of unequal-`T` cells. [A-B7](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_A_SELECTION_RULE.md:188>)

- **BS1-4 — MAJOR — §13.5 estimate.** The quoted base arithmetic is plausible: `104×20,000×3.5s + 90h ≈ 2,112 core-hours`. But BS1-1 makes every cell use 30,000 total replications, raising the same arithmetic to about 3,123 core-hours before QJ weighting and overhead—at least 26 ideal days with five workers. Fix: repair BS1-1, then re-estimate using the final manifest, weighted QJ cost, measured `T_C2` timings, checkpoints and retries. [Estimate](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md:486>)

- **BS1-5 — MAJOR, pre-run — §13.5 checkpoints.** “Every cell is checkpointed” does not bind checkpoint cadence, atomic writes, integrity hashes, deterministic replication ranges, duplicate/skip prevention, canonical reduction order, or namespace/runtime validation on resume. The compute plan says the full-run driver is not built, and prior evidence says 8 GB was already tight. Fix: specify chunk-level atomic checkpoints bound to object hash, runtime, namespace, cell and replication range; test interrupted-versus-clean byte-identical completion; and measure five-worker RAM/thermal behavior before the full run.

No other decided-record conflict found: K=1 and K=2 preserve O18-4’s one/two-trial families; the `0.0035 + 0.0015 = 0.005` per-family allocation preserves P18-7/U-1 and QJ’s direct `0.01` bound; removing `L/T` is permitted because A-B7 delegates classifier contents to D-19. This read-only answer is not yet the committed review record required by project policy.

The cheaper plan’s core threshold numbers are right, but its development rule currently makes qualification impossible.  
The real laptop estimate is at least about 3,100 core-hours under the written rule, not 2,000.  
Do not accept rev 7b yet; repair the replication rule, exact classifier accounting, future-window wording, and resumability specification first.
