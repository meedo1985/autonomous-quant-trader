# Adjudication of the two reviews of the broadened method design rev1 (`6481f28`)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`), author of the
design, so not independent; decides nothing. Records:
`SOL_REVIEW_6481F28.md` (SB1-1..SB1-9, UNSOUND as written),
`FABLE_REVIEW_6481F28.md` (FB1-1..FB1-17, SOUND WITH FIXES).

## Agreement

Both accept the core: a joint recentred stationary block bootstrap of the
declared family is a defensible way to supply the expected null maximum
`S0`, and an effective-count scalar becomes unnecessary within a cycle.

| Topic | Sol | Fable | Adjudication → revision 2 |
|---|---|---|---|
| "Largest PW length is conservative" is false; `L > T/4` can never fire | SB1-3 | FB1-1, FB1-4 | Accept. Claim withdrawn; rule deleted; block rule chosen in D-19 development from {largest, median}; cap-binding is a support boundary; `L/T` a classifier covariate. |
| Supported domain must be explicit (short memory, finite variance); long memory, breaks, infinite variance are challenges | SB1-2 | FB1 Q1, FB1-5 | Accept (§2.6). Block length from the null influence `u` (FB1-5). |
| Seeds / stream purpose / conventions; `T_min` not an AI default | SB1-4 | FB1-7, FB1-8 | Accept: family seed from the canonical declaration; `T_min` from development, checked at eligibility, not `U_proc`. |
| Lifetime count: per-cycle claim only; cross-cycle accumulation is an owner budget question | SB1-5, SB1-8 | FB1-12 | Accept: B-5; both bounds reported. |
| B-3 within D-18 via O18-2, but numerical meaning of `D` changes | SB1-6 | FB1-10 | Accept: B-3 restated. |
| MC error at B = 2000; calibration reruns the exact inner algorithm | SB1-7 | FB1 §2(d) | Accept (§4). |
| D-19 must be a complete preregistration | SB1-9 | FB1-16, FB1-17 | Accept (§4). |

## One reviewer only, accepted

- **SB1-1 (BLOCKER):** `D` from recentred resamples is the null variance, not
  the nominee's; shifted exponential example inflates `z` by 1.58. Fable
  FB1-10 noted the same fact as a disclosure. Accepted: `D_j` now from the
  **uncentred** resamples on the same index sequences.
- **FB1-2 (BLOCKER):** `D` and `z` must exist for every column (P18-3).
  Accepted.
- **FB1-3 (BLOCKER):** Constitution §9 line 106 governs; no count in the score
  needs a §9 amendment. Accepted; B-1, §7.
- FB1-6 (sparse columns), FB1-9 (arithmetic), FB1-11 (cell-dependent null,
  B-6), FB1-13 (citations i, ii fixed; iii inherited and labelled), FB1-14,
  FB1-15 (K lever), FB1-17 (compute): accepted.

## Correction to a reviewer citation

FB1 §2(c) cites the cap at `statistics.py:375`; at HEAD the cap is line 378
(`maximum = min(n, math.ceil(min(3 * math.sqrt(n), n / 3)))`). The value is
unaffected.

No frozen file edited; promotion stays blocked.
