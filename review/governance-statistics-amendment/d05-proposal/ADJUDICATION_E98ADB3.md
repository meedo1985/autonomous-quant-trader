# Adjudication of the reviews of the D-05 proposal rev1 (`e98adb3`)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`). Reviews:
`FABLE_REVIEW_E98ADB3.md` (FP1, SOUND WITH FIXES, `eed8265`) and
`SOL_REVIEW_E98ADB3.md` (SP1, SOUND WITH FIXES, `30c0a2c`). Both endorse
failing an available `v <= 0`. All findings are accepted; none is rejected.
They are applied in revision 2 without a further check [AI default].

| Finding(s) | Disposition in rev 2 |
|---|---|
| FP1-1, SP1-2 | Ordered evaluation: an unavailable `v` or neighbour gives `UNAVAILABLE` before any `FAIL` (§3 steps 1–4) |
| FP1-2 | Precedence stated: step 2 (unavailable) before step 3 (`v <= 0`) |
| FP1-3, SP1-1 | "Close to half" and "unreachable" removed; the share depends on the null cell; (b) split into (b1) `UNAVAILABLE` and (b2) `N/A` |
| FP1-4, SP1-3 | The relation to G-1 is an untested hypothesis; the same-series condition and the 1,900/2,000 condition are stated; the case where (a) newly blocks promotion is disclosed |
| FP1-5, SP1-6 | §1 restated precisely, with FP1's worked case |
| FP1-6, SP1-4 | "Available neighbour" = present in the grid [AI default], stated as a binding (C-2); the median of an even count and pooling across dimensions are defined |
| FP1-7, SP1-5 | `v = 0` treated as a live structural boundary and included in `FAIL`; the reference float64 result decides |
| FP1-8, SP1-7 | Neutral owner question, one consequence per option, including keep-blocked and the no-statistician disclosure |
| FP1-9 | Citation corrected to `statistics.py:591–651` |
| FP1-10 | Peak-semantics consequence of D-04 disclosed (C-4) |
