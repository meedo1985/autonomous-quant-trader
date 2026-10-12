# Adjudication of BF5 (Fable) and BS5 (Sol) on the D-19 §13 rev 7f at `02c14e5`

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter

**Records:**
- `FABLE_REVIEW_02C14E5.md` (`d69fe25`): READY WITH FIXES (one minor advisory finding)
- `SOL_REVIEW_02C14E5.md` (`d46c870`): READY WITH FIXES (one minor finding)

**Result:** `PREREGISTRATION.md` §13 rev 7g.

Both findings are accepted. Both are minor and touch only the cost estimate and one sentence of wording; nothing statistical changes. No further review round is planned. Rev 7g goes to the owner, together with these records.

| Finding | Disposition |
|---|---|
| BS5-1 | **No independence is assumed for the QJ escape cost.** Each QJ cell is budgeted at 0–50 hours, so the two QJ cells add 0–100 hours. The scenario totals become ranges: about 6,000–6,200, 6,700–6,800 and 7,200–7,300 server-core-hours. The month figures (about 4, 4½ and 5) do not change. The re-pilot measures the joint QJ escape rate directly. |
| BF5-1 | **libc is gated through the image digest.** It is not a separate identity field, and §13 now says so. No engine change is needed. |
