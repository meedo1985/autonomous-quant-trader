# D-12 decision proposal, revision 2 (senior-statistical-governance agent)

Revision of `PROPOSAL.md` (rev 1, reviewed at `55554c6`) after the R19-2 reviews `SOL_REVIEW_55554C6.md` (gpt-6-sol, FIX, D12R-S-1..6) and `ASTRA_REVIEW_55554C6.md` (gpt-6-astra, FIX, D12R-A-1..8; the verbatim report labels them `D12R-S-n`, and its header maps them to `D12R-A-n`, which is used here). Prepared on checkout `aqt-freeze-sheet`, branch freeze-sheet, HEAD `59bec18`, under `.agents/skills/statistical-binding-review/SKILL.md`.

---

# D-12 decision proposal, revision 2: the lockbox attestation's coarse fields

**Reviewer model (observed):** Claude Fable 5.1, model ID `claude-fable-5-1`, per this session's metadata. I am an AI reviewer, not an authority.
**Status: INACTIVE PROPOSAL.** It accepts, signs and activates nothing. It needs an owner decision and then the owner's signed C2 §4 amendment before it binds anything. No frozen file, hash or sidecar was changed. The agent wrote only this file. It staged and committed nothing; any commit of this file was made afterwards by the requesting session. No simulation was run, and there was no confirmation, lockbox, network or credential access.
**Review status:** revision 2 has not been reviewed. R19-2 requires a focused re-check by two different model families before the owner decides.
**VERDICT: `AMENDMENT_REQUIRED`.**
- The field definitions and the lemma (§2) are a `BINDING_CANDIDATE`. Both reviews confirmed them.
- PASS-only issuance, the index rules, the failure paths and the accounting order are new C2 wording. The frozen text allows them but does not establish them.
- D12-3 (§4) is an explicit exception to PASS_FAIL_ONLY that only the signed amendment can grant.
- `KEEP_BLOCKED` is admissible at every point. Under DRAFT l.356–358, it means C2 cannot be signed.

## 0. Verification run (agent protocol items)

- **Citations checked both ways (item 1).** A topic search of the frozen corpus for `LOCKBOX_FAIL`, `descendant`, `upside`, `cooling_off_start` and attestation found one governing clause rev 1 did not cite: protocol l.296 `descendant_retry_same_cycle_after_fail: false`. It now supports §5. Protocol l.89 ("upside exceedance is logged") was also uncited and is now bound in §7 (A-8).
- **Referents (item 2).** O-4 (`OWNER_DECISION_O1_O7.md` l.34, l.49–50) decides only which outcomes open the deployable-baseline path. The `NO_RESULT` definition, including "its lockbox read failed technically", is draft wording at DRAFT l.82 marked "[AI default: the label names]". Rev 1's "OWNER-DECIDED O-4" was wrong (A-2). D-11's pre-read rule ("a technical failure, a `NO_RESULT` cause; no retry in C2") is in `d11-proposal/PROPOSAL_REV3.md` l.52–55, which `OWNER_DECISION_D11.md` l.16 adopts.
- **Bytes (item 3).** Schema SHA-256 is `43e975bf…0ab9c2fa`, the same as its sidecar. `git ls-files --eol` gives `i/lf w/lf attr/-text`. Both checked again at `59bec18`.
- **Arithmetic.** I did no new numerical calculation. The lemma is logical. The float residue example (`T_L = 8.384297404680616e-16`, which reads `positive`) was reproduced by Astra, as its report states. I did not re-run it.

## 1. Disposition of review findings

Overlaps: S-1 = A-1; S-2 ≈ A-3; S-3 = A-5; S-4 = A-6; S-5 overlaps A-2 and A-4; S-6 overlaps A-4. A-7 matches Sol's unnumbered owner-question paragraph. A-8 is Astra's alone.

