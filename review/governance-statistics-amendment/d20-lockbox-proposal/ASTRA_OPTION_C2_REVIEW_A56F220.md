# Codex Astra re-check of D-20 option C revision C2 (a56f220)

Prompt: scratchpad `optc2_astra_prompt.md` (reproduced in section "Prompt" below). Reviewer metadata from the Codex CLI header (2026-10-30): model `gpt-6-astra`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a18c9f-7db6-7a63-8002-ad7883d6f790`, 92,791 tokens. Reviewed `OPTION_C_PROPOSAL_REV2.md` at `a56f220`. Bitcoin node paused for the runs (stopped at 696,568, restarted after both). Sol and Astra ran sequentially with outputs in the session scratchpad only.

Verdict: **FIX** (REVISION_REQUIRED): 2 BLOCKER (D20C2-A-1, A-2), 4 NON-BLOCKING (A-3..6). Findings D20C2-A-1..6, no gaps.

No finding is left unrepaired by decision yet; dispositions go in revision C3.

## Report (verbatim)

**VERDICT: FIX.** Binding status: **REVISION_REQUIRED**.

C2 repairs the central result invariant and restores the required signed cooling-off field. Two issues remain blocking: the unconditional completion guarantee and the visibility of results following non-calendar termination. The other findings need clarification or narrower claims, not additional machinery.

Reviewed [C2](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV2.md) byte-for-byte against `a56f220`, independently of other C2 reviews. Reviewer model identification remains for the caller to verify.

| Authority | Status |
|---|---|
| Constitution, protocol, threat model, schema | Frozen and controlling |
| D-12 owner decisions | Recorded; binding through the signed amendment |
| Revision 8 and C2 | Inactive proposals |
| This review | Advisory; grants no acceptance or activation |

**Disposition of every C2 §1a row**

Line references below are to C2 unless otherwise stated.

| Prior finding | Assessment | Evidence |
|---|---|---|
| D20C1-S-1 / D20C1-A-5 | **ACCEPT WITH NOTES** | Separate delivery identities, verify-and-reuse, `L_pub`, owner-account copy and read-back repair the identified recovery/access problems (§1.4). The timestamp assertion remains conditional on clock trust: A-4 below. |
| D20C1-S-2 / D20C1-A-1 | **ACCEPT** | §§1.2 and 1.7 explicitly retain shared-resource and recovery dependence. Same-host clock binding removes the former two-clock skew scenario. |
| D20C1-S-3 / D20C1-A-4 | **ACCEPT WITH NOTES** | Effectiveness and revisions now serialize through the index; Q7 explicitly includes effectiveness. Physical durability can nevertheless occur after C, and some permanently uncertifiable requests remain “pending”: A-3/A-6. |
| D20C1-S-4 | **FIX** | Automatic backstop and pending accounting address voluntary omission, but the completion guarantee and report visibility remain defective: A-1/A-2. |
| D20C1-S-5 / D20C1-A-2 | **ACCEPT WITH NOTES** | Unbounded delays, pre-`R_0` dependence, possible performance hints, expiry and stopped state are disclosed (§§1.7–1.8, QC3). Align the meaning of `STOPPED`: A-6. |
| D20C1-S-6 / D20C1-A-6 | **ACCEPT WITH NOTES** | Recovery-aware proof, step 2a, rev-8 qualification and deletion of T-4’s equal-outage claim are correct. Additional boundary tests and qualifications are identified below. |
| D20C1-A-7 | **ACCEPT WITH NOTES** | §1.10 addresses the principal obsolete contracts, including compromise reconciliation and descendant visibility. Some inherited references remain: A-5. |
| D20C1-S-7 / D20C1-A-8 | **ACCEPT** | D20L-82 is expressly not adopted; separate isolation design and cap cost remain necessary. |
| C1 D20L-76..81 | **ACCEPT WITH NOTES** | Superseding them with D20L-83..89 is appropriate, but “repaired” is premature for D20L-87 and overstates some guarantees. |
| D20C1-A-3 — omitted from §1a | **ACCEPT** substantively | §1.5 restores signed `cooling_off_start`. Add its missing disposition row; it is discussed elsewhere but absent from the purported complete table. |

**Findings**

1. **D20C2-A-1 — BLOCKER — §1.6, especially lines 207–212; QC1. Unsupported completion guarantee.**

   **Scenario:** A finish holds `L_store` beyond `C + 14 days`, or a corrupt RESULT bundle causes an unresolved §26 stop. Both are expressly permitted failure cases. Backstop retries cannot produce a release by the claimed deadline. Permanent unavailability also defeats unconditional eventual release.

   **Minimal repair:** Say the backstop *attempts* automatic release and removes dependence on an owner request; eventual completion requires recovery and successful reconciliation. Keep incomplete reports visibly incomplete without postponing termination. Remove “guarantees” and unconditional “nothing can stay unreleased.”

   Also correct C3: a backstop restricted to reads **without a release entry** cannot resume outbox creation for an already released read. Either narrow C3’s claim or include missing outboxes in recovery.

2. **D20C2-A-2 — BLOCKER — §1.1 reader row, §1.6 report claims. Non-calendar termination has no matching report visibility rule.**

   **Scenario:** A revision ends the cycle before calendar termination. The backstop releases an undelivered result, and §1.6 says the cycle report shows it. The reader row nevertheless withholds it until RESULT delivery or **calendar** termination. Neither necessarily occurs for that terminated cycle; later closed-cycle requests may also be refused under line 83.

   **Minimal repair:** Define report visibility for every relevant termination cause, including released results that arrive after termination. Align the reader row and closed-cycle access rule with that report contract. No additional diagnostic channel is needed: expose the already permitted result and accounting.

3. **D20C2-A-3 — NON-BLOCKING — §§1.4–1.5, Q7, TC-4. Distinguish check-time effectiveness from physical completion.**

   **Scenario:** The effectiveness clock check occurs at `C−1 second`; the append becomes durable at `C+1 second`. Alternatively, its whole unfsynced line survives and is recovered after C. Q7 accepts this by convention. Therefore “no signature becomes effective after C” is true only in the defined accounting sense, not as a physical durability guarantee.

   Q7’s “while nobody can read” is also too broad: the owner already possesses the attestation bytes before this append. What remains unavailable is the authoritative effective-entry confirmation.

   **Minimal repair:** State these distinctions explicitly, as §1.3 already does for finishing. Add tests crossing C **after the effectiveness check**, plus whole/lost/partial recovery after C. Current C10 primarily covers crossing before the delivery decision.

   Index ordering against revision is sound: a later revision cannot overtake an earlier append under the same lock, and durable-before-use protects the recovered ordering.

4. **D20C2-A-4 — NON-BLOCKING — §1.4 line 155, §1.3 clock inventory, TC-3/TC-7. Event order is established; unconditional timestamp order is not.**

   **Scenario:** The owner copy becomes durable, then the host clock steps backward before `record_delivery`. The recorded timestamp can precede the copy’s actual creation time despite correct execution order. A forward clock jump during cooling-off can also satisfy the nominal 72-hour guard early.

   **Minimal repair:** Qualify “never earlier” and “72 hours of actual access” with R3’s accurate elapsed-clock assumption, including forward jumps. TC-3 proves operation order, not elapsed-time accuracy. No new clock mechanism is required merely to disclose this assumption.

   Under that assumption, enduring owner access and the specified fsync semantics, crash/retry and concurrency do not shorten cooling-off.

5. **D20C2-A-5 — NON-BLOCKING — §1.10 and inherited tests/capabilities. Supersession is not fully consolidated.**

   **Scenario:** An implementer follows rev-4 lines 95–97’s replacement signer guard, rev-3 line 204’s `guard_state` test, or retained rev-8 T-S2 calls to `state`. Those operations no longer exist. The replacement capability table also omits the replay role while B4.4 remains unchanged.

   **Minimal repair:** Explicitly supersede the amended signer guard and obsolete test calls; retain or identify the replay capability. Add D20C1-A-3 to §1a and correct its superseding-findings section reference. Consolidate these references without adding mechanisms.

6. **D20C2-A-6 — NON-BLOCKING — response codes, §§1.5 and 1.7–1.8. Some status descriptions do not match their paths.**

   **Scenario:** Signing fails before producing a file; C or a revision then passes. A new `sign_permit` is refused, so ATTESTATION delivery never runs and never writes VOID. Line 182 can therefore keep returning `PASS_CERTIFICATE_PENDING` indefinitely although certification is impossible.

   Separately, `STOPPED` includes **any request error**, whereas QC3 describes an incident stop.

   **Minimal repair:** Use the existing uncertifiable status for terminal cap/revision refusal, without requiring a new signed artifact or record mechanism. Explain that `STOPPED` can represent a refused/failed request as well as an active service incident, and align §1.8 accordingly. Preserve immutable PASS.

**Remaining checks**

The §1.3 proof holds under the stated storage assumptions: recovery either preserves and fsyncs the finished record before use or finds it absent; a durable release prevents later finishing through step 2a. Concurrent releases return that entry. This establishes result safety, not bounded completion.

| Consumer | Assessment |
|---|---|
| Finish deadline `D*` | Pre-deadline clock check plus step 2a; rev-8 persistence qualification correctly retained and routed to Q7 |
| Earliest release `R_0` | Store refuses earlier release; revision-triggered backstops must respect this too |
| Cooling-off | RESULT delivery plus 259,200 seconds; later signing does not itself shorten result access |
| Constitution §13 / schema | Restored signed field conforms; neither requires the certificate itself to exist throughout those 72 hours |
| P-6 revision boundary | Effective-before-revision certificates remain effective; later effectiveness is refused by index order |
| PASS/FAIL | Signing refusal, expiry and VOID do not convert a released PASS into FAIL |
| Lineage | `ANCESTOR_UNRELEASED` is result-independent; released FAIL bars descendants |
| Backstop residual | Automatic work adds contention/latency, already within the disclosed residual; its report visibility needs A-2 |

The comparison is broadly fair. QC3 is materially improved. QC1 should replace “nothing … can be asked” with “no result is released before seven days”: early requests and pending accounting exist. Q7 should state its durability cost directly.

Read-only validation passed: C2 matches `a56f220`; 28 protected inventory/byte checks, 14 sidecars, Constitution canonical hash, manifest and protocol bindings. Independent arithmetic confirmed the `C+47 h` expiry example. Git working/staged checks were empty, with a global-ignore permission warning.

Implementation tests, lint, type and import checks were N/A for this document-only review. Platform durability remains unverified. **Adoption remains blocked. Nothing was written; this is an uncommitted review response, not a completed repository review record.**
## Prompt

# Re-check: D-20 option C, revision C2

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. Re-check `review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV2.md` (Claude Opus 5.5, commit a56f220). It replaces C1 whole and is a delta on `PROPOSAL_REV8.md`. It answers `SOL_OPTION_C1_REVIEW_C604827.md` (D20C1-S-1..7) and `ASTRA_OPTION_C1_REVIEW_C604827.md` (D20C1-A-1..8). Review independently of any other C2 review; none is in the repository. Context: `PROPOSAL_REV8.md`, `PROPOSAL_REV3.md` l.176-220 and l.305-311, `PROPOSAL_REV4.md` l.92-110 and l.175, `../d12-proposal/OWNER_DECISION_D12.md`, `../d12-proposal/PROPOSAL_REV7.md` (P-1..P-8, R1-R4, T-1..T-8), `docs/RESEARCH_CONSTITUTION.md` (§5, §6, §7, §13, §16, §26), `schemas/attestation.schema.json`, `docs/THREAT_MODEL_v1.md`, `protocols/protocol_v1.yaml`.

**Direction:** simplify rather than patch; claim only what is true and testable. Prefer flagging a residual for honest disclosure over demanding new mechanism, unless the claim made is false or a frozen rule is broken.

**IDs:** findings `D20C2-A-n`. Use exactly that prefix even if you cannot see your model variant; the caller verifies the model from the CLI header.

**Check:**
1. For EVERY C2 disposition of the C1 findings (§1a), say ACCEPT, ACCEPT WITH NOTES or FIX, with evidence. You may check the other reviewer's rows.
2. §1.3: the recovery-aware proof and step 2a; the clock list; rev 8's qualification and the Q7 routing.
3. §1.4: delivery idempotency, `L_pub`, owner-account read-back; is `delivered_at` truly never earlier than the owner's durable copy under every crash and concurrency case? Is the "uncertain completion" (whole-but-unfsynced entry) handling consistent with rev 8 and Q7?
4. §1.5 (focus): `cooling_off_start` = RESULT `delivered_at`, signed after it; conformance with Constitution §13 and the frozen schema; `sign_permit`; effectiveness as one append with VOID; index-ordered revision entries; P-6 l.245 ("attested nominee is unaffected"). Can a signature become effective after C or after a revision, can cooling-off give under 72 h of actual access, or can a PASS become FAIL?
5. §1.6: backstop at `R_0 + 7 days` and at revision/invalidation/termination; pending list; completion; `ANCESTOR_UNRELEASED`. Does the backstop add a channel? Is the reader row consistent with the cycle report showing backstop-released results?
6. §1.7-§1.8: is the residual now complete and accurately stated, and does the §7 row cover exactly it?
7. §1.1 codes and capabilities, §1.9 crash rows and tests, §1.10 superseded clauses (complete?), §2 crosswalk, §3 comparison, §4 owner questions (fair and plain for a non-statistician).

**Findings:** each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
