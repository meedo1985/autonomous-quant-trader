# D-11 decision proposal, revision 2 (senior-statistical-governance agent)

Revision of `PROPOSAL.md` (c870152) after the R19-2 reviews `SOL_REVIEW_C870152.md` and `ASTRA_REVIEW_C870152.md` (3a116a6). Agent `senior-statistical-governance`, read-only, checkout `aqt-freeze-sheet` at `3a116a6`. Model reported by the agent: Claude Fable 5.1 (`claude-fable-5-1`). Report verbatim below (harness indentation removed).

---

# D-11 decision proposal, revision 2: lockbox prediction distribution and pass rule (L-1..L-4)

**Reviewer model (observed):** Claude Fable 5.1, model ID `claude-fable-5-1`, as reported by this session's metadata. I am an AI reviewer, not an authority. This is a proposal only: it accepts, signs and activates nothing.

**Revises:** revision 1 (`d11-proposal/PROPOSAL.md`, `c870152`), answering the R19-2 reviews `SOL_REVIEW_C870152.md` (gpt-6-sol, FIX, D11R-S-1..7) and `ASTRA_REVIEW_C870152.md` (gpt-6-astra, FIX, D11R-A-1..7), both in `3a116a6`. Both were read in full.

**Checkout:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch freeze-sheet, HEAD `3a116a6`. The working tree was clean before and after; nothing was edited, staged or committed. No simulation was run, and there was no confirmation, lockbox, network or credential access.

**Review status:** revision 2 is unreviewed. R19-2 requires a focused re-check by two different model families before any owner decision.

**VERDICT: `AMENDMENT_REQUIRED`.**
- The statistics (Route A) is a `BINDING_CANDIDATE`, read from the frozen text.
- But the lockbox run cannot be executed under the current Constitution §7a and threat model (section 4).
- The C2 amendment therefore needs one more access clause (Q2) before D-11 can be complete.
- Keeping D-11 blocked remains a valid choice.

## 1. Authority and status

| Item | Status | Source |
|---|---|---|
| Prediction construction, tail, pass rule | FROZEN v1.0 | `protocols/protocol_v1.yaml` l.83–92 |
| Bootstrap type, PW blocks, 2,000 iterations | FROZEN | l.223–226 |
| Lockbox cost 1.0; PASS_FAIL_ONLY; cooldown | FROZEN; kept in force by the draft | l.75–76, l.80–82; DRAFT_WORDING §4 |
| Coarse attestation fields | FROZEN; open under D-12 | l.77–79 |
| Lockbox partition | FROZEN; C2 keeps it | l.67; DRAFT §2.1 |
| 24-month training window; 30-day step and retrain; purge | FROZEN | l.198–200, l.205 |
| Lockbox = "future data readable only by lockbox_eval" | FROZEN | Constitution §0 l.20; DRAFT: l.20 unchanged |
| Only lockbox_eval reads it; every read marks the segment EXPOSED; exposed segments never re-lock | FROZEN | Constitution §7 l.73–85 |
| Confirmation reachable only through the experiment engine | FROZEN | Constitution §7a l.90, l.94 |
| lockbox_eval permission: "lockbox read + attestation signing only" | FROZEN | `docs/THREAT_MODEL_v1.md`, core permissions |
| E-IMPROV and E-DIFF named separately; L-4 is E-IMPROV, "subject to D-11" | OWNER D-01/D-02 | `OWNER_DECISION_D01_D04.md` l.42–44 |
| Nomination and DSR use E-DIFF | OWNER D-18 | DRAFT §2.4 |
| Two AI reviews plus the owner replace a statistician | OWNER R19-2 (recorded as weaker) | `OWNER_STEP0_DECISION.md` |
| Lockbox code bindings | OPEN (R-8: "No lockbox clause is bound here") | DRAFT l.147 |
| `LOCKBOX_PREDICTION_PROPOSAL.md`; this document | Unaccepted AI proposals | — |

## 2. Definitions (Route A)

