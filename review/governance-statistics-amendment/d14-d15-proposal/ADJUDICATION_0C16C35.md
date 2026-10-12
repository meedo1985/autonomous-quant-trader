# Adjudication of the focused checks of D-14/D-15 rev5 (`0c16c35`)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`).

Reviews:
- `FABLE_REVIEW_0C16C35.md`: FN5, NOT READY, `86d005d`.
- `SOL_REVIEW_0C16C35.md`: SN5, NOT READY, `d95244a`.

All findings are accepted; none is rejected. They are applied in revision 6.

| Finding(s) | Disposition in rev 6 |
|---|---|
| FN5-1, SN5-1 | §1.2 defines three classes, fixed at declaration: signal-timed, timing-free (constant `s` and no overlay) and overlay-timed. The rev 5 claims are withdrawn. Q2 `N/A` applies only to timing-free trials. Q2b recommends that overlay-timed trials fail, with `N/A` (promotion without G-11 evidence) and "different null later" as alternatives; FN5's (α) is listed. The owner's recorded rule is mapped: its fixed size does not fit `s·τ/σ̂` (a separate registration question), and it is overlay-timed, so it fails G-11 under Q2b(a). |
| SN5-2, FN5-2 | §2.1: eligibility is classified at decision time and never re-judged. A reduction order is clamped at fill to `min(target, held)` and so never fills as an increase [AI default]. The clock is set only on fills that actually raised exposure, which, because of the clamp, are only 00:00 orders. Q10 is now one anchor question. The "never binds" disclosure is re-derived under the clamp. |
| SN5-3, FN5-7 | §2.3 has a separate row for each leg. Q15(b) and Q17(b) are explicitly "ETH entirely at baseline, overriding Q14/Q16 for ETH". Q13 offers the alternative reading (the whole ETH rule at 1x). |
| FN5-3 | §2.2: model outputs are not lagged separately. They are re-inferred on lagged features at their own emission times. The coarser-feature rule is labelled a reading of l.267. |
| FN5-4 | §2.2 lists the lagged inputs, including the overlay's price triggers [AI default] and the band-test target. Held exposure is position accounting at the current price. |
| FN5-5 | Q20(iii) applies at 00:00 and at intraday decisions. It cites BACKTESTER l.10 and CANONICAL l.12; C-3 is updated. |
| FN5-6 | Q20(i)'s consequence is reworded: the position is trapped while the price is below entry. |
| FN5-8 | §3 separates per-nominee candidate runs from the shared per-cell benchmark runs. |

**Review cadence [AI default].** The overlay-class change is substantive, so
both families run a final focused check of the 5→6 diff before the owner is
asked.
