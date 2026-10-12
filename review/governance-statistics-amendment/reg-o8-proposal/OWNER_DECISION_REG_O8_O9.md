# Owner decision: REG-1, REG-2 (combined), O-8, O-9

**Date:** 2026-10-04
**Authority:** The owner decided these items in a Claude Code session. Each
item first went through two different-model reviews under R19-2.
- Fable: FR1 `36e24ab`, FR2 `4f230cb`, FR4 `6b7a5f2`.
- Codex `gpt-5.6-sol`: SR1 `8a68d02`, SR3 `26f3615`, SR4 `8142647`. SR2 was
  stopped by the system for low memory and produced no output.
- Adjudication: `ADJUDICATION_370C50C.md` with addenda 1–4.

The questions were asked and the answers recorded by Claude Opus 5.5
(`claude-opus-5-5`).

## Decided object

`PROPOSAL.md` revision 5, commit `8142647`, §6.

Revision 5 applied the FR4 and SR4 changes without a further check, which is
recorded as weaker. Both families had found the questions ready, subject to
those changes.

## Exchange (answers verbatim; question text as shown, abridged here only by omitting option descriptions identical to PROPOSAL §6)

1. **REG-1 + REG-2.**
   - The question: what sizing a C2 strategy may use, and whether its signal
     may use its own volatility-sizing number. If it does, the random-timing
     check partly measures a sizing mismatch rather than timing skill, which
     can wrongly pass a deliberately built strategy or wrongly fail an honest
     one. Under any choice, the 10% rule still needs a real entry signal from
     research. Nothing is activated, and no statistician reviewed this.
   - Options: "(A) Vol-target, number barred (Recommended)" / "(B) Vol-target,
     number allowed" / "(C) Add fixed-size class + (A)'s ban" / "Keep blocked".
     Each was shown with its consequences from §6.
   - Answer: **"(A) Vol-target, number barred (Recommended)"**.
2. **O-8.**
   - The question: do the order and fill rules apply to normal (baseline)
     backtests too? Checked against the code, this changes nothing beyond
     exits-to-zero. The benchmark fingerprints change, and the values are
     expected to stay the same, which is confirmed only once the new code
     exists.
   - Options: "(a) Yes, all runs (Recommended)" / "(b) Only the test runs".
   - Answer: **"(a) Yes, all runs (Recommended)"**.
3. **O-9.**
   - The question: if a cycle is invalidated after its fingerprint post, is
     the window used up?
   - Options: "(a) No, window reusable (Recommended)" / "(b) Yes, window used
     up". Option (b) stated that promotion would end for both families until
     a later amendment.
   - Answer: **"(a) No, window reusable (Recommended)"**.

## Effect

- **REG (A).** C2 sizing is vol-targeted only (the C-10 form).
  - Each trial declares `s_inputs`, and the engine gives `s` only those
    inputs.
  - `σ̂`, the sizing estimator's output and any frozen feature identical to
    it (currently `ewma_vol_168h` for a trial sized by `EWMA_168h`) are never
    among those inputs.
  - The mapping and the enforcement fall under `<<OPEN D-20>>` and §16.
  - A violation invalidates the declaration.
- **Accepted for REG (A):**
  - The ban stops only direct and accidental use. Deliberate rebuilding of
    `σ̂`, or a close proxy for it, remains possible.
  - The fixed-10% rule cannot be registered directly in C2. 10% remains a
    deployment choice under L-01..L-04.
  - Honest default-sized signals lose `ewma_vol_168h` as an input.
- **O-8 (a).** The full event contract (Annex C C-6) governs every run, baseline
  and benchmark included. The band is read through `reaches_rebalance_band`
  (FR1-7, binding `<<OPEN D-20>>`).
- **O-9 (a).** A cycle invalidated after its declaration post increments `m`
  and does not consume the eligible window.

## Not changed by this decision

- O-6a, the public channel, stays open. It is deferred to its own specification
  and review before signing.
- D-19, D-11..D-13 and D-20 stay open.
- Nothing is activated.
- No frozen file and no `HUMAN_DECISION_MATRIX.md` is edited.
- No cycle, trial, data access, deployment or trading is authorized.
