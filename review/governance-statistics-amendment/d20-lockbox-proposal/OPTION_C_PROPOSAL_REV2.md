# D-20 lockbox bindings, option C: release on request (revision C2; replaces C1 whole; delta on revision 8)

**Author:** Claude Opus 5.5 (`claude-opus-5-5`, this session's environment metadata), main Claude Code session, 2026-10-30. AI drafting, not an authority. I propose and check bindings. I cannot decide, accept, activate or amend anything.

**Status: INACTIVE PROPOSAL, UNREVIEWED.** Nothing frozen changed. No row binds until the owner decides and signs the C2 §4 amendment. R19-2 requires a two-family re-check of this revision before any owner decision. No human statistician has reviewed it. `OPTION_C_PROPOSAL_REV1.md` (c604827) and the sketch stay as history.

**Owner direction (2026-10-30):** "Go ahead" with revision C2 answering both C1 reviews. Standing direction: simplify rather than patch, claim only what is true and testable.

**Answers** (both read in full):
- `SOL_OPTION_C1_REVIEW_C604827.md` (gpt-6-sol): FIX, D20C1-S-1..7;
- `ASTRA_OPTION_C1_REVIEW_C604827.md` (gpt-6-astra): FIX, D20C1-A-1..8.

**How to read it.** This revision replaces C1 whole and, like C1, is a **delta on `PROPOSAL_REV8.md`**.
- **Kept from rev 8 §1.2 (the read side):** records; `L_store`; durable before use; the time rule for `begin_read` (deadline C) and `mark_finished` (deadline `D*`, steps 1-4); start checks; cap scope; `begin_read`; the read gate; startup; crash rows 1-9, 11 and 12; tests T-S2, T-S4 for those rows; T-S6.
- **Changed:** `mark_finished` gains step 2a (§1.3).
- **Replaced:** rev 8's B1 row; "The result", its proof and its step-5/P-7 reading; the availability carry-forward; crash rows 10 and 13; tests T-S1 (release half), T-S3, T-S5; §1.3 R5; §1.4 §7 row; Q1, Q6, Q7.
- **Inherited clauses superseded** (D20C1-A-7): listed in §1.10.
- **Unchanged:** the A-rows, B2, B3 (except as §1.10 says), B4.2, B4.4, B5, B6, the fixture, Q2(i), Q2(ii), Q3-Q5. The consolidated S4 signing text remains an obligation (D20L-59).

**VERDICT: `AMENDMENT_REQUIRED`.**

## 0. What both reviews established, and the main changes

**Both reviews confirm the core** (Sol l.5, Astra l.29-40): once a release entry is durable, the shown result cannot change, whatever the clock does. Concurrent releases return the same entry. The proof's wording needed a fix for the post-lookup-fsync case (§1.3).

**The main changes from C1:**
1. **The certificate keeps `cooling_off_start`** (Constitution §13 l.124; `schemas/attestation.schema.json` requires it; D20C1-A-3). It is set to the moment the **owner's own account** read the PASS (the result delivery), and it is signed after that moment. Cooling-off is the owner's 72 hours with the result in hand. A later certificate delay therefore cannot shorten it.
2. **One authoritative transition makes a certificate effective:** the store's attestation-delivery entry, appended under `L_store`. It checks the cap and every revision or invalidation entry at that same point. Index order decides against a revision (D20C1-S-3, A-4).
3. **Delivery is idempotent and proven by the owner's account** (D20C1-S-1, A-5).
4. **A backstop release:** if the owner has not asked, the publisher releases every read at `R_0 + 7 days`, and at a revision, invalidation or termination. The result is recorded either way, so nothing can stay unreleased (D20C1-S-4).
5. **The residual and the §7 row now state the full risk:** waits of any length, including before `R_0`, can consume day-255 slack and cause expiry. The `STOPPED` code is a disclosed owner-visible fact. "Small" and "never delayed by days" are deleted (D20C1-S-5, A-2).

**Verification (read this session):**
- both C1 review records in full;
- `OPTION_C_PROPOSAL_REV1.md` (this session's own file);
- Constitution §13 l.121-126;
- `schemas/attestation.schema.json` (required fields include `cooling_off_start`);
- rev 3 l.176-220 (role table, signer guard, compromise rule, B3a) and l.305-311 (B4.3);
- rev 4 l.92-110 (B1, B3a), l.175 (B4.3 release entry);
- rev 5 l.55, rev 6 l.113;
- `OWNER_DECISION_D12.md`;
- D-12 `PROPOSAL_REV7.md` l.76-150;
- THREAT_MODEL l.1-20.

## 1a. Dispositions

| ID | Disposition | Repair |
|---|---|---|
| **D20C1-S-1 = D20C1-A-5** (BLOCKER / NON-BLOCKING; delivery idempotency, owner access) | **Accepted.** Two delivery kinds per evaluation, RESULT and ATTESTATION, each with at most one index entry. Deterministic file names and bytes. An existing file is verified and reused, never re-created. A publisher lock serialises requests per evaluation. Delivery completes only when **the owner's account** has read the file and returned its hash. | §1.4; TC-3 |
| **D20C1-S-2 = D20C1-A-1** (BLOCKER; `NOT_YET` not independent) | **Accepted, by narrowing the claim.** `NOT_YET` only avoids taking `L_store`. Publisher and store read one host clock, so no skew case exists (S4 binding). The publisher's `R_0` copy is durable and recovered. Shared-resource dependence before `R_0` is disclosed. | §1.2, §1.7, §1.8 |
| **D20C1-S-3 = D20C1-A-4** (BLOCKER; effectiveness across cap and revision) | **Accepted.** Effectiveness is one store append under `L_store`, checking `t < C` and the index for any revision or invalidation entry. Revisions are index entries too, so index order is authoritative. A refused effectiveness writes a permanent VOID entry. The signing cutoff is advisory; a signature made late is never effective. Uncertain completion follows the Q7 save rule, now listed for this save too. | §1.5; Q7 |
| **D20C1-S-4** (BLOCKER; eventual release) | **Accepted.** Backstop release at `R_0 + 7 days`, and at revision, invalidation and termination. The owner receives the pending list. Completion uses "released", not "delivered". | §1.6 |
| **D20C1-S-5 = D20C1-A-2** (BLOCKER; residual understated) | **Accepted.** Every callable and operational path is listed. Delays of any length, including those exhausting day-255 slack, are disclosed. `STOPPED` is covered. No claim is made about PASS versus performance FAIL. QC3 and §1.8 are rewritten. | §1.7, §1.8, §3, QC3 |
| **D20C1-S-6 = D20C1-A-6** (NON-BLOCKING; proof wording, tests, clock list) | **Accepted.** The proof is recovery-aware; the clock inventory is complete; rev 8's qualification is kept; `D* ≤ R_0 − 12 h` is no longer said to bound a hold; tests added; the T-4 crosswalk is corrected. | §1.3, §1.9, §2 |
| **D20C1-A-7** (NON-BLOCKING; inherited clauses) | **Accepted.** Superseded clauses are listed one by one. The signer's guard source and the publisher's permitted pre-read metadata are specified. | §1.1, §1.10 |
| **D20C1-S-7 = D20C1-A-8** (QUESTION; D20L-82 wait rule) | **Accepted: not adopted.** Recorded as an isolation alternative requiring its own design. | §4 |
| C1's D20L-76..81 | Superseded by D20L-83..89 (§4). | |

## 1. Bindings

### 1.1 Actors and capabilities (replaces rev 8's B1 row and rev 3's role table, l.176-183)

| Identity | May do | Receives | Never |
|---|---|---|---|
| **owner** | Run the fixed operation `request_release <evaluation_id>` (§1.2) as a forced command over the channel S4 fixes. The command is not a login shell. Read his own record directory, which is on a machine other than the lockbox machine. | One response code (below). On delivery, the delivery file, which the owner's side of the command copies into his record. The pending list (§1.6). | An interactive login, shell or debugger on the lockbox machine while any read is open (§1.7); the sealed directory; logs or stderr of any lockbox process; reconciliation views |
| **publisher** (separate OS identity, D-12 Q6(i)) | `begin_read`; `release`; `record_delivery`; `sign_permit` requests on the signer's behalf; the backstop (§1.6); its own lock `L_pub` and its own `R_0` file | From `begin_read`: `R_0` and the pre-read identity fields (evaluation ID, family, nominee ID, prediction-artifact hash, eligibility and lockbox IDs) for P-8. From the store: release entries and delivery entries. From the signer: the attestation. | commitments' preimages, nonces, sealed bundles, cause classes, finished-record presence or time before release, lockbox bars |
| **signer** (`lockbox_eval`'s key, THREAT_MODEL l.9) | Sign one attestation per evaluation, only on a `sign_permit` (§1.5) obtained from the store, never on the publisher's word | The permit, which carries the message fields and the sealed record reference it verifies (P-2) | Any other index row |
| **worker** (`lockbox_eval`) | As rev 8, plus step 2a (§1.3) | lockbox bars through the read gate | index writes |
| **reader** (replaces rev 3 l.183) | Index rows of public accounting only: pre-read entries (identity fields, `R_0`), rejection entries, release entries **after their RESULT delivery entry, or from calendar termination for every released read** (the cycle report, §1.6), delivery entries, revision entries | | everything else |
| **reconciler** | §26 reconciliation | A view fixed by S4 | **S4 gate (D20LR8-S-3):** S4 names this person and a view that cannot show the owner a sealed result or an undelivered release. If no such person or view exists, that is a Constitution question put to the owner before the access design is adopted. |

**Response codes.** A request returns exactly one code, with fixed bytes. **Precedence:** `STOPPED` first; then the evaluation's state.

| Code | When |
|---|---|
| `STOPPED` | A §26 stop is active, or this request hit an error. Errors are never printed; they go to logs the owner cannot read. |
| `NOT_YET` | The host clock is before `R_0`. |
| `FAIL` | Released FAIL, delivered. |
| `PASS_CERTIFICATE_PENDING` | Released PASS, delivered, with `cooling_off_start`; no attestation delivery yet. |
| `PASS_CERTIFIED` | Attestation delivered and effective. |
| `PASS_NOT_CERTIFIABLE` | Attestation VOID: cap or revision. |

Evaluation IDs are authorised at the command boundary: an ID that has no pre-read entry, or that belongs to another cycle's closed record, returns `STOPPED`, logged. §16 review checks that nothing else reaches the owner.

**THREAT_MODEL l.9:** as D-12 planned: the publisher identity is added; `lockbox_eval` keeps "lockbox read + attestation signing only".

### 1.2 The request (replaces C1 §1.2 step 1)

The publisher runs one request per evaluation at a time, under `L_pub(evaluation_id)`, a lock no sealed or store operation takes.

1. **`NOT_YET` without `L_store`.** If the host clock is before `R_0`, answer `NOT_YET`.
   - `R_0` comes from the publisher's own `R_0` file. That file is written durably, by write-temp, fsync, link, directory fsync, before the publisher returns `begin_read`'s success.
   - If a crash loses the reply or the file, the publisher recovers `R_0` by re-reading the pre-read entry through `begin_read`'s idempotent lookup. That lookup takes `L_store`, so a request made during recovery can wait on store work (§1.7 item 1).
   - **What is claimed:** an ordinary `NOT_YET` does not acquire `L_store`. **What is not claimed:** that its latency is independent of sealed work. Publisher, store and sealed work share one machine (§1.7).
   - **Clock:** publisher and store run on the same host and read the same system clock (an S4 binding). The store still refuses a release before `R_0` (step 2); a refusal is logged and answered `STOPPED`.
2. **`release`** (§1.3).
3. **Result delivery** (§1.4).
4. **On PASS: signing and attestation delivery** (§1.5), unless the attestation is already effective or VOID.
5. Return the code (§1.1).

### 1.3 One result: the first release fixes it (replaces rev 8's "The result")

**`release(evaluation_id)`**, under `L_store`, after rev 8's lookups and then fsyncs:
- If the store clock is before `R_0`, refuse.
- If a release entry exists, return it.
- Otherwise the result is the finished record's `{result, commitment}` if one exists and its RESULT bundle verifies. A bundle that does not verify is a **§26 stop** (`STOPPED`), never a silent FAIL (§6 l.70; disclosed in §1.7 and §1.8). With no finished record, the result is the DEFAULT's FAIL.
- Append `{evaluation_id, result, commitment, released_at}` and fsync it before unlocking. `released_at` is the clock reading under the lock.

**`mark_finished` step 2a (new):** in step 2, under `L_store` and after the lookups and fsyncs, refuse if a release entry exists for the evaluation. The bundle is then late output, void.

**Proof that a shown result cannot change (recovery-aware; D20C1-S-6, A-6).** Nothing shows a result until a release entry is durable, because steps 3-5 of §1.2 run only after `release` returned. Take any finish F and the first durable release entry E.
1. **F's hold came before E's.** Then F's finished record is either:
   - durable; or
   - linked but not yet directory-fsynced (a crash after F's link and before its fsync).

   In the second case, E's lookup either finds the name, and E's post-lookup fsync makes it durable before E uses it, or does not find it, and E uses the DEFAULT. Either way, E's result matches the records that survive. No result was shown before E.
2. **E's hold came first.** Then F finds E in step 2a and refuses.
3. **A crash loses E before its fsync completed.** Then nothing was shown, and a later release is the first durable one.
4. **A second release** returns E.

So every shown result equals E's. **No clock assumption is needed for this.** Conditions: rev 8's durable-before-use rule, fail-closed recovery (a partial index tail is a §26 stop), and the platform assumptions, which stay `UNVERIFIED_EXTERNAL_ASSUMPTION`.

**What still trusts the clock** (R3; complete list, D20C1-A-6). Every clock is the one host clock.

| Check | Clock reading |
|---|---|
| worker deadline `D*` | `t_f` in `mark_finished` |
| cap C | admission, `sign_permit`, effectiveness (§1.5), the promotion guard |
| 30-day cooldown | its check |
| `R_0` | publisher `NOT_YET`; store `release` |
| `released_at`, `delivered_at`, `cooling_off_start` | when each is taken |
| the backstop time `R_0 + 7 days` | the backstop's check |
| "72 hours of actual access" | elapsed host time across restarts |

A backward step can break any of these, but none of them can change a result already released.

**D-12 step 5 under this.** "Only while the store clock is before `D_w`" becomes rev 8's `t_f < D*` under `L_store`, plus step 2a. **Rev 8's qualification stands:** a finish whose clock check was before `D*` may still be saving after `D*`. It survives or is lost in a crash. "After `D*` no new finish counts" means no new clock check qualifies, not that saving has ended. `D* ≤ R_0 − 12 h` separates the thresholds; it does **not** bound how long a finish holds `L_store` (D20C1-A-6). This reading goes to Q7.

### 1.4 Delivery, proven by the owner's account (D20C1-S-1, A-5)

**Two delivery kinds per evaluation:**
- **RESULT:** `{evaluation_id, result, released_at, release_entry_hash}`;
- **ATTESTATION:** the attestation bytes.

Each has a deterministic file name, `<evaluation_id>.<kind>.json`, and deterministic bytes (canonical JSON; the signature scheme is deterministic).

**Delivery of one kind**, under `L_pub(evaluation_id)`:
1. **Publisher, outbox.** If the outbox file exists, verify that its bytes equal the expected bytes. A mismatch is a §26 stop. Otherwise create it: write temp, fsync, link without replacing, fsync the directory. The outbox is readable by the owner's command account only.
2. **Owner's side** (the forced command, running as the owner's account). Read the outbox file, copy it into the owner's record directory (write temp, fsync, link, fsync the directory), read the copy back, and return its SHA-256 to the publisher.
3. **Publisher → store, `record_delivery(evaluation_id, kind, hash)`**, under `L_store`, after rev 8's lookups and then fsyncs:
   - if a delivery entry of this kind exists, return it;
   - if `hash` is not the expected file's hash, refuse (`STOPPED`, logged);
   - otherwise append `{evaluation_id, kind, file_hash, delivered_at}`, where `delivered_at` is the clock reading under the lock, after the owner's read-back. For ATTESTATION, §1.5 adds the effectiveness checks to this same append.

**What this proves.** `delivered_at` is never earlier than the owner account's durable copy, because step 3 runs only after step 2 returns the copy's hash. Every crash or retry repeats steps 1-3 with the same bytes. An existing file is reused, and an existing entry is returned. So delivery can be later than intended but **never earlier**. Two concurrent requests are serialised by `L_pub`, and the store keeps at most one entry per kind.

**Uncertain completion.** An entry line written whole but not yet fsynced when the machine crashes may survive whole (rev 8 row 2 pattern). It then counts at its `delivered_at`. Nobody was shown the code, because the code is returned only after the fsync. This is the Q7 save rule, which now lists delivery.

**Owner access after delivery.** The owner holds a durable copy on his own machine, so later store or lockbox-machine outages cannot shorten his access. Keeping that copy (backups) is the owner's responsibility. The record directory must not be on the lockbox machine (§1.1).

### 1.5 Cooling-off, signing and effectiveness (replaces C1 §1.3-§1.4; D20C1-S-3, A-3, A-4)

**Cooling-off start** = the RESULT delivery's `delivered_at` for a PASS: the moment the owner's account had the PASS in hand. **The attestation binds it** as `cooling_off_start`, as Constitution §13 l.124 and the frozen schema require. D-12 P-5's "cooling-off from `R_j`" is replaced by this (§2).

**`sign_permit(evaluation_id)`**, under `L_store`. The store answers PERMIT only if all of these hold:
- the release entry says PASS;
- a RESULT delivery entry exists;
- no ATTESTATION delivery or VOID entry exists;
- no revision or invalidation entry follows the pre-read entry in the index;
- the store clock is before C.

The permit carries the message fields: the frozen schema's hashes, eligibility and lockbox IDs, and `cooling_off_start`. It also carries the sealed record reference for P-2. The signer verifies the sealed record against the release entry's commitment, checks P-2, signs deterministically, and creates the sealed attestation file without replacing; if that file exists, it must equal the new bytes. The publisher validates the attestation (P-8: signature, identity fields equal the pre-read entry, the three fields, `cooling_off_start` equals the RESULT `delivered_at`) and delivers it as ATTESTATION (§1.4).

**Effectiveness: the one authoritative transition.** `record_delivery(evaluation_id, ATTESTATION, hash)` under `L_store`, after the lookups and fsyncs:
- If the store clock is before C **and** no revision or invalidation entry follows the pre-read entry in the index, append the ATTESTATION delivery entry. **The attestation is effective from this entry.**
- Otherwise append `{evaluation_id, kind: VOID, reason: CAP | REVISION}`. The attestation is **never** effective; any later request returns `PASS_NOT_CERTIFIABLE`.

**Revisions and invalidations** (P-6 l.245) are recorded as index entries `{kind: REVISION | INVALIDATION, at}`, appended under `L_store` by the governance action S4 names. **Index order is authoritative:** an ATTESTATION delivery entry before the revision entry is effective, and stays effective after it (P-6: "an attested nominee is unaffected"). One after it is impossible, because the check above writes VOID instead.

**The signing cutoff is advisory.** A signer may stall past C after its permit. Its signature is then refused at effectiveness and recorded VOID. No signature becomes effective after C or after a revision.

**A signing refusal, timeout or P-8 mismatch** writes nothing. The code stays `PASS_CERTIFICATE_PENDING`, and the next request retries; if the sealed attestation file exists, it is reused, not re-signed. **The PASS result never changes.** A FAIL is never written, and a certificate never becomes effective late.

**Four separate facts per evaluation:**

| Fact | Values | Changes |
|---|---|---|
| result | PASS or FAIL (release entry) | never |
| delivery | RESULT `delivered_at`; ATTESTATION `delivered_at` | each written once |
| attestation | none, effective, VOID | VOID and effective are final |
| promotion status | eligible, promoted, `U_ops`, n/a (FAIL) | the promotion guard |

**Promotion guard.** It accepts an owner decision at time `t_dec` only if:
- the attestation is effective;
- `t_dec ≥ cooling_off_start + 259,200`;
- `t_dec ≤ C`.

Otherwise:
- a PASS that cannot meet these by C is `U_ops` (P-6);
- a PASS released or delivered after C shows PASS, its attestation is VOID or none, and it is `U_ops`;
- a FAIL is never `U_ops` (T-6).

`request_release` warns when `now + 72 h` is past C. That is a convenience; the guard enforces the cap.

### 1.6 Every read is released (D20C1-S-4)

- **Backstop.** At `R_0 + 604,800`, and at every revision, invalidation and calendar termination, the publisher runs `release` and outbox step 1 for every counted read without a release entry. This is a fixed-time step whose path does not depend on the result. A failure is retried; the result is already fixed by the first durable release (§1.3).
- **Pending list.** At each backstop run and at termination, the owner receives the list of counted evaluation IDs without a RESULT delivery entry, as public accounting only, through the forced command's pending view.
- **If the owner never asks**, every read is still released. Its result stands in the index, and the cycle report shows it. Only RESULT delivery, and so cooling-off, waits for the owner.
- **Completion.** A cycle report is complete only when every counted read has a release entry. The backstop guarantees that by the later of `C + 14 days` and the last revision or invalidation. Incompleteness never postpones termination, invalidation or cap effects: those apply at their own time.
- **Lineage** (P-3, Q3). `begin_read` refuses a descendant while any ancestor's read has no release entry: reason `ANCESTOR_UNRELEASED`, fixed before any lockbox byte (Q2b). The same code and bytes are returned whatever the ancestor's hidden result. A released FAIL ancestor bars the descendant (`BARRED_DESCENDANT`), recorded at that time (§1.10).
- **Owner timing.** When the owner asks cannot change a result (§1.3). Using one family's released result in deciding another is R4, already accepted. **Omission is not R4:** the backstop removes it.

### 1.7 Timing residual R5c, all paths (replaces C1 §1.6; D20C1-S-5, A-1, A-2)

**Owner-visible facts:**
- the response code and its latency, for every request, before and after `R_0`;
- the times in delivery files and the pending list;
- `STOPPED`, whenever a §26 stop is active.

**What can delay a response or a step, without bound:**
1. **Before `R_0`:** shared CPU, memory and disk with sealed work and with other reads. `L_pub` waits behind this evaluation's own recovery. The `R_0` recovery lookup takes `L_store`.
2. **After `R_0`, every `L_store` holder:**
   - `begin_read` and rejection appends of any evaluation;
   - the read gate of any open read;
   - `mark_finished` of any read (including this one if stalled);
   - `release`, `record_delivery`, `sign_permit` and revision entries of any evaluation;
   - startup, reconciliation, `verify_replay`.
3. **Shared resources:** the same machine's CPU, memory, disk and filesystem journal, used by all of the above and by sealed work.
4. **Delivery and signing:** owner-side copy failures, signer stalls, and §26 stops.

**What these can reveal:** that sealed work is running or finishing, for this read or another, and when. Whether PASS and performance FAIL take different time is **not known**: their compute paths differ (rev 8 R5 item 1), and no claim is made either way. `STOPPED` reveals that an incident occurred, for example a RESULT bundle that failed to verify, which implies a finished record existed.

**What they can cause:** a delay of any length in release, delivery or certification. Near day 255, that can make a PASS expire `U_ops`. **Example (Astra l.62):** a request at `C − 73 h` delayed 48 hours gives delivery at `C − 25 h` and an earliest decision at `C + 47 h`, past the cap.

**What option C does remove:** the daily missed-slot mechanism, signing before the result is known, and every `state`-type query before `R_0`. **What none of these can do:** change a result or a counted try.

### 1.8 Proposed Constitution §7 row (replaces C1 §1.7; only if the owner accepts QC3)

| Ref | Current v1.0 text | Proposed v1.1 text |
|---|---|---|
| §7 l.79 | "Research receives PASS/FAIL only." | "Research receives PASS/FAIL only, except that the cycle outcome of §5 may show that a family had no result because its lockbox read failed technically. The following are not results under this rule, even where they allow a guess about a result or about another read's progress: how quickly the lockbox service answers any request, before or after a result's earliest release time; a delay of any length in a release, its delivery or its certification, and an expiry at the processing cap caused by such a delay; and the fact that the service has stopped for an incident. This exception covers only these effects of the lockbox service specified in the protocol. It permits no added research-visible field, message, record or diagnostic: audit, incident, delivery and revision records required by the protocol may exist, and what research can see of them is limited to release, delivery and cooling-off times, the pending list and the stopped state. No component may vary its timing to convey a result." |

The first sentence is D-12 Q2a's row. This row is **not narrower than rev 8's** in what it allows about delays (D20C1-A-2). It drops rev 8's daily "missed release" wording because that mechanism no longer exists, and it adds pre-`R_0` latency and the stopped state.

### 1.9 Crash points and tests (replace C1 §1.8-§1.9)

**Crash rows.** Rev 8 rows 1-9, 11 and 12 stand. P = process crash, M = machine crash, with rev 8's outcomes for un-fsynced data.

| # | Crash at | After restart | Effect |
|---|---|---|---|
| C1 | `R_0` file temp or link, before `begin_read`'s reply | file present or absent | absent: recovered by the idempotent lookup (§1.2) |
| C2 | release line written, not fsynced | whole, lost or partial | whole: the release (no code was shown); lost: retry or backstop; partial: §26 stop |
| C3 | release durable, no RESULT delivery | | the next request or the backstop's outbox step continues; finishes refuse (step 2a) |
| C4 | outbox file linked, directory not fsynced | present or absent | present: verified and reused; absent: re-created with the same bytes |
| C5 | owner copy made, hash not yet returned | owner copy present | the retry re-reads it, returns the same hash; `delivered_at` is later |
| C6 | delivery line written, not fsynced | whole, lost or partial | whole: counts at its `delivered_at`, and no code was shown (Q7 rule); lost: redelivered later; partial: §26 stop |
| C7 | permit given, before signing or before the attestation link | no attestation file | retry: a new permit (still before C), same bytes |
| C8 | attestation file linked, ATTESTATION delivery not durable | file present or absent | reused if present; effectiveness is decided only at the delivery entry |
| C9 | revision entry appended between C8 and the ATTESTATION delivery | | effectiveness check writes VOID |
| C10 | store clock reaches C between permit and ATTESTATION delivery | | VOID (CAP) |
| C11 | backstop run interrupted | | the next run repeats it; first durable release stands |

**Tests** (rev 8's T-S1 `begin_read` half, T-S2, T-S4 rows 1-9/11/12 and T-S6 stand):
- **TC-1 `NOT_YET`:**
  - before `R_0`, an instrumented `L_store` records no acquisition;
  - after deleting the `R_0` file, recovery takes `L_store` once;
  - a store-side refusal before `R_0` is logged and returns `STOPPED`.
- **TC-2 one result:**
  - a finish stalled in its hold across `R_0`: the release waits, then shows its result;
  - a finish linked then M-crashed before its directory fsync, while a release looks it up: after restart, the release's result equals the surviving records;
  - a finish after the release entry is refused, also with the clock set back below `D*`;
  - two concurrent releases return one entry;
  - a corrupt RESULT bundle gives `STOPPED`, not FAIL.
- **TC-3 delivery:**
  - crashes at C4-C6 under P and M;
  - two concurrent requests leave one entry per kind;
  - an existing outbox file with wrong bytes gives a §26 stop;
  - `delivered_at` is never before the owner copy's durable link (instrumented order);
  - the owner-side read uses the owner account (a permission test: the publisher account cannot complete step 2).
- **TC-4 signing and effectiveness:**
  - refusal, timeout or P-8 mismatch: `PASS_CERTIFICATE_PENDING`, no FAIL;
  - an existing attestation file is reused;
  - C9 and C10 give VOID, and a later request returns `PASS_NOT_CERTIFIABLE`;
  - an effective attestation followed by a revision entry stays effective;
  - `cooling_off_start` equals the RESULT `delivered_at`;
  - the attestation validates against `schemas/attestation.schema.json`.
- **TC-5 completion, backstop, lineage:**
  - without any request, the backstop releases at `R_0 + 604,800` and at a revision;
  - the pending list contains exactly the undelivered IDs;
  - `ANCESTOR_UNRELEASED` has identical bytes for an ancestor that is PASS, performance FAIL or DEFAULT;
  - a report with an unreleased read is not complete.
- **TC-6 interface:**
  - the six codes have fixed bytes and the precedence above;
  - injected exceptions give `STOPPED` only;
  - an unknown or closed-cycle ID gives `STOPPED`;
  - the owner account cannot read logs, stderr, sealed files or the outbox of another evaluation (ACL test; §16 review for the rest).
- **TC-7 guard:**
  - a decision at `cooling_off_start + 259,199` is refused, and at `+ 259,200` accepted if `≤ C`;
  - after C, refused;
  - a FAIL is never `U_ops`.

None measures timing. No timing property is claimed.

### 1.10 Inherited clauses superseded (D20C1-A-7)

| Inherited | Superseded by |
|---|---|
| rev 3 l.180-183 role table; rev 4 l.92-93; rev 5 l.55; rev 6 l.62; rev 8 B1 (`state`, `guard_state`, `insert_release`, reader `t ≥ visible_from`) | §1.1 |
| rev 3 l.185-192 signer guard (`R_j`, `guard_state`, `store_now < R_j`, "no release entry exists") | §1.5 `sign_permit` and effectiveness |
| rev 3 l.196-198 compromise rule, second test ("a committed release entry with `visible_from = cooling_off_start` references it") | "an ATTESTATION delivery entry for this evaluation exists before any revision or invalidation entry, and the attestation's `cooling_off_start` equals the RESULT `delivered_at`". The first test (signed message equals what the guard rules produce) stands with §1.5's rules. |
| rev 3 l.213-220 and rev 4 l.101-110 B3a comparisons (release insert `R_j`, attestation `R_j < C`, PASS with `R_j ≥ C`, row visible, cooling-off end `E`, decision `E ≤ t_dec < C`) and their equality tests | §1.3 (release at `≥ R_0`), §1.5 (effectiveness `< C`; guard `cooling_off_start + 259,200 ≤ t_dec ≤ C`), TC-7. B3a's anchor and cap rows (rev 3 l.208-209) stand. |
| rev 3 l.306 and rev 4 l.175 B4.3 release entry `{…, visible_from, …, attestation}` | `{evaluation_id, result, commitment, released_at}`; the attestation is a sealed file plus its ATTESTATION delivery entry |
| rev 3 l.310 barred-descendant `visible_from` = ancestor's release `visible_from` | a barred descendant can be recorded only after the ancestor's release entry exists (`ANCESTOR_UNRELEASED` before that). Its rejection entry is visible from its own insert. |
| rev 6 l.113 "`insert_release`, `state` … `guard_state` each evaluate it on demand" | §1.3 |

## 2. D-12 crosswalk (replaces C1 §2)

| D-12 material | Treatment |
|---|---|
| P-1 PASS-only attestation; Q1 | **Kept.** The attestation binds the frozen schema's fields, including `cooling_off_start` (= RESULT delivery). |
| P-2 signer checks | **Kept**, through `sign_permit` (§1.5). |
| P-3; Q2a; Q3 | **Semantics kept.** `ANCESTOR_UNRELEASED`, the backstop and completion added (§1.6). |
| P-4; Q2b | **Kept;** Q2b covers `ANCESTOR_UNRELEASED`. |
| Q4, Q5 | **Unchanged.** |
| P-5 cooling-off from `R_j`, availability hours | **Replaced:** from the owner account's RESULT delivery, bound in the attestation (§1.5). |
| P-6 cap, revision; Q6(ii) | **Intent kept;** one effectiveness transition; index-ordered revisions; guard (§1.5). |
| P-7 daily release | **Deleted;** release on request at or after `R_0`, and the backstop (§1.3, §1.6). |
| P-8 | **Kept**, applied before ATTESTATION delivery (§1.5). |
| Q6(i) | **Kept;** the owner only triggers (§1.1). |
| Actors, steps 2 and 5, records | Step 2 adds the publisher's `R_0` file. Step 5 adds step 2a and rev 8's qualification. Records: release entry, delivery entries, VOID entry, revision entry (§1.3-§1.5). |
| R1 | **Changed:** a signing fault cannot delay the result or cooling-off, only certification, and so it can cause `U_ops` near C (§1.7). |
| R2 | **Unchanged.** |
| R3 | **Changed:** the clock list in §1.3, the one host clock, and the owner-side read-back. |
| R4 | **Unchanged;** it does not cover omission (§1.6). |
| T-1 | **Replaced:** TC-1, TC-6, and the reader row (§1.1). |
| T-2 | **Replaced:** TC-2. |
| T-3 | **Replaced:** every outcome takes the same release and RESULT-delivery path. PASS-only steps come after delivery (TC-4). |
| T-4 | **Deleted.** No claim is made that an outage affects every outcome alike (D20C1-S-6); outages are in §1.7. |
| T-5 | **Replaced:** TC-2, TC-3, C2-C11. |
| T-6 | **Kept** as TC-7 with C9-C10. |
| T-7 | **Deleted;** cooling-off is from the owner's delivery (TC-3). |
| T-8 | **Replaced:** TC-4. |

## 3. Comparison (replaces C1 §3)

| | Revision 8, if revised again | Option C2 |
|---|---|---|
| Review status | Sol FIX (D20LR8-S-1); no Astra re-check | C1: both FIX with the core proof confirmed; C2 unreviewed |
| One shown result | needs a cross-call clock invariant not yet specified | clock-free once released; deadlines trust the clock |
| Delays and expiry | unbounded; daily slips; cap expiry | unbounded; no daily slips; cap expiry still possible |
| Hints | lock waits during and after a read; signing before release | latency of any request, before and after `R_0`; no signing before the owner knows the result |
| Still to design and test | availability log, T-7 | owner-side delivery channel, `sign_permit`, effectiveness and VOID, backstop, revision entries, capability boundary |
| D-12 re-decision | none for the schedule; Q7 | P-5 and P-7 replaced; others reworded; Q6(i) kept; Q7 |

**Recommendation (AI drafting choice, conditional):** option C2, if its re-check finds §1.3-§1.5 sound. Otherwise, keep blocked.

## 4. Owner questions (replace rev 8's Q1, Q6, Q7; Q2(i), Q2(ii), Q3-Q5 unchanged; each has "Keep blocked")

**QC1. Switch the lockbox to "release on request"?**

*In short:* nothing about a test can be asked until seven days after it started. Then you ask, and the posting job releases the result and puts it into your own records: PASS or FAIL, nothing else. If you don't ask within another seven days, it is released anyway, so no result can stay hidden; your copy waits until you ask. On a PASS, your 72 hours start when your copy arrives, and the signed certificate carries that time.

What it changes:
- **kept:** your separate posting job, PASS/FAIL only, every technical fail counts, the day-255 rule;
- **replaced:** the daily posting timetable, and counting the 72 hours by service uptime;
- **reworded:** the signer's checks.
- **Options:**
  - **"Switch to release on request (Recommended)."**
  - **"Keep the daily timetable (revision 8)."** A revision 9 would be needed.
  - **"Keep blocked."**

**QC2. Adopt the detail rows?** As rev 8's Q1, with:
- the request, delivery, signing and backstop rules of §1.2-§1.6;
- no login for you on the lockbox computer while a test runs (you use one fixed command instead);
- your results are copied to your own machine, and keeping that copy is up to you.

Adopting QC2 does not settle D11-15; the D20L-36 sentence stands.
- **"Adopt (Recommended)."** Cost: several builds, each needing §16 review. A lost key can cost a good PASS.
- **"Keep blocked."**

**QC3. May the service's speed and delays give hints?**

*In short:* the hidden test and the parts that answer you share one computer.
- How long any answer takes, even "not yet", can depend on hidden work, for this test or another. Someone timing it closely might guess that a test is still running or has just finished.
- Nobody has shown that it cannot hint at pass versus fail.
- A busy or broken computer can delay a result, its copy to you or its certificate by any length of time. Near day 255, that can make a PASS expire unpromoted.
- If the service stops for an incident, you see that it stopped.

None of this can change a result. The Constitution says research receives PASS/FAIL only, so allowing these hints needs the written exception in §1.8, which you would sign in C2 after a person reviews it.
- **"Accept the exception (Recommended)."**
- **"Keep blocked."** Stronger separation would be needed, such as separate machines. This draft does not propose it.

**Q7. When does a save count as made in time?** Rev 8's Q7, now for **three saves**:
- starting a test (before day 255);
- finishing a test (before the worker deadline);
- the certificate becoming valid (before day 255 and before any revision).

A save counts at the service's clock check, made while nobody can read. If a crash loses it, it never happened: no test, a technical fail, or a certificate attempt retried, and refused if day 255 has passed by then. The stricter rule "needs additional durable evidence and design work" (D20LR8-S-2). Options as in rev 8.

## 5. Findings, remaining, unauthorised, self-check

**New findings** (D20L-83..89; C1's D20L-76..82 superseded):
- **D20L-83 BLOCKER (repaired; §1.4).** Delivery was not idempotent or proven to reach the owner (D20C1-S-1, A-5). Now RESULT and ATTESTATION deliveries, verify-and-reuse, `L_pub`, and owner-account read-back.
- **D20L-84 BLOCKER (repaired by narrowing; §1.2, §1.7).** `NOT_YET`'s independence was overclaimed (D20C1-S-2, A-1). Now one host clock, a durable `R_0` file with recovery, and disclosure.
- **D20L-85 BLOCKER (repaired; §1.5).** Effectiveness lacked one transition ordered against cap and revision (D20C1-S-3, A-4). Now the ATTESTATION delivery append with VOID, and index-ordered revision entries.
- **D20L-86 BLOCKER (repaired; §1.5, §1.10).** C1 dropped `cooling_off_start` required by Constitution §13 and the frozen schema (D20C1-A-3). Restored, bound to the RESULT delivery.
- **D20L-87 BLOCKER (repaired; §1.6).** Release was not guaranteed if the owner never asked (D20C1-S-4). Now the backstop and the pending list.
- **D20L-88 BLOCKER (repaired by disclosure; §1.7, §1.8, QC3).** The residual was understated (D20C1-S-5, A-2). Unbounded delays, cap expiry, pre-`R_0` latency and the stopped state are now disclosed.
- **D20L-89 NON-BLOCKING (applied; §1.3, §1.9, §1.10, §2).** Proof wording, clock list, tests, inherited clauses, T-4 (D20C1-S-6, A-6, A-7).
- **D20L-82** (wait until no other read is open): **not adopted** (D20C1-S-7, A-8). It is an isolation alternative needing its own design and cap cost.

**Remaining:**
- the R19-2 re-check of C2;
- owner QC1-QC3, Q7, then Q2(i), Q2(ii), Q3-Q5;
- S4 items:
  - the forced-command channel and the owner record location;
  - the one-host-clock binding;
  - the reconciler and view;
  - the governance action that appends revision entries;
  - the no-login procedure;
- the consolidated S4 signing text;
- the C2 rows (§2, the §7 row if QC3 is accepted);
- builds and tests TC-1..TC-7 with rev 8's test file layer, each under §16 review.

**Unauthorised:** frozen edits; activation; acceptance; any code; key generation; simulation; confirmation or lockbox access; promotion; deployment; trading. `KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid outcomes.

**Self-check:**
- one file written in this step;
- all 15 C1 findings answered (D20C1-S-1..7, D20C1-A-1..8);
- new findings D20L-83..89, no gaps;
- frozen `cooling_off_start` restored; no frozen file edited;
- added: `L_pub`, the `R_0` file, `record_delivery` with two kinds, `sign_permit`, the VOID and revision entries, the backstop, the pending list, the six codes;
- deleted relative to C1: the claims "no store contact means independent", "never delayed by days", "none expires", "small hints", and the attestation without `cooling_off_start`.
