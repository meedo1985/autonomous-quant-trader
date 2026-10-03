# Fable check of the owner's D-14/D-15/N-3/N-4 answers (`e2a1a74`, rev7 `411e1af`) — INCONSISTENT

Date: 2026-10-03. The owner asked for this check ("let the agent check the
answers"). This is the Anthropic-family check under R19-2. It ran in parallel
with the Sol check and without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_DECISION_CHECK.md` (committed `5df9c93`) with `{{PREFIX}}` = `FC7`.
- Model metadata: the reviewer reports `claude-fable-5-1` from its session metadata.
  The recorder observed the `fable` override but could not check the ID
  independently.
- The recorder checked the FC7-1 premise directly: `OWNER_DECISION.md`
  l.16–17 reads "ETH remains at 1x. The proposed ETH 2x tightening is
  rejected. The frozen ETH 1x sanity rule is preserved."
- The reviewer's final report follows, copied verbatim from its hand-back
  message (indentation removed).

---

claude-fable-5-1

**Reviewer:** Claude Fable 5.1, Anthropic Claude family (model ID `claude-fable-5-1` from session metadata). An AI reviewer for R19-2, not an authority; not a human, statistician or §16 review.
**Commits checked:** `411e1af` (PROPOSAL rev 7) and `e2a1a74` (OWNER_DECISION_D14_D15.md) at HEAD `5df9c93`; clean tree. Read ADJUDICATION/FABLE/SOL_REVIEW_4C8648F.md and the frozen lines that rev 7 cites. For coherence, also read OWNER_DECISION.md (2026-09-15), OWNER_STEP0_DECISION.md, and the D01–D04, N1–N2, D18 and B owner records. The other reviewer's check was not read. No network, no confirmation or lockbox data, nothing edited.
**Verdict: INCONSISTENT.** One BLOCKER, FC7-1: the Q12/Q13 (N-3) answer reverses a standing owner decision that the owner was never shown.

## What I calculated (`.venv/Scripts/python.exe -B -`, Fraction)

- **Q20:** a 0.10 position after a −0.5% move holds 199/1999 ≈ 0.09955, below 0.10, so the band blocks the exit. The "about 9.95%" in the question is correct.
- **Q9:** for plus-one, the smallest number of draws strictly below that passes is 476: 25/501 ≤ 0.05, and 26/501 > 0.05.
- **G-11 availability:** with m = 30, T_min = 559 days.
- **The owner's rule:** σ̂ = (1/2, 4/5, 2/5, 1, 3/5, 7/10), τ = 3/5, s_h = (1/10)·σ̂_h/τ. The candidate's target is exactly 1/10 every hour. Draw k = 2 gives (2/25, 1/8, 3/20, 7/100, 1/12, 4/35), which is not constant. The wrong treatment, constant s, gives a vol-scaled target (1/10, 1/16, 1/8, …), which is not the owner's rule. This is the evidence for FC7-3.

## Findings

| ID | Sev | Location | Scenario | Evidence | Proposed disposition (proposal only) |
|---|---|---|---|---|---|
| FC7-1 | **BLOCKER** | Record l.78 (question), l.126–130 (Effect); PROPOSAL l.342 | Under N-3, Q13(a) puts the ETH candidate's point estimate (and the ETH benchmark) at 2x inside the G-5 stress. | `OWNER_DECISION.md` l.16–17 (2026-09-15): "ETH remains at 1x. The proposed ETH 2x tightening is rejected." The rejected proposal (`5f501c7` DRAFT l.152–155) was "2x stress reruns both candidate and comparison on both assets … ETH requires positive paired improvement and drawdown pass at 2x"; Q13(a) is that same tightening without the drawdown part. `DRAFT_AMENDMENT_PROPOSAL.md` l.155–159 still reads "Extending that stress gate to ETH was … rejected". `OWNER_STEP0_DECISION.md` l.41–45 says the 09-15 record **stands**. The owner was told only "ETH drawdown stays at 1x as frozen" — not that the ETH point estimate moves to 2x, and not that this reverses his own decision. The proposal never cites 09-15. FN4-11 (`FABLE_REVIEW_83FC993.md:45`) called (a) "the more natural reading" and SN5 (`SOL_REVIEW_0C16C35.md:34`) closed it, so both reviews missed this. Inherited from rev 3 onward. | Ask the owner again, explicitly: (a) set aside 09-15 item 3, or (b) keep ETH at 1x (= Q13(b)). Until he answers, treat the ETH part of N-3 as undecided. |
| FC7-2 | NON-BLOCKING | Record l.79–81; PROPOSAL l.344, 346, 357 | Q15(a) and Q17(a) also stress ETH under the delay gates. | Q18 says survival "mirror[s] l.283". The owner's 09-15 reading of l.283 keeps ETH sanity at 1x inside a stress gate (DRAFT l.150–156), which points to Q15(b) and Q17(b). The 09-15 decision speaks only about cost, so it does not bind these rows. | Put Q15 and Q17 to the owner again together with FC7-1. |
| FC7-3 | NON-BLOCKING | Record l.28–33 (Q2b), l.138–140; PROPOSAL l.136–143 | The owner was told: "your recorded rule … under (A) it skips this check". | "A fixed 10% is not expressible as s·τ/σ̂" is false: §1.2 allows s to be built from market data, Q3(a) credits a signal that depends on volatility, and s = 0.1·σ̂/τ gives exactly 0.10 (calculation above). That s is not constant, so declaring the rule `constant_signal` gives `CLASS_MISMATCH`; it must be declared `signal_timed`, and G-11 ranks it — comparing constant sizing against misaligned vol sizing, which has nothing to do with the stop or take-profit. "N/A" applies only to a vol-scaled variant, which is not his rule. More generally, whether G-11 applies depends on how a trial declares its parts, not on its exposure path (e.g. τ/σ̂_GARCH = τ·(σ̂_E168/σ̂_GARCH)/σ̂_E168). Inherited from rev 6 and accepted by SN6-1 (`SOL_REVIEW_4C8648F.md:40`) and FN6-8 (`:44`). The A/B choice is unchanged: (B) still blocks the rule, and (A) still allows it. | Correct the statement and the Effect. Add an owner/statistician question: may s depend on σ̂, and how should a fixed-size rule be classified? |
| FC7-4 | NON-BLOCKING | Record l.33–34; PROPOSAL l.115 | "Your 5% false-promotion limit … holds either way." | Right conclusion, overstated reason. E_f = A_f ∩ {z ≥ z_crit} (D-18 `9718fdc` l.320–321) excludes G-11, so marking G-11 N/A cannot change it. But the bound is a calibration target not yet reached: D-18's Effect calls it "conditional evidence", OWNER_DECISION.md l.13–15 keeps promotion blocked, and B-5 makes 5% the allowance for the first eligible cycle only. | Reword: "N/A does not change the DSR error event, and that bound is still conditional on the D-19 calibration." |
| FC7-5 | NON-BLOCKING | Record l.136–145 | The Effect lists as "accepted" consequences the verbatim questions never showed the owner. | Not shown in any question: that registering a fixed size is a separate, undecided question; that the 24 h clause becomes inert; the D-19 workload; that Q19 governs baseline runs (only N-4 was flagged as affecting all runs); that Q11's effect on daily inputs depends on phase (none at 12:00, one day at 00:00, PROPOSAL l.312); that Q13 is "a reading"; that Q2(b) "closes the vol family" (l.127). The untestability claim in Q2 also depends on the construction chosen in Q1, which was answered later. | Relabel these as "recorded in rev 7, not presented", or confirm them with the owner. |
| FC7-6 | NON-BLOCKING | Record l.116–118, l.141; PROPOSAL l.286–289 | Q10(b) "makes the 24 h clause inert". | In every baseline run, under either anchor, increase decisions and their fills both happen at 00:00, so the clause already never binds there; under (a) it binds only in the execution-delay run. Choosing (b) changes only G-7. Right conclusion, but the change is described as larger than it is. | Restate: "under (a) it binds only under execution delay; under (b) it binds nowhere." |
| FC7-7 | NON-BLOCKING | Record l.4–6 | "reviews of seven revisions" | Six revisions were reviewed (six FABLE and six SOL files); l.19–20 of the same record say rev 7 was not checked. | Correct in a later record, as the owner's act. |
| FC7-8 | NON-BLOCKING | Record l.10–11, l.76 | "By answering, the owner adds … these rows". | Q20 said "new row N-4"; for N-3 the question said only "(N-3)", which falls short of the N-1/N-2 precedent (N1_N2 record l.28–29). | Disclose when FC7-1 is put to the owner again. |
| FC7-9 | NON-BLOCKING | PROPOSAL l.214 vs l.96–98 | The Q9 table still says type-7 "passes" on all ties, but l.97 overrides that. | Presentation only; plus-one was chosen, so no effect. | Add "(overridden: FAIL)" to the table. |

## Q1–Q4

1. **Fidelity:** mostly faithful and neutral, except the Q12/Q13 summary (FC7-1), the claim about the owner's rule (FC7-3), and the "holds" wording (FC7-4).
2. **Record:** all 22 items take the rev-7 recommendation (verified: 4 in the first batch + 18 in the second). The Effect records more as "accepted" than the owner was shown (FC7-5), and records N-3's ETH 2x without noting that it supersedes 09-15 (FC7-1).
3. **Coherence:** consistent with D-01..D-04 (E-IMPROV filters with no error rate), N-2 (476 of 500), D-18 P18-7 (preregistered N/A outside U_proc; CLASS_MISMATCH counts as UNAVAILABLE), and B-5/B-7 (T_min). **Inconsistent with the 2026-09-15 ETH 1x decision.** N-4(iii), Q10(b) and the clamp do not conflict with each other.
4. **Revision 7:** resolves FN6-1..FN6-7, SN6-2..SN6-6 and FN6-8/SN6-1 as written; however, the FN6-8/SN6-1 resolution rests on a false premise (FC7-3). The only new defect is FC7-9, which is cosmetic.

**Protocol items run.** 1: topic search found 09-15 and COST_MODEL l.36–40 (consistent with Q14). 2: checked against the frozen text — protocol l.42–43, 53, 55, 57, 60–61, 112–127, 134–140, 266–267, 279, 283, 289; Constitution l.97, 111, 119; BACKTESTER l.9–10; CANONICAL l.10–12, 23, 26; FEATURE_FACTORY l.5, 20. 3: no hashes claimed; both files `i/lf w/lf eol=lf`. 4: the discriminating example above. 5: the "null shifts only s" lemma applied to the owner's rule → FC7-3. 6: FC7-4, FC7-6. 7: no verifier applies. 8: Fraction throughout. 9: no repairs. 10: FC7-7. 11: inheritance noted under FC7-1, FC7-3. 12: other reviews attributed by file and line. 13: §16 not applicable to Markdown; it governs the later engine and null code.

**Remaining owner decisions:** the ETH tightening in Q13 (and Q15/Q17); whether s may depend on σ̂ and how a fixed-size rule is classified; whether to confirm the FC7-5 consequences.
**Unauthorized:** changing any answer; matrix, frozen-file or §4 edits; engine, null or delay code; simulations; confirmation or lockbox access; promotion; trading.

## Summary for the owner

1. Most of your answers match revision 7 and fit with your earlier decisions.
2. One answer conflicts with your own 2026-09-15 decision: you rejected running the ETH check at 2x cost, the new N-3 brings it back, and the question did not tell you.
3. You were told your 10%/stop/take-profit rule would "skip" the random-timing check. Written as a fixed 10%, it would actually be tested — though on something unrelated to its stop or take-profit.
4. Several consequences listed as "accepted" were never shown to you in the questions.
5. Please re-answer Q13 (and probably Q15 and Q17) knowing about the 09-15 conflict. Everything stays blocked, and no statistician has reviewed this.