| Symbol | Binding |
|---|---|
| `[L0, L1)` | L0 = 2025-06-01T00:00Z; L1 = 2026-09-01T00:00Z. |
| `m` | 457 scheduled complete UTC days. This is a **proposed interpretation** of l.85's "decision-count", not frozen text (D11-6). It rests on one decision per day (l.209; C-11 uses the same convention, although N-1 decided only G-12 and CPCV). It is fixed before any read. |
| Source | The nominee's BTC baseline 1x run over `[w0, w1)`. Both legs go through `daily_net_returns` and are aligned by `paired_daily_returns`. `d_t = c_t − b_t`, and n = (w1 − w0)/1 day. |
| Block input | **The Sharpe influence process of `d`** (section 3). |
| Resampling | Stationary bootstrap. Each attempt draws m = 457 indices over 0..n−1: restart with probability 1/b, otherwise step forward modulo n. The path is d at those indices. Exact identity: applying the same indices to the pairs (c, b) and then differencing gives the same path. So for E-DIFF, "joint-leg" and "difference-series" resampling coincide. |
| Statistic | `T = difference_series_sharpe.scaled` = √365·mean(d)/sd(d), with n−1 (E-DIFF). |
| Quantile | q = `type_seven_quantile(T*_0..T*_1999, 0.05)`. The reference code's float64 result decides (C-0 Numerics, made explicit for the L gates). |
| L-1 | PASS iff T_L ≥ q. |
| L-2 | PASS iff T_L > 0, the same statistic, because l.91 uses one token for both. |
| L-3 | PASS iff `max_drawdown(cand) − max_drawdown(bench) ≤ 0.05`, on the BTC lockbox BacktestResults over `[L0, L1)` (hourly segments). |
| L-4 | PASS iff C-3 holds on the ETH lockbox 1x run: E-IMPROV > 0 AND DD(ETH). |

**Availability (fail-closed; UNAVAILABLE never passes):**
1. **Source days.** The timestamps are exactly w0 + k days for k = 0..n−1. Candidate and benchmark identities, asset and cost string match. n ≥ 16.
2. **Source E-DIFF.** `difference_series_sharpe.reason` is None. This field is the test, **not** the aggregate `.reason`. The repository code shows they differ in both directions: a constant candidate leg gives aggregate `ZERO_VARIANCE` while E-DIFF is computed, and identical legs give aggregate `None` while E-DIFF is `ZERO_VARIANCE`.
3. **Block length.** `block_length(ψ)` returns 1 ≤ b ≤ n.
4. **Attempts.** All 2,000 attempts are run in order, and every T*_r is available and finite. Nothing is omitted, replaced or extended. q is finite.
5. **Lockbox days.** The timestamps are exactly L0 + k days for k = 0..456: 457 days and 10,968 hourly segments for both legs. A shorter complete path is UNAVAILABLE. T_L comes from the d-field and is available.
6. **L-3.** Both BTC legs' max_drawdown values are finite.
7. **L-4.** The ETH timestamps pass the same checks, and **both** leg Sharpes are available (`paired_sharpe_improvement` not None, aggregate reason None).

## 3. Block-length input (D11R-S-2, D11R-A-2)

Line 85 says "Politis-White blocks" but does **not** say from which series. Revision 1's "literal" claim for raw `d` is withdrawn.

- **(i) Raw d.** PW chooses b for the variance of the *mean of d* and ignores dependence in the squared component. Under volatility clustering with little autocorrelation in returns, which is typical of crypto, it can choose blocks too short for a Sharpe statistic.
- **(ii) The Sharpe influence process of d:** ψ_t = u_t − (S/2)(u_t² − 1), where u is d standardised with the population scale and S is the sample daily Sharpe of d. This is the Task 12 convention (`IMPLEMENTATION_CONVENTIONS.md` §"Paired-Sharpe influence"), applied to one series.

**Binding: (ii).** It targets the dependence of the statistic actually computed, it matches the accepted G-1 convention, and the code exists (`_influence`, currently private, and `block_length`).

**Honest limits:**
- At typical daily Sharpe values the u² weight S/2 is small, so (i) and (ii) may give similar b. The gap was not quantified.
- PPW chooses b for a mean's long-run variance. It **does not establish coverage** for a selected nominee's predictive quantile at horizon m ≠ n (`UNVERIFIED_EXTERNAL_ASSUMPTION`; Astra cites Politis–White §2).
- Reference vectors for ψ pass to D-20.

## 4. Data flow and identity boundary (D11R-S-3, D11R-A-1)

