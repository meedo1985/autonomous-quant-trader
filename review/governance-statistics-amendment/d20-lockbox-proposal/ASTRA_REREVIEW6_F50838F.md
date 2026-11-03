# Codex Astra re-check of D-20 lockbox revision 7 (f50838f)

Prompt: `REREVIEW6_PROMPT.md`, prefixed with "Do NOT open or read SOL_REREVIEW6_F50838F.md or any other SOL_* file in that folder; review independently. Use finding IDs D20LR7-A-n." Reviewer metadata from the Codex CLI header (2026-10-27): model `gpt-6-astra`, provider openai, sandbox read-only, reasoning effort high, Codex CLI v0.164.0, session id `01a17c7b-2544-7663-ba19-fe4c77c7502c`, 76,449 tokens. Reviewed HEAD `103b5df`. A first run was killed by the Claude Code low-memory reaper before producing output; this record is the complete second run (Bitcoin node paused to free memory). Independence check: the only `SOL_REREVIEW6` hit in the CLI log is the prompt prefix.

Verdict: **FIX** (3 BLOCKER, 3 NON-BLOCKING). Findings D20LR7-A-1..6. Dispositions: D20LR6-A-1 ACCEPT WITH NOTES; D20LR6-A-2 FIX (-> A-1, A-4); D20LR6-A-3 ACCEPT WITH NOTES; D20LR6-A-4 ACCEPT WITH NOTES (-> A-5); D20LR6-A-5 ACCEPT WITH NOTES. E7-1, E7-3, E7-4 confirmed; E7-2 D-12 line 92 confirmed.

Convergence with Sol (`SOL_REREVIEW6_F50838F.md`): A-1 = S-2 (link-after-fsync race on selected sealed name); A-2 = S-3 (outage entry undercounts / crash gap); A-3 = S-5 (narrow the impossibility claim; Astra BLOCKER, Sol NON-BLOCKING); A-5 ~ S-4 (§7 exception wording vs outage entry; Astra adds cap expiry); D-12 step 5 literal fixation not preserved (Astra "other checks" = S-1). Astra-only: A-4 (crash table/mock coverage), A-6 (Q1 shutdown wording, delete "briefly").

No finding is left unrepaired yet; dispositions go in the next revision.

## Report (verbatim)

**Verdict: FIX — 3 BLOCKERs.** Statistical-binding status: **REVISION_REQUIRED**.

Reviewed HEAD `103b5dfd0fc39e3e104578439c619298ebb3cdf3`. I wrote nothing and opened no `SOL_*` file. IDs use **A** as instructed; verified model metadata must come from the caller’s CLI header.

| Authority | Status |
|---|---|
| Frozen Constitution and protocol | Controlling |
| D-12 owner decisions | Recorded; binding through signed C2 |
| D-20 revision 7 | Inactive proposal; this review authorizes nothing |

**Disposition of every prior Astra finding**

| Prior finding | Decision | Evidence |
|---|---|---|
| **D20LR6-A-1:** mutable result | **ACCEPT WITH NOTES** | Rev 7 lines 124–133 make one durable fixed entry authoritative for all later answers. The previous FAIL→PASS contradiction is removed. This does not establish durability of every consumed prerequisite; see A-1 below. |
| **D20LR6-A-2:** visibility versus durability | **FIX** | Index recovery is improved, but fsync **before** looking up concurrently created sealed names leaves another race. A-1 and A-4. |
| **D20LR6-A-3:** availability/R5 overclaim | **ACCEPT WITH NOTES** | Lines 219–229 disclose shared resources, performance-outcome inference, activity after `D*`, missed releases and cap expiry. T-S3 tests a narrower, achievable property. Q1 still contradicts this disclosure; A-6. |
| **D20LR6-A-4:** explicit §7 exception | **ACCEPT WITH NOTES** | Section 1.4 and Q6 explicitly propose an exception and disclose its application to later cycles. Its expiry wording needs correction; A-5. |
| **D20LR6-A-5:** commit-point wording | **ACCEPT WITH NOTES** | Lines 30 and 122 accurately describe `append_entry` and preserve post-C releases. Remove the residual “briefly” claim at line 215; no duration bound exists. |

