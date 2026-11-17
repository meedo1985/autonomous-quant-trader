# Codex Astra review of D-12 proposal (55554c6)

Prompt: `REVIEW_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-astra`, sandbox read-only, reasoning effort high, session id `01a174d2-87a9-79d3-8074-ccddad6c2edb`, 86,497 tokens. (The report says model metadata was not exposed inside the session; the CLI header above is the verified source.)

Verdict: **FIX**. Findings D12R-A-1 .. A-8.

**ID note:** the report below labels its findings `D12R-S-1` .. `D12R-S-8` and calls its namespace `D12R-S`, which is the Sol prefix the prompt reserved. The text is kept verbatim; in this record and every later reference, Astra finding `D12R-S-n` in the report below is **`D12R-A-n`** (same n). Sol's findings are in `SOL_REVIEW_55554C6.md`.

## Report (verbatim)

**Verdict: FIX.** Route 1’s PASS-only certificate is defensible, and its three-field lemma is correct. The proposal does not yet establish that the complete disclosure arrangement changes nothing frozen or is leak-free.

Reviewer namespace: `D12R-S`. Exact runtime model metadata is not exposed here; verify it before recording this review’s model identity under R19-2. Reviewed checkout: `55554c681c3746853bb8ad741d3129963225f10c`. Nothing written.

| Authority | Status |
|---|---|
| Constitution, protocol, schema and threat model | Frozen requirements |
| D-11, including adopted revisions and adjudication | Owner-decided; requires the signed C2 amendment to become operative |
| C2 wording and D-12 | Inactive proposals |
| This review | Advisory; accepts or activates nothing |

The numerical binding is sound, subject to D-11’s availability requirements:

| Consumer | Correct binding |
|---|---|
| L-2 / sign field | \(T_L=\sqrt{365}\,\overline{(c-b)}/s_{c-b}\), daily net returns, sample variance; use the same finite float64 result |
| L-1 / prediction field | `T_L >= q`, using the adopted float64 lower prediction quantile |
| L-3 / drawdown field | BTC hourly-path `MDD(candidate) − MDD(benchmark) <= 0.05`, in fraction units |
| L-4 | ETH E-IMPROV strictly positive **and** ETH drawdown condition; no separate coarse field |
| Disclosure, logs, lineage and reproduction | Unresolved as detailed below |

Thus PASS implies `(positive, true, true)`. The converse is false: those three fields can hold while ETH fails. The attestation writer must verify the complete available L-1–L-4 result.

**Findings**

1. **D12R-S-1 — MEDIUM / correction required. Schema compatibility is mistaken for schema enforcement.**  
   **Place:** [PROPOSAL.md:45](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL.md:45), D12-2, Route 2.  
   **Failure scenario:** An object containing all 12 required keys, with `cooling_off_start: null` and an extra `result: "FAIL"`, satisfies every assertion in the frozen schema. It specifies neither property types nor PASS-only semantics.  
   **Minimal repair:** Describe PASS-only issuance as the proposed promotion-path binding, compatible with §13—not something the schema proves. I found **no frozen requirement** to issue FAIL attestations or FAIL coarse fields. Route 2 requires a disclosure-policy decision, but a schema change is not established merely by `required: cooling_off_start`.

2. **D12R-S-2 — HIGH / BLOCKER. The cycle-label exception was not decided by O-4.**  
   **Place:** [PROPOSAL.md:96](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL.md:96).  
   **Failure scenario:** With the other family already unavailable, `NO_RESULT` versus an outcome reflecting a completed performance failure can distinguish technical unavailability behind the same research-facing FAIL. Waiting until cycle end does not remove that information. Nor are all availability failures performance-independent: zero variance and nonfinite return arithmetic depend on the realized path.  
   **Evidence:** [OWNER_DECISION_O1_O7.md:34](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/OWNER_DECISION_O1_O7.md:34) decides **baseline-path eligibility**, not a PASS/FAIL disclosure exception.  
   **Minimal repair:** Remove that attribution and the independence claim. Explicitly decide recipients and permitted outcome disclosure, with corresponding §7/protocol wording if an exception is intended.

3. **D12R-S-3 — HIGH / BLOCKER. The public index creates unaddressed disclosure channels.**  
   **Place:** [PROPOSAL.md:54](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL.md:54).  
   **Failure scenario:** Early UNAVAILABLE, completed performance FAIL, and late signing failure can produce distinguishable completion timestamps or certificate timing. A public hash of a predictable sealed bundle also permits testing candidate diagnoses; hashing supplies integrity, not secrecy. A two-candidate synthetic bundle suffices to demonstrate that attack.  
   **Minimal repair:** Define who can read the index, permissible timing metadata, and release behavior. Keep detailed timing and diagnostic commitments private, or specify a hiding commitment. Certificate **existence alone** adds no bit beyond an already released PASS; earlier publication or distinguishable failure behavior can.

