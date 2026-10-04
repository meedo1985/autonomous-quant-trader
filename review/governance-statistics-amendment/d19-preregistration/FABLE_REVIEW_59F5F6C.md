# Fable re-review DF3 of the D-19 preregistration rev 3 at `59f5f6c`: SOUND WITH FIXES

Date: 2026-10-04. This is an R19-2 independent statistical re-review, run as a Claude Code subagent with the `fable` model. The drafter is Claude Opus 5.5. The subagent's final report is reproduced below unchanged.

---

Model: Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family. The drafter, Claude Opus 5.5, is in the same family, so this is only the Claude half of R19-2.
Commit: `59f5f6c` (branch `docs/d19-recommendation`). Object: `review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md` rev 3.
Verdict: **SOUND WITH FIXES.** Both DS2 blockers are closed. The α budget is now consistent, and the §1/§11 claim matches owner decision U-1. Four MAJOR findings remain:
- rev 3 departs from decided O18-4 without an owner decision;
- the classifier thresholds are fitted before cells are demoted;
- the §5 choice order is circular;
- the AQTQ1 adaptation cannot handle the second attempt.

None of the four is a BLOCKER, and each is a paper fix.

## Status of DF2 and DS2

| ID | Status | Note |
|---|---|---|
| DF2-1 | RESOLVED | 0.025/M per attempt. τ verified: 0.01768 (error, N=20k), 0.00113 (DSR, N=20k), 0.00041 (0.0015 share, N=40k), at M=1000. |
| DF2-2 | RESOLVED | Residual: DF3-2. |
| DF2-3 | PARTIAL | Opposites, duplicates, clusters and the min/max correlation are added. The joint generator was replaced by an AI default, not an owner decision: DF3-1. |
| DF2-4 | RESOLVED for the listed K | Dropping K=2 conflicts with O18-4: DF3-1. |
| DF2-5 | RESOLVED | Closed by U-1. The §1, §7 and §11 wording matches U-1 items 1–4. |
| DF2-6 | RESOLVED | Residual: DF3-8. |
| DF2-7 | PARTIAL | The design is sound. Its O-6a adaptation does not work for attempt 2: DF3-4. |
| DF2-8 | RESOLVED | Residual: DF3-3. |
| DF2-9 | RESOLVED | My count at T_min=365 is 272 agnostic + 12 Q5 cells, so M = 852. That is inside 700–1,000. |
| DF2-10 | RESOLVED | |
| DF2-11 | RESOLVED | Residual: DF3-7. |
| DF2-12 | RESOLVED | The cap rule now interacts with O18-4: DF3-1, DF3-2. |
| DS2-1 | RESOLVED | |
| DS2-2 | RESOLVED | U-1 (clause A-U1). |
| DS2-3 | RESOLVED | The screen is hourly, uses production draws, and has no nonce. Residual: DF3-8. |
| DS2-4 | RESOLVED | Estimators, tails, quantile convention and order are now fixed. |
| DS2-5 | RESOLVED | 22,000 replications in every cell. |
| DS2-6 | RESOLVED | |
| DS2-7 | RESOLVED | |
| DS2-8 | RESOLVED | Residual: DF3-7. |

## Assessment of the new designs

- **0.025/M per attempt.** Sound. Bonferroni over at most two attempts gives at least 95% family-wise.
- **U_proc^R claim.** Consistent with U-1. The gate lists are identical in §1, §7.1, §11 and U-1.
- **Threshold run.** Sound. The per-tail exceedance of the `ceil(0.99999n)` order statistic at n = 10⁶ is about 1.1e-5. The 12 tails in the text give about 1.3e-4, not 1.2e-4, which is still within 2e-4. The table actually defines 9 tails. Residual: DF3-2.
- **O18-4 cells.** Improved. See DF3-1 and DF3-5.
- **K in {1, 5, 20, 80}.** Internally consistent, but it conflicts with O18-4's two-trial families (DF3-1).
- **G-12 at all H.** Sound.
- **Hourly screen.** It can run. The detection power is stated correctly: 0.958 at a 10% per-path rate and 0.260 at 1%. Residual: DF3-8.
- **22,000 development reps with the 90% UCB rule.** Sound. The certification's validity rests on the held-out run, not on development. Residual: DF3-3.
- **AQTQ1 plus drand.** Sound in principle: the commit is made before the beacon is known. Residual: DF3-4.
- **Seed encodings.** Nearly exact. Residual: DF3-7.
- **§1 overstatement.** None remains beyond the G-4 caveat in DF3-6.

