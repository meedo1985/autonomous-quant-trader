# Fable review of the D-06/D-07 proposal rev1 at `abcc2c9` — SOUND WITH FIXES

Date: 2026-10-03. The Anthropic-family review for R19-2. It ran in parallel with the Sol review and without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_R1.md` (committed `abcc2c9`) with `{{PREFIX}}` = `FF1`.
- Model metadata: the reviewer reports `claude-fable-5-1` from its session metadata.
  The recorder observed the `fable` override but could not check the ID
  independently.
- The reviewer's final report, copied verbatim from its hand-back message (indentation removed):

---

claude-fable-5-1

**Reviewer:** Claude Fable 5.1 (Anthropic Claude family), model ID `claude-fable-5-1` from session metadata (observed, not intended).
**Commit reviewed:** `abcc2c9` (branch `docs/d19-recommendation`), target `review/governance-statistics-amendment/d06-d07-proposal/PROPOSAL.md` revision 1.
**Verdict:** **SOUND WITH FIXES** (skill vocabulary: `REVISION_REQUIRED`). The definitions P6-1..P7-3 are faithful to the frozen terms; the consequences in §4 (C-1) and the owner question in §5 are not yet decision-ready.

Read-only: no other review of this proposal read; nothing edited, staged, committed or pushed; no network, confirmation or lockbox access.

## Checks run (protocol items)

- **1 Citations both directions:** every cited line resolves — protocol l.201–204, 280–282; §4 draft R-3, §2.1; P18-7 l.320–357; matrix rows D-06/D-07 (both `STAT`); Task 12 conventions l.11–23; `statistics.py` l.100–137, 173–200. Topic search of the frozen corpus found one uncited governing clause: Constitution §7a l.92 (FF1-4).
- **2 Referents:** R-3, P18-5, P18-7, FE1-5 point at the rows claimed.
- **3 Bytes:** no digests claimed; both files `i/lf w/lf attr/text eol=lf`.
- **4/8 Exact, discriminating:** block counts, binomial figures and the month rule computed exactly in memory (below).
- **5 Lemma sweep:** the l.204 "no denominator change" argument applied to every alternative (FF1-3).
- **11 Inheritance:** the wrong C-1 example is new (FE1-5 has no such example); the "D-19 must measure" framing in C-1 repeats a defect FE1-5 already corrected.

## Independent calculations (exact, in memory)

- **Window:** 2022-01-01..2025-05-31 inclusive = 1,247 days; with g = 28, 1,219 days (both match).
- **Block counts:** for every g in 0..29, exactly **13** complete blocks of 90–92 days; the final partial block runs from 61 days (g = 0) down to 32 days (g = 29). Calendar-quarter anchoring with g > 0 would give 12 complete blocks plus two partial blocks.
- **Month rule:** for C2, s falls between Jan 1 and Jan 30 and boundaries fall only in Jan/Apr/Jul/Oct, so the overflow rule **never fires in C2**. It still matters in general, because the alternatives differ: s = 2023-01-31 → proposal 2023-05-01, "clip to month end" 2023-04-30, chained addition gives 2023-08-01 for the next boundary instead of 07-31; s = 2022-11-30 → proposal 2023-03-01, clipping 2023-02-28.
- **No-edge pass rate** (independent blocks, win probability 1/2): at 13 blocks, 8 wins are needed, probability **595/2048 = 0.2905** (C-2's 29% is right). Not monotone in the number of blocks: 4 blocks 5/16, 5 blocks **1/2**, 12 blocks 397/2048.
- **Threshold:** 8/13 ≥ 3/5 true, 7/13 false; float `w/n >= 0.60` agrees with exact `5w >= 3n` for every n < 2000.
- **Code:** `statistics.py` l.120–123 rejects the whole series on any missing hour (`NONCONTIGUOUS_SEGMENTS`); l.179 returns `ZERO_VARIANCE` when every value in the series is identical.

## Findings

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| FF1-1 | BLOCKER | §4 C-1 | **Wrong example and understated risk.** (1) "Flat at a fixed exposure that tracks the benchmark exactly" does **not** give a zero-variance candidate leg — it still moves with BTC; an exact match gives E-IMPROV = 0, which P7-2 counts as an available non-win (it is the E-DIFF difference series that would have zero variance). (2) "Never trades" is not the trigger either: a never-trading candidate that holds BTC has variance. The real trigger is a block in which every daily return is identical — in practice, a full quarter 100% in cash. (3) For a long-only trend family, the 2022 bear market in the C2 window makes a cash quarter plausible rather than rare. One such block makes G-4 `UNAVAILABLE`; under P18-5 that leaves the family with no promotable trial, and it counts toward `U_proc` ≤ 0.01, which is a qualification condition (P18-7 l.327–334), not something D-19 merely "measures" — FE1-5 already corrected this framing. | `statistics.py:179`; P18-5; P18-7; FE1-5; §12 ("de-risking, not alpha"). Whether declared exposure mappings reach zero is not verified here. | Rewrite C-1: correct trigger, drop the wrong example, `U_proc` as a qualification target, and say the 2022 bear market can make cash blocks likely for trend nominees. |
| FF1-2 | BLOCKER | §5 | **Owner question incomplete.** Omits P7-2 (one cash block makes the check unavailable, and its cost), P6-5 (`B_min`), ties as non-wins, the "8 of 13" arithmetic, the ~29% no-edge pass rate (C-2), and the R19-2 no-statistician disclosure. The D-01..D-04 question listed its consequences; this one lists none. | `OWNER_DECISION_D01_D04.md` question 2 and "Accepted consequences" | Add these consequences in plain words; offer the FF1-3 alternative as an option; keep "Keep blocked". |
| FF1-3 | NON-BLOCKING (owner choice) | P7-2; prompt Q2 | **A fail-closed alternative to `UNAVAILABLE` exists.** (b) Count a block whose E-IMPROV is unavailable as a **non-win**: nothing is dropped, the denominator does not change (l.204), it can only make passing harder (so it never "passes on unavailability", P18-7 l.356), and it removes this route into `U_proc`. Cost: a quarter spent in cash during a crash scores as a loss, against the spirit of §12. (c) Define the Sharpe of an all-zero leg as 0: this changes the Task 12 convention (l.22–23 "no epsilon floor"), so it is a statistical change, not a definition. | §6 (governs data, not statistics); P18-7 | List (a) as proposed, (b) and (c) in §3/§5; the reviewer does not choose between them. |
| FF1-4 | NON-BLOCKING | §1, §2 | **Uncited consumer:** Constitution §7a l.92 "Sandbox receives only metrics.json, 3-month fold aggregates, and report.md from confirmation" — the block definition also fixes what the sandbox receives. In the proposal's favour: s is computed once before declaration (§2.1 `gap_embargo.rule`), so different trials' block boundaries cannot be offset and differenced to recover finer confirmation returns. | Constitution l.92 | Cite §7a; state that these blocks are the §7a aggregates and the partial block goes out only through metrics.json/report.md. |
| FF1-5 | NON-BLOCKING | §4 C-3 | **"No §4 needed" overstated.** P6-5 adds a minimum-block condition with an `UNAVAILABLE` consequence that l.280–282 lacks; its never-fires guarantee rests on `t_min_days`, which is §4 amendment text (draft l.111); s rests on R-3 and the amended `confirmation.start`; C-3 itself puts the G-4 text in the §4 draft. | §2.1, R-3 | Reword: P6-1..P6-4 and P7-1..P7-3 are definitions; P6-5 and the anchoring value are amendment text. |
| FF1-6 | NON-BLOCKING | P6-1 | **Cost multiplier unstated.** Task 12 requires both legs to share a multiplier but does not pick one; the 2x-cost rule (l.283) lists its own components and excludes the fold win rate. | protocol l.283; conventions l.12–13 | State "BTC, 1x cost". |
| FF1-7 | NON-BLOCKING | P6-3 | **Edge cases.** The text assumes a final partial block always exists — if the window end falls on a boundary there is none; window end 23:59:59Z should be stated as an exclusive 2025-06-01T00:00Z; a partial block shorter than 2 days gives `INSUFFICIENT_OBSERVATIONS`. In C2 a 32–61-day partial block always exists (verified). | calculations above | State all three cases. |
| FF1-8 | NON-BLOCKING | P6-2 month rule | **Prose could be misread.** The rule is a definitional choice the frozen text does not make, harmless for C2. "+ n months" prose could be read as chained addition, which gives different boundaries (example above); the formula `s + 3k months` is correct. "Gap at most 28 days" assumes the ACF cutoff is ≤ max_lag = 28 (FA1-7); at 29 days there are still 13 blocks. | calculations above | Add "computed from s, never chained". |
| FF1-9 | NON-BLOCKING | C-2 | **Correct but incomplete.** The no-edge pass rate is not monotone (1/2 at 5 blocks; 5/16 at the `B_min` = 4 floor); the `B_min` = 4 default ignores this. "Win half the time" needs per-block E-IMPROV to be symmetric about zero under the null — holds if the zero-mean legs are jointly sign-symmetric, but small-sample Sharpe bias and leg differences can shift it (`UNVERIFIED_EXTERNAL_ASSUMPTION`). | exact binomial above | Add both points; leave `B_min` to D-19. |
| FF1-10 | NON-BLOCKING | P6-4 | **Consistent with §6 and l.204 but redundant:** Task 12 already rejects the whole series on any missing hour (code l.120–123), which disables every paired gate, not only G-4. The calibration simulates no missing days, so P6-4 adds nothing to simulated `U_proc`; in operation its cause code (`U_ops` infrastructure vs `U_proc`, P18-7 l.345–349) is unassigned. Whether actual 2022–2025 Binance outages left missing hourly bars, and how the backtester represents §6 "outages untradeable", is `UNVERIFIED_EXTERNAL_ASSUMPTION`. | P18-7; §6 | Add this availability route to C-1; assign a cause code. |
| FF1-11 | NON-BLOCKING | §1 | **Not mapped to the D-06 row**, which asks for "anchoring, UTC completeness, and minimum days"; the proposal answers with minimum *blocks*. Calendar construction already gives 90–92 days per block (verified), so the row is covered, but the proposal never says so. | matrix l.38 | Map each of the three row items to its rule. |

## Answers to the four questions

1. **Faithful?** Yes. Anchoring at the window start is the better reading of l.202–204, for the reason given (only a final partial block expected). The month rule is a free choice, unambiguous and never firing in C2. P6-5 adds a condition (FF1-5).
2. **Consistent with §6 and `U_proc`?** On §6, both rules are consistent. On `U_proc`, P7-2 is expensive (FF1-1); the better fail-closed candidate is FF1-3 option (b), which is the owner's choice.
3. **Consequences correct and complete?** C-2's figure is exactly right; C-1 is wrong and understated (FF1-1); FF1-9 and FF1-10 are missing from §4.
4. **Owner question accurate, neutral and complete?** Neutral and accurate as far as it goes, but incomplete (FF1-2).

## Remaining decisions (owner, under R19-2)

The P7-2 rule (option (a) or (b), or keep blocked); `B_min` and `T_min` in D-19; acceptance that no human statistician reviewed this.

## Not authorized by this review

Deciding D-06/D-07; editing the proposal, the matrix, any frozen file or hash; any activation or amendment; calibration or simulation; confirmation or lockbox access; any trading or promotion. This review does not replace the owner's decision, or the §16 different-model and human PR review for later protected code.

## Plain-language summary for the owner

1. The way the 3-month blocks are drawn matches the rulebook; the C2 window gives exactly 13 blocks, so the strategy needs 8 wins.
2. One explanation in the proposal is wrong: the check breaks only when the strategy sits entirely in cash for a whole quarter, not when it copies the benchmark.
3. Sitting in cash through a crash quarter is exactly what a cautious strategy might do in 2022 — and under this proposal it would block the strategy.
4. A safer option exists: count such a quarter as a "loss" instead of "unavailable". It never makes passing easier, but it is harsh on cautious strategies.
5. The question to you should list these trade-offs, and the ~29% chance a strategy with no real edge passes this check, before you answer.
