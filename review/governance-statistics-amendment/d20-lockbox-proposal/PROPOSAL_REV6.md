# D-20 lockbox bindings: proposal, revision 6 (delta on revision 5; the store section is self-contained)

**Author:** the `senior-statistical-governance` agent. Observed model: Claude Opus 5.5, model ID `claude-opus-5-5` (this session's environment metadata). I am an AI reviewer, not an authority. I propose and check bindings. I cannot decide, accept, activate or amend anything.

**Status: INACTIVE PROPOSAL.** Nothing frozen changed. No row binds until the owner decides and signs the C2 §4 amendment. Revisions 1-5 stay as history.

**How to read it:** this is a **delta on `PROPOSAL_REV5.md`**, which is itself a delta on revisions 4, 3 and 2. Every section below that says "replaces" replaces the named text. One exception: **§1.2 (the store) is self-contained.** It replaces the whole of revision 4's B4.1 (l.113-155) and revision 5's B4.1 (l.76-122). For the store's locking, timing and crash rules, read §1.2 only. The A-rows, B2, B3, B3a, B4.2-B4.4, B5, B6 and the fixture are untouched by this simplification, so the rest stays a delta. Consolidating everything into one effective text is **deferred to the S4 signing draft**, as both reviewers allowed. That draft must be one consolidated text that resolves replacement precedence (Astra report l.31 in the record; Sol report l.43 in the record). It is a stated obligation, not an option (D20L-59).

**VERDICT: `AMENDMENT_REQUIRED`.**

**Answers** (both read in full): `SOL_REREVIEW4_06C6989.md` (gpt-6-sol, FIX, D20LR5-S-1..4) and `ASTRA_REREVIEW4_06C6989.md` (gpt-6-astra, FIX, D20LR5-A-1..3).

**Owner direction for this revision** (the same as for D-12 revision 7): simplify rather than patch. Revisions 4 and 5 added a shared lock, then a split lock, a public snapshot, a scheduled fix step, a fixed answer delay `Δ` and a contention test. Each round found new holes in that machinery. This revision **deletes** it. It keeps what is simple and testable, and it states the remaining timing residual plainly as an owner choice (new Q6). It does not claim timing protection it cannot test.

**Review status:** revision 6 is unreviewed. R19-2 requires a focused re-check by two model families before any owner decision. No human statistician has reviewed it.

**Checkout and mode:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch `freeze-sheet`. I wrote this one file only and ran **no git command**. No confirmation or lockbox data, network, credentials, keys or simulation were used.

## 0. Verification

**Read this session:** revisions 5 and 4 in full; revision 3 l.1-30 and l.100-320; `REREVIEW4_PROMPT.md`; both re-check records; `d12-proposal/PROPOSAL_REV7.md` l.1-40, l.55-182; `OWNER_DECISION_D12.md`; Constitution l.70-80, l.145-153, l.185-196; `THREAT_MODEL_v1.md`; DRAFT_WORDING l.240-246; `src/aqt/*/ledger.py`, by searching its definitions and errors.

**Code fact the crash analysis depends on (read, not run).** `read_entries` takes no lock and raises on a damaged file (`ledger.py` l.301-307). Bytes with no terminating newline count as damage (l.277). An unlocked reader that runs during an append can therefore see a torn tail and raise a false §26 incident. That is why §1.2 keeps every index read under `L_store`.

**Governing text found by searching on each topic (item 1):**
- Constitution §7 l.79, "Research receives PASS/FAIL only." It governs the residual in §1.3. Revision 5 never cited it for timing.
- D-12 REV7 l.127 (R1) and l.129 (R3): the precedent for disclosed residuals. `OWNER_DECISION_D12.md` records that R1-R4 were "accepted as disclosed, not removed".
- D-12 REV7 l.113: "No release-time step can turn a PASS into a FAIL". It is tested against the new design in D20L-61.
- DRAFT l.244, "at day 255 processing ends". It governs D20L-56.
- Constitution §26 l.191 (append-only logs) bears on the "no rewrite" rule in §1.2.

**Exact integer arithmetic.** I ran it in the main checkout's venv Python, with `-I -B`, using `python -c`, and wrote nothing. Definitions: `r0 = t_s + 604,800`, `d_w = r0 − 43,200`, `D* = min(d_w, C)`, and the publisher boundary `b = r0 − 21,600`.
- **Claim:** `b − D* ≥ 21,600` and `D* > t_s`, for every admitted `t_s < C`. The sweep covered `t_s` ∈ [C − 700,000, C) in steps of 997, plus the edge points, and the claim held throughout.
- **Worked values:**
  - `t_s = C − 1` gives `D* − t_s = 1` and `b − D* = 583,199`;
  - `t_s = C − 3,600` gives 3,600 and 579,600;
  - `t_s = C − 648,000` gives `D* = d_w`, with 561,600 and exactly 21,600.

  So `D* = d_w` whenever `t_s ≤ C − 561,600`; otherwise `D* = C`.
- **Discriminating case for D20LR5-S-1.** Under revision 5's latched sample, take `t_s = C − 1` and an entry committed at `C + 1`. The worker then gets `D* − (C + 1) = −1` s: the try is spent with no time at all, after processing has ended. The commit-point rule in §1.2 refuses this case. The two treatments give different outcomes.

## 1a. Dispositions

| ID | Disposition | Evidence | Repair (where; finding) |
|---|---|---|---|
| **D20LR5-S-1** (BLOCKER; latched `t_s` allows writes after C) | **Accepted** | Rev 5 l.99 samples `t_s` once. Its step 3 checks the cap on that sample. Rev 4 steps 6-7 then write after verification, entitlement and the default write. Nothing re-reads the clock. Worked case in §0. | §1.2 commit-point rule, swept to every time-limited write; D20L-56 |
| **D20LR5-S-2 = D20LR5-A-2** (BLOCKER; snapshot `P` has no crash recovery) | **Accepted; repaired by deletion** | `P` (rev 5 l.84-88) was a second durable copy of index facts, and the fix step (l.90-95) a third. Each pair could disagree after a crash. Revision 6 deletes `P` and the fix step. The index and the sealed files are the only records, and every reader reads them directly. §1.2 lists each crash point and shows that none leaves two copies to reconcile. | §1.2; D20L-57 |
| **D20LR5-S-3 ~ D20LR5-A-1** (BLOCKER; timing and availability across the fix boundary) | **Accepted; repaired by deleting the claim and its machinery** | `Δ` is a measured value, not a bound (rev 5 l.97). An over-`Δ` answer discloses. A held `L_seal` across `D*` gives `fixed: false` where an idle store gives FAIL (Astra). The test could not hold `L_seal` through the fix (Sol). Revision 6 deletes `Δ`, `L_seal`, the fix step and the contention test. Availability no longer depends on sealed work, which is tested (§1.2, T-S3). The timing residual that remains is stated in §1.3 and put to the owner as Q6. | §1.2, §1.3, Q6; D20L-58, D20L-60 |
| **D20LR5-S-4 = D20LR5-A-3** (NON-BLOCKING; Q1 omits the boundary move and overstates protection) | **Accepted** | Rev 5 l.150-151 and l.153-156. | Q1 rewritten; D20L-59 |
| Astra: replace "usually" with "may fail if insufficient time remains" | **Accepted** | Astra report l.89 in the record. "Usually" was an unverified runtime expectation. | Q1; D20L-59 |
| Astra and Sol: the S4 text must be one consolidated effective text | **Accepted as an obligation; deferred to S4** | Consolidating now, while Q1-Q6 are open, would mean doing it twice. | Header; §4; D20L-59 |
| Rev 5 rows that both reviewers accepted (D20L-51, D20L-54, D20L-55, the `CAP_REACHED` order, the deletion of `earliest`) | **Unchanged** | Sol l.27, l.30, l.41; Astra l.71-75 in the records | none |

## 1. Bindings

### 1.1 Replacements outside the store section

**B1 publisher row, replaces revision 5's row (l.55).**

| Role | Allowed store operations | Never |
|---|---|---|
| publisher | `begin_read` (§1.2). `insert_release(evaluation_id, j, attestation \| null)`: the store fills `result` and the effective commitment itself, at the insert, using the effective-result rule (§1.2). The attestation rule is revision 5's, unchanged: required iff the effective result is PASS and `R_j < C`; it must verify under the C2 public key, and must name this evaluation ID and `cooling_off_start = R_j`. `state(evaluation_id)`: `{"fixed": false, "store_now": t}` while `t < R_0 − 21,600`; from then on `{"fixed": true, "released": bool, "result": "PASS" \| "FAIL", "store_now": t}`, with the same shape for every FAIL. | commitments, nonces, sealed bundles, cause classes, finished-record presence or time, lockbox bars |

**The `state` boundary `R_0 − 21,600`, with its reason restated.** The boundary stays at six hours before `R_0`, which is when the publisher's first window opens. Revision 4 had put it at `d_w`, twelve hours before `R_0`. Revision 5's reason ("absorb the fix step's wait", l.57) is gone with the fix step. The new reasons:
1. The publisher holds a result for at most six hours before it is due, never twelve.
2. Every evaluation of the effective result happens at least 21,600 s after `D*` (§0). A sealed write already under way at `D*` has at least six hours to land first.

*Operational effect:* none on a normal release, because the publisher has nothing to do before its window. A monitor that calls `state` between `R_0 − 43,200` and `R_0 − 21,600` sees `fixed: false` where revision 4 showed the result. For `j ≥ 1` nothing changes. Q1 lists this.

**Worker deadline (revision 5 §1, l.44-49) stands.** It is `D* = min(d_w, C)`, with the time checks done at the commit point (§1.2).

### 1.2 The store (self-contained; replaces revision 4's B4.1 and revision 5's B4.1)

**Records.** There are two kinds, and nothing else is authoritative.
- **The index:** the append-only ledger. It holds pre-read entries, rejection entries, release entries and no-read entries.
- **Sealed files:** each written once and never replaced (§26). They are:
  - the DEFAULT bundle with its nonce and commitment, under `(evaluation_id, attempt)`;
  - the worker's RESULT bundles;
  - at most one finished record per evaluation (`aqt.lockbox.finished.v1`, revision 3 l.285);
  - the pre-read check record (at most one per `evaluation_id`; revision 4 l.117);
  - the startup records.

A sealed file is created like this: write a temporary file, fsync it, link it to its final name **without replacing** an existing name, then fsync the directory. A second create of the same name is refused. Temporary files are never read, and are logged when found. There is **no public snapshot, no fix step and no scheduler**. Every answer is computed from these records when it is asked for.

**One lock.** `L_store` is the store's own lock file, not the ledger's sidecar lock (D20L-46's no-nesting fix stands). It is held by every operation that reads or appends the index:
- `begin_read`, `insert_release` and no-read inserts;
- `state`, readers' row reads and `guard_state`'s release-presence check;
- `verify_replay`, reconciliation and startup;
- the read gate's entitlement check (below).

The store runs each of these itself, so the lock is never held by a worker or caller process. Sealed creates, bar serving and the effective-result evaluation take no lock. Concurrent creates resolve through exclusive linking, and readers see a sealed file whole or not at all.

**The commit-point rule (D20L-56) [DETAIL].** Every time-limited write has one commit point:
- for an index append, the call to `append_entry`;
- for a sealed create, the link to the final name;
- for bars, the sending of each response.

The store re-reads its clock **immediately before** the commit point. The write is on time iff that reading is before the write's deadline; otherwise nothing is written and the call is refused. The deadlines are these:

| Write | Deadline on the re-read | Refusal answer |
|---|---|---|
| pre-read rejection, `BUDGET_EXHAUSTED` rejection, DEFAULT create, pre-read entry (all inside `begin_read`) | `C` | `CAP_REACHED` |
| `record_pre_read_check` | `C` | `CAP_REACHED` |
| `write_bundle`, `mark_finished`, each bar response | `D*` | refused, deadline |
| `insert_release` | `R_j − 21,600 ≤ t < R_j`, both bounds on the re-read | refused (a missed release, P-7) |

**What must happen before C (S-1's question).** The commit point must come before C. Durability may complete after it, within the one system call and fsync that the commit already started. Nothing has to be durable before C beyond that. A commit that never becomes durable (a crash) did not happen, and the crash rules below apply. After C, no write in the table above reaches a commit point. This is how §1.2 reads "processing ends" (DRAFT l.244): no new step starts at or after C, and a step already under way may finish writing. `t_s` remains the sample for `r0`, the cooldown and the order checks. A late re-read can only refuse a write. It never admits one.

**Effective result [DETAIL; replaces rev 5's fix step].** For an evaluation, the effective `{result, commitment}` is a pure function of the records present when it is evaluated:
- the finished record, if one is present with `finished_at < D*`;
- otherwise, the DEFAULT's.

`finished_at` is the clock re-read at that record's commit point. `insert_release`, `state` (from `R_0 − 21,600`) and `guard_state` each evaluate it on demand, and all of them run at least 21,600 s after `D*`. **The committed release entry, which embeds the result and the commitment (B4.3), is final.** A finished record that appears later and disagrees with it is a §26 incident, found by reconciliation. It never changes the release (D20L-61).

**The pre-read check record:** as revision 4 (l.117). It is created once per `evaluation_id` under the commit-point rule against C.

**`begin_read(evaluation_id)`, under `L_store`.** Sample `t_s` = the store clock, floored to the second.
1. Verify the index (`read_entries`). Damage stops the process as a §26 incident.
2. **Read-only reconciliation**, allowed at any time, including after C:
   - if a pre-read entry exists, check that its DEFAULT exists and verifies (otherwise a §26 incident, and stop), and return the entry unchanged;
   - if a rejection entry for this nominee exists, return it unchanged.

   Nothing is written.
3. **Cap:** if `t_s ≥ C`, answer `CAP_REACHED` and write nothing.
4. **Entitlement,** as revision 4 step 3. A failed check appends a rejection entry, subject to the commit-point rule.
5. **Budget,** as revision 4 step 4. The rejection append is subject to the rule.
6. **Order and cooldown,** as revision 4 step 5, without its cap bullet. Defer with `DEFERRED` (no `earliest` field) while `t_s < r0′ − 604,800 + 2,592,000`, or while the trend family is status (a) with neither an entry nor a rejection. Nothing is written.
7. `r0 = t_s + 604,800` and `d_w = r0 − 43,200`. Set `attempt` = 1 + the highest attempt present. Create the nonce and the DEFAULT bundle (`sealed_at = t_s`), and create the DEFAULT file under the rule.
8. Append `aqt.lockbox.pre_read.v1` exactly as revision 4 step 7 (l.134), under the rule, fsynced before `L_store` is released.

If step 8's re-read is at or after C, the step-7 DEFAULT is an orphan (revision 3 l.249): it is void and binds nothing, no budget is spent, and the answer is `CAP_REACHED`.

**The read gate.** When `lockbox_eval` opens a read session, the store checks entitlement **once**, under `L_store`. All three must hold:
- the pre-read entry exists;
- its DEFAULT verifies;
- the caller holds a `PASS` startup record for the check record's module hash and image.

Revision 4's argument (l.141) is unchanged: step 8 fsyncs before releasing the lock, so the check only ever sees durable entries. Bars over `[S_pre, L1)` are then served without the lock, each response under the commit-point rule against `D*`. No bar is served once the re-read reaches `D*`, whose value is at most C. This holds for an entry made before C and reconciled after it.

**Startup.** Before serving any call, the store does three things under `L_store`:
- fsyncs the sealed directory;
- verifies the index (damage stops the process, §26);
- runs revision 3's reconciliation (l.248-250): orphans are void, and an entry whose DEFAULT is missing or fails is an incident.

There is no projection to rebuild and no fix step to replay.

**Crash points (S-2 = A-2; each has one durable copy).**

| Crash between or during | State after restart | Effect |
|---|---|---|
| DEFAULT create and the pre-read append | orphan DEFAULT, no entry | no read, no budget spent; the next call before C uses `attempt + 1` |
| the pre-read append's fsync and the reply | entry durable | `begin_read` returns it; the gate sees it, because it reads the index itself; after C the gate serves nothing (`D* ≤ C`) |
| a torn index append (partial line) | the index is damaged | §26 stop for human reconciliation, as revision 3. This is inherited, conservative, and not a silent repair |
| a sealed create, before the link | a temporary file only | the record is absent; for `mark_finished` the effective result is DEFAULT |
| the release append's fsync and the reply | release durable | readers see it from `visible_from`; a retried insert is refused (one per evaluation), and `state` shows `released: true` |
| restart after C, with an entry made before C | entry durable | as the second row; the release is later inserted as FAIL/DEADLINE, unless a finished record has `finished_at < D*` |

**Pre-read reason codes:** revision 2's list without `COOLDOWN_NOT_ELAPSED` (revision 4 l.145).

**Tests.** These are revision 3's list (l.253-258) and revision 4's list (l.147-155), with the cooldown boundary taken at `r0′ − 604,800 + 2,592,000` instead of `earliest`, plus revision 5's cap-order, reconciliation-after-C and worker-deadline tests (l.114-116). Revision 5's contention test (l.117-122) is **deleted**. Added:
- **T-S1, crossing C.** With an injected clock, `t_s = C − 1` and the re-read at `C`, separately before each of the four `begin_read` commit points and before `record_pre_read_check`. Each is refused with `CAP_REACHED`, and nothing after that point is written. Crossing before step 8 leaves one void orphan and no entry. With the clock crossing C **after** a commit point, the write stands and counts as on time.
- **T-S2, crossing `D*`.** The same for `write_bundle`, `mark_finished` and a bar response, for `D* = d_w` and for `D* = C`; also `insert_release` crossing `R_j`.
- **T-S3, availability independent of sealed work.** A worker blocks inside `write_bundle` or `mark_finished` (injected stall), and separately a worker crashes, across `D*` and across `R_0 − 21,600`. `state` must return `fixed: true` with the effective result at `R_0 − 21,600`, and `insert_release` must succeed in the window, in every case. A held-up sealed create never makes a public call wait or answer `fixed: false` after the boundary.
- **T-S4, crash points.** One test per row of the table above, including a restart after C.
- **T-S5, late landing.** A `mark_finished` whose re-read is `D* − 1` and whose link is delayed (injected):
  - landing before the first evaluation, it counts;
  - landing after a FAIL release entry, the release stands and reconciliation logs an incident;
  - landing between `state` and `insert_release`, the null-attestation insert is refused, it becomes a missed release, and the PASS is released at `R_{j+1}`.
- **T-S6, payload shape.** `state` and release bytes have the identical shape for crash, deadline, technical and performance FAIL (D-12's "same shape for every FAIL").

None of these tests measures timing. No timing property is claimed (§1.3).

### 1.3 The timing residual (R5), stated rather than hidden (D20L-58)

**What is still separated.** The worker and the signer never hold a store lock, and no public answer waits on a sealed lock (there is none). Publication time is still fixed: `D*` fixes the result and `R_j` fixes the release, so D-12 T-3 holds. Every FAIL answer has the same bytes and shape (T-S6).

**What is not hidden.** Public calls share one machine (CPU, disk and memory) with the sealed work. They also share `L_store` with one short gate check per read session, and with the signer's release-presence check. So **how fast** a public call answers can vary with sealed activity. Someone who can call the store, meaning the publisher or the reader account (the owner and, by D-12's working rule, research), and who times answers closely might infer:
1. **During a read** (`t_s` to `D*`, at most 6.5 days): whether the worker is running, stopped early or restarted, and roughly when it finished. This hints at "a technical breakdown" versus "ran to the end", which is a FAIL-kind fact, before the release. I have **not** shown that it cannot also hint at PASS versus performance FAIL. Compute paths differ slightly by outcome (for example, `upside` is computed only for a finite `T_L`).
2. **In the release window** (`R_j − 6 h` to `R_j`): whether the signer was asked. That reveals a PASS up to six hours before its release. The evaluation of finished-versus-DEFAULT records also differs by microseconds.

**How much:** not measured, and no bound is claimed. It depends on the hardware, the load and how closely the caller times. It may be undetectable or clear.

**What it cannot do:** change a result, a release time, an order of release, or a counted try.

**Compared with D-12's accepted R1** (REV7 l.127): R1 needs a signing fault, and it can only hint at a PASS, never at a FAIL kind. R5 needs no fault, and it can hint at a technical breakdown. Q2a already lets the cycle label show that fact, but only at cycle end and only when the other family has no result. R5 can show it earlier and in every case. **So R5 is not covered by the owner's acceptance of R1-R4 (Astra's point). It needs its own choice: Q6.** Whether R5 can be disclosed as a residual, as R1-R4 were, or needs a row in C2's Constitution table under §7 l.79 is an S4 and R19-2 question. The AI does not decide it (D20L-60).

## 2. Findings

**Changes to earlier findings:**
- **D20L-46:** repaired by holding `L_store` for every index read and append. That was revision 4's repair. Revision 5's snapshot repair is withdrawn with the snapshot.
- **D20L-53** becomes **partly repaired, with the remainder disclosed.** The repair that remains is that sealed writes take no store lock. The fixed delay `Δ`, `L_seal`, `P` and the contention test are withdrawn, and so are revision 5's claims that they "stop the timing … hinting at a result" (l.151) and that the over-`Δ` case is "not hidden" (l.139). The residual is R5 (§1.3).

**New findings:**
- **D20L-56 BLOCKER (repaired, §1.2 commit-point rule).** Revision 5 checked the cap and the deadlines on a latched sample, so writes could commit after C or `D*` (§0 worked case). Swept to every time-limited write, including `insert_release` against `R_j` and bar responses, which the finding did not name. (D20LR5-S-1.)
- **D20L-57 BLOCKER (repaired by deletion, §1.2).** The snapshot `P` and the fix step were extra durable copies with no recovery, so a crash between the copies hid a consumed try or a committed release. Both are deleted, and every crash point now leaves one copy (table in §1.2). (D20LR5-S-2 = D20LR5-A-2.)
- **D20L-58 BLOCKER (repaired by deleting the claim; the residual goes to Q6).** Revision 5 claimed timing protection that `Δ` could not guarantee, and its fix step made availability depend on sealed work. Availability is now independent of sealed work and tested (T-S3). Timing is not protected, and §1.3 says so. (D20LR5-S-3 ~ D20LR5-A-1.)
- **D20L-59 NON-BLOCKING (applied).** In Q1: the boundary move and its effect are listed, `Δ` is dropped, the protection is no longer overstated, and "usually" becomes "may fail if insufficient time remains". The S4 consolidation obligation is recorded. (D20LR5-S-4 = D20LR5-A-3; Astra notes.)
- **D20L-60 QUESTION (for S4 and R19-2; not decided here).** Can R5 be accepted as a disclosed residual, like D-12's R1-R4, under Constitution §7 l.79, or does it need a C2 Constitution-table row? R5 differs from R1 in needing no fault and in touching FAIL kind.
- **D20L-61 NON-BLOCKING (disclosed fault residual; reviewers please check).** Deleting the fix step means that a finished record whose commit point preceded `D*`, but whose link stalls until after a FAIL release entry is committed, is published as FAIL (T-S5). D-12 l.113's "no release-time step can turn a PASS into a FAIL" still holds, because this is a sealed-write fault six or more hours long, not a release-time step. Such a write is treated like a worker crash before finishing (D-12 step 5). It extends R3 ("trusted store"), and is logged by reconciliation.

## 3. Owner questions (Q1 is replaced; Q6 is new; Q2(i), Q2(ii), Q3, Q4 and Q5 are as in revision 5; each has "Keep blocked")

**Q1. Adopt the detail rows and the new defaults?**

*In short:* this adopts the AI-drafted rule book for running, sealing and posting the lockbox test. With it, the builds can start, each needing §16 review. Without it, the lockbox cannot run.

Three rules added since revision 4 matter to you:
- **Work stops at day 255.** A test still running then is posted as a technical fail, and the pick expires unpromoted. This follows from the day-255 rule you decided. A test started shortly before day 255 **may fail this way if too little time remains**. For example, one started an hour before day 255 has one hour. Its one try is spent either way. A step already under way in the last instant before day 255 may finish writing just after it; nothing new starts at or after day 255.
- **The posting job learns a result six hours before its scheduled posting time, not twelve.** Its posting window opens at six hours, so normal posting is unaffected. A check run between twelve and six hours before would see "not yet".
- **No timing protection is claimed.** The earlier fixed answer delay is dropped. What the service's speed might still hint at is your separate choice in Q6.

The list is revision 4's Q1 list, plus:
- the worker deadline `D*`;
- the commit-point rule;
- the one-lock store, with no snapshot;
- the six-hour `state` boundary.

Adopting Q1 does **not** settle D11-15. The D20L-36 sentence (revision 4 Q1) stands.
- **"Adopt (Recommended)."** Cost: several builds, each needing §16 review. A lost key can cost a good PASS.
- **"Keep blocked."**

**Q6. May the speed of the lockbox service hint at what is happening inside it?** (new)

*In short:* the part that runs the sealed test and the part that answers the posting job and you share one computer. While a test runs (up to 6.5 days), and in the six hours before a result is posted, how fast the service answers can change with that hidden work. Someone timing its answers very closely (you, or research working with you) might guess, before the post:
- that a test broke down or stopped early, rather than running to the end;
- roughly when it finished;
- in the last six hours, that a PASS is coming, because only a PASS gets signed.

It cannot change any result or move any posting time. Nobody has measured how clear these hints would be: they could be invisible or obvious. Five earlier drafts tried to hide this with timing tricks, and each left gaps, so this draft no longer claims to hide it. You already accepted a similar hint from signing faults (D-12 R1), but that one needs a fault and can only hint at a PASS. This one needs no fault, and it can also hint that a FAIL was a technical breakdown. You allowed that fact in the end-of-cycle label (D-12 Q2a), but this could show it earlier and in every case.
- **"Accept it, written into C2 as a disclosed risk (Recommended)."** Cost: the hints above. The S4 review must also confirm whether the Constitution's "research receives PASS/FAIL only" needs a written exception for it (D20L-60).
- **"Keep blocked."** The lockbox cannot run until someone designs and tests stronger separation, for example separate machines. This draft does not propose that.

## 4. Remaining, unauthorised, self-check

**Remaining:**
- the R19-2 re-check of this revision;
- owner Q1-Q6;
- the S4 items of revision 4, plus D20L-60;
- the consolidated S4 signing text (an obligation);
- the C2 rows of revision 4;
- the builds of revision 4, plus the commit-point rule, the one-lock store and tests T-S1..T-S6, each under §16 review (Constitution l.147-153; lockbox ACL tooling, l.152).

Revision 5's build items `L_seal`, the snapshot, the fix step and the fixed schedule (l.180) are withdrawn.

**Unauthorised:** frozen edits; activation; acceptance; any code; key generation; simulation; confirmation or lockbox access; promotion; deployment; trading. `KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid outcomes.

**Self-description check** (done after the last edit):
- one file written, no git command run;
- re-check findings answered: 7 IDs (D20LR5-S-1..4, D20LR5-A-1..3), forming 4 distinct issues, plus 2 notes;
- new findings D20L-56..61, with no gaps;
- one new owner question (Q6), and Q1 replaced;
- mechanisms deleted: the fixed delay `Δ`, `L_seal`, the public snapshot `P`, the scheduled fix step and the contention test.
