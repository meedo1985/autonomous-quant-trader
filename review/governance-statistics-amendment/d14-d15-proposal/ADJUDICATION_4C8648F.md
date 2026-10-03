# Adjudication of the focused checks of D-14/D-15 rev6 (`4c8648f`)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`).

Reviews:
- `FABLE_REVIEW_4C8648F.md` (FN6, NOT READY, `9a9925d`)
- `SOL_REVIEW_4C8648F.md` (SN6, NOT READY, `263af1a`)

All findings are accepted and none is rejected. They are applied in revision 7
**without a further check** [AI default]. The core construction has been stable
since revision 3, and the remaining findings concern owner choices and
definitions. Skipping a further check is weaker than running one, and that is
recorded here.

| Finding(s) | Disposition in rev 7 |
|---|---|
| FN6-1 | Accepted as structural: G-11 never tests overlay timing in any class (FN6 E1). Q2b becomes one owner decision covering all classes: (A) accept and disclose, with `constant_signal` trials `N/A` (recommended); (B) fail-closed for market-reading overlays until an overlay null exists; (C) materiality, which is undefined. Rev 6's "fail" recommendation is withdrawn. The C-2 wording is corrected. |
| SN6-1 | A declared `g11_class` field is added, with a per-run constancy check (`CLASS_MISMATCH` returns `UNAVAILABLE`). The owner's rule is described conditionally, and the sizing-registration question is put first. |
| FN6-2 | An all-tie result is `FAIL` whatever Q9 chooses. |
| FN6-3 | The owner's rule mappings are labelled as readings. Both mappings are shown: with and without an entry signal. |
| FN6-4 | Q2(a) now rests on the null keeping `σ̂` aligned, plus §12. |
| FN6-5, SN6-6 | The G-5 ETH count is "1 under Q13(a), 0 under (b)". |
| FN6-6, SN6-3 | §2.2 lists the direct market-data inputs of `s`. `s`, `σ̂`, the model and the overlay are recomputed from lagged inputs, and the targets are formed from them. The model-output claim is qualified. |
| FN6-7 | BACKTESTER l.9 and CANONICAL l.11 are cited in Q10 and C-3. |
| FN6-8 | An overlay may only keep the target or set it to 0. It cannot set or rescale size [AI default], so a fixed size is a registration question. |
| SN6-2 | Q10 options are mutually exclusive. (a) Fill time, as frozen, gives a 23 h block under stress. (b) Decision time, recommended, amends l.57, l.113, BACKTESTER l.9 and CANONICAL l.11. |
| SN6-4 | Q11 offers (a) a one-clock-hour cutoff, whose effect on coarser inputs depends on phase (recommended), or (b) the immediately preceding emission, a uniform one-emission delay. They are no longer described as equivalent. |
| SN6-5 | Q13 states separately the costs of the ETH candidate, the ETH benchmark (following Q12) and the ETH drawdown. |
