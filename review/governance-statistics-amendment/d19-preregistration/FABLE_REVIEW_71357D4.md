# Fable re-review DF2 of the D-19 preregistration rev 2 at `71357d4`: SOUND WITH FIXES

Date: 2026-10-04. This is an R19-2 independent statistical re-review, run as a Claude Code subagent with the `fable` model. The drafter is Claude Opus 5.5. The subagent's final report is reproduced below unchanged.

---

Model: Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family. The drafter, Claude Opus 5.5, is in the same family, so this review is only the Claude half of R19-2.
Commit: `71357d4` (branch `docs/d19-recommendation`). Object: `review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md` rev 2.
Verdict: **SOUND WITH FIXES.** Rev 2 repairs most of the rev 1 design. The sign-flip null, the exact-binomial targets, the gate-by-cause matrix and seeds bound to the qualification object are all sound. Seven MAJOR findings remain, and none is a BLOCKER:
- the α for the two held-out attempts is stated inconsistently;
- the classifier thresholds cannot be estimated as specified;
- the grid omits cells that O18-4 requires;
- some allowed K values are not certified for every law;
- route S changes decided P18-7 and its wording overstates the claim;
- the screen cannot run as specified;
- the held-out seeds can be ground.

## Status of DF1 and DS1

| ID | Status | Note |
|---|---|---|
| DF1-1 | RESOLVED | Route S is no longer an estimate; it is now a screen. New issues: DF2-5, DF2-6. |
| DF1-2 | RESOLVED | The §5 targets check out at pass probability 0.99 and M = 1000: 0.01852, 0.00134, 0.00051. At 0.999 they are 0.0178, 0.00116, 0.00043. |
| DF1-3 | RESOLVED | Two-stage development is in place. Residual: DF2-8. |
| DF1-4 | RESOLVED | The sign flip gives an exact zero mean. |
| DF1-5 | RESOLVED for route R | Residuals: DF2-6 (hourly), DF2-10. |
| DF1-6 | PARTIAL | DF2-4 |
| DF1-7 | RESOLVED | The single ARFIMA column is a reported challenge cell. |
| DF1-8 | RESOLVED | Q3 added, plus the block-60 sensitivity run. |
| DF1-9 | RESOLVED | No library and no "resembles" judgement. Residual: DF2-6. |
| DF1-10 | RESOLVED | Residual: DF2-12. |
| DF1-11 | PARTIAL | DF2-9 |
| DF1-12 | PARTIAL | §4 contradicts §6: DF2-1. |
| DF1-13 | RESOLVED | Disclosed in §1. |
| DF1-14 | RESOLVED | Residual: DF2-11. |
| DF1-15 | RESOLVED | A measured pilot is required. Development cost: DF2-8. |
| DS1-1 | PARTIAL | DF2-2, DF2-3 |
| DS1-2 | RESOLVED for route R | DF2-6, DF2-10 |
| DS1-3 | RESOLVED | |
| DS1-4 | RESOLVED | It is no longer an estimate. The replacement screen has new issues: DF2-5, DF2-6. |
| DS1-5 | RESOLVED | |
| DS1-6 | PARTIAL | DF2-9 |
| DS1-7 | RESOLVED | |
| DS1-8 | PARTIAL | DF2-7, DF2-11 |
| DS1-9 | RESOLVED | |

## Assessment of the new designs

- **(a) Classifier.** A mechanical classifier at evaluation is the right idea, and counting its refusals inside `U_proc` is consistent with P18-7. The threshold construction is defective (DF2-2), and the classifier misses negative correlation (DF2-3).
- **(b) Sign-flip null (Q5).** Sound. The signs are independent of the path and `E[s_t] = 0`, so `E[X] = 0` exactly. The geometric-block sign process is stationary. Two side effects should be disclosed (DF2-10): each column's skewness becomes zero in distribution, and the implied exposures range over [−1, 2].
- **(c) Route S.** Calling it a screen and not a bound is honest. It is still not a D-19 choice: it narrows decided P18-7, which made the 1% target cover every pre-lockbox mandatory gate, so the amendment can authorise it only through an explicit owner decision. As written it also cannot run, and its seed can be shopped (DF2-5, DF2-6).
- **(d) Exact-binomial targets.** Sound, and the numbers above are confirmed. There is a winner's-curse residual in the choice of `z_crit`, and the α for each attempt is inconsistent (DF2-1, DF2-8).
- **(e) Leg generators.** Adequate for route R. The GARCH-t5 fourth-moment condition holds (0.9825 < 1). Minor gaps are in DF2-10.
- **(f) Seeds.** Binding the held-out seeds to `qualification_object_sha256` closes DS1-8's binding gap. It does not stop grinding (DF2-7).

## New findings

