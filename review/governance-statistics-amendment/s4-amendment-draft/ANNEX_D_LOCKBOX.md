# Annex D: the lockbox (D-11, D-12, D-20, R-14a), consolidated

**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-31. This is AI drafting and not an authority.

**Status: DRAFT rev 2, UNREVIEWED.** Rev 1 (`c5cb1ff`) was reviewed in `SOL_FIDELITY_REVIEW_C5CB1FF.md` and `ASTRA_FIDELITY_REVIEW_C5CB1FF.md` (both FIX). Rev 2 repairs every finding and applies the owner choices in `OWNER_DECISION_S4_FOLDIN.md`; the dispositions are in `FIDELITY_DISPOSITIONS_C5CB1FF.md`. Nothing here binds until the owner signs the C2 §4 amendment after the required human review. This annex invents no rule. Each row restates a decided rule, cites its source, and marks any wording the AI chose as `[AI wording]`. Where the sources disagree, the later owner decision governs and the difference is noted.

**Sources and precedence.** A later item governs an earlier one where they differ:

| Order | Source | What it decides |
|---|---|---|
| 1 | `d11-proposal/OWNER_DECISION_D11.md` on `PROPOSAL_REV2.md` §2-3 with `PROPOSAL_REV3.md` §2, §4, §7 | the prediction distribution and the pass rule L-1..L-4; the read and execution contract; the historical window |
| 2 | `d12-proposal/OWNER_DECISION_D12.md` on `PROPOSAL_REV7.md` §3 (P-1..P-8) | attestation fields; technical FAIL; cooling-off; cap; publisher |
| 3 | `d20-lockbox-proposal/OWNER_DECISION_D20_LOCKBOX.md` on `PROPOSAL_REV3.md`..`PROPOSAL_REV8.md` (read side) and `OPTION_C_PROPOSAL_REV2.md`..`_REV5.md` | the bindings, release on request, Q2-Q5, Q7, QC1-QC3 |
| 4 | `r14-exception/OWNER_DECISION_R14A.md` on `PROPOSAL_REV2.md` + `_REV3.md` | where the lockbox and confirmation code live |

---

## §D-1 The prediction distribution and the pass rule (D-11, Route A)

### D-1.1 Window and length

- `L0 = 2025-06-01T00:00Z`, `L1 = 2026-09-01T00:00Z`. (D-11 rev 2 §2)
- `m = 457` scheduled complete UTC days. This reads l.85's "decision-count" as one decision per day (l.209). It is fixed before any read. (rev 2 §2; decided, D-11 "Recorded meaning")
- **The window is a historical held-back check, not a fresh test.** Its prices are public, so it cannot detect strategies shaped by them. Fresh evidence comes only from later paper trading under its own rules, fixed in advance. (D-11 Q3) The Constitution §0 reading that this needs is a row of DRAFT §1.

### D-1.2 The source and the statistic

- **Source.** The nominee's BTC baseline 1x run over `[w0, w1)`:
  - both legs' daily returns come from `screen.daily_returns` through the adapter of §D-3.3. D-20 A6 replaced D-11 rev 2's `daily_net_returns`/`paired_daily_returns` wording (D-20 rev 2 l.363-364);
  - `d_t = c_t − b_t`;
  - `n = (w1 − w0) / 1 day`.

  (rev 2 §2) The run itself, including its start state and final hour, is §D-3 (D-20 A6; Q2).
- **Statistic.** `T = difference_series_sharpe.scaled = √365 · mean(d) / sd(d)`, with the `n − 1` divisor (E-DIFF). (rev 2 §2; D-11 Q1, Route A)

### D-1.3 Block length

`b = block_length(ψ)`, where ψ is the Sharpe influence process of `d`:

`ψ_t = u_t − (S/2)(u_t² − 1)`

Here `u` is `d` standardised with the population scale, and `S` is the sample daily Sharpe of `d`. This follows the Task 12 convention, applied to one series. (rev 2 §3)

**Disclosed limit:** PPW chooses `b` for the long-run variance of a mean. It does not establish coverage for a selected nominee's predictive quantile at horizon `m ≠ n` (`UNVERIFIED_EXTERNAL_ASSUMPTION`). (rev 2 §3)

### D-1.4 Resampling and the quantile

- **Stationary bootstrap, 2,000 attempts.** Each attempt draws `m = 457` indices over `0..n−1`: restart with probability `1/b`, otherwise step forward modulo `n`. The attempt's path is `d` at those indices, and `T*_r` is the statistic of that path. (rev 2 §2; D-11 "Recorded meaning")

  The generator and its stream are §D-3 (D-20 A4).
- **Quantile.** `q = type_seven_quantile(T*_0 .. T*_1999, 0.05)`. (rev 2 §2)
- **Numerics.** The float64 output of the reference code decides L-1 and L-2, including sign residues. (rev 3 §2; adopted by D-11, "Recorded meaning")

### D-1.5 The pass rule

| Gate | PASS iff | Source |
|---|---|---|
| L-1 | `T_L ≥ q` | rev 2 §2 |
| L-2 | `T_L > 0` (the same statistic as L-1) | rev 2 §2 |
| L-3 | `max_drawdown(cand) − max_drawdown(bench) ≤ 0.05` on the BTC lockbox runs over `[L0, L1)`, hourly segments | rev 2 §2 |
| L-4 | Annex C C-3 holds on the ETH lockbox 1x run: E-IMPROV > 0 and DD(ETH) | rev 2 §2 |

`T_L` is E-DIFF of the BTC lockbox legs' daily `d` over `[L0, L1)`.

### D-1.6 Availability (fail-closed; UNAVAILABLE never passes)

From rev 2 §2:

1. **Source days.** The timestamps are exactly `w0 + k` days for `k = 0..n−1`. Candidate and benchmark identities, asset and cost string match, and `n ≥ 16`.
2. **Source E-DIFF.** `difference_series_sharpe.reason` is None. The test is this field, not the aggregate `.reason`.
3. **Block length.** `1 ≤ b ≤ n`.
4. **Attempts.** All 2,000 attempts are run in order, and every `T*_r` is available and finite. Nothing is omitted, replaced or extended. `q` is finite.
5. **Lockbox days.** The timestamps are exactly `L0 + k` days for `k = 0..456`: 457 days and 10,968 hourly segments for both legs. A shorter path is UNAVAILABLE. `T_L` comes from the `d`-field and is available.
6. **L-3.** Both BTC legs' `max_drawdown` values are finite.
7. **L-4.** The ETH timestamps pass the same checks, and both leg Sharpes are available (`paired_sharpe_improvement` not None, aggregate reason None).

A gate that is UNAVAILABLE fails. How that failure is labelled is §D-2 (D-12 P-3).

### D-1.7 Reads, budget and sealing

- **One read per family.** Each family's read:
  - consumes that family's lockbox budget;
  - is logged;
  - has its own evaluation ID;
  - leaves the segment EXPOSED.

  Release to confirmation happens only between cycles (§7 l.81-83). The two reads are at least 30 days apart (DRAFT l.243). (rev 3 §7)
- **Sealing before the first read.** Each declared family's terminal pre-lockbox status is sealed and recorded as exactly one of these (rev 3 §7; D-11 "Recorded meaning"):
  - (a) a fixed nominee that is ELIGIBLE, with a valid sealed prediction artifact;
  - (b) no nominee (`UNAVAILABLE`, Annex A P18-3);
  - (c) a nominee that is not ELIGIBLE;
  - (d) a nominee whose gates or prediction artifact are `UNAVAILABLE`.

  Where both (c) and (d) apply, (d) governs. Only (a) requests a read, and one family's status never blocks the other.

