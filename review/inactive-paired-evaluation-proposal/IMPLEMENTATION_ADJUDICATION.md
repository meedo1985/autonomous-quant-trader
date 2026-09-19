# Implementation review adjudication

**Date:** 2026-09-19
**Status:** all review findings adjudicated; no local blocker remains

| ID | Disposition | Resolution and evidence |
|---|---|---|
| B1 | AGREE | Replaced decimal formatting with exact numeric equality. Added the `1.04` versus `1.0` regression; it fails closed. |
| N1 | AGREE | Expected stream window now uses compact `json.dumps`, matching the existing canonical convention. |
| N2 | AGREE | Added independent assertions for both legs, all permitted horizon inputs used across tests, Newey-West, and explicit zero-variance fallback. The type docstring disclaims protocol `effective_decisions`. |
| N3 | AGREE | Added window, asset, multiplier, and invalid-type cases. |
| N4 | AGREE | Added hand-calculated mean, sample variance, paired improvement, and difference-series fixtures. |
| N5 | AGREE | The stream path now runs under selected file, environment, process, socket, and URL tripwires; global RNG and stream identity are preserved. Test name states the finite guard scope. |
| N6 | AGREE | Added validation, allocation, and monitoring to the import contract. `aqt.data.bars` remains reachable only through the required production backtester and cannot be forbidden indirectly. |
| N7 | AGREE | Added a comment explaining segment alignment before complete-day statistics. |
| N8 | AGREE | Window start and exclusive end are normalized to UTC. |
| N9 | AGREE | Replaced duplicated `interval_reason` with assembler-only `interval_absence_reason`; primitive failures remain on `interval.reason`. |
| Q1 | CLARIFIED | The prohibition concerns a module-provided export method. No type can prevent a caller from manually traversing public values; the result remains explicitly not a governed report. |
| Q2 | DEFER | Difference-series ESS is an unresolved scientific choice and remains outside authorization. |
| Q3 | AGREE | The inactive module intentionally has no package-root re-export. |

No architecture, statistical convention, threshold, frozen artifact, trial, or
governance rule was changed while resolving the review.
