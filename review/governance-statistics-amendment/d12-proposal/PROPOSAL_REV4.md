# D-12 decision proposal, revision 4 (delta on revision 3)

**Reviewer model (observed):** Claude Fable 5.1, model ID `claude-fable-5-1`, per this session's metadata. I am an AI reviewer, not an authority.

**What it revises:** `PROPOSAL_REV3.md` (reviewed at `0b18a41`). It answers `SOL_REREVIEW2_0B18A41.md` (gpt-6-sol, FIX, D12R3-S-1..4) and `ASTRA_REREVIEW2_0B18A41.md` (gpt-6-astra, FIX, D12R3-A-1..4, reviewed at `04c9cf1`). I read both in full.

**How to read it:** a delta. Every rev 3 section not restated below stands (and through it, rev 2). Restated sections replace rev 3's in full. §8'' replaces all owner questions.

**Checkout and mode:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch freeze-sheet, HEAD `d42fb67`. The agent wrote only this one new file, at the caller's instruction. Nothing was staged or committed. No frozen file, hash or sidecar was touched. No simulation; no confirmation, lockbox, network or credential access.

**Status: INACTIVE PROPOSAL.** It needs an owner decision on Q1-Q6 and then the owner's signed C2 §4 amendment (which here must also amend the frozen threat model) before it binds anything. Nothing frozen changed.
**Review status:** revision 4 is unreviewed. R19-2 requires a focused re-check by two model families before the owner decides.
**VERDICT: `AMENDMENT_REQUIRED`** (unchanged).

## 0. Verification run

- **Citations re-read:** protocol l.67-95 (l.74 value 2, l.75 cooldown 30, l.76 PASS_FAIL_ONLY, l.89 upside logged), l.294-300 (l.296 no descendant retry, l.300 `cooling_off_hours: 72`); Constitution §3 l.41 and l.45, §4 l.47-52, §16 l.146-152, §26 l.191, §27 l.194; `THREAT_MODEL_v1.md` l.9; `schemas/attestation.schema.json` (`cooling_off_start` required, l.15); DRAFT l.217-245.
- **Bytes:** `THREAT_MODEL_v1.md` SHA-256 `8817a315…2745d4e`, equal to its sidecar (re-run at `d42fb67`).
- **Exact arithmetic (`fractions.Fraction`, days):** with the visibility barrier of §3'' (Δ = 1 h = 1/24 day), the R-a/R-b concurrent calendar has its last scheduled visibility at 217 + g + 1/24. Visible by day 255: g ≤ 37. Cooling-off also ended by day 255: g ≤ 34 (rev 3, without Δ: 35). Discriminating check: dropping Δ gives 35, so the hour matters at the boundary.

## 1. Disposition of re-check 2 findings

Overlaps: S-2 ≈ A-1 (R-b joint decision); S-1 ≈ A-4 (deadline and late publication); S-4 ≈ A-3 (Q2 split); A-2 single-reviewer; S-3 against Astra's closing note on authority.

| ID | Disposition | Evidence | Repaired in |
|---|---|---|---|
| S-2 / A-1 | **Accepted.** Rev 3 kept one state record per evaluation, so a primary could be signed and `READY` while its audit was still `OPEN`, and the two entries could be published with different results. | rev 3 l.72, l.78-80, l.94-97 | §6'' R-b |
| S-1 / A-4 | **Accepted.** Rev 3 said the worker's CAS "must land before `T_r`" but guarded it only on `OPEN`; a late publisher let a late PASS in. And `cooling_off_start := T_r` lets a publisher outage eat the owner's 72 hours, which runs against the spirit of §4 l.52 (no capital-increase cooling-off below 72 h; whether promotion is covered there is a reading, not verified). | rev 3 l.55, l.78-82; protocol l.300; §4 l.52; DRAFT l.244 | §3'', §6'', Q6 |
| A-2 | **Accepted; rev 3's claim was wrong.** "Both branches do the same work" was false: the crash path did `OPEN → CLOSED` before the append, an extra durable write before visibility. Equal field shapes and `released_at = T_r` do not hide when an entry appears. | rev 3 l.79-81 | §3'' barrier, §6'', §9'' T-1..T-3 |
| S-4 / A-3 | **Accepted.** Q2's second option disposed only of the cycle-label bit. The two disclosures are independent (one is data-linked, one is not), so they are now two questions. | rev 3 l.119-122 | Q2a, Q2b |
| S-3 | **Accepted; Astra's venue view rejected.** Astra (closing note) said the publisher "introduces no additional reader" (true) and that its permission "remains an explicit D-20/§16 condition". But D-20/§16 cannot grant it: THREAT_MODEL l.9 says "lockbox read + attestation signing only", and writing a research-visible index is neither. The threat model ranks above the protocol (§3 l.41), so a C2 protocol clause cannot override it either. Changing it is a §4 amendment of a frozen document (§3 l.45). §16 l.152 ("lockbox ACL tooling") is a merge-review duty for code that *implements* permissions, not a source of them. Rev 3 §9' l.147 was wrong on the same point. | THREAT_MODEL l.9; §3 l.41, l.45; §4; §16 l.152 | §6'' actors, Q6 |
| S-3 placement | **Partly rejected.** Sol asked to put the permission cost in Q4. A publisher is needed under R-a too, so the cost goes in a new Q6, and Q4 points to it. | rev 3 §6' (publisher in both R-a and R-b) | Q4, Q6 |

