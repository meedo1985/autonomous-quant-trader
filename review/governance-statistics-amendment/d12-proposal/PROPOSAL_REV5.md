# D-12 decision proposal, revision 5 (delta on revision 4)

**Reviewer model (observed):** Claude Fable 5.1, model ID `claude-fable-5-1`, per this session's metadata. I am an AI reviewer, not an authority.

**What it revises:** `PROPOSAL_REV4.md` (reviewed at `df9e0d0`). It answers `SOL_REREVIEW3_DF9E0D0.md` (gpt-6-sol, FIX; verbatim labels `D12R4-U-n`, mapped by its header to **D12R4-S-1..5**, used here) and `ASTRA_REREVIEW3_DF9E0D0.md` (gpt-6-astra, FIX, D12R4-A-1..4). I read both in full.

**How to read it:** a delta. Every rev 4 section not restated stands (and through it rev 3 and rev 2). Restated sections replace rev 4's in full. §8''' replaces all owner questions. §11 at the end is a consolidated **current binding summary**; where it differs from any earlier revision, §11 wins.

**Checkout and mode:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch freeze-sheet, HEAD `5fa4f71`. The agent wrote only this one new file, at the caller's instruction (the agent definition in this worktree still lists `Write` as disallowed; the caller's scope was followed, as in rev 3). Nothing was staged or committed. No frozen file, hash or sidecar was touched. No simulation; no confirmation, lockbox, network or credential access.

**Status: INACTIVE PROPOSAL.** It needs an owner decision on Q1-Q6 and then the owner's signed C2 §4 amendment (which must also amend THREAT_MODEL l.9) before it binds anything. Nothing frozen changed.
**Review status:** revision 5 is unreviewed. R19-2 requires a focused re-check by two model families before the owner decides.
**VERDICT: `AMENDMENT_REQUIRED`** (unchanged).

## 0. Verification run

