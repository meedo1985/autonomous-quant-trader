# Independent review: D-12 decision proposal (lockbox attestation coarse fields)

You are an independent adversarial reviewer. You work read-only and you are not an authority. The owner, who is not a statistician and is trading his own capital, makes the decision. This review is one of the two different-model AI reviews that owner decision R19-2 (`review/governance-statistics-amendment/d19-recommendation/OWNER_STEP0_DECISION.md`) requires in place of a human statistician.

**What to review:** `review/governance-statistics-amendment/d12-proposal/PROPOSAL.md`. Claude Fable 5.1 drafted it under `.agents/skills/statistical-binding-review/SKILL.md`; read that skill and follow its method.

**Verify it against:**
- the frozen `protocols/protocol_v1.yaml` (l.67, l.75-95, l.294-300);
- `docs/RESEARCH_CONSTITUTION.md` §7, §8, §13, §16, §26 and §27;
- `schemas/attestation.schema.json`, together with its sidecar;
- `docs/THREAT_MODEL_v1.md`;
- the owner D-11 decision `review/governance-statistics-amendment/d11-proposal/OWNER_DECISION_D11.md`, including the rev 3 proposal and the adjudication it adopts;
- the C2 draft `review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md` (§2, §2.3, l.82, l.325-356).

Write nothing.

**Check:**
1. Is Route 1 a faithful reading that changes nothing frozen? In particular, is it correct that an attestation exists only for a PASS (because `cooling_off_start` is required), so that the three coarse fields appear only on a PASS? Does any frozen text require an attestation or coarse fields on a FAIL?
2. Is the lemma correct that PASS implies (positive, true, true) under D-11? Are the field definitions exact, including the float64 sign, `-0.0`, the residue, the consistency with L-1/L-2, and the treatment of L-3 and L-4?
3. Is the recipient table correct and leak-free? Check the binary research channel; UNAVAILABLE reported as FAIL; the public log index against the sealed bundle; the owner's lack of raw lockbox access; and the second-family separation, including D12-6 (lineage) and D12-7 (human approval).
4. Are findings D12-1..D12-8 right? Is anything missing, for example:
   - what the PASS/FAIL timing or the existence of an attestation reveals;
   - how logging the EXPOSED mark interacts with this;
   - §27 reproduction against the read budget;
   - verification-failure logging;
   - what D-20 inherits.
5. Are the owner questions Q1-Q2 fair, complete and answerable by a non-statistician, and is the recommended option honest? Is any decision missing, such as the D12-3 or D12-8 readings?

**Findings:** use IDs `D12R-<reviewer>-n` (Codex Sol: `D12R-S-n`; Codex Astra: `D12R-A-n`). Give each finding a severity, a place, a failure scenario and a minimal repair.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