### D-1.8 Access and execution (needs the DRAFT §1 rows for Constitution §7a and the threat model)

`lockbox_eval` may read BTC and ETH 1h bars over `[S_pre, L1)`, with `S_pre = 2022-11-13T00:00Z`. The history part runs up to L0, so 31 May 2025 is included (owner choice 2, `OWNER_DECISION_S4_FOLDIN.md`). It reads them read-only, under the cycle's data-manifest hash, and runs the registered strategy itself. (D-11 Q2; rev 3 §4 item 4)

1. **Inputs handed over: identifiers only.** These are the cycle-record hash, the declaration hash, `trial_id`, the hypothesis hash, the configuration hash, and the sealed prediction artifact. No confirmation per-bar output and no fitted model crosses identities. (rev 3 §4 item 1) The artifact's fields are §D-3 (D-20 A7).
2. **Immutable lookup and verification before any lockbox byte is read.** This covers the hypothesis record, the trial code and configuration, the nominee's model seed, the engine and backtester code at the bound commit, and the data-manifest hash. Every hash must match.
   - On a mismatch, no lockbox data is read, the segment is not EXPOSED, and the result is a technical failure with no retry in C2.

   (rev 3 §4 items 2-3) The artifact identity and retrieval path are §D-3 (D-20 A2/A3, D11R3-S-1).
3. **Warm-up.** EMA, EWMA and benchmark-volatility state start at `S_pre`, with the feature factory's own convention. (rev 3 §4 item 4)
4. **Fits.** `lockbox_eval` refits the nominee itself, with the nominee's estimator seed (§D-3; D-20 Q5):
   - at `r_k = L0 + 30k` days, `k = 0..15`;
   - each trained on `[r_k − 24 months, r_k)`, with labels purged at `r_k`.

   No confirmation-fitted model is used, and rule-based nominees skip fitting. (rev 3 §4 item 5)
5. **Start state: both legs flat at L0, for BTC and ETH.** Exposure 0, no pending order, an unset clock, a fresh overlay, equity 1.0, and MDD measured from L0. **Each leg pays its entry cost at its first permitted entry.** (D-11 Q2; D-20 Q2(i), D20L-42) This corrects rev 3 §4 item 6's "both legs pay their entry cost at L0", which D20L-42 found inherited and wrong.
6. **Computation.** The worker reads and computes twice. Matching twice checks determinism only (D-12 rev 7 l.82), and it is separate from the later R-a replay (§D-2.10). It captures all input hashes, the code commit, the image, seeds and streams.
7. **Outputs.** Research receives PASS/FAIL only (§7 l.79). The attestation and the human approver are covered in §D-2. Every other output stays under the `lockbox_eval` identity. (rev 3 §4 item 7, as decided by D-12)

### D-1.9 Not decided here

D11-15 is decided by owner choice 1 (`OWNER_DECISION_S4_FOLDIN.md`): processing ends at the earlier of day 255 and 75 days after the look (§D-2.7). The §16 review of `lockbox_eval` is still required.

---

## §D-2 Results, release, certification and promotion (D-12 as changed by D-20 option C)

**Sources:**
- D-12 P-1..P-8 (`d12-proposal/PROPOSAL_REV7.md` §3) and owner answers Q1-Q6;
- D-20 QC1 (release on request), QC2 (the detail rules), QC3 (the §7 exception) and Q7 (when a save counts);
- the option C text: `OPTION_C_PROPOSAL_REV2.md` §1 as amended by `_REV3.md`, `_REV4.md` and `_REV5.md`.

QC1 **replaces** D-12's P-5 "cooling-off from `R_j`, counted in hours of reader-path availability" and P-7's daily release times `R_j`. It **keeps** the separate publisher, PASS/FAIL only, every technical FAIL counting, and the day-255 rule. (D-20 decision item 1)

### D-2.1 Fields and the PASS-only attestation (D-12 P-1, P-2; Q1, Q5)

- `T_L` is the float64 L-2 statistic (§D-1.5). The attestation's fields:
  - `paired_delta_sharpe_sign` is `positive` iff `T_L > 0.0`, `zero` iff `T_L == 0.0` (including −0.0), and `negative` iff `T_L < 0.0`;
  - `prediction_decay_test_passed` is L-1;
  - `drawdown_constraint_held` is L-3.

  L-4 has no field. On a PASS the three fields always read (`positive`, `true`, `true`). (D-12 rev 7 §3 "Fields")
- **P-1.** An attestation exists only for a PASS. No attestation or field record is made for any other outcome.
- **P-2.** The fields come only from a finite, available `T_L` and L-1..L-3. Before marking a read PASS, the worker checks all of L-1..L-4 and the field values. A mismatch the worker finds before its deadline `D*` is a technical FAIL. The signer checks them again against the sealed record. A mismatch there is a signing fault (§D-2.6), never a FAIL.
- **Q5.** No sealed detail is shown. Research receives PASS/FAIL only, subject to the Constitution §7 row (§D-2.9).

### D-2.2 Technical FAIL, lineage and the upside record (D-12 P-3, P-4; Q2a, Q2b, Q3)

- **P-3.** Every outcome released as FAIL is a `LOCKBOX_FAIL` for Constitution §7 l.85 and protocol l.296, including a technical FAIL. A pre-read rejection is not a read and is not a `LOCKBOX_FAIL`. Lineage is fixed at sealing. A barred nominee gets `BARRED_DESCENDANT` and no read. (D-12 Q3)
- **Lineage order (option C).** `begin_read` refuses a descendant while any ancestor's read has no release entry, with reason `ANCESTOR_UNRELEASED`. This is fixed before any lockbox byte is read, and the bytes are identical whatever the ancestor's hidden result. A released FAIL ancestor bars the descendant, recorded at that time, and the rejection entry is visible from its own insert. (C2 §1.6, §1.10; C3 §1.6) This can block a descendant indefinitely if release is blocked.
- **Q2a.** The cycle outcome may show that a family had no result because its lockbox read failed technically (§D-2.9, row (a)).
- **Q2b.** A pre-read rejection shows its reason code.
- **P-4 (sealed only).** The sealed prediction artifact also stores the 2,000 sorted replicates. The pre-read check confirms 2,000 finite ascending values, and that D-11's type-7 function returns the sealed `q` at `p = 1/20`. The sealed bundle holds `upside = {status: COMPUTED | NOT_COMPUTED, k, exceeds_p95, reason}`. It is not a gate and is never shown to research. (D-20 rev 2 B2)
  - It is computed only for a finite `T_L`. `k` is the number of replicates strictly below `T_L`, so ties are not counted. `exceeds_p95 = T_L > type_seven_quantile(values, 0.95)`. The object is then `{status: COMPUTED, k: int, exceeds_p95: bool, reason: null}` (rev 3 l.272).
  - Otherwise it is `{status: NOT_COMPUTED, k: null, exceeds_p95: null, reason: "T_L_UNAVAILABLE"}`.
  - The sign field uses the same float64 `T_L`. A null `T_L` is a technical FAIL.
  - P-3 lineage is fixed at sealing, through the transitive `parent_id` chain of the hypothesis records.

### D-2.3 Identities (D-12 Q6(i); option C C2 §1.1, C3 §1.1, C4 item 2)

