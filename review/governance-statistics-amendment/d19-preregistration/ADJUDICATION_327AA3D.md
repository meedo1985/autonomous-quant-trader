# Adjudication of DF5 (Fable) and DS5 (Sol) on the D-19 preregistration rev 5 at `327aa3d`

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter
**Records:**
- `FABLE_REVIEW_327AA3D.md` (`df65001`): READY WITH FIXES
- `SOL_REVIEW_327AA3D.md`: READY WITH FIXES

**Result:** `PREREGISTRATION.md` revision 6. Every finding is accepted and applied as the reviewer proposed.

| Findings | Disposition |
|---|---|
| DS5-1 (MAJOR), DF5-3 | `D_Q2` is removed from the acceptance tuple and bound only in the attempt-2 record, before its post. |
| DF5-1 | A void attempt uses up its key. When no key remains, qualification has not been obtained, and a further key needs a new acceptance. |
| DF5-2 | Before the run, a check of the O-6a invalidation conditions and a run-start record are committed. An invalidation not listed in that check counts as a post-start failure. |
| DF5-4 | The opposites row cites the §3.1 `Σ`, with no further negation. |
| DF5-5, DS5-2 | Q2m: columns `j < ceil(K/2)` are t₅. Scales are 0.5 for even `j` and 2 for odd `j`. Both laws have both scales at `K ≥ 5`; the confounding at `K = 2` is stated and accepted. |
| DS5-3 | `M_max ≈ 1,167` (379 cells). The τ values and critical counts are unchanged. |

Fable said these need no further review round. Sol asked for a narrow re-check, which is run on revision 6.
