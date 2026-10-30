# D-20 lockbox bindings, option C: release on request (revision C3; delta on C2)

**Author:** Claude Opus 5.5 (`claude-opus-5-5`, this session's environment metadata), main Claude Code session, 2026-10-30. AI drafting, not an authority. I propose and check bindings. I cannot decide, accept, activate or amend anything.

**Status: INACTIVE PROPOSAL, UNREVIEWED.** Nothing frozen changed. No row binds until the owner decides and signs the C2 §4 amendment. R19-2 requires a two-family re-check before any owner decision. No human statistician has reviewed it.

**Owner direction (2026-10-30):** "Go ahead" with C3. Both C2 re-checks asked for narrower claims and clarifications, not new machinery. This revision adds **no new record type, lock, operation or role**. It moves the existing VOID append into `sign_permit` (D20L-91), and adds report and outbox duties to the existing backstop.

**Answers** (both read in full):
- `SOL_OPTION_C2_REVIEW_A56F220.md` (gpt-6-sol): FIX, D20C2-S-1..6;
- `ASTRA_OPTION_C2_REVIEW_A56F220.md` (gpt-6-astra): FIX, D20C2-A-1..6.

Both reviews confirm again:
- the §1.3 result proof, under rev 8's storage assumptions;
- the restored signed `cooling_off_start` (Constitution §13, frozen schema);
- delivery's causal order;
- index ordering against revisions.

**How to read it:** a **delta on `OPTION_C_PROPOSAL_REV2.md`**. The sections named in each heading replace C2's text whole. Everything else in C2 stands, and through C2, rev 8's read side.

**VERDICT: `AMENDMENT_REQUIRED`.**

## 1a. Dispositions

| ID | Disposition | Repair |
|---|---|---|
| **D20C2-S-1 ~ D20C2-A-3** (Sol BLOCKER, Astra NON-BLOCKING; effectiveness check before C, durable after C) | **Accepted at BLOCKER.** The two moments are now named separately: the **check** (counts) and **durability** (confirmed). P-6's "at the cap" is read as "at the check", proposed to the owner in Q7 with its consequence and the stricter alternative. Q7's "nobody can read" is corrected. Tests cross C after the check. | §1.5a; Q7; C12-C13; TC-4 |
| **D20C2-S-2 = D20C2-A-1** (BLOCKER; completion guarantee) | **Accepted.** The backstop **attempts** release. A read whose `R_0` is still ahead waits for `R_0`. An outage or §26 stop can block it indefinitely. No date is guaranteed. The report stays visibly incomplete; termination effects are not postponed. The backstop also re-creates missing outboxes (fixes C2's row C3). | §1.6; C3; QC1 |
| **D20C2-A-2** (BLOCKER; report visibility after non-calendar termination) | **Accepted.** The cycle report is visible from the cycle's termination, **whatever its cause**, and includes results released after that. The reader row is aligned, and the closed-cycle refusal is deleted. | §1.1 reader row; §1.6 |
| **D20C2-S-3** (BLOCKER; "cannot change a result" too broad) | **Accepted.** The invariant is stated for **released** results only. Before release, delay can make a finish miss `D*` (a technical FAIL) or an admission miss C (`CAP_REACHED`). Both are disclosed in §1.7 and QC3. | §1.7; QC3 |
| **D20C2-S-4 ~ D20C2-A-6** (BLOCKER / NON-BLOCKING; §7 row vs codes; `STOPPED`) | **Accepted at BLOCKER.** The §7 row now enumerates the six codes and the public accounting facts. `STOPPED` is defined as **an undifferentiated refusal whose cause is withheld** (an active §26 stop, a failed request, an unknown ID). | §1.1 codes; §1.8; QC3 |
| **D20C2-S-5 = D20C2-A-6** (NON-BLOCKING; PENDING forever) | **Accepted.** `sign_permit` refused for cap or revision now appends the VOID entry itself, so the code becomes `PASS_NOT_CERTIFIABLE` with no signing attempt. | §1.5b; C14; TC-4 |
| **D20C2-A-4** (NON-BLOCKING; clock qualification) | **Accepted.** "Never earlier" is a statement about **operation order**. Timestamps and "72 hours of actual access" rely on R3's accurate elapsed clock, including no forward jump. TC-3 proves order only. | §1.5c |
| **D20C2-S-6 ~ D20C2-A-5** (NON-BLOCKING; inherited tests and clauses) | **Accepted.** rev 8 T-S2 and T-S6, rev 4 l.95-97 and rev 3 l.204 are superseded. The replay role (rev 3 l.182) is kept by reference. C2's missing §1a row for D20C1-A-3 is added. C2's "D20L-83..89 (§4)" should read "(§5)". | §1.10a; §4 |
| **D20C1-A-3** (C2 omitted its row) | **Accepted in C2** (§1.5: `cooling_off_start` = RESULT `delivered_at`, signed after it; D20L-86). Both C2 reviews ACCEPT it (Sol l.17, Astra l.29). | C2 §1.5 |

## 1. Replacements

### §1.1, response codes and reader row (replace C2's code table, its ID sentence and its reader row)

| Code | When |
|---|---|
| `STOPPED` | **An undifferentiated refusal; its cause is withheld.** It covers an active §26 stop, a request that failed for any reason (including a hash mismatch in delivery), and an ID with no pre-read entry. Causes go to logs the owner cannot read. |
| `NOT_YET` | The host clock is before `R_0`. |
| `FAIL` | Released FAIL, RESULT delivered. |
| `PASS_CERTIFICATE_PENDING` | Released PASS, RESULT delivered, attestation neither effective nor VOID. |
| `PASS_CERTIFIED` | ATTESTATION delivery entry exists: effective. |
| `PASS_NOT_CERTIFIABLE` | VOID entry exists (CAP or REVISION). |

**Precedence:** `STOPPED`, then the state in table order. Each code has fixed bytes; `FAIL` has the same bytes for every kind of FAIL. An ID that has no pre-read entry returns `STOPPED`. An ID of a terminated cycle is served normally, so the owner can still collect his copy. C2's closed-cycle refusal is **deleted** (D20C2-A-2).

**Reader row:** pre-read entries (identity fields, `R_0`), rejection entries, delivery entries, VOID entries, revision entries, and release entries that are visible:
- after their RESULT delivery entry; **or**
- from the termination of their cycle, whatever its cause (calendar, revision, invalidation), for a release entry made before or after that termination (§1.6).

**Replay role:** rev 3 l.182 stands unchanged (`verify_replay`, B4.4).

### §1.5a, when a certificate counts (new paragraph; replaces C2's sentence "The attestation is effective from this entry")

Two moments are distinct, as for finishing (§1.3):
- **The check:** the clock reading `t_e` taken under `L_store` in `record_delivery(ATTESTATION)`, with no revision or invalidation entry before it in the index.
- **Durability:** the fsync of the ATTESTATION delivery entry, after which the code `PASS_CERTIFIED` may be returned.

**Draft rule (Q7):** the certificate counts as effective **at `t_e`**, if `t_e < C`. Its entry may become durable after C. If a machine crash leaves the entry whole but un-fsynced and it survives, it counts at `t_e` even when recovery runs after C. If the entry is lost, there is no certificate; the retry's check is after C, so the retry writes VOID (CAP).

**How P-6 reads under this:** "a nominee not attested by day 255 expires" means "no ATTESTATION delivery entry with `t_e < C`". This is a proposed meaning of the decided D-12 P-6, put to the owner in Q7 with the stricter alternative: count a certificate only if its durability was confirmed, by a clock reading after the fsync, before C.

**Correction of C2 (D20C2-A-3):** before durability, the owner already holds the attestation bytes; they were delivered to his record (§1.4). What nobody can obtain before durability is the authoritative confirmation: the entry and the code `PASS_CERTIFIED`. The promotion guard reads only the entry, so the bytes alone confer nothing.

**Index order against revisions stands** (C2 §1.5; both reviews accept).

### §1.5b, a terminal answer without signing (replaces C2's `sign_permit` refusal behaviour)

`sign_permit` under `L_store`:
- If the release is PASS and the RESULT delivery exists, but the clock is at or after C, or a revision or invalidation entry follows the pre-read entry, then it **appends `{evaluation_id, kind: VOID, reason: CAP | REVISION}`** (the existing VOID record) and refuses.
- Any other refusal writes nothing.

So a PASS for which certification has become impossible gets `PASS_NOT_CERTIFIABLE` at the next request. It no longer stays `PASS_CERTIFICATE_PENDING` (D20C2-S-5). The same check at `record_delivery` (C2 §1.5) still covers a signer that stalls past C or past a revision after its permit. Both paths write one VOID at most: the store refuses a second.

### §1.5c, clock qualification (appended to C2 §1.4 "What this proves" and §1.5 "Promotion guard")

- **"`delivered_at` is never earlier than the owner's durable copy"** is a statement about **operation order**: `record_delivery` runs only after the owner's read-back. That the timestamp is not earlier than the copy's real creation time, and that `cooling_off_start + 259,200` is at least 72 real hours later, both rely on **R3: an accurate host clock, with no backward step and no forward jump**. TC-3 tests order, not elapsed-time accuracy. A forward jump during cooling-off could let the guard accept a decision early.
- This is disclosed, not repaired: the trusted clock is already R3 for every time rule (C2 §1.3 list).

### §1.6, every read is released, as far as the service can (replaces C2 §1.6)

**Backstop attempts.** The backstop is the publisher's fixed-time step. It attempts `release` for every counted read without a release entry, and outbox creation for every released read without a RESULT delivery entry. It runs:
- at `R_0 + 604,800` for each read;
- at every revision, invalidation and calendar termination, for all reads.

A read whose `R_0` is still ahead **waits for its `R_0`**; the store refuses earlier releases (C2 §1.3). Every failed attempt is retried at the next run, and runs repeat daily until no read is pending. An outage, a stalled `L_store` holder or an unresolved §26 stop **can block release indefinitely**. No completion date is guaranteed.

**What the backstop does guarantee:** release no longer depends on the owner asking. The result, once released, is fixed (§1.3), whenever that happens.

**Pending list:** as C2. It holds public accounting only: evaluation IDs without a release, and IDs released but without RESULT delivery.

**Cycle report.**
- **Visible** from the cycle's termination, whatever its cause. It shows every counted read's released result, including results released **after** termination as they arrive.
- **Marked incomplete** while any counted read has no release entry, listing those IDs as `PENDING_RELEASE`.
- **Incompleteness never postpones** termination, invalidation or cap effects; those apply at their own time.
- **Not complete** until every counted read is released. If the service never recovers, the report stays incomplete, which is a §26 incident.

**Lineage:** `ANCESTOR_UNRELEASED` as C2 (identical bytes whatever the hidden result). It can block a descendant indefinitely under the same conditions.

**QC1's sentences** "no result can stay hidden" and "nothing … can be asked" are replaced (§3).

### §1.7, residual, item "What none of these can do" (replaces C2's last paragraph of §1.7)

**What delays can cause before release** (D20C2-S-3):
- A finish delayed past `D*` (by contention, a stall, or the machine being down) is refused. The read is a **technical FAIL**, although it might have passed. This is not a released result changing; it is how the read's result is formed.
- An admission delayed past C is `CAP_REACHED`.
- Both effects are disclosed. Under P-3, every technical FAIL counts as a FAIL.

**What nothing can do:** change a result **after it is released** (§1.3), or a counted try.

**What option C removes:** the daily missed-slot mechanism, signing before the owner has the result, and every `state`-type query.

### §1.8, proposed Constitution §7 row (replaces C2 §1.8; only if the owner accepts QC3)

| Ref | Current v1.0 text | Proposed v1.1 text |
|---|---|---|
| §7 l.79 | "Research receives PASS/FAIL only." | "Research receives PASS/FAIL only, except as follows. (a) The cycle outcome of §5 may show that a family had no result because its lockbox read failed technically. (b) The lockbox service may answer a request only with one of these fixed responses: not yet; FAIL; PASS, certificate pending; PASS, certified; PASS, not certifiable; or stopped, a refusal whose cause is withheld. (c) Research may see these public accounting facts: a read's identity and earliest release time; its release, delivery and cooling-off times; the pending list; whether a cycle report is complete; and revision entries. (d) How quickly the service answers any request; a delay of any length in a release, its delivery or its certification; an expiry at the processing cap caused by such a delay; and a technical fail caused by a delay before the worker deadline are not results under this rule, even where they allow a guess about a result or about another read's progress. This exception permits no other research-visible field, message, record or diagnostic. No component may vary its timing to convey a result." |

The first clause is D-12 Q2a's row. The row now lists exactly the interface in §1.1 and §1.6 (D20C2-S-4).

### §1.9, crash rows and tests (amend C2 §1.9)

**Row C3 replaced:** "release durable, no RESULT delivery: the next request **or the backstop** re-creates the outbox if missing; RESULT delivery still waits for the owner's request. Finishes refuse (step 2a)."

**New rows:**

| # | Crash or event | Effect |
|---|---|---|
| C12 | effectiveness check at `t_e < C`; append durable after C | counts at `t_e` (Q7 draft rule); `PASS_CERTIFIED` is returned only after the fsync |
| C13 | M crash after a whole, un-fsynced ATTESTATION entry; recovery after C | **whole:** counts at `t_e`. **lost:** the retry's check is after C, so it writes VOID (CAP). **partial:** §26 stop |
| C14 | `sign_permit` at or after C, or after a revision, with no attestation | VOID appended; `PASS_NOT_CERTIFIABLE` |
| C15 | revision before `R_0` | backstop waits for `R_0`; the report lists the read `PENDING_RELEASE` until then |

**TC-4 additions:**
- check at `C − 1` with the clock moved to `C + 1` before the fsync: it counts, and `PASS_CERTIFIED` is shown only after the fsync;
- C13, all three outcomes;
- C14 with no signer call;
- a second VOID is refused.

**TC-5 additions:**
- a revision before `R_0`: no release until `R_0`;
- an injected permanent store outage: the report stays incomplete and termination effects still apply;
- after a revision terminates the cycle, a backstop-released result appears in the report without RESULT delivery;
- a terminated-cycle ID is served.

**TC-6 changed:**
- `STOPPED` has the same bytes for every cause: §26 stop, injected exception, hash mismatch, unknown ID;
- `FAIL` has the same bytes for every FAIL kind.

### §1.10a, more inherited clauses superseded (appended to C2 §1.10)

| Inherited | Superseded by |
|---|---|
| rev 4 l.95-97, signer guard time bullets (`R_j = R_0 + j·86,400`; `R_j − 21,600 ≤ store_now < R_j`, `R_j < C`) | C2 §1.5 `sign_permit` and §1.5b |
| rev 3 l.204 test, "the signer refuses when `guard_state` and the publisher's request disagree" | "the signer refuses when the publisher's request lacks a store `sign_permit` or disagrees with it" (TC-4) |
| rev 8 T-S2, "a concurrent `state` waits and then shows it" | "a concurrent `release` waits and then shows it". The rest of T-S2 stands. |
| rev 6 l.169 / rev 8 T-S6, "`state` and release bytes have the identical shape for every FAIL" | "the release entry and the RESULT delivery file have the identical shape, and `FAIL` identical bytes, for crash, deadline, technical and performance FAIL" (TC-6) |
| C2 §1.1 "an ID that … belongs to another cycle's closed record, returns `STOPPED`" | deleted (§1.1 above) |
| C2 §1a last row "(§4)" | read "(§5)" (erratum; C2 is not edited) |

## 3. Owner questions (amend C2 §4)

**QC1**, the "In short" paragraph becomes:

> No result is released before seven days after its test started. You can ask earlier, and you get "not yet". From then on you ask, and the posting job releases the result and copies it to your own records: PASS or FAIL, nothing else. If you don't ask, the service tries to release it by itself after another seven days, so release doesn't depend on you; but a broken service can hold it up, and then the cycle report stays marked incomplete. On a PASS, your 72 hours start when your copy arrives, and the signed certificate carries that time.

The options are unchanged.

**QC3**, the "In short" list becomes:
- How long any answer takes, even "not yet", can depend on hidden work, for this test or another. Someone timing it closely might guess that a test is still running or has just finished.
- Nobody has shown that it cannot hint at pass versus fail.
- A busy or broken computer can delay a result, its copy to you or its certificate by any length of time. Near day 255, that can make a PASS expire unpromoted.
- **Before a result is released, a busy or broken computer can make a test miss its deadline. It then counts as a technical fail, although it might have passed.**
- You see only six fixed answers: not yet; FAIL; PASS, certificate pending; PASS, certified; PASS, not certifiable; or "stopped", which never says why.

The closing sentence and the options are unchanged.

**Q7** becomes:

**Q7. When does a save count as made in time?** Three saves have deadlines:
- starting a test (before day 255);
- finishing a test (before the worker deadline);
- a certificate becoming valid (before day 255 and before any revision).

**Draft rule:** a save counts at the moment the service checks its clock, while it holds its lock, if that is before the deadline. The service shows "done" only after the save is safely on disk. If a crash loses the save, it never happened: no test, a technical fail, or a certificate attempt retried (refused after day 255).
- *Cost:* a save may reach the disk just after the deadline and still count. For a certificate, that means one checked a moment before day 255 counts even if it is saved a moment after. Your day-255 rule would be read this way in C2.

**Stricter rule (possible; not drafted):** a save counts only if the service confirmed, after the disk finished, that the deadline had not passed.
- *Cost:* some saves made in time are thrown away: a technical fail, or a certificate refused. It needs additional durable evidence and design work.

No rule can both keep every on-time save and refuse every late one, because after a crash the records can look the same either way.

The options are unchanged.

## 4. Findings, remaining, unauthorised, self-check

**New findings** (continuing; C2's D20L-83..89 stand, with D20L-87 and D20L-88 amended here):
- **D20L-90 BLOCKER (repaired; §1.5a, Q7).** Effectiveness at the check versus at durability was unstated, and P-6's reading was implicit (D20C2-S-1 ~ A-3).
- **D20L-91 NON-BLOCKING (repaired; §1.5b).** A PASS could stay pending forever after certification became impossible (D20C2-S-5 = A-6).
- **D20L-92 BLOCKER (repaired by narrowing; §1.6, QC1).** Completion was claimed as guaranteed (D20C2-S-2 = A-1). D20L-87 is amended: the backstop attempts release.
- **D20L-93 BLOCKER (repaired; §1.1, §1.6).** There was no report visibility after non-calendar termination (D20C2-A-2).
- **D20L-94 BLOCKER (repaired by disclosure; §1.7, QC3).** Pre-release delays can cause a technical FAIL (D20C2-S-3). D20L-88 is amended.
- **D20L-95 BLOCKER (repaired; §1.1, §1.8).** The §7 row did not enumerate the interface, and `STOPPED` was ambiguous (D20C2-S-4 ~ A-6).
- **D20L-96 NON-BLOCKING (applied; §1.5c, §1.10a).** Clock qualification, inherited tests and clauses, missing §1a row, erratum (D20C2-A-4, S-6 ~ A-5).

**Remaining:** as C2 §5, with the R19-2 re-check now of C3.

**Unauthorised:** as C2. `KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid outcomes.

**Self-check:**
- one file written in this step;
- all 12 C2 findings answered (D20C2-S-1..6, D20C2-A-1..6), plus the missing D20C1-A-3 row;
- new findings D20L-90..96, no gaps;
- no new record type, lock, operation or role. The VOID append moved into `sign_permit`, and the backstop gained outbox recovery and the cycle-report duty;
- deleted: the closed-cycle refusal, and the claims "guarantees … by `C + 14 days`", "no result can stay hidden", "nothing … can be asked" and "none of these can change a result" (now limited to released results).
