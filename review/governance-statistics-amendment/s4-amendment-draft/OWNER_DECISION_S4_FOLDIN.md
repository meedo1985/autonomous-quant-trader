# Owner decision: four choices left by the S4 fold-in fidelity reviews

**Decision by:** the owner, in the Claude Code session on 2026-10-31, answering four questions in one form.
**Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`). The AI made no decision.
**Basis:**
- `SOL_FIDELITY_REVIEW_C5CB1FF.md` (S4F-S-1, S-10, S-11);
- `ASTRA_FIDELITY_REVIEW_C5CB1FF.md` (S4F-A-1, A-11, A-12);
- on the fold-in at `c5cb1ff` (`ANNEX_D_LOCKBOX.md`, `DRAFT_WORDING.md`).

No human statistician reviewed this.

**How the questions were asked:** each question summarised the issue and the reviewers' point. Each option carried a one-line summary.

## Answers (option labels chosen, verbatim)

1. **D11-15 (what ends lockbox processing): "Earlier of the two (Recommended)".**
   - Asked: the D-20 detail rules the owner adopted keep a provisional cap, the earlier of (a) day 255, counted from the archive time T of the declaration post, and (b) 75 days after the single nomination look.
   - Meaning: `C = min(T + 255 days, look + 75 days)`, as `d20-lockbox-proposal/PROPOSAL_REV3.md` B3a (l.208-209) states, kept by option C (`OPTION_C_PROPOSAL_REV2.md` l.312).
   - This settles D11-15, the question that D-11 and D-20 left open.
2. **History read endpoint (D-11 Q2): "Up to 1 June 00:00 (Recommended)".**
   - `lockbox_eval` reads history up to the lockbox start, `L0 = 2025-06-01T00:00Z`, so 31 May 2025 is included.
   - This follows D-11 `PROPOSAL_REV3.md` §4 item 4 (`[S_pre, L1)`). It resolves the bracket in `OWNER_DECISION_D11.md` l.11 ("[2022-11-13, 2025-05-31)"), which read as excluding 31 May.
3. **Reason order: "Lineage first (Recommended)".**
   - In `begin_read`, the lineage checks (`BARRED_DESCENDANT`, `ANCESTOR_UNRELEASED`) come before the budget check, so a barred descendant is recorded as D-12 P-3 names it.
4. **A7 `code` field: "Both modules (Recommended)".**
   - The prediction artifact's `code` is `{lockbox_module_sha256, confirmation_module_sha256, engine_commit, screen_object_sha256}`.
   - Each module's contract names the fields it produces.

## Recorded meaning

These answers fill choices the decided records left open: D11-15, the S4-level shape of the A7 field, and the precedence of rejection reasons. Answer 2 resolves an inconsistency inside the D-11 record. Like the rest of the C2 text, they bind only through the owner's signed C2 amendment, after the required human review.