| ID | Sev | Location | Problem | Evidence | Fix |
|---|---|---|---|---|---|
| DF2-1 | MAJOR | §4 step 6 vs §5, §6; §1 | The α for each attempt contradicts itself. §4 and the adjudication say "each attempt uses α = 0.025/M". §6 says 0.05/M on the first attempt and 0.025/M on the second. Under §6, two attempts carry a total α of 0.075, so §1's "simultaneous one-sided 95%" is false. | `PREREGISTRATION.md` lines 206 and 240; `ADJUDICATION_AA981D8.md` (DF1-12 row). | Use 0.025/M for both attempts, then recompute τ. At M = 1000 and pass probability 0.999: error 0.01768, DSR availability 0.00113, other route-R gates 0.00041. |
| DF2-2 | MAJOR | §3.5 thresholds | **The thresholds cannot be estimated as written.** A 99.99th percentile is not estimable from the 2,000 stage-1 replications: it is the sample maximum, which a new draw exceeds with probability 1/2001 = 5.0e-4 per component. **They are fitted in-sample and circularly:** the thresholds depend on which cells qualify, which depends on `T_min`, which depends on availability, which includes the refusals. The development refusal rate is measured on the same replications the thresholds were fitted to. **Some lower thresholds are missing:** the minimum skewness and the correlation have no lower threshold, and mean pairwise correlation is undefined at K = 1. **The budget is compared with the wrong number:** "≈0.001, inside the 0.0035 share" should be compared with τ ≈ 0.00116, so the classifier would use almost the whole development target for DSR availability and leave about 2e-4 for Annex B rules 1–6. | Python check: P(exceed max of 2,000) = 5.0e-4; P(exceed max of 22,000) = 4.5e-5. | Fit the thresholds from a separate, large run of the generator only (the diagnostics are cheap, e.g. ≥10⁶ draws per cell, 99.999th percentile). Make them two-sided where needed and fit them for each `T_min` candidate before the §5 choices. Give the classifier an explicit refusal budget per cell (e.g. ≤ 2e-4) and define the K = 1 vector. |
| DF2-3 | MAJOR | §3.2 vs decided O18-4 | O18-4 requires the qualifying cells to include duplicates and opposites, unequal clusters and a joint two-family generator sharing the BTC days. Rev 2 has only ρ ≥ 0 equicorrelation. The classifier has only an upper threshold on mean pairwise correlation, so a negatively correlated or clustered window passes it with no qualifying cell behind it. | `d18-proposal/PROPOSAL.md` O18-4 (around lines 420–430). | Add cells for opposite pairs (ρ < 0) and block-cluster correlation. State what happens to duplicates (DESIGN line 210). Add min and max pairwise correlation to the classifier. Record, visibly to the owner, that the joint generator is replaced by P18-7's per-family allocation option. |
| DF2-4 | MAJOR | §3.2 K rule | **The allowed K values outrun the certified laws.** A declaration may use K ∈ {1, 2, 3, 5, 10, 20, 40, 80}. The non-Gaussian groups certify only part of that: Q2 {1, 5, 20, 80}, Q3 and Q5 {5, 20, 80}, Q4 {2, 3, 20}. Because `P_0(E_f)` is not monotone in K (FB1-16), K = 3, 10 or 40 under heavy tails, GARCH or a factor structure is not certified. The DF1-6 hole is narrowed, not closed. | §3.2 lines 95–124. | Restrict the declarable K to values present in every law group (e.g. {5, 20, 80}, plus K = 1 and 2 where their laws are defined), or extend Q2–Q5 to every allowed K. |
| DF2-5 | MAJOR | §1 item 2, §7, §11 | **Route S changes decided text.** It narrows P18-7, whose 1% target covers "any pre-lockbox mandatory gate". P18-7 leaves D-19 only "joint cells or per-family allocation", so this is an amendment of decided D-18 text and needs an explicit owner decision row, as A-B7 was. **§11 contradicts itself:** "U_proc is certified … by (S) a fail-closed screen", then "Route S is … not a calibrated bound". **§1 overstates:** "the cycle's bound is at most 0.01" uses `U_proc` while silently excluding gates G-3, G-5–G-8, G-11 and G-14. | Annex A P18-7; DRAFT_WORDING §4. | Define `U_proc^R`. Word it as: "P18-7's 1% target applies to `U_proc^R`; gates … are excluded from the calibrated target and governed by a pre-declaration screen; their unavailability on the window is a `U_proc` event recorded without a certified rate." Put it to the owner as a decision row. |
| DF2-6 | MAJOR | §7 route S | **The screen cannot run as specified.** The Q5 generator produces daily returns, while the declared strategies and gates G-5..G-7, G-11 and G-14 run on the hourly event contract (C-6 step 4; G-6 `t − 1h`). "With signs" means nothing for market paths. **Its detection power is low:** 50 paths catch a 1% per-path unavailability with probability 0.39, and catch it with probability 0.95 only at about 5.8%. **The real-declaration seed is undefined:** the §8 "screen" stream is keyed by (cell, rep), so a declarer can re-screen with new seeds until the set passes. | Annex C C-6 and C-7; Python check of 1 − (1 − p)⁵⁰. | Specify an hourly null-path generator (e.g. an hourly stationary bootstrap of exploration data). Set the screen seed to SHA256 of the declared trial-set hash, with no free nonce, and record or post every screen run. State the detection power. |
| DF2-7 | MAJOR | §8 held-out anchor | **The held-out seeds can be ground.** They are a deterministic function of `qualification_object_sha256`, which the builder controls. The synthetic beacon is derived from the seed and adds no outside entropy. Unrecorded pre-runs over cosmetic variants of the object could pick favourable held-out sets, and this could not be detected. | §8 lines 298–319; DRAFT R-7. | After the freeze commit is posted, mix an unpredictable external value (the existing O-6a / drand seed_disclosure mechanism) into the held-out anchor, and record it. |
| DF2-8 | MINOR | §5 | **Winner's curse in `z_crit`:** `z_crit` is the smallest value at which every cell's estimate is ≤ τ, so it favours cells whose estimates came out low. At 22,000 replications, a cell with a true rate of 0.0195 shows ≤ τ with P ≈ 0.14 and then passes held-out with P ≈ 0.90; at 0.020 the figures are 0.05 and 0.78. **Optimistic report:** a joint pass probability computed from point estimates is too high. **Trigger not defined:** the stage-2 trigger has no stated z. Since τ/2 ≈ 0.009 for the error test, almost every cell triggers, so development costs about as much as held-out, and §10 does not show this. | Python exact binomial. | Report the joint pass probability from upper confidence values. Evaluate the trigger at z = 1.96, or store `z_f*` per replication. Add the development cost to §10. |
| DF2-9 | MINOR | §3.2, §6 | "Family label" is undefined for Q1–Q4, whose generators are the same for both families. If every cell is run for both families, M ≈ 247 cells × 3 bounds × 2 ≈ 1,500, not 750–1,000. | Count with `T_min` = 365: Q1 145, Q2 84, Q3–Q5 6 each. | Define the label and recount M. The effect on τ is small. |
| DF2-10 | MINOR | §3.1, §3.4 | **Leg scale:** the C standard deviation is about 2.3% per day (b ≈ 0.6 × 3.5% = 2.1%, X 1.05%), not 1–2%. **ETH leg:** the joint law of `X^E` with `X` is unspecified, and `X^E` is unused in route R. **Q5 side effects:** the sign flip makes each column's skewness zero in distribution and implies exposures in [−1, 2]. **Positivity:** the "1 − 10⁻⁹" equity-positivity figure is unverified for GARCH-t5 and skew-t. | Arithmetic. | Correct the scale. Specify `X^E` or drop it. Disclose the Q5 side effects. Verify the positivity figure in the pilot or drop it. |
| DF2-11 | MINOR | §8 | The byte encodings of `seed‖"h"‖j` and `seed‖"beacon"` are unspecified (hex or raw bytes, decimal j). The outer seed is written in set-like notation. | Lines 298 and 317. | Write the exact JSON objects and encodings. |
| DF2-12 | MINOR | §7.1, §3.2, §3.5 | **Integrity boundary:** the line between the integrity check (`U_ops`) and Annex B rule 1 `INVALID_SERIES` (`U_proc`) is undefined. **Wrong `g` at C2:** "C2 is not covered" has no fail-closed consequence. **Cap rule:** a qualifying cell whose cap rate lies between τ ≈ 0.00116 and 1% guarantees certification failure. | Annex B §2.5. | Make input market data `U_ops` and derived series `U_proc`. Make a wrong `g` ineligible. Align the cap cutoff or state the intent. |

