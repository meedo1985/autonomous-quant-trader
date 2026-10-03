# Sol High focused check of the §4 amendment draft rev3 at `fcc0cf2` — NOT READY

Date: 2026-10-03. The OpenAI-family focused check for R19-2. It ran in parallel with the Fable check and without sight of it.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a101ff-5a6e-7351-8719-71b134eec8cb`;
  tokens used 126,490; exit 0. (The reviewer's self-report names only "GPT-5 family"; the CLI
  header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_R3.md` (committed `1aa523f`) with `{{PREFIX}}` = `SA3`
  (substituted file SHA-256 `c859990022a803fe2410b01004b6b0d65e977adfbe8ca7158fec76992f14d061`).
- The reviewer's final message, verbatim:

---

Model: **Codex, GPT-5 family**; exact serving-model identifier is not exposed to me.  
Commit reviewed: **`fcc0cf231230c0519e11e1261490e317211d432a`**  
Verdict: **NOT READY**  
Blocking defects: **SA3-1, SA3-2, SA3-3**.

## Revision-2 findings

| Finding | Status | Reason |
|---|---|---|
| FA2-1 | RESOLVED | R-6 expressly subordinates P18-2(a) to the calendar limit and owner-filled cap rule. |
| FA2-2 | PARTLY | G-1..G-13 cover the pre-lockbox promotion checks, but the O18-5-required lockbox pass rule at frozen lines 90–91 is omitted; SA3-3. |
| FA2-3 | RESOLVED | “Keep blocked” is removed, and every open gate must be decided before signing. |
| FA2-4 | RESOLVED | D-12 is narrowed to lines 77–79 and D-11 to 83–92; unaffected lockbox clauses expressly remain in force. |
| FA2-5 | DEFERRED — O-3 | Both constitutional readings are presented without an AI recommendation. |
| FA2-6 | PARTLY | R-1, R-2 and R-4 stabilize most referents, but R-1 and R-8 conflict over whether code references are normative; SA3-4. |
| FA2-7 | DEFERRED — O-6 | R-7 removes the impossible timing rule and discloses seed selection risk; the owner must choose the final treatment. |
| FA2-8 | RESOLVED | Nomination deadline, hard calendar limit, and plan-completion rule are now separate operative keys. |
| FA2-9 | RESOLVED | The proposed Constitution now fixes conditions (i)–(v) as the minimum eligibility baseline. |
| FA2-10 | PARTLY | Ceiling is specified, but the corrected data-source rule loses to Annex A under the new precedence order; SA3-2. |
| FA2-11 | RESOLVED | A technically failed lockbox read is expressly a `NO_RESULT` cause; baseline consequences remain O-4. |
| FA2-12 | RESOLVED | Constitution v1.1 is now highest in the stated precedence order. |
| FA2-13 | RESOLVED | D-13 is present and D-20 has identified insertion points in R-8 and §2.4. |
| FA2-14 | RESOLVED | The general raw-count fallback is retained conditionally while C2 may use no count. |
| SA2-1 | PARTLY | Termination is reconciled, but the C2-window override contains a nonexistent path and does not override Annex A’s gap-data source; SA3-1 and SA3-2. |
| SA2-2 | RESOLVED | R-7 makes the “before any data exists” sentence informative and binds pre-evaluation/pre-stream-use timing. |
| SA2-3 | DEFERRED — O-2 | The contradictory meanings are structurally separated; the final window, limit, and cap rule remain owner choices. |
| SA2-4 | RESOLVED | The identified object and boolean leaf shapes are restored. |
| SA2-5 | RESOLVED | The lockbox open-row ranges no longer suspend the cooldown or request controls. |
| SA2-6 | DEFERRED — O-2 | The recommendation demonstrates that the normal schedule fits and identifies governance/infrastructure expiry as `U_ops`; the owner must adopt or replace it. |
| SA2-7 | DEFERRED — O-3 | The unsupported interpretation was removed and both readings are reserved to the owner. |
| SA2-8 | RESOLVED | The rationale no longer makes a review-count claim invalidated by this check. |

## Revision-3 findings

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| SA3-1 | BLOCKER | [DRAFT_WORDING.md:85](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:85>) | A conforming consumer resolves R-3’s start path literally and cannot find it. | R-3 names `partitions.confirmation.start.value`, but the preserved v1 leaf and rev3 line 99 are scalar `partitions.confirmation.start`; no `.value` exists. | Change R-3 to `partitions.confirmation.start` and recheck every override path against the promised v1 leaf shapes. |
| SA3-2 | BLOCKER | [DRAFT_WORDING.md:33](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:33>), [line 107](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:107>); Annex A line 29 | A reader determines the gap from all data outside the window—including potentially restricted later data—instead of only data already mounted or evaluated. | Annex A says “data outside the window.” Rev3’s corrected source is ordinary protocol text, while the declared order places Annex A above ordinary protocol text. R-3 overrides the dropped days but not the source rule. | Put the ceiling and permitted source data into an R-clause that expressly replaces Annex A’s sentence, or amend and re-review the annex. Explicitly exclude confirmation/lockbox data not already authorized. |
| SA3-3 | BLOCKER | [DRAFT_WORDING.md:187](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:187>), [line 210](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:210>); [PROPOSAL.md:432](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/d18-proposal/PROPOSAL.md:432>) | Every marker is filled, yet the amendment still fails owner decision O18-5’s complete `H_f` enumeration. | O18-5 requires PASS/FAIL/N/A/UNAVAILABLE behavior for lines 90–91 and 270–292. G-1..G-13 cover the latter; rev3 explicitly excludes the lockbox stage and supplies no corresponding lockbox row. | Add a separate lockbox pass-rule row, governed by D-11, with all four behaviors and an explicit statement that it is post-eligibility and outside `U_proc`. |
| SA3-4 | NON-BLOCKING | [DRAFT_WORDING.md:83](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:83>), [line 90](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:90>) | After D-20 is filled, readers disagree whether Annex B’s code references are merely informative or hash-bound normative dependencies. | R-1 makes code paths informative; R-8 binds named existing-code references. Both occupy the same precedence tier, with no stated exception or intra-tier order. | Narrow R-1 or state explicitly that R-8 is its exception. |
| SA3-5 | NON-BLOCKING | [DRAFT_WORDING.md:309](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:309>) | A declarer privately evaluates many prospective declarations and records only the favorable one as the “first” official declaration. | O-6 recognizes private replay but recommends logging declaration attempts; repository logging cannot observe uncommitted private attempts, so it does not mitigate the stated attack. | Retain the disclosure, but do not present logging as protection against private seed grinding. If mitigation is required, use an unpredictable post-commitment seed source subject to owner/statistician review. |

The precedence/gap and gate-list defects survive even after every current marker is filled. The separate calendar keys, removal of “keep blocked,” and restored v1 leaf shapes are otherwise sound. O-1, O-4, and O-5 are coherent; O-2 is coherent but undecided; O-3 is correctly left without a recommendation; O-6 needs the qualification in SA3-5.

Review gate: **BLOCKED** by SA3-1 through SA3-3. Tests, lint, typing, and import checks are N/A for this wording-only read. The working tree was clean; I made no edits, used no network or restricted data, and did not re-verify the unchanged annex copies or hashes.

Revision 3 fixes most of the previous review findings.  
One override points to a configuration field that does not exist.  
The corrected embargo rule is still defeated by the stated precedence order.  
The required list of gates still omits the lockbox pass rule.  
Fix those three defects, fill every marker, and re-review before the owner authors the amendment.