# Adjudication of DF2 (Fable) and DS2 (Sol) on the D-19 preregistration rev 2 at `71357d4`

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter
**Records:**
- `FABLE_REVIEW_71357D4.md` (`552af72`), verdict SOUND WITH FIXES
- `SOL_REVIEW_71357D4.md` (`169985e`), verdict UNSOUND
- the owner decision U-1 (`OWNER_DECISION_UPROC_SCOPE.md`, `8e04dd8`), taken on DF2-5 and DS2-2

**Result:** `PREREGISTRATION.md` revision 3

All findings are accepted, including those on earlier findings that the reviewers rated partial or unresolved.

| Findings | Disposition | Rev 3 |
|---|---|---|
| DS2-1 (BLOCKER), DF2-1, DF1-12 | Both held-out attempts use α = 0.025/`M`, so the family-wise total is 0.05. Every target is recomputed from this α. | §4, §5, §6 |
| DS2-2 (BLOCKER), DF2-5 | **Owner decision U-1** (clause A-U1). The calibrated 1% applies to `U_proc^R`. The §1 claim and the §11 wording are rewritten to match, with no cycle-wide claim over the screened gates. | §1, §7, §11 |
| DF2-2, DS2-4, DS1-1 | **Classifier.** The thresholds come from a separate threshold run that uses the generator only, with 10⁶ draws per cell, independent of development. They are fitted for each `T_min` candidate before the §5 choices. **Fixed definitions:** the estimators, the two-sided tails, the quantile convention (order statistic `ceil(q·n)`) and the tail level (99.999%). **Refusal budget:** at most 2·10⁻⁴ per cell. **Order:** the classifier runs after Annex B rules 1–4 (it needs `L`) and before rule 5. A non-finite diagnostic is a refusal. The `K = 1` vector is defined. | §3.5 |
| DF2-3, DS1-6 | **Dependence (O18-4).** Added: opposite pairs, near-duplicate and exact-duplicate pairs, and unequal clusters. The classifier has minimum and maximum pairwise correlation. The joint two-family generator is replaced by P18-7's per-family allocation option. This is an AI default, shown to the owner. | §3.2, §3.5 |
| DF2-4, DF1-6 | **Allowed `K`.** The declarable `K` is {1, 5, 20, 80}. Every law group runs at every allowed `K` where its law is defined; the mixed column and the factor need `K ≥ 5`. | §3.2 |
| DS2-7 | Every replication computes G-12's availability for each `H` ∈ {24, 72, 168}. | §2, §7.1 |
| DS2-3, DF2-6 | **The screen can now run.** It uses an hourly null-path generator: an hourly stationary bootstrap of exploration-partition bars (mean block 168 h), with block sign flips on the hourly returns (mean 24 h), so the paths have no drift exactly. **Production settings:** draw counts of 500 for G-11 and G-14; `n_S = 30` paths. **Detection power is stated:** a 10% per-path rate is detected with P = 0.96, and a 1% rate with P = 0.26. **No nonce:** the seed is fixed by the trial-set hash. Every screen run is recorded and counted in the declaration. | §7.2 |
| DS2-5, DF2-8, DF1-3 | **Development.** Stage 2 runs in every cell, so development uses 22,000 replications everywhere. `z_f*` is stored per replication, so `z_crit` is chosen without a rerun. **Winner's curse:** `z_crit` must keep each cell's development 90% upper confidence bound at or below τ. The joint pass probability is reported from upper confidence values. The development cost is added to §10. | §5, §10 |
| DS2-6, DF2-9, DF1-11 | **Families and M.** Q1–Q4 are family-agnostic: the law is identical for both families, so each test counts once and certifies both. Q5 is family-labelled (trend rule library and vol rule library). `M` is taken from the manifest. | §3.2, §6 |
| DS2-8, DF2-10 | **Generator settings fixed:** Azzalini skew-t with ν = 5 and the skewness parameter frozen numerically; a 500-day burn-in with unconditional starts; factor loadings from the columns stream once per replication; EWMA seeded at the unconditional σ. **Corrections:** ETH legs are removed from route R (G-3 is screened), the C scale is corrected to about 2.3% per day, and the positivity claim is removed (a path at or below 0 is `INVALID_SERIES`). The Q5 side effects are disclosed. | §3.1, §3.4 |
| DF2-7 | **Held-out seed grinding.** The held-out anchor mixes in public randomness after a one-post commitment to `qualification_object_sha256`. The commitment uses the O-6a mechanism on its own dedicated key `A_Q`, with prefix `AQTQ1`. **This is an AI default with a cost:** two more Bitcoin fees, shown to the owner. | §8 |
| DF2-11, DS2-8 | Exact canonical JSON objects are given for every seed derivation. | §8 |
| DF2-12 | **Integrity.** Input bars are `U_ops`; derived series are `U_proc`. A `g` that differs from the frozen value makes the C2 declaration invalid. A cell is qualifying only if its development cap rate is at most τ_DSR/4; otherwise it is a challenge cell. | §3.2, §3.5, §7.1 |
