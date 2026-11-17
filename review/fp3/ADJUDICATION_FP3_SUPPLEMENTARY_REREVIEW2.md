# Adjudication: re-reviews 2 of the FP3 supplementary acceptance draft, revision 3

Records: `SOL_FP3_SUPPLEMENTARY_REREVIEW2.md` (gpt-6-sol, FIX, FP3S3-R1..R3) and `FABLE_FP3_SUPPLEMENTARY_REREVIEW2.md` (claude-fable-5-1, FIX, FP3S3-G1..G5). Adjudicated by Claude Opus 5.5 (the drafter), 2026-10-25.

The findings are accepted: a relay's latest round does not prove global publication time (R1); the check time could decide late-publication cases (R2, G1); a later latest-round report is not proof of timely publication (R3); evidence search before attempt 2's post could depend on the result (G2); endpoint matching and independence were loose (G3); the daily-check start was impossible (G4); the header was stale (G5).

**Resolution: the void rule is withdrawn.** These are not wording defects: the drafter judged that any 7-day cutoff requires proof of when drand published, which cannot be obtained cleanly from outside. The owner was given that tradeoff and chose "No time limit (Recommended)" (`OWNER_PREFERENCES_2026-10-25.md` item 7, superseding items 3, 5, 6). Revision 4 has no void for a missing output, so R1, R2, R3, G1, G2, G3 and G4 have no remaining subject. G5: the header now says "Revision 4".
