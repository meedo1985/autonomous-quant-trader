# Owner decision: D-11 (lockbox prediction and pass rule L-1..L-4)

**Decision by:** the owner, in the Claude Code session on 2026-10-25, answering three questions.
**Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`). The AI made no decision.
**Basis:** `PROPOSAL.md` (c870152), `PROPOSAL_REV2.md` (845a516) and `PROPOSAL_REV3.md` (6ce228c), all by claude-fable-5-1. R19-2 reviews by gpt-6-sol and gpt-6-astra: `SOL_REVIEW_C870152.md`, `ASTRA_REVIEW_C870152.md`, `SOL_REREVIEW_845A516.md`, `ASTRA_REREVIEW_845A516.md`, `SOL_REREVIEW2_6CE228C.md`, `ASTRA_REREVIEW2_6CE228C.md`. Adjudication: `ADJUDICATION_REV3.md` (edf469d), which also holds the questions exactly as asked.
**Disclosed before the decision:** the review rounds ended without an ACCEPT verdict, and the last repairs were not re-reviewed. Per R19-2, no human statistician reviewed this.

## Answers (option labels chosen, verbatim)

1. **Q1 (main BTC lockbox test): "Average daily difference (Recommended)".** Route A: L-1 and L-2 use E-DIFF (the Sharpe of the daily candidate-minus-benchmark series), and the frozen l.84–91 text is kept.
2. **Q2 (history read and execution contract): "Yes, add to C2 (Recommended)".** The C2 §4 amendment must amend Constitution §7a and the threat-model permission so that `lockbox_eval` may read BTC/ETH 1h bars over [2022-11-13, 2025-05-31) and run the registered strategy itself (PROPOSAL_REV3 §4). Both legs start flat at 2025-06-01, each paying its entry cost at its first permitted entry. Research receives PASS/FAIL only.
3. **Q3 (historical window): "Keep as held-back check (Recommended)".** The C2 amendment must state, at the level of Constitution §0, that "future data" means later than confirmation and held back from research. The lockbox [2025-06-01, 2026-09-01) is kept as a **historical held-back check, not a fresh test**. Its prices are public, and it cannot detect strategies shaped by them. Fresh evidence comes only from later paper trading under its own pre-fixed rules.

## Recorded meaning

- **D-11 is decided as Route A** (PROPOSAL_REV2 §2–3 with REV3's §2, §4 and §7 changes):
  - m = 457 days;
  - the stationary bootstrap of d, with blocks chosen from the Sharpe influence process ψ of d;
  - 2,000 attempts;
  - type-7 5th percentile, with the float64 reference result deciding (the proposed numerics rule, now adopted);
  - L-1: T ≥ q; L-2: T > 0; L-3: the drawdown difference ≤ 0.05 over the lockbox; L-4: C-3 on ETH;
  - fail-closed availability;
  - terminal-status sealing of both families before the first read, where (d) takes precedence over (c);
  - each family's read is budgeted, logged and has its own evaluation ID.
- **Carried forward as conditions (not decided here):**
  - **D-20 must define** the stored artifact identity and verified retrieval path for the nominee's trial code, configuration and model seed (D11R3-S-1). It must also bind the confirmation baseline's start state (D11-16), the lockbox seed source and stream identity, the m≠n index generator, the ψ reference vectors, and the R-8 extension for `max_drawdown`.
  - **D-12** (the coarse attestation fields versus PASS_FAIL_ONLY) is still open.
  - **D11-15** (which of the day-255 and 75-day timing rules governs) goes to the S4 draft.
  - **The §16 review of `lockbox_eval`** is still to come.
- **Binding only through the owner's signed C2 §4 amendment.** This record activates nothing. It changes no frozen file, and it authorises no code, data access, promotion or trading.
