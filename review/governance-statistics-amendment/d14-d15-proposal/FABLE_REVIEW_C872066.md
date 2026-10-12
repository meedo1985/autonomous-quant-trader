# Fable review of the D-14/D-15 proposal rev2 at `c872066` — UNSOUND

Date: 2026-10-03. This is the Anthropic-family review for R19-2. It ran in parallel with the Sol review and without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_R2.md` (committed `c872066`) with `{{PREFIX}}` = `FN2`.
- Model metadata: the reviewer reports `claude-fable-5-1` from its session metadata.
  The recorder observed the `fable` override but could not check the ID
  independently.
- The reviewer's final report follows, copied verbatim from its hand-back message (indentation removed):

---

claude-fable-5-1

**Reviewer:** Claude Fable 5.1, Anthropic Claude family (session metadata `claude-fable-5-1`); an AI reviewer, not an authority. This is the Anthropic-family review for R19-2.
**Commit reviewed:** `c872066` (branch `docs/d19-recommendation`), target `review/governance-statistics-amendment/d14-d15-proposal/PROPOSAL.md` revision 2.
**Verdict: UNSOUND.** The ratio null fixes revision 1's defect only for candidates whose departures from the benchmark do not depend on volatility; for most of the volatility family the defect returns in a new form (FN2-1). D-15 alone would be SOUND WITH FIXES, but it has two blocking gaps (FN2-2, FN2-3). Skill verdict: `REVISION_REQUIRED`; both rows stay `KEEP_BLOCKED`.

No other revision-2 review was read; nothing was edited, committed or pushed; no confirmation or lockbox data was read.

## Independent calculations (exact, `fractions.Fraction`, in-memory `.venv` Python)

- **C1, the revision-1 case under the ratio null:** σ=[1,1,2,2]×2; the candidate holds 1/σ and the benchmark (3/5)/σ, so r is constant at 5/3; every draw equals the candidate, and the gate FAILS on ties. The ratio null does remove the FN1-1 defect for this case.
- **C2, the defect returns for the volatility family:** true σ constant; within-day returns z=[2,0]; benchmark sizing-error factor u=(1,2,3,1,2,3), candidate v=(1,1,2,2,3,3). Same multiset, so S(c)=S(b) exactly and the candidate's `E-IMPROV` = 0. A draw's risk exposure is u_j·v_{j+s}/u_{j+s}. ρ for the candidate is 6/7; for shifts 1–5 it is 1849/2877, 1681/2373, 6/7, 1849/2877, 1681/2373. Four draws are strictly below the candidate, one ties, none is above. The identity Sharpe² = ρ/(2−ρ) was checked exactly. A candidate with no information about returns and zero improvement therefore beats its own draws.
- **C3, mean exposure is not preserved even before clipping:** b=(1,1/2), r=(1/2,1): candidate mean exposure 1/2, swapped draw 5/8.
- **C4, the 1.5x tilt:** c=3/2, b=(1,1/2) gives r=(1,3/2), not constant. Since r ≤ 3/2 everywhere, every draw's target min(1, b_t·r_{t+s}) ≤ min(1, 1.5·b_t) = a_t, so every draw is pointwise no more exposed than the candidate.
- **C5, the §1.3 distinctness rule:** "distinct iff D=T−2m ≥ 499" checked for D=0..2999 with no violation. Discriminating: D=498 gives only 499 distinct values under both floor and ceiling variants. For T=1219, m=30: shifts 30..1189, minimum circular distance 30.
- **C6, pass-rule levels:** 25/501 ≈ 0.04990 and 26/501 ≈ 0.05190.

## Findings

| ID | Sev | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| FN2-1 | BLOCKER | §1.2 "What it keeps", "Both families" [AI default]; option B row | **"Keeps the benchmark's volatility alignment" is false whenever r depends on volatility.** For vol-family trials, r is the ratio of the two volatility estimates. Shifting r pairs the benchmark's sizing error with a mismatched copy of both errors, so the draws are penalised and a no-skill candidate passes. Only EWMA_168h at 0.60 (identical to the benchmark) gives r≡1; the other 14 of the 15 vol-family grid points (l.121–128) have a volatility-dependent r, through the estimator ratio or through clipping when τ≠0.60. The same clipping route applies to trend trials at τ≠0.60. | C2. Mechanism under an idealized model with independent z: the draw's log risk exposure carries about 2·Var log u + Var log v of noise, against Var log v for the candidate. Empirical strength for BTC is `UNVERIFIED_EXTERNAL_ASSUMPTION`. Adjudication brief item 1 required the vol-family question to be an **owner choice**; revision 2 made it an AI default and left it out of §5. Rejecting option B because it "always fails" a constant-signal vol trial is not neutral: Constitution §12 l.119 ("de-risking, not alpha") is relevant and uncited. | Owner/STAT choice for the vol family: (a) the ratio null with this inertness disclosed; (b) G-11 `N/A`, or a different null, for pure-sizing trials; (c) keep blocked. Present A and B symmetrically. Restrict the "keeps alignment" claim to r that does not depend on volatility. |
| FN2-2 | BLOCKER | §2.1 pending orders | **Under a one-bar delay, the fill for the decision at close(t) happens at open(t+2), the same instant as the next hourly decision at close(t+1).** The order of operations at that instant is unstated. If the decision comes first and "newer decision replaces pending" applies, the 01:00 evaluation (which cannot increase risk) replaces every pending 00:00 increase, and the stressed run never adds risk. The band rule's "current" (held or pending) is undefined, and so is whether a cancelled increase resets the 24-hour clock. | Fill time from l.6 / BACKTESTER_SPEC item 2 and COST_MODEL l.40; results range from "normal" to "never increases". | Fix the drafting: fill before the decision at the same instant; "current" = held exposure after the fill; only a decision that emits an order replaces a pending one; the clock counts executed increases only. Put this to the owner within a split Q4. |
| FN2-3 | BLOCKER | §2.3 "ETH legs are treated the same way as BTC legs"; §2.4 survival | **Uncited governing clauses:** l.42 and l.279 read `drawdown_constraint_holds_at_1x_cost`, and l.283 imports that rule into G-5. Option (i) applied to ETH under G-5 contradicts this frozen text unless declared an amendment, so the delay gates' ETH leg (stressed or 1x) is undecided. Separately, §10 l.111's "execution **baseline**" can be read as favouring (ii), so labelling (i) "follows §10" and (ii) "departs" is not neutral. | Read; line numbers checked (`-text` attribute, LF, keeps them stable). | Add the l.279 clause to the question; mark ETH under (i) for G-5 as amendment-required; present both readings of §10 neutrally. |
| FN2-4 | NON-BLOCKING | §1.2 "Match" | **The mismatch is attributed to "clipping, bands, minimum hold", and the frozen word "match" is reworded to suit.** In fact target mean exposure differs whenever r and b covary (C3). For the 1.5x tilt the owner was warned about (D-01..D-04 decision l.32), every draw is pointwise no more exposed than the candidate (C4), so "removes … time-in-market advantage" (l.138) is not delivered. The brief's alternative — realised matching within a tolerance — is not offered. The wording to amend is l.137, not l.136. | C3, C4. Sharpe is scale-invariant, so the practical effect works through dispersion and clipping (FN2-1) rather than the mean. | Correct the description; offer the tolerance option; fix the line reference. |
| FN2-5 | NON-BLOCKING | §1.2 edge cases | "The same holds for any … constant multiple" is false for c>1 when clipping binds, including the D-01..D-04 1.5x example. | C4: r=(1,3/2) | Restrict to c≤1, or to b ≤ 1/c everywhere. |
| FN2-6 | NON-BLOCKING | §1.4, Q2 | **Lemma L-1 (METHOD_CANDIDATE l.67–74) applies:** all draws and the candidate share one benchmark leg, so ranking by `E-IMPROV` equals ranking by the candidate's own Sharpe, and "versus VOL_TARGET_BUY_AND_HOLD" has no effect on G-11's outcome. `E-DIFF` would rank the departure P&L b(r−1)·ret, exactly the object the null shifts. Per I-12, L-1 is a ranking fact only; no substitution is implied. | Exact (L-1). Inherited: METHOD_CANDIDATE row 12 proposed `E-IMPROV` without this note, in a committed artifact; neither FN1 nor SN1 raised it. | Disclose in Q2, and state `E-DIFF`'s fit to the null object. |
| FN2-7 | NON-BLOCKING | §1.3, §1.5 | The deterministic, evenly spaced shifts and m=30 are AI defaults and absent from §5. They depart from the frozen names "random_exposure" and "samples" (l.135, l.139), the seed policy (l.266), and N-2's seeded random shifts (OWNER_DECISION_N1_N2 l.60–61). The 30-day floor is not based on persistence, and its power cost (FN1-14) is undisclosed. A deterministic subset excluding near-identity shifts is not a randomization group, so the 25/501 column needs a stronger caveat. | C5 confirms the formula itself is exact. | Add an owner question on the shift design; disclose the power cost and the level caveat. |
| FN2-8 | NON-BLOCKING | §1.3 | "N-1's `T >= 840`" names the wrong source: N-1 says G-12 can fail only for T ≤ 839, and T_min ≥ 840 is something D-19 *could* set (n1-n2 PROPOSAL l.66–67), not an established fact. | Read | Reword: availability holds if D-19 sets T_min ≥ 559. |
| FN2-9 | NON-BLOCKING | §2.4 | Bounded degradation is said to have "no frozen precedent", but the plateau rule l.264 uses "≥ 0.5 × selected-point value". | Read | Cite l.264 as a partial precedent. |
| FN2-10 | NON-BLOCKING | §3 | G-6 needs model re-inference on lagged features in every fold, not just a backtest; under (ii) the count is 4, not 8. Option (i)'s 2×2×2=8 is correct. | Read | Add both points to the inventory. |
| FN2-11 | NON-BLOCKING | §5 | Q4 bundles the execution and feature contracts and their AI defaults (decision-time clock, inference-only lag), against brief item 7. Missing: the vol-family question (FN2-1), the tolerance alternative (FN2-4), the shift design (FN2-7), the L-1 disclosure (FN2-6). The table omits that type-7 was the matrix's PROPOSED (a) (matrix l.56). | Read | Split Q4 and add the missing questions. |
| FN2-12 | QUESTION | §2.2 | For features built on daily aggregates, does "value computed one 1 h bar earlier" mean recomputing with a 23:00 cutoff, or taking the last value emitted, which may be about 25 hours old? | Read | State which. |
| FN2-13 | NON-BLOCKING (inherited) | `FABLE_REVIEW_0F16E97.md` FN1-1 | The committed FN1 record cites "Constitution §12 (l.115)"; l.115 is §11 text, and §12's sentence is at l.119. | `sed` check, LF | The record is committed; correcting it is the recorder's or owner's call. No edit made here. |

**Verified correct:** the §1.3 "iff" condition; the shift range and exclusion of the identity shift; the levels 25/501 and 26/501; the wrap point adds one discontinuity in r; a ratio that is identically constant fails on ties; b>0 whenever σ̂ is finite and positive; the §10 l.111 quotation; measuring the 24-hour clock from decisions removes FN1-7's blocking; N-2 is decided at ≥ 476; §1.6's "unavailable, no replacement".

## Revision-1 findings

| Finding | Status | Note |
|---|---|---|
| FN1-1 | PARTLY | fixed where r does not depend on volatility; returns for the vol family (FN2-1) |
| FN1-2 | RESOLVED | |
| FN1-3 | PARTLY | departure from the matrix's option (a) not disclosed (FN2-11) |
| FN1-4 | RESOLVED | |
| FN1-5 | PARTLY | FN2-3 |
| FN1-6 | RESOLVED | FN2-12 is a residual question |
| FN1-7 | RESOLVED | |
| FN1-8 | PARTLY | FN2-10; the analytic-availability option is not offered |
| FN1-9 | RESOLVED | |
| FN1-10 | RESOLVED | |
| FN1-11 | RESOLVED | FN2-6 is a new disclosure point |
| FN1-12 | RESOLVED | |
| FN1-13 | PARTLY | FN2-11 |
| FN1-14 | PARTLY | FN2-7 |
| SN1-1 | PARTLY | FN2-4 |
| SN1-2 | RESOLVED | |
| SN1-3 | RESOLVED | |
| SN1-4 | RESOLVED | |
| SN1-5 | PARTLY | FN2-2 |
| SN1-6 | RESOLVED | precedent claim wrong (FN2-9) |
| SN1-7 | RESOLVED | |
| SN1-8 | PARTLY | FN2-10 |
| SN1-9 | PARTLY | FN2-11 |

## Verification protocol items applied

1 (citations both ways): topic search found uncited l.42/l.279 (ETH at 1x cost), l.264 (the 0.5× rule), l.266 (seed policy), §12 l.119, L-1/I-12. 2 (referents): l.136→l.137, N-1's 840, the 1.5x tilt. 3 (bytes): not applicable — no hashes; line numbers rely on `i/lf w/lf attr/-text`. 4 (discriminating checks): C1 vs C2; C5. 5 (lemma sweep): L-1 against §1.4; the ρ-lemma against the ratio null. 6 (right answer, wrong reason): option B's rejection; the "match" attribution. 7 (tooling): no verifier applies; all calculations ran. 8 (exact arithmetic): throughout. 9 (no repair beyond authority): every disposition is a proposal. 10 (self-descriptions): history and N-2 claims true; FN2-8 is the exception. 11 (inheritance): FN2-6, FN2-13. 12 (other reviews): only the revision-1 records were read, as the prompt allows. 13: §16 does not apply to this Markdown proposal; it governs the later null and delay code.

## Remaining owner/STAT decisions

Vol-family treatment at G-11; "match" (reword vs tolerance); deterministic vs random shifts and the 30-day floor; `E-IMPROV` vs `E-DIFF` for G-11, once L-1 is disclosed; 476 vs 475; same-instant ordering under execution delay; benchmark and ETH stress (§10, l.279); survival vs bounded degradation.

**Unauthorized:** deciding D-14/D-15; matrix or frozen-file edits; null, delay or stream code; simulation; confirmation or lockbox access; any cycle, promotion or trading. This review is not a human, statistician or §16 review.

## Plain-language summary

1. Shifting the ratio to the benchmark fixes the old problem for trend-style strategies at the standard volatility target.
2. For most volatility-sizing strategies it does not: a strategy with no skill can still beat its own shifted copies, and choosing what to do here was supposed to be your decision.
3. The delayed-order rule can be read in a way that cancels every daily risk increase, so it needs one more sentence.
4. The rulebook says the ETH drawdown check uses normal (1x) costs, and the stress question ignores that.
5. Keep both rows blocked until these are fixed. No statistician has checked any of this.