| ID | Disposition | Evidence | Repaired in |
|---|---|---|---|
| S-1 / A-1 | **Accepted.** The schema lists 12 required keys with no types and no `additionalProperties: false`. A FAIL object with `cooling_off_start: null` would validate. The schema permits PASS-only issuance; it does not prove it. Route 2 is a disclosure decision, and no schema change is shown to be needed. | `schemas/attestation.schema.json` l.4–17; Constitution §13 l.122–124 | §2 (proposed C2 binding P-1), §8 Q1 |
| S-2 / A-3 | **Accepted.** §26 l.191 requires the logs to be append-only and tamper-evident, not public. Completion timing can separate the failure branches. A plain hash of a low-entropy bundle can be brute-forced against guessed diagnoses. | §26 l.191; §7 l.79 | §3 (index recipients, fixed release time, salted commitment) |
| S-3 / A-5 | **Accepted.** Rev 1's "no one may cancel family 2's read" contradicts §7 l.85 and protocol l.296 when family 2's nominee descends from family 1's. Both reviewers offered a precedence rule; Sol also offered requiring independent nominees. I use the precedence rule because it applies the frozen text and adds no eligibility condition. Independence at sealing remains an owner option. | §7 l.85; protocol l.296; DRAFT l.241 (only a *promotion* never stops the other family); DRAFT l.333 (l.294–296 stay in force) | §5, §8 Q3 |
| S-4 / A-6 | **Accepted.** Computing twice inside one run checks determinism; it does not reproduce independently. §7 l.77 charges *every* read, and "releases nothing" grants no exemption. One addition: §27 l.194 asks that artifacts *can* reproduce "from recorded hashes/seeds". So complete capture meets its precondition, and an actual re-run is a separate question. | §7 l.77; §27 l.194; DRAFT §2.3 l.222 | §6, §8 Q4 |
| S-5 | **Accepted.** Pre-read rejection and post-read failure are now separate paths, with what research sees at each step. The claim that "integrity failures do not depend on performance" is withdrawn. | PROPOSAL_REV3 l.52–55; §7 l.77 | §4 |
| S-6 | **Accepted.** A value and type contract is added: a nonfinite or unavailable statistic gets no sign, and a mismatch after a read becomes a recorded, budgeted failure. Astra's preamble adds a point: the three fields can hold while ETH fails, so before signing the writer checks the full L-1..L-4 PASS, not just the fields. | Astra report l.32 | §2 P-2, §6 step 5, §9 |
| A-2 | **Accepted.** O-4 was misattributed (see §0). The label leak exists: when the other family has no result, `NO_RESULT` versus `NO_EDGE_FOUND` reveals a technical failure behind a FAIL that research has already seen. Waiting for the cycle end does not remove it. Zero variance or nonfinite arithmetic depends on the realized path, so the independence claim is withdrawn. | O1_O7 l.34, l.49–50; DRAFT l.82 | §4, §8 Q2 |
| A-4 | **Accepted.** The budget and EXPOSED records are durable before any byte is read. A crash after that is a recorded failure and is never retried. PASS is published only after the attestation is signed, in one append-only entry. | §7 l.77; §26 l.191 | §6 |
| A-7 | **Accepted.** Confidentiality and audit are now separate questions, D12-3, D12-6 and D12-8 each get a question with a defer or keep-blocked option, recommendations are conditional, and the "no one ever sees the margin" claim is withdrawn. The lockbox prices are public (OWNER_DECISION_D11 l.12), and the segment rolls into confirmation (§7 l.81). | — | §8 |
| A-8 | **Accepted.** Protocol l.89 is a frozen logging consumer that rev 1 left out. It is now bound to the sealed bundle and invents no gate. | protocol l.87–89 | §7 |

Totals: 14 findings. 14 accepted, 0 in part, 0 rejected. On S-3, Sol offered two remedies; I took one and left the other to the owner. I found no reviewer claim that the frozen text contradicts.

## 2. Definitions and issuance (unchanged numerics; issuance recast)

`T_L` = the float64 L-2 statistic, `difference_series_sharpe.scaled` on the lockbox E-DIFF series (D-11 Route A).

| Field | Definition (unchanged from rev 1) |
|---|---|
| `paired_delta_sharpe_sign` | from the same float64 `T_L` that decides L-2: `positive` iff `T_L > 0.0`; `zero` iff `T_L == 0.0`, including `−0.0`; `negative` iff `T_L < 0.0` |
| `prediction_decay_test_passed` | the L-1 boolean `T_L ≥ q` |
| `drawdown_constraint_held` | the L-3 boolean (BTC `MDD_c − MDD_b ≤ 0.05`) |
| ETH (L-4) | no field. It counts only through PASS |

**Lemma.** PASS ⇔ L-1 ∧ L-2 ∧ L-3 ∧ L-4, all available. So PASS ⇒ (`positive`, `true`, `true`). The converse is false, because ETH can fail. On a PASS the fields add no information (D12-1).

