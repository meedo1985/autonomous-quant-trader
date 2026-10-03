# Fable review of the D-02..D-04 proposal rev1 at `5e28376` — SOUND WITH FIXES

Date: 2026-10-03. The Anthropic-family review for R19-2. It ran in parallel with the Sol review and without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_R1.md` (committed `5e28376`) with `{{PREFIX}}` = `FE1`.
- Model metadata: the reviewer reports `claude-fable-5-1` from its session metadata.
  The recorder observed the `fable` override but could not check the ID
  independently.
- The reviewer's final report, copied verbatim from its hand-back message (indentation removed):

---

claude-fable-5-1

# FE1 review: D-02..D-04 estimand proposal, revision 1

- **Reviewer:** Claude Fable 5.1 (Anthropic Claude family); model ID from session metadata: `claude-fable-5-1`.
- **Commit reviewed:** `5e28376` (branch `docs/d19-recommendation`), target `review/governance-statistics-amendment/d02-d04-proposal/PROPOSAL.md`.
- **Verdict:** **SOUND WITH FIXES** (`statistical-binding-review` output contract: `REVISION_REQUIRED`). The `E-IMPROV` recommendation for D-02..D-04 is defensible and I endorse the conclusion; four reasoning and consequence texts must be fixed before the owner is asked (FE1-1, FE1-4, FE1-5, FE1-6).
- **Session conduct:** read-only; no other review of this proposal read; no edits, staging or commits.

## Checks run (mandatory protocol)

- **1 (citations both directions):** every protocol, appendix, matrix, D-18, s4 draft and `statistics.py` citation resolves. Topic search found uncited frozen clauses: l.85, l.137–140, l.221, l.229, l.239–240, l.247, and Constitution §1.
- **2 (referents):** checked O18-6, L-2, L-4, D-20, `statistics.py:325/591`, matrix D-03.
- **3 (byte characterization):** not applicable; the target records no digests.
- **4/8 (exact arithmetic, discriminating):** Fraction arithmetic in memory, no files: Example B reproduces exactly (S(b)²=1/12, S(c)²=243/4, S(d)²=3/3604 with negative sign → `E-IMPROV`>0, `E-DIFF`<0); it discriminates (computing `E-DIFF` from the legs would give a positive sign). Exposure-tilt identity: c=(3/2)·b → S(c)=S(b), S(d)=S(b)>0. Point-4 boundary 1972/1645 ≈ 1.1988 and the worked counterexample under FE1-3. Φ⁻¹(0.95)=1.64485 (float, descriptive only).
- **5 (lemma sweep):** the point-4 dominance lemma applied to G-8/D-05 (→ FE1-7) and to the `E-IMPROV` G-1 (→ FE1-4).
- **6 (right answer, right reason):** see points 4 and 5 below.
- **7:** no verifier exists for this artifact, so not applicable; Python ran successfully.
- **11 (inheritance):** FE1-6, FE1-13.
- **13:** §16 does not apply to a Markdown proposal; it still governs any later protected code.

## Answers to the four questions

**Q1 (§3).** Point 1 overstated (FE1-1). Point 2 cites one side only (FE1-2). Point 3 correct (`paired_sharpe_improvement_interval` :591, improvement influence :325). Point 4 right in direction, imprecise as stated (FE1-3). Point 5 literally correct — E_f = A_f ∩ {z_f* ≥ z_crit} contains no other gate, so no gate's estimand can change P₀(E_f) — but incomplete (FE1-4).

**Q2 (§4).** C-2, C-4 and C-5 contain errors or omissions (FE1-5, FE1-6, FE1-7); consequences are missing (FE1-8, FE1-10).

**Q3 (§5).** Mostly fair, with cost asymmetries (FE1-9); the strongest argument for the recommendation is omitted (FE1-8).

**Q4 (§6).** Neutral but incomplete (FE1-11).

## Findings

| ID | Sev. | Location | Scenario / evidence | Proposed disposition |
|---|---|---|---|---|
| FE1-1 | BLOCKER | §3 pt 1; §5 | "Changes no frozen word" and "`E-DIFF` reads against plain sense" are contradicted by frozen usage where only `E-DIFF` is computable: l.240 `ranking_metric: "paired_delta_sharpe"` on a "paired-difference return matrix"; l.85 "compute delta-Sharpe per path" on resampled difference paths. Decided D-18 (§2 l.187–188) already binds l.240 to `E-DIFF`. Adopting the proposal gives one frozen token, `paired_delta_sharpe`, two meanings — an undisclosed cost. Minor: l.275 reads `sharpe_delta`, not "delta-Sharpe". | Restate point 1 as "frozen usage is mixed"; disclose the token split in §4 and §6. The recommendation can stand. |
| FE1-2 | NON-BLOCKING | §3 pt 2 | §12 (l.119) is about the vol-managed system lagging buy-and-hold, and the comparison benchmark is already vol-targeted. The protocol states the opposite purpose three times: l.229 "incremental evidence rather than BTC beta", l.239 "same incremental objective as DSR", l.247 "incremental OOS evidence". §1, the actual purpose clause, is estimand-neutral. Only l.93–95 directly supports `E-IMPROV`. | Cite both sides; keep l.93–95 as the supporting clause. |
| FE1-3 | NON-BLOCKING | §3 pt 4 | Endorsed in direction, not in reason. With a common standard error and the normal approximation the implication is exact, not "nearly" (z_crit ≥ 1.645 and S0 ≥ 0 ⇒ S ≥ 1.645·sd); it already held under frozen v1.0 (Φ⁻¹(0.95) is the same critical value as a two-sided 90% interval); "K ≥ 2" is unnecessary. G-1 can still decide after a DSR pass: its standard error comes from its own block length and stream, while Annex B uses a family length (largest/median), which biases the variance down (FB1-1); and the interval is a percentile one, not normal. G-1 binds iff sd_G1/sd_DSR > (S0/sd_DSR + z_crit)/1.645 = 1972/1645 ≈ 1.199 at S0=0. Worked case: sd_DSR=0.05, S0=0.02, z_crit=1.972, sd_G1=0.075, S=0.12: DSR passes, G-1 fails. Redundancy costs information, not validity. | Reword point 4 as conditional on comparable standard errors; keep it `UNVERIFIED`. |
| FE1-4 | BLOCKER | §3 pt 5; C-1 | P₀ is computed under the all-zero-mean `E-DIFF` null (O18-1), which does not fix `E-IMPROV` (equal means, lower candidate volatility → `E-IMPROV` > 0). The `E-IMPROV` G-1 is computed after selection on a correlated statistic and has no coverage (D-18 §3 l.384–387: 81 null trials → 98.4%). So the `E-IMPROV` part of a promotion has no error control; C-1's "requires both kinds of edge" overstates it. Constitution §1: passing validation means only "failure to falsify". | Add: the 2.5%/5% bound covers only the `E-DIFF` claim; the `E-IMPROV` gates are uncalibrated filters. |
| FE1-5 | BLOCKER | C-2 | C-2 says "D-19 must report" availability; under P18-7 (l.327–335) it is a qualification target (≤1% whole-cycle `U_proc` bound, every gate computed for every nominee). Further: (a) Annex B §2.1 simulates only the T×K difference matrix X. Under `E-DIFF`, G-1 and G-8 read columns of X directly; under `E-IMPROV`, D-19 must also simulate a benchmark-leg law, an extra nuisance in the frozen qualification object. (b) Both families share the benchmark, so `U_proc` failures are correlated across families, which bears on the joint cells (l.353–355). (c) The Task 12 interval fails closed on one invalid replicate in 2000 (`statistics.py:644–645`), including a zero-variance candidate leg. | Correct C-2; state (a)–(c). |
| FE1-6 | BLOCKER | C-5 | "L-4 can use only `E-DIFF`" is false: L-4 is the ETH sanity rule on lockbox data, where both legs exist (the s4 draft lists it as `<<OPEN D-11, D-02>>`). L-2 is a point statistic on lockbox data; its tie to D-11 is a same-sentence coherence reading inherited from `METHOD_CANDIDATE.md` §6.3 item 7, not an identifiability limit. Only L-1's frozen reference distribution is limited to `E-DIFF`. The real incoherence is l.91, which uses "delta-Sharpe" twice in one rule. | Rewrite C-5; add L-4 to "Why now". |
| FE1-7 | NON-BLOCKING | C-4 | "Still" hides an asymmetry. Under `E-DIFF`, a DSR pass forces the plateau's selected value (the same BTC OOS series) above zero, so the D-05 inversion cannot affect a promotable nominee (it can still matter for `U_proc` if D-05 chooses (b)). Under `E-IMPROV` it is live. | Disclose as a cost of `E-IMPROV`. |
| FE1-8 | NON-BLOCKING | C-1; §5 | Omitted exposure-tilt case: c=k·b → `E-IMPROV`=0, `E-DIFF`=S(b)>0 (exact). The spot cap of 100% (§12) still leaves room whenever the vol-target benchmark runs below full exposure. `E-DIFF` nomination plus the DSR can favour such trials; the `E-IMPROV` gates (and G-11) filter them. This is the strongest argument for the recommendation, and a cost of "`E-DIFF` everywhere". | Add to C-1 and §5. |
| FE1-9 | NON-BLOCKING | §5 | Cost comparison asymmetric: both point estimators already exist in `paired_sharpe_statistics` (l.218–233), so D-02/D-04 discard nothing; both interval routes need D-20 review; an `E-DIFF` interval need not come from Annex B — the Task 12 machinery with single-series influence (l.311) would serve. | Make the comparison symmetric. |
| FE1-10 | NON-BLOCKING | §1; §6 | Consumer list incomplete: G-11 random-exposure null (l.137–140; the D-14 candidate also uses `E-IMPROV`), CPCV diagnostic (l.221, D-13), `oos_is_ratio` (l.247, frozen on `E-DIFF`), L-1, L-2, D-12. | List them as "not decided here". |
| FE1-11 | NON-BLOCKING | §6 | The owner question omits: the token split (FE1-1); the uncontrolled `E-IMPROV` claim (FE1-4); the added D-19 simulation scope (FE1-5); that G-8 stays blocked by D-05 and G-4 by D-06. | Add a short clause for each; owner wording is the owner's. |
| FE1-12 | NON-BLOCKING | §2 | "O18-6 requires D-08…" — O18-6 itself is conditional ("if D-08 adopts E-DIFF"); the requirement is in D-18 §2 l.187–188. | Fix the citation. |
| FE1-13 | NON-BLOCKING (inherited) | Matrix D-03 | The committed matrix cites `statistics.py:208–233` (point statistics) as the "inactive estimator"; the interval is at :591. The proposal cites it correctly. | Owner decides whether to correct the matrix; no AI edit. |

No finding is left without a disposition. I applied none; every repair is a proposal for the author and the owner.

## Remaining decisions and unauthorized acts

**Still for the owner (R19-2):** D-01..D-04 after both reviews and adjudication; then D-05, D-06/D-07, D-11, D-12, D-14, D-20.
**Still unauthorized:** frozen-file edits, activation of any binding, building or running the D-19 calibration, Task 13, confirmation or lockbox access, promotion, deployment, trading, any AI acceptance or merge.

## Plain-language summary for the owner

1. Recommending "Sharpe of candidate minus Sharpe of benchmark" (`E-IMPROV`) for these gates is reasonable, and this review supports it.
2. Some reasons are overstated: the frozen rules already use the same words for the other measure, so after this choice one phrase carries two meanings.
3. Your 5% false-promotion protection covers only the "adds return" measure (`E-DIFF`); the "better Sharpe" checks are useful filters but carry no guarantee of their own.
4. The proposal's lockbox consequence is wrong (L-4 can use either measure), and the extra simulation work this choice creates for D-19 is understated.
5. Fix these points, then ask the question. Nothing is activated either way.
