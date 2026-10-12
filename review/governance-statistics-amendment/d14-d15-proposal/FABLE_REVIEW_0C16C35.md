# Fable focused check of the D-14/D-15 proposal rev5 at `0c16c35` — NOT READY

Date: 2026-10-03. This is the Anthropic-family focused check for R19-2. It ran in parallel with the Sol check, without access to it.

- Invocation: Claude Code subagent `senior-statistical-governance` with model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_R5.md` (committed `2caf045`) with `{{PREFIX}}` = `FN5`.
- Model metadata: the reviewer reports `claude-fable-5-1` from its session metadata.
  The recorder observed the `fable` override but could not check the ID
  independently.
- The reviewer's final report follows, copied verbatim from its hand-back message (indentation removed).

---

claude-fable-5-1

**Reviewer:** Claude Fable 5.1 (Anthropic Claude family); session metadata reports `claude-fable-5-1`. An AI reviewer, not an authority.
**Commit reviewed:** `0c16c35`, `review/governance-statistics-amendment/d14-d15-proposal/PROPOSAL.md` (revision 5); HEAD `2caf045`, clean tree.
**Verdict: NOT READY.** One BLOCKER, FN5-1. Skill terms: `REVISION_REQUIRED`; D-14 and D-15 stay `KEEP_BLOCKED`.

**Scope.** The full revision-5 text (the 83fc993→0c16c35 diff rewrites most of it), checked against the revision-4 wording where needed; the FN4 and SN4 reviews and `ADJUDICATION_83FC993.md`. The frozen protocol, Constitution, CANONICAL_BENCHMARKS, FEATURE_FACTORY and BACKTESTER_SPEC files were opened only at the lines the proposal cites; `TRADING_RULE_2026-09-27.md` was read. The other reviewer's revision-5 review was not read; no network; no confirmation or lockbox data; nothing edited, committed or pushed. All calculations ran in memory with `.venv/Scripts/python.exe -B -` using `Fraction`.

## Independent exact calculations

- **E1, overlay escape:** s≡1 with an overlay — 0.10 entry at 00:00 when flat, a −0.5% stop, a +10% take-profit. The candidate's exposure changes over time, yet all 5 shifted draws are **identical** to the candidate: shifting a constant does nothing, and the overlay re-runs on the same price path from the same starting state.
- **E2, fixed 10% sizing written into s:** writing the rule as s=0.1·σ̂/τ, with σ̂ = 1/2 at the real hour and 1 at the shifted hour, gives a draw exposure of 1/5 against the candidate's 1/10 — each draw is mis-sized by the ratio σ̂_shift/σ̂_real.
- **E3, a direction flip:** a planned cut from held 3/5 to target 1/2 fills as a reduction when r=2/3 (held at fill = 1/2) but as an increase when r=13/20 (held at fill = 39/79). Across held levels with a 0.10 band, the flip needs a fall of roughly 33% or more within one hour.
- **E4, clock anchored at a 13:00 decision:** the next two 00:00 decisions come 11 h and 35 h later, so the 24 h test does bind.
- **E5, drift-trap boundary:** a 0.10 position has held ≥ 1/10 exactly when r ≥ 1 — r=199/200 gives 199/1999 (blocked); r=1 gives 1/10 (allowed).

## Findings

| ID | Sev | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| FN5-1 | BLOCKER | §1.2 l.57–62, Q1b(a) l.78, Q2(a) l.87, C-2 | **Timing can be moved into the overlay, which the null never shifts.** The overlay reads the run's own price path, which is the same for every draw. A trial can put all its timing in a "hysteresis" or stop overlay (e.g. exit when close < SMA) and declare s constant: its draws all equal the candidate (E1), so Q2(a) gives it `N/A`, or, if `N/A` is not granted, plus-one fails on the all-tie row. So Q1b(a)'s "no `N/A` route through overlays" is false, and so is Q2(a)'s "it then makes no timing claim at all". **The owner's rule is the clearest case:** its fixed 0.10 size cannot be written as s·τ/σ̂ with the restricted σ̂ unless volatility enters s, which mis-sizes the draws (E2), or the overlay rescales, which the proposal neither allows nor forbids. Without a separate entry signal, the rule gets either `N/A` or an automatic fail. | E1, E2. Lemma sweep of revision 5's closure of the σ̂ route (FN4-4) applied to the overlay layer. **Inherited in part:** my predecessor FN4-1 offered "`N/A` only when timing lives entirely in the overlay" (`FABLE_REVIEW_83FC993.md`, FN4-1 row); revision 5 dropped that qualifier and added the false claims. | Proposal for the owner, not applied here: (1) correct both claims; (2) offer options — (α) limit overlays to the run's own position and entry-relative P&L, so all market-data timing sits in s; (β) allow Q2(a) `N/A` only when s is constant **and** there is no overlay; (γ) accept the gap and disclose it; (3) state how the owner's rule maps onto the three layers, including whether an overlay may rescale size, and what G-11 then does for it; (4) define the "mechanical" testability check. |
| FN5-2 | NON-BLOCKING | §2.1 step 2 l.191, Q10a l.203–206, disclosure l.214–218 | Under Q10a "at fill", step 2's "qualifying increase" cannot be judged at decision time under execution stress. A planned intraday reduction can fill as an increase (E3) — a risk increase away from 00:00, which l.57 forbids — and it anchors the clock intraday, where the 24 h test does bind (E4), contradicting the "never binds" disclosure. Rare: it needs a fall of about 33% within one hour. | E3, E4 | Say that step 2 classifies at decision time and Q10a governs only the clock; qualify "never" in the disclosure. |
| FN5-3 | NON-BLOCKING | §2.2 l.222–231, §3 l.276 | **Model outputs are ambiguous:** the bullet says a daily model output is "one of its own periods old", but §3 says G-6 re-infers the model on lagged features (a one-bar delay); for a model declared to emit daily these give a 1-bar or a 24-bar delay. Separately, the rule turns frozen l.267 `feature_delay_stress_bars: 1` into "one emission period", without labelling it a reading. | Read against l.267 and FEATURE_FACTORY l.5, l.20 | Choose one treatment for model outputs, and label the departure from l.267 as a reading or an amendment. |
| FN5-4 | NON-BLOCKING | §2.2 l.223, l.232–233 | "The band inputs" are lagged, yet held exposure (valued at the current price) is "unchanged"; and it is not said whether an overlay's price triggers are lagged under G-6. "Band inputs" is inherited from revision 4 (l.216 "hourly band inputs"). | Read | List the market-data inputs of the band and the overlay explicitly. |
| FN5-5 | NON-BLOCKING | §2.1 Q20(iii) l.183, step 2 l.188–193 | The exit-to-0 exception appears only in the intraday bullet, not the 00:00 bullet. Option (iii) also amends BACKTESTER_SPEC l.10 and CANONICAL_BENCHMARKS l.12, which are not cited; C-3 cites only l.60. | Two-way citation search | Apply the exception to both bullets and cite all three frozen clauses in C-3. |
| FN5-6 | NON-BLOCKING | Q20(i) l.181 | "Can never be closed" overstates the trap: the position can be closed once it drifts back to 0.10 or above, exactly when r ≥ 1 (E5). The stop's exit is blocked whenever price is below entry. | E5 | Reword the consequence accordingly. |
| FN5-7 | NON-BLOCKING | §2.3 l.243–250 | Q13 now offers no alternative (revision 4 had (i) and (ii)). Q15(b) "ETH entirely at baseline" overrides the column header "BTC and ETH alike" under Q14(i). | Diff against revision 4 l.239 | Offer the other reading of `_at_1x_cost` as Q13's alternative, and note the Q15(b) override. |
| FN5-8 | NON-BLOCKING | §3 l.267, l.277–278 | Stressed benchmark legs are the same for every nominee in a cell, so multiplying "gross" per-nominee counts by the number of nominees overstates the work. | Read | Separate the shared benchmark runs from the per-nominee runs. |

## Q1 — status of revision-4 findings

FN4-1 PARTLY (FN5-1). FN4-2 RESOLVED (residuals FN5-5, FN5-6). FN4-3 RESOLVED (residual FN5-2). FN4-4 PARTLY — σ̂ route closed, overlay route open (FN5-1). FN4-5 RESOLVED. FN4-6 PARTLY (FN5-3). FN4-7 PARTLY (FN5-2). FN4-8 RESOLVED. FN4-9 RESOLVED (per-gate counts check out). FN4-10 RESOLVED (minor residual FN5-7). FN4-11 RESOLVED. FN4-12 RESOLVED (l.37–38). FN4-13 RESOLVED. FN4-14 RESOLVED (qualifiers checked against FN3 l.19 and SN3 l.43). SN4-1 RESOLVED. SN4-2 PARTLY (FN5-2). SN4-3 PARTLY (FN5-1). SN4-4 PARTLY (FN5-3). SN4-5 RESOLVED (Q19). SN4-6 RESOLVED. SN4-7 RESOLVED.

## Q2 — new defects

Overlay re-run: FN5-1. N-4 option (iii): FN5-5, FN5-6 (the recommendation itself is sound by E5). Q10a/Q10b split: FN5-2. Emission-schedule lag: FN5-3, FN5-4. §2.3 benchmark/ETH table: FN5-7 (candidate-only ETH stress can now be expressed). §3 counts: correct as stressed runs per gate (checked); only FN5-8.

## Q3 — readiness

NOT READY. The only blocker is FN5-1, which affects Q1, Q1b and Q2; every other finding can be fixed in the same edit.

## Protocol items applied

1–2: two-way citation search found the uncited BACKTESTER l.10 and CANONICAL l.12 (FN5-5) and the l.267 reading (FN5-3); referents checked — FN4 E1, the SN4 2/5→1/2 example (verified: 4/7), FN3-11. 3: not applicable (no hashes in this change; the proposal is LF, protected by `text eol=lf`). 4: E3 and E5 test both sides of each boundary. 5: lemma sweep (FN5-1). 6: I endorse the N-4(iii) recommendation and the Q10a reading, but not the "never binds" justification. 7: no verifier applies. 8: all arithmetic exact. 9: no repairs; every disposition is a proposal. 10: self-descriptions at l.18 and l.22–23 checked; both true. 11: inheritance noted in FN5-1 and FN5-4. 12: attributions carry line references. 13: Constitution §16 does not apply to this Markdown proposal; it governs the later engine, null and delay code.

**Remaining owner/statistician decisions:** the overlay boundary and how the owner's rule fits under G-11; whether Q2's `N/A` applies when an overlay is present; Q1–Q20.
**Unauthorized:** deciding D-14, D-15, N-3 or N-4; matrix or frozen-file edits; amendment wording; engine, null or delay code; simulations; confirmation or lockbox access; trading. This is not a human, statistician or §16 review.

## Plain-language summary

1. Most of the revision-4 fixes went in correctly, and the delay-test counts now add up.
2. One real gap remains: a strategy can put its buy/sell timing inside its "stop/take-profit" layer, and the random-copies test never shuffles that layer.
3. Your own 10% / stop / take-profit rule, with no separate entry signal, would either skip that test or fail it automatically. You should be told this before you choose.
4. The other items are wording fixes: rare order flips, daily model inputs, citations, and run counts.
5. Fix item 2, then run a short re-check. D-14 and D-15 stay blocked, and no statistician has reviewed any of this.
