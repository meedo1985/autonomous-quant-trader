# Owner decision: D-12 (lockbox attestation coarse fields versus PASS_FAIL_ONLY)

**Decision by:** the owner, in the Claude Code session on 2026-10-26, answering eight questions in two forms.
**Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`). The AI made no decision.
**Basis:** `PROPOSAL_REV7.md` at e1b263b (revision 6 by claude-fable-5-1; revision 7 edits and the §7b wording by claude-opus-5-5), which holds the full questions in §6. R19-2 reviews by gpt-6-sol and gpt-6-astra: `SOL_REVIEW_55554C6.md`, `ASTRA_REVIEW_55554C6.md`, the five re-check rounds `SOL_/ASTRA_REREVIEW*_*.md` (all FIX), and the focused confirmations of revision 7, `SOL_CONFIRM_1E88935.md` and `ASTRA_CONFIRM_1E88935.md` (both ACCEPT WITH NOTES, 0 BLOCKER).
**Disclosed before the decision:** both confirmations had no blocker. Not stated in the question forms: their four wording notes (D12R7-S-1..2, D12R7-A-1..2) were applied in §7b (e1b263b) and were not re-reviewed; §7b states that no rule, test or question changed. Per R19-2, no human statistician reviewed this.
**How the questions were asked:** each option label was shortened to fit the form, and each option carried a one-line summary of the §6 text. The mapping below names the §6 option each answer selects.

## Answers (option labels chosen, verbatim)

1. **Q1 (what a result tells you): "PASS or FAIL only (Recommended)".** §6 option "PASS or FAIL only". The three items appear only on a PASS certificate; no Constitution §7 row for Q1.
2. **Q2a (cycle label for a technical FAIL): "Allow it, openly (Recommended)".** §6 option "Allow it, stated openly". C2 needs a Constitution row changing §7 l.79 for this one cycle-label fact, applying to later cycles too; this also settles D12-30 (DRAFT l.82 stays, now matched by the §7 exception).
3. **Q2b (reason for a pre-read stop): "Show the reason (Recommended)".**
4. **Q3 (descendant after a FAIL): "Not read; any FAIL counts (Recommended)".** §6 option "The later pick is not read, and any FAIL counts, including a technical breakdown".
5. **Q4 (reproducibility): "Record all; re-run later (Recommended)".** §6 option "Record everything; re-run later once the period becomes confirmation data" (route R-a). No second counted read.
6. **Q5 (sealed details): "No, sealed (Recommended)".**
7. **Q6(i) (who posts): "Separate posting job (Recommended)".** §6 option "A separate posting job that cannot read lockbox data". C2 must change THREAT_MODEL l.9 accordingly; the posting code needs §16 review.
8. **Q6(ii) (day-255 cap): "Visible+72h+decided by 255 (Recommended)".** §6 option "A pick must be visible, cooled off for 72 hours and decided by you by day 255; results already finished keep their outcome". O-2 is unchanged.

## Recorded meaning

- **D-12 is decided as PROPOSAL_REV7 §3 (P-1..P-8)** with the recommended option on every question:
  - P-1 PASS-only attestation; a FAIL carries no item values;
  - P-3 every technical FAIL counts as a lockbox FAIL, with the Q2a cycle-label fact disclosed openly;
  - P-5 cooling-off from `R_j`, 72 hours counted in hours of reader-path availability;
  - P-6 cap wording per Q6(ii); P-7 fixed daily release; P-8 validation by a separate publisher.
- **Carried forward as conditions (not decided here):**
  - **The signed C2 must carry:** the Constitution §7 l.79 row for the Q2a fact; the clarifying sentence of D12-31 if the owner adopts it; protocol rows P-1..P-8; the THREAT_MODEL l.9 change for the publisher identity.
  - **D-20 must bind:** the record shapes (§3 Records), the signature scheme, the publisher identity and key, `R_0` and `D_w`, and tests T-1..T-8 (§5 checklist).
  - **§16 review** of the lockbox access tooling, the publisher and the results store.
  - **Residual channels R1-R4** are accepted as disclosed, not removed.
- **Binding only through the owner's signed C2 §4 amendment.** This record activates nothing. It changes no frozen file, and it authorises no code, data access, promotion or trading.
