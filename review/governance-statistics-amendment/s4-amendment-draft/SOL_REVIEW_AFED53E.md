# Sol High focused check of the §4 amendment draft rev2 at `afed53e` — NOT READY

Date: 2026-10-03. The OpenAI-family focused check for R19-2. It ran in parallel with the Fable check and without sight of it.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a101f3-192a-70d3-a302-e057e05b0559`;
  tokens used 85,455; exit 0. (The reviewer's self-report names only "GPT-5 family"; the CLI
  header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_R2.md` (committed `61543cd`) with `{{PREFIX}}` = `SA2`
  (substituted file SHA-256 `468bf61731dcf875eea60844b808353b137844416499c752324e172b941d7110`).
- The reviewer's final message, verbatim:

---

Model: **Codex, GPT-5 family**; exact serving-model identifier is not exposed to me.  
Commit reviewed: **`afed53e12eb67a7033a634e0a08e9fdc3755e03f`**  
Verdict: **NOT READY**  
Blocking defects: whole-prose annex precedence creates unresolved contradictions; Annex B makes C2’s seed timing impossible; termination keys have contradictory machine meanings; several YAML leaf shapes are not preserved; and the lockbox open-row range conflicts with the bound cooldown.

## Verification

- Annex A payload: all 177 lines exactly match `9718fdc:.../PROPOSAL.md` lines 184–360.
- Annex B payload: all 163 lines exactly match `a3d2c59:.../DESIGN.md` lines 42–204.
- Annex A raw blob: no CR bytes, final LF, SHA-256 `836adec7a40c8d0b494352e71116752ea577dd3403d59b0c8769a2445d388480`.
- Annex B raw blob: no CR bytes, final LF, SHA-256 `80ad6b785de337568e806d6feda9168f2ec9b07aed2d8e1e5c14c955ff2b25d0`.
- Exact B-5 arithmetic is correct: after \(n\) eligible cycles the total is \(0.10(1-2^{-n})<0.10\); its infinite limit is \(0.10\).
- Working tree was clean apart from the known inaccessible global-ignore warning. No tests apply to this wording-only review.

## Revision-1 findings

| Finding | Status | Reason |
|---|---|---|
| FA1-1 | DEFERRED — O-1 | The schedule is now constitutional, the finite/infinite totals are correct, and C2 binds only its allowance; which outcomes increment `m` remains O-1. |
| FA1-2 | RESOLVED | Annex B supplies the named numerical, reduction, cap, failure-order, seed and stream conventions and is hash-bound. |
| FA1-3 | PARTLY | Explicit markers now exist, but the lockbox range is overbroad and conflicts with the independently bound cooldown; see SA2-5. |
| FA1-4 | RESOLVED | The rationale now says the targets are conditional simulation results, identifies the global null, C2 selection weakness, support limitation and uncertified infrastructure failures. |
| FA1-5 | RESOLVED | Post-v1 confirmation entry is removed from C2 and explicitly deferred to a later C3 amendment. |
| FA1-6 | RESOLVED | The after-seeing-data assignment choice is removed; the later rule must be fixed before the data. |
| FA1-7 | PARTLY | A distinct whole-day `gap_embargo` and exact timestamp marker were added, but Annex A’s C2 “first embargo dropped” prose now conflicts with the whole-prose precedence rule. |
| FA1-8 | RESOLVED | Annex A P18-0 plus A-B7 supplies fail-closed eligibility, declaration evidence, operative promotion restriction and `T_min`. |
| FA1-9 | RESOLVED | The omitted P18-1/P18-4/P18-6/P18-7 details are incorporated through Annex A. |
| FA1-10 | DEFERRED — O-2 | The state-machine structure is present, but cap precedence and window length remain O-2. |
| FA1-11 | DEFERRED — O-4 | `NO_RESULT` is widened; deployable-baseline-path eligibility remains O-4. |
| FA1-12 | PARTLY | Required top-level paths were restored, but leaf shapes and `calendar_days_elapsed` semantics remain defective; see SA2-3 and SA2-4. |
| FA1-13 | RESOLVED | `added_purposes` no longer purports to replace the existing lockbox bootstrap purpose. |
| FA1-14 | RESOLVED | D-20 and the previously unrecorded D-02/D-03/D-04/D-07 rows are listed as open. |
| FA1-15 | RESOLVED | Versioning, rationale, incident check, full §16 scope, C1 verification and re-review after material edits are listed. |
| FA1-16 | RESOLVED | The draft requires `-text` before hashing and describes the signed manifest-addition process. |
| FA1-17 | RESOLVED | Per-cycle accounting is marked derived; substantive unresolved choices are owner or D-19 markers. |
| FA1-18 | DEFERRED — O-3 | Post-look revision/invalidation precedence is explicitly reserved to O-3. |
| FA1-19 | RESOLVED | Automatic reruns are cited to P18-1 and the incorrect §27 hash-tooling citation was removed. |
| SA1-1 | RESOLVED | Annex A P18-7 binds the event, denominator, simultaneous bounds, mandatory gate computation, cause precedence, timeout and `U_proc`/`U_ops` split; allocation remains D-19. |
| SA1-2 | RESOLVED | Annex A P18-0 plus A-B7 binds the full eligibility object, declaration evidence, C2 weakness and `T_min`. |
| SA1-3 | RESOLVED | Declaration validity, exact nomination and frozen qualification/no-retuning rules are incorporated by Annex A. |
| SA1-4 | RESOLVED | Annex B contains the required deterministic method conventions. |
| SA1-5 | PARTLY | The main draft cleanly defers post-v1 entry, but making all Annex A prose superior normative text reintroduces scope ambiguity. |
| SA1-6 | PARTLY | A post-nomination structure was added, but its termination semantics contradict themselves and Annex A; O-2/O-3 alone do not repair that. |
| SA1-7 | PARTLY | Open rows are visible, but the lockbox range is not clause-accurate and conflicts with §2.3. |
| SA1-8 | RESOLVED | The finite-total/limit distinction and “C2 only if eligible” qualification are correct. |
| SA1-9 | RESOLVED | Drafting choices, derived rules and owner-reserved decisions are now distinguished. |
| SA1-10 | DEFERRED — O-5 | The missing process controls are present; safety classification remains explicitly reserved to O-5. |
| SA1-11 | DEFERRED — declaration | The expression is now an explicit declaration-time marker requiring an exact UTC timestamp. |

