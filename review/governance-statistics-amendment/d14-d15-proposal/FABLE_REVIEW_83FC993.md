# Fable focused check of the D-14/D-15 proposal rev4 at `83fc993` — NOT READY

Date: 2026-10-03. This is the Anthropic-family focused check for R19-2. It ran in parallel with the Sol check and without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_R4.md` (committed `cb8102b`), with `{{PREFIX}}` = `FN4`.
- Model metadata: the reviewer reports `claude-fable-5-1` from its session metadata.
  The recorder observed the `fable` override but could not check the ID
  independently.
- The reviewer's final report, copied verbatim from its hand-back message with indentation removed, follows.

---

claude-fable-5-1

**Reviewer:** Claude Fable 5.1, Anthropic Claude family (session metadata `claude-fable-5-1`); an AI reviewer, not an authority. This is the Anthropic-family focused check for R19-2.
**Commit reviewed:** `83fc993`, file `review/governance-statistics-amendment/d14-d15-proposal/PROPOSAL.md` (revision 4). HEAD `cb8102b`, clean tree; the target has not changed since `83fc993`.
**Verdict: NOT READY.** Two BLOCKERs (FN4-1, FN4-2) must be fixed before the owner is asked; each needs only a disclosure plus an added option, not a redesign. Skill terms: `REVISION_REQUIRED`; D-14 and D-15 stay `KEEP_BLOCKED`.

Scope as instructed: the 540e773→83fc993 diff (the full rev-3 and rev-4 texts, because the diff output was truncated), the FN3 and SN3 reviews, and `ADJUDICATION_540E773.md`. Frozen and cited files were opened only at the lines the changed text cites. The other reviewer's rev-4 review was not read; the protected confirmation and lockbox data were not read; the network was not used; nothing was edited, committed or pushed. All calculations ran in memory with `.venv/Scripts/python.exe -B -` using `fractions.Fraction`.

## Independent exact calculations

- **E1 (price drift plus the band):** a 0.10 position with 0.90 in cash, price falls 0.5%. Held exposure becomes 199/1999 ≈ 0.09955, so |0 − held| < 0.10 and the exit is blocked. Under the no-drift reading held stays 1/10 and the exit is allowed. After a 0.5% rise held is ≈ 0.10045 and the exit is allowed. The two readings differ.
- **E2 (moving the signal into the estimator):** s=[1,1/4], τ=3/5, σ̂=[1/2,1] gives a=[1,3/20]; rewriting as s'≡1, σ̂'=σ̂/s=[1/2,4] gives the identical a=[1,3/20].
- **E3 (the clock):** hours since the anchor at each later 00:00 decision. Baseline, either anchor: (24, 48), so the 24 h test always passes. Stress with anchor (b): (24, 48), always passes. Stress with anchor (a): (23 blocked, 47 allowed).
- **E4 (shift count):** the deterministic formula gives 499 distinct shifts when T−2m=498 and 500 when T−2m=499, matching the proposal.
- **E5 (direction flip of a delayed order):** a reduction decided at held 0.60 to target 0.50 becomes an increase at fill only if the price ratio r < 2/3 — a fall of more than 33% within one hour.

## Findings

| ID | Sev | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| FN4-1 | BLOCKER | §1.2 applicability contract l.56–64; Q1b l.288 | **Under the recommended preregistered `N/A`, G-11 becomes optional.** Any directional trial can escape it by declaring a stop, take-profit or hysteresis that never fires. That turns the draft's G-11 `na: "never"` (DRAFT_WORDING l.215) into a declaration-time choice, and the proposal does not say so. **The stated reason for the exclusion is also contradicted by the contract itself:** path-dependent state is already re-simulated on every draw — held exposure drifts, the band applies, the clock runs, and every run starts at exposure 0 (§1.5 l.124–125, §2.1). A declared stop or take-profit overlay could be re-run on each draw's own path in the same way. | Lemma sweep of "depend on the trial's own path" (l.58–59) against §2.1. **Inherited:** the `N/A` route came from FN3-3 (`FABLE_REVIEW_540E773.md` l.41) and SN3-1 (`SOL_REVIEW_540E773.md` l.22); neither stated this consequence. | (1) State the opt-out consequence in Q1b. (2) Add an option: "re-run declared path-dependent overlays on each draw; `N/A` only when timing lives entirely in the overlay". (3) Keep the C2-restriction option, labelled as an amendment. |
| FN4-2 | BLOCKER | §2.1 l.178–179 (drift, AI default) with the band l.188–193 | **Under drift, a position held below 0.10 can never be closed, at any hour or at 00:00.** The owner's 0.10 position cannot be stopped out after a −0.5% move — exactly when the stop fires (E1). This reverses the reading in `TRADING_RULE_2026-09-27.md` l.36–38 ("A full exit from 0.10 meets that exactly"). The contract also governs **baseline** runs, so it changes C1 behaviour beyond the two gates. | E1, which discriminates drift from no-drift. **Partly inherited:** frozen l.60 already traps small positions after a reduction to a target in (0, 0.10), even without drift. FN3-8 (mine, l.46) asked for drift to be bound "for the baseline engine". | Disclose the consequence. Make drift an owner question with three options: (i) drift; (ii) measure the band against the last filled target; (iii) exempt exits to 0 from the band, which amends l.60. Label all of this a baseline-engine binding that goes beyond D-15. |
| FN4-3 | NON-BLOCKING | §2.1 Q10 l.202–211 | The 24 h test never binds in baseline runs under either anchor, nor under stress with the recommended (b) (E3). So (b) has the same effect as dropping l.57's 24 h clause for a one-bar delay; only stress with (a) is ever bound by it. Uncited: protocol l.113 `minimum_holding_hours_for_risk_increase: 24`, BACKTESTER_SPEC l.9, CANONICAL_BENCHMARKS l.11 ("minimum-hold"). Under (b) the time from one fill to the next is 24 h, but from a fill to the next decision 23 h. | E3; two-way citation search | Add the vacuity sentence and cite l.113 in Q10 and C-3. The recommendation can stand. |
| FN4-4 | NON-BLOCKING | §1.2 l.51 "its own declared sizing estimator" | Without a limit on σ̂, any trial can move its signal into σ̂ and declare s≡1 (E2), which gives it `N/A` under Q2(a). Frozen l.114–122 closes this route (EWMA_168h default; the vol family may choose only from the allowed set), but the contract does not cite it. Lemma sweep: l.98–99 rejects Q3(b) as "open to gaming", yet the recommended Q1b(a) and Q2(a) are also open to gaming (FN4-1). | E2; protocol l.114–122 | Restrict σ̂ to l.115 and l.121 and state its annualization (CANONICAL_BENCHMARKS l.23). Apply the gaming argument to every option, not only Q3(b). |
| FN4-5 | NON-BLOCKING | §2.1 l.188–190 band on increases | Constitution §8 l.97 makes "rebalance rule including band+min hold" a field each hypothesis declares. The AI default hard-codes 0.10 without citing l.97, or CANONICAL_BENCHMARKS l.10 and l.26, which support the band for the benchmark. | Uncited governing clause. **Inherited:** FN3-3 cited l.97 only for decision frequency. | Reword as "the trial's declared band (l.112 sets 0.10)" and cite l.97. |
| FN4-6 | NON-BLOCKING | §2.2 Q11 l.218–224 | FEATURE_FACTORY_v1 defines only trailing hourly-bar features (l.5, l.20) and no daily aggregates, so options (a) and (b) coincide for any feature the baseline emits every hour; they differ only through an emission schedule that is still undefined (as FN3-9 asked to fix). Option (a)'s "exactly as the baseline would compute it at t−1h" is undefined for a complete-day feature. | Read the frozen spec. **Inherited:** rev-3 l.178–179 and FN3-9's framing. | Define when features and model outputs are emitted; state that (a) and (b) differ only for features or model outputs emitted less often than hourly. |
| FN4-7 | NON-BLOCKING | §2.1 l.177 absolute target with drift and stress | A delayed order can change direction before it fills (a reduction can fill as an intraday increase, or the reverse), leaving l.57, l.60 and Q10(b)'s "increase that was later filled" undefined for such orders. It needs a move of more than 33% in an hour (E5), so the practical effect is small. | E5 | State whether an order is classified at decision or at fill. |
| FN4-8 | NON-BLOCKING | §2.1 steps 2 and 5 | A baseline fill happens in step 5, after step 2, so no step records the clock or held state for that fill. Harmless for the clock (FN4-3), but the order of steps is incomplete. | Read | Add "apply step 2 after a same-instant fill". |
| FN4-9 | NON-BLOCKING | §3 l.260, l.262 | The G-7 row ("4, or 2 … Add 0, 2 or 4 ETH runs") double-counts ETH — rev 3's 4 already meant 2 assets × 2 legs — and gives three values for a two-option Q15. The G-5 row ignores that Q12 and Q13 are now separate; the counts should be 4, 3, 3 or 2. | Compared with rev-3 l.222 | Use stressed runs only: BTC 2 or 1, plus ETH 0 or 2 (1 if the ETH benchmark follows Q14(ii)). |
| FN4-10 | NON-BLOCKING | §2.3 Q15 | Q15 bundles the ETH candidate, benchmark and drawdown, and does not follow Q14 the way Q17 follows Q16. Choosing Q14(ii) with Q15(i) gives inconsistent benchmark treatment between BTC and ETH. | Residual of SN3-6 | Use "benchmark as Q14" in Q15. |
| FN4-11 | NON-BLOCKING | §2.3 Q13 | Q13 assumes the ETH candidate's point estimate is at 2x, reading the suffix `_at_1x_cost` (l.43, l.279) as applying to the drawdown only. That is the more natural reading (otherwise there is no reason to specify 1x), but it remains a reading. | Residual of FN3-12 | Label it as a reading. |
| FN4-12 | NON-BLOCKING | ADJUDICATION_540E773 l.30; proposal l.17 | The adjudication says "the source of `g` and the floor `f` are a separate question (Q6)", but §1.1 l.35 fixes g = `gap_embargo.value_days`, and Q6 (l.139–140, l.293) asks only about f. So proposal l.17, "applies every disposition", is overstated. | Self-description check | Either add the g-source question or correct the adjudication record; the record is committed, so that is the recorder's call. |
| FN4-13 | NON-BLOCKING | §1.1 l.33 and §1.5 l.119 | T is defined as the number of "complete" UTC days, but any incomplete day already makes the gate unavailable, and h=0…24T−1 assumes contiguous days. "Task 12 conventions" was not checked (outside my reading scope). | Read | Define T as the number of UTC days in the window. |
| FN4-14 | NON-BLOCKING | History l.14–15 | "Both verified the core construction exactly" drops FN3's qualifier (l.19: "for signals that do not depend on volatility") and SN3's (l.43: "does not prove exchangeability"). L.75–76 restores only part of this. | Attribution check (item 12) | Restore both qualifiers. |

## Status of revision-3 findings (Q1)

- FN3-1 RESOLVED (residual FN4-3).
- FN3-2 RESOLVED (residual FN4-8).
- FN3-3 RESOLVED as requested (new consequence FN4-1).
- FN3-4 RESOLVED (lemma residual FN4-4).
- FN3-5 RESOLVED.
- FN3-6 RESOLVED (minor residual FN4-13).
- FN3-7 RESOLVED (residual FN4-5).
- FN3-8 RESOLVED as an AI default (its consequence is the blocker FN4-2).
- FN3-9 PARTLY: emission time still undefined (FN4-6).
- FN3-10 RESOLVED.
- FN3-11 RESOLVED (l.83, C-3).
- FN3-12 PARTLY: N-3 created; Q13's reading not labelled (FN4-11).
- FN3-13 PARTLY: arithmetic wrong (FN4-9).
- FN3-14 RESOLVED in the proposal; the committed C872066 record is left as is, and the correction is in ADJUDICATION_540E773 l.28.
- FN3-15 RESOLVED (l.233).
- SN3-1 RESOLVED (residual FN4-4).
- SN3-2 RESOLVED.
- SN3-3 RESOLVED (l.162–166).
- SN3-4 PARTLY (FN4-12).
- SN3-5 RESOLVED.
- SN3-6 PARTLY (FN4-10).
- SN3-7 RESOLVED.
- SN3-8 RESOLVED.

## Verified correct

Frozen quotations l.134–140, 289, 55, 127, 42–43, 279, 283, and Constitution l.119 and l.111; matrix l.56 (type-7 is PROPOSED (a)); DRAFT_WORDING l.115 `excluded_days_status` and l.215 (G-11 `na: "never"`); `statistics.py:173–200` (`_sharpe`: insufficient observations, non-finite, zero variance); the shifted-index formula keeps the time of day; the shift-count boundary holds (E4); the tie row for each pass rule; consistent Q numbering across §1–§5.

## Q3 — readiness

NOT READY. The only blockers are FN4-1 (Q1b, and Q2 through FN4-4) and FN4-2 (the AI default inside the D-15 contract). All other findings can be fixed in the same edit.

## Protocol items applied

1 (citations both directions: found the uncited l.113–122, §8 l.97, CANONICAL_BENCHMARKS l.10/11/23, BACKTESTER l.9, FEATURE_FACTORY l.5/20); 2 (referents: the adjudication's Q6 (FN4-12), Q-number mapping, matrix l.56, DRAFT l.215); 3 (bytes: not applicable, no hashes; line numbers rest on LF files — proposal `text eol=lf`, frozen `-text` with i/lf and w/lf); 4 (discriminating checks: E1 drift vs no-drift, E3 anchor (a) vs (b)); 5 (lemma sweeps: path-dependence (FN4-1), gaming (FN4-4)); 6 (right answer, wrong reason: the reason given for the `N/A` class (FN4-1); I endorse Q10(b) but ask for added disclosure (FN4-3)); 7 (tooling: no verifier applies; every calculation ran); 8 (arithmetic exact throughout); 9 (every disposition is a proposal; no repairs); 10 (self-descriptions: FN4-12, FN4-14); 11 (inheritance: FN4-1, FN4-2, FN4-5, FN4-6 noted as inherited, including from my own predecessor's advice FN3-3, FN3-8, FN3-9); 12 (every attribution to another review cites its line); 13 (Constitution §16 does not apply to this Markdown proposal; it governs the later null, delay and engine code).

**Remaining owner/statistician decisions:** the Q1b opt-out trade-off (or re-running overlays on each draw); the drift and band reading for exits; whether to accept that (b) makes the 24 h clause inert; the emission schedule; Q1–Q18 as listed.

**Unauthorized:** deciding D-14, D-15 or N-3; matrix or frozen-file edits, or amendment wording; engine, null, delay or stream code; simulations; confirmation or lockbox access; any cycle, promotion or trading. This is not a human, statistician or §16 review.

## Plain-language summary

1. The core random-copies test is still sound, and most of the earlier fixes went in correctly.
2. As now proposed, any strategy could skip that test simply by adding a stop rule that never fires. You should be told this before you choose.
3. A hidden default on how positions drift with price means a small position, like your own 10% trade, could not be sold after a small loss, so your −0.5% stop could never fire.
4. The 24-hour waiting rule turns out never to bind under the recommended reading. That is fine, but it should be stated.
5. Fix these two items first. Keep D-14 and D-15 blocked; no statistician has checked any of this.