**Self-findings.** D12-18: rev 3's step 2 also had `lockbox_eval` writing the pre-read entry to the index, a second unpermitted write that S-3 did not name; now covered (§6''). D12-19: rev 3's R-b schedule bound (g ≤ 38/35) ignored publication latency; restated in §0.

Totals: 8 findings, of which 4 overlap pairs; all accepted in substance; one placement rejected; one reviewer's view (Astra on venue) rejected with evidence. Earlier findings that both reviewers marked resolved are not reopened.

## 3''. Who sees what, and when (replaces rev 3 §3')

**Working rule (unchanged):** whatever the owner sees counts as research-visible.

**Index entries [AI default; D-20 implements].** Pre-read entry: unchanged from rev 3 (written before any lockbox byte), but written by the publisher identity (§6''). Release entry: evaluation ID; `result ∈ {PASS, FAIL}`; `released_at = T_r`; `commitment` (32 bytes); `attestation_ref` (PASS only). Same shape for every outcome, as in rev 3.

**Visibility barrier (new).** Release entries are written *staged*, unreadable. At the scheduled visibility time `V_s = T_r + Δ` (Δ = 1 h [AI default]) the publisher makes all entries due at that `T_r` readable in one atomic append, a *batch marker* carrying `published_at` (the actual time). Nothing is readable before its batch marker. If staging is unfinished at `V_s`, the marker waits; it is never partial. Staging time can then differ between outcomes without being observable, unless staging overruns Δ, which only a publisher outage does.