## New findings

| ID | Sev | Location | Problem | Evidence | Fix |
|---|---|---|---|---|---|
| DF3-1 | MAJOR | §3.2, §1, §11 vs decided O18-4 | **Departures from decided O18-4 without an owner decision.** (a) O18-4 requires "one-trial and two-trial families", and notes that "the worst known cell is two near-identical trials". Rev 3 makes K=2 undeclarable and uncertified. (b) O18-4 requires "a joint two-family generator sharing the BTC benchmark days". Rev 3 replaces it with an "[AI default, shown to the owner]". (c) The cap rule (development cap rate > τ_DSR/4 means a challenge cell) can demote O18-4-mandated cells, such as duplicates, opposites and ρ = 0.99. Then O18-4 holds only on paper. U-1 set the precedent that narrowing decided D-18 text needs an owner decision row. | PROPOSAL.md lines 420–430. Annex A P18-7 permits the per-family allocation for `U_proc` only. | Add K=2 (Q1 at the levels defined for pairs, and Q2) to the declarable set, or put the K restriction to the owner. Put the joint-generator replacement to the owner as a decision row. Rule that if any O18-4-mandated category has no qualifying cell after development, the method does not qualify unless the owner decides otherwise. |
| DF3-2 | MAJOR | §3.5, §4 steps 3–4 | **Thresholds include cells that are later demoted.** The thresholds are the extreme over the cells that qualify at the threshold run. The cap rule demotes cells later, in development. The frozen classifier therefore still accepts windows that look like demoted, uncertified challenge cells. The thresholds are also pooled over T, so the T=365 spread loosens them at T_C2. | §4 freeze order; §3.2 qualifying rule. | Before the freeze, recompute each frozen threshold as the extreme of the stored per-cell order statistics over the **final** qualifying cells at the chosen T_min, per T level (cheap, no rerun). Each qualifying cell's refusal rate stays at or below about 1.1e-5 per tail. In §9, report the classifier's acceptance rate on every challenge cell. |
| DF3-3 | MAJOR | §5, §6 | **The frozen choice order is circular or undefined.** (a) Step 2 picks T_min so that "every τ_i" is met, including the error test, but z_crit is set only in step 3. (b) Step 1 runs at z = 1.96 without saying at which T levels. (c) τ_i depends on M and N_i. M depends on T_min and qualification, and N_i (20k or 40k) depends on development "binding", which depends on τ_i. Note that at N = 20,000 the 0.0015-share τ is 0.000175, not 0.00041. | Python exact binomial at M = 852 and 1,000: τ(0.0015, 20k) = 0.000175, τ(0.0015, 40k) = 0.000415–0.000433. Development at 22k allows at most 4 events for τ = 0.00041. | Choose T_min on the availability tests only, since z_crit meets the error test by construction. Fix the T levels for step 1. Compute τ with M_max, the manifest count at the smallest T_min candidate with every cell (conservative). Set N_i = 40,000 exactly when the development 90% UCB of the 0.0015 share exceeds τ(20,000). Print both τ values. |
| DF3-4 | MAJOR | §4 steps 5 and 7, §8, §12 item 3 | **The AQTQ1 adaptation of O-6a fails for the second attempt.** O-6a binds one coin F. Its first-post rule makes any later post from the key invalidating. §4 step 7 requires "a new post" for attempt 2. O-6a's failure outcomes ("cycle invalidated", "+1 m") have no meaning for qualification. The AQTQ1 script bytes are not given. "Two Bitcoin fees" covers only one attempt. | o6a-channel/SPEC.md §3 (bound coin, first-post rule) and §5 (no capture leads to invalidation). | Use one key and bound coin per attempt (`A_Q1`, `A_Q2`), each under O-6a §3–§5. Map every O-6a invalidation to "attempt void: held-out not run, namespace not burned, re-post on the same attempt key not allowed, so the next attempt key is used". Give the 39-byte script. State the fees per attempt. |
| DF3-5 | MINOR | §3.2 | Unequal clusters of sizes K/4 and 3K/4 are undefined at K=5. | 5/4 is not an integer. | Fix the sizes, e.g. {1, 4} at K=5, or start the level at K = 20. |
| DF3-6 | MINOR | §3.2 Q5; §7.1 G-4 | (a) Q5 omits K=1, although K=1 is declarable and the trend/vol law is defined there. (b) G-4 route D proves only n = 0. Annex C C-4 also makes the gate UNAVAILABLE for a non-finite day in a complete block. (c) The cap rate is not defined as a point estimate or a UCB. | Annex C C-4 step 4. | Add K=1 to Q5. Compute G-4 in every replication (it is cheap). Define the cap rate statistic. |
| DF3-7 | MINOR | §8 | Some encodings are still unfixed: the Philox variant and how the key and counter are mapped (e.g. numpy `Philox` 4x64-10, counter 0, pinned numpy version), and whether j and rep are 0- or 1-based. | §8 "Philox key: first 16 bytes". | State them. |
| DF3-8 | MINOR | §7.2, §10, §12 | The screen's path length and strategy warm-up history are unspecified. The screen costs up to 80 × 30 × 1,004, about 2.4M hourly strategy runs, repeated for every rejected set. The owner was told in U-1 that strategy-level simulation at scale is beyond this computer. | §7.2; U-1 question text. | Fix the path length as the C2 window plus the declared warm-up. In §12, tell the owner that if the measured screen cost is infeasible, C2 cannot declare a set of that size. |

