# D-12 decision proposal, revision 6 (consolidated; supersedes revisions 1-5)

**Reviewer model (observed):** Claude Fable 5.1, model ID `claude-fable-5-1`, per this session's metadata. I am an AI reviewer, not an authority. I propose and check bindings only; I cannot accept, activate or amend governance.

**Status: INACTIVE PROPOSAL.** It needs the owner's decisions on Q1-Q6 and then the owner's signed C2 amendment before it binds anything. **Nothing frozen changed.**
**Review status:** revision 6 is unreviewed. R19-2 requires a focused re-check by two model families before the owner decides.
**VERDICT: `AMENDMENT_REQUIRED`** (unchanged).

**How to read it:** this file is self-contained. It replaces `PROPOSAL.md` and `PROPOSAL_REV2.md`..`PROPOSAL_REV5.md` for the owner; those stay as history. It answers the re-check 4 records `SOL_REREVIEW4_6A880C2.md` (gpt-6-sol, FIX, D12R5-S-1..4; the report's verbatim labels are `D12R5-U-n`, mapped by its header to S-n) and `ASTRA_REREVIEW4_6A880C2.md` (gpt-6-astra, FIX, D12R5-A-1..5). I read both in full.

**Owner direction for this revision:** simplify rather than patch. Revisions 3-5 built hourly slots, a staging barrier, batch markers and up to 1,632 pre-signed certificates per read, and each round found new holes in that machinery. The goal is narrow: **when a result is published must not reveal whether a FAIL was a technical breakdown or a performance failure**, and the certificate's `cooling_off_start` must be the moment the result really became visible (Constitution §13 l.124). §3 below is the simplest design I found that does both.

**Checkout and mode:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch freeze-sheet, HEAD `bcaf37d`. The agent wrote only this one new file, at the caller's instruction (this worktree's agent definition still lists `Write` as disallowed; the caller's scope was followed, as in revisions 3-5). Nothing was staged or committed. No frozen file, hash or sidecar was touched. No simulation; no confirmation, lockbox, network or credential access.

## 0. Verification run

- **Citations re-read:** Constitution §3 l.41, l.45; §4 l.48, l.50, l.52; §5 l.63; §7 l.73-85 (l.79 "Research receives PASS/FAIL only"); §13 l.122-126; §26 l.191; §27 l.194. Protocol l.67-95 (l.74, l.75, l.76, l.77-79, l.89), l.294-300 (l.296, l.300). `THREAT_MODEL_v1.md` l.9, l.13. C2 draft `DRAFT_WORDING.md` l.1, l.43-44, l.55-59, l.75-92, l.221-245, l.406. `OWNER_DECISION_O1_O7.md` l.43-46. `OWNER_DECISION_D11.md` l.26.
- **Topic search, both directions (item 1).** Searching the C2 draft for "Constitution" found the controlling fact for D12R5-S-1 that no revision cited: the C2 draft **is itself a Constitution §4 amendment that produces Constitution v1.1** (title l.1; l.43-44; clause table l.75-92; version bump l.406). Its row at **l.82 already rewrites Constitution §5 l.63** to define `NO_RESULT` as including "its lockbox read failed technically". Earlier revisions called this "draft l.82" without noticing it is a Constitution-level row (D12-30).
- **Exact arithmetic (`fractions.Fraction`, run this session).** Trend read starts on day 180 + g, volatility 30 days later; release `R_0` = read start + 7 days; cooling-off 3 days; cap day 255. With j missed releases: visible by the cap iff **g + j ≤ 38**; cooling-off also ended iff **g + j ≤ 35**; slack for the owner's answer = 35 − g − j days. Worked example: g = 34.5, j = 0 leaves half a day; j = 1 expires the pick. Discriminating: rev 5's hourly design gives 911/24 and 839/24 (37 + 23/24 and 34 + 23/24), so the one-hour visibility delay is gone. Rev 5's pre-signed certificate counts reproduce: **1,632** (trend read) and **912** (volatility read), confirming S-3 and A-3.

## 1. Disposition of re-check 4 findings

Overlaps: S-3 = A-3 (certificate count); S-2 ≈ A-1 (late or recovered publication against a pre-signed certificate). S-1, S-4, A-2, A-4 and A-5 are single-reviewer.

| ID | Disposition | Evidence | Where |
|---|---|---|---|
| **S-2** (BLOCKER, late marker) | **Superseded by simplification; gone by construction.** There is no marker and no staging. The release is one insert whose `visible_from` must be later than the store's clock when it commits; the store refuses any other. A late commit is therefore impossible, and the certificate's `cooling_off_start` is the same value as `visible_from`. | rev 5 l.36-42 | §3 P-7; T-2 |
| **A-1** (BLOCKER, crash after staging) | **Superseded by simplification; gone by construction.** Nothing is staged. A crash leaves either a committed row (it becomes visible at its time, correctly) or no row (the next attempt signs a fresh certificate for its own time). A certificate counts only if a committed release entry with the same time references it. | rev 5 l.39; rev 4 l.67 | §3 P-7; T-5 |
| **S-3 / A-3** (count of pre-signed certificates) | **Accepted, then moot.** The counts 1,632 / 912 are right (§0). Pre-signing is dropped: one certificate is signed per release attempt, normally exactly one per PASS. | rev 5 l.42 | §3 |
| **S-1** (BLOCKER, Q1 / Q2a exceed §7) | **Accepted on the premise, corrected on the remedy.** Sol is right that protocol wording cannot authorize Q1's FAIL items or Q2a's label: §7 l.79 ranks above the protocol (§3 l.41), and C2's own precedence puts Constitution v1.1 first (DRAFT l.55-56). But **no separate Constitution amendment is needed**: the signed C2 is itself the §4 amendment that makes Constitution v1.1. Either option needs an **explicit row in C2's Constitution table (DRAFT §1) changing §7 l.79**, not protocol text. Costs per option are in §2 and Q1/Q2a. Inherited tension found in the sweep: D12-30. | §3 l.41; §4 l.48; DRAFT l.1, l.43-44, l.55-56, l.75-92, l.406 | §2, Q1, Q2a |
| **S-4** (status fixed at revision) | **Accepted.** The l.245 wording now fixes status at the event, and says no certificate can become effective afterwards. | rev 5 l.49 | §3 P-6 |
| **A-2** (BLOCKER, cap relabels finished results) | **Accepted.** Expiry now applies only to a result or an owner decision still pending at day 255. Results already finished keep their outcome, as O-2 requires (O1_O7 l.43: "no promotion for any nominee not yet processed"). | rev 5 l.48; O1_O7 l.43 | §3 P-6 |
| **A-4** (stale T-2) | **Accepted, rewritten.** All timing tests are replaced (T-1..T-6, §5) and state their fault assumptions. | rev 4 l.122 | §5 |
| **A-5** (disclosure wording, Q3, Q2a) | **Accepted.** Permitted disclosures and fault residuals are now separate lists (§4). The faulty-signer channel is listed. Q6 says plainly what a delay can reveal. Q3 now reads "exempting technical failures from the descendant bar would show…". Q2a's recommendation now reads "if you want the label to distinguish technical breakdowns". | rev 5 l.52, l.76, l.66, l.90 | §4, Q2a, Q3, Q6 |

Totals: 9 findings, 2 overlap pairs. All accepted in substance. S-2 and A-1 are removed by the simpler design, not patched. On S-1, Sol's remedy ("a formal Constitution amendment") is narrowed to "a row in the C2 amendment's Constitution table", with evidence. No reviewer claim was found contrary to the frozen text.

## 2. Can C2 change Constitution §7? (answer to S-1)

**Yes, if the change is written as a Constitution row.** C2 is a Constitution §4 amendment, not only a protocol amendment (DRAFT l.1, l.43-44). It already changes §5, §7 (a new line after l.81), §7a, §9 and §27 (DRAFT l.75-92). §4 l.48 sets one procedure for every amendment, and C2 follows it (version bump, owner-signed commit, cycle end, activation before the new cycle; DRAFT l.406). So the same signed commit can amend §7 l.79. What it **cannot** do is grant the exception in protocol text (§2) alone: a protocol clause cannot override the Constitution (§3 l.41; DRAFT l.55-56).

**Exact cost, by option:**
- **Q1 "PASS/FAIL only" and Q2a "plain FAIL":** no §7 row needed for these. But Q2a "plain FAIL" must edit the existing §5 l.63 row (DRAFT l.82) to drop "or its lockbox read failed technically".
- **Q2a "allow the label":** one added row: §7 l.79 becomes "Research receives PASS/FAIL only, except that the cycle outcome of §5 may show that a family had no result because its lockbox read failed technically." Because Constitution v1.1 outlives C2, this exception applies to **every later cycle** until amended again.
- **Q1 "show the three items on a FAIL":** one added row, worded for C2 only so it does not outlive the cycle: "In cycle C2 only, research also receives, for a FAIL, the three attestation fields, each as its value or 'unavailable'." Protocol l.76 (`PASS_FAIL_ONLY`) must also change in C2's protocol text.
- **Common to both:** the added rows go through C2's existing R19-2 re-review of the final wording (DRAFT l.400-403). No extra signature, no extra activation delay (C2 is already safety-relevant under O-5 with the 72-hour delay), no separate amendment.
- **Recommended in any case (D12-31):** add one clarifying sentence to the same §7 row: "A lockbox result is the outcome of a read. Facts fixed before any lockbox byte is read (a pre-read rejection and its reason, a barred descendant) and the publication time are not lockbox results." Without it, Q2b and the `BARRED_DESCENDANT` record rest on a reading of l.79 rather than its text.

## 3. The proposal in full (every binding is proposed C2 wording; none is active)

**Fields (rev 1-2, unchanged).** `T_L` is the float64 L-2 statistic (`difference_series_sharpe.scaled` on the lockbox E-DIFF series, D-11 Route A).
- `paired_delta_sharpe_sign`: from the same `T_L` that decides L-2. `positive` iff `T_L > 0.0`; `zero` iff `T_L == 0.0` (including −0.0); `negative` iff `T_L < 0.0`.
- `prediction_decay_test_passed`: L-1, `T_L ≥ q`. `drawdown_constraint_held`: L-3. ETH (L-4) has no field.
- **Lemma.** PASS ⇔ L-1 ∧ L-2 ∧ L-3 ∧ L-4, all available, so on a PASS the three fields always read (`positive`, `true`, `true`) and add nothing (D12-1). The converse is false: ETH can fail.

**P-1 PASS-only attestation.** An attestation exists only for a PASS. No attestation or field record is made for any other outcome.

**P-2 Value contract.** The fields come only from a finite, available `T_L` and L-1..L-3. Before a read is marked PASS, the worker checks all of L-1..L-4 and the field values. The signer checks them again at release. Any mismatch is a post-read technical FAIL.

**P-3 Descendants.** Every outcome released as FAIL is a `LOCKBOX_FAIL` for §7 l.85 and protocol l.296, including a technical FAIL. A pre-read rejection is not a read and is not a `LOCKBOX_FAIL`. Lineage is fixed at sealing. A barred nominee gets `BARRED_DESCENDANT` and no read. Its record is published no earlier than its ancestor's release.

**P-4 Upside record (sealed only).** The sealed prediction artifact also stores the 2,000 sorted replicates. The pre-read check confirms 2,000 finite ascending values, and that D-11's type-7 function returns the sealed q at p = 1/20. The sealed bundle then holds `upside = {status: COMPUTED | NOT_COMPUTED, k, exceeds_p95, reason}`, computed only for a finite `T_L` (p = 19/20 on the same vector, an AI default). It is not a gate and is never shown to research.

**Actors (needs Q6 i).** The *worker* (`lockbox_eval`) reads, computes, writes the sealed store and marks the read finished. It never writes the index. The *publisher* writes index entries and reads only state and commitments, never lockbox bytes. The *signer* (`lockbox_eval`'s signing key) signs attestations. The *store* is append-only (§26) and checks every time rule against its own clock.

**Order of one read.**
1. Pre-read check (D-11 item 3 and the P-4 vector check). On failure, a pre-read rejection (content per Q2b), and stop.
2. Before any lockbox byte is opened, the publisher durably writes the evaluation ID, the budget decrement, EXPOSED, the release time `R_0` = read start + 7 days, the worker deadline `D_w = R_0 − 12 h`, a default failure bundle, and the pre-read index entry. The store computes and holds every commitment, `SHA-256(nonce ‖ bundle)`, with a 256-bit nonce that never leaves the store. If any of this fails, there is no read.
3. The worker reads and computes twice; matching twice checks determinism only. It captures all input hashes, the code commit, the image, seeds and streams.
4. The worker writes the sealed bundle; the store computes its commitment.
5. The worker records the read as finished, with result PASS or FAIL, only while the store clock is before `D_w`. After `D_w` the result is fixed: a finished read keeps its result, and an unfinished one is a technical FAIL with the default commitment. Late worker output is void, logged sealed, never published.

**P-7 Release (replaces rev 3-5 slots, staging, markers and pre-signing).** [Release cadence, the 6-hour window and the 12-hour deadline are AI defaults.]
- Release times are `R_j = R_0 + j days` (one fixed time per day). Normally j = 0.
- In the window `[R_j − 6 h, R_j)` the publisher first checks that the signer is reachable, **for every outcome**. Then:
  - **FAIL (any kind):** it inserts the release entry, with the commitment the store holds.
  - **PASS:** it asks the signer for the attestation with `cooling_off_start = R_j`. The signer signs only if the read is finished as PASS, P-2 holds, `R_j` is in the future, `R_j` is not after day 255, and no release entry exists for this evaluation. The publisher then inserts the release entry referencing it.
- **The insert is the release.** It is one atomic row with `visible_from = R_j`. The store refuses it unless its own clock is before `R_j`, and accepts at most one release entry per evaluation (or per pair under R-b). Readers see a row only from its `visible_from`, by store clock.
- **Missed release:** if no row is committed before `R_j`, the release moves to `R_{j+1}`, with a fresh signature for `R_{j+1}`, and a §26 incident is logged. The result was fixed at `D_w`, so a miss can never change it.
- **A certificate is effective only if a committed release entry with `visible_from` equal to its `cooling_off_start` references it.** Any other signature is void forever.
- After day 255 no certificate is signed. A result first released after the cap shows PASS or FAIL and nothing more (see P-6).

**P-5 Cooling-off.** The attestation's `cooling_off_start` equals `R_j`, the exact moment the result became visible. No owner decision is accepted before `R_j + 72 h` (protocol l.300).

**P-6 Cap and revision (replaces DRAFT l.244-245).** "Attested" means a valid PASS attestation is visible.
- *l.244:* "At day 255 processing ends. A nominee whose lockbox result is not yet visible, or whose owner decision is not yet recorded, expires unpromoted, recorded with cause U_ops (Annex A P18-7). An outcome completed earlier is kept: a visible FAIL stays a FAIL, a pre-read rejection stays a rejection, a barred descendant stays barred. A nominee is promoted only if it is attested and the owner's decision is recorded after its full cooling-off and by day 255."
- *l.245:* "A revision or invalidation fixes every nominee's status at the moment it happens. It ends processing of every nominee not attested at that moment. An attested nominee is unaffected: 'open promotion' in Constitution §4 l.48 means attested in this sense. An entry already committed but not yet visible then still shows its result, but its attestation is void. No signature that is not effective at that moment can become effective later."

**P-8 Validation.** The publisher publishes only (a) PASS or FAIL from the finished record and (b) on PASS, the attestation, after checking its signature and that every field equals the step-2 values, `R_j` and (`positive`, `true`, `true`). Any mismatch publishes FAIL with the default commitment, in the same row shape. D-20 picks a deterministic signature scheme with no embedded time.

**Records.**
- *Pre-read entry* (step 2): evaluation ID, family, nominee ID, prediction-artifact hash, `R_0`, EXPOSED, and the audit ID under R-b.
- *Release entry:* evaluation ID, `result ∈ {PASS, FAIL}`, `visible_from`, commitment, `attestation_ref` (PASS only). Every kind of FAIL has the same shape.
- *Sealed bundle* (`lockbox_eval` only): `T_L`, q, both MDDs, ETH E-IMPROV and drawdown, each condition, availability reasons, cause class, actual times, upside record, capture hashes.

**Reproduction (Q4).**
- *R-a:* capture everything. Re-run after the segment rolls into confirmation (§7 l.81); a mismatch voids the promotion (§27 l.194).
- *R-b:* a concurrent counted audit. It needs (i) two evaluations per family (primary plus audit; DRAFT l.221-222 says 1) and (ii) no 30-day cooldown between a primary and its own audit. One pair record: both reads are fixed at step 2 and both run unconditionally. One signature is allowed only if both finished with identical scientific bytes and PASS. A missing, late or disagreeing run means FAIL for both. Both entries go out in one insert with the same result. The calendar is the same as R-a's (§0).

**Why the timing goal holds.** Both kinds of FAIL take the identical publisher path: the same signer check, one insert, no signing. Their result is fixed at `D_w`, before the window opens. `visible_from` is the scheduled `R_j`, so commit timing is never visible. A move to the next day depends only on publisher, signer or store uptime, which never reads lockbox data.

## 4. Disclosure: what research can learn

Working rule: whatever the owner sees counts as research-visible, because he works with the research AI.

**Permitted (written into C2):**
1. PASS or FAIL per read.
2. The cycle-label fact, if Q2a allows it (needs the §7 row, §2).
3. The three FAIL items, if Q1's alternative is chosen (needs the §7 row and l.76).
4. The pre-read rejection and, per Q2b, its reason. These are fixed before any lockbox byte is read.
5. The release time and day index j. They depend only on outages.

**Residual channels (faults and trusted parts), disclosed, not claimed away:**
- **R1 signing fault.** A fault in the signer *after* the reachability check affects only a PASS. It can delay a PASS by one day, and an incident visible before the delayed release would hint "PASS" up to a day early. It cannot separate technical from performance FAIL. That is the timing residual the owner accepted.
- **R2 faulty signer.** A deliberately faulty signer could hide bits in a signature. A deterministic scheme and publisher checks narrow this; they do not remove it.
- **R3 trusted store.** The store's clock, its refusal of late inserts and its `visible_from` filter are trusted. If they are bypassed, commit times leak. They are covered by §16 review of the lockbox access tooling.
- **R4 owner judgment.** The owner's decision on one family may reflect the other family's result (D12-7). That is allowed and disclosed.

## 5. D-20 checklist (complete; replaces all earlier lists)

- **D-11 items** (`OWNER_DECISION_D11.md` l.26): nominee artifact identity and verified retrieval path; confirmation baseline start state; lockbox seed source and stream identity; m≠n index generator; ψ reference vectors; the R-8 `max_drawdown` extension.
- **Signing:** attestation writer, key, deterministic timeless scheme, the signer's release-time guard (P-7), and the effectiveness rule.
- **Contracts:** P-1, P-2, the sign function and its float rule, P-3 (lineage at sealing, `BARRED_DESCENDANT`, publication after the ancestor), P-4.
- **Order:** steps 1-5, `D_w`, P-7, P-8. Under R-b, the pair record and bindings (i)-(ii).
- **Records:** the pre-read and release entry shapes, the sealed-bundle schema, the store-held nonce and commitments, and the pre-read reason codes per Q2b.
- **Timing tests:**
  - **T-1** no release row is readable before its `visible_from`, by any reader path.
  - **T-2** the store refuses an insert at or after `R_j`, and a second release entry for the same evaluation.
  - **T-3** with no fault, PASS, performance FAIL, crash FAIL, deadline FAIL, P-8 mismatch FAIL and (R-b) disagreement FAIL all publish at `R_0`, and all FAIL classes run the identical publisher calls.
  - **T-4** an injected publisher, store or signer outage over `R_j` moves every outcome class to `R_{j+1}` alike.
  - **T-5** a crash before the insert leaves no row; a crash after it leaves the row; a certificate for a missed time is never accepted later, including across day 255.
  - **T-6** the cap and a revision keep completed outcomes and fix status at the event (P-6).
- **Review:** §16 review of the lockbox access tooling and the promotion gate.
- **Not a D-20 item:** the publishing permission. It comes only from Q6 (i).

## 6. Owner questions (final; replace all earlier ones)

Choosing "keep blocked" on Q1-Q4 or Q6 means C2 cannot be signed yet. Q5 can be deferred. Every recommendation assumes C2 goes ahead at all; "keep blocked" everywhere, and `NO_EDGE_FOUND`, remain valid outcomes.

**Q1. What does a lockbox result tell you?**
- **"PASS or FAIL only (Recommended)."** The three items appear only on a PASS certificate, where they always read "positive / yes / yes". On a FAIL you learn nothing about which test failed. No Constitution change is needed.
- **"Also show me the three items on a FAIL."** Each item shows its value or "unavailable" (a crash shows all three "unavailable"). This is a partial diagnosis, with no ETH item and no reason. Research learns it too, because you work with the research AI. "Unavailable" reveals a technical breakdown on every read, so Q2a's plain-FAIL choice could no longer hide that. Cost: a C2-only row changing Constitution §7 l.79 plus a change to protocol l.76.
- **"Keep blocked."**

**Q2a. At the end of a cycle, may the label show that a FAIL was a technical breakdown?** This matters only when the other family has no result either. "Technical" includes failures caused by the data (for example zero variance), so this one fact can say something about the lockbox data.
- **"Allow it, stated openly (Recommended, if you want the label to distinguish technical breakdowns)."** At most one data-linked fact per cycle. Cost: a row changing Constitution §7 l.79 that also applies to every later cycle.
- **"Count a technical breakdown as a plain FAIL."** This removes the extra cycle-label disclosure (Q1's alternative, if chosen, still discloses its own items). Cost: a broken run can end the cycle as `NO_EDGE_FOUND` and open the baseline path, and the C2 row rewriting Constitution §5 l.63 changes.
- **"Keep blocked."** Note that C2 as drafted already contains the label at Constitution level, so one of the first two rows must change before signing either way.

**Q2b. If a pick is stopped before any lockbox data is read, may the record show the reason?** The reason is fixed before any lockbox byte is touched.
- **"Show the reason (Recommended)."** It helps you fix the cause and reveals nothing about lockbox results.
- **"Show only 'stopped before reading'."** Slightly more closed, and less to act on. That no read happened is visible either way.
- **"Keep blocked."**

**Q3. If one family's pick is built on the other's, and the earlier one's result is FAIL, what happens?**
- **"The later pick is not read, and any FAIL counts, including a technical breakdown (Recommended)."** This applies the frozen no-descendant rule. Cost: a crash in the first read can stop the second pick. Exempting technical failures from the descendant bar would show research which kind of FAIL happened.
- **"Do not allow related picks at all."** A new C2 eligibility rule; the bar never arises.
- **"Keep blocked."**

**Q4. How is the lockbox result checked for reproducibility?**
- **"Record everything; re-run later once the period becomes confirmation data (Recommended)."** No extra lockbox read. Cost: a later mismatch voids an already approved promotion.
- **"A second, counted audit read at the same time as the first."** Both runs must finish and agree before any certificate is signed, otherwise both FAIL. No extra days. Cost: C2 must allow two reads per family and waive the 30-day wait between a read and its own audit (an exception to a frozen anti-probing rule). Every read counts, a disagreement can cost a good pick, there is more to review, and it needs Q6's permission.
- **"Keep blocked."**

**Q5. May anyone open the sealed details (the margin, the drawdowns) later?**
- **"No, sealed and machine-checked only (Recommended)."** They are not secret forever: prices are public, and the period becomes confirmation data.
- **"I may open them after C2 ends."** That reaches research through you, so it needs explicit wording.
- **"Decide later."** They stay sealed; C2 is not blocked.

**Q6. Who posts lockbox results, and what happens when posting is late?** Results appear once a day at a fixed time, fixed before the data is read. Your 72 hours start exactly when you can see the result. If an outage stops a posting, it moves to the same time next day and is logged as an incident. Such a move cannot tell anyone whether a FAIL was technical or performance. A rare fault in the signing step can delay only a PASS by one day, which could hint early that it is a PASS. A deliberately faulty signer could still hide information in its signature; the checks reduce but do not remove that.
- *Part (i), who posts.* The frozen threat model lets the lockbox job only read and sign (l.9), so posting needs a change to that frozen document inside the signed C2, plus §16 review of the code.
  - **"A separate posting job that cannot read lockbox data (Recommended)."** It reduces the risk of accidental disclosure. Cost: one more identity and key to set up and review.
  - **"Let the lockbox job also post fixed-format results."** Simpler, but the job that read the data also writes what research sees.
  - **"Keep blocked."** No lockbox read can be published, so C2 cannot run.
- *Part (ii), the day-255 cap.*
  - **"A pick must be visible, cooled off for 72 hours and decided by you by day 255; results already finished keep their outcome (Recommended)."** This keeps your 255-day limit (O-2). Cost: if the lockbox stage is reached late (about day 35 after the look) or posting slips by days near the cap, a good PASS can expire unpromoted. Slack is 35 − g − j days.
  - **"Allow your decision after day 255 if the result was visible by day 255."** Fewer lost passes, but it changes your decision O-2 and needs its own deadline.
  - **"Keep blocked."**

## 7. What changed since rev 5, and why

1. **Publication rebuilt, not patched** (owner direction; S-2, A-1, S-3, A-3). Hourly slots, staging, batch markers and per-slot pre-signing are gone. Now there is one release time per day, one atomic insert committed before it, a store that refuses late inserts, and one certificate signed for the attempted time. The two blockers cannot arise.
2. **Cooling-off is exactly visibility.** `cooling_off_start = R_j = visible_from`. The one-hour Δ is gone, so the bounds become whole numbers: 38 and 35 (with j missed days, g + j ≤ 38 and g + j ≤ 35).
3. **Constitution route stated** (S-1). Q1's alternative and Q2a's "allow" each need a row in C2's Constitution table; no separate amendment. The existing §5 row conflicts with §7 as drafted (D12-30).
4. **Cap keeps finished results** (A-2); **status fixed at a revision** (S-4).
5. **Disclosure split** into permitted items and fault residuals (A-5). The wording of Q2a, Q3 and Q6 is fixed.
6. **Tests rewritten** with stated fault assumptions (A-4).
7. **Consolidated:** one self-contained file; the earlier revisions are history only.

## 8. Findings (numbering continues rev 5)

- **D12-28 NON-BLOCKING.** Simplified P-7 release; removes S-2 and A-1 by construction and makes S-3/A-3 moot.
- **D12-29 QUESTION (Q1, Q2a).** §7 l.79 exceptions need explicit C2 Constitution rows; C2 can carry them (§2).
- **D12-30 NON-BLOCKING (inherited; owner wording item).** DRAFT l.82 already puts "lockbox read failed technically" into Constitution v1.1 §5 with no matching §7 exception. It was inherited from the C2 draft's O-4 fold-in and carried by D-12 revisions 2-5, which treated l.82 as protocol-level. Whichever Q2a option is chosen, one row must change before signing. Proposal only; not edited.
- **D12-31 QUESTION.** Whether §7 l.79 covers non-read facts (pre-read reason, barred descendant, release time). Recommended: the clarifying sentence in §2.
- **D12-32 NON-BLOCKING.** P-6 cap and revision wording (A-2, S-4).
- **D12-33 NON-BLOCKING.** Disclosure split and residuals R1-R4 (A-5).

Earlier findings D12-1..D12-27 stand as resolved or as owner questions, now carried in §3-§6. Those superseded by this rebuild are D12-12, D12-13, D12-21, D12-23 and D12-25 (release envelope, publication fencing, visibility barrier, slots, pre-signing). Their goals are kept by P-7.

**Remaining:** the R19-2 re-check of this revision; owner Q1-Q6; then the owner-authored, signed C2 with the D-12 rows (Constitution §5/§7 rows per Q1/Q2a, protocol P-1..P-8, THREAT_MODEL l.9 per Q6 i); D-20; §16 review.
**Still unauthorized:** frozen edits, activation, code, simulation, confirmation or lockbox access, promotion and trading.
