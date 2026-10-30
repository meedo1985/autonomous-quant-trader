# D-20 lockbox bindings, option C: release on request (revision C1; delta on revision 8)

**Author:** Claude Opus 5.5 (`claude-opus-5-5`, this session's environment metadata), in the main Claude Code session, 2026-10-30. AI drafting, not an authority. I propose and check bindings. I cannot decide, accept, activate or amend anything.

**Status: INACTIVE PROPOSAL, UNREVIEWED.** Nothing frozen changed. No row binds until the owner decides and signs the C2 §4 amendment. R19-2 requires a two-family review of this revision before any owner decision. No human statistician has reviewed it. `OPTION_C_MANUAL_RELEASE_SKETCH.md` (c3fc60b) stays as history; this proposal replaces it.

**Owner direction (2026-10-30):** after the sketch and its review, the owner said "Yes do it": write the full option C proposal. Earlier standing direction still applies: simplify rather than patch, prefer deleting mechanism, claim only what is true and testable.

**How to read it.** This is a **delta on `PROPOSAL_REV8.md`**.
- **Kept from rev 8 §1.2 (the read side):** records (except that rev 8's release-entry use is replaced by §1.3 here); one lock `L_store`; durable before use; the time rule for `begin_read` (deadline C) and `mark_finished` (deadline `D*`, steps 1-4) plus rule (5) below; start checks; cap scope; `begin_read`; the read gate; startup; crash rows 1-9, 11 and 12; tests T-S2 and T-S4 for those rows; T-S6.
- **Replaced:**
  - rev 8 §1.1's B1 publisher row;
  - from rev 8 §1.2: "The result", its proof, the step-5/P-7 reading, the availability carry-forward, crash rows 10 and 13, and tests T-S1 (release half), T-S3 and T-S5;
  - rev 8 §1.3 (R5) and §1.4 (§7 row), whole;
  - owner questions Q1, Q6 and Q7.
- **Unchanged from earlier revisions:** the A-rows, B2, B3, B3a, B4.2-B4.4, B5, B6, the fixture, Q2(i), Q2(ii), Q3-Q5. The consolidated S4 signing text remains an obligation (D20L-59).

**VERDICT: `AMENDMENT_REQUIRED`.**

## 0. Why, and what changes

Revisions 3-8 kept one service: from six hours before `R_0`, the store answered `state` calls, and a publisher job inserted a release on a fixed daily schedule, while a finish could still be landing. Each round's blockers came from that overlap:
- the clock (D20LR8-S-1);
- a finish racing an answer (D20L-62, D20L-69);
- daily slips and cap expiry (P-7, D20L-72);
- an availability log nobody had designed (D20L-70);
- lock-wait hints (R5).

**Option C removes the overlap.**
1. Nobody can ask about a read until `R_0`, twelve hours after its worker deadline.
2. At or after `R_0`, the owner asks for the release. The publisher performs it: it writes the release entry, which fixes the result for good, and delivers PASS or FAIL to the owner's own record.
3. Only after that, on a PASS, the signer signs.
4. Cooling-off counts from delivery.

**What option C deletes:** `state`, `guard_state`, the daily `R_j` schedule, the 6-hour window, the missed-release rule, the pre-release signing step, the availability log, and the clock invariant D20LR8-S-1 asked for.

**What it keeps:** the separate posting job of D-12 Q6(i). The owner triggers it; he does not become it (D20C-A-3).

**Read in full this session:** `OPTION_C_MANUAL_RELEASE_SKETCH.md`, `ASTRA_OPTION_C_REVIEW_C3FC60B.md` (D20C-A-1..8), `PROPOSAL_REV8.md`, `SOL_REREVIEW7_E68B947.md` (D20LR8-S-1..3), `REREVIEW7_PROMPT.md`, `ASTRA_REREVIEW6_F50838F.md` l.1-25, `../d12-proposal/OWNER_DECISION_D12.md`, `../d12-proposal/PROPOSAL_REV7.md` l.76-150 (actors, steps 1-5, P-5..P-8, records, R1-R4, T-1..T-8), `PROPOSAL_REV6.md` l.54-72 (B1 row, `state` boundary), `PROPOSAL_REV5.md` l.143-172 (Q1, Q2(ii), Q4, Q5), `docs/THREAT_MODEL_v1.md` l.1-20, `protocols/protocol_v1.yaml` l.75 and l.300.

**Not done:** no rev-8 Astra re-check was run. The owner moved to option C before it. Rev 8's own open findings are answered here only where this revision touches them (§1a).

## 1a. Dispositions

| ID | Disposition | Repair |
|---|---|---|
| **D20C-A-1** (BLOCKER; entry is not delivery) | **Accepted.** Cooling-off runs from a recorded, confirmed **delivery**, not from the release entry. Uncertain delivery delays it; it never shortens it. | §1.4; D20L-77 |
| **D20C-A-2** (BLOCKER; callable lock channel survives; R1 survives) | **Accepted, in two parts.** (a) A request before `R_0` is refused by the publisher from its own copy of `R_0`; it never contacts the store, so it cannot wait on sealed work. After `R_0` the residual is listed and still needs a narrowed §7 exception. (b) Signing happens **after** the release entry, so a signing fault can no longer hide or delay a result. It can delay only the start of cooling-off, and only after the result has been delivered. | §1.2, §1.3, §1.6, §1.7; D20L-78 |
| **D20C-A-3** (NON-BLOCKING; privilege boundary) | **Accepted.** Option C keeps D-12 Q6(i)'s separate publisher. The owner gets one fixed operation, and the capability table names what each identity receives, including errors, logs and reconciliation views. | §1.1; D20L-76 |
| **D20C-A-4** (BLOCKER; eventual release not enforced) | **Accepted.** An unreleased counted read blocks cycle completion, and a descendant cannot be admitted while an ancestor is unreleased. | §1.5; D20L-79 |
| **D20C-A-5** (BLOCKER; post-cap signing and status) | **Accepted.** Four separate facts are kept apart: result, release, attestation and promotion status. Nothing is signed from C on. The promotion guard enforces the cap; the warning is only a convenience. The revision/invalidation rule of P-6 l.245 is restated. | §1.3, §1.4; D20L-80 |
| **D20C-A-6** (NON-BLOCKING; clock and durability overstated) | **Accepted.** One property needs no clock: once released, a result cannot change. Everything else that uses time is listed as relying on the trusted store clock (R3). The crash table covers the read side as well as the release side. | §1.2, §1.8; D20L-81 |
| **D20C-A-7** (NON-BLOCKING; D-12 crosswalk incomplete) | **Accepted.** Every D-12 row and T-1..T-8 is mapped. | §2 |
| **D20C-A-8** (NON-BLOCKING; comparison overstated) | **Accepted.** The comparison now lists established mechanisms and open obligations. It makes no prediction of review rounds and recommends conditionally. | §3 |
| **D20LR8-S-1** (BLOCKER on rev 8; clock invariant) | **Overtaken for the published result.** The proof in §1.2 needs no clock, because every finish refuses once a release entry exists. Deadline enforcement still trusts the clock (R3), and is stated as such. | §1.2 |
| **D20LR8-S-2** (Q7 "one more record per save") | **Accepted**; the wording is now "additional durable evidence and design work". | Q7 |
| **D20LR8-S-3** (reconciler could see sealed facts) | **Accepted as an explicit gate.** S4 must name the reconciler and a view that cannot expose a sealed result or an unreleased result to the owner. If the owner must see either, that is a Constitution amendment question before the access design is adopted. | §1.1; D20L-76 |

## 1. Bindings

### 1.1 Actors and capabilities (replaces rev 8's B1 row)

| Identity | May do | Receives | Never |
|---|---|---|---|
| **owner** | Run the fixed operation `request_release <evaluation_id>`. It takes no other argument, option or environment input. Read his own record (§1.4). Acknowledge a delivery. | One of the fixed codes below. On delivery: the delivery file (§1.4). | A shell or debugger on the lockbox machine during an open read (§1.7); the sealed directory; the publisher's or signer's logs; stderr of any lockbox process; reconciliation views (D20L-76) |
| **publisher** (separate OS identity, D-12 Q6(i)) | `begin_read`; `release(evaluation_id)` (§1.3); `record_delivery` (§1.4); ask the signer for an attestation after a release entry exists | `R_0` of each read, from `begin_read`'s answer; at release, the release entry; on PASS, the attestation | commitments' preimages, nonces, sealed bundles, cause classes, finished-record presence or time before release, lockbox bars |
| **signer** (`lockbox_eval`'s key, THREAT_MODEL l.9) | Sign one attestation per PASS release, under §1.3's guard | the release entry and the sealed record it verifies (P-2) | the index other than release entries |
| **worker** (`lockbox_eval`) | As rev 8 (read, compute, `write_bundle`, `mark_finished`) | lockbox bars through the read gate | index writes |
| **reconciler** | §26 reconciliation | A view fixed by S4 | **S4 gate (D20LR8-S-3):** S4 names this person and a view that cannot show a sealed result, or any release row before delivery, to the owner. If no such person or view exists, that is a Constitution question put to the owner before the access design is adopted. |

**Fixed codes of `request_release`.** Every code has one fixed message and nothing else. Errors are mapped to `STOPPED` and never printed.

| Code | Meaning |
|---|---|
| `NOT_YET` | Refused before `R_0`. Decided by the publisher alone (§1.2). |
| `DELIVERED <PASS\|FAIL>` | The result was delivered, with its delivery time. |
| `ATTESTATION_PENDING` | PASS delivered, attestation not yet delivered (§1.3). |
| `STOPPED` | A §26 stop. |

Logs and stderr of the publisher, signer and store go to an account the owner cannot read. S4 fixes the mechanism. §16 review checks that nothing else reaches the owner.

**THREAT_MODEL l.9:** unchanged from D-12's plan. The publisher identity is added to the actor list; `lockbox_eval` keeps "lockbox read + attestation signing only".

### 1.2 One result: the release fixes it (replaces rev 8's "The result" and its proof)

**Release, `release(evaluation_id)`**, run by the publisher:
1. **Without contacting the store:** if the publisher's clock is before `R_0 + 60 s`, answer `NOT_YET`. `R_0` is the publisher's own copy from `begin_read`. The 60 s margin covers clock disagreement; a store refusal (step 2) is logged as a fault.
2. **Under `L_store`**, after rev 8's lookups-then-fsyncs:
   - If the store clock is before `R_0`, refuse; this is the fault case named in step 1.
   - If a release entry exists, return it.
   - Otherwise determine the result: the finished record's `{result, commitment}` if one exists and its RESULT bundle verifies; a bundle that does not verify is a §26 stop, never a silent FAIL (§6 l.70). With no finished record, the DEFAULT's FAIL.
   - Append the release entry `{evaluation_id, result, commitment, released_at}` and fsync it before unlocking. `released_at` is the clock reading under the lock.
3. **`mark_finished` gains rule (5):** in step 2, under `L_store`, if a release entry exists for the evaluation, refuse. The finish counts as late output, void.

**Proof that a shown result cannot change (no clock needed).** Every output that shows a result comes from a durable release entry, because nothing shows a result before step 2 completes. Let F be any finish and E the first release entry; both hold `L_store`, so their holds do not overlap.
- If F's hold came first, F's record was durable before E's lookup (rev 8's durable-before-use rule), so E contains F's result.
- If E's hold came first, F finds E and refuses under rule (5).
- A second release returns E unchanged.

So every shown result equals E, whatever the clock does. **Condition:** rev 8's durable-before-use rule and the platform assumptions (fsync semantics, lock released on exit), which stay `UNVERIFIED_EXTERNAL_ASSUMPTION`.

**What still trusts the clock (R3; not claimed clock-free, D20C-A-6):**
- the worker deadline `D*` (a backward step below `D*` before a release could admit a finish that should have been late; R3 trusts the clock not to do this);
- the cap C on admission;
- the 30-day cooldown;
- the 7-day `R_0`;
- the 72-hour cooling-off;
- `D* ≤ R_0 − 12 h`, which keeps a normal finish's lock hold well before any release.

Release timing cannot change a result **given R3**. Without R3, only results already released are protected.

**D-12 step 5 under this.** "Only while the store clock is before `D_w`" becomes rev 8's `t_f < D*` under `L_store`, plus rule (5). "After `D_w` the result is fixed" holds: after `D*` no new finish counts (R3), and after the first release nothing can change. P-7's "committed before `R_j`" no longer exists (§2). This reading goes to the owner as Q7, which is now narrower.

### 1.3 Signing after release (replaces D-12's pre-release signing)

After a PASS release entry exists, the publisher asks the signer. The signer signs only if:
- the release entry's result is PASS;
- the sealed record verifies against the entry's commitment (P-2);
- P-2's scientific checks hold;
- the store clock is before C;
- no attestation exists for this evaluation;
- no revision or invalidation has happened since the pre-read entry (P-6 l.245).

The attestation names the evaluation ID and the release entry's hash. It carries **no `cooling_off_start`**: that time comes from delivery (§1.4). The publisher validates it as in P-8 (identity fields, the three fields, signature) and links it to the release entry as a sealed-style create (write temporary file, fsync, link, fsync directory).

**A signing refusal, timeout or P-8 mismatch** writes nothing new. The PASS stays delivered with `ATTESTATION_PENDING`, and the publisher retries on the next request. **It never turns a PASS into a FAIL, and it cannot hide or delay the result**, which the owner already holds. It can only delay the attestation and so the start of cooling-off (D20C-A-2 b).

**Four separate facts per evaluation (D20C-A-5):**

| Fact | Values | Changes? |
|---|---|---|
| result | PASS or FAIL, in the release entry | never, once written |
| released | release entry exists, and when | written once |
| attestation | none, effective (delivered before C and not voided), or void | becomes void at a revision or invalidation if not yet effective (P-6 l.245); a void attestation never becomes effective |
| promotion status | eligible, promoted, `U_ops`, or not applicable (FAIL) | decided by the promotion guard (§1.4) |

**From C on, nothing is signed.** A PASS released or delivered after C shows PASS and nothing more, and its status is `U_ops` (P-6). A visible FAIL never receives `U_ops` (T-6).

### 1.4 Delivery and cooling-off (replaces P-5's availability rule; D20C-A-1)

**Delivery.** The publisher writes the delivery file `{evaluation_id, result, released_at, attestation | null, release_entry_hash}` to the owner's record directory: write a temporary file, fsync, link, fsync the directory. It then reads the file back, checks its hash, and appends `{evaluation_id, delivered_at, file_hash}` to the index under `L_store`. `delivered_at` is the clock reading taken after the read-back.
- A PASS's attestation is delivered the same way, as its own delivery with its own `delivered_at`.
- If any step fails or crashes, there is no delivery entry. The next `request_release` repeats the delivery of the same release entry, and `delivered_at` is the new, later time. **Delivery can be late; it cannot be early.**

**Owner acknowledgement.** The owner's record directory holds the file. The command shows `DELIVERED` only after the delivery entry is durable.

**Cooling-off start** = the `delivered_at` of the attestation's delivery. The promotion guard accepts an owner decision only if:
- an effective attestation exists;
- the decision time is at least `cooling-off start + 72 h`;
- the decision time is no later than C (day 255).

A revision or invalidation after the attestation became effective does not affect it; "attested" in P-6 l.245 means an effective attestation. One not yet effective at that moment is void (§1.3, row C9).

The guard enforces the cap. `request_release` also warns when `now + 72 h` is past C (a convenience, not a guard). The owner holds his copy, so later store outages cannot shorten his access. **What remains:** the time between `released_at` and delivery is not cooling-off; nothing is counted until delivery.

### 1.5 Every read gets released (D20C-A-4)

- **Cycle completion.** A cycle's report cannot be marked complete while any counted read has no delivered release. Such a read shows `PENDING_RELEASE` by evaluation ID. Withholding a release blocks completion; it does not hide the read. The pre-read entry already shows that it happened.
- **Lineage (P-3, Q3).** `begin_read` refuses a descendant while any ancestor's read has no delivered release, with a new pre-read reason code `ANCESTOR_UNRELEASED`. It is fixed before any lockbox byte, so Q2b's "show the reason" applies. A released FAIL ancestor bars the descendant as before (`BARRED_DESCENDANT`).
- **No automatic release.** Rule 5 of the sketch ("released afterwards by the same command") is kept as the only route; completion and lineage now enforce it.
- **Owner timing.** Release order and time cannot change a result (§1.2, given R3). The owner's decision on one family may reflect another family's released result, which is R4, already accepted. **R4 does not authorise omission;** omission is now blocked by the two rules above.

### 1.6 Timing residual R5c (replaces rev 8's R5)

**Owner-visible interfaces, all of them:** the code `request_release` returns; how long it takes; the delivery files and their times; and, during an open read, anything visible from a login on the lockbox machine, which §1.1 forbids to the owner.

**What can still leak:**
1. **Before `R_0`:** nothing through `request_release`; `NOT_YET` never contacts the store. If the publisher's and store's clocks disagree by more than 60 s, a request can reach the store and wait on `L_store`. That is a logged fault. Its hint (that a finish was in progress) is part of this residual.
2. **After `R_0`:** a release waits on `L_store` if another operation holds it:
   - a finish of **this** read stalled for 12 h or more past `D*` (a fault). The wait reveals that the read ran to the end, though not PASS versus performance FAIL, and the release shows the result anyway;
   - sealed work of **another** open read (its finish, its gate check). That can reveal the other read's progress before its own release.
3. **Machine activity** (CPU, disk) is visible to anyone logged in to the lockbox machine during a read. The owner and research have no login during an open read (§1.1, an S4 procedure). Maintenance during an open read is done by the reconciler under the D20L-76 gate. This rests on procedure and cannot be tested.
4. **Signing:** none before the result is delivered. After delivery, a signing fault delays only the attestation of a result the owner already holds.

**How much:** not measured; no bound is claimed. **What it cannot do:** change a result or a counted try. Unlike rev 8's R5, it cannot delay a result's release by days or cause a cap expiry. Only the owner's own request time, or a signing fault, can delay a PASS's cooling-off.

### 1.7 Proposed Constitution §7 row (replaces rev 8 §1.4; proposal only, only if the owner accepts QC3)

| Ref | Current v1.0 text | Proposed v1.1 text |
|---|---|---|
| §7 l.79 | "Research receives PASS/FAIL only." | "Research receives PASS/FAIL only, except that the cycle outcome of §5 may show that a family had no result because its lockbox read failed technically. How quickly the lockbox service answers a release request, and an attestation delayed by a signing fault after its result was released, are not results under this rule, even where they allow a guess about a result or about another read's progress. This exception covers only these timing effects of the lockbox service specified in the protocol. It permits no added research-visible field, message, record or diagnostic: audit, incident and delivery records required by the protocol may exist, and what research can see of them is limited to a release's time, a delivery's time and the cooling-off start. No component may vary its timing to convey a result." |

The first sentence is D-12 Q2a's row, as in rev 8. This row is narrower than rev 8's: no delayed or missed releases, and no cap expiry caused by them.

### 1.8 Crash points (rows 1-9, 11, 12 of rev 8 stand; rows 10 and 13 are replaced)

P = process crash, M = machine crash, with rev 8's outcomes for un-fsynced data.

| # | Crash at | After restart | Effect |
|---|---|---|---|
| C1 | `NOT_YET` answered | nothing written | none |
| C2 | release entry line written, fsync not completed | P: whole. M: whole, lost, or partial | whole: it is the release (nothing was shown before its fsync); lost: no release, retry; partial: rev 8 row 4 (§26 stop) |
| C3 | release fsync completed, before delivery | release durable, no delivery entry | the next request delivers; `delivered_at` is later; any finish refuses (rule 5) |
| C4 | delivery file linked, directory not fsynced | P: present. M: present or absent | no delivery entry, so not delivered; redelivered with the same content |
| C5 | delivery entry written, fsync not completed | P/M: whole, lost, or partial | whole: delivered at `delivered_at`, and the code was not yet shown; lost: redelivered later; partial: §26 stop |
| C6 | after the delivery entry's fsync, before the code is shown | delivered | the owner's file is there; the next request shows `DELIVERED` |
| C7 | signer asked, before the attestation link | no attestation | `ATTESTATION_PENDING`; retry; a deterministic scheme gives the same bytes |
| C8 | attestation linked, not yet delivered | present or absent (M) | not effective until its delivery entry is durable (C4-C6) |
| C9 | revision or invalidation between C8 and its delivery | attestation void (P-6 l.245) | never effective |

Apart from the §26 stops, every row leaves one set of durable records. Delivery can only be later than it would have been without the crash.

### 1.9 Tests (replace rev 8's T-S1 release half, T-S3 and T-S5; rev 8's T-S1 `begin_read` half, T-S2, T-S4 for rows 1-9, 11, 12, and T-S6 stand)

**TC-1 `NOT_YET`.**
- At publisher clock `R_0 + 59 s`, the answer is `NOT_YET` and the store records **no call**: an instrumented store raises on any contact.
- At `R_0 + 60 s` with the store clock at `R_0 − 1`, the store refuses and the fault is logged.

**TC-2 one result.**
- A PASS finish with `t_f < D*` stalled inside its hold across `R_0`: the release waits, then shows PASS.
- A finish whose hold starts after the release entry: refused under rule (5), even with the store clock set back below `D*` (the clock-free proof).
- A second release returns the same entry.
- A corrupted RESULT bundle with a finished record: §26 stop, not FAIL.

**TC-3 delivery.** Inject a crash at each of rows C2-C6, under P and M, using rev 8's test file layer:
- `delivered_at` is never earlier than the read-back of a durable file;
- the promotion guard refuses a decision earlier than `delivered_at + 72 h`.

**TC-4 signing.**
- A refusal, timeout or P-8 mismatch leaves the PASS delivered with `ATTESTATION_PENDING` and writes no FAIL.
- At store clock C, nothing is signed.
- A revision before delivery voids the attestation (C9).
- A deterministic scheme gives identical bytes on retry.

**TC-5 completion and lineage.**
- A cycle with one undelivered counted read cannot be marked complete and lists `PENDING_RELEASE`.
- A descendant `begin_read` with an undelivered ancestor returns `ANCESTOR_UNRELEASED` before any lockbox byte.

**TC-6 interface.**
- Each of the four codes has fixed bytes.
- An injected exception in the publisher, signer or store prints only `STOPPED`.
- The owner account cannot read the logs, stderr or sealed directory. §16 review also checks this; the test checks only the configured ACLs.

**TC-7 cap and status.**
- A PASS delivered at `C − 71 h` warns; the guard refuses a decision after C.
- A PASS first released after C shows PASS, has no attestation, and has status `U_ops`.
- A FAIL is never `U_ops`.

None of these tests measures timing. No timing property is claimed.

## 2. D-12 crosswalk (D20C-A-7; what a new owner decision must cover)

| D-12 material | Treatment under option C |
|---|---|
| P-1 PASS-only attestation; Q1 | **Unchanged** in substance. The attestation now names the release entry hash instead of `cooling_off_start` (§1.3). |
| P-2 signer checks | **Kept.** The guard gains "after a PASS release entry exists" and "before C" (§1.3). |
| P-3 every technical FAIL counts; Q2a; Q3 | **Semantics kept.** Enforcement gains `ANCESTOR_UNRELEASED` and the completion rule (§1.5). |
| P-4 vector check; Q2b | **Unchanged.** Q2b also covers `ANCESTOR_UNRELEASED`. |
| Q4, Q5 (reproduction, sealed details) | **Unchanged.** |
| P-5 cooling-off from `R_j`, availability hours | **Replaced** by cooling-off from the attestation's delivery (§1.4). |
| P-6 cap and revision; Q6(ii) | **Intent kept.** The guard and statuses are made explicit, and l.245 is restated (§1.3, §1.4). |
| P-7 fixed daily release, missed releases | **Deleted.** The release happens on request at or after `R_0` (§1.2). |
| P-8 publisher validation | **Kept**, applied after release (§1.3). |
| Q6(i) separate posting job | **Kept.** The owner triggers it; THREAT_MODEL l.9 changes as D-12 planned (§1.1). |
| Actors, steps 2 and 5, record shapes | Step 2 unchanged. Step 5 gains rule (5). The release entry loses `visible_from` and `attestation_ref`, and gains `released_at`. A new delivery entry is added (§1.2, §1.4). |
| R1 signing fault | **Narrowed:** it can no longer delay or hint at a result, only delay a PASS's cooling-off after delivery. |
| R2 faulty signer | **Unchanged.** |
| R3 trusted store | **Changed:** it now trusts the clock for `D*`, C, the cooldown, `R_0` and the 72 h, and the delivery read-back. It no longer trusts a `visible_from` filter or an availability log. |
| R4 owner judgement | **Unchanged.** It does not authorise omission (§1.5). |
| T-1 nothing readable before `visible_from` | **Replaced** by TC-1 (nothing shown before `R_0`) and TC-6. |
| T-2 refuse insert at or after `R_j`; one entry | **Replaced** by TC-2 (one entry; refuse before `R_0`). |
| T-3 all outcomes publish at `R_0` alike | **Replaced:** every outcome takes the same release path (TC-2). A PASS's extra signing comes after delivery (TC-4). |
| T-4 outage moves every outcome to `R_{j+1}` | **Deleted** (no schedule). An outage delays a request alike for every outcome (TC-3). |
| T-5 crash before or after insert | **Replaced** by TC-3 and rows C2-C9. |
| T-6 cap and revision keep outcomes | **Kept** as TC-7 plus C9. |
| T-7 reader outage moves the decision time | **Deleted;** cooling-off starts at delivery (TC-3). |
| T-8 signer fault on PASS | **Replaced** by TC-4. |

## 3. Comparison (D20C-A-8)

| | Revision 8, if revised again | Option C1 |
|---|---|---|
| Review status | rev 8: Sol FIX (1 BLOCKER, D20LR8-S-1); no Astra re-check; no rev 9 exists | unreviewed; the sketch had 4 BLOCKERs, answered here, not yet checked |
| One shown result | needs a cross-call clock invariant not yet specified | clock-free once released (§1.2); deadlines trust the clock |
| Timing hints | R5: lock waits during and after a read; release slips by days; cap expiry | R5c: lock waits after `R_0` from a 12 h stall or another read; machine activity by procedure; no slips |
| Mechanisms still to design and test | availability log (D20L-70), T-7 | delivery read-back and guard (§1.4), completion and lineage rules (§1.5), owner capability boundary (§1.1) |
| D-12 re-decision | none for the schedule; Q7's step-5 and P-7 reading | P-5 and P-7 replaced, P-1/P-2/P-6/P-8 reworded; Q6(i) kept; Q7 narrower |
| Owner's role | none in releasing | asks for each release; must release every read (§1.5) |

**Recommendation (AI drafting choice, conditional):** option C1, **if** its review finds the §1.2 proof, the delivery rule and the §1.1 boundary sound. Otherwise, keep blocked or return to revision 8.

## 4. Owner questions (replace rev 8's Q1, Q6, Q7; Q2(i), Q2(ii), Q3-Q5 unchanged; each has "Keep blocked")

**QC1. Switch the lockbox to "release on request"?**

*In short:* instead of a posting job on a fixed daily timetable, nothing about a test can be asked until seven days after it started. Then you ask, and the posting job releases the result to you: PASS or FAIL, nothing else. Your 72-hour waiting period starts when a PASS's signed certificate is in your own records.

This changes your D-12 decisions as follows:
- **kept:** the separate posting job, PASS or FAIL only, every technical fail counts;
- **replaced:** the daily timetable and its "moved to the next day" rule; the 72-hour count based on service uptime;
- **reworded:** the signer's checks and the day-255 rule.

You must ask for every test's result. A cycle cannot be completed, and a later pick from the same line cannot be tested, while any result is unreleased.
- **"Switch to release on request (Recommended)."** Cost: you run one command per test; the rule changes above go into C2.
- **"Keep the daily timetable (revision 8)."** A revision 9 would be needed.
- **"Keep blocked."**

**QC2. Adopt the detail rows?** As rev 8's Q1, with these changes:
- the release, delivery and signing rules of §1.2-§1.4;
- the completion and lineage rules of §1.5;
- one new rule: no login for you on the lockbox computer while a test runs.

Adopting QC2 does not settle D11-15; the D20L-36 sentence stands.
- **"Adopt (Recommended)."** Cost: several builds, each needing §16 review. A lost key can cost a good PASS (its certificate can never be signed).
- **"Keep blocked."**

**QC3. May the service's speed give small hints?**

*In short:* after a test's seven days are up, the release can be slower if the computer is busy with another test that is still running, or if this test's last save got stuck. Someone timing it closely might guess that the other test is near its end. A signing fault on a PASS delays only its certificate, after you already know it passed. Results are never delayed by days, and none expires because of the service. The Constitution says research receives PASS/FAIL only, so allowing these hints needs the written exception in §1.7, which you would sign in C2 after a person reviews it.
- **"Accept the narrower exception (Recommended)."**
- **"Keep blocked."** Stronger separation would be needed, for example one test at a time or separate machines. This draft does not propose that.

**Q7. When does a save count as made in time?** Rev 8's Q7, now for **two saves only**: starting a test (before day 255) and finishing a test (before the worker deadline). Posting no longer has a deadline. The stricter rule's cost reads: "needs additional durable evidence and design work" (D20LR8-S-2). Options as in rev 8.

## 5. Findings, remaining, unauthorised, self-check

**New findings** (continuing rev 8's D20L numbering):
- **D20L-76 BLOCKER (repaired; §1.1).** The owner's capability boundary was undefined (D20C-A-3), and the reconciler could see sealed facts (D20LR8-S-3). Fixed operation and codes; logs and views withheld; S4 gate on the reconciler.
- **D20L-77 BLOCKER (repaired; §1.4).** Cooling-off from entry creation could give less than 72 h of access (D20C-A-1). It now runs from the confirmed delivery.
- **D20L-78 BLOCKER (repaired in part; §1.2, §1.3, §1.6).** Early requests waited on sealed work, and signing faults hinted at a PASS (D20C-A-2). Now `NOT_YET` makes no store contact and signing follows release. The after-`R_0` residual remains, disclosed, and goes to QC3.
- **D20L-79 BLOCKER (repaired; §1.5).** Eventual release was not enforced (D20C-A-4).
- **D20L-80 BLOCKER (repaired; §1.3, §1.4).** Post-cap signing and status conflicted (D20C-A-5).
- **D20L-81 NON-BLOCKING (repaired; §1.2, §1.8).** The clock and durability reductions were overstated (D20C-A-6).
- **D20L-82 QUESTION.** Should a release wait until no **other** read is open, to remove R5c item 2? It would delay releases while another family reads and add a scheduling rule. It is not proposed; reviewers may disagree.

**Remaining:**
- the R19-2 two-family review of this revision;
- owner QC1-QC3 and Q7, then Q2(i), Q2(ii), Q3-Q5 as before;
- S4 items: the capability mechanism, the reconciler and view (D20L-76), and the no-login procedure;
- the consolidated S4 signing text;
- the C2 rows (crosswalk §2, the §7 row if QC3 is accepted);
- the builds: publisher release and delivery, the guard, completion and lineage, and tests TC-1..TC-7 with rev 8's test file layer, each under §16 review.

**Unauthorised:** frozen edits; activation; acceptance; any code; key generation; simulation; confirmation or lockbox access; promotion; deployment; trading. `KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid outcomes.

**Self-check:**
- one file written in this step;
- D20C-A-1..8 and D20LR8-S-1..3 all answered;
- new findings D20L-76..82, no gaps;
- mechanisms deleted: `state`, `guard_state`, `insert_release`'s window, the `R_j` schedule, the missed-release rule, pre-release signing, the availability log;
- mechanisms added: rule (5) in `mark_finished`, `release`, the delivery entry and read-back, the promotion guard's delivery bound, `ANCESTOR_UNRELEASED`, the completion rule, the fixed owner codes.
