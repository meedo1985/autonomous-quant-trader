# Codex Sol review of D-20 option C revision C1 (c604827)

Prompt: scratchpad `optc1_sol_prompt.md` (reproduced in section "Prompt" below). Reviewer metadata from the Codex CLI header (2026-10-30): model `gpt-6-sol`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a18c85-ad8e-7c00-8222-9b47c91dd867`, 63,075 tokens. Reviewed `OPTION_C_PROPOSAL_REV1.md` at `c604827`. Bitcoin node paused for the runs (stopped at 694,018, restarted after both). Sol and Astra ran sequentially; their outputs were written to the session scratchpad only, so neither saw the other's report. 

Verdict: **FIX**: 5 BLOCKER (D20C1-S-1..5), 1 NON-BLOCKING (S-6), 1 QUESTION (S-7). Findings D20C1-S-1..7, no gaps.

No finding is left unrepaired by decision yet; dispositions go in revision C2.

## Report (verbatim)

## Verdict: FIX

C1 is an inactive proposal, not an accepted binding. The frozen [Constitution](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/docs/RESEARCH_CONSTITUTION.md:72>) and [protocol](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/protocols/protocol_v1.yaml:73>) control; the [D-12 owner decision](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/OWNER_DECISION_D12.md:20>) remains conditional on signed C2 wording. The review below concerns [C1](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV1.md>). It approves no amendment or implementation.

**The central result proof is sound with a wording repair.** Once the first release entry is durable, a later finish cannot change its result: the two operations serialize under `L_store`, and a finish that follows the entry refuses. Concurrent releases return that same entry. On a crash after a finished-record link but before its directory fsync, however, the record need not have been durable *before* release looked it up. Release’s post-lookup fsync can make a surviving link durable before use. A lost link yields the default, and no result was shown before release. This depends on rev 8’s durable-before-use rule, fail-closed recovery, and its explicitly unverified filesystem and lock assumptions. D-12 step 5’s proposed save-point reading is correctly sent to Q7.

### §1a disposition check

| Prior finding | Assessment | Evidence |
|---|---|---|
| D20C-A-1 | **FIX** | §1.4 moves the clock start to delivery, but publisher read-back does not establish owner access; crash replay is incomplete. S-1. |
| D20C-A-2 | **FIX** | Local `NOT_YET` removes the store-lock wait only under a bounded clock skew; shared-machine timing and later waits remain. S-2, S-5. |
| D20C-A-3 | **ACCEPT WITH NOTES** | A fixed command, separate publisher, withheld diagnostics and an S4 reconciler gate are adequate proposal boundaries. S4 must also constrain ID authorization and owner-file access. |
| D20C-A-4 | **FIX** | Completion and lineage gates expose pending reads, but do not ensure a release at cycle termination. S-4. |
| D20C-A-5 | **FIX** | The four facts are useful; signing, delivery, cap and revision are not ordered atomically. S-3. |
| D20C-A-6 | **ACCEPT WITH NOTES** | The *post-release result* is clock-free. The clock list omits the publisher clock and effectiveness boundaries; the crash table omits decisive retries. S-1–S-3, S-6. |
| D20C-A-7 | **ACCEPT WITH NOTES** | All D-12 rows and T-1–T-8 are mapped, but the claimed replacement tests and equal-outage behavior need correction. S-6. |
| D20C-A-8 | **FIX** | §3 and QC3 still claim no service-caused day-scale delay or cap expiry despite unbounded waits. S-5. |
| D20LR8-S-1 | **ACCEPT WITH NOTES** | The published-result clock invariant is replaced by release-entry serialization. Before release, deadline semantics still trust the clock; Q7 remains necessary. |
| D20LR8-S-2 | **ACCEPT** | Q7 removes the unsupported “one more record per save” claim. |
| D20LR8-S-3 | **ACCEPT WITH NOTES** | S4 explicitly gates the reconciler’s identity and view. It must be resolved before access design is adopted, as C1 says. |

### Findings

**D20C1-S-1 — BLOCKER — §1.4, C4–C6, TC-3: delivery is neither recoverably idempotent nor proven accessible.** A crash after the owner-file link but before its delivery entry can leave the final name present. The next create-without-replace fails; mapping that error to `STOPPED` can strand a PASS indefinitely. Two concurrent requests can race the same way or create duplicate delivery entries with different times. Separately, publisher read-back proves its own access, not the owner’s: if the owner first gains access 24 hours later, a decision at `delivered_at + 72 h` provides only **48 hours of actual access**. The no-login rule can itself restrict access if the owner directory is on that machine. **Repair:** define one idempotent result delivery and one attestation delivery per evaluation, including existing-file verification, unique index entries and concurrent retries. Establish owner-account access to a durable copy before starting its 72 hours; define recovery and outages of that access path. Test those cases.

**D20C1-S-2 — BLOCKER — §1.2 step 1, §1.6 item 1: `NOT_YET` is not independent of sealed work as claimed.** The 60-second margin has no stated bound on publisher/store skew. A fast publisher can enter the store before its `R_0` and wait on a finish. Even when it never calls the store, a publisher sharing CPU, disk or scheduling with sealed work can take a variable time to return `NOT_YET`. Restart recovery of its own `R_0` copy is unspecified. **Repair:** bind durable local `R_0` recovery, a verified skew bound or fail-closed timing rule, and either isolate the pre-`R_0` response path or disclose its remaining timing channel in QC3 and §7. Do not describe a logged clock fault as eliminating the hint.

**D20C1-S-3 — BLOCKER — §1.3–§1.4, C8–C9: attestation effectiveness can cross a cap or revision.** A signer may check `clock < C`, stall, and sign after C. A revision can occur after its “no revision” check but before attestation delivery; the proposed effectiveness rule could then activate a signature that was ineffective at revision. The signer’s stated view also lacks the revision information needed for its check. “No attestation” versus “effective or void” omits a signed, pending-delivery state. **Repair:** define a serialized, durable effectiveness decision that checks cap and revision at the same boundary as attestation delivery, with fail-closed restart behavior. Define the signing cutoff separately, and test cap/revision interleavings. Route any new save-point interpretation to the owner with Q7. Keep the PASS result immutable through every refusal or mismatch.

**D20C1-S-4 — BLOCKER — §1.5: the rules detect omission but do not guarantee eventual release.** An owner can leave a counted read pending, never request cycle completion, and reach day 255 or invalidation without a delivered result. `ANCESTOR_UNRELEASED` prevents a descendant read but cannot release the ancestor. The owner-visible pre-read and pending-report path is also not specified by §1.1. **Repair:** bind reconciliation and disposition of every counted ID at calendar termination, revision and invalidation, including who receives the pending list and what happens if the owner never requests release. Preserve counts and the recorded outcome; do not treat an incomplete cycle as a completed one.

**D20C1-S-5 — BLOCKER — §1.6–§1.7, §3, QC3: the residual is understated.** After `R_0`, startup, reconciliation, another `begin_read`, read-gate checks, a stalled finish, shared resource contention, store outage and delivery failure can delay an answer without a bound. Some can consume day-255 slack. A corrupt RESULT bundle yields owner-visible `STOPPED` instead of a default FAIL, an explicit fault-dependent code that the proposed §7 *timing-only* exception does not clearly cover. The phrase “small hints” also lacks evidence: runtime may differ between PASS and performance FAIL. **Repair:** enumerate all callable and operational paths, remove the “cannot delay by days/cause expiry” claims, and put the actual observable codes and timing risks to the owner in QC3 and the proposed §7 wording. Keep diagnostics withheld and authorize evaluation IDs at the command boundary.

**D20C1-S-6 — NON-BLOCKING — §1.2 proof, §1.8–§1.9 and §2: proof wording and tests overstate coverage.** Replace “F’s record was durable before E’s lookup” with the post-lookup-fsync case above. Add crash/retry tests for an existing delivery filename, concurrent release and delivery calls, revision/cap races, owner-account access, and publisher restart with its local `R_0`. TC-3’s publisher read-back assertion cannot establish actual owner access. The T-4 crosswalk’s “outage delays a request alike for every outcome” is not established by the proposed paths. **Repair:** amend those statements and make the tests discriminate the named failure cases.

**D20C1-S-7 — QUESTION — §5, D20L-82: keep it a question; do not adopt the proposed wait.** Waiting until no other read is open can itself reveal when that read ends and can delay a requested release arbitrarily, including past the cap. It adds a scheduling rule without closing the shared-machine channel. Consider it only as part of a separately reviewed isolation design.

D20L-76–82 identify the right topics, but **76, 77, 78, 79 and 80 are not fully repaired** for the scenarios above; 81 is repaired only for the narrow post-release invariant. C1’s §2 crosswalk is broad enough as an inventory, while §3, §4 and the §7 row need the corrections above before a non-statistician owner can decide on their stated costs.

This was read-only. No implementation or platform durability test was run; the working tree remained clean. This response is an uncommitted review record.
## Prompt

# Review: D-20 option C, revision C1 (release on request)

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. Review `review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV1.md` (Claude Opus 5.5, commit c604827), a delta on `PROPOSAL_REV8.md`. It answers `ASTRA_OPTION_C_REVIEW_C3FC60B.md` (D20C-A-1..8, on the sketch `OPTION_C_MANUAL_RELEASE_SKETCH.md`) and `SOL_REREVIEW7_E68B947.md` (D20LR8-S-1..3). Context: `PROPOSAL_REV8.md`, `../d12-proposal/OWNER_DECISION_D12.md`, `../d12-proposal/PROPOSAL_REV7.md` (P-1..P-8, R1-R4, T-1..T-8), `docs/RESEARCH_CONSTITUTION.md` (§4, §5, §6, §7, §16, §26), `docs/THREAT_MODEL_v1.md`, `protocols/protocol_v1.yaml` (cooldown, cooling-off, PASS_FAIL_ONLY).

**IDs:** findings `D20C1-S-n`. Use exactly that prefix even if you cannot see your model variant; the caller verifies the model from the CLI header.

**Check:**
1. For every disposition in §1a, say ACCEPT, ACCEPT WITH NOTES or FIX, with evidence.
2. §1.2 (focus): is the clock-free proof that a shown result cannot change correct under every interleaving, process or machine crash and restart, including a crash between the release entry and delivery, and two concurrent requests? Is the list of what still trusts the clock complete and correctly stated? Is the D-12 step-5 reading correctly routed to Q7?
3. §1.2 step 1 and §1.6: does a `NOT_YET` answered from the publisher's copy of `R_0` truly avoid any dependence on sealed work? Is the 60 s margin and the fault path sound? Is the after-`R_0` residual list complete (including other reads, reconciliation, startup, delivery and signing)?
4. §1.1: is the owner capability boundary (fixed operation, four codes, withheld logs/stderr/views, no-login rule, reconciler S4 gate) sufficient at proposal stage? Does keeping the separate publisher match D-12 Q6(i) and THREAT_MODEL l.9?
5. §1.3-§1.4: signing after release, four separate facts, no signing from C, P-6 l.245 handling; delivery read-back, `delivered_at` never early, cooling-off from attestation delivery, promotion guard. Do these meet protocol cooling-off (72 h) and D-12 P-5/P-6 intent? Any way to get less than 72 h of actual access, a signature becoming effective after C or after a revision, or a PASS turned into FAIL?
6. §1.5: completion and `ANCESTOR_UNRELEASED`. Does it close omission and lineage gaps without new channels? Consistent with P-3, Q2b, Q3?
7. §1.7 §7 row: accurate and minimal for the residual? §1.8 crash rows and §1.9 tests: complete and discriminating?
8. §2 crosswalk, §3 comparison and §4 owner questions: complete, fair, plain enough for a non-statistician owner, no overstatement?
9. New findings D20L-76..82: classification correct? Should D20L-82 (wait until no other read is open) be adopted?

**Findings:** each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