- **Citations re-read:** Constitution §4 l.48-52, §7 l.73-85 (l.79 PASS/FAIL only), §13 l.122-124 (l.124: the attestation binds "cooling-off start"); protocol l.67-95 (l.74, l.75, l.76, l.89), l.294-300; `THREAT_MODEL_v1.md` l.9; DRAFT l.221-222, l.241-245. **Line correction:** DRAFT l.244 is `calendar_cap_rule` and l.245 is `revision_or_invalidation_after_look` (the "open promotion" clause). Sol's "l.244" link points at the cap; both clauses use "attested".
- **Exact arithmetic (`fractions.Fraction`, days; reproduced):** last no-outage visibility = 217 + g + 1/24. Visible by day 255 iff g ≤ 911/24 = **37 + 23/24**; cooling-off also ended iff g ≤ 839/24 = **34 + 23/24**. Worked example: g = 34.5 ends cooling-off at 6109/24 = day 254 + 13/24 (inside the cap; rev 4's "g ≤ 34" wrongly excluded it). Discriminating: truncation gives 37/34 (rev 4's figures), dropping Δ gives 38/35; only the fractional form matches the rule. With k hourly slot delays (§3'''), slack = 839/24 − g − k/24; g = 30, k = 5 gives 19/4 days; g = 34, k = 23 gives exactly 0.

## 1. Disposition of re-check 3 findings

Overlaps: S-3 ≈ A-1 (recovery timing); S-4 ≈ A-2 (fractional bounds); S-1 ≈ A-4 (cooling-off start; stale checklist); S-5 ≈ A-3 (overstated assurances); S-2 single-reviewer.

| ID | Disposition | Evidence | Repaired in |
|---|---|---|---|
| S-3 / A-1 | **Accepted; rev 4's claim withdrawn.** Rev 4 l.44 ("only a publisher outage" overruns) and l.48 (`published_at` "leaks nothing") were false: after an outage the marker followed staging completion, so Astra's 1 ms vs 2 ms counterexample is valid, and Sol's in-hour overrun with the publisher up is not ruled out by T-2. **Adopted the parent's fixed-slot suggestion, improved:** the slot is computed by the store from the publisher's restart time *before* staging, and visibility is store-enforced at the slot, so staging duration no longer moves visibility at all. One residual remains (a staging fault that overruns its window while the publisher is up) and is disclosed, not claimed away. | rev 4 l.44, l.48, l.68, l.122; §7 l.79; protocol l.76 | §3''' P-7, §9''' T-4..T-6 |
| S-4 / A-2 | **Accepted.** Bounds are 37 + 23/24 and 34 + 23/24; slack is 34 d 23 h − g, shared between slot delay and the owner's response time. **g is not bound to whole days**: it is elapsed time from the nomination look to the first read. 37/34 are integer maxima only. | §0 | §0, §3''' P-6 |
| S-1 / A-4 | **Accepted; record the effective start (not a meaning change).** §13 l.124 binds the *cooling-off start*; rev 4 bound `V_s`, which differs from the effective start after a delay. Now `cooling_off_start := V_k`, the slot at which the result actually becomes visible. Because the signature is made before `k` is known, the worker pre-signs one attestation per candidate slot (§3'''). Sol's alternative (amend the field's meaning, gate on the marker) was rejected: it changes the meaning of a frozen Constitution field for no gain. Rev 3 l.142 (`:= T_r`) and rev 4 l.47 (`:= V_s`) are superseded. | §13 l.124; rev 3 l.142; rev 4 l.47 | §3''', §11 |
| S-2 | **Accepted.** Rev 4 P-6 made "attested" mean "decided", but the attestation is signed before publication, and DRAFT l.244/l.245 use "attested" for expiry and for the "open promotion" protection. Repair: **one** meaning, "attested = a valid PASS attestation is visible", used in both clauses; the decide-by-day-255 rule becomes an explicit extra condition in l.244, not a redefinition. Exact wording in P-6; disclosed in Q6 part (ii). | DRAFT l.244-245; §4 l.48; O-3 reading (a) (DRAFT l.431) | §3''' P-6, Q6 |
| S-5 / A-3 | **Accepted, extended.** Q2a now says "removes the additional cycle-label disclosure"; Q6 says separation "reduces accidental disclosure risk". Self-extension: the worker-supplied 32-byte commitment was itself a 256-bit channel. Now the sealed store computes it (P-8); the publisher validates every remaining worker value. A deliberately faulty signer could still hide bits in a signature nonce; this is disclosed. | rev 4 l.64, l.89, l.113 | P-8, Q2a, Q6 |

Totals: 9 findings, 4 overlap pairs; all accepted; one reviewer-offered alternative (S-1 meaning change) rejected with reason; no reviewer claim found contrary to frozen text.

## 3'''. Publication timing and cooling-off (replaces rev 4 §3'' "visibility barrier" and "certificate time" bullets; index shapes stand)

**P-7 (publication slots) [proposed C2 binding; Δ = W = 1 h are AI defaults].**
- Release slots for a `T_r` are `V_k = V_s + k·Δ`, k = 0, 1, 2, … with `V_s = T_r + Δ`.
- When the publisher first acts on a `T_r`, the store computes, once and before any staging, `k := min{k ≥ 0 : V_k ≥ R + W}`, where `R` is the publisher's current start time as recorded by the store. It records `k` and `V_k`. Inputs are `T_r` and `R` only, both outcome-blind. With no outage `R ≤ T_r`, so k = 0.
- The publisher stages the entries, then writes one batch marker with `visible_from = V_k`, a scheduled value and never a clock reading. The **store** makes the marker and its entries readable at its own clock time `V_k`, never earlier, whatever the append time. Staging speed therefore cannot move visibility.
- **Residual (disclosed):** if staging is not complete at `V_k` although the publisher is up (a fault beyond W), the batch moves to the next slot computed the same way from the fault's restart. That is a §26 incident. Research can then see a slot shift whose cause may correlate with the path taken. Bound: only on a fault, and only "which hourly slot". T-6 tests that injected delays below W never shift the slot.

**Cooling-off start.** `cooling_off_start := V_k`. At step 5 the worker requests one attestation per candidate slot `V_k ≤ day 255` (at most 912 for g = 0; identical except this field; deterministic, timeless scheme). Staging only *selects* the one for the recorded k; the others are void and never published. No signing happens during publication. A PASS whose `V_k` falls after day 255 is published as PASS with no attestation and is recorded expired (`U_ops`); no promotion can follow.

**P-5 [replaces rev 4 P-5]:** "The 72-hour cooling-off of protocol l.300 runs from the attestation's `cooling_off_start = V_k`, the time the result became visible. No owner decision is accepted before `V_k + 72 h`."

**P-6 [replaces rev 4 P-6; proposed C2 wording].**
- *Definition:* "A nominee is **attested** when its valid PASS attestation is visible (its batch marker is readable). A voided or unpublished signature is not an attestation."
- *DRAFT l.244 becomes:* "at day 255 processing ends. A nominee is promoted only if it is attested and its owner decision is recorded after its full cooling-off (P-5) and by day 255. Any other nominee expires unpromoted, recorded with cause U_ops (Annex A P18-7)."
- *DRAFT l.245 becomes:* "ends processing of every nominee not yet attested; an attested nominee is unaffected: its cooling-off and owner decision proceed under l.244 ('open promotion' in Constitution §4 l.48 means attested in this sense)."
- *Cost:* with g ≤ 34 + 23/24 the decision fits, with slack 34 d 23 h − g − k h shared with owner response. Rejected alternative (decision allowed after day 255): it changes owner decision O-2's hard limit. It is offered only as a Q6 option.

**Disclosure bound (replaces rev 4's):** (i) PASS/FAIL per read; (ii) the cycle-label fact if Q2a allows it; (iii) the FAIL items if Q1's alternative is chosen; (iv) the slot shift on a staging fault (P-7 residual). Pre-read rejections and outage-only delays are independent of the lockbox data.

**P-8 (worker-supplied values) [proposed; D-20 implements].** The sealed store computes `commitment = SHA-256(nonce ‖ bundle)` itself; the worker never supplies it. The publisher stages only (a) `result ∈ {PASS, FAIL}` from the `READY` record and (b) on PASS, the attestation for k after verifying its signature and that every field equals the step-2 values, `V_k` and (`positive`, `true`, `true`). Any mismatch stages FAIL with the default commitment, in the same transaction shape.

## 8'''. Owner questions (replace rev 4 Q1-Q6)

Choosing "keep blocked" on Q1-Q4 or Q6 means C2 cannot be signed yet. Q5 can be deferred. All recommendations assume C2 proceeds at all; "keep blocked" everywhere and `NO_EDGE_FOUND` remain valid outcomes.

**Q1. What does a lockbox result tell you?**
- **"PASS or FAIL only (Recommended)."** The three items appear only on a PASS certificate, where they always read "positive / yes / yes". On a FAIL you learn nothing about which test failed.
- **"Also show me the three items on a FAIL."** Each shows its value or "unavailable" (a crash shows all three "unavailable"). This is a partial diagnosis, with no ETH item and no reason. Research learns it too, because you work with the research AI. "Unavailable" reveals a technical breakdown on every read, so Q2a's plain-FAIL choice can no longer hide that. It needs explicit C2 wording.
- **"Keep blocked."**

**Q2a. At the end of a cycle, may the label show that a FAIL was a technical breakdown?** This arises only when the other family has no result. "Technical" includes failures caused by the data (for example zero variance), so this one fact can say something about the lockbox data.
- **"Allow it, stated openly in C2 (Recommended, if you value an honest end label)."** At most one data-linked fact per cycle, written down.
- **"Count a technical breakdown as a plain FAIL."** This removes the additional cycle-label disclosure (Q1's alternative, if chosen, still discloses its own items). Cost: a broken run can end the cycle as `NO_EDGE_FOUND` and open the baseline path, and draft l.82 changes.
- **"Keep blocked."**

**Q2b. If a pick is stopped before any lockbox data is read, may the record show the reason?** The reason is fixed before any lockbox byte is touched.
- **"Show the reason (Recommended)."** It helps you fix the cause and reveals nothing about lockbox results.
- **"Show only 'stopped before reading'."** It is slightly more closed and gives you less to act on. That no read happened is visible either way.
- **"Keep blocked."**

**Q3. If one family's pick is built on the other's, and the earlier one's result is FAIL, what happens?**
- **"The later pick is not read, and any FAIL counts, including a technical breakdown (Recommended)."** This applies the frozen no-descendant rule. Cost: a crash in the first read can stop the second pick. The alternative would show research which kind of FAIL happened.
- **"Do not allow related picks at all."** A new C2 eligibility rule.
- **"Keep blocked."**

**Q4. How is the lockbox result checked for reproducibility?**
- **"Record everything; re-run later once the period becomes confirmation data (Recommended)."** No extra lockbox read. Cost: a later mismatch voids an already approved promotion.
- **"A second, counted audit read at the same time as the first."** Both runs must finish and agree before any certificate is signed; if not, both FAIL. No extra days. Cost: C2 must allow two reads per family and waive the 30-day wait between a read and its own audit (an exception to a frozen anti-probing rule). Every read counts, a disagreement can cost a good pick, there is more machinery to review, and it needs the Q6 permission.
- **"Keep blocked."**

**Q5. May anyone open the sealed details (the margin, the drawdowns) later?**
- **"No, sealed and machine-checked only (Recommended)."** The details are not secret forever: prices are public, and the period becomes confirmation data.
- **"I may open them after C2 ends."** That reaches research through you, so it needs explicit wording.
- **"Decide later."** They stay sealed; C2 is not blocked.

**Q6. Who posts lockbox results, and what happens when posting is late?** The frozen threat model lets the lockbox job only read and sign. Posting needs a change to that frozen document inside the signed C2 amendment, plus the extra review that permission code gets. Results appear only on fixed hourly slots. Your 72 hours start when you can actually see the result. An outage delays visibility to a later slot, and that delay does not depend on the result.
- *Part (i), who posts:*
  - **"A separate posting job that cannot read lockbox data (Recommended)."** It reduces the risk of accidental disclosure. The data-reading job still supplies PASS/FAIL and the certificate, so the posting job must check them (P-8), and a rare internal fault can still shift the posting slot. Cost: one more identity and key to set up and review.
  - **"Let the lockbox job also post fixed-format results."** Simpler, but the job that read the data also writes what research sees.
  - **"Keep blocked."** No lockbox read can be published, so C2 cannot run.
- *Part (ii), the day-255 cap:*
  - **"A pick must be visible, cooled off for 72 hours and decided by you by day 255 (Recommended)."** This keeps your 255-day limit. Cost: if processing reaches the lockbox late (about day 35 after the look) or posting is delayed near the cap, a PASS can expire unpromoted, even with nothing wrong with it. A pick already visible keeps its 72 hours if a protocol revision happens.
  - **"Allow your decision after day 255 if the result was visible by day 255."** Fewer lost passes, but it changes your earlier decision O-2 (255 days is the hard limit) and needs a decision deadline of its own.
  - **"Keep blocked."**

## 9'''. D-20 changes (consolidated list in §11)

- **T-4:** identical outage and restart schedules give the same `k` and the same `V_k` for PASS, ordinary FAIL, crash FAIL, deadline-miss FAIL, P-8 mismatch FAIL and, under R-b, disagreement and missing-audit FAIL.
- **T-5:** no marker or entry is readable before `V_k` by store clock, whatever its append time.
- **T-6:** injected staging delays below W never shift the slot, for every outcome class. An overrun is logged as a §26 incident.

## 10'''. New findings (numbering continues rev 4)

- **D12-23 NON-BLOCKING.** P-7 fixed slots and store-enforced visibility; P-7 residual disclosed (S-3/A-1).
- **D12-24 NON-BLOCKING.** Fractional bounds; g real-valued (S-4/A-2).
- **D12-25 NON-BLOCKING.** `cooling_off_start := V_k`, with pre-signed slot attestations (S-1/A-4).
- **D12-26 QUESTION (Q6 ii).** One meaning of "attested"; l.244/l.245 wording (S-2).
- **D12-27 NON-BLOCKING (partly self-finding).** P-8: store-computed commitment, publisher validation, and the disclosed signature-nonce residual (S-5/A-3).

## 11. Current binding summary (supersedes every earlier revision where they differ)

**Proposed C2 bindings** (none active):
- **P-1** PASS-only attestation (rev 2).
- **P-2** value contract and full L-1..L-4 check before signing (rev 2).
- **P-3** every released FAIL is a `LOCKBOX_FAIL`; a pre-read rejection is not (rev 3).
- **P-4** upside record, sealed only, with the replicate vector and its pre-read check (rev 3).
- **P-5** cooling-off runs from `V_k` (rev 5).
- **P-6** "attested" definition and the l.244/l.245 wording (rev 5; Q6 ii).
- **P-7** publication slots (rev 5).
- **P-8** worker-value validation (rev 5).
- **Owner-dependent:** D12-3 exception (Q2a); FAIL items (Q1 alternative); pre-read reason (Q2b); R-b bindings (i) two reads per family and (ii) no cooldown between a primary and its audit (Q4); THREAT_MODEL l.9 change (Q6 i).

**D-20 checklist (current; all prior lists superseded):**
- **D-11 items** (`OWNER_DECISION_D11.md` l.26), as in rev 2 §9.
- **Signing.** The attestation writer and signing key; a deterministic, timeless scheme; per-slot pre-signing; `cooling_off_start := V_k`. This replaces rev 3 l.142 (`T_r`) and rev 4 l.47 (`V_s`).
- **Contracts.** P-1, P-2, the sign function and its float rule, P-3, P-4.
- **Order.** Steps 1-8 of rev 4 §6'', with the store-enforced deadline `D_w = T_r − 1 h` on signing and on `→ READY`, no `CLOSED` state, and one publisher transaction per evaluation or pair.
- **Records.** Pre-read and release entry shapes and the batch marker (`visible_from = V_k`); the store-held nonce and store-computed commitment (P-8); the sealed-bundle schema.
- **Pre-read and lineage.** Pre-read reason codes per Q2b; descendant computation and `BARRED_DESCENDANT`.
- **Reproduction.** Full capture plus the Q4 route; under R-b, the pair record and bindings (i)-(ii).
- **Timing.** P-5, P-6, P-7, P-8; tests T-1..T-6.
- **Review.** §16 review of the lockbox ACL tooling and the promotion gate.
- **Not a D-20 item:** the publishing permission, which comes only from the Q6 threat-model amendment.

**Status:** inactive proposal. It requires the owner's decisions on Q1-Q6 and a signed C2 §4 amendment (including THREAT_MODEL l.9), then D-20 and §16 review. Nothing frozen changed. **Remaining:** the R19-2 re-check of this revision. **Still unauthorized:** frozen edits, activation, code, simulation, confirmation or lockbox access, promotion and trading.