**Certificate time and cooling-off (replaces rev 3's timestamp bullet).**
- The attestation's `cooling_off_start := V_s`, fixed at step 2; a deterministic, timeless signature scheme (unchanged).
- **P-5 [proposed C2 binding]:** "The 72-hour cooling-off of protocol l.300 ends at `max(V_s, published_at) + 72 h`. No owner decision is accepted earlier." Measuring from actual visibility gives the owner a full 72 hours of sight. `published_at` depends only on the publisher's uptime, not on the result, so publishing it leaks nothing about the lockbox.
- **P-6 [proposed C2 reading of DRAFT l.244]:** "A nominee is attested for the day-255 cap only when its owner decision is recorded after its full cooling-off and by day 255." Cost: a publisher outage near the cap can expire a PASS with no promotion (`U_ops`). Slack is 34 − g days (§0). Voiding a late-published read was considered and rejected: C2 allows one read per family with no replacement (DRAFT l.222), so voiding destroys the read for no disclosure gain.
- Under Q3's no-descendant rule a descendant's read also waits until its ancestor's result is visible; an outage can delay it.

**Disclosure bound (unchanged in substance):** (i) PASS/FAIL per read; (ii) the cycle-label bit if Q2a allows it; (iii) the FAIL items if Q1's alternative is chosen. Pre-read rejections, publication delays and `published_at` are independent of the lockbox data.

## 6''. Accounting, publication, recovery (replaces rev 3 §6' steps and actors; R-b schedule arithmetic stands)

**Actors (needs Q6).** The *worker* (`lockbox_eval`) reads the lockbox, computes, writes the sealed store and requests a signature. It never writes the index. The *publisher* writes the step-2 accounting, the pre-read entries, staged release entries and batch markers. It reads only the state table and commitments, never lockbox bytes or sealed bundles. Recommended: the publisher is a **separate identity** (Q6). Either way a §4 amendment to THREAT_MODEL l.9 is needed.

**Store-enforced deadline.** `D_w = T_r − 1 h` [AI default]. The append-only store (§26) evaluates every guard against its own commit clock, not the worker's.

**States:** `OPEN → READY` (worker, guarded) and `OPEN | READY → RELEASED` (publisher). Rev 3's `CLOSED` state is removed; the deadline guard does its job.

1. Pre-read verification (unchanged). On failure: a pre-read rejection (disclosure governed by Q2b), and stop.
2. Publisher durably writes the evaluation ID, budget decrement, EXPOSED, `T_r = read start + 7 days`, `V_s`, state `OPEN`, the default failure bundle and its commitment, and the pre-read entry. Only then is the read grant issued. If anything fails, there is no read.
3-4. Worker reads, computes twice (determinism check), writes the sealed bundle and commitment (unchanged).
5. Signing service signs only if `state = OPEN` and `store_time < D_w`, and, under R-b, only on the pair condition below.
6. Worker CAS `OPEN → READY` succeeds only if `state = OPEN` **and** `store_time < D_w`. A refused CAS voids the worker's outputs. They are logged sealed and never published. A signature not referenced by a `READY` record is void.
7. Publisher, at or after `T_r`, in **one atomic transaction per evaluation (or pair):** read the state. From `READY`, stage the worker's result and commitment. From `OPEN`, which can only mean the deadline was missed, stage `FAIL` with the default commitment (post-read technical failure, never retried). In both cases set `RELEASED`. Every path is the same single transaction; the barrier (§3'') makes visibility identical.
8. Recovery: a crashed transaction either committed or did not. On restart, repeat step 7; at most one staged entry per evaluation ID. The batch marker follows when all due entries are staged. Delay beyond `V_s` is a §26 incident, and P-5/P-6 govern its effect.

**R-b pair transaction (replaces rev 3's "R-b rules"; schedule, bindings (i)-(ii) and cost stand).**
- One **pair record** (pair ID, primary ID, audit ID) is the only state machine; neither evaluation has its own. Step 2 writes both IDs, two budget decrements, both EXPOSED marks, one `T_r`/`V_s`, both default failure bundles and both pre-read entries, in one write. Both reads are fixed before any byte and both run unconditionally.
- **Before signing:** both runs have completed and both bundles and commitments are recorded, and their scientific bytes are equal. Only then, and only if L-1..L-4 PASS and P-2 holds, is **one** signature requested, carrying the primary's `lockbox_evaluation_id`. The signing service checks this pair condition itself.
- Pair `OPEN → READY` (deadline-guarded) carries both commitments and one result. Matching runs that agree on FAIL give `READY` with FAIL. Disagreeing runs give `READY` with FAIL, cause sealed.
- **Missing, late, crashed or unavailable audit (or primary):** the pair is still `OPEN` at `D_w`, so the terminal result is FAIL with both default commitments.
- **Publication:** one transaction stages **both** entries with the **same** result, sets the pair `RELEASED`, and one batch marker shows both. On PASS both entries carry the same `attestation_ref` (one certificate). A partially published PASS cannot arise: both entries are staged or neither is, and no signature exists without the pair condition.
- Any pair FAIL is a `LOCKBOX_FAIL` under P-3, for both evaluations.

## 8''. Owner questions (replace rev 3 Q1-Q5)

Choosing "keep blocked" on Q1-Q4 or Q6 means C2 cannot be signed yet. Q5 can be deferred without blocking.

**Q1. What does a lockbox result tell you?**
- **"PASS or FAIL only (Recommended)."** The three items appear only on a PASS certificate, where they always read "positive / yes / yes". On a FAIL you learn nothing about which test failed.
- **"Also show me the three items on a FAIL."** Each item shows its value, or "unavailable" if it could not be computed (a crash shows all three "unavailable"). You get a partial diagnosis, but no ETH item and no reason. Because you work with the research AI, research learns it too. And "unavailable" reveals a technical breakdown on every read, so Q2a's "plain FAIL" choice can no longer hide that. It needs explicit C2 disclosure wording.
- **"Keep blocked."**

**Q2a. At the end of a cycle, may the label show that a FAIL was a technical breakdown?** This arises only when the other family has no result. "Technical" includes failures caused by the data itself, such as a zero-variance or non-numeric result, so this one fact can say something about the lockbox data.
- **"Allow it, stated openly in C2 (Recommended, if you value an honest end label)."** At most one data-linked fact per cycle, written down rather than hidden.
- **"Count a technical breakdown as a plain FAIL."** Nothing leaks. Cost: a broken run can then end the cycle as `NO_EDGE_FOUND` and open the baseline path, and draft l.82 changes.
- **"Keep blocked."**

**Q2b. If a pick is stopped *before* any lockbox data is read (for example, its sealed prediction file fails its check), may the record show the reason?** The reason is fixed before any lockbox byte is touched, so it says nothing about the lockbox.
- **"Show the reason (Recommended)."** It helps you fix the cause. It reveals nothing about lockbox results.
- **"Show only 'stopped before reading', with no reason."** It is slightly more closed and gives you less to act on. The fact that no read happened is still visible either way.
- **"Keep blocked."**

**Q3. If one family's pick is built on the other's, and the earlier one's lockbox result is FAIL, what happens?**
- **"The later pick is not read, and any FAIL counts, including a technical breakdown (Recommended)."** This applies the frozen no-descendant rule, and C2 must say a technical FAIL counts. Cost: a crash in the first read can stop the second pick, even though nothing showed it was bad. The alternative would show research which kind of FAIL happened.
- **"Do not allow related picks at all."** A new C2 eligibility rule; the bar then never arises.
- **"Keep blocked."**

**Q4. How is the lockbox result checked for reproducibility?**
- **"Record everything; re-run later once the period becomes confirmation data (Recommended)."** It uses no extra lockbox read. Cost: if the later re-run does not match, an already approved promotion is voided.
- **"A second, counted audit read at the same time as the first."** Both runs must finish and agree before any certificate is signed. If the audit is missing, late or disagrees, both reads FAIL. It adds no days. Cost: C2 must allow two reads per family and waive the 30-day wait between a read and its own audit (an exception to a frozen anti-probing rule). Every read counts, a disagreement can cost a good pick its promotion, and there is more machinery to review. It also needs the same publishing permission as Q6.
- **"Keep blocked."**

**Q5. May anyone open the sealed details (the margin, the drawdowns) later?** Unchanged:
- **"No, sealed and machine-checked only (Recommended)."** The details are not secret forever: prices are public, and the period becomes confirmation data.
- **"I may open them after C2 ends."** That reaches research through you, so it needs explicit wording.
- **"Decide later."** They stay sealed until you decide. C2 is not blocked.

**Q6. Who posts lockbox results, and what if posting is late?** The frozen threat model lets the lockbox job only read and sign. Posting results needs a change to that frozen document, made inside the signed C2 amendment, with the extra review that permission-handling code gets. Under every option, a late posting starts your 72 hours when you can actually see the result. If that pushes your decision past day 255, the pick expires unpromoted.
- **"A separate posting job that cannot read lockbox data (Recommended)."** The job that sees the data can never write anything research reads, so it cannot leak by mistake. Cost: one more identity and key to set up and review.
- **"Let the lockbox job also post fixed-format results."** It is simpler, but the job that read the data can also write to what research sees.
- **"Keep blocked."** No lockbox read can be published, so C2 cannot run.

My recommendations are conditional: they assume C2 proceeds at all. "Keep blocked" everywhere remains a valid answer, and `NO_EDGE_FOUND` is a valid result.

## 9''. Additions to "what D-20 must bind" (rev 3 §9' stands, except its "unchecked" bullet, which is withdrawn)

- The store-enforced deadline guard on signing and on `→ READY`; the removal of `CLOSED`; the single publisher transaction; the visibility barrier and batch marker; P-5 and P-6; the R-b pair record.
- **Observable-timing requirements:** **T-1**: no release entry is readable before its batch marker. **T-2**: in synthetic tests, PASS, ordinary FAIL, crash FAIL, deadline-miss FAIL and (R-b) disagreement FAIL each have a batch marker at `V_s` when the publisher is up. **T-3**: one marker per `T_r`, covering every due entry, and never partial.
- The permission itself is **not** a D-20 item. It comes only from the Q6 threat-model amendment.

## 10''. New findings (numbering continues rev 3)

- **D12-18 NON-BLOCKING (self-finding).** Rev 3 had `lockbox_eval` writing pre-read entries too (§6'').
- **D12-19 NON-BLOCKING (self-finding).** Rev 3's schedule bound ignored publication latency (§0).
- **D12-20 QUESTION (Q6).** A threat-model amendment for the publisher; P-5 and P-6.
- **D12-21 NON-BLOCKING.** The visibility barrier and T-1..T-3 (A-2).
- **D12-22 NON-BLOCKING.** The R-b pair transaction (S-2/A-1).

**Remaining:** the R19-2 re-check of this revision; owner Q1-Q6; signed C2 §4 wording for P-1 to P-6, §3'', §5', §6'' and the THREAT_MODEL l.9 change; D-20; §16 review of the lockbox ACL tooling. **Still unauthorized:** frozen edits, activation, code, simulation, confirmation or lockbox access, promotion and trading.
