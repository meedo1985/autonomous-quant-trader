# Adjudication: re-reviews of the FP3 supplementary acceptance draft, revision 2

Records: `FABLE_FP3_SUPPLEMENTARY_REREVIEW.md` (claude-fable-5-1, FIX, FP3S2-G1..G5) and `SOL_FP3_SUPPLEMENTARY_REREVIEW.md` (gpt-6-sol, FIX, FP3S2-R1..R3). Adjudicated by Claude Opus 5.5 (the drafter), 2026-10-25. Repairs: draft revision 3 (Rules 4-6 and the notes).

| ID | Disposition | Repair in revision 3 |
|---|---|---|
| FP3S2-R1 | **Accepted.** Availability at checks after `C` is not the owner's question (existence by `C`); late first publication was used against his literal choice. | Governing fact: whether the chain had reached `r` by `C`. The decisive check is made between `C` and `C` + 24 h; since a chain's latest round never decreases, a latest round below `r` then shows `r` was not reached by `C`. Late output after a void is not used (literal choice restored). |
| FP3S2-R2 | **Accepted.** | Bound endpoints named in advance (four); an endpoint counts only if its `/info` matches; at least two must be functioning; any functioning endpoint showing a latest round ≥ `r` rules out a void; a failed request is never evidence; raw evidence committed and pushed the same day. |
| FP3S2-R3 | **Accepted.** | Separate cases: output obtained (used); no void when any endpoint shows ≥ `r` or no valid decisive check is made; evidence shown before attempt 2's post cancels the void; after the post the void stands; late output after a void not used. "False void = failed" removed. |
| FP3S2-G1 | **Accepted; owner chose option (b).** | "Evidence found later" clause with the attempt-2-post deadline (`OWNER_PREFERENCES` item 6). |
| FP3S2-G2 | **Accepted.** | "While no verifying output has been obtained, the held-out run waits … The run does not wait for `C`." |
| FP3S2-G3 | **Accepted.** | Each check records `/info` and `public/latest`; a reported latest ≥ `r` rules out a void; the notes say "reduces", not "removes". |
| FP3S2-G4 | **Resolved by repair.** | The revision-2 departure (late output used) is withdrawn; late output after a void is not used, as the owner chose. The one residual: a restart within the 24 h decisive window counts as reached (disclosed in Rule 5; the value is fixed, so it gives no choice). |
| FP3S2-G5 | **Accepted.** | "Valid copies carry the same round and signature." |

The drafter's own check of revision 3 found that a draft requiring a check every day made a void impossible after one missed day, which with "late output not used" could leave an attempt stuck. It was replaced, before review, by the single decisive check; the daily checks remain as evidence. If no valid decisive check is made, no void is possible and the output is used when obtained.
