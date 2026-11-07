# Adjudication of the Sol re-check 4 of confirmation slices 1-3 at e3348bf (`SOL_CONFIRMATION_RECHECK4_E3348BF.md`)

Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-07. The finding is accepted and repaired.

| ID | Verdict | Repair |
|---|---|---|
| R14C5-S-1 | AGREE | Verified against DRAFT_WORDING R-3 ("the eligible window starts at partitions.confirmation.start") and its `partitions.confirmation.start` binding (`2022-01-01T00:00:00Z + gap_embargo.value_days`): the bound C2 start already contains g, so adding g again started the window g days late and turned valid series into `MISALIGNED_SERIES`. `check_eligibility` now takes `c2_start` (the signed C2's `partitions.confirmation.start`), requires it to equal exactly `V1_CONFIRMATION_START` (`protocol_v1.yaml:66`, 2022-01-01T00:00:00Z) plus g, and uses it as w0. This also corrects the R14C-S-3 repair, whose docstring read the unshifted partition start. Test: `test_eligibility_recomputed` now passes the bound field; it checks w0 is not shifted again and refuses an unshifted or off-by-one-day C2 start. |

Mutation check (cycle tests rerun; each caught, 1 failed): g added a second time to the C2 start; the C2 start not checked against v1 start + g.

Validation: see the commit message for the exact commands and results.