**Findings**

1. **D20LR7-A-1 — BLOCKER: the initial directory fsync does not cover a subsequent concurrent link.**

   **Place:** [REV7:86](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV7.md:86), lines 124–126, crash-table row 6.

   **Failure scenario:**  
   - `state` holds `L_store` and completes its initial sealed-directory fsync.
   - The lock-free `mark_finished` links a valid finished PASS record, then stalls before its directory fsync.
   - `state` discovers that name, writes and fsyncs the fixed PASS entry, and answers.
   - A machine crash loses the finished-record name while retaining the fixed entry.

   The fixed result remains PASS, so this is **not** the old result-switching bug. It disproves the stronger claim that no answer rests on a removable name and loses the completion evidence used to select PASS. The same ordering issue applies to a newly linked startup prerequisite consumed by the read gate.

   **Minimal repair:** after selecting an existing immutable sealed dependency, ensure its name is durable **before using it**, rather than relying solely on a directory fsync preceding discovery. Specify the selection point and add this interleaving to T-S4/T-S5. No new lock or scheduler is necessary.

2. **D20LR7-A-2 — BLOCKER: the new outage entry can undercount reader unavailability.**

   **Place:** [REV7:107](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV7.md:107), Q7, D-12 P-5/T-7.

   **Failure scenario:** let `R_j=1,000`, release append return at `t2=1,100`, and the following outage-entry append hold `L_store` until `4,700`. The recorded interval contains **100 seconds**, while readers have been excluded for **3,700 seconds**. A crash between the release append and outage append creates another accounting gap. The unspecified availability log might repair these gaps, but the proposal does not bind how.

   **Minimal repair:** make `[R_j,t2)` a partial interval, not sufficient proof of full accounting. Require availability accounting through actual reader-path restoration, including outage-record writes and crash recovery, with no double counting. Unreconciled availability must block promotion. Add this schedule to T-7.

   The general availability-measurement design may remain an **explicit mandatory S4/build carry-forward**. The present claim that this new entry already provides the required extension cannot.

3. **D20LR7-A-3 — BLOCKER: Q7 presents an overly strong impossibility claim.**

   **Place:** [REV7:41](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV7.md:41), lines 254 and 297.

   **Failure scenario:** an owner is told that strict durability-before-deadline cannot be enforced, making acceptance of late durability appear technically unavoidable.

   The argument establishes an **ambiguity**: the durable records can be identical when the write completed on opposite sides of the deadline. It does not establish that a strict safety rule is unenforceable. Refusing ambiguous recovered operations—or stopping for reconciliation—can preserve the rule while rejecting some valid on-time operations. What cannot be obtained from these records is perfect classification with both no false acceptance and no false rejection.

   **Minimal repair:** narrow the claim and explain the tradeoff in Q7: “This proposal accepts saves whose initial clock check was on time. A stricter policy could refuse uncertain crash cases, at the cost of losing some on-time saves.” No replacement mechanism needs implementation in this proposal.

4. **D20LR7-A-4 — NON-BLOCKING: the crash table and mock overstate their coverage.**

   **Place:** [REV7:173](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV7.md:173), lines 177–180 and T-S4.

   **Failure scenario:** an un-fsynced complete line or linked name survives a machine crash. Several rows describe only loss/partial loss, although lack of fsync does not require disappearance. A layer that always discards everything un-fsynced exercises one permitted outcome, not all persistence outcomes or the actual filesystem’s cross-process fsync behavior.

   **Minimal repair:** include complete survival, loss and relevant partial persistence; distinguish crashes before and after completed fsync. Retain “unavailable blocks completion.” Describe the mock as validating the algorithm under its model. The target OS/filesystem assumption remains **UNVERIFIED_EXTERNAL_ASSUMPTION** until separately supported; a mock cannot verify the underlying platform.