## Findings

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| SA2-1 | BLOCKER | Draft lines 25–33; Annex A P18-0/P18-2 | Two conforming readers choose different C2-window and termination rules because the entire proposal narrative is superior normative text. | The draft says Annex A wins. Annex A says C2’s first embargo is dropped and that the cycle ends only after every nominee is processed; the main text adds a C2 gap and O-2 recommends that the calendar cap can end processing first. Annex A also retains “to be confirmed” prose outside the marker system. | Bind a clause-granular normative rule rather than the whole proposal narrative, or enumerate explicit overrides and precedence. Rehash and re-review the resulting annex. |
| SA2-2 | BLOCKER | Annex B §2.4, lines 97–113, especially line 108 | C2 cannot satisfy its normative seed rule because its 2022–2025 data already exist. | Annex B says seeds are fixed “before any data exists,” while Annex A expressly discloses that C2 uses historical public data. P18-1 requires freezing before evaluation, not before historical data exist. | Replace this with the intended pre-evaluation/pre-stream-use timing, or mark the sentence nonnormative. The full annex can no longer be described as verbatim superior normative text without an explicit correction. |
| SA2-3 | BLOCKER | Draft lines 116–132 | An implementation terminates at day 180 while the prose expects day 180 plus the post-nomination window. | `calendar_days_elapsed: 180` remains the machine value, while its `ends_when_any` comment redefines that same key as `180 + post_nomination_window_days`. O-2 cannot make both readings true. | Keep a separate nomination deadline of 180 and give the termination key the actual final numeric duration, or define a new unambiguous machine key and amend its schema/consumer contract. |
| SA2-4 | BLOCKER | Draft lines 97–112 and 103–104 | Existing consumers fail or interpret clauses differently despite the claim that v1 paths are preserved. | Frozen `trend_budget`, `volatility_budget`, and `max_evaluations_per_family_per_cycle` are `{value, justification}` objects but become scalars; `promotion.trial_budget_hard_stop` changes from boolean to a policy string. These are unmarked machine-interface changes. | Preserve the v1 leaf shapes and place explanatory rules in `justification`, or formally include and validate the schema/consumer changes. |
| SA2-5 | BLOCKER | Draft lines 68, 130, 171–186 | The cooldown is simultaneously operative and blocked by D-11/D-12. | §2.3 binds 30 days, but §3 marks frozen lines 74–92 except 74 as open, which includes line 75’s cooldown and unaffected fields such as `PASS_FAIL_ONLY`. The prior affected ranges were specifically 77–78 and 83–92. | Narrow each marker to its actual clauses and show the exact carried-over YAML locations. Ensure no clause is both bound and marked open. |
| SA2-6 | NON-BLOCKING | O-2, lines 237–239 | A planned calendar cap is labelled `U_ops`, potentially excluding predictable procedure incompleteness from the certified event. | Annex A assigns `U_ops` to infrastructure/governance failures and day-180 unfinished trials; it does not expressly classify a deliberately short post-nomination window as `U_ops`. | Before adopting the recommendation, bind its cause code and justify why it cannot evade `U_proc`; preferably choose a window that makes planned cap expiry impossible under the declared schedule. |
| SA2-7 | NON-BLOCKING | O-3, lines 240–243 | The owner relies on an incorrect reading of the no-retroactivity clause. | Constitution §4 says “no retroactive effect on open promotions”; the recommendation says this protects only already-attested promotions. That limitation is not in the cited text. | Remove that claimed interpretation and have the owner decide O-3 directly against the actual §4 wording. |
| SA2-8 | NON-BLOCKING | Rationale lines 204–206 | The final amendment repeats a statement that becomes false once this focused check is recorded. | It says revision 2 finished “without a further check”; this review is that further check, and another model-family check is planned. | Update the factual review-history sentence after the required review records are committed; treat that bookkeeping edit as non-material unless substantive text also changes. |

The `gap_embargo` concept itself is a reasonable separate control and correctly leaves fold embargo unchanged, but it is not presently safe because of SA2-1. The B-5 formula is correct; O-1 must still replace the marker with an explicit increment rule. O-1, O-4 and O-5 recommendations are conservative and coherent. O-2 and O-3 require the corrections in SA2-6 and SA2-7 before adoption.

This review made no edits and therefore is not yet a completed R19-2 record under the repository rule. An authorized person must record it verbatim and commit it; I did not commit, push, use the network, or access confirmation/lockbox data.

The annex copies and their hashes are accurate.  
The problem is that copied explanatory prose is being treated as superior law.  
The calendar limit also says both 180 days and 180 plus the extra window.  
Some unchanged-looking YAML fields silently change machine shape or remain both open and fixed.  
Fix the five blockers, fill every marker, and re-review before the owner authors the amendment.