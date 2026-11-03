# Codex Astra re-check of D-20 lockbox revision 6 (2cdbf88)

Prompt: `REREVIEW5_PROMPT.md`, prefixed with "Do NOT open or read SOL_REREVIEW5_2CDBF88.md or any other SOL_* file in that folder; review independently. Use finding IDs D20LR6-A-n." Reviewer metadata from the Codex CLI header (2026-10-27): model `gpt-6-astra`, provider openai, sandbox read-only, reasoning effort high, Codex CLI v0.164.0, session id `01a17c3c-13d0-7b60-a4a4-85642df19a7f`, 102,180 tokens. Reviewed HEAD `efc676a`. Independence check: the CLI log's only `SOL_REREVIEW5` hits are the prompt prefix and references to the D-12 file `SOL_REREVIEW5_884B75B.md` inside `d12-proposal/PROPOSAL_REV7.md`; the D-20 Sol record was not opened.

Verdict: **FIX** (3 BLOCKER, 1 NON-BLOCKING, 1 QUESTION). Findings D20LR6-A-1..5. Dispositions: D20LR5-A-1 FIX (-> A-3); D20LR5-A-2 ACCEPT WITH NOTES (-> A-2); D20LR5-A-3 ACCEPT; "usually" wording ACCEPT; S4 consolidation ACCEPT WITH NOTES. E6-1 confirmed.

Convergence with Sol (`SOL_REREVIEW5_2CDBF88.md`): A-1 = S-2 (late PASS completion changes a fixed result; D20L-61 not an accepted R3 residual); A-2 ~ S-5 (crash table: append-before-fsync, link-before-directory-fsync; Astra rates BLOCKER, Sol NON-BLOCKING); A-3 = S-3 (shared-resource availability, R5/Q6 overclaim); A-4 = S-4 (explicit C2 §7 exception); A-5 ~ S-1 (commit-point scope; Sol rates the durable-append crossing BLOCKER).

No finding is left unrepaired yet; dispositions go in revision 7.

## Report (verbatim)

**Verdict: FIX — 3 BLOCKERs.** Statistical-binding status: **REVISION_REQUIRED**.

Reviewed committed HEAD `efc676abc8e6453ae31a917cf45e3e0e9e808457`. I wrote nothing and opened no `SOL_*` file. Finding IDs use **A** as instructed; exact model metadata must come from the caller’s CLI header.

| Authority | Status |
|---|---|
| Frozen Constitution and protocol | Controlling |
| D-11/D-12 owner decisions | Recorded; activation requires signed C2 |
| D-20 revision 6 | Inactive proposal; this review grants no authority |

**Prior Astra dispositions**

| Finding or note | Decision | Evidence |
|---|---|---|
| **D20LR5-A-1** — timing/availability | **FIX** | Deleting the fix step removes that particular lock wait. The remaining availability claim and disclosure remain incomplete; see A-3. |
| **D20LR5-A-2** — snapshot recovery | **ACCEPT WITH NOTES** | Deleting `P` eliminates the stale projection. New durability gaps remain in the replacement; see A-2. |
| **D20LR5-A-3** — Q1 boundary/overclaim | **ACCEPT** | Rev-6 lines 208–210 explicitly explain the six-hour boundary and withdraw timing protection. |
| Replace “usually” | **ACCEPT** | Line 208 now says “may fail … if too little time remains.” |
| Consolidate at S4 | **ACCEPT WITH NOTES** | Lines 7 and 239 make consolidation obligatory. Signing and implementation must use that consolidated text. |

**Findings**

1. **D20LR6-A-1 — BLOCKER: the effective result remains mutable, including after a final release.**

   **Place:** [REV6 lines 109–113](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV6.md:109), T-S5, lines 175 and 199.

   **Failure scenario:** let `D*=0` and the first public boundary be `21,600`. A PASS `mark_finished` samples `−1` but lands at `21,601`. At `21,600`, `state` reports `fixed:true, FAIL`. An insert before landing publishes FAIL; one after landing encounters PASS. Publication-path timing therefore selects the outcome.

   Worse, after a committed FAIL, the stated effective-result function selects the newly present PASS record. Subsequent `state` can report `released:true, result:PASS` while the immutable release says FAIL. Logging an incident does not define consistent consumer behavior.

   D-12 fixes results at the worker deadline and preserves them through release failures. Its accepted R3 concerns trusted clock/filter/availability behavior; it does not already authorize this outcome substitution.

   **Minimal repair:** define one authoritative completion rule and consistent post-release lookup. Preserve D-12’s fixed-result contract, or explicitly propose its replacement for owner/C2 approval. D20L-61 cannot be classified as an already accepted R3 residual.