## Commands run

- `git rev-parse HEAD`, `git log --oneline -3`.
- `cat`/`sed`/`grep` reads of:
  - `PREREGISTRATION.md`, `ADJUDICATION_71357D4.md`, `OWNER_DECISION_UPROC_SCOPE.md`, `FABLE_REVIEW_71357D4.md` and `SOL_REVIEW_71357D4.md`;
  - Annex A (P18-3..P18-7, A-B7) and Annex C (C-1..C-4, C-8, C-9, C-11);
  - `DRAFT_WORDING.md` (G-9 and G-13 lines), `d18-proposal/PROPOSAL.md` O18-2 and O18-4, and `o6a-channel/SPEC.md` §3 and §5.
- `.venv\Scripts\python.exe -` in memory, with no scipy available, using a log-space binomial and bisection Clopper–Pearson: τ at M ∈ {852, 1000} and N ∈ {20k, 40k}; the maximum development events at 22k under a 90% UCB; the order-statistic exceedance; screen power; the cell count and M.
- No files were written, nothing was edited or committed, and the network was not used. `data/` and the confirmation and lockbox data were not opened. Tests, lint and type checks are N/A because this is a review of a document only.

## For the owner

1. Revision 3 fixes the two blocking problems: the confidence level is now consistent, and the no-result promise now matches your U-1 decision.
2. Four paper repairs remain before you accept it. The most important for you: rev 3 quietly drops two-strategy families and the joint two-family simulation that you required in O18-4, so that needs your decision. The Bitcoin fingerprint post also needs a separate key for the second attempt.
3. Nothing has been built or run. After these fixes and the Codex half of the review, it should be ready for you to accept, subject to the measured pilot.
