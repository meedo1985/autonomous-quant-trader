# Fable focused check of the §4 amendment draft rev2 at `afed53e` — NOT READY

Date: 2026-10-03. The Anthropic-family focused check for R19-2. It ran in parallel with the Sol check and without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_R2.md` (committed `61543cd`) with `{{PREFIX}}` = `FA2`.
- Model metadata: the reviewer reports `claude-fable-5-1` from its session metadata.
  The recorder observed the `fable` override but could not check the ID
  independently.
- The reviewer's final report, copied verbatim from its hand-back message (indentation removed):

---

claude-fable-5-1

# FA2 review: §4 amendment draft wording, revision 2

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family — model ID from session metadata, not chosen by me.
**Commit reviewed:** `afed53e` (HEAD `61543cd`, branch `docs/d19-recommendation`). Other reviewer's revision-2 review not read.
**Verdict:** **NOT READY** — three BLOCKERs (FA2-1..FA2-3), each with a small fix. Skill scale: `REVISION_REQUIRED`; promotion `KEEP_BLOCKED`.

## Verification (what was computed vs only read)

- **Annexes verbatim (computed):** diff of `git show 9718fdc:…/PROPOSAL.md` l.184–360 and `git show a3d2c59:…/DESIGN.md` l.42–204 against the annexes: the only differences are the added header block (7 lines each) and the appended A-B7 clause in Annex A.
- **Hashes and EOL (computed):** working tree, `afed53e` index blob, and draft value agree for both (`836adec7…`, `80ad6b78…`); 0 CR bytes; `git ls-files --eol` = `i/lf w/lf attr/text eol=lf`, from the nested `review/governance-statistics-amendment/.gitattributes` — the files stay LF on checkout, so the recorded values are portable.
- **Discriminating (computed):** wrong treatments give different values — Annex A: CRLF `2eb576a8`, stripped trailing newline `9add5b8c`, body without header `335d5cf7`; Annex B: `619f4e3f`, `25b1bc5e`, `4f1c8813`.
- **Exact arithmetic (Fraction):** seven eligible cycles sum to 127/1280 = 1/10 − 1/1280; per family 1/40, 1/80, 1/160…; v1 window 1,247 days.
- **Read only, not verified:** cited lines of protocol v1.0, Constitution, protocol schema (permissive, `additionalProperties: true`), decision matrix, OWNER_DECISION_B, PROPOSAL §4 (O18-1..O18-8).
- Mandatory protocol: 1 (topic searches found missing O18-5, §0 l.21, §4 l.48), 2 (referent checks found the §3 range errors, FA2-4), 3/4 as above, 5 ("annex wins" applied to every owner item → FA2-1; "keep blocked" applied to P18-5/P18-7 → FA2-3; FA1-1's reasoning applied to eligibility → FA2-9), 6 (FA2-5, FA2-7), 7 not applicable (no verifier exists for wording), 8 as above, 10 (self-description "every line in §3 carries a marker" fails for the D-20 row, which has no lines → FA2-13), 11 (inherited marked), 13 (§16 not triggered by this Markdown; the checklist covers later code).

## Q1 — revision-1 findings

| ID | Status | Reason |
|---|---|---|
| FA1-1 | RESOLVED | B-5 in Constitution §9; protocol binds only `z_crit_1`; `m` from the first eligible cycle; counting rule → O-1 |
| FA1-2 | PARTLY | Annex B binds `u_j`, `psi_j`, cap, `B−1`, fsum, seed JSON; still relies on unhashed code ("existing replicate-seed construction", `bootstrap_indices`, PW routine) — that residue falls under OPEN D-20, which has no insertion point (FA2-13) |
| FA1-3 | PARTLY | Markers added; some ranges wrong (FA2-4); D-13 missing |
| FA1-4 | RESOLVED | §4 rationale conditional, accepted weaknesses listed |
| FA1-5 | RESOLVED | Post-v1 entry deferred to the C3 amendment; residual wording in FA2-6 |
| FA1-6 | RESOLVED (DEFERRED, C3 amendment) | P18-0's "assigned at ingest" text has no effect for C2 under unchanged §0 l.20 |
| FA1-7 | PARTLY | (a), (c), (d) fixed; rounding direction for whole days undefined (FA2-10) |
| FA1-8 | PARTLY | Eligibility via Annex A; `T_min` under `selection_rule`; the new §0 "not remove them" has no reference set (FA2-9) |
| FA1-9 | PARTLY | P18-1/4/6/7 and SR6-2 bound; the O18-5 gate list is not (FA2-2) |
| FA1-10 | DEFERRED (O-2) | Its recommendation conflicts with the annex (FA2-1) |
| FA1-11 | PARTLY | `NO_RESULT` widened and O-4 added; a technically failed lockbox read is still unclassified (FA2-11) |
| FA1-12 | RESOLVED | Schema needs only top-level keys plus `cycle_termination.calendar_days_elapsed`; both kept |
| FA1-13 | RESOLVED | `added_purposes` |
| FA1-14 | RESOLVED | D-20, D-02, D-03 listed; D-13 omitted (FA2-13) |
| FA1-15 | RESOLVED | Checklist steps 3–7 |
| FA1-16 | RESOLVED | §0 activation steps |
| FA1-17 | RESOLVED | Labels fixed; minor: "max over declared horizons" is a reviewer suggestion and carries no label |
| FA1-18 | DEFERRED (O-3) | The recommendation's reasoning is flawed (FA2-5) |
| FA1-19 | RESOLVED | Both citations fixed |
| SA1-1 | PARTLY | P18-7 event and denominator now in Annex A; the gate list it depends on is missing (FA2-2) |
| SA1-2 | RESOLVED | Annex A P18-0 + A-B7 |
| SA1-3 | RESOLVED | Annex A P18-1/4/6 |
| SA1-4 | PARTLY | As FA1-2 |
| SA1-5 | RESOLVED | By deferral |
| SA1-6 | PARTLY | State machine and timestamps written; precedence → O-2/O-3, and O-2 conflicts with the annex (FA2-1) |
| SA1-7 | PARTLY | FA2-3, FA2-4, FA2-13 |
| SA1-8 | RESOLVED | Exact check above |
| SA1-9 | RESOLVED | Labels fixed |
| SA1-10 | RESOLVED | Checklist |
| SA1-11 | RESOLVED | `<<DECLARATION>>` marker |

## Findings

| ID | Sev. | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| FA2-1 | BLOCKER | §0 "Annex text wins"; §2.3 `calendar_days_elapsed`; O-2 | **O-2 conflicts with the annex.** The owner adopts O-2's recommendation ("the cap wins"), but Annex A P18-2(a) says "the cycle ends only when (b)–(d) complete" and §0 makes annex text win. His answer is void and the calendar cap is inoperative: e.g. a nominee awaiting `APPROVE_AS_IS` keeps the cycle open without limit, against §5 l.61 ("calendar/time limit … Otherwise invalid"). Filling the marker cannot repair it. Inherited ambiguity from P18-2 (FA1-10); revision 2's precedence rule makes it decisive. | Annex A l.84–91; draft l.33, 118, 121, 237–239 | Write the O-2 answer, whichever it is, as an owner clause inside Annex A ("A-O2", like A-B7), or state that A-clauses prevail over the verbatim D-18 text. |
| FA2-2 | BLOCKER | §2.3 `per_nominee`; §2.4 `procedure_no_result` | **The decided O18-5 gate list is missing and has no marker.** O18-5 requires the amendment to enumerate every `H_f` component (protocol l.90–91, 270–292) with PASS/FAIL/N/A/UNAVAILABLE behaviour, including PBO enablement. P18-7's `U_proc` (1% target) depends on which gates are mandatory and which are "frozen `N/A`". Without it, D-19 cannot define the event it calibrates, and a "no marker left" check passes. FA1-9 raised it (FABLE_REVIEW l.37); the adjudication annexed only PROPOSAL §2, not §4. | PROPOSAL `9718fdc` l.432–435 | Add the O18-5 gate table, or a `<<D18 O18-5>>` marker at §2.3. |
| FA2-3 | BLOCKER | §5 step 1 "or the owner explicitly keeps those gates blocked" | **"Keep blocked" is not a safe way to fill a marker.** P18-5: any gate `UNAVAILABLE` → no promotable trial; P18-7: a gate not computed counts as `UNAVAILABLE`. With any mandatory pre-lockbox gate kept blocked, every replication is a `U_proc` event, so D-19 can never certify and the `<<D19>>` markers can never be filled. If C2 runs anyway, it spends the only eligible window on both families (P18-1), which "may take years" to replace, with zero chance of promotion. The option also invites reading "blocked" as "frozen N/A". | Annex A l.53–57, 121–124, 155–158 | Remove the option for mandatory pre-lockbox gates, or state these consequences and forbid converting "blocked" to N/A without a §4 decision. |
| FA2-4 | NON-BLOCKING | §3 row "74–92 (except 74), 294–296" | **Wrong referents.** D-11 covers l.83–91 and D-12 covers l.77–78 (matrix l.48–49); the row also suspends l.75 (cooldown), l.76 (PASS_FAIL_ONLY), l.80–82, and l.294–296, which are `lockbox_request` (eligibility precondition, no retry), not attestation fields. §2.3 relies on l.75; Annex A relies on l.75 (P18-2) and l.295 (P18-7). Damage is mitigated because Constitution l.79/85 and the annex back these rules. | protocol l.73–96, 294–296 | Change the row to 77–79 and 83–92; state that l.75, 76, 295, 296 stay in force. |
| FA2-5 | NON-BLOCKING | O-3 recommendation | **Right answer, wrong reason, contradicted inside the document.** O-3 reads §4 l.48 "open promotions" as "already attested"; §5 step 9 treats an open promotion as an in-progress one, and §0 l.21 defines promotion = eligibility → lockbox → attestation. Under that reading an already-ELIGIBLE nominee may be protected from a post-look revision. | Constitution l.21, 48 | Present both readings to the owner; it stays an owner decision. |
| FA2-6 | NON-BLOCKING | Both annexes | **Normative text with drifting referents:** bare v1.0 line numbers ("line 74", "line 295"), "reconciliation lines 118–119" (unnamed, unbound file), `METHOD_CANDIDATE.md`, `IMPLEMENTATION_CONVENTIONS.md`, code paths, "Proposed"/"AI default" labels; P18-0's "needs the amendment" now points to a later amendment; the hashed bytes include the "not an amendment" status header, which must change at activation. | Annex A l.11, 47–49, 83, 120; Annex B l.49, 106–113 | Add an owner reading clause: line numbers refer to the v1.0 files at their frozen hashes; citations and labels are informative; P18-0's last sentence means a later amendment. Re-review the final annex bytes (step 2). |
| FA2-7 | NON-BLOCKING (inherited, DESIGN rev 3) | Annex B §2.4 | **"Seeds are fixed before any data exists … cannot be gamed" is false for C2.** The v1 window is public; the family seed hashes trial ids and `data_manifest_hash`, so iterating declarations against private replays can select a seed. At `B=2000` the relative MC error of `sd_b` ≈ 1/sqrt(2·1999) = 1.58% (normal-theory approximation, `UNVERIFIED_EXTERNAL_ASSUMPTION` for these replicates) ≈ 0.03 per standard deviation on z ≈ 2. | Annex B l.107–109 | Owner: add it to the disclosed weaknesses, or derive the seed from a commitment published after declaration. |
| FA2-8 | NON-BLOCKING | §2.3 | **Operative meaning sits in YAML comments.** `calendar_days_elapsed: 180` now means the look day; the real limit (180 + window) appears only in a comment and in the annex. After a day-180 timeout (`U_ops`) the plan never completes, so `all_family_trial_budgets_exhausted` and `plan_exhaustion` are undefined and the cycle waits for the cap. | draft l.117–121, 126 | Add explicit data keys; define "plan complete" after a timeout. |
| FA2-9 | NON-BLOCKING | §1 §0 new definition | **Circular protection.** "May add conditions but not remove them" has no baseline, because each protocol freezes its own rule (the same reasoning as FA1-1). Harmless now, since any eligible post-v1 window needs a further amendment. | draft l.46 | Name Annex A P18-0 (i)–(iii) and A-B7 (v) as the minimum. |
| FA2-10 | NON-BLOCKING | §2.1 `gap_embargo` | **"In whole days" has no rounding direction** while P18-0 requires "at least", so it should round up; "data outside the window" literally includes lockbox data, and the limiting note is not operative. | draft l.86, 91 | Ceiling; "data mounted in the sandbox before declaration". |
| FA2-11 | NON-BLOCKING | §1 §5 l.63 | **A technically failed lockbox read is unclassified.** `NO_RESULT` covers pre-lockbox failures only, so such a cycle defaults to `NO_EDGE_FOUND`, which may open the baseline path. | P18-5; §0 l.17 | Add this case to O-4. |
| FA2-12 | NON-BLOCKING | §0 | **"Annex text wins over any summary in §1–§2"** subordinates Constitution v1.1 clauses to protocol annexes. | draft l.33 | Restrict it to the protocol summaries in §2. |
| FA2-13 | NON-BLOCKING | §3 | **D-13 (CPCV diagnostic report, l.215–222) omitted; the D-20 row has no lines** for inserting its wording. | matrix l.55, 72 | Add D-13; place D-20 at §2.4 `random_seed_policy.family` and `added_purposes`. |
| FA2-14 | NON-BLOCKING | §1 §9 l.106 | **Loss of a general rule.** A general fallback rule is replaced by a fact about one method ("The frozen DSR method uses no effective trial count"); a later method would lose the raw-count fallback. | Constitution l.106; B-1 | Word it conditionally; owner's text. |

No finding was declined. All are proposals for the owner; I applied none.

## Q2 — other new defects

Verbatim annex binding: FA2-1, FA2-6, FA2-12. B-5 sentence: correct (exact arithmetic); counting → O-1. Removing post-v1 data: correct for C2 (FA2-6 residue). `gap_embargo`: FA2-10. Termination keys: FA2-1, FA2-8. §3 markers: FA2-3, FA2-4, FA2-13. Owner items: O-1, O-4, O-5 sound; O-2 affected by FA2-1; O-3 by FA2-5.

## Q3

**NOT READY.** Blocking defects: FA2-1, FA2-2, FA2-3.

## Remaining owner or statistician decisions

O-1..O-5; the FA2-1 wording; the FA2-5 reading; the FA2-7 disclosure; D-02..D-15 and D-20.

## Still unauthorized

Frozen edits, activation, signing or accepting the text, D-19 calibration, any cycle/trial/confirmation/lockbox access, code, promotion, trading. Any §16-protected code still needs a different-model review and the owner's own PR review. This review signs nothing.

## Plain-language summary

1. Revision 2 fixes most earlier problems, and the two annexes are exact copies of your decided texts.
2. Your recommended answer on the time cap would be cancelled by the annex's own wording, so the cap answer must be written into the annex.
3. The list of which checks count as "missing" is not yet written down, and the 1% target depends on it.
4. Leaving some checks blocked would either stop the calibration or use up your only clean data window with no chance of promotion.
5. The other points are wording fixes to make before you sign.