**Proposed C2 bindings (new wording, not proven by the schema):**
- **P-1 (PASS-only issuance).** "An attestation is issued only for a nominee whose lockbox result is PASS. No attestation or coarse-field record is created for any other outcome." Rationale: §13 l.122 places the attestation on the promotion path. The frozen text has no FAIL attestation and does not forbid one.
- **P-2 (value contract).** The sign is one of the three strings, and the two fields are JSON booleans. They are computed only from a finite, available `T_L` and L-1..L-3 results. Before signing, `lockbox_eval` asserts that all of L-1..L-4 are available and PASS and that the fields read (`positive`, `true`, `true`). If the assertion fails, nothing is signed, and the result is a post-read technical failure (§4).

## 3. Who sees what, and when (replaces rev 1 §3)

**Working rule.** Anything the owner sees is treated as research-visible, because the owner works with the research AI (the rev 1 Route 2 argument). So the index must itself be research-safe.

| Record | Readers | Content |
|---|---|---|
| Lockbox index (append-only; "public" dropped) | owner, governance tooling, research | evaluation ID; family; nominee ID; prediction-artifact hash (sealed before any read); scheduled release time; EXPOSED mark; research-facing result; bundle commitment |
| Attestation (PASS only, P-1) | owner/approver; promotion tooling | the 12 schema fields plus the three fields (§2) |
| Sealed bundle | `lockbox_eval` identity only | `T_L`, `q`, both MDDs, ETH E-IMPROV and DD, each condition's boolean, availability reasons, failure cause class, actual start and finish times, the upside-exceedance record (§7), captured input hashes (§6) |

**Timing [AI default].** Each read's release time is fixed and written to the index before the read (§6 step 2). For example, the read start plus a fixed allowance, such as D-11's p = 7 days. Every outcome is released at that scheduled time: PASS, FAIL, or a post-read technical failure shown as FAIL. Only the bundle holds actual completion times. If a run is not finished by the release time, it is a post-read technical failure.

**Commitment [AI default].** The index carries `SHA-256(nonce ‖ canonical bundle bytes)`, a hiding commitment. The nonce is 256 random bits created at runtime and kept inside the sealed store. It never goes into the repository, logs or prompts. A plain bundle hash is not used.

**Attestation existence** adds nothing beyond a PASS that is released at the same moment (Astra A-3).

## 4. Failure paths and what research sees (D12-3; replaces rev 1 D12-3)

| Path | When | Budget / EXPOSED | Research sees at request · release · cycle end |
|---|---|---|---|
| **Pre-read rejection** (D-11 REV3 l.52–55: hash or identity mismatch) | before any lockbox byte | no read, so not EXPOSED. The family's one read is gone, because C2 allows no retry | `PRE_READ_REJECTED` with a fixed reason code · — · `NO_RESULT` cause. Nothing about the lockbox is revealed, because the outcome is fixed before any byte is read |
| **Performance FAIL** | after the read | spent; EXPOSED | — · `FAIL` · counts as a result (outcome `NO_EDGE_FOUND` if no family passes) |
| **Post-read technical failure** (L-gate `UNAVAILABLE`, crash, P-2 mismatch, signing failure, missed release time) | after the read | spent; EXPOSED | — · `FAIL` · `NO_RESULT` cause (DRAFT l.82, l.325–326) |
| **PASS** | after the read | spent; EXPOSED | — · `PASS` together with the attestation · promotion path |

**The leak (D12-3).** Per read, research sees only PASS or FAIL. The cycle label adds information in one case only: when every other declared family also has no result. Then `NO_RESULT` versus `NO_EDGE_FOUND` tells research whether this family's FAIL was technical. That is at most one extra bit per cycle. It is not independent of the data, because zero variance or a nonfinite value depends on the realized path. It is an exception to l.76 and §7 l.79 that the signed C2 must state; it cannot be read into the frozen text. O-4 did not decide it. The options are in §8 Q2.

## 5. Cross-family descendants (D12-6; replaces rev 1 "second family")

**Precedence rule (a reading of the frozen text).**
- At sealing, before the first read, `lockbox_eval` records from immutable §8 lineage whether either nominee descends from the other, including indirect descent.
- If the earlier-processed nominee's read ends in FAIL of any kind, a descendant nominee gets the terminal disposition `BARRED_DESCENDANT` and no read (§7 l.85; protocol l.296). Every outcome released to research as FAIL counts as `LOCKBOX_FAIL` here, including a post-read technical failure.
- A pre-read rejection is not a read, so it bars nothing.