**What a run of the registered strategy over `[L0, L1)` needs:**
- Feature history before L0. `sma_4800` needs 200 days (`FEATURE_FACTORY_v1.md` l.20). The EMA, EWMA and benchmark volatility features (half-life 168 h, `CANONICAL_BENCHMARKS_v1.md` l.21–22) need a fixed start.
- For trained models, refits at r_k = L0 + 30k days, k = 0..15 (16 refits). Each is trained on `[r_k − 24 months, r_k)`, with labels purged at r_k (l.198–200, l.205).

**Why no boundary-preserving contract can run the registered rolling refits:**
- Every refit after L0 mixes confirmation and lockbox rows.
- The experiment engine cannot read the lockbox (§7), and lockbox_eval may read only the lockbox (threat model).
- A "sealed package" of confirmation bars still hands confirmation data to another identity; hashing does not change that.
- Handing over only a fitted model cannot support the later refits.

**Proposed contract. It needs a §4 amendment to Constitution §7a and to the threat model's lockbox_eval permission (owner question Q2):**
1. **Read access.** lockbox_eval reads, read-only and under the cycle's data-manifest hash, BTC and ETH 1h bars in `[S_pre, L0)`, with S_pre = L0 − 24 months − 200 days = **2022-11-13T00:00Z**, together with the lockbox bars.
2. **Feature warm-up.** All features and the benchmark estimator start at S_pre, with the feature factory's own initialisation.
3. **Start state, for both legs, BTC and ETH.** At L0 each leg is flat: exposure 0, no pending orders, an unset risk-increase clock (C-6 lets the first increase through), fresh overlay state, equity 1.0. MDD is measured on the equity path from L0. This follows the D-13 precedent for CPCV (C-14 (3)).
4. **Refits.** Fits and refits as above, under the nominee's registered training rule. Rule-based nominees skip fitting.
5. **From the experiment engine:** only the sealed prediction artifact (q, n, b, stream identity, hashes) and the nominee's identity. No per-bar confirmation output crosses identities.
6. **Out of lockbox_eval:** PASS/FAIL to research, plus whatever D-12 decides.

**Why this does not leak:** information flows only into the most restricted identity, and no new path to research is created.

**Rejected alternative:** freezing the model at L0 and warming up inside the lockbox. That drops the registered retraining rule and shortens m, so it no longer tests the registered strategy.

## 5. Consumer matrix

| Consumer | Frozen wording | Binding | Open |
|---|---|---|---|
| l.84–86 | bootstrap the difference series → delta-Sharpe | E-DIFF paths, m = 457, ψ blocks | D-20 code |
| l.87–89 | lower 5th percentile | type 7, float64 | — |
| l.91 L-1, L-2 | the same token twice | E-DIFF: T ≥ q; T > 0 | — |
| l.91 L-3 | drawdown constraint (l.276–278, O-7) | hourly MDD over `[L0, L1)` | R-8 extension |
| l.91 L-4 | ETH sanity (l.42–43, l.279) | C-3, E-IMPROV (D-02) | — |
| l.77–79 | coarse fields | sign ← L-2, drawdown ← L-3, decay ← L-1 | D-12, incl. L-4 disclosure and PASS_FAIL_ONLY |
| §7a; threat model | access | section 4 contract | §4 amendment (Q2) |
| §0 l.20 | "future data" | reading in section 9 | Q3 |
| l.74; DRAFT §2.3 | reads per family | section 7 | — |
| l.93–95 | net-return rule REMOVED | tension in D11-10 | — |

## 6. Worked examples (results from the repository code, read-only, CPython 3.14.7)

**Positive boundary** (y[99] = 0.30, y[100] = 0.32):
- Exact arithmetic gives q = 319/1000. Type 6 would give 301/1000, and nearest rank 0.30.
- **Operative float64:** `type_seven_quantile` returns q = 0.31900000000000006.
  - T = 0.319: **L-1 FAIL**, L-2 PASS.
  - T = 0.31900000000000006: L-1 PASS (equality), L-2 PASS.
  - T = 0.31: L-1 FAIL.

**Negative boundary** (−0.42, −0.40):
- Exact arithmetic gives q = −401/1000.
- **Operative float64:** q = −0.40099999999999997.
  - T = −0.401: **L-1 FAIL**, L-2 FAIL.
  - T = −0.40099999999999997: L-1 PASS, L-2 FAIL.
  - T = 0.0: L-1 PASS, L-2 FAIL (strict inequality).

