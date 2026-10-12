# Adjudication of BF4 (Fable) and BS4 (Sol) on the D-19 §13 rev 7e at `9d811e6`

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter
**Records:**
- `FABLE_REVIEW_9D811E6.md` (`23ce5f4`): READY WITH FIXES (minor only)
- `SOL_REVIEW_9D811E6.md` (`026a23a`): READY WITH FIXES

**Result:** `PREREGISTRATION.md` §13 rev 7f. Every finding is accepted.

| Findings | Disposition |
|---|---|
| BS4-1, BF4-1 | **Escape cost.** The cost is now 25·E[ordinary escapes] + 50·E[QJ escapes]. Each QJ cell's escape probability counts both of its `U_G` tests (about 0.38, 0.65 and 0.68, assuming the tests are independent). The scenario totals are about 6,100, 6,800 and 7,300 server-core-hours, which is about 4, 4½ and 5 months. A run with no escapes would take about 5,400, shown separately. The scenarios are labelled conditional on the assumed rates. |
| BS4-1, BF4-2 | **Re-pilot.** The re-pilot list now matches item 3: `U_G` and DSR-availability rates in the thin categories. It adds an all-groups `U_G` rate, taken from at least one cell of each group. The go-ahead estimate uses that measured rate. |
| BF4-3 | **"Platform" defined.** It means the operating system and machine architecture inside the image, plus the image's libc, without the host kernel release. The engine's `runtime_identity` already records `platform.system()` and `platform.machine()` only (branch `d19-calibration-engine`, `calibration/dsr.py`), so no code change is needed for this. The host kernel release is now host provenance. |
| BS4-2 | **History row.** Rev 7e's row now cites the committed BF4 and BS4 records and their verdicts. Rev 7f's row says "awaiting fix-check". |