**Order.** C2's order is trend, then volatility (DRAFT l.241). So only a volatility nominee that descends from the trend nominee can be barred.

**Outcome.** A barred descendant has no result. The cycle outcome then follows the other family: `NO_EDGE_FOUND` after a performance FAIL, `NO_RESULT` after a technical one. Research learns nothing new, because the bar follows from a FAIL it has already seen.

**Unchanged.** Everything else stays sealed and mandatory (D-11 REV3 §7). D12-7 stands: the owner's `APPROVE_AS_IS` or `REJECT` may take the other family's result into account, but it cannot change sealed inputs or cancel processing that is still required.

## 6. Accounting order, publication and reproduction (D12-8; replaces rev 1 D12-8)

**One read, in this order [AI default; D-20 implements]:**
1. Pre-read verification (D-11 REV3 item 3). If it fails, follow the §4 pre-read path and stop.
2. Durably write the evaluation ID, the budget decrement, the EXPOSED mark and the scheduled release time, and confirm the write, **before any lockbox byte is opened**. If the write fails, no read happens.
3. Read and compute. Capture the hashes of every input byte, the code commit, the image, the seeds and stream identities, and the outputs. Keep scientific bytes apart from timestamps and signatures. Compute twice and compare the scientific bytes. This checks determinism only; it is not independent reproduction.
4. Write the sealed bundle and its commitment.
5. Only if all of L-1..L-4 PASS and P-2 holds: sign the attestation.
6. At the release time, make **one** append-only index entry with the result, plus the attestation reference on a PASS. If anything in steps 3–5 failed, or a crash leaves step 2's record without a step 6 entry, the entry is a post-read technical failure. It is never retried.

**Reproduction against the read budget (owner choice, §8 Q4).** In C2, §7 l.77 and the one-read limit (DRAFT l.222) leave no budget-free re-read. The routes:
- **R-a.** Capture everything in step 3. Run the independent re-execution only after the segment has rolled into confirmation (§7 l.81), through the experiment engine. That re-run is not a lockbox read. If it does not reproduce, the promotion is void (§27 l.194). Cost: that check comes after the cooling-off, so an approved promotion could be voided later.
- **R-b.** C2 grants one extra, separately logged audit re-run per family before signing. It gets its own evaluation ID and counts against the budget. v1.0 l.74 already allows two evaluations per family, so the total stays within the frozen limit. C2 must say this explicitly.
- **Keep blocked.**

## 7. Upside exceedance (A-8; new)

Protocol l.89 requires upside exceedance to be "logged". It does not make it a gate. Proposed binding:
- The sealed prediction artifact also stores the sorted 2,000 replicate values and their hash. D-11's artifact (q, n, b, stream identity) cannot reconstruct a rank, so this is an identifiability addition that D-20 carries.
- The sealed bundle records `k = #{replicates ≤ T_L}` as an exact integer, and `upside_exceedance = T_L > type-7 95th percentile` of the same vector. The 95th percentile is an [AI default] chosen to mirror the frozen 5th.
- The only reader is the bundle. Nothing goes to research, the attestation or the index, and nothing decides a result.

## 8. Owner questions (replace rev 1 Q1–Q2)

Choosing keep blocked on any of Q1–Q4 means C2 cannot be signed yet. Q5 can be deferred without blocking.

**Q1. What does a lockbox result report?**
- **"PASS or FAIL only (Recommended if you accept Q2's cost)."** The three items appear only on a PASS certificate, and there they always read "positive / yes / yes". On a FAIL you will not learn which test failed. Even the alternative would not tell you everything: there is no ETH item and no reason code.
- **"Also show me the three items on a FAIL."** You get a partial diagnosis. Because you work with the research AI, research effectively learns it too, which breaks "PASS/FAIL only". It needs an explicit disclosure rule in C2. A schema change is probably not needed.
- **"Keep blocked."**

**Q2. When the other family has no result, the end-of-cycle label tells research whether a FAIL was a technical breakdown. Allow that?**
- **"Allow it, and state it openly in C2 (Recommended, conditionally)."** At most one extra fact per cycle, written down rather than hidden.
- **"Count a technical breakdown as a plain FAIL."** That closes the leak, but a broken run could then end the cycle as `NO_EDGE_FOUND` and open the baseline path. It changes draft l.82.
- **"Keep blocked."**

