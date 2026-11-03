# Codex Astra first review of D-20 option C sketch (c3fc60b)

Prompt: scratchpad `optc_astra_prompt.md` (reproduced in section "Prompt" below). Reviewer metadata from the Codex CLI header (2026-10-30): model `gpt-6-astra`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a18c72-e188-7fc2-980d-479adb7098f5`, 73,853 tokens. Reviewed `OPTION_C_MANUAL_RELEASE_SKETCH.md` at `c3fc60b`. Bitcoin node paused for the run (stopped 10:54:17Z at 690,193, restarted after). The prompt asked Astra to read `SOL_REREVIEW7_E68B947.md` for context; this is not an independent-of-Sol review of rev 8, and no Sol review of option C exists yet.

Verdict: **SOUND BASIS WITH NOTES** (binding status REVISION_REQUIRED): 4 BLOCKER (D20C-A-1, A-2, A-4, A-5), 4 NON-BLOCKING (A-3, A-6, A-7, A-8). Findings D20C-A-1..8, no gaps.

No finding is left unrepaired by decision yet; dispositions go in the full option C proposal if the owner pursues option C. Astra's side note on six oracle/canary working files with CRLF raw-hash differences (committed blobs match) is outside this review's scope and was not acted on.

## Report (verbatim)

**VERDICT: SOUND BASIS WITH NOTES.** Binding status: **REVISION_REQUIRED**.

Manual release is a viable direction, but four guarantees below need repair before adoption. This review does not approve or activate anything. Findings use **D20C-A-n** as requested; model metadata must come from the caller’s CLI header.

| Authority | Status |
|---|---|
| Constitution, protocol and threat model | Frozen and controlling |
| D-12 owner decision | Recorded; binding requires signed C2 |
| Revision 8 and option C | Inactive proposals |

All sketch line references below refer to [OPTION_C_MANUAL_RELEASE_SKETCH.md](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_MANUAL_RELEASE_SKETCH.md>), verified at `c3fc60b`.

**Rule 1’s central argument works conditionally.** If finish wins the lock, release consumes its durable record. If release wins, every subsequent finish finds the release and refuses, regardless of clock rollback. Concurrent releases return the same entry. With revision 8’s durable-before-use rules, output only after durable commit, and fail-closed recovery, I found no process/machine-crash interleaving producing contradictory shown results. These storage conditions remain essential; locking alone is insufficient.

**D20C-A-1 — BLOCKER — Rule 3, lines 11 and 21: entry creation is not delivery.**

**Failure scenario:** The release entry commits at hour 0; the process crashes before printing or copying the attestation. The owner obtains it at hour 24. Accepting a decision at entry +72 hours supplies only **48 hours of actual access**. A stalled copy has the same problem without a crash.

**Minimal repair:** Bind durable delivery of the complete result and attestation, its evidence, and recovery. Require the decision no earlier than 72 hours after established delivery; uncertain delivery must delay acceptance. If `cooling_off_start` must remain the entry timestamp, bind an additional delivery-based lower bound. A durable owner copy removes subsequent *store* availability dependence, not this initial handoff gap.

**D20C-A-2 — BLOCKER — Rules 1–2 and §3, lines 15–20, 27–30: the callable lock channel survives.**

**Failure scenario:** Before `R_0`, the owner invokes `lockbox_release`. Its check takes `L_store`, which `mark_finished` may hold. The eventual refusal therefore reveals a wait correlated with hidden finishing activity. No owner shell is necessary. After `R_0`, unfinished writes and other evaluations can still affect response latency.

Deleting the signing window also does not eliminate signing-fault leakage: a PASS-only signing refusal can delay or prevent release and cause cap expiry. That is a surviving R1-type effect.

**Minimal repair:** Bind all observable interfaces, including refusals, retries, timing, errors and maintenance access. Remove early probes’ dependence on sealed work, and substantiate the remaining isolation claims. Otherwise retain an accurately scoped, owner-decided §7 exception. “Machine activity only, handled by procedure” is not established.

**D20C-A-3 — NON-BLOCKING — Rule 2 and §4, lines 20 and 37: manual invocation does not determine privilege separation.**

**Failure scenario:** A separate account may still execute an overpowered launcher, expose diagnostics through stderr, or let an owner acting as reconciler inspect sealed records. Denying directory reads alone does not define the command’s authority.

**Minimal repair:** At sketch stage, require a constrained invocation interface and an explicit capability boundary: the owner invokes only fixed operations; a separate publisher identity receives only permitted release material; sealed verification and signing remain protected. Include logs, error output and reconciliation views. Exact OS mechanics can remain S4 work.

An owner-triggered command **can** preserve D-12 Q6(i)’s separate-publisher principle. Manual triggering does not inherently require combining publisher and `lockbox_eval`. Specify which design is proposed before asserting a different THREAT_MODEL amendment. Constitution §7 still governs every owner-visible channel.

**D20C-A-4 — BLOCKER — Rule 5 and §3, lines 23 and 32–33: mandatory eventual release is not enforced.**

**Failure scenario:** The owner never invokes the command for one evaluation. Nothing described subsequently releases it. Its pre-read record proves an evaluation occurred, but does not disclose its FAIL. The owner can also leave an ancestor unreleased while attempting a descendant read.

**Minimal repair:** Require reconciliation of every counted evaluation before accepting a complete cycle report; missing releases remain explicitly pending and block completion. Bind a manual completion/recovery procedure and descendant admission that cannot treat an unreleased ancestor as cleared.

With immutable nominees, fixed results, complete eventual reporting and enforced lineage rules, choosing release order need not introduce another scientific trial. **Selective omission is nevertheless broader than R4**, which accepts cross-family influence on owner decisions, not suppression of outcomes.

**D20C-A-5 — BLOCKER — Rules 2, 4–5, lines 20–23: post-cap signing and terminal status conflict.**

**Failure scenario:** A finished PASS is first released after day 255. Rule 2 says PASS gets an attestation; rule 5 says post-cap release is PASS/FAIL only. D-12 P-7 expressly prohibits post-cap signing. The sketch also does not restate P-6’s revision/invalidation rule preventing a previously ineffective signature from becoming effective later.

**Minimal repair:** Preserve explicit distinctions between the immutable scientific result, release, attestation effectiveness and promotion status. Post-cap results must not revive expired promotions. Bind revision/invalidation handling and signing/validation failures; those failures must never silently turn a finished PASS into FAIL. A cap warning supplements, but cannot replace, an enforced promotion guard.

**D20C-A-6 — NON-BLOCKING — Rule 1 and §3, lines 19, 31–32: clock and durability reductions are overstated.**

**Failure scenario:** Before any release, a clock rollback below `D*` permits a finish that would otherwise be late. Releasing before that finish yields DEFAULT FAIL; withholding release can yield PASS. Thus “release timing cannot change a result” requires the remaining deadline assumption, although **already released results** remain protected by the durable release entry.

The clock also supports admission/cap checks, the 30-day read cooldown and 72-hour cooling-off—not merely `R_0` and `D*`.

**Minimal repair:** Separate the clock-independent post-release invariant from deadline enforcement and elapsed-time guarantees. Preserve explicit save-counting semantics for admission and finishing. The crash obligations still include pre-read accounting, startup/read-gate dependencies, reconciliation, signing and delivery—not just worker creates and one release write.

**D20C-A-7 — NON-BLOCKING — §4, lines 35–41: the change inventory is incomplete.**

**Failure scenario:** A full proposal follows the “unchanged” list and inherits incompatible deadline fixation, signing-fault handling or scheduled-release tests.

**Minimal repair:** Expand the crosswalk:

| D-12 material | Required treatment |
|---|---|
| P-1, P-4; Q1, Q2a/Q2b, Q4/Q5 | Substantive choices can remain; preserve their disclosure/reproduction restrictions |
| P-2, P-8 | Rebind signing, validation, failures and permitted capabilities |
| P-3, Q3 | Preserve semantics; bind enforcement with unreleased ancestors |
| P-5, P-7, actors, read-order steps 2/5, record shapes | Replace affected publication/fixation contracts explicitly |
| P-6, Q6(ii) | Preserve cap intent; bind delivery, expiry and revision/invalidation interactions |
| Q6(i), R1–R4 | Reassess actor implementation and residuals; R2 remains, R3 changes, R4 does not authorize omission |
| T-1–T-8 | Review **all eight**; T-1/T-2/T-5/T-6 also change with visibility, uniqueness, crash and cap semantics |

**D20C-A-8 — NON-BLOCKING — §5, lines 47–55: comparison understates both routes’ obligations.**

**Failure scenario:** The owner interprets “none known” and “four rows” as demonstrated reductions, despite unresolved delivery and disclosure contracts. Conversely, revision 8 already routes interpretation of decided D-12 rules through Q7, so “D-12 re-decision needed: no” is too categorical.

**Minimal repair:** Compare established mechanisms and unresolved obligations. Mark revision 9 as prospective; no revision-9 document was present. Remove predictions about further review rounds. Recommend C conditionally on the bindings above.

The full proposal should retain manual release as an option, with **KEEP_BLOCKED** available until these contracts and owner decisions are resolved. The architecture offers real simplification; it does not yet justify deleting all timing, durability or availability obligations.

Read-only checks found a clean worktree and no staged changes. Frozen manifest hashes, canonical Constitution hash and embedded protocol bindings matched. Six unrelated oracle/canary working files had CRLF-related raw-hash differences; their committed blobs matched their recorded hashes. Implementation tests, lint, type and import checks were N/A for this document-only review; no platform durability claim was validated.

Nothing was written. This response remains an **uncommitted review**, not a completed repository review record.
## Prompt

# First review: D-20 option C (manual release, no automatic publisher)

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. Review `review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_MANUAL_RELEASE_SKETCH.md` (Claude Opus 5.5, commit c3fc60b), an inactive, unreviewed sketch offered to the owner as an alternative to revising `PROPOSAL_REV8.md`. Context you should read: `PROPOSAL_REV8.md`, `SOL_REREVIEW7_E68B947.md` (the open rev-8 blocker D20LR8-S-1), `../d12-proposal/OWNER_DECISION_D12.md`, `../d12-proposal/PROPOSAL_REV7.md` (P-1..P-8, R1-R4, T-1..T-8), `docs/RESEARCH_CONSTITUTION.md` (§4, §6, §7, §16, §26) and `protocols/protocol_v1.yaml` (cooling-off, PASS_FAIL_ONLY).

**IDs:** findings `D20C-A-n`. Use the letter A even if you cannot see your model variant; the caller verifies the model from the CLI header.

**Check:**
1. Rule 1: does "first release fixes the result; a finish is refused once a release entry exists" really make every shown result unchangeable without a clock invariant? Any interleaving, crash (process or machine) or restart that lets two releases or a release and a later finish disagree? What does the clock still have to be trusted for, and is that stated correctly?
2. Rule 2: can the owner-invoked release command be built so the owner learns only PASS/FAIL (and on PASS the attestation)? Is the sketch's handling (separate OS account, no sealed-directory read) sufficient at sketch stage, or is a binding needed now? Does it conflict with D-12 Q6(i), THREAT_MODEL l.9, or Constitution §7?
3. Rule 3 (72 h from the release entry, owner holds a copy): does this satisfy protocol cooling-off and the intent of D-12 P-5? Any way the store or a crash shortens actual access?
4. Rules 4-5 (cap, warning, every read released): consistent with D-12 P-6 and Q3? Can owner choice of release time, or withholding, create a selection or disclosure channel beyond the accepted R4?
5. Section 3: is the deletion list correct, and is the remaining-risk list complete (in particular, machine-level activity, durability, owner timing)? Is anything claimed removed that is not?
6. Section 4: are the listed D-12 rows that need re-decision complete and correct? Is anything listed as unchanged actually affected?
7. Section 5 comparison and recommendation: fair to revision 8/9? Any overstatement (for example "none known" blockers)?
8. Overall: is option C a sound basis for a full proposal, and what must the full proposal bind that the sketch leaves open?

**Findings:** each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair.

**Verdict:** SOUND BASIS, SOUND BASIS WITH NOTES, or NOT A SOUND BASIS.