4. **D12R-S-4 — MEDIUM / mandatory D-20 condition. Failure accounting and publication order are incomplete.**  
   **Place:** [PROPOSAL.md:47](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL.md:47), lines 57–60 and §7.  
   **Failure scenario:** A process reads lockbox bytes and crashes before recording EXPOSED; or research receives PASS before signing fails, contradicting “PASS implies an attestation exists.”  
   **Minimal repair:** Require durable budget/evaluation/exposure accounting before access, persistent post-access failure records, and a defined attestation/result publication transaction. True pre-read rejection may be logged openly with a fixed, non-sensitive reason, but must preserve D-11’s no-retry rule. Post-read verification failures remain exposed, budgeted failures with sealed diagnostics. EXPOSED records access, not success; §26 does not require public diagnostic logs.

5. **D12R-S-5 — HIGH / BLOCKER. Recording lineage does not resolve the second-family contradiction.**  
   **Place:** [PROPOSAL.md:65](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL.md:65) and D12-6.  
   **Failure scenario:** Family 2’s sealed nominee descends from family 1’s nominee. Family 1 fails. Mandatory reading conflicts with §7’s descendant prohibition; merely sealing the relationship leaves both commands standing.  
   **Minimal repair:** State an explicit precedence rule: process every nominee, but a prohibited descendant receives a terminal no-read disposition. Bind its outcome classification and the meaning of `LOCKBOX_FAIL` when outward FAIL includes UNAVAILABLE. Keeping both reads unconditional instead requires an amendment. Human approval may consider family 1’s result, but cannot rewrite family 2’s sealed inputs or cancel otherwise required processing.

6. **D12R-S-6 — HIGH / BLOCKER. Silent audit reruns have no established budget exemption.**  
   **Place:** [PROPOSAL.md:103](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL.md:103).  
   **Failure scenario:** An audit reacquires lockbox inputs after the family’s sole evaluation, yet consumes no budget because it releases nothing. Neither §7 nor D-11 supplies that exception. Conversely, computing twice over retained objects does not by itself demonstrate reconstruction from recorded hashes/seeds.  
   **Minimal repair:** Define the bounded evaluation/read transaction, reproducible payload and failure handling. Separate scientific bytes from timestamps/signatures. Later access must follow existing accounting or an explicit amendment; “no output” is not an exemption.

7. **D12R-S-7 — MEDIUM / correction required. Q1–Q2 conceal material choices.**  
   **Place:** [PROPOSAL.md:120](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL.md:120).  
   **Failure scenario:** The owner selects “PASS or FAIL only” while unknowingly accepting a technical-status leak through cycle outcomes. Q2 combines post-C2 retention with an unresolved same-read reproduction mechanism. Its promise that nobody ever sees the margin is too absolute given public historical prices and eventual confirmation release.  
   **Minimal repair:** Separate confidentiality from audit access. Add explicit decisions for D12-3, D12-6 and D12-8, with defer/keep-blocked available. Explain that FAIL coarse fields provide only partial diagnosis—there is no ETH field or availability reason. Recommend Route 1 **conditionally**, with these unresolved costs stated plainly.

8. **D12R-S-8 — MEDIUM / QUESTION requiring disposition. A frozen logging consumer is omitted.**  
   **Place:** Proposal consumer matrix and D-20 list; [protocol_v1.yaml:89](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/protocols/protocol_v1.yaml:89).  
   **Failure scenario:** Implementation records only `T_L`, lower quantile `q` and gate booleans, without a defined record of the required “upside exceedance.”  
   **Minimal repair:** Add this consumer. Bind the meaning, necessary reference and sealed logging representation without inventing an upper rejection gate or publishing another diagnostic.

**Disposition of D12-1..D12-8:** D12-1 and D12-4 are correct; D12-5 is correct for a field representing the complete L-4 boolean. D12-2’s schema justification is wrong. D12-3 needs a new explicit decision. D12-6 and D12-8 identify real problems but do not resolve them. D12-7 is acceptable within the processing restrictions above.

D-20 must inherit these publication, accounting, lineage, audit and logging conditions **alongside** D-11’s outstanding artifact retrieval, seeds/streams, reference vectors and start-state bindings. Protected implementation still requires §16 review.

Independent checks reproduced `T_L = 8.384297404680616e-16` for the adopted exact-zero-mean example; `-0.0` maps to zero and fails L-2. All 13 sidecars, seven manifest bindings and the Constitution self-hash verified. The attestation SHA-256 matches `43e975bf…c2fa`. Frozen Git content matches `f1c17eb`; the sole working-byte difference is existing CRLF checkout conversion in `docs/README.md`.

Tests/lint/type/import checks are N/A to this document-only review; no implementation changed. No restricted data or simulation was used. Nothing was committed, as requested, so this response is not yet a committed R19-2 review record.
