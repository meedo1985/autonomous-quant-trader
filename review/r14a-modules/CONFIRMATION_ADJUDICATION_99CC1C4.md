# Adjudication of the Sol re-check 5 of confirmation slices 1-3 at 99cc1c4 (`SOL_CONFIRMATION_RECHECK5_99CC1C4.md`)

Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-07. The finding is accepted and repaired.

| ID | Verdict | Repair |
|---|---|---|
| R14C6-S-1 | AGREE | `check_eligibility` no longer takes a free `window_end`. It takes `c2_end`, the signed C2's inclusive `partitions.confirmation.end`, requires it to equal `V1_CONFIRMATION_END` = 2025-05-31T23:59:59Z (`protocol_v1.yaml:66`; the C2 `partitions` binding keeps that end), and computes T over `[w0, c2_end + 1 s)`. With g = 30, T = 1217 and the window ends exactly at 2025-06-01T00:00:00Z, so `nominate`'s expected index is every day of the partition, no fewer and none past it. That each of those days is present in the data stays the loader's manifest check (slice 6). Test: `test_eligibility_recomputed` uses the bound end, checks T = 1217 and the exclusive end, and refuses the end one day early, one day late and one second late; the T_min check now uses `t_min = 1218`. |

Mutation check (cycle tests rerun; each caught, 1 failed): C2 end not checked; the last partition day dropped from the window.

Validation: see the commit message for the exact commands and results.