| Identity | May do | Never |
|---|---|---|
| **owner** | Run the one fixed command `request_release <evaluation_id>` as a forced command over the channel S4 fixes, not a login shell. Read his own record directory on a machine other than the lockbox machine. | An interactive login, shell or debugger on the lockbox machine while any read is open; the sealed directory; logs or stderr of any lockbox process; reconciliation views |
| **publisher** (a separate OS identity; THREAT_MODEL l.9 changed, §D-2.9) | `begin_read`; `release`; `record_delivery`; `sign_permit` requests for the signer; the backstop; its own lock `L_pub` and `R_0` file. It receives `R_0` and the pre-read identity fields (for P-8), release and delivery entries, and the attestation. | Commitment preimages, nonces, sealed bundles, cause classes, finished-record presence or time before release, lockbox bars |
| **signer** (`lockbox_eval`'s key) | Sign one attestation per evaluation, only on a store `sign_permit`, never on the publisher's word | any other index row |
| **worker** (`lockbox_eval`) | the read side (§D-3) | index writes |
| **reader** | the projection in §D-2.8 | everything else |
| **reconciler** | §26 reconciliation, through a view S4 fixes | **S4 gate:** S4 names this person and a view that cannot show the owner a sealed result or an undelivered release. If no such person or view exists, that is a Constitution question for the owner before the access design is adopted. |

Publisher and store run on one host and read one system clock (an S4 binding; C2 §1.2).

### D-2.4 Release on request (QC1; C2 §1.2-§1.3; C3 §1.6)

**Times.** For a read admitted at store time `t_s`:
- `R_0 = t_s + 604,800` s (7 days), the earliest release time;
- the worker deadline is `D* = min(R_0 − 43,200, C)`, where C is the cap of §D-2.7.

The read side (§D-3) enforces `D*`. (D-20 rev 5; D-12 step 2)

**The request**, run by the publisher one at a time per evaluation under `L_pub(evaluation_id)`:
1. **`NOT_YET`** if the host clock is before `R_0`.
   - `R_0` comes from the publisher's own durably written `R_0` file. If that file is lost, `R_0` is recovered through `begin_read`'s idempotent lookup, which takes `L_store`.
   - Claimed: an ordinary `NOT_YET` takes no `L_store`. Not claimed: that its latency is independent of sealed work.
2. **`release(evaluation_id)`**, under `L_store`, after the lookups and fsyncs (§D-3):
   - before `R_0` it refuses (logged; answered `STOPPED`);
   - if a release entry exists, it returns it;
   - otherwise the result is the finished record's `{result, commitment}` if one exists and its RESULT bundle verifies. A bundle that does not verify is a §26 stop (`STOPPED`), never a silent FAIL. With no finished record, the result is the DEFAULT's FAIL;
   - it appends `{evaluation_id, result, commitment, released_at}` and fsyncs it before unlocking. `released_at` is the clock reading under the lock.
3. **RESULT delivery** (§D-2.5).
4. **On a PASS:** signing and ATTESTATION delivery (§D-2.6), unless the attestation is already effective or VOID.
5. **Return one response code** (§D-2.8).

**The first durable release fixes the result.** A finish after a release entry exists is refused (`mark_finished` step 2a, §D-3). Every shown result equals the first durable release entry's. No clock assumption is needed for this. It relies on durable-before-use, fail-closed recovery, and platform assumptions that stay `UNVERIFIED_EXTERNAL_ASSUMPTION`. (C2 §1.3 proof)

**Backstop.** The publisher attempts `release` for every counted read without a release entry, and outbox creation for every released read without a RESULT delivery entry. It runs at `R_0 + 604,800` for each read, and at every revision, invalidation and calendar termination for all reads.
- A read whose `R_0` is still ahead waits for its `R_0`.
- Failed attempts are retried daily until no read is pending.
- An outage, a stalled `L_store` holder or an unresolved §26 stop can block release indefinitely. **No completion date is guaranteed.** (C3 §1.6)

**Pending list.** At each backstop run and at termination, the owner receives the evaluation IDs without a release, and those released without a RESULT delivery, as public accounting only.

**Cycle report.**
- It is visible from the cycle's termination, whatever its cause, and shows every counted read's released result as it arrives.
- It is marked incomplete, listing `PENDING_RELEASE`, while any counted read has no release entry. A report that never completes is a §26 incident.
- Incompleteness never postpones termination, invalidation or cap effects. (C3 §1.6)

### D-2.5 Delivery to the owner's own record (C2 §1.4; C3 §1.5c; C4 item 2)

There are two delivery kinds per evaluation, each with a deterministic file name `<evaluation_id>.<kind>.json` and deterministic bytes:
- **RESULT** `{evaluation_id, result, released_at}`;
- **ATTESTATION**, the attestation bytes.

Under `L_pub(evaluation_id)`:
1. **Outbox.** The publisher creates the outbox file (write temp, fsync, link without replacing, fsync the directory), or verifies an existing one byte for byte. A mismatch is a §26 stop. Only the owner's command account can read it.
2. **Owner's side.** Running as the owner's account, the forced command copies the file durably into the owner's record directory, reads the copy back, and returns its SHA-256.
3. **`record_delivery(evaluation_id, kind, hash)`**, under `L_store`:
   - if an entry of this kind exists, it returns it;
   - a wrong hash is refused (`STOPPED`, logged);
   - otherwise it appends `{evaluation_id, kind, file_hash, delivered_at}`, with `delivered_at` read under the lock after the owner's read-back.

   For ATTESTATION, the first step is §D-2.6's "already final" test, and the append is the effectiveness check.

**Order, not elapsed time.** `delivered_at` is never earlier, in operation order, than the owner's durable copy. That the timestamp and the 72 hours are accurate in real time rests on R3: an accurate host clock, with no backward step and no forward jump.

The owner keeps his copy, and its backups are his responsibility.

### D-2.6 Cooling-off, signing and effectiveness (C2 §1.5; C3 §1.5a-b; C4 item 1)

- **Cooling-off start** is the PASS's RESULT delivery `delivered_at`. The attestation binds it as `cooling_off_start` (Constitution §13 l.124; `schemas/attestation.schema.json`).
- **`sign_permit(evaluation_id)`**, under `L_store`, in this order:
  1. If an ATTESTATION delivery entry or a VOID entry exists, return the existing state and write nothing.
  2. Otherwise, if the release is PASS and the RESULT delivery exists, but the clock is at or after C or a revision or invalidation entry follows the pre-read entry, append `{evaluation_id, kind: VOID, reason: CAP | REVISION}` and refuse.
  3. Otherwise, PERMIT only if the release says PASS, a RESULT delivery exists, no revision or invalidation entry follows the pre-read entry, and the clock is before C. The permit carries the message fields and the sealed record reference.
- **The signer** verifies the sealed record against the release entry's commitment, checks P-2, and signs deterministically. The signature scheme has no embedded time. The signer creates the sealed attestation file without replacing it; an existing file must equal the new bytes.
- **The publisher validates the attestation (P-8):** its signature; identity fields equal to the pre-read entry; the three fields; and `cooling_off_start` equal to the RESULT `delivered_at`. It then delivers it as ATTESTATION.
- **Effectiveness: the one authoritative transition.** In `record_delivery(ATTESTATION)`:
  - after the "already final" test, if the clock reading `t_e` under `L_store` is before C and no revision or invalidation entry precedes it in the index, the ATTESTATION entry is appended and the certificate is effective;
  - otherwise a VOID is appended and the certificate is never effective. The store refuses a second VOID.
- **When a certificate counts (Q7, the draft rule the owner accepted).** It counts at `t_e` if `t_e < C`, even if its entry becomes durable after C. `PASS_CERTIFIED` is returned only after the fsync. If a crash loses the entry, there is no certificate, and the retry, now after C, writes VOID (CAP). P-6's "attested by day 255" means an ATTESTATION entry with `t_e < C`.
- **Index order decides against a revision.** An ATTESTATION entry before a revision entry stays effective. An effective certificate and a VOID are both final.
- **The signing cutoff is advisory.** A refusal, timeout or P-8 mismatch writes nothing. The code stays `PASS_CERTIFICATE_PENDING` and the next request retries, reusing an existing attestation file. A PASS never becomes a FAIL.
- **Revisions and invalidations** are index entries `{kind: REVISION | INVALIDATION, at}`, appended under `L_store` by the governance action S4 names.

### D-2.7 The cap, revisions and the promotion guard (D-12 P-6; Q6(ii); C2 §1.5)

- **The cap C** (D-20 rev 3 B3a l.208-209, kept by C2 l.312; D11-15 decided by owner choice 1):
  - the anchor is `A = T`, the archive timestamp of the declaration post;
  - `C = min(A + 255 × 86,400 s, look + 75 × 86,400 s)`, computed once and held in the store's configuration. The signer and the store use that one value, compared in integer store-clock seconds;
  - **"day 255" in P-6 below means C.**
- **D-12 P-6 l.244, as decided:** "At day 255 processing ends. A nominee whose lockbox result is not yet visible, or whose visible PASS attestation still awaits an owner decision, expires unpromoted, recorded with cause U_ops (Annex A P18-7). An outcome completed earlier is kept: a visible FAIL stays a FAIL, a pre-read rejection stays a rejection, a barred descendant stays barred. A nominee is promoted only if it is attested and the owner's decision is recorded after its full cooling-off and by day 255."
  - Under option C, "attested" means an effective certificate (§D-2.6). A result is "visible" as the release row of §D-2.8 makes it visible: after its RESULT delivery, or from its cycle's termination. `[AI wording]`
- **D-12 P-6 l.245, as decided:** "A revision or invalidation fixes every nominee's status at the moment it happens. It ends processing of every nominee not attested at that moment. An attested nominee is unaffected: 'open promotion' in Constitution §4 l.48 means attested in this sense. An entry already committed but not yet visible then still shows its result, but its attestation is void. No signature that is not effective at that moment can become effective later."
- **Promotion guard.** An owner decision at `t_dec` is accepted only if:
  - the attestation is effective;
  - `cooling_off_start + 259,200 ≤ t_dec`;
  - `t_dec ≤ C`.

  Otherwise a PASS that cannot meet these by C is `U_ops`. A PASS released or delivered after C shows PASS, has a VOID or no attestation, and is `U_ops`. A FAIL is never `U_ops`.
- **Admission at the cap.** A read whose admission check is at or after C gets `CAP_REACHED`, and nothing is written. A read cut off by `D* = C` is a technical FAIL (DEADLINE) and expires `U_ops`. (rev 5 D20L-52) Letting authorised work continue after C would need its own §4 exception, and none is made.

### D-2.8 What the owner and research see (C3 §1.1; C4 item 2; QC3)

**Response codes**, each with fixed bytes. `STOPPED` comes first; the others follow in table order.

| Code | When |
|---|---|
| `STOPPED` | An undifferentiated refusal whose cause is withheld: an active §26 stop, a request that failed for any reason, or an ID with no pre-read entry. Causes go to logs the owner cannot read. |
| `NOT_YET` | The host clock is before `R_0`. |
| `FAIL` | Released FAIL, RESULT delivered. The bytes are identical for every kind of FAIL. |
| `PASS_CERTIFICATE_PENDING` | Released PASS, RESULT delivered, attestation neither effective nor VOID. |
| `PASS_CERTIFIED` | An ATTESTATION delivery entry exists. |
| `PASS_NOT_CERTIFIABLE` | A VOID entry exists (CAP or REVISION). |

An ID of a terminated cycle is served normally.

**Reader projection.** The reader sees only these fields:

| Record | Fields | Visible |
|---|---|---|
| pre-read entry | evaluation ID, family, nominee ID, prediction-artifact hash, eligibility ID, lockbox ID, `R_0`, EXPOSED | always |
| rejection entry (`PRE_READ_REJECTION`, `BARRED_DESCENDANT`) | family, nominee ID, kind, reason code (Q2b, including `ANCESTOR_UNRELEASED`), ancestor evaluation ID | always |
| release entry | evaluation ID, result, `released_at` | after its RESULT delivery entry, or from its cycle's termination, whatever the cause |
| delivery entry | evaluation ID, kind, `delivered_at` | always |
| VOID entry | evaluation ID, reason (CAP or REVISION) | always |
| revision or invalidation entry | kind, `at` | always |
| cycle report | per counted read, the result if visible, else `PENDING_RELEASE`; complete or incomplete | from the cycle's termination |
| pending list | the evaluation IDs it lists | always |

Withheld from the reader: the commitment, record and file hashes, nonces, and every other field of any record.

### D-2.9 Rows this section needs in DRAFT §1 (Constitution and threat model)

- **Constitution §7 l.79** (D-12 Q2a with D-20 QC3, accepted). The proposed text is `d20-lockbox-proposal/OPTION_C_PROPOSAL_REV4.md` item 4; its field list for (c) is §D-2.8's projection.
- **THREAT_MODEL l.9** (D-12 Q6(i)): the publisher identity is added, and `lockbox_eval` keeps "lockbox read + attestation signing only".
- **Constitution §7a and the threat-model permission** for `lockbox_eval`'s history read (D-11 Q2; §D-1.8).
- **Constitution §0**, the reading of "future data" (D-11 Q3; §D-1.1).

### D-2.10 Reproduction and disclosed residuals (D-12 Q4, R2-R4; option C R5c)

- **Q4, route R-a.** Everything is captured. The read is re-run after the segment rolls into confirmation (§7 l.81), and a mismatch voids the promotion (§27 l.194). There is no second counted read.
- **Accepted as disclosed, not removed:**
  - R2, a faulty signer;
  - R3, the trusted store and host clock;
  - R4, the owner's judgment across families;
  - **R5c**, timing (C2 §1.7; C3 §1.7). Any response's latency, before or after `R_0`, and a `STOPPED` answer can reveal that sealed work is running or finishing, for this read or another. Whether PASS and performance FAIL take different time is not known.

  Delays of any length can hold up release, delivery or certification, and near day 255 can make a PASS expire `U_ops`. Before release, a delay can make a finish miss `D*`, which is a technical FAIL, or an admission miss C (`CAP_REACHED`). Nothing can change a result **after it is released**, or a counted try.
- **R1, changed (C2 l.332).** The daily missed-release mechanism is gone. A signer refusal, outage or fault, or a P-8 mismatch, still affects only a PASS: it leaves the code at `PASS_CERTIFICATE_PENDING` (§D-2.6). Near the cap that can make the PASS expire `U_ops`. So a pending certificate, a delay or such an expiry can hint that the read was a PASS. It can never produce a FAIL.

---

## §D-3 Bindings: seeds, the prediction artifact, the store and the read (D-20)

**Sources:**
- `d20-lockbox-proposal/PROPOSAL_REV2.md` §1.1 (A1a-A7), B1 and §1.3, as changed by `PROPOSAL_REV3.md` (A1b, A5, A6, A7, B1, B4.2-B4.4), `PROPOSAL_REV4.md` (A1b, A6, B4.1, B4.2) and `PROPOSAL_REV5.md` (the worker deadline);
- the store of `PROPOSAL_REV8.md` §1.2, as changed by option C (`OPTION_C_PROPOSAL_REV2.md` §1.3, §1.9, §1.10; `_REV3.md` §1.9, §1.10a; `_REV4.md` item 6; `_REV5.md`);
- the owner's D-20 answers Q2(i), Q2(ii), Q3, Q4, Q5 and QC2, and R-14a.

QC2 adopted these detail rules. Items marked `[DETAIL]` or `[NEW DEFAULT]` in the sources are decided by QC2.

### D-3.1 Where the code lives (R-14a; D-20 Q4)

- **R-14a** (`r14-exception/PROPOSAL_REV2.md` §1, with `PROPOSAL_REV3.md` items 1-2) is a row of DRAFT §2.0.
- The C2 lockbox code lives in one reviewed **lockbox module**, and the confirmation-side code in one reviewed **confirmation module**. Their SHA-256 rows are in the signed C2 protocol bytes.
- The model fit and the final-hour rule live in the frozen `screen.py` (`walk_forward` with `model_seed`; `estimator_seed`; `confirmation_path`). The three pre-freeze conditions of the D-20 decision (`OWNER_DECISION_D20_LOCKBOX.md` l.25) apply:
  1. the Q2(ii) and Q5 pieces are in the same reviewed change: PR #81, merged as `f715dfe`, review records in `review/pre-freeze-screen/`;
  2. the freeze is built from a commit that contains it;
  3. if the freeze came first, C2 would stay blocked until a formal amendment.
- **Contract allocation** (R-14a rev 3 item 2):
  - the confirmation module performs A7's confirmation-side work on the experiment-engine path: the source re-run, the forecast (A4) and the sealing of the artifact;
  - the lockbox module performs only the `lockbox_eval` side.
- **`code` in the A7 artifact** is `{lockbox_module_sha256, confirmation_module_sha256, engine_commit, screen_object_sha256}` (owner choice 4, `OWNER_DECISION_S4_FOLDIN.md`). Each module hash is that module's signed SHA-256, and each module's contract names the A7 fields it produces.
- **R-14a's accepted residuals** (`r14-exception/PROPOSAL_REV2.md` §2; `PROPOSAL_REV3.md` item 3), disclosed with the row:
  - the two modules are written after the `AQTQ1` post, whose earlier public anchor does not cover them. Their later anchor is the accepted C2 declaration post's chain, verified before every evaluation;
  - some statistical implementation is not frozen at `AQTQ1` (for example A4's bootstrap), and reusing qualified primitives does not qualify the way they are put together;
  - code written after the post can reflect public prices, and it can change until C2 is signed;
  - an error in alignment, error mapping or aggregation can change a decision while every frozen function is called correctly. §16 review and the contract tests are controls, not guarantees;
  - the later anchor fixes the modules' bytes. It does not prove that no protected-data access happened earlier; the read gates and access records remain the controls for that.

### D-3.1a Shared encodings (D-20 rev 2 §1)

- `cj` is `calibration/seeds.py` l.11-19, matching `HASH_CANONICALIZATION_v1.md` l.4-9.
- Times are `YYYY-MM-DDTHH:MM:SSZ` strings in whole UTC seconds. Every comparison is on integer seconds.
- `hexf(x)` is `struct.pack(">d", x).hex()`, 16 lowercase hex digits; `unhexf` reverses it.
- Unavailable values are JSON `null`, with a reason. NaN is never written, because `cj` refuses it.
- Order between floats is always numeric, on decoded values, never lexicographic on the hex strings.
- `evaluation_id = "<cycle_id>/<family>/1"`.
- The commitment nonce has 256 bits and never leaves the store (D-12 rev 7 l.81).

### D-3.2 Seeds (A1b; D-20 Q3, Q5; R-13)

- **The nominee's own fit (Q5, policy `L266_MOD_2_31`):**
  - `seed_l266 = preregistration.trial_seed(protocol_hash, hypothesis_hash, trial_index)`, the l.266 seed that R-13 keeps for the nominee's own fit. `protocol_hash` is the C2 protocol hash, and `trial_index` is the one in the nominee's C2 trial record;
  - `estimator_seed = int(seed_l266, 16) % 2**31`, which is `screen.estimator_seed`. A value of 0 is legitimate.

  It is passed as `random_state` where a constructor accepts it, as `seed` to LightGBM, and to no other estimator (Annex C C-12 (5)). The confirmation fit, the A7 sealing re-run and the lockbox refit all use it. The signed C2 records `estimator_seed_policy = L266_MOD_2_31`. A fit counts as C2 evidence only if its record names that policy and the seed derived under it; the check is on the policy and the derivation, never on the value 0. (rev 2 A1b; rev 4 A1b, D20L-44)
- **Annex C C-12 (5) wording:** "The nominee's own fit uses the estimator seed of the signed estimator-seed policy (D-20 A1b). Null-draw seeds come from their own stream and are never derived from it; an equal value arising by chance is not reuse." (rev 4)
- **The lockbox prediction stream (Q3, `R13_TRIAL_SEED`):**
  - `seed_hex = SHA256(cj({"family_seed": family_seed_f, "trial_id": <nominee trial_id>}))`, the R-13 trial seed;
  - `purpose = "lockbox_prediction"`, `asset = "BTCUSDT"`, `cost = "1.0"`;
  - `evaluation_window_id` is the canonical `["<w0>","<w1>"]`;
  - `m = 457`, `r = 0..1999`.

  It needs a row adding this stream to R-13, and `lockbox_prediction` to `added_purposes`. (rev 2 A3, §1.3)
- **What Q3's seed does and does not do** (rev 2 §1.3):
  - it prevents choosing the realised bootstrap seed through cosmetic edits before the declaration post;
  - it does not stop a search over the strategy or the model seed;
  - it does not stop outcome-dependent invalidation and re-declaration;
  - it does not hide `q` after the post;
  - no bound shows that bootstrap noise near the boundary is negligible.

### D-3.3 The source run (A2, A6; D-20 Q2(i), Q2(ii))

- **Start state (Q2(i)).** Both legs are flat at `w0` for the confirmation source, and at L0 for the lockbox: exposure 0, no pending order, an unset clock, a fresh overlay, equity 1.0. Each leg pays its entry cost at its first permitted entry, and MDD is measured from the start. (rev 2 A2; D20L-42)
- **Final hour (Q2(ii)).** The price at a window's end instant is the close of the window's last bar: `screen.confirmation_path` appends one derived terminal row whose open equals that close. This governs every C2 confirmation run and the lockbox run alike, so no run reads the bar at its window's end. (rev 3 A6; D20L-34, D20L-48) The DRAFT C-0/C-6 wording is a row of DRAFT §2.0.
- **Adapter** (rev 3 A6; rev 4 A6). It takes `(series, result)` pairs and, for each leg, checks:
  - the asset;
  - the same series and `start` for both legs;
  - `series.bars[result.start].open_time` equal to L0 or `w0`;
  - `series.interval == 1 h`;
  - `len(result.equity) == 24 · m_days`;
  - every equity value finite and > 0.

  A failure gives `DAYS_INCOMPLETE` or `NONFINITE_EQUITY`. An equity `EventContractError` becomes `RUN:NONFINITE_EQUITY`; any other runner error becomes `RUN:RUN_FAILED`. A failed BTC run makes L-1..L-3 null, and a failed ETH run makes L-4 null.
- **Metrics** (rev 2 A6):
  - daily returns are `screen.daily_returns`;
  - MDD is `descriptive._max_drawdown((1.0, *equity))`;
  - `screen.leg_stats` is not used;
  - BTC L-1/L-2 availability is `difference_series_sharpe.reason is None`;
  - ETH L-4 availability is `paired_sharpe_improvement is not None` and the aggregate reason None.
- **R-8 extension** (rev 2 A6; R-14a item 8). R-8's binding extends, for L-1..L-4, to:
  - in `statistics.py`: `sharpe`, `paired_sharpe_statistics`, `_influence`, `block_length`, `_uniform_index`, `SEED_DOMAIN`, `CONVENTION_DOCUMENT_SHA256` and `type_seven_quantile`;
  - `_max_drawdown` in `descriptive.py`;
  - `daily_returns`, `estimator_seed` and `confirmation_path` in the object copy of `screen.py`;
  - the two module hashes of R-14a.

  The run uses the qualified image.

### D-3.4 The forecast (A4, A5)

- **Generator (A4).** The seed material is the production layout of IMPLEMENTATION_CONVENTIONS l.84-94, with purpose `lockbox_prediction` and `output_length` 457. The draws follow the `bootstrap_indices` draw order, run `m` times over `[0, n)`. `T*_r = sharpe(d[idx_r]).scaled`, and `q = type_seven_quantile(T*, 0.05)`. `ReplicateStream` is not touched.
- **ψ and b (A5).** `ψ = statistics._influence(d, sharpe(d))` and `b = block_length(ψ).value`.
- **Reference vectors (A5),** frozen with the code review for one published synthetic `d`:
  - ψ's hash and every `BlockLength` field (hexf);
  - the first 10 indices of `r = 0` and `r = 1999`, and the hash of all sequences;
  - the hash of the replicates;
  - `q` in hexf.

  Floats are hashed as big-endian `>d`, and indices as `>I`. The vectors are reproduced once per process start (the startup records below). That replaced rev 2's "checked every run" (D-20 rev 3 A5).
- **Startup records (rev 3 A5).** At each start on the qualified image, the lockbox process recomputes the vectors and the store appends `aqt.lockbox.startup.v1 = {startup_check_id, lockbox_module_sha256, image_digest, vectors_sha256, result}`. A process without a `PASS` record for its own module hash and image is refused at the pre-read check (`REFERENCE_VECTOR_MISMATCH`).

### D-3.5 The prediction artifact and sealing (A7; R-14a rev 3 item 2)

- **Schema `aqt.lockbox.prediction.v1`:**
  - `cycle_id`, `family`;
  - `nominee {trial_id, configuration_hash, hypothesis_hash, protocol_hash, trial_index, seed_l266, estimator_seed_policy, estimator_seed}`;
  - `source {window_id, n, d_sha256, evaluation_record_sha256}`;
  - `block {psi_sha256, value: hexf, raw: hexf | null, clipping: "LOWER" | "UPPER" | null}`;
  - `stream {seed_hex, seed_source: "R13_TRIAL_SEED", purpose, asset, cost, m: 457, attempts: 2000}`;
  - `replicates_sorted` (2,000 hexf strings, sorted by decoded value);
  - `q` (hexf);
  - `code` (§D-3.1).

  `artifact_sha256 = SHA256(cj(artifact))`. (rev 2-4 A7; A1b)
- **Pre-look record.** The C2 evaluation record of every trial stores `d_sha256` when the trial is evaluated, before the look.
- **Sealing,** on the experiment-engine path, by the confirmation module (R-14a):
  1. re-run the nominee's BTC baseline pair from the confirmation bars with the registered code, `estimator_seed` and the final-hour rule;
  2. require `d`'s hash to equal the pre-look `d_sha256`;
  3. compute ψ, b, the replicates and `q`;
  4. store the artifact and write `artifact_sha256` into `aqt.lockbox.sealing.v1`, which holds each family's status (a)-(d) (§D-1.7) and is written before any lockbox read.

  Any failure gives status (d).
- **Artifacts of the nominee (A1a).** These are the trial object (`TRIAL_FIELDS`; `configuration_hash = trial_sha256(trial)`) and its signal and overlay source files, by raw SHA-256. They are stored as hash-named files under the cycle's §26 store, fixed by one ledger entry `aqt.c2.artifacts.v1 = {items: [{kind, sha256, size}]}` before the declaration post. Retrieval follows `screen.load`'s hash-before-execute order, and a mismatch is a pre-read rejection.
- **Pre-read checks** (`lockbox_eval`; rev 2-3 A7):
  - the artifact hash matches the sealing entry;
  - `seed_l266` and `estimator_seed` re-derive from the nominee record under the signed policy;
  - `seed_hex` re-derives from `family_seed_f` and `trial_id`;
  - `seed_source`, `purpose`, `m` and the module hashes match the signed values;
  - P-4 (§D-2.2).

  A difference gives `IDENTITY_MISMATCH`.

### D-3.6 Signing (B1)

- Ed25519 (PureEdDSA, RFC 8032) through the maintained `cryptography` library, hash-pinned in one small signer-and-publisher environment. The key is generated before C2, and the raw public key goes in the signed C2.
- **Message:** the 12 fields `attestation.schema.json` requires, plus `family`, `nominee_trial_id`, `prediction_artifact_sha256` and the three fields (§D-2.1). `lockbox_evaluation_id` is the evaluation ID. The signed bytes are `cj` of the object without `signature`.
- Ed25519 verifiers differ (ZIP215 against strict RFC 8032), so the verifier is fixed with the code. (rev 2 B1, D20L-17)
- **Key lifecycle** (rev 2 B1):
  1. Before the owner signs C2, the signer host generates the key pair with the library, from the OS random source.
  2. The raw 32-byte public key, as 64 hex characters, is written into the signed C2's signing values (a `<<SIGNING>>` marker in DRAFT §4), so the protocol hash binds it.
  3. The private key file is readable only by the signer's service account. It is never copied, backed up, logged or put in the repository (Constitution l.198-199).
- **Verification** (rev 2 B1). The publisher reads the public-key bytes from the signed C2 protocol file, never from the signer. It verifies every attestation with the same pinned library and version as the signer, then applies P-8.
- **Loss or compromise** (rev 3 B1, with option C's replacement of the second test, C2 §1.10):
  - there is no key replacement during C2;
  - *lost key:* certificates already effective stay valid. A PASS not yet certified expires `U_ops` (P-6);
  - *suspected compromise:* this is a §26 incident, and no further signing with the key is allowed. A certificate stands only if it has a recorded owner approval **and** incident reconciliation on the store's records shows both of these:
    - its signed message equals the message §D-2.6's rules produce from those records;
    - an ATTESTATION delivery entry for the evaluation exists before any revision or invalidation entry, and the attestation's `cooling_off_start` equals the RESULT `delivered_at`.

    Every other certificate is void. If the store's own records are in doubt, every certificate without a completed promotion is void.
- **Store identities:** one store service holds the sealed store, the index and the clock. Callers reach it over a local channel that tells it the caller's OS account. The accounts mapped are `publisher`, `lockbox_eval` (worker and signer), `replay`, `reader` and the owner's command account (§D-2.3). Any other caller is refused and logged. (rev 3 B1)

### D-3.7 The store (rev 8 §1.2, as changed by option C)

**Records.** Only these are authoritative.
- **The index**, an append-only ledger, holding:
  - pre-read entries `aqt.lockbox.pre_read.v1 = {evaluation_id, attempt, family, nominee_trial_id, prediction_artifact_sha256, eligibility_result_id, lockbox_evaluation_id, pre_read_check_id, budget_before: 1, budget_after: 0, segment_status: "EXPOSED", r0}`;
  - rejection entries `aqt.lockbox.no_read.v1 = {family, nominee_trial_id, kind ∈ {PRE_READ_REJECTION, BARRED_DESCENDANT}, reason, ancestor_evaluation_id | null, visible_from}`. `visible_from` is the store-internal insert time `t1` for both kinds (rev 8 l.99; C2 §1.10: a barred descendant is visible from its own insert). The reader projection withholds it (§D-2.8; C5). Neither kind consumes budget or creates an evaluation ID;
  - release entries `{evaluation_id, result, commitment, released_at}`;
  - delivery entries `{evaluation_id, kind, file_hash, delivered_at}`;
  - VOID entries `{evaluation_id, kind: VOID, reason}`;
  - revision and invalidation entries `{kind, at}`.

  (rev 4 B4.1; rev 3 B4.3; C2 §1.3-§1.5, §1.10)
- **Sealed files**, each written once and never replaced:
  - the DEFAULT bundle with its nonce and commitment, under `(evaluation_id, attempt)`;
  - RESULT bundles;
  - at most one finished record per evaluation, `aqt.lockbox.finished.v1 = {evaluation_id, result, commitment, finished_at}`;
  - the pre-read check record `aqt.lockbox.pre_read_check.v1 = {check_id, evaluation_id, family, nominee_trial_id, prediction_artifact_sha256, eligibility_result_id, lockbox_evaluation_id, sealing_id, startup_check_id, lockbox_module_sha256, image_digest, result: "PASS" | <reason code>, checked_at}`. There is at most one per `evaluation_id`, because there is no retry in C2. It is not on the index. (rev 4 B4.1);
  - startup records;
  - attestation files.

  A sealed file is created by writing a temporary file, fsyncing it, linking it without replacing, and fsyncing the directory. All sealed files are in one directory.
- **The sealed bundle `aqt.lockbox.sealed_bundle.v1`** (rev 3 B4.2 with rev 4 B4.2):
  - fields `schema, evaluation_id, kind (RESULT | DEFAULT), result, cause_class, values {t_l, q, mdd_btc_cand, mdd_btc_bench, eth_e_improv, mdd_eth_cand, mdd_eth_bench}, conditions {L1..L4}, reasons, upside, capture {engine_commit, image_digest, input_manifest_sha256, lockbox_module_sha256, prediction_artifact_sha256}, operational {read_start, sealed_at, startup_check_id}`;
  - **`operational`** fields are all filled in by the store, never by the worker. `read_start` is the store second at which the first lockbox byte was served (null in a DEFAULT). `sealed_at` is the store second of the bundle write (`t_s` for a DEFAULT). (rev 3 l.274)
  - each atomic comparison is null iff one of its own inputs is null; `L4 = AND3(c4a, c4b)`;
  - **precedence:** DEFAULT gives FAIL/DEADLINE; else any false gives FAIL/PERFORMANCE; else any null gives FAIL/TECHNICAL; else PASS with `cause_class` null;
  - **`reasons`:** a sorted, unique list of `<scope>:<code>` strings, `[]` if none. Scope is one of `BTC_EDIFF`, `BTC_MDD`, `ETH_EIMPROV`, `ETH_MDD`, `RUN` or `DEADLINE`. Code is one of `INSUFFICIENT_OBSERVATIONS`, `ZERO_VARIANCE`, `NONFINITE_RESULT`, `NONPOSITIVE_LONG_RUN_VARIANCE`, `DAYS_INCOMPLETE`, `NONFINITE_EQUITY`, `RUN_FAILED` or `NOT_FINISHED_BY_D_W`. (rev 2 B4.2)
  - **DEFAULT bundle:** `kind DEFAULT`, FAIL/DEADLINE, every value null except `q`, conditions all null, `reasons ["DEADLINE:NOT_FINISHED_BY_D_W"]` (read as "not finished by `D*`", rev 5), upside `NOT_COMPUTED` with reason `T_L_UNAVAILABLE`, `operational.read_start` null, and `sealed_at = t_s`. The capture values are known before the read, so a DEFAULT carries the same values;
  - `values` are hexf or null;
  - "failed technically" (Q2a) means `cause_class ∈ {TECHNICAL, DEADLINE}`;
  - `commitment = SHA256(nonce ‖ cj(bundle))`.

  The PASS fixture is rev 4 B4.2's (1,053 bytes, SHA-256 `d64d228b…ba520`).
- **Pre-read reason codes (Q2b):** `ARTIFACT_NOT_FOUND`, `ARTIFACT_HASH_MISMATCH`, `IDENTITY_MISMATCH`, `PREDICTION_ARTIFACT_INVALID`, `REFERENCE_VECTOR_MISMATCH`, `IMAGE_MISMATCH`, `BUDGET_EXHAUSTED` and `ANCESTOR_UNRELEASED`. (rev 2 list without `COOLDOWN_NOT_ELAPSED`, per rev 4; `ANCESTOR_UNRELEASED` per C2 §1.6)

**One lock.** `L_store` is the store's own lock file. The store takes it for:
- `begin_read` (including the `R_0` recovery lookup);
- rejection appends;
- `release`, `record_delivery` and `sign_permit`;
- revision and invalidation appends;
- reader rows;
- `verify_replay`, reconciliation and startup;
- the read gate's entitlement check;
- steps 2-4 of `mark_finished` (with step 2a).

`NOT_YET` takes no lock. The worker and the signer never hold `L_store`. `write_bundle` and every other sealed create take no lock. Every index reader goes through these operations; this is an obligation on the store code, checked by tests and §16 review. (rev 8 l.75 as replaced by C5 item 3)

**Durable before use.** Holding `L_store`, an operation first does its lookups. It then fsyncs the index file, the index's directory and the sealed directory. Only then does it answer, append, create, serve a bar or authorise a signature. An fsync error is a §26 stop.
- *Platform assumptions:* an fsync makes durable whatever is already written to that file or directory, and the OS releases `L_store` when its holder exits. Both stay `UNVERIFIED_EXTERNAL_ASSUMPTION`.

**Time rule (Q7, accepted).** A save with a deadline counts as made at the clock reading `t1` taken while holding `L_store`, immediately before it starts, if `t1` is before the deadline. A save lost in a crash before it is durable never happened. No rule can both keep every on-time save and refuse every late one.
- **Index appends:** `begin_read`'s append has deadline C. A `LedgerError` before writing means nothing was written: a timeout is refused, and damage is a §26 stop. Any error after the write starts is a §26 stop.
- **`mark_finished(evaluation_id)`,** deadline `D*`:
  1. Without the lock, verify the RESULT bundle against its commitment, then fsync the bundle and the sealed directory.
  2. Take `L_store`, look up the pre-read entry and any finished record, do the fsyncs, then read `t_f`.
  - 2a. If a release entry exists, refuse; the bundle is late output and void.
  3. If `t_f ≥ D*` or a finished record exists, refuse.
  4. Otherwise create the finished record with `finished_at = t_f`, including its directory fsync, and only then release `L_store`.

  A finish whose check was before `D*` may still be saving after `D*`. It survives or is lost in a crash, and "after `D*` no new finish counts" means no new check qualifies.
- **Start checks:** `record_pre_read_check` (deadline C) and each bar (deadline `D*`) read the clock before starting and refuse at or after the deadline.
- **Cap scope:** from C on, no operation limited by C or `D*` starts: no pre-read check, read authorisation, rejection append, bar or counted finish. Release, delivery, `write_bundle`, reads, reconciliation and replay continue.

**`begin_read(evaluation_id)`,** called by the publisher, under `L_store`. The lookups come first (index verification, reconciliation, entitlement, budget, order and cooldown), then the fsyncs, then any answer, append or sealed create.
1. Index damage is a §26 stop.
2. **Reconciliation:** return an existing pre-read entry, after checking that its DEFAULT verifies (otherwise a §26 stop), or an existing rejection entry.
3. **Cap:** sample `t_s`, the store clock floored to the second. If `t_s ≥ C`, answer `CAP_REACHED` and write nothing.
4. **Entitlement:**
   - sealing records exist for every declared family, and this family is status (a) for this nominee and artifact;
   - a check record's identity fields equal the sealing record and the request;
   - its `startup_check_id` names a `PASS` startup record for the same module hash and image.

   With no check record or differing identities, refuse, write nothing and log an incident. A check result that is a reason code appends a rejection entry.
5. **Lineage, before budget** (owner choice 3, `OWNER_DECISION_S4_FOLDIN.md`): an ancestor without a release entry appends an `ANCESTOR_UNRELEASED` rejection; a released FAIL ancestor appends `BARRED_DESCENDANT`. Neither consumes budget. (C2 §1.6; D-12 P-3)
6. **Budget:** an existing pre-read entry for the family this cycle appends a `BUDGET_EXHAUSTED` rejection.
7. **Order and cooldown:** return `DEFERRED` and write nothing while `t_s < r0′ − 604,800 + 2,592,000`, or while the trend family is status (a) with neither an entry nor a rejection.
8. `r0 = t_s + 604,800`. Pick `attempt`, and create the nonce and DEFAULT bundle with `sealed_at = t_s`.
9. Append the pre-read entry under the time rule with deadline C. A miss leaves the DEFAULT a void orphan, spends no budget, and answers `CAP_REACHED`.

(rev 4 B4.1; rev 6 step 6; rev 7 l.140-152; rev 8 l.99; C2 §1.6)

**The read gate.** Under `L_store`, the store looks up the pre-read entry, its DEFAULT and a `PASS` startup record for the check record's module hash and image, then does the fsyncs, verifies the DEFAULT, and opens a session for `lockbox_eval`. Bars over `[S_pre, L1)` under the manifest are served without the lock, each under the start check against `D*`. After C the gate serves nothing.

**Startup and reconciliation.** Before serving anything, under `L_store`: index verification and reconciliation, then the fsyncs. Nothing is rebuilt or replayed.
- A sealed DEFAULT whose attempt has no pre-read entry is a void orphan.
- A pre-read entry whose DEFAULT is missing or does not verify is a §26 incident.
- Temporary files and void bundles are logged.

**Replay under R-a, `verify_replay(evaluation_id, projection_bytes)`.** It is for the `replay` role only, on a PASS, after the segment has rolled into confirmation.
- It checks the bundle against the release entry's commitment, then compares `cj(bundle without "operational")` with `projection_bytes`.
- It returns only `MATCH` or `MISMATCH`, and a MISMATCH voids the promotion (§27, Constitution l.194). It never returns a nonce or a diagnostic.
- If the bundle-against-commitment check fails, it returns `MISMATCH` **and logs a §26 incident**.
- The replay job builds its projection by re-running under the recorded `capture`. If it cannot load the bars under `input_manifest_sha256`, the result is `MISMATCH`. (rev 3 B4.4)

### D-3.8 Crash points and tests (rev 8 §1.2; option C C2 §1.9, C3 §1.9, C5)

- **Crash rows:** rev 8 rows 1-9, 11 and 12, plus option C rows C1-C15. Under a machine crash, un-fsynced data may survive whole, be lost, or (an index tail) be partly written. A partial index tail is a §26 stop.
- **Tests, the complete effective list** (each against a synthetic store with an injectable clock; synthetic data only):
  - **D-12 T-1..T-8** (D-12 rev 7 l.140-147), as option C's crosswalk (`OPTION_C_PROPOSAL_REV2.md` l.336-343) reads them:
    - T-1 is replaced by TC-1, TC-6 and the reader row;
    - T-2 by TC-2;
    - T-3 by the single release and RESULT-delivery path (TC-4);
    - T-5 by TC-2, TC-3 and C2-C11;
    - T-6 is kept as TC-7 with C9-C10;
    - T-8 is replaced by TC-4;
    - **T-4 and T-7 are deleted.**
  - **A1a artifacts:** a flipped byte is refused for each kind; a valid Python source file is never parsed as JSON.
  - **A1b seeds:**
    - same-seed reproduction, for each allowed class;
    - one re-derivation vector per policy, including an `L266_MOD_2_31` seed that maps to 0, which is accepted;
    - a fit recorded under the other policy is refused;
    - the stored seeds re-derive from the trial record.
  - **A5:** the reference vectors and the startup check (`REFERENCE_VECTOR_MISMATCH`).
  - **A6:**
    - the kernel and `max_drawdown` give equal values on one synthetic path, bit for bit;
    - BTC E-DIFF stays available when ETH E-IMPROV is unavailable, and the reverse;
    - the hourly instants are `start + i h` for `i = 0..24·m − 1`;
    - a two-hour series is refused by the interval check;
    - the derived terminal bar changes nothing except the last hour's return (PR #81 tests T4).
  - **A7:** one `seed_hex` test vector per `seed_source` branch, and a differing `seed_source` gives `IDENTITY_MISMATCH`.
  - **B1 signing:**
    - RFC 8032 §7.1 vectors, cited from the RFC at build time;
    - signing twice gives identical bytes;
    - each guard refusal (rev 2 l.255);
    - an attestation signed by a different key is refused.
  - **B1 roles:**
    - a caller from an unmapped account is refused;
    - each role is refused each operation outside its row;
    - the signer refuses when the publisher's request lacks a store `sign_permit` or disagrees with it (C3 §1.10a);
    - the compromise reconciliation cases: approved and consistent, approved and inconsistent, unapproved.
  - **B4.2 bundles:** byte-exact bundles for each kind, including the PASS fixture and rev 4's two ETH rows.
  - **B4.4 replay:** identical science with different `operational` fields gives MATCH; one flipped bit in `values` gives MISMATCH; a tampered stored bundle gives MISMATCH plus an incident; an input manifest whose bars cannot be loaded gives MISMATCH.
  - **`begin_read`,** from rev 3 l.253-257, rev 4 l.147-155, rev 6's cooldown boundary at `r0′ − 604,800 + 2,592,000`, and rev 5's cap-order test:
    - two concurrent calls make one entry;
    - a crash after the DEFAULT leaves an orphan, and the next call uses `attempt + 1`;
    - a crash after the append returns the existing entry;
    - the budget refusal, with owner choice 3's lineage-before-budget order;
    - a damaged index stops the process;
    - two families concurrently and in sequence inside the cooldown;
    - the cooldown boundary;
    - order deferral, and its release by a trend entry and by a trend rejection (rev 4 l.150);
    - `t_s` at `C − 1` and at C;
    - a read-gate check racing the append;
    - a call with no check record;
    - a failed check called twice gives exactly one rejection;
    - an existing entry with a damaged DEFAULT is an incident.
  - **Store:** T-S2 and T-S4 for the kept crash rows, and option C's TC-1..TC-7, with these replacements:
    - **T-S1:**
      - `begin_read` at `t1 = C − 1` is accepted, and at `t1 = C` refused with nothing written. With an accepted `t1`, the clock is advanced past C at each point inside `append_entry`, and the entry counts. An injected write, flush or fsync error gives a §26 stop and serves nothing (rev 8, its `begin_read` half);
      - every concurrent reader-row, `release`, `sign_permit` and `begin_read` call waits until the append is durable, then answers from the durable state by its own return contract (C5 item 2);
    - **T-S2:** a concurrent `release` whose clock reading under `L_store` is before `R_0` is refused; one at or after `R_0` waits for the finish's hold and shows its result (C5 item 2);
    - **T-S6:** each of the release entry and the RESULT delivery file has one fixed shape for every FAIL cause, no record's bytes depend on the cause, and their shared fields agree (C5 item 1);
    - **TC-6:** an ID with no pre-read entry gives `STOPPED`; a terminated-cycle ID is served.
  - The machine-crash rows need a test file layer that applies each permitted outcome. If the build cannot provide it, those rows are not available and block completion.
  - No test measures timing, and no timing property is claimed.
- **R-14a contracts (item 5).** Each module's input-to-record contract is part of the signed C2, with consumer-boundary tests for missing, duplicate and misaligned observations.

### D-3.9 Not decided here (S4 or later)

- the channel for the owner's forced command, the clock source, the reconciler and his view (§D-2.3), and the governance action that appends revision entries;
- each build, under §16 review: the store, publisher, signer, both modules and the access tooling.
