# Adjudication of the Fable and Sol narrow re-checks of the D-20/D-13 proposal rev 4 (4645e0a)

Records: `FABLE_RECHECK3_4645E0A.md` (claude-fable-5-1),
`SOL_RECHECK3_4645E0A.md` (gpt-6-sol). Adjudicated by Claude Opus 5.5, the
drafter. Revision 5 applies every disposition below.

| ID | Severity | Decision | Reasoning and evidence | Disposition in rev 5 |
|---|---|---|---|---|
| DC4-R1 | blocking | AGREE | A fresh, data-independent seed does not transfer the `U_G` rate to an attempt reached adaptively. Such an attempt is conditioned on an earlier outcome, and its data law may differ (Sol's example: unavailability driven by a data feature). | §4: the `U_G` bound is asserted only for an attempt whose declaration is fixed before any outcome on the window is seen (in practice the first). Not for adaptive attempts, and not as a frequency over retained cycles. No sequential argument is offered. The narrower point (escaping unavailability is conservative) stays. |
| DC4-R2 / DF4-R3 | blocking / note | AGREE | The allowance sum is a probability bound only if each cycle's test controls error at its allowance given the history that led to it. A re-declaration adapted to earlier results on the same window breaks that. | §4 retry paragraph and calibration bullets: `m` is the applicable multiplicity correction; the bound holds under that conditional premise; adapted re-declarations are part of the disclosed open route (DF-R10), which no allowance corrects. "(b) meets it except for the priced retries" is replaced. |
| DC4-R3 | note | AGREE | The sum is below 0.10 for any finite number of cycles and approaches 0.10 in the limit. | §4: "below 0.10 after any finite number of cycles, and at most 0.10 overall". |
| DF4-R1 | note | AGREE | Under the two checks, the C2 evaluation's own code can load only from the engine commit or an object file. | §1: the build-order consequence is stated. |
| DF4-R2 | note | AGREE | The rebuilt image left the re-pilot and the go-ahead unaddressed. | §3a (a): re-pilot measurements carry over on the proven-identical outputs; the CPU probe and the interrupt-and-resume test are redone on the rebuilt image; FE-4's image status reopens until the image PR merges. |

Nothing was left unrepaired. All of rev 5's changes narrow claims or add
notes. No binding, stream rule, option or recommendation changes.