**Zero-boundary float residue (new; D11-12):** c = (0.01)×5, b = (0.01, 0.02, −0.01, 0.03, 0.0). mean(d) is exactly 0, so L-2 FAILs in exact arithmetic. Float64 gives E-DIFF = 8.384e−16, so L-2 **PASSES** under the operative rule.

**The two measures disagree:** c = (0.012, 0.004, 0.012, 0.004), b = (0.03, −0.01, 0.03, −0.01).
- Exact: S(c)² = 3, S(b)² = 3/16, S(d)² = 3/256.
- E-IMPROV = 24.818088161661457; E-DIFF = −2.0681740134717863 (float64, matching the closed forms).
- So L-2 passes under E-IMPROV and fails under E-DIFF.

**Approximate illustrations only** (not operational probabilities, not calibration). Assumptions: a normal limit; iid stationary days; independent source and target; the nominee **not** selected (selection worsens this); equal per-day asymptotic variance in source and target.
- **L-1 false-fail rate:** Φ(−1.645·√(n/(n+m))) = **0.0797** at n = 1247, and **0.0834** at n = 1100.
- **L-2 only** (not the whole lockbox), with the Gaussian near-zero-Sharpe standard error √(365/m)·√(1 + S_d²/2) (factor 1.00034 at an annual 0.5): the standard deviation is ≈ 0.894. L-2 alone passes about 0.50 of the time at a true E-DIFF of 0, and about 0.712 at 0.5.
- Fat tails or skew change these. The higher-moment variance is an `UNVERIFIED_EXTERNAL_ASSUMPTION` (Astra cites Lo, A32–A33).

## 7. Dependence, selection, and the second family's read (D11R-S-5)

**Selection.** The source is the family's top E-DIFF nominee, so the centre is biased upward; the frozen text forbids recentring. The plug-in also leaves out source estimation error (D11-3).

**The second family's read.**
- v1.0 allowed two reads per family on one lockbox window (l.74), and §7 l.77 marks EXPOSED at every read. So v1.0 itself requires a read of an already-EXPOSED segment within a cycle.
- "Never re-lock" (§7 l.81) governs status between cycles: release goes to confirmation, and only between cycles (l.83).

**Proposed default:**
- Each family's nominee gets one separate lockbox_eval evaluation of the same `[L0, L1)`.
- Exposure is recorded at the first read.
- Release happens at the end of C2; using it in C3 needs the later amendment noted in DRAFT §1.
- The second result discloses PASS/FAIL only.
- [AI default, for review:] both nominees' prediction artifacts are sealed before the first lockbox read.

**Limits.** The second nominee is fixed at the single nomination look (DRAFT §2.3, `before_look`), so no adaptive change is possible. The two results share one market path and one benchmark path: they are correlated, not a replication.

## 8. Routes

All routes need D-20 work:
- a generator that outputs m ≠ n indices (the current `bootstrap_indices` fixes the output length at n);
- a new stream purpose (`ReplicateStream` accepts only `paired_sharpe_ci`);
- the ψ input;
- reference vectors;
- an R-8 extension for `max_drawdown`.

**The lockbox seed source and the full source/target/nominee identity are undecided.** The beacon seed decision for G-1, G-11 and G-14 does not extend to the lockbox (D11R-S-7).