2. **D20LR6-A-2 — BLOCKER: visibility is confused with durability at two omitted crash points.**

   **Place:** [REV6 lines 83–91](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV6.md:83), startup lines 140–145, crash table and T-S4.

   **Failure scenarios:**

   - A finished record is linked, but its directory fsync has not completed. Lock-free consumers can read it, sign, and commit a PASS release. A machine crash can lose the unfinished directory update. Restarting and fsyncing the directory cannot restore a lost name.
   - A pre-read append writes a complete valid line, then the process crashes before fsync. Restart reads that line from the OS cache. Startup verifies the index but does **not fsync it** before the gate serves bars. A subsequent machine crash can lose the entry after exposure. [Ledger lines 411–414](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/src/aqt/core/ledger.py:411) establish the separate write/flush/fsync steps.

   The inherited partial-line case correctly stops for human reconciliation; it does not cover a complete, unsynced line.

   **Minimal repair:** establish durability before consuming recovered index entries or sealed dependencies. Expand T-S4 to cover complete append-before-fsync and link-before-directory-fsync, with both process and machine crashes, including restart after C. No snapshot rebuild is needed, but the present table is insufficient.

3. **D20LR6-A-3 — BLOCKER: availability independence and the R5 disclosure still overclaim.**

   **Place:** [REV6 T-S3 and §1.3](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV6.md:163), Q6.

   **Failure scenario:** sealed work stalls shared storage or exhausts shared execution resources. Public index reads/appends can then wait or miss their release window despite having no shared sealed lock. The read gate also performs its DEFAULT verification while holding `L_store`. T-S3’s requirement that insertion succeed “in every case” is unsupported without resource/fault assumptions.

   The disclosed windows are also incomplete: T-S5 expressly permits sealed activity after `D*`, potentially after release. Q6 omits §1.3’s admission that timing during computation might distinguish PASS from performance FAIL. The blanket assurance that timing cannot move publication is inconsistent with shared-resource delays causing missed windows.

   **Minimal repair:** claim only the lock dependency actually removed; state resource assumptions and availability residuals. Include extended fault windows and possible early outcome inference in Q6. Test the narrower claim without treating successful injections as proof of unconditional availability.

4. **D20LR6-A-4 — QUESTION: R5 needs explicit C2 treatment under §7.**

   **Place:** [REV6 D20L-60 and Q6](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV6.md:198).

   **Failure scenario:** the owner accepts R5 as ordinary risk disclosure, while C2 still promises PASS/FAIL only and permits only D-12’s narrow end-of-cycle technical-failure disclosure. R5 allows earlier, potentially repeated, fault-free diagnostic inference.

   **Minimal repair:** carry an explicit, scoped Constitution §7 clarification/exception into C2, with matching protocol wording where necessary, for human governance review. Do not infer permission from accepted R1–R4. Q6 can be understandable to a non-statistician once A-3’s omissions and this governance cost are stated.

5. **D20LR6-A-5 — NON-BLOCKING: commit-point explanations need precise scope.**

   **Place:** [REV6 lines 93–107](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV6.md:93), Q1.

   **Failure scenario:** “After C, no write in the table … reaches a commit point” prohibits the same table’s explicitly permitted post-C release inserts. Also, `append_entry` is not one system call: it acquires a lock, verifies the chain, constructs bytes, writes and fsyncs.

   **Minimal repair:** scope the cap statement to C/`D*`-limited operations, preserve post-C releases, and describe an already-started operation accurately. “Just after” must not imply an established latency bound.

**Remaining requested checks**

| Consumer | Governing time, in store-clock seconds | Assessment |
|---|---|---|
| Admission/check records | `t<C` | A decided-before-C write may finish afterward under an explicitly adopted in-flight-operation rule. This is not durability-before-C. |
| Worker writes/bar responses | `t<D*=min(d_w,C)` | Per-response checking is specified. Late completion semantics remain subject to A-1/A-2. |
| Release insertion | `R_j−21,600≤t<R_j` | Both bounds are specified; inherited equality tests remain applicable. |
| Public state | Boundary `R_0−21,600` | Boundary is clear; fixedness/availability claims need repair. |

T-S1/T-S2 cover the named operation classes and deadline checks, including release insertion and bar responses. They do **not** establish coverage of every durability crossing or interleaving identified above.

Independent integer checks reproduced:

- Ordinary worker allowance: **561,600 seconds = 6.5 days**.
- Starts at `C−3,600` and `C−1`: **3,600** and **1** second.
- Public-boundary slack after `D*`: at least **21,600 seconds**, which is slack, not an I/O bound.

Q2(i), Q2(ii), Q3–Q5 retain their previous meanings and introduce no new conflict with the store replacement. S4 consolidation deferral is acceptable as recorded.

**E6-1 confirmed:** committed revision 6, line 52, contains **“Sol l.27, l.30, l.41”**. I did not inspect the prohibited source to validate those references.

Read-only Python 3.14.7 checks exited 0: all **14 sidecars**, seven manifest bindings, seven protocol bindings and the Constitution self-hash passed. Frozen inventory matched HEAD; `docs/README.md` differed only by newline encoding. Git diffs were empty; status emitted a global-ignore permission warning. Implementation tests, lint, types and import checks are N/A for this proposal-only review; proposed T-S tests were not executed.

**LOCAL GATE: BLOCKED. Claude status: NOT SENT.** This response remains uncommitted evidence; the caller must preserve the complete report and verified model metadata before counting it as completed R19-2 evidence.