# Fable focused check of the D-14/D-15 proposal rev6 at `4c8648f` — NOT READY

Date: 2026-10-03. This is the Anthropic-family focused check for R19-2. It ran in parallel with the Sol check and without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_R6.md` (committed `5d851d6`), with `{{PREFIX}}` = `FN6`.
- Model metadata: the reviewer reports `claude-fable-5-1` from its session metadata.
  The recorder observed the `fable` override but could not check the ID
  independently.
- The reviewer's final report follows verbatim, copied from its hand-back message with indentation removed.

---

claude-fable-5-1

**Reviewer:** Claude Fable 5.1, Anthropic Claude family (session metadata model ID `claude-fable-5-1`). An AI reviewer, not an authority.
**Commit reviewed:** `4c8648f`, `review/governance-statistics-amendment/d14-d15-proposal/PROPOSAL.md` (revision 6); HEAD `5d851d6`, clean tree.
**Verdict: NOT READY.** One BLOCKER, FN6-1. Skill terms: `REVISION_REQUIRED`; D-14 and D-15 stay `KEEP_BLOCKED`.

**Scope.** Read: the diff `0c16c35..4c8648f` of PROPOSAL.md plus the full rev6 text for context; `FABLE_REVIEW_0C16C35.md`, `SOL_REVIEW_0C16C35.md`, `ADJUDICATION_0C16C35.md`; frozen files only at the lines the changes cite (protocol l.42–43, 55–62, 111–128, 181–182, 266–268, 277–289; Constitution l.97, 111, 119; CANONICAL_BENCHMARKS l.8–12, 20–26; BACKTESTER_SPEC l.8–12; FEATURE_FACTORY l.5, 20); `review/owner-input/TRADING_RULE_2026-09-27.md`. The other reviewer's revision-6 review was not read; no network; no confirmation or lockbox data; nothing edited, committed or pushed.

## Independent exact calculations (`.venv/Scripts/python.exe -B -`, Fraction, in memory)

- **E1, the class boundary is a discontinuity.** Stylized, no band: 12 daily returns; an overlay exposure `b_d` (1/10, or flat the day after a loss) identical in every draw; on top, a micro-signal `ε·m_d` with `m_d = 1` if the previous day's return was positive; draws are cyclic shifts k=1..11. Sharpe compared exactly via the sign of the mean and mean²/var. ε=0: all 11 draws tie (fail). ε=1/100: the candidate beats draws {3, 11}. ε=10⁻⁶ and ε=10⁻¹²: it beats **the same** draws {3, 11}. A second return series gives 6/11 at both ε=1/100 and ε=10⁻¹². So the rank does not depend on ε as ε → 0⁺; it is set entirely by the micro-signal's timing, and the overlay's timing cancels out.
- **E2, the direction flip:** a cut from 3/5 to 1/2 fills as an increase exactly when r < 2/3, from 0.6r/(0.6r+0.4) < 1/2. Confirms l.243.
- **E3, the drift trap:** a 0.10 position has held 0.1r/(0.1r+0.9) ≥ 1/10 exactly when r ≥ 1. Confirms l.220.

## Q1 — revision-5 findings

FN5-1 **PARTLY** — the false claims are withdrawn and the classes are defined; still open: escape via a near-constant `s` (FN6-1), the "mechanical" constancy test is undefined, and whether an overlay may set the position size is unanswered (FN6-8). FN5-2 **RESOLVED** — eligibility at decision time, the clamp, E2 checks out; "never binds" under (b) is re-derived correctly. FN5-3 **RESOLVED** (wording residual FN6-6). FN5-4 **RESOLVED** (wording residual FN6-6). FN5-5 **RESOLVED**. FN5-6 **RESOLVED** (E3). FN5-7 **RESOLVED**. FN5-8 **RESOLVED** — the benchmark target is fixed at 0.60 (CANONICAL l.24), so its runs can be shared; residual FN6-5. SN5-1 **PARTLY** (FN6-1). SN5-2 **RESOLVED**. SN5-3 **RESOLVED** — the override is explicit; residual FN6-5.

## Findings

| ID | Sev | Location | Scenario | Evidence | Proposed disposition (proposal only) |
|---|---|---|---|---|---|
| FN6-1 | BLOCKER | l.76–82, Q2b(a) l.111, C-2 l.366–368 | A strategy whose timing sits in an overlay declares any non-constant market-derived `s`, however small; the class test marks it "signal-timed". G-11 then ranks only the timing of that tiny signal, and the overlay's market timing is common to the candidate and every draw. So "fail-closed … can never be promoted unless it declares a non-constant entry signal" is only nominally true. C-2's "cannot test timing that lives **only** in an overlay" implies overlay timing is tested otherwise; in fact it is never tested in any class. The owner's rule plus any tiny entry signal escapes Q2b(a). | E1 exact. A sweep of the FN5-1 lemma ("the null shifts only `s`") across the class boundary. Partly inherited: the conditioning on the overlay has existed since the overlay re-run was introduced; what is new is the fail-closed guarantee attached to the recommendation. | (1) Correct l.111 and C-2. (2) Owner options: (i) any market-reading overlay needs the Q2b(c) null; (ii) a materiality-based class test, which needs a definition; (iii) accept the gap and disclose it. (3) Define the "constant `s`" test — declared, or observed over the window. (4) Note that (α) (l.114) does not close this, because entry-relative P&L still reads the price, and that (α) belongs to Q1b, not Q2b. |
| FN6-2 | NON-BLOCKING | Q2(b) l.103, Q2b(a) l.111, §3 l.344 vs Q9 l.196 | "Fail" is justified by "all draws tie, so the rank rules fail", but Q9's type-7 option **passes** on all ties; under Q9 type-7, Q2b(a) silently becomes promotion without evidence. | l.196 | State "fail regardless of Q9", or make the dependence explicit. |
| FN6-3 | NON-BLOCKING | l.116–118, l.124 | The record specifies size, take-profit and stop, but says nothing about "entry when flat", and its own note says "A profit needs a real entry signal". With an entry signal, the rule is signal-timed (Q1b) and FN6-1 applies. | TRADING_RULE l.15–17, l.28 | Label "entry when flat, no signal" as a reading, and show both mappings. |
| FN6-4 | NON-BLOCKING | Q2(a) l.100–102 | "No timing exists to test" overstates: `σ̂` changes exposure over time. The right reason is that the null keeps `σ̂` aligned and so cannot test it, and §12 l.119 calls this de-risking. | l.119, l.66–67 | I endorse the recommendation, not the stated reason; reword. |
| FN6-5 | NON-BLOCKING | §3 l.345 | ETH G-5 per nominee shows "1" unconditionally, but under Q13(b) the whole ETH rule is at 1x, so it should be 0. The shared table (l.354) correctly makes its count depend on Q13(a). | l.314, l.345, l.354 | "1 under Q13(a), 0 under (b)". |
| FN6-6 | NON-BLOCKING | §2.2 l.276–289 | Three gaps: "The inputs are:" omits the direct market-data inputs of a signal not produced by the model; only the band-test target is said to be lagged, not the order target or the overlay output; "a daily model output carries only the one-bar lag" is false when the model's inputs are themselves coarse (l.291–292). | Read | Name the signal inputs and the order target; qualify the claim at l.289. |
| FN6-7 | NON-BLOCKING | Disclosure l.264–268, C-3 l.377–378 | Inherited from rev5: the 24 h clause that becomes inert also appears in BACKTESTER l.9 and CANONICAL l.11; only l.57 and l.113 are cited. | Two-way citation search | Add both citations. |
| FN6-8 | NON-BLOCKING | l.49, l.119–123 | FN5-1 item (3) asked whether the overlay may set or override the size, which would make a fixed 0.10 expressible. Rev6 leaves sizing to registration, so Q1 is answered without knowing whether the owner's rule can be expressed. | FN5-1 row | State whether the overlay output may change the size, or list it as an open question for Q1. |

## Q2 — new defects by area

Classes and Q2/Q2b: FN6-1, FN6-2, FN6-4. The owner's rule: FN6-3, FN6-8. Clamp and clock: no defect — the clamp is causal, has no effect on baseline runs (decision and fill share a price), and makes "only 00:00 increase orders set the clock" true; only residual FN6-7. §2.2 inputs and model outputs: FN6-6. §2.3 rows: consistent. §3 split: FN6-5.

## Q3 — readiness

**NOT READY.** FN6-1 alone blocks the owner questions (Q1b, Q2b, C-2). Every other finding can be fixed in the same edit.

## Protocol items applied

1 (citations both ways → FN6-7); 2 (referents: FN5 E1/E2/E3/E5, FN3-11 and the frozen line numbers point to the right rows; CANONICAL l.12 is a defensible citation for the exit amendment); 3 (no hash claims, so not applicable; PROPOSAL.md is `i/lf w/lf`, protected by `text eol=lf`); 4 (discriminating reproduction: ε=0 vs ε>0 in E1; both sides of the boundary tested in E2 and E3); 5 (lemma sweep: FN6-1, FN6-2); 6 (right answer, right reason: FN6-4); 7 (no verifier applies); 8 (all calculations with Fraction); 9 (no repairs); 10 (self-descriptions at l.1, l.18–20 and the adjudication table rows are true); 11 (inheritance noted in FN6-1, FN6-7); 12 (attributions by row); 13 (§16 not applicable to this Markdown file; it governs the later engine, null and delay code).

**Remaining owner/statistician decisions:** the treatment of overlay timing under a non-constant `s` (FN6-1); the Q2b–Q9 interaction; whether the overlay may set the size; Q1–Q20.
**Unauthorized:** deciding D-14, D-15, N-3 or N-4; frozen-file or matrix edits; amendment wording; engine, null or delay code; simulations; confirmation or lockbox access; trading. This is not a human, statistician or §16 review.

## Plain-language summary

1. The revision-5 fixes mostly went in correctly: the order-direction rule, the clock, the citations and the ETH table.
2. One real gap remains: a strategy that makes its decisions in its stop/take-profit layer can add a tiny, meaningless "signal" and be judged only on that signal.
3. So the promise that such strategies "can never be promoted" is not reliable — and the same applies to your own rule.
4. The other items are wording and count fixes, plus making sure the "fail" choice can't flip to "pass" under a different ranking rule.
5. Fix item 2 and do a short re-check. D-14 and D-15 stay blocked, and no statistician has reviewed this.
