# Adjudication of the reviews of the D-06/D-07 proposal rev1 (`abcc2c9`)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`). Reviews:
`FABLE_REVIEW_ABCC2C9.md` (FF1, SOUND WITH FIXES, `ffbe94e`) and
`SOL_REVIEW_ABCC2C9.md` (SF1, SOUND WITH FIXES, `626b24f`). All findings are
accepted; none is rejected. Applied in revision 2 without a further check [AI
default].

| Finding(s) | Disposition in rev 2 |
|---|---|
| FF1-1 | C-1/§3: the trigger is a full cash quarter (a constant leg); the wrong example is removed; the 2022 bear market is noted; `U_proc` is treated as a qualification target |
| FF1-2, SF1-6 | §5 owner question lists every binding and consequence; options accept-loss / accept-unavailable / revise / reject / keep blocked |
| FF1-3, SF1-4 | §3 choice table (a)/(b)/(c); recommends (b) non-win for valid zero-variance blocks; data-integrity failures stay `UNAVAILABLE` |
| FF1-4 | §7a cited; partial block reported only via metrics.json / report.md; C-3 |
| FF1-5, SF1-2 | §1 separates definitions from candidate bindings that become §4 text |
| FF1-6 | P6-1: BTC, 1x cost |
| FF1-7 | P6-3: no partial block when `e` falls on a boundary; exclusive end `e`; a partial block that cannot be computed is reported only |
| FF1-8, SF1-1 | P6-2: target-month end clipping, computed from `s`, never chained, half-open `[s, e)` at 00:00 UTC |
| FF1-9, SF1-3 | P6-5: `B_min` removed; `T_min` governs; zero complete blocks → `UNAVAILABLE`; non-monotone pass rate noted for D-19 |
| FF1-10 | P6-4: noted as redundant with Task 12; cause code follows P18-7 precedence (`U_ops` for infrastructure) |
| FF1-11 | §1 maps each D-06 matrix item to its rule |
| SF1-5 | C-2: 29% labelled as an exchangeable-independent illustration; no 28-day cap assumed (13 blocks for any gap 0–29) |