5. **D20LR7-A-5 — NON-BLOCKING: the §7 exception does not clearly cover the disclosed cap expiry.**

   **Place:** [REV7:239](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV7.md:239).

   **Failure scenario:** a delayed release causes expiry **at C**. That expiry did not “come late,” yet its occurrence reveals the outcome-related hint expressly disclosed in Q6.

   **Minimal repair:** cover “delayed or missed releases, and cap expiry caused by those delays.” Clarify that “no added … log entry” prohibits additional **research-visible disclosure**, without prohibiting required sealed audit/outage records. The protocol cross-reference is sensible; retaining `PASS_FAIL_ONLY` is compatible with a properly scoped Constitution exception.

   Application to later cycles is explicitly disclosed in Q6; there is no undisclosed duration expansion.

6. **D20LR7-A-6 — NON-BLOCKING: Q1 still promises a broader shutdown than the operative rules.**

   **Place:** [REV7:267](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV7.md:267), lines 269 and 215.

   **Failure scenario:** the owner reads “Work stops” and “Nothing new starts … except posting,” while `write_bundle` may start after C and reads, reconciliation and replay continue. “Before every action” also overstates the scope of the initial fsync rule.

   **Minimal repair:** say that new admissions and counted completion stop at C; late sealed output can continue but cannot qualify. Scope the durability statement to operations consuming authoritative records, and delete “briefly.”

**Other requested checks**

| Consumer/boundary | Assessment |
|---|---|
| Finished result: `t_f < D*=min(d_w,C)` | Reading the clock after RESULT durability proves the stated one-way deadline property, assuming the trusted clock and effective fsync. |
| Fixed result: first eligible lookup at `R_0−21,600` or later | Once its entry is durable, later `state`, `guard_state` and release values cannot differ under the specified lock discipline. |
| Admission: `t1<C`; release: `R_j−21,600≤t1<R_j` | Logical commit-point semantics are coherent as a proposed owner choice. Every index reader is expressly covered by lines 94–100; existing `read_entries` alone provides no such enforcement. |
| D-12 step 5 | Post-fix immutability is preserved. Literal fixation at `D_w` is not: a predeadline finish’s later arrival can still determine the result before the first fixation. Q7 discloses that choice; S4 must reconcile step 5/P-7 explicitly rather than claim unchanged semantics. |

T-S1/T-S2 now explicitly inject inside `append_entry`, during sealing, and between bar clock read and send. Clarify T-S1’s equality wording: the **lower** release-window boundary is accepted; the upper boundary is refused.

T-S3 is testable when the stalled create is the worker’s independent sealed operation and the fixture already supplies admission prerequisites. It establishes lock independence, not resource availability.

S4 must enumerate both `aqt.lockbox.fixed.v1` **and the new P-5 outage record**, including payload, visibility, replay and recovery semantics. The current authoritative-index list omits the latter.

Q6 is substantially clearer and answerable by a non-statistician. Q7 needs A-2/A-3; Q1 needs A-6. Q2(i), Q2(ii), Q3–Q5 remain consistent with this delta.

Errata: **E7-1 confirmed; E7-3 confirmed as superseded; E7-4 confirmed at committed line 69.** For E7-2, D-12’s clause is indeed line 92. I did not inspect the prohibited Sol record to verify its erroneous citation.

Independent integer checks gave:

- Ordinary allowance: **561,600 seconds**.
- Starts at `C−3,600` and `C−1`: **3,600** and **1** second.
- Fixing slack: minimum **21,600 seconds**; respectively **579,600** and **583,199** near C.

Read-only PowerShell assertions reproduced these values and both event-order counterexamples. Hash verification passed **14 sidecars**, seven manifest file bindings and the Constitution self-hash. Frozen inventory matched HEAD; its only raw-byte difference was `docs/README.md` CRLF/LF encoding. `rtk git status --untracked-files=all` was clean; working and staged diffs were empty.

**LOCAL GATE: BLOCKED. Claude status: NOT SENT.** This response is uncommitted evidence; the caller must preserve the complete report and verified model metadata before counting it as completed R19-2 evidence.

Implementation tests, lint, types and import checks were N/A for this proposal-only review. T-S1–T-S6 and real filesystem durability were not executed or established.