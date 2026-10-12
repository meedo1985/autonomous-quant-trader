# Fable focused check of the §4 amendment draft rev3 at `fcc0cf2` — NOT READY

Date: 2026-10-03. The Anthropic-family focused check for R19-2. It ran in parallel with the Sol check and without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_R3.md` (committed `1aa523f`) with `{{PREFIX}}` = `FA3`.
- Model metadata: the reviewer reports `claude-fable-5-1` from its session metadata.
  The recorder observed the `fable` override but could not check the ID
  independently.
- The reviewer's final report, copied verbatim from its hand-back message (indentation removed):

---

claude-fable-5-1

# FA3 review: §4 amendment draft wording, revision 3

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family — model ID from session metadata, not chosen by me.
**Commit reviewed:** `fcc0cf2` (HEAD `1aa523f`, branch `docs/d19-recommendation`). Other reviewer's revision-3 review not read.
**Verdict:** **NOT READY** — three BLOCKERs (FA3-1..FA3-3), all in the new gate list, each with a small fix. Skill scale: `REVISION_REQUIRED`; promotion `KEEP_BLOCKED`.

## Verification

- **Computed:** annexes unchanged between `afed53e` and `fcc0cf2` (`git diff --quiet` succeeded; hashes not re-verified, per the prompt). `DRAFT_WORDING.md` EOL `i/lf w/lf attr/text eol=lf`. O-2 schedule: two lockbox reads 30 days apart plus 72 h cooling-off = 33 days, leaving 42 days of the 75-day window for gate computation; 180 + 75 = 255. O-6 seed effect (FA3-8).
- **Read only, not verified independently:** protocol v1.0 l.36–300; Constitution l.10–161; schema (permissive; only `cycle_termination` has required leaves); `HUMAN_DECISION_MATRIX.md` l.28–82; O18-5/O18-7 text (`9718fdc` PROPOSAL l.432–448); `SCIENTIFIC_DECISION_PACKET.md` R3, R6; `IMPLEMENTATION_CONVENTIONS.md` l.1–38; Annex A in full, Annex B §2.4 seed lines only.
- **Mandatory protocol:** 1 (citations audited both ways; topic search for line 289 and the nulls found the shuffled-labels gate metric → FA3-2; for ESS and drawdown found decision packet R3/R6 → FA3-1); 2 (every D-nn checked against the matrix — all correct; found FA3-5, FA3-6); 3/4 not applicable (annex bytes unchanged); 5 (lemma sweep: "no keep blocked" swept across every gate → FA3-1, FA3-2, FA3-10; "leaf shapes kept" swept across every leaf → FA3-4); 8 (exact arithmetic for the schedule); 10 (self-descriptions → FA3-4, FA3-6); 11 (FA3-11 inherited); 7 not applicable (no verifier exists for wording); 13 not triggered by Markdown.

## Q1 — revision-2 findings

| ID | Status | Reason |
|---|---|---|
| FA2-1 | RESOLVED | R-6 at precedence 2 puts P18-2(a) under the calendar limit; the value is DEFERRED to O-2 |
| FA2-2 | PARTLY | Gate list exists, but G-12 is wrongly marked defined (FA3-1), the shuffled-labels null is missing (FA3-2), the list has no frozen home (FA3-3), and lines 90–91 are not enumerated (FA3-9) |
| FA2-3 | RESOLVED | Option removed, with the reason in §4 |
| FA2-4 | RESOLVED | 77–79 and 83–92; lines 75, 76, 80–82, 294–296, 300 stay in force |
| FA2-5 | RESOLVED | DEFERRED to O-3, with both readings and no recommendation |
| FA2-6 | RESOLVED | R-1, R-2, R-4 |
| FA2-7 | PARTLY | R-7 and §5 disclosure; O-6's mitigation is ineffective and its magnitude is understated (FA3-8) |
| FA2-8 | RESOLVED | Separate keys, `plan_complete_rule`, `ends_when_any_meaning` as data |
| FA2-9 | RESOLVED | Conditions (i)–(v) named |
| FA2-10 | RESOLVED | Ceiling; data mounted or evaluated before declaration |
| FA2-11 | RESOLVED | `NO_RESULT` now includes a technically failed lockbox read; O-4 |
| FA2-12 | RESOLVED | Four-level precedence, Constitution first |
| FA2-13 | RESOLVED | D-13 row added, D-20 placed (the placement causes FA3-6) |
| FA2-14 | RESOLVED | Worded conditionally |
| SA2-1 | RESOLVED | Precedence plus R-1..R-6 (path defect in R-3 → FA3-5) |
| SA2-2 | RESOLVED | R-7 |
| SA2-3 | RESOLVED | `nomination_deadline_days` separate; hard limit under O-2 |
| SA2-4 | PARTLY | The four named leaves are restored, but `validation.dsr.minimum` and `promotion.dsr_minimum` change from number to string (FA3-4) |
| SA2-5 | RESOLVED | Ranges narrowed |
| SA2-6 | RESOLVED | DEFERRED to O-2; the schedule claim holds (42 days of slack, computed) |
| SA2-7 | RESOLVED | Both readings presented |
| SA2-8 | RESOLVED | Count sentence removed |

## Findings

| ID | Sev. | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| FA3-1 | BLOCKER | §3 G-12 "defined" (also G-2) | **G-12 has no operative definition but is marked defined**, so §4's "decide every OPEN gate before signing" check never catches it; D-19 would certify `U_proc` over a gate whose availability depends on an unbound estimator. | Protocol l.242–244 names a Newey-West ESS with no kernel, bandwidth or fallback trigger; those details exist only in `IMPLEMENTATION_CONVENTIONS.md` l.25–38, whose l.3 says "not governance-active"; decision packet R3 (l.28–35): never compare the ESS with the minimum of 120, and a statistician must approve any governed use; no D-row covers ESS. For G-2, R6 (l.53–57): "Never evaluate the protocol drawdown constraint." | Mark G-12 `<<OPEN new row: ESS series, kernel, bandwidth, fallback trigger>>`; owner or statistician to confirm that G-2 is operative as written (sign and scale of maximum drawdown). |
| FA3-2 | BLOCKER | §3 G-11 | **Shuffled-labels null omitted.** Line 289 (`null_minimum_percentile`) is unqualified; both nulls carry a `gate_metric`, and the shuffled-labels one (l.141–145) is the out-of-sample Spearman IC. The draft assigns 289 to the random-exposure null only, silently settling which gates are mandatory and so defining `U_proc`. | protocol l.134–145, 289; allowed model classes are fitted (l.155), so the IC exists; D-14 (matrix l.56) covers only the random-exposure null; a grep of `review/` finds the shuffled-labels null only as the §18 backtester canary | Add a row with an open marker and a new D-row, or an explicit owner decision that line 289 does not apply to it. |
| FA3-3 | BLOCKER | §0 activation list; §2.3 l.153, §2.4 l.179 ("gates of §3") | **The gate list does not live in any activated artifact.** Only the Constitution, the protocol YAML and the two annexes are activated; in `protocol_v1.1.yaml`, "§3" points at nothing, so the `U_proc` domain is not part of the frozen protocol. | draft l.43–46, 153, 179 | Encode it in the YAML (e.g. `promotion.gates` with PASS/FAIL/N/A/UNAVAILABLE per gate), or add a hashed Annex C. |
| FA3-4 | NON-BLOCKING | §2 l.74 "Every v1.0 key path and leaf shape is kept" | **The self-description is false:** `validation.dsr.minimum` and `promotion.dsr_minimum` change from the number `0.95` to a string. Non-blocking because no code consumer exists (grep of `src/`, `tests/`) and the schema does not type these leaves — this differs from SA2-4's BLOCKER rating. | draft l.168, 181; protocol l.231, 287 | Name the two exceptions, or keep a number-valued key with the z-test in `justification`. |
| FA3-5 | NON-BLOCKING | R-3 | **R-3 cites a non-existent path:** `partitions.confirmation.start.value`; the start is a plain value with no `.value` field. | v1.0 l.66; draft l.99 | `partitions.confirmation.start`. |
| FA3-6 | NON-BLOCKING | §4 l.216; G-9 | **"No clause is both bound and marked" is false:** §2.4 binds `added_purposes` and the family seed (l.165, 174) while §4 l.231 marks them `<<OPEN D-20>>`; G-9 is "defined" although its code binding (R-8) is still open under D-20. | draft l.165, 174, 202, 231 | G-9 status "D-19 values; `<<OPEN D-20>>`"; reword the claim. |
| FA3-7 | NON-BLOCKING | §1 §5 l.61 | **Revision 3 dropped revision 2's "termination follows the protocol's post-nomination procedure".** Without it, the highest-precedence text equates budget exhaustion with plan completion, while protocol l.146 requires "plan complete AND every nominee processed"; Annex P18-2(a) "ends only when (b)–(d) complete" saves the intended reading only by inference. | rev 2 vs rev 3 diff; draft l.146 | Restore the revision 2 clause. |
| FA3-8 | NON-BLOCKING | O-6 | **The mitigation does not stop the threat, and the magnitude is understated.** The family seed = hash of `data_manifest_hash` + trial ids + hypothesis hashes (Annex B l.97–100), all searchable offline, so logging declaration attempts does not stop the search. 0.03 is the single-seed z spread (computed 2/√3998 = 0.0316); choosing the best of k seeds shifts z by about 0.049 (k=10), 0.079 (100), 0.103 (1000) (computed from expected normal maxima; the normal approximation is an `UNVERIFIED_EXTERNAL_ASSUMPTION` inherited from FA2-7). | draft l.309–313 | Correct the figure; present FA2-7's alternative, a seed from entropy published after declaration; owner's choice. |
| FA3-9 | NON-BLOCKING | §3 l.210–211 | **O18-5 also names lines 90–91**; the list collapses them into a sentence. Components: ΔSharpe ≥ 5th percentile, ΔSharpe > 0, drawdown, ETH sanity. | PROPOSAL l.432 | List each with PASS/FAIL/N/A/UNAVAILABLE (UNAVAILABLE → `NO_RESULT`, outside `U_proc`), under D-11. |
| FA3-10 | NON-BLOCKING | §3 row for l.292 | **"A violation invalidates the cycle" is an unlabelled new consequence**; v1.0 says only `true`, and §2.2 describes prevention, not invalidation. | draft l.125, 208 | Label it `[AI default]` or make it an owner decision. |
| FA3-11 | NON-BLOCKING (inherited from rev 1/2, not raised by FA2/SA2) | §2.1 | **The excluded gap days belong to no partition**: whether they can be mounted, and whether they can be engine training input, is undefined. | draft l.99; v1.0 l.65–66; Constitution l.83 | State that they are not exploration, never mounted, engine-only. |
| FA3-12 | NON-BLOCKING | §6 step 1; §8 | **Order of work.** P18-7 computes every gate in simulation and P18-6 freezes the qualification object before held-out replications. If D-19 is preregistered before the gate rows are decided (as §8 currently orders it), the 1% certification does not cover the final gates, and redoing it burns the held-out seed namespace. | Annex A l.131–138, 155–158 | Require the rows governing gate availability (D-02..D-10, D-14, D-15, and the FA3-1/FA3-2 rows) to be decided before D-19 is frozen. |

I declined no finding. All twelve are proposals for the owner; I applied none.

## Q2 — new defects

Precedence and R-1..R-8: sound, apart from FA3-5 and FA3-7. Gate list G-1..G-13: FA3-1, FA3-2, FA3-3, FA3-6, FA3-9, FA3-10; the N/A cases checked out for G-8 (l.264), G-10 (l.235) and OOS/IS (l.249). Removing "keep blocked": correct — note that a "(c) keep blocked" answer on D-08, D-14 or D-20 then means the amendment cannot be signed. Separate calendar keys: correct. Leaf shapes: FA3-4. Owner items: O-1, O-3, O-4, O-5 sound; O-2 verified; O-6 affected by FA3-8.

## Q3

**NOT READY.** Blocking: FA3-1, FA3-2, FA3-3.

## Remaining owner or statistician decisions

O-1..O-6; new decision rows for the ESS gate (FA3-1) and the shuffled-labels null (FA3-2); the G-2 reading; D-02..D-15 and D-20; D-19, which must come after the gate rows (FA3-12).

## Still unauthorized

Frozen edits, activation, signing or accepting the text, D-19 calibration, any cycle/trial/confirmation/lockbox access, code, promotion, trading. Any §16-protected code still needs a different-model review and the owner's own PR review. This review signs nothing and is not a completed record until someone authorized commits it verbatim.

## Plain-language summary

1. Revision 3 fixes the earlier blockers: the time cap, the seed timing, the overlapping blocked lines and the machine field shapes.
2. The new list of checks a strategy must pass marks the "minimum effective decisions" check as ready, but its formula has never been approved for real use.
3. One frozen check, the shuffled-labels test, is missing from the list entirely.
4. The list exists only in this draft document, not in any file that would actually be frozen.
5. Fix those three, decide the open checks before the calibration starts, then sign; the other points are wording fixes.