| Route | Content | Governance | Frozen wording |
|---|---|---|---|
| **A** (recommended) | E-DIFF for L-1 and L-2; sections 2–4 | fills the D-11 marker; plus the Q2 access amendment | compatible (a reading) |
| B | joint legs, E-IMPROV (revision 1's source proposal) | amends the l.85 input; plus Q2 | needs an amendment |
| C | L-1 E-DIFF, L-2 E-IMPROV | only as explicit amendment wording; the D-12 sign becomes ambiguous | contested |
| D | KEEP_BLOCKED | **prevents signing C2 as currently drafted** (DRAFT l.356); a research-only C2 would need its own revised wording and review | — |

**Why A, stated precisely:**
- It keeps the frozen input.
- It gives the BTC lockbox one estimand, the same one the DSR certifies and nomination uses.
- **Its power cost is unquantified.** A nominee whose average daily lockbox difference is ≤ 0 fails even if it improves risk-adjusted return. Neither selection nor DSR clearance guarantees a positive future mean difference.
- B is a different, uncalibrated additional filter. With nomination fixed and no retries, choosing B over A does not enlarge the upstream false-promotion event.

## 9. Is the lockbox "future data"? (D11R-A-5)

Constitution §0 l.20 calls the lockbox "future data". Protocol v1.0 was frozen on 2026-09-12 (`f1c17eb`, with the Constitution and threat model in the same commit), with a lockbox ending 2026-08-31: **already past at freezing**.

**R1: calendar-future.** This is the plain meaning, and it matches the purpose of a lockbox. Under R1 the v1.0 set conflicted with itself on the day it was frozen. By §3 the Constitution prevails, so the lockbox would be void and no promotion possible until the partitions are amended.

**R2: later than confirmation and held back from research.** This fits:
- "readable only by lockbox_eval";
- the threat model's treatment of the lockbox as an access domain;
- §7 l.81 ("Lockbox boundary only moves forward");
- and it makes the frozen set consistent.

**My assessment.**
- The documents support R2 better. But the word is genuinely ambiguous, and the repository history (from 2026-09-08) cannot show whether the window was designed while it still lay in the future.
- D-18's accepted weakness covers public confirmation prices, not this question. So any retention needs the owner's R2 reading **written into the C2 amendment**.
- Retention means a **historical, held-back check with no demonstrated predictive coverage, possibly contaminated by selection**. It can catch overfitting to confirmation, but not trial designs shaped by public 2025–26 prices.
- Later paper trading is fresh evidence only under its own procedure, fixed in advance.

**What a truly future window would cost:**
- **457 days:** the read cannot come before about 15 months after the C2 declaration plus processing. That is past the 255-day cycle cap, so the partitions (l.67) and the cycle termination (O-2) would both need amending.
- **Fitting inside 255 days:** m ≈ 180–225 days, ending before reads at about day 200–225. The approximate L-2 standard deviation becomes 1.27–1.42 instead of 0.89, a weaker check. The partitions and the "15 months" basis (l.92) would need amending, and reads could come no earlier than about day 200.

## 10. Findings

**Carried over from revision 1:**
- **D11-1 (BLOCKER, inherited):** Route B changes the l.85 input. Retained.
- **D11-2 (NON-BLOCKING):** the boundary is decided by the float64 result. Retained; revision 1's worked pass claims are corrected in section 6.
- **D11-3 (NON-BLOCKING):** the plug-in undercovers. Retained, with its assumptions labelled.
- **D11-4:** the data flow was unspecified. Now answered by section 4, which becomes the Q2 amendment.
- **D11-5:** public lockbox prices. Merged into section 9 and Q3.
- **D11-6 (NON-BLOCKING):** 457 is now called a *proposed interpretation*; N-1 did not decide D-11.
- **D11-7 (NON-BLOCKING, conditional):** a declared outage inside the window makes the result UNAVAILABLE. Whether one exists cannot be known without access.
- **D11-8 (NON-BLOCKING):** DRAFT l.254's "lockbox interval" purpose does not exist. Retained.
- **D11-9 (NON-BLOCKING):** expanded; section 7 resolves the EXPOSED read.
- **D11-10 (NON-BLOCKING):** sign(E-DIFF) = sign(mean d) stands. **The "small cost" claim is withdrawn as unsupported.**
- **D11-11 (NON-BLOCKING):** L-3's window and R-8 binding are bound in section 2.

**New:**
- **D11-12 (NON-BLOCKING):** float64 residue can turn a true-zero mean difference into an L-2 PASS (section 6). This is accepted under C-0 Numerics but must be disclosed.
- **D11-13 (BLOCKER for executing any route):** revision 1 missed the threat model's "lockbox_eval: lockbox read + attestation signing only". Section 4 requires amending both that permission and §7a.
- **D11-14 (QUESTION):** revision 1 missed Constitution §0's "future data", a two-way citation-audit failure on my part. Assessed in section 9; goes to Q3.

## 11. Dispositions of the review findings

| ID | Disposition |
|---|---|
| S-1 | Accepted, repaired (section 6) |
| S-2 | Accepted, repaired: ψ bound (section 3) |
| S-3 | Accepted. Contract in section 4; needs a §4 amendment, which becomes Q2 |
| S-4 | Accepted, repaired (section 2, availability) |
| S-5 | Accepted, repaired (section 7) |
| S-6 | Accepted, repaired (sections 8, 12; D11-10) |
| S-7 | Accepted, repaired (section 8) |
| A-1 | Accepted, as S-3 |
| A-2 | Accepted, repaired: the "literal" claim is withdrawn and the PPW limit stated |
| A-3 | Accepted, repaired, including the shorter-path rule |
| A-4 | Accepted, repaired, including that B does not enlarge the false-promotion event |
| A-5 | Accepted (section 9); it becomes Q3 after the textual conflict is resolved |
| A-6 | Accepted, repaired (Route D) |
| A-7 | Accepted, repaired: labelled L-2-only with assumptions; the higher-moment variance marked unverified |

## 12. Questions for the owner

**Q1. What should the lockbox's main BTC test measure?**
- **"Average daily difference, as written (Recommended)."** The strategy passes only if its average daily return over the lockbox beats the benchmark's (it does not have to win every day), and its result is not unexpectedly low compared with what confirmation predicted. This keeps the frozen rule text and tests the same claim your luck test certifies. A smoother strategy that earns less on average fails; how often that happens to good strategies is unknown.
- **"Sharpe minus Sharpe."** Like your ETH and confidence-interval checks. The frozen rule text must be rewritten, it needs new code, and it tests a claim the luck test never certified.
- **"Keep blocked."** C2 cannot be signed as drafted.

**Q2. May the lockbox checker also read the 2022-11-13 to 2025-05-31 price history, so the strategy can run and retrain exactly as registered?**
- **"Yes, add it to the C2 amendment (Recommended)."** This changes Constitution §7a and the threat model. The data flows only into the most locked-down program, and only PASS/FAIL comes out.
- **"No / decide later."** The lockbox cannot run, so there is no promotion in C2.

**Q3. The lockbox period (June 2025 to August 2026) had already ended when the rules were frozen, and its prices are public. What should happen?**
- **"Keep it as a held-back historical check (Recommended)."** The reading "future = later than confirmation and held back from research" is written into the amendment, and any claim that it is a fresh test is given up. Later paper trading is fresh only under its own rules, fixed in advance.
- **"Use a truly future window."** Either wait about 15 months and change the cycle limit, or use about 6–7 months, a weaker test. Both need amendments.
- **"Decide later."** The lockbox cannot run until this is decided.

## 13. Protocol items, and what remains

**Protocol items run:**
1. Two-way citations: found §0 l.20 and the threat model, which revision 1 had missed.
2. Referents: checked.
3. Bytes: N/A.
4. Discriminating checks: float64 against exact arithmetic, and the zero residue.
5. Lemma sweep: the sign identity, tilt and selection, across all routes.
6. Right answer versus right reason: the "literal" and "small cost" claims withdrawn.
7. Tooling: there is no `python` on PATH. I used `D:\PMP-programs-for-sharawi\autonomous-quant-trader\.venv\Scripts\python.exe -B` from a temporary directory and deleted the script afterwards. No tests were run.
8. Exact arithmetic: `Fraction` where needed.
9. No repairs to other documents.
10. Self-descriptions re-checked: 14 consecutive findings; 14 review findings dispositioned.
11. Inherited: D11-1.
12. Every attribution to another record cites its lines.
13. §16: not applicable here; it governs the later lockbox_eval code (Constitution l.152).

**Could not determine:** the real coverage; n (it depends on the gap embargo); whether the lockbox has outages; the size of the raw-d versus ψ block gap; the design intent before 2026-09-08. No statistician has reviewed this.

**Remaining:** owner Q1–Q3; the R19-2 re-check of revision 2; D-12; the lockbox rows of D-20 (seed source, identity, generator, vectors); §16 review of lockbox_eval; the owner's signed §4 commit.

**Still unauthorized:** editing frozen files, activation, code, simulation, confirmation or lockbox access, promotion, deployment, trading.

**Not checked:** the gap between raw-d and ψ block lengths. The section 7 sealing default and the S_pre date are AI defaults for the re-check to test.
