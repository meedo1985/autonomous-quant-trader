# D-12 decision proposal (senior-statistical-governance agent)

Requested by Claude Opus 5.5 on 2026-10-25, after the owner said "go D-12". Prepared by the `senior-statistical-governance` agent, which worked read-only under `.agents/skills/statistical-binding-review/SKILL.md` on checkout `aqt-freeze-sheet` at `5e4c019`. The agent reported its model as Claude Fable 5.1 (`claude-fable-5-1`). The report below is reproduced verbatim; only the harness indentation was removed.

---

# D-12 decision proposal: the lockbox attestation's coarse fields

**Reviewer model (observed):** Claude Fable 5.1, model ID `claude-fable-5-1`, per session metadata. I am an AI reviewer, not an authority. This is a proposal only. It accepts, signs and activates nothing.
**Checkout:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, HEAD `5e4c019`. Read-only: no edits, no commits, no simulation, and no confirmation, lockbox, network or credential access.
**VERDICT:** `BINDING_CANDIDATE` for Route 1. It reads the frozen text and changes nothing frozen. Routes 2 and 3 are `AMENDMENT_REQUIRED`. KEEP_BLOCKED is admissible.
**Not yet reviewed:** R19-2 requires two different-model reviews before the owner decides.

## 1. Authority and status

| Item | Status | Source |
|---|---|---|
| `result_to_research: PASS_FAIL_ONLY` ("Prevents tuning feedback") | FROZEN | `protocols/protocol_v1.yaml` l.76 |
| `attestation_coarse_fields: [paired_delta_sharpe_sign, drawdown_constraint_held, prediction_decay_test_passed]` ("Enumerated fields prevent diagnostic drift") | FROZEN; D-12 is open | l.77–79; DRAFT §4 l.337 |
| Research gets no raw lockbox data and no full diagnostics; research gets PASS/FAIL only; each read gets an evaluation ID | FROZEN | Constitution §7 l.75, l.77, l.79 |
| Attestation binds the hashes, the eligibility ID, the lockbox ID and the cooling-off start; the human answers `APPROVE_AS_IS` or `REJECT` | FROZEN | §13; protocol l.298–300 |
| Attestation schema: 12 required fields, including `cooling_off_start`; no `additionalProperties: false` | FROZEN | `schemas/attestation.schema.json` |
| `lockbox_eval` may read the lockbox and sign attestations only; the owner has no default raw lockbox access | FROZEN; D-11 is amending the read scope | `docs/THREAT_MODEL_v1.md` |
| Lockbox logs and attestations are append-only and tamper-evident | FROZEN | §26 |
| D-11: L-1 T≥q, L-2 T>0 (E-DIFF, float64 decides), L-3 DD≤0.05, L-4 C-3 on ETH; both families sealed before the first read; each read budgeted, logged and given its own ID | OWNER-DECIDED | `d11-proposal/OWNER_DECISION_D11.md` |
| Cycle outcome `NO_RESULT` includes "its lockbox read failed technically" | OWNER-DECIDED O-4 (draft wording) | DRAFT l.82 |
| A technically failed lockbox read is a `NO_RESULT` cause | Draft | DRAFT l.325–326 |

Schema bytes checked: SHA-256 `43e975bf…c2fa` matches the sidecar. `git ls-files --eol` reports `i/lf w/lf attr/-text`, so the file is protected from line-ending conversion.

## 2. Definitions (Route 1)

`T_L` is the float64 L-2 statistic, `difference_series_sharpe.scaled` on the lockbox.

| Field | Definition |
|---|---|
| `paired_delta_sharpe_sign` | Taken from the same float64 `T_L` that decides L-2. `positive` iff `T_L > 0.0`; `zero` iff `T_L == 0.0`, which includes `−0.0`; `negative` iff `T_L < 0.0`. A float residue such as 8.4e−16 reads as `positive`, as D-11's adopted numerics rule requires. |
| `prediction_decay_test_passed` | The L-1 boolean `T_L ≥ q`, in float64. |
| `drawdown_constraint_held` | The L-3 boolean. |
| ETH (L-4) | No field. ETH counts only through PASS. |

