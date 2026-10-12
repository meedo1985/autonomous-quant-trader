# Fable review of the D-05 proposal rev1 at `e98adb3` — SOUND WITH FIXES

Date: 2026-10-03. The Anthropic-family review for R19-2. It ran in parallel with the Sol review and without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_R1.md` (committed `e98adb3`) with `{{PREFIX}}` = `FP1`.
- Model metadata: the reviewer reports `claude-fable-5-1` from its session metadata.
  The recorder observed the `fable` override but could not check the ID
  independently.
- The reviewer's final report, copied verbatim from its hand-back message (indentation removed):

---

claude-fable-5-1

**Reviewer:** Claude Fable 5.1 (Anthropic Claude family), model ID `claude-fable-5-1` from session metadata. AI reviewer with no authority; closes no D-row, accepts no method.
**Commit reviewed:** `e98adb3` (branch `docs/d19-recommendation`, clean tree); target `D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d05-proposal/PROPOSAL.md`.
**Verdict: SOUND WITH FIXES.** Option (a) "fail when `v <= 0`" is defensible, but the proposed wording mishandles a value that cannot be computed (FP1-1), two of the reasons are right answers argued by an overstated or wrong route (FP1-3, FP1-4), and the owner question is not neutral (FP1-8).

## Independent checks (computed vs read)

- **Computed exactly** (`.venv/Scripts/python.exe -B -`, `fractions.Fraction`, nothing written): worked example with `v = -2/5`, threshold `0.5·v = -1/5`: flat plateau `m = -2/5` fails as written and under (a); valley `m = -1/10` **passes as written**, fails under (a); isolated peak `m = -1` fails as written and under (a). So the frozen rule and (a) differ **only** on valleys, which also checks that the comparison discriminates. G-1 lower end: type-7 position for 2000 replicates = 1999/20, so j = 99, fraction 19/20; a lower endpoint above 0 needs at least 1900 of the 2000 replicates above 0. E-DIFF null sign: with `d` independent of `b` and `μ_b > 0`, `σ_c² = σ_b² + σ_d²`, and the population E-IMPROV `= μ_b(1/σ_c − 1/σ_b)` is negative for **every** trial.
- **Read and confirmed:** protocol l.260–265 (N/A at l.264); `statistics.py` l.591 (function start) and the stationary/circular index scheme l.535–551; D-04 = E-IMPROV (`OWNER_DECISION_D01_D04.md`); D-18 decided with the 1% `U_proc` target (`OWNER_DECISION_D18.md` l.13); P18-7 (`d18-proposal/PROPOSAL.md` l.320–359); G-8 still open (`DRAFT_WORDING.md` l.212) and preamble l.196–200 ("technically invalid" and "not computed" mean `UNAVAILABLE`); matrix row D-05; appendix §3.

## Findings

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| FP1-1 | BLOCKER | §3 wording ("otherwise `FAIL`"), §4 C-4 | The selected point's own E-IMPROV `v` cannot be computed (e.g. a zero-variance leg); read literally, the same applies when no neighbour value exists. | "PASS iff v > 0 AND … otherwise FAIL" turns unavailability into FAIL. That contradicts the gate-list preamble (DRAFT_WORDING l.196–200), P18-7 ("error control cannot pass on unavailability") and the proposal's own C-4, and it removes `U_proc` events, making the 1% target look easier than it is. C-4 covers neighbours only, never `v`. | Add to the wording: "if `v` is not finite, or no neighbour value is available: `UNAVAILABLE`"; name the case in §4. |
| FP1-2 | NON-BLOCKING | §3 wording, C-4 | `v <= 0` or the selected point is on a boundary, but the neighbours cannot be computed. | Whether the already-decidable FAIL wins over UNAVAILABLE is unstated, and the choice changes the `U_proc` count. | State the order explicitly, as an `[AI default]` or owner item; P18-7 means every gate is computed anyway. |
| FP1-3 | NON-BLOCKING (right answer, wrong reason) | §3 point 3 | "Under the global null … close to half of all nominees." | The share with `v <= 0` depends on the benchmark law and its co-movement with the difference series (which D-19 must now model, an accepted D-04 consequence) and on max-E-DIFF selection. With an independent difference and `μ_b > 0`, `P(v<=0) → 1` (computed). "About half" holds only with `μ_b = 0` and no selection; a de-risker null can make it small. The conclusion stands, because the 1% bound must hold in **every** qualifying cell. | Restate as "in plausible null cells, a large share of nominees"; drop "close to half". |
| FP1-4 | NON-BLOCKING | §3 points 2, 4 | "G-1 almost always fails when `v <= 0`." | (i) Needs G-1 and the plateau `v` computed on the **same** BTC OOS paired series; l.274–275 names no window, l.264 says only "BTC OOS". (ii) A lower endpoint above 0 needs ≥ 1900/2000 replicates above 0 while the point estimate is `<= 0`; for smooth statistics the bias is O(1/n) against a standard error of O(n^-1/2), so only small n or heavy tails (`UNVERIFIED_EXTERNAL_ASSUMPTION`, smooth-function bootstrap theory); the circular index scheme has no edge bias in the mean. (iii) G-1 may be `UNAVAILABLE` rather than FAIL (l.644–645). (iv) Self-application: point 2 applies equally to (a), (b)-N/A, (c) and (d). It does not favour (a) on promotion outcomes; it separates (a) only from (b)-UNAVAILABLE, and only via `U_proc`. Point 4's "cannot pass G-1 anyway" overstates point 2's "almost always". | State the same-series condition and the neutrality across options; "cannot" → "almost never". |
| FP1-5 | NON-BLOCKING | §1 `v < 0` | "The opposite of its purpose." | Computed: for `v < 0` the frozen rule still rejects isolated peaks and flat plateaus; its fault is that it passes valleys and fails plateaus. "Rewards a selected point that is worse than its neighbours" is accurate. `v > 0` and `v = 0` statements are correct (at `v = 0`: `m >= v`, zero tolerance). | Replace "the opposite of its purpose" with the precise statement. |
| FP1-6 | NON-BLOCKING | C-4 | A neighbour's E-IMPROV is not finite (e.g. a constant candidate leg). | Its E-DIFF stays finite (difference variance = benchmark variance), so `A_f` (P18-3) holds; C-4 then drops that neighbour and takes the median of the rest — a pass on partial evidence. l.261 "available +/-1-step neighbors" may mean "exists in the grid / EWMA subclass" rather than "has a finite value"; "This is not new; it is the frozen wording" states a reading as fact. | Mark it as an interpretation, and make it an explicit owner/statistician item. Out of D-05 scope but also unset: the median of an even number of neighbours, and whether neighbours are pooled across dimensions. |
| FP1-7 | NON-BLOCKING | C-2 | `v` very close to 0. | Sharpe is invariant to positive scaling, so a near-multiple of the benchmark has `v ≈ 0`, and in float64 the `v > 0` test can be decided by rounding. G-1 fails anyway, so promotion is unaffected; reproducibility is affected. | State that the reference implementation's float64 result decides (as in P18-4/P18-6). |
| FP1-8 | NON-BLOCKING | §5 | Owner question. | (b) gets a cost; (a) gets "[recommended]" and no cost (it changes the rule's meaning and needs §4 wording). Omitted: the N/A variant of (b), which is in the table; what (d) does; the effect of "keep it blocked" (G-8, and so promotion, stay blocked); that the choice rarely changes promotion and mainly matters for coherence and `U_proc`. "Invent" is a loaded word for (c). The R19-2 no-statistician disclosure is missing (the D-01..D-04 record listed it among accepted consequences). "Improvement" should say Sharpe-ratio improvement (E-IMPROV). | Rewrite neutrally, with one consequence per option. |
| FP1-9 | NON-BLOCKING | §3 point 2 | Citation `statistics.py:591–660`. | The file has 651 lines (working tree and HEAD). | 591–651. |
| FP1-10 | NON-BLOCKING (inherited from D-04, not a D-05 defect) | §3 point 1, §4 | Peak semantics. | The nominee is the E-DIFF peak, but G-8 measures the E-IMPROV surface, so even with `v > 0` the selected point need not be an E-IMPROV peak; the rule does not check the surface that selection searched. The D-04 accepted consequences do not state this. | Disclose in §4; any change is a D-04 matter for the owner, not an edit here. |

**Answers:** (1) Correct for all three signs; the `v < 0` description is slightly overstated (FP1-5). (2) Points 1 and 5 correct; point 2's conclusion plausible but conditional (FP1-4); point 3's conclusion right, reason wrong (FP1-3); point 4 overstated (FP1-4). (3) §4 correct but incomplete (FP1-1, -2, -6, -7, -10). (4) §5 accurate but not neutral or complete (FP1-8).

**Verification protocol items run:** 1 (topic search of the Constitution for unavailable/N/A/fail clauses: no uncited governing clause; l.79 "PASS/FAIL only" is lockbox-only and does not apply); 2 (referents P18-7, C-4, G-8, l.260–265, D-18, D-04 checked); 3 not applicable (no hashes); 4 (frozen rule vs (a) differ only on valleys); 5 (the "G-1 fails anyway" argument tested against every option → FP1-4); 6 (FP1-3, FP1-4, FP1-5); 7 (no tool failed); 8 (exact `Fraction`); 9 (every repair left as a proposal); 11 (§1 consistent with appendix §3 and matrix D-05; FP1-10 inherited); 12 not applicable (no other review read); 13 (C-1's §4 requirement applies; §16 does not apply to a Markdown-only change).

**Remaining owner decisions:** the D-05 option; FAIL-vs-UNAVAILABLE order (FP1-2); the meaning of "available neighbour" (FP1-6); acceptance of the FP1-10 disclosure.
**Not authorized:** activating or merging any wording; editing frozen files or the matrix; D-19 simulation or calibration build; confirmation or lockbox access; promotion; trading.

## Plain-language summary for the owner

1. The plateau check really does turn upside down when the chosen strategy is no better than the benchmark; "just fail it" is a sensible fix.
2. The proposed wording would also mark the check "failed" when a number cannot be calculated at all. That hides the "no result" cases your 1% limit is supposed to count, so it must be fixed first.
3. "About half of strategies would be affected" under the null is not supported; the true share could be much higher or lower. The conclusion still holds: calling them "unavailable" would break your 1% limit.
4. Whichever option you pick almost never changes whether a strategy is promoted, because another check (G-1) usually rejects it anyway; the choice is mostly about keeping the rules consistent.
5. The question you are asked should describe every option's downside fairly; as drafted it describes only the downside of the options it does not recommend.