## Commands run

- `git rev-parse HEAD`.
- `cat`/`sed`/`grep` reads of: `PREREGISTRATION.md`, `ADJUDICATION_AA981D8.md`, `FABLE_REVIEW_AA981D8.md`, `SOL_REVIEW_AA981D8.md`, Annexes A, B and C, the `DRAFT_WORDING.md` excerpts, and `d18-proposal/PROPOSAL.md` O18-2 and O18-4.
- `.venv\Scripts\python.exe -` in memory: exact binomial CDF and Clopper–Pearson upper bounds by bisection; τ at M ∈ {750, 1000}, both α readings and pass probabilities 0.99 and 0.999; the sample-maximum exceedance probability; screen detection power; the winner's-curse check.

No files were written, nothing was edited or committed, and the network was not used. `data/` and the confirmation and lockbox data were not opened.

## For the owner

1. Revision 2 fixes most of what the two earlier reviews found. The plan is now workable, but about seven specific repairs are still needed before you accept it.
2. The most important are these: the confidence level is stated two inconsistent ways; the gate screen (route S) needs your explicit decision because it changes a rule you already decided, and as written it cannot run; and the held-out random seeds must include an outside random value so nobody can pick lucky ones.
3. Nothing has been built or run, and every fix is a paper change. A revision 3 still needs the other-family (Codex) review.