**Lemma (exact).** Under D-11, PASS ⇔ L-1 ∧ L-2 ∧ L-3 ∧ L-4. So PASS implies `T_L > 0`, `T_L ≥ q` and DD held. The three fields are therefore (`positive`, `true`, `true`) whenever the result is PASS. In a PASS-only attestation they are a fixed function of PASS and carry no information beyond it (D12-1).

**Where the fields appear.**
- An attestation exists only on the promotion path. The frozen schema requires `cooling_off_start`, and a cooling-off exists only for a PASS.
- No attestation is created for FAIL or for UNAVAILABLE.
- Before signing, `lockbox_eval` checks that the fields equal (`positive`, `true`, `true`). Any mismatch means no attestation, and the read counts as technically failed.
- No new attestation field is added. `lockbox_evaluation_id` links to the log entry, which carries the prediction-artifact hash.

## 3. Who may see what

| Recipient | Receives |
|---|---|
| Research (sandbox, research AI, research user) | PASS or FAIL for each read. FAIL covers both a performance failure and a lockbox-side UNAVAILABLE. A PASS implies an attestation exists. The cycle outcome label comes only after every nominee is processed (O-4). |
| Attestation record (PASS only) | The 12 schema fields plus the three coarse fields from §2. |
| Human approver | The attestation. No diagnostics. |
| Lockbox log, public index (append-only) | Evaluation ID, family, nominee identifiers, prediction-artifact hash, read timestamps, the EXPOSED mark, PASS/FAIL, and the hash of the sealed bundle. |
| Lockbox log, sealed bundle (`lockbox_eval` identity only) | `T_L`, `q`, both MDDs, ETH E-IMPROV and DD, each condition's boolean, availability reasons, and the cause class (performance or technical). [AI default] Not unsealed during C2. |

**Pre-read verification failures.** D-11 says these involve no lockbox read. They may be logged openly as a request rejected for verification, a `NO_RESULT` cause, because they carry no lockbox information.

**Second family.**
- Family 2's terminal status, nominee and prediction artifact are sealed before family 1's read (D-11).
- Family 2's lockbox evaluation is a deterministic function of sealed inputs plus lockbox data.
- No one may cancel or defer family 2's read because of family 1's result. Processing is mandatory (DRAFT §2.3).
- The owner's `APPROVE_AS_IS`/`REJECT` on family 2 may be influenced by family 1's result. That is allowed human judgment and is disclosed here (D12-7).

## 4. Consumer matrix

| Consumer | Binding | Open |
|---|---|---|
| l.76 PASS_FAIL_ONLY | Research gets a binary result per read | D12-3 (the cycle label) |
| l.77–79 fields | As in §2; present only in a PASS attestation | — |
| §13 / schema | No schema change | — |
| §26 logs | Public index plus sealed bundle | D-20 |
| §27 reproduction | Deterministic re-run | D12-8 |
| §7 l.85 descendants | Lineage fixed at sealing | D12-6 |

## 5. Routes

| Route | Content | Governance | Falsifier |
|---|---|---|---|
| **1 (recommended)** | Fields only in PASS attestations (redundant there); research binary; details sealed | A reading; no frozen change | A frozen text requiring an attestation for FAIL |
| 2 | Fields also on a FAIL record, shown to the owner | A FAIL record type not in the schema (`cooling_off_start` is required); in practice it crosses PASS_FAIL_ONLY because the owner works with the research AI. AMENDMENT | — |
| 3 | Add an ETH field, or give the owner the margin (`T_L − q`) | Changes the enumerated list l.77–79 ("diagnostic drift"). AMENDMENT | — |
| 4 | KEEP_BLOCKED | DRAFT l.356: C2 cannot be signed as drafted | — |

**Recommendation: Route 1.** It is the reading that keeps l.76, l.77–79, §7 and the frozen schema all true at once.
- **What it costs:** on a FAIL, no one learns which condition failed.
- **What it does not give:** the fields add no information on a PASS either.

