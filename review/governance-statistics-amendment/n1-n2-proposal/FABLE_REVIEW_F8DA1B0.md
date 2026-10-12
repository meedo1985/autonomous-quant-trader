# Fable review of the N-1/N-2 proposal rev1 at `f8da1b0` — SOUND WITH FIXES

Date: 2026-10-03. The Anthropic-family review for R19-2. It ran in parallel with the Sol review and without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_R1.md` (committed `f8da1b0`) with `{{PREFIX}}` = `FQ1`.
- Model metadata: the reviewer reports `claude-fable-5-1` from its session metadata.
  The recorder observed the `fable` override but could not check the ID
  independently.
- The reviewer's final report, copied verbatim from its hand-back message (indentation removed):

---

claude-fable-5-1

# FQ1 review — N-1/N-2 proposal, revision 1

**Reviewer:** Claude Fable 5.1 (Anthropic Claude family); model ID `claude-fable-5-1` from session metadata, not independently verified.
**Commit reviewed:** `f8da1b0`. During the review HEAD moved to `317a3fc` (other sessions committed `4e125c9` Sol SQ1 and `317a3fc`); `git diff f8da1b0 HEAD` is empty for PROPOSAL.md, src, protocols, docs, specs and review/task12. No other review of this proposal was read.
**Mode:** read-only — nothing edited, staged or committed; in-memory Python only; no confirmation or lockbox data; no network.
**Verdict:** **SOUND WITH FIXES** — two BLOCKERs (FQ1-1, FQ1-2), both with small wording fixes. Skill scale: `REVISION_REQUIRED`; promotion stays `KEEP_BLOCKED`.

## Independent calculations (exact `Fraction` work, plus the repo function run in memory)

1. **Lag at n = 1219:** `floor(4·(n/100)^(2/9)) ≥ k` ⇔ `n²·4⁹ ≥ k⁹·100²`. The term is 6 for 621 ≤ n ≤ 1240 and 7 at n = 1241. So at n = 1219, `L = max(h−1, 6) = 6` for h = 1, 3, 7 — **the proposal's claim is correct**. The check discriminates: rounding or `ceil` gives 7, as does exponent 1/4. The 1,219 figure (1247 − 28) is inherited from D-06/D-07 and verified.
2. **Identity:** for centred `e` and Bartlett weights, `n(L+1)·Ω = Σ_j (sum of e over the zero-padded window j..j+L)²` (verified exactly on a 40-point integer example). So `Ω ≥ 0`, with `Ω = 0` only when every `e = 0`; by Cauchy–Schwarz, `Ω ≤ (L+1)·γ0`, so **`ESS ≥ n/(L+1)` for every series**.
3. **G-12 cannot fail for n ≥ 840:** `n/(L+1) < 120` only for n ≤ 839, for all three horizons; at n = 1219 the bound is 1219/7 ≈ 174.14. A near-worst case (a ±1 square wave in 200-day blocks) gives ESS = 178.484; the exact calculation and the repo's `effective_sample_size` agree (`NEWEY_WEST`, lag 6). The zero-variance fallback gives `n/h` ≥ 174.14.
4. **Code probes** (`src/aqt/metrics/statistics.py:261–301`): `horizon_hours=48` is accepted (h = 2); a non-finite input **raises** `StatisticsError` rather than returning `UNAVAILABLE`; an all-zero series with n = 300, H = 168 gives `HORIZON_FALLBACK` = 42.857.

## Findings

| ID | Sev. | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| FQ1-1 | BLOCKER | §1 "Consequences" bullet 1; §4 Q1 | The proposal calls ESS > 120 a `UNVERIFIED` heuristic that holds "unless returns are strongly autocorrelated", and Q1 says the check "will almost always pass". At the C2 length the gate **cannot fail for any series**, and the owner would accept a check that does nothing in C2 without being told. | Calcs 2–3: `ESS ≥ n/(L+1)`; G-12 can fail only if n ≤ 839. The inertness comes from the fixed Task 12 bandwidth; a data-dependent bandwidth such as Andrews (1991) would not have this property (`UNVERIFIED_EXTERNAL_ASSUMPTION`). | Replace the heuristic with the proven bound. State in Q1: "in cycle 2 this check cannot fail; it can fail only for windows of 839 days or fewer." Tie it to D-19's `T_min`: if `T_min` ≥ 840, G-12 is always `PASS`. Keeping it as written is the owner's choice. |
| FQ1-2 | BLOCKER | §2 "Proposal N2" | The shuffle and IC cannot be computed deterministically. Unstated: (i) training/OOS row frequency — hourly bars, or 00:00 UTC daily decisions (l.54, l.209); (ii) the asset — presumably BTC, since the trial unit is BTC and ETH jointly (l.179); (iii) the **order of shuffle and purge** — shuffling before purge/embargo can move a test-overlapping label onto a retained training row, which leaks; (iv) a fixed parameter point, including any logistic sign objective (l.161); (v) the model's own RNG seed (e.g. LightGBM). | protocol l.54, 161, 179, 205–207, 209; proposal l.72–78 | Add: daily decision rows; BTC; purge and embargo first, then permute within the retained training rows; the same `parameter_point` with no retuning; model seeds derived per draw from the D-20 stream. |
| FQ1-3 | NON-BLOCKING | §2 Shuffle | Labels at H = 72 and 168 overlap (MA(h−1)), so they are **not exchangeable** under the null. An i.i.d. permutation then gives a null distribution that is too narrow for persistent features, so a no-skill model passes more often than 25/500 (`UNVERIFIED_EXTERNAL_ASSUMPTION` for the size of the effect: spurious regression with persistent regressors). D-14's own "Why shifts" argument — a shift preserves structure (d14-d15 PROPOSAL l.40–45) — applies here but was not carried across. | protocol l.104, 109; d14-d15 l.40–45 | Disclose; present a circular shift of labels within each window as an alternative; whether "shuffled" allows it is the owner's call. Q2 should not imply a 5% rate. |
| FQ1-4 | NON-BLOCKING | §3 | The D-19 problem is **real** but the list is incomplete. Annex B's matrix holds only E-DIFF differences (Annex B l.19–22), from which leg-based gates cannot be reconstructed: G-1, G-2, G-4 (E-IMPROV per D-07), G-5 (also needs a 2x-cost re-run plus ETH), and G-12 (the candidate leg). G-12 does have the deterministic route the section asks for: it is available whenever the series is valid with n ≥ 2, because the fallback covers constant series. | Annex A P18-7 l.151–158; the skill's identifiability invariant | Extend the list; record G-12's deterministic availability argument. |
| FQ1-5 | NON-BLOCKING | §1 bullet 2 | Right conclusion (an all-cash nominee takes the fallback and passes), but the reason is overstated. "Its other gates are unavailable anyway" is false: G-4 is a **FAIL** (D-07 counts a zero-variance block as not a win); G-9 and G-10 are computable (E-DIFF = −benchmark). Only G-1 and G-11 are `UNAVAILABLE`. | OWNER_DECISION_D06_D07 l.47; d14-d15 P14-4 | Correct the sentence. |
| FQ1-6 | NON-BLOCKING | §2 table, option (a) | (i) Decided P18-7 exempts only "frozen `N/A`" (Annex A l.154); the new N/A in option (a) stays out of `U_proc` only if the §4 text makes it frozen (draft l.265), otherwise (a) behaves like (c). (ii) N/A status must be fixed at preregistration from hypothesis fields (Constitution l.97), not judged after results. (iii) Asymmetry the owner should see: a hypothesis can avoid G-14 entirely by not fitting a model of the target. (iv) The l.249 precedent comes from an informative, non-gate item (draft l.224); frozen gate N/As are better precedents (G-8 l.264, G-10 l.235). | as cited | Add all four points. |
| FQ1-7 | NON-BLOCKING | §1, §2 citations | Uncited governing clauses: (a) Constitution §23 l.182 requires reports to state raw decisions, overlap factor and ESS with its method — N1's "Report" bullet omits raw decisions and the overlap factor; (b) Constitution §18 l.161 already requires the shuffled-label null as a backtester trust test, so the canary role of option (b) exists under every option; (c) "decisions equals days" is an interpretation of `raw_decisions` (l.244): hypotheses declare a decision frequency (Constitution l.97), and intraday reductions are permitted (l.55, 59). Checked and not applicable: Constitution l.106 ("raw count") governs trial counts, not decisions. | Constitution l.97, 161, 182; protocol l.54–61 | Cite these; label "decisions equals days" as an interpretation. |
| FQ1-8 | NON-BLOCKING | §1 "Fallback" | "Exactly the Task 12 convention" holds for the formula, but the code does not enforce the stated `UNAVAILABLE` routes: it accepts H = 48, raises on non-finite input, and does not check time. Separately, the `Ω ≤ 0` fallback is reachable only through rounding (calc 2). | calc 4; statistics.py l.262–266, 270 | The caller must enforce H ∈ {24, 72, 168} and valid days and map exceptions to `UNAVAILABLE`; note the `Ω` branch is a numerical guard only. |
| FQ1-9 | QUESTION | §1 header | Does N-1 also bind the CPCV switch at l.216? At n = 1219, ESS ∈ (174, 1219], so the ≥ 250 switch is **not** inert there. | calc 3 | Owner to decide, or defer to D-13. |
| FQ1-10 | NON-BLOCKING | §4 | Questions not neutral or complete. Q1 offers "keep blocked" without saying the amendment then cannot be signed (draft l.260–266). Q2 offers neither keep-blocked nor revise, and omits the 500-refit cost, the U_proc consequence of (c), the asymmetry in (a), and that the (b) canary is required anyway. Q1 should also state that it lifts decision packet R3 ("never compare with 120") and l.70. R19-2's Effect names only the DSR record (OWNER_STEP0 l.41–45), although the D-06/D-07 precedent did extend it to R4. | as cited | Revise both, with parallel option sets: accept / revise / keep blocked, each with its consequence. |
| FQ1-11 | NON-BLOCKING | §2 | (i) "The same count rule as D-14" depends on the undecided D-14 rev1; the matrix row for D-14 prefers a type-7 quantile (HUMAN_DECISION_MATRIX l.56). (ii) The citation "l.153" points at `models:`; the class list is l.154–155 and named `allowed_classes_cycle_1`, so its carry-over to C2 should be stated. (iii) A permutation keeps each training window's label mean, so intercept-only refits give identical null ICs — valid ties, handled conservatively by the strict rule. | as cited | Add a dependency note; fix the citation. |

**Answers.** Q1: a faithful adoption of Task 12, with correct L arithmetic; the consequence is misdescribed (FQ1-1) and the fallback routes depend on the caller (FQ1-8). Q2: option (a) is the correct literal reading of l.141–145 and l.289, and the alternatives are mostly fair; the definition is incomplete (FQ1-2, FQ1-3, FQ1-6). Q3: real but incomplete (FQ1-4). Q4: not accurate or complete (FQ1-1, FQ1-10).

**Protocol items run:** 1 (Constitution topic search → FQ1-7); 2 (every G-/D-/P18-/FA3-/line referent re-read — all resolve; FQ1-11 records one citation nit); 3/4 (no hashes in the target; eol LF, attribute-protected); 5 (D-14's shift lemma swept across N-2 → FQ1-3; "unavailable anyway" swept across the gates → FQ1-5); 6 (FQ1-5); 7 (no verifier exists, so the repo function was run directly); 8 (exact arithmetic throughout); 9 (proposals only, nothing repaired); 11 (1,219 inherited and verified); 13 (§16 does not apply; Markdown-only).

**No findings left unrecorded:** FQ1-1 to FQ1-11 are consecutive with no gaps.

**Remaining owner decisions:** whether to accept G-12 as inert in C2, and its relation to `T_min`; the shuffle scheme; N-2 option (a), (b) or (c); the CPCV binding (FQ1-9); whether R19-2 supersedes packet R3.

**Still unauthorized:** frozen edits, amendment authorship, matrix rows, calibration or simulation, governed trials, confirmation or lockbox access, promotion, deployment, trading. No AI review replaces the §16 different-model plus human review for later protected code.

## Plain-language summary for the owner

1. The "120 effective decisions" check uses a formula that, over cycle 2's roughly 1,219 days, mathematically cannot fail — the proposal says "almost always", but it is "always".
2. The shuffled-labels check is a reasonable reading of the rules for strategies that use a prediction model, but its recipe is missing details needed to run it the same way every time.
3. Shuffling overlapping weekly labels may make that check too easy to pass; a time-shift version is an alternative you should be shown.
4. The warning about the calibration (D-19) is right, and it covers even more checks than listed.
5. Your questions should be rewritten so that each option states its real consequence, including what "keep blocked" would mean.
