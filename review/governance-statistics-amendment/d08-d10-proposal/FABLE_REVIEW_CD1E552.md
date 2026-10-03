# Fable review of the D-08..D-10 proposal rev1 at `cd1e552` — SOUND WITH FIXES

Date: 2026-10-03. The Anthropic-family review for R19-2. It ran in parallel with the Sol review and without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_R1.md` (committed `cd1e552`) with `{{PREFIX}}` = `FB8`.
- Model metadata: the reviewer reports `claude-fable-5-1` from its session metadata.
  The recorder observed the `fable` override but could not check the ID
  independently.
- The reviewer's final report, copied verbatim from its hand-back message (indentation removed):

---

claude-fable-5-1

# FB8 review — D-08..D-10 PBO proposal, revision 1

**Reviewer:** Claude Fable 5.1, Anthropic Claude family (`claude-fable-5-1` in session metadata). AI reviewer, not an authority; closes no D-row, accepts no method.
**Commit reviewed:** `cd1e552` (branch `docs/d19-recommendation`), target `review/governance-statistics-amendment/d08-d10-proposal/PROPOSAL.md`.
**Verdict:** **SOUND WITH FIXES.** The three recommendations (E-DIFF ranking; the per-half Sharpe rule with no block minimum; uniform averaging over ties) are correct. The owner question in §6 must not be asked as written (FB8-1).

## Answers to the four questions

1. **D-08.** E-DIFF is correct, and it is the only choice that leaves the frozen input unchanged: the stored matrix holds only differences, so it cannot give E-IMPROV (appendix §2). Lemma L-1 holds within each half and was swept over the other proposals; nothing else in this document ranks by E-IMPROV. The wording consequence (a §4 amendment of one clause, l.240) is stated correctly in §2 but missing from §6 (FB8-1). The reason "very selection that produced the nominee" is overstated (FB8-5).
2. **D-09.** "Defined Sharpe on every half" is correct and sufficient: every split is computable, and a block minimum is not needed for that. The conditional AI-default floor is unjustified and misplaced (FB8-3). `|J_f|` is the better reading but is an unflagged interpretation of a frozen clause (FB8-2).
3. **D-10.** The claim is correct, checked with exact arithmetic below. Duplicate columns do change `phi` itself, though, and the proposal leaves that out (FB8-4).
4. **§5–§6.** Mostly accurate. §6 is not neutral and leaves out material consequences (FB8-1, FB8-3, FB8-2).

## What I computed myself (exact `Fraction`, in memory, no files)

- **Toy PBO:** 4 blocks × 2 days, all 6 oriented 2/2 splits, midranks, `omega = r/(N+1)`, score 1/0.5/0. Trials A, B, C: `phi = 7/12` under both tie rules. Adding A′, an exact copy of A: `phi = 1/3` under both rules — this confirms the D-10 claim, and also shows that **adding a duplicate moved `phi` from 7/12 to 1/3**.
- **Discriminating check:** trial D = A with its IS blocks swapped and a different OOS half, so D ties A exactly on IS={0,1}. Lowest-id rule: `phi = 0` with D named first, `1/6` with A named first. Uniform average: `1/12` under either naming. So the two rules differ only when tied trials differ out of sample, as stated.
- **Appendix §4:** squared signed Sharpe values `S(c1)² = 243/4`, `S(c2)² = 507/3844`, `E-DIFF` keys `−3/3604` and `27/4` — the reversal is confirmed.
- **Day count:** `1247 − 28 = 1219 = 16·76 + 3`; halves 608–611 days, so "about 610" is right.

## Read, not computed

Protocol l.234–241, 288; Constitution l.12, 13, 67; D-18 rev 7 and its owner record; the D-01..D-04 record; `OWNER_DECISION_B.md`; Annex B §2.5; DRAFT_WORDING §3, l.61, l.290; `statistics.py` `_sharpe` (l.173–200). Line endings of both proposal files: `i/lf w/lf attr eol=lf`. No hashes are recorded, so protocol item 3 does not apply.

## Findings

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| FB8-1 | BLOCKER (for asking §6 as written) | §6; also §2 "It matches D-18" | The owner, who is not a statistician, is told that D-08 is already settled. | "as your D-18 decision already requires" overstates: D-18 rev 7 says "must" in §2 (l.187–188) but "if D-08 adopts E-DIFF" in O18-6 (l.436–437) — an inconsistency inside owner-decided D-18 text, not new here. D-08 is a separate row needing §4 authority (matrix l.45), and D-18 cannot close it. The question omits: (a) D-08 needs an owner-signed §4 wording amendment; (b) an unavailable PBO counts toward the 1% `U_proc` target (P18-7 l.329–331); (c) the conditional 10-day floor; (d) the enablement-count reading; (e) that option (b) exists and why it is rejected. The supporting line in the D-01..D-04 owner record (l.50–51, "PBO (l.240) stays E-DIFF", an accepted consequence) is not cited. | Rewrite: "D-18's text directs E-DIFF; D-08 is still your separate §4 choice", and list (a)–(e). The recommendation is unchanged. |
| FB8-2 | NON-BLOCKING | §3 "Enablement" | A family declares 19 trials and one is re-run, giving 20 counted trials (P18-1 l.251–253; Constitution l.13: counts when evaluation begins); or a later cycle has ≥ 20 lifetime trials but `|J_f|` < 20. | No D-row covers which count l.235 means (D-09, matrix l.46, is unit and minimum). Uncited: Constitution l.12 (family has current-cycle and lifetime accounting) and l.67 (lifetime counts persist; no pooling of matrices). The DRAFT_WORDING l.61 override limits lifetime counts only for the DSR score. Supporting authority, also uncited: B-2 (`OWNER_DECISION_B.md`). | I agree with `|J_f|` (the columns are declared current-cycle trials, and l.67 forbids pooling, so a lifetime count would switch PBO on with fewer than 20 columns). Label it an interpretation, cite these clauses, extend the l.61 wording to PBO enablement, and show it in §6. The owner decides whether it needs §4 wording. |
| FB8-3 | NON-BLOCKING | §3 AI default "10 days/block if `T_min` < 160" | An eligible window with `T_min` ≤ T < 160 in a family of ≥ 20 trials. | The threshold is new and underived. Because it applies after eligibility, every such case becomes a computed UNAVAILABLE = a `U_proc` event (Annex B §2.5 ordering), so those cells fail the 1% target for certain. The D-06 proposal (P6-5, l.55–58) instead sets its minimum so it never fires on an eligible window. My view that short windows push `phi` toward 0.5, so the gate tends to fail rather than pass, is a heuristic (`UNVERIFIED_EXTERNAL_ASSUMPTION`). | Either drop the floor and require D-19 to set `T_min` with this in mind, or move it into eligibility (`T_min` ≥ 160). Disclose the choice in §6. |
| FB8-4 | NON-BLOCKING | §4/§5 | A declared set contains exact duplicates or near-copies. | Exact toy: `phi` 7/12 → 1/3 when A is duplicated. D-18 allows duplicates (broadened `DESIGN.md` §2.7 "available"). The D-10 claim is true, but the text reads as if duplicates were harmless; they are a declaration-time lever on `phi`, like FB1-15 for the DSR. | Add a consequence C-5; include families with duplicates and near-duplicates in the D-19 PBO cells. No recommendation change. |
| FB8-5 | NON-BLOCKING | §2 second bullet | Right answer, overstated reason. | The nominee is chosen on the full window (P18-4); PBO applies the same ranking rule to half-length IS sets, and `phi` does not depend on which trial is the nominee. "Contradicts l.239" via L-1 is an interpretation; the decisive reasons are identifiability (appendix §2) and the DSR series (l.228–229). | Say "the same ranking rule as the nomination". I endorse the conclusion, not this reason. |
| FB8-6 | NON-BLOCKING | §3 definition | An implementation must choose things D-09 leaves unstated. | Window and series appear only in C-2. Not stated: the alignment rule (`METHOD_CANDIDATE.md` l.222–224); the Sharpe convention (ddof 1, `statistics.py` l.173–200); what an "exact tie" means in float64 (unlike P18-4 l.293–296). The 1,219-day figure is unsourced here — it traces to the D-06 proposal l.59 and assumes the data-dependent embargo (protocol l.206–207) is ≤ 28 days. | State: the E-DIFF daily series of each declared trial on the eligible window, equal to Annex B's `X_j`; the reference float64 result decides ties; cite the source of 1,219. |
| FB8-7 | NON-BLOCKING | C-4; §4 last bullet; header | Wrong referents and authority. | The matrix gives D-09 authority as "`STAT` then `§4`" (l.46); C-4 drops the §4 part, while G-10 is OPEN in DRAFT_WORDING l.214, so all three rows end up in amendment text. The D-10 tension in the matrix is with "the DSR draft's own tie rule" (l.47; `DSR_METHOD_PREREGISTRATION_DRAFT.md` l.63), not D-18; it is the same rule in Annex A l.116, so the substance stands. FA3-12 supports "why now"; the `U_proc` inclusion comes from P18-7. | Correct the citations. No substantive change. |
| FB8-8 | NON-BLOCKING | §2–§4 | The predecessor draft is not engaged. | `DRAFT_AMENDMENT_PROPOSAL.md` l.124–132 said "candidate/common-comparison matrix", "rank by paired Sharpe improvement" (E-IMPROV in D-01 terms) and "20 current-family evaluated trials" — leaning toward option (b) and with different count wording. Never accepted, so this is inherited ambiguity, not authority. | Record the departure in one sentence. |

## Verification protocol items run

1 citations both directions (found the uncited clauses above: Constitution l.12, 13, 67; D-01..D-04 record l.50–51; O18-6; B-2; draft amendment l.124–132); 2 referents (FB8-7); 3 not applicable (no hashes); 4 discriminating reproduction (the tie-rule renaming check); 5 L-1 swept across all three proposals; 6 right answer vs right reason (FB8-5); 7 no verifier exists for this change, so none failed; 8 exact arithmetic throughout; 9 every disposition is a proposal; 10 self-descriptions accurate ("Three details are open", "12,870", "`K` ≤ 80", "about 610"); 11 the D-18 "must"/"if" inconsistency is inherited from owner-decided text; 12 no other review read or cited; 13 §16 does not apply to this Markdown proposal, but it does apply to later PBO gate code (promotion gate).

## Overall verdict

**REVISION_REQUIRED** for the proposal text; D-08 itself is **AMENDMENT_REQUIRED** (it changes the wording of l.240).

**Decisions left for the owner:** D-08..D-10 themselves; the enablement-count reading (FB8-2); keep, drop or move the floor (FB8-3); whether the enablement reading needs §4 wording. No human statistician has reviewed this (R19-2).

**Still not authorized:** frozen-file or matrix edits, activation, PBO code (protected under §16), calibration runs, confirmation or lockbox access, promotion, trading.

## Plain-language summary for the owner

1. Ranking strategies by the "difference" measure (E-DIFF) is right; it is the only option the stored data supports.
2. It still needs a one-line rulebook amendment that you sign. The draft question to you does not say so, and it wrongly suggests you have already decided this.
3. The tie rule is fine: for duplicate strategies both options give the same answer, which I checked by hand.
4. Duplicate strategies do change the overfitting score, so the list you declare can move it.
5. Two small rules (which trials count toward the 20, and a 10-day floor) need to be stated openly before you are asked.
