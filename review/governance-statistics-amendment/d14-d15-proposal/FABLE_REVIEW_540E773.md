# Fable review of the D-14/D-15 proposal rev3 at `540e773` — SOUND WITH FIXES

Date: 2026-10-03. This is the Anthropic-family review for R19-2. It ran in parallel with the Sol review and without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_R3.md` (committed `540e773`), with `{{PREFIX}}` = `FN3`.
- Model metadata: the reviewer reports `claude-fable-5-1` from its session metadata.
  The recorder observed the `fable` override but could not check the ID
  independently.
- The reviewer's final report follows verbatim, copied from its hand-back message (indentation removed).

---

claude-fable-5-1

**Reviewer:** Claude Fable 5.1, Anthropic Claude family (session metadata `claude-fable-5-1`); an AI reviewer, not an authority. This is the Anthropic-family review for R19-2.
**Commit reviewed:** `540e773` (branch `docs/d19-recommendation`), target `review/governance-statistics-amendment/d14-d15-proposal/PROPOSAL.md` revision 3; the working tree was clean.
**Verdict: SOUND WITH FIXES.** The core of the revision-3 null — shift the declared signal, size each draw with the trial's own estimator at the real hour — removes the revision-1 and revision-2 misalignment for signals that do not depend on volatility (exact, C1). Four BLOCKERs (FN3-1..FN3-4) must still be fixed before any owner question; each fix is bounded (a sentence, a disclosure, or an added owner option), and none needs a redesign. The changed sections should be re-reviewed. Skill terms: `REVISION_REQUIRED`; D-14 and D-15 stay `KEEP_BLOCKED`.

No other revision-3 review was read; nothing was edited, committed or pushed; no confirmation or lockbox data was read. All calculations ran in memory with `.venv/Scripts/python.exe -B -` using `fractions.Fraction`; no files were written.

## Independent calculations (exact)

- **C1, alignment under rev3, discriminating against rev2.** Idealized engine (no bands, no minimum hold, no initial state; clipping included). For each of the 8 rotations of the market path (σ, σ̂, z), the number of the 7 shifts strictly below the candidate:
  - trend trial at τ=0.40 where the benchmark clips (σ̂ includes 1/2): rev3 `[0,7,4,1,6,2,5,3]`, an exact permutation of 0..7 with mean 7/2; rev2 `[0,7,2,0,6,2,5,2]`, mean 3;
  - vol-family trial whose own estimator is 2 days stale while the benchmark's is 1 day stale, τ=0.80, s∈{1,1/2}: rev3 `[0,7,2,1,6,3,4,5]`, again a permutation; rev2 mean 3/2.
  - Proof: Sharpe is unchanged by a joint circular rotation, so Sharpe(rot_k s, M) = Sharpe(s, rot_−k M); when s does not depend on the market, the candidate's rank is uniform across rotations. With bands, minimum hold, starting state and the wrap, this identity is approximate only.
- **C2, variance timing passes through the signal.** σ=(1,2,4,8,8,4,2,1), the sizing estimator is 2 days stale, s_d = 1/2 if σ_{d−1}>σ_{d−2} else 1 (causal), τ=1/10 (no clipping), and every day has the same standardized hourly pattern (2,0), so there is no directional information at all. Candidate mean²/var = 289/583; draws 289/583 (tie), 1681/4831, 9409/28879, 338/953, 338/953, 9409/28879, 1681/4831 → **6 of 7 strictly below, 1 tie.**
- **C3, type-7 with ties:** the type-7 0.95 quantile of 500 equal values is that value; the candidate is ≥ it, so the gate **passes**.
- **C4, the clock under execution stress:** baseline — the increase fills at 00:00 and the next 00:00 is 24 h later; stressed — it fills at 01:00, the next 00:00 is **23 h** later, so the increase is blocked; two days later the gap is 47 h, which is allowed.
- **C5, age of a daily feature under the lag:** with emission at 00:00 the age is at most **24 h** (reached at t=24n), not 25 h.
- **C6, pass-rule arithmetic:** under exchangeability P(≥476 of 500 below) = 25/501; the set {m..T−m} has T−2m+1 elements, so 500 draws without replacement are possible iff T−2m ≥ 499. Both match the proposal.

## Findings

| ID | Sev | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| FN3-1 | BLOCKER | §2.1 step 2 ("clock set only when a risk increase is actually filled") | **Revision 3 brings back FN1-7.** Under execution stress a 00:00 increase fills at 01:00, so the next day's 00:00 is 23 h later and is blocked. The stressed run (and the benchmark under option (i)) can then increase risk at most every other day, so G-7 becomes a test of a roughly 48 h hold, not of a one-bar delay. | C4. FN1-7 (`FABLE_REVIEW_0F16E97.md` l.41) raised exactly this; rev2 fixed it with a decision-time clock, which FN2 verified (`FABLE_REVIEW_C872066.md` l.50). Rev3 then followed SN2-5's preference for an actual-fill clock (`SOL_REVIEW_C872066.md` l.26) and FN2-2's "executed increases only" (l.37) without re-checking FN1-7. The rev2 reviewers' advice — my model family's included — was ambiguous on time versus eligibility. | Make the clock anchor an owner question with the consequence stated: (a) fill time, giving the 23 h block; (b) the decision time of an increase that was later filled — cancelled orders never count; (c) amend l.57. State that "24 h have passed" means ≥ 24 h. |
| FN3-2 | BLOCKER | §2.1 steps 1–5 | **There is no step in which the baseline fill can happen.** A decision at close(t) fills at open(t+1), the same instant; step 1 at that instant has already run, so read literally the fill drops to the next timestamp "at that bar's open", and the baseline becomes the stressed run. "Fills come first … can never cancel a due daily increase" holds only if timestamps are instants (close(t)=open(t+1)); if timestamps index bars, the FN2-2 replacement problem returns. | BACKTESTER_SPEC l.6; COST_MODEL l.6–7, l.40 | Define timestamps as instants. Add a step: "in the baseline the order created in step 4 fills at this same instant at open(t+1)". Note that under the instant reading the step-4 replacement rule is never used. |
| FN3-3 | BLOCKER | §1.2 declaration requirement labelled "[AI default]" | **The form excludes, without saying so, hypotheses the frozen text allows:** (i) hourly signals — l.55 `hourly_signal_evaluation: true` and §8 (l.97) "bar+decision frequency" allow intraday signal-driven reductions, but s is daily only; (ii) rules that depend on the trial's own position or path (stops, take-profits, hysteresis), which shifting s does not reproduce. This includes the owner's recorded rule (`review/owner-input/TRADING_RULE_2026-09-27.md`: fixed 10%, −0.5% stop, +10% take-profit); whether that rule fits the frozen `vol_target` parameter point is a separate question I have not settled. The form also never requires s to be a function of market and model data only. | Read. This narrows §8 and l.55 by amendment, so "AI default" is the wrong label. | Allow an hourly s_h shifted by 24k hours (time of day kept); require s to depend on market and model data only; disclose the remaining exclusions as a separate owner question labelled amendment-required. |
| FN3-4 | BLOCKER | §1.2 "keeps the trial's own volatility alignment"; §1.1; Q2; C-2 | **This holds for σ̂ only; the shift breaks any volatility alignment that sits in s.** A vol-regime signal with no directional information beats its shifted copies (C2: 6 of 7 strictly below), meeting §1.1's own failure test ("a trial with no skill beats its own shifted copies"). Under the recommended option (a), the same economic content placed in σ̂ gives `N/A`, while placed in s it is tested and credited. Whether that is skill is a §12 (l.119) question, and it is not disclosed. | C2 exact; C1 shows the defect is limited to signals that depend on volatility. | Restrict the claim to σ̂; add to Q2 and C-2 that G-11 credits variance timing carried in s, and offer an option: credit it, or treat signals that depend only on volatility as pure sizing. |
| FN3-5 | NON-BLOCKING | §1.2 tie claims; §1.6 type-7; Q2/Q6 | **Lemma sweep:** "all 500 tie, the gate fails" and option (b) "always fail" hold only under the rank rules. Under type-7 a constant-signal trial or a benchmark clone **always passes** (C3). Under recommended option (a), the s≡1 trend clone in §1.2 would be `N/A`, not "fails". | C3 | Make Q6 depend on Q2 and disclose the type-7 consequence; correct the clone sentence. |
| FN3-6 | NON-BLOCKING | §1.2–1.5 | **Regressions from rev2:** g and T are no longer defined (rev2 l.99: gap_embargo.value_days and the window length in days); the statistic's window, its 1x cost and BTC-only scope were dropped; "a non-finite candidate or draw statistic makes the gate `UNAVAILABLE`; nothing is replaced" was dropped, and it matters more now that draws are seeded and random; `(d+k) mod T` uses 1-based days and produces index 0. | `git show c872066` l.95–103, 105–109, 127–131 | Restore all of these. |
| FN3-7 | NON-BLOCKING | §2.1 step 3 | **Uncited governing clause:** l.112 `rebalance_band_absolute: 0.10`. The contract applies the band to reductions at every hour but says nothing on 00:00 increases; without a band, a tiny increase is traded and also resets the clock. | protocol l.112; BACKTESTER l.10 | State the band rule for increases, citing l.112, or ask the owner. |
| FN3-8 | QUESTION | §2.1 "held exposure" | Does held exposure drift with price between fills? This affects the band test. The ambiguity comes from the frozen BACKTESTER_SPEC (l.1, 3, 8); it is not new. | Read | Bind it for the baseline engine and these gates. |
| FN3-9 | NON-BLOCKING | §2.2 daily aggregates; Q8 | **"Last emitted" turns G-6 into a one-day signal delay** at the 00:00 decision for any trial built on daily features. The "up to 25 h" is at most 24 h with emission at 00:00, and the emission time is undefined (C5). The alternative — recomputing with a 23:00 cutoff (FN2-12) — is not offered, and Q8 has no options. | C5 | Define the emission time and fix the number; offer both readings in Q8. |
| FN3-10 | NON-BLOCKING | §1.3 and §2.2 warm-up "permitted by R-9" | **Wrong referent:** R-9 governs only the P18-0(iii) gap embargo. The clause that bears on warm-up is `excluded_days_status` ("reachable only through the engine"). Whether engine warm-up may read the gap days is undecided; if not, estimator state at the window start is g days stale. | DRAFT_WORDING l.96, §2.1 | Cite the right clause and ask the question, or label it an AI default. |
| FN3-11 | NON-BLOCKING | §1.2 option (a) | The S4 draft's gate list has G-11 `na: "never"` (DRAFT_WORDING §3); option (a) needs that changed and the P18-7 frozen-`N/A` exception applied, as G-14 has. Neither is stated. | Read | Add both to C-3 and Q2. |
| FN3-12 | NON-BLOCKING | §2.3 G-5 row | The G-5 benchmark-leg question has no D-row (D-15 covers G-6/G-7; D-02 fixed only G-5's estimand, OWNER_DECISION_D01_D04 l.42–44). The ETH point-estimate cost under G-5 is not asked. | Read | Name the row the answer belongs to (an N-row or a D-02 follow-up); add the ETH point-estimate question. |
| FN3-13 | NON-BLOCKING | §3 | The G-6/G-7 counts omit the §2.3 option "ETH kept at baseline", under which no stressed ETH runs are needed. | Read | Add those counts. |
| FN3-14 | NON-BLOCKING | History l.16–18 (also `ADJUDICATION_C872066.md` l.9–10) | **Misattribution:** only SN2-1 suggested shifting the pre-sizing signal (SOL l.22); FN2-1's dispositions were the ratio null with disclosure, `N/A` or a different null, or keep blocked (FABLE l.36). | Read | Fix the proposal; the committed adjudication is the recorder's or owner's call. |
| FN3-15 | NON-BLOCKING (inherited) | §2.3 "Protocol l.42" | The `_at_1x_cost` value is on l.43; l.42 is the key. Carried over from FN2-3. | `cat -n` | Cite l.42–43. |

**Verified correct:** the frozen quotations at l.134–140, 289, 57, 60, 264, 266, 279–283 and Constitution l.97, 111, 119; 25/501 and "available iff T−2m ≥ 499"; N-2's ≥ 476; L-1 (under E-IMPROV, draws rank exactly by the trial's own Sharpe); a circular shift preserves time-in-market for binary s; G-5 keeps the ETH drawdown at 1x as frozen; the G-11 total of 502 gross runs.

## Q1–Q3 in brief

1. Yes for signals that do not depend on volatility (C1, discriminating against rev2); no for signals that do (FN3-4). The declaration form cannot express everything the frozen text allows, and its label is wrong (FN3-3).
2. Options nearly complete; gaps are FN3-5, FN3-6, FN3-10.
3. §2.1 is not yet unambiguous (FN3-2, FN3-7), and its clock reading departs in effect from the frozen l.57 (FN3-1). §2.2 is executable but fixes a material choice without offering the alternative (FN3-9).

## Status of revision-2 findings (Q4)

| Finding | Status | Note |
|---|---|---|
| FN2-1 | RESOLVED | residual in FN3-4 |
| FN2-2 | PARTLY | FN3-1, FN3-2 |
| FN2-3 | RESOLVED | residual in FN3-12 |
| FN2-4 | RESOLVED | |
| FN2-5 | RESOLVED | |
| FN2-6 | RESOLVED | |
| FN2-7 | RESOLVED | |
| FN2-8 | RESOLVED | g and T undefined again (FN3-6) |
| FN2-9 | RESOLVED | |
| FN2-10 | RESOLVED | residual in FN3-13 |
| FN2-11 | PARTLY | Q7 and Q8 have no options (FN3-1, FN3-9) |
| FN2-12 | RESOLVED | residual in FN3-9 |
| FN2-13 | DEFERRED | owner's call |
| SN2-1 | RESOLVED | residual in FN3-4 |
| SN2-2 | RESOLVED | |
| SN2-3 | PARTLY | FN3-6, FN3-10; reason codes not enumerated; missing-bar behaviour not covered |
| SN2-4 | RESOLVED | |
| SN2-5 | PARTLY | FN3-1, FN3-2, FN3-7 |
| SN2-6 | RESOLVED | residual in FN3-9 |
| SN2-7 | RESOLVED | residual in FN3-12 |
| SN2-8 | RESOLVED | |
| SN2-9 | PARTLY | embedded choices not offered as questions |

## Protocol items applied

1. two-way citation search found the uncited l.112 and l.55, §8 l.97, the gate list's `na`, and `excluded_days_status`;
2. referent checks: R-9, l.42, the History attribution, g/T;
3. not applicable — the proposal records no hashes; line numbers rest on LF files (proposal `text eol=lf`; frozen files `-text`);
4. discriminating checks: C1 compares rev2 with rev3;
5. lemma sweep: the tie lemma against type-7 (FN3-5), and L-1 against §2.4;
6. right answer, wrong reason: the alignment claim (FN3-4);
7. no verifier applies, and all calculations ran;
8. exact arithmetic throughout;
9. every disposition is a proposal; nothing was repaired;
10. self-descriptions: FN3-14;
11. inheritance: FN3-1 (the rev2 reviews' advice), FN3-8 (BACKTESTER_SPEC), FN3-15 (FN2-3);
12. every attribution to another review cites a line;
13. Constitution §16 does not apply to this Markdown proposal; it governs the later null and delay code.

**Remaining owner/statistician decisions:** the clock anchor; the band on increases; whether variance timing carried in s is credited; the declaration scope (hourly or path-dependent rules); the daily-feature lag; the warm-up source; which row the G-5 question belongs to; plus Q1–Q10 as listed in the proposal.

**Unauthorized:** deciding D-14/D-15; matrix or frozen-file edits; null, delay or stream code; simulations; any confirmation or lockbox access; any cycle, promotion or trading. This review is not a human, statistician or §16 review.

## Plain-language summary

1. The new random-copies test is now built the right way for most strategies: it shifts only the strategy's own buy/hold signal and keeps its own risk sizing.
2. A strategy that only cuts risk when volatility rises can still beat its copies without predicting price. Whether that counts as skill has to be your choice.
3. As written, the delayed-order test would stop a strategy from adding risk on two days in a row — a much harsher test than "one hour late", and the earlier review had already flagged it.
4. The required strategy format quietly rules out hourly signals and stop-loss or take-profit rules, including your own recorded rule.
5. Keep both items blocked until these are fixed. No statistician has checked any of this.
