# Codex Astra review of D-20 option C revision C1 (c604827)

Prompt: scratchpad `optc1_astra_prompt.md` (reproduced in section "Prompt" below). Reviewer metadata from the Codex CLI header (2026-10-30): model `gpt-6-astra`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a18c88-3a32-79f0-9670-8540290934ba`, 90,545 tokens. Reviewed `OPTION_C_PROPOSAL_REV1.md` at `c604827`. Bitcoin node paused for the runs (stopped at 694,018, restarted after both). Sol and Astra ran sequentially; their outputs were written to the session scratchpad only, so neither saw the other's report. Independence check: no reference to the Sol output in the Astra CLI log.

Verdict: **FIX** (REVISION_REQUIRED): 4 BLOCKER (D20C1-A-1..4), 3 NON-BLOCKING (A-5..7), 1 QUESTION (A-8). Findings D20C1-A-1..8, no gaps.

No finding is left unrepaired by decision yet; dispositions go in revision C2.

## Report (verbatim)

**VERDICT: FIX.** Binding status: **REVISION_REQUIRED**.

C1 fixes the central shown-result race, conditional on its storage assumptions. It does not yet establish all its delivery, timing-isolation and cap claims.

Reviewed [C1](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV1.md>) byte-for-byte against `c604827`. Reviewer model identification remains for the caller to verify from the CLI header.

| Authority | Status |
|---|---|
| Constitution, protocol, threat model and schemas | Frozen and controlling |
| D-12 owner decision | Recorded; activation requires signed C2 |
| Revision 8 and C1 | Inactive proposals; this review grants no authority |

**Dispositions of every §1a entry**

| Finding | Disposition | Evidence |
|---|---|---|
| D20C-A-1 | **ACCEPT WITH NOTES** | §1.4 moves cooling-off after durable file placement and read-back. This fixes entry-versus-delivery in principle; recovery and effectiveness still need clarification below. |
| D20C-A-2 | **FIX** | No store call does not establish timing independence. §§1.6–1.7 also understate surviving delays and cap expiry: A-1/A-2 below. |
| D20C-A-3 | **ACCEPT WITH NOTES** | Fixed invocation, withheld diagnostics, separate publisher and explicit S4 gates are sufficient proposal-stage requirements. Guard-information permissions and recovery paths need consolidation. |
| D20C-A-4 | **ACCEPT WITH NOTES** | §1.5 blocks accepting an incomplete report and admitting descendants of undelivered ancestors. This enforces completeness, not unconditional eventual delivery. |
| D20C-A-5 | **FIX** | Four separate facts and immutable PASS are improvements. Delivery effectiveness across C/revision remains underspecified: A-4. |
| D20C-A-6 | **FIX** | The post-release invariant is clock-independent, but the proof wording, clock inventory and durability claims need correction: A-4/A-6. |
| D20C-A-7 | **FIX** | All named D-12 rows appear, but Constitution §13/schema consequences and retained obsolete contracts are missing: A-3/A-7. |
| D20C-A-8 | **FIX** | Conditional recommendation and review-status comparison are fair. “No slips” and the owner’s assurance against service-caused expiry are not: A-2. |
| D20LR8-S-1 | **ACCEPT WITH NOTES** | Durable release-entry precedence removes this clock-dependent shown-result race. Correct the crash case in the proof: A-6. |
| D20LR8-S-2 | **ACCEPT** | Q7 uses “additional durable evidence and design work,” removing the unsupported record-count claim. |
| D20LR8-S-3 | **ACCEPT** | §1.1 explicitly gates S4 on a named reconciler and a view that cannot disclose sealed or undelivered results to the owner. |

**The central proof and consumer audit**

The shown-result invariant holds under the stated durable-before-use, exclusive-lock and fail-closed recovery assumptions:

- A surviving finished record is made durable before release uses it; an absent record contributes nothing.
- A release is durable before any result is exposed.
- Every subsequent finish finds that release and refuses.
- Two concurrent release requests serialize and return the same release entry.
- A crash between release and delivery cannot change the result: recovery delivers that entry.
- A lost, previously unshown release may be recreated; a partial index tail stops processing.

This establishes safety, not bounded delivery time.

| Quantity / consumer | Units and required binding | Assessment |
|---|---|---|
| `D*` — counted finish | UTC seconds; `t_f < D*`, plus no existing release | Q7 must retain the pre-deadline-check convention and its crash qualification. |
| `C` — admission, signing, effectiveness, decision | UTC seconds; distinct boundaries | Admission is carried forward; effectiveness needs A-4. |
| `R_0` — earliest release | UTC seconds; store refuses earlier release | Store gate survives; publisher isolation/skew claims need A-1. |
| Cooldown | 30 days | Still clock-dependent. |
| `delivered_at` — cooling-off | UTC seconds; at least 259,200 seconds of established access | Sound lower bound under trusted elapsed time and an enduring owner-readable copy. |
| Attestation | Signed binding required by Constitution §13 | C1 omits a required binding: A-3. |
| Reporting and lineage | Every counted read accounted for; FAIL descendants barred | §1.5 is sound with delivery-status precedence and report/termination distinction. |

**D20C1-A-1 — BLOCKER — §1.2 step 1; §1.6 item 1; TC-1: no store contact does not prove no sealed-work dependence.**

**Failure scenario:** A publisher answering locally can still share CPU, disk or a request queue with sealed work. An older evaluation’s release request can block a serialized publisher while a younger evaluation’s `NOT_YET` request waits behind it. Neither requires the younger request to contact the store. Revision 8 explicitly acknowledged shared-resource contention; C1 establishes no replacement isolation.

The 60-second fault claim also fails in one concrete interleaving: publisher time is `R_0+60`, store time is `R_0−1`; the request waits two seconds for the lock, then passes the store check at `R_0+1`. No refusal logs the excessive skew.

**Minimal repair:** Claim only removal of this request’s direct store-lock acquisition. Either establish independent refusal handling, or disclose queue/resource dependence before `R_0` in R5c and QC3. State the required clock-skew premise explicitly. Bind recovery of the publisher’s `R_0` copy after `begin_read` commits but its reply is lost; recovery must not silently invalidate the early-refusal claim.

**D20C1-A-2 — BLOCKER — §§1.6–1.7, §2 T-4, §3 comparison and QC3: service delays and cap expiry remain possible.**

**Failure scenario:** The owner requests at `C−73 h`. A shared-lock stall, startup reconciliation, filesystem outage or delivery failure delays attestation delivery by 48 hours. Delivery occurs at `C−25 h`; the earliest decision is **`C+47 h`**. Service delay has exhausted promotion slack.

Deleting daily release slots removes day-sized scheduling increments. It does not bound delays. The residual also omits reconciliation, startup, replay/index operations, delivery appends, shared-resource contention and signing activity affecting another evaluation. A uniform release path does not prove equal outage effects across outcomes.

**Minimal repair:** Restore these residuals and service-caused expiry to the disclosure, proposed §7 exception and comparison. Remove “small,” “never delayed by days,” “none expires because of the service,” and “only” owner timing/signing can delay cooling-off. Preserve the narrower, supportable claim: **there is no daily missed-slot mechanism**. Do not assert that timing cannot distinguish PASS from performance FAIL without evidence.

**D20C1-A-3 — BLOCKER — §1.3 line 124 and §2 crosswalk: the attestation drops a frozen mandatory binding.**

**Failure scenario:** C1 produces an otherwise valid certificate without `cooling_off_start`. It fails the frozen [attestation schema](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/schemas/attestation.schema.json>) and Constitution §13, which requires the attestation to bind cooling-off start. A signed release-entry hash cannot itself bind a delivery timestamp created later.

**Minimal repair:** Either preserve a conforming signed binding and enforce the delivery-based lower bound additionally, or explicitly propose the necessary Constitution §13 and schema changes through C2. Update the consumer crosswalk and owner questions. “P-1 unchanged in substance” does not cover this consequence.

**D20C1-A-4 — BLOCKER — §§1.3–1.4, C5/C8/C9 and Q7: effectiveness has no complete cap/revision commit rule.**

**Failure scenario:** An attestation is copied and read back at `C−1 second`; its delivery entry becomes durable at `C+1 second`. The timestamp says delivery preceded C, while C8 says effectiveness begins only when the delivery entry is durable. The proposal does not resolve which event controls eligibility.

Similarly, a revision can occur after the delivery path starts but before its entry becomes durable. The signer’s earlier revision check is insufficient. C9 states the desired outcome, but `record_delivery` has no specified atomic check against revision/invalidation or permanent void status. Recovery of a whole, previously un-fsynced C5 entry compounds the ambiguity.

**Minimal repair:** Define one authoritative effectiveness transition, its ordering against revision/invalidation and C, and restart treatment of uncertain completion. Serialize the relevant checks and record changes. Route any pre-deadline-check convention through the owner explicitly; Q7 cannot simply say only admission and finishing need save semantics while leaving effectiveness unresolved. Specify signing’s cap-check point too.

The result must remain PASS throughout; an ineffective certificate cannot revive promotion.

**D20C1-A-5 — NON-BLOCKING — §§1.3–1.4 and §§1.8–1.9: delivery recovery and concurrent requests need explicit idempotency.**

**Failure scenario:** Two requests obtain the same release entry, independently copy the same delivery and append different delivery timestamps. Alternatively, C4 leaves the destination file present without a delivery entry, or C8 leaves a certificate present without certificate delivery. Blindly repeating exclusive creation or signing encounters an existing object; the draft does not specify the normal recovery branch.

**Minimal repair:** Bind separate identities for result delivery and attestation delivery; verify and reuse existing matching files; define the authoritative delivery record and immutable cooling-off start. Resume delivery of an existing valid certificate instead of repeatedly asking to sign. Reconcile “any failure means no delivery entry” with C5’s surviving-whole-entry case.

Add discriminating tests for concurrent requests, existing-file recovery, C7–C9, cap crossing during delivery, revision during delivery, and owner readability. Require durable result delivery before starting signing. Resolve code precedence between a delivered PASS, `ATTESTATION_PENDING`, and `STOPPED`.

**D20C1-A-6 — NON-BLOCKING — §1.2 proof, clock inventory and step-5 explanation: qualifications remain missing.**

**Failure scenario:** F acquires the lock first, links its finished record, then crashes before directory fsync. The record may survive and become durable through E’s fsync, or disappear. Therefore line 96’s claim that F’s record was durable **before E’s lookup** is false, although the overall invariant survives.

Also, `D* ≤ R_0−12 h` separates clock-check thresholds; it does not bound the finish’s lock-hold duration.

**Minimal repair:** Use the recovery-aware proof above. List publisher-clock/skew dependence, signing/effectiveness/decision cap checks, delivery timestamp provenance and elapsed-time trust across restarts. State that “later timestamp” and 72 hours of actual access require those clock assumptions.

Routing D-12 step 5 to Q7 is correct. Retain revision 8’s qualification: a pre-deadline finish still being saved may survive or be lost after the deadline. “After `D*` no new finish counts” must mean no newly qualifying clock check, not that persistence is already settled.

**D20C1-A-7 — NON-BLOCKING — delta inheritance, capability table and §2: obsolete dependencies remain designated unchanged.**

**Failure scenario:** An implementer follows retained B3/B3a/B4.3 text and encounters `guard_state`, `visible_from`, scheduled-release comparisons and compromise reconciliation requiring `visible_from = cooling_off_start`. C1 deletes those mechanisms.

The signer’s listed inputs also do not identify how it receives authoritative revision/cap state and pre-read identities; the publisher still must perform P-8 identity comparisons.

**Minimal repair:** Explicitly supersede the affected inherited clauses, including compromise reconciliation and barred-descendant visibility. Specify narrowly filtered, authenticated guard information and permitted pre-read metadata without exposing sealed diagnostics. Carry these into the consolidated S4 text.

The separate publisher itself is appropriate and matches D-12 Q6(i) and the intended threat-model amendment.

**D20C1-A-8 — QUESTION — D20L-82: do not adopt the proposed wait rule as written.**

**Failure scenario:** Waiting for another read to close exposes its closing time and can delay release for days. A check followed by release also races a new admission unless coordinated. Closing a read does not necessarily stop late writes, reconciliation or other resource contention.

**Minimal repair:** Keep this as an alternative requiring a separate scheduling/isolation design and explicit cap cost. It does not establish removal of R5c merely by waiting. Prefer accurate residual disclosure unless the owner chooses stronger separation.

**Completion, classifications and remaining decisions**

§1.5 closes the identified omission and lineage gaps at proposal stage. `PENDING_RELEASE` and `ANCESTOR_UNRELEASED` can depend only on already-public accounting/delivery facts. Test that every undelivered ancestor produces the same reason regardless of its hidden result. Report incompleteness must not postpone mandatory cycle termination, invalidation or cap effects.

For D20L-76..82:

- **76:** Proposal-stage boundary repair is acceptable; S4 remains mandatory.
- **77:** Core cooling-off repair accepted conditionally; delivery recovery remains.
- **78:** Correctly BLOCKER/partial, but the residual includes pre-`R_0` dependence too.
- **79:** Repaired for complete-report acceptance and descendant admission.
- **80:** Remains open at BLOCKER pending A-4.
- **81:** Non-blocking proof corrections remain; broader overclaims are blocking under A-2.
- **82:** Correctly QUESTION; not recommended as drafted.

Option C remains a viable simplification. Keep adoption blocked pending these repairs and the required owner/human decisions; this review does not require returning to revision 8.

Read-only validation found C1 identical to `c604827`; working and staged diffs were empty. Independent arithmetic confirmed the 47-hour cap overrun above. A read-only Python equivalent of `review/task6/verify_frozen.ps1` passed the 28-file trusted inventory/byte checks, 14 sidecars, Constitution canonical hash and manifest/protocol bindings; `pwsh` itself was unavailable.

Implementation tests, lint, type and import checks were N/A for this proposal review. Platform durability and timing isolation remain unverified. No repository files were written; this response is an **uncommitted review**, not a completed repository review record.
## Prompt

# Review: D-20 option C, revision C1 (release on request)

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. Review `review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV1.md` (Claude Opus 5.5, commit c604827), a delta on `PROPOSAL_REV8.md`. It answers `ASTRA_OPTION_C_REVIEW_C3FC60B.md` (D20C-A-1..8, on the sketch `OPTION_C_MANUAL_RELEASE_SKETCH.md`) and `SOL_REREVIEW7_E68B947.md` (D20LR8-S-1..3). Context: `PROPOSAL_REV8.md`, `../d12-proposal/OWNER_DECISION_D12.md`, `../d12-proposal/PROPOSAL_REV7.md` (P-1..P-8, R1-R4, T-1..T-8), `docs/RESEARCH_CONSTITUTION.md` (§4, §5, §6, §7, §16, §26), `docs/THREAT_MODEL_v1.md`, `protocols/protocol_v1.yaml` (cooldown, cooling-off, PASS_FAIL_ONLY).

**IDs:** findings `D20C1-A-n`. Use exactly that prefix even if you cannot see your model variant; the caller verifies the model from the CLI header.

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