## 6. Findings

- **D12-1 NON-BLOCKING (disclosure).** On a PASS, the coarse fields are determined by the PASS itself (lemma above), so they add nothing. They are kept because the frozen list names them.
- **D12-2 NON-BLOCKING.** The frozen schema makes an attestation PASS-only and permits the coarse fields as additional properties. Recording them needs no schema change. Byte form verified in §1.
- **D12-3 QUESTION.** The O-4 cycle label `NO_RESULT` ("lockbox read failed technically") reveals a third lockbox status, in addition to PASS/FAIL. Proposed reading: the per-read result stays binary, and the technical cause becomes visible only through the cycle outcome after all reads. This carve-out sits at amendment level and the owner already chose it in O-4. If he does not accept the reading, it is an amendment question.
  - The information content is low: data-integrity failures do not depend on performance.
  - It is still more than PASS/FAIL.
- **D12-4 NON-BLOCKING.** The sign field comes from the same float64 `T_L` as L-2, so the two cannot disagree. `−0.0` maps to `zero`, and a positive residue maps to `positive`.
- **D12-5 NON-BLOCKING.** ETH has no frozen field. Adding one would be an amendment (Route 3), and under Route 1 it would always read `true`.
- **D12-6 QUESTION.** §7 l.85 bars descendants after a LOCKBOX_FAIL. If family 2's nominee lists family 1's nominee in its parent lineage (§8), family 1's FAIL would cancel family 2's read. The sealed terminal status should record that lineage fact before the first read, so the consequence is fixed in advance.
- **D12-7 NON-BLOCKING (disclosure).** The family-2 human approval may reflect family 1's result.
- **D12-8 QUESTION.** §27 requires promotion artifacts to be reproducible. A re-run reads the lockbox again, and §7 says every read consumes budget, while C2 allows one read per family.
  - Proposal (D-20): `lockbox_eval` computes the evaluation twice under one evaluation ID and compares byte-for-byte before emitting. Any later audit re-run is logged and releases nothing.
  - Whether such an audit run counts as a "read" is a reading the owner must adopt. Otherwise the question is unresolved.

## 7. What D-20 must bind

- The attestation writer, its schema conformance and the signing key (`lockbox_eval`'s attestation signing).
- The sign function and its float rule.
- The PASS consistency assertion.
- The split between the public log index and the sealed bundle, and the bundle hash.
- The binary research channel.
- The double computation (D12-8).
- The lineage field in the sealed status (D12-6).
- §16 review of `lockbox_eval` (Constitution l.152: lockbox ACL tooling, promotion gate).

## 8. Owner questions

**Q1. What should the lockbox record show?**
- **"PASS or FAIL only (Recommended).** The three named items appear only on a PASS certificate, where they always read 'positive / yes / yes'." Cost: on a FAIL you will not learn which test failed. The details stay sealed.
- **"Also record the three items on a FAIL, shown to me."** You learn which part failed. Because you work with the AI, research effectively learns it too, which breaks 'PASS/FAIL only' in practice. It also needs a rule and schema change.
- **"Keep blocked."** C2 cannot be signed.

**Q2. What happens to the sealed lockbox details after C2?**
- **"They stay sealed; a machine re-check only (Recommended).** The result is checked by computing it twice inside the same read." Cost: no one ever sees the margin by which the strategy passed or failed.
- **"I may open them after C2 ends."** You gain insight, but it flows into later research through you. That is more than PASS/FAIL and needs an amendment.

## 9. What remains

**Remaining:** the R19-2 reviews; owner Q1–Q2; readings D12-3, D12-6 and D12-8; D-20; §16.
**Still unauthorized:** frozen edits, activation, code, simulation, data access, promotion and trading.

I did not check how the D-19/G-gate records label a family whose nominee is UNAVAILABLE in the cycle outcome beyond DRAFT l.82, nor whether any existing code already writes attestations. The ledger only mentions them.
