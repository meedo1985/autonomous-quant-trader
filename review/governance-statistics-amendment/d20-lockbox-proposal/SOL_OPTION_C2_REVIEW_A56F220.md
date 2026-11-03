# Codex Sol re-check of D-20 option C revision C2 (a56f220)

Prompt: scratchpad `optc2_sol_prompt.md` (reproduced in section "Prompt" below). Reviewer metadata from the Codex CLI header (2026-10-30): model `gpt-6-sol`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a18c9b-72ce-78b3-bf70-1c7b91d6677e`, 72,234 tokens. Reviewed `OPTION_C_PROPOSAL_REV2.md` at `a56f220`. Bitcoin node paused for the runs (stopped at 696,568, restarted after both). Sol and Astra ran sequentially with outputs in the session scratchpad only.

Verdict: **FIX**: 4 BLOCKER (D20C2-S-1..4), 2 NON-BLOCKING (S-5, S-6). Findings D20C2-S-1..6, no gaps.

No finding is left unrepaired by decision yet; dispositions go in revision C3.

## Report (verbatim)

## VERDICT: FIX

C2 is an **inactive amendment proposal**. The frozen [Constitution](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/docs/RESEARCH_CONSTITUTION.md:72>), [protocol](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/protocols/protocol_v1.yaml:73>) and [attestation schema](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/schemas/attestation.schema.json>) control; the [D-12 decision](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/OWNER_DECISION_D12.md:20>) still requires signed C2 wording. This review grants no approval or activation.

The central result argument in [C2 §1.3](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV2.md:101>) is sound **under rev 8’s stated lock, durability and fail-closed assumptions**: a durable release fixes the shown PASS/FAIL, including the linked-but-unfsynced finish case. The owner-account copy and read-back establish the *causal order* of delivery across the specified crash and concurrent-request cases. The single host clock remains necessary for timestamp order and 72 elapsed hours; a clock step can defeat those time claims. The platform assumptions remain unverified.

### C1 finding dispositions

| C1 finding | Assessment of C2 | Evidence |
|---|---|---|
| S-1 / A-5 | **ACCEPT WITH NOTES** | §1.4 gives each delivery kind one file and entry, verify-and-reuse recovery, `L_pub`, and owner-account read-back. “Never earlier” needs the trusted-clock qualification. |
| S-2 / A-1 | **ACCEPT** | §1.2 narrows `NOT_YET` to no ordinary `L_store` acquisition; §1.7 discloses shared-resource and recovery waits. |
| S-3 / A-4 | **FIX** | §1.5 orders revision entries and attestation delivery under one lock, but its cap check can precede an append that becomes durable after C. D20C2-S-1. |
| S-4 | **FIX** | §1.6 adds a backstop and pending list, but release before `R₀` is refused and unbounded failures defeat its completion guarantee. D20C2-S-2. |
| S-5 / A-2 | **FIX** | §1.7 discloses unbounded waits and expiry. Its claim that delays cannot change a result is too broad, and the proposed §7 row does not cover the stated interface consistently. D20C2-S-3–4. |
| S-6 / A-6 | **ACCEPT WITH NOTES** | §1.3 repairs the proof, clock inventory and rev 8 qualification; Q7 receives the save rule. Retained tests still name removed operations. D20C2-S-6. |
| A-3 | **ACCEPT** | §1.5 restores signed `cooling_off_start =` RESULT `delivered_at`, satisfying Constitution §13’s required binding and the schema field. |
| A-7 | **ACCEPT WITH NOTES** | §1.10 explicitly supersedes the principal obsolete clauses; the inherited test text needs cleanup. |
| S-7 / A-8 | **ACCEPT** | §4 leaves the proposed wait-for-other-reads rule unadopted. |

### Findings

- **D20C2-S-1 — BLOCKER — §1.5, Q7.** At `C−1`, `record_delivery` can pass its cap check; its append and fsync can complete at `C+1`. C2 says effectiveness starts **from that entry**, yet also says no signature becomes effective after C. [D-12 P-6](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV7.md:98>) fixes unattested status at the cap. A whole, unfsynced entry surviving a crash presents the same issue. **Minimal repair:** state separately when the attempt counts and when the certificate becomes effective; give the owner the explicit after-C consequence in Q7 and reconcile P-6, or require durability before C for effectiveness. A revision appended first is correctly excluded by index order; an attestation entry first correctly remains effective under P-6’s “attested nominee is unaffected” rule.

- **D20C2-S-2 — BLOCKER — §1.6, QC1.** A revision, invalidation or termination can occur before `R₀`; §1.3 then refuses the backstop’s release. A continuing store outage can also prevent release past `C+14 days`, despite §1.6’s guarantee. Thus “every read is released” and QC1’s “no result can stay hidden” are not established. **Minimal repair:** describe event-time attempts as pending until `R₀` and service recovery; keep the cycle report incomplete while any counted read lacks a release. State the completion target conditionally, without a guaranteed date. The pending list and `ANCESTOR_UNRELEASED` use public accounting facts and add no result-dependent channel. A backstop result shown in a cycle report after termination is consistent with the reader row, even if RESULT delivery has not occurred.

- **D20C2-S-3 — BLOCKER — §1.7, QC3.** “None of these can change a result” is true only **after durable release**. Before that, resource contention can delay a would-be PASS finish past `D*`; `mark_finished` then refuses it and release gives the default technical FAIL. No committed PASS turns into FAIL, but the owner wording hides this deadline effect. **Minimal repair:** limit the invariant to an already released result and disclose that delays before a counted finish can cause technical FAIL.

- **D20C2-S-4 — BLOCKER — §1.1, §1.8.** The proposed Constitution §7 row says it permits no added research-visible “message” and limits visible records to times, pending list and stopped state. §1.1 nevertheless supplies six fixed response codes, including certificate status; `STOPPED` also covers unknown IDs and request errors, not only an incident stop. **Minimal repair:** make the proposed exception enumerate the permitted fixed codes and public accounting facts, and describe `STOPPED` as an undifferentiated refusal whose cause is withheld. Put that exact interface to the owner in QC3.

- **D20C2-S-5 — NON-BLOCKING — §1.1, §1.5, TC-4.** If C or a revision arrives before any attestation exists, `sign_permit` refuses and writes nothing. Requests can then return `PASS_CERTIFICATE_PENDING` indefinitely although certification is impossible; `PASS_NOT_CERTIFIABLE` currently requires VOID. **Minimal repair:** define the terminal response at cap or revision without requiring a certificate-delivery attempt, and test it.

- **D20C2-S-6 — NON-BLOCKING — inheritance and §1.9.** C2 retains rev 8 T-S2 and T-S6 while superseding `state`; [T-S2](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV8.md:138>) still asserts what concurrent `state` shows, and [T-S6](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV6.md:169>) tests its payload. **Minimal repair:** replace those assertions with C2’s release, delivery and fixed-code interfaces; list these test clauses in §1.10.

The cap counterexample is exact: a check at `C−1` followed by durable append at `C+1` is **two seconds across the boundary**. Likewise C2’s own example gives `C−73 h + 48 h = C−25 h` for delivery and `C+47 h` for the earliest 72-hour decision. These are boundary calculations, not timing or platform tests.

**Recommendation:** keep C2 blocked, repair the claims and owner questions above, then obtain the required independent re-check and human decisions. The narrower release-on-request design remains a candidate; returning to daily releases or adding an isolation mechanism is not required by these findings. No implementation tests, lint or type checks apply to this read-only proposal review. I wrote nothing; this response is **not a committed repository review record**.
## Prompt

# Re-check: D-20 option C, revision C2

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/statistical-binding-review/SKILL.md`. Re-check `review/governance-statistics-amendment/d20-lockbox-proposal/OPTION_C_PROPOSAL_REV2.md` (Claude Opus 5.5, commit a56f220). It replaces C1 whole and is a delta on `PROPOSAL_REV8.md`. It answers `SOL_OPTION_C1_REVIEW_C604827.md` (D20C1-S-1..7) and `ASTRA_OPTION_C1_REVIEW_C604827.md` (D20C1-A-1..8). Context: `PROPOSAL_REV8.md`, `PROPOSAL_REV3.md` l.176-220 and l.305-311, `PROPOSAL_REV4.md` l.92-110 and l.175, `../d12-proposal/OWNER_DECISION_D12.md`, `../d12-proposal/PROPOSAL_REV7.md` (P-1..P-8, R1-R4, T-1..T-8), `docs/RESEARCH_CONSTITUTION.md` (§5, §6, §7, §13, §16, §26), `schemas/attestation.schema.json`, `docs/THREAT_MODEL_v1.md`, `protocols/protocol_v1.yaml`.

