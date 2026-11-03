# Independent review: D-20 lockbox binding proposal

You are an independent adversarial reviewer. You work read-only and you are not an authority. The owner, who is not a statistician and is trading his own capital, makes the decision. This review is one of the two different-model AI reviews that owner decision R19-2 (`review/governance-statistics-amendment/d19-recommendation/OWNER_STEP0_DECISION.md`) requires in place of a human statistician.

**What to review:** `review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL.md`. Claude Opus 5.5 drafted it under `.agents/skills/statistical-binding-review/SKILL.md`; read that skill and follow its method.

**Verify it against:**
- the owner decisions it builds on: `d11-proposal/OWNER_DECISION_D11.md` (with `PROPOSAL_REV2.md`, `PROPOSAL_REV3.md`), `d12-proposal/OWNER_DECISION_D12.md` (with `PROPOSAL_REV7.md` §3 and §5), `d20-proposal/OWNER_DECISION_D20_V.md`, `d20-d13-proposal/OWNER_DECISION_D20_D13.md` (with its `PROPOSAL.md` rev 6);
- `v1.1-method-candidate/HUMAN_DECISION_MATRIX.md` l.72 and l.80, and `IMPLEMENTATION_CONVENTIONS.md`;
- the frozen `protocols/protocol_v1.yaml` (lockbox section, l.266, l.294-300), `docs/RESEARCH_CONSTITUTION.md` (§7, §13, §16, §27) and `docs/THREAT_MODEL_v1.md`;
- the C2 draft `s4-amendment-draft/DRAFT_WORDING.md`;
- the code it cites (`src/aqt/metrics/statistics.py`, `calibration/`, `src/aqt/core/`).

All folder paths above are under `review/governance-statistics-amendment/`. Write nothing.

**Check:**
1. Is each row (A1-A6, B1-B6) exact enough to implement and test, and does it bind to the right existing code? Check especially:
   - the stream layout and the claim that the new generator reproduces `bootstrap_indices` when m = n;
   - which influence process sets the block length (D20L-1, D20L-2);
   - the float64 quantile rule (1999/20);
   - the `max_drawdown` extension;
   - the baseline start state.
2. Is the lockbox seed proposal sound? Does it really prevent an offline search before the post, and does it conflict with any frozen anti-probing rule or with the D20_D13 seed decision?
3. Does anything contradict the D-11 or D-12 decisions, the frozen texts or day 255? Are the TECHNICAL / CHOICE labels honest, or is a real choice hidden as technical?
4. Are findings D20L-1..D20L-14 right, and is anything missing? Consider, for example: key custody and rotation for the signer, and whether R-14 (Q3) really blocks lockbox code.
5. Are the owner questions Q1-Q4 fair and answerable by a non-statistician? Is each recommended option honest, and is any needed decision missing?
6. Is anything over-engineered? Name machinery that could be dropped.

**Findings:** use IDs `D20LR-<reviewer>-n` (Codex Sol: `D20LR-S-n`; Codex Astra: `D20LR-A-n`). Give each finding a severity (BLOCKER, NON-BLOCKING or QUESTION), a place, a failure scenario and a minimal repair. State your own model name as shown in your session metadata.

**Verdict:** ACCEPT, ACCEPT WITH NOTES, or FIX.