**Q3. If one family's pick is built on the other family's pick, and the earlier one fails, what happens?**
- **"The frozen rule wins: the later pick is not read (Recommended)."** This applies the existing rule that descendants of a failed candidate get no lockbox read. It is decided in advance.
- **"Do not allow such related picks at all."** This is a new C2 eligibility rule.
- **"Keep blocked."**

**Q4. How is the lockbox result checked for reproducibility?**
- **"Record everything; re-run later on the same period once it becomes ordinary confirmation data (Recommended, conditionally)."** It uses no extra lockbox read. Cost: if the later re-run does not match, an already approved promotion is voided.
- **"Allow one extra, counted audit read before the certificate is signed."** It catches a problem earlier. It uses a second read per family, which v1.0 allows and C2 must state.
- **"Keep blocked."**

**Q5. May anyone open the sealed details (the margin, the drawdowns) later?**
- **"No. They stay sealed and machine-checked only (Recommended)."** This keeps the record from feeding back into research. It does not keep the information secret forever: the prices are public, and the period becomes confirmation data next cycle, where similar numbers can be recomputed.
- **"I may open them after C2 ends."** That gives you insight, but it reaches research through you. It is more than PASS/FAIL and needs explicit amendment wording.
- **"Decide later."** They stay sealed until you decide. C2 is not blocked.

## 9. What D-20 must bind (updated)

- **From D-11 (`OWNER_DECISION_D11.md` l.26):** the nominee artifact's identity and a verified retrieval path for its trial code, configuration and model seed; the confirmation baseline's start state (D11-16); the lockbox seed source and stream identity; the m≠n index generator; the ψ reference vectors; the R-8 extension for `max_drawdown`.
- **From D-12:**
  - the attestation writer and its signing key;
  - P-1;
  - P-2's value and type contract, with the full L-1..L-4 check;
  - the sign function and its float rule;
  - the step 1–6 order, with durable writes;
  - the publication transaction and the fixed release time;
  - the index fields and readers;
  - the salted commitment and how the nonce is held;
  - the sealed-bundle schema, including §7's replicate vector, `k` and exceedance flag;
  - the pre-read reason codes;
  - the descendant computation at sealing and the `BARRED_DESCENDANT` disposition;
  - reproduction capture, plus the Q4 route chosen.
- **§16 review** of `lockbox_eval`: lockbox ACL tooling and the promotion gate (Constitution l.152; DRAFT l.418).

## 10. Findings (rev 2 numbering continues rev 1's)

- **D12-1 NON-BLOCKING.** On a PASS, the coarse fields are fixed by the PASS itself, so they add no information.
- **D12-2 NON-BLOCKING, corrected.** The schema permits PASS-only issuance; it does not prove it. P-1 is new C2 wording.
- **D12-3 QUESTION (Q2).** The cycle label leaks at most one bit per cycle. Only an explicit C2 exception can allow it. O-4 did not decide it.
- **D12-4 NON-BLOCKING.** The sign and L-2 use the same float64 value and cannot disagree.
- **D12-5 NON-BLOCKING.** There is no ETH field. Adding one would be an amendment.
- **D12-6 QUESTION (Q3).** The precedence rule in §5.
- **D12-7 NON-BLOCKING.** The human approval of one family may reflect the other family's result, within the limits in §5.
- **D12-8 QUESTION (Q4).** Reproduction versus the read budget, §6.
- **D12-9 NON-BLOCKING (new).** The index, timing and commitment rules in §3. Plain hashes and completion timestamps are kept out of the index.
- **D12-10 NON-BLOCKING (new).** Upside-exceedance logging in §7 needs the replicate vector added to D-11's sealed artifact. That is a D-20 item.
- **D12-11 QUESTION (Q5).** Opening the sealed details after C2.

## 11. What remains

**Remaining:** the R19-2 re-check of this revision; owner Q1–Q5; the signed C2 §4 wording for P-1, §3, §4, §5 and §6; D-20; §16.
**Still unauthorized:** frozen edits, activation, code, simulation, confirmation or lockbox access, promotion and trading.
**Not checked:** whether any existing code already writes attestations or lockbox logs; whether Annex A P18-7 cause codes need a code for pre-read rejection (I assumed the fixed reason code fits under `NO_RESULT`).