**Direction:** simplify rather than patch; claim only what is true and testable. Prefer flagging a residual for honest disclosure over demanding new mechanism, unless the claim made is false or a frozen rule is broken.

**IDs:** findings `D20C2-S-n`. Use exactly that prefix even if you cannot see your model variant; the caller verifies the model from the CLI header.

**Check:**
1. For EVERY C2 disposition of the C1 findings (§1a), say ACCEPT, ACCEPT WITH NOTES or FIX, with evidence. You may check the other reviewer's rows.
2. §1.3: the recovery-aware proof and step 2a; the clock list; rev 8's qualification and the Q7 routing.
3. §1.4: delivery idempotency, `L_pub`, owner-account read-back; is `delivered_at` truly never earlier than the owner's durable copy under every crash and concurrency case? Is the "uncertain completion" (whole-but-unfsynced entry) handling consistent with rev 8 and Q7?
4. §1.5 (focus): `cooling_off_start` = RESULT `delivered_at`, signed after it; conformance with Constitution §13 and the frozen schema; `sign_permit`; effectiveness as one append with VOID; index-ordered revision entries; P-6 l.245 ("attested nominee is unaffected"). Can a signature become effective after C or after a revision, can cooling-off give under 72 h of actual access, or can a PASS become FAIL?
5. §1.6: backstop at `R_0 + 7 days` and at revision/invalidation/termination; pending list; completion; `ANCESTOR_UNRELEASED`. Does the backstop add a channel? Is the reader row consistent with the cycle report showing backstop-released results?
6. §1.7-§1.8: is the residual now complete and accurately stated, and does the §7 row cover exactly it?
7. §1.1 codes and capabilities, §1.9 crash rows and tests, §1.10 superseded clauses (complete?), §2 crosswalk, §3 comparison, §4 owner questions (fair and plain for a non-statistician).

**Findings:** each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario and minimal repair.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
