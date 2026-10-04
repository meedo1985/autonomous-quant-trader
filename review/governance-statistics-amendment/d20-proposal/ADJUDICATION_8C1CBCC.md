# Adjudication of VF2 (Fable) and VS2 (Sol) on the D-20 V binding rev 2 at `8c1cbcc`

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter

**Records:**
- `FABLE_REVIEW_8C1CBCC.md` (`fe9b0bc`): READY WITH FIXES
- `SOL_REVIEW_8C1CBCC.md` (`8ab8d78`): NOT READY

**Result:** `V_BINDING.md` revision 3. The engine changes are in `80315dd` and `e021207`.

Every finding is accepted.

| Findings | Disposition |
|---|---|
| VS2-1 (BLOCKER), VF2-1 | **The runtime check is mandatory.** V raises a `U_ops` error unless `v_runtime_check(expected)` has passed in the process. `expected` is required, and entry points pass the frozen identity from the qualification object. The pilot prints the identity it ran on. Tests cover running V unchecked, and, in a fresh process, a matching identity, a mismatched identity and a missing environment. |
| VS2-2 | `fsum` overflow on extreme finite inputs is `INVALID_REPLICATE`, covered by a test. |
| VF2-2 | **Rule 5 is now exact in both directions.** Flagged columns that hold distinct values are recomputed with the Task 12 two-pass. |
| VF2-3 | The base interpreter executable and its shared library are hashed. |
| VF2-4 | The Task 12 decision is recorded for every reference vector. Agreement is required, except on vectors designated near-degenerate before the freeze, where any difference is disclosed. |
| VF2-5 | The owner question now states that V's result counts when V and the original calculation disagree, and that the difference is disclosed. |

**Note.** The pilot timing run after these changes (11.0 s per replication at `K = 80`) overlapped with a Sol review that was running on the same machine. The changes add almost no cost, so the re-measurement at idle stays as in rev 2 (6.7 s) until a clean run is recorded.
